"""Shelly HTTP protocol adapter.

Supports both Gen1 and Gen2 Shelly devices:
- Gen1: GET http://{ip}/relay/{channel}?turn=on|off
- Gen2: POST http://{ip}/rpc/Switch.Set {"id": channel, "on": true|false}
"""

from __future__ import annotations

import logging

import httpx

from app.equipment.models import ControllableEquipment
from app.equipment.protocols.dispatch import DispatchResult, register_protocol

logger = logging.getLogger(__name__)

_TIMEOUT = 10.0


async def handle_command(
    equipment: ControllableEquipment,
    action: str,
    value: int | None = None,
) -> DispatchResult:
    """Send command to Shelly device via HTTP."""
    config = equipment.protocol_config
    ip_address = config.get("ip_address")
    if not ip_address:
        return DispatchResult(success=False, message="Missing ip_address in protocol_config")

    generation = config.get("generation", 1)
    channel = config.get("channel", 0)

    if action == "set_brightness":
        if value is None:
            return DispatchResult(success=False, message="set_brightness requires a value")
        return await _set_brightness(ip_address, generation, channel, value)

    # Map action to on/off boolean
    if action == "on":
        turn_on = True
    elif action == "off":
        turn_on = False
    elif action == "toggle":
        # Get current state and invert
        current = await _get_state(ip_address, generation, channel)
        if current is None:
            return DispatchResult(success=False, message="Cannot determine current state for toggle")
        turn_on = not current
    else:
        return DispatchResult(success=False, message=f"Unsupported action: {action}")

    if generation >= 2:
        return await _gen2_switch(ip_address, channel, turn_on)
    else:
        return await _gen1_relay(ip_address, channel, turn_on)


async def _gen1_relay(ip: str, channel: int, on: bool) -> DispatchResult:
    """Gen1 Shelly relay control."""
    turn = "on" if on else "off"
    url = f"http://{ip}/relay/{channel}?turn={turn}"

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

    return DispatchResult(
        success=True,
        message=f"Shelly Gen1 relay {channel} turned {turn}",
        device_info=data,
    )


async def _gen2_switch(ip: str, channel: int, on: bool) -> DispatchResult:
    """Gen2 Shelly switch control via RPC."""
    url = f"http://{ip}/rpc/Switch.Set"
    payload = {"id": channel, "on": on}

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

    action_str = "on" if on else "off"
    return DispatchResult(
        success=True,
        message=f"Shelly Gen2 switch {channel} turned {action_str}",
        device_info=data,
    )


async def _set_brightness(ip: str, generation: int, channel: int, value: int) -> DispatchResult:
    """Set Shelly dimmer brightness."""
    value = max(0, min(100, value))

    if generation >= 2:
        url = f"http://{ip}/rpc/Light.Set"
        payload = {"id": channel, "on": value > 0, "brightness": value}
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
    else:
        turn = "on" if value > 0 else "off"
        url = f"http://{ip}/light/{channel}?turn={turn}&brightness={value}"
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

    return DispatchResult(
        success=True,
        message=f"Shelly brightness set to {value}%",
        device_info=data,
    )


async def _get_state(ip: str, generation: int, channel: int) -> bool | None:
    """Get current relay/switch state."""
    try:
        if generation >= 2:
            url = f"http://{ip}/rpc/Switch.GetStatus"
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(url, json={"id": channel})
                resp.raise_for_status()
                data = resp.json()
                return data.get("output", False)
        else:
            url = f"http://{ip}/status"
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                relays = data.get("relays", [])
                if channel < len(relays):
                    return relays[channel].get("ison", False)
    except Exception as exc:
        logger.debug("Failed to get Shelly state at %s: %s", ip, exc)
    return None


async def test_shelly_connection(equipment: ControllableEquipment) -> DispatchResult:
    """Test Shelly device connectivity."""
    config = equipment.protocol_config
    ip_address = config.get("ip_address")
    if not ip_address:
        return DispatchResult(success=False, message="Missing ip_address in protocol_config")

    generation = config.get("generation", 1)

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            if generation >= 2:
                resp = await client.post(f"http://{ip_address}/rpc/Shelly.GetDeviceInfo", json={})
            else:
                resp = await client.get(f"http://{ip_address}/shelly")
            resp.raise_for_status()
            data = resp.json()

        return DispatchResult(
            success=True,
            message=f"Shelly Gen{generation} device reachable",
            device_info=data,
        )
    except httpx.ConnectError:
        return DispatchResult(success=False, message=f"Cannot connect to {ip_address}")
    except httpx.TimeoutException:
        return DispatchResult(success=False, message=f"Connection to {ip_address} timed out")
    except Exception as exc:
        return DispatchResult(success=False, message=f"Shelly test failed: {exc!s}")


# Register with dispatch
register_protocol("shelly_http", handle_command, test_shelly_connection)
