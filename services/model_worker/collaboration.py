"""Explicit, narrow sharing: owner-selected facts for support and typed tool drafts.

Support grants hold an immutable selected-facts snapshot; they never bypass RLS
on tool_runs or expose inputs, raw uploads, account secrets or asset identifiers.
"""

import hashlib
import json
import time
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, Integer, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column
from .store import (
    Base,
    User,
    Session,
    Run,
    Workspace,
    Consent,
    Config,
    ROOT,
    seal,
    open_sealed,
    uid,
    now,
)
from .auth import identify, authorize, db_session, audit
from .domain import F

CAT = {
    m["slug"]: m
    for m in json.loads((ROOT / "packages/module-registry/catalogue.json").read_text())[
        "modules"
    ]
}
router = APIRouter(prefix="/api")


class SupportGrant(Base):
    __tablename__ = "support_access_grants"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    recipient_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    run_id: Mapped[str] = mapped_column(
        ForeignKey("tool_runs.id", ondelete="CASCADE"), index=True
    )
    encrypted: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[int] = mapped_column(Integer)
    revoked_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(String, default=now)


class ToolTransfer(Base):
    __tablename__ = "tool_transfers"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    source_run_id: Mapped[str] = mapped_column(
        ForeignKey("tool_runs.id", ondelete="CASCADE"), index=True
    )
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    target_module: Mapped[str] = mapped_column(String)
    encrypted: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String, default="draft")
    consumed_run_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GrantInput(Strict):
    run_id: str
    recipient_email: str = Field(min_length=3, max_length=254)
    fact_keys: list[str] = Field(min_length=1, max_length=30)
    reason: str = Field(min_length=10, max_length=1000)
    minutes: int = Field(ge=1, le=60, strict=True)
    consent: bool = Field(strict=True)


class Mapping(Strict):
    source: str
    target: str


class TransferInput(Strict):
    source_run_id: str
    target_module: str
    workspace_id: str
    mapping: list[Mapping] = Field(min_length=1, max_length=30)
    consent: bool = Field(default=False, strict=True)


def own_run(db, user, rid):
    r = db.scalar(select(Run).where(Run.id == rid, Run.user_id == user.id))
    if not r:
        raise HTTPException(404, "Record not found / রেকর্ড পাওয়া যায়নি")
    return r


def grant_view(g):
    p = open_sealed(g.encrypted)
    return {
        "id": g.id,
        "run_id": g.run_id,
        "recipient_id": g.recipient_id,
        "recipient_email": p["recipient_email"],
        "reason": p["reason"],
        "fact_keys": list(p["facts"]),
        "expires_at": g.expires_at,
        "revoked": g.revoked_at is not None,
        "active": g.revoked_at is None and g.expires_at > int(time.time()),
        "created_at": g.created_at,
    }


@router.post("/support/grants", status_code=201)
def create_grant(
    p: GrantInput, request: Request, u=Depends(identify), db=Depends(db_session)
):
    if not p.consent:
        raise HTTPException(
            422, "Explicit support-access consent required / আলাদা সম্মতি দিন"
        )
    if len(p.reason.strip()) < 10:
        raise HTTPException(422, "Explain the support purpose / সহায়তার কারণ লিখুন")
    r = own_run(db, u, p.run_id)
    recipient = db.scalar(
        select(User).where(
            User.email == p.recipient_email.strip().casefold(), User.banned == False
        )
    )
    if (
        not recipient
        or recipient.id == u.id
        or recipient.role not in ["support_agent", "super_admin"]
        or not recipient.mfa_enabled
    ):
        raise HTTPException(
            422,
            "Choose an eligible MFA-enabled support account / অনুমোদিত সহায়তাকারীর ইমেইল দিন",
        )
    payload = open_sealed(r.encrypted)
    facts = payload["output"].get("facts", {})
    if (
        not isinstance(facts, dict)
        or len(set(p.fact_keys)) != len(p.fact_keys)
        or any(k not in facts for k in p.fact_keys)
    ):
        raise HTTPException(422, "Choose existing result facts only")
    chosen = {k: facts[k] for k in p.fact_keys}
    if len(json.dumps(chosen).encode()) > 32000:
        raise HTTPException(422, "Selected facts exceed the sharing limit")
    g = SupportGrant(
        user_id=u.id,
        recipient_id=recipient.id,
        run_id=r.id,
        expires_at=(
            min(int(time.time()) + p.minutes * 60, request.state.session.expires)
            if u.role == "guest"
            else int(time.time()) + p.minutes * 60
        ),
        encrypted=seal(
            {
                "facts": chosen,
                "reason": p.reason.strip(),
                "recipient_email": recipient.email,
                "module": r.module,
                "scope": "selected_result_facts_only",
                "source_created_at": r.created_at,
            }
        ),
    )
    db.add(g)
    db.add(
        Consent(
            user_id=u.id,
            module=r.module,
            purpose="temporary_support_selected_facts",
            granted=True,
        )
    )
    db.flush()
    audit(
        db,
        u.id,
        "support_grant_created",
        g.id,
        {
            "scope": "selected_result_facts_only",
            "minutes": p.minutes,
            "fields": len(chosen),
        },
    )
    return grant_view(g)


