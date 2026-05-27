"""Unit tests for Living Soil grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.living_soil import LIVING_SOIL_CONFIG

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
    "living_soil_ecosystem",
    "total_grow_days",
]


class TestLivingSoilConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in LIVING_SOIL_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in LIVING_SOIL_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in LIVING_SOIL_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in LIVING_SOIL_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(LIVING_SOIL_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in LIVING_SOIL_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in LIVING_SOIL_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in LIVING_SOIL_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestLivingSoilEcosystem:
    """Verify living soil ecosystem section (core differentiator)."""

    def test_living_soil_ecosystem_exists(self):
        assert "living_soil_ecosystem" in LIVING_SOIL_CONFIG

    def test_has_core_subsections(self):
        lse = LIVING_SOIL_CONFIG["living_soil_ecosystem"]
        expected = ["no_till_methodology", "soil_food_web", "soil_recipe", "knf_inputs", "cover_cropping"]
        for key in expected:
            assert key in lse, f"Missing living_soil_ecosystem subsection: {key}"

    def test_soil_food_web_has_content(self):
        sfw = LIVING_SOIL_CONFIG["living_soil_ecosystem"]["soil_food_web"]
        assert isinstance(sfw, dict)
        assert len(sfw) >= 2, "soil_food_web should have multiple entries"

    def test_soil_recipe_has_content(self):
        sr = LIVING_SOIL_CONFIG["living_soil_ecosystem"]["soil_recipe"]
        assert isinstance(sr, dict)
        assert len(sr) >= 2, "soil_recipe should have multiple entries"

    def test_no_till_methodology_has_content(self):
        nt = LIVING_SOIL_CONFIG["living_soil_ecosystem"]["no_till_methodology"]
        assert isinstance(nt, dict)
        assert len(nt) >= 2, "no_till_methodology should have multiple entries"
