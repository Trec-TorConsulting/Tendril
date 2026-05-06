"""Paddle payment provider adapter (Paddle Billing API v2)."""

from __future__ import annotations

import hashlib
import hmac
import json
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

logger = logging.getLogger("tendril.billing.paddle")

_PADDLE_URLS = {
    "sandbox": "https://sandbox-api.paddle.com",
    "live": "https://api.paddle.com",
}


@register_provider
class PaddleProvider(BasePaymentProvider):
    """Paddle Billing adapter (v2 API).

    Config keys:
      - api_key: Paddle API key
      - mode: "sandbox" or "live"
      - webhook_secret: Paddle webhook secret for signature verification
    """

    provider_type = "paddle"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self._api_key = config["api_key"]
        self._mode = config.get("mode", "sandbox")

    @property
    def base_url(self) -> str:
        return _PADDLE_URLS.get(self._mode, _PADDLE_URLS["sandbox"])

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def create_customer(self, email: str, metadata: dict[str, Any] | None = None) -> CustomerResult:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.base_url}/customers",
                headers=self.headers,
                json={"email": email, "custom_data": metadata or {}},
            )
            resp.raise_for_status()
            customer = resp.json()["data"]

        return CustomerResult(
            external_id=customer["id"],
            email=customer.get("email"),
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
        """Create Paddle checkout via transaction API."""
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.base_url}/transactions",
                headers=self.headers,
                json={
                    "customer_id": customer_id,
                    "items": [{"price_id": price_id, "quantity": 1}],
                    "checkout": {
                        "url": success_url,
                    },
                    "custom_data": metadata or {},
                },
            )
            resp.raise_for_status()
            txn = resp.json()["data"]

        checkout_url = txn.get("checkout", {}).get("url", "")
        return CheckoutResult(
            url=checkout_url,
            session_id=txn["id"],
            provider_type="paddle",
        )

    async def create_portal_session(self, customer_id: str, return_url: str) -> PortalResult:
        """Paddle has a customer portal via their hosted pages."""
        # Paddle's update/cancel URLs are per-subscription
        if self._mode == "live":
            url = "https://customer-portal.paddle.com"
        else:
            url = "https://sandbox-customer-portal.paddle.com"
        return PortalResult(url=url)

    async def create_subscription(self, customer_id: str, price_id: str) -> SubscriptionResult:
        """Paddle subscriptions are created via transactions (require checkout)."""
        result = await self.create_checkout_session(
            customer_id=customer_id,
            price_id=price_id,
            success_url="",
            cancel_url="",
        )
        return SubscriptionResult(
            subscription_id=result.session_id,
            status="pending",
            plan_id=price_id,
        )

    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> SubscriptionResult:
        async with httpx.AsyncClient(timeout=15) as client:
            effective_from = "next_billing_period" if at_period_end else "immediately"
            resp = await client.post(
                f"{self.base_url}/subscriptions/{subscription_id}/cancel",
                headers=self.headers,
                json={"effective_from": effective_from},
            )
            resp.raise_for_status()
            sub = resp.json()["data"]

        return SubscriptionResult(
            subscription_id=sub["id"],
            status=sub.get("status", "canceled"),
            cancel_at_period_end=at_period_end,
        )

    async def update_subscription(self, subscription_id: str, new_price_id: str) -> SubscriptionResult:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.patch(
                f"{self.base_url}/subscriptions/{subscription_id}",
                headers=self.headers,
                json={
                    "items": [{"price_id": new_price_id, "quantity": 1}],
                    "proration_billing_mode": "prorated_immediately",
                },
            )
            resp.raise_for_status()
            sub = resp.json()["data"]

        return SubscriptionResult(
            subscription_id=sub["id"],
            status=sub.get("status", "active"),
            plan_id=new_price_id,
        )

    async def verify_webhook(self, payload: bytes, signature: str, secret: str) -> WebhookEvent:
        """Verify Paddle webhook using ts + h1 signature."""
        # Paddle signature format: "ts=123;h1=abc..."
        parts = dict(p.split("=", 1) for p in signature.split(";") if "=" in p)
        ts = parts.get("ts", "")
        h1 = parts.get("h1", "")

        signed_payload = f"{ts}:{payload.decode()}"
        expected = hmac.HMAC(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected, h1):
            raise ValueError("Paddle webhook signature mismatch")

        body = json.loads(payload)
        return WebhookEvent(
            event_type=body.get("event_type", ""),
            data=body.get("data", {}),
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
        """Create/update Paddle product + price."""
        interval_map = {"month": "month", "year": "year"}
        paddle_interval = interval_map.get(interval, "month")

        async with httpx.AsyncClient(timeout=15) as client:
            # Product
            if existing_product_id:
                resp = await client.patch(
                    f"{self.base_url}/products/{existing_product_id}",
                    headers=self.headers,
                    json={"name": name, "description": description or ""},
                )
                resp.raise_for_status()
                product_id = existing_product_id
            else:
                resp = await client.post(
                    f"{self.base_url}/products",
                    headers=self.headers,
                    json={
                        "name": name,
                        "description": description or "",
                        "tax_category": "standard",
                    },
                )
                resp.raise_for_status()
                product_id = resp.json()["data"]["id"]

            # Price
            resp = await client.post(
                f"{self.base_url}/prices",
                headers=self.headers,
                json={
                    "product_id": product_id,
                    "description": f"{name} - {paddle_interval}ly",
                    "unit_price": {"amount": str(price_cents), "currency_code": currency.upper()},
                    "billing_cycle": {"interval": paddle_interval, "frequency": 1},
                },
            )
            resp.raise_for_status()
            price_id = resp.json()["data"]["id"]

            # Archive old price
            if existing_price_id and existing_price_id != price_id:
                await client.post(
                    f"{self.base_url}/prices/{existing_price_id}/archive",
                    headers=self.headers,
                )

        return PlanSyncResult(
            external_product_id=product_id,
            external_price_id=price_id,
        )

    async def get_payment_methods(self, customer_id: str) -> list[PaymentMethodInfo]:
        """Paddle manages payment methods internally."""
        return []

    def list_supported_checkout_methods(self) -> list[str]:
        return ["card", "paypal", "apple_pay", "google_pay", "wire_transfer"]

    async def report_usage(self, subscription_id: str, metric: str, quantity: int) -> bool:
        """Report usage for metered items (Paddle supports this)."""
        # Paddle doesn't have native metered billing in the same way
        logger.info("Paddle usage reporting: %s=%d for sub %s", metric, quantity, subscription_id)
        return False

    async def test_connection(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/event-types", headers=self.headers)
                return resp.status_code == 200
        except Exception:
            return False
