"""Devices domain service.

Holds the business operations for device registration, pairing,
listing, updates, revocation, and soft-deletion. Route handlers in
``app.devices.routes`` are HTTP-only and delegate to this module.

Conventions match the project standard (PR #192 / #208 / #209 / #210):

* First positional argument is always ``session: AsyncSession``.
* Functions return ORM model instances, dataclasses, or primitives;
  they never raise ``HTTPException`` — lookup misses return ``None``
  and domain validation failures raise typed errors.
* Query-builder helpers (``*_query``) return SQLAlchemy ``Select``
  for the route layer to hand to ``app.pagination.paginate``.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import bcrypt
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tenants.models import Device


class DevicePairingError(Exception):
    """Raised when a pairing attempt fails domain validation.

    ``status_code`` carries the HTTP status the route should map to:
    409 if the device belongs to another tenant, 401 if the PSK is
    wrong. Route layer translates this into an ``HTTPException``.
    """

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass(frozen=True, slots=True)
class DeviceCredentials:
    """The cleartext PSK + bcrypt hash for a newly minted device.

    The PSK is returned exactly once to the API caller; only the hash
    is persisted.
    """

    device_id: str
    psk: str
    psk_hash: str


# ─────────────────────────────────────────────────────────────────────────────
# Credential generation
# ─────────────────────────────────────────────────────────────────────────────


def generate_device_credentials() -> DeviceCredentials:
    """Generate a fresh ``td-…`` device id, a 32-byte url-safe PSK,
    and the bcrypt hash to persist alongside it."""
    device_id = f"td-{secrets.token_hex(6)}"
    psk = secrets.token_urlsafe(32)
    psk_hash = bcrypt.hashpw(psk.encode(), bcrypt.gensalt()).decode()
    return DeviceCredentials(device_id=device_id, psk=psk, psk_hash=psk_hash)


# ─────────────────────────────────────────────────────────────────────────────
# Lookups
# ─────────────────────────────────────────────────────────────────────────────


async def get_device_by_external_id(session: AsyncSession, device_id: str) -> Device | None:
    """Fetch a device by its external ``device_id`` (e.g. ``td-abc123``).

    Returns the row even when soft-deleted — callers that should treat
    soft-deletes as not-found must check ``device.deleted_at``.
    """
    result = await session.execute(select(Device).where(Device.device_id == device_id))
    return result.scalar_one_or_none()


def list_devices_query(*, tenant_id: UUID) -> Select:
    """Build the query for listing live (not soft-deleted) devices in
    the tenant; route layer paginates."""
    return (
        select(Device)
        .where(Device.deleted_at.is_(None), Device.tenant_id == tenant_id)
        .order_by(Device.created_at.desc())
    )


# ─────────────────────────────────────────────────────────────────────────────
# Mutations
# ─────────────────────────────────────────────────────────────────────────────


async def register_device(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    label: str | None,
) -> tuple[Device, str]:
    """Mint a new device + PSK pair, persist it, record metered usage.

    Returns ``(device, plaintext_psk)``. The caller must surface the
    PSK exactly once and never store it.
    """
    # Local import keeps the billing module out of devices' import cycle.
    from app.billing.metering import record_usage

    creds = generate_device_credentials()
    device = Device(
        tenant_id=tenant_id,
        device_id=creds.device_id,
        psk_hash=creds.psk_hash,
        label=label,
        status="unpaired",
    )
    session.add(device)
    await record_usage(session, tenant_id, "devices")
    await session.commit()
    await session.refresh(device)
    return device, creds.psk


async def pair_device(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    device_id: str,
    psk: str,
    tent_id: UUID | None,
) -> Device | None:
    """Attempt to pair a device to ``tenant_id``.

    Returns the paired ``Device`` on success; returns ``None`` when no
    device exists with that external id (route → 404). Raises
    ``DevicePairingError`` with the appropriate status code for
    cross-tenant conflict (409) or invalid PSK (401).
    """
    device = await get_device_by_external_id(session, device_id)
    if device is None:
        return None

    if device.status == "paired" and device.tenant_id != tenant_id:
        raise DevicePairingError(409, "Device is already claimed by another tenant")

    if not bcrypt.checkpw(psk.encode(), device.psk_hash.encode()):
        raise DevicePairingError(401, "Invalid pre-shared key")

    device.status = "paired"
    device.tenant_id = tenant_id
    if tent_id is not None:
        device.tent_id = tent_id
    await session.commit()
    await session.refresh(device)
    return device


async def update_device(
    session: AsyncSession,
    device: Device,
    *,
    label: str | None = None,
    tent_id: UUID | None = None,
    unassign_tent: bool = False,
) -> Device:
    """Apply partial updates to a device.

    Mirrors the route's tri-state for tent assignment:
    * ``tent_id`` provided → assign
    * ``unassign_tent`` True → clear
    * neither → no change
    """
    if label is not None:
        device.label = label
    if tent_id is not None:
        device.tent_id = tent_id
    elif unassign_tent:
        device.tent_id = None
    await session.commit()
    await session.refresh(device)
    return device


async def revoke_device(session: AsyncSession, device: Device) -> Device:
    """Mark a device revoked; MQTT auth will reject future connections."""
    device.status = "revoked"
    await session.commit()
    await session.refresh(device)
    return device


async def soft_delete_device(session: AsyncSession, device: Device) -> None:
    """Soft-delete a device by stamping ``deleted_at``."""
    device.deleted_at = datetime.now(UTC)
    await session.commit()
