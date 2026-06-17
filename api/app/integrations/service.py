"""Integrations domain service.

Holds the business operations for the integration platform: config
CRUD, device-map CRUD, sync log listing, webhook ingestion, manual
sync trigger, and device discovery. Routes in
``app.integrations.routes`` are HTTP-only and delegate to this module.

Conventions match the project standard (PR #192 / #208-#218):

* First positional argument is always ``session: AsyncSession``.
* Functions return ORM models, dataclasses, or primitives; they never
  raise ``HTTPException`` — lookup misses return ``None`` and domain
  validation failures raise typed errors.
* Query-builder helpers (``*_query``) return ``Select`` for the route
  layer to hand to ``app.pagination.paginate``.
"""

from __future__ import annotations

import hmac
import logging
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.integrations.connectors.base import get_connector_class
from app.integrations.crypto import decrypt_config, encrypt_config
from app.integrations.models import (
    IntegrationConfig,
    IntegrationDeviceMap,
    IntegrationSyncLog,
)

logger = logging.getLogger("tendril.integrations")


# ─────────────────────────────────────────────────────────────────────────────
# Typed errors
# ─────────────────────────────────────────────────────────────────────────────


class IntegrationDisabledError(Exception):
    """Raised when callers try to act on a disabled integration. Route → 409."""


class WebhookAuthError(Exception):
    """Raised when the supplied webhook secret doesn't match. Route → 401."""


class UnsupportedConnectorError(Exception):
    """Raised when no connector class is registered for a config's type.
    Route → 501."""

    def __init__(self, integration_type: str) -> None:
        self.integration_type = integration_type
        super().__init__(f"Connector not registered: {integration_type!r}")


class DiscoveryNotSupportedError(Exception):
    """Raised when a connector doesn't implement ``discover_devices``.
    Route → 501."""


# ─────────────────────────────────────────────────────────────────────────────
# Config CRUD
# ─────────────────────────────────────────────────────────────────────────────


def generate_webhook_secret() -> str:
    """Mint a 32-byte url-safe webhook secret."""
    return secrets.token_urlsafe(32)


async def create_integration(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    integration_type: str,
    name: str,
    config: dict[str, Any],
    enabled: bool,
    poll_interval_s: int,
) -> IntegrationConfig:
    """Create an ``IntegrationConfig`` and record metered usage.

    The ``config`` dict is encrypted at rest via ``encrypt_config``.
    A fresh ``webhook_secret`` is generated.
    """
    # Local import keeps billing out of integrations' import cycle.
    from app.billing.metering import record_usage

    cfg = IntegrationConfig(
        tenant_id=tenant_id,
        type=integration_type,
        name=name,
        config=encrypt_config(config),
        webhook_secret=generate_webhook_secret(),
        enabled=enabled,
        poll_interval_s=poll_interval_s,
    )
    session.add(cfg)
    await record_usage(session, tenant_id, "integrations")
    await session.commit()
    await session.refresh(cfg)
    return cfg


def list_integrations_query(*, tenant_id: UUID, integration_type: str | None = None) -> Select:
    """Build the listing query; route layer paginates."""
    q = (
        select(IntegrationConfig)
        .where(IntegrationConfig.tenant_id == tenant_id)
        .order_by(IntegrationConfig.created_at.desc())
    )
    if integration_type:
        q = q.where(IntegrationConfig.type == integration_type)
    return q


async def get_integration(
    session: AsyncSession,
    integration_id: UUID,
    *,
    tenant_id: UUID | None = None,
) -> IntegrationConfig | None:
    """Fetch an integration by id. When ``tenant_id`` is provided, returns
    ``None`` for cross-tenant access (route → 404 either way; no leak)."""
    cfg = await session.get(IntegrationConfig, integration_id)
    if cfg is None:
        return None
    if tenant_id is not None and cfg.tenant_id != tenant_id:
        return None
    return cfg


