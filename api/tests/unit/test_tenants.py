"""Integration tests for tenant management API."""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


@pytest_asyncio.fixture
async def viewer_tenant(db_session):
    """Tenant with a viewer-role user for RBAC testing."""
    import bcrypt
    from app.auth.jwt import create_access_token
    from app.tenants.models import User

    factory = TenantFactory(db_session)
    data = await factory.create(name="Viewer Org")
    viewer = User(
        tenant_id=data["tenant"].id,
        email=f"viewer-{uuid4().hex[:8]}@test.com",
        password_hash=bcrypt.hashpw(b"viewerpass", bcrypt.gensalt()).decode(),
        display_name="Viewer User",
        role="viewer",
    )
    db_session.add(viewer)
    await db_session.commit()
    await db_session.refresh(viewer)
    token = create_access_token(viewer.id, data["tenant"].id, "viewer")
    data["viewer_headers"] = {"Authorization": f"Bearer {token}"}
    data["viewer_user"] = viewer
    return data


class TestTenantMe:
    async def test_get_tenant_me(self, client, tenant):
        resp = await client.get("/v1/tenants/me", headers=tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data
        assert "slug" in data
        assert "plan" in data

    async def test_update_tenant_me(self, client, tenant):
        resp = await client.patch(
            "/v1/tenants/me",
            json={"name": "Updated Org Name"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Org Name"

    async def test_update_tenant_requires_owner(self, client, viewer_tenant):
        resp = await client.patch(
            "/v1/tenants/me",
            json={"name": "Nope"},
            headers=viewer_tenant["viewer_headers"],
        )
        assert resp.status_code == 403

    async def test_tenant_requires_auth(self, client):
        resp = await client.get("/v1/tenants/me")
        assert resp.status_code in (401, 403)


class TestTenantMembers:
    async def test_list_members(self, client, tenant):
        resp = await client.get("/v1/tenants/members", headers=tenant["headers"])
        assert resp.status_code == 200
        members = resp.json()
        assert len(members) >= 1  # At least the owner

    async def test_invite_member(self, client, tenant):
        resp = await client.post(
            "/v1/tenants/members",
            json={
                "email": f"invite-{uuid4().hex[:8]}@test.com",
                "display_name": "New Member",
                "password": "SecurePass123!",
                "role": "member",
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["role"] == "member"

    async def test_update_member_role(self, client, tenant):
        # First invite a member
        r = await client.post(
            "/v1/tenants/members",
            json={
                "email": f"role-{uuid4().hex[:8]}@test.com",
                "password": "SecurePass123!",
                "role": "member",
            },
            headers=tenant["headers"],
        )
        mid = r.json()["id"]
        resp = await client.patch(
            f"/v1/tenants/members/{mid}",
            json={"role": "viewer"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "viewer"

    async def test_delete_member(self, client, tenant):
        r = await client.post(
            "/v1/tenants/members",
            json={
                "email": f"del-{uuid4().hex[:8]}@test.com",
                "password": "SecurePass123!",
                "role": "member",
            },
            headers=tenant["headers"],
        )
        mid = r.json()["id"]
        resp = await client.delete(f"/v1/tenants/members/{mid}", headers=tenant["headers"])
        assert resp.status_code == 204

    async def test_invite_requires_owner(self, client, viewer_tenant):
        resp = await client.post(
            "/v1/tenants/members",
            json={
                "email": "nope@test.com",
                "password": "SecurePass123!",
                "role": "member",
            },
            headers=viewer_tenant["viewer_headers"],
        )
        assert resp.status_code == 403
