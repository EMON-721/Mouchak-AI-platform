"""Audited operational workflows. No administrator gets blanket private access."""

import hashlib, json, time
from urllib.parse import urlparse
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, Integer, String, Text, select, update
from sqlalchemy.orm import Mapped, mapped_column, load_only
from .store import (
    Base,
    CMSVersion,
    Config,
    Source,
    Feedback,
    Notification,
    User,
    uid,
    now,
    open_sealed,
)
from .auth import identify, authorize, db_session, audit

router = APIRouter(prefix="/api")


def fingerprint(value):
    return hashlib.sha256((value or "").encode()).hexdigest()


class PublishSchedule(Base):
    __tablename__ = "cms_publish_schedules"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    version_id: Mapped[str] = mapped_column(
        ForeignKey("cms_versions.id", ondelete="CASCADE"), index=True
    )
    author: Mapped[str] = mapped_column(String)
    due_at: Mapped[int] = mapped_column(Integer, index=True)
    base_hash: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String, default="scheduled")
    created_at: Mapped[str] = mapped_column(String, default=now)


class SourceReview(Base):
    __tablename__ = "source_rights_reviews"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    source_id: Mapped[str] = mapped_column(
        ForeignKey("dataset_sources.id", ondelete="CASCADE"), index=True
    )
    reviewer: Mapped[str] = mapped_column(String)
    round: Mapped[int] = mapped_column(Integer)
    decision: Mapped[str] = mapped_column(String)
    asset_hash: Mapped[str] = mapped_column(String)
    evidence: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ScheduleInput(Strict):
    version_id: str
    due_at: int = Field(strict=True)


class RightsInput(Strict):
    decision: Literal["approved_reference_only", "approved_train_and_reuse", "revoked"]
    asset_url: str = Field(min_length=10, max_length=2000)
    terms_url: str = Field(min_length=10, max_length=2000)
    license_uri: str = Field(min_length=10, max_length=2000)
    scope: str = Field(min_length=10, max_length=1000)
    coverage: str = Field(min_length=3, max_length=300)
    source_date: str = Field(min_length=10, max_length=30)
    evidence: str = Field(min_length=30, max_length=4000)
    sensitivity: Literal["public_nonpersonal", "personal", "sensitive"]


class FeedbackInput(Strict):
    status: Literal["new", "triaged", "in_progress", "resolved", "rejected"]
    category: Literal[
        "bug", "accessibility", "content", "privacy", "model_quality", "other"
    ]


class NoticeInput(Strict):
    user_id: str
    body_bn: str = Field(min_length=1, max_length=1000)
    body_en: str = Field(min_length=1, max_length=1000)


class ReadInput(Strict):
    read: bool


def schedule_view(s, db):
    v = db.get(CMSVersion, s.version_id)
    return {
        "id": s.id,
        "version_id": s.version_id,
        "page": v.page if v else None,
        "due_at": s.due_at,
        "state": s.state,
        "created_at": s.created_at,
        "author": s.author,
    }


@router.get("/admin/publishing")
def schedules(u=Depends(authorize("cms")), db=Depends(db_session, scope="function")):
    return [
        schedule_view(s, db)
        for s in db.scalars(
            select(PublishSchedule)
            .order_by(PublishSchedule.created_at.desc())
            .limit(300)
        )
    ]


@router.post("/admin/publishing", status_code=201)
def schedule(p: ScheduleInput, u=Depends(authorize("cms")), db=Depends(db_session, scope="function")):
    current = int(time.time())
    if not current + 30 <= p.due_at <= current + 366 * 86400:
        raise HTTPException(422, "Choose a future date within one year")
    v = db.get(CMSVersion, p.version_id)
    if not v:
        raise HTTPException(404)
    if v.page == "site-builder":
        from . import site_builder
        site_builder.publication_lock(db)
        if v.status != "reviewed":
            raise HTTPException(409, "Schedule requires an independently reviewed draft")
        site_builder.validate_publication(db, v)
    if db.scalar(
        select(PublishSchedule).where(
            PublishSchedule.version_id == v.id, PublishSchedule.state == "scheduled"
        )
    ):
        raise HTTPException(409, "Version already scheduled")
    conf = db.get(Config, "cms:" + v.page)
    s = PublishSchedule(
        version_id=v.id,
        author=u.id,
        due_at=p.due_at,
        base_hash=fingerprint(conf.value if conf else None),
    )
    db.add(s)
    db.flush()
    audit(db, u.id, "cms_scheduled", s.id, {"page": v.page, "due_at": p.due_at})
    return schedule_view(s, db)


@router.post("/admin/publishing/{sid}/cancel")
def cancel(sid: str, u=Depends(authorize("cms")), db=Depends(db_session, scope="function")):
    s = db.scalar(
        select(PublishSchedule).where(PublishSchedule.id == sid).with_for_update()
    )
    if not s:
        raise HTTPException(404)
    if s.state != "scheduled":
        raise HTTPException(409, "Schedule has already finished")
    s.state = "cancelled"
    audit(db, u.id, "cms_schedule_cancelled", sid)
    return schedule_view(s, db)


