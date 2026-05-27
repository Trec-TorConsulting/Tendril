"""Unit tests for DWC grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.dwc import DWC_CONFIG

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
    "reservoir",
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
    "dwc_reservoir_management",
    "total_grow_days",
]


class TestDWCConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in DWC_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in DWC_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in DWC_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in DWC_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(DWC_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in DWC_CONFIG["equipment"]}
        assert "essential" in categories
        assert "recommended" in categories

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in DWC_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in DWC_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestDWCReservoirManagement:
    """Verify DWC reservoir management section is comprehensive."""

    def test_has_all_subsections(self):
        rm = DWC_CONFIG["dwc_reservoir_management"]
        expected = [
            "top_off_decision_tree",
            "change_schedule",
            "emergency_drain_protocol",
            "beneficial_microbes",
            "dissolved_oxygen",
            "water_temperature_management",
        ]
        for key in expected:
            assert key in rm, f"Missing reservoir management subsection: {key}"

    def test_change_schedule_covers_stages(self):
        schedule = DWC_CONFIG["dwc_reservoir_management"]["change_schedule"]
        assert "seedling" in schedule
        assert "early_flower" in schedule
        assert "flush" in schedule
        for stage_data in schedule.values():
            assert "interval_days" in stage_data

    def test_emergency_protocols_have_actions(self):
        protocols = DWC_CONFIG["dwc_reservoir_management"]["emergency_drain_protocol"]
        assert len(protocols) >= 3, "Need at least 3 emergency protocols"
        for protocol in protocols:
            assert "trigger" in protocol
            assert "action" in protocol

    def test_dissolved_oxygen_targets(self):
        do = DWC_CONFIG["dwc_reservoir_management"]["dissolved_oxygen"]
        assert do["minimum_ppm"] > 0
        assert do["target_ppm"] > do["minimum_ppm"]
        assert do["critical_low_ppm"] < do["minimum_ppm"]

    def test_water_temperature_range(self):
        wt = DWC_CONFIG["dwc_reservoir_management"]["water_temperature_management"]
        assert wt["target_f"] < wt["danger_zone_f"]["above"]
        assert wt["acceptable_range_f"]["min"] < wt["acceptable_range_f"]["max"]
