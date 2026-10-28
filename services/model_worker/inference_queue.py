"""Durable, encrypted inference with leases and fenced publication.

Inference may execute more than once after a crash; only the current lease can
commit a result. This queue is for local model/calculation calls without external
side effects. It must not be used for payments, messages or provider mutations.
"""

import hashlib, json, os, secrets, signal, subprocess, sys, threading, time
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, Index, select, update, or_, and_, text
from sqlalchemy.orm import Mapped, mapped_column, load_only
from fastapi import HTTPException
from .store import Base, DB, User, Session, Run, seal, open_sealed, uid, PRODUCTION

LEASE_SECONDS = 300
MAX_ATTEMPTS = 3


class InferenceJob(Base):
    __tablename__ = "inference_jobs"
    __table_args__ = (UniqueConstraint("user_id", "module", "request_key", name="uq_inference_request"),
                      Index("ix_inference_claim", "state", "lease_until", "created_at"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    module: Mapped[str] = mapped_column(String)
    request_key: Mapped[str] = mapped_column(String)
    fingerprint: Mapped[str] = mapped_column(String(64))
    encrypted: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String, index=True, default="queued")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    claim_token: Mapped[str | None] = mapped_column(String, nullable=True)
    lease_until: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[int] = mapped_column(Integer, index=True)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("tool_runs.id", ondelete="SET NULL"), nullable=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True)


def enabled():
    return os.getenv("ENABLE_DURABLE_INFERENCE", "0") == "1"


def clock(db):
    if db.bind.dialect.name == "postgresql":
        return int(db.scalar(text("SELECT EXTRACT(EPOCH FROM clock_timestamp())")))
    return int(time.time())


def view(job):
    # Never return inputs, encrypted payloads, session identifiers or lease tokens.
    return {"id": job.id, "module": job.module, "state": job.state,
            "run_id": job.run_id, "error": job.error, "expires_at": job.expires_at}


