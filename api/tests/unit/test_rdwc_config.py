"""Unit tests for RDWC grow type configuration completeness and validity."""

from __future__ import annotations

from app.grows.grow_type_configs.rdwc import RDWC_CONFIG

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
    "plumbing_architecture",
    "system_sizing",
    "flow_distribution",
    "failure_modes",
    "cross_contamination_protocol",
    "plumbing_maintenance",
    "rdwc_system_tiers",
    "strain_variants",
    "water_sources",
    "total_grow_days",
]


class TestRDWCConfigCompleteness:
    """Verify all required sections and stages are present."""

    def test_all_top_level_keys_present(self):
        for key in REQUIRED_TOP_LEVEL_KEYS:
            assert key in RDWC_CONFIG, f"Missing top-level key: {key}"

    def test_all_12_stages_present(self):
        stage_ids = [s["id"] for s in RDWC_CONFIG["stages"]]
        for sid in REQUIRED_STAGE_IDS:
            assert sid in stage_ids, f"Missing stage: {sid}"

    def test_stages_have_required_fields(self):
        for stage in RDWC_CONFIG["stages"]:
            for field in REQUIRED_STAGE_FIELDS:
                assert field in stage, f"Stage '{stage['id']}' missing field: {field}"

    def test_stages_ordered_sequentially(self):
        orders = [s["order"] for s in RDWC_CONFIG["stages"]]
        assert orders == sorted(orders), "Stages are not in sequential order"

    def test_equipment_has_items(self):
        assert len(RDWC_CONFIG["equipment"]) >= 10, "Equipment list too short"
        categories = {e["category"] for e in RDWC_CONFIG["equipment"]}
        assert "essential" in categories
        assert "recommended" in categories

    def test_troubleshooting_has_categories(self):
        categories = [t["category"] for t in RDWC_CONFIG["troubleshooting"]]
        assert len(categories) >= 3, "Need at least 3 troubleshooting categories"

    def test_environment_variants_on_stages(self):
        """At least germination and seedling should have environment variants."""
        for stage in RDWC_CONFIG["stages"]:
            if stage["id"] in ("germination", "seedling", "early_veg"):
                assert "environment_variants" in stage, f"Stage '{stage['id']}' missing environment_variants"


class TestRDWCPlumbingSizing:
    """Verify plumbing sizing values scale logically."""

    def test_pipe_sizing_scales_with_site_count(self):
        table = RDWC_CONFIG["plumbing_architecture"]["pipe_sizing_by_site_count"]
        assert len(table) >= 4, "Need at least 4 pipe sizing tiers"
        # Supply diameter should increase across tiers
        diameters = [row["supply_diameter_in"] for row in table]
        assert diameters == sorted(diameters), "Supply diameters should increase with site count"

    def test_system_sizing_has_formulas(self):
        sizing = RDWC_CONFIG["system_sizing"]
        assert "total_volume_formula" in sizing
        assert "pump_sizing" in sizing
        assert "chiller_sizing" in sizing
        assert "air_pump_sizing" in sizing

    def test_pump_sizing_examples_scale(self):
        examples = RDWC_CONFIG["system_sizing"]["pump_sizing"]["examples"]
        gphs = [e["pump_min_gph"] for e in examples]
        assert gphs == sorted(gphs), "Pump GPH should increase with site count"

    def test_flow_distribution_by_stage(self):
        flow = RDWC_CONFIG["flow_distribution"]["gph_per_site_by_stage"]
        # Germination should be 0, flower should be highest
        assert flow["germination"] == 0
        assert flow["early_flower"]["target"] >= flow["seedling"]["target"]

    def test_flow_by_pipe_diameter_scales(self):
        table = RDWC_CONFIG["flow_distribution"]["gph_by_pipe_diameter"]
        # Larger pipes should support higher GPH
        assert table["2.0_inch"]["max_gph"] > table["0.75_inch"]["max_gph"]


class TestRDWCFailureModes:
    """Verify failure modes are comprehensive."""

    def test_critical_failures_defined(self):
        failures = RDWC_CONFIG["failure_modes"]
        critical = [f for f in failures if f["severity"] == "critical"]
        assert len(critical) >= 2, "Need at least 2 critical failure modes (pump failure, power outage)"

    def test_each_failure_has_response(self):
        for failure in RDWC_CONFIG["failure_modes"]:
            assert "immediate_response" in failure, f"Failure '{failure['failure']}' missing immediate_response"
            assert "prevention" in failure, f"Failure '{failure['failure']}' missing prevention"
            assert len(failure["immediate_response"]) >= 1


class TestRDWCScaleTiers:
    """Verify scale tiers cover hobby to commercial."""

    def test_has_hobby_and_commercial_tiers(self):
        tiers = RDWC_CONFIG["rdwc_system_tiers"]
        tier_ids = [t["tier"] for t in tiers]
        assert any("hobby" in t for t in tier_ids), "Missing hobby tier"
        assert any("commercial" in t for t in tier_ids), "Missing commercial tier"

    def test_tiers_volume_increases(self):
        tiers = RDWC_CONFIG["rdwc_system_tiers"]
        volumes = [t["typical_total_volume_gal"]["max"] for t in tiers]
        assert volumes == sorted(volumes), "Volume should increase across tiers"
