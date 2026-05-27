"""Unit tests for Ebb & Flow grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.ebb_flow import EBB_FLOW_CONFIG

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
    "flood_engineering",
    "total_grow_days",
]


class TestEbbFlowConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in EBB_FLOW_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in EBB_FLOW_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in EBB_FLOW_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in EBB_FLOW_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(EBB_FLOW_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in EBB_FLOW_CONFIG["equipment"]}
        assert "essential" in categories
        assert "recommended" in categories

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in EBB_FLOW_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in EBB_FLOW_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestEbbFlowFloodEngineering:
    """Verify flood engineering section is comprehensive."""

    def test_has_all_subsections(self):
        fe = EBB_FLOW_CONFIG["flood_engineering"]
        expected = [
            "flood_cycle_timing",
            "media_selection_guide",
            "tray_engineering",
            "pump_and_timer_configuration",
            "failure_modes",
            "multi_tray_systems",
        ]
        for key in expected:
            assert key in fe, f"Missing flood engineering subsection: {key}"

    def test_flood_cycle_covers_stages(self):
        timing = EBB_FLOW_CONFIG["flood_engineering"]["flood_cycle_timing"]["by_stage"]
        assert "seedling" in timing
        assert "early_flower" in timing
        assert "flush" in timing
        for stage_data in timing.values():
            assert "floods_per_day" in stage_data
            assert "flood_duration_min" in stage_data

    def test_media_selection_has_options(self):
        media = EBB_FLOW_CONFIG["flood_engineering"]["media_selection_guide"]
        assert len(media) >= 3, "Need at least 3 media options"
        for _name, info in media.items():
            assert "flood_retention" in info
            assert "best_for" in info

    def test_tray_sizes_defined(self):
        trays = EBB_FLOW_CONFIG["flood_engineering"]["tray_engineering"]["tray_sizes"]
        assert len(trays) >= 3, "Need at least 3 tray sizes"
        for _size, info in trays.items():
            assert "plant_capacity" in info
            assert "reservoir_gal" in info

    def test_failure_modes_present(self):
        failures = EBB_FLOW_CONFIG["flood_engineering"]["failure_modes"]
        assert len(failures) >= 3, "Need at least 3 failure modes"
        for f in failures:
            assert "failure" in f
            assert "severity" in f
            assert "prevention" in f

    def test_multi_tray_options(self):
        mt = EBB_FLOW_CONFIG["flood_engineering"]["multi_tray_systems"]
        assert "parallel_flooding" in mt
        assert "sequential_flooding" in mt
        assert "independent_systems" in mt
