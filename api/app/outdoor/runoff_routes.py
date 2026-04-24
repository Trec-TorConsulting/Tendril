"""Runoff reading API — input vs runoff pH/EC tracking for container grows."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import GrowCycle, Bucket, RunoffReading

router = APIRouter()


# ---------- Schemas ----------

class RunoffCreate(BaseModel):
    bucket_id: UUID
    recorded_at: datetime | None = None
    input_ph: float | None = Field(default=None, ge=0, le=14)
    input_ec: float | None = Field(default=None, ge=0, le=20)
    runoff_ph: float | None = Field(default=None, ge=0, le=14)
    runoff_ec: float | None = Field(default=None, ge=0, le=20)
    runoff_pct: float | None = Field(default=None, ge=0, le=100)
    notes: str | None = None


class RunoffResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    bucket_id: UUID
    recorded_at: datetime
    input_ph: float | None
    input_ec: float | None
    runoff_ph: float | None
    runoff_ec: float | None
    runoff_pct: float | None
    notes: str | None

    model_config = {"from_attributes": True}


class RunoffStatsResponse(BaseModel):
    bucket_id: UUID
    reading_count: int
    avg_input_ph: float | None
    avg_input_ec: float | None
    avg_runoff_ph: float | None
    avg_runoff_ec: float | None
    avg_ph_delta: float | None
    avg_ec_delta: float | None
    latest_input_ph: float | None
    latest_input_ec: float | None
    latest_runoff_ph: float | None
    latest_runoff_ec: float | None


# ---------- Endpoints ----------

@router.post("/{grow_id}/runoff", response_model=RunoffResponse, status_code=201)
async def create_runoff_reading(
    grow_id: UUID,
    body: RunoffCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log a runoff reading (input vs runoff pH/EC)."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow not found")

    bucket = await session.get(Bucket, body.bucket_id)
    if bucket is None or bucket.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Bucket not found in this grow")

    data = body.model_dump()
    reading = RunoffReading(tenant_id=user.tenant_id, grow_cycle_id=grow_id, **data)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


@router.get("/{grow_id}/runoff", response_model=list[RunoffResponse])
async def list_runoff_readings(
    grow_id: UUID,
    bucket_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    user: Annotated[CurrentUser, Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_tenant_session)] = None,
):
    """List runoff readings for a grow, optionally filtered by bucket."""
    q = select(RunoffReading).where(RunoffReading.grow_cycle_id == grow_id)
    if bucket_id:
        q = q.where(RunoffReading.bucket_id == bucket_id)
    q = q.order_by(desc(RunoffReading.recorded_at)).limit(limit)
    result = await session.execute(q)
    return result.scalars().all()


@router.get("/{grow_id}/runoff/stats", response_model=list[RunoffStatsResponse])
async def get_runoff_stats(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get aggregated runoff stats per bucket for a grow."""
    # Aggregate stats
    agg_result = await session.execute(
        select(
            RunoffReading.bucket_id,
            func.count(RunoffReading.id).label("reading_count"),
            func.avg(RunoffReading.input_ph).label("avg_input_ph"),
            func.avg(RunoffReading.input_ec).label("avg_input_ec"),
            func.avg(RunoffReading.runoff_ph).label("avg_runoff_ph"),
            func.avg(RunoffReading.runoff_ec).label("avg_runoff_ec"),
        )
        .where(RunoffReading.grow_cycle_id == grow_id)
        .group_by(RunoffReading.bucket_id)
    )
    agg_rows = agg_result.all()

    stats = []
    for row in agg_rows:
        # Get latest reading for this bucket
        latest_result = await session.execute(
            select(RunoffReading)
            .where(
                RunoffReading.grow_cycle_id == grow_id,
                RunoffReading.bucket_id == row.bucket_id,
            )
            .order_by(desc(RunoffReading.recorded_at))
            .limit(1)
        )
        latest = latest_result.scalar_one_or_none()

        avg_ph_delta = None
        if row.avg_runoff_ph is not None and row.avg_input_ph is not None:
            avg_ph_delta = round(row.avg_runoff_ph - row.avg_input_ph, 2)
        avg_ec_delta = None
        if row.avg_runoff_ec is not None and row.avg_input_ec is not None:
            avg_ec_delta = round(row.avg_runoff_ec - row.avg_input_ec, 2)

        stats.append(RunoffStatsResponse(
            bucket_id=row.bucket_id,
            reading_count=row.reading_count,
            avg_input_ph=round(row.avg_input_ph, 2) if row.avg_input_ph else None,
            avg_input_ec=round(row.avg_input_ec, 2) if row.avg_input_ec else None,
            avg_runoff_ph=round(row.avg_runoff_ph, 2) if row.avg_runoff_ph else None,
            avg_runoff_ec=round(row.avg_runoff_ec, 2) if row.avg_runoff_ec else None,
            avg_ph_delta=avg_ph_delta,
            avg_ec_delta=avg_ec_delta,
            latest_input_ph=latest.input_ph if latest else None,
            latest_input_ec=latest.input_ec if latest else None,
            latest_runoff_ph=latest.runoff_ph if latest else None,
            latest_runoff_ec=latest.runoff_ec if latest else None,
        ))

    return stats


@router.delete("/{grow_id}/runoff/{reading_id}", status_code=204)
async def delete_runoff_reading(
    grow_id: UUID,
    reading_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a runoff reading."""
    reading = await session.get(RunoffReading, reading_id)
    if reading is None or reading.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Runoff reading not found")
    await session.delete(reading)
    await session.commit()
