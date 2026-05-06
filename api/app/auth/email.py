"""Transactional email service — sends auth emails via Resend API."""

from __future__ import annotations

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger("tendril.email")

_RESEND_URL = "https://api.resend.com/emails"


async def send_email(to: str, subject: str, html: str) -> bool:
    """Send a transactional email via Resend. Returns True on success."""
    settings = get_settings()
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not configured — email to %s suppressed", to)
        return False

    payload = {
        "from": settings.email_from,
        "to": [to],
        "subject": subject,
        "html": html,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                _RESEND_URL,
                json=payload,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            )
        if resp.status_code >= 400:
            logger.error("Resend API error %d: %s", resp.status_code, resp.text)
            return False
        return True
    except httpx.HTTPError:
        logger.exception("Failed to send email to %s", to)
        return False


async def send_verification_email(to: str, token: str) -> bool:
    """Send email verification link."""
    settings = get_settings()
    verify_url = f"https://{settings.domain}/verify-email?token={token}"
    html = f"""\
<h2>Verify your email</h2>
<p>Click the link below to verify your email address for {settings.app_name}:</p>
<p><a href="{verify_url}"
 style="display:inline-block;padding:12px 24px;background:#16a34a;
 color:#fff;border-radius:6px;text-decoration:none;font-weight:600;"
>Verify Email</a></p>
<p style="color:#666;font-size:13px;">Or copy this link: {verify_url}</p>
<p style="color:#666;font-size:13px;">This link expires in 24 hours.</p>
"""
    return await send_email(to, f"Verify your {settings.app_name} email", html)


async def send_password_reset_email(to: str, token: str) -> bool:
    """Send password reset link."""
    settings = get_settings()
    reset_url = f"https://{settings.domain}/reset-password?token={token}"
    html = f"""\
<h2>Reset your password</h2>
<p>Someone requested a password reset for your {settings.app_name} account.</p>
<p><a href="{reset_url}"
 style="display:inline-block;padding:12px 24px;background:#16a34a;
 color:#fff;border-radius:6px;text-decoration:none;font-weight:600;"
>Reset Password</a></p>
<p style="color:#666;font-size:13px;">Or copy this link: {reset_url}</p>
<p style="color:#666;font-size:13px;">This link expires in 1 hour.
 If you didn't request this, ignore this email.</p>
"""
    return await send_email(to, f"Reset your {settings.app_name} password", html)
