"""MQTT handlers for equipment state feedback.

Processes Tasmota and generic MQTT state messages to update
equipment confirmed_state.

Topic patterns handled:
  - stat/{mqtt_topic}/RESULT  → Tasmota relay state changes
  - tele/{mqtt_topic}/SENSOR  → Tasmota power/energy telemetry
  - {state_topic}             → Generic MQTT state feedback
"""

from __future__ import annotations

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.equipment.models import ControllableEquipment
from app.equipment.protocols.tasmota import parse_tasmota_result, parse_tasmota_sensor
from app.equipment.service import confirm_equipment_state

logger = logging.getLogger("tendril.equipment.mqtt")


async def handle_equipment_state_message(topic: str, payload_bytes: bytes) -> None:
    """Route equipment state messages to the appropriate parser.

    Called by the MQTT worker for equipment-related topics.
    """
    topic_parts = topic.split("/")

    try:
        payload_str = payload_bytes.decode("utf-8")
        payload = json.loads(payload_str) if payload_str.startswith("{") else payload_str
    except UnicodeDecodeError, json.JSONDecodeError:
        logger.debug("Cannot parse equipment state payload for topic %s", topic)
        return

    # Tasmota: stat/{mqtt_topic}/RESULT
    if len(topic_parts) >= 3 and topic_parts[0] == "stat" and topic_parts[-1] == "RESULT":
        mqtt_topic = "/".join(topic_parts[1:-1])
        if isinstance(payload, dict):
            await _handle_tasmota_result(mqtt_topic, payload)
        return

    # Tasmota: tele/{mqtt_topic}/SENSOR
    if len(topic_parts) >= 3 and topic_parts[0] == "tele" and topic_parts[-1] == "SENSOR":
        mqtt_topic = "/".join(topic_parts[1:-1])
        if isinstance(payload, dict):
            await _handle_tasmota_sensor(mqtt_topic, payload)
        return

    # Generic MQTT: check if topic matches any equipment state_topic config
    await _handle_generic_state(topic, payload_str if isinstance(payload, str) else json.dumps(payload))


async def _handle_tasmota_result(mqtt_topic: str, payload: dict) -> None:
    """Process a Tasmota stat/RESULT message."""
    state = parse_tasmota_result(payload)
    if not state:
        return

    async with async_session_factory() as session:
        equipment = await _find_equipment_by_mqtt_topic(session, mqtt_topic)
        if equipment is None:
            logger.debug("No equipment found for Tasmota topic: %s", mqtt_topic)
            return

        # Merge with existing confirmed state
        confirmed = dict(equipment.confirmed_state)
        confirmed.update(state)
        await confirm_equipment_state(session, equipment, confirmed)
        await session.commit()
        logger.info("Equipment %s state confirmed: %s", equipment.name, confirmed)


async def _handle_tasmota_sensor(mqtt_topic: str, payload: dict) -> None:
    """Process a Tasmota tele/SENSOR message for energy data."""
    state = parse_tasmota_sensor(payload)
    if not state:
        return

    async with async_session_factory() as session:
        equipment = await _find_equipment_by_mqtt_topic(session, mqtt_topic)
        if equipment is None:
            return

        # Merge energy data with existing confirmed state
        confirmed = dict(equipment.confirmed_state)
        confirmed.update(state)
        await confirm_equipment_state(session, equipment, confirmed, source="device_report")
        await session.commit()


async def _handle_generic_state(topic: str, payload_str: str) -> None:
    """Process a generic MQTT state message."""
    from app.equipment.protocols.generic_mqtt import parse_generic_state

    async with async_session_factory() as session:
        equipment = await _find_equipment_by_state_topic(session, topic)
        if equipment is None:
            return

        state = parse_generic_state(payload_str, equipment.protocol_config)
        if not state:
            return

        confirmed = dict(equipment.confirmed_state)
        confirmed.update(state)
        await confirm_equipment_state(session, equipment, confirmed)
        await session.commit()
        logger.info("Equipment %s state confirmed via generic MQTT: %s", equipment.name, confirmed)


async def _find_equipment_by_mqtt_topic(session: AsyncSession, mqtt_topic: str) -> ControllableEquipment | None:
    """Find equipment by Tasmota MQTT topic."""
    # Search for equipment with protocol=tasmota_mqtt and matching mqtt_topic in config
    stmt = select(ControllableEquipment).where(
        ControllableEquipment.protocol == "tasmota_mqtt",
        ControllableEquipment.enabled.is_(True),
    )
    equipment_list = (await session.execute(stmt)).scalars().all()

    for equip in equipment_list:
        config_topic = equip.protocol_config.get("mqtt_topic", "")
        if config_topic == mqtt_topic:
            return equip

    return None


async def _find_equipment_by_state_topic(session: AsyncSession, topic: str) -> ControllableEquipment | None:
    """Find equipment by generic MQTT state topic."""
    stmt = select(ControllableEquipment).where(
        ControllableEquipment.protocol == "generic_mqtt",
        ControllableEquipment.enabled.is_(True),
    )
    equipment_list = (await session.execute(stmt)).scalars().all()

    for equip in equipment_list:
        state_topic = equip.protocol_config.get("state_topic", "")
        if state_topic == topic:
            return equip

    return None


def get_equipment_subscribe_topics() -> list[str]:
    """Get the MQTT topics that the worker should subscribe to for equipment state.

    Returns shared subscription topics for Tasmota state/telemetry.
    Generic MQTT state topics are dynamic (per-equipment) and handled separately.
    """
    return [
        "$share/tendril-workers/stat/+/RESULT",
        "$share/tendril-workers/tele/+/SENSOR",
        "$share/tendril-workers/tele/+/LWT",
    ]