def run_due(db, at=None):
    """One transaction per poll. Claimed rows and publication roll back together."""
    at = int(time.time()) if at is None else at
    done = []
    for s in db.scalars(
        select(PublishSchedule)
        .where(PublishSchedule.state == "scheduled", PublishSchedule.due_at <= at)
        .order_by(PublishSchedule.due_at)
        .with_for_update(skip_locked=True)
        .limit(100)
    ):
        claimed = db.execute(
            update(PublishSchedule)
            .where(PublishSchedule.id == s.id, PublishSchedule.state == "scheduled")
            .values(state="processing")
        )
        if claimed.rowcount != 1:
            continue
        v = db.get(CMSVersion, s.version_id)
        author = db.scalar(
            select(User)
            .options(load_only(User.id, User.role, User.banned))
            .where(User.id == s.author)
        )
        if (
            not author
            or author.banned
            or author.role not in ["content_editor", "super_admin"]
        ):
            s.state = "author_unavailable"
            audit(db, "scheduler", "cms_schedule_denied", s.id)
            done.append({"id": s.id, "state": s.state})
            continue
        if v.page == "site-builder":
            from . import site_builder
            site_builder.publication_lock(db)
            try:
                site_builder.validate_publication(db, v)
                if v.status != "reviewed":
                    raise HTTPException(409, "Version is no longer pending publication")
            except HTTPException:
                s.state = "review_unavailable"
                audit(db, "scheduler", "site_schedule_denied", s.id)
                done.append({"id": s.id, "state": s.state})
                continue
        conf = db.scalar(
            select(Config).where(Config.key == "cms:" + v.page).with_for_update()
        )
        if fingerprint(conf.value if conf else None) != s.base_hash:
            s.state = "conflict"
            audit(db, "scheduler", "cms_schedule_conflict", s.id, {"page": v.page})
            done.append({"id": s.id, "state": s.state})
            continue
        if v.page == "site-builder":
            site_builder.set_active(db, v)
        elif conf:
            conf.value = v.body
        else:
            db.add(Config(key="cms:" + v.page, value=v.body))
        v.status = "published"
        s.state = "published"
        audit(
            db,
            "scheduler",
            "cms_scheduled_publish",
            s.id,
            {"page": v.page, "version": v.id},
        )
        done.append({"id": s.id, "state": s.state})
    heartbeat = db.get(Config, "scheduler:heartbeat")
    encoded = json.dumps({"last_poll_at": int(time.time()), "completed": len(done)})
    if heartbeat:
        heartbeat.value = encoded
    else:
        db.add(Config(key="scheduler:heartbeat", value=encoded))
    return done


@router.get("/admin/publishing/health")
def scheduler_health(u=Depends(authorize("cms")), db=Depends(db_session, scope="function")):
    c = db.get(Config, "scheduler:heartbeat")
    data = json.loads(c.value) if c else {"last_poll_at": None}
    return {
        **data,
        "worker_recently_seen": bool(
            data["last_poll_at"] and int(time.time()) - data["last_poll_at"] < 90
        ),
        "production_deployment_verified": False,
    }


def safe_url(value):
    p = urlparse(value)
    if (
        p.scheme not in ["https", "http"]
        or not p.hostname
        or p.username
        or p.password
        or p.fragment
    ):
        raise HTTPException(
            422, "Use a public reference URL without credentials or fragment"
        )


def rights_round(db, sid, advance=False):
    key = "source-review-round:" + sid
    c = db.get(Config, key)
    value = int(c.value) if c else 0
    if advance:
        value += 1
        if c:
            c.value = str(value)
        else:
            db.add(Config(key=key, value=str(value)))
    return value


@router.get("/admin/sources/{sid}/reviews")
def reviews(sid: str, u=Depends(authorize("sources")), db=Depends(db_session, scope="function")):
    if not db.get(Source, sid):
        raise HTTPException(404)
    return [
        {
            "id": r.id,
            "reviewer": r.reviewer,
            "round": r.round,
            "decision": r.decision,
            "created_at": r.created_at,
            **json.loads(r.evidence),
        }
        for r in db.scalars(
            select(SourceReview)
            .where(SourceReview.source_id == sid)
            .order_by(SourceReview.created_at.desc())
        )
    ]


