"""Unit tests for Aquaponics grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.aquaponics import AQUAPONICS_CONFIG

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
    "aquaponics_ecosystem",
    "total_grow_days",
]


class TestAquaponicsConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in AQUAPONICS_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in AQUAPONICS_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in AQUAPONICS_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in AQUAPONICS_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(AQUAPONICS_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in AQUAPONICS_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in AQUAPONICS_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in AQUAPONICS_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestAquaponicsEcosystem:
    """Verify aquaponics ecosystem section (core differentiator)."""

    def test_aquaponics_ecosystem_exists(self):
        assert "aquaponics_ecosystem" in AQUAPONICS_CONFIG

    def test_has_core_subsections(self):
        ae = AQUAPONICS_CONFIG["aquaponics_ecosystem"]
        expected = ["nitrogen_cycle", "fish_species", "system_types", "system_balance", "pest_management"]
        for key in expected:
            assert key in ae, f"Missing aquaponics_ecosystem subsection: {key}"

    def test_nitrogen_cycle_has_steps(self):
        nc = AQUAPONICS_CONFIG["aquaponics_ecosystem"]["nitrogen_cycle"]
        assert "steps" in nc
        assert len(nc["steps"]) >= 4, "Nitrogen cycle should have at least 4 steps"

    def test_fish_species_has_options(self):
        fs = AQUAPONICS_CONFIG["aquaponics_ecosystem"]["fish_species"]
        assert len(fs) >= 3, "Should have at least 3 fish species"
        assert "tilapia" in fs

    def test_system_balance_has_ratios(self):
        sb = AQUAPONICS_CONFIG["aquaponics_ecosystem"]["system_balance"]
        assert "fish_to_plant_ratio" in sb
        assert "common_supplements" in sb

    def test_pest_management_has_constraints(self):
        pm = AQUAPONICS_CONFIG["aquaponics_ecosystem"]["pest_management"]
        assert "allowed_methods" in pm
        assert "banned_methods" in pm
        assert len(pm["banned_methods"]) >= 3
