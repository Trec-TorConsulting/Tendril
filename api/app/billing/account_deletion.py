"""Account deletion (GDPR compliance) — schedule or cancel account deletion."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_tenant_session, require_role
from app.billing.email_service import send_account_deletion_scheduled
from app.config import get_settings
from app.database import async_session_factory
from app.tenants.models import Account, Tenant, TenantMembership, User

router = APIRouter()
logger = logging.getLogger("tendril.account.deletion")


class DeletionRequest(BaseModel):
    confirm_email: str  # Must match account owner email for safety


class DeletionResponse(BaseModel):
    status: str  # scheduled | cancelled
    deletion_date: str | None = None
    message: str


class DeletionStatusResponse(BaseModel):
    deletion_scheduled: bool
    deletion_date: str | None = None
    days_remaining: int | None = None


@router.post("/delete", response_model=DeletionResponse)
async def request_account_deletion(
    body: DeletionRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Schedule account deletion. Data retained for 30 days then permanently purged.

    Requires the account owner's email as confirmation.
    User can cancel by calling DELETE /account/delete before the retention period expires.
    """
    settings = get_settings()

    # Verify email matches current user
    user_record = await session.get(User, user.user_id)
    if not user_record or user_record.email != body.confirm_email:
        raise HTTPException(status_code=400, detail="Email does not match account owner")

    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    account = None
    if tenant.account_id:
        account = await session.get(Account, tenant.account_id)

    deletion_date = datetime.now(UTC) + timedelta(days=settings.data_retention_days)

    # Mark account for deletion
    if account:
        account.deletion_scheduled_at = datetime.now(UTC)
        account.deletion_date = deletion_date
    else:
        # No account — mark tenant directly
        tenant.deletion_scheduled_at = datetime.now(UTC)
        tenant.deletion_date = deletion_date

    await session.commit()

    # Send confirmation email
    await send_account_deletion_scheduled(
        email=user_record.email,
        deletion_date=deletion_date.strftime("%B %d, %Y"),
    )

    logger.info(
        "Account deletion scheduled for user %s (tenant %s), date: %s", user.user_id, user.tenant_id, deletion_date
    )

    return DeletionResponse(
        status="scheduled",
        deletion_date=deletion_date.isoformat(),
        message=(
            f"Your account and all data will be permanently deleted on"
            f" {deletion_date.strftime('%B %d, %Y')}. Log in before then to cancel."
        ),
    )


@router.delete("/delete", response_model=DeletionResponse)
async def cancel_account_deletion(
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Cancel a pending account deletion."""
    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    account = None
    if tenant.account_id:
        account = await session.get(Account, tenant.account_id)

    if account:
        if not account.deletion_scheduled_at:
            raise HTTPException(status_code=400, detail="No deletion scheduled")
        account.deletion_scheduled_at = None
        account.deletion_date = None
    else:
        if not getattr(tenant, "deletion_scheduled_at", None):
            raise HTTPException(status_code=400, detail="No deletion scheduled")
        tenant.deletion_scheduled_at = None
        tenant.deletion_date = None

    await session.commit()
    logger.info("Account deletion cancelled for user %s", user.user_id)

    return DeletionResponse(
        status="cancelled",
        message="Account deletion has been cancelled. Your data is safe.",
    )


@router.get("/delete/status", response_model=DeletionStatusResponse)
async def get_deletion_status(
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Check if account deletion is pending."""
    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    deletion_date = None
    if tenant.account_id:
        account = await session.get(Account, tenant.account_id)
        if account and account.deletion_scheduled_at:
            deletion_date = account.deletion_date
    elif getattr(tenant, "deletion_scheduled_at", None):
        deletion_date = tenant.deletion_date

    if deletion_date:
        days_remaining = max(0, (deletion_date - datetime.now(UTC)).days)
        return DeletionStatusResponse(
            deletion_scheduled=True,
            deletion_date=deletion_date.isoformat(),
            days_remaining=days_remaining,
        )

    return DeletionStatusResponse(deletion_scheduled=False)


async def purge_expired_accounts() -> None:
    """Scheduled job: permanently delete accounts past their retention date.

    Should run daily via the scheduler.
    """
    async with async_session_factory() as session:
        now = datetime.now(UTC)

        # Find accounts past deletion date
        expired_accounts = (
            (
                await session.execute(
                    select(Account).where(
                        Account.deletion_date.isnot(None),
                        Account.deletion_date <= now,
                    )
                )
            )
            .scalars()
            .all()
        )

        for account in expired_accounts:
            logger.info("Purging account %s (deletion date: %s)", account.id, account.deletion_date)

            # Delete all tenants under this account (cascades to all data via FK)
            tenants = (await session.execute(select(Tenant).where(Tenant.account_id == account.id))).scalars().all()

            for tenant in tenants:
                # Delete tenant members
                await session.execute(delete(TenantMembership).where(TenantMembership.tenant_id == tenant.id))
                await session.delete(tenant)

            await session.delete(account)

        if expired_accounts:
            await session.commit()
            logger.info("Purged %d expired accounts", len(expired_accounts))


async def export_user_data(session: AsyncSession, user_id, tenant_id) -> dict:
    """Export all user data (GDPR data portability). Returns a dict suitable for JSON."""
    from app.grows.expense_models import Expense
    from app.grows.models import GrowCycle

    user = await session.get(User, user_id)
    tenant = await session.get(Tenant, tenant_id)

    if user is None:
        raise ValueError(f"User {user_id} not found")
    if tenant is None:
        raise ValueError(f"Tenant {tenant_id} not found")

    grows = (await session.execute(select(GrowCycle).where(GrowCycle.tenant_id == tenant_id))).scalars().all()

    expenses = (await session.execute(select(Expense).where(Expense.tenant_id == tenant_id))).scalars().all()

    return {
        "exported_at": datetime.now(UTC).isoformat(),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "display_name": getattr(user, "display_name", None),
            "created_at": str(user.created_at) if hasattr(user, "created_at") else None,
        },
        "tenant": {
            "id": str(tenant.id),
            "name": tenant.name,
            "plan": tenant.plan,
        },
        "grows": [
            {
                "id": str(g.id),
                "name": g.name,
                "grow_type": g.grow_type,
                "status": g.status,
                "started_at": str(g.started_at),
            }
            for g in grows
        ],
        "expenses": [
            {
                "id": str(e.id),
                "category": e.category,
                "amount_cents": e.amount_cents,
                "date": str(e.date),
                "description": e.description,
            }
            for e in expenses
        ],
    }
