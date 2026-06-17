"""Integration CRUD, webhook receiver, and manual sync routes.

This module is HTTP-only. All persistence, encryption, connector
dispatch, webhook authentication, and sync bookkeeping live in
``app.integrations.service``.
"""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_tenant_session, require_role
from app.billing.tier_gate import require_usage_limit
from app.database import get_db
from app.integrations import service
from app.integrations.crypto import decrypt_config, redact_config
from app.integrations.models import IntegrationConfig
from app.integrations.schemas import (
    DeviceMapCreate,
    DeviceMapResponse,
    DeviceMapUpdate,
    DiscoveredDeviceResponse,
    IntegrationCreate,
    IntegrationResponse,
    IntegrationUpdate,
    SyncLogResponse,
)
from app.pagination import PaginatedResponse, PaginationParams, paginate

logger = logging.getLogger("tendril.integrations")

router = APIRouter()


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------


def _config_to_response(cfg: IntegrationConfig) -> IntegrationResponse:
    """Build an IntegrationResponse with credentials redacted."""
    plain = decrypt_config(cfg.config)
    return IntegrationResponse(
        id=cfg.id,
        type=cfg.type,
        name=cfg.name,
        config=redact_config(plain),
        webhook_secret=cfg.webhook_secret,
        enabled=cfg.enabled,
        poll_interval_s=cfg.poll_interval_s,
        last_synced_at=cfg.last_synced_at,
        error_count=cfg.error_count,
        created_at=cfg.created_at,
        updated_at=cfg.updated_at,
    )


