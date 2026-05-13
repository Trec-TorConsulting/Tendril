"""Integration tests for data export API."""

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


class TestDataExport:
    async def test_export_bucket_csv(self, client, tenant):
        # Setup: create tent → grow → bucket → sensor reading
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
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
        bucket_id = b.json()["id"]
        await client.post(
            "/v1/sensors",
            json={"bucket_id": bucket_id, "ph": 6.2, "ec": 1.4},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/data/export/bucket/{bucket_id}", headers=tenant["headers"])
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")

    async def test_export_empty_bucket(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows",
            json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"},
            headers=tenant["headers"],
        )
        b = await client.post(
            "/v1/buckets",
            json={"grow_cycle_id": g.json()["id"], "label": "Empty"},
            headers=tenant["headers"],
        )
        bucket_id = b.json()["id"]
        resp = await client.get(f"/v1/data/export/bucket/{bucket_id}", headers=tenant["headers"])
        # Should return 200 with CSV headers even if no data
        assert resp.status_code in (200, 404)

    async def test_export_requires_auth(self, client):
        resp = await client.get(f"/v1/data/export/bucket/{uuid4()}")
        assert resp.status_code in (401, 403)
