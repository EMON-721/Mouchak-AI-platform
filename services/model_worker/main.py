from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Any
import json, os, time, secrets, hashlib, re, csv, io, subprocess, shutil, threading, base64
from fastapi import (
    FastAPI,
    Request,
    Response,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select, delete, func
from .store import *
from .auth import *
from .domain import process, F, InputError
from .inference import model_health, ocr, compare_images, audio_stats, retrieve
from . import storage, rate_limit, uploads, inference_queue
from . import retail, collaboration, operations, anonymous, bills, directories
from . import pose_runtime, pose_video
from .legacy_workflows import READING, PRODUCTS, reading_reflection, basket_compare

CAT = json.loads((ROOT / "packages/module-registry/catalogue.json").read_text())
MODULES = {m["slug"]: m for m in CAT["modules"]}
DOCS = json.loads((ROOT / "data/authored/learning.json").read_text())


@asynccontextmanager
async def lifespan(app):
    if not PRODUCTION:
        migrate()
    yield


app = FastAPI(
    title="Mouchak AI private API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/internal/docs" if not PRODUCTION else None,
)
app.include_router(retail.router)
app.include_router(collaboration.router)
app.include_router(operations.router)
app.include_router(anonymous.router)
app.include_router(uploads.router)
app.include_router(bills.router)
app.include_router(directories.router)
RATE = {}
RATE_LOCK = threading.Lock()


@app.middleware("http")
async def protection(request, call_next):
    internal_token = os.getenv("PRIVATE_API_TOKEN", "")
    if PRODUCTION and (
        not 32 <= len(internal_token) <= 512
        or not internal_token.isascii()
        or not hmac.compare_digest(request.headers.get("x-internal-api-token", "").encode("utf-8"), internal_token.encode("ascii"))
    ):
        return JSONResponse({"detail": "Private service authorization required"}, 403)
    if request.method not in ["GET", "HEAD", "OPTIONS"]:
        origin = request.headers.get("origin")
        trusted = os.getenv("PUBLIC_ORIGIN", "http://localhost:3000").rstrip("/")
        if origin and origin.rstrip("/") != trusted:
            return JSONResponse({"detail": "Origin rejected / উৎস অনুমোদিত নয়"}, 403)
        content_length = request.headers.get("content-length")
        if content_length and (
            not content_length.isdigit() or int(content_length) > 12 * 1024 * 1024
        ):
            return JSONResponse({"detail": "Request too large / অনুরোধ বেশি বড়"}, 413)
        key = (
            request.client.host if request.client else "local",
            (
                request.url.path.split("/")[2]
                if len(request.url.path.split("/")) > 2
                else ""
            ),
        )
        if PRODUCTION:
            # Transport peer is trusted; arbitrary forwarded/client IP headers are not.
            # Proxied traffic shares this ceiling until a reviewed edge identity exists.
            from starlette.concurrency import run_in_threadpool
            try:
                allowed, retry = await run_in_threadpool(
                    rate_limit.guard, key[0], key[1], request.cookies.get("mouchak_session", "")
                )
            except Exception:
                return JSONResponse({"detail": "Request guard unavailable / নিরাপত্তা সেবা পাওয়া যাচ্ছে না"}, 503)
            if not allowed:
                return JSONResponse(
                    {"detail": "Rate limit / কিছুক্ষণ পরে চেষ্টা করুন"}, 429,
                    headers={"Retry-After": str(retry), "Cache-Control": "no-store"},
                )
        else:
            with RATE_LOCK:
                ts = time.time()
                b = [t for t in RATE.get(key, []) if ts - t < 60]
                if len(b) >= 60:
                    return JSONResponse({"detail": "Rate limit / কিছুক্ষণ পরে চেষ্টা করুন"}, 429)
                if len(RATE) > 10000:
                    RATE.clear()
                b.append(ts)
                RATE[key] = b
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.exception_handler(InputError)
async def input_error(request, e):
    return JSONResponse({"detail": str(e)}, 422)


@app.exception_handler(ValueError)
async def value_error(request, e):
    return JSONResponse({"detail": "Invalid input format / ইনপুটের ফরম্যাট ভুল"}, 422)


@app.exception_handler(RequestValidationError)
async def validation_error(request, e):
    return JSONResponse(
        {
            "detail": "Input validation failed / ঘরগুলো সঠিকভাবে পূরণ করুন",
            "fields": [str(x["loc"][-1]) for x in e.errors()],
        },
        422,
    )


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Credentials(Strict):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=256)
    name: str = Field(default="", max_length=100)


class RunInput(Strict):
    inputs: dict[str, Any]
    consent: bool
    transfer_id: str | None = Field(default=None, max_length=100)
    workspace_id: str | None = None
    asset_ids: list[str] = Field(default_factory=list, max_length=2)
    language: str = "bn"
    idempotency_key: str | None = Field(default=None, max_length=100)


class Body(Strict):
    value: dict[str, Any]


def view_user(u):
    return {
        "id": u.id,
        "email": u.email,
        "name": u.name,
        "role": u.role,
        "language": u.language,
        "verified": u.verified,
        "mfa_enabled": u.mfa_enabled,
    }


