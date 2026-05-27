"""Unit tests for Aeroponics grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.aeroponics import AERO_CONFIG

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
    "mist_engineering",
    "total_grow_days",
]


class TestAeroConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in AERO_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in AERO_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in AERO_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in AERO_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(AERO_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in AERO_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in AERO_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in AERO_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestAeroMistEngineering:
    """Verify mist engineering section is comprehensive."""

    def test_has_all_subsections(self):
        me = AERO_CONFIG["mist_engineering"]
        expected = [
            "hpa_vs_lpa",
            "mist_cycle_timing",
            "nozzle_management",
            "root_chamber_design",
            "failure_modes",
            "nutrient_approach",
        ]
        for key in expected:
            assert key in me, f"Missing mist engineering subsection: {key}"

    def test_hpa_vs_lpa_pressure_ranges(self):
        hpa = AERO_CONFIG["mist_engineering"]["hpa_vs_lpa"]["high_pressure_aeroponics"]
        lpa = AERO_CONFIG["mist_engineering"]["hpa_vs_lpa"]["low_pressure_aeroponics"]
        assert hpa["pressure_psi"]["min"] > lpa["pressure_psi"]["max"]

    def test_mist_cycle_has_stages(self):
        timing = AERO_CONFIG["mist_engineering"]["mist_cycle_timing"]["by_stage"]
        assert "seedling" in timing
        assert "early_flower" in timing
        for stage_data in timing.values():
            assert "on_seconds" in stage_data
            assert "off_seconds" in stage_data

    def test_nozzle_types_defined(self):
        nozzles = AERO_CONFIG["mist_engineering"]["nozzle_management"]["types"]
        assert len(nozzles) >= 3, "Need at least 3 nozzle types"

    def test_failure_modes_have_responses(self):
        failures = AERO_CONFIG["mist_engineering"]["failure_modes"]
        assert len(failures) >= 3, "Need at least 3 failure modes"
        for f in failures:
            assert "failure" in f
            assert "severity" in f
            assert "immediate_response" in f

    def test_nutrient_approach_ec_targets(self):
        na = AERO_CONFIG["mist_engineering"]["nutrient_approach"]
        assert na["synthetic_only"] is True
        ec = na["ec_targets"]
        assert ec["seedling"]["max"] < ec["flower"]["max"]
