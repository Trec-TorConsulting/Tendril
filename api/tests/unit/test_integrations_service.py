"""Unit tests for app.integrations.service pure helpers + custom errors."""

from __future__ import annotations

import pytest

from app.integrations.service import (
    DiscoveryNotSupportedError,
    IntegrationDisabledError,
    UnsupportedConnectorError,
    WebhookAuthError,
    generate_webhook_secret,
    verify_webhook_secret,
)


class TestGenerateWebhookSecret:
    def test_produces_url_safe_string(self):
        s = generate_webhook_secret()
        # token_urlsafe(32) -> 43 chars (no padding)
        assert len(s) >= 32
        # Url-safe alphabet only
        assert all(c.isalnum() or c in "-_" for c in s)

    def test_unique_per_call(self):
        assert generate_webhook_secret() != generate_webhook_secret()


class TestVerifyWebhookSecret:
    def test_accepts_matching(self):
        verify_webhook_secret("abc123", "abc123")  # no raise

    def test_rejects_mismatch(self):
        with pytest.raises(WebhookAuthError):
            verify_webhook_secret("wrong", "expected")

    def test_rejects_empty_provided(self):
        with pytest.raises(WebhookAuthError):
            verify_webhook_secret("", "expected")

    def test_constant_time_compare_doesnt_short_circuit_on_length(self):
        # Functional smoke — both length-different inputs raise the same
        # exception type.  (The hmac.compare_digest call inside the
        # service guards against length-based timing leaks; we can't
        # test timing in a unit test, but we can pin the raise behaviour.)
        with pytest.raises(WebhookAuthError):
            verify_webhook_secret("short", "much-longer-expected-value")

    def test_coerces_non_string_provided(self):
        # The route accepts dict-popped values which can be non-strings;
        # the service coerces via str() before compare.
        with pytest.raises(WebhookAuthError):
            verify_webhook_secret(None, "expected")  # type: ignore[arg-type]


class TestCustomErrors:
    """Each typed error maps to a specific HTTP status in the route layer."""

    def test_integration_disabled_is_exception(self):
        err = IntegrationDisabledError("disabled")
        assert isinstance(err, Exception)
        assert "disabled" in str(err)

    def test_webhook_auth_is_exception(self):
        err = WebhookAuthError("bad secret")
        assert isinstance(err, Exception)

    def test_unsupported_connector_carries_type(self):
        err = UnsupportedConnectorError("totally_made_up")
        assert err.integration_type == "totally_made_up"
        assert "totally_made_up" in str(err)

    def test_discovery_not_supported_is_exception(self):
        err = DiscoveryNotSupportedError("nope")
        assert isinstance(err, Exception)
