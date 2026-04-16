"""Bucket photos API — upload, list, delete, caption."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import BucketPhoto

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


@router.get("", response_model=list[PhotoResponse])
async def list_photos(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    bucket_id: UUID | None = None,
):
    q = select(BucketPhoto).order_by(desc(BucketPhoto.created_at))
    if bucket_id:
        q = q.where(BucketPhoto.bucket_id == bucket_id)
    result = await session.execute(q)
    return result.scalars().all()


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
