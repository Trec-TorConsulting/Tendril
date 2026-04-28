"""Photos API — bucket URL photos + grow-level file uploads (S3/MinIO)."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.database import async_session_factory
from app.grows.models import BucketPhoto, GrowPhoto
from app.pagination import PaginatedResponse, PaginationParams, paginate
from app.storage import (
    ALLOWED_CONTENT_TYPES,
    MAX_FILE_SIZE,
)
from app.storage import (
    delete_photo as s3_delete,
)
from app.storage import (
    get_photo as s3_get,
)
from app.storage import (
    upload_photo as s3_upload,
)

logger = logging.getLogger("tendril.photos")
router = APIRouter()


class PhotoCreate(BaseModel):
    bucket_id: UUID
    url: str
    caption: str | None = None


class PhotoUpdate(BaseModel):
    caption: str | None = None


class PhotoResponse(BaseModel):
    id: UUID
    bucket_id: UUID
    url: str
    caption: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


@router.post("", response_model=PhotoResponse, status_code=201)
async def create_photo(
    body: PhotoCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    photo = BucketPhoto(tenant_id=user.tenant_id, **body.model_dump())
    session.add(photo)
    await session.commit()
    await session.refresh(photo)
    return photo


@router.get("", response_model=PaginatedResponse[PhotoResponse])
async def list_photos(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    bucket_id: UUID | None = None,
):
    q = select(BucketPhoto).order_by(desc(BucketPhoto.created_at))
    if bucket_id:
        q = q.where(BucketPhoto.bucket_id == bucket_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.patch("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: UUID,
    body: PhotoUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    photo = await session.get(BucketPhoto, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    if body.caption is not None:
        photo.caption = body.caption
    await session.commit()
    await session.refresh(photo)
    return photo


@router.delete("/{photo_id}", status_code=204)
async def delete_photo(
    photo_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    photo = await session.get(BucketPhoto, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    await session.delete(photo)
    await session.commit()


# ---------- Grow-level photos (S3 file upload) ----------

class GrowPhotoResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    bucket_id: UUID | None
    source: str
    caption: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class GrowPhotoUpdate(BaseModel):
    caption: str | None = None


@router.post("/grow", response_model=GrowPhotoResponse, status_code=201)
async def upload_grow_photo(
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    file: UploadFile = File(...),
    grow_cycle_id: str = Form(...),
    bucket_id: str | None = Form(None),
    caption: str | None = Form(None),
):
    """Upload a photo file (JPEG/PNG/WebP) for a grow cycle."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are allowed")

    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image must be under 10 MB")

    loop = asyncio.get_running_loop()
    key = await loop.run_in_executor(
        None, s3_upload, data, file.content_type, str(user.tenant_id), grow_cycle_id,
    )

    photo = GrowPhoto(
        tenant_id=user.tenant_id,
        grow_cycle_id=UUID(grow_cycle_id),
        bucket_id=UUID(bucket_id) if bucket_id else None,
        source="upload",
        storage_key=key,
        caption=caption,
    )
    session.add(photo)
    await session.commit()
    await session.refresh(photo)
    return photo


