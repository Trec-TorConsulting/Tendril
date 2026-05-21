"""Transactional email service using Resend."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger("tendril.email")

_RESEND_URL = "https://api.resend.com/emails"


async def send_email(
    to: str,
    subject: str,
    html: str,
    *,
    reply_to: str | None = None,
    tags: list[dict[str, str]] | None = None,
) -> bool:
    """Send a transactional email via Resend.

    Returns True if sent successfully, False otherwise.
    """
    settings = get_settings()
    api_key = settings.resend_api_key

    if not api_key:
        logger.info("Email skipped (no RESEND_API_KEY): to=%s subject=%s", to, subject)
        return False

    payload: dict[str, Any] = {
        "from": settings.email_from,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if reply_to:
        payload["reply_to"] = reply_to
    if tags:
        payload["tags"] = tags

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                _RESEND_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            logger.info("Email sent: to=%s subject=%s", to, subject)
            return True
    except Exception:
        logger.exception("Failed to send email: to=%s subject=%s", to, subject)
        return False


# ─── Billing Email Templates ─────────────────────────────────────────────────

_BASE_STYLE = """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 560px; margin: 0 auto; padding: 32px 24px; color: #e5e5e5; background: #171717; border-radius: 12px;">
  <div style="margin-bottom: 24px;">
    <span style="font-size: 20px; font-weight: bold; color: #22c55e;">🌿 Tendril</span>
  </div>
  {content}
  <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #333; font-size: 12px; color: #737373;">
    <p>Tendril — Managed by Trec-Tor Consulting for Geek Info LLC</p>
    <p>New Jersey, USA · <a href="https://tendrilgrow.com" style="color: #22c55e;">tendrilgrow.com</a></p>
  </div>
