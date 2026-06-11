"""Generic MQTT protocol adapter.

Allows users to control any MQTT-speaking device via configurable
command/state topics and on/off payloads.

Config schema:
  {
    "command_topic": "home/relay/1/set",
    "state_topic": "home/relay/1/state",      (optional, for feedback)
    "on_payload": "ON",
    "off_payload": "OFF",
    "brightness_topic": "home/relay/1/brightness/set",  (optional)
    "brightness_range": [0, 100]              (optional, default 0-100)
  }
"""

from __future__ import annotations

import logging

from app.equipment.models import ControllableEquipment
from app.equipment.protocols.dispatch import DispatchResult, register_protocol

logger = logging.getLogger(__name__)


async def handle_command(
    equipment: ControllableEquipment,
    action: str,
    value: int | None = None,
) -> DispatchResult:
    """Send command to generic MQTT device."""
    from app.mqtt.publisher import publish_command

    config = equipment.protocol_config
    command_topic = config.get("command_topic")
    if not command_topic:
        return DispatchResult(success=False, message="Missing command_topic in protocol_config")

    on_payload = config.get("on_payload", "ON")
    off_payload = config.get("off_payload", "OFF")

    if action == "on":
        payload = on_payload
    elif action == "off":
        payload = off_payload
    elif action == "toggle":
        # Toggle based on current requested state
        current_on = equipment.requested_state.get("is_on", False)
        payload = off_payload if current_on else on_payload
    elif action == "set_brightness":
        if value is None:
            return DispatchResult(success=False, message="set_brightness requires a value")
        brightness_topic = config.get("brightness_topic", command_topic)
        brightness_range = config.get("brightness_range", [0, 100])
        # Scale value from 0-100 to device range
        low, high = brightness_range[0], brightness_range[1]
        scaled = int(low + (value / 100) * (high - low))
        await publish_command(brightness_topic, str(scaled))
        return DispatchResult(
            success=True,
            message=f"Brightness command sent to {brightness_topic}: {scaled}",
        )
    else:
        return DispatchResult(success=False, message=f"Unsupported action: {action}")

    await publish_command(command_topic, payload)
    return DispatchResult(
        success=True,
        message=f"MQTT command sent to {command_topic}: {payload}",
    )


async def test_generic_mqtt_connection(equipment: ControllableEquipment) -> DispatchResult:
    """Test generic MQTT — we can only verify the topic is configured."""
    config = equipment.protocol_config
    command_topic = config.get("command_topic")

    if not command_topic:
        return DispatchResult(success=False, message="Missing command_topic in protocol_config")

    # For generic MQTT we can't truly test without subscribing to a response
    # Just validate config is present
    state_topic = config.get("state_topic")
    return DispatchResult(
        success=True,
        message=f"Configuration valid. Command topic: {command_topic}"
        + (f", State topic: {state_topic}" if state_topic else ""),
    )


def parse_generic_state(payload: str, config: dict) -> dict:
    """Parse a generic MQTT state message into normalized state.

    Compares payload against configured on_payload/off_payload.
    """
    on_payload = config.get("on_payload", "ON")
    off_payload = config.get("off_payload", "OFF")

    payload_stripped = payload.strip()
    if payload_stripped == on_payload:
        return {"is_on": True}
    elif payload_stripped == off_payload:
        return {"is_on": False}
    else:
        # Try to parse as brightness level
        try:
            brightness = int(payload_stripped)
            brightness_range = config.get("brightness_range", [0, 100])
            low, high = brightness_range[0], brightness_range[1]
            if high > low:
                pct = int(((brightness - low) / (high - low)) * 100)
                return {"is_on": pct > 0, "brightness": max(0, min(100, pct))}
        except ValueError, TypeError:
            pass

    return {}


# Register with dispatch
register_protocol("generic_mqtt", handle_command, test_generic_mqtt_connection)