def get_mod(slug, db):
    if slug not in MODULES:
        raise HTTPException(404, "Unknown tool / টুল পাওয়া যায়নি")
    m = dict(MODULES[slug])
    conf = db.get(Config, "module:" + slug)
    if conf:
        m.update(json.loads(conf.value))
    m["execution_mode"] = "queued" if inference_queue.enabled() else "synchronous"
    m["fields"] = F[m["engine"]]
    if slug in directories.MODULES:
        m["fields"] = directories.fields(m["engine"])
        if directories.availability(db, slug):
            m["release_status"] = "limited_support"
            m["description_bn"] = "হালনাগাদ অনুমোদিত তালিকায় সেবা বা ওষুধের নাম খুঁজুন; সরাসরি নিশ্চিত করুন।"
            m["description_en"] = "Search current rights-reviewed service or medicine records; confirm directly with the provider."
    if m["engine"] == "video" and pose_runtime.availability()["experimental_enabled"]:
        m["release_status"] = "experimental"
        m["fields"] = [{**f, "optional": True} for f in m["fields"]]
        m["description_bn"] = (
            "পরীক্ষামূলক: ছোট MP4 থেকে শরীরের pose ও 2D কোণ দেখুন; দক্ষতা বা injury মূল্যায়ন নয়।"
        )
        m["description_en"] = (
            "Experimental: body pose and 2D angles from short MP4 clips; no skill or injury assessment."
        )
    if m["engine"] == "reading":
        m["fields"] = [
            (
                {**f, "options": f.get("options", []) + [d["id"] for d in READING]}
                if f["key"] == "passage_id"
                else f
            )
            for f in m["fields"]
        ]
    return m


def owner_run(db, u, rid):
    r = db.scalar(select(Run).where(Run.id == rid, Run.user_id == u.id))
    if not r:
        raise HTTPException(404, "Record not found / রেকর্ড পাওয়া যায়নি")
    return r


def owner_asset(db, u, aid):
    a = db.scalar(select(Asset).where(Asset.id == aid, Asset.user_id == u.id))
    if not a:
        raise HTTPException(404, "File not found / ফাইল পাওয়া যায়নি")
    return a


def asset_bytes(a):
    # Local adapter stores encrypted bytes, never public static assets.
    return storage.get(a.path)


@app.get("/api/health")
def health():
    return {
        "api": "ok",
        "database_adapter": engine.dialect.name,
        "production_ready": False,
        "models": model_health(),
        "tools": 50,
        "processing_mode": "queued" if inference_queue.enabled() else "synchronous",
    }


@app.get("/api/modules")
def modules(db=Depends(db_session)):
    return {"modules": [get_mod(x, db) for x in MODULES], "total": 50}


@app.get("/api/modules/{slug}")
def module(slug: str, db=Depends(db_session)):
    return get_mod(slug, db)


@app.get("/api/sources")
def sources(module: str | None = None, db=Depends(db_session)):
    q = select(Source)
    if module:
        q = q.where(Source.module == module)
    return [
        {"id": s.id, "state": s.state, **json.loads(s.metadata_json)}
        for s in db.scalars(q)
    ]


@app.get("/api/learning")
def learning():
    return DOCS


@app.get("/api/reading/passages")
def reading_passages():
    return [{k: v for k, v in p.items() if k != "answer"} for p in READING]


@app.get("/api/commodities")
def commodities():
    return PRODUCTS


@app.get("/api/phrases")
def phrases():
    with (ROOT / "requirements/original-kit/seed/SEED_ACCESSIBILITY_PHRASES.csv").open(
        encoding="utf-8-sig"
    ) as f:
        return list(csv.DictReader(f))


@app.get("/api/public/cms/{page:path}")
def public_cms(page: str, db=Depends(db_session)):
    conf = db.get(Config, "cms:" + page)
    return json.loads(conf.value) if conf else {}


@app.post("/api/auth/register", status_code=201)
def register(
    p: Credentials, request: Request, response: Response, db=Depends(db_session)
):
    raise HTTPException(
        410,
        "Visitor accounts are not used. Open a tool directly. / ব্যবহারকারীর অ্যাকাউন্ট নেই; সরাসরি টুল খুলুন।",
    )


@app.post("/api/auth/login")
def login(p: Credentials, request: Request, response: Response, db=Depends(db_session)):
    u = db.scalar(select(User).where(User.email == p.email.strip().casefold()))
    valid = False
    if u and u.role in PRIVILEGED:
        try:
            valid = PH.verify(u.password, p.password)
        except VerificationError:
            pass
    else:
        PH.hash(p.password)  # similar work for nonexistent accounts
    if not valid or u.banned:
        raise HTTPException(401, "Invalid credentials / ইমেইল বা পাসওয়ার্ড ভুল")
    if PRODUCTION and not u.verified:
        raise HTTPException(403, "Verify your email first / আগে ইমেইল নিশ্চিত করুন")
    return {"user": view_user(u), "csrf": new_session(db, u, request, response)}


@app.get("/api/auth/me")
def me(request: Request, u=Depends(identify)):
    if u.role not in PRIVILEGED:
        raise HTTPException(401, "Operator authentication required")
    return {
        "user": view_user(u),
        "csrf": request.state.session.csrf,
        "mfa_verified": request.state.session.mfa_until > time.time(),
    }


@app.post("/api/auth/logout")
def logout(
    request: Request, response: Response, u=Depends(identify), db=Depends(db_session)
):
    db.delete(request.state.session)
    response.delete_cookie("mouchak_session", path="/")
    return {"revoked": True}


@app.get("/api/auth/sessions")
def sessions(request: Request, u=Depends(identify), db=Depends(db_session)):
    return [
        {
            "id": s.id,
            "device": s.device,
            "last_seen": s.last_seen,
            "expires": s.expires,
            "current": s.id == request.state.session.id,
        }
        for s in db.scalars(select(Session).where(Session.user_id == u.id))
    ]


@app.delete("/api/auth/sessions/{sid}")
def revoke(sid: str, u=Depends(identify), db=Depends(db_session)):
    s = db.scalar(select(Session).where(Session.id == sid, Session.user_id == u.id))
    if not s:
        raise HTTPException(404)
    db.delete(s)
    return {"revoked": True}


@app.post("/api/auth/request-reset", status_code=202)
def request_reset(p: Body, db=Depends(db_session)):
    email = str(p.value.get("email", "")).casefold()
    u = db.scalar(select(User).where(User.email == email))
    if u and u.role in PRIVILEGED:
        send_token(db, u, "reset")
    return {
        "message": "If the account exists, instructions will be sent when email is configured. / অ্যাকাউন্ট থাকলে কনফিগার করা ইমেইলে নির্দেশনা যাবে।"
    }


