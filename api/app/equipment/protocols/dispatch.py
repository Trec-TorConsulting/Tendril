"""Protocol dispatch — routes equipment commands to the correct adapter."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.equipment.models import ControllableEquipment

logger = logging.getLogger(__name__)


@dataclass
class DispatchResult:
    """Result of a protocol command dispatch."""

    success: bool
    message: str
    device_info: dict[str, Any] | None = None


async def dispatch_command(
    equipment: ControllableEquipment,
    action: str,
    value: int | None = None,
) -> DispatchResult:
    """Dispatch a control command to equipment via its configured protocol.

    Routes to the appropriate protocol adapter based on equipment.protocol.
    """
    protocol = equipment.protocol
    handler = _PROTOCOL_HANDLERS.get(protocol)

    if handler is None:
        return DispatchResult(
            success=False,
            message=f"Unsupported protocol: {protocol}",
        )

    try:
        return await handler(equipment, action, value)
    except Exception as exc:
        logger.exception(
            "Protocol dispatch failed for equipment %s (%s): %s",
            equipment.id,
            protocol,
            exc,
        )
        return DispatchResult(
            success=False,
            message=f"Protocol error: {exc!s}",
        )


async def test_connection(equipment: ControllableEquipment) -> DispatchResult:
    """Test connectivity to equipment via its configured protocol."""
    protocol = equipment.protocol
    tester = _CONNECTION_TESTERS.get(protocol)

    if tester is None:
        return DispatchResult(
            success=False,
            message=f"No connection test available for protocol: {protocol}",
        )

    try:
        return await tester(equipment)
    except Exception as exc:
        logger.exception(
            "Connection test failed for equipment %s (%s): %s",
            equipment.id,
            protocol,
            exc,
        )
        return DispatchResult(
            success=False,
            message=f"Connection test error: {exc!s}",
        )


# Protocol handler type
type ProtocolHandler = Any  # Callable[[ControllableEquipment, str, int | None], Awaitable[DispatchResult]]
type ConnectionTester = Any  # Callable[[ControllableEquipment], Awaitable[DispatchResult]]

# Registry populated by adapter modules
_PROTOCOL_HANDLERS: dict[str, ProtocolHandler] = {}
_CONNECTION_TESTERS: dict[str, ConnectionTester] = {}


def register_protocol(
    protocol_name: str,
    handler: ProtocolHandler,
    tester: ConnectionTester | None = None,
) -> None:
    """Register a protocol adapter."""
    _PROTOCOL_HANDLERS[protocol_name] = handler
    if tester is not None:
        _CONNECTION_TESTERS[protocol_name] = tester


# Import adapters to trigger registration
from app.equipment.protocols import generic_mqtt, shelly, tasmota, tuya  # noqa: E402, F401
