"""Owner-scoped encrypted chunk assembly. No unscanned bytes become assets."""

import base64, hashlib, time
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, select, func, delete
from sqlalchemy.orm import Mapped, mapped_column
from .store import Base, User, Asset, seal, open_sealed, uid
from .auth import identify, db_session

router = APIRouter(prefix="/api/uploads")
CHUNK_BYTES = 1024 * 1024
MAX_BYTES = 10 * CHUNK_BYTES


class ChunkUpload(Base):
    __tablename__ = "chunk_uploads"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    size: Mapped[int] = mapped_column(Integer)
    checksum: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[int] = mapped_column(Integer, index=True)
    asset_id: Mapped[str | None] = mapped_column(ForeignKey("private_assets.id", ondelete="SET NULL"), nullable=True)
    state: Mapped[str] = mapped_column(String, default="uploading")


class UploadPart(Base):
    __tablename__ = "upload_parts"
    __table_args__ = (UniqueConstraint("upload_id", "part", name="uq_upload_part"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    upload_id: Mapped[str] = mapped_column(ForeignKey("chunk_uploads.id", ondelete="CASCADE"), index=True)
    part: Mapped[int] = mapped_column(Integer)
    checksum: Mapped[str] = mapped_column(String(64))
    encrypted: Mapped[str] = mapped_column(Text)


class StartInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    size: int = Field(strict=True, gt=0, le=MAX_BYTES)
    checksum: str = Field(pattern=r"^[a-f0-9]{64}$")
    consent: bool = Field(strict=True)


def owner(db, u, upload_id):
    item = db.scalar(select(ChunkUpload).where(
        ChunkUpload.id == upload_id, ChunkUpload.user_id == u.id
    ).with_for_update())
    if not item:
        raise HTTPException(404)
    if item.expires_at <= int(time.time()):
        raise HTTPException(410, "Upload expired / আপলোডের মেয়াদ শেষ")
    return item


@router.post("", status_code=201)
def start(p: StartInput, u=Depends(identify), db=Depends(db_session)):
    if not p.consent:
        raise HTTPException(422, "Processing consent required / সম্মতি প্রয়োজন")
    # Serialize reservations for the same owner, including requests on other replicas.
    db.scalar(select(User.id).where(User.id == u.id).with_for_update())
    at = int(time.time())
    reserved, count = db.execute(select(func.coalesce(func.sum(ChunkUpload.size), 0), func.count()).where(
        ChunkUpload.user_id == u.id, ChunkUpload.state == "uploading", ChunkUpload.expires_at > at
    )).one()
    stored = db.scalar(select(func.coalesce(func.sum(Asset.size), 0)).where(Asset.user_id == u.id))
    if count >= 2 or reserved + stored + p.size > 50 * CHUNK_BYTES:
        raise HTTPException(429, "Private upload quota reached / ব্যক্তিগত আপলোডের সীমা শেষ")
    item = ChunkUpload(user_id=u.id, size=p.size, checksum=p.checksum, expires_at=at + 900)
    db.add(item)
    db.flush()
    return {"id": item.id, "chunk_bytes": CHUNK_BYTES, "expires_at": item.expires_at}


@router.put("/{upload_id}/parts/{part}")
async def put_part(upload_id: str, part: int, request: Request, u=Depends(identify), db=Depends(db_session)):
    item = owner(db, u, upload_id)
    if item.state != "uploading":
        raise HTTPException(409, "Upload already finalized")
    offset = part * CHUNK_BYTES
    if part < 0 or offset >= item.size:
        raise HTTPException(422, "Invalid part")
    expected = min(CHUNK_BYTES, item.size - offset)
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > expected:
            raise HTTPException(413, "Chunk too large")
    if len(data) != expected:
        raise HTTPException(422, "Chunk size mismatch")
    checksum = hashlib.sha256(data).hexdigest()
    previous = db.scalar(select(UploadPart).where(UploadPart.upload_id == item.id, UploadPart.part == part))
    if previous:
        if previous.checksum != checksum:
            raise HTTPException(409, "A different chunk already occupies this part")
    else:
        db.add(UploadPart(upload_id=item.id, part=part, checksum=checksum,
                          encrypted=seal(base64.b64encode(data).decode())))
    return {"part": part, "checksum": checksum}


@router.post("/{upload_id}/complete", status_code=201)
def complete(upload_id: str, u=Depends(identify), db=Depends(db_session)):
    from .main import persist_asset, owner_asset

    item = owner(db, u, upload_id)
    if item.state == "complete":
        a = owner_asset(db, u, item.asset_id)
        return {"id": a.id, "kind": a.kind, "bytes": a.size, "scan_state": a.scan_state}
    parts = list(db.scalars(select(UploadPart).where(UploadPart.upload_id == item.id).order_by(UploadPart.part)))
    if [p.part for p in parts] != list(range((item.size + CHUNK_BYTES - 1) // CHUNK_BYTES)):
        raise HTTPException(409, "Upload has missing chunks / কিছু অংশ বাকি আছে")
    data = b"".join(base64.b64decode(open_sealed(p.encrypted), validate=True) for p in parts)
    if len(data) != item.size or hashlib.sha256(data).hexdigest() != item.checksum:
        raise HTTPException(422, "File checksum mismatch / ফাইলের checksum মেলেনি")
    # Same signature, resolution, quota, scanner and encrypted-storage checks as /upload.
    db.scalar(select(User.id).where(User.id == u.id).with_for_update())
    result = persist_asset(data, u, db)
    db.flush()
    item.asset_id, item.state = result["id"], "complete"
    db.execute(delete(UploadPart).where(UploadPart.upload_id == item.id))
    return result


@router.delete("/{upload_id}")
def cancel(upload_id: str, u=Depends(identify), db=Depends(db_session)):
    item = owner(db, u, upload_id)
    db.delete(item)  # Never deletes a completed private asset.
    return {"cancelled": True}


def cleanup(db, at=None):
    at = int(time.time()) if at is None else at
    ids = list(db.scalars(select(ChunkUpload.id).where(ChunkUpload.expires_at <= at).limit(100)))
    if ids:
        db.execute(delete(ChunkUpload).where(ChunkUpload.id.in_(ids)))
    return len(ids)
