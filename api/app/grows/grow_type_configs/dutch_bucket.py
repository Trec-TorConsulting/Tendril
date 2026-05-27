"""Dutch Bucket (Bato Bucket) — Complete grow type configuration.

Enterprise-grade configuration for Dutch bucket / Bato bucket growing.
Recirculating or drain-to-waste systems with individual containers connected
to a shared reservoir and drain line. Scalable from 4 to 400+ buckets.

Data sources:
  - Commercial Dutch bucket greenhouse operations (CropKing, FarmTek)
  - Cannabis production facility designs
  - Hydroponic supply company technical guides
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES
# ─────────────────────────────────────────────────────────────────────────────

DUTCH_BUCKET_STAGES: list[dict] = [
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Germinate in starter cubes (rockwool or rapid rooters). System doesn't need to run yet — seedlings stay in propagation tray until ready for buckets.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
        },
        "reservoir": {"ec": 0, "ph": {"min": 5.5, "max": 6.0}, "notes": "System off. Propagation only."},
        "nutrients": {"strength_pct": 0, "approach": "Plain water in propagation tray."},
        "tasks": [
            {
                "name": "Soak starter cubes",
                "description": "pH 5.5 water. Rockwool or rapid rooters.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Plant seeds",
                "description": "One seed per cube, 1/4 inch deep.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check germination",
                "description": "Look for taproot or sprout.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Seeds cracking?", "Cubes staying moist (not soaked)?"],
        "common_problems": [
            {
                "issue": "No germination after 7 days",
                "cause": "Temperature too low or seeds too old",
                "solution": "Use heat mat. Test seed viability.",
            },
        ],
        "transition_signals": ["Taproot visible", "Cotyledons emerging"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Germinate indoors for control."}, "extra_tasks": []},
            "greenhouse": {
                "environment_overrides": {"notes": "Propagation bench with humidity dome."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Seedlings in starter cubes under mild light. Transplant to buckets once roots emerge from cube. Run system at low flow to keep media moist.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 60, "max": 75, "target": 68},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 300, "target": 200},
            "light_dli": {"min": 6, "max": 19, "target": 13},
        },
        "reservoir": {
            "ec": {"min": 0.4, "max": 0.8, "target": 0.6},
            "ph": {"min": 5.6, "max": 6.0, "target": 5.8},
            "notes": "Very light feed. 15 min on / 60 min off timer.",
        },
        "nutrients": {"strength_pct": 25, "approach": "1/4 strength veg formula."},
        "tasks": [
            {
                "name": "Transplant to buckets",
                "description": "Place cube in bucket media when roots show. Bury 1-2 inches.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Set drip timer",
                "description": "15 min on / 60 off. Gentle flow to seedling zone.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor media moisture",
                "description": "Should be moist, not saturated around seedling.",
                "interval_days": 1,
                "priority": "high",
            },
            {"name": "Check pH/EC", "description": "Reservoir and runoff.", "interval_days": 2, "priority": "medium"},
        ],
        "health_checks": ["Seedling growing?", "Media moisture correct?", "Drip emitters flowing?"],
        "common_problems": [
            {
                "issue": "Seedling drying out",
                "cause": "Drip emitter not reaching root zone",
                "solution": "Move emitter closer. Increase frequency. Hand-water supplementally.",
            },
            {
                "issue": "Damping off",
                "cause": "Media too wet + poor airflow",
                "solution": "Reduce drip frequency. Improve ventilation.",
            },
        ],
        "transition_signals": ["3-4 true leaf sets", "Roots growing into bucket media", "Vigorous new growth"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "System outdoors if frost-free."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Ideal Dutch bucket environment."}, "extra_tasks": []},
        },
    },
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Plants establishing in buckets. Roots growing through media. Increase feed strength and frequency. Each bucket operating independently.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 600, "target": 500},
            "light_dli": {"min": 25, "max": 39, "target": 32},
        },
        "reservoir": {
            "ec": {"min": 0.8, "max": 1.2, "target": 1.0},
            "ph": {"min": 5.6, "max": 6.2, "target": 5.9},
            "notes": "Increase feed cycles. 15 min on / 30 min off.",
        },
        "nutrients": {"strength_pct": 50, "approach": "Half-strength veg. High nitrogen."},
        "tasks": [
            {
                "name": "Increase feed frequency",
                "description": "15 on / 30 off during lights. Off at night.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check runoff EC/pH",
                "description": "Runoff EC should be within 0.3 of input.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Inspect drain lines",
                "description": "All buckets draining freely.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Begin training",
                "description": "LST or topping at 4th-5th node.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["All emitters flowing?", "Runoff EC acceptable?", "Drain lines clear?", "Even growth?"],
        "common_problems": [
            {
                "issue": "Uneven growth between buckets",
                "cause": "Clogged emitter or genetics",
                "solution": "Check each emitter flow rate. Clean or replace.",
            },
            {
                "issue": "Salt buildup in media",
                "cause": "EC too high or insufficient runoff",
                "solution": "Increase runoff to 20-30%. Flush with plain water.",
            },
        ],
        "transition_signals": ["5-6 nodes developed", "Root mass filling bucket", "Vigorous daily growth"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Protect reservoir from sun (algae)."}, "extra_tasks": []},
            "greenhouse": {
                "environment_overrides": {"notes": "Excellent light + controlled environment."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 14, "max": 35, "typical": 21},
        "description": "Aggressive growth. Full nutrient strength. Dutch buckets excel — each plant gets abundant feed with individual drain monitoring. Train canopy.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 65, "target": 58},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 500, "max": 700, "target": 600},
            "light_dli": {"min": 32, "max": 45, "target": 39},
        },
        "reservoir": {
            "ec": {"min": 1.2, "max": 1.6, "target": 1.4},
            "ph": {"min": 5.6, "max": 6.2, "target": 5.9},
            "notes": "Full veg strength. Multiple feed cycles.",
        },
        "nutrients": {"strength_pct": 75, "approach": "3/4 strength veg. Cal-mag if coco media."},
        "tasks": [
            {
                "name": "Monitor reservoir consumption",
                "description": "Large plants drink 1-2 gal/day each.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check runoff per bucket",
                "description": "Individual EC/pH. Identify problem plants.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Clean inline filter",
                "description": "Prevents emitter clogs.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Train canopy",
                "description": "SCROG or LST. Dutch buckets support large plants.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["Reservoir level?", "All emitters equal flow?", "Drain line clear?", "Canopy even?"],
        "common_problems": [
            {
                "issue": "Reservoir depleting too fast",
                "cause": "Large plants drink heavily",
                "solution": "Larger reservoir. Float valve auto-fill.",
            },
            {
                "issue": "Root intrusion into drain line",
                "cause": "Roots growing out of bucket",
                "solution": "Ensure siphon elbows installed. Check drain fittings.",
            },
        ],
        "transition_signals": ["Canopy 50-60% filled", "Ready for flip", "Healthy uniform growth"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Cover reservoir from rain/debris."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Ventilate for humidity control."}, "extra_tasks": []},
        },
    },
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Flip to 12/12. Plants stretch 50-100%. Transition nutrients to bloom. Dutch bucket advantage: individual plant monitoring during transition.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 64, "max": 72, "target": 68},
            "humidity_pct": {"min": 45, "max": 60, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.3, "target": 1.1},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 800, "target": 700},
            "light_dli": {"min": 25, "max": 35, "target": 30},
        },
        "reservoir": {
            "ec": {"min": 1.2, "max": 1.6, "target": 1.4},
            "ph": {"min": 5.6, "max": 6.2, "target": 5.9},
            "notes": "50/50 veg-bloom transition.",
        },
        "nutrients": {"strength_pct": 75, "approach": "Transition: 50% veg + 50% bloom."},
        "tasks": [
            {
                "name": "Flip light schedule",
                "description": "Switch to 12/12.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Transition nutrients",
                "description": "Begin bloom formula. Reduce N, increase P-K.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Manage stretch",
                "description": "LST/supercrop individual buckets as needed.",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": ["Stretch managed?", "All buckets receiving flow?", "Nutrient transition smooth?"],
        "common_problems": [
            {
                "issue": "Excessive stretch in some buckets",
                "cause": "Genetic variation",
                "solution": "Raise individual buckets or supercrop tall ones.",
            },
        ],
        "transition_signals": ["Stretch slowing", "Pre-flowers visible", "Pistils emerging"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Natural photoperiod trigger."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Blackout covers if needed."}, "extra_tasks": []},
        },
    },
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Bud sites forming. Full bloom nutrients. Dutch buckets deliver consistent feed — ideal for uniform bud development across the row.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 79, "target": 75},
            "temp_night_f": {"min": 62, "max": 70, "target": 66},
            "humidity_pct": {"min": 40, "max": 55, "target": 48},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 25, "max": 39, "target": 32},
        },
        "reservoir": {
            "ec": {"min": 1.4, "max": 1.8, "target": 1.6},
            "ph": {"min": 5.6, "max": 6.2, "target": 5.9},
            "notes": "Full bloom. High P-K.",
        },
        "nutrients": {"strength_pct": 100, "approach": "Full bloom formula. High P-K ratio."},
        "tasks": [
            {
                "name": "Switch to full bloom",
                "description": "Complete transition to flower nutrients.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Remove lower fan leaves blocking bud sites.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Check drain consistency",
                "description": "Each bucket 20-30% runoff.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["Bud sites forming?", "EC runoff per bucket?", "Humidity below 55%?"],
        "common_problems": [
            {
                "issue": "Nutrient burn on some buckets only",
                "cause": "Emitter delivering more to that bucket",
                "solution": "Equalize emitter flow rates. Check for partial clogs.",
            },
        ],
        "transition_signals": ["Buds forming at all sites", "White pistils abundant", "Stretch complete"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Pest pressure increases."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Airflow between buckets critical."}, "extra_tasks": []},
        },
    },
    {
        "id": "mid_flower",
        "name": "Mid Flower (Bulk Phase)",
        "order": 7,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Peak bud development. Maximum nutrient demand. Dutch buckets handle large flower loads — media provides root support for heavy colas.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 78, "target": 74},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 38, "max": 50, "target": 44},
            "vpd_kpa": {"min": 1.2, "max": 1.5, "target": 1.3},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
        },
        "reservoir": {
            "ec": {"min": 1.6, "max": 2.0, "target": 1.8},
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "notes": "Peak strength. Monitor for lockout.",
        },
        "nutrients": {"strength_pct": 100, "approach": "Full bloom + PK booster weeks 4-6."},
        "tasks": [
            {
                "name": "Monitor reservoir daily",
                "description": "Peak consumption. 2-3 gal/day per plant.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "PK boost",
                "description": "Add PK booster weeks 4-6 of flower.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Support heavy colas",
                "description": "Yo-yo supports or trellis per bucket.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Inspect for bud rot",
                "description": "Dense buds in humid environments.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": ["Buds swelling?", "Reservoir keeping up?", "No rot?", "Trichomes developing?"],
        "common_problems": [
            {
                "issue": "Salt buildup in media",
                "cause": "High EC over weeks",
                "solution": "Increase runoff to 30%+. Plain water flush weekly.",
            },
            {
                "issue": "Different plants at different stages",
                "cause": "Multi-strain setup",
                "solution": "Flush/feed individual buckets differently.",
            },
        ],
        "transition_signals": ["Buds dense and heavy", "Trichomes milky", "Pistils browning"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Rain cover critical."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Dehumidifier may be needed."}, "extra_tasks": []},
        },
    },
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Final ripening. Reduce nutrients. Dutch bucket advantage: harvest individual buckets at different times based on readiness.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 72},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 48, "target": 42},
            "vpd_kpa": {"min": 1.2, "max": 1.5, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 800},
            "light_dli": {"min": 25, "max": 39, "target": 35},
        },
        "reservoir": {
            "ec": {"min": 1.0, "max": 1.4, "target": 1.2},
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "notes": "Reduce strength. Preparing for flush.",
        },
        "nutrients": {"strength_pct": 75, "approach": "75% bloom. Stop PK boosters."},
        "tasks": [
            {
                "name": "Check trichomes",
                "description": "60x loupe. 70-80% milky, 10-20% amber.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Reduce nutrients",
                "description": "Drop EC. Simpler formula.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Plan staggered harvest",
                "description": "Identify earliest-ready buckets.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["Trichome progression?", "No rot?", "Pistils receded?"],
        "common_problems": [
            {
                "issue": "Some plants not ripening",
                "cause": "Strain variation or excess nitrogen",
                "solution": "Begin individual bucket flush early. Reduce N.",
            },
        ],
        "transition_signals": ["70-80% milky trichomes", "Pistils mostly orange", "Swollen calyxes"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Fall temps help. Watch for frost."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Night temp drops enhance terpenes."}, "extra_tasks": []},
        },
    },
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Switch reservoir to plain pH'd water. Media flushes clean within 3-5 days due to frequent irrigation. Can flush individual buckets by disconnecting from main system.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 72},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 48, "target": 42},
            "vpd_kpa": {"min": 1.2, "max": 1.5, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 17, "max": 30, "target": 26},
        },
        "reservoir": {
            "ec": {"min": 0, "max": 0.2, "target": 0.1},
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "notes": "Plain water only.",
        },
        "nutrients": {"strength_pct": 0, "approach": "Plain pH'd water. No nutrients."},
        "tasks": [
            {
                "name": "Switch to plain water",
                "description": "Drain nutrient reservoir. Refill with pH'd water.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Increase feed cycles",
                "description": "More cycles to flush media faster.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Check runoff EC",
                "description": "Target < 0.3 EC = fully flushed.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": ["Runoff EC dropping?", "Plant fading?", "Buds healthy?"],
        "common_problems": [
            {
                "issue": "EC not dropping in runoff",
                "cause": "Dense media holding salts",
                "solution": "Extend flush. More cycles. Switch to perlite next round.",
            },
        ],
        "transition_signals": ["Runoff EC < 0.3", "Fan leaves yellow", "7-14 days complete"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Continue timer-based feed with plain water."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Standard flush."}, "extra_tasks": []},
        },
    },
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Chop plants. Dutch bucket advantage: staggered harvest — take ready buckets first. Remove root mass, media is reusable.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
        },
        "reservoir": {"notes": "System keeps running for unharvested buckets."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Chop plant at base",
                "description": "Cut stem above media.",
                "interval_days": None,
                "priority": "high",
            },
            {"name": "Trim", "description": "Wet or dry trim preference.", "interval_days": None, "priority": "high"},
            {
                "name": "Remove root ball",
                "description": "Pull roots from bucket. Rinse media for reuse.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Clean bucket",
                "description": "H2O2 rinse bucket + siphon elbow.",
                "interval_days": None,
                "priority": "low",
            },
        ],
        "health_checks": ["Trichomes at target?", "All ready buckets harvested?"],
        "common_problems": [
            {
                "issue": "Root mass hard to remove",
                "cause": "Dense root ball in media",
                "solution": "Soak bucket 30 min. Roots slide out.",
            },
        ],
        "transition_signals": ["Plants chopped", "Branches hung"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Harvest before frost."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Harvest at convenience."}, "extra_tasks": []},
        },
    },
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Standard hang dry. 60°F, 60% RH, darkness, gentle air movement.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "light_hours": 0,
        },
        "reservoir": {"notes": "Clean system during drying for next cycle."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Hang branches",
                "description": "Whole plant or individual branches.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor conditions",
                "description": "60-65°F, 55-62% RH, darkness.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Stem snap test",
                "description": "Small stems snap = ready to jar.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": ["Temp/humidity correct?", "No mold?", "Even drying?"],
        "common_problems": [
            {
                "issue": "Drying too fast",
                "cause": "Too warm or low humidity",
                "solution": "Lower temp, raise humidity, hang whole plants.",
            },
        ],
        "transition_signals": ["Small stems snap", "Outside crispy, inside slightly moist"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Always dry indoors."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Dry in separate controlled space."}, "extra_tasks": []},
        },
    },
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Jar cure. Burp daily for 2 weeks, then weekly. 4-8 weeks ideal.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "light_hours": 0,
        },
        "reservoir": {"notes": "System ready for next cycle."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {"name": "Burp jars", "description": "Daily 2 weeks, then weekly.", "interval_days": 1, "priority": "high"},
            {
                "name": "Monitor humidity",
                "description": "58-62%. Boveda 62 packs.",
                "interval_days": 1,
                "priority": "medium",
            },
        ],
        "health_checks": ["Humidity in range?", "No ammonia?", "No mold?"],
        "common_problems": [
            {"issue": "Ammonia smell", "cause": "Jarred too wet", "solution": "Remove, dry 12-24h, re-jar."},
        ],
        "transition_signals": ["Smooth smoke", "Full terpenes", "No hay smell"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT
# ─────────────────────────────────────────────────────────────────────────────

DUTCH_BUCKET_EQUIPMENT: list[dict] = [
    {
        "name": "Dutch/Bato buckets (3-5 gal)",
        "category": "essential",
        "essential": True,
        "description": "Individual containers with siphon elbow drain. 3.5 gal standard.",
    },
    {
        "name": "Reservoir (50-100 gal)",
        "category": "essential",
        "essential": True,
        "description": "Shared nutrient reservoir. Size based on bucket count.",
    },
    {
        "name": "Feed pump (submersible)",
        "category": "essential",
        "essential": True,
        "description": "Pumps from reservoir to drip manifold.",
    },
    {
        "name": "Drip manifold + emitters",
        "category": "essential",
        "essential": True,
        "description": "Mainline, branches, and drip stakes per bucket.",
    },
    {
        "name": "Return/drain line",
        "category": "essential",
        "essential": True,
        "description": "Shared drain collecting runoff from all buckets.",
    },
    {
        "name": "Siphon elbows",
        "category": "essential",
        "essential": True,
        "description": "Maintains 1-2 inch water level in bucket bottom.",
    },
    {
        "name": "Digital timer",
        "category": "essential",
        "essential": True,
        "description": "Controls feed pump cycles. Minute-precision.",
    },
    {
        "name": "Growing media (perlite/hydroton/coco)",
        "category": "essential",
        "essential": True,
        "description": "Fills each bucket. Perlite most common.",
    },
    {
        "name": "Inline filter",
        "category": "recommended",
        "essential": False,
        "description": "Screen filter between pump and emitters.",
    },
    {
        "name": "pH/EC meters",
        "category": "essential",
        "essential": True,
        "description": "Monitor reservoir and runoff.",
    },
    {
        "name": "Air pump + stones",
        "category": "recommended",
        "essential": False,
        "description": "Aerate reservoir. Prevents stagnation.",
    },
    {
        "name": "Float valve",
        "category": "recommended",
        "essential": False,
        "description": "Auto-top-off reservoir from water line.",
    },
    {
        "name": "Drain catch trays",
        "category": "recommended",
        "essential": False,
        "description": "Funnel runoff to drain line.",
    },
    {
        "name": "Bucket stands/rail",
        "category": "optional",
        "essential": False,
        "description": "Elevated for gravity drain to reservoir.",
    },
    {
        "name": "UV sterilizer",
        "category": "optional",
        "essential": False,
        "description": "For recirculating setups. Prevents pathogen spread.",
    },
    {
        "name": "Backup pump",
        "category": "optional",
        "essential": False,
        "description": "Redundancy for critical feed system.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

DUTCH_BUCKET_QUICK_REFERENCE: dict = {
    "method_summary": "Individual media-filled buckets with shared top-feed drip and common drain line. Recirculating or drain-to-waste.",
    "difficulty": "intermediate",
    "maintenance_level": "Medium — daily reservoir checks, weekly emitter/drain inspection.",
    "key_advantages": [
        "Scalable (4 to 400+ buckets)",
        "Individual plant control",
        "Media buffer (forgiving)",
        "Staggered harvest",
        "Commercial proven",
    ],
    "key_challenges": [
        "Emitter clogging",
        "Uneven flow at scale",
        "Disease spread in recirculating mode",
        "Salt buildup over time",
    ],
    "feed_schedule": {
        "seedling": "15 min on / 60 min off",
        "veg": "15 min on / 30 min off (lights on)",
        "flower": "15 min on / 15 min off or continuous",
    },
    "critical_rules": [
        "Every bucket MUST have a siphon elbow",
        "Aim for 20-30% runoff to prevent salt buildup",
        "Clean inline filter weekly",
        "DTW for disease prevention in commercial settings",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING
# ─────────────────────────────────────────────────────────────────────────────

DUTCH_BUCKET_TROUBLESHOOTING: list[dict] = [
    {
        "category": "feed_system",
        "issues": [
            {
                "symptom": "Emitter clogged",
                "cause": "Mineral deposits or debris",
                "solution": "Soak in vinegar/H2O2. Check inline filter.",
            },
            {
                "symptom": "Uneven flow between buckets",
                "cause": "Pressure drop or partial clogs",
                "solution": "Pressure-compensating emitters. Shorten runs. Clean all.",
            },
            {
                "symptom": "Pump running but no flow",
                "cause": "Clogged impeller or air-lock",
                "solution": "Clean pump intake. Ensure submerged. Prime.",
            },
        ],
    },
    {
        "category": "drain_system",
        "issues": [
            {
                "symptom": "Bucket overflowing",
                "cause": "Clogged siphon elbow or drain blockage",
                "solution": "Clear siphon. Check for root intrusion. Snake drain.",
            },
            {
                "symptom": "Drain line backing up",
                "cause": "Insufficient slope or blockage",
                "solution": "Minimum 1/4 in/ft slope. Clear blockage. Larger pipe.",
            },
            {
                "symptom": "Standing water above siphon level",
                "cause": "Siphon installed wrong",
                "solution": "Reinstall at correct height (1-2 inch pool).",
            },
        ],
    },
    {
        "category": "nutrient_issues",
        "issues": [
            {
                "symptom": "EC climbing in reservoir",
                "cause": "Plants taking more water than nutrients",
                "solution": "Top off with plain water. Reduce base EC.",
            },
            {
                "symptom": "pH swinging wildly",
                "cause": "Inadequate buffering or root rot",
                "solution": "Larger reservoir. Fresh nutrient change. Check roots.",
            },
            {
                "symptom": "Different deficiencies per bucket",
                "cause": "Uneven feed or genetics",
                "solution": "Check individual emitter flow. Adjust per-plant.",
            },
        ],
    },
    {
        "category": "disease_control",
        "issues": [
            {
                "symptom": "Root rot spreading",
                "cause": "Recirculating system spreading pathogens",
                "solution": "Switch to DTW. H2O2. UV sterilizer. Isolate affected.",
            },
            {
                "symptom": "Algae in lines",
                "cause": "Light exposure to solution",
                "solution": "Light-proof all lines/reservoir. H2O2 clean.",
            },
            {
                "symptom": "Pythium in one bucket",
                "cause": "Overwatering or dead roots",
                "solution": "Isolate bucket. Beneficial microbes. H2O2 drench.",
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# DUTCH BUCKET SYSTEM — Core differentiator
# ─────────────────────────────────────────────────────────────────────────────

DUTCH_BUCKET_SYSTEM: dict = {
    "bucket_design": {
        "standard_size_gal": 3.5,
        "siphon_elbow": {
            "purpose": "Maintains 1-2 inch reservoir in bucket bottom for continuous root moisture.",
            "height_inches": {"min": 1, "max": 2, "recommended": 1.5},
            "material": "PVC elbow in drain hole",
        },
        "media_selection": {
            "perlite": {
                "water_retention": "low",
                "drainage": "excellent",
                "reusability": "single-use",
                "best_for": "Commercial, fast turnaround",
            },
            "hydroton": {
                "water_retention": "low",
                "drainage": "excellent",
                "reusability": "sterilize + reuse",
                "best_for": "Permanent installations",
            },
            "coco_coir": {
                "water_retention": "high",
                "drainage": "good",
                "reusability": "single-use",
                "best_for": "Longer feed intervals",
            },
        },
    },
    "drain_line_engineering": {
        "material": "2-inch PVC or food-grade poly",
        "slope_min_inches_per_foot": 0.25,
        "dtw_vs_recirculating": {
            "drain_to_waste": {
                "advantages": ["Zero disease transmission", "Fresh nutrients always", "Simpler system"],
                "best_for": "Commercial",
            },
            "recirculating": {
                "advantages": ["50-70% less water/nutrient usage", "Lower cost"],
                "best_for": "Hobby, water-scarce areas",
            },
        },
    },
    "top_feed_configuration": {
        "mainline": "3/4-inch poly tubing from pump",
        "branch_lines": "1/4-inch spaghetti tubing, max 24 inches",
        "emitters": {
            "type": "Pressure-compensating drip stakes",
            "flow_rate_gph": {"min": 1, "max": 4, "recommended": 2},
            "per_bucket": {"small_plant": 1, "large_plant": 2},
        },
    },
    "scalability": {
        "hobby_4_to_8": {"reservoir_gal": 30, "pump_gph": 200, "notes": "Simple single run."},
        "mid_12_to_24": {"reservoir_gal": 75, "pump_gph": 500, "notes": "Loop design. PC emitters essential."},
        "commercial_50_plus": {
            "reservoir_gal": 200,
            "pump_gph": 1000,
            "notes": "Multiple zones. Auto-dosing mandatory.",
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLED CONFIG EXPORT
# ─────────────────────────────────────────────────────────────────────────────

DUTCH_BUCKET_CONFIG: dict = {
    "grow_type_id": "dutch_bucket",
    "version": "1.0.0",
    "stages": DUTCH_BUCKET_STAGES,
    "equipment": DUTCH_BUCKET_EQUIPMENT,
    "quick_reference": DUTCH_BUCKET_QUICK_REFERENCE,
    "troubleshooting": DUTCH_BUCKET_TROUBLESHOOTING,
    "dutch_bucket_system": DUTCH_BUCKET_SYSTEM,
    "total_grow_days": {"min": 105, "max": 210, "typical": 150},
}