@app.post("/api/auth/verify")
def verify(p: Body, db=Depends(db_session)):
    t = db.get(Token, digest(str(p.value.get("token", ""))))
    if not t or t.purpose != "verify" or t.expires < time.time():
        raise HTTPException(422, "Expired or invalid verification token")
    u = db.get(User, t.user_id)
    u.verified = True
    db.delete(t)
    return {"verified": True}


@app.post("/api/auth/reset")
def reset(p: Body, db=Depends(db_session)):
    t = db.get(Token, digest(str(p.value.get("token", ""))))
    if not t or t.purpose != "reset" or t.expires < time.time():
        raise HTTPException(422, "Expired or invalid reset token")
    password = str(p.value.get("password", ""))
    password_valid(password)
    u = db.get(User, t.user_id)
    u.password = PH.hash(password)
    db.delete(t)
    db.execute(delete(Session).where(Session.user_id == u.id))
    return {"reset": True, "sessions_revoked": True}


@app.post("/api/auth/mfa/enroll")
def mfa_enroll(u=Depends(identify), db=Depends(db_session)):
    if u.role not in PRIVILEGED:
        raise HTTPException(403, "Operator access only")
    if u.mfa_enabled:
        raise HTTPException(409, "MFA already enrolled")
    secret = base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")
    u.mfa_secret = seal(secret)
    return {
        "secret": secret,
        "issuer": "Mouchak AI",
        "algorithm": "SHA1",
        "digits": 6,
        "period": 30,
    }


@app.post("/api/auth/mfa/verify")
def mfa_verify(p: Body, request: Request, u=Depends(identify), db=Depends(db_session)):
    code = canonical_totp(str(p.value.get("code", "")))
    if not u.mfa_secret or not valid_totp(
        open_sealed(u.mfa_secret), code
    ):
        raise HTTPException(401, "Invalid MFA code / MFA কোড ভুল")
    confkey = "mfa-replay:" + u.id
    last = db.get(Config, confkey)
    if last and json.loads(last.value).get("code") == digest(code):
        raise HTTPException(401, "Code already used; wait for next code")
    payload = json.dumps({"code": digest(code), "at": int(time.time())})
    if last:
        last.value = payload
    else:
        db.add(Config(key=confkey, value=payload))
    u.mfa_enabled = True
    request.state.session.mfa_until = int(time.time()) + 900
    audit(db, u.id, "mfa_verified", u.id)
    return {"verified": True, "valid_for_seconds": 900}


@app.patch("/api/profile")
def profile(p: Body, u=Depends(identify)):
    raise HTTPException(
        410,
        "Visitor profiles are not part of this platform / ব্যবহারকারীর প্রোফাইল নেই",
    )


@app.get("/api/workspaces")
def workspaces(u=Depends(identify), db=Depends(db_session)):
    return [
        {"id": w.id, "name": w.name}
        for w in db.scalars(select(Workspace).where(Workspace.user_id == u.id))
    ]


@app.post("/api/workspaces", status_code=201)
def new_workspace(p: Body, u=Depends(identify), db=Depends(db_session)):
    name = str(p.value.get("name", "")).strip()
    if not name or len(name) > 100:
        raise HTTPException(422, "Workspace name required")
    if (
        db.scalar(
            select(func.count()).select_from(Workspace).where(Workspace.user_id == u.id)
        )
        >= 20
    ):
        raise HTTPException(429, "Workspace limit reached")
    w = Workspace(user_id=u.id, name=name)
    db.add(w)
    db.flush()
    return {"id": w.id, "name": w.name}


@app.get("/api/workspaces/{wid}/history")
def history(
    wid: str, module: str | None = None, u=Depends(identify), db=Depends(db_session)
):
    w = db.scalar(
        select(Workspace).where(Workspace.id == wid, Workspace.user_id == u.id)
    )
    if not w:
        raise HTTPException(404)
    q = select(Run).where(Run.user_id == u.id, Run.workspace_id == wid)
    if module:
        q = q.where(Run.module == module)
    return [
        {
            "id": r.id,
            "module": r.module,
            "created_at": r.created_at,
            "saved": r.saved,
            "parent_id": r.parent_id,
        }
        for r in db.scalars(q.order_by(Run.created_at.desc()).limit(200))
    ]


@app.post("/api/consent", status_code=201)
def consent(p: Body, u=Depends(identify), db=Depends(db_session)):
    module = p.value.get("module")
    purpose = p.value.get("purpose")
    if module not in MODULES or purpose not in [
        "service_processing",
        "training_contribution",
        "cross_tool_transfer",
    ]:
        raise HTTPException(422, "Invalid consent purpose or module")
    c = Consent(
        user_id=u.id,
        module=module,
        purpose=purpose,
        granted=p.value.get("granted") is True,
    )
    db.add(c)
    db.flush()
    return {"id": c.id, "granted": c.granted}


@app.get("/api/consent")
def consents(u=Depends(identify), db=Depends(db_session)):
    return [
        {
            "id": c.id,
            "module": c.module,
            "purpose": c.purpose,
            "granted": c.granted,
            "created_at": c.created_at,
        }
        for c in db.scalars(select(Consent).where(Consent.user_id == u.id))
    ]


@app.delete("/api/consent/{cid}")
def withdraw(cid: str, u=Depends(identify), db=Depends(db_session)):
    c = db.scalar(select(Consent).where(Consent.id == cid, Consent.user_id == u.id))
    if not c:
        raise HTTPException(404)
    c.granted = False
    if c.module == "billdetect-ai" and c.purpose in ["private_bill_model_training", "training_contribution"]:
        from sqlalchemy import update
        db.scalar(select(User.id).where(User.id == u.id).with_for_update())
        db.execute(delete(bills.BillModel).where(bills.BillModel.user_id == u.id))
        db.execute(update(bills.BillEntry).where(bills.BillEntry.user_id == u.id).values(training_allowed=False))
    return {"withdrawn": True, "training_corpus_uses": 0}


