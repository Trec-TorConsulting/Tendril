"""Data management — retention and CSV export."""

from __future__ import annotations

import csv
import io
import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("tendril.data")

# Default retention periods in days (overridable per tenant)
DEFAULT_RETENTION = {
    "sensor_readings": 365,  # 1 year
    "weather_readings": 180,  # 6 months
    "alert_history": 90,  # 3 months
    "notification_log": 30,  # 1 month
}


async def enforce_retention(session: AsyncSession) -> dict[str, int]:
    """Delete data older than retention period. Returns counts of deleted rows."""
    from app.automation.models import AlertHistory
    from app.grows.models import BucketSensorReading, WeatherReading
    from app.notifications.models import NotificationLog

    now = datetime.now(UTC)
    deleted = {}

    table_map = {
        "sensor_readings": (BucketSensorReading, BucketSensorReading.recorded_at, DEFAULT_RETENTION["sensor_readings"]),
        "weather_readings": (WeatherReading, WeatherReading.recorded_at, DEFAULT_RETENTION["weather_readings"]),
        "alert_history": (AlertHistory, AlertHistory.created_at, DEFAULT_RETENTION["alert_history"]),
        "notification_log": (NotificationLog, NotificationLog.created_at, DEFAULT_RETENTION["notification_log"]),
    }

    for name, (model, ts_col, days) in table_map.items():
        cutoff = now - timedelta(days=days)
        result = await session.execute(delete(model).where(ts_col < cutoff))
        deleted[name] = result.rowcount  # type: ignore[attr-defined]

    await session.commit()
    return deleted