@router.get("/grow", response_model=PaginatedResponse[GrowPhotoResponse])
async def list_grow_photos(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    grow_cycle_id: UUID | None = None,
):
    q = select(GrowPhoto).order_by(desc(GrowPhoto.created_at))
    if grow_cycle_id:
        q = q.where(GrowPhoto.grow_cycle_id == grow_cycle_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/grow/file/{photo_id}")
async def serve_grow_photo(
    photo_id: UUID,
    request: Request,
    sig: str = Query(..., description="HMAC signature"),
    exp: str = Query(..., description="Expiry timestamp"),
    tid: str = Query(..., description="Tenant ID"),
):
    """Serve an uploaded photo from S3 storage. Uses HMAC-signed URLs for <img> tags."""
    from app.auth.signed_url import verify_signed_url
    tenant_id = verify_signed_url(request.url.path, sig, exp, tid)

    async with async_session_factory() as session:
        await session.execute(text(f"SET app.current_tenant = '{tenant_id}'"))
        photo = await session.get(GrowPhoto, photo_id)

    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    loop = asyncio.get_running_loop()
    try:
        data, content_type = await loop.run_in_executor(None, s3_get, photo.storage_key)
    except Exception:
        logger.exception("Failed to fetch photo from S3: %s", photo.storage_key)
        raise HTTPException(status_code=502, detail="Failed to retrieve photo")

    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.patch("/grow/{photo_id}", response_model=GrowPhotoResponse)
async def update_grow_photo(
    photo_id: UUID,
    body: GrowPhotoUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    photo = await session.get(GrowPhoto, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    if body.caption is not None:
        photo.caption = body.caption
    await session.commit()
    await session.refresh(photo)
    return photo


@router.delete("/grow/{photo_id}", status_code=204)
async def delete_grow_photo(
    photo_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    photo = await session.get(GrowPhoto, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Remove from S3
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, s3_delete, photo.storage_key)
    except Exception:
        logger.warning("Failed to delete S3 object: %s", photo.storage_key)

    await session.delete(photo)
    await session.commit()


# ---------- Timelapse (animated GIF from health-check snapshots) ----------

def _build_timelapse_gif(frames: list[tuple[bytes, str]]) -> bytes:
    """Stitch snapshot frames into an animated GIF with timestamp overlay.

    Each frame tuple is (image_bytes, caption_text).
    Returns the GIF bytes.
    """
    from io import BytesIO

    from PIL import Image, ImageDraw, ImageFont

    FRAME_WIDTH = 640
    DURATION_MS = 800  # ms per frame

    pil_frames: list[Image.Image] = []
    for img_bytes, caption in frames:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        # Resize proportionally to fixed width
        ratio = FRAME_WIDTH / img.width
        img = img.resize((FRAME_WIDTH, int(img.height * ratio)), Image.LANCZOS)

        # Overlay timestamp caption at the bottom
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except OSError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), caption, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        y = img.height - th - 10
        # Semi-transparent background bar
        draw.rectangle([(0, y - 4), (img.width, img.height)], fill=(0, 0, 0))
        draw.text(((img.width - tw) // 2, y - 2), caption, fill="white", font=font)

        pil_frames.append(img)

    buf = BytesIO()
    pil_frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=pil_frames[1:],
        duration=DURATION_MS,
        loop=0,
    )
    return buf.getvalue()


@router.get("/grow/timelapse/{grow_cycle_id}")
async def get_timelapse(
    grow_cycle_id: UUID,
    request: Request,
    sig: str = Query(..., description="HMAC signature"),
    exp: str = Query(..., description="Expiry timestamp"),
    tid: str = Query(..., description="Tenant ID"),
):
    """Generate an animated GIF timelapse from health-check snapshots.

    Uses HMAC-signed URLs for <img> tags.
    """
    from app.auth.signed_url import verify_signed_url
    tenant_id = verify_signed_url(request.url.path, sig, exp, tid)

    async with async_session_factory() as session:
        await session.execute(text(f"SET app.current_tenant = '{tenant_id}'"))

        photos = (await session.execute(
            select(GrowPhoto)
            .where(
                GrowPhoto.grow_cycle_id == grow_cycle_id,
                GrowPhoto.source == "health_check",
            )
            .order_by(GrowPhoto.created_at)
        )).scalars().all()

    if len(photos) < 2:
        raise HTTPException(
            status_code=404,
            detail="Not enough snapshots yet — need at least 2 health-check photos for a timelapse",
        )

    # Fetch all snapshot images from S3
    loop = asyncio.get_running_loop()
    frames: list[tuple[bytes, str]] = []
    for photo in photos:
        try:
            data, _ct = await loop.run_in_executor(None, s3_get, photo.storage_key)
            ts = photo.created_at.strftime("%b %d, %Y  %I:%M %p")
            caption = f"{ts}  —  {photo.caption or ''}"
            frames.append((data, caption))
        except Exception:
            logger.warning("Skipping unreadable snapshot %s", photo.storage_key)

    if len(frames) < 2:
        raise HTTPException(status_code=404, detail="Not enough readable snapshots for timelapse")

    gif_bytes = await loop.run_in_executor(None, _build_timelapse_gif, frames)

    return Response(
        content=gif_bytes,
        media_type="image/gif",
        headers={"Cache-Control": "public, max-age=300"},
    )
