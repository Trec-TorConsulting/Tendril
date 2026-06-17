"""Integration tests for device registration, pairing, MQTT auth/ACL webhooks."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


@pytest.fixture
async def tenant_b(db_session):
    factory = TenantFactory(db_session)
    return await factory.create(name="Other Org")


# ---------- Device Registration ----------


class TestDeviceRegistration:
    async def test_register_device(self, client: AsyncClient, tenant):
        res = await client.post(
            "/v1/devices/register",
            json={"label": "Tent A Hub"},
            headers=tenant["headers"],
        )
        assert res.status_code == 201
        data = res.json()
        assert data["device_id"].startswith("td-")
        assert len(data["psk"]) > 20
        assert data["status"] == "unpaired"
        assert data["label"] == "Tent A Hub"

    async def test_register_device_no_label(self, client: AsyncClient, tenant):
        res = await client.post(
            "/v1/devices/register",
            json={},
            headers=tenant["headers"],
        )
        assert res.status_code == 201
        assert res.json()["label"] is None

    async def test_register_requires_auth(self, client: AsyncClient):
        res = await client.post("/v1/devices/register", json={})
        assert res.status_code == 403


# ---------- Device Pairing ----------


class TestDevicePairing:
    async def test_pair_device(self, client: AsyncClient, tenant):
        # Register
        reg = await client.post(
            "/v1/devices/register",
            json={"label": "Hub 1"},
            headers=tenant["headers"],
        )
        data = reg.json()

        # Pair
        res = await client.post(
            "/v1/devices/pair",
            json={"device_id": data["device_id"], "psk": data["psk"]},
            headers=tenant["headers"],
        )
        assert res.status_code == 200
        assert res.json()["status"] == "paired"

    async def test_pair_bad_psk(self, client: AsyncClient, tenant):
        reg = await client.post(
            "/v1/devices/register",
            json={},
            headers=tenant["headers"],
        )
        res = await client.post(
            "/v1/devices/pair",
            json={"device_id": reg.json()["device_id"], "psk": "wrong-key"},
            headers=tenant["headers"],
        )
        assert res.status_code == 401

    async def test_pair_nonexistent_device(self, client: AsyncClient, tenant):
        res = await client.post(
            "/v1/devices/pair",
            json={"device_id": "td-nonexistent", "psk": "test"},
            headers=tenant["headers"],
        )
        assert res.status_code == 404


# ---------- Device CRUD ----------


class TestDeviceCRUD:
    async def test_list_devices(self, client: AsyncClient, tenant):
        # Register two devices
        await client.post("/v1/devices/register", json={"label": "A"}, headers=tenant["headers"])
        await client.post("/v1/devices/register", json={"label": "B"}, headers=tenant["headers"])

        res = await client.get("/v1/devices", headers=tenant["headers"])
        assert res.status_code == 200
        assert len(res.json()) >= 2

    async def test_get_device(self, client: AsyncClient, tenant):
        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        device_id = reg.json()["device_id"]

        res = await client.get(f"/v1/devices/{device_id}", headers=tenant["headers"])
        assert res.status_code == 200
        assert res.json()["device_id"] == device_id

    async def test_rename_device(self, client: AsyncClient, tenant):
        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        device_id = reg.json()["device_id"]

        res = await client.patch(
            f"/v1/devices/{device_id}",
            json={"label": "New Name"},
            headers=tenant["headers"],
        )
        assert res.status_code == 200
        assert res.json()["label"] == "New Name"

    async def test_revoke_device(self, client: AsyncClient, tenant):
        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        device_id = reg.json()["device_id"]

        res = await client.post(f"/v1/devices/{device_id}/revoke", headers=tenant["headers"])
        assert res.status_code == 200
        assert res.json()["status"] == "revoked"

    async def test_delete_device(self, client: AsyncClient, tenant):
        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        device_id = reg.json()["device_id"]

        res = await client.delete(f"/v1/devices/{device_id}", headers=tenant["headers"])
        assert res.status_code == 204

        res = await client.get(f"/v1/devices/{device_id}", headers=tenant["headers"])
        assert res.status_code == 404

    async def test_get_qr_code(self, client: AsyncClient, tenant):
        from app.auth.signed_url import sign_url

        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        device_id = reg.json()["device_id"]
        tid = str(tenant["tenant"].id)

        signed = sign_url(f"http://test/v1/devices/{device_id}/qr", tid)
        # Extract query params from signed URL
        from urllib.parse import urlparse

        parsed = urlparse(signed)
        res = await client.get(
            f"/v1/devices/{device_id}/qr?{parsed.query}",
            headers=tenant["headers"],
        )
        assert res.status_code == 200
        assert res.headers["content-type"] == "image/png"


# ---------- MQTT Auth Webhook ----------


class TestMQTTAuthWebhook:
    @pytest.fixture
    def webhook_client(self):
        from app.mqtt.auth_webhook import webhook_app

        transport = ASGITransport(app=webhook_app)
        return AsyncClient(transport=transport, base_url="http://test")

    async def test_auth_valid_device(self, client: AsyncClient, webhook_client, tenant):
        # Register + pair
        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        data = reg.json()
        await client.post(
            "/v1/devices/pair",
            json={"device_id": data["device_id"], "psk": data["psk"]},
            headers=tenant["headers"],
        )

        res = await webhook_client.post(
            "/auth",
            json={
                "clientid": data["device_id"],
                "username": data["device_id"],
                "password": data["psk"],
            },
        )
        assert res.json()["result"] == "allow"

    async def test_auth_bad_psk(self, client: AsyncClient, webhook_client, tenant):
        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        data = reg.json()
        await client.post(
            "/v1/devices/pair",
            json={"device_id": data["device_id"], "psk": data["psk"]},
            headers=tenant["headers"],
        )

        res = await webhook_client.post(
            "/auth",
            json={
                "clientid": data["device_id"],
                "username": data["device_id"],
                "password": "wrong-psk",
            },
        )
        assert res.json()["result"] == "deny"

    async def test_auth_revoked_device(self, client: AsyncClient, webhook_client, tenant):
        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        data = reg.json()
        await client.post(
            "/v1/devices/pair",
            json={"device_id": data["device_id"], "psk": data["psk"]},
            headers=tenant["headers"],
        )
        await client.post(f"/v1/devices/{data['device_id']}/revoke", headers=tenant["headers"])

        res = await webhook_client.post(
            "/auth",
            json={
                "clientid": data["device_id"],
                "username": data["device_id"],
                "password": data["psk"],
            },
        )
        assert res.json()["result"] == "deny"

    async def test_auth_unknown_device(self, webhook_client):
        res = await webhook_client.post(
            "/auth",
            json={
                "clientid": "td-nonexistent",
                "username": "td-nonexistent",
                "password": "test",
            },
        )
        assert res.json()["result"] == "deny"


# ---------- MQTT ACL Webhook ----------


class TestMQTTACLWebhook:
    @pytest.fixture
    def webhook_client(self):
        from app.mqtt.auth_webhook import webhook_app

        transport = ASGITransport(app=webhook_app)
        return AsyncClient(transport=transport, base_url="http://test")

    async def test_acl_own_topic(self, client: AsyncClient, webhook_client, tenant):
        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        data = reg.json()
        await client.post(
            "/v1/devices/pair",
            json={"device_id": data["device_id"], "psk": data["psk"]},
            headers=tenant["headers"],
        )

        tenant_id = tenant["tenant"].id
        res = await webhook_client.post(
            "/acl",
            json={
                "clientid": data["device_id"],
                "username": data["device_id"],
                "topic": f"t/{tenant_id}/d/{data['device_id']}/sensor/readings",
                "action": "publish",
            },
        )
        assert res.json()["result"] == "allow"

    async def test_acl_other_tenant_topic(self, client: AsyncClient, webhook_client, tenant, tenant_b):
        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        data = reg.json()
        await client.post(
            "/v1/devices/pair",
            json={"device_id": data["device_id"], "psk": data["psk"]},
            headers=tenant["headers"],
        )

        other_tenant_id = tenant_b["tenant"].id
        res = await webhook_client.post(
            "/acl",
            json={
                "clientid": data["device_id"],
                "username": data["device_id"],
                "topic": f"t/{other_tenant_id}/d/{data['device_id']}/sensor/readings",
                "action": "publish",
            },
        )
        assert res.json()["result"] == "deny"

    async def test_acl_other_device_topic(self, client: AsyncClient, webhook_client, tenant):
        reg = await client.post("/v1/devices/register", json={}, headers=tenant["headers"])
        data = reg.json()
        await client.post(
            "/v1/devices/pair",
            json={"device_id": data["device_id"], "psk": data["psk"]},
            headers=tenant["headers"],
        )

        tenant_id = tenant["tenant"].id
        res = await webhook_client.post(
            "/acl",
            json={
                "clientid": data["device_id"],
                "username": data["device_id"],
                "topic": f"t/{tenant_id}/d/td-someone-else/sensor/readings",
                "action": "publish",
            },
        )
        assert res.json()["result"] == "deny"

    async def test_acl_malformed_topic(self, webhook_client):
        res = await webhook_client.post(
            "/acl",
            json={
                "clientid": "td-test",
                "username": "td-test",
                "topic": "invalid/topic",
                "action": "publish",
            },
        )
        assert res.json()["result"] == "deny"


# ---------- Service-layer unit tests ----------


class TestDevicesServiceHelpers:
    """Direct coverage for ``app.devices.service`` pure helpers."""

    def test_generate_device_credentials_format(self):
        import bcrypt

        from app.devices.service import generate_device_credentials

        creds = generate_device_credentials()
        # Device id matches the documented "td-<12 hex chars>" shape.
        assert creds.device_id.startswith("td-")
        assert len(creds.device_id) == 3 + 12
        int(creds.device_id[3:], 16)  # all hex
        # PSK is reasonably high-entropy and the persisted hash verifies it.
        assert len(creds.psk) >= 32
        assert bcrypt.checkpw(creds.psk.encode(), creds.psk_hash.encode())

    def test_generate_device_credentials_unique(self):
        from app.devices.service import generate_device_credentials

        a = generate_device_credentials()
        b = generate_device_credentials()
        assert a.device_id != b.device_id
        assert a.psk != b.psk
        assert a.psk_hash != b.psk_hash

    def test_device_pairing_error_carries_status(self):
        from app.devices.service import DevicePairingError

        err = DevicePairingError(409, "Device is already claimed by another tenant")
        assert err.status_code == 409
        assert err.detail == "Device is already claimed by another tenant"
        assert str(err) == "Device is already claimed by another tenant"