@router.post("/admin/sources/{sid}/reviews", status_code=201)
def rights_review(
    sid: str, p: RightsInput, u=Depends(authorize("sources")), db=Depends(db_session, scope="function")
):
    from datetime import date, datetime
    from zoneinfo import ZoneInfo

    s = db.scalar(select(Source).where(Source.id == sid).with_for_update())
    if not s:
        raise HTTPException(404)
    for v in [p.asset_url, p.terms_url, p.license_uri]:
        safe_url(v)
    try:
        if (
            date.fromisoformat(p.source_date)
            > datetime.now(ZoneInfo("Asia/Dhaka")).date()
        ):
            raise ValueError()
    except ValueError:
        raise HTTPException(422, "Use a valid source date, not a future date")
    rd = rights_round(db, sid, p.decision == "revoked")
    payload = p.model_dump()
    asset_hash = fingerprint(
        json.dumps(
            {k: v for k, v in payload.items() if k != "evidence"}, sort_keys=True
        )
    )
    if db.scalar(
        select(SourceReview).where(
            SourceReview.source_id == sid,
            SourceReview.round == rd,
            SourceReview.reviewer == u.id,
            SourceReview.asset_hash == asset_hash,
        )
    ):
        raise HTTPException(409, "This reviewer has already recorded this decision")
    r = SourceReview(
        source_id=sid,
        reviewer=u.id,
        round=rd,
        decision=p.decision,
        asset_hash=asset_hash,
        evidence=json.dumps(payload, ensure_ascii=False),
    )
    db.add(r)
    db.flush()
    distinct = {
        x
        for x in db.scalars(
            select(SourceReview.reviewer).where(
                SourceReview.source_id == sid,
                SourceReview.round == rd,
                SourceReview.asset_hash == asset_hash,
                SourceReview.decision == p.decision,
            )
        )
    }
    from .collaboration import CAT

    high = (
        CAT[s.module]["category"] in ["health", "civic", "consumer"]
        or p.sensitivity != "public_nonpersonal"
    )
    required = 2 if high and p.decision == "approved_train_and_reuse" else 1
    if p.decision == "revoked":
        s.state = "revoked"
    elif len(distinct) >= required:
        s.state = p.decision
    else:
        s.state = "rights_review"
    s.evidence = json.dumps(
        {
            "review_id": r.id,
            "asset_url": p.asset_url,
            "terms_url": p.terms_url,
            "license_uri": p.license_uri,
            "scope": p.scope,
            "sensitivity": p.sensitivity,
            "independent_reviewers": len(distinct),
            "required_reviewers": required,
        },
        ensure_ascii=False,
    )
    s.reviewer = u.id
    audit(
        db,
        u.id,
        "asset_rights_review",
        sid,
        {
            "decision": p.decision,
            "state": s.state,
            "reviewers": len(distinct),
            "round": rd,
        },
    )
    return {
        "id": r.id,
        "source_id": sid,
        "state": s.state,
        "independent_reviewers": len(distinct),
        "required_reviewers": required,
        "data_imported": False,
    }


@router.get("/admin/feedback")
def feedback_list(u=Depends(authorize("support")), db=Depends(db_session, scope="function")):
    result = []
    for f in db.scalars(
        select(Feedback).order_by(Feedback.created_at.desc()).limit(300)
    ):
        c = db.get(Config, "feedback-status:" + f.id)
        result.append(
            {
                "id": f.id,
                "text": open_sealed(f.body),
                "created_at": f.created_at,
                **(
                    json.loads(c.value) if c else {"status": "new", "category": "other"}
                ),
            }
        )
    return result


@router.patch("/admin/feedback/{fid}")
def classify_feedback(
    fid: str, p: FeedbackInput, u=Depends(authorize("support")), db=Depends(db_session, scope="function")
):
    if not db.get(Feedback, fid):
        raise HTTPException(404)
    key = "feedback-status:" + fid
    c = db.get(Config, key)
    value = json.dumps(p.model_dump())
    if c:
        c.value = value
    else:
        db.add(Config(key=key, value=value))
    audit(db, u.id, "feedback_triaged", fid, p.model_dump())
    return {"id": fid, **p.model_dump()}


@router.post("/admin/notifications", status_code=201)
def send_notice(
    p: NoticeInput, u=Depends(authorize("operations")), db=Depends(db_session, scope="function")
):
    user = db.get(User, p.user_id)
    if not user or user.banned:
        raise HTTPException(404)
    n = Notification(
        user_id=p.user_id,
        body=json.dumps({"bn": p.body_bn, "en": p.body_en}, ensure_ascii=False),
    )
    db.add(n)
    db.flush()
    audit(db, u.id, "notice_created", n.id, {"scope": "single_user"})
    return {"id": n.id}


@router.patch("/notifications/{nid}")
def read_notice(nid: str, p: ReadInput, u=Depends(identify), db=Depends(db_session, scope="function")):
    n = db.scalar(
        select(Notification).where(Notification.id == nid, Notification.user_id == u.id)
    )
    if not n:
        raise HTTPException(404)
    n.read = p.read
    return {"id": n.id, "read": n.read}


@router.get("/admin/notifications")
def notice_dispatches(u=Depends(authorize("operations")), db=Depends(db_session, scope="function")):
    from .store import Audit

    return [
        {"id": a.target, "created_at": a.created_at, "status": "created"}
        for a in db.scalars(
            select(Audit)
            .where(Audit.actor == u.id, Audit.action == "notice_created")
            .order_by(Audit.created_at.desc())
            .limit(300)
        )
    ]
