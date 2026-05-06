"""Square payment provider adapter."""

from __future__ import annotations

import logging
from typing import Any

import httpx

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

logger = logging.getLogger("tendril.billing.square")

_SQUARE_URLS = {
    "sandbox": "https://connect.squareupsandbox.com/v2",
    "production": "https://connect.squareup.com/v2",
}


@register_provider
class SquareProvider(BasePaymentProvider):
    """Square payment adapter.

    Config keys:
      - access_token: Square access token
      - mode: "sandbox" or "production"
      - location_id: Square location ID
      - webhook_signature_key: Square webhook signature key
    """

    provider_type = "square"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self._access_token = config["access_token"]
        self._mode = config.get("mode", "sandbox")
        self._location_id = config.get("location_id", "")

    @property
    def base_url(self) -> str:
        return _SQUARE_URLS.get(self._mode, _SQUARE_URLS["sandbox"])

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "Square-Version": "2024-01-18",
        }

    async def create_customer(self, email: str, metadata: dict[str, Any] | None = None) -> CustomerResult:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.base_url}/customers",
                headers=self.headers,
                json={
                    "email_address": email,
                    "reference_id": (metadata or {}).get("tenant_id", ""),
                },
            )
            resp.raise_for_status()
            customer = resp.json()["customer"]

        return CustomerResult(
            external_id=customer["id"],
            email=customer.get("email_address"),
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
        """Create a Square checkout link for subscription."""
        import uuid

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.base_url}/online-checkout/payment-links",
                headers=self.headers,
                json={
                    "idempotency_key": str(uuid.uuid4()),
                    "quick_pay": {
                        "name": "Tendril Subscription",
                        "price_money": {"amount": 0, "currency": "USD"},
                        "location_id": self._location_id,
                    },
                    "checkout_options": {
                        "redirect_url": success_url,
                        "subscription_plan_id": price_id,
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()

        link = data.get("payment_link", {})
        return CheckoutResult(
            url=link.get("url", ""),
            session_id=link.get("id", ""),
            provider_type="square",
        )

    async def create_portal_session(self, customer_id: str, return_url: str) -> PortalResult:
        """Square doesn't have a customer portal — no equivalent."""
        return PortalResult(url=return_url)

    async def create_subscription(self, customer_id: str, price_id: str) -> SubscriptionResult:
        import uuid

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.base_url}/subscriptions",
                headers=self.headers,
                json={
                    "idempotency_key": str(uuid.uuid4()),
                    "location_id": self._location_id,
                    "plan_variation_id": price_id,
                    "customer_id": customer_id,
                },
            )
            resp.raise_for_status()
            sub = resp.json()["subscription"]

        return SubscriptionResult(
            subscription_id=sub["id"],
            status=sub.get("status", "PENDING").lower(),
            plan_id=price_id,
        )

    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> SubscriptionResult:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.base_url}/subscriptions/{subscription_id}/cancel",
                headers=self.headers,
                json={},
            )
            resp.raise_for_status()
            sub = resp.json()["subscription"]

        return SubscriptionResult(
            subscription_id=sub["id"],
            status="canceled",
            cancel_at_period_end=at_period_end,
        )

    async def update_subscription(self, subscription_id: str, new_price_id: str) -> SubscriptionResult:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.put(
                f"{self.base_url}/subscriptions/{subscription_id}",
                headers=self.headers,
                json={
                    "subscription": {"plan_variation_id": new_price_id},
                },
            )
            resp.raise_for_status()
            sub = resp.json()["subscription"]

        return SubscriptionResult(
            subscription_id=sub["id"],
            status=sub.get("status", "active").lower(),
            plan_id=new_price_id,
        )

    async def verify_webhook(self, payload: bytes, signature: str, secret: str) -> WebhookEvent:
        """Verify Square webhook signature."""
        import hashlib
        import hmac
        import json

        # Square uses HMAC-SHA256
        expected = hmac.HMAC(secret.encode(), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise ValueError("Square webhook signature mismatch")

        body = json.loads(payload)
        return WebhookEvent(
            event_type=body.get("type", ""),
            data=body.get("data", {}).get("object", {}),
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
        """Create a subscription plan in Square Catalog."""
        import uuid

        interval_map = {"month": "MONTHLY", "year": "EVERY_TWELVE_MONTHS"}
        sq_cadence = interval_map.get(interval, "MONTHLY")

        async with httpx.AsyncClient(timeout=15) as client:
            plan_id = f"#plan_{uuid.uuid4().hex[:8]}"
            variation_id = f"#variation_{uuid.uuid4().hex[:8]}"

            resp = await client.post(
                f"{self.base_url}/catalog/object",
                headers=self.headers,
                json={
                    "idempotency_key": str(uuid.uuid4()),
                    "object": {
                        "type": "SUBSCRIPTION_PLAN",
                        "id": plan_id,
                        "subscription_plan_data": {
                            "name": name,
                            "phases": [
                                {
                                    "cadence": sq_cadence,
                                    "pricing": {
                                        "type": "STATIC",
                                        "price_money": {
                                            "amount": price_cents,
                                            "currency": currency.upper(),
                                        },
                                    },
                                }
                            ],
                        },
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()
            catalog_obj = data.get("catalog_object", {})

        return PlanSyncResult(
            external_product_id=catalog_obj.get("id", plan_id),
            external_price_id=catalog_obj.get("id", variation_id),
        )

    async def get_payment_methods(self, customer_id: str) -> list[PaymentMethodInfo]:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self.base_url}/customers/{customer_id}/cards",
                headers=self.headers,
            )
            if resp.status_code != 200:
                return []
            cards = resp.json().get("cards", [])

        return [
            PaymentMethodInfo(
                id=c["id"],
                type="card",
                last4=c.get("last_4"),
                brand=c.get("card_brand"),
                exp_month=c.get("exp_month"),
                exp_year=c.get("exp_year"),
            )
            for c in cards
        ]

    def list_supported_checkout_methods(self) -> list[str]:
        return ["card", "apple_pay", "google_pay", "cash_app"]

    async def report_usage(self, subscription_id: str, metric: str, quantity: int) -> bool:
        logger.warning("Square does not support metered usage reporting natively")
        return False

    async def test_connection(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/merchants", headers=self.headers)
                return resp.status_code == 200
        except Exception:
            return False
