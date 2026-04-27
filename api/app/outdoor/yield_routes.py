"""Harvest yield API — per-plant yield tracking and analytics for outdoor grows."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import GrowCycle, Bucket, HarvestYield, PlotGrid
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


# ---------- Schemas ----------

class YieldCreate(BaseModel):
    bucket_id: UUID
    harvested_at: datetime | None = None
    wet_weight_oz: float | None = None
    dry_weight_oz: float | None = None
    trim_weight_oz: float | None = None
    quality_rating: int | None = Field(default=None, ge=1, le=10)
    trichome_stage: str | None = None  # clear | cloudy | amber | mixed
    notes: str | None = None


class YieldResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    bucket_id: UUID
    harvested_at: datetime
    wet_weight_oz: float | None
    dry_weight_oz: float | None
    trim_weight_oz: float | None
    quality_rating: int | None
    trichome_stage: str | None
    notes: str | None

    model_config = {"from_attributes": True}


class YieldUpdate(BaseModel):
    wet_weight_oz: float | None = None
    dry_weight_oz: float | None = None
    trim_weight_oz: float | None = None
    quality_rating: int | None = Field(default=None, ge=1, le=10)
    trichome_stage: str | None = None
    notes: str | None = None


class YieldSummary(BaseModel):
    total_plants: int
    plants_harvested: int
    total_wet_oz: float
    total_dry_oz: float
    total_trim_oz: float
    avg_dry_per_plant_oz: float
    avg_quality: float | None
    yield_per_sqft_oz: float | None


# ---------- Endpoints ----------

@router.post("/{grow_id}/yields", response_model=YieldResponse, status_code=201)
async def create_yield(
    grow_id: UUID,
    body: YieldCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log a harvest yield for a plant."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow not found")
    bucket = await session.get(Bucket, body.bucket_id)
    if bucket is None or bucket.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Plant/bucket not found in this grow")

    entry = HarvestYield(
        tenant_id=user.tenant_id,
        grow_cycle_id=grow_id,
        **body.model_dump(),
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


@router.get("/{grow_id}/yields")
async def list_yields(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all harvest yields for a grow."""
    q = (
        select(HarvestYield)
        .where(HarvestYield.grow_cycle_id == grow_id)
        .order_by(desc(HarvestYield.harvested_at))
    )
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{grow_id}/yields/{yield_id}", response_model=YieldResponse)
async def get_yield(
    grow_id: UUID,
    yield_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single yield entry by ID."""
    entry = await session.get(HarvestYield, yield_id)
    if entry is None or entry.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Yield entry not found")
    return entry


@router.patch("/{grow_id}/yields/{yield_id}", response_model=YieldResponse)
async def update_yield(
    grow_id: UUID,
    yield_id: UUID,
    body: YieldUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a harvest yield entry."""
    entry = await session.get(HarvestYield, yield_id)
    if entry is None or entry.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Yield entry not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await session.commit()
    await session.refresh(entry)
    return entry


@router.get("/{grow_id}/yields/summary", response_model=YieldSummary)
async def get_yield_summary(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get aggregated yield stats for a grow."""
    # Count total buckets/plants
    bucket_count = (await session.execute(
        select(func.count()).where(Bucket.grow_cycle_id == grow_id)
    )).scalar() or 0

    # Aggregate yields
    result = await session.execute(
        select(
            func.count(HarvestYield.id),
            func.coalesce(func.sum(HarvestYield.wet_weight_oz), 0),
            func.coalesce(func.sum(HarvestYield.dry_weight_oz), 0),
            func.coalesce(func.sum(HarvestYield.trim_weight_oz), 0),
            func.avg(HarvestYield.quality_rating),
        ).where(HarvestYield.grow_cycle_id == grow_id)
    )
    row = result.one()
    harvested, wet, dry, trim, avg_quality = row

    avg_dry = dry / harvested if harvested > 0 else 0.0

    # Calculate yield per sqft if plot grid exists
    yield_per_sqft = None
    grid_result = await session.execute(
        select(PlotGrid).where(PlotGrid.grow_cycle_id == grow_id)
    )
    grid = grid_result.scalar_one_or_none()
    if grid and dry > 0:
        sqft = (grid.rows * grid.cell_size_inches * grid.cols * grid.cell_size_inches) / 144
        if sqft > 0:
            yield_per_sqft = round(dry / sqft, 2)

    return YieldSummary(
        total_plants=bucket_count,
        plants_harvested=harvested,
        total_wet_oz=round(wet, 2),
        total_dry_oz=round(dry, 2),
        total_trim_oz=round(trim, 2),
        avg_dry_per_plant_oz=round(avg_dry, 2),
        avg_quality=round(avg_quality, 1) if avg_quality else None,
        yield_per_sqft_oz=yield_per_sqft,
    )


@router.delete("/{grow_id}/yields/{yield_id}", status_code=204)
async def delete_yield(
    grow_id: UUID,
    yield_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a harvest yield entry."""
    entry = await session.get(HarvestYield, yield_id)
    if entry is None or entry.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Yield entry not found")
    await session.delete(entry)
    await session.commit()