@app.post("/api/tools/{slug}/jobs", status_code=202)
def submit_job(slug: str, p: RunInput, request: Request, u=Depends(identify), db=Depends(db_session)):
    return enqueue_request(slug, p, request, u, db)


def enqueue_request(slug, p, request, u, db, parent=None):
    m = get_mod(slug, db)
    if m.get("enabled") is False:
        raise HTTPException(503, "Tool disabled / টুলটি বন্ধ আছে")
    if not p.consent or p.language not in ["bn", "en"]:
        raise HTTPException(422, "Processing consent and supported language required")
    if len(json.dumps(p.inputs)) > 100000:
        raise HTTPException(413, "Input too large")
    workspace = db.scalar(select(Workspace).where(
        Workspace.user_id == u.id,
        *([Workspace.id == p.workspace_id] if p.workspace_id else [])
    ).limit(1))
    if not workspace:
        raise HTTPException(404, "Workspace not found")
    for aid in p.asset_ids:
        owner_asset(db, u, aid)
    p.workspace_id = workspace.id
    payload = p.model_dump()
    if parent:
        payload["_parent_run_id"] = parent
    return inference_queue.submit(db, u, request.state.session, slug, payload)


@app.get("/api/jobs")
def pending_jobs(u=Depends(identify), db=Depends(db_session)):
    return [inference_queue.view(j) for j in db.scalars(select(inference_queue.InferenceJob).where(
        inference_queue.InferenceJob.user_id == u.id
    ).order_by(inference_queue.InferenceJob.created_at.desc()).limit(100))]


def owner_job(db, u, jid):
    j = db.scalar(select(inference_queue.InferenceJob).where(
        inference_queue.InferenceJob.id == jid, inference_queue.InferenceJob.user_id == u.id
    ))
    if not j:
        raise HTTPException(404)
    return j


@app.get("/api/jobs/{jid}")
def get_job(jid: str, u=Depends(identify), db=Depends(db_session)):
    return inference_queue.view(owner_job(db, u, jid))


@app.post("/api/jobs/{jid}/cancel")
def cancel_job(jid: str, u=Depends(identify), db=Depends(db_session)):
    j = owner_job(db, u, jid)
    from sqlalchemy import update
    db.execute(update(inference_queue.InferenceJob).where(
        inference_queue.InferenceJob.id == j.id,
        inference_queue.InferenceJob.state.in_(["queued", "running"])
    ).values(state="cancelled", encrypted=seal({}), claim_token=None, lease_until=0))
    db.refresh(j)
    return inference_queue.view(j)


@app.post("/api/tools/{slug}/runs", status_code=201)
def create_run(slug: str, p: RunInput, u=Depends(identify), db=Depends(db_session)):
    if inference_queue.enabled():
        raise HTTPException(409, "Use the durable jobs endpoint / queue-তে কাজ জমা দিন")
    return execute(slug, p, u, db)


def execute(slug: str, p: RunInput, u=Depends(identify), db=Depends(db_session)):
    m = get_mod(slug, db)
    if m.get("enabled") is False:
        raise HTTPException(503, "Tool disabled / টুলটি বন্ধ আছে")
    if not p.consent:
        raise HTTPException(
            422, "Explicit processing consent required / স্পষ্ট সম্মতি প্রয়োজন"
        )
    if p.language not in ["bn", "en"]:
        raise HTTPException(422, "Unsupported language")
    if len(json.dumps(p.inputs)) > 100000:
        raise HTTPException(413, "Input too large")
    if p.idempotency_key:
        previous = db.scalar(
            select(Run).where(
                Run.user_id == u.id,
                Run.module == slug,
                Run.idempotency_key == p.idempotency_key,
            )
        )
        if previous:
            return {"id": previous.id, **open_sealed(previous.encrypted)["output"]}
    w = (
        db.scalar(
            select(Workspace).where(
                Workspace.user_id == u.id, Workspace.id == p.workspace_id
            )
        )
        if p.workspace_id
        else db.scalar(select(Workspace).where(Workspace.user_id == u.id))
    )
    if not w:
        raise HTTPException(404, "Workspace not found")
    assets = [owner_asset(db, u, a) for a in p.asset_ids]
    context = {"documents": DOCS}
    if PRODUCTION and any(a.scan_state != "clean" for a in assets):
        raise HTTPException(422, "File has not passed malware scanning")
    if m["engine"] == "rag":
        from .domain import text as required_text

        context["rag"] = retrieve(
            required_text(p.inputs), p.inputs.get("grade"), p.language
        )
    if m["engine"] in ["image_compare", "drain"] and len(assets) == 2:
        context["image_comparison"] = compare_images(*[asset_bytes(a) for a in assets])
    if m["engine"] == "audio" and assets:
        context["audio"] = audio_stats(asset_bytes(assets[0]))
    if m["engine"] == "video" and pose_runtime.availability()["experimental_enabled"]:
        if not 1 <= len(assets) <= 2 or any(a.kind != "mp4" for a in assets):
            raise HTTPException(
                422,
                "Choose one private MP4 and optionally a reference clip / একটি MP4 ও চাইলে একটি reference clip দিন",
            )
        context["pose"] = pose_video.analyze([asset_bytes(a) for a in assets])
    start = time.perf_counter()
    if slug in directories.MODULES:
        output = directories.search(db, slug, p.inputs)
    elif m["engine"] == "reading" and str(p.inputs.get("passage_id", "")).startswith(
        "legacy:"
    ):
        output = reading_reflection(p.inputs)
    elif m["engine"] == "prices" and p.inputs.get("mode") == "basket":
        output = basket_compare(p.inputs)
    else:
        output = process(m["engine"], p.inputs, context)
    output.update(
        {
            "module": slug,
            "language": p.language,
            "created_at": now(),
            "source_as_of": None,
            "full_module_complete": False,
            "advanced_pipeline_status": "not_production_validated",
        }
    )
    output.setdefault("source_kind", "user_confirmed_input")
    output.setdefault("latency_ms", round((time.perf_counter() - start) * 1000, 2))
    payload = p.inputs
    if m["engine"] == "scam":
        payload = {
            "text": output["facts"]["redacted_text"],
            "url_domain": output["facts"]["domain_only"],
        }
    r = Run(
        user_id=u.id,
        workspace_id=w.id,
        module=slug,
        encrypted=seal({"inputs": payload, "output": output, "asset_ids": p.asset_ids}),
        idempotency_key=p.idempotency_key,
    )
    db.add(r)
    db.add(
        Consent(user_id=u.id, module=slug, purpose="service_processing", granted=True)
    )
    db.flush()
    collaboration.link_transfer(db, u, p.transfer_id, slug, w.id, p.inputs, r)
    return {"id": r.id, **output}


