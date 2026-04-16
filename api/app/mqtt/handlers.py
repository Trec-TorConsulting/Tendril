"""MQTT message handlers — parse sensor payloads and store readings."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import update

from app.database import async_session_factory
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


async def handle_sensor_message(
    tenant_id: UUID, device_id_str: str, sensor_type: str, payload_bytes
) -> None:
    """Parse sensor payload and store reading."""
    try:
        payload = json.loads(payload_bytes)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Invalid JSON payload from device %s", device_id_str)
        return

    logger.debug(
        "Sensor reading: tenant=%s device=%s type=%s payload=%s",
        tenant_id, device_id_str, sensor_type, payload,
    )

    # Update last_seen on any sensor message
    async with async_session_factory() as session:
        await session.execute(
            update(Device)
            .where(Device.device_id == device_id_str)
            .values(last_seen=datetime.now(timezone.utc))
        )
        await session.commit()

    # TODO: Phase 3 — write to bucket_sensor_readings table
    # await store_sensor_reading(tenant_id, device_id_str, sensor_type, payload)


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
            .values(status=new_status, last_seen=datetime.now(timezone.utc))
        )
        await session.commit()

    logger.info("Device %s status → %s (via MQTT)", device_id_str, new_status)
