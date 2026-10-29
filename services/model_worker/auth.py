import hashlib, secrets, time, os, hmac, base64, struct, smtplib, json
from email.message import EmailMessage
from fastapi import HTTPException, Request, Depends
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from sqlalchemy import select, delete
from .store import DB, User, Session, Token, Audit, seal, open_sealed, now, PRODUCTION

PH = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
ROLES = {
    "guest",
    "user",
    "guardian",
    "organization_staff",
    "content_editor",
    "dataset_reviewer",
    "model_operator",
    "support_agent",
    "module_manager",
    "auditor",
    "super_admin",
}
PRIVILEGED = ROLES - {"guest", "user", "guardian", "organization_staff"}
PERMISSIONS = {
    "cms": {"content_editor", "super_admin"},
    "sources": {"dataset_reviewer", "super_admin"},
    "models": {"model_operator", "super_admin"},
    "modules": {"module_manager", "super_admin"},
    "audit": {"auditor", "super_admin"},
    "users": {"super_admin"},
    "jobs": {"dataset_reviewer", "super_admin"},
    "overview": PRIVILEGED,
    "support": {"support_agent", "super_admin"},
    "operations": {"super_admin"},
}


def digest(s):
    return hashlib.sha256(s.encode()).hexdigest()


def db_session():
    # Every API binding uses Depends(..., scope="function"): commit/rollback
    # must finish before response.start, including cookie and rights writes.
    with DB() as db:
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise


def password_valid(s):
    if len(s) < 12 or len(s) > 256:
        raise HTTPException(
            422, "Password must be 12–256 characters / পাসওয়ার্ড ১২–২৫৬ অক্ষর হতে হবে"
        )


def identify(request: Request, db=Depends(db_session, scope="function")):
    raw = request.cookies.get("mouchak_session", "")
    s = db.get(Session, digest(raw)) if raw else None
    ts = int(time.time())
    if not s or s.expires <= ts:
        raise HTTPException(401, "Session expired / সেশনের মেয়াদ শেষ")
    u = db.get(User, s.user_id)
    if not u or u.banned or (PRODUCTION and u.role != "guest" and not u.verified):
        raise HTTPException(401, "Session unavailable / সেশন পাওয়া যাচ্ছে না")
    if u.role != "guest" and ts - s.last_seen > 1800:
        raise HTTPException(
            401, "Operator session expired / প্রশাসনিক সেশনের মেয়াদ শেষ"
        )
    if request.method not in ["GET", "HEAD", "OPTIONS"] and not hmac.compare_digest(
        request.headers.get("x-csrf-token", "").encode("utf-8"), s.csrf.encode("utf-8")
    ):
        raise HTTPException(403, "Invalid CSRF token / নিরাপত্তা টোকেন ভুল")
    s.last_seen = ts
    request.state.session = s
    if db.bind.dialect.name == "postgresql":
        from sqlalchemy import text

        db.execute(text("SELECT set_config('app.user_id', :uid, true)"), {"uid": u.id})
        db.execute(
            text("SELECT set_config('app.mfa_until', :expires, true)"),
            {"expires": str(s.mfa_until if u.mfa_enabled else 0)},
        )
    return u


def authorize(permission):
    def check(request: Request, u=Depends(identify)):
        if u.role not in PERMISSIONS.get(permission, set()):
            raise HTTPException(403, "Permission denied / অনুমতি নেই")
        if not u.mfa_enabled or request.state.session.mfa_until < int(time.time()):
            raise HTTPException(403, "MFA_REQUIRED")
        return u

    return check


def new_session(db, u, request, response, anonymous=False, ttl=86400):
    raw = secrets.token_urlsafe(40)
    csrf = secrets.token_urlsafe(32)
    t = int(time.time())
    s = Session(
        id=digest(raw),
        user_id=u.id,
        csrf=csrf,
        expires=t + ttl,
        last_seen=t,
        device=(
            "anonymous browser"
            if anonymous
            else request.headers.get("user-agent", "unknown")[:180]
        ),
    )
    db.add(s)
    request.state.session = s
    response.set_cookie(
        "mouchak_session",
        raw,
        httponly=True,
        secure=PRODUCTION,
        samesite="strict",
        max_age=ttl,
        path="/",
    )
    return csrf


def totp(secret, at=None):
    key = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
    msg = struct.pack(">Q", int((at or time.time()) // 30))
    mac = hmac.new(key, msg, hashlib.sha1).digest()
    i = mac[-1] & 15
    return f'{(struct.unpack(">I",mac[i:i+4])[0]&0x7fffffff)%1000000:06d}'


def canonical_totp(code):
    return code.translate(str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789"))


def valid_totp(secret, code):
    # Bengali/ASCII digits represent the same six-digit authenticator code.
    # All other input is refused before compare_digest's ASCII string boundary.
    code = canonical_totp(code)
    return len(code) == 6 and code.isascii() and code.isdigit() and any(
        hmac.compare_digest(totp(secret, time.time() + x * 30), code)
        for x in [-1, 0, 1]
    )


def audit(db, actor, action, target, detail=None):
    # Do not include private records, secrets or auth token content in the audit.
    if db.bind.dialect.name == "postgresql":
        from sqlalchemy import text

        db.execute(text("SELECT pg_advisory_xact_lock(742001)"))
    previous = db.scalars(
        select(Audit).order_by(Audit.created_at.desc(), Audit.id.desc()).limit(1)
    ).first()
    prev = previous.event_hash if previous else "0" * 64
    ts = now()
    d = json.dumps(detail or {}, sort_keys=True)
    value = digest("|".join([prev, actor, action, target, d, ts]))
    db.add(
        Audit(
            actor=actor,
            action=action,
            target=target,
            detail=d,
            previous_hash=prev,
            event_hash=value,
            created_at=ts,
        )
    )


def send_token(db, u, purpose):
    raw = secrets.token_urlsafe(40)
    db.add(
        Token(
            id=digest(raw),
            user_id=u.id,
            purpose=purpose,
            expires=int(time.time()) + 1800,
        )
    )
    origin = os.getenv("PUBLIC_ORIGIN", "http://localhost:3000")
    link = f'{origin}/admin/{"verify" if purpose=="verify" else "reset"}?token={raw}'
    host = os.getenv("SMTP_HOST")
    if not host:
        if not PRODUCTION:
            from .store import STATE

            p = STATE / "development-mail"
            p.mkdir(exist_ok=True)
            (p / (digest(raw) + ".json")).write_text(
                json.dumps({"to": u.email, "purpose": purpose, "link": link})
            )
            (p / (digest(raw) + ".json")).chmod(0o600)
        return False
    msg = EmailMessage()
    msg["To"] = u.email
    msg["From"] = os.environ["SMTP_FROM"]
    msg["Subject"] = "Mouchak AI account verification"
    msg.set_content(link)
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=10) as smtp:
        smtp.starttls()
        if os.getenv("SMTP_USERNAME"):
            smtp.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)
    return True
