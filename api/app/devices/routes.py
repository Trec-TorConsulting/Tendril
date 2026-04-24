"""Device registration, pairing, and management API endpoints."""
from __future__ import annotations

import io
import secrets
from typing import Annotated
from uuid import UUID

import bcrypt
import qrcode
import qrcode.constants
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.auth.jwt import decode_token
from app.database import async_session_factory
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
    last_seen: str | None
    firmware_version: str | None

    model_config = {"from_attributes": True}


# ---------- Endpoints ----------

@router.post("/register", response_model=DeviceRegisterResponse, status_code=201)
async def register_device(
    body: DeviceRegisterRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Register a new device. Returns the PSK once — it cannot be retrieved again."""
    device_id = f"td-{secrets.token_hex(6)}"
    psk = secrets.token_urlsafe(32)
    psk_hash = bcrypt.hashpw(psk.encode(), bcrypt.gensalt()).decode()

    device = Device(
        tenant_id=user.tenant_id,
        device_id=device_id,
        psk_hash=psk_hash,
        label=body.label,
        status="unpaired",
    )
    session.add(device)
    await session.commit()
    await session.refresh(device)

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
    result = await session.execute(select(Device).where(Device.device_id == body.device_id))
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.status == "paired" and device.tenant_id != user.tenant_id:
        raise HTTPException(status_code=409, detail="Device is already claimed by another tenant")

    if not bcrypt.checkpw(body.psk.encode(), device.psk_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid pre-shared key")

    device.status = "paired"
    device.tenant_id = user.tenant_id
    if body.tent_id is not None:
        device.tent_id = body.tent_id
    await session.commit()
    await session.refresh(device)
    return device


@router.get("", response_model=list[DeviceResponse])
async def list_devices(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """List all devices for the current tenant (RLS-enforced)."""
    result = await session.execute(select(Device).order_by(Device.created_at.desc()))
    return result.scalars().all()


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a specific device by device_id."""
    result = await session.execute(select(Device).where(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if device is None:
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
    result = await session.execute(select(Device).where(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    if body.label is not None:
        device.label = body.label
    if body.tent_id is not None:
        device.tent_id = body.tent_id
    elif body.unassign_tent:
        device.tent_id = None
    await session.commit()
    await session.refresh(device)
    return device


@router.post("/{device_id}/revoke", response_model=DeviceResponse)
async def revoke_device(
    device_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Revoke a device — it will no longer be able to connect via MQTT."""
    result = await session.execute(select(Device).where(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    device.status = "revoked"
    await session.commit()
    await session.refresh(device)
    return device


@router.delete("/{device_id}", status_code=204)
async def delete_device(
    device_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a device permanently."""
    result = await session.execute(select(Device).where(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    await session.delete(device)
    await session.commit()


@router.get("/{device_id}/qr", response_class=StreamingResponse)
async def get_device_qr(
    device_id: str,
    token: str = Query(..., description="JWT access token"),
):
    """Generate a QR code PNG containing the device_id for pairing."""
    from jose import JWTError
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    tenant_id = payload["tid"]

    async with async_session_factory() as session:
        await session.execute(text(f"SET app.current_tenant = '{tenant_id}'"))
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
