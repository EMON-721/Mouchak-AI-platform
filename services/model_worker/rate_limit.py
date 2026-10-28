"""Atomic shared fixed-window limits; no raw addresses or cookies are persisted."""

import hashlib, hmac, time
from sqlalchemy import Integer, String, delete, text, select
from sqlalchemy.orm import Mapped, mapped_column
from .store import Base, DB, Session, key


class RateBucket(Base):
    __tablename__ = "request_rate_buckets"
    subject: Mapped[str] = mapped_column(String(64), primary_key=True)
    window_start: Mapped[int] = mapped_column(Integer, primary_key=True)
    used: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[int] = mapped_column(Integer, index=True)


def subject(value):
    return hmac.new(key.encode(), value.encode(), hashlib.sha256).hexdigest()


def consume(identity, limit=60, seconds=60, factory=DB, at=None):
    """One atomic UPSERT across processes. A storage error must not allow traffic.

    Production clock comes from PostgreSQL, avoiding application clock skew.
    Fixed windows permit a boundary burst; this is not a rolling-window promise.
    """
    with factory.begin() as db:
        ts = int(at) if at is not None else (
            int(db.scalar(text("SELECT EXTRACT(EPOCH FROM clock_timestamp())")))
            if db.bind.dialect.name == "postgresql" else int(time.time())
        )
        window = ts // seconds * seconds
        row = db.execute(text("""
            INSERT INTO request_rate_buckets(subject, window_start, used, expires_at)
            VALUES (:subject, :window, 1, :expiry)
            ON CONFLICT(subject, window_start) DO UPDATE SET used=request_rate_buckets.used+1
            WHERE request_rate_buckets.used < :limit
            RETURNING used
        """), {"subject": subject(identity), "window": window,
               "expiry": window + seconds, "limit": limit}).first()
        return row is not None, window + seconds - ts


def guard(peer, group, raw_cookie):
    # A peer ceiling also bounds callers rotating fabricated cookies. Only an
    # existing, unexpired server session receives its own owner quota.
    allowed, retry = consume("transport:" + peer + ":" + group, limit=600)
    if not allowed:
        return allowed, retry
    identity = None
    if raw_cookie:
        with DB() as db:
            session = db.get(Session, hashlib.sha256(raw_cookie.encode()).hexdigest())
            if session and session.expires > int(time.time()):
                identity = session.user_id
    return consume(("owner:" + identity if identity else "unauthenticated:" + peer) + ":" + group)


def cleanup(db, at=None):
    at = int(time.time()) if at is None else at
    # Bounded batches prevent an accumulated table from blocking the worker.
    stale = db.execute(select(RateBucket.subject, RateBucket.window_start).where(
        RateBucket.expires_at < at - 60
    ).limit(1000)).all()
    for identity, window in stale:
        db.execute(delete(RateBucket).where(
            RateBucket.subject == identity, RateBucket.window_start == window
        ))
    return len(stale)
