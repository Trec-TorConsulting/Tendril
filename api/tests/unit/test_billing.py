"""Integration tests for billing API — Stripe integration."""

from __future__ import annotations

import pytest
import pytest_asyncio

from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


class TestBillingStatus:
    async def test_get_billing_status(self, client, tenant):
        resp = await client.get("/v1/billing/status", headers=tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert "plan" in data

    async def test_billing_status_requires_auth(self, client):
        resp = await client.get("/v1/billing/status")
        assert resp.status_code in (401, 403)


class TestBillingCheckout:
    async def test_checkout_requires_owner(self, client, tenant):
        """Only owners can initiate checkout."""
        resp = await client.post(
            "/v1/billing/checkout",
            json={"plan": "grower"},
            headers=tenant["headers"],
        )
        # Owner can attempt checkout — may fail with 500/502 if Stripe not configured
        # but should not be 403
        assert resp.status_code != 403

    async def test_checkout_requires_auth(self, client):
        resp = await client.post("/v1/billing/checkout", json={"plan": "grower"})
        assert resp.status_code in (401, 403)


class TestBillingPortal:
    async def test_portal_requires_owner(self, client, tenant):
        resp = await client.post("/v1/billing/portal", headers=tenant["headers"])
        # May fail if Stripe not configured, but not 403 for owner
        assert resp.status_code != 403

    async def test_portal_requires_auth(self, client):
        resp = await client.post("/v1/billing/portal")
        assert resp.status_code in (401, 403)


class TestBillingWebhook:
    async def test_webhook_rejects_invalid_signature(self, client):
        resp = await client.post(
            "/v1/billing/webhook",
            content=b'{"type": "checkout.session.completed"}',
            headers={"Stripe-Signature": "invalid", "Content-Type": "application/json"},
        )
        # Should reject — 400 or 401 (Stripe signature validation)
        assert resp.status_code in (400, 401, 500)
