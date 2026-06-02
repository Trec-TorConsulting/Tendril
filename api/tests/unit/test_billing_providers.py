"""Unit tests for billing provider adapters, sync, and metering."""

from __future__ import annotations

import pytest

from app.billing.providers.base import (
    BasePaymentProvider,
    CustomerResult,
    get_provider_class,
    list_registered_providers,
)


class TestProviderRegistry:
    """Verify the provider registry discovers all adapters."""

    def test_all_providers_registered(self):
        # Import triggers registration via decorators
        import app.billing.providers.paddle_provider
        import app.billing.providers.paypal_provider
        import app.billing.providers.square_provider
        import app.billing.providers.stripe_provider  # noqa: F401

        registered = list_registered_providers()
        assert "stripe" in registered
        assert "paypal" in registered
        assert "square" in registered
        assert "paddle" in registered

    def test_get_provider_class_returns_class(self):
        import app.billing.providers.stripe_provider  # noqa: F401

        cls = get_provider_class("stripe")
        assert cls is not None
        assert issubclass(cls, BasePaymentProvider)
        assert cls.provider_type == "stripe"

    def test_unknown_provider_returns_none(self):
        assert get_provider_class("nonexistent") is None


class TestPayPalProvider:
    """Test PayPal adapter methods (unit — no network calls)."""

    def _make_provider(self):
        from app.billing.providers.paypal_provider import PayPalProvider

        return PayPalProvider(
            {
                "client_id": "test_id",
                "client_secret": "test_secret",
                "mode": "sandbox",
                "webhook_id": "WH-TEST",
            }
        )

    def test_provider_type(self):
        p = self._make_provider()
        assert p.provider_type == "paypal"

    def test_base_url_sandbox(self):
        p = self._make_provider()
        assert "sandbox" in p.base_url

    def test_base_url_live(self):
        from app.billing.providers.paypal_provider import PayPalProvider

        p = PayPalProvider(
            {
                "client_id": "x",
                "client_secret": "x",
                "mode": "live",
            }
        )
        assert "sandbox" not in p.base_url
        from urllib.parse import urlparse

        parsed = urlparse(p.base_url)
        assert parsed.hostname == "api-m.paypal.com"

    def test_create_customer_uses_email_hash(self):
        import asyncio

        p = self._make_provider()
        result = asyncio.run(p.create_customer("test@example.com"))
        assert isinstance(result, CustomerResult)
        assert result.email == "test@example.com"
        assert len(result.external_id) == 32  # SHA256 truncated

    def test_supported_methods(self):
        p = self._make_provider()
        methods = p.list_supported_checkout_methods()
        assert "paypal" in methods
        assert "card" in methods
        assert "venmo" in methods


class TestSquareProvider:
    """Test Square adapter methods (unit — no network calls)."""

    def _make_provider(self):
        from app.billing.providers.square_provider import SquareProvider

        return SquareProvider(
            {
                "access_token": "test_token",
                "location_id": "LOC123",
                "environment": "sandbox",
            }
        )

    def test_provider_type(self):
        p = self._make_provider()
        assert p.provider_type == "square"

    def test_supported_methods(self):
        p = self._make_provider()
        methods = p.list_supported_checkout_methods()
        assert "card" in methods
        assert "apple_pay" in methods


class TestPaddleProvider:
    """Test Paddle adapter methods (unit — no network calls)."""

    def _make_provider(self):
        from app.billing.providers.paddle_provider import PaddleProvider

        return PaddleProvider(
            {
                "api_key": "test_key",
                "environment": "sandbox",
            }
        )

    def test_provider_type(self):
        p = self._make_provider()
        assert p.provider_type == "paddle"

    def test_supported_methods(self):
        p = self._make_provider()
        methods = p.list_supported_checkout_methods()
        assert "card" in methods
        assert "paypal" in methods


class TestStripeProvider:
    """Test Stripe adapter methods (unit — no network calls)."""

    def _make_provider(self):
        from app.billing.providers.stripe_provider import StripeProvider

        return StripeProvider(
            {
                "secret_key": "sk_test_fake123",
                "webhook_secret": "whsec_test",
                "tax_enabled": False,
            }
        )

    def test_provider_type(self):
        p = self._make_provider()
        assert p.provider_type == "stripe"

    def test_supported_methods_include_wallets(self):
        p = self._make_provider()
        methods = p.list_supported_checkout_methods()
        assert "card" in methods
        assert "apple_pay" in methods
        assert "google_pay" in methods


class TestBaseProviderContract:
    """Verify all adapters implement the full abstract interface."""

    @pytest.mark.parametrize("provider_type", ["stripe", "paypal", "square", "paddle"])
    def test_all_abstract_methods_implemented(self, provider_type):
        import app.billing.providers.paddle_provider
        import app.billing.providers.paypal_provider
        import app.billing.providers.square_provider
        import app.billing.providers.stripe_provider  # noqa: F401

        cls = get_provider_class(provider_type)
        assert cls is not None

        # Should be instantiable (not abstract)
        configs = {
            "stripe": {"secret_key": "sk_test", "webhook_secret": "whsec", "tax_enabled": False},
            "paypal": {"client_id": "x", "client_secret": "x", "mode": "sandbox"},
            "square": {"access_token": "x", "location_id": "x", "environment": "sandbox"},
            "paddle": {"api_key": "x", "environment": "sandbox"},
        }
        instance = cls(configs[provider_type])
        assert instance is not None

        # Verify all base methods exist
        required_methods = [
            "create_customer",
            "create_checkout_session",
            "create_portal_session",
            "create_subscription",
            "cancel_subscription",
            "update_subscription",
            "verify_webhook",
            "sync_plan",
            "get_payment_methods",
            "list_supported_checkout_methods",
            "report_usage",
            "test_connection",
        ]
        for method_name in required_methods:
            assert hasattr(instance, method_name), f"{provider_type} missing {method_name}"
            assert callable(getattr(instance, method_name))


class TestSyncModule:
    """Test the billing sync module structure."""

    def test_reconcile_function_importable(self):
        from app.billing.sync import pull_plans_from_provider, reconcile_all_providers

        assert callable(reconcile_all_providers)
        assert callable(pull_plans_from_provider)


class TestMeteringModule:
    """Test metering module structure."""

    def test_metering_importable(self):
        from app.billing.metering import record_usage

        assert callable(record_usage)