@router.get("/support/grants")
def owner_grants(u=Depends(identify), db=Depends(db_session)):
    return [
        grant_view(g)
        for g in db.scalars(
            select(SupportGrant)
            .where(SupportGrant.user_id == u.id)
            .order_by(SupportGrant.created_at.desc())
        )
    ]


@router.post("/support/grants/{gid}/revoke")
def revoke_grant(gid: str, u=Depends(identify), db=Depends(db_session)):
    g = db.scalar(
        select(SupportGrant).where(SupportGrant.id == gid, SupportGrant.user_id == u.id)
    )
    if not g:
        raise HTTPException(404)
    if not g.revoked_at:
        g.revoked_at = int(time.time())
        audit(db, u.id, "support_grant_revoked", gid)
    return grant_view(g)


@router.get("/admin/support")
def support_inbox(u=Depends(authorize("support")), db=Depends(db_session)):
    return [
        {"id": g.id, "expires_at": g.expires_at, "created_at": g.created_at}
        for g in db.scalars(
            select(SupportGrant).where(
                SupportGrant.recipient_id == u.id,
                SupportGrant.revoked_at.is_(None),
                SupportGrant.expires_at > int(time.time()),
            )
        )
    ]


@router.get("/admin/support/{gid}")
def read_support(gid: str, u=Depends(authorize("support")), db=Depends(db_session)):
    g = db.scalar(
        select(SupportGrant).where(
            SupportGrant.id == gid,
            SupportGrant.recipient_id == u.id,
            SupportGrant.revoked_at.is_(None),
            SupportGrant.expires_at > int(time.time()),
        )
    )
    if not g:
        raise HTTPException(
            404, "Grant unavailable or expired / অনুমতি নেই বা মেয়াদ শেষ"
        )
    owner = db.get(User, g.user_id)
    if (
        not owner
        or owner.banned
        or (
            owner.role == "guest"
            and not db.scalar(
                select(Session.id)
                .where(Session.user_id == owner.id, Session.expires > int(time.time()))
                .limit(1)
            )
        )
    ):
        raise HTTPException(404)
    p = open_sealed(g.encrypted)
    audit(db, u.id, "support_selected_facts_read", gid)
    return {
        "id": g.id,
        "expires_at": g.expires_at,
        "scope": p["scope"],
        "reason": p["reason"],
        "module": p["module"],
        "facts": p["facts"],
        "source_created_at": p["source_created_at"],
    }


def transfer_preview(p, db, u):
    r = own_run(db, u, p.source_run_id)
    target = CAT.get(p.target_module)
    if not target or target["slug"] == r.module:
        raise HTTPException(422, "Choose a different known tool")
    if not db.scalar(
        select(Workspace).where(
            Workspace.id == p.workspace_id, Workspace.user_id == u.id
        )
    ):
        raise HTTPException(404, "Workspace not found")
    configured = db.get(Config, "module:" + p.target_module)
    if target.get("release_status") == "blocked" or (
        configured and json.loads(configured.value).get("enabled") is False
    ):
        raise HTTPException(
            503, "Destination tool unavailable / গন্তব্য টুল এখন চালু নেই"
        )
    source_fields = {f["key"]: f for f in F[CAT[r.module]["engine"]]}
    target_fields = {f["key"]: f for f in F[target["engine"]]}
    inputs = open_sealed(r.encrypted).get("inputs", {})
    copied = {}
    mapping = []
    for m in p.mapping:
        a = source_fields.get(m.source)
        b = target_fields.get(m.target)
        if not a or not b or m.source not in inputs or m.target in copied:
            raise HTTPException(422, "Choose unique available declared fields")
        if a["type"] != b["type"] or (
            a["type"] == "table" and a.get("columns") != b.get("columns")
        ):
            raise HTTPException(
                422, "Incompatible field types; edit manually in the destination"
            )
        copied[m.target] = inputs[m.source]
        mapping.append(m.model_dump())
    if len(json.dumps(copied).encode()) > 64000:
        raise HTTPException(422, "Transferred fields exceed limit")
    return {
        "source_run_id": r.id,
        "source_module": r.module,
        "target_module": p.target_module,
        "workspace_id": p.workspace_id,
        "inputs": copied,
        "mapping": mapping,
        "state": "draft",
        "automatic_analysis": False,
        "notice": "Only selected fields are copied. Units are unchanged. Review and separately consent before processing. / শুধু বাছা তথ্য; একক বদলায়নি। দেখে নিয়ে আবার সম্মতি দিন।",
    }