def submit(db, u, session, module, payload):
    if not enabled():
        raise HTTPException(503, "Queued processing unavailable / queue সেবা পাওয়া যাচ্ছে না")
    request_key = payload.get("idempotency_key")
    if not request_key:
        raise HTTPException(422, "An idempotency key is required")
    fingerprint = hashlib.sha256(json.dumps(
        {k: v for k, v in payload.items() if k != "idempotency_key"},
        sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode()).hexdigest()
    db.scalar(select(User.id).where(User.id == u.id).with_for_update())
    existing = db.scalar(select(InferenceJob).where(
        InferenceJob.user_id == u.id, InferenceJob.module == module, InferenceJob.request_key == request_key
    ))
    if existing:
        if existing.fingerprint != fingerprint:
            raise HTTPException(409, "This request key belongs to different input")
        return view(existing)
    active = db.scalar(select(InferenceJob.id).where(
        InferenceJob.user_id == u.id, InferenceJob.state.in_(["queued", "running"])
    ).offset(1).limit(1))
    if active:
        raise HTTPException(429, "Two jobs are already pending / দুটি কাজ চলমান আছে")
    at = clock(db)
    job = InferenceJob(user_id=u.id, session_id=session.id, module=module,
                       request_key=request_key, fingerprint=fingerprint,
                       encrypted=seal(payload), created_at=at,
                       expires_at=min(at + 900, session.expires))
    db.add(job)
    db.flush()
    return view(job)


def verify_role(db):
    if PRODUCTION and db.scalar(text("SELECT current_user")) != "mouchak_inference":
        raise RuntimeError("Production inference requires dedicated mouchak_inference role")


def claim(factory=DB):
    with factory.begin() as db:
        verify_role(db)
        at = clock(db)
        # Bounded reaping, including jobs whose final worker died before publishing.
        exhausted = list(db.scalars(select(InferenceJob.id).where(
            InferenceJob.state.in_(["queued", "running"]),
            or_(InferenceJob.expires_at <= at,
                and_(InferenceJob.attempts >= MAX_ATTEMPTS, InferenceJob.lease_until <= at))
        ).with_for_update(skip_locked=True).limit(100)))
        if exhausted:
            db.execute(update(InferenceJob).where(InferenceJob.id.in_(exhausted)).values(
                state="failed", error="Processing expired / কাজের মেয়াদ শেষ",
                encrypted=seal({}), claim_token=None, lease_until=0))
        candidate = db.scalar(select(InferenceJob).where(
            InferenceJob.expires_at > at, InferenceJob.attempts < MAX_ATTEMPTS,
            or_(InferenceJob.state == "queued", and_(InferenceJob.state == "running", InferenceJob.lease_until <= at))
        ).order_by(InferenceJob.created_at, InferenceJob.id).with_for_update(skip_locked=True).limit(1))
        if not candidate:
            return None
        token = secrets.token_hex(24)
        result = db.execute(update(InferenceJob).where(
            InferenceJob.id == candidate.id,
            InferenceJob.state.in_(["queued", "running"]), InferenceJob.lease_until <= at
        ).values(state="running", attempts=InferenceJob.attempts + 1,
                 claim_token=token, lease_until=at + LEASE_SECONDS))
        if result.rowcount != 1:
            return None
        return {"id": candidate.id, "token": token}


class LostLease(Exception):
    pass


def active_owner(db, job):
    u = db.scalar(select(User).options(load_only(User.id, User.role, User.banned, User.verified)).where(User.id == job.user_id).execution_options(populate_existing=True))
    s = db.get(Session, job.session_id, populate_existing=True, options=[load_only(Session.id, Session.user_id, Session.expires, Session.last_seen)])
    at = clock(db)
    if (not u or u.banned or not s or s.user_id != job.user_id or s.expires <= at
        or (u.role != "guest" and (at - s.last_seen > 1800 or (PRODUCTION and not u.verified)))):
        raise HTTPException(401, "Processing session expired / সেশনের মেয়াদ শেষ")
    return u


def publish_claim(claimed, factory=DB):
    """All writes, including run/consent/transfer, commit with the lease fence."""
    from .main import RunInput, execute, owner_run
    job_id, token = claimed["id"], claimed["token"]
    try:
        with factory.begin() as db:
            verify_role(db)
            job = db.get(InferenceJob, job_id)
            if not job or job.state != "running" or job.claim_token != token or job.lease_until <= clock(db):
                return False
            if db.bind.dialect.name == "postgresql":
                db.execute(text("SELECT set_config('app.user_id', :uid, true)"), {"uid": job.user_id})
            user = active_owner(db, job)
            payload = open_sealed(job.encrypted)
            parent = payload.pop("_parent_run_id", None)
            p = RunInput(**payload)
            p.idempotency_key = "job:" + job.id
            output = execute(job.module, p, user, db)
            if parent:
                old = owner_run(db, user, parent)
                db.get(Run, output["id"]).parent_id = old.id
                db.flush()
            active_owner(db, job)  # Clearing/revocation/expiry must not publish later.
            at = clock(db)
            final = db.execute(update(InferenceJob).where(
                InferenceJob.id == job_id, InferenceJob.state == "running",
                InferenceJob.claim_token == token, InferenceJob.lease_until > at,
                InferenceJob.expires_at > at
            ).values(state="succeeded", run_id=output["id"], encrypted=seal({}),
                     claim_token=None, lease_until=0))
            if final.rowcount != 1:
                raise LostLease()
        return True
    except LostLease:
        return False
    except Exception as error:
        # Do not persist exception text: model/SQL errors can contain private data.
        message = ("Input rejected / ইনপুট গ্রহণ করা যায়নি"
                   if isinstance(error, HTTPException) and error.status_code < 500
                   else "Processing unavailable / প্রসেসিং সেবা পাওয়া যাচ্ছে না")
        with factory.begin() as db:
            verify_role(db)
            db.execute(update(InferenceJob).where(
                InferenceJob.id == job_id, InferenceJob.state == "running", InferenceJob.claim_token == token
            ).values(state="failed", error=message, encrypted=seal({}), claim_token=None, lease_until=0))
        return False


def main():
    if "--execute-claim" in sys.argv:
        publish_claim(json.loads(sys.stdin.read(512)))
        return
    if not enabled():
        raise SystemExit("ENABLE_DURABLE_INFERENCE=1 is required")
    # Import every additive table before development migrations.
    from . import main as application
    if not PRODUCTION:
        application.migrate()
    with DB() as db:
        verify_role(db)
    stop = threading.Event()
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, lambda *_: stop.set())
    while not stop.is_set():
        try:
            claimed = claim()
            if claimed:
                try:
                    # Child termination rolls back its DB transaction. Expired leases retry.
                    subprocess.run([sys.executable, "-m", __package__ + ".inference_worker", "--execute-claim"],
                                   input=json.dumps(claimed), text=True, timeout=240,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    print(json.dumps({"inference_attempt": "finished"}), flush=True)
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    print(json.dumps({"inference_attempt": "interrupted", "recovery": "lease_expiry"}), flush=True)
            else:
                stop.wait(2)
        except Exception:
            print(json.dumps({"inference_poll": "failed"}), flush=True)
            stop.wait(5)

