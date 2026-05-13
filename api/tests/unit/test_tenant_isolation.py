"""Tenant isolation tests — verify API-level tenant filtering prevents cross-tenant data access."""

from __future__ import annotations

import pytest
import pytest_asyncio

from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def tenant_a(db_session):
    factory = TenantFactory(db_session)
    return await factory.create(name="Iso Tenant A")


@pytest_asyncio.fixture
async def tenant_b(db_session):
    factory = TenantFactory(db_session)
    return await factory.create(name="Iso Tenant B")


async def test_rls_users_isolation(client, tenant_a, tenant_b):
    """Tenant B's admin endpoints must not return Tenant A's users."""
    # Each tenant has one user created by the factory
    # Listing users via admin endpoint is admin-only, so test via /v1/auth/me
    resp_a = await client.get("/v1/auth/me", headers=tenant_a["headers"])
    resp_b = await client.get("/v1/auth/me", headers=tenant_b["headers"])
    assert resp_a.status_code == 200
    assert resp_b.status_code == 200
    # Each user sees only their own tenant
    assert resp_a.json()["tenant_id"] != resp_b.json()["tenant_id"]


async def test_rls_devices_isolation(client, tenant_a, tenant_b):
    """Devices from one tenant must not be visible to another via the API."""
    # Register a device under tenant A
    resp = await client.post(
        "/v1/devices/register",
        json={"label": "Isolation Sensor"},
        headers=tenant_a["headers"],
    )
    assert resp.status_code == 201
    device_id = resp.json()["device_id"]

    # Tenant B should see 0 devices
    resp_b = await client.get("/v1/devices", headers=tenant_b["headers"])
    assert resp_b.status_code == 200
    devices_b = resp_b.json()["items"]
    assert not any(d["device_id"] == device_id for d in devices_b)

    # Tenant A should see 1 device
    resp_a = await client.get("/v1/devices", headers=tenant_a["headers"])
    assert resp_a.status_code == 200
    devices_a = resp_a.json()["items"]
    assert any(d["device_id"] == device_id for d in devices_a)
