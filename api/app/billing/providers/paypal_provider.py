"""PayPal payment provider adapter."""

from __future__ import annotations

import base64
import hashlib
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

logger = logging.getLogger("tendril.billing.paypal")

_PAYPAL_URLS = {
    "sandbox": "https://api-m.sandbox.paypal.com",
    "live": "https://api-m.paypal.com",
}


@register_provider
class PayPalProvider(BasePaymentProvider):
    """PayPal payment adapter using PayPal REST API v2.

    Config keys:
      - client_id: PayPal app client ID
      - client_secret: PayPal app secret
      - mode: "sandbox" or "live"
      - webhook_id: PayPal webhook ID for verification
    """

    provider_type = "paypal"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self._client_id = config["client_id"]
        self._client_secret = config["client_secret"]
        self._mode = config.get("mode", "sandbox")
        self._webhook_id = config.get("webhook_id", "")
        self._access_token: str | None = None

    @property
    def base_url(self) -> str:
        return _PAYPAL_URLS.get(self._mode, _PAYPAL_URLS["sandbox"])

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        """Get OAuth2 access token."""
        if self._access_token:
            return self._access_token

        auth = base64.b64encode(f"{self._client_id}:{self._client_secret}".encode()).decode()
        resp = await client.post(
            f"{self.base_url}/v1/oauth2/token",
            headers={"Authorization": f"Basic {auth}"},
            data={"grant_type": "client_credentials"},
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        return self._access_token

    async def _auth_headers(self, client: httpx.AsyncClient) -> dict[str, str]:
        token = await self._get_token(client)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def create_customer(self, email: str, metadata: dict[str, Any] | None = None) -> CustomerResult:
        """PayPal doesn't have a customer object — use email as reference."""
        # PayPal uses payer email directly; we store email as external_id
        return CustomerResult(
            external_id=hashlib.sha256(email.encode()).hexdigest()[:32],
            email=email,
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
        """Create a PayPal subscription with approval link."""
        async with httpx.AsyncClient(timeout=15) as client:
            headers = await self._auth_headers(client)
            resp = await client.post(
                f"{self.base_url}/v1/billing/subscriptions",
                headers=headers,
                json={
                    "plan_id": price_id,
                    "application_context": {
                        "return_url": success_url,
                        "cancel_url": cancel_url,
                        "brand_name": "Tendril",
                        "user_action": "SUBSCRIBE_NOW",
                    },
                    "custom_id": (metadata or {}).get("tenant_id", ""),
                },
            )
            resp.raise_for_status()
            data = resp.json()

        # Find approval link
        approval_url = ""
        for link in data.get("links", []):
            if link["rel"] == "approve":
                approval_url = link["href"]
                break

        return CheckoutResult(
            url=approval_url,
            session_id=data["id"],
            provider_type="paypal",
        )

    async def create_portal_session(self, customer_id: str, return_url: str) -> PortalResult:
        """PayPal doesn't have a portal — redirect to PayPal subscriptions page."""
        if self._mode == "live":
            url = "https://www.paypal.com/myaccount/autopay"
        else:
            url = "https://www.sandbox.paypal.com/myaccount/autopay"
        return PortalResult(url=url)

    async def create_subscription(self, customer_id: str, price_id: str) -> SubscriptionResult:
        """Create a PayPal subscription (requires user approval — use checkout instead)."""
        # In practice, PayPal subscriptions require user redirect
        # This creates a draft subscription
        async with httpx.AsyncClient(timeout=15) as client:
            headers = await self._auth_headers(client)
            resp = await client.post(
                f"{self.base_url}/v1/billing/subscriptions",
                headers=headers,
                json={"plan_id": price_id},
            )
            resp.raise_for_status()
            data = resp.json()

        return SubscriptionResult(
            subscription_id=data["id"],
            status=data.get("status", "APPROVAL_PENDING").lower(),
            plan_id=price_id,
        )

    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> SubscriptionResult:
        async with httpx.AsyncClient(timeout=15) as client:
            headers = await self._auth_headers(client)
            resp = await client.post(
                f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/cancel",
                headers=headers,
                json={"reason": "Customer requested cancellation"},
            )
            resp.raise_for_status()

        return SubscriptionResult(
            subscription_id=subscription_id,
            status="cancelled",
            cancel_at_period_end=at_period_end,
        )

    async def update_subscription(self, subscription_id: str, new_price_id: str) -> SubscriptionResult:
        """Revise subscription plan in PayPal."""
        async with httpx.AsyncClient(timeout=15) as client:
            headers = await self._auth_headers(client)
            resp = await client.post(
                f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/revise",
                headers=headers,
                json={"plan_id": new_price_id},
            )
            resp.raise_for_status()
            data = resp.json()

        return SubscriptionResult(
            subscription_id=subscription_id,
            status=data.get("status", "active").lower(),
            plan_id=new_price_id,
        )

    async def verify_webhook(self, payload: bytes, signature: str, secret: str) -> WebhookEvent:
        """Verify PayPal webhook using notification verification API."""
        import json

        body = json.loads(payload)

        async with httpx.AsyncClient(timeout=15) as client:
            headers = await self._auth_headers(client)
            resp = await client.post(
                f"{self.base_url}/v1/notifications/verify-webhook-signature",
                headers=headers,
                json={
                    "webhook_id": self._webhook_id,
                    "transmission_id": body.get("id", ""),
                    "transmission_time": body.get("create_time", ""),
                    "cert_url": "",
                    "auth_algo": "SHA256withRSA",
                    "transmission_sig": signature,
                    "webhook_event": body,
                },
            )
            data = resp.json()
            if data.get("verification_status") != "SUCCESS":
                raise ValueError("PayPal webhook signature verification failed")

        event_type = body.get("event_type", "")
        resource = body.get("resource", {})

        return WebhookEvent(
            event_type=event_type,
            data=resource,
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
        """Create/update PayPal product + billing plan."""
        interval_map = {"month": "MONTH", "year": "YEAR"}
        paypal_interval = interval_map.get(interval, "MONTH")

        async with httpx.AsyncClient(timeout=15) as client:
            headers = await self._auth_headers(client)

            # Create or get product
            if existing_product_id:
                product_id = existing_product_id
            else:
                resp = await client.post(
                    f"{self.base_url}/v1/catalogs/products",
                    headers=headers,
                    json={
                        "name": name,
                        "description": description or name,
                        "type": "SERVICE",
                        "category": "SOFTWARE",
                    },
                )
                resp.raise_for_status()
                product_id = resp.json()["id"]

            # Create billing plan (PayPal plans are immutable — always create new)
            resp = await client.post(
                f"{self.base_url}/v1/billing/plans",
                headers=headers,
                json={
                    "product_id": product_id,
                    "name": name,
                    "description": description or name,
                    "billing_cycles": [
                        {
                            "frequency": {"interval_unit": paypal_interval, "interval_count": 1},
                            "tenure_type": "REGULAR",
                            "sequence": 1,
                            "pricing_scheme": {
                                "fixed_price": {
                                    "value": str(price_cents / 100),
                                    "currency_code": currency.upper(),
                                },
                            },
                        }
                    ],
                    "payment_preferences": {
                        "auto_bill_outstanding": True,
                        "payment_failure_threshold": 3,
                    },
                },
            )
            resp.raise_for_status()
            plan_data = resp.json()

            # Deactivate old plan if replaced
            if existing_price_id and existing_price_id != plan_data["id"]:
                await client.post(
                    f"{self.base_url}/v1/billing/plans/{existing_price_id}/deactivate",
                    headers=headers,
                )

        return PlanSyncResult(
            external_product_id=product_id,
            external_price_id=plan_data["id"],
        )

    async def get_payment_methods(self, customer_id: str) -> list[PaymentMethodInfo]:
        """PayPal doesn't expose saved methods via REST easily."""
        return []

    def list_supported_checkout_methods(self) -> list[str]:
        return ["paypal", "card", "venmo"]

    async def report_usage(self, subscription_id: str, metric: str, quantity: int) -> bool:
        """PayPal doesn't support metered billing natively."""
        logger.warning("PayPal does not support metered usage reporting")
        return False

    async def test_connection(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await self._get_token(client)
            return True
        except Exception:
            return False
