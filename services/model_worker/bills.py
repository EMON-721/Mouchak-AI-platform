"""Private bill history and genuine, owner-specific IsolationForest inference.

No tariffs, government observations or real training records are bundled here.
Owner assertions are not independently verified Bangladesh evaluation data.
"""

import base64, hashlib, json, re, time
from datetime import date
from decimal import Decimal
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, Integer, Boolean, String, Text, UniqueConstraint, select, delete, func
from sqlalchemy.orm import Mapped, mapped_column
from .store import Base, User, Workspace, Run, Consent, uid, now, seal, open_sealed, PRODUCTION
from .auth import identify, db_session, audit
from .domain import number, normalize

router = APIRouter(prefix="/api/bills")
BillType = Literal["electricity", "gas", "water", "internet"]
FEATURES = ["log1p_units_per_day", "log1p_consumption_bdt_per_day", "log1p_stated_bdt_per_day", "period_days_over_31"]
VERSION = "private-bill-iforest-v1"
NOTICE = "নিজের ইতিহাসের পরীক্ষামূলক তুলনা; ভুল চার্জ, জালিয়াতি বা ভবিষ্যৎ বিলের প্রমাণ নয়। / Exploratory comparison with your history; not evidence of wrong charges, fraud or future bills."


class BillEntry(Base):
    __tablename__ = "bill_history_entries"
    __table_args__ = (UniqueConstraint("user_id", "workspace_id", "bill_type", "month", name="uq_private_bill_month"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    bill_type: Mapped[str] = mapped_column(String)
    month: Mapped[str] = mapped_column(String)
    encrypted: Mapped[str] = mapped_column(Text)
    training_allowed: Mapped[bool] = mapped_column(Boolean)
    is_demo: Mapped[bool] = mapped_column(Boolean)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str] = mapped_column(String, default=now)


class BillModel(Base):
    __tablename__ = "bill_personal_models"
    __table_args__ = (UniqueConstraint("user_id", "workspace_id", "bill_type", name="uq_private_bill_model"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    bill_type: Mapped[str] = mapped_column(String)
    checksum: Mapped[str] = mapped_column(String(64))
    encrypted: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BillInput(Strict):
    workspace_id: str
    bill_type: BillType
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    period_days: int = Field(strict=True, ge=1, le=62)
    units: str = Field(max_length=30)
    consumption_bdt: str = Field(max_length=30)
    fixed_bdt: str = Field(default="0", max_length=30)
    tax_bdt: str = Field(default="0", max_length=30)
    adjustment_bdt: str = Field(default="0", max_length=30)
    stated_bdt: str = Field(max_length=30)
    confirmed: bool = Field(strict=True)
    processing_consent: bool = Field(strict=True)
    allow_personal_model: bool = Field(default=False, strict=True)
    is_demo: bool = Field(default=False, strict=True)


class TrainInput(Strict):
    workspace_id: str
    bill_type: BillType
    consent: bool = Field(strict=True)


def scope(db, u, workspace_id, lock=False):
    if lock:
        db.scalar(select(User.id).where(User.id == u.id).with_for_update())
    workspace = db.scalar(select(Workspace).where(Workspace.id == workspace_id, Workspace.user_id == u.id))
    if not workspace:
        raise HTTPException(404, "Workspace not found")
    return workspace


def clean(p):
    if not p.confirmed or not p.processing_consent:
        raise HTTPException(422, "Confirm every amount and give processing consent / সংখ্যা যাচাই ও সম্মতি প্রয়োজন")
    try:
        start = date.fromisoformat(p.month + "-01")
    except ValueError:
        raise HTTPException(422, "Invalid bill month")
    if start.year < 1971 or start > date.today().replace(day=1):
        raise HTTPException(422, "Choose an existing bill month / অতীত বা চলতি বিলের মাস দিন")
    values = {name: str(number(getattr(p, name), minimum=-100000000 if name == "adjustment_bdt" else 0, maximum=100000000).quantize(Decimal(".01")))
              for name in ["consumption_bdt", "fixed_bdt", "tax_bdt", "adjustment_bdt", "stated_bdt"]}
    values["units"] = str(number(p.units, maximum=100000000).quantize(Decimal(".0001")))
    computed = sum(Decimal(values[name]) for name in ["consumption_bdt", "fixed_bdt", "tax_bdt", "adjustment_bdt"])
    if computed < 0:
        raise HTTPException(422, "The entered charge breakdown has a negative total")
    return {**values, "period_days": p.period_days, "bill_type": p.bill_type, "month": p.month,
            "computed_bdt": str(computed), "difference_bdt": str(Decimal(values["stated_bdt"]) - computed),
            "source_kind": "owner_confirmed_claim", "independently_verified": False,
            "confirmed_at": now(), "consent_version": "private-bill-v1"}


def feature_vector(data):
    import numpy as np
    days = data["period_days"]
    return np.array([np.log1p(float(data["units"]) / days),
                     np.log1p(float(data["consumption_bdt"]) / days),
                     np.log1p(float(data["stated_bdt"]) / days), days / 31.0], dtype=np.float32)


def entries(db, u, workspace_id, bill_type):
    return list(db.scalars(select(BillEntry).where(
        BillEntry.user_id == u.id, BillEntry.workspace_id == workspace_id, BillEntry.bill_type == bill_type
    ).order_by(BillEntry.month, BillEntry.id)))


def entry_view(entry):
    return {"id": entry.id, "workspace_id": entry.workspace_id, "bill_type": entry.bill_type,
            "month": entry.month, "allow_personal_model": entry.training_allowed,
            "is_demo": entry.is_demo, "revision": entry.revision, **open_sealed(entry.encrypted)}


def invalidate(db, u, workspace_id, bill_type):
    # Deleting or withdrawing a row erases every active derived artifact for this series.
    db.execute(delete(BillModel).where(BillModel.user_id == u.id, BillModel.workspace_id == workspace_id, BillModel.bill_type == bill_type))


@router.get("/history")
def history(workspace_id: str, bill_type: BillType, u=Depends(identify), db=Depends(db_session, scope="function")):
    scope(db, u, workspace_id)
    return [entry_view(e) for e in entries(db, u, workspace_id, bill_type)]


@router.post("/history", status_code=201)
def create(p: BillInput, u=Depends(identify), db=Depends(db_session, scope="function")):
    scope(db, u, p.workspace_id, lock=True)
    data = clean(p)
    existing = entries(db, u, p.workspace_id, p.bill_type)
    if len(existing) >= 500:
        raise HTTPException(429, "At most 500 bills per type/workspace")
    if any(e.month == p.month for e in existing):
        raise HTTPException(409, "This month already exists; edit its record / এই মাসের বিল আগেই আছে")
    invalidate(db, u, p.workspace_id, p.bill_type)
    item = BillEntry(user_id=u.id, workspace_id=p.workspace_id, bill_type=p.bill_type, month=p.month,
                     encrypted=seal(data), training_allowed=p.allow_personal_model, is_demo=p.is_demo)
    db.add(item)
    db.flush()
    return entry_view(item)


def owned(db, u, entry_id):
    item = db.scalar(select(BillEntry).where(BillEntry.id == entry_id, BillEntry.user_id == u.id))
    if not item:
        raise HTTPException(404)
    return item


@router.patch("/history/{entry_id}")
def edit(entry_id: str, p: BillInput, u=Depends(identify), db=Depends(db_session, scope="function")):
    scope(db, u, p.workspace_id, lock=True)
    item = owned(db, u, entry_id)
    if item.workspace_id != p.workspace_id or item.bill_type != p.bill_type:
        raise HTTPException(422, "A correction cannot silently move a bill to another series")
    if any(e.month == p.month and e.id != item.id for e in entries(db, u, p.workspace_id, p.bill_type)):
        raise HTTPException(409, "This month already exists")
    data = clean(p)
    invalidate(db, u, p.workspace_id, p.bill_type)
    item.month, item.encrypted = p.month, seal(data)
    item.training_allowed, item.is_demo = p.allow_personal_model, p.is_demo
    item.revision += 1
    return entry_view(item)


@router.delete("/history/{entry_id}")
def remove(entry_id: str, u=Depends(identify), db=Depends(db_session, scope="function")):
    db.scalar(select(User.id).where(User.id == u.id).with_for_update())
    item = owned(db, u, entry_id)
    invalidate(db, u, item.workspace_id, item.bill_type)
    db.delete(item)
    return {"deleted": True, "derived_model_erased": True, "backup_expiry_is_separate": True}


def model_for(db, u, workspace_id, bill_type):
    return db.scalar(select(BillModel).where(BillModel.user_id == u.id, BillModel.workspace_id == workspace_id, BillModel.bill_type == bill_type))


def eligible(rows):
    return [e for e in rows if e.training_allowed and not e.is_demo]


def fingerprint(rows):
    # Only stored in this owner's encrypted artifact; not a public dataset digest.
    return hashlib.sha256(json.dumps([(r.id, r.revision, open_sealed(r.encrypted)) for r in rows], sort_keys=True).encode()).hexdigest()


def load_artifact(model):
    import onnxruntime as ort
    ort.disable_telemetry_events()
    data = open_sealed(model.encrypted)
    artifact = base64.b64decode(data["onnx"], validate=True)
    if len(artifact) > 2 * 1024 * 1024 or hashlib.sha256(artifact).hexdigest() != model.checksum:
        raise HTTPException(503, "Private model integrity check failed")
    options = ort.SessionOptions()
    options.intra_op_num_threads, options.inter_op_num_threads = 2, 1
    return ort.InferenceSession(artifact, sess_options=options, providers=["CPUExecutionProvider"]), data["card"]


@router.get("/model")
def model_status(workspace_id: str, bill_type: BillType, u=Depends(identify), db=Depends(db_session, scope="function")):
    scope(db, u, workspace_id)
    rows = eligible(entries(db, u, workspace_id, bill_type))
    model = model_for(db, u, workspace_id, bill_type)
    card = None
    if model:
        _, card = load_artifact(model)  # Report an actually loadable artifact, not a flag.
        if card["baseline_fingerprint"] != fingerprint(rows):
            raise HTTPException(409, "The baseline changed; rebuild the private model")
    return {"status": "production_blocked" if PRODUCTION else ("personal_unvalidated_baseline" if card else "not_fitted"), "eligible_rows": len(rows),
            "production_enabled": False, "evaluation_available": not PRODUCTION,
            "minimum_rows": 25, "model_id": model.id if model else None,
            "checksum": model.checksum if model else None, "card": card,
            "production_validated": False, "notice": NOTICE}


@router.post("/model/train")
def train(p: TrainInput, u=Depends(identify), db=Depends(db_session, scope="function")):
    if PRODUCTION:
        raise HTTPException(503, "Private bill ML is not production-validated; Bangladesh holdout and release review pending")
    if not p.consent:
        raise HTTPException(422, "Separate private-model training consent required / মডেলের জন্য আলাদা সম্মতি প্রয়োজন")
    scope(db, u, p.workspace_id, lock=True)
    rows = eligible(entries(db, u, p.workspace_id, p.bill_type))
    if not 25 <= len(rows) <= 500:
        raise HTTPException(422, "Need 25–500 individually consented, confirmed non-demo bills of the same type / একই ধরনের অন্তত ২৫টি সম্মতিপ্রাপ্ত নিশ্চিত বিল প্রয়োজন")
    digest = fingerprint(rows)
    previous = model_for(db, u, p.workspace_id, p.bill_type)
    if previous:
        _, card = load_artifact(previous)
        if card["baseline_fingerprint"] == digest:
            return {"model_id": previous.id, "checksum": previous.checksum, "card": card, "reused": True}
    import numpy as np, sklearn, skl2onnx
    from sklearn.ensemble import IsolationForest
    from skl2onnx import to_onnx
    started = time.perf_counter()
    matrix = np.stack([feature_vector(open_sealed(r.encrypted)) for r in rows])
    if np.unique(matrix, axis=0).shape[0] < 5:
        raise HTTPException(422, "The baseline has too little variation for this model")
    forest = IsolationForest(n_estimators=100, random_state=42, contamination="auto", n_jobs=1).fit(matrix)
    graph = to_onnx(forest, matrix[:1], name=VERSION, target_opset={"": 18, "ai.onnx.ml": 3}, options={id(forest): {"score_samples": True}})
    artifact = graph.SerializeToString()
    checksum = hashlib.sha256(artifact).hexdigest()
    item = BillModel(id=uid(), user_id=u.id, workspace_id=p.workspace_id, bill_type=p.bill_type, checksum=checksum)
    card = {"model_id": "sklearn.IsolationForest", "version": VERSION, "format": "ONNX",
            "sklearn_version": sklearn.__version__, "exporter_version": skl2onnx.__version__,
            "features": FEATURES, "n_estimators": 100, "random_state": 42, "contamination": "auto",
            "rows": len(rows), "source_kind": "owner_confirmed_claim", "independently_verified": False,
            "allowed_use": "this_owner_private_bill_comparison_only", "shared_training": False,
            "consent_version": "private-bill-v1", "baseline_fingerprint": digest,
            "training_row_ids": [r.id for r in rows], "is_demo": False,
            "bangladesh_holdout_evaluated": False, "confidence_calibrated": False,
            "production_validated": False, "trained_at": now(), "artifact_sha256": checksum}
    item.encrypted = seal({"onnx": base64.b64encode(artifact).decode(), "card": card})
    session, _ = load_artifact(item)
    actual = session.run(["scores"], {session.get_inputs()[0].name: matrix})[0].ravel()
    delta = float(np.max(np.abs(actual - forest.decision_function(matrix))))
    if not np.isfinite(actual).all() or delta > 1e-5:
        raise HTTPException(503, "Model export parity check failed")
    card["export_max_absolute_error"] = delta
    card["fit_and_export_ms"] = round((time.perf_counter() - started) * 1000, 2)
    item.encrypted = seal({"onnx": base64.b64encode(artifact).decode(), "card": card})
    if previous:
        db.delete(previous)
        db.flush()
    db.add(item)
    db.flush()
    db.add(Consent(user_id=u.id, module="billdetect-ai", purpose="private_bill_model_training", granted=True))
    audit(db, u.id, "private_bill_model_fitted", item.id, {"rows": len(rows), "version": VERSION})
    return {"model_id": item.id, "checksum": checksum, "card": card, "reused": False}


@router.post("/predict", status_code=201)
def predict(p: BillInput, u=Depends(identify), db=Depends(db_session, scope="function")):
    if PRODUCTION:
        raise HTTPException(503, "Private bill ML is not production-validated; Bangladesh holdout and release review pending")
    scope(db, u, p.workspace_id, lock=True)
    data = clean(p)
    model = model_for(db, u, p.workspace_id, p.bill_type)
    if not model:
        raise HTTPException(409, "Fit your private model using 25+ confirmed bills first")
    rows = eligible(entries(db, u, p.workspace_id, p.bill_type))
    session, card = load_artifact(model)
    if len(rows) < 25 or card["baseline_fingerprint"] != fingerprint(rows):
        raise HTTPException(409, "Private baseline is no longer eligible")
    started = time.perf_counter()
    score = float(session.run(["scores"], {session.get_inputs()[0].name: feature_vector(data)[None, :]})[0].ravel()[0])
    if not (-1 <= score <= 1):
        raise HTTPException(503, "Non-finite or invalid model output")
    output = {"module": "billdetect-ai", "method": "Real owner-specific IsolationForest / ONNX CPU",
              "model_version": VERSION + "/" + model.checksum, "status": "personal_unvalidated_baseline",
              "facts": {"decision_score": round(score, 6), "unusual_against_your_baseline": score < 0,
                        "computed_bdt": data["computed_bdt"], "entered_total_difference_bdt": data["difference_bdt"]},
              "details": {"baseline_rows": len(rows), "model_id": model.id, "bill_type": p.bill_type,
                          "features": FEATURES, "is_demo_input": p.is_demo, "confidence": None,
                          "government_tariff_checked": False, "shared_training": False},
              "uncertainties": [NOTICE, "এই model বাংলাদেশি holdout-এ যাচাই হয়নি। / No Bangladesh holdout evaluation has passed."],
              "references": [], "created_at": now(), "latency_ms": round((time.perf_counter() - started) * 1000, 2),
              "full_module_complete": False, "advanced_pipeline_status": "personal_baseline_not_production_validated"}
    run = Run(user_id=u.id, workspace_id=p.workspace_id, module="billdetect-ai", encrypted=seal({"inputs": data, "output": output, "asset_ids": []}))
    db.add(run)
    db.add(Consent(user_id=u.id, module="billdetect-ai", purpose="private_bill_inference", granted=True))
    db.flush()
    return {"id": run.id, **output}


@router.get("/export")
def export(workspace_id: str, bill_type: BillType, u=Depends(identify), db=Depends(db_session, scope="function")):
    data = {"bills": history(workspace_id, bill_type, u, db), "model": model_status(workspace_id, bill_type, u, db)}
    return Response(json.dumps(data, ensure_ascii=False, indent=2), media_type="application/json",
                    headers={"Content-Disposition": 'attachment; filename="mouchak-private-bills.json"'})


def draft_fields(ocr_result):
    patterns = {
        "stated_bdt": r"(?:grand\s*total|total\s*(?:due|payable|amount)|amount\s*due|^total\b|সর্বমোট|সর্বমোট|মোট বিল|পরিশোধযোগ্য)",
        "consumption_bdt": r"(?:energy\s*charge|consumption\s*charge|usage\s*charge|বিদ্যুৎ চার্জ|এনার্জি চার্জ|ব্যবহার.*চার্জ)",
        "fixed_bdt": r"(?:fixed\s*charge|demand\s*charge|স্থির চার্জ|ডিমান্ড চার্জ)",
        "tax_bdt": r"(?:\bvat\b|\btax\b|ভ্যাট|মূসক)",
        "units": r"(?:units\s*(?:used|consumed)|consumed\s*units|ব্যবহৃত ইউনিট|মোট ইউনিট)",
    }
    identifiers = re.compile(r"(?:account|customer|consumer|meter\s*(?:no|number|id)|গ্রাহক|হিসাব নম্বর|মিটার নম্বর)", re.I)
    amounts = re.compile(r"(?<![\w.])\d+(?:,\d{3})*(?:\.\d{1,2})?(?![\w.])")
    candidates, text_lines = [], []
    for page in ocr_result["pages"]:
        lines = {}
        for word in page["words"]:
            lines.setdefault(word["line"], []).append(word)
        for words in lines.values():
            line = " ".join(w["text"] for w in words)
            if identifiers.search(line):
                text_lines.append("[গ্রাহক/হিসাবের পরিচয় লুকানো / identifier line hidden]")
                continue
            text_lines.append(line)
            normalized = normalize(line)
            field = next((name for name, expression in patterns.items() if re.search(expression, normalized, re.I)), None)
            found = amounts.findall(normalized)
            if not field or len(found) != 1:
                continue  # Ambiguous numbers are never silently chosen.
            candidates.append({"field": field, "value": found[0].replace(",", ""),
                               "page": page["page"], "line": line,
                               "engine_word_confidence_min": min(w["engine_word_confidence"] for w in words),
                               "low_confidence_heuristic": any(w["low_confidence_heuristic"] for w in words),
                               "boxes": [{k: w[k] for k in ["x", "y", "width", "height"]} for w in words]})
    fields = {}
    for name in patterns:
        values = {c["value"] for c in candidates if c["field"] == name}
        fields[name] = next(iter(values)) if len(values) == 1 else None
    return {"draft_fields": fields, "candidates": candidates, "redacted_text": "\n".join(text_lines),
            "unknown_fields": [k for k, v in fields.items() if v is None],
            "confidence": None, "word_confidence_is_calibrated": False,
            "human_review_required": True, "model_id": ocr_result["model"],
            "page_count": ocr_result["page_count"], "notice": "OCR খসড়া; সব সংখ্যা নিজে যাচাই করুন। / OCR draft: verify every number."}


@router.post("/extract/{asset_id}")
def extract(asset_id: str, page: int = 1, u=Depends(identify), db=Depends(db_session, scope="function")):
    from .main import owner_asset, asset_bytes, PRODUCTION
    from .inference import ocr
    asset = owner_asset(db, u, asset_id)
    if asset.kind not in ["png", "jpeg", "pdf"]:
        raise HTTPException(422, "A bill image or PDF is required")
    if PRODUCTION and asset.scan_state != "clean":
        raise HTTPException(422, "File has not passed scanning")
    # One page per request keeps the operation bounded for the Netlify proxy.
    return draft_fields(ocr(asset_bytes(asset), asset.kind, page_number=page))
