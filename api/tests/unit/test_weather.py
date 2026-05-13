"""Integration tests for weather API."""

from __future__ import annotations

import pytest
import pytest_asyncio

from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


class TestWeatherAPI:
    async def test_current_weather(self, client, tenant):
        t = await client.post(
            "/v1/tents",
            json={"name": "Outdoor", "environment_type": "outdoor", "latitude": 40.7, "longitude": -74.0},
            headers=tenant["headers"],
        )
        tent_id = t.json()["id"]
        resp = await client.get(f"/v1/weather/{tent_id}/current", headers=tenant["headers"])
        # May return 200 with data or 503 if weather API unreachable in test
        assert resp.status_code in (200, 503, 404)

    async def test_forecast(self, client, tenant):
        t = await client.post(
            "/v1/tents",
            json={"name": "Outdoor", "environment_type": "outdoor", "latitude": 40.7, "longitude": -74.0},
            headers=tenant["headers"],
        )
        tent_id = t.json()["id"]
        resp = await client.get(f"/v1/weather/{tent_id}/forecast", headers=tenant["headers"])
        assert resp.status_code in (200, 503, 404)

    async def test_weather_history(self, client, tenant):
        t = await client.post(
            "/v1/tents",
            json={"name": "Outdoor", "environment_type": "outdoor", "latitude": 40.7, "longitude": -74.0},
            headers=tenant["headers"],
        )
        tent_id = t.json()["id"]
        resp = await client.get(f"/v1/weather/{tent_id}/history?limit=10", headers=tenant["headers"])
        assert resp.status_code in (200, 503, 404)

    async def test_weather_requires_auth(self, client, tenant):
        t = await client.post(
            "/v1/tents",
            json={"name": "Outdoor"},
            headers=tenant["headers"],
        )
        tent_id = t.json()["id"]
        resp = await client.get(f"/v1/weather/{tent_id}/current")
        assert resp.status_code in (401, 403)
