"""Integration tests for weather API + unit tests for the weather service layer."""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio

from app.weather import service as weather_service
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

    async def test_current_rejects_indoor_tent(self, client, tenant):
        t = await client.post(
            "/v1/tents",
            json={"name": "Indoor", "environment_type": "indoor"},
            headers=tenant["headers"],
        )
        tent_id = t.json()["id"]
        resp = await client.get(f"/v1/weather/{tent_id}/current", headers=tenant["headers"])
        assert resp.status_code == 400
        assert "outdoor" in resp.json()["detail"].lower()

    async def test_current_rejects_tent_without_coordinates(self, client, tenant):
        t = await client.post(
            "/v1/tents",
            json={"name": "Outdoor-noloc", "environment_type": "outdoor"},
            headers=tenant["headers"],
        )
        tent_id = t.json()["id"]
        resp = await client.get(f"/v1/weather/{tent_id}/current", headers=tenant["headers"])
        assert resp.status_code == 400
        assert "lat" in resp.json()["detail"].lower()

    async def test_current_404_for_unknown_tent(self, client, tenant):
        resp = await client.get(f"/v1/weather/{uuid4()}/current", headers=tenant["headers"])
        assert resp.status_code == 404


class TestWeatherService:
    """Direct unit coverage for ``app.weather.service``."""

    async def test_get_tent_returns_none_for_missing(self, db_session):
        assert await weather_service.get_tent(db_session, uuid4()) is None

    async def test_get_weather_capable_tent_returns_none_for_missing(self, db_session):
        assert await weather_service.get_weather_capable_tent(db_session, uuid4()) is None

    async def test_get_weather_capable_tent_rejects_indoor(self, db_session, client, tenant):
        resp = await client.post(
            "/v1/tents",
            json={"name": "Indoor", "environment_type": "indoor"},
            headers=tenant["headers"],
        )
        tent_id = resp.json()["id"]
        with pytest.raises(weather_service.WeatherUnavailableError) as exc:
            await weather_service.get_weather_capable_tent(db_session, tent_id)
        assert "outdoor" in exc.value.reason.lower()

    async def test_get_weather_capable_tent_rejects_no_coords(self, db_session, client, tenant):
        resp = await client.post(
            "/v1/tents",
            json={"name": "Outdoor-noloc", "environment_type": "outdoor"},
            headers=tenant["headers"],
        )
        tent_id = resp.json()["id"]
        with pytest.raises(weather_service.WeatherUnavailableError) as exc:
            await weather_service.get_weather_capable_tent(db_session, tent_id)
        assert "lat" in exc.value.reason.lower()

    async def test_get_weather_capable_tent_success_narrows_coords(self, db_session, client, tenant):
        resp = await client.post(
            "/v1/tents",
            json={
                "name": "Outdoor-loc",
                "environment_type": "outdoor",
                "latitude": 40.7,
                "longitude": -74.0,
            },
            headers=tenant["headers"],
        )
        tent_id = resp.json()["id"]
        capable = await weather_service.get_weather_capable_tent(db_session, tent_id)
        assert capable is not None
        assert capable.latitude == 40.7
        assert capable.longitude == -74.0
        assert capable.tent.environment_type == "outdoor"

    async def test_list_weather_history_empty(self, db_session):
        readings = await weather_service.list_weather_history(db_session, tent_id=uuid4(), limit=10)
        assert readings == []
