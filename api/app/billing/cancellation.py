"""Cancellation flow with retention offer and exit survey."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_tenant_session, require_role
from app.billing.email_service import send_retention_offer, send_subscription_cancelled
from app.billing.service import get_primary_provider
from app.tenants.models import Account, Tenant

router = APIRouter()
logger = logging.getLogger("tendril.billing.cancellation")


# ─── Schemas ──────────────────────────────────────────────────────────────────


class CancelRequest(BaseModel):
    reason: str | None = None  # too_expensive, not_using, missing_features, switching, other
    feedback: str | None = None
    accept_retention_offer: bool = False


class CancelResponse(BaseModel):
    status: str  # retention_offered | cancelled | already_free
    retention_offer: RetentionOffer | None = None
    cancellation_date: str | None = None


class RetentionOffer(BaseModel):
    discount: str  # "20% off for 3 months"
    offer_code: str
    expires_at: str


class ExitSurveyEntry(BaseModel):
    reason: str
    feedback: str | None = None


# ─── Routes ───────────────────────────────────────────────────────────────────


@router.post("/cancel", response_model=CancelResponse)
async def initiate_cancellation(
    body: CancelRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Initiate subscription cancellation with optional retention offer.

    First call: Returns a retention offer (20% off for 3 months).
    Second call with accept_retention_offer=False: Proceeds with cancellation.
    """
    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if tenant.plan == "free":
        return CancelResponse(status="already_free")

    account = None
    if tenant.account_id:
        account = await session.get(Account, tenant.account_id)

    # If user hasn't seen the retention offer yet (first cancellation attempt)
    if not body.accept_retention_offer and body.reason != "__confirmed_cancel__":
        offer_code = f"STAY-{uuid.uuid4().hex[:8].upper()}"
        offer_expires = datetime.now(UTC) + timedelta(hours=48)

        # Store exit survey
        if body.reason:
            logger.info(
                "Exit survey: tenant=%s reason=%s feedback=%s",
                user.tenant_id,
                body.reason,
                body.feedback,
            )

        # Send retention email
        if account:
            from app.billing.dunning import _get_account_owner_email

            owner_email = await _get_account_owner_email(session, account.id)
            if owner_email:
                await send_retention_offer(
                    email=owner_email,
                    discount="20% off for 3 months",
                    offer_code=offer_code,
                )

        return CancelResponse(
            status="retention_offered",
            retention_offer=RetentionOffer(
                discount="20% off for 3 months",
                offer_code=offer_code,
                expires_at=offer_expires.isoformat(),
            ),
        )

    # User declined the offer — proceed with cancellation
    provider_result = await get_primary_provider(session)

    if provider_result and account and account.stripe_subscription_id:
        _, adapter = provider_result
        try:
            result = await adapter.cancel_subscription(account.stripe_subscription_id, at_period_end=True)
            cancellation_date = result.current_period_end or datetime.now(UTC).isoformat()
        except Exception as exc:
            logger.exception("Failed to cancel subscription via provider")
            raise HTTPException(status_code=502, detail="Failed to cancel subscription with payment provider") from exc
    else:
        # No active subscription — just downgrade directly
        tenant.plan = "free"
        await session.commit()
        cancellation_date = datetime.now(UTC).isoformat()

    # Send cancellation email
    if account:
        from app.billing.dunning import _get_account_owner_email

        owner_email = await _get_account_owner_email(session, account.id)
        if owner_email:
            await send_subscription_cancelled(email=owner_email, end_date=cancellation_date[:10])

    logger.info("Subscription cancelled for tenant %s (reason: %s)", user.tenant_id, body.reason)

    return CancelResponse(
        status="cancelled",
        cancellation_date=cancellation_date,
    )
