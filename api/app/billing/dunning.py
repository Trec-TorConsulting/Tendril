"""Dunning management — grace period handling for failed payments."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.email_service import send_payment_failed, send_subscription_cancelled
from app.config import get_settings
from app.database import async_session_factory
from app.tenants.models import Account, Tenant, User

logger = logging.getLogger("tendril.billing.dunning")


async def handle_payment_failed(session: AsyncSession, account_id: UUID) -> None:
    """Handle a failed payment: set grace period, notify user.

    Called from webhook handler when a payment attempt fails.
    Grace period: 14 days (configurable via DUNNING_GRACE_DAYS).
    Retry schedule: days 1, 3, 7, 14.
    """
    settings = get_settings()
    grace_days = settings.dunning_grace_days

    account = await session.get(Account, account_id)
    if not account:
        return

    # Set grace period start if not already in dunning
    if not account.dunning_started_at:
        account.dunning_started_at = datetime.now(UTC)
        account.dunning_attempts = 1
    else:
        account.dunning_attempts = (account.dunning_attempts or 0) + 1

    grace_end = account.dunning_started_at + timedelta(days=grace_days)
    days_remaining = max(0, (grace_end - datetime.now(UTC)).days)

    # Determine next retry date (1, 3, 7, 14 day schedule)
    retry_schedule = [1, 3, 7, 14]
    attempts = account.dunning_attempts or 1
    next_retry_offset = retry_schedule[min(attempts, len(retry_schedule) - 1)]
    next_retry_date = datetime.now(UTC) + timedelta(days=next_retry_offset)

    await session.commit()

    # Get the account owner email
    owner = await _get_account_owner_email(session, account_id)
    if owner:
        await send_payment_failed(
            email=owner,
            retry_date=next_retry_date.strftime("%B %d, %Y"),
            grace_days=days_remaining,
        )

    logger.warning(
        "Payment failed for account %s (attempt %d, %d days remaining)",
        account_id,
        attempts,
        days_remaining,
    )


async def handle_grace_period_expired(session: AsyncSession, account_id: UUID) -> None:
    """Downgrade account to free after grace period expires.

    Called by the scheduler when dunning_started_at + grace_days < now.
    """
    account = await session.get(Account, account_id)
    if not account:
        return

    # Downgrade all tenants to free
    tenants = (await session.execute(select(Tenant).where(Tenant.account_id == account_id))).scalars().all()

    for tenant in tenants:
        tenant.plan = "free"

    # Clear subscription and dunning state
    account.stripe_subscription_id = None
    account.dunning_started_at = None
    account.dunning_attempts = None

    await session.commit()

    # Notify owner
    owner = await _get_account_owner_email(session, account_id)
    if owner:
        await send_subscription_cancelled(
            email=owner,
            end_date=datetime.now(UTC).strftime("%B %d, %Y"),
        )

    logger.info("Grace period expired for account %s — downgraded to free", account_id)


async def clear_dunning(session: AsyncSession, account_id: UUID) -> None:
    """Clear dunning state after a successful payment."""
    account = await session.get(Account, account_id)
    if not account:
        return

    if account.dunning_started_at:
        account.dunning_started_at = None
        account.dunning_attempts = None
        await session.commit()
        logger.info("Dunning cleared for account %s — payment successful", account_id)


async def check_expired_grace_periods() -> None:
    """Scheduled job: find accounts past grace period and downgrade them.

    Should be called periodically (every hour) by the scheduler.
    """
    settings = get_settings()
    grace_days = settings.dunning_grace_days
    cutoff = datetime.now(UTC) - timedelta(days=grace_days)

    async with async_session_factory() as session:
        expired_accounts = (
            (
                await session.execute(
                    select(Account).where(
                        Account.dunning_started_at.isnot(None),
                        Account.dunning_started_at < cutoff,
                    )
                )
            )
            .scalars()
            .all()
        )

        for account in expired_accounts:
            await handle_grace_period_expired(session, account.id)


async def _get_account_owner_email(session: AsyncSession, account_id: UUID) -> str | None:
    """Get the email of the account owner."""
    # Look up the first user associated with this account via tenant membership
    from app.tenants.models import TenantMembership

    result = await session.execute(
        select(User.email)
        .join(TenantMembership, TenantMembership.user_id == User.id)
        .join(Tenant, Tenant.id == TenantMembership.tenant_id)
        .where(Tenant.account_id == account_id, TenantMembership.role == "admin")
        .limit(1)
    )
    row = result.scalar_one_or_none()
    return row
