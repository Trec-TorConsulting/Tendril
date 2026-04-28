"""Stripe billing — Checkout, Customer Portal, webhooks."""
from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

import stripe
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.config import get_settings
from app.database import async_session_factory
from app.tenants.models import Tenant

router = APIRouter()
logger = logging.getLogger("tendril.billing")

# Pricing tiers → Stripe Price IDs (set via env)
import os
PRICE_IDS = {
    "grower": os.environ.get("STRIPE_PRICE_GROWER", ""),
    "pro": os.environ.get("STRIPE_PRICE_PRO", ""),
    "commercial": os.environ.get("STRIPE_PRICE_COMMERCIAL", ""),
}

PLAN_NAMES = {
    "free": "Seedling (Free)",
    "grower": "Grower ($14.99/mo)",
    "pro": "Pro ($29.99/mo)",
    "commercial": "Commercial ($79.99/mo)",
}


# ---------- Schemas ----------

class CheckoutRequest(BaseModel):
    plan: str  # grower, pro, commercial

class BillingStatusResponse(BaseModel):
    plan: str
    plan_name: str
    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    portal_url: str | None


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

    portal_url = None
    if tenant.stripe_customer_id:
        settings = get_settings()
        stripe.api_key = settings.stripe_secret_key
        try:
            portal = stripe.billing_portal.Session.create(
                customer=tenant.stripe_customer_id,
                return_url=f"https://{settings.domain}/dashboard/settings",
            )
            portal_url = portal.url
        except Exception:
            logger.exception("Failed to create portal session")

    return BillingStatusResponse(
        plan=tenant.plan,
        plan_name=PLAN_NAMES.get(tenant.plan, tenant.plan),
        stripe_customer_id=tenant.stripe_customer_id,
        stripe_subscription_id=tenant.stripe_subscription_id,
        portal_url=portal_url,
    )


# ---------- Checkout ----------

@router.post("/checkout")
async def create_checkout(
    body: CheckoutRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a Stripe checkout session for plan upgrade."""
    if body.plan not in PRICE_IDS or not PRICE_IDS[body.plan]:
        raise HTTPException(status_code=400, detail="Invalid plan")

    settings = get_settings()
    stripe.api_key = settings.stripe_secret_key

    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get or create Stripe customer
    if not tenant.stripe_customer_id:
        customer = stripe.Customer.create(
            metadata={"tenant_id": str(tenant.id)},
        )
        tenant.stripe_customer_id = customer.id
        await session.commit()

    checkout = stripe.checkout.Session.create(
        customer=tenant.stripe_customer_id,
        mode="subscription",
        line_items=[{"price": PRICE_IDS[body.plan], "quantity": 1}],
        success_url=f"https://{settings.domain}/dashboard/settings?billing=success",
        cancel_url=f"https://{settings.domain}/dashboard/settings?billing=cancelled",
        metadata={"tenant_id": str(tenant.id), "plan": body.plan},
    )

    return {"checkout_url": checkout.url}


# ---------- Customer Portal ----------

@router.post("/portal")
async def create_portal(
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a Stripe customer portal session for billing management."""
    settings = get_settings()
    stripe.api_key = settings.stripe_secret_key

    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant or not tenant.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account")

    portal = stripe.billing_portal.Session.create(
        customer=tenant.stripe_customer_id,
        return_url=f"https://{settings.domain}/dashboard/settings",
    )
    return {"portal_url": portal.url}


# ---------- Webhook ----------

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Annotated[str | None, Header(alias="Stripe-Signature")] = None,
):
    """Handle Stripe webhook events."""
    settings = get_settings()
    stripe.api_key = settings.stripe_secret_key

    body = await request.body()

    if not stripe_signature or not settings.stripe_webhook_secret:
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        event = stripe.Webhook.construct_event(
            body, stripe_signature, settings.stripe_webhook_secret,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    data = event["data"]["object"]

    async with async_session_factory() as session:
        if event_type == "checkout.session.completed":
            await _handle_checkout_completed(session, data)
        elif event_type == "customer.subscription.updated":
            await _handle_subscription_updated(session, data)
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(session, data)
        elif event_type == "invoice.payment_failed":
            await _handle_payment_failed(session, data)
        else:
            logger.info("Unhandled Stripe event: %s", event_type)

    return {"status": "ok"}


async def _handle_checkout_completed(session: AsyncSession, data: dict) -> None:
    tenant_id = data.get("metadata", {}).get("tenant_id")
    plan = data.get("metadata", {}).get("plan")
    subscription_id = data.get("subscription")

    if not tenant_id:
        logger.warning("Checkout completed without tenant_id metadata")
        return

    tenant = await session.get(Tenant, UUID(tenant_id))
    if not tenant:
        return

    tenant.plan = plan or tenant.plan
    tenant.stripe_subscription_id = subscription_id
    await session.commit()
    logger.info("Tenant %s upgraded to plan %s", tenant_id, plan)


async def _handle_subscription_updated(session: AsyncSession, data: dict) -> None:
    customer_id = data.get("customer")
    if not customer_id:
        return

    tenant = (await session.execute(
        select(Tenant).where(Tenant.stripe_customer_id == customer_id)
    )).scalar_one_or_none()
    if not tenant:
        return

    # Map Stripe price ID back to plan name
    items = data.get("items", {}).get("data", [])
    if items:
        price_id = items[0].get("price", {}).get("id")
        for plan, pid in PRICE_IDS.items():
            if pid == price_id:
                tenant.plan = plan
                break

    tenant.stripe_subscription_id = data.get("id")
    await session.commit()
    logger.info("Subscription updated for tenant %s", tenant.id)


async def _handle_subscription_deleted(session: AsyncSession, data: dict) -> None:
    customer_id = data.get("customer")
    if not customer_id:
        return

    tenant = (await session.execute(
        select(Tenant).where(Tenant.stripe_customer_id == customer_id)
    )).scalar_one_or_none()
    if not tenant:
        return

    tenant.plan = "free"
    tenant.stripe_subscription_id = None
    await session.commit()
    logger.info("Subscription cancelled for tenant %s, reverted to free", tenant.id)


async def _handle_payment_failed(session: AsyncSession, data: dict) -> None:
    customer_id = data.get("customer")
    logger.warning("Payment failed for customer %s", customer_id)
    # Could add notification dispatch here
