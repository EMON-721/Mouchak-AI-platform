"""Owner-private stock ledger adapted from DokanLens V3 movement rules."""

import hashlib, json
from datetime import datetime, date, timedelta, time, timezone
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    select,
    update,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from .store import Base, Workspace, Consent, seal, open_sealed, uid, now
from .auth import identify, db_session
from .domain import number
from .legacy_workflows import canonical


class StockItem(Base):
    __tablename__ = "stock_items"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "workspace_id", "sku_hash", name="uq_stock_owner_workspace_sku"
        ),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    sku_hash: Mapped[str] = mapped_column(String)
    encrypted: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)
    minimum: Mapped[int] = mapped_column(Integer)
    revision: Mapped[int] = mapped_column(Integer, default=0)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[str] = mapped_column(String, default=now)


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "workspace_id", "idempotency_key", name="uq_stock_movement_retry"
        ),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[str] = mapped_column(
        ForeignKey("stock_items.id", ondelete="CASCADE"), index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String)
    encrypted: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String, default=now)


class ItemInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    sku: str = Field(min_length=1, max_length=100)
    unit: Literal["packet", "piece", "kg", "g", "l", "ml"] = "packet"
    quantity: int = Field(ge=0, le=10000000, strict=True)
    minimum: int = Field(ge=0, le=10000000, strict=True)
    unit_cost: str | None = None
    expiry: str | None = None
    consent: bool


class MovementInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["sale", "purchase", "return", "damage", "supplier_return"]
    quantity: int = Field(gt=0, le=1000000, strict=True)
    expected_revision: int = Field(ge=0, strict=True)
    idempotency_key: str = Field(min_length=8, max_length=100)
    date: str | None = None
    consent: bool


router = APIRouter(prefix="/api/retail")


def workspace(db, user, wid):
    w = db.scalar(
        select(Workspace).where(Workspace.id == wid, Workspace.user_id == user.id)
    )
    if not w:
        raise HTTPException(404, "Workspace not found / কর্মক্ষেত্র পাওয়া যায়নি")
    return w


def owned_item(db, user, wid, iid):
    workspace(db, user, wid)
    i = db.scalar(
        select(StockItem).where(
            StockItem.id == iid,
            StockItem.user_id == user.id,
            StockItem.workspace_id == wid,
        )
    )
    if not i:
        raise HTTPException(404, "Item not found / পণ্য পাওয়া যায়নি")
    return i


def item_view(i):
    data = open_sealed(i.encrypted)
    expiry = data.get("expiry")
    return {
        "id": i.id,
        **data,
        "quantity": i.quantity,
        "minimum": i.minimum,
        "revision": i.revision,
        "reorder": i.quantity <= i.minimum,
        "expired": bool(
            expiry
            and date.fromisoformat(expiry) < datetime.now(ZoneInfo("Asia/Dhaka")).date()
        ),
        "archived": i.archived,
        "source_kind": "user_confirmed_stock",
    }


@router.get("/{wid}/items")
def items(wid: str, user=Depends(identify), db=Depends(db_session)):
    workspace(db, user, wid)
    return [
        item_view(i)
        for i in db.scalars(
            select(StockItem)
            .where(
                StockItem.user_id == user.id,
                StockItem.workspace_id == wid,
                StockItem.archived == False,
            )
            .order_by(StockItem.created_at)
            .limit(500)
        )
    ]


