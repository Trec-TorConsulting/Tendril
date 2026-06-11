"""Season comparison API — compare 2-4 grows with normalized time-series."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.grows.models import (
    Bucket,
    BucketSensorReading,
    GrowCycle,
    HarvestYield,
    Strain,
    TentSensorReading,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────────────────


class GrowSummary(BaseModel):
    """Per-grow summary statistics."""

    grow_id: str
    grow_name: str
    grow_type: str
    strain_name: str | None = None
    stage: str
    status: str
    started_at: str
    ended_at: str | None
    duration_days: int | None
    avg_ph: float | None = None
    avg_ec: float | None = None
    avg_vpd: float | None = None
    avg_temp_f: float | None = None
    avg_humidity: float | None = None
    total_dry_weight_oz: float | None = None
    avg_quality: float | None = None


class TimeSeriesPoint(BaseModel):
    """A single data point in a normalized time series."""

    day: int
    value: float | None


class GrowTimeSeries(BaseModel):
    """Time-series data for one grow."""

    grow_id: str
    grow_name: str
    data: list[TimeSeriesPoint]


class CompareResponse(BaseModel):
    """Response from the comparison endpoint."""

    metric: str
    grows: list[GrowTimeSeries]
    summaries: list[GrowSummary]


# ── Routes ─────────────────────────────────────────────────────────────────────


@router.get("/compare", response_model=CompareResponse)
async def compare_grows(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    grow_ids: list[UUID] = Query(..., alias="grow_id", min_length=2, max_length=4),
    metric: str = Query(default="ph", description="Metric to compare: ph, ec, vpd, temp, humidity"),
):
    """Compare 2-4 grows with normalized time-series data (day-in-grow as X axis).

    Returns daily averages for the selected metric aligned by day-in-grow.
    """
    valid_metrics = {"ph", "ec", "vpd", "temp", "humidity", "water_temp"}
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Must be one of: {sorted(valid_metrics)}",
        )

    # Load grows
    grows = []
    for gid in grow_ids:
        grow = await session.get(GrowCycle, gid)
        if grow is None or grow.tenant_id != user.tenant_id:
            raise HTTPException(status_code=404, detail=f"Grow {gid} not found")
        grows.append(grow)

    # Build summaries and time-series for each grow
    summaries = []
    series_list = []

    for grow in grows:
        summary = await _build_grow_summary(session, grow)
        summaries.append(summary)

        ts = await _build_time_series(session, grow, metric)
        series_list.append(
            GrowTimeSeries(
                grow_id=str(grow.id),
                grow_name=grow.name,
                data=ts,
            )
        )

    return CompareResponse(metric=metric, grows=series_list, summaries=summaries)


@router.get("/comparable/{grow_id}")
async def get_comparable_grows(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Find grows comparable to the given one (same strain + grow type)."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None or grow.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Grow not found")

    # Get strain from buckets
    strain_id = await _get_grow_strain_id(session, grow)

    # Find other grows with same grow_type (and optionally same strain)
    stmt = (
        select(GrowCycle)
        .where(
            GrowCycle.tenant_id == user.tenant_id,
            GrowCycle.id != grow.id,
            GrowCycle.grow_type == grow.grow_type,
            GrowCycle.deleted_at.is_(None),
        )
        .order_by(GrowCycle.started_at.desc())
        .limit(10)
    )
    candidates = (await session.execute(stmt)).scalars().all()

    # Score candidates: same strain = higher priority
    result = []
    for c in candidates:
        c_strain = await _get_grow_strain_id(session, c)
        same_strain = strain_id and c_strain and strain_id == c_strain
        result.append(
            {
                "grow_id": str(c.id),
                "grow_name": c.name,
                "grow_type": c.grow_type,
                "status": c.status,
                "started_at": c.started_at.isoformat() if c.started_at else None,
                "same_strain": same_strain,
            }
        )

    # Sort: same strain first, then by date
    result.sort(key=lambda x: (not x["same_strain"], x.get("started_at", "") or ""), reverse=False)
    return result[:6]


# ── Private Helpers ────────────────────────────────────────────────────────────


async def _build_grow_summary(session: AsyncSession, grow: GrowCycle) -> GrowSummary:
    """Build summary statistics for a grow."""
    duration = None
    if grow.started_at:
        end = grow.ended_at or datetime.now(UTC)
        duration = (end - grow.started_at).days

    # Get strain name from first bucket
    strain_name = None
    bucket = (
        await session.execute(select(Bucket).where(Bucket.grow_cycle_id == grow.id).limit(1))
    ).scalar_one_or_none()
    if bucket and bucket.strain_id:
        strain = await session.get(Strain, bucket.strain_id)
        if strain:
            strain_name = strain.name

    # Bucket sensor averages (pH, EC, water_temp)
    bucket_ids = (await session.execute(select(Bucket.id).where(Bucket.grow_cycle_id == grow.id))).scalars().all()

    avg_ph = avg_ec = None
    if bucket_ids:
        row = (
            await session.execute(
                select(
                    func.avg(BucketSensorReading.ph),
                    func.avg(BucketSensorReading.ec),
                ).where(BucketSensorReading.bucket_id.in_(bucket_ids))
            )
        ).one_or_none()
        if row:
            avg_ph = round(row[0], 2) if row[0] else None
            avg_ec = round(row[1], 2) if row[1] else None

    # Tent sensor averages (VPD, temp, humidity)
    avg_vpd = avg_temp = avg_humidity = None
    if grow.tent_id:
        cutoff = grow.started_at if grow.started_at else None
        tent_stmt = select(
            func.avg(TentSensorReading.vpd),
            func.avg(TentSensorReading.ambient_temp_f),
            func.avg(TentSensorReading.ambient_humidity),
        ).where(TentSensorReading.tent_id == grow.tent_id)
        if cutoff:
            tent_stmt = tent_stmt.where(TentSensorReading.recorded_at >= cutoff)
        if grow.ended_at:
            tent_stmt = tent_stmt.where(TentSensorReading.recorded_at <= grow.ended_at)

        tent_row = (await session.execute(tent_stmt)).one_or_none()
        if tent_row:
            avg_vpd = round(tent_row[0], 2) if tent_row[0] else None
            avg_temp = round(tent_row[1], 1) if tent_row[1] else None
            avg_humidity = round(tent_row[2], 1) if tent_row[2] else None

    # Yield totals
    total_dry = avg_quality = None
    if bucket_ids:
        yield_row = (
            await session.execute(
                select(
                    func.sum(HarvestYield.dry_weight_oz),
                    func.avg(HarvestYield.quality_rating),
                ).where(HarvestYield.grow_cycle_id == grow.id)
            )
        ).one_or_none()
        if yield_row:
            total_dry = round(yield_row[0], 2) if yield_row[0] else None
            avg_quality = round(yield_row[1], 1) if yield_row[1] else None

    return GrowSummary(
        grow_id=str(grow.id),
        grow_name=grow.name,
        grow_type=grow.grow_type,
        strain_name=strain_name,
        stage=grow.stage,
        status=grow.status,
        started_at=grow.started_at.isoformat() if grow.started_at else "",
        ended_at=grow.ended_at.isoformat() if grow.ended_at else None,
        duration_days=duration,
        avg_ph=avg_ph,
        avg_ec=avg_ec,
        avg_vpd=avg_vpd,
        avg_temp_f=avg_temp,
        avg_humidity=avg_humidity,
        total_dry_weight_oz=total_dry,
        avg_quality=avg_quality,
    )


async def _build_time_series(session: AsyncSession, grow: GrowCycle, metric: str) -> list[TimeSeriesPoint]:
    """Build normalized time-series data (day-in-grow as X axis) for a metric."""
    if not grow.started_at:
        return []

    start = grow.started_at
    end = grow.ended_at or datetime.now(UTC)
    max_days = min((end - start).days + 1, 200)  # Cap at 200 days

    # Determine which table and column to query
    if metric in ("ph", "ec", "water_temp"):
        return await _bucket_metric_series(session, grow, metric, start, max_days)
    else:
        return await _tent_metric_series(session, grow, metric, start, max_days)


async def _bucket_metric_series(
    session: AsyncSession, grow: GrowCycle, metric: str, start: datetime, max_days: int
) -> list[TimeSeriesPoint]:
    """Get daily averages from bucket sensor readings."""
    column_map = {
        "ph": BucketSensorReading.ph,
        "ec": BucketSensorReading.ec,
        "water_temp": BucketSensorReading.water_temp_f,
    }
    col = column_map[metric]

    bucket_ids = (await session.execute(select(Bucket.id).where(Bucket.grow_cycle_id == grow.id))).scalars().all()

    if not bucket_ids:
        return []

    points: list[TimeSeriesPoint] = []
    for day in range(max_days):
        day_start = start + timedelta(days=day)
        day_end = day_start + timedelta(days=1)

        avg_val = (
            await session.execute(
                select(func.avg(col)).where(
                    BucketSensorReading.bucket_id.in_(bucket_ids),
                    BucketSensorReading.recorded_at >= day_start,
                    BucketSensorReading.recorded_at < day_end,
                )
            )
        ).scalar_one_or_none()

        points.append(TimeSeriesPoint(day=day + 1, value=round(avg_val, 2) if avg_val else None))

    return points


async def _tent_metric_series(
    session: AsyncSession, grow: GrowCycle, metric: str, start: datetime, max_days: int
) -> list[TimeSeriesPoint]:
    """Get daily averages from tent sensor readings."""
    column_map = {
        "vpd": TentSensorReading.vpd,
        "temp": TentSensorReading.ambient_temp_f,
        "humidity": TentSensorReading.ambient_humidity,
    }
    col = column_map.get(metric)
    if col is None or not grow.tent_id:
        return []

    points: list[TimeSeriesPoint] = []
    for day in range(max_days):
        day_start = start + timedelta(days=day)
        day_end = day_start + timedelta(days=1)

        avg_val = (
            await session.execute(
                select(func.avg(col)).where(
                    TentSensorReading.tent_id == grow.tent_id,
                    TentSensorReading.recorded_at >= day_start,
                    TentSensorReading.recorded_at < day_end,
                )
            )
        ).scalar_one_or_none()

        points.append(TimeSeriesPoint(day=day + 1, value=round(avg_val, 2) if avg_val else None))

    return points


async def _get_grow_strain_id(session: AsyncSession, grow: GrowCycle) -> UUID | None:
    """Get the strain ID from the first bucket in a grow."""
    bucket = (
        await session.execute(
            select(Bucket.strain_id)
            .where(
                Bucket.grow_cycle_id == grow.id,
                Bucket.strain_id.isnot(None),
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    return bucket
