"""Tuya cloud protocol adapter.

Delegates to the existing TuyaConnector.toggle_device() method for device control.
Requires an active Tuya integration configured for the tenant.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import select

from app.equipment.models import ControllableEquipment
from app.equipment.protocols.dispatch import DispatchResult, register_protocol

logger = logging.getLogger(__name__)


async def handle_command(
    equipment: ControllableEquipment,
    action: str,
    value: int | None = None,
) -> DispatchResult:
    """Send command to Tuya device via cloud API."""
    config = equipment.protocol_config
    integration_id = config.get("integration_id")
    external_device_id = config.get("external_device_id")

    if not integration_id or not external_device_id:
        return DispatchResult(
            success=False,
            message="Missing integration_id or external_device_id in protocol_config",
        )

    # Resolve on/off
    if action == "on":
        turn_on = True
    elif action == "off":
        turn_on = False
    elif action == "toggle":
        # Tuya toggle: invert current requested_state
        current_on = equipment.requested_state.get("is_on", False)
        turn_on = not current_on
    else:
        return DispatchResult(success=False, message=f"Unsupported action for Tuya: {action}")

    try:
        connector = await _get_tuya_connector(integration_id, equipment.tenant_id)
        if connector is None:
            return DispatchResult(
                success=False,
                message=f"Tuya integration {integration_id} not found or not configured",
            )

        result = await connector.toggle_device(external_device_id, turn_on)
        success = result.get("success", False)
        msg = result.get("msg", "")

        if success:
            return DispatchResult(
                success=True,
                message=f"Tuya device {'on' if turn_on else 'off'}: {external_device_id}",
            )
        else:
            return DispatchResult(success=False, message=f"Tuya API error: {msg}")

    except Exception as exc:
        return DispatchResult(success=False, message=f"Tuya command failed: {exc!s}")


async def test_tuya_connection(equipment: ControllableEquipment) -> DispatchResult:
    """Test Tuya device reachability via status query."""
    config = equipment.protocol_config
    integration_id = config.get("integration_id")
    external_device_id = config.get("external_device_id")

    if not integration_id or not external_device_id:
        return DispatchResult(
            success=False,
            message="Missing integration_id or external_device_id in protocol_config",
        )

    try:
        connector = await _get_tuya_connector(integration_id, equipment.tenant_id)
        if connector is None:
            return DispatchResult(
                success=False,
                message=f"Tuya integration {integration_id} not found",
            )

        # Use discover to verify the device exists
        devices = await connector.discover_devices()
        found = any(d.external_id == external_device_id for d in devices)

        if found:
            return DispatchResult(
                success=True,
                message=f"Tuya device {external_device_id} found and reachable",
            )
        else:
            return DispatchResult(
                success=False,
                message=f"Tuya device {external_device_id} not found in cloud project",
            )
    except Exception as exc:
        return DispatchResult(success=False, message=f"Tuya test failed: {exc!s}")


async def _get_tuya_connector(integration_id: str, tenant_id: uuid.UUID):
    """Load the TuyaConnector for a given integration."""
    from app.database import async_session_factory
    from app.integrations.connectors.base import get_connector_class
    from app.integrations.crypto import decrypt_config
    from app.integrations.models import IntegrationConfig, IntegrationDeviceMap

    async with async_session_factory() as session:
        config = await session.get(IntegrationConfig, uuid.UUID(integration_id))
        if config is None or config.tenant_id != tenant_id:
            return None
        if config.integration_type != "tuya":
            return None

        device_maps = (
            (
                await session.execute(
                    select(IntegrationDeviceMap).where(IntegrationDeviceMap.integration_id == config.id)
                )
            )
            .scalars()
            .all()
        )

        connector_cls = get_connector_class("tuya")
        if connector_cls is None:
            return None

        decrypted = decrypt_config(config.encrypted_config)
        return connector_cls(config, decrypted, list(device_maps))


# Register with dispatch
register_protocol("tuya_cloud", handle_command, test_tuya_connection)
