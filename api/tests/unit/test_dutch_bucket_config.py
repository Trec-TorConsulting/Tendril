"""Unit tests for Dutch Bucket grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.dutch_bucket import DUTCH_BUCKET_CONFIG

REQUIRED_STAGE_IDS = [
    "germination",
    "seedling",
    "early_veg",
    "late_veg",
    "transition",
    "early_flower",
    "mid_flower",
    "late_flower",
    "flush",
    "harvest",
    "drying",
    "curing",
]

REQUIRED_STAGE_FIELDS = [
    "id",
    "name",
    "order",
    "duration_days",
    "description",
    "environment",
    "nutrients",
    "tasks",
    "health_checks",
    "common_problems",
    "transition_signals",
]

REQUIRED_TOP_LEVEL_KEYS = [
    "grow_type_id",
    "version",
    "stages",
    "equipment",
    "quick_reference",
    "troubleshooting",
    "dutch_bucket_system",
    "total_grow_days",
]


class TestDutchBucketConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in DUTCH_BUCKET_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in DUTCH_BUCKET_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in DUTCH_BUCKET_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in DUTCH_BUCKET_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(DUTCH_BUCKET_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in DUTCH_BUCKET_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in DUTCH_BUCKET_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in DUTCH_BUCKET_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestDutchBucketSystem:
    """Verify dutch bucket system section (core differentiator)."""

    def test_dutch_bucket_system_exists(self):
        assert "dutch_bucket_system" in DUTCH_BUCKET_CONFIG

    def test_has_core_subsections(self):
        dbs = DUTCH_BUCKET_CONFIG["dutch_bucket_system"]
        expected = ["bucket_design", "drain_line_engineering", "top_feed_configuration", "scalability"]
        for key in expected:
            assert key in dbs, f"Missing dutch_bucket_system subsection: {key}"

    def test_bucket_design_has_content(self):
        bd = DUTCH_BUCKET_CONFIG["dutch_bucket_system"]["bucket_design"]
        assert isinstance(bd, dict)
        assert len(bd) >= 2, "bucket_design should have multiple entries"

    def test_drain_line_engineering_has_content(self):
        dl = DUTCH_BUCKET_CONFIG["dutch_bucket_system"]["drain_line_engineering"]
        assert isinstance(dl, dict)
        assert len(dl) >= 2, "drain_line_engineering should have multiple entries"

    def test_scalability_has_content(self):
        sc = DUTCH_BUCKET_CONFIG["dutch_bucket_system"]["scalability"]
        assert isinstance(sc, dict)
        assert len(sc) >= 2, "scalability should have multiple entries"
