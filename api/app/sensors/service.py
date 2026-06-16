"""Sensors domain service.

Holds the business operations for bucket-level and tent-level sensor
readings, including the related analytics (drift over a window, trend
extraction). Route handlers in ``app.sensors.routes`` and
``app.sensors.tent_routes`` are HTTP-only — request parsing, response
shaping, and ``HTTPException`` raising — and delegate to this module.

Conventions match the project standard established by
``app.automation.service`` (PR #192):

* The first positional argument is always ``session: AsyncSession``.
* Functions return ORM model instances or plain values; they never
  raise ``HTTPException`` — lookup misses return ``None``.
* Query-builder helpers (``*_query``) return SQLAlchemy ``Select``
  objects so the route layer can hand them to ``app.pagination.paginate``.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import BucketSensorReading, TentSensorReading

logger = logging.getLogger("tendril.sensors")


# ─────────────────────────────────────────────────────────────────────────────
# Bucket sensor readings
# ─────────────────────────────────────────────────────────────────────────────


def _derive_ec_ppm(data: dict[str, Any]) -> dict[str, Any]:
    """Auto-derive EC↔PPM when only one of the pair is provided.

    Uses the 500-scale conversion (PPM_500 = EC_mScm * 500). Mutates and
    returns ``data`` so callers can chain.
    """
    if data.get("ec") is not None and data.get("ppm") is None:
        data["ppm"] = round(data["ec"] * 500.0, 1)
    elif data.get("ppm") is not None and data.get("ec") is None:
        data["ec"] = round(data["ppm"] / 500.0, 3)
    return data


async def create_bucket_reading(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    data: dict[str, Any],
) -> BucketSensorReading:
    """Record a new bucket sensor reading.

    Performs three side effects beyond the simple insert:
      1. Auto-derives missing EC↔PPM from the provided pair member.
      2. Propagates the reading to all site buckets when the source
         bucket is an RDWC header bucket.
      3. Best-effort real-time alert evaluation (critical / composite /
         trend). Failures here are logged at DEBUG and never surface to
         the caller — they must not block reading ingest.
    """
    # Local import to avoid pulling integrations into this module's import
    # graph at startup — matches the original route-level pattern.
    from app.integrations.connectors.base import propagate_header_bucket_readings

    data = _derive_ec_ppm(dict(data))
    reading = BucketSensorReading(tenant_id=tenant_id, **data)
    session.add(reading)
    await session.flush()  # Surface the row so propagation can reference it.

    await propagate_header_bucket_readings(session, str(reading.bucket_id), reading)

    await session.commit()
    await session.refresh(reading)

    await _evaluate_realtime_alerts(session, tenant_id=tenant_id, reading=reading)

    return reading


async def _evaluate_realtime_alerts(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    reading: BucketSensorReading,
) -> None:
    """Best-effort alert evaluation triggered by a new bucket reading."""
    try:
        from app.automation.engine import (
            evaluate_composite_alerts,
            evaluate_critical_alerts,
            evaluate_trend_alerts,
        )
        from app.grows.models import Bucket, GrowCycle

        bucket = await session.get(Bucket, reading.bucket_id)
        if bucket is None or bucket.grow_cycle_id is None:
            return
        grow = await session.get(GrowCycle, bucket.grow_cycle_id)
        if grow is None:
            return
        await evaluate_critical_alerts(session, grow.grow_type, tenant_id, grow.id, reading)
        await evaluate_composite_alerts(session, grow.grow_type, tenant_id, grow.id, reading)
        await evaluate_trend_alerts(session, grow.grow_type, tenant_id, grow.id, reading.bucket_id)
    except Exception:
        logger.debug("Alert evaluation failed for reading %s", reading.id, exc_info=True)


def list_bucket_readings_query(
    *,
    tenant_id: UUID,
    bucket_id: UUID | None = None,
) -> Select:
    """Build the query for listing bucket readings; route layer paginates it."""
    q = (
        select(BucketSensorReading)
        .where(BucketSensorReading.tenant_id == tenant_id)
        .order_by(desc(BucketSensorReading.recorded_at))
    )
    if bucket_id is not None:
        q = q.where(BucketSensorReading.bucket_id == bucket_id)
    return q


async def get_latest_bucket_reading(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    bucket_id: UUID,
) -> BucketSensorReading | None:
    """Return the most recent reading for a bucket, or ``None`` if none exist."""
    result = await session.execute(
        select(BucketSensorReading)
        .where(BucketSensorReading.tenant_id == tenant_id)
        .where(BucketSensorReading.bucket_id == bucket_id)
        .order_by(desc(BucketSensorReading.recorded_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_recent_bucket_readings(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    bucket_id: UUID,
    since: datetime,
) -> list[BucketSensorReading]:
    """Return all readings for a bucket since ``since``, oldest first."""
    result = await session.execute(
        select(BucketSensorReading)
        .where(BucketSensorReading.tenant_id == tenant_id)
        .where(BucketSensorReading.bucket_id == bucket_id)
        .where(BucketSensorReading.recorded_at >= since)
        .order_by(BucketSensorReading.recorded_at)
    )
    return list(result.scalars().all())


def compute_drift_stats(values: list[float]) -> dict[str, Any] | None:
    """Compute min/max/first/last/delta/count for a series.

    Returns ``None`` when fewer than two samples are present (delta is
    undefined for a single observation).
    """
    if len(values) < 2:
        return None
    return {
        "min": min(values),
        "max": max(values),
        "first": values[0],
        "last": values[-1],
        "delta": round(values[-1] - values[0], 3),
        "count": len(values),
    }


async def compute_bucket_drift(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    bucket_id: UUID,
    hours: int,
) -> dict[str, dict[str, Any] | None]:
    """Compute pH / EC / ORP drift over the trailing ``hours`` window."""
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    readings = await list_recent_bucket_readings(session, tenant_id=tenant_id, bucket_id=bucket_id, since=cutoff)
    return {
        "ph": compute_drift_stats([r.ph for r in readings if r.ph is not None]),
        "ec": compute_drift_stats([r.ec for r in readings if r.ec is not None]),
        "orp": compute_drift_stats([r.orp for r in readings if r.orp is not None]),
    }


async def get_bucket_reading(session: AsyncSession, reading_id: UUID) -> BucketSensorReading | None:
    return await session.get(BucketSensorReading, reading_id)


async def delete_bucket_reading(session: AsyncSession, reading: BucketSensorReading) -> None:
    await session.delete(reading)
    await session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Tent sensor readings
# ─────────────────────────────────────────────────────────────────────────────


async def create_tent_reading(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    data: dict[str, Any],
) -> TentSensorReading:
    """Record a new tent-level sensor reading."""
    reading = TentSensorReading(tenant_id=tenant_id, **data)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


def list_tent_readings_query(
    *,
    tenant_id: UUID,
    tent_id: UUID | None = None,
) -> Select:
    """Build the query for listing tent readings; route layer paginates it."""
    q = (
        select(TentSensorReading)
        .where(TentSensorReading.tenant_id == tenant_id)
        .order_by(desc(TentSensorReading.recorded_at))
    )
    if tent_id is not None:
        q = q.where(TentSensorReading.tent_id == tent_id)
    return q


async def get_latest_tent_reading(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    tent_id: UUID,
) -> TentSensorReading | None:
    """Return the most recent reading for a tent, or ``None`` if none exist."""
    result = await session.execute(
        select(TentSensorReading)
        .where(TentSensorReading.tenant_id == tenant_id)
        .where(TentSensorReading.tent_id == tent_id)
        .order_by(desc(TentSensorReading.recorded_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_recent_tent_readings(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    tent_id: UUID,
    since: datetime,
) -> list[TentSensorReading]:
    """Return all readings for a tent since ``since``, oldest first."""
    result = await session.execute(
        select(TentSensorReading)
        .where(TentSensorReading.tenant_id == tenant_id)
        .where(TentSensorReading.tent_id == tent_id)
        .where(TentSensorReading.recorded_at >= since)
        .order_by(TentSensorReading.recorded_at)
    )
    return list(result.scalars().all())


async def get_tent_reading(session: AsyncSession, reading_id: UUID) -> TentSensorReading | None:
    return await session.get(TentSensorReading, reading_id)


async def delete_tent_reading(session: AsyncSession, reading: TentSensorReading) -> None:
    await session.delete(reading)
    await session.commit()
