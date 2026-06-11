"""Tasmota MQTT protocol adapter.

Tasmota devices use MQTT topics:
- Command: cmnd/{topic}/Power → ON/OFF/TOGGLE
- State:   stat/{topic}/RESULT → {"POWER":"ON"}
- Telemetry: tele/{topic}/SENSOR → {"ENERGY":{"Power":120,...}}
- LWT:    tele/{topic}/LWT → Online/Offline
"""

from __future__ import annotations

import logging
from typing import Any

from app.equipment.models import ControllableEquipment
from app.equipment.protocols.dispatch import DispatchResult, register_protocol

logger = logging.getLogger(__name__)


async def handle_command(
    equipment: ControllableEquipment,
    action: str,
    value: int | None = None,
) -> DispatchResult:
    """Send command to Tasmota device via MQTT."""
    from app.mqtt.publisher import publish_command

    config = equipment.protocol_config
    mqtt_topic = config.get("mqtt_topic")
    if not mqtt_topic:
        return DispatchResult(success=False, message="Missing mqtt_topic in protocol_config")

    # Determine Tasmota command payload
    if action == "on":
        payload = "ON"
    elif action == "off":
        payload = "OFF"
    elif action == "toggle":
        payload = "TOGGLE"
    elif action == "set_brightness":
        if value is None:
            return DispatchResult(success=False, message="set_brightness requires a value")
        # Tasmota dimmer: 0-100
        payload = str(max(0, min(100, value)))
        topic = f"cmnd/{mqtt_topic}/Dimmer"
        await publish_command(topic, payload)
        return DispatchResult(
            success=True,
            message=f"Dimmer command sent: {payload}%",
        )
    else:
        return DispatchResult(success=False, message=f"Unsupported action: {action}")

    # Power channel (default channel 1, configurable)
    channel = config.get("channel", "")
    power_suffix = f"Power{channel}" if channel else "Power"
    topic = f"cmnd/{mqtt_topic}/{power_suffix}"

    await publish_command(topic, payload)

    return DispatchResult(
        success=True,
        message=f"Tasmota command sent: {power_suffix} {payload}",
    )


async def test_tasmota_connection(equipment: ControllableEquipment) -> DispatchResult:
    """Test Tasmota device connectivity by requesting status."""
    from app.mqtt.publisher import publish_command

    config = equipment.protocol_config
    mqtt_topic = config.get("mqtt_topic")
    if not mqtt_topic:
        return DispatchResult(success=False, message="Missing mqtt_topic in protocol_config")

    # Request status — device will reply on stat/{topic}/STATUS
    topic = f"cmnd/{mqtt_topic}/Status"
    try:
        await publish_command(topic, "0")
        return DispatchResult(
            success=True,
            message=f"Status request sent to {mqtt_topic}. Check device LWT for online status.",
        )
    except Exception as exc:
        return DispatchResult(success=False, message=f"MQTT publish failed: {exc!s}")


def parse_tasmota_result(payload: dict[str, Any]) -> dict[str, Any]:
    """Parse a Tasmota stat/RESULT message into normalized state.

    Example payload: {"POWER":"ON"} or {"POWER1":"OFF","POWER2":"ON"}
    """
    state: dict[str, Any] = {}

    for key, val in payload.items():
        if key.startswith("POWER"):
            state["is_on"] = val == "ON"
        elif key == "Dimmer":
            state["brightness"] = int(val)

    return state


def parse_tasmota_sensor(payload: dict[str, Any]) -> dict[str, Any]:
    """Parse a Tasmota tele/SENSOR message for energy data.

    Example: {"ENERGY":{"Power":120,"Voltage":230,"Current":0.52,"Total":12.3}}
    """
    state: dict[str, Any] = {}
    energy = payload.get("ENERGY", {})

    if "Power" in energy:
        state["power_w"] = float(energy["Power"])
    if "Voltage" in energy:
        state["voltage_v"] = float(energy["Voltage"])
    if "Current" in energy:
        state["current_ma"] = float(energy["Current"]) * 1000
    if "Total" in energy:
        state["energy_kwh"] = float(energy["Total"])

    return state


# Register with dispatch
register_protocol("tasmota_mqtt", handle_command, test_tasmota_connection)
