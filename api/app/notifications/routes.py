"""Notification API routes — channels, preferences, push subscriptions."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.notifications.models import NotificationChannel, NotificationLog, NotificationPreference, PushSubscription
from app.pagination import PaginatedResponse, PaginationParams, paginate

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


class PreferenceUpdate(BaseModel):
    severity_filter: str | None = None
    event_types: str | None = None
    enabled: bool | None = None


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


class NotificationLogResponse(BaseModel):
    id: str
    channel_type: str
    event_type: str
    severity: str
    subject: str
    body: str | None
    status: str
    error: str | None
    created_at: datetime


# ---------- Notification Channels ----------


@router.post("/channels", status_code=201)
async def create_channel(
    body: ChannelCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a new notification channel (email, SMS, push, or webhook)."""
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
        id=str(channel.id),
        channel_type=channel.channel_type,
        name=channel.name,
        config=channel.config,
        enabled=channel.enabled,
    )


@router.get("/channels", response_model=PaginatedResponse[ChannelResponse])
async def list_channels(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all notification channels for the current tenant."""
    q = select(NotificationChannel).where(NotificationChannel.tenant_id == user.tenant_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(
        items=[
            ChannelResponse(
                id=str(c.id),
                channel_type=c.channel_type,
                name=c.name,
                config=c.config,
                enabled=c.enabled,
            )
            for c in items
        ],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/channels/{channel_id}")
async def get_channel(
    channel_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single notification channel by ID."""
    channel = await session.get(NotificationChannel, UUID(channel_id))
    if not channel or channel.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Channel not found")
    return ChannelResponse(
        id=str(channel.id),
        channel_type=channel.channel_type,
        name=channel.name,
        config=channel.config,
        enabled=channel.enabled,
    )


@router.patch("/channels/{channel_id}")
async def update_channel(
    channel_id: str,
    body: ChannelUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a notification channel's configuration."""
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
        id=str(channel.id),
        channel_type=channel.channel_type,
        name=channel.name,
        config=channel.config,
        enabled=channel.enabled,
    )


@router.delete("/channels/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a notification channel by ID."""
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
    """Send a test notification through a channel to verify configuration."""
    from app.notifications.service import dispatch_alert

    channel = await session.get(NotificationChannel, UUID(channel_id))
    if not channel or channel.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Channel not found")

    try:
        await dispatch_alert(
            session,
            user.tenant_id,
            "info",
            "Test Notification",
            "This is a test notification from Tendril.",
        )
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Send failed: {e}") from e


# ---------- Preferences ----------


@router.get("/preferences", response_model=PaginatedResponse[PreferenceResponse])
async def list_preferences(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List notification preferences for the current user."""
    q = select(NotificationPreference).where(
        NotificationPreference.tenant_id == user.tenant_id,
        NotificationPreference.user_id == user.user_id,
    )
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(
        items=[
            PreferenceResponse(
                id=str(p.id),
                channel_id=str(p.channel_id),
                severity_filter=p.severity_filter,
                event_types=p.event_types,
                enabled=p.enabled,
            )
            for p in items
        ],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post("/preferences", status_code=201)
async def create_preference(
    body: PreferenceCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a notification preference linking a channel to event types."""
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
        id=str(pref.id),
        channel_id=str(pref.channel_id),
        severity_filter=pref.severity_filter,
        event_types=pref.event_types,
        enabled=pref.enabled,
    )


@router.get("/preferences/{pref_id}")
async def get_preference(
    pref_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single notification preference by ID."""
    pref = await session.get(NotificationPreference, UUID(pref_id))
    if not pref or pref.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Preference not found")
    return PreferenceResponse(
        id=str(pref.id),
        channel_id=str(pref.channel_id),
        severity_filter=pref.severity_filter,
        event_types=pref.event_types,
        enabled=pref.enabled,
    )


@router.patch("/preferences/{pref_id}")
async def update_preference(
    pref_id: str,
    body: PreferenceUpdate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a notification preference."""
    pref = await session.get(NotificationPreference, UUID(pref_id))
    if not pref or pref.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Preference not found")
    if body.severity_filter is not None:
        pref.severity_filter = body.severity_filter
    if body.event_types is not None:
        pref.event_types = body.event_types
    if body.enabled is not None:
        pref.enabled = body.enabled
    await session.commit()
    await session.refresh(pref)
    return PreferenceResponse(
        id=str(pref.id),
        channel_id=str(pref.channel_id),
        severity_filter=pref.severity_filter,
        event_types=pref.event_types,
        enabled=pref.enabled,
    )


@router.delete("/preferences/{pref_id}", status_code=204)
async def delete_preference(
    pref_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a notification preference by ID."""
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
    """Subscribe a device for web push notifications."""
    # Upsert: remove old subscriptions for same endpoint
    existing = (
        await session.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == user.user_id,
                PushSubscription.endpoint == body.endpoint,
            )
        )
    ).scalar_one_or_none()
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
    """Unsubscribe a device from web push notifications."""
    subs = (
        (await session.execute(select(PushSubscription).where(PushSubscription.user_id == user.user_id)))
        .scalars()
        .all()
    )
    for sub in subs:
        await session.delete(sub)
    await session.commit()


# ---------- Notification Log ----------


@router.get("/logs", response_model=PaginatedResponse[NotificationLogResponse])
async def list_notification_logs(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    event_type: str | None = None,
    channel_type: str | None = None,
    status: str | None = None,
):
    """List notification log entries for the current tenant."""
    query = select(NotificationLog).where(NotificationLog.tenant_id == user.tenant_id)
    if event_type:
        query = query.where(NotificationLog.event_type == event_type)
    if channel_type:
        query = query.where(NotificationLog.channel_type == channel_type)
    if status:
        query = query.where(NotificationLog.status == status)

    items, total = await paginate(session, query.order_by(NotificationLog.created_at.desc()), pagination)
    return PaginatedResponse(
        items=[
            NotificationLogResponse(
                id=str(item.id),
                channel_type=item.channel_type,
                event_type=item.event_type,
                severity=item.severity,
                subject=item.subject,
                body=item.body,
                status=item.status,
                error=item.error,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )
