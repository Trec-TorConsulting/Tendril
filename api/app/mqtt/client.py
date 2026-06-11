"""MQTT Client — connects to EMQX and subscribes to sensor + status + equipment + generic topics."""

from __future__ import annotations

import asyncio
import logging

from app.config import Settings
from app.equipment.mqtt_handler import get_equipment_subscribe_topics, handle_equipment_state_message
from app.mqtt.handlers import handle_message

logger = logging.getLogger("tendril.mqtt.client")

# Topic patterns:
#   t/{tenant_id}/d/{device_id}/sensor/#  — sensor readings
#   t/{tenant_id}/d/{device_id}/status    — online/offline (last-will)
# Using EMQX shared subscriptions ($share/group/topic) so multiple worker
# replicas load-balance messages instead of each receiving every message.
SUBSCRIBE_TOPICS = [
    "$share/tendril-workers/t/+/d/+/sensor/#",
    "$share/tendril-workers/t/+/d/+/status",
]

# Equipment state topics (Tasmota stat/RESULT, tele/SENSOR)
EQUIPMENT_TOPICS = get_equipment_subscribe_topics()

# Prefixes that indicate equipment state messages
_EQUIPMENT_PREFIXES = ("stat/", "tele/")

# Tendril device topic prefix
_TENDRIL_DEVICE_PREFIX = "t/"


class MQTTClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._generic_topics: set[str] = set()

    async def run(self, shutdown_event: asyncio.Event) -> None:
        import aiomqtt

        # Load generic MQTT integration topics
        generic_topics = await self._load_generic_topics()

        all_topics = SUBSCRIBE_TOPICS + EQUIPMENT_TOPICS + generic_topics

        while not shutdown_event.is_set():
            try:
                async with aiomqtt.Client(
                    hostname=self.settings.mqtt_broker_host,
                    port=self.settings.mqtt_broker_port,
                ) as client:
                    for topic in all_topics:
                        await client.subscribe(topic)
                        logger.info("Subscribed to %s", topic)

                    async for message in client.messages:
                        if shutdown_event.is_set():
                            break
                        try:
                            topic_str = str(message.topic)
                            # Route to equipment handler for stat/tele topics
                            if any(topic_str.startswith(p) for p in _EQUIPMENT_PREFIXES):
                                await handle_equipment_state_message(topic_str, message.payload)
                            # Route to Tendril device handler for t/{tenant}/d/{device}/...
                            elif topic_str.startswith(_TENDRIL_DEVICE_PREFIX):
                                await handle_message(message)
                            # Everything else goes to generic MQTT handler
                            else:
                                await self._handle_generic_message(topic_str, message.payload)
                        except Exception:
                            logger.exception("Error handling MQTT message: %s", message.topic)

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("MQTT connection error, reconnecting in 5s")
                await asyncio.sleep(5)

    async def _load_generic_topics(self) -> list[str]:
        """Load generic MQTT topics from database on startup."""
        try:
            from app.integrations.mqtt_subscriptions import get_shared_subscription_topics

            topics = await get_shared_subscription_topics()
            self._generic_topics = {t.replace("$share/tendril-workers/", "") for t in topics}
            if topics:
                logger.info("Loaded %d generic MQTT subscription topics", len(topics))
            return topics
        except Exception:
            logger.exception("Failed to load generic MQTT topics — will retry on reconnect")
            return []

    async def _handle_generic_message(self, topic: str, payload: bytes) -> None:
        """Route message to generic MQTT integration handler."""
        try:
            from app.integrations.mqtt_subscriptions import handle_generic_mqtt_message

            await handle_generic_mqtt_message(topic, payload)
        except Exception:
            logger.exception("Error handling generic MQTT message on %s", topic)
