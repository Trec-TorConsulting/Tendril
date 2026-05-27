"""Unit tests for Drip grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.drip import DRIP_CONFIG

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
    "irrigation_management",
    "total_grow_days",
]


class TestDripConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in DRIP_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in DRIP_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in DRIP_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in DRIP_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(DRIP_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in DRIP_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in DRIP_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in DRIP_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestDripIrrigationManagement:
    """Verify irrigation management section is comprehensive."""

    def test_has_all_subsections(self):
        im = DRIP_CONFIG["irrigation_management"]
        expected = [
            "emitter_types_and_selection",
            "runoff_monitoring",
            "drain_to_waste_vs_recirculating",
            "media_profiles_for_drip",
            "crop_steering_with_drip",
            "scheduling_strategies",
        ]
        for key in expected:
            assert key in im, f"Missing irrigation management subsection: {key}"

    def test_emitter_types_defined(self):
        emitters = DRIP_CONFIG["irrigation_management"]["emitter_types_and_selection"]
        assert len(emitters) >= 3, "Need at least 3 emitter types"
        for _name, info in emitters.items():
            assert "best_for" in info

    def test_runoff_targets_defined(self):
        runoff = DRIP_CONFIG["irrigation_management"]["runoff_monitoring"]
        targets = runoff["target_runoff_percent"]
        assert "standard" in targets
        assert targets["standard"]["min"] > 0
        assert targets["standard"]["max"] > targets["standard"]["min"]

    def test_dtw_vs_recirc_both_present(self):
        dtw = DRIP_CONFIG["irrigation_management"]["drain_to_waste_vs_recirculating"]
        assert "drain_to_waste" in dtw
        assert "recirculating" in dtw
        assert "pros" in dtw["drain_to_waste"]
        assert "pros" in dtw["recirculating"]

    def test_media_profiles_have_irrigation_events(self):
        profiles = DRIP_CONFIG["irrigation_management"]["media_profiles_for_drip"]
        assert len(profiles) >= 3, "Need at least 3 media profiles"
        for _name, info in profiles.items():
            assert "irrigation_events_per_day" in info

    def test_crop_steering_vegetative_and_generative(self):
        cs = DRIP_CONFIG["irrigation_management"]["crop_steering_with_drip"]
        assert "vegetative_steering" in cs
        assert "generative_steering" in cs
        assert "strategy" in cs["vegetative_steering"]
        assert "strategy" in cs["generative_steering"]

    def test_scheduling_strategies(self):
        sched = DRIP_CONFIG["irrigation_management"]["scheduling_strategies"]
        assert "timer_based" in sched
        assert "sensor_driven" in sched