async def update_integration(
    session: AsyncSession,
    cfg: IntegrationConfig,
    updates: dict[str, Any],
) -> IntegrationConfig:
    """Apply partial updates to an integration config.

    The ``config`` field, when present, is re-encrypted before assignment.
    ``updated_at`` is bumped to ``now(UTC)``.
    """
    if "config" in updates and updates["config"] is not None:
        updates["config"] = encrypt_config(updates["config"])
    for field, value in updates.items():
        setattr(cfg, field, value)
    cfg.updated_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(cfg)
    return cfg


async def delete_integration(session: AsyncSession, cfg: IntegrationConfig) -> None:
    await session.delete(cfg)
    await session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Device map CRUD
# ─────────────────────────────────────────────────────────────────────────────


async def create_device_map(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    integration_id: UUID,
    data: dict[str, Any],
) -> IntegrationDeviceMap:
    dm = IntegrationDeviceMap(
        tenant_id=tenant_id,
        integration_id=integration_id,
        **data,
    )
    session.add(dm)
    await session.commit()
    await session.refresh(dm)
    return dm


def list_device_maps_query(*, integration_id: UUID) -> Select:
    return select(IntegrationDeviceMap).where(IntegrationDeviceMap.integration_id == integration_id)


async def get_device_map(
    session: AsyncSession,
    *,
    integration_id: UUID,
    device_map_id: UUID,
) -> IntegrationDeviceMap | None:
    """Fetch a device map and assert it belongs to ``integration_id``.

    Returns ``None`` for unknown id *or* mismatch — route maps both
    cases to 404 with the same detail.
    """
    dm = await session.get(IntegrationDeviceMap, device_map_id)
    if dm is None or dm.integration_id != integration_id:
        return None
    return dm


async def update_device_map(
    session: AsyncSession,
    dm: IntegrationDeviceMap,
    updates: dict[str, Any],
) -> IntegrationDeviceMap:
    for field, value in updates.items():
        setattr(dm, field, value)
    await session.commit()
    await session.refresh(dm)
    return dm


async def delete_device_map(session: AsyncSession, dm: IntegrationDeviceMap) -> None:
    await session.delete(dm)
    await session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Sync logs
# ─────────────────────────────────────────────────────────────────────────────


def list_sync_logs_query(*, integration_id: UUID) -> Select:
    return (
        select(IntegrationSyncLog)
        .where(IntegrationSyncLog.integration_id == integration_id)
        .order_by(IntegrationSyncLog.synced_at.desc())
    )


# ─────────────────────────────────────────────────────────────────────────────
# Webhook receiver
# ─────────────────────────────────────────────────────────────────────────────


def verify_webhook_secret(provided: str, expected: str) -> None:
    """Constant-time compare; raise :class:`WebhookAuthError` on mismatch."""
    if not hmac.compare_digest(str(provided), expected):
        raise WebhookAuthError("Invalid webhook secret")


@dataclass(frozen=True, slots=True)
class WebhookSyncResult:
    """Public shape returned by the webhook + sync endpoints."""

    status: str
    readings_count: int
    error_message: str | None


async def _list_enabled_device_maps(
    session: AsyncSession, *, integration_id: UUID, eager_integration: bool = False
) -> list[IntegrationDeviceMap]:
    """Active device maps for ``integration_id``. With ``eager_integration``
    the join to the parent integration is pre-loaded (the manual-sync
    path needs this since the connector inspects ``dm.integration``)."""
    stmt = select(IntegrationDeviceMap).where(
        IntegrationDeviceMap.integration_id == integration_id,
        IntegrationDeviceMap.enabled.is_(True),
    )
    if eager_integration:
        stmt = stmt.options(selectinload(IntegrationDeviceMap.integration))
    return list((await session.execute(stmt)).scalars().all())


def _resolve_connector(cfg: IntegrationConfig):
    """Resolve the connector class for ``cfg.type`` or raise."""
    connector_cls = get_connector_class(cfg.type)
    if connector_cls is None:
        raise UnsupportedConnectorError(cfg.type)
    return connector_cls


