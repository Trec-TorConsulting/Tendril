"""Unit tests for NFT grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.nft import NFT_CONFIG

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
    "channel_engineering",
    "total_grow_days",
]


class TestNFTConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in NFT_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in NFT_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in NFT_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in NFT_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(NFT_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in NFT_CONFIG["equipment"]}
        assert "essential" in categories
        assert "recommended" in categories

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in NFT_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        for stage in NFT_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestNFTChannelEngineering:
    """Verify channel engineering section is comprehensive."""

    def test_has_all_subsections(self):
        ce = NFT_CONFIG["channel_engineering"]
        expected = [
            "channel_specifications",
            "flow_rate_management",
            "root_mat_management",
            "pump_failure_protocol",
            "salt_accumulation",
            "propagation_to_nft_transfer",
        ]
        for key in expected:
            assert key in ce, f"Missing channel engineering subsection: {key}"

    def test_channel_slope_defined(self):
        specs = NFT_CONFIG["channel_engineering"]["channel_specifications"]
        slope = specs["slope_percent"]
        assert slope["min"] < slope["max"]
        assert slope["min"] <= slope["target"] <= slope["max"]

    def test_flow_rate_targets(self):
        flow = NFT_CONFIG["channel_engineering"]["flow_rate_management"]
        assert flow["target_lpm"]["min"] < flow["target_lpm"]["max"]
        assert "adjustment_by_stage" in flow

    def test_pump_failure_has_backup_recommendations(self):
        pf = NFT_CONFIG["channel_engineering"]["pump_failure_protocol"]
        assert "time_to_damage" in pf
        assert "immediate_actions" in pf
        assert "backup_system_recommendations" in pf
        assert len(pf["backup_system_recommendations"]) >= 2

    def test_salt_accumulation_has_cleaning(self):
        salt = NFT_CONFIG["channel_engineering"]["salt_accumulation"]
        assert "prevention" in salt
        assert "cleaning_protocol" in salt
        assert len(salt["cleaning_protocol"]) >= 3

    def test_propagation_transfer_protocol(self):
        prop = NFT_CONFIG["channel_engineering"]["propagation_to_nft_transfer"]
        assert "ideal_root_length_inches" in prop
        assert "transfer_protocol" in prop
        assert len(prop["transfer_protocol"]) >= 3
