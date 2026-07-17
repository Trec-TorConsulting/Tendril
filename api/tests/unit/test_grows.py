"""Integration tests for Phase 3 grow APIs — tents, grows, buckets, sensors, strains, yields."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
import pytest_asyncio

from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


# ---------- Tents ----------


class TestTentCRUD:
    async def test_create_tent(self, client, tenant):
        resp = await client.post(
            "/v1/tents",
            json={"name": "Main Tent", "environment_type": "indoor"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Main Tent"
        assert data["environment_type"] == "indoor"

    async def test_list_tents(self, client, tenant):
        await client.post("/v1/tents", json={"name": "T1"}, headers=tenant["headers"])
        await client.post("/v1/tents", json={"name": "T2"}, headers=tenant["headers"])
        resp = await client.get("/v1/tents", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 2

    async def test_update_tent(self, client, tenant):
        r = await client.post("/v1/tents", json={"name": "Old"}, headers=tenant["headers"])
        tid = r.json()["id"]
        resp = await client.patch(f"/v1/tents/{tid}", json={"name": "New"}, headers=tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["name"] == "New"

    async def test_delete_tent(self, client, tenant):
        r = await client.post("/v1/tents", json={"name": "ToDelete"}, headers=tenant["headers"])
        tid = r.json()["id"]
        resp = await client.delete(f"/v1/tents/{tid}", headers=tenant["headers"])
        assert resp.status_code == 204

    async def test_tent_not_found(self, client, tenant):
        resp = await client.get(f"/v1/tents/{uuid4()}", headers=tenant["headers"])
        assert resp.status_code == 404


# ---------- Grow Cycles ----------


class TestGrowCRUD:
    async def test_create_grow(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "Tent"}, headers=tenant["headers"])
        tid = t.json()["id"]
        resp = await client.post(
            "/v1/grows",
            json={"tent_id": tid, "name": "Spring 2025", "grow_type": "dwc"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Spring 2025"
        assert data["status"] == "active"
        assert data["stage"] == "seedling"

    async def test_list_grows_filter_status(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        tid = t.json()["id"]
        await client.post(
            "/v1/grows", json={"tent_id": tid, "name": "G1", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        resp = await client.get("/v1/grows?status=active", headers=tenant["headers"])
        assert resp.status_code == 200
        assert all(g["status"] == "active" for g in resp.json()["items"])

    async def test_complete_grow_sets_ended_at(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "nft"}, headers=tenant["headers"]
        )
        gid = g.json()["id"]
        resp = await client.patch(f"/v1/grows/{gid}", json={"status": "completed"}, headers=tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["ended_at"] is not None

    async def test_delete_grow(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "soil"}, headers=tenant["headers"]
        )
        resp = await client.delete(f"/v1/grows/{g.json()['id']}", headers=tenant["headers"])
        assert resp.status_code == 204

    async def test_update_grow_type(self, client, tenant):
        tent = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        grow = await client.post(
            "/v1/grows",
            json={"tent_id": tent.json()["id"], "name": "G", "grow_type": "aquaponics"},
            headers=tenant["headers"],
        )
        grow_id = grow.json()["id"]

        resp = await client.patch(
            f"/v1/grows/{grow_id}",
            json={"grow_type": "dwc"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        assert resp.json()["grow_type"] == "dwc"

    async def test_update_grow_type_rejects_unknown_type(self, client, tenant):
        tent = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        grow = await client.post(
            "/v1/grows",
            json={"tent_id": tent.json()["id"], "name": "G", "grow_type": "dwc"},
            headers=tenant["headers"],
        )
        grow_id = grow.json()["id"]

        resp = await client.patch(
            f"/v1/grows/{grow_id}",
            json={"grow_type": "not_a_real_type"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 400
        assert "Unknown grow type" in resp.json()["detail"]

    async def test_grow_type_change_purges_stale_auto_tasks(self, client, tenant, db_session):
        """Correcting grow_type deletes stale pending auto tasks (e.g. aquaponics
        'fish' tasks) while preserving completed task history."""
        from app.commercial.models import Task

        tent = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        grow = await client.post(
            "/v1/grows",
            json={"tent_id": tent.json()["id"], "name": "G", "grow_type": "aquaponics"},
            headers=tenant["headers"],
        )
        grow_id = grow.json()["id"]

        # Simulate scheduler-generated aquaponics tasks for this grow.
        db_session.add_all(
            [
                Task(
                    tenant_id=tenant["tenant"].id,
                    title="Feed fish",
                    status="pending",
                    source="auto",
                    category="fish_feed",
                    created_by=tenant["user"].id,
                    grow_cycle_id=UUID(grow_id),
                ),
                Task(
                    tenant_id=tenant["tenant"].id,
                    title="Observe fish health",
                    status="completed",
                    source="auto",
                    category="fish_health_check",
                    created_by=tenant["user"].id,
                    grow_cycle_id=UUID(grow_id),
                ),
            ]
        )
        await db_session.commit()

        resp = await client.patch(
            f"/v1/grows/{grow_id}",
            json={"grow_type": "dwc"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200

        async def total(category: str, status: str) -> int:
            r = await client.get(
                f"/v1/tasks?grow_cycle_id={grow_id}&category={category}&status={status}",
                headers=tenant["headers"],
            )
            assert r.status_code == 200
            return r.json()["total"]

        # Stale pending fish task removed; completed history preserved.
        assert await total("fish_feed", "pending") == 0
        assert await total("fish_health_check", "completed") == 1


# ---------- Buckets ----------


class TestBucketCRUD:
    async def test_create_bucket(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        resp = await client.post(
            "/v1/buckets",
            json={"grow_cycle_id": g.json()["id"], "label": "B1", "strain_name": "Blue Dream"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["label"] == "B1"
        assert data["strain_name"] == "Blue Dream"

    async def test_list_buckets_by_grow(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        gid = g.json()["id"]
        await client.post("/v1/buckets", json={"grow_cycle_id": gid, "label": "B1"}, headers=tenant["headers"])
        await client.post("/v1/buckets", json={"grow_cycle_id": gid, "label": "B2"}, headers=tenant["headers"])
        resp = await client.get(f"/v1/buckets?grow_cycle_id={gid}", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 2


# ---------- Sensor Readings ----------


class TestSensorReadings:
    async def test_create_reading(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        b = await client.post("/v1/buckets", json={"grow_cycle_id": g.json()["id"]}, headers=tenant["headers"])
        bid = b.json()["id"]
        resp = await client.post(
            "/v1/sensors",
            json={"bucket_id": bid, "ph": 6.2, "ec": 1.4, "water_temp_f": 68.5},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["ph"] == 6.2
        assert data["ec"] == 1.4

    async def test_latest_reading(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        b = await client.post("/v1/buckets", json={"grow_cycle_id": g.json()["id"]}, headers=tenant["headers"])
        bid = b.json()["id"]
        await client.post("/v1/sensors", json={"bucket_id": bid, "ph": 5.8}, headers=tenant["headers"])
        await client.post("/v1/sensors", json={"bucket_id": bid, "ph": 6.5}, headers=tenant["headers"])
        resp = await client.get(f"/v1/sensors/latest/{bid}", headers=tenant["headers"])
        assert resp.status_code == 200
        # Latest should be the most recent reading
        assert resp.json()["ph"] == 6.5

    async def test_drift_analysis(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        b = await client.post("/v1/buckets", json={"grow_cycle_id": g.json()["id"]}, headers=tenant["headers"])
        bid = b.json()["id"]
        await client.post("/v1/sensors", json={"bucket_id": bid, "ph": 6.0, "ec": 1.2}, headers=tenant["headers"])
        await client.post("/v1/sensors", json={"bucket_id": bid, "ph": 6.3, "ec": 1.5}, headers=tenant["headers"])
        resp = await client.get(f"/v1/sensors/drift/{bid}?hours=24", headers=tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["ph"] is not None
        assert data["ph"]["delta"] == pytest.approx(0.3, abs=0.01)


# ---------- Strains ----------


class TestStrainCRUD:
    async def test_create_strain(self, client, tenant):
        resp = await client.post(
            "/v1/strains",
            json={"name": "Blue Dream", "breeder": "DJ Short", "genetics": "Blueberry x Haze"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "Blue Dream"

    async def test_list_strains(self, client, tenant):
        await client.post("/v1/strains", json={"name": "S1"}, headers=tenant["headers"])
        await client.post("/v1/strains", json={"name": "S2"}, headers=tenant["headers"])
        resp = await client.get("/v1/strains", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 2

    async def test_delete_strain(self, client, tenant):
        r = await client.post("/v1/strains", json={"name": "ToDelete"}, headers=tenant["headers"])
        resp = await client.delete(f"/v1/strains/{r.json()['id']}", headers=tenant["headers"])
        assert resp.status_code == 204


# ---------- Yields ----------


class TestYieldCRUD:
    async def test_create_yield(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        b = await client.post("/v1/buckets", json={"grow_cycle_id": g.json()["id"]}, headers=tenant["headers"])
        resp = await client.post(
            "/v1/yields",
            json={"bucket_id": b.json()["id"], "wet_weight_g": 150.0, "dry_weight_g": 35.0, "quality_rating": 8},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["wet_weight_g"] == 150.0
        assert data["quality_rating"] == 8


# ---------- Grow Types ----------


class TestGrowTypes:
    async def test_list_grow_types(self, client, tenant):
        resp = await client.get("/v1/grow-types", headers=tenant["headers"])
        assert resp.status_code == 200
        types = resp.json()
        assert len(types) == 17
        names = [t["name"] for t in types]
        assert "DWC (Deep Water Culture)" in names

    async def test_get_grow_type_detail(self, client, tenant):
        resp = await client.get("/v1/grow-types/dwc", headers=tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        # The DB model uses UUID for `id`; `slug` is the stable string handle
        # used in URLs and as the foreign key in tenant-scoped settings.
        assert data["slug"] == "dwc"
        assert "sensor_kit" in data
        assert "health_check_questions" in data

    async def test_grow_type_not_found(self, client, tenant):
        resp = await client.get("/v1/grow-types/nonexistent", headers=tenant["headers"])
        assert resp.status_code == 404


# ---------- Journal + Photos ----------


class TestJournalAndPhotos:
    async def test_create_journal_entry(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        b = await client.post("/v1/buckets", json={"grow_cycle_id": g.json()["id"]}, headers=tenant["headers"])
        resp = await client.post(
            "/v1/journal",
            json={"bucket_id": b.json()["id"], "event_type": "feeding", "content": "Fed 5ml CalMag"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        assert resp.json()["event_type"] == "feeding"

    async def test_create_photo(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        b = await client.post("/v1/buckets", json={"grow_cycle_id": g.json()["id"]}, headers=tenant["headers"])
        resp = await client.post(
            "/v1/photos",
            json={"bucket_id": b.json()["id"], "url": "https://example.com/photo.jpg", "caption": "Day 14"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        assert resp.json()["caption"] == "Day 14"


# ---------- Feeding / Doses ----------


class TestFeedingAndDoses:
    async def test_create_dose_profile(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        resp = await client.post(
            "/v1/feeding/doses",
            json={"grow_cycle_id": g.json()["id"], "name": "CalMag", "dose_type": "supplement", "dose_ml": 5.0},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "CalMag"

    async def test_create_feeding_schedule(self, client, tenant):
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        resp = await client.post(
            "/v1/feeding/feeding",
            json={
                "grow_cycle_id": g.json()["id"],
                "name": "Veg Week 2",
                "stage": "vegetative",
                "nutrients": [{"name": "Micro", "ml_per_gal": 5}, {"name": "Grow", "ml_per_gal": 5}],
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        assert resp.json()["stage"] == "vegetative"


# ---------- Quick Log ----------


class TestQuickLogWaterChange:
    """Tests for the water change quick-log endpoint and journal interaction."""

    async def test_water_change_creates_reading_and_journal(self, client, tenant):
        """Water change endpoint creates both a sensor reading and a journal entry."""
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        b = await client.post(
            "/v1/buckets", json={"grow_cycle_id": g.json()["id"], "label": "B1"}, headers=tenant["headers"]
        )
        bid = b.json()["id"]

        resp = await client.post(
            "/v1/quick-log/water-change",
            json={"bucket_ids": [bid], "ph": 6.0, "ec": 1.2, "volume_gal": 5.0, "notes": "Full flush"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["created"] == 1
        assert bid in data["bucket_ids"]

        # Verify journal entry was created with event_type water_change
        journal_resp = await client.get(f"/v1/journal?bucket_id={bid}", headers=tenant["headers"])
        assert journal_resp.status_code == 200
        entries = journal_resp.json()["items"]
        water_entries = [e for e in entries if e["event_type"] == "water_change"]
        assert len(water_entries) == 1
        assert water_entries[0]["content"] == "Full flush"
        assert water_entries[0]["payload"]["volume_gal"] == 5.0

    async def test_water_change_ec_ppm_auto_derive(self, client, tenant):
        """EC-only input auto-derives PPM in the sensor reading."""
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        b = await client.post("/v1/buckets", json={"grow_cycle_id": g.json()["id"]}, headers=tenant["headers"])
        bid = b.json()["id"]

        resp = await client.post(
            "/v1/quick-log/water-change",
            json={"bucket_ids": [bid], "ec": 2.0},
            headers=tenant["headers"],
        )
        assert resp.status_code == 201

        # Verify sensor reading has derived PPM
        readings_resp = await client.get(f"/v1/sensors?bucket_id={bid}", headers=tenant["headers"])
        assert readings_resp.status_code == 200
        items = readings_resp.json()["items"]
        assert len(items) >= 1
        assert items[0]["ppm"] == 1000.0  # 2.0 * 500

    async def test_water_change_bucket_not_found(self, client, tenant):
        resp = await client.post(
            "/v1/quick-log/water-change",
            json={"bucket_ids": [str(uuid4())], "ph": 6.0},
            headers=tenant["headers"],
        )
        assert resp.status_code == 404

    async def test_last_water_change_from_journal(self, client, tenant):
        """Multiple water changes — last one is the most recent by created_at."""
        t = await client.post("/v1/tents", json={"name": "T"}, headers=tenant["headers"])
        g = await client.post(
            "/v1/grows", json={"tent_id": t.json()["id"], "name": "G", "grow_type": "dwc"}, headers=tenant["headers"]
        )
        b = await client.post("/v1/buckets", json={"grow_cycle_id": g.json()["id"]}, headers=tenant["headers"])
        bid = b.json()["id"]

        # First water change
        await client.post(
            "/v1/quick-log/water-change",
            json={"bucket_ids": [bid], "ph": 5.8, "notes": "First"},
            headers=tenant["headers"],
        )
        # Second water change
        await client.post(
            "/v1/quick-log/water-change",
            json={"bucket_ids": [bid], "ph": 6.2, "notes": "Second"},
            headers=tenant["headers"],
        )

        # Get journal entries and verify last water change
        journal_resp = await client.get(f"/v1/journal?bucket_id={bid}", headers=tenant["headers"])
        entries = journal_resp.json()["items"]
        water_entries = [e for e in entries if e["event_type"] == "water_change"]
        assert len(water_entries) == 2
        # Most recent should be "Second" (sorted by created_at desc by default)
        latest = max(water_entries, key=lambda e: e["created_at"])
        assert latest["content"] == "Second"