def _instantiate_connector(connector_cls, cfg: IntegrationConfig, device_maps: list[IntegrationDeviceMap]):
    """Build a connector instance with the decrypted config."""
    return connector_cls(
        config=cfg,
        decrypted_config=decrypt_config(cfg.config),
        device_maps=device_maps,
    )


async def _persist_and_log_sync(
    session: AsyncSession,
    connector,
    result,
    cfg: IntegrationConfig,
    *,
    context: str,
) -> None:
    """Shared bookkeeping for webhook + manual sync flows:

    * persist readings (best-effort — failures get appended to
      ``result.errors`` so they show up in the sync log without
      aborting the rest of the bookkeeping),
    * write sync log,
    * bump ``last_synced_at`` and ``error_count``.
    """
    if result.readings:
        try:
            written = await connector.persist_readings(session, result)
            logger.info(
                "%s persisted %d readings for %s (%s)",
                context,
                written,
                cfg.id,
                cfg.type,
            )
        except Exception:
            logger.exception("%s persist failed for %s (%s)", context, cfg.id, cfg.type)
            result.errors.append("Reading persistence failed")

    await connector.write_sync_log(session, result)
    cfg.last_synced_at = datetime.now(UTC)
    if result.status == "error":
        cfg.error_count += 1
    else:
        cfg.error_count = 0
    await session.commit()


async def process_webhook(
    session: AsyncSession,
    *,
    cfg: IntegrationConfig,
    provided_secret: str,
    payload: dict[str, Any],
) -> WebhookSyncResult:
    """Authenticate + dispatch + persist a webhook delivery.

    Raises ``IntegrationDisabledError`` (route → 409),
    ``WebhookAuthError`` (route → 401), or
    ``UnsupportedConnectorError`` (route → 501).
    """
    if not cfg.enabled:
        raise IntegrationDisabledError("Integration is disabled")
    verify_webhook_secret(provided_secret, cfg.webhook_secret)

    connector_cls = _resolve_connector(cfg)
    device_maps = await _list_enabled_device_maps(session, integration_id=cfg.id)
    connector = _instantiate_connector(connector_cls, cfg, device_maps)

    result = await connector.handle_webhook(payload)
    await _persist_and_log_sync(session, connector, result, cfg, context="Webhook")

    return WebhookSyncResult(
        status=result.status,
        readings_count=result.readings_count,
        error_message=result.error_message,
    )


async def trigger_sync(session: AsyncSession, *, cfg: IntegrationConfig) -> WebhookSyncResult:
    """Run an immediate poll for a polling-based integration.

    Same error semantics as :func:`process_webhook` (minus the secret
    check — the route already authorises via ``require_role``).
    """
    if not cfg.enabled:
        raise IntegrationDisabledError("Integration is disabled")

    connector_cls = _resolve_connector(cfg)
    device_maps = await _list_enabled_device_maps(session, integration_id=cfg.id, eager_integration=True)
    connector = _instantiate_connector(connector_cls, cfg, device_maps)

    result = await connector.poll()
    await _persist_and_log_sync(session, connector, result, cfg, context="Manual sync")

    return WebhookSyncResult(
        status=result.status,
        readings_count=result.readings_count,
        error_message=result.error_message,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Discovery
# ─────────────────────────────────────────────────────────────────────────────


async def discover_devices(session: AsyncSession, *, cfg: IntegrationConfig) -> list:
    """Ask the connector to enumerate available devices.

    Raises ``IntegrationDisabledError`` (409),
    ``UnsupportedConnectorError`` (501), or
    ``DiscoveryNotSupportedError`` (501) when the resolved connector
    doesn't implement ``discover_devices``.

    Any unexpected exception from the connector is re-raised so the
    route can map it to a 502.
    """
    if not cfg.enabled:
        raise IntegrationDisabledError("Integration is disabled")

    connector_cls = _resolve_connector(cfg)
    device_maps = await _list_enabled_device_maps(session, integration_id=cfg.id)
    connector = _instantiate_connector(connector_cls, cfg, device_maps)

    if not hasattr(connector, "discover_devices"):
        raise DiscoveryNotSupportedError("Connector does not support device discovery")

    return await connector.discover_devices()