async def _get_config_or_404(
    integration_id: UUID,
    session: AsyncSession,
    tenant_id: UUID | None = None,
) -> IntegrationConfig:
    cfg = await service.get_integration(session, integration_id, tenant_id=tenant_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Integration not found")
    return cfg


# ---------------------------------------------------------------------------
# Integration Config CRUD
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=IntegrationResponse,
    status_code=201,
    dependencies=[Depends(require_usage_limit("integrations"))],
)
async def create_integration(
    body: IntegrationCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a new third-party integration (Home Assistant, MQTT, etc.)."""
    assert user.tenant_id is not None  # guaranteed by require_role
    cfg = await service.create_integration(
        session,
        tenant_id=user.tenant_id,
        integration_type=body.type,
        name=body.name,
        config=body.config,
        enabled=body.enabled,
        poll_interval_s=body.poll_interval_s or 60,
    )
    logger.info("Integration created: %s (%s) for tenant %s", cfg.id, cfg.type, user.tenant_id)
    return _config_to_response(cfg)


@router.get("", response_model=PaginatedResponse[IntegrationResponse])
async def list_integrations(
    user: Annotated[CurrentUser, Depends(require_role("owner", "member", "viewer"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    integration_type: str | None = Query(None, alias="type"),
):
    """List all integrations for the current tenant."""
    assert user.tenant_id is not None
    q = service.list_integrations_query(tenant_id=user.tenant_id, integration_type=integration_type)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(
        items=[_config_to_response(c) for c in items],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member", "viewer"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get an integration by ID."""
    cfg = await _get_config_or_404(integration_id, session, tenant_id=user.tenant_id)
    return _config_to_response(cfg)


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: UUID,
    body: IntegrationUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update an integration's configuration."""
    cfg = await _get_config_or_404(integration_id, session)
    await service.update_integration(session, cfg, body.model_dump(exclude_unset=True))
    return _config_to_response(cfg)


@router.delete("/{integration_id}", status_code=204)
async def delete_integration(
    integration_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete an integration by ID."""
    cfg = await _get_config_or_404(integration_id, session)
    await service.delete_integration(session, cfg)
    logger.info("Integration deleted: %s for tenant %s", integration_id, user.tenant_id)


# ---------------------------------------------------------------------------
# Device Map CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/{integration_id}/devices",
    response_model=DeviceMapResponse,
    status_code=201,
)
async def create_device_map(
    integration_id: UUID,
    body: DeviceMapCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a device mapping between an integration and a local device."""
    config = await _get_config_or_404(integration_id, session)

    # MQTT topic validation is connector-specific and lives there; the
    # route's role is only to surface the 400 detail.
    if config.type == "mqtt_generic" and body.external_id:
        from app.integrations.connectors.mqtt_generic import validate_mqtt_topic

        topic_error = validate_mqtt_topic(body.external_id)
        if topic_error:
            raise HTTPException(status_code=400, detail=f"Invalid MQTT topic: {topic_error}")

    assert user.tenant_id is not None
    return await service.create_device_map(
        session,
        tenant_id=user.tenant_id,
        integration_id=integration_id,
        data=body.model_dump(),
    )


@router.get(
    "/{integration_id}/devices",
    response_model=PaginatedResponse[DeviceMapResponse],
)
async def list_device_maps(
    integration_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member", "viewer"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List device mappings for an integration."""
    await _get_config_or_404(integration_id, session)
    q = service.list_device_maps_query(integration_id=integration_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.patch(
    "/{integration_id}/devices/{device_id}",
    response_model=DeviceMapResponse,
)
async def update_device_map(
    integration_id: UUID,
    device_id: UUID,
    body: DeviceMapUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a device mapping."""
    await _get_config_or_404(integration_id, session)
    dm = await service.get_device_map(session, integration_id=integration_id, device_map_id=device_id)
    if dm is None:
        raise HTTPException(status_code=404, detail="Device mapping not found")
    await service.update_device_map(session, dm, body.model_dump(exclude_unset=True))
    return dm


@router.delete("/{integration_id}/devices/{device_id}", status_code=204)
async def delete_device_map(
    integration_id: UUID,
    device_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a device mapping by ID."""
    await _get_config_or_404(integration_id, session)
    dm = await service.get_device_map(session, integration_id=integration_id, device_map_id=device_id)
    if dm is None:
        raise HTTPException(status_code=404, detail="Device mapping not found")
    await service.delete_device_map(session, dm)


# ---------------------------------------------------------------------------
# Sync Logs
# ---------------------------------------------------------------------------


@router.get(
    "/{integration_id}/logs",
    response_model=PaginatedResponse[SyncLogResponse],
)
async def list_sync_logs(
    integration_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member", "viewer"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List synchronization logs for an integration."""
    await _get_config_or_404(integration_id, session)
    q = service.list_sync_logs_query(integration_id=integration_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


# ---------------------------------------------------------------------------
# Webhook Receiver
# ---------------------------------------------------------------------------


@router.post("/webhook/{integration_id}")
async def receive_webhook(
    integration_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Receive inbound data from an external platform.

    The webhook_secret must be provided as a ``secret`` query param or in the
    JSON body under the ``webhook_secret`` key.
    """
    cfg = await service.get_integration(session, integration_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Integration not found")

    payload = await request.json()
    provided_secret = request.query_params.get("secret") or payload.pop("webhook_secret", "")

    try:
        result = await service.process_webhook(session, cfg=cfg, provided_secret=provided_secret, payload=payload)
    except service.IntegrationDisabledError as exc:
        raise HTTPException(status_code=409, detail="Integration is disabled") from exc
    except service.WebhookAuthError as exc:
        raise HTTPException(status_code=401, detail="Invalid webhook secret") from exc
    except service.UnsupportedConnectorError as exc:
        logger.warning("No connector registered for type %s", exc.integration_type)
        raise HTTPException(
            status_code=501,
            detail=f"Connector '{exc.integration_type}' not implemented",
        ) from exc

    return {
        "status": result.status,
        "readings_count": result.readings_count,
        "error_message": result.error_message,
    }


# ---------------------------------------------------------------------------
# Manual Sync Trigger
# ---------------------------------------------------------------------------


@router.post("/{integration_id}/sync")
async def trigger_sync(
    integration_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Trigger an immediate poll for a polling-based integration."""
    cfg = await _get_config_or_404(integration_id, session)
    try:
        result = await service.trigger_sync(session, cfg=cfg)
    except service.IntegrationDisabledError as exc:
        raise HTTPException(status_code=409, detail="Integration is disabled") from exc
    except service.UnsupportedConnectorError as exc:
        raise HTTPException(
            status_code=501,
            detail=f"Connector '{exc.integration_type}' not implemented",
        ) from exc

    return {
        "status": result.status,
        "readings_count": result.readings_count,
        "error_message": result.error_message,
    }


# ---------------------------------------------------------------------------
# Device Discovery
# ---------------------------------------------------------------------------


@router.post(
    "/{integration_id}/discover",
    response_model=list[DiscoveredDeviceResponse],
)
async def discover_devices(
    integration_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Discover available devices from an external platform.

    Calls the connector's ``discover_devices()`` method to fetch available
    devices/sensors that can be mapped to tents or buckets.
    """
    cfg = await _get_config_or_404(integration_id, session)
    try:
        devices = await service.discover_devices(session, cfg=cfg)
    except service.IntegrationDisabledError as exc:
        raise HTTPException(status_code=409, detail="Integration is disabled") from exc
    except service.UnsupportedConnectorError as exc:
        raise HTTPException(
            status_code=501,
            detail=f"Connector '{exc.integration_type}' not implemented",
        ) from exc
    except service.DiscoveryNotSupportedError as exc:
        raise HTTPException(
            status_code=501,
            detail="This connector does not support device discovery",
        ) from exc
    except Exception as exc:
        logger.exception("Discovery failed for integration %s", integration_id)
        raise HTTPException(status_code=502, detail=f"Discovery failed: {exc}") from exc

    return [
        DiscoveredDeviceResponse(
            external_id=d.external_id,
            name=d.name,
            device_type=d.device_type,
            latest_reading=d.latest_reading,
        )
        for d in devices
    ]
