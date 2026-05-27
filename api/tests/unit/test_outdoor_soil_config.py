"""Unit tests for Outdoor Soil grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.outdoor_soil import OUTDOOR_SOIL_CONFIG

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
    "soil_specific",
    "outdoor_specific",
    "outdoor_environment",
    "total_grow_days",
]


class TestOutdoorSoilConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in OUTDOOR_SOIL_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in OUTDOOR_SOIL_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in OUTDOOR_SOIL_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in OUTDOOR_SOIL_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(OUTDOOR_SOIL_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in OUTDOOR_SOIL_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in OUTDOOR_SOIL_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in OUTDOOR_SOIL_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestOutdoorSoilEnvironment:
    """Verify outdoor environment section is comprehensive."""

    def test_has_all_subsections(self):
        oe = OUTDOOR_SOIL_CONFIG["outdoor_environment"]
        expected = [
            "site_selection",
            "in_ground_vs_raised_bed",
            "seasonal_timing",
            "pest_management_outdoor",
            "water_management_outdoor",
        ]
        for key in expected:
            assert key in oe, f"Missing outdoor environment subsection: {key}"

    def test_site_selection_sunlight(self):
        ss = OUTDOOR_SOIL_CONFIG["outdoor_environment"]["site_selection"]
        sun = ss["sunlight_requirements"]
        assert sun["minimum_hours"] > 0
        assert sun["optimal_hours"] > sun["minimum_hours"]

    def test_in_ground_vs_raised_bed(self):
        ig = OUTDOOR_SOIL_CONFIG["outdoor_environment"]["in_ground_vs_raised_bed"]
        assert "direct_in_ground" in ig
        assert "raised_beds" in ig
        assert "pros" in ig["direct_in_ground"]
        assert "pros" in ig["raised_beds"]

    def test_seasonal_timing_has_photoperiod(self):
        st = OUTDOOR_SOIL_CONFIG["outdoor_environment"]["seasonal_timing"]
        assert "photoperiod_awareness" in st
        assert "hardening_off" in st
        assert "last_frost_rule" in st

    def test_pest_management_has_common_pests(self):
        pm = OUTDOOR_SOIL_CONFIG["outdoor_environment"]["pest_management_outdoor"]
        assert "common_outdoor_pests" in pm
        assert "prevention_first" in pm
        assert "mold_mildew_prevention" in pm
        pests = pm["common_outdoor_pests"]
        assert len(pests) >= 3, "Need at least 3 common pest entries"

    def test_water_management(self):
        wm = OUTDOOR_SOIL_CONFIG["outdoor_environment"]["water_management_outdoor"]
        assert "mulching" in wm
        assert "rain_considerations" in wm
