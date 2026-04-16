"""Bucket CRUD API — tenant-scoped, linked to grow cycles."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import Bucket

router = APIRouter()


class BucketCreate(BaseModel):
    grow_cycle_id: UUID
    position: int = 1
    label: str | None = None
    strain_name: str | None = None
    growth_stage: str = "seedling"
    volume_gallons: float | None = None
    settings: dict | None = None


class BucketUpdate(BaseModel):
    label: str | None = None
    strain_name: str | None = None
    growth_stage: str | None = None
    status: str | None = None
    position: int | None = None
    volume_gallons: float | None = None
    settings: dict | None = None


class BucketResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    position: int
    label: str | None
    strain_name: str | None
    growth_stage: str
    status: str
    volume_gallons: float | None
    settings: dict | None
    model_config = {"from_attributes": True}


@router.post("", response_model=BucketResponse, status_code=201)
async def create_bucket(
    body: BucketCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    bucket = Bucket(tenant_id=user.tenant_id, **body.model_dump())
    session.add(bucket)
    await session.commit()
    await session.refresh(bucket)
    return bucket


@router.get("", response_model=list[BucketResponse])
async def list_buckets(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    grow_cycle_id: UUID | None = None,
):
    q = select(Bucket).order_by(Bucket.position)
    if grow_cycle_id:
        q = q.where(Bucket.grow_cycle_id == grow_cycle_id)
    result = await session.execute(q)
    return result.scalars().all()


@router.get("/{bucket_id}", response_model=BucketResponse)
async def get_bucket(
    bucket_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    bucket = await session.get(Bucket, bucket_id)
    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    return bucket


@router.patch("/{bucket_id}", response_model=BucketResponse)
async def update_bucket(
    bucket_id: UUID,
    body: BucketUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    bucket = await session.get(Bucket, bucket_id)
    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(bucket, field, value)
    await session.commit()
    await session.refresh(bucket)
    return bucket


@router.delete("/{bucket_id}", status_code=204)
async def delete_bucket(
    bucket_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    bucket = await session.get(Bucket, bucket_id)
    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    await session.delete(bucket)
    await session.commit()
