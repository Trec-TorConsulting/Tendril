"""Notification dispatch — send alerts via configured channels."""

from __future__ import annotations

import json
import logging
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.models import (
    NotificationChannel,
    NotificationLog,
    PushSubscription,
)

logger = logging.getLogger("tendril.notifications")


async def dispatch_alert(
    session: AsyncSession,
    tenant_id: UUID,
    severity: str,
    subject: str,
    body: str,
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

    for channel in channels:
        try:
            if channel.channel_type == "discord":
                await _send_discord(channel.config, severity, subject, body)
            elif channel.channel_type == "slack":
                await _send_slack(channel.config, severity, subject, body)
            elif channel.channel_type == "email":
                await _send_email(channel.config, severity, subject, body)
            elif channel.channel_type == "sms":
                await _send_sms(channel.config, severity, subject, body)

            session.add(
                NotificationLog(
                    tenant_id=tenant_id,
                    channel_type=channel.channel_type,
                    severity=severity,
                    subject=subject,
                    body=body,
                    status="sent",
                )
            )
        except Exception as e:
            logger.exception("Failed to send %s notification for tenant %s", channel.channel_type, tenant_id)
            session.add(
                NotificationLog(
                    tenant_id=tenant_id,
                    channel_type=channel.channel_type,
                    severity=severity,
                    subject=subject,
                    body=body,
                    status="failed",
                    error=str(e),
                )
            )

    # Send Web Push to all subscribed users
    await _send_web_push(session, tenant_id, severity, subject, body)

    await session.commit()


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
    tenant_id: UUID,
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

    subs = (
        (await session.execute(select(PushSubscription).where(PushSubscription.tenant_id == tenant_id))).scalars().all()
    )

    payload = json.dumps(
        {
            "title": f"[{severity.upper()}] {subject}",
            "body": body[:200],
            "icon": "/icons/icon-192x192.png",
            "badge": "/icons/icon-72x72.png",
        }
    )

    for sub in subs:
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