@app.get("/api/runs/{rid}")
def get_run(rid: str, u=Depends(identify), db=Depends(db_session)):
    r = owner_run(db, u, rid)
    return {
        "id": r.id,
        "module": r.module,
        "created_at": r.created_at,
        "saved": r.saved,
        **open_sealed(r.encrypted),
    }


@app.patch("/api/runs/{rid}")
def save_run(rid: str, p: Body, u=Depends(identify), db=Depends(db_session)):
    r = owner_run(db, u, rid)
    r.saved = p.value.get("saved") is True
    return {"saved": r.saved}


@app.post("/api/runs/{rid}/correct", status_code=201)
def correction(rid: str, p: RunInput, request: Request, u=Depends(identify), db=Depends(db_session)):
    old = owner_run(db, u, rid)
    p.workspace_id = old.workspace_id
    if inference_queue.enabled():
        return JSONResponse(enqueue_request(old.module, p, request, u, db, old.id), status_code=202)
    response = execute(old.module, p, u, db)
    r = db.get(Run, response["id"])
    r.parent_id = old.id
    return response


@app.delete("/api/runs/{rid}")
def delete_run(rid: str, u=Depends(identify), db=Depends(db_session)):
    r = owner_run(db, u, rid)
    db.delete(r)
    return {"deleted": True}


@app.get("/api/runs/{rid}/export")
def export_run(
    rid: str, format: str = "json", u=Depends(identify), db=Depends(db_session)
):
    r = owner_run(db, u, rid)
    data = {
        "id": r.id,
        "module": r.module,
        "created_at": r.created_at,
        **open_sealed(r.encrypted),
    }
    if format == "json":
        return Response(
            json.dumps(data, ensure_ascii=False, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="mouchak-{rid}.json"'
            },
        )
    if format == "csv":
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["key", "value"])
        for k, v in data["output"]["facts"].items():
            s = str(v)
            writer.writerow(
                [k, "'" + s if s.startswith(("=", "+", "-", "@", "\t", "\r")) else s]
            )
        return Response(
            "\ufeff" + out.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="mouchak-{rid}.csv"'
            },
        )
    if format == "pdf":
        from .pdf_report import report

        return Response(
            report(data),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="mouchak-{rid}.pdf"'
            },
        )
    raise HTTPException(422, "Choose json, csv or pdf")


@app.post("/api/upload", status_code=201)
async def upload(
    request: Request,
    file: UploadFile = File(...),
    consent: bool = Form(...),
    u=Depends(identify),
    db=Depends(db_session),
):
    if not consent:
        raise HTTPException(422, "Processing consent required")
    data = await file.read(10 * 1024 * 1024 + 1)
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(413, "10 MB limit / সর্বোচ্চ ১০ MB")
    return persist_asset(data, u, db)


def persist_asset(data, u, db):
    db.scalar(select(User.id).where(User.id == u.id).with_for_update())
    total = db.scalar(
        select(func.coalesce(func.sum(Asset.size), 0)).where(Asset.user_id == u.id)
    )
    if total + len(data) > 50 * 1024 * 1024:
        raise HTTPException(
            429, "Private vault limit reached / ব্যক্তিগত ফাইলের সীমা শেষ"
        )
    kind = (
        "pdf"
        if data.startswith(b"%PDF-")
        else (
            "png"
            if data.startswith(b"\x89PNG\r\n\x1a\n")
            else (
                "jpeg"
                if data.startswith(b"\xff\xd8\xff")
                else (
                    "wav"
                    if data.startswith(b"RIFF") and data[8:12] == b"WAVE"
                    else None
                )
            )
        )
    )
    if len(data) >= 16 and data[4:8] == b"ftyp":
        if not pose_runtime.availability()["experimental_enabled"]:
            raise HTTPException(
                503,
                "Experimental pose uploads are disabled; production validation pending",
            )
        pose_video.validate_upload(data)
        kind = "mp4"
    if not kind:
        raise HTTPException(
            422,
            "Only PNG, JPEG, PDF or PCM WAV by file signature / PNG, JPEG, PDF বা PCM WAV দিন",
        )
    if kind in ["png", "jpeg"]:
        from PIL import Image

        try:
            with Image.open(io.BytesIO(data)) as im:
                if im.width * im.height > 24000000:
                    raise HTTPException(422, "Image too large")
                im.verify()
        except Exception:
            raise HTTPException(422, "Invalid image or excessive resolution")
    scan = "unscanned_development"
    if shutil.which("clamscan"):
        import tempfile

        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(data)
            tmp.flush()
            r = subprocess.run(
                ["clamscan", "--no-summary", tmp.name], capture_output=True, timeout=30
            )
            if r.returncode != 0:
                raise HTTPException(422, "Malware scan did not pass")
            scan = "clean"
    elif PRODUCTION:
        raise HTTPException(503, "Malware scanning service unavailable; upload blocked")
    aid = uid()
    path = storage.put(aid, data)
    a = Asset(
        id=aid,
        user_id=u.id,
        kind=kind,
        size=len(data),
        checksum=hashlib.sha256(data).hexdigest(),
        path=str(path),
        scan_state=scan,
    )
    db.add(a)
    return {
        "id": aid,
        "kind": kind,
        "bytes": len(data),
        "scan_state": scan,
        "original_filename_stored": False,
    }


