"""Unit tests for Rockwool grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.rockwool import ROCKWOOL_CONFIG

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
    "substrate_management",
    "substrate_engineering",
    "total_grow_days",
]


class TestRockwoolConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in ROCKWOOL_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in ROCKWOOL_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in ROCKWOOL_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in ROCKWOOL_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(ROCKWOOL_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in ROCKWOOL_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in ROCKWOOL_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in ROCKWOOL_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestRockwoolSubstrateEngineering:
    """Verify substrate engineering section is comprehensive."""

    def test_has_all_subsections(self):
        se = ROCKWOOL_CONFIG["substrate_engineering"]
        expected = [
            "conditioning_protocol",
            "cube_and_slab_management",
            "water_content_management",
            "ph_management_in_rockwool",
            "ec_management_rockwool",
            "disposal_and_sustainability",
        ]
        for key in expected:
            assert key in se, f"Missing substrate engineering subsection: {key}"

    def test_conditioning_protocol(self):
        cp = ROCKWOOL_CONFIG["substrate_engineering"]["conditioning_protocol"]
        assert "standard_soak" in cp
        soak = cp["standard_soak"]
        assert soak["solution_ph"] < 5.0  # Must be acidic
        assert soak["duration_hours"] >= 12

    def test_cube_and_slab_types(self):
        csm = ROCKWOOL_CONFIG["substrate_engineering"]["cube_and_slab_management"]
        assert "propagation_cubes" in csm
        assert "grow_cubes" in csm
        assert "slabs" in csm

    def test_water_content_saturation_targets(self):
        wc = ROCKWOOL_CONFIG["substrate_engineering"]["water_content_management"]
        targets = wc["saturation_targets"]
        assert "propagation" in targets
        assert "veg" in targets
        assert "generative_steering" in targets
        # Generative should be drier than propagation
        assert targets["generative_steering"]["percent"] < targets["propagation"]["percent"]

    def test_ph_management_range(self):
        ph = ROCKWOOL_CONFIG["substrate_engineering"]["ph_management_in_rockwool"]
        assert ph["input_ph_range"]["min"] < ph["input_ph_range"]["max"]
        assert ph["input_ph_range"]["min"] >= 5.0

    def test_single_use_only(self):
        disposal = ROCKWOOL_CONFIG["substrate_engineering"]["disposal_and_sustainability"]
        assert disposal["single_use_only"] is True
