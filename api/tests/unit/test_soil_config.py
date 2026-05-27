"""Unit tests for Soil grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.soil import SOIL_CONFIG

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
    "soil_biology",
    "total_grow_days",
]


class TestSoilConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in SOIL_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in SOIL_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in SOIL_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in SOIL_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(SOIL_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in SOIL_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in SOIL_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in SOIL_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestSoilBiologyManagement:
    """Verify soil biology management section is comprehensive."""

    def test_has_all_subsections(self):
        sb = SOIL_CONFIG["soil_biology"]
        expected = [
            "living_soil_ecosystem",
            "compost_tea_protocol",
            "top_dressing_protocol",
            "wet_dry_cycle_mastery",
            "no_till_living_soil",
        ]
        for key in expected:
            assert key in sb, f"Missing soil biology subsection: {key}"

    def test_living_soil_has_organisms(self):
        ecosystem = SOIL_CONFIG["soil_biology"]["living_soil_ecosystem"]
        organisms = ecosystem["key_organisms"]
        assert "mycorrhizae" in organisms
        assert "trichoderma" in organisms
        assert "beneficial_bacteria" in organisms

    def test_compost_tea_has_recipe(self):
        tea = SOIL_CONFIG["soil_biology"]["compost_tea_protocol"]
        assert "aerated_compost_tea" in tea
        recipe = tea["aerated_compost_tea"]
        assert "recipe" in recipe
        assert "brewing" in recipe
        assert "application" in recipe

    def test_wet_dry_cycle_has_phases(self):
        wdc = SOIL_CONFIG["soil_biology"]["wet_dry_cycle_mastery"]
        assert "phases" in wdc
        assert "saturation" in wdc["phases"]
        assert "ready_to_water" in wdc["phases"]
        assert "container_size_impact" in wdc

    def test_no_till_has_recipe(self):
        nt = SOIL_CONFIG["soil_biology"]["no_till_living_soil"]
        assert "initial_soil_recipe_per_cubic_foot" in nt
        assert "between_grows" in nt
        assert len(nt["between_grows"]) >= 3

    def test_top_dressing_veg_and_flower(self):
        td = SOIL_CONFIG["soil_biology"]["top_dressing_protocol"]
        assert "veg_top_dress" in td
        assert "flower_top_dress" in td
        assert "ingredients" in td["veg_top_dress"]
        assert "ingredients" in td["flower_top_dress"]
