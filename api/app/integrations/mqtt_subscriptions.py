"""MQTT subscription manager for generic MQTT devices.

Manages dynamic topic subscriptions for mqtt_generic integrations.
On worker startup, loads all active mqtt_generic device maps and subscribes
to their configured topics (stored as external_id on IntegrationDeviceMap).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.integrations.connectors.base import get_connector_class
from app.integrations.crypto import decrypt_config
from app.integrations.models import IntegrationConfig, IntegrationDeviceMap

logger = logging.getLogger("tendril.integrations.mqtt_subscriptions")


async def get_generic_mqtt_topics() -> list[str]:
    """Load all active MQTT topics from enabled mqtt_generic integrations.

    Returns a deduplicated list of topics to subscribe to.
    """
    topics: set[str] = set()

    async with async_session_factory() as session:
        # Find all enabled mqtt_generic integrations
        configs = (
            (
                await session.execute(
                    select(IntegrationConfig).where(
                        IntegrationConfig.type == "mqtt_generic",
                        IntegrationConfig.enabled.is_(True),
                    )
                )
            )
            .scalars()
            .all()
        )

        if not configs:
            return []

        config_ids = [c.id for c in configs]

        # Get all enabled device maps for these integrations
        device_maps = (
            (
                await session.execute(
                    select(IntegrationDeviceMap).where(
                        IntegrationDeviceMap.integration_id.in_(config_ids),
                        IntegrationDeviceMap.enabled.is_(True),
                    )
                )
            )
            .scalars()
            .all()
        )

        for dm in device_maps:
            topic = dm.external_id
            if topic and topic.strip():
                topics.add(topic.strip())

    result = sorted(topics)
    if result:
        logger.info("Loaded %d generic MQTT topics for subscription", len(result))
    return result


async def get_shared_subscription_topics() -> list[str]:
    """Get generic MQTT topics formatted as EMQX shared subscriptions.

    Uses the same shared group as Tendril workers for load-balanced delivery.
    """
    topics = await get_generic_mqtt_topics()
    return [f"$share/tendril-workers/{t}" for t in topics]


async def handle_generic_mqtt_message(topic: str, payload_bytes: bytes) -> None:
    """Route an incoming MQTT message to the appropriate mqtt_generic connector.

    Called by the MQTT worker when a message arrives on a generic device topic.
    """
    # Parse payload
    try:
        payload_str = payload_bytes.decode("utf-8")
    except UnicodeDecodeError:
        logger.debug("Cannot decode generic MQTT payload on topic %s", topic)
        return

    # Try JSON parse
    try:
        raw_payload = json.loads(payload_str)
    except json.JSONDecodeError:
        # Might be a single numeric value
        try:
            numeric = float(payload_str.strip())
            raw_payload = {"value": numeric}
        except ValueError:
            logger.debug(
                "Non-JSON/non-numeric payload on generic MQTT topic %s: %s",
                topic,
                payload_str[:100],
            )
            return

    if not isinstance(raw_payload, dict):
        # If it's a list or other type, wrap it
        raw_payload = {"value": raw_payload}

    # Find matching integration + device maps
    async with async_session_factory() as session:
        await _process_message(session, topic, raw_payload)


async def _process_message(session: AsyncSession, topic: str, raw_payload: dict[str, Any]) -> None:
    """Find the matching connector and process the message."""
    from app.integrations.connectors.mqtt_generic import _topic_matches

    # Find device maps where external_id matches this topic
    device_maps = (
        (
            await session.execute(
                select(IntegrationDeviceMap).where(
                    IntegrationDeviceMap.enabled.is_(True),
                )
            )
        )
        .scalars()
        .all()
    )

    # Group by integration_id, filtering for topic matches
    matching_by_integration: dict[Any, list] = {}
    for dm in device_maps:
        if dm.external_id == topic or _topic_matches(dm.external_id, topic):
            if dm.integration_id not in matching_by_integration:
                matching_by_integration[dm.integration_id] = []
            matching_by_integration[dm.integration_id].append(dm)

    if not matching_by_integration:
        return

    for integration_id, maps in matching_by_integration.items():
        config = await session.get(IntegrationConfig, integration_id)
        if config is None or not config.enabled or config.type != "mqtt_generic":
            continue

        connector_cls = get_connector_class("mqtt_generic")
        if connector_cls is None:
            continue

        decrypted = decrypt_config(config.encrypted_config) if config.encrypted_config else {}
        connector = connector_cls(config, decrypted, maps)

        # Build webhook-style payload
        webhook_payload = {"_topic": topic, "_raw": raw_payload}
        result = await connector.handle_webhook(webhook_payload)

        if result.readings:
            count = await connector.persist_readings(session, result)
            await connector.write_sync_log(session, result)
            await session.commit()
            logger.info(
                "Generic MQTT: persisted %d readings from topic %s",
                count,
                topic,
            )

        if result.errors:
            for err in result.errors:
                logger.warning("Generic MQTT error on topic %s: %s", topic, err)
