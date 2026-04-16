"""Notification API routes — channels, preferences, push subscriptions."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.notifications.models import NotificationChannel, NotificationPreference, PushSubscription

router = APIRouter()


# ---------- Schemas ----------

class ChannelCreate(BaseModel):
    channel_type: str  # discord, slack, email, sms
    name: str
    config: dict

class ChannelUpdate(BaseModel):
    name: str | None = None
    config: dict | None = None
    enabled: bool | None = None

class ChannelResponse(BaseModel):
    id: str
    channel_type: str
    name: str
    config: dict
    enabled: bool

class PreferenceCreate(BaseModel):
    channel_id: str
    severity_filter: str = "warning,critical"
    event_types: str = "all"

class PreferenceResponse(BaseModel):
    id: str
    channel_id: str
    severity_filter: str
    event_types: str
    enabled: bool

class PushSubCreate(BaseModel):
    endpoint: str
    p256dh: str
    auth: str

class PushSubResponse(BaseModel):
    id: str
    endpoint: str


# ---------- Notification Channels ----------

@router.post("/channels", status_code=201)
async def create_channel(
    body: ChannelCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    if body.channel_type not in ("discord", "slack", "email", "sms"):
        raise HTTPException(status_code=422, detail="Invalid channel type")

    channel = NotificationChannel(
        tenant_id=user.tenant_id,
        channel_type=body.channel_type,
        name=body.name,
        config=body.config,
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return ChannelResponse(
        id=str(channel.id), channel_type=channel.channel_type,
        name=channel.name, config=channel.config, enabled=channel.enabled,
    )


@router.get("/channels")
async def list_channels(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    result = await session.execute(
        select(NotificationChannel).where(NotificationChannel.tenant_id == user.tenant_id)
    )
    return [
        ChannelResponse(
            id=str(c.id), channel_type=c.channel_type,
            name=c.name, config=c.config, enabled=c.enabled,
        )
        for c in result.scalars().all()
    ]


@router.patch("/channels/{channel_id}")
async def update_channel(
    channel_id: str,
    body: ChannelUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    channel = await session.get(NotificationChannel, UUID(channel_id))
    if not channel or channel.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Channel not found")

    if body.name is not None:
        channel.name = body.name
    if body.config is not None:
        channel.config = body.config
    if body.enabled is not None:
        channel.enabled = body.enabled

    await session.commit()
    await session.refresh(channel)
    return ChannelResponse(
        id=str(channel.id), channel_type=channel.channel_type,
        name=channel.name, config=channel.config, enabled=channel.enabled,
    )


@router.delete("/channels/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    channel = await session.get(NotificationChannel, UUID(channel_id))
    if not channel or channel.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Channel not found")
    await session.delete(channel)
    await session.commit()


# ---------- Test channel ----------

@router.post("/channels/{channel_id}/test")
async def test_channel(
    channel_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    from app.notifications.service import dispatch_alert

    channel = await session.get(NotificationChannel, UUID(channel_id))
    if not channel or channel.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Channel not found")

    try:
        await dispatch_alert(
            session, user.tenant_id, "info",
            "Test Notification", "This is a test notification from Tendril.",
        )
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Send failed: {e}")


# ---------- Preferences ----------

@router.get("/preferences")
async def list_preferences(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    result = await session.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == user.user_id,
        )
    )
    return [
        PreferenceResponse(
            id=str(p.id), channel_id=str(p.channel_id),
            severity_filter=p.severity_filter, event_types=p.event_types,
            enabled=p.enabled,
        )
        for p in result.scalars().all()
    ]


@router.post("/preferences", status_code=201)
async def create_preference(
    body: PreferenceCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    pref = NotificationPreference(
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        channel_id=UUID(body.channel_id),
        severity_filter=body.severity_filter,
        event_types=body.event_types,
    )
    session.add(pref)
    await session.commit()
    await session.refresh(pref)
    return PreferenceResponse(
        id=str(pref.id), channel_id=str(pref.channel_id),
        severity_filter=pref.severity_filter, event_types=pref.event_types,
        enabled=pref.enabled,
    )


@router.delete("/preferences/{pref_id}", status_code=204)
async def delete_preference(
    pref_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    pref = await session.get(NotificationPreference, UUID(pref_id))
    if not pref or pref.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Preference not found")
    await session.delete(pref)
    await session.commit()


# ---------- Push Subscriptions ----------

@router.post("/push/subscribe", status_code=201)
async def push_subscribe(
    body: PushSubCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    # Upsert: remove old subscriptions for same endpoint
    existing = (await session.execute(
        select(PushSubscription).where(
            PushSubscription.user_id == user.user_id,
            PushSubscription.endpoint == body.endpoint,
        )
    )).scalar_one_or_none()
    if existing:
        existing.p256dh = body.p256dh
        existing.auth = body.auth
    else:
        sub = PushSubscription(
            tenant_id=user.tenant_id,
            user_id=user.user_id,
            endpoint=body.endpoint,
            p256dh=body.p256dh,
            auth=body.auth,
        )
        session.add(sub)
    await session.commit()
    return {"status": "subscribed"}


@router.delete("/push/unsubscribe", status_code=204)
async def push_unsubscribe(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    subs = (await session.execute(
        select(PushSubscription).where(PushSubscription.user_id == user.user_id)
    )).scalars().all()
    for sub in subs:
        await session.delete(sub)
    await session.commit()
