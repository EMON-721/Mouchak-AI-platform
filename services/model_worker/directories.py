"""Reviewed nonpersonal directories. No clinic, pharmacy or stock records are invented.

Publication is a schema-specific path over the existing encrypted ingestion jobs.
Health-directory reuse requires two current independent rights decisions and a
second operator's publication decision. Serving always rechecks rights and age.
"""
import hashlib
import json
from datetime import datetime, timezone
from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from sqlalchemy import select, text as sql_text

from .auth import authorize, audit, db_session
from .domain import InputError, field, normalize, result, text
from .operations import SourceReview, fingerprint, rights_round
from .store import Config, Job, Source, open_sealed, seal

router = APIRouter(prefix="/api/admin/directories")
MODULES = {"cliniccompass-bd": "facility_v1", "oshudhkhoj-bd": "pharmacy_v1"}
MAX_AGE = {"facility_v1": 90 * 86400, "pharmacy_v1": 86400}


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Record(Strict):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    name_bn: str = Field(min_length=1, max_length=160)
    name_en: str = Field(min_length=1, max_length=160)
    district_bn: str = Field(min_length=1, max_length=80)
    district_en: str = Field(min_length=1, max_length=80)
    address_bn: str = Field(min_length=1, max_length=240)
    address_en: str = Field(min_length=1, max_length=240)
    latitude: float | None = Field(default=None, ge=20, le=27)
    longitude: float | None = Field(default=None, ge=88, le=93)
    verified_at: datetime

    @model_validator(mode="after")
    def coordinates_and_time(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Supply both coordinates or neither")
        if self.verified_at.tzinfo is None:
            raise ValueError("verified_at must include its timezone")
        if self.verified_at > datetime.now(timezone.utc):
            raise ValueError("Future verification timestamps are prohibited")
        return self


class Facility(Record):
    services_bn: list[str] = Field(min_length=1, max_length=20)
    services_en: list[str] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def services(self):
        if any(not v.strip() or len(v) > 100 for v in self.services_bn + self.services_en):
            raise ValueError("Service labels must contain 1–100 characters")
        return self


class Pharmacy(Record):
    product_name: str = Field(min_length=1, max_length=160)
    strength: str = Field(min_length=1, max_length=80)
    formulation: str = Field(min_length=1, max_length=80)
    reported_availability: Literal["reported_available", "reported_unavailable", "not_confirmed"]


class Batch(Strict):
    source_id: str = Field(min_length=1, max_length=100)
    schema_name: Literal["facility_v1", "pharmacy_v1"]
    records: list[dict] = Field(min_length=1, max_length=200)


class Publish(Strict):
    expected_revision: str | None = Field(default=None, max_length=100)


def schema_records(schema, values):
    model = Facility if schema == "facility_v1" else Pharmacy
    try:
        records = [model.model_validate(v).model_dump(mode="json") for v in values]
    except ValidationError:
        # Never echo submitted records or identifiers in validation output.
        raise HTTPException(422, "Invalid directory schema, coordinates or timezone-aware timestamp") from None
    if len({v["id"] for v in records}) != len(records):
        raise HTTPException(422, "Duplicate directory record IDs")
    current = datetime.now(timezone.utc).timestamp()
    if any(current - datetime.fromisoformat(v["verified_at"]).timestamp() >= MAX_AGE[schema] for v in records):
        raise HTTPException(422, "Stale records must be reverified before import")
    return records


def approved_source(db, sid, schema):
    source = db.scalar(select(Source).where(Source.id == sid).with_for_update())
    if not source or MODULES.get(source.module) != schema or source.state != "approved_train_and_reuse":
        raise HTTPException(422, "A matching source approved for reuse is required")
    reviews = list(db.scalars(select(SourceReview).where(
        SourceReview.source_id == sid,
        SourceReview.round == rights_round(db, sid),
        SourceReview.decision == "approved_train_and_reuse",
    )))
    for review in reversed(reviews):
        same = [r for r in reviews if r.asset_hash == review.asset_hash]
        evidence = json.loads(review.evidence)
        if len({r.reviewer for r in same}) < 2 or evidence.get("sensitivity") != "public_nonpersonal":
            continue
        # Source's active review must refer to this very asset, not an older one.
        active = json.loads(source.evidence or "{}")
        if active.get("review_id") not in {r.id for r in same}:
            continue
        url = urlsplit(evidence.get("asset_url", ""))
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise HTTPException(422, "Approved asset must have a credential-free HTTPS reference")
        return source, {
            "round": rights_round(db, sid),
            "evidence_hash": fingerprint(source.evidence),
            "asset_hash": review.asset_hash,
            "asset_url": evidence["asset_url"],
            "license_uri": evidence["license_uri"],
            "source_date": evidence["source_date"],
            "independent_reviewers": len({r.reviewer for r in same}),
        }
    raise HTTPException(422, "Two matching independent public-nonpersonal asset rights reviews are required")


def key(slug):
    return "directory:" + slug


def publication_lock(db, slug):
    if db.bind.dialect.name == "postgresql":
        # One transaction-scoped lock per module, even before its pointer exists.
        lock_id = int.from_bytes(hashlib.sha256(key(slug).encode()).digest()[:8], "big", signed=True)
        db.execute(sql_text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_id})