@app.get("/api/assets")
def assets(u=Depends(identify), db=Depends(db_session)):
    return [
        {
            "id": a.id,
            "kind": a.kind,
            "size": a.size,
            "scan_state": a.scan_state,
            "created_at": a.created_at,
        }
        for a in db.scalars(select(Asset).where(Asset.user_id == u.id))
    ]


@app.get("/api/assets/{aid}")
def download_asset(aid: str, u=Depends(identify), db=Depends(db_session)):
    a = owner_asset(db, u, aid)
    return Response(
        asset_bytes(a),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="private-{a.id}.{a.kind}"'
        },
    )


@app.delete("/api/assets/{aid}")
def delete_asset(aid: str, u=Depends(identify), db=Depends(db_session)):
    a = owner_asset(db, u, aid)
    storage.remove(a.path)
    db.delete(a)
    return {"deleted": True}


@app.post("/api/assets/{aid}/ocr")
def extract(aid: str, u=Depends(identify), db=Depends(db_session)):
    a = owner_asset(db, u, aid)
    if a.kind == "wav":
        raise HTTPException(422, "Use text or document input; ASR is unavailable")
    if PRODUCTION and a.scan_state != "clean":
        raise HTTPException(422, "File not scanned")
    return ocr(asset_bytes(a), a.kind)


@app.get("/api/privacy/export")
def account_export(u=Depends(identify), db=Depends(db_session)):
    data = {
        "scope": {
            "mode": "anonymous" if u.role == "guest" else "operator",
            "profile_collected": False,
        },
        "runs": [
            {"id": r.id, "module": r.module, **open_sealed(r.encrypted)}
            for r in db.scalars(select(Run).where(Run.user_id == u.id))
        ],
        "consents": consents(u, db),
        "retail": retail.export_owned_stock(db, u),
        "collaboration": collaboration.export_owned(db, u),
        "notifications": notifications(u, db),
        "feedback": [
            {"id": f.id, "text": open_sealed(f.body), "created_at": f.created_at}
            for f in db.scalars(select(Feedback).where(Feedback.user_id == u.id))
        ],
        "assets": assets(u, db),
        "inference_jobs": pending_jobs(u, db),
        "bill_history": [bills.entry_view(r) for r in db.scalars(select(bills.BillEntry).where(bills.BillEntry.user_id == u.id))],
        "bill_model_cards": [open_sealed(r.encrypted)["card"] for r in db.scalars(select(bills.BillModel).where(bills.BillModel.user_id == u.id))],
        "pending_processing_inputs": [
            {"id": j.id, "request": open_sealed(j.encrypted)} for j in db.scalars(
                select(inference_queue.InferenceJob).where(
                    inference_queue.InferenceJob.user_id == u.id,
                    inference_queue.InferenceJob.state.in_(["queued", "running"])
                )
            )
        ],
    }
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": 'attachment; filename="mouchak-private-export.json"'
        },
    )


@app.delete("/api/privacy/account")
def delete_account(
    p: Body, response: Response, u=Depends(identify), db=Depends(db_session)
):
    try:
        valid = PH.verify(u.password, str(p.value.get("password", "")))
    except VerificationError:
        valid = False
    if not valid:
        raise HTTPException(401, "Password required for deletion")
    for a in db.scalars(select(Asset).where(Asset.user_id == u.id)):
        storage.remove(a.path)
    for f in db.scalars(select(Feedback).where(Feedback.user_id == u.id)):
        status = db.get(Config, "feedback-status:" + f.id)
        if status:
            db.delete(status)
    for table in [
        Run,
        Asset,
        Consent,
        Session,
        Token,
        Workspace,
        Feedback,
        Notification,
    ]:
        db.execute(delete(table).where(table.user_id == u.id))
    for conf in db.scalars(select(Config).where(Config.key.like("mfa-replay:" + u.id))):
        db.delete(conf)
    db.delete(u)
    response.delete_cookie("mouchak_session", path="/")
    return {
        "deleted": True,
        "backup_retention_notice": "Operator-managed encrypted backups require separate retention expiry.",
    }


@app.get("/api/notifications")
def notifications(u=Depends(identify), db=Depends(db_session)):
    return [
        {"id": n.id, "body": n.body, "read": n.read, "created_at": n.created_at}
        for n in db.scalars(select(Notification).where(Notification.user_id == u.id))
    ]


@app.post("/api/feedback", status_code=201)
def feedback(p: Body, u=Depends(identify), db=Depends(db_session)):
    body = str(p.value.get("text", "")).strip()
    if not body or len(body) > 2000:
        raise HTTPException(422)
    f = Feedback(user_id=u.id, body=seal(body))
    db.add(f)
    db.flush()
    return {"id": f.id}


@app.get("/api/admin/overview")
def overview(u=Depends(authorize("overview")), db=Depends(db_session)):
    # Counts only, no private record content or individual behavioral analytics.
    return {
        "registered_tools": 50,
        "full_modules_production_validated": 0,
        "users": db.scalar(select(func.count()).select_from(User)),
        "records": db.scalar(select(func.count()).select_from(Run)),
        "sources": db.scalar(select(func.count()).select_from(Source)),
        "jobs": db.scalar(select(func.count()).select_from(Job)),
        "models": model_health(),
        "production_ready": False,
    }


