"""Config completeness and structural validation for all grow type configurations.

Validates:
  - All configs have required top-level keys
  - All stages have required fields (environment, nutrients, tasks, etc.)
  - Threshold ordering (info < warning < alert < critical)
  - Nutrient brand dosing sanity (PPM/EC reasonable per stage)
  - Kratky drift thresholds (wider ranges reflecting passive nature)

These are pure-Python tests that do not require a database connection.
Run with: pytest tests/unit/test_grow_type_configs.py -p no:asyncio
"""

from __future__ import annotations

import pytest

from app.grows.grow_type_configs import GROW_TYPE_CONFIGS
from app.grows.grow_type_configs.enhancements import (
    MONITORING_THRESHOLDS,
    NUTRIENT_BRANDS,
    SCALE_TIERS,
)

# ─────────────────────────────────────────────────────────────────────────────
# Required keys
# ─────────────────────────────────────────────────────────────────────────────

REQUIRED_TOP_LEVEL_KEYS = {
    "grow_type_id",
    "version",
    "stages",
    "equipment",
    "quick_reference",
    "troubleshooting",
    "total_grow_days",
    # Enhancements (applied by apply_enhancements)
    "scale_tiers",
    "strain_adjustments",
    "monitoring_thresholds",
    "advanced_techniques",
    "nutrient_brands",
    "water_source_profiles",
    "harvest_decision_matrix",
    "post_harvest_guide",
}

REQUIRED_STAGE_KEYS = {
    "id",
    "name",
    "order",
    "duration_days",
    "description",
    "environment",
    "nutrients",
    "tasks",
}

REQUIRED_ENVIRONMENT_KEYS = {
    "temp_day_f",
    "temp_night_f",
    "humidity_pct",
    "light_hours",
}

ALL_GROW_TYPE_IDS = list(GROW_TYPE_CONFIGS.keys())


# ─────────────────────────────────────────────────────────────────────────────
# Config completeness tests
# ─────────────────────────────────────────────────────────────────────────────


