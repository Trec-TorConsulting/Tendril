"""Unit tests for Outdoor Container grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.outdoor_container import OUTDOOR_CONTAINER_CONFIG

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
    "outdoor_specific",
    "container_management",
    "total_grow_days",
]


class TestOutdoorContainerConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in OUTDOOR_CONTAINER_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in OUTDOOR_CONTAINER_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in OUTDOOR_CONTAINER_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in OUTDOOR_CONTAINER_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(OUTDOOR_CONTAINER_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in OUTDOOR_CONTAINER_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in OUTDOOR_CONTAINER_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in OUTDOOR_CONTAINER_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestOutdoorContainerManagement:
    """Verify container management section is comprehensive."""

    def test_has_all_subsections(self):
        cm = OUTDOOR_CONTAINER_CONFIG["container_management"]
        expected = [
            "container_selection",
            "root_zone_temperature",
            "watering_outdoor_containers",
            "mobility_advantage",
            "wind_management",
        ]
        for key in expected:
            assert key in cm, f"Missing container management subsection: {key}"

    def test_container_types_defined(self):
        cs = OUTDOOR_CONTAINER_CONFIG["container_management"]["container_selection"]
        assert "fabric_pots" in cs
        assert "plastic_pots" in cs
        for _pot_type, info in cs.items():
            assert "pros" in info
            assert "cons" in info

    def test_root_zone_temperature_management(self):
        rzt = OUTDOOR_CONTAINER_CONFIG["container_management"]["root_zone_temperature"]
        assert "heat_management" in rzt
        assert "cold_management" in rzt
        heat = rzt["heat_management"]
        assert "cooling_strategies" in heat
        assert len(heat["cooling_strategies"]) >= 3

    def test_watering_by_season(self):
        w = OUTDOOR_CONTAINER_CONFIG["container_management"]["watering_outdoor_containers"]
        assert "by_season" in w
        seasons = w["by_season"]
        assert "spring" in seasons
        assert "peak_summer" in seasons
        assert "fall" in seasons

    def test_mobility_use_cases(self):
        ma = OUTDOOR_CONTAINER_CONFIG["container_management"]["mobility_advantage"]
        assert "use_cases" in ma
        assert len(ma["use_cases"]) >= 5
        assert "weight_considerations" in ma

    def test_wind_management_solutions(self):
        wm = OUTDOOR_CONTAINER_CONFIG["container_management"]["wind_management"]
        assert "solutions" in wm
        assert "stability" in wm["solutions"]
        assert "wind_protection" in wm["solutions"]
