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
    IntegrationCreate,
    IntegrationResponse,
    IntegrationUpdate,
    SyncLogResponse,
)

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
) -> IntegrationConfig:
    cfg = await session.get(IntegrationConfig, integration_id)
    if cfg is None:
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


@router.get("", response_model=list[IntegrationResponse])
async def list_integrations(
    user: Annotated[CurrentUser, Depends(require_role("owner", "member", "viewer"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    integration_type: str | None = Query(None, alias="type"),
):
    q = select(IntegrationConfig).order_by(IntegrationConfig.created_at.desc())
    if integration_type:
        q = q.where(IntegrationConfig.type == integration_type)
    result = await session.execute(q)
    return [_config_to_response(c) for c in result.scalars().all()]


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member", "viewer"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    cfg = await _get_config_or_404(integration_id, session)
    return _config_to_response(cfg)


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: UUID,
    body: IntegrationUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
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
    response_model=list[DeviceMapResponse],
)
async def list_device_maps(
    integration_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member", "viewer"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    await _get_config_or_404(integration_id, session)
    q = select(IntegrationDeviceMap).where(IntegrationDeviceMap.integration_id == integration_id)
    result = await session.execute(q)
    return result.scalars().all()


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
    response_model=list[SyncLogResponse],
)
async def list_sync_logs(
    integration_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member", "viewer"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    limit: int = Query(default=50, le=500),
):
    await _get_config_or_404(integration_id, session)
    q = (
        select(IntegrationSyncLog)
        .where(IntegrationSyncLog.integration_id == integration_id)
        .order_by(IntegrationSyncLog.synced_at.desc())
        .limit(limit)
    )
    result = await session.execute(q)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Webhook Receiver
# ---------------------------------------------------------------------------


@router.post("/webhook/{integration_id}")
async def receive_webhook(
    integration_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
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
