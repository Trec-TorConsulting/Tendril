"""Integration tests for Phase 6 commercial features — custom grow types, tasks, audit, API keys."""

from __future__ import annotations

import pytest
import pytest_asyncio

from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def commercial_tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create(plan="commercial")


@pytest_asyncio.fixture
async def pro_tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create(plan="pro")


@pytest_asyncio.fixture
async def free_tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create(plan="free")


# ===================== Custom Grow Types =====================


class TestCustomGrowTypes:
    async def test_create_custom_grow_type(self, client, pro_tenant):
        resp = await client.post(
            "/v1/custom-grow-types",
            json={
                "name": "My DWC Variant",
                "slug": "my-dwc-variant",
                "category": "hydroponic",
                "description": "A customized DWC setup",
                "base_type": "dwc",
                "profile": {"feeding_approach": "aggressive"},
            },
            headers=pro_tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "My DWC Variant"
        assert data["slug"] == "my-dwc-variant"
        assert data["base_type"] == "dwc"

    async def test_list_custom_grow_types(self, client, pro_tenant):
        await client.post(
            "/v1/custom-grow-types",
            json={"name": "Type A", "slug": "type-a", "category": "custom", "description": "Test", "profile": {}},
            headers=pro_tenant["headers"],
        )
        resp = await client.get("/v1/custom-grow-types", headers=pro_tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_update_custom_grow_type(self, client, pro_tenant):
        create = await client.post(
            "/v1/custom-grow-types",
            json={
                "name": "Old Name",
                "slug": "update-test",
                "category": "custom",
                "description": "Test",
                "profile": {},
            },
            headers=pro_tenant["headers"],
        )
        gt_id = create.json()["id"]
        resp = await client.patch(
            f"/v1/custom-grow-types/{gt_id}",
            json={"name": "New Name"},
            headers=pro_tenant["headers"],
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    async def test_delete_custom_grow_type(self, client, pro_tenant):
        create = await client.post(
            "/v1/custom-grow-types",
            json={"name": "Delete Me", "slug": "delete-me", "category": "custom", "description": "Test", "profile": {}},
            headers=pro_tenant["headers"],
        )
        gt_id = create.json()["id"]
        resp = await client.delete(f"/v1/custom-grow-types/{gt_id}", headers=pro_tenant["headers"])
        assert resp.status_code == 204

    async def test_submit_for_review(self, client, pro_tenant):
        create = await client.post(
            "/v1/custom-grow-types",
            json={"name": "Submit Me", "slug": "submit-me", "category": "custom", "description": "Test", "profile": {}},
            headers=pro_tenant["headers"],
        )
        gt_id = create.json()["id"]
        resp = await client.post(f"/v1/custom-grow-types/{gt_id}/submit", headers=pro_tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["status"] == "submitted"

    async def test_duplicate_slug_rejected(self, client, pro_tenant):
        await client.post(
            "/v1/custom-grow-types",
            json={"name": "First", "slug": "dupe-slug", "category": "custom", "description": "Test", "profile": {}},
            headers=pro_tenant["headers"],
        )
        resp = await client.post(
            "/v1/custom-grow-types",
            json={"name": "Second", "slug": "dupe-slug", "category": "custom", "description": "Test", "profile": {}},
            headers=pro_tenant["headers"],
        )
        assert resp.status_code == 409

    async def test_free_plan_rejected(self, client, free_tenant):
        resp = await client.post(
            "/v1/custom-grow-types",
            json={"name": "Nope", "slug": "nope", "category": "custom", "description": "Test", "profile": {}},
            headers=free_tenant["headers"],
        )
        assert resp.status_code == 403


# ===================== Tasks =====================


class TestTasks:
    async def test_create_task(self, client, commercial_tenant):
        resp = await client.post(
            "/v1/tasks",
            json={"title": "Water the plants", "priority": "high"},
            headers=commercial_tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Water the plants"
        assert data["priority"] == "high"
        assert data["status"] == "pending"

    async def test_list_tasks(self, client, commercial_tenant):
        await client.post("/v1/tasks", json={"title": "Task 1"}, headers=commercial_tenant["headers"])
        resp = await client.get("/v1/tasks", headers=commercial_tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 1

    async def test_complete_task(self, client, commercial_tenant):
        create = await client.post("/v1/tasks", json={"title": "Complete me"}, headers=commercial_tenant["headers"])
        task_id = create.json()["id"]
        resp = await client.post(f"/v1/tasks/{task_id}/complete", headers=commercial_tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"
        assert resp.json()["completed_at"] is not None

    async def test_recurring_task_creates_next(self, client, commercial_tenant):
        create = await client.post(
            "/v1/tasks",
            json={"title": "Recurring", "recurring": "weekly", "due_date": "2025-01-01T00:00:00Z"},
            headers=commercial_tenant["headers"],
        )
        task_id = create.json()["id"]
        await client.post(f"/v1/tasks/{task_id}/complete", headers=commercial_tenant["headers"])

        resp = await client.get("/v1/tasks?status=pending", headers=commercial_tenant["headers"])
        pending = resp.json()["items"]
        assert any(t["title"] == "Recurring" for t in pending)

    async def test_delete_task(self, client, commercial_tenant):
        create = await client.post("/v1/tasks", json={"title": "Delete me"}, headers=commercial_tenant["headers"])
        task_id = create.json()["id"]
        resp = await client.delete(f"/v1/tasks/{task_id}", headers=commercial_tenant["headers"])
        assert resp.status_code == 204

    async def test_filter_by_status(self, client, commercial_tenant):
        await client.post("/v1/tasks", json={"title": "A"}, headers=commercial_tenant["headers"])
        resp = await client.get("/v1/tasks?status=pending", headers=commercial_tenant["headers"])
        assert resp.status_code == 200
        assert all(t["status"] == "pending" for t in resp.json()["items"])

    async def test_non_commercial_rejected(self, client, pro_tenant):
        resp = await client.post("/v1/tasks", json={"title": "Nope"}, headers=pro_tenant["headers"])
        assert resp.status_code == 403


# ===================== Audit Trail =====================


class TestAuditTrail:
    async def test_list_empty(self, client, commercial_tenant):
        resp = await client.get("/v1/audit", headers=commercial_tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_non_commercial_rejected(self, client, pro_tenant):
        resp = await client.get("/v1/audit", headers=pro_tenant["headers"])
        assert resp.status_code == 403

    async def test_pagination_params(self, client, commercial_tenant):
        resp = await client.get("/v1/audit?page=1&page_size=10", headers=commercial_tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 10


# ===================== API Keys =====================


class TestApiKeys:
    async def test_create_api_key(self, client, commercial_tenant):
        resp = await client.post(
            "/v1/api-keys",
            json={"name": "My Integration", "scopes": "read"},
            headers=commercial_tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "My Integration"
        assert data["key"].startswith("tnd_")
        assert len(data["key"]) > 20

    async def test_list_api_keys(self, client, commercial_tenant):
        await client.post(
            "/v1/api-keys",
            json={"name": "Key 1", "scopes": "read"},
            headers=commercial_tenant["headers"],
        )
        resp = await client.get("/v1/api-keys", headers=commercial_tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_revoke_api_key(self, client, commercial_tenant):
        create = await client.post(
            "/v1/api-keys",
            json={"name": "Revoke Me"},
            headers=commercial_tenant["headers"],
        )
        key_id = create.json()["id"]
        resp = await client.delete(f"/v1/api-keys/{key_id}", headers=commercial_tenant["headers"])
        assert resp.status_code == 204

        # Verify it's gone from the active list
        list_resp = await client.get("/v1/api-keys", headers=commercial_tenant["headers"])
        assert all(k["id"] != key_id for k in list_resp.json())

    async def test_invalid_scopes_rejected(self, client, commercial_tenant):
        resp = await client.post(
            "/v1/api-keys",
            json={"name": "Bad", "scopes": "read,superadmin"},
            headers=commercial_tenant["headers"],
        )
        assert resp.status_code == 400

    async def test_non_commercial_rejected(self, client, pro_tenant):
        resp = await client.post(
            "/v1/api-keys",
            json={"name": "Nope"},
            headers=pro_tenant["headers"],
        )
        assert resp.status_code == 403

    async def test_key_with_expiry(self, client, commercial_tenant):
        resp = await client.post(
            "/v1/api-keys",
            json={"name": "Expiring", "scopes": "read", "expires_in_days": 30},
            headers=commercial_tenant["headers"],
        )
        assert resp.status_code == 201
        assert resp.json()["expires_at"] is not None
