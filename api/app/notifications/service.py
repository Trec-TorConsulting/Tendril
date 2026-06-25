"""Notification dispatch — send alerts via configured channels."""

from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.models import (
    NotificationChannel,
    NotificationLog,
    NotificationPreference,
    PushSubscription,
)

logger = logging.getLogger("tendril.notifications")


def _record_notification_log(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    channel_type: str,
    severity: str,
    subject: str,
    body: str,
    status: str,
    event_type: str,
    error: str | None = None,
) -> None:
    session.add(
        NotificationLog(
            tenant_id=tenant_id,
            channel_type=channel_type,
            event_type=event_type,
            severity=severity,
            subject=subject,
            body=body,
            status=status,
            error=error,
        )
    )


def _in_app_delivery_status(
    *,
    eligible_channels: Sequence[NotificationChannel],
    push_subscriptions: Sequence[PushSubscription],
) -> str:
    return "sent" if eligible_channels or push_subscriptions else "skipped"


async def dispatch_alert(
    session: AsyncSession,
    tenant_id: UUID,
    severity: str,
    subject: str,
    body: str,
    *,
    event_type: str = "all",
) -> None:
    """Send a notification through all enabled channels for a tenant."""
    channels = (
        (
            await session.execute(
                select(NotificationChannel).where(
                    NotificationChannel.tenant_id == tenant_id,
                    NotificationChannel.enabled.is_(True),
                )
            )
        )
        .scalars()
        .all()
    )

    eligible_channels = await _filter_channels_for_event(
        session,
        tenant_id=tenant_id,
        channels=channels,
        severity=severity,
        event_type=event_type,
    )
    push_subscriptions = await _list_push_subscriptions(session, tenant_id=tenant_id)

    _record_notification_log(
        session,
        tenant_id=tenant_id,
        channel_type="in_app",
        severity=severity,
        subject=subject,
        body=body,
        status=_in_app_delivery_status(
            eligible_channels=eligible_channels,
            push_subscriptions=push_subscriptions,
        ),
        event_type=event_type,
    )

    for channel in eligible_channels:
        try:
            if channel.channel_type == "discord":
                await _send_discord(channel.config, severity, subject, body)
            elif channel.channel_type == "slack":
                await _send_slack(channel.config, severity, subject, body)
            elif channel.channel_type == "email":
                await _send_email(channel.config, severity, subject, body)
            elif channel.channel_type == "sms":
                await _send_sms(channel.config, severity, subject, body)

            _record_notification_log(
                session,
                tenant_id=tenant_id,
                channel_type=channel.channel_type,
                severity=severity,
                subject=subject,
                body=body,
                status="sent",
                event_type=event_type,
            )
        except Exception as e:
            logger.exception("Failed to send %s notification for tenant %s", channel.channel_type, tenant_id)
            _record_notification_log(
                session,
                tenant_id=tenant_id,
                channel_type=channel.channel_type,
                severity=severity,
                subject=subject,
                body=body,
                status="failed",
                event_type=event_type,
                error=str(e),
            )

    # Send Web Push to all subscribed users
    await _send_web_push(session, push_subscriptions, severity, subject, body)

    await session.commit()


def _preference_allows_event(pref: NotificationPreference, *, severity: str, event_type: str) -> bool:
    severities = {item.strip() for item in pref.severity_filter.split(",") if item.strip()}
    events = {item.strip() for item in pref.event_types.split(",") if item.strip()}

    severity_matches = not severities or severity in severities
    event_matches = not events or "all" in events or event_type in events
    return severity_matches and event_matches


async def _filter_channels_for_event(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    channels: list[NotificationChannel],
    severity: str,
    event_type: str,
) -> list[NotificationChannel]:
    if not channels:
        return []

    prefs = (
        (
            await session.execute(
                select(NotificationPreference).where(
                    NotificationPreference.tenant_id == tenant_id,
                    NotificationPreference.enabled.is_(True),
                )
            )
        )
        .scalars()
        .all()
    )
    prefs_by_channel: dict[UUID, list[NotificationPreference]] = {}
    for pref in prefs:
        prefs_by_channel.setdefault(pref.channel_id, []).append(pref)

    eligible: list[NotificationChannel] = []
    for channel in channels:
        channel_prefs = prefs_by_channel.get(channel.id, [])
        if not channel_prefs:
            eligible.append(channel)
            continue
        if any(_preference_allows_event(pref, severity=severity, event_type=event_type) for pref in channel_prefs):
            eligible.append(channel)
    return eligible