def current_revision(db, slug):
    conf = db.get(Config, key(slug))
    return json.loads(conf.value).get("revision") if conf else None


@router.get("")
def list_batches(u=Depends(authorize("jobs")), db=Depends(db_session)):
    # Other dataset jobs can contain private previews; only return schema metadata.
    batches = []
    for job in db.scalars(select(Job).where(Job.state.like("directory_%")).order_by(Job.created_at.desc()).limit(200)):
        payload = open_sealed(job.payload)
        batches.append({"id": job.id, "source_id": job.source_id, "state": job.state,
                        "module": payload["module"], "records": len(payload["records"]),
                        "owner": job.owner, "created_at": job.created_at,
                        "base_revision": payload["base_revision"]})
    return {"active": {slug: current_revision(db, slug) for slug in MODULES}, "batches": batches}


@router.post("/dry-run", status_code=201)
def dry_run(p: Batch, u=Depends(authorize("jobs")), db=Depends(db_session)):
    if len(json.dumps(p.records, ensure_ascii=False)) > 200000:
        raise HTTPException(413, "Directory batch is too large")
    source, rights = approved_source(db, p.source_id, p.schema_name)
    records = schema_records(p.schema_name, p.records)
    payload = {"module": source.module, "schema_name": p.schema_name, "records": records,
               "rights": rights, "base_revision": current_revision(db, source.module)}
    checksum = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    job = Job(source_id=source.id, owner=u.id, payload=seal(payload), state="directory_dry_run", checksum=checksum)
    db.add(job)
    db.flush()
    audit(db, u.id, "directory_dry_run", job.id, {"module": source.module, "records": len(records)})
    return {"id": job.id, "records": len(records), "schema_name": p.schema_name,
            "preview": records[:3], "base_revision": payload["base_revision"], "published": False}


@router.get("/{jid}")
def review_batch(jid: str, u=Depends(authorize("jobs")), db=Depends(db_session)):
    job = db.get(Job, jid)
    if not job or not job.state.startswith("directory_"):
        raise HTTPException(404)
    payload = open_sealed(job.payload)
    return {"id": job.id, "owner": job.owner, "state": job.state, "checksum": job.checksum, **payload}