async def export_bucket_csv(session: AsyncSession, bucket_id: UUID) -> str:
    """Export all sensor readings for a bucket as CSV string."""
    from app.grows.models import BucketSensorReading

    readings = (
        (
            await session.execute(
                select(BucketSensorReading)
                .where(BucketSensorReading.bucket_id == bucket_id)
                .order_by(BucketSensorReading.recorded_at)
            )
        )
        .scalars()
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    columns = [
        "recorded_at",
        "ph",
        "ec",
        "ppm",
        "water_temp_f",
        "water_level_pct",
        "dissolved_oxygen",
        "flow_rate",
        "mist_pressure",
        "soil_moisture",
        "soil_temp",
        "runoff_ph",
        "runoff_ec",
        "ambient_temp_f",
        "ambient_humidity",
    ]
    writer.writerow(columns)

    for r in readings:
        writer.writerow(
            [
                r.recorded_at.isoformat() if r.recorded_at else "",
                r.ph,
                r.ec,
                r.ppm,
                r.water_temp_f,
                r.water_level_pct,
                r.dissolved_oxygen,
                r.flow_rate,
                r.mist_pressure,
                r.soil_moisture,
                r.soil_temp,
                r.runoff_ph,
                r.runoff_ec,
                r.ambient_temp_f,
                r.ambient_humidity,
            ]
        )

    return output.getvalue()


async def export_grow_csv(session: AsyncSession, grow_cycle_id: UUID) -> str:
    """Export full grow data (grow info + all bucket readings) as CSV."""
    from app.grows.models import Bucket, BucketSensorReading, GrowCycle

    grow = await session.get(GrowCycle, grow_cycle_id)
    if not grow:
        return ""

    # Get all buckets
    buckets = (await session.execute(select(Bucket).where(Bucket.grow_cycle_id == grow_cycle_id))).scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Grow info section
    writer.writerow(["# Grow Cycle Info"])
    writer.writerow(["Name", grow.name or ""])
    writer.writerow(["Grow Type", grow.grow_type or ""])
    writer.writerow(["Stage", grow.stage or ""])
    writer.writerow(["Start Date", grow.created_at.isoformat() if grow.created_at else ""])
    writer.writerow([])

    # Sensor readings
    columns = [
        "bucket_label",
        "recorded_at",
        "ph",
        "ec",
        "ppm",
        "water_temp_f",
        "water_level_pct",
        "dissolved_oxygen",
        "flow_rate",
        "mist_pressure",
        "soil_moisture",
        "soil_temp",
        "runoff_ph",
        "runoff_ec",
        "ambient_temp_f",
        "ambient_humidity",
    ]
    writer.writerow(columns)

    for bucket in buckets:
        readings = (
            (
                await session.execute(
                    select(BucketSensorReading)
                    .where(BucketSensorReading.bucket_id == bucket.id)
                    .order_by(BucketSensorReading.recorded_at)
                )
            )
            .scalars()
            .all()
        )

        label = bucket.label or f"bucket-{str(bucket.id)[:8]}"
        for r in readings:
            writer.writerow(
                [
                    label,
                    r.recorded_at.isoformat() if r.recorded_at else "",
                    r.ph,
                    r.ec,
                    r.ppm,
                    r.water_temp_f,
                    r.water_level_pct,
                    r.dissolved_oxygen,
                    r.flow_rate,
                    r.mist_pressure,
                    r.soil_moisture,
                    r.soil_temp,
                    r.runoff_ph,
                    r.runoff_ec,
                    r.ambient_temp_f,
                    r.ambient_humidity,
                ]
            )

    return output.getvalue()


async def export_sensor_data_csv(
    session: AsyncSession,
    bucket_id: UUID,
    start: datetime | None = None,
    end: datetime | None = None,
) -> str:
    """Export sensor readings for a bucket with optional date range filtering."""
    from app.grows.models import BucketSensorReading

    query = (
        select(BucketSensorReading)
        .where(BucketSensorReading.bucket_id == bucket_id)
        .order_by(BucketSensorReading.recorded_at)
    )
    if start:
        query = query.where(BucketSensorReading.recorded_at >= start)
    if end:
        query = query.where(BucketSensorReading.recorded_at <= end)

    readings = (await session.execute(query)).scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    columns = [
        "recorded_at",
        "ph",
        "ec",
        "ppm",
        "water_temp_f",
        "water_level_pct",
        "dissolved_oxygen",
        "flow_rate",
        "mist_pressure",
        "soil_moisture",
        "soil_temp",
        "runoff_ph",
        "runoff_ec",
        "ambient_temp_f",
        "ambient_humidity",
    ]
    writer.writerow(columns)

    for r in readings:
        writer.writerow(
            [
                r.recorded_at.isoformat() if r.recorded_at else "",
                r.ph,
                r.ec,
                r.ppm,
                r.water_temp_f,
                r.water_level_pct,
                r.dissolved_oxygen,
                r.flow_rate,
                r.mist_pressure,
                r.soil_moisture,
                r.soil_temp,
                r.runoff_ph,
                r.runoff_ec,
                r.ambient_temp_f,
                r.ambient_humidity,
            ]
        )

    return output.getvalue()


async def export_tasks_csv(session: AsyncSession, grow_cycle_id: UUID) -> str:
    """Export all tasks for a grow as CSV."""
    from app.commercial.models import Task

    tasks = (
        (await session.execute(select(Task).where(Task.grow_cycle_id == grow_cycle_id).order_by(desc(Task.created_at))))
        .scalars()
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["title", "status", "priority", "due_at", "completed_at", "category", "created_at"])

    for t in tasks:
        writer.writerow(
            [
                t.title,
                t.status,
                t.priority,
                t.due_date.isoformat() if t.due_date else "",
                t.completed_at.isoformat() if t.completed_at else "",
                getattr(t, "category", ""),
                t.created_at.isoformat() if t.created_at else "",
            ]
        )

    return output.getvalue()


async def export_journal_csv(session: AsyncSession, grow_cycle_id: UUID) -> str:
    """Export journal entries for a grow as CSV."""
    from app.grows.models import JournalEntry

    entries = (
        (
            await session.execute(
                select(JournalEntry)
                .where(JournalEntry.grow_cycle_id == grow_cycle_id)  # type: ignore[attr-defined]
                .order_by(desc(JournalEntry.created_at))
            )
        )
        .scalars()
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "category", "title", "content"])

    for e in entries:
        writer.writerow(
            [
                e.created_at.isoformat() if e.created_at else "",
                getattr(e, "category", ""),
                getattr(e, "title", ""),
                getattr(e, "content", ""),
            ]
        )

    return output.getvalue()
