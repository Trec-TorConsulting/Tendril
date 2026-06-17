"""Season comparison API — compare 2-4 grows with normalized time-series.

This module is HTTP-only. All persistence, aggregation, and metric
dispatch live in ``app.analytics.service``.
"""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics import service
from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session

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
    try:
        service.validate_metric(metric)
    except service.InvalidMetricError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Must be one of: {sorted(service.VALID_METRICS)}",
        ) from exc

    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    # Load grows + check tenant ownership up front so we surface 404 before
    # spending time on the (potentially expensive) summary/series queries.
    grows = []
    for gid in grow_ids:
        grow = await service.get_tenant_grow(session, tenant_id=user.tenant_id, grow_id=gid)
        if grow is None:
            raise HTTPException(status_code=404, detail=f"Grow {gid} not found")
        grows.append(grow)

    summaries: list[GrowSummary] = []
    series_list: list[GrowTimeSeries] = []

    for grow in grows:
        s = await service.build_grow_summary(session, grow)
        summaries.append(
            GrowSummary(
                grow_id=str(s.grow_id),
                grow_name=s.grow_name,
                grow_type=s.grow_type,
                strain_name=s.strain_name,
                stage=s.stage,
                status=s.status,
                started_at=s.started_at.isoformat() if s.started_at else "",
                ended_at=s.ended_at.isoformat() if s.ended_at else None,
                duration_days=s.duration_days,
                avg_ph=s.avg_ph,
                avg_ec=s.avg_ec,
                avg_vpd=s.avg_vpd,
                avg_temp_f=s.avg_temp_f,
                avg_humidity=s.avg_humidity,
                total_dry_weight_oz=s.total_dry_weight_oz,
                avg_quality=s.avg_quality,
            )
        )

        ts = await service.build_time_series(session, grow, metric)
        series_list.append(
            GrowTimeSeries(
                grow_id=str(grow.id),
                grow_name=grow.name,
                data=[TimeSeriesPoint(day=p.day, value=p.value) for p in ts],
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
    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    grow = await service.get_tenant_grow(session, tenant_id=user.tenant_id, grow_id=grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow not found")

    strain_id = await service.get_grow_strain_id(session, grow)
    candidates = await service.list_comparable_candidates(session, tenant_id=user.tenant_id, grow=grow)

    rows = []
    for c in candidates:
        c_strain = await service.get_grow_strain_id(session, c)
        same_strain = bool(strain_id and c_strain and strain_id == c_strain)
        rows.append(
            {
                "grow_id": str(c.id),
                "grow_name": c.name,
                "grow_type": c.grow_type,
                "status": c.status,
                "started_at": c.started_at.isoformat() if c.started_at else None,
                "same_strain": same_strain,
            }
        )

    return service.rank_comparable_candidates(rows)
