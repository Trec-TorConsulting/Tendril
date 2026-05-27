"""Unit tests for Coco grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.coco import COCO_CONFIG

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
    "coco_specific",
    "fertigation_management",
    "total_grow_days",
]


class TestCocoConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in COCO_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in COCO_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in COCO_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in COCO_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(COCO_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in COCO_CONFIG["equipment"]}
        assert len(categories) >= 3, "Need at least 3 equipment categories"

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in COCO_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in COCO_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestCocoFertigationManagement:
    """Verify fertigation management section is comprehensive."""

    def test_has_all_subsections(self):
        fm = COCO_CONFIG["fertigation_management"]
        expected = [
            "high_frequency_fertigation",
            "calcium_magnesium_buffering",
            "coco_preparation",
            "runoff_management",
            "reuse_and_recycling",
        ]
        for key in expected:
            assert key in fm, f"Missing fertigation management subsection: {key}"

    def test_always_feed_rule(self):
        hff = COCO_CONFIG["fertigation_management"]["high_frequency_fertigation"]
        assert hff["always_feed"] is True
        assert "frequency_by_stage" in hff
        assert "seedling" in hff["frequency_by_stage"]
        assert "flower" in hff["frequency_by_stage"]

    def test_calmag_buffering_protocol(self):
        cm = COCO_CONFIG["fertigation_management"]["calcium_magnesium_buffering"]
        assert "initial_buffering_protocol" in cm
        assert "ongoing_supplementation" in cm
        assert len(cm["initial_buffering_protocol"]) >= 3

    def test_coco_preparation_methods(self):
        prep = COCO_CONFIG["fertigation_management"]["coco_preparation"]
        assert "brick_vs_loose" in prep
        assert "washing_protocol" in prep
        assert "perlite_ratio" in prep

    def test_runoff_ec_monitoring(self):
        rm = COCO_CONFIG["fertigation_management"]["runoff_management"]
        assert "target_runoff_percent" in rm
        assert "runoff_ec_monitoring" in rm
        assert rm["target_runoff_percent"]["min"] > 0

    def test_reuse_limits(self):
        reuse = COCO_CONFIG["fertigation_management"]["reuse_and_recycling"]
        assert reuse["can_reuse"] is True
        assert reuse["max_reuses"] >= 1
        assert "reconditioning_protocol" in reuse
