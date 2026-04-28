"""Integration tests for the integrations framework API."""

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
async def tenant_b(db_session):
    factory = TenantFactory(db_session)
    return await factory.create(name="Tenant B")


# ---------- Integration Config CRUD ----------


class TestIntegrationConfigCRUD:
    async def test_create_integration(self, client, tenant):
        resp = await client.post(
            "/v1/integrations",
            json={
                "type": "home_assistant",
                "name": "My HA",
                "config": {"host": "http://ha.local:8123", "api_key": "test-secret-key-12345"},
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "home_assistant"
        assert data["name"] == "My HA"
        assert data["enabled"] is True
        assert data["error_count"] == 0
        assert "webhook_secret" in data
        # Credentials should be redacted
        assert "••••" in data["config"]["api_key"]
        assert data["config"]["host"] == "http://ha.local:8123"

    async def test_create_integration_with_poll_interval(self, client, tenant):
        resp = await client.post(
            "/v1/integrations",
            json={
                "type": "ecowitt",
                "name": "Weather Station",
                "config": {"mac": "AA:BB:CC:DD:EE:FF"},
                "poll_interval_s": 300,
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        assert resp.json()["poll_interval_s"] == 300

    async def test_create_integration_poll_interval_minimum(self, client, tenant):
        resp = await client.post(
            "/v1/integrations",
            json={
                "type": "test",
                "name": "Too Fast",
                "config": {},
                "poll_interval_s": 10,
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 422  # Validation: min 60s

    async def test_list_integrations(self, client, tenant):
        await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "HA1", "config": {}},
            headers=tenant["headers"],
        )
        await client.post(
            "/v1/integrations",
            json={"type": "ecowitt", "name": "EW1", "config": {}},
            headers=tenant["headers"],
        )
        resp = await client.get("/v1/integrations", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 2

    async def test_list_integrations_filter_type(self, client, tenant):
        await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "HA", "config": {}},
            headers=tenant["headers"],
        )
        await client.post(
            "/v1/integrations",
            json={"type": "ecowitt", "name": "EW", "config": {}},
            headers=tenant["headers"],
        )
        resp = await client.get("/v1/integrations?type=ha", headers=tenant["headers"])
        assert resp.status_code == 200
        assert all(i["type"] == "ha" for i in resp.json()["items"])

    async def test_get_integration(self, client, tenant):
        r = await client.post(
            "/v1/integrations",
            json={"type": "pulse", "name": "Pulse", "config": {"token": "abc123"}},
            headers=tenant["headers"],
        )
        iid = r.json()["id"]
        resp = await client.get(f"/v1/integrations/{iid}", headers=tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["name"] == "Pulse"

    async def test_get_integration_not_found(self, client, tenant):
        resp = await client.get(f"/v1/integrations/{uuid4()}", headers=tenant["headers"])
        assert resp.status_code == 404

    async def test_update_integration(self, client, tenant):
        r = await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "Old", "config": {"host": "old.local"}},
            headers=tenant["headers"],
        )
        iid = r.json()["id"]
        resp = await client.patch(
            f"/v1/integrations/{iid}",
            json={"name": "New Name", "enabled": False},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "New Name"
        assert data["enabled"] is False

    async def test_update_integration_config(self, client, tenant):
        r = await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "HA", "config": {"api_key": "old-key-value"}},
            headers=tenant["headers"],
        )
        iid = r.json()["id"]
        resp = await client.patch(
            f"/v1/integrations/{iid}",
            json={"config": {"api_key": "new-key-value"}},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        # Should be re-encrypted and redacted
        assert "••••" in resp.json()["config"]["api_key"]

    async def test_delete_integration(self, client, tenant):
        r = await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "Delete Me", "config": {}},
            headers=tenant["headers"],
        )
        iid = r.json()["id"]
        resp = await client.delete(f"/v1/integrations/{iid}", headers=tenant["headers"])
        assert resp.status_code == 204
        # Verify gone
        resp2 = await client.get(f"/v1/integrations/{iid}", headers=tenant["headers"])
        assert resp2.status_code == 404


# ---------- Integration Tenant Isolation ----------


class TestIntegrationIsolation:
    async def test_tenant_b_cannot_see_tenant_a_integrations(self, client, tenant, tenant_b):
        await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "A's HA", "config": {}},
            headers=tenant["headers"],
        )
        resp = await client.get("/v1/integrations", headers=tenant_b["headers"])
        assert resp.status_code == 200
        assert not any(i["name"] == "A's HA" for i in resp.json()["items"])

    async def test_tenant_b_cannot_access_tenant_a_integration(self, client, tenant, tenant_b):
        r = await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "A Only", "config": {}},
            headers=tenant["headers"],
        )
        iid = r.json()["id"]
        resp = await client.get(f"/v1/integrations/{iid}", headers=tenant_b["headers"])
        assert resp.status_code == 404


