"""MQTT message handlers — parse sensor payloads and store readings."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update

from app.database import async_session_factory
from app.grows.models import (
    Bucket,
    BucketSensorReading,
    GrowCycle,
    TentSensorReading,
)
from app.tenants.models import Device

logger = logging.getLogger("tendril.mqtt.handlers")


async def handle_message(message) -> None:
    """Route MQTT messages based on topic structure."""
    topic_str = str(message.topic)
    topic_parts = topic_str.split("/")

    if len(topic_parts) < 4 or topic_parts[0] != "t" or topic_parts[2] != "d":
        logger.warning("Unexpected topic format: %s", topic_str)
        return

    tenant_id = UUID(topic_parts[1])
    device_id_str = topic_parts[3]

    if len(topic_parts) >= 5 and topic_parts[4] == "status":
        await handle_status_message(device_id_str, message.payload)
    elif len(topic_parts) >= 5 and topic_parts[4] == "sensor":
        sensor_type = "/".join(topic_parts[5:]) if len(topic_parts) > 5 else "readings"
        await handle_sensor_message(tenant_id, device_id_str, sensor_type, message.payload)
    else:
        logger.debug("Unhandled topic: %s", topic_str)


async def handle_sensor_message(tenant_id: UUID, device_id_str: str, sensor_type: str, payload_bytes) -> None:
    """Parse sensor payload and store reading.

    sensor_type "ambient" → tent_sensor_readings (tent-level)
    sensor_type "readings" → bucket_sensor_readings (per-bucket)
    """
    try:
        payload = json.loads(payload_bytes)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Invalid JSON payload from device %s", device_id_str)
        return

    logger.debug(
        "Sensor reading: tenant=%s device=%s type=%s payload=%s",
        tenant_id,
        device_id_str,
        sensor_type,
        payload,
    )

    # Update last_seen on any sensor message
    async with async_session_factory() as session:
        await session.execute(
            update(Device).where(Device.device_id == device_id_str).values(last_seen=datetime.now(UTC))
        )
        await session.commit()

    await store_sensor_reading(tenant_id, device_id_str, sensor_type, payload)


# ── Allowed payload keys for each target table ──────────────────

_BUCKET_SENSOR_FIELDS = {
    "water_temp_f",
    "ph",
    "ec",
    "ppm",
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
}

_TENT_SENSOR_FIELDS = {
    "ambient_temp_f",
    "ambient_humidity",
    "vpd",
    "co2",
    "lux",
    "dew_point_f",
    "par_ppfd",
    "air_pressure",
    "voc",
}


EC_PPM_FACTOR = 500.0  # PPM = EC (mS/cm) x 500 (NaCl/Hanna scale)


def _derive_ec_ppm(values: dict) -> dict:
    """Auto-derive EC from PPM or vice versa when only one is present."""
    ec = values.get("ec")
    ppm = values.get("ppm")
    if ec is not None and ppm is None:
        values["ppm"] = round(ec * EC_PPM_FACTOR, 1)
    elif ppm is not None and ec is None:
        values["ec"] = round(ppm / EC_PPM_FACTOR, 3)
    return values


async def store_sensor_reading(tenant_id: UUID, device_id_str: str, sensor_type: str, payload: dict) -> None:
    """Persist an MQTT sensor payload to the appropriate readings table.

    sensor_type "ambient" → tent_sensor_readings (needs device.tent_id)
    sensor_type "readings" → bucket_sensor_readings (needs device.tent_id + payload.position)
    """
    async with async_session_factory() as session:
        # Look up the device to find its tent assignment
        device = (
            await session.execute(
                select(Device).where(
                    Device.device_id == device_id_str,
                    Device.tenant_id == tenant_id,
                )
            )
        ).scalar_one_or_none()

        if device is None:
            logger.warning("store_sensor_reading: unknown device %s", device_id_str)
            return

        if device.tent_id is None:
            logger.debug(
                "Device %s has no tent_id assigned — skipping storage",
                device_id_str,
            )
            return

        now = datetime.now(UTC)

        if sensor_type == "ambient":
            # Filter payload to only known ambient columns
            values = {k: float(v) for k, v in payload.items() if k in _TENT_SENSOR_FIELDS and v is not None}
            if not values:
                return
            reading = TentSensorReading(
                tenant_id=tenant_id,
                tent_id=device.tent_id,
                device_id=device_id_str,
                recorded_at=now,
                **values,
            )
            session.add(reading)
            await session.commit()
            logger.debug("Stored ambient reading for tent %s", device.tent_id)

        else:
            # "readings" → bucket-level; use payload["position"] to find the bucket
            position = payload.get("position", 1)

            # Find an active grow cycle in this tent, then the bucket at the given position
            bucket = (
                await session.execute(
                    select(Bucket)
                    .join(GrowCycle, Bucket.grow_cycle_id == GrowCycle.id)
                    .where(
                        GrowCycle.tent_id == device.tent_id,
                        GrowCycle.tenant_id == tenant_id,
                        GrowCycle.status == "active",
                        Bucket.position == position,
                    )
                    .limit(1)
                )
            ).scalar_one_or_none()

            if bucket is None:
                logger.debug(
                    "No active bucket at position %s in tent %s — skipping",
                    position,
                    device.tent_id,
                )
                return

            # Filter payload to only known bucket sensor columns
            values = {k: float(v) for k, v in payload.items() if k in _BUCKET_SENSOR_FIELDS and v is not None}
            if not values:
                return
            _derive_ec_ppm(values)
            reading = BucketSensorReading(
                tenant_id=tenant_id,
                bucket_id=bucket.id,
                device_id=device_id_str,
                recorded_at=now,
                **values,
            )
            session.add(reading)
            await session.flush()

            # Propagate header readings to all site buckets in RDWC grows
            from app.integrations.connectors.base import propagate_header_bucket_readings

            await propagate_header_bucket_readings(session, str(bucket.id), reading)

            await session.commit()

            # Evaluate real-time alerts (non-blocking — failures logged but don't fail ingestion)
            try:
                from app.automation.engine import (
                    evaluate_composite_alerts,
                    evaluate_critical_alerts,
                    evaluate_trend_alerts,
                )
                from app.grows.models import GrowCycle

                grow = await session.get(GrowCycle, bucket.grow_cycle_id)
                if grow:
                    await evaluate_critical_alerts(session, grow.grow_type, tenant_id, grow.id, reading)
                    await evaluate_composite_alerts(session, grow.grow_type, tenant_id, grow.id, reading)
                    await evaluate_trend_alerts(session, grow.grow_type, tenant_id, grow.id, bucket.id)
            except Exception:
                logger.debug("Alert evaluation failed for bucket %s", bucket.id, exc_info=True)

            logger.debug(
                "Stored bucket reading for bucket %s (position %s)",
                bucket.id,
                position,
            )


async def handle_status_message(device_id_str: str, payload_bytes) -> None:
    """Handle device status messages (last-will = offline)."""
    try:
        payload = json.loads(payload_bytes)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Invalid JSON in status message from %s", device_id_str)
        return

    new_status = payload.get("status", "offline")
    if new_status not in ("online", "offline"):
        new_status = "offline"

    async with async_session_factory() as session:
        await session.execute(
            update(Device)
            .where(Device.device_id == device_id_str)
            .values(status=new_status, last_seen=datetime.now(UTC))
        )
        await session.commit()

    logger.info("Device %s status → %s (via MQTT)", device_id_str, new_status)
