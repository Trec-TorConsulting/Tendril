"""MQTT Client — connects to EMQX and subscribes to sensor + status topics."""
from __future__ import annotations

import asyncio
import logging

from app.config import Settings
from app.mqtt.handlers import handle_message

logger = logging.getLogger("tendril.mqtt.client")

# Topic patterns:
#   t/{tenant_id}/d/{device_id}/sensor/#  — sensor readings
#   t/{tenant_id}/d/{device_id}/status    — online/offline (last-will)
SUBSCRIBE_TOPICS = [
    "t/+/d/+/sensor/#",
    "t/+/d/+/status",
]


class MQTTClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def run(self, shutdown_event: asyncio.Event) -> None:
        import aiomqtt

        while not shutdown_event.is_set():
            try:
                async with aiomqtt.Client(
                    hostname=self.settings.mqtt_broker_host,
                    port=self.settings.mqtt_broker_port,
                ) as client:
                    for topic in SUBSCRIBE_TOPICS:
                        await client.subscribe(topic)
                        logger.info("Subscribed to %s", topic)

                    async for message in client.messages:
                        if shutdown_event.is_set():
                            break
                        try:
                            await handle_message(message)
                        except Exception:
                            logger.exception("Error handling MQTT message: %s", message.topic)

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("MQTT connection error, reconnecting in 5s")
                await asyncio.sleep(5)
