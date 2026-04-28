"""Integration CRUD, webhook receiver, and manual sync routes."""

from __future__ import annotations

import hmac
import logging
import secrets
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.middleware import CurrentUser, get_tenant_session, require_role
from app.database import get_db
from app.integrations.connectors.base import get_connector_class
from app.integrations.crypto import decrypt_config, encrypt_config, redact_config
from app.integrations.models import (
    IntegrationConfig,
    IntegrationDeviceMap,
    IntegrationSyncLog,
)
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
# Helpers
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
    cfg = await session.get(IntegrationConfig, integration_id)
    if cfg is None or (tenant_id and cfg.tenant_id != tenant_id):
        raise HTTPException(status_code=404, detail="Integration not found")
    return cfg


# ---------------------------------------------------------------------------
# Integration Config CRUD
# ---------------------------------------------------------------------------


@router.post("", response_model=IntegrationResponse, status_code=201)
async def create_integration(
    body: IntegrationCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a new third-party integration (Home Assistant, MQTT, etc.)."""
    cfg = IntegrationConfig(
        tenant_id=user.tenant_id,
        type=body.type,
        name=body.name,
        config=encrypt_config(body.config),
        webhook_secret=secrets.token_urlsafe(32),
        enabled=body.enabled,
        poll_interval_s=body.poll_interval_s,
    )
    session.add(cfg)
    await session.commit()
    await session.refresh(cfg)
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
    q = (
        select(IntegrationConfig)
        .where(IntegrationConfig.tenant_id == user.tenant_id)
        .order_by(IntegrationConfig.created_at.desc())
    )
    if integration_type:
        q = q.where(IntegrationConfig.type == integration_type)
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
    updates = body.model_dump(exclude_unset=True)
    if "config" in updates and updates["config"] is not None:
        updates["config"] = encrypt_config(updates["config"])
    for field, value in updates.items():
        setattr(cfg, field, value)
    cfg.updated_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(cfg)
    return _config_to_response(cfg)


@router.delete("/{integration_id}", status_code=204)
async def delete_integration(
    integration_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete an integration by ID."""
    cfg = await _get_config_or_404(integration_id, session)
    await session.delete(cfg)
    await session.commit()
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
    await _get_config_or_404(integration_id, session)
    dm = IntegrationDeviceMap(
        tenant_id=user.tenant_id,
        integration_id=integration_id,
        **body.model_dump(),
    )
    session.add(dm)
    await session.commit()
    await session.refresh(dm)
    return dm


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
    q = select(IntegrationDeviceMap).where(IntegrationDeviceMap.integration_id == integration_id)
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
    dm = await session.get(IntegrationDeviceMap, device_id)
    if dm is None or dm.integration_id != integration_id:
        raise HTTPException(status_code=404, detail="Device mapping not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(dm, field, value)
    await session.commit()
    await session.refresh(dm)
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
    dm = await session.get(IntegrationDeviceMap, device_id)
    if dm is None or dm.integration_id != integration_id:
        raise HTTPException(status_code=404, detail="Device mapping not found")
    await session.delete(dm)
    await session.commit()


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
    q = (
        select(IntegrationSyncLog)
        .where(IntegrationSyncLog.integration_id == integration_id)
        .order_by(IntegrationSyncLog.synced_at.desc())
    )
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
    cfg = await session.get(IntegrationConfig, integration_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Integration not found")
    if not cfg.enabled:
        raise HTTPException(status_code=409, detail="Integration is disabled")

    # Authenticate via query param or body field
    payload = await request.json()
    provided_secret = request.query_params.get("secret") or payload.pop("webhook_secret", "")
    if not hmac.compare_digest(str(provided_secret), cfg.webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    connector_cls = get_connector_class(cfg.type)
    if connector_cls is None:
        logger.warning("No connector registered for type %s", cfg.type)
        raise HTTPException(status_code=501, detail=f"Connector '{cfg.type}' not implemented")

    device_maps_result = await session.execute(
        select(IntegrationDeviceMap).where(
            IntegrationDeviceMap.integration_id == integration_id,
            IntegrationDeviceMap.enabled.is_(True),
        )
    )
    device_maps = device_maps_result.scalars().all()

    connector = connector_cls(
        config=cfg,
        decrypted_config=decrypt_config(cfg.config),
        device_maps=list(device_maps),
    )
    result = await connector.handle_webhook(payload)

    # Persist readings to sensor tables
    if result.readings:
        try:
            await connector.persist_readings(session, result)
        except Exception:
            logger.exception("Webhook persist failed for %s (%s)", cfg.id, cfg.type)
            result.errors.append("Reading persistence failed")

    await connector.write_sync_log(session, result)
    cfg.last_synced_at = datetime.now(UTC)
    if result.status == "error":
        cfg.error_count += 1
    else:
        cfg.error_count = 0
    await session.commit()

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
    if not cfg.enabled:
        raise HTTPException(status_code=409, detail="Integration is disabled")

    connector_cls = get_connector_class(cfg.type)
    if connector_cls is None:
        raise HTTPException(status_code=501, detail=f"Connector '{cfg.type}' not implemented")

    device_maps_result = await session.execute(
        select(IntegrationDeviceMap)
        .where(
            IntegrationDeviceMap.integration_id == integration_id,
            IntegrationDeviceMap.enabled.is_(True),
        )
        .options(selectinload(IntegrationDeviceMap.integration))
    )
    device_maps = device_maps_result.scalars().all()

    connector = connector_cls(
        config=cfg,
        decrypted_config=decrypt_config(cfg.config),
        device_maps=list(device_maps),
    )
    result = await connector.poll()

    # Persist readings to sensor tables
    if result.readings:
        try:
            written = await connector.persist_readings(session, result)
            logger.info("Manual sync persisted %d readings for %s (%s)", written, cfg.id, cfg.type)
        except Exception:
            logger.exception("Manual sync persist failed for %s (%s)", cfg.id, cfg.type)
            result.errors.append("Reading persistence failed")

    await connector.write_sync_log(session, result)
    cfg.last_synced_at = datetime.now(UTC)
    if result.status == "error":
        cfg.error_count += 1
    else:
        cfg.error_count = 0
    await session.commit()

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
    if not cfg.enabled:
        raise HTTPException(status_code=409, detail="Integration is disabled")

    connector_cls = get_connector_class(cfg.type)
    if connector_cls is None:
        raise HTTPException(status_code=501, detail=f"Connector '{cfg.type}' not implemented")

    device_maps_result = await session.execute(
        select(IntegrationDeviceMap).where(
            IntegrationDeviceMap.integration_id == integration_id,
            IntegrationDeviceMap.enabled.is_(True),
        )
    )
    device_maps = device_maps_result.scalars().all()

    connector = connector_cls(
        config=cfg,
        decrypted_config=decrypt_config(cfg.config),
        device_maps=list(device_maps),
    )

    if not hasattr(connector, "discover_devices"):
        raise HTTPException(status_code=501, detail="This connector does not support device discovery")

    try:
        devices = await connector.discover_devices()
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
