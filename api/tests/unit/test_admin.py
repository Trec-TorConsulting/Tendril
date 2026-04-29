"""Integration tests for admin API — requires platform_admin or support role."""

from __future__ import annotations

import pytest
import pytest_asyncio
from app.auth.jwt import create_access_token
from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


@pytest_asyncio.fixture
async def admin_tenant(db_session):
    """Tenant with a platform admin user."""
    factory = TenantFactory(db_session)
    data = await factory.create(name="Admin Org")
    # Create admin token with super_admin platform role
    admin_token = create_access_token(
        data["user"].id,
        platform_role="super_admin",
        tenant_id=data["tenant"].id,
        tenant_role="admin",
        account_id=data["account"].id,
    )
    data["admin_headers"] = {"Authorization": f"Bearer {admin_token}", "X-CSRF-Token": "test-csrf-token"}
    return data


@pytest_asyncio.fixture
async def support_tenant(db_session):
    """Tenant with a support user."""
    factory = TenantFactory(db_session)
    data = await factory.create(name="Support Org")
    support_token = create_access_token(
        data["user"].id,
        platform_role="support",
        tenant_id=data["tenant"].id,
        tenant_role="admin",
        account_id=data["account"].id,
    )
    data["support_headers"] = {"Authorization": f"Bearer {support_token}"}
    return data


class TestAdminTenants:
    async def test_list_tenants_as_admin(self, client, admin_tenant):
        resp = await client.get("/v1/admin/tenants", headers=admin_tenant["admin_headers"])
        assert resp.status_code == 200
        assert isinstance(resp.json()["items"], list)

    async def test_list_tenants_as_support(self, client, support_tenant):
        resp = await client.get("/v1/admin/tenants", headers=support_tenant["support_headers"])
        assert resp.status_code == 200

    async def test_list_tenants_forbidden_for_normal_user(self, client, tenant):
        resp = await client.get("/v1/admin/tenants", headers=tenant["headers"])
        assert resp.status_code == 403

    async def test_list_tenants_requires_auth(self, client):
        resp = await client.get("/v1/admin/tenants")
        assert resp.status_code in (401, 403)


class TestAdminUsers:
    async def test_list_tenant_users(self, client, admin_tenant, tenant):
        resp = await client.get(
            f"/v1/admin/tenants/{tenant['tenant'].id}/users",
            headers=admin_tenant["admin_headers"],
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_all_users(self, client, admin_tenant):
        resp = await client.get("/v1/admin/users", headers=admin_tenant["admin_headers"])
        assert resp.status_code == 200
        assert isinstance(resp.json()["items"], list)

    async def test_update_user_flags(self, client, admin_tenant, tenant):
        user_id = str(tenant["user"].id)
        resp = await client.patch(
            f"/v1/admin/users/{user_id}",
            json={"platform_role": "support"},
            headers=admin_tenant["admin_headers"],
        )
        assert resp.status_code == 200
        assert resp.json()["platform_role"] == "support"

    async def test_update_user_flags_requires_admin(self, client, support_tenant, tenant):
        """Support users cannot update user flags — only platform admins can."""
        user_id = str(tenant["user"].id)
        resp = await client.patch(
            f"/v1/admin/users/{user_id}",
            json={"platform_role": "support"},
            headers=support_tenant["support_headers"],
        )
        assert resp.status_code == 403


class TestAdminStats:
    async def test_get_stats(self, client, admin_tenant):
        resp = await client.get("/v1/admin/stats", headers=admin_tenant["admin_headers"])
        assert resp.status_code == 200
