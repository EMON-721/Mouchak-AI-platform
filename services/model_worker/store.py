from pathlib import Path
from datetime import datetime, timezone
import os, json, uuid
from sqlalchemy import create_engine, String, Text, Integer, Boolean, ForeignKey, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parents[2]
STATE = Path(os.getenv("MOUCHAK_STATE_DIR", ROOT / ".state"))
STATE.mkdir(exist_ok=True, parents=True)
PRODUCTION = os.getenv("MOUCHAK_ENV") == "production"
url = os.getenv("DATABASE_URL", f"sqlite:///{STATE}/development.db")
if PRODUCTION and (
    not url.startswith("postgresql") or not os.getenv("DATA_ENCRYPTION_KEY")
):
    raise RuntimeError("Production requires PostgreSQL and DATA_ENCRYPTION_KEY")
key = os.getenv("DATA_ENCRYPTION_KEY")
if not key:
    path = STATE / "encryption.key"
    if not path.exists():
        path.write_bytes(Fernet.generate_key())
        path.chmod(0o600)
    key = path.read_text()
CIPHER = Fernet(key.encode())
engine = create_engine(
    url,
    connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
    pool_pre_ping=True,
)
if url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def pragmas(conn, record):
        conn.execute("PRAGMA foreign_keys=ON")


DB = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def uid():
    return str(uuid.uuid4())


def now():
    return datetime.now(timezone.utc).isoformat()


def seal(value):
    return CIPHER.encrypt(json.dumps(value, ensure_ascii=False).encode()).decode()


def open_sealed(value):
    return json.loads(CIPHER.decrypt(value.encode()))


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="user")
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    banned: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String, default="bn")
    mfa_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    csrf: Mapped[str] = mapped_column(String)
    expires: Mapped[int] = mapped_column(Integer)
    last_seen: Mapped[int] = mapped_column(Integer)
    mfa_until: Mapped[int] = mapped_column(Integer, default=0)
    device: Mapped[str] = mapped_column(String)


class Token(Base):
    __tablename__ = "auth_tokens"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    purpose: Mapped[str] = mapped_column(String)
    expires: Mapped[int] = mapped_column(Integer)


class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String)


class Run(Base):
    __tablename__ = "tool_runs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    module: Mapped[str] = mapped_column(String, index=True)
    encrypted: Mapped[str] = mapped_column(Text)
    parent_id: Mapped[str | None] = mapped_column(String, nullable=True)
    saved: Mapped[bool] = mapped_column(Boolean, default=False)
    idempotency_key: Mapped[str | None] = mapped_column(
        String, nullable=True, index=True
    )
    created_at: Mapped[str] = mapped_column(String, default=now)


class Asset(Base):
    __tablename__ = "private_assets"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String)
    size: Mapped[int] = mapped_column(Integer)
    checksum: Mapped[str] = mapped_column(String)
    path: Mapped[str] = mapped_column(String)
    scan_state: Mapped[str] = mapped_column(String, default="quarantined")
    created_at: Mapped[str] = mapped_column(String, default=now)


class Consent(Base):
    __tablename__ = "user_consents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    module: Mapped[str] = mapped_column(String)
    purpose: Mapped[str] = mapped_column(String)
    granted: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Config(Base):
    __tablename__ = "configuration"
    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(Text)


class CMSVersion(Base):
    __tablename__ = "cms_versions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    page: Mapped[str] = mapped_column(String, index=True)
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="draft")
    author: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Audit(Base):
    __tablename__ = "admin_audit_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    actor: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    target: Mapped[str] = mapped_column(String)
    detail: Mapped[str] = mapped_column(Text)
    previous_hash: Mapped[str] = mapped_column(String)
    event_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Source(Base):
    __tablename__ = "dataset_sources"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    module: Mapped[str] = mapped_column(String, index=True)
    metadata_json: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String, default="candidate")
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer: Mapped[str | None] = mapped_column(String, nullable=True)


class Job(Base):
    __tablename__ = "ingestion_jobs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    source_id: Mapped[str] = mapped_column(String)
    owner: Mapped[str] = mapped_column(String)
    payload: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String, default="dry_run")
    checksum: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    body: Mapped[str] = mapped_column(Text)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[str] = mapped_column(String, default=now)


def migrate():
    Base.metadata.create_all(engine)
    with DB.begin() as db:
        seed_key = "source-seed:2026-10-27-v2"
        if db.get(Config, seed_key):
            return
        candidates = json.loads(
            (ROOT / "packages/module-registry/source-candidates.json").read_text()
        )["sources"]
        for index, s in enumerate(candidates):
            k = f"SRC-{index+1:04}"
            if not db.get(Source, k):
                db.add(
                    Source(
                        id=k,
                        module=s["module_id"],
                        metadata_json=json.dumps(s, ensure_ascii=False),
                        state="candidate",
                    )
                )
        db.add(
            Config(key=seed_key, value="244 candidate sources; rights states preserved")
        )
