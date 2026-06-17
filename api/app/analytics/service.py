"""Analytics domain service.

Holds the business operations for season-compare and comparable-grow
discovery: per-grow summary aggregation, day-in-grow normalized
time-series, strain lookup, and comparable-candidate ranking.

Route handlers in ``app.analytics.routes`` are HTTP-only and delegate
to this module.

Conventions match the project standard (PR #192 / #208-#216):

* First positional argument is always ``session: AsyncSession``.
* Functions return ORM, dataclasses, or primitives; they never raise
  ``HTTPException`` — lookup misses return ``None`` and validation
  failures raise typed errors.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import (
    Bucket,
    BucketSensorReading,
    GrowCycle,
    HarvestYield,
    Strain,
    TentSensorReading,
)

# Public metric set — single source of truth.  Bucket-side metrics are
# served from ``BucketSensorReading``; tent-side metrics from
# ``TentSensorReading``.  The split is exposed via the two constants
# below so route validation and dispatch share one definition.
BUCKET_METRICS: frozenset[str] = frozenset({"ph", "ec", "water_temp"})
TENT_METRICS: frozenset[str] = frozenset({"vpd", "temp", "humidity"})
VALID_METRICS: frozenset[str] = BUCKET_METRICS | TENT_METRICS

# Time-series day cap so a 5-year-old "grow" can't generate 1800 day
# buckets and starve the event loop.
MAX_SERIES_DAYS: int = 200


class InvalidMetricError(Exception):
    """Raised when a caller asks for an unknown metric. Route → 400."""

    def __init__(self, metric: str) -> None:
        self.metric = metric
        super().__init__(f"Invalid metric: {metric!r}")


def validate_metric(metric: str) -> None:
    """Assert ``metric`` is in :data:`VALID_METRICS`; raise otherwise."""
    if metric not in VALID_METRICS:
        raise InvalidMetricError(metric)


# ─────────────────────────────────────────────────────────────────────────────
# Per-grow summary
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class GrowSummaryData:
    """Aggregated KPI snapshot for a single grow."""

    grow_id: UUID
    grow_name: str
    grow_type: str
    strain_name: str | None
    stage: str
    status: str
    started_at: datetime | None
    ended_at: datetime | None
    duration_days: int | None
    avg_ph: float | None
    avg_ec: float | None
    avg_vpd: float | None
    avg_temp_f: float | None
    avg_humidity: float | None
    total_dry_weight_oz: float | None
    avg_quality: float | None


def compute_duration_days(grow: GrowCycle, *, now: datetime | None = None) -> int | None:
    """Days between ``grow.started_at`` and ``grow.ended_at`` (or ``now``)."""
    if grow.started_at is None:
        return None
    end = grow.ended_at or (now or datetime.now(UTC))
    return (end - grow.started_at).days


async def _list_grow_bucket_ids(session: AsyncSession, grow: GrowCycle) -> list[UUID]:
    """Return the ids of all buckets that belong to ``grow``."""
    result = await session.execute(select(Bucket.id).where(Bucket.grow_cycle_id == grow.id))
    return list(result.scalars().all())


async def _get_first_bucket_strain_name(session: AsyncSession, grow: GrowCycle) -> str | None:
    """Look up the strain name from the first bucket of ``grow``."""
    bucket = (
        await session.execute(select(Bucket).where(Bucket.grow_cycle_id == grow.id).limit(1))
    ).scalar_one_or_none()
    if bucket is None or bucket.strain_id is None:
        return None
    strain = await session.get(Strain, bucket.strain_id)
    return strain.name if strain else None


def _round_optional(value: Any, ndigits: int) -> float | None:
    """Round ``value`` only when truthy. Matches previous route behaviour
    (``0`` and ``None`` both become ``None``)."""
    return round(value, ndigits) if value else None


async def _get_bucket_averages(session: AsyncSession, bucket_ids: list[UUID]) -> tuple[float | None, float | None]:
    """Average pH + EC across the given buckets. Returns ``(None, None)``
    when there are no buckets."""
    if not bucket_ids:
        return (None, None)
    row = (
        await session.execute(
            select(
                func.avg(BucketSensorReading.ph),
                func.avg(BucketSensorReading.ec),
            ).where(BucketSensorReading.bucket_id.in_(bucket_ids))
        )
    ).one_or_none()
    if row is None:
        return (None, None)
    return (_round_optional(row[0], 2), _round_optional(row[1], 2))


async def _get_tent_averages(session: AsyncSession, grow: GrowCycle) -> tuple[float | None, float | None, float | None]:
    """Average VPD / ambient temp / ambient humidity for the grow's tent
    over the grow's date range. Returns ``(None, None, None)`` when the
    grow has no tent."""
    if grow.tent_id is None:
        return (None, None, None)

    stmt = select(
        func.avg(TentSensorReading.vpd),
        func.avg(TentSensorReading.ambient_temp_f),
        func.avg(TentSensorReading.ambient_humidity),
    ).where(TentSensorReading.tent_id == grow.tent_id)
    if grow.started_at:
        stmt = stmt.where(TentSensorReading.recorded_at >= grow.started_at)
    if grow.ended_at:
        stmt = stmt.where(TentSensorReading.recorded_at <= grow.ended_at)

    row = (await session.execute(stmt)).one_or_none()
    if row is None:
        return (None, None, None)
    return (
        _round_optional(row[0], 2),
        _round_optional(row[1], 1),
        _round_optional(row[2], 1),
    )


async def _get_yield_totals(
    session: AsyncSession, grow: GrowCycle, bucket_ids: list[UUID]
) -> tuple[float | None, float | None]:
    """Return ``(total_dry_oz, avg_quality)`` for a grow's yields.

    Matches previous route behaviour: the yield query is only issued
    when the grow has at least one bucket (yields are bucket-scoped).
    """
    if not bucket_ids:
        return (None, None)
    row = (
        await session.execute(
            select(
                func.sum(HarvestYield.dry_weight_oz),
                func.avg(HarvestYield.quality_rating),
            ).where(HarvestYield.grow_cycle_id == grow.id)
        )
    ).one_or_none()
    if row is None:
        return (None, None)
    return (_round_optional(row[0], 2), _round_optional(row[1], 1))


async def build_grow_summary(session: AsyncSession, grow: GrowCycle) -> GrowSummaryData:
    """Aggregate the per-grow KPI snapshot used by the comparison API."""
    bucket_ids = await _list_grow_bucket_ids(session, grow)
    strain_name = await _get_first_bucket_strain_name(session, grow)
    avg_ph, avg_ec = await _get_bucket_averages(session, bucket_ids)
    avg_vpd, avg_temp, avg_humidity = await _get_tent_averages(session, grow)
    total_dry, avg_quality = await _get_yield_totals(session, grow, bucket_ids)

    return GrowSummaryData(
        grow_id=grow.id,
        grow_name=grow.name,
        grow_type=grow.grow_type,
        strain_name=strain_name,
        stage=grow.stage,
        status=grow.status,
        started_at=grow.started_at,
        ended_at=grow.ended_at,
        duration_days=compute_duration_days(grow),
        avg_ph=avg_ph,
        avg_ec=avg_ec,
        avg_vpd=avg_vpd,
        avg_temp_f=avg_temp,
        avg_humidity=avg_humidity,
        total_dry_weight_oz=total_dry,
        avg_quality=avg_quality,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Time-series (day-in-grow X-axis)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TimeSeriesPointData:
    """A single (day, value) point in a normalized time series."""

    day: int
    value: float | None


def compute_series_day_count(grow: GrowCycle, *, now: datetime | None = None, cap: int = MAX_SERIES_DAYS) -> int:
    """Number of day-buckets to render for ``grow``, capped at ``cap``."""
    if grow.started_at is None:
        return 0
    end = grow.ended_at or (now or datetime.now(UTC))
    return min((end - grow.started_at).days + 1, cap)


_BUCKET_COLUMN_MAP = {
    "ph": BucketSensorReading.ph,
    "ec": BucketSensorReading.ec,
    "water_temp": BucketSensorReading.water_temp_f,
}

_TENT_COLUMN_MAP = {
    "vpd": TentSensorReading.vpd,
    "temp": TentSensorReading.ambient_temp_f,
    "humidity": TentSensorReading.ambient_humidity,
}


async def _bucket_metric_series(
    session: AsyncSession,
    grow: GrowCycle,
    metric: str,
    *,
    start: datetime,
    days: int,
) -> list[TimeSeriesPointData]:
    """Per-day average for a bucket-side metric."""
    col = _BUCKET_COLUMN_MAP[metric]
    bucket_ids = await _list_grow_bucket_ids(session, grow)
    if not bucket_ids:
        return []

    out: list[TimeSeriesPointData] = []
    for day in range(days):
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
        out.append(TimeSeriesPointData(day=day + 1, value=_round_optional(avg_val, 2)))
    return out


async def _tent_metric_series(
    session: AsyncSession,
    grow: GrowCycle,
    metric: str,
    *,
    start: datetime,
    days: int,
) -> list[TimeSeriesPointData]:
    """Per-day average for a tent-side metric."""
    col = _TENT_COLUMN_MAP[metric]
    if grow.tent_id is None:
        return []

    out: list[TimeSeriesPointData] = []
    for day in range(days):
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
        out.append(TimeSeriesPointData(day=day + 1, value=_round_optional(avg_val, 2)))
    return out


async def build_time_series(session: AsyncSession, grow: GrowCycle, metric: str) -> list[TimeSeriesPointData]:
    """Build the normalized time-series for ``metric`` on ``grow``.

    Caller must have validated ``metric`` via :func:`validate_metric`.
    """
    if grow.started_at is None:
        return []
    days = compute_series_day_count(grow)
    if metric in BUCKET_METRICS:
        return await _bucket_metric_series(session, grow, metric, start=grow.started_at, days=days)
    return await _tent_metric_series(session, grow, metric, start=grow.started_at, days=days)


# ─────────────────────────────────────────────────────────────────────────────
# Tenant-scoped grow lookup + comparable discovery
# ─────────────────────────────────────────────────────────────────────────────


async def get_tenant_grow(session: AsyncSession, *, tenant_id: UUID, grow_id: UUID) -> GrowCycle | None:
    """Fetch ``grow_id`` only when it belongs to ``tenant_id``.

    Returns ``None`` both for unknown ids and for cross-tenant access —
    the route maps either case to 404 so we don't leak existence.
    """
    grow = await session.get(GrowCycle, grow_id)
    if grow is None or grow.tenant_id != tenant_id:
        return None
    return grow


async def get_grow_strain_id(session: AsyncSession, grow: GrowCycle) -> UUID | None:
    """Return the first non-null ``strain_id`` from any bucket in ``grow``."""
    return (
        await session.execute(
            select(Bucket.strain_id)
            .where(
                Bucket.grow_cycle_id == grow.id,
                Bucket.strain_id.isnot(None),
            )
            .limit(1)
        )
    ).scalar_one_or_none()


async def list_comparable_candidates(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    grow: GrowCycle,
    limit: int = 10,
) -> list[GrowCycle]:
    """Other live grows in the same tenant + grow type, most-recent first."""
    result = await session.execute(
        select(GrowCycle)
        .where(
            GrowCycle.tenant_id == tenant_id,
            GrowCycle.id != grow.id,
            GrowCycle.grow_type == grow.grow_type,
            GrowCycle.deleted_at.is_(None),
        )
        .order_by(GrowCycle.started_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


def rank_comparable_candidates(candidates: Iterable[dict], *, top: int = 6) -> list[dict]:
    """Sort same-strain matches first, then by ``started_at`` (no key →
    treated as empty string, matching previous behaviour). Returns at
    most ``top`` rows."""
    # Sorting on a tuple of (not-same_strain, started_at_or_empty) gives:
    #   * same-strain rows first (False sorts before True),
    #   * within each group, oldest-first because the original sort wasn't
    #     reversed.  (Preserving prior behaviour byte-for-byte.)
    rows = sorted(
        candidates,
        key=lambda x: (not x.get("same_strain"), x.get("started_at", "") or ""),
    )
    return rows[:top]
