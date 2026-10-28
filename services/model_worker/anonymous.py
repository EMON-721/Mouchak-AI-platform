"""Account-free visitor sessions with existing owner isolation and explicit consent.

No visitor email/name/password is collected. The reserved internal owner marker
only adapts the existing foreign-key schema; it is never a sign-in account or
public profile. Privileged operator authentication remains separate in the UI.
"""

import os, secrets, time
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, delete, exists, text
from sqlalchemy.orm import load_only
from .store import (
    DB,
    User,
    Session,
    Workspace,
    Asset,
    Consent,
    Run,
    Config,
    uid,
    now,
    PRODUCTION,
)
from .auth import identify, db_session, new_session, PRIVILEGED, digest
from . import storage

router = APIRouter(prefix="/api/session")
TTL = max(900, min(86400, int(os.getenv("ANONYMOUS_SESSION_TTL_SECONDS", "86400"))))


def activate_owner(db, owner_id):
    if db.bind.dialect.name == "postgresql":
        db.execute(
            text("SELECT set_config('app.user_id', :uid, true)"), {"uid": owner_id}
        )


def view(u, s):
    return {
        "mode": "anonymous" if u.role == "guest" else "operator",
        "visitor_id": u.id,
        "role": u.role,
        "expires_at": s.expires,
        "csrf": s.csrf,
        "requires_account": False,
        "profile_collected": False,
    }


@router.post("")
def visitor(request: Request, response: Response, db=Depends(db_session)):
    existing = request.cookies.get("mouchak_session", "")
    s = db.get(Session, digest(existing)) if existing else None
    if s and s.expires > int(time.time()):
        u = db.get(User, s.user_id)
        if (
            u
            and not u.banned
            and (u.role == "guest" or u.role in PRIVILEGED)
            and (
                u.role == "guest"
                or (
                    int(time.time()) - s.last_seen <= 1800
                    and (not PRODUCTION or u.verified)
                )
            )
        ):
            # This same-origin handshake only returns this cookie's current scope.
            # It never accepts an owner ID or role from the caller.
            s.last_seen = int(time.time())
            request.state.session = s
            activate_owner(db, u.id)
            return view(u, s)
    identity = uid()
    u = User(
        id=identity,
        email=identity + "@anonymous.invalid",
        password="!anonymous-no-password",
        name="",
        role="guest",
        verified=False,
        language="bn",
    )
    db.add(u)
    db.flush()
    activate_owner(db, identity)
    db.add(Workspace(user_id=identity, name="এই সেশনের কাজ / Session work"))
    new_session(db, u, request, response, anonymous=True, ttl=TTL)
    return view(u, request.state.session)


class ClearInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirm: bool = Field(strict=True)


def remove_visitor(db, u):
    for a in db.scalars(select(Asset).where(Asset.user_id == u.id)):
        storage.remove(a.path)
    db.delete(u)
    db.flush()  # Existing FK cascades remove only this owner.


@router.post("/clear")
def clear(
    p: ClearInput, response: Response, u=Depends(identify), db=Depends(db_session)
):
    if u.role != "guest":
        raise HTTPException(403, "Only an anonymous session can be cleared here")
    if not p.confirm:
        raise HTTPException(
            422, "Confirm clearing this session / এই সেশনের তথ্য মুছতে সম্মতি দিন"
        )
    remove_visitor(db, u)
    response.delete_cookie("mouchak_session", path="/")
    return {
        "cleared": True,
        "backup_retention_notice": "Encrypted operator backups expire under their separate retention policy.",
    }


def purge_expired(factory=DB, at=None, limit=100):
    """Operator task: never remove legacy accounts or an active visitor."""
    at = int(time.time()) if at is None else at
    removed = 0
    with factory() as db:
        ids = list(
            db.scalars(
                select(User.id)
                .where(
                    User.role == "guest",
                    ~exists(
                        select(Session.id).where(
                            Session.user_id == User.id, Session.expires > at
                        )
                    ),
                )
                .limit(limit)
            )
        )
    for identity in ids:
        with factory.begin() as db:
            u = db.scalar(
                select(User).options(load_only(User.id, User.role))
                .where(User.id == identity, User.role == "guest")
                .with_for_update()
            )
            if not u or db.scalar(
                select(Session.id)
                .where(Session.user_id == identity, Session.expires > at)
                .limit(1)
            ):
                continue
            activate_owner(db, identity)
            remove_visitor(db, u)
            removed += 1
    return {"expired_visitor_scopes_removed": removed, "legacy_accounts_removed": 0}
