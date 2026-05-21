"""Stripe payment provider adapter."""

from __future__ import annotations

import asyncio
import functools
from typing import Any

import stripe

from app.billing.providers.base import (
    BasePaymentProvider,
    CheckoutResult,
    CustomerResult,
    PaymentMethodInfo,
    PlanSyncResult,
    PortalResult,
    SubscriptionResult,
    WebhookEvent,
    register_provider,
)


@register_provider
class StripeProvider(BasePaymentProvider):
    """Stripe payment adapter.

    Config keys:
      - secret_key: Stripe secret key (sk_live_... or sk_test_...)
      - publishable_key: Stripe publishable key (pk_live_... or pk_test_...)
      - webhook_secret: Stripe webhook signing secret (whsec_...)
    """

    provider_type = "stripe"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self._api_key = config["secret_key"]

    def _call_sync(self, resource_method, *args, **kwargs):
        """Call a Stripe API method synchronously with the instance's API key."""
        kwargs.setdefault("api_key", self._api_key)
        return resource_method(*args, **kwargs)

    async def _call(self, resource_method, *args, **kwargs):
        """Call a Stripe API method in a thread pool (non-blocking)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, functools.partial(self._call_sync, resource_method, *args, **kwargs))

    async def create_customer(self, email: str, metadata: dict[str, Any] | None = None) -> CustomerResult:
        customer = await self._call(
            stripe.Customer.create,
            email=email,
            metadata=metadata or {},
        )
        return CustomerResult(
            external_id=customer.id,
            email=customer.email,
            metadata=metadata or {},
        )

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict[str, Any] | None = None,
    ) -> CheckoutResult:
        from app.config import get_settings

        settings = get_settings()

        checkout_params: dict[str, Any] = {
            "customer": customer_id,
            "mode": "subscription",
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": metadata or {},
            "payment_method_types": ["card"],
            "allow_promotion_codes": True,
        }

        # Enable Stripe Tax for automatic tax calculation
        if settings.stripe_tax_enabled:
            checkout_params["automatic_tax"] = {"enabled": True}
            checkout_params["customer_update"] = {"address": "auto"}

        session = await self._call(stripe.checkout.Session.create, **checkout_params)
        return CheckoutResult(
            url=session.url,
            session_id=session.id,
            provider_type="stripe",
        )

    async def create_portal_session(self, customer_id: str, return_url: str) -> PortalResult:
        session = await self._call(
            stripe.billing_portal.Session.create,
            customer=customer_id,
            return_url=return_url,
        )
        return PortalResult(url=session.url)

    async def create_subscription(self, customer_id: str, price_id: str) -> SubscriptionResult:
        sub = await self._call(
            stripe.Subscription.create,
            customer=customer_id,
            items=[{"price": price_id}],
        )
        return SubscriptionResult(
            subscription_id=sub.id,
            status=sub.status,
            current_period_end=str(sub.current_period_end),
            plan_id=price_id,
            cancel_at_period_end=sub.cancel_at_period_end,
        )

    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> SubscriptionResult:
        if at_period_end:
            sub = await self._call(
                stripe.Subscription.modify,
                subscription_id,
                cancel_at_period_end=True,
            )
        else:
            sub = await self._call(stripe.Subscription.cancel, subscription_id)
        return SubscriptionResult(
            subscription_id=sub.id,
            status=sub.status,
            cancel_at_period_end=sub.cancel_at_period_end,
        )

    async def update_subscription(self, subscription_id: str, new_price_id: str) -> SubscriptionResult:
        sub = await self._call(stripe.Subscription.retrieve, subscription_id)
        updated = await self._call(
            stripe.Subscription.modify,
            subscription_id,
            items=[{"id": sub["items"]["data"][0]["id"], "price": new_price_id}],
            proration_behavior="create_prorations",
        )
        return SubscriptionResult(
            subscription_id=updated.id,
            status=updated.status,
            plan_id=new_price_id,
            cancel_at_period_end=updated.cancel_at_period_end,
        )

    # Map Stripe event types to normalized provider-agnostic names
    _EVENT_TYPE_MAP: dict[str, str] = {
        "checkout.session.completed": "checkout.completed",
        "customer.subscription.updated": "subscription.updated",
        "customer.subscription.deleted": "subscription.cancelled",
        "invoice.payment_failed": "payment.failed",
        "invoice.paid": "invoice.paid",
    }

    async def verify_webhook(self, payload: bytes, signature: str, secret: str) -> WebhookEvent:
        event = stripe.Webhook.construct_event(payload, signature, secret)
        raw_type = event["type"]
        normalized_type = self._EVENT_TYPE_MAP.get(raw_type, raw_type)
        return WebhookEvent(
            event_type=normalized_type,
            data=event["data"]["object"],
            raw_payload=payload,
        )

    async def sync_plan(
        self,
        name: str,
        description: str | None,
        price_cents: int,
        interval: str,
        currency: str,
        existing_product_id: str | None = None,
        existing_price_id: str | None = None,
    ) -> PlanSyncResult:
        # Create or update product
        if existing_product_id:
            product = await self._call(
                stripe.Product.modify, existing_product_id, name=name, description=description or ""
            )
        else:
            product = await self._call(stripe.Product.create, name=name, description=description or "")

        # Create new price (Stripe prices are immutable — always create new)
        price = await self._call(
            stripe.Price.create,
            product=product.id,
            unit_amount=price_cents,
            currency=currency,
            recurring={"interval": interval},
        )

        # Archive old price if replaced
        if existing_price_id and existing_price_id != price.id:
            await self._call(stripe.Price.modify, existing_price_id, active=False)

        return PlanSyncResult(
            external_product_id=product.id,
            external_price_id=price.id,
        )

    async def get_payment_methods(self, customer_id: str) -> list[PaymentMethodInfo]:
        methods = await self._call(stripe.PaymentMethod.list, customer=customer_id, type="card")
        customer = await self._call(stripe.Customer.retrieve, customer_id)
        default_pm = (customer.get("invoice_settings") or {}).get("default_payment_method")

        return [
            PaymentMethodInfo(
                id=pm.id,
                type="card",
                last4=pm.card.last4,
                brand=pm.card.brand,
                exp_month=pm.card.exp_month,
                exp_year=pm.card.exp_year,
                is_default=(pm.id == default_pm),
            )
            for pm in methods.data
        ]

    def list_supported_checkout_methods(self) -> list[str]:
        return ["card", "apple_pay", "google_pay", "link"]

    async def report_usage(self, subscription_id: str, metric: str, quantity: int) -> bool:
        """Report metered usage via Stripe Usage Records (for metered billing items)."""
        import time

        sub = await self._call(stripe.Subscription.retrieve, subscription_id)
        # Find the metered subscription item
        for item in sub["items"]["data"]:
            if item["price"].get("recurring", {}).get("usage_type") == "metered":
                await self._call(
                    stripe.SubscriptionItem.create_usage_record,
                    item["id"],
                    quantity=quantity,
                    timestamp=int(time.time()),
                    action="set",
                )
                return True
        return False

    async def test_connection(self) -> bool:
        """Verify Stripe credentials by fetching account info."""
        try:
            await self._call(stripe.Account.retrieve)
            return True
        except Exception:
            return False
