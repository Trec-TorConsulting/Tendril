"""Data management — retention and CSV export."""
from __future__ import annotations

import csv
import io
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import delete, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("tendril.data")

# Default retention periods in days (overridable per tenant)
DEFAULT_RETENTION = {
    "sensor_readings": 365,     # 1 year
    "weather_readings": 180,    # 6 months
    "alert_history": 90,        # 3 months
    "notification_log": 30,     # 1 month
}


async def enforce_retention(session: AsyncSession) -> dict[str, int]:
    """Delete data older than retention period. Returns counts of deleted rows."""
    from app.grows.models import BucketSensorReading, WeatherReading
    from app.automation.models import AlertHistory
    from app.notifications.models import NotificationLog

    now = datetime.now(timezone.utc)
    deleted = {}

    table_map = {
        "sensor_readings": (BucketSensorReading, BucketSensorReading.recorded_at, DEFAULT_RETENTION["sensor_readings"]),
        "weather_readings": (WeatherReading, WeatherReading.recorded_at, DEFAULT_RETENTION["weather_readings"]),
        "alert_history": (AlertHistory, AlertHistory.created_at, DEFAULT_RETENTION["alert_history"]),
        "notification_log": (NotificationLog, NotificationLog.created_at, DEFAULT_RETENTION["notification_log"]),
    }

    for name, (model, ts_col, days) in table_map.items():
        cutoff = now - timedelta(days=days)
        result = await session.execute(
            delete(model).where(ts_col < cutoff)
        )
        deleted[name] = result.rowcount

    await session.commit()
    return deleted


async def export_bucket_csv(session: AsyncSession, bucket_id: UUID) -> str:
    """Export all sensor readings for a bucket as CSV string."""
    from app.grows.models import BucketSensorReading

    readings = (await session.execute(
        select(BucketSensorReading)
        .where(BucketSensorReading.bucket_id == bucket_id)
        .order_by(BucketSensorReading.recorded_at)
    )).scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    columns = [
        "recorded_at", "ph", "ec", "water_temp_f", "air_temp_f", "humidity",
        "co2_ppm", "vpd", "light_par", "dissolved_oxygen", "flow_rate",
        "soil_moisture", "soil_temp", "runoff_ph", "runoff_ec", "mist_pressure",
    ]
    writer.writerow(columns)

    for r in readings:
        writer.writerow([
            r.recorded_at.isoformat() if r.recorded_at else "",
            r.ph, r.ec, r.water_temp_f, r.air_temp_f, r.humidity,
            r.co2_ppm, r.vpd, r.light_par,
            getattr(r, "dissolved_oxygen", None),
            getattr(r, "flow_rate", None),
            getattr(r, "soil_moisture", None),
            getattr(r, "soil_temp", None),
            getattr(r, "runoff_ph", None),
            getattr(r, "runoff_ec", None),
            getattr(r, "mist_pressure", None),
        ])

    return output.getvalue()
