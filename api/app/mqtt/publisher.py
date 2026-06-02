"""MQTT outbound publisher — delivers commands to devices via MQTT broker."""

from __future__ import annotations

import logging

logger = logging.getLogger("tendril.mqtt.publisher")

# Module-level MQTT client reference (initialized by worker startup)
_client = None


def set_client(client) -> None:
    """Set the shared MQTT client for outbound publishing.

    Called during MQTT worker initialization after the client connects.
    """
    global _client
    _client = client
    logger.info("MQTT publisher initialized")


async def publish_command(topic: str, payload: str) -> None:
    """Publish a command message to the MQTT broker.

    Raises RuntimeError if the client is not connected.
    """
    if _client is None:
        raise RuntimeError("MQTT client not initialized — command queued for device poll")

    try:
        result = _client.publish(topic, payload.encode(), qos=1)
        if hasattr(result, "rc") and result.rc != 0:
            raise RuntimeError(f"MQTT publish failed with rc={result.rc}")
        logger.debug("Published command to %s", topic)
    except Exception:
        logger.exception("Failed to publish to %s", topic)
        raise