@router.post("/transfers/preview")
def preview_transfer(p: TransferInput, u=Depends(identify), db=Depends(db_session)):
    return transfer_preview(p, db, u)


@router.post("/transfers", status_code=201)
def create_transfer(p: TransferInput, u=Depends(identify), db=Depends(db_session)):
    if not p.consent:
        raise HTTPException(422, "Explicit cross-tool consent required")
    preview = transfer_preview(p, db, u)
    t = ToolTransfer(
        user_id=u.id,
        source_run_id=p.source_run_id,
        workspace_id=p.workspace_id,
        target_module=p.target_module,
        encrypted=seal(preview),
    )
    db.add(t)
    db.add(
        Consent(
            user_id=u.id,
            module=p.target_module,
            purpose="selected_cross_tool_transfer",
            granted=True,
        )
    )
    db.flush()
    audit(
        db,
        u.id,
        "tool_transfer_draft",
        t.id,
        {"target": p.target_module, "fields": len(preview["inputs"])},
    )
    return {"id": t.id, **preview}


@router.get("/transfers")
def transfers(u=Depends(identify), db=Depends(db_session)):
    return [
        {
            "id": t.id,
            "source_run_id": t.source_run_id,
            "target_module": t.target_module,
            "workspace_id": t.workspace_id,
            "state": t.state,
            "created_at": t.created_at,
        }
        for t in db.scalars(
            select(ToolTransfer)
            .where(ToolTransfer.user_id == u.id)
            .order_by(ToolTransfer.created_at.desc())
        )
    ]


@router.get("/transfers/{tid}")
def get_transfer(tid: str, u=Depends(identify), db=Depends(db_session)):
    t = db.scalar(
        select(ToolTransfer).where(ToolTransfer.id == tid, ToolTransfer.user_id == u.id)
    )
    if not t:
        raise HTTPException(404)
    return {
        **open_sealed(t.encrypted),
        "id": t.id,
        "state": t.state,
        "consumed_run_id": t.consumed_run_id,
    }


def link_transfer(db, u, tid, module, workspace_id, inputs, run):
    if not tid:
        return
    # Lock on PostgreSQL; the state update remains atomic on both adapters.
    from sqlalchemy import update

    t = db.scalar(
        select(ToolTransfer)
        .where(ToolTransfer.id == tid, ToolTransfer.user_id == u.id)
        .with_for_update()
    )
    if not t or t.target_module != module or t.workspace_id != workspace_id:
        raise HTTPException(404, "Transfer not found")
    if t.state != "draft":
        raise HTTPException(409, "Transfer already processed; create a fresh draft")
    change = db.execute(
        update(ToolTransfer)
        .where(ToolTransfer.id == tid, ToolTransfer.state == "draft")
        .values(state="processed", consumed_run_id=run.id)
    )
    if change.rowcount != 1:
        raise HTTPException(409, "Concurrent transfer processing")
    run.parent_id = t.source_run_id
    audit(
        db, u.id, "tool_transfer_processed", tid, {"run_id": run.id, "target": module}
    )


def export_owned(db, u):
    return {
        "support_grants": [
            grant_view(g)
            for g in db.scalars(
                select(SupportGrant).where(SupportGrant.user_id == u.id)
            )
        ],
        "transfers": [
            {
                "id": t.id,
                "state": t.state,
                "consumed_run_id": t.consumed_run_id,
                **open_sealed(t.encrypted),
            }
            for t in db.scalars(
                select(ToolTransfer).where(ToolTransfer.user_id == u.id)
            )
        ],
    }
