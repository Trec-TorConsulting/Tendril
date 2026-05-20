"""Bucket CRUD API — tenant-scoped, linked to grow cycles."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import Bucket, JournalEntry, Strain
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


class BucketCreate(BaseModel):
    grow_cycle_id: UUID
    position: int = 1
    label: str | None = None
    strain_name: str | None = None
    strain_id: UUID | None = None
    growth_stage: str = "seedling"
    volume_gallons: float | None = None
    settings: dict | None = None


class BucketUpdate(BaseModel):
    label: str | None = None
    strain_name: str | None = None
    strain_id: UUID | None = None
    growth_stage: str | None = None
    status: str | None = None
    position: int | None = None
    volume_gallons: float | None = None
    settings: dict | None = None


class StrainSummary(BaseModel):
    id: UUID
    name: str
    breeder: str | None = None
    genetics: str | None = None
    flowering_days: int | None = None
    thc_pct: float | None = None
    cbd_pct: float | None = None
    terpene_profile: dict | None = None
    model_config = {"from_attributes": True}


class BucketResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    position: int
    label: str | None
    strain_name: str | None
    strain_id: UUID | None = None
    strain: StrainSummary | None = None
    growth_stage: str
    status: str
    volume_gallons: float | None
    settings: dict | None
    last_water_change_at: datetime | None = None
    model_config = {"from_attributes": True}


@router.post("", response_model=BucketResponse, status_code=201)
async def create_bucket(
    body: BucketCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a new bucket (plant site) in a grow cycle."""
    data = body.model_dump()
    # Auto-populate strain_name from strain if strain_id provided
    if data.get("strain_id") and not data.get("strain_name"):
        strain = await session.get(Strain, data["strain_id"])
        if strain:
            data["strain_name"] = strain.name
    bucket = Bucket(tenant_id=user.tenant_id, **data)
    session.add(bucket)
    await session.commit()
    await session.refresh(bucket)
    return bucket


@router.get("", response_model=PaginatedResponse[BucketResponse])
async def list_buckets(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    grow_cycle_id: UUID | None = None,
):
    """List buckets with optional grow cycle filtering."""
    q = select(Bucket).where(Bucket.tenant_id == user.tenant_id).order_by(Bucket.position)
    if grow_cycle_id:
        q = q.where(Bucket.grow_cycle_id == grow_cycle_id)
    items, total = await paginate(session, q, pagination)

    # Batch-fetch last water change timestamps for all returned buckets
    bucket_ids = [b.id for b in items]
    water_change_map = await _get_last_water_changes(session, bucket_ids)
    results = []
    for bucket in items:
        data = BucketResponse.model_validate(bucket)
        data.last_water_change_at = water_change_map.get(bucket.id)
        results.append(data)

    return PaginatedResponse(items=results, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{bucket_id}", response_model=BucketResponse)
async def get_bucket(
    bucket_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a bucket by ID."""
    bucket = await session.get(Bucket, bucket_id)
    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    water_change_map = await _get_last_water_changes(session, [bucket_id])
    data = BucketResponse.model_validate(bucket)
    data.last_water_change_at = water_change_map.get(bucket_id)
    return data


@router.patch("/{bucket_id}", response_model=BucketResponse)
async def update_bucket(
    bucket_id: UUID,
    body: BucketUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a bucket's details."""
    bucket = await session.get(Bucket, bucket_id)
    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    updates = body.model_dump(exclude_unset=True)
    # Auto-populate strain_name from strain if strain_id changed
    if "strain_id" in updates and updates["strain_id"] and "strain_name" not in updates:
        strain = await session.get(Strain, updates["strain_id"])
        if strain:
            updates["strain_name"] = strain.name
    for field, value in updates.items():
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
    """Soft-delete a bucket."""
    bucket = await session.get(Bucket, bucket_id)
    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    await session.delete(bucket)
    await session.commit()


async def _get_last_water_changes(session: AsyncSession, bucket_ids: list[UUID]) -> dict[UUID, datetime | None]:
    """Batch-fetch the most recent water_change/flushing journal timestamp per bucket."""
    if not bucket_ids:
        return {}
    from sqlalchemy import func

    subq = (
        select(
            JournalEntry.bucket_id,
            func.max(JournalEntry.created_at).label("last_change"),
        )
        .where(
            JournalEntry.bucket_id.in_(bucket_ids),
            JournalEntry.event_type.in_(["water_change", "flushing"]),
        )
        .group_by(JournalEntry.bucket_id)
    )
    result = await session.execute(subq)
    return {row.bucket_id: row.last_change for row in result}
