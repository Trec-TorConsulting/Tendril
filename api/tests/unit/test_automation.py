"""Integration tests for Phase 4 automation — rules, alerts, schedules."""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio

from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


@pytest_asyncio.fixture
async def viewer_tenant(db_session):
    """Tenant with a viewer-role user for RBAC testing."""
    import bcrypt

    from app.auth.jwt import create_access_token
    from app.tenants.models import PlatformRole, TenantMembership, TenantRole, User

    factory = TenantFactory(db_session)
    data = await factory.create(name="Viewer Org")
    viewer = User(
        email=f"viewer-{uuid4().hex[:8]}@test.com",
        password_hash=bcrypt.hashpw(b"viewerpass", bcrypt.gensalt()).decode(),
        display_name="Viewer User",
        platform_role=PlatformRole.user,
    )
    db_session.add(viewer)
    await db_session.flush()
    membership = TenantMembership(
        tenant_id=data["tenant"].id,
        user_id=viewer.id,
        role=TenantRole.viewer,
    )
    db_session.add(membership)
    await db_session.commit()

    token = create_access_token(
        viewer.id,
        platform_role="user",
        tenant_id=data["tenant"].id,
        tenant_role="viewer",
    )
    data["viewer_headers"] = {"Authorization": f"Bearer {token}", "X-CSRF-Token": "test-csrf-token"}
    return data


@pytest_asyncio.fixture
async def tent_id(client, tenant):
    resp = await client.post(
        "/v1/tents",
        json={"name": "Auto Tent", "environment_type": "indoor"},
        headers=tenant["headers"],
    )
    return resp.json()["id"]


# ---------- Automation Rules ----------


