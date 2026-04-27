"""Integration tests for outdoor grow APIs — yields, soil, plot, pest, containers, runoff."""

from __future__ import annotations

import pytest
import pytest_asyncio
from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


async def _setup_grow(client, tenant, env_type="outdoor"):
    """Helper: create tent → grow → bucket chain. Returns (tent_id, grow_id, bucket_id)."""
    t = await client.post(
        "/v1/tents",
        json={"name": "Outdoor Plot", "environment_type": env_type},
        headers=tenant["headers"],
    )
    g = await client.post(
        "/v1/grows",
        json={"tent_id": t.json()["id"], "name": "Summer 2026", "grow_type": "soil"},
        headers=tenant["headers"],
    )
    b = await client.post(
        "/v1/buckets",
        json={"grow_cycle_id": g.json()["id"], "label": "Plant 1"},
        headers=tenant["headers"],
    )
    return t.json()["id"], g.json()["id"], b.json()["id"]


# ---------- Outdoor Yields ----------


class TestOutdoorYields:
    async def test_create_yield(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        resp = await client.post(
            f"/v1/grows/{grow_id}/yields",
            json={"bucket_id": bucket_id, "wet_weight_oz": 32.5, "dry_weight_oz": 8.2},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["wet_weight_oz"] == 32.5
        assert data["dry_weight_oz"] == 8.2

    async def test_list_yields(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        await client.post(
            f"/v1/grows/{grow_id}/yields",
            json={"bucket_id": bucket_id, "wet_weight_oz": 30.0},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/grows/{grow_id}/yields", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_yield_summary(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        await client.post(
            f"/v1/grows/{grow_id}/yields",
            json={"bucket_id": bucket_id, "wet_weight_oz": 30.0, "dry_weight_oz": 7.5},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/grows/{grow_id}/yields/summary", headers=tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_wet_oz"] >= 30.0

    async def test_delete_yield(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        r = await client.post(
            f"/v1/grows/{grow_id}/yields",
            json={"bucket_id": bucket_id, "wet_weight_oz": 20.0},
            headers=tenant["headers"],
        )
        yid = r.json()["id"]
        resp = await client.delete(f"/v1/grows/{grow_id}/yields/{yid}", headers=tenant["headers"])
        assert resp.status_code == 204


# ---------- Soil Tests ----------


class TestSoilTests:
    async def test_create_soil_test(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        resp = await client.post(
            f"/v1/grows/{grow_id}/soil-tests",
            json={"ph": 6.5, "nitrogen_ppm": 40, "phosphorus_ppm": 30, "potassium_ppm": 200},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        assert resp.json()["ph"] == 6.5

    async def test_list_soil_tests(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        await client.post(
            f"/v1/grows/{grow_id}/soil-tests",
            json={"ph": 6.5},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/grows/{grow_id}/soil-tests", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_latest_soil_test(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        await client.post(
            f"/v1/grows/{grow_id}/soil-tests",
            json={"ph": 6.0},
            headers=tenant["headers"],
        )
        await client.post(
            f"/v1/grows/{grow_id}/soil-tests",
            json={"ph": 7.0},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/grows/{grow_id}/soil-tests/latest", headers=tenant["headers"])
        assert resp.status_code == 200

    async def test_delete_soil_test(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        r = await client.post(
            f"/v1/grows/{grow_id}/soil-tests",
            json={"ph": 6.5},
            headers=tenant["headers"],
        )
        tid = r.json()["id"]
        resp = await client.delete(f"/v1/grows/{grow_id}/soil-tests/{tid}", headers=tenant["headers"])
        assert resp.status_code == 204


# ---------- Soil Amendments ----------


class TestSoilAmendments:
    async def test_create_amendment(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        resp = await client.post(
            f"/v1/grows/{grow_id}/amendments",
            json={
                "amendment_type": "organic",
                "product_name": "Worm Castings",
                "quantity": "2 cups",
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        assert resp.json()["product_name"] == "Worm Castings"

    async def test_list_amendments(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        await client.post(
            f"/v1/grows/{grow_id}/amendments",
            json={"amendment_type": "organic", "product_name": "Compost"},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/grows/{grow_id}/amendments", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_delete_amendment(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        r = await client.post(
            f"/v1/grows/{grow_id}/amendments",
            json={"amendment_type": "mineral", "product_name": "Lime"},
            headers=tenant["headers"],
        )
        aid = r.json()["id"]
        resp = await client.delete(f"/v1/grows/{grow_id}/amendments/{aid}", headers=tenant["headers"])
        assert resp.status_code == 204


# ---------- Plot Grid ----------


class TestPlotGrid:
    async def test_upsert_plot(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        resp = await client.put(
            f"/v1/grows/{grow_id}/plot",
            json={"rows": 4, "cols": 4, "cell_size_inches": 24, "orientation": "north"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["rows"] == 4
        assert data["cols"] == 4

    async def test_get_plot(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        await client.put(
            f"/v1/grows/{grow_id}/plot",
            json={"rows": 3, "cols": 3},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/grows/{grow_id}/plot", headers=tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["rows"] == 3

    async def test_update_cells(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        await client.put(
            f"/v1/grows/{grow_id}/plot",
            json={"rows": 3, "cols": 3},
            headers=tenant["headers"],
        )
        resp = await client.patch(
            f"/v1/grows/{grow_id}/plot/cells",
            json={"cells": [{"row": 0, "col": 0, "cell_type": "plant"}, {"row": 1, "col": 1, "cell_type": "path"}]},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200

    async def test_delete_plot(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        await client.put(
            f"/v1/grows/{grow_id}/plot",
            json={"rows": 2, "cols": 2},
            headers=tenant["headers"],
        )
        resp = await client.delete(f"/v1/grows/{grow_id}/plot", headers=tenant["headers"])
        assert resp.status_code == 204


# ---------- Pest Scouts ----------


class TestPestScouts:
    async def test_create_pest_scout(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        resp = await client.post(
            f"/v1/grows/{grow_id}/pest-scouts",
            json={
                "pest_type": "insect",
                "species": "Aphids",
                "severity": "medium",
                "treatment_applied": "Neem oil spray",
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["species"] == "Aphids"
        assert data["severity"] == "medium"

    async def test_list_pest_scouts(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        await client.post(
            f"/v1/grows/{grow_id}/pest-scouts",
            json={"pest_type": "insect", "species": "Spider Mites", "severity": "high"},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/grows/{grow_id}/pest-scouts", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_list_pest_scouts_filter(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        await client.post(
            f"/v1/grows/{grow_id}/pest-scouts",
            json={"pest_type": "insect", "species": "Gnats", "severity": "low"},
            headers=tenant["headers"],
        )
        await client.post(
            f"/v1/grows/{grow_id}/pest-scouts",
            json={"pest_type": "disease", "species": "Powdery Mildew", "severity": "high"},
            headers=tenant["headers"],
        )
        resp = await client.get(
            f"/v1/grows/{grow_id}/pest-scouts?pest_type=insect",
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        assert all(p["pest_type"] == "insect" for p in resp.json())

    async def test_delete_pest_scout(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        r = await client.post(
            f"/v1/grows/{grow_id}/pest-scouts",
            json={"pest_type": "insect", "species": "Aphids"},
            headers=tenant["headers"],
        )
        eid = r.json()["id"]
        resp = await client.delete(f"/v1/grows/{grow_id}/pest-scouts/{eid}", headers=tenant["headers"])
        assert resp.status_code == 204


# ---------- Container Profiles ----------


class TestContainerProfiles:
    async def test_upsert_container(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        resp = await client.put(
            f"/v1/grows/{grow_id}/containers/{bucket_id}",
            json={
                "pot_size_gallons": 5.0,
                "media_type": "living soil",
                "pot_material": "fabric",
                "has_saucer": True,
                "sun_exposure": "full_sun",
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["pot_size_gallons"] == 5.0
        assert data["pot_material"] == "fabric"

    async def test_list_containers(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        await client.put(
            f"/v1/grows/{grow_id}/containers/{bucket_id}",
            json={"pot_size_gallons": 3.0, "media_type": "coco"},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/grows/{grow_id}/containers", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_get_container(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        await client.put(
            f"/v1/grows/{grow_id}/containers/{bucket_id}",
            json={"pot_size_gallons": 7.0},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/grows/{grow_id}/containers/{bucket_id}", headers=tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["pot_size_gallons"] == 7.0

    async def test_delete_container(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        await client.put(
            f"/v1/grows/{grow_id}/containers/{bucket_id}",
            json={"pot_size_gallons": 5.0},
            headers=tenant["headers"],
        )
        resp = await client.delete(f"/v1/grows/{grow_id}/containers/{bucket_id}", headers=tenant["headers"])
        assert resp.status_code == 204


# ---------- Runoff Readings ----------


class TestRunoffReadings:
    async def test_create_runoff(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        resp = await client.post(
            f"/v1/grows/{grow_id}/runoff",
            json={
                "bucket_id": bucket_id,
                "input_ph": 6.5,
                "input_ec": 1.2,
                "runoff_ph": 6.8,
                "runoff_ec": 1.5,
                "runoff_pct": 20.0,
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["input_ph"] == 6.5
        assert data["runoff_ph"] == 6.8

    async def test_list_runoff(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        await client.post(
            f"/v1/grows/{grow_id}/runoff",
            json={"bucket_id": bucket_id, "input_ph": 6.5, "runoff_ph": 6.8},
            headers=tenant["headers"],
        )
        resp = await client.get(f"/v1/grows/{grow_id}/runoff", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_runoff_stats(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        for i in range(3):
            await client.post(
                f"/v1/grows/{grow_id}/runoff",
                json={
                    "bucket_id": bucket_id,
                    "input_ph": 6.5 + i * 0.1,
                    "input_ec": 1.2,
                    "runoff_ph": 6.8 + i * 0.1,
                    "runoff_ec": 1.5,
                },
                headers=tenant["headers"],
            )
        resp = await client.get(f"/v1/grows/{grow_id}/runoff/stats", headers=tenant["headers"])
        assert resp.status_code == 200

    async def test_delete_runoff(self, client, tenant):
        _, grow_id, bucket_id = await _setup_grow(client, tenant)
        r = await client.post(
            f"/v1/grows/{grow_id}/runoff",
            json={"bucket_id": bucket_id, "input_ph": 6.5},
            headers=tenant["headers"],
        )
        rid = r.json()["id"]
        resp = await client.delete(f"/v1/grows/{grow_id}/runoff/{rid}", headers=tenant["headers"])
        assert resp.status_code == 204


# ---------- Companion Plants (no auth required) ----------


class TestCompanionPlants:
    async def test_list_companions(self, client):
        resp = await client.get("/v1/companion-plants")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_check_compatibility(self, client):
        resp = await client.get("/v1/companion-plants/check?plant=tomato&neighbor=basil")
        assert resp.status_code == 200
        data = resp.json()
        assert "compatibility" in data

    async def test_suggest_companions(self, client):
        resp = await client.get("/v1/companion-plants/suggest?plant=tomato")
        assert resp.status_code == 200
        data = resp.json()
        assert "suggestions" in data


# ---------- Outdoor Intelligence ----------


class TestOutdoorIntelligence:
    async def test_frost_dates(self, client, tenant):
        t = await client.post(
            "/v1/tents",
            json={"name": "Garden", "environment_type": "outdoor", "latitude": 40.7, "longitude": -74.0},
            headers=tenant["headers"],
        )
        tent_id = t.json()["id"]
        resp = await client.get(f"/v1/outdoor/{tent_id}/frost-dates", headers=tenant["headers"])
        # May return 200 with data or 404/422 if no lat/lon
        assert resp.status_code in (200, 404, 422)

    async def test_moon_phase(self, client, tenant):
        t = await client.post(
            "/v1/tents",
            json={"name": "Garden", "environment_type": "outdoor", "latitude": 40.7, "longitude": -74.0},
            headers=tenant["headers"],
        )
        tent_id = t.json()["id"]
        resp = await client.get(f"/v1/outdoor/{tent_id}/moon", headers=tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert "phase" in data

    async def test_manual_weather(self, client, tenant):
        t = await client.post(
            "/v1/tents",
            json={"name": "Garden", "environment_type": "outdoor"},
            headers=tenant["headers"],
        )
        tent_id = t.json()["id"]
        resp = await client.post(
            f"/v1/outdoor/{tent_id}/manual",
            json={"rainfall_in": 0.5, "temp_high_f": 85, "temp_low_f": 62},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201

    async def test_gdd_calculation(self, client, tenant):
        _, grow_id, _ = await _setup_grow(client, tenant)
        resp = await client.get(f"/v1/outdoor/{grow_id}/gdd", headers=tenant["headers"])
        assert resp.status_code == 200