class TestConfigCompleteness:
    """Verify every registered grow type has complete, well-formed config."""

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_has_required_top_level_keys(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        missing = REQUIRED_TOP_LEVEL_KEYS - set(config.keys())
        assert not missing, f"{grow_type_id} missing top-level keys: {missing}"

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_grow_type_id_field_is_string(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        assert isinstance(config["grow_type_id"], str)
        assert len(config["grow_type_id"]) > 0

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_has_at_least_8_stages(self, grow_type_id: str):
        """Every grow should have at minimum germination through harvest."""
        config = GROW_TYPE_CONFIGS[grow_type_id]
        assert len(config["stages"]) >= 8, f"{grow_type_id} has only {len(config['stages'])} stages"

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_stages_have_required_keys(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        for stage in config["stages"]:
            missing = REQUIRED_STAGE_KEYS - set(stage.keys())
            assert not missing, f"{grow_type_id}/{stage['id']} missing keys: {missing}"

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_stages_ordered_sequentially(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        orders = [s["order"] for s in config["stages"]]
        assert orders == sorted(orders), f"{grow_type_id} stages not in order: {orders}"

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_stages_have_unique_ids(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        ids = [s["id"] for s in config["stages"]]
        assert len(ids) == len(set(ids)), f"{grow_type_id} has duplicate stage IDs"

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_environment_has_required_fields(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        for stage in config["stages"]:
            env = stage["environment"]
            # Post-harvest stages don't need standard environment keys
            if stage["id"] in ("harvest", "drying", "curing", "storage"):
                continue
            missing = REQUIRED_ENVIRONMENT_KEYS - set(env.keys())
            assert not missing, f"{grow_type_id}/{stage['id']} environment missing: {missing}"

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_duration_days_has_min_max(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        for stage in config["stages"]:
            dur = stage["duration_days"]
            assert "min" in dur and "max" in dur, f"{grow_type_id}/{stage['id']} duration_days must have min/max"
            assert dur["min"] <= dur["max"], f"{grow_type_id}/{stage['id']} duration min > max"

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_tasks_are_non_empty(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        for stage in config["stages"]:
            tasks = stage["tasks"]
            # Storage stage may have no tasks
            if stage["id"] == "storage":
                continue
            assert len(tasks) > 0, f"{grow_type_id}/{stage['id']} has no tasks"

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_equipment_is_non_empty(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        assert config["equipment"], f"{grow_type_id} has empty equipment section"

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_troubleshooting_is_non_empty(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        assert config["troubleshooting"], f"{grow_type_id} has empty troubleshooting"

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_total_grow_days_structure(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        tgd = config["total_grow_days"]
        assert "min" in tgd and "max" in tgd, f"{grow_type_id} total_grow_days missing min/max"
        assert tgd["min"] < tgd["max"]


# ─────────────────────────────────────────────────────────────────────────────
# Threshold validation
# ─────────────────────────────────────────────────────────────────────────────


class TestMonitoringThresholds:
    """Verify threshold ordering: info < warning < alert < critical for severity."""

    @pytest.mark.parametrize("sensor", list(MONITORING_THRESHOLDS.keys()))
    def test_threshold_low_values_descend(self, sensor: str):
        """Lower boundaries should get less restrictive at higher severity."""
        levels = MONITORING_THRESHOLDS[sensor]
        assert levels["info"]["low"] >= levels["warning"]["low"]
        assert levels["warning"]["low"] >= levels["alert"]["low"]
        assert levels["alert"]["low"] >= levels["critical"]["low"]

    @pytest.mark.parametrize("sensor", list(MONITORING_THRESHOLDS.keys()))
    def test_threshold_high_values_ascend(self, sensor: str):
        """Upper boundaries should get less restrictive at higher severity."""
        levels = MONITORING_THRESHOLDS[sensor]
        assert levels["info"]["high"] <= levels["warning"]["high"]
        assert levels["warning"]["high"] <= levels["alert"]["high"]
        assert levels["alert"]["high"] <= levels["critical"]["high"]

    @pytest.mark.parametrize("sensor", list(MONITORING_THRESHOLDS.keys()))
    def test_info_range_is_narrowest(self, sensor: str):
        """Info range should be the narrowest (tightest acceptable band)."""
        levels = MONITORING_THRESHOLDS[sensor]
        info_range = levels["info"]["high"] - levels["info"]["low"]
        critical_range = levels["critical"]["high"] - levels["critical"]["low"]
        assert info_range <= critical_range


# ─────────────────────────────────────────────────────────────────────────────
# Kratky drift threshold validation
# ─────────────────────────────────────────────────────────────────────────────


class TestKratkyDriftThresholds:
    """Kratky has wider acceptable ranges due to passive nature — no pump to correct."""

    def test_kratky_config_exists(self):
        assert "kratky" in GROW_TYPE_CONFIGS

    def test_kratky_has_specific_section(self):
        config = GROW_TYPE_CONFIGS["kratky"]
        assert "kratky_specific" in config, "Kratky config must have kratky_specific section"

    def test_kratky_ph_range_wider_than_hydro(self):
        """Kratky pH drift is expected — acceptable range should be wider than active hydro."""
        kratky = GROW_TYPE_CONFIGS["kratky"]
        dwc = GROW_TYPE_CONFIGS["dwc"]
        kratky_stages = {s["id"]: s for s in kratky["stages"]}
        dwc_stages = {s["id"]: s for s in dwc["stages"]}
        # Compare reservoir pH ranges (both systems store pH in reservoir dict)
        for stage_id in ("early_veg", "late_veg"):
            ks = kratky_stages.get(stage_id, {}).get("reservoir", {})
            ds = dwc_stages.get(stage_id, {}).get("reservoir", {})
            k_ph = ks.get("ph")
            d_ph = ds.get("ph")
            if k_ph and d_ph and isinstance(k_ph, dict) and isinstance(d_ph, dict):
                k_range = k_ph["max"] - k_ph["min"]
                d_range = d_ph["max"] - d_ph["min"]
                # Kratky should have same or wider pH range (passive = less control)
                assert k_range >= d_range, f"Kratky {stage_id} pH range ({k_range}) should be >= DWC ({d_range})"
                return  # One valid comparison is enough
        pytest.fail("Could not find comparable pH range stages between Kratky and DWC")

    def test_kratky_critical_rules_documented(self):
        """Kratky's critical rules (never refill to original level) must be present."""
        config = GROW_TYPE_CONFIGS["kratky"]
        specific = config["kratky_specific"]
        assert "critical_rules" in specific
        assert len(specific["critical_rules"]) >= 3


# ─────────────────────────────────────────────────────────────────────────────
# Nutrient brand dosing sanity
# ─────────────────────────────────────────────────────────────────────────────


class TestNutrientBrandSanity:
    """Verify nutrient brand dosing values are within reasonable ranges."""

    @pytest.mark.parametrize("brand", NUTRIENT_BRANDS, ids=lambda b: b["id"])
    def test_brand_has_required_fields(self, brand: dict):
        assert "id" in brand
        assert "name" in brand
        assert "dosing_by_stage" in brand
        assert "components" in brand

    @pytest.mark.parametrize("brand", NUTRIENT_BRANDS, ids=lambda b: b["id"])
    def test_brand_has_flush_stage_at_zero(self, brand: dict):
        """Flush stage should have zero nutrients for every brand."""
        dosing = brand["dosing_by_stage"]
        if "flush" in dosing:
            flush = dosing["flush"]
            for key, val in flush.items():
                if key == "unit" or key == "line":
                    continue
                assert val == 0, f"{brand['id']} flush stage has non-zero {key}={val}"

    @pytest.mark.parametrize("brand", NUTRIENT_BRANDS, ids=lambda b: b["id"])
    def test_brand_dosing_increases_from_seedling_to_mid(self, brand: dict):
        """Dosing should generally increase from seedling toward peak flower."""
        dosing = brand["dosing_by_stage"]
        if "seedling" not in dosing or "mid_flower" not in dosing:
            pytest.skip("Brand missing seedling or mid_flower stage")

        # Sum all numeric values per stage as a rough "total nutrient load"
        def stage_total(stage_data: dict) -> float:
            return sum(v for v in stage_data.values() if isinstance(v, (int, float)))

        seedling_total = stage_total(dosing["seedling"])
        mid_total = stage_total(dosing["mid_flower"])
        assert mid_total > seedling_total, (
            f"{brand['id']}: mid_flower total ({mid_total}) should exceed seedling ({seedling_total})"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Enhancement application validation
# ─────────────────────────────────────────────────────────────────────────────


class TestEnhancementApplication:
    """Verify enhancements are properly applied to all configs."""

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_scale_tiers_applied(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        assert config["scale_tiers"] == SCALE_TIERS

    @pytest.mark.parametrize("grow_type_id", ALL_GROW_TYPE_IDS)
    def test_strain_adjustments_applied(self, grow_type_id: str):
        config = GROW_TYPE_CONFIGS[grow_type_id]
        assert "photoperiod" in config["strain_adjustments"]
        assert "autoflower" in config["strain_adjustments"]

    def test_hydro_types_have_reservoir_management(self):
        hydro_types = {"dwc", "rdwc", "nft", "ebb_flow", "drip", "aeroponics"}
        for gt_id in hydro_types:
            if gt_id in GROW_TYPE_CONFIGS:
                assert "reservoir_management" in GROW_TYPE_CONFIGS[gt_id], f"{gt_id} should have reservoir_management"

    def test_coco_has_specific_section(self):
        assert "coco_specific" in GROW_TYPE_CONFIGS["coco"]

    def test_soil_types_have_soil_specific(self):
        for gt_id in ("soil", "outdoor_soil"):
            if gt_id in GROW_TYPE_CONFIGS:
                assert "soil_specific" in GROW_TYPE_CONFIGS[gt_id]

    def test_outdoor_types_have_outdoor_specific(self):
        for gt_id in ("outdoor_soil", "outdoor_container"):
            if gt_id in GROW_TYPE_CONFIGS:
                assert "outdoor_specific" in GROW_TYPE_CONFIGS[gt_id]