class TestAutomationRules:
    async def test_create_rule(self, client, tenant):
        resp = await client.post(
            "/v1/automation/rules",
            json={
                "name": "High pH Alert",
                "sensor": "ph",
                "condition": ">",
                "threshold": 7.0,
                "action": "alert",
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "High pH Alert"
        assert data["sensor"] == "ph"
        assert data["threshold"] == 7.0
        assert data["enabled"] is True

    async def test_list_rules(self, client, tenant):
        await client.post(
            "/v1/automation/rules",
            json={"name": "R1", "sensor": "ph", "condition": ">", "threshold": 7, "action": "alert"},
            headers=tenant["headers"],
        )
        await client.post(
            "/v1/automation/rules",
            json={"name": "R2", "sensor": "ec", "condition": "<", "threshold": 0.5, "action": "alert"},
            headers=tenant["headers"],
        )
        resp = await client.get("/v1/automation/rules", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 2

    async def test_update_rule(self, client, tenant):
        create = await client.post(
            "/v1/automation/rules",
            json={"name": "Test", "sensor": "ph", "condition": ">", "threshold": 7, "action": "alert"},
            headers=tenant["headers"],
        )
        rule_id = create.json()["id"]

        resp = await client.patch(
            f"/v1/automation/rules/{rule_id}",
            json={"enabled": False, "threshold": 7.5},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["enabled"] is False
        assert data["threshold"] == 7.5

    async def test_delete_rule(self, client, tenant):
        create = await client.post(
            "/v1/automation/rules",
            json={"name": "Del", "sensor": "ph", "condition": ">", "threshold": 7, "action": "alert"},
            headers=tenant["headers"],
        )
        rule_id = create.json()["id"]

        resp = await client.delete(f"/v1/automation/rules/{rule_id}", headers=tenant["headers"])
        assert resp.status_code == 204

    async def test_rules_no_auth(self, client):
        resp = await client.get("/v1/automation/rules")
        assert resp.status_code in (401, 403)

    async def test_stage_thresholds_crud(self, client, tenant):
        create = await client.post(
            "/v1/automation/rules",
            json={"name": "Stage EC", "sensor": "ec", "condition": "gt", "threshold": 2.5, "action": "alert"},
            headers=tenant["headers"],
        )
        assert create.status_code == 201
        rule_id = create.json()["id"]

        set_resp = await client.put(
            f"/v1/automation/rules/{rule_id}/stage-thresholds",
            json={"thresholds": {"vegetative": 1.6, "flowering": 2.2}},
            headers=tenant["headers"],
        )
        assert set_resp.status_code == 200
        set_data = set_resp.json()
        assert set_data["condition"] == "gt"
        assert set_data["thresholds"]["vegetative"] == 1.6
        assert set_data["thresholds"]["flowering"] == 2.2

        get_resp = await client.get(
            f"/v1/automation/rules/{rule_id}/stage-thresholds",
            headers=tenant["headers"],
        )
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["thresholds"]["vegetative"] == 1.6

        clear_resp = await client.delete(
            f"/v1/automation/rules/{rule_id}/stage-thresholds",
            headers=tenant["headers"],
        )
        assert clear_resp.status_code == 200
        assert clear_resp.json()["thresholds"] == {}

    async def test_stage_thresholds_not_found(self, client, tenant):
        missing_id = uuid4()

        get_resp = await client.get(
            f"/v1/automation/rules/{missing_id}/stage-thresholds",
            headers=tenant["headers"],
        )
        assert get_resp.status_code == 404

        put_resp = await client.put(
            f"/v1/automation/rules/{missing_id}/stage-thresholds",
            json={"thresholds": {"flowering": 2.1}},
            headers=tenant["headers"],
        )
        assert put_resp.status_code == 404

        delete_resp = await client.delete(
            f"/v1/automation/rules/{missing_id}/stage-thresholds",
            headers=tenant["headers"],
        )
        assert delete_resp.status_code == 404

    async def test_stage_thresholds_viewer_permissions(self, client, viewer_tenant):
        create = await client.post(
            "/v1/automation/rules",
            json={"name": "Stage pH", "sensor": "ph", "condition": "gt", "threshold": 6.5, "action": "alert"},
            headers=viewer_tenant["headers"],
        )
        assert create.status_code == 201
        rule_id = create.json()["id"]

        get_resp = await client.get(
            f"/v1/automation/rules/{rule_id}/stage-thresholds",
            headers=viewer_tenant["viewer_headers"],
        )
        assert get_resp.status_code == 200

        put_resp = await client.put(
            f"/v1/automation/rules/{rule_id}/stage-thresholds",
            json={"thresholds": {"flowering": 2.1}},
            headers=viewer_tenant["viewer_headers"],
        )
        assert put_resp.status_code == 403

        delete_resp = await client.delete(
            f"/v1/automation/rules/{rule_id}/stage-thresholds",
            headers=viewer_tenant["viewer_headers"],
        )
        assert delete_resp.status_code == 403


# ---------- Alert History ----------


class TestAlertHistory:
    async def test_list_alerts_empty(self, client, tenant):
        resp = await client.get("/v1/automation/alerts", headers=tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    async def test_alerts_no_auth(self, client):
        resp = await client.get("/v1/automation/alerts")
        assert resp.status_code in (401, 403)


# ---------- Environment Schedules ----------


class TestEnvironmentSchedules:
    async def test_create_schedule(self, client, tenant, tent_id):
        resp = await client.post(
            "/v1/automation/schedules",
            json={
                "tent_id": tent_id,
                "name": "Veg Lights",
                "schedule_type": "light",
                "on_time": "06:00",
                "off_time": "00:00",
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Veg Lights"
        assert data["schedule_type"] == "light"
        assert data["enabled"] is True

    async def test_list_schedules(self, client, tenant, tent_id):
        await client.post(
            "/v1/automation/schedules",
            json={"tent_id": tent_id, "name": "S1", "schedule_type": "light", "on_time": "06:00", "off_time": "18:00"},
            headers=tenant["headers"],
        )
        resp = await client.get("/v1/automation/schedules", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 1

    async def test_filter_schedules_by_tent(self, client, tenant, tent_id):
        await client.post(
            "/v1/automation/schedules",
            json={
                "tent_id": tent_id,
                "name": "Filtered",
                "schedule_type": "fan",
                "on_time": "08:00",
                "off_time": "20:00",
            },
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/automation/schedules?tent_id={tent_id}", headers=tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()["items"]
        assert all(s["tent_id"] == tent_id for s in data)

    async def test_update_schedule(self, client, tenant, tent_id):
        create = await client.post(
            "/v1/automation/schedules",
            json={"tent_id": tent_id, "name": "Upd", "schedule_type": "pump", "on_time": "06:00", "off_time": "18:00"},
            headers=tenant["headers"],
        )
        sched_id = create.json()["id"]

        resp = await client.patch(
            f"/v1/automation/schedules/{sched_id}",
            json={"enabled": False, "on_time": "07:00"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        assert resp.json()["enabled"] is False
        assert resp.json()["on_time"] == "07:00"

    async def test_delete_schedule(self, client, tenant, tent_id):
        create = await client.post(
            "/v1/automation/schedules",
            json={"tent_id": tent_id, "name": "Rm", "schedule_type": "light", "on_time": "06:00", "off_time": "18:00"},
            headers=tenant["headers"],
        )
        sched_id = create.json()["id"]

        resp = await client.delete(f"/v1/automation/schedules/{sched_id}", headers=tenant["headers"])
        assert resp.status_code == 204

    async def test_schedules_no_auth(self, client):
        resp = await client.get("/v1/automation/schedules")
        assert resp.status_code in (401, 403)
