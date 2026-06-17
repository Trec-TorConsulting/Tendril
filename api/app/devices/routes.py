"""Device registration, pairing, and management API endpoints.

This module is HTTP-only. All persistence, credential generation, and
pairing/validation logic live in ``app.devices.service``.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Annotated
from uuid import UUID

import qrcode
import qrcode.constants
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import record_audit
from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.billing.tier_gate import require_usage_limit
from app.database import async_session_factory
from app.devices import service
from app.pagination import PaginatedResponse, PaginationParams, paginate
from app.tenants.models import Device

router = APIRouter()


# ---------- Schemas ----------


class DeviceRegisterRequest(BaseModel):
    label: str | None = None


class DeviceRegisterResponse(BaseModel):
    id: UUID
    device_id: str
    psk: str  # returned ONCE at registration — user must save it
    label: str | None
    status: str


class DevicePairRequest(BaseModel):
    device_id: str
    psk: str
    tent_id: UUID | None = None


class DeviceUpdateRequest(BaseModel):
    label: str | None = None
    tent_id: UUID | None = None
    unassign_tent: bool = False


class DeviceResponse(BaseModel):
    id: UUID
    device_id: str
    label: str | None
    tent_id: UUID | None
    status: str
    last_seen: datetime | None
    firmware_version: str | None

    model_config = {"from_attributes": True}


# ---------- Endpoints ----------


@router.post(
    "/register",
    response_model=DeviceRegisterResponse,
    status_code=201,
    dependencies=[Depends(require_usage_limit("devices"))],
)
async def register_device(
    body: DeviceRegisterRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Register a new device. Returns the PSK once — it cannot be retrieved again."""
    assert user.tenant_id is not None  # guaranteed by require_role
    device, psk = await service.register_device(session, tenant_id=user.tenant_id, label=body.label)
    return DeviceRegisterResponse(
        id=device.id,
        device_id=device.device_id,
        psk=psk,
        label=device.label,
        status=device.status,
    )


@router.post("/pair", response_model=DeviceResponse)
async def pair_device(
    body: DevicePairRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Pair a device to the current tenant by verifying its PSK."""
    assert user.tenant_id is not None  # guaranteed by require_role
    try:
        device = await service.pair_device(
            session,
            tenant_id=user.tenant_id,
            device_id=body.device_id,
            psk=body.psk,
            tent_id=body.tent_id,
        )
    except service.DevicePairingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.get("", response_model=PaginatedResponse[DeviceResponse])
async def list_devices(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all devices for the current tenant (RLS-enforced)."""
    assert user.tenant_id is not None
    q = service.list_devices_query(tenant_id=user.tenant_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a specific device by device_id."""
    device = await service.get_device_by_external_id(session, device_id)
    if device is None or device.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    body: DeviceUpdateRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update device label or tent assignment."""
    device = await service.get_device_by_external_id(session, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return await service.update_device(
        session,
        device,
        label=body.label,
        tent_id=body.tent_id,
        unassign_tent=body.unassign_tent,
    )


@router.post("/{device_id}/revoke", response_model=DeviceResponse)
async def revoke_device(
    device_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Revoke a device — it will no longer be able to connect via MQTT."""
    device = await service.get_device_by_external_id(session, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return await service.revoke_device(session, device)


@router.delete("/{device_id}", status_code=204)
async def delete_device(
    device_id: str,
    request: Request,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a device permanently."""
    device = await service.get_device_by_external_id(session, device_id)
    if device is None or device.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Device not found")
    await record_audit(session, user.tenant_id, user.user_id, "delete", "device", device_id, request=request)
    await service.soft_delete_device(session, device)


@router.get("/{device_id}/qr", response_class=StreamingResponse)
async def get_device_qr(
    device_id: str,
    request: Request,
    sig: str = Query(..., description="HMAC signature"),
    exp: str = Query(..., description="Expiry timestamp"),
    tid: str = Query(..., description="Tenant ID"),
):
    """Generate a QR code PNG containing the device_id for pairing."""
    from app.auth.signed_url import verify_signed_url
    from app.database import set_rls_tenant

    tenant_id = verify_signed_url(request.url.path, sig, exp, tid)

    async with async_session_factory() as session:
        await set_rls_tenant(session, UUID(tenant_id))
        result = await session.execute(select(Device).where(Device.device_id == device_id))
        device = result.scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data(device.device_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
