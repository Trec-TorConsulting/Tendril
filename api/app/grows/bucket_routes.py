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
    role: str = "site"  # site | header
    settings: dict | None = None


class BucketUpdate(BaseModel):
    label: str | None = None
    strain_name: str | None = None
    strain_id: UUID | None = None
    growth_stage: str | None = None
    status: str | None = None
    position: int | None = None
    volume_gallons: float | None = None
    role: str | None = None
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
    role: str = "site"
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
    from app.grows.models import GrowCycle

    # Validate role
    if body.role not in ("site", "header"):
        raise HTTPException(status_code=400, detail="Invalid role: must be 'site' or 'header'")

    # Only RDWC grows support a header bucket (shared reservoir)
    if body.role == "header":
        grow = await session.get(GrowCycle, body.grow_cycle_id)
        if not grow:
            raise HTTPException(status_code=404, detail="Grow cycle not found")
        if grow.grow_type != "rdwc":
            raise HTTPException(
                status_code=400,
                detail=f"Header buckets are only supported for RDWC grows, not '{grow.grow_type}'.",
            )
        existing_header = await session.scalar(
            select(Bucket).where(
                Bucket.grow_cycle_id == body.grow_cycle_id,
                Bucket.role == "header",
            )
        )
        if existing_header:
            raise HTTPException(
                status_code=409,
                detail=f"RDWC grow already has a header bucket: {existing_header.label or 'Unnamed'}. "
                "Only one header is allowed per grow. Update the existing header's role to 'site' first.",
            )

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
    from app.grows.models import GrowCycle

    bucket = await session.get(Bucket, bucket_id)
    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")

    updates = body.model_dump(exclude_unset=True)

    # Validate role if being changed
    if "role" in updates and updates["role"] not in ("site", "header"):
        raise HTTPException(status_code=400, detail="Invalid role: must be 'site' or 'header'")

    # For RDWC grows, enforce at most one header and handle transitions
    if "role" in updates and updates["role"] == "header":
        grow = await session.get(GrowCycle, bucket.grow_cycle_id)
        if grow and grow.grow_type == "rdwc":
            existing_header = await session.scalar(
                select(Bucket).where(
                    Bucket.grow_cycle_id == bucket.grow_cycle_id,
                    Bucket.role == "header",
                    Bucket.id != bucket.id,  # Don't count the current bucket
                )
            )
            if existing_header:
                # Auto-demote existing header to site
                existing_header.role = "site"

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
    """Batch-fetch the most recent water_change/flushing journal timestamp per bucket.

    For RDWC grows, a water change on the header bucket counts for all site
    buckets in the same grow (they share the same reservoir).
    """
    if not bucket_ids:
        return {}
    from sqlalchemy import func

    from app.grows.models import GrowCycle

    # Direct water change entries per bucket
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
    water_map: dict[UUID, datetime | None] = {row.bucket_id: row.last_change for row in result}

    # For RDWC grows, propagate the header's water change to site buckets.
    # Find which requested buckets belong to RDWC grows.
    rdwc_buckets = (
        await session.execute(
            select(Bucket.id, Bucket.grow_cycle_id, Bucket.role)
            .join(GrowCycle, Bucket.grow_cycle_id == GrowCycle.id)
            .where(Bucket.id.in_(bucket_ids), GrowCycle.grow_type == "rdwc")
        )
    ).all()

    if rdwc_buckets:
        # Group by grow and find header water change dates
        grow_ids = {b.grow_cycle_id for b in rdwc_buckets}
        header_dates: dict[UUID, datetime | None] = {}
        for grow_id in grow_ids:
            header_row = (
                await session.execute(
                    select(func.max(JournalEntry.created_at))
                    .join(Bucket, JournalEntry.bucket_id == Bucket.id)
                    .where(
                        Bucket.grow_cycle_id == grow_id,
                        Bucket.role == "header",
                        JournalEntry.event_type.in_(["water_change", "flushing"]),
                    )
                )
            ).scalar_one_or_none()
            header_dates[grow_id] = header_row

        # Apply header date to site buckets where it's more recent
        for b in rdwc_buckets:
            if b.role == "header":
                continue
            header_dt = header_dates.get(b.grow_cycle_id)
            if header_dt is None:
                continue
            existing = water_map.get(b.id)
            if existing is None or header_dt > existing:
                water_map[b.id] = header_dt

    return water_map
