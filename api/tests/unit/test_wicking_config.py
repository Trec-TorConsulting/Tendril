"""Unit tests for Wicking grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.wicking import WICKING_CONFIG

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
    "capillary_system",
    "total_grow_days",
]


class TestWickingConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in WICKING_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in WICKING_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in WICKING_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in WICKING_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(WICKING_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in WICKING_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in WICKING_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in WICKING_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestWickingCapillarySystem:
    """Verify capillary system section (core differentiator for wicking)."""

    def test_capillary_system_exists(self):
        assert "capillary_system" in WICKING_CONFIG

    def test_has_core_subsections(self):
        cs = WICKING_CONFIG["capillary_system"]
        expected = ["bed_construction", "capillary_science", "reservoir_management"]
        for key in expected:
            assert key in cs, f"Missing capillary_system subsection: {key}"

    def test_capillary_science_has_content(self):
        cs = WICKING_CONFIG["capillary_system"]["capillary_science"]
        assert isinstance(cs, dict)
        assert len(cs) >= 2, "capillary_science should have multiple entries"

    def test_bed_construction_has_content(self):
        bc = WICKING_CONFIG["capillary_system"]["bed_construction"]
        assert isinstance(bc, dict)
        assert len(bc) >= 2, "bed_construction should have multiple entries"

    def test_reservoir_management_has_content(self):
        rm = WICKING_CONFIG["capillary_system"]["reservoir_management"]
        assert isinstance(rm, dict)
        assert len(rm) >= 2, "reservoir_management should have multiple entries"
