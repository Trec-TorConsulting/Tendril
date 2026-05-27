"""Unit tests for Vertical Tower grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.vertical_tower import VERTICAL_TOWER_CONFIG

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
    "vertical_tower_system",
    "total_grow_days",
]


class TestVerticalTowerConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in VERTICAL_TOWER_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in VERTICAL_TOWER_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in VERTICAL_TOWER_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in VERTICAL_TOWER_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(VERTICAL_TOWER_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in VERTICAL_TOWER_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in VERTICAL_TOWER_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in VERTICAL_TOWER_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestVerticalTowerSystem:
    """Verify vertical tower system section (core differentiator)."""

    def test_vertical_tower_system_exists(self):
        assert "vertical_tower_system" in VERTICAL_TOWER_CONFIG

    def test_has_core_subsections(self):
        vts = VERTICAL_TOWER_CONFIG["vertical_tower_system"]
        expected = ["tower_construction", "flow_dynamics", "lighting_strategy", "space_efficiency"]
        for key in expected:
            assert key in vts, f"Missing vertical_tower_system subsection: {key}"

    def test_tower_construction_has_content(self):
        tc = VERTICAL_TOWER_CONFIG["vertical_tower_system"]["tower_construction"]
        assert isinstance(tc, dict)
        assert len(tc) >= 2, "tower_construction should have multiple entries"

    def test_flow_dynamics_has_content(self):
        fd = VERTICAL_TOWER_CONFIG["vertical_tower_system"]["flow_dynamics"]
        assert isinstance(fd, dict)
        assert len(fd) >= 2, "flow_dynamics should have multiple entries"

    def test_lighting_strategy_has_content(self):
        ls = VERTICAL_TOWER_CONFIG["vertical_tower_system"]["lighting_strategy"]
        assert isinstance(ls, dict)
        assert len(ls) >= 2, "lighting_strategy should have multiple entries"
