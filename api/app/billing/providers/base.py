"""Payment provider adapter base class and registry."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CustomerResult:
    """Result of creating/fetching a customer."""

    external_id: str
    email: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckoutResult:
    """Result of creating a checkout session."""

    url: str
    session_id: str
    provider_type: str = ""


@dataclass
class PortalResult:
    """Result of creating a customer portal session."""

    url: str


@dataclass
class SubscriptionResult:
    """Result of subscription operations."""

    subscription_id: str
    status: str  # active, past_due, canceled, trialing
    current_period_end: str | None = None
    plan_id: str | None = None
    cancel_at_period_end: bool = False


@dataclass
class WebhookEvent:
    """Parsed webhook event from payment provider."""

    event_type: str  # checkout.completed, subscription.updated, etc.
    data: dict[str, Any] = field(default_factory=dict)
    raw_payload: bytes = b""


@dataclass
class PlanSyncResult:
    """Result of syncing a plan to the provider."""

    external_product_id: str
    external_price_id: str
    external_annual_price_id: str | None = None


@dataclass
class PaymentMethodInfo:
    """Payment method summary."""

    id: str
    type: str  # card, paypal, bank_account
    last4: str | None = None
    brand: str | None = None
    exp_month: int | None = None
    exp_year: int | None = None
    is_default: bool = False


class BasePaymentProvider(abc.ABC):
    """Abstract base for all payment provider adapters.

    Each provider (Stripe, PayPal, Square, Paddle) subclasses this
    and implements all methods.
    """

    provider_type: str = ""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with decrypted provider configuration."""
        self.config = config

    @abc.abstractmethod
    async def create_customer(self, email: str, metadata: dict[str, Any] | None = None) -> CustomerResult:
        """Create a customer in the payment provider."""

    @abc.abstractmethod
    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict[str, Any] | None = None,
    ) -> CheckoutResult:
        """Create a hosted checkout session for subscription."""

    @abc.abstractmethod
    async def create_portal_session(self, customer_id: str, return_url: str) -> PortalResult:
        """Create a customer billing portal session."""

    @abc.abstractmethod
    async def create_subscription(self, customer_id: str, price_id: str) -> SubscriptionResult:
        """Create a subscription directly (without checkout page)."""

    @abc.abstractmethod
    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> SubscriptionResult:
        """Cancel a subscription (immediately or at period end)."""

    @abc.abstractmethod
    async def update_subscription(self, subscription_id: str, new_price_id: str) -> SubscriptionResult:
        """Change a subscription to a different plan/price."""

    @abc.abstractmethod
    async def verify_webhook(self, payload: bytes, signature: str, secret: str) -> WebhookEvent:
        """Verify and parse a webhook payload from the provider."""

    @abc.abstractmethod
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
        """Create or update a product + price in the payment provider."""

    @abc.abstractmethod
    async def get_payment_methods(self, customer_id: str) -> list[PaymentMethodInfo]:
        """List payment methods for a customer."""

    @abc.abstractmethod
    def list_supported_checkout_methods(self) -> list[str]:
        """Return supported checkout methods (card, apple_pay, google_pay, etc.)."""

    @abc.abstractmethod
    async def report_usage(self, subscription_id: str, metric: str, quantity: int) -> bool:
        """Report metered usage to the provider for overage billing."""

    async def test_connection(self) -> bool:
        """Test that credentials are valid. Override per provider."""
        return True


# ─── Provider Registry ─────────────────────────────────────────────────────────

_registry: dict[str, type[BasePaymentProvider]] = {}


def register_provider(cls: type[BasePaymentProvider]) -> type[BasePaymentProvider]:
    """Decorator to register a payment provider adapter."""
    _registry[cls.provider_type] = cls
    return cls


def get_provider_class(provider_type: str) -> type[BasePaymentProvider] | None:
    """Look up a registered provider class by type."""
    return _registry.get(provider_type)


def list_registered_providers() -> list[str]:
    """Return all registered provider type strings."""
    return list(_registry.keys())