@router.post("/{jid}/publish")
def publish(jid: str, p: Publish, u=Depends(authorize("jobs")), db=Depends(db_session)):
    candidate = db.get(Job, jid)
    if not candidate or not candidate.state.startswith("directory_"):
        raise HTTPException(404)
    publication_lock(db, open_sealed(candidate.payload)["module"])
    job = db.scalar(select(Job).where(Job.id == jid).with_for_update().execution_options(populate_existing=True))
    if not job or job.state not in {"directory_dry_run", "directory_retired"}:
        raise HTTPException(409, "Choose a staged or retired directory revision")
    if job.owner == u.id:
        raise HTTPException(403, "A second operator must review and publish this batch")
    payload = open_sealed(job.payload)
    source, rights = approved_source(db, job.source_id, payload["schema_name"])
    if rights != payload["rights"]:
        raise HTTPException(409, "Rights changed; create a new reviewed batch")
    records = schema_records(payload["schema_name"], payload["records"])
    conf = db.scalar(select(Config).where(Config.key == key(source.module)).with_for_update())
    previous = json.loads(conf.value).get("revision") if conf else None
    if p.expected_revision != previous:
        raise HTTPException(409, "Directory changed; refresh before publishing")
    # Full immutable public snapshot: the queue worker never reads private jobs.
    encoded = json.dumps({**payload, "records": records, "revision": job.id,
                          "source_id": job.source_id, "published_at": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False)
    if conf:
        conf.value = encoded
    else:
        db.add(Config(key=key(source.module), value=encoded))
    if previous:
        old = db.get(Job, previous)
        if old:
            old.state = "directory_retired"
    job.state = "directory_published"
    audit(db, u.id, "directory_published", job.id, {"module": source.module, "records": len(records), "previous": previous})
    return {"revision": job.id, "records": len(records), "previous_revision": previous}


@router.post("/{slug}/withdraw")
def withdraw(slug: str, p: Publish, u=Depends(authorize("jobs")), db=Depends(db_session)):
    if slug not in MODULES:
        raise HTTPException(404)
    publication_lock(db, slug)
    conf = db.scalar(select(Config).where(Config.key == key(slug)).with_for_update())
    current = json.loads(conf.value) if conf else {}
    if p.expected_revision != current.get("revision"):
        raise HTTPException(409, "Directory changed; refresh before withdrawing")
    if current.get("revision"):
        job = db.get(Job, current["revision"])
        if job:
            job.state = "directory_retired"
    if conf:
        conf.value = json.dumps({"revision": None})
    audit(db, u.id, "directory_withdrawn", slug, {"previous": current.get("revision")})
    return {"withdrawn": True}


def availability(db, slug):
    conf = db.get(Config, key(slug))
    snapshot = json.loads(conf.value) if conf else {}
    if not snapshot.get("revision"):
        return None
    source = db.get(Source, snapshot["source_id"])
    rights = snapshot["rights"]
    if (not source or source.state != "approved_train_and_reuse"
            or rights_round(db, source.id) != rights["round"]
            or fingerprint(source.evidence) != rights["evidence_hash"]):
        return None
    current = datetime.now(timezone.utc).timestamp()
    records = [r for r in snapshot["records"] if 0 <= current - datetime.fromisoformat(r["verified_at"]).timestamp() < MAX_AGE[snapshot["schema_name"]]]
    return {**snapshot, "records": records} if records else None


def fields(engine):
    return [field("text", "সেবা বা ওষুধের নাম", "Service or medicine name"),
            field("district", "জেলা (ঐচ্ছিক)", "District (optional)", optional=True)]


@lru_cache(maxsize=8)
def search_index(revision, encoded):
    from .inference import embed, tokens
    from rank_bm25 import BM25Okapi
    from numpy import concatenate
    records = json.loads(encoded)
    documents = [" ".join(str(value) if not isinstance(value, list) else " ".join(value)
                          for name, value in r.items() if name not in {"verified_at", "latitude", "longitude", "id"}) for r in records]
    # Keep peak ONNX attention memory bounded even for the 200-record limit.
    vectors = concatenate([embed(documents[i:i + 8]) for i in range(0, len(documents), 8)])
    return vectors, BM25Okapi([tokens(t) or ["_"] for t in documents]), documents


def search(db, slug, inputs):
    query = text(inputs)
    if len(query) > 300:
        raise InputError("Search must contain at most 300 characters / সর্বোচ্চ ৩০০ অক্ষর")
    district = text(inputs, "district", required=False)
    if len(district) > 80:
        raise InputError("District must contain at most 80 characters / সর্বোচ্চ ৮০ অক্ষর")
    snapshot = availability(db, slug)
    if not snapshot:
        raise InputError("Unavailable: no fresh rights-approved directory records / হালনাগাদ অনুমোদিত তালিকা নেই")
    records = snapshot["records"]
    from .inference import embed, tokens
    vectors, lexical, documents = search_index(snapshot["revision"], json.dumps(records, sort_keys=True, ensure_ascii=False))
    semantic = vectors @ embed([query])[0]
    lexical_scores = lexical.get_scores(tokens(query))
    needle = normalize(query).casefold()
    location = normalize(district).casefold()
    ranked = []
    for i, record in enumerate(records):
        if location and not any(location == normalize(record[k]).casefold() for k in ["district_bn", "district_en"]):
            continue
        exact = needle in normalize(documents[i]).casefold()
        # Medicine retrieval requires literal product evidence: no semantic substitution.
        if snapshot["schema_name"] == "pharmacy_v1":
            if needle not in normalize(record["product_name"]).casefold():
                continue
        elif not exact and (float(semantic[i]) < .2 or float(lexical_scores[i]) <= 0):
            continue
        score = float(semantic[i]) + .12 * float(lexical_scores[i]) + (1 if exact else 0)
        ranked.append((score, record))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    warnings = ["Directory information only; contact the provider to confirm services, hours and availability. / তালিকার তথ্য; সেবা ও সময় সরাসরি নিশ্চিত করুন।",
                "No diagnosis, treatment, medicine substitution, dosage or guaranteed stock. / রোগনির্ণয়, চিকিৎসা, বিকল্প ওষুধ, ডোজ বা স্টকের নিশ্চয়তা নয়।"]
    output = result("Rights-gated multilingual MiniLM + BM25 directory retrieval",
                    {"matching_records": len(ranked), "returned_records": min(len(ranked), 20),
                     "records": [r for _, r in ranked[:20]], "directory_revision": snapshot["revision"]},
                    {"source_id": snapshot["source_id"], "published_at": snapshot["published_at"], "maximum_record_age_seconds": MAX_AGE[snapshot["schema_name"]]}, warnings)
    output["model_version"] = "Xenova/paraphrase-multilingual-MiniLM-L12-v2/ONNX-int8+directory-v1"
    output["references"] = [{"kind": "rights_reviewed_directory", "official": False,
                             **{k: snapshot["rights"][k] for k in ["asset_url", "license_uri", "source_date", "independent_reviewers"]}}]
    output["source_kind"] = "rights_reviewed_directory"
    return output
