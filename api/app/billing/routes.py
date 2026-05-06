"""Billing — Checkout, Customer Portal, webhooks (multi-provider adapter)."""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.billing.models import BillingPlan, PaymentProvider
from app.billing.providers.base import get_provider_class
from app.billing.service import decrypt_provider_config, get_primary_provider
from app.config import get_settings
from app.database import async_session_factory
from app.tenants.models import Account, Tenant

router = APIRouter()
logger = logging.getLogger("tendril.billing")


# ---------- Schemas ----------


class CheckoutRequest(BaseModel):
    plan: str  # hobby, pro, commercial, enterprise


class BillingStatusResponse(BaseModel):
    plan: str
    plan_name: str
    billing_model: str | None
    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    portal_url: str | None
    supported_methods: list[str] | None


# ---------- Helpers ----------


async def _get_account_for_tenant(session: AsyncSession, tenant_id: UUID) -> Account | None:
    """Get the Account that owns the given tenant."""
    tenant = await session.get(Tenant, tenant_id)
    if not tenant or not tenant.account_id:
        return None
    return await session.get(Account, tenant.account_id)


# ---------- Billing Status ----------


@router.get("/status")
async def billing_status(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get the current tenant's billing status and plan details."""
    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    account = await _get_account_for_tenant(session, user.tenant_id)

    # Get plan display name from DB
    plan_row = (await session.execute(select(BillingPlan).where(BillingPlan.slug == tenant.plan))).scalar_one_or_none()
    plan_name = plan_row.name if plan_row else tenant.plan

    portal_url = None
    supported_methods = None

    # Try to get portal URL from primary provider
    provider_result = await get_primary_provider(session)
    if provider_result and account and account.stripe_customer_id:
        provider_row, adapter = provider_result
        supported_methods = provider_row.supported_methods
        try:
            settings = get_settings()
            result = await adapter.create_portal_session(
                customer_id=account.stripe_customer_id,
                return_url=f"https://{settings.domain}/dashboard/settings",
            )
            portal_url = result.url
        except Exception:
            logger.exception("Failed to create portal session")

    return BillingStatusResponse(
        plan=tenant.plan,
        plan_name=plan_name,
        billing_model=getattr(tenant, "billing_model", None),
        stripe_customer_id=account.stripe_customer_id if account else None,
        stripe_subscription_id=account.stripe_subscription_id if account else None,
        portal_url=portal_url,
        supported_methods=supported_methods,
    )


# ---------- Checkout ----------


@router.post("/checkout")
async def create_checkout(
    body: CheckoutRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a checkout session for plan upgrade via the primary payment provider."""
    # Validate plan exists
    plan_row = (
        await session.execute(select(BillingPlan).where(BillingPlan.slug == body.plan, BillingPlan.is_active.is_(True)))
    ).scalar_one_or_none()
    if not plan_row or body.plan == "free":
        raise HTTPException(status_code=400, detail="Invalid plan")

    # Get the primary provider adapter
    provider_result = await get_primary_provider(session)
    if not provider_result:
        raise HTTPException(status_code=503, detail="No payment provider configured")
    _provider_row, adapter = provider_result

    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    account = await _get_account_for_tenant(session, user.tenant_id)
    if not account:
        raise HTTPException(status_code=400, detail="No billing account")

    settings = get_settings()

    # Get or create customer on the provider
    if not account.stripe_customer_id:
        customer_result = await adapter.create_customer(
            email=user.email or "",
            metadata={"account_id": str(account.id), "tenant_id": str(tenant.id)},
        )
        account.stripe_customer_id = customer_result.customer_id
        await session.commit()

    # Create checkout session
    checkout_result = await adapter.create_checkout_session(
        customer_id=account.stripe_customer_id,
        plan_id=body.plan,
        success_url=f"https://{settings.domain}/dashboard/settings?billing=success",
        cancel_url=f"https://{settings.domain}/dashboard/settings?billing=cancelled",
        metadata={"tenant_id": str(tenant.id), "plan": body.plan},
    )

    return {"checkout_url": checkout_result.url}


# ---------- Customer Portal ----------


@router.post("/portal")
async def create_portal(
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a customer portal session for billing management."""
    account = await _get_account_for_tenant(session, user.tenant_id)
    if not account or not account.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account")

    provider_result = await get_primary_provider(session)
    if not provider_result:
        raise HTTPException(status_code=503, detail="No payment provider configured")
    _, adapter = provider_result

    settings = get_settings()
    result = await adapter.create_portal_session(
        customer_id=account.stripe_customer_id,
        return_url=f"https://{settings.domain}/dashboard/settings",
    )
    return {"portal_url": result.url}


# ---------- Webhook ----------


@router.post("/webhook/{provider_type}")
async def payment_webhook(
    provider_type: str,
    request: Request,
):
    """Handle payment provider webhook events (route by provider type)."""
    body = await request.body()
    headers = dict(request.headers)

    # Extract provider-specific signature header
    signature_map = {
        "stripe": "stripe-signature",
        "paypal": "paypal-transmission-sig",
        "square": "x-square-hmacsha256-signature",
        "paddle": "paddle-signature",
    }
    sig_header = signature_map.get(provider_type, "")
    signature = headers.get(sig_header, "")

    async with async_session_factory() as session:
        # Find the provider by type
        provider_row = (
            await session.execute(
                select(PaymentProvider).where(
                    PaymentProvider.provider_type == provider_type,
                    PaymentProvider.is_active.is_(True),
                )
            )
        ).scalar_one_or_none()

        if not provider_row:
            raise HTTPException(status_code=404, detail="Provider not found")

        config = decrypt_provider_config(provider_row.config_encrypted)
        provider_cls = get_provider_class(provider_type)
        if not provider_cls:
            raise HTTPException(status_code=500, detail="No adapter for provider")

        adapter = provider_cls(config)

        # Get webhook secret
        webhook_secret = None
        if provider_row.webhook_secret_encrypted:
            ws_data = decrypt_provider_config(provider_row.webhook_secret_encrypted)
            webhook_secret = ws_data.get("secret")

        # Verify and parse webhook
        event = await adapter.verify_webhook(body, signature, webhook_secret or "")
        if not event:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        # Dispatch event
        await _dispatch_webhook_event(session, event)

    return {"status": "ok"}


# Legacy Stripe-specific webhook endpoint (backward-compat)
@router.post("/webhook")
async def stripe_webhook_legacy(request: Request):
    """Legacy Stripe webhook endpoint — redirects to provider-specific handler."""
    # Check if Stripe-Signature header is present
    if "stripe-signature" in request.headers:
        request.scope["path_params"] = {"provider_type": "stripe"}
        return await payment_webhook("stripe", request)
    raise HTTPException(status_code=400, detail="Missing provider signature header")


async def _dispatch_webhook_event(session: AsyncSession, event) -> None:
    """Route a parsed webhook event to the correct handler."""
    event_type = event.event_type

    if event_type == "checkout.completed":
        await _handle_checkout_completed(session, event.data)
    elif event_type == "subscription.updated":
        await _handle_subscription_updated(session, event.data)
    elif event_type == "subscription.cancelled":
        await _handle_subscription_deleted(session, event.data)
    elif event_type == "payment.failed":
        customer_id = event.data.get("customer")
        logger.warning("Payment failed for customer %s", customer_id)
        # Trigger dunning flow
        account = (
            await session.execute(select(Account).where(Account.stripe_customer_id == customer_id))
        ).scalar_one_or_none()
        if account:
            from app.billing.dunning import handle_payment_failed

            await handle_payment_failed(session, account.id)
    elif event_type == "invoice.paid":
        # Clear dunning on successful payment
        customer_id = event.data.get("customer")
        if customer_id:
            account = (
                await session.execute(select(Account).where(Account.stripe_customer_id == customer_id))
            ).scalar_one_or_none()
            if account:
                from app.billing.dunning import clear_dunning

                await clear_dunning(session, account.id)
                # Send receipt email
                from app.billing.dunning import _get_account_owner_email
                from app.billing.email_service import send_payment_receipt

                owner_email = await _get_account_owner_email(session, account.id)
                if owner_email:
                    amount = event.data.get("amount_paid", 0)
                    invoice_url = event.data.get("hosted_invoice_url")
                    await send_payment_receipt(
                        email=owner_email,
                        amount=f"${amount / 100:.2f}" if isinstance(amount, int | float) else str(amount),
                        date=event.data.get("date", ""),
                        invoice_url=invoice_url,
                    )
    else:
        logger.info("Unhandled webhook event: %s", event_type)


async def _handle_checkout_completed(session: AsyncSession, data: dict) -> None:
    # Stripe nests custom data in metadata; other providers may put it at top level
    metadata = data.get("metadata", {})
    tenant_id = metadata.get("tenant_id") or data.get("tenant_id")
    plan = metadata.get("plan") or data.get("plan")
    subscription_id = data.get("subscription") or data.get("subscription_id")

    if not tenant_id:
        logger.warning("Checkout completed without tenant_id metadata")
        return

    tenant = await session.get(Tenant, UUID(tenant_id))
    if not tenant:
        return

    tenant.plan = plan or tenant.plan

    # Store subscription on account
    if tenant.account_id:
        account = await session.get(Account, tenant.account_id)
        if account and subscription_id:
            account.stripe_subscription_id = subscription_id

    await session.commit()
    logger.info("Tenant %s upgraded to plan %s", tenant_id, plan)


async def _handle_subscription_updated(session: AsyncSession, data: dict) -> None:
    customer_id = data.get("customer")
    if not customer_id:
        return

    account = (
        await session.execute(select(Account).where(Account.stripe_customer_id == customer_id))
    ).scalar_one_or_none()
    if not account:
        return

    tenant = (
        await session.execute(select(Tenant).where(Tenant.account_id == account.id).limit(1))
    ).scalar_one_or_none()

    # Extract plan from Stripe subscription object: check metadata, then items lookup_key
    metadata = data.get("metadata", {})
    plan = metadata.get("plan")
    if not plan:
        # Try to extract from the first subscription item's price lookup_key
        items = data.get("items", {}).get("data", [])
        if items:
            price = items[0].get("price", {})
            plan = price.get("lookup_key") or price.get("metadata", {}).get("plan")

    if plan and tenant:
        tenant.plan = plan

    subscription_id = data.get("subscription_id")
    if subscription_id:
        account.stripe_subscription_id = subscription_id

    await session.commit()
    logger.info("Subscription updated for account %s", account.id)


async def _handle_subscription_deleted(session: AsyncSession, data: dict) -> None:
    customer_id = data.get("customer")
    if not customer_id:
        return

    account = (
        await session.execute(select(Account).where(Account.stripe_customer_id == customer_id))
    ).scalar_one_or_none()
    if not account:
        return

    # Revert all tenants in this account to free
    tenants = (await session.execute(select(Tenant).where(Tenant.account_id == account.id))).scalars().all()
    for tenant in tenants:
        tenant.plan = "free"

    account.stripe_subscription_id = None
    await session.commit()
    logger.info("Subscription cancelled for account %s, reverted to free", account.id)


# ---------- Usage Alerts ----------


class UsageAlertItem(BaseModel):
    metric: str
    current: int
    limit: int
    plan: str


class UsageAlertsResponse(BaseModel):
    alerts: list[UsageAlertItem]


@router.get("/usage-alerts", response_model=UsageAlertsResponse)
async def get_usage_alerts(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get usage alerts for metrics approaching their plan limits (80%+ threshold)."""
    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant:
        return UsageAlertsResponse(alerts=[])

    plan = (
        await session.execute(
            select(BillingPlan).where(BillingPlan.slug == tenant.plan, BillingPlan.is_active.is_(True))
        )
    ).scalar_one_or_none()

    if not plan:
        return UsageAlertsResponse(alerts=[])

    from app.billing.metering import get_usage_summary

    usage = await get_usage_summary(session, user.tenant_id)

    limit_map = {
        "grows": plan.max_grows,
        "devices": plan.max_devices,
        "team_members": plan.max_team_members,
        "ai_analyses": plan.max_ai_analyses_month,
        "storage_gb": plan.max_storage_gb,
        "automations": plan.max_automations,
        "integrations": plan.max_integrations,
        "journal_entries": plan.max_journal_entries_month,
    }

    alerts = []
    for metric, limit in limit_map.items():
        if limit is None:
            continue  # Unlimited
        current = usage.get(metric, 0)
        if current >= limit * 0.8:  # 80% threshold
            alerts.append(
                UsageAlertItem(
                    metric=metric,
                    current=current,
                    limit=limit,
                    plan=tenant.plan,
                )
            )

    # Send email notification if at 80% (idempotent, only once per period)
    if alerts:
        from app.billing.dunning import _get_account_owner_email
        from app.billing.email_service import send_approaching_limit

        if tenant.account_id:
            account = await session.get(Account, tenant.account_id)
            if account:
                owner_email = await _get_account_owner_email(session, account.id)
                if owner_email:
                    # Only send for the most critical alert
                    top_alert = max(alerts, key=lambda a: a.current / a.limit)
                    if top_alert.current >= top_alert.limit * 0.9:  # Only email at 90%+
                        await send_approaching_limit(
                            email=owner_email,
                            metric=top_alert.metric,
                            current=top_alert.current,
                            limit=top_alert.limit,
                            plan=tenant.plan,
                        )

    return UsageAlertsResponse(alerts=alerts)