</div>
"""


def _wrap(content: str) -> str:
    return _BASE_STYLE.format(content=content)


async def send_welcome_email(email: str, name: str) -> bool:
    """Send welcome email after registration."""
    html = _wrap(f"""
    <h2 style="color: #fff; margin-bottom: 8px;">Welcome to Tendril, {name}! 🌱</h2>
    <p>Your account is ready. Start tracking your grows with AI-powered insights, IoT sensors, and smart automation.</p>
    <div style="margin: 24px 0;">
      <a href="https://tendrilgrow.com/dashboard" style="display: inline-block; background: #22c55e; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">Go to Dashboard</a>
    </div>
    <p style="color: #a3a3a3;">You're on the <strong>Seedling (Free)</strong> plan. Upgrade anytime to unlock more grows, devices, and AI analyses.</p>
    """)
    return await send_email(email, "Welcome to Tendril 🌿", html, tags=[{"name": "category", "value": "welcome"}])


async def send_subscription_confirmed(email: str, plan_name: str, amount: str) -> bool:
    """Send subscription confirmation after successful checkout."""
    html = _wrap(f"""
    <h2 style="color: #fff; margin-bottom: 8px;">Subscription Confirmed ✅</h2>
    <p>You're now on the <strong style="color: #22c55e;">{plan_name}</strong> plan.</p>
    <div style="background: #262626; border-radius: 8px; padding: 16px; margin: 16px 0;">
      <p style="margin: 0;"><strong>Amount:</strong> {amount}/month</p>
      <p style="margin: 8px 0 0;"><strong>Plan:</strong> {plan_name}</p>
    </div>
    <p style="color: #a3a3a3;">Manage your subscription anytime from <a href="https://tendrilgrow.com/dashboard/billing" style="color: #22c55e;">Dashboard → Billing</a>.</p>
    """)
    return await send_email(
        email, f"Subscription Confirmed — {plan_name}", html, tags=[{"name": "category", "value": "billing"}]
    )


async def send_payment_failed(email: str, retry_date: str, grace_days: int) -> bool:
    """Send payment failure notification with retry info."""
    html = _wrap(f"""
    <h2 style="color: #fff; margin-bottom: 8px;">Payment Failed ⚠️</h2>
    <p>We were unable to process your subscription payment. Don't worry — we'll retry automatically.</p>
    <div style="background: #362a1a; border: 1px solid #854d0e; border-radius: 8px; padding: 16px; margin: 16px 0;">
      <p style="margin: 0; color: #fbbf24;"><strong>Next retry:</strong> {retry_date}</p>
      <p style="margin: 8px 0 0; color: #fbbf24;"><strong>Grace period:</strong> {grace_days} days remaining</p>
    </div>
    <p>To avoid interruption, please update your payment method:</p>
    <div style="margin: 16px 0;">
      <a href="https://tendrilgrow.com/dashboard/billing" style="display: inline-block; background: #22c55e; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">Update Payment Method</a>
    </div>
    <p style="color: #a3a3a3; font-size: 13px;">If payment isn't resolved within {grace_days} days, your account will be downgraded to the Free plan.</p>
    """)
    return await send_email(
        email, "Action Required: Payment Failed", html, tags=[{"name": "category", "value": "dunning"}]
    )


async def send_subscription_cancelled(email: str, end_date: str) -> bool:
    """Send cancellation confirmation."""
    html = _wrap(f"""
    <h2 style="color: #fff; margin-bottom: 8px;">Subscription Cancelled</h2>
    <p>Your subscription has been cancelled. You'll retain access to your current plan features until <strong>{end_date}</strong>.</p>
    <p>After that date, your account will revert to the <strong>Seedling (Free)</strong> plan. Your data will be preserved.</p>
    <div style="margin: 16px 0;">
      <a href="https://tendrilgrow.com/dashboard/billing" style="display: inline-block; border: 1px solid #525252; color: #e5e5e5; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">Resubscribe</a>
    </div>
    <p style="color: #a3a3a3; font-size: 13px;">We'd love to have you back. If you have feedback, reply to this email.</p>
    """)
    return await send_email(
        email,
        "Subscription Cancelled",
        html,
        reply_to="info@tendrilgrow.com",
        tags=[{"name": "category", "value": "billing"}],
    )


async def send_approaching_limit(email: str, metric: str, current: int, limit: int, plan: str) -> bool:
    """Send usage limit approaching notification (80% threshold)."""
    pct = int((current / limit) * 100)
    html = _wrap(f"""
    <h2 style="color: #fff; margin-bottom: 8px;">Approaching Usage Limit 📊</h2>
    <p>You've used <strong>{pct}%</strong> of your monthly <strong>{metric.replace("_", " ")}</strong> allowance.</p>
    <div style="background: #262626; border-radius: 8px; padding: 16px; margin: 16px 0;">
      <p style="margin: 0;"><strong>Used:</strong> {current} / {limit}</p>
      <p style="margin: 8px 0 0;"><strong>Plan:</strong> {plan}</p>
      <div style="background: #404040; border-radius: 4px; height: 8px; margin-top: 12px; overflow: hidden;">
        <div style="background: {"#f59e0b" if pct < 90 else "#ef4444"}; height: 100%; width: {pct}%; border-radius: 4px;"></div>
      </div>
    </div>
    <p>Upgrade your plan for higher limits:</p>
    <div style="margin: 16px 0;">
      <a href="https://tendrilgrow.com/dashboard/billing" style="display: inline-block; background: #22c55e; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">Upgrade Plan</a>
    </div>
    """)
    return await send_email(
        email,
        f"Usage Alert: {pct}% of {metric.replace('_', ' ')} used",
        html,
        tags=[{"name": "category", "value": "usage"}],
    )


async def send_payment_receipt(email: str, amount: str, date: str, invoice_url: str | None = None) -> bool:
    """Send payment receipt after successful charge."""
    invoice_link = f'<a href="{invoice_url}" style="color: #22c55e;">View Invoice</a>' if invoice_url else ""
    html = _wrap(f"""
    <h2 style="color: #fff; margin-bottom: 8px;">Payment Receipt 🧾</h2>
    <div style="background: #262626; border-radius: 8px; padding: 16px; margin: 16px 0;">
      <p style="margin: 0;"><strong>Amount:</strong> {amount}</p>
      <p style="margin: 8px 0 0;"><strong>Date:</strong> {date}</p>
      {f'<p style="margin: 8px 0 0;">{invoice_link}</p>' if invoice_link else ""}
    </div>
    <p style="color: #a3a3a3; font-size: 13px;">This is a receipt for your Tendril subscription payment. No action is needed.</p>
    """)
    return await send_email(email, f"Payment Receipt — {amount}", html, tags=[{"name": "category", "value": "receipt"}])


async def send_account_deletion_scheduled(email: str, deletion_date: str) -> bool:
    """Send confirmation that account deletion has been scheduled."""
    html = _wrap(f"""
    <h2 style="color: #fff; margin-bottom: 8px;">Account Deletion Scheduled</h2>
    <p>Your account and all associated data will be permanently deleted on <strong>{deletion_date}</strong>.</p>
    <p>If you change your mind, you can cancel the deletion by logging in before that date.</p>
    <div style="background: #362a1a; border: 1px solid #854d0e; border-radius: 8px; padding: 16px; margin: 16px 0;">
      <p style="margin: 0; color: #fbbf24;">⚠️ This action is irreversible after {deletion_date}.</p>
    </div>
    <div style="margin: 16px 0;">
      <a href="https://tendrilgrow.com/login" style="display: inline-block; border: 1px solid #525252; color: #e5e5e5; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">Cancel Deletion</a>
    </div>
    """)
    return await send_email(email, "Account Deletion Scheduled", html, tags=[{"name": "category", "value": "account"}])


async def send_retention_offer(email: str, discount: str, offer_code: str) -> bool:
    """Send retention discount offer during cancellation."""
    html = _wrap(f"""
    <h2 style="color: #fff; margin-bottom: 8px;">We'd Hate to See You Go 💚</h2>
    <p>Before you leave, we'd like to offer you <strong style="color: #22c55e;">{discount}</strong> as a thank you for being a Tendril grower.</p>
    <div style="background: #14532d; border: 1px solid #22c55e; border-radius: 8px; padding: 16px; margin: 16px 0; text-align: center;">
      <p style="margin: 0; font-size: 18px; color: #22c55e; font-weight: bold;">{discount}</p>
      <p style="margin: 4px 0 0; color: #a3a3a3; font-size: 13px;">Code: {offer_code}</p>
    </div>
    <div style="margin: 16px 0;">
      <a href="https://tendrilgrow.com/dashboard/billing" style="display: inline-block; background: #22c55e; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">Keep My Subscription</a>
    </div>
    <p style="color: #a3a3a3; font-size: 13px;">This offer expires in 48 hours. After that, your cancellation will proceed as scheduled.</p>
    """)
    return await send_email(
        email, "A Special Offer Just For You", html, tags=[{"name": "category", "value": "retention"}]
    )