@app.get("/api/admin/modules")
def admin_modules(u=Depends(authorize("modules")), db=Depends(db_session)):
    return [get_mod(x, db) for x in MODULES]


@app.patch("/api/admin/modules/{slug}")
def edit_module(
    slug: str, p: Body, u=Depends(authorize("modules")), db=Depends(db_session)
):
    get_mod(slug, db)
    allowed = {
        "enabled",
        "name",
        "description_en",
        "description_bn",
        "quota",
        "retention_days",
    }
    if set(p.value) - allowed:
        raise HTTPException(422, "Unsupported editable fields")
    if "enabled" in p.value and not isinstance(p.value["enabled"], bool):
        raise HTTPException(422)
    if "retention_days" in p.value and not 1 <= int(p.value["retention_days"]) <= 365:
        raise HTTPException(422)
    k = "module:" + slug
    conf = db.get(Config, k)
    value = json.loads(conf.value) if conf else {}
    value.update(p.value)
    if conf:
        conf.value = json.dumps(value, ensure_ascii=False)
    else:
        db.add(Config(key=k, value=json.dumps(value, ensure_ascii=False)))
    audit(db, u.id, "module_updated", slug, {"fields": list(p.value)})
    return get_mod(slug, db)


@app.get("/api/admin/users")
def users(u=Depends(authorize("users")), db=Depends(db_session)):
    return [
        view_user(x)
        for x in db.scalars(select(User).where(User.role.in_(PRIVILEGED)).limit(200))
    ]


@app.patch("/api/admin/users/{uid}")
def user_admin(
    uid: str, p: Body, u=Depends(authorize("users")), db=Depends(db_session)
):
    other = db.get(User, uid)
    if not other:
        raise HTTPException(404)
    if other.id == u.id:
        raise HTTPException(422, "Cannot revoke your own administrative access")
    role = p.value.get("role", other.role)
    if role not in ROLES:
        raise HTTPException(422)
    other.role = role
    if "banned" in p.value:
        other.banned = p.value["banned"] is True
    db.execute(delete(Session).where(Session.user_id == other.id))
    audit(
        db, u.id, "account_access_updated", uid, {"role": role, "banned": other.banned}
    )
    return view_user(other)


@app.get("/api/admin/cms")
def cms_list(u=Depends(authorize("cms")), db=Depends(db_session)):
    return [
        {
            "id": v.id,
            "page": v.page,
            "status": v.status,
            "created_at": v.created_at,
            "author": v.author,
            "body": json.loads(v.body),
        }
        for v in db.scalars(
            select(CMSVersion).order_by(CMSVersion.created_at.desc()).limit(200)
        )
    ]


@app.post("/api/admin/cms", status_code=201)
def cms_draft(p: Body, u=Depends(authorize("cms")), db=Depends(db_session)):
    page = str(p.value.get("page", ""))
    body = p.value.get("body")
    if (
        not re.fullmatch(r"[a-z0-9_/-]{1,120}", page)
        or not isinstance(body, dict)
        or len(json.dumps(body)) > 60000
    ):
        raise HTTPException(422, "Invalid page body")
    # CMS is plain structured text. No executable HTML/SVG/scripts.
    if re.search(
        r"<\s*(script|iframe|svg|object|embed)|javascript:", json.dumps(body), re.I
    ):
        raise HTTPException(422, "Executable content is prohibited")
    v = CMSVersion(page=page, body=json.dumps(body, ensure_ascii=False), author=u.id)
    db.add(v)
    db.flush()
    audit(db, u.id, "cms_draft", v.id, {"page": page})
    return {"id": v.id, "status": "draft"}


@app.post("/api/admin/cms/{vid}/publish")
def publish(vid: str, u=Depends(authorize("cms")), db=Depends(db_session)):
    v = db.get(CMSVersion, vid)
    if not v:
        raise HTTPException(404)
    conf = db.scalar(
        select(Config).where(Config.key == "cms:" + v.page).with_for_update()
    )
    if conf:
        conf.value = v.body
    else:
        db.add(Config(key="cms:" + v.page, value=v.body))
    v.status = "published"
    audit(db, u.id, "cms_published", vid, {"page": v.page})
    return {"published": True, "version": vid}


@app.get("/api/admin/sources")
def admin_sources(u=Depends(authorize("sources")), db=Depends(db_session)):
    return [
        {
            "id": s.id,
            "module": s.module,
            "state": s.state,
            "evidence": s.evidence,
            "reviewer": s.reviewer,
            **json.loads(s.metadata_json),
        }
        for s in db.scalars(select(Source))
    ]


@app.patch("/api/admin/sources/{sid}")
def review_source(
    sid: str, p: Body, u=Depends(authorize("sources")), db=Depends(db_session)
):
    s = db.get(Source, sid)
    if not s:
        raise HTTPException(404)
    state = p.value.get("state")
    evidence = p.value.get("evidence")
    allowed = [
        "candidate",
        "access_review",
        "rights_review",
        "approved_reference_only",
        "approved_train_and_reuse",
        "quarantined",
        "revoked",
    ]
    if state not in allowed:
        raise HTTPException(422, "Invalid review state")
    if state.startswith("approved") and (
        not isinstance(evidence, str) or len(evidence) < 30
    ):
        raise HTTPException(
            422, "Document asset-level rights, license, scope and reviewer evidence"
        )
    high = MODULES[s.module]["category"] in ["health", "civic", "consumer"]
    if high and state == "approved_train_and_reuse":
        raise HTTPException(
            422,
            "Use independent asset reviews for high-sensitivity training approval; this single-review endpoint cannot approve it",
        )
    if state in ["revoked", "quarantined"]:
        operations.rights_round(db, sid, True)
    s.state = state
    s.evidence = evidence
    s.reviewer = u.id
    audit(db, u.id, "source_review", sid, {"state": state})
    return {"id": sid, "state": state}


