"""Unit tests for Kratky grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.kratky import KRATKY_CONFIG

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
    "kratky_specific",
    "passive_system",
    "total_grow_days",
]


class TestKratkyConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in KRATKY_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in KRATKY_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in KRATKY_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in KRATKY_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(KRATKY_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in KRATKY_CONFIG["equipment"]}
        assert "essential" in categories
        assert "recommended" in categories

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in KRATKY_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in KRATKY_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestKratkyPassiveSystem:
    """Verify passive system section is comprehensive."""

    def test_has_all_subsections(self):
        ps = KRATKY_CONFIG["passive_system"]
        expected = [
            "air_gap_management",
            "container_sizing",
            "nutrient_management_passive",
            "failure_modes_passive",
            "true_set_and_forget",
        ]
        for key in expected:
            assert key in ps, f"Missing passive system subsection: {key}"

    def test_air_gap_progression(self):
        ag = KRATKY_CONFIG["passive_system"]["air_gap_management"]
        assert "air_gap_progression" in ag
        assert "refill_rules" in ag
        assert "initial_setup" in ag

    def test_container_sizing_recommendations(self):
        cs = KRATKY_CONFIG["passive_system"]["container_sizing"]
        assert "recommendations" in cs
        recs = cs["recommendations"]
        assert len(recs) >= 3, "Need at least 3 container size recommendations"

    def test_passive_nutrient_management(self):
        nm = KRATKY_CONFIG["passive_system"]["nutrient_management_passive"]
        assert "single_mix_approach" in nm
        assert "ph_drift" in nm
        single = nm["single_mix_approach"]
        assert "ec_target" in single

    def test_failure_modes_defined(self):
        failures = KRATKY_CONFIG["passive_system"]["failure_modes_passive"]
        assert len(failures) >= 3, "Need at least 3 failure modes"
        for f in failures:
            assert "failure" in f
            assert "severity" in f
            assert "prevention" in f

    def test_set_and_forget_checklist(self):
        sf = KRATKY_CONFIG["passive_system"]["true_set_and_forget"]
        assert "checklist_for_zero_maintenance" in sf
        assert len(sf["checklist_for_zero_maintenance"]) >= 5
        assert "kratky_advantage" in sf