async def _send_discord(config: dict, severity: str, subject: str, body: str) -> None:
    """Send notification via Discord webhook."""
    webhook_url = config.get("webhook_url")
    if not webhook_url:
        return

    color_map = {"critical": 0xFF0000, "warning": 0xFFA500, "info": 0x00FF00}
    payload = {
        "embeds": [
            {
                "title": f"{'🔴' if severity == 'critical' else '🟡' if severity == 'warning' else '🟢'} {subject}",
                "description": body,
                "color": color_map.get(severity, 0x808080),
                "footer": {"text": "Tendril Grow Assistant"},
            }
        ]
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(webhook_url, json=payload)
        resp.raise_for_status()


async def _send_slack(config: dict, severity: str, subject: str, body: str) -> None:
    """Send notification via Slack webhook."""
    webhook_url = config.get("webhook_url")
    if not webhook_url:
        return

    emoji = {"critical": ":red_circle:", "warning": ":warning:", "info": ":large_green_circle:"}
    payload = {
        "text": f"{emoji.get(severity, ':bell:')} *{subject}*\n{body}",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(webhook_url, json=payload)
        resp.raise_for_status()


async def _send_email(config: dict, severity: str, subject: str, body: str) -> None:
    """Send notification via email.

    Uses SMTP configuration from channel config.
    Falls back to logging if SMTP is not configured.
    """
    email_to = config.get("email")
    smtp_host = config.get("smtp_host")
    if not email_to:
        return

    if not smtp_host:
        logger.info("Email notification (no SMTP): to=%s subject=%s", email_to, subject)
        return

    import smtplib
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = f"[Tendril {severity.upper()}] {subject}"
    msg["From"] = config.get("smtp_from", "noreply@tendrilgrow.com")
    msg["To"] = email_to
    msg.set_content(body)

    smtp_port = config.get("smtp_port", 587)
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if config.get("smtp_tls", True):
            server.starttls()
        smtp_user = config.get("smtp_user")
        smtp_pass = config.get("smtp_pass")
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)


async def _send_sms(config: dict, severity: str, subject: str, body: str) -> None:
    """Send notification via SMS (Twilio).

    Requires twilio_sid, twilio_auth_token, twilio_from, phone in config.
    """
    phone = config.get("phone")
    twilio_sid = config.get("twilio_sid")
    twilio_token = config.get("twilio_auth_token")
    twilio_from = config.get("twilio_from")

    if not all([phone, twilio_sid, twilio_token, twilio_from]):
        logger.info("SMS notification (not configured): phone=%s subject=%s", phone, subject)
        return

    url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            url,
            data={"To": phone, "From": twilio_from, "Body": f"[{severity.upper()}] {subject}: {body[:140]}"},
            auth=(twilio_sid or "", twilio_token or ""),
        )
        resp.raise_for_status()


async def _send_web_push(
    session: AsyncSession,
    subscriptions: Sequence[PushSubscription],
    severity: str,
    subject: str,
    body: str,
) -> None:
    """Send Web Push notifications to all subscribed users for this tenant."""
    import os

    from pywebpush import WebPushException, webpush

    vapid_private = os.environ.get("VAPID_PRIVATE_KEY")
    vapid_email = os.environ.get("VAPID_EMAIL", "mailto:admin@tendrilgrow.com")

    if not vapid_private:
        return

    payload = json.dumps(
        {
            "title": f"[{severity.upper()}] {subject}",
            "body": body[:200],
            "icon": "/icons/icon-192x192.png",
            "badge": "/icons/icon-72x72.png",
        }
    )

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=payload,
                vapid_private_key=vapid_private,
                vapid_claims={"sub": vapid_email},
            )
        except WebPushException as e:
            logger.warning("Web push failed for subscription %s: %s", sub.id, e)
            if "410" in str(e) or "404" in str(e):
                await session.delete(sub)


async def _list_push_subscriptions(
    session: AsyncSession,
    *,
    tenant_id: UUID,
) -> list[PushSubscription]:
    return (
        (await session.execute(select(PushSubscription).where(PushSubscription.tenant_id == tenant_id))).scalars().all()
    )