@app.get("/api/admin/models")
def models(u=Depends(authorize("models"))):
    return {
        "runtime": model_health(),
        "candidates": json.loads(
            (ROOT / "packages/module-registry/model-candidates.json").read_text()
        )["models"],
        "production_validated_modules": 0,
    }


@app.post("/api/admin/datasets/import/dry-run", status_code=201)
def import_dry_run(p: Body, u=Depends(authorize("jobs")), db=Depends(db_session)):
    sid = str(p.value.get("source_id", ""))
    s = db.get(Source, sid)
    if not s or s.state != "approved_train_and_reuse":
        raise HTTPException(422, "Source must be approved for ingestion and reuse")
    raw = str(p.value.get("csv", ""))
    if len(raw) > 100000:
        raise HTTPException(413)
    try:
        reader = csv.DictReader(io.StringIO(raw.lstrip("\ufeff")))
        data = list(reader)
    except csv.Error:
        raise HTTPException(422, "Malformed CSV")
    if not data or len(data) > 200 or not reader.fieldnames:
        raise HTTPException(422, "CSV must contain 1–200 rows and named headers")
    if len(set(reader.fieldnames)) != len(reader.fieldnames) or any(
        not x for x in reader.fieldnames
    ):
        raise HTTPException(422, "Headers must be unique and nonempty")
    if any(None in row or None in row.values() for row in data):
        raise HTTPException(422, "CSV row width does not match headers")
    if any(
        re.search(r"phone|nid|passport|patient|child|password|token", x, re.I)
        for x in reader.fieldnames
    ):
        raise HTTPException(
            422, "Sensitive identifiers must not be imported into shared datasets"
        )
    duplicates = len(data) - len({json.dumps(x, sort_keys=True) for x in data})
    j = Job(
        source_id=sid,
        owner=u.id,
        payload=seal(
            {
                "rows": data,
                "source_snapshot": {"state": s.state, "evidence": s.evidence},
            }
        ),
        checksum=digest(raw),
    )
    db.add(j)
    db.flush()
    audit(
        db, u.id, "dataset_dry_run", j.id, {"rows": len(data), "duplicates": duplicates}
    )
    return {
        "job_id": j.id,
        "rows": len(data),
        "duplicates": duplicates,
        "preview": data[:5],
        "ingested": False,
    }


@app.post("/api/admin/datasets/import/{jid}/approve")
def import_approve(jid: str, u=Depends(authorize("jobs")), db=Depends(db_session)):
    j = db.get(Job, jid)
    if not j or j.state != "dry_run":
        raise HTTPException(422)
    s = db.get(Source, j.source_id)
    if not s or s.state != "approved_train_and_reuse":
        raise HTTPException(422, "Rights changed; import blocked")
    j.state = "approved_staged"
    audit(db, u.id, "dataset_staged", jid, {"source": j.source_id})
    return {
        "state": j.state,
        "publicly_indexed": False,
        "reason": "Schema-specific publication and evaluation remain a separate release gate",
    }


@app.post("/api/admin/datasets/import/{jid}/rollback")
def rollback_import(jid: str, u=Depends(authorize("jobs")), db=Depends(db_session)):
    j = db.get(Job, jid)
    if not j:
        raise HTTPException(404)
    if j.state.startswith("directory_"):
        raise HTTPException(409, "Use directory withdrawal or publish a retired reviewed revision")
    j.state = "rolled_back"
    j.payload = seal({"removed": True})
    audit(db, u.id, "dataset_rollback", jid)
    return {"rolled_back": True}


@app.get("/api/admin/jobs")
def jobs(u=Depends(authorize("jobs")), db=Depends(db_session)):
    return [
        {
            "id": j.id,
            "source_id": j.source_id,
            "state": j.state,
            "created_at": j.created_at,
            "checksum": j.checksum,
        }
        for j in db.scalars(select(Job).limit(200))
    ]


@app.get("/api/admin/audit")
def audit_list(u=Depends(authorize("audit")), db=Depends(db_session)):
    return [
        {
            "id": a.id,
            "actor": a.actor,
            "action": a.action,
            "target": a.target,
            "detail": json.loads(a.detail),
            "previous_hash": a.previous_hash,
            "event_hash": a.event_hash,
            "created_at": a.created_at,
        }
        for a in db.scalars(select(Audit).order_by(Audit.created_at.desc()).limit(300))
    ]


@app.post("/api/assets/{aid}/transcribe")
def speech(aid: str, p: Body, u=Depends(identify), db=Depends(db_session)):
    from .inference import transcribe

    a = owner_asset(db, u, aid)
    if a.kind != "wav":
        raise HTTPException(422, "PCM WAV required")
    if p.value.get("adult_consent") is not True:
        raise HTTPException(
            422, "Adult recording consent required; child audio is not enabled"
        )
    if PRODUCTION:
        raise HTTPException(
            503, "Bangla speech has not passed the production evaluation gate"
        )
    return transcribe(asset_bytes(a), str(p.value.get("language", "bn")))


@app.post("/api/personal/anomalies")
def anomalies(p: Body, u=Depends(identify)):
    from .inference import personal_anomalies

    if p.value.get("confirmed_private_baseline") is not True:
        raise HTTPException(422, "Confirmed private baseline consent required")
    if PRODUCTION:
        raise HTTPException(
            503,
            "The personal anomaly adapter is experimental and not released for production",
        )
    values = p.value.get("values")
    if not isinstance(values, list):
        raise HTTPException(422)
    try:
        return personal_anomalies(values)
    except (TypeError, ValueError):
        raise HTTPException(422, "Invalid measurements / মাপ সঠিক নয়")
