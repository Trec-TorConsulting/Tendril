"""Integration tests for sensor reading APIs — bucket + tent sensors."""

from __future__ import annotations

import pytest
import pytest_asyncio
from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


async def _setup_bucket(client, tenant):
    """Helper: create a tent → grow → bucket and return bucket_id."""
    t = await client.post("/v1/tents", json={"name": "Tent"}, headers=tenant["headers"])
    g = await client.post(
        "/v1/grows",
        json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"},
        headers=tenant["headers"],
    )
    b = await client.post(
        "/v1/buckets",
        json={"grow_cycle_id": g.json()["id"], "label": "B1"},
        headers=tenant["headers"],
    )
    return t.json()["id"], b.json()["id"]


# ---------- Bucket Sensors ----------


class TestBucketSensorCRUD:
    async def test_create_sensor_reading(self, client, tenant):
        _, bucket_id = await _setup_bucket(client, tenant)
        resp = await client.post(
            "/v1/sensors",
            json={"bucket_id": bucket_id, "ph": 6.2, "ec": 1.4, "water_temp_f": 68.5},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["ph"] == 6.2
        assert data["ec"] == 1.4
        assert data["water_temp_f"] == 68.5
        assert "recorded_at" in data

    async def test_list_sensor_readings(self, client, tenant):
        _, bucket_id = await _setup_bucket(client, tenant)
        await client.post(
            "/v1/sensors",
            json={"bucket_id": bucket_id, "ph": 6.0},
            headers=tenant["headers"],
        )
        await client.post(
            "/v1/sensors",
            json={"bucket_id": bucket_id, "ph": 6.5},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/sensors?bucket_id={bucket_id}", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    async def test_list_sensor_readings_limit(self, client, tenant):
        _, bucket_id = await _setup_bucket(client, tenant)
        for i in range(5):
            await client.post(
                "/v1/sensors",
                json={"bucket_id": bucket_id, "ph": 6.0 + i * 0.1},
                headers=tenant["headers"],
            )
        resp = await client.get(f"/v1/sensors?bucket_id={bucket_id}&limit=2", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_latest_sensor_reading(self, client, tenant):
        _, bucket_id = await _setup_bucket(client, tenant)
        await client.post(
            "/v1/sensors",
            json={"bucket_id": bucket_id, "ph": 5.8},
            headers=tenant["headers"],
        )
        await client.post(
            "/v1/sensors",
            json={"bucket_id": bucket_id, "ph": 6.3},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/sensors/latest/{bucket_id}", headers=tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["ph"] == 6.3

    async def test_drift_analysis(self, client, tenant):
        _, bucket_id = await _setup_bucket(client, tenant)
        for ph in [6.0, 6.1, 6.2, 6.3, 6.4]:
            await client.post(
                "/v1/sensors",
                json={"bucket_id": bucket_id, "ph": ph},
                headers=tenant["headers"],
            )
        resp = await client.get(f"/v1/sensors/drift/{bucket_id}?hours=24", headers=tenant["headers"])
        assert resp.status_code == 200


# ---------- Tent Sensors ----------


class TestTentSensorCRUD:
    async def test_create_tent_reading(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "Tent"}, headers=tenant["headers"])
        tent_id = t.json()["id"]
        resp = await client.post(
            "/v1/tent-sensors",
            json={"tent_id": tent_id, "ambient_temp_f": 75.2, "ambient_humidity": 55.0},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["ambient_temp_f"] == 75.2
        assert data["ambient_humidity"] == 55.0

    async def test_list_tent_readings(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "Tent"}, headers=tenant["headers"])
        tent_id = t.json()["id"]
        await client.post(
            "/v1/tent-sensors",
            json={"tent_id": tent_id, "ambient_temp_f": 74.0},
            headers=tenant["headers"],
        )
        await client.post(
            "/v1/tent-sensors",
            json={"tent_id": tent_id, "ambient_temp_f": 76.0},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/tent-sensors?tent_id={tent_id}", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    async def test_latest_tent_reading(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "Tent"}, headers=tenant["headers"])
        tent_id = t.json()["id"]
        await client.post(
            "/v1/tent-sensors",
            json={"tent_id": tent_id, "ambient_temp_f": 70.0},
            headers=tenant["headers"],
        )
        await client.post(
            "/v1/tent-sensors",
            json={"tent_id": tent_id, "ambient_temp_f": 78.0},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/tent-sensors/latest/{tent_id}", headers=tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["ambient_temp_f"] == 78.0

    async def test_tent_sensor_trends(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "Tent"}, headers=tenant["headers"])
        tent_id = t.json()["id"]
        for temp in [72.0, 73.5, 75.0, 76.5, 78.0]:
            await client.post(
                "/v1/tent-sensors",
                json={"tent_id": tent_id, "ambient_temp_f": temp, "ambient_humidity": 50.0},
                headers=tenant["headers"],
            )
        resp = await client.get(f"/v1/tent-sensors/trends/{tent_id}?hours=24", headers=tenant["headers"])
        assert resp.status_code == 200