@router.post("/{wid}/items", status_code=201)
def create_item(wid: str, p: ItemInput, user=Depends(identify), db=Depends(db_session)):
    workspace(db, user, wid)
    if not p.consent:
        raise HTTPException(422, "Processing consent required")
    if not p.name.strip() or not p.sku.strip():
        raise HTTPException(422, "Name and SKU are required")
    if db.scalar(
        select(StockItem).where(
            StockItem.user_id == user.id,
            StockItem.workspace_id == wid,
            StockItem.sku_hash == hashlib.sha256(canonical(p.sku).encode()).hexdigest(),
        )
    ):
        raise HTTPException(409, "SKU already exists / SKU আগে থেকে আছে")
    if p.expiry:
        try:
            date.fromisoformat(p.expiry)
        except ValueError:
            raise HTTPException(422, "Use a confirmed ISO expiry date")
    cost = (
        None
        if p.unit_cost in [None, ""]
        else int(
            (number(p.unit_cost) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )
    )
    i = StockItem(
        user_id=user.id,
        workspace_id=wid,
        sku_hash=hashlib.sha256(canonical(p.sku).encode()).hexdigest(),
        encrypted=seal(
            {
                "name": p.name.strip(),
                "sku": p.sku.strip(),
                "unit": p.unit,
                "unit_cost_paisa": cost,
                "expiry": p.expiry or None,
            }
        ),
        quantity=p.quantity,
        minimum=p.minimum,
    )
    db.add(i)
    db.add(
        Consent(
            user_id=user.id,
            module="dokanlens-ai",
            purpose="service_processing",
            granted=True,
        )
    )
    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(409, "Concurrent duplicate SKU; refresh and review")
    return item_view(i)


@router.post("/{wid}/items/{iid}/movements", status_code=201)
def movement(
    wid: str, iid: str, p: MovementInput, user=Depends(identify), db=Depends(db_session)
):
    i = owned_item(db, user, wid, iid)
    if not p.consent:
        raise HTTPException(422, "Processing consent required")
    fingerprint = hashlib.sha256(
        json.dumps(
            {"item_id": iid, "type": p.type, "quantity": p.quantity, "date": p.date},
            sort_keys=True,
        ).encode()
    ).hexdigest()
    old = db.scalar(
        select(StockMovement).where(
            StockMovement.user_id == user.id,
            StockMovement.workspace_id == wid,
            StockMovement.idempotency_key == p.idempotency_key,
        )
    )
    if old:
        event = open_sealed(old.encrypted)
        if event["request_hash"] != fingerprint:
            raise HTTPException(409, "Retry key reused with different values")
        return {
            "id": old.id,
            "item": item_view(i),
            "event": {k: v for k, v in event.items() if k != "request_hash"},
            "replayed": True,
        }
    if i.archived:
        raise HTTPException(409, "Item is archived")
    if i.revision != p.expected_revision:
        raise HTTPException(
            409, "Stock changed; refresh before recording / স্টক বদলেছে; আবার দেখুন"
        )
    delta = p.quantity * (
        {"sale": -1, "purchase": 1, "return": 1, "damage": -1, "supplier_return": -1}[
            p.type
        ]
    )
    after = i.quantity + delta
    if after < 0:
        raise HTTPException(
            422, "Insufficient confirmed stock / পর্যাপ্ত নিশ্চিত স্টক নেই"
        )
    if after > 10000000:
        raise HTTPException(422, "Stock limit exceeded")
    current = datetime.now(ZoneInfo("Asia/Dhaka"))
    try:
        day = current.date() if not p.date else date.fromisoformat(p.date)
    except ValueError:
        raise HTTPException(422, "Use a confirmed ISO movement date")
    if day > current.date():
        raise HTTPException(422, "A stock movement cannot be future-dated")
    changed = db.execute(
        update(StockItem)
        .where(
            StockItem.id == i.id,
            StockItem.user_id == user.id,
            StockItem.revision == p.expected_revision,
        )
        .values(quantity=after, revision=StockItem.revision + 1)
    )
    if changed.rowcount != 1:
        raise HTTPException(409, "Concurrent stock change; refresh")
    payload = {
        "type": p.type,
        "quantity": p.quantity,
        "delta": delta,
        "before": i.quantity - delta if i.quantity == after else i.quantity,
        "after": after,
        "request_hash": fingerprint,
        "method": "confirmed-stock-movement-v1",
    }
    # SQLAlchemy may synchronize the updated object; before is derived from after.
    payload["before"] = after - delta
    event = StockMovement(
        user_id=user.id,
        workspace_id=wid,
        item_id=i.id,
        idempotency_key=p.idempotency_key,
        encrypted=seal(payload),
        occurred_at=(
            current
            if day == current.date()
            else datetime.combine(day, time(12), ZoneInfo("Asia/Dhaka"))
        ).isoformat(),
    )
    db.add(event)
    db.add(
        Consent(
            user_id=user.id,
            module="dokanlens-ai",
            purpose="service_processing",
            granted=True,
        )
    )
    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(409, "Concurrent retry; refresh")
    db.refresh(i)
    return {
        "id": event.id,
        "item": item_view(i),
        "event": {k: v for k, v in payload.items() if k != "request_hash"},
        "replayed": False,
    }


@router.get("/{wid}/items/{iid}/history")
def history(wid: str, iid: str, user=Depends(identify), db=Depends(db_session)):
    i = owned_item(db, user, wid, iid)
    events = list(
        db.scalars(
            select(StockMovement)
            .where(
                StockMovement.user_id == user.id,
                StockMovement.workspace_id == wid,
                StockMovement.item_id == iid,
            )
            .order_by(StockMovement.created_at.desc())
            .limit(1001)
        )
    )
    current = datetime.now(ZoneInfo("Asia/Dhaka"))
    cutoff = current - timedelta(days=28)
    recent = list(
        db.scalars(
            select(StockMovement)
            .where(
                StockMovement.user_id == user.id,
                StockMovement.workspace_id == wid,
                StockMovement.item_id == iid,
                StockMovement.occurred_at >= cutoff.isoformat(),
                StockMovement.occurred_at <= current.isoformat(),
            )
            .limit(10001)
        )
    )
    sales = [e for e in recent if open_sealed(e.encrypted)["type"] == "sale"]
    days = {
        datetime.fromisoformat(e.occurred_at).astimezone(ZoneInfo("Asia/Dhaka")).date()
        for e in sales
    }
    velocity = {
        "status": "insufficient",
        "records": len(sales),
        "days": len(days),
        "minimum_sales": 5,
        "minimum_distinct_days": 3,
        "ml_forecast": False,
    }
    if len(recent) > 10000:
        velocity["status"] = "too_many_records_for_summary"
    elif len(sales) >= 5 and len(days) >= 3:
        first = min(datetime.fromisoformat(e.occurred_at) for e in sales)
        span = max(1, int((current - first).total_seconds() / 86400 + 0.999999))
        units = sum(open_sealed(e.encrypted)["quantity"] for e in sales)
        returned = sum(
            open_sealed(e.encrypted)["quantity"]
            for e in recent
            if open_sealed(e.encrypted)["type"] == "return"
            and datetime.fromisoformat(e.occurred_at) >= first
        )
        velocity.update(
            {
                "status": "descriptive_rule",
                "observed_days": span,
                "net_units_per_day": str(
                    (Decimal(max(0, units - returned)) / span).quantize(
                        Decimal(".0001")
                    )
                ),
            }
        )
    return {
        "item": item_view(i),
        "history_truncated": len(events) > 1000,
        "history_limit": 1000,
        "events": [
            {
                "id": e.id,
                "occurred_at": e.occurred_at,
                **{
                    k: v
                    for k, v in open_sealed(e.encrypted).items()
                    if k != "request_hash"
                },
            }
            for e in events[:1000]
        ],
        "velocity": velocity,
    }


def export_owned_stock(db, user):
    return {
        "items": [
            item_view(i)
            for i in db.scalars(select(StockItem).where(StockItem.user_id == user.id))
        ],
        "movements": [
            {
                "id": e.id,
                "workspace_id": e.workspace_id,
                "item_id": e.item_id,
                "occurred_at": e.occurred_at,
                **{
                    k: v
                    for k, v in open_sealed(e.encrypted).items()
                    if k != "request_hash"
                },
            }
            for e in db.scalars(
                select(StockMovement).where(StockMovement.user_id == user.id)
            )
        ],
    }