# ---------- Device Map CRUD ----------


class TestDeviceMapCRUD:
    async def _create_integration(self, client, tenant):
        r = await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "HA", "config": {}},
            headers=tenant["headers"],
        )
        return r.json()["id"]

    async def test_create_device_map(self, client, tenant):
        iid = await self._create_integration(client, tenant)
        resp = await client.post(
            f"/v1/integrations/{iid}/devices",
            json={
                "external_id": "sensor.temperature_1",
                "external_name": "Tent Temp Sensor",
                "sensor_mapping": {"temperature": "ambient_temp_f"},
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["external_id"] == "sensor.temperature_1"
        assert data["integration_id"] == iid

    async def test_list_device_maps(self, client, tenant):
        iid = await self._create_integration(client, tenant)
        await client.post(
            f"/v1/integrations/{iid}/devices",
            json={"external_id": "sensor.temp_1"},
            headers=tenant["headers"],
        )
        await client.post(
            f"/v1/integrations/{iid}/devices",
            json={"external_id": "sensor.humidity_1"},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/integrations/{iid}/devices", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 2

    async def test_update_device_map(self, client, tenant):
        iid = await self._create_integration(client, tenant)
        r = await client.post(
            f"/v1/integrations/{iid}/devices",
            json={"external_id": "sensor.temp_1"},
            headers=tenant["headers"],
        )
        did = r.json()["id"]
        resp = await client.patch(
            f"/v1/integrations/{iid}/devices/{did}",
            json={"external_name": "Updated Name", "enabled": False},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        assert resp.json()["external_name"] == "Updated Name"
        assert resp.json()["enabled"] is False

    async def test_delete_device_map(self, client, tenant):
        iid = await self._create_integration(client, tenant)
        r = await client.post(
            f"/v1/integrations/{iid}/devices",
            json={"external_id": "sensor.temp_1"},
            headers=tenant["headers"],
        )
        did = r.json()["id"]
        resp = await client.delete(f"/v1/integrations/{iid}/devices/{did}", headers=tenant["headers"])
        assert resp.status_code == 204

    async def test_device_map_not_found(self, client, tenant):
        iid = await self._create_integration(client, tenant)
        resp = await client.patch(
            f"/v1/integrations/{iid}/devices/{uuid4()}",
            json={"external_name": "X"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 404


# ---------- Sync Logs ----------


class TestSyncLogs:
    async def test_list_sync_logs_empty(self, client, tenant):
        r = await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "HA", "config": {}},
            headers=tenant["headers"],
        )
        iid = r.json()["id"]
        resp = await client.get(f"/v1/integrations/{iid}/logs", headers=tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["items"] == []


# ---------- Webhook ----------


class TestWebhook:
    async def test_webhook_invalid_secret(self, client, tenant):
        r = await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "HA", "config": {}},
            headers=tenant["headers"],
        )
        iid = r.json()["id"]
        resp = await client.post(
            f"/v1/integrations/webhook/{iid}",
            json={"webhook_secret": "wrong-secret", "data": {}},
        )
        assert resp.status_code == 401

    async def test_webhook_not_found(self, client, tenant):
        resp = await client.post(
            f"/v1/integrations/webhook/{uuid4()}",
            json={"webhook_secret": "anything"},
        )
        assert resp.status_code == 404

    async def test_webhook_no_connector(self, client, tenant):
        r = await client.post(
            "/v1/integrations",
            json={"type": "unregistered_type", "name": "X", "config": {}},
            headers=tenant["headers"],
        )
        iid = r.json()["id"]
        webhook_secret = r.json()["webhook_secret"]
        resp = await client.post(
            f"/v1/integrations/webhook/{iid}",
            json={"webhook_secret": webhook_secret, "temperature": 72.5},
        )
        assert resp.status_code == 501


# ---------- Manual Sync ----------


class TestManualSync:
    async def test_sync_no_connector(self, client, tenant):
        r = await client.post(
            "/v1/integrations",
            json={"type": "unregistered_type", "name": "X", "config": {}},
            headers=tenant["headers"],
        )
        iid = r.json()["id"]
        resp = await client.post(f"/v1/integrations/{iid}/sync", headers=tenant["headers"])
        assert resp.status_code == 501

    async def test_sync_disabled_integration(self, client, tenant):
        r = await client.post(
            "/v1/integrations",
            json={"type": "ha", "name": "Disabled", "config": {}, "enabled": False},
            headers=tenant["headers"],
        )
        # Need to disable after creation since enabled defaults to True
        iid = r.json()["id"]
        await client.patch(
            f"/v1/integrations/{iid}",
            json={"enabled": False},
            headers=tenant["headers"],
        )
        resp = await client.post(f"/v1/integrations/{iid}/sync", headers=tenant["headers"])
        assert resp.status_code == 409
