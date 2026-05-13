"""MQTT Worker — sensor ingestion from ESP32 devices via EMQX.

Subscribes to `t/+/d/+/sensor/#` and writes readings to PostgreSQL.
Also serves EMQX auth/ACL webhook endpoints.
"""

from __future__ import annotations

import asyncio
import logging
import signal

from app.config import get_settings
from app.mqtt.auth_webhook import start_webhook_server
from app.mqtt.client import MQTTClient

logger = logging.getLogger("tendril.mqtt")


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
    logger.info("MQTT Worker starting")

    shutdown_event = asyncio.Event()

    def _signal_handler():
        logger.info("Shutdown signal received")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _signal_handler)

    # Start EMQX auth/ACL webhook server
    webhook_task = asyncio.create_task(start_webhook_server())

    # Start MQTT subscriber
    client = MQTTClient(settings)
    subscribe_task = asyncio.create_task(client.run(shutdown_event))

    await shutdown_event.wait()
    subscribe_task.cancel()
    webhook_task.cancel()
    logger.info("MQTT Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
