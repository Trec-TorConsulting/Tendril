"""Wicking Bed (Sub-Irrigated Planter) — Complete grow type configuration.

Enterprise-grade configuration for wicking bed / sub-irrigated planter (SIP)
growing. Passive capillary action draws water from sub-surface reservoir up
through media to plant roots. Zero pumps, zero electricity, low maintenance.

Data sources:
  - Sub-irrigated planter research (Cornell, extension services)
  - Wicking bed community best practices
  - Cannabis SIP/wicking growers (forums, YouTube)
  - Capillary irrigation science
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — 13 stages from germination through curing
# ─────────────────────────────────────────────────────────────────────────────

WICKING_STAGES: list[dict] = [
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Germinate separately from wicking bed. Paper towel or starter plug. Pre-saturate wicking bed reservoir so media is ready.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
        },
        "reservoir": {"notes": "Fill reservoir with plain water. Let media saturate 24-48h before planting."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Germinate seeds",
                "description": "Paper towel method. 78°F, dark, moist.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Pre-saturate wicking bed",
                "description": "Fill reservoir to overflow. Let media wick upward fully.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Check germination",
                "description": "Look for taproot emergence.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Seed cracking?", "Wicking bed media saturating evenly?"],
        "common_problems": [
            {
                "issue": "Media not wicking",
                "cause": "Air pockets or media too coarse",
                "solution": "Repack wicking layer. Use finer media above reservoir.",
            },
        ],
        "transition_signals": ["Taproot emerged", "Wicking bed fully saturated"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Germinate indoors. Bed can saturate outdoors."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Greenhouse propagation works well."}, "extra_tasks": []},
        },
    },
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Transplant seedling into wicking bed. Top-water for first 3-5 days until roots reach capillary zone, then let wicking take over.",
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
            "refill_interval_days": 5,
            "notes": "Keep full. Top-water seedling directly until roots reach moisture zone.",
        },
        "nutrients": {"strength_pct": 25, "approach": "1/4 strength in reservoir or light organic top-dress."},
        "tasks": [
            {
                "name": "Transplant to bed",
                "description": "Plant in top soil layer. Roots grow down to moisture zone.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Top-water daily",
                "description": "Light watering from above for 3-5 days until wicking takes over.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check reservoir level",
                "description": "Use sight tube or dipstick. Never let it empty.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Mulch surface",
                "description": "1-2 inch mulch to prevent evaporation and salt crust.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Seedling growing new leaves?", "Reservoir level adequate?", "Soil surface not waterlogged?"],
        "common_problems": [
            {
                "issue": "Seedling wilting despite full reservoir",
                "cause": "Roots haven't reached wicking zone",
                "solution": "Continue top-watering. Patience — takes 3-7 days.",
            },
            {
                "issue": "Mosquitoes in reservoir",
                "cause": "Standing water accessible",
                "solution": "Screen openings. BTI dunks in reservoir.",
            },
        ],
        "transition_signals": [
            "Growing without top-watering",
            "3-4 sets of true leaves",
            "No wilting between reservoir checks",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Wicking beds ideal outdoors — self-watering."},
                "extra_tasks": [
                    {
                        "name": "Mosquito prevention",
                        "description": "Seal reservoir access. BTI dunks.",
                        "interval_days": 14,
                        "priority": "medium",
                    }
                ],
            },
            "greenhouse": {"environment_overrides": {"notes": "Low-labor greenhouse setup."}, "extra_tasks": []},
        },
    },
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Roots have reached capillary zone. Plant is self-watering from reservoir. Low maintenance — just refill reservoir and watch for salt crust.",
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
            "refill_interval_days": {"min": 4, "max": 7, "typical": 5},
            "notes": "Small plants drink less. Check twice per week.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half-strength veg nutrients in reservoir OR organic top-dress (worm castings + kelp).",
        },
        "tasks": [
            {
                "name": "Refill reservoir",
                "description": "Check 2x/week via sight tube. Never let empty.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Top-water flush",
                "description": "Flush from top every 2-3 weeks to clear surface salts.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Check for salt crust",
                "description": "White crust on surface? Scrape off and flush.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Begin training",
                "description": "LST or topping at 5th node.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["Reservoir level?", "Salt crust forming?", "Vigorous growth?", "Overflow drain clear?"],
        "common_problems": [
            {
                "issue": "Salt crust on surface",
                "cause": "Minerals wick up and deposit via evaporation",
                "solution": "Top-water flush. Mulch layer. Reduce reservoir nutrient concentration.",
            },
            {
                "issue": "Slow growth",
                "cause": "Nutrients not reaching roots (too dilute in reservoir)",
                "solution": "Increase reservoir nutrient strength. Top-dress amendments.",
            },
        ],
        "transition_signals": ["5-6 nodes developed", "Vigorous daily growth", "Roots firmly in moisture zone"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Outdoor wicking beds are self-sufficient in early veg."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Minimal intervention needed."}, "extra_tasks": []},
        },
    },
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 14, "max": 35, "typical": 21},
        "description": "Plants growing aggressively. Reservoir consumption increases. Training to fill canopy. Wicking beds produce vigorous, healthy plants due to constant moisture.",
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
            "refill_interval_days": {"min": 3, "max": 5, "typical": 4},
            "notes": "Larger plants drink more. May need refills every 3-4 days.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "3/4 strength veg in reservoir. Top-dress organics every 2-3 weeks.",
        },
        "tasks": [
            {
                "name": "Refill reservoir",
                "description": "Every 3-4 days. Plants drinking more now.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Top-water flush",
                "description": "Flush surface salts every 2 weeks.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Top-dress amendments",
                "description": "Worm castings + kelp meal on surface. Water in lightly.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Train canopy",
                "description": "LST/SCROG to fill space. Consistent moisture = fast recovery from training.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["Reservoir consumption rate predictable?", "Canopy filling evenly?", "No deficiencies?"],
        "common_problems": [
            {
                "issue": "Reservoir emptying too fast",
                "cause": "Large plant mass, hot conditions",
                "solution": "Larger reservoir or more frequent refills. Float valve for auto-fill.",
            },
            {
                "issue": "Anaerobic reservoir",
                "cause": "Stagnant water decomposing organic matter",
                "solution": "Flush reservoir. Don't add organic teas directly. Small air stone optional.",
            },
        ],
        "transition_signals": ["Canopy 50-60% full", "Ready for flip", "Healthy vigorous growth"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Peak summer consumption. Check daily in heat."},
                "extra_tasks": [
                    {
                        "name": "Daily reservoir check in heat",
                        "description": "Hot days = 2+ gal/day consumption.",
                        "interval_days": 1,
                        "priority": "high",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Monitor reservoir more in warm greenhouse."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Flip to 12/12. Plants stretch 50-100%. Wicking bed handles increased water demand effortlessly. Begin transitioning nutrients to bloom.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 64, "max": 72, "target": 68},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.0, "max": 1.3, "target": 1.1},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 800, "target": 700},
            "light_dli": {"min": 25, "max": 35, "target": 30},
        },
        "reservoir": {
            "refill_interval_days": {"min": 2, "max": 4, "typical": 3},
            "notes": "Stretching plants increase water uptake. Check every 2-3 days.",
        },
        "nutrients": {"strength_pct": 75, "approach": "Transition to bloom nutrients. 50/50 veg/bloom in reservoir."},
        "tasks": [
            {
                "name": "Flip light schedule",
                "description": "Switch to 12/12.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Refill reservoir",
                "description": "Stretching increases demand.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Manage stretch",
                "description": "LST/supercropping if needed for height control.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Switch nutrients",
                "description": "Begin transitioning to bloom formula in reservoir.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Stretch managed?", "Reservoir keeping up?", "No nutrient burn from transition?"],
        "common_problems": [
            {
                "issue": "Excessive stretch",
                "cause": "Genetics or insufficient light",
                "solution": "Supercrop tall branches. Increase light intensity.",
            },
        ],
        "transition_signals": ["Stretch slowing", "Pre-flowers visible", "Pistils emerging"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Natural photoperiod triggers transition. No manual flip needed."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Use blackout covers for photoperiod control if needed."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Bud sites forming. Increased nutrient demand. Wicking bed provides consistent moisture ideal for flower development. Switch fully to bloom nutrients.",
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
            "refill_interval_days": {"min": 2, "max": 4, "typical": 3},
            "notes": "Flowering plants have peak water demand. Monitor closely.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom nutrients in reservoir. High P-K. Organic: bone meal + langbeinite top-dress.",
        },
        "tasks": [
            {
                "name": "Refill reservoir",
                "description": "Peak demand. Every 2-3 days.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Remove fan leaves blocking bud sites.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Top-water flush",
                "description": "Continue flushing surface salts every 2 weeks.",
                "interval_days": 14,
                "priority": "medium",
            },
        ],
        "health_checks": ["Bud sites developing?", "Airflow adequate?", "No deficiencies?", "Humidity below 55%?"],
        "common_problems": [
            {
                "issue": "Nutrient burn on tips",
                "cause": "Reservoir too concentrated + salt buildup",
                "solution": "Dilute reservoir. Top-water flush to clear salts.",
            },
        ],
        "transition_signals": ["Buds forming at all sites", "White pistils abundant", "Stretch complete"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Watch for caterpillars and bud rot as buds form."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Good airflow critical as buds develop."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "mid_flower",
        "name": "Mid Flower (Bulk Phase)",
        "order": 7,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Peak bud development. Maximum nutrient and water demand. Wicking bed's consistent moisture shines here — no wet/dry stress means better bud quality.",
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
            "refill_interval_days": {"min": 2, "max": 3, "typical": 2},
            "notes": "Peak consumption. Large plants may need daily checks.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom nutrients. Consider PK booster weeks 4-6 of flower.",
        },
        "tasks": [
            {
                "name": "Refill reservoir",
                "description": "Every 2 days. Peak demand period.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Monitor bud development",
                "description": "Check for rot, pests, deficiencies.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Support heavy buds",
                "description": "Trellis or stakes for heavy colas.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Buds swelling?",
            "No bud rot?",
            "Trichomes developing?",
            "Reservoir keeping up with demand?",
        ],
        "common_problems": [
            {
                "issue": "Bud rot",
                "cause": "Dense buds + humidity from wicking surface",
                "solution": "Defoliate. Good airflow. Mulch reduces surface evaporation. Keep humidity < 50%.",
            },
            {
                "issue": "Reservoir empties daily",
                "cause": "Peak consumption from large flowering plant",
                "solution": "Larger reservoir. Float valve auto-fill. Top-feed supplement if needed.",
            },
        ],
        "transition_signals": ["Buds dense and filling in", "Trichomes visible", "Pistils starting to orange"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Rain on buds = rot. Cover during rain events."},
                "extra_tasks": [
                    {
                        "name": "Rain protection",
                        "description": "Cover buds during rain.",
                        "interval_days": 1,
                        "priority": "high",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Ideal rain protection. Monitor humidity."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Final ripening. Trichomes maturing. Reduce nutrient strength. Wicking bed's gentle delivery suits this phase well — no dramatic swings.",
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
            "refill_interval_days": {"min": 2, "max": 4, "typical": 3},
            "notes": "Consumption may slightly decrease as plant ripens.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Reduce to 75% bloom. Stop PK boosters. Some growers begin reducing for final flush.",
        },
        "tasks": [
            {
                "name": "Check trichomes",
                "description": "Magnification. Looking for milky with some amber.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Reduce nutrients",
                "description": "Lower reservoir strength. Preparing for flush.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Inspect for bud rot",
                "description": "Daily inspection of dense buds.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Trichome color progression?", "No rot or mold?", "Pistils mostly orange?"],
        "common_problems": [
            {
                "issue": "Trichomes not maturing",
                "cause": "Light too intense or too warm",
                "solution": "Slightly reduce light intensity. Ensure night temps drop for color development.",
            },
        ],
        "transition_signals": ["70-80% milky trichomes", "10-20% amber", "Pistils mostly receded"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Fall temps help color development. Watch for early frost."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Can manipulate temp drop for color/terpenes."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Final salt flush. Fill reservoir with plain pH'd water. Top-water flush heavily from above to push salts down and out through overflow. Wicking beds flush beautifully — top-water pushes through entire soil column.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 72},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 48, "target": 42},
            "vpd_kpa": {"min": 1.2, "max": 1.5, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 17, "max": 30, "target": 26},
        },
        "reservoir": {"notes": "Plain pH'd water only. No nutrients. Drain and refill reservoir with clean water."},
        "nutrients": {"strength_pct": 0, "approach": "Plain water only. Flush all nutrients from reservoir and soil."},
        "tasks": [
            {
                "name": "Drain and refill reservoir",
                "description": "Empty nutrient water. Refill with plain pH'd water.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Heavy top-water flush",
                "description": "Flush from top to push salts through entire bed and out overflow.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Monitor plant fade",
                "description": "Yellowing fan leaves = plant using stored nutrients. Good sign.",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Fan leaves yellowing (desired)?",
            "Buds still healthy?",
            "Salt crust clearing from surface?",
        ],
        "common_problems": [
            {
                "issue": "No fade after 10 days",
                "cause": "Organic soil has too many stored nutrients",
                "solution": "Continue flush longer. Living soil may not fully flush — that's OK.",
            },
        ],
        "transition_signals": [
            "Fan leaves yellowed/falling",
            "7-14 days plain water complete",
            "Trichomes at target maturity",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Rain helps flush naturally. Let it rain on the bed."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Standard flush procedure."}, "extra_tasks": []},
        },
    },
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Chop plant. Wicking bed can be left to rest or immediately prepared for next cycle (refill, amend soil, plant cover crop).",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
        },
        "reservoir": {"notes": "Empty or leave with plain water for cover crop / next cycle prep."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Chop plant",
                "description": "Cut at base. Leave roots in soil (they decompose and feed biology).",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Wet or dry trim",
                "description": "Preference. Wet trim for faster dry, dry trim for slower cure.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Prep bed for next cycle",
                "description": "Top-dress fresh amendments. Plant cover crop. Or let rest.",
                "interval_days": None,
                "priority": "low",
            },
        ],
        "health_checks": ["Trichomes at target?", "Harvest window correct?"],
        "common_problems": [
            {
                "issue": "Harvested too early",
                "cause": "Impatience or unclear trichome reading",
                "solution": "Use 60x loupe. Target 70-80% milky, 10-20% amber.",
            },
        ],
        "transition_signals": ["Plant chopped", "Branches hung for drying"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Harvest before frost. Bring inside to dry."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Harvest and dry indoors."}, "extra_tasks": []},
        },
    },
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Standard hang dry. 60°F, 60% RH, complete darkness. Slow dry preserves terpenes.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "light_hours": 0,
        },
        "reservoir": {"notes": "Bed resting. Can prep for next cycle during this time."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Check drying conditions",
                "description": "60-65°F, 55-62% RH. Complete darkness.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Stem snap test",
                "description": "Small stems snap = ready for jars.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": ["Drying conditions correct?", "No mold?", "Even drying?"],
        "common_problems": [
            {
                "issue": "Drying too fast",
                "cause": "Humidity too low or temp too high",
                "solution": "Slow down: lower temp, raise humidity, larger whole-plant hangs.",
            },
        ],
        "transition_signals": ["Small stems snap", "Buds slightly crispy outside, still moist inside"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Always dry indoors in controlled environment."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Dry indoors, not in greenhouse."}, "extra_tasks": []},
        },
    },
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Jar cure. Burp daily for 2 weeks, then weekly. Minimum 2-week cure, 4-8 weeks ideal.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "light_hours": 0,
        },
        "reservoir": {"notes": "Bed resting or already growing next cycle."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Burp jars",
                "description": "Daily for 2 weeks, then weekly.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor humidity",
                "description": "58-62% in jars. Boveda 62% packs help.",
                "interval_days": 1,
                "priority": "medium",
            },
        ],
        "health_checks": ["Humidity 58-62%?", "No ammonia smell?", "No mold?"],
        "common_problems": [
            {
                "issue": "Ammonia smell",
                "cause": "Jarred too wet — anaerobic bacteria",
                "solution": "Dump out, dry another 12-24h, re-jar.",
            },
        ],
        "transition_signals": ["Smooth smoke", "Full terpene profile developed", "No hay/grass smell"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Cure indoors in stable environment."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT
# ─────────────────────────────────────────────────────────────────────────────

WICKING_EQUIPMENT: list[dict] = [
    {
        "name": "Wicking bed container",
        "category": "essential",
        "essential": True,
        "description": "DIY tote, raised bed, or commercial SIP planter. Must be waterproof on bottom half.",
    },
    {
        "name": "Reservoir layer material",
        "category": "essential",
        "essential": True,
        "description": "Gravel, scoria, or purpose-built false floor to create sub-surface water reservoir.",
    },
    {
        "name": "Geotextile fabric",
        "category": "essential",
        "essential": True,
        "description": "Separates reservoir from soil above. Allows water through, keeps soil out of reservoir.",
    },
    {
        "name": "Overflow drain fitting",
        "category": "essential",
        "essential": True,
        "description": "Positioned at top of reservoir layer. Prevents waterlogging soil. CRITICAL safety feature.",
    },
    {
        "name": "Fill pipe (PVC)",
        "category": "essential",
        "essential": True,
        "description": "Vertical pipe from surface down into reservoir for easy refilling without disturbing soil.",
    },
    {
        "name": "Growing medium",
        "category": "essential",
        "essential": True,
        "description": "Quality potting soil or living soil mix. Must have capillary properties (not too coarse).",
    },
    {
        "name": "Sight tube or dipstick",
        "category": "recommended",
        "essential": False,
        "description": "Clear tube connected to reservoir to visually check water level without disturbing anything.",
    },
    {
        "name": "Mulch material",
        "category": "recommended",
        "essential": False,
        "description": "Straw, wood chips, or rice hulls. 2-3 inches on surface to reduce evaporation and salt migration.",
    },
    {
        "name": "BTI mosquito dunks",
        "category": "recommended",
        "essential": False,
        "description": "Biological mosquito larvicide safe for plants. Essential for outdoor wicking beds.",
    },
    {
        "name": "Nutrients (liquid or organic)",
        "category": "essential",
        "essential": True,
        "description": "Liquid feed for reservoir or dry organic amendments for top-dressing.",
    },
    {
        "name": "pH meter",
        "category": "recommended",
        "essential": False,
        "description": "Monitor reservoir water pH. Target 6.0-6.8 for soil-based wicking.",
    },
    {
        "name": "EC meter",
        "category": "recommended",
        "essential": False,
        "description": "Monitor nutrient concentration in reservoir.",
    },
    {
        "name": "Wicking material (optional)",
        "category": "optional",
        "essential": False,
        "description": "Fabric wicks or capillary matting if media alone doesn't wick well. Usually not needed with proper media.",
    },
    {
        "name": "Float valve",
        "category": "optional",
        "essential": False,
        "description": "Auto-refill from water line. Perfect for vacation growing or large beds.",
    },
    {
        "name": "Small air stone + pump",
        "category": "optional",
        "essential": False,
        "description": "Prevents anaerobic conditions in reservoir. Useful if using organic nutrients in reservoir.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

WICKING_QUICK_REFERENCE: dict = {
    "method_summary": "Passive self-watering via capillary action from sub-surface reservoir. Zero pumps, zero electricity.",
    "difficulty": "beginner",
    "maintenance_level": "Very low — refill reservoir every 3-7 days, flush salts every 2-3 weeks.",
    "key_advantages": [
        "Zero electricity needed",
        "Self-watering (vacation-proof)",
        "Cannot overwater (overflow prevents it)",
        "Extremely low maintenance",
        "Works with organic or synthetic",
    ],
    "key_challenges": [
        "Surface salt buildup",
        "Cannot let reservoir fully empty (breaks capillary action)",
        "Slower nutrient delivery than active hydro",
        "Limited control vs precision systems",
    ],
    "reservoir_refill_schedule": {
        "seedling": "Every 5-7 days",
        "veg": "Every 3-5 days",
        "flower": "Every 2-3 days",
    },
    "nutrient_approach": {
        "synthetic": "Add to reservoir water at 50-75% recommended strength",
        "organic": "Top-dress amendments (worm castings, kelp, bone meal) every 2-3 weeks",
        "hybrid": "Organic soil + light liquid feed in reservoir",
    },
    "critical_rules": [
        "NEVER let reservoir fully empty — breaks capillary continuity",
        "Top-water flush every 2-3 weeks to prevent salt lockout",
        "Overflow drain is non-negotiable — prevents soil waterlogging",
        "Mulch surface to reduce evaporation and salt migration",
        "Screen all openings against mosquitoes (standing water = breeding)",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING
# ─────────────────────────────────────────────────────────────────────────────

WICKING_TROUBLESHOOTING: list[dict] = [
    {
        "category": "reservoir",
        "issues": [
            {
                "symptom": "Reservoir empties in 1-2 days",
                "cause": "Reservoir too small for plant size or hot conditions",
                "solution": "Larger reservoir, float valve auto-fill, or more frequent refills.",
            },
            {
                "symptom": "Reservoir water smells bad",
                "cause": "Anaerobic conditions from stagnant organic matter",
                "solution": "Drain and refill with clean water. Add air stone. Avoid organic teas in reservoir.",
            },
            {
                "symptom": "Reservoir won't fill (water runs out overflow immediately)",
                "cause": "Overflow drain too low or reservoir layer compromised",
                "solution": "Check overflow height — should be at TOP of reservoir layer. Ensure no cracks/leaks below overflow.",
            },
        ],
    },
    {
        "category": "capillary_action",
        "issues": [
            {
                "symptom": "Soil surface bone dry despite full reservoir",
                "cause": "Capillary break — air gap between soil and reservoir, or media too coarse",
                "solution": "Top-water heavily to re-establish capillary continuity. May need to re-pack media. Use finer-textured soil.",
            },
            {
                "symptom": "Soil surface too wet/waterlogged",
                "cause": "Overflow too high or media wicking too aggressively",
                "solution": "Lower overflow height. Add coarser layer between reservoir and soil. Improve drainage in top layer.",
            },
            {
                "symptom": "Uneven moisture (wet on one side, dry on other)",
                "cause": "Bed not level or wicking layer unevenly packed",
                "solution": "Level the bed. May need to rebuild wicking layer for even distribution.",
            },
        ],
    },
    {
        "category": "nutrient_issues",
        "issues": [
            {
                "symptom": "White salt crust on soil surface",
                "cause": "Minerals wicking up and depositing via evaporation",
                "solution": "Top-water flush. Scrape off crust. Mulch surface. Reduce reservoir nutrient concentration.",
            },
            {
                "symptom": "Nutrient lockout despite feeding",
                "cause": "Salt buildup in soil from upward wicking",
                "solution": "Heavy top-water flush (3x pot volume). Reset reservoir nutrients at lower concentration.",
            },
            {
                "symptom": "Deficiency symptoms despite nutrients in reservoir",
                "cause": "pH drift in reservoir or root zone",
                "solution": "Check reservoir pH (target 6.0-6.8). Flush and reset.",
            },
        ],
    },
    {
        "category": "pests_disease",
        "issues": [
            {
                "symptom": "Mosquitoes breeding in reservoir",
                "cause": "Standing water accessible to egg-laying mosquitoes",
                "solution": "Screen all openings with fine mesh. Add BTI dunks (safe for plants). Seal fill pipe cap.",
            },
            {
                "symptom": "Fungus gnats on soil surface",
                "cause": "Constantly moist surface attracts gnats",
                "solution": "Mulch layer (deters egg-laying). Yellow sticky traps. Let surface dry between flushes. BTI in top-water.",
            },
            {
                "symptom": "Root rot",
                "cause": "Saturated zone too high — roots sitting in standing water",
                "solution": "Check overflow drain position (defines saturation line). Top 4-6 inches MUST be above saturation.",
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# CAPILLARY SYSTEM — Wicking's core differentiator
# ─────────────────────────────────────────────────────────────────────────────

WICKING_CAPILLARY_SYSTEM: dict = {
    "bed_construction": {
        "layers_bottom_to_top": [
            {
                "layer": "Container base",
                "depth_inches": 0,
                "material": "Waterproof container (tote, raised bed with pond liner, commercial SIP)",
                "notes": "Must hold water without leaking.",
            },
            {
                "layer": "Reservoir",
                "depth_inches": {"min": 4, "max": 8, "recommended": 6},
                "material": "Gravel, scoria, perlite, or false floor with void space",
                "notes": "This IS the water reservoir. Holds water below overflow drain.",
            },
            {
                "layer": "Geotextile barrier",
                "depth_inches": 0,
                "material": "Landscape fabric or geotextile",
                "notes": "Allows water through but keeps soil from filling reservoir voids.",
            },
            {
                "layer": "Wicking/transition layer",
                "depth_inches": {"min": 2, "max": 4},
                "material": "Fine perlite, sand, or wicking fabric bridge",
                "notes": "Creates capillary bridge between reservoir and soil above.",
            },
            {
                "layer": "Growing medium",
                "depth_inches": {"min": 8, "max": 14, "recommended": 12},
                "material": "Quality potting soil, living soil, or soilless mix (must wick)",
                "notes": "Top 4-6 inches should be ABOVE capillary saturation point.",
            },
            {
                "layer": "Mulch",
                "depth_inches": {"min": 2, "max": 4},
                "material": "Straw, wood chips, rice hulls, or living cover crop",
                "notes": "Prevents evaporation and salt migration to surface.",
            },
        ],
        "overflow_drain": {
            "position": "At the TOP of the reservoir layer (where geotextile begins)",
            "purpose": "Prevents water from rising into soil (waterlogging). Defines the maximum saturation line.",
            "critical": True,
            "sizing": "3/4 inch minimum fitting. Flush with inside wall of container.",
        },
        "fill_pipe": {
            "material": "1.5-2 inch PVC pipe, vertical, from surface down into reservoir",
            "position": "Corner or edge of bed. Cap on top (mosquito prevention).",
            "purpose": "Refill reservoir without disturbing soil surface.",
        },
    },
    "capillary_science": {
        "how_it_works": "Water moves upward through small pore spaces in soil via capillary action (surface tension). Finer particles = higher wicking height but slower rate. Balance is key.",
        "wicking_height_by_media": {
            "fine_sand": {
                "max_height_inches": 24,
                "rate": "slow",
                "notes": "Wicks highest but very slow. Too fine for most growing.",
            },
            "potting_soil": {
                "max_height_inches": 12,
                "rate": "moderate",
                "notes": "Ideal balance of height and speed for wicking beds.",
            },
            "perlite": {
                "max_height_inches": 6,
                "rate": "fast",
                "notes": "Fast wicking but limited height. Good for reservoir layer, not grow layer alone.",
            },
            "coarse_gravel": {
                "max_height_inches": 1,
                "rate": "none",
                "notes": "Does not wick. Used for reservoir voids only.",
            },
            "coco_coir": {
                "max_height_inches": 10,
                "rate": "moderate-fast",
                "notes": "Excellent wicking material. Great in mixes.",
            },
        },
        "ideal_soil_recipe": {
            "components": [
                "40% quality compost/potting soil",
                "30% coco coir (excellent wicking)",
                "20% perlite (aeration in top layer)",
                "10% worm castings (nutrition + biology)",
            ],
            "notes": "This mix wicks well (coco + compost) while providing aeration (perlite) in the upper zone where roots need oxygen.",
        },
        "capillary_break": {
            "what": "Air gap that stops capillary action. Once broken, water cannot wick past the gap.",
            "cause": "Reservoir fully emptying, or air pocket forming between layers.",
            "consequence": "Soil above break dries out. Plant wilts. Re-establishing requires heavy top-watering.",
            "prevention": "NEVER let reservoir fully empty. Keep at minimum 25% level. Ensure no air pockets in wicking layer.",
        },
    },
    "reservoir_management": {
        "sizing_rule": "Minimum 1/3 of total bed volume should be reservoir. Bigger = less frequent refills.",
        "sizing_examples": {
            "small_tote_20gal": {"reservoir_gal": 7, "soil_gal": 13, "refill_days": "3-5"},
            "medium_bed_50gal": {"reservoir_gal": 17, "soil_gal": 33, "refill_days": "5-7"},
            "large_bed_100gal": {"reservoir_gal": 35, "soil_gal": 65, "refill_days": "7-14"},
        },
        "nutrient_delivery_via_reservoir": {
            "method": "Add liquid nutrients to fill water at reduced strength (50-75% of label)",
            "ph_target": {"min": 6.0, "max": 6.8, "target": 6.3},
            "ec_target": {"veg": {"min": 0.5, "max": 1.0}, "flower": {"min": 0.8, "max": 1.4}},
            "caution": "Nutrients concentrate as water evaporates. Start conservative. Flush regularly from top.",
        },
        "anaerobic_prevention": [
            "Don't add organic teas or particulate matter directly to reservoir (decomposition uses oxygen)",
            "Optional: small aquarium air stone keeps water oxygenated",
            "If reservoir smells sulfurous: drain completely, refill with fresh water",
            "Use clean, filtered water for reservoir fills",
        ],
    },
    "salt_management": {
        "mechanism": "Water wicks UP carrying dissolved minerals. Water evaporates at surface. Minerals deposit as white crust. This is the #1 maintenance challenge of wicking beds.",
        "prevention": [
            "Mulch layer (2-3 inches) — dramatically reduces surface evaporation and salt deposition",
            "Lower nutrient concentration in reservoir (less minerals to deposit)",
            "Regular top-water flushes push salts back down through soil",
            "Organic growing with top-dress amendments avoids reservoir-based salt issues",
        ],
        "flush_protocol": [
            "Every 2-3 weeks (or when white crust visible): water heavily from TOP",
            "Use plain pH'd water, enough to flow out the overflow drain",
            "This pushes accumulated salts downward and out",
            "Wait 24h then resume reservoir feeding",
            "If crust is severe: scrape off surface layer, flush, then re-mulch",
        ],
    },
    "failure_modes": [
        {
            "failure": "Capillary break (reservoir empty)",
            "severity": "high",
            "time_to_damage": "24-48 hours depending on conditions",
            "response": "Refill reservoir AND top-water heavily to re-establish capillary continuity. May take 24h to fully reconnect.",
        },
        {
            "failure": "Overflow drain blocked",
            "severity": "high",
            "time_to_damage": "Next heavy rain or over-fill causes waterlogging",
            "response": "Clear blockage immediately. Drill second overflow as backup. Check monthly.",
        },
        {
            "failure": "Reservoir leaking",
            "severity": "medium",
            "time_to_damage": "Days — reservoir empties faster than expected",
            "response": "Find and seal leak. Pond liner repair kit. May need to rebuild reservoir section.",
        },
        {
            "failure": "Media compaction over time",
            "severity": "low",
            "time_to_damage": "Weeks — gradually reduced wicking efficiency",
            "response": "Gently aerate top layer. Add fresh coco/perlite to surface. Rebuild every 3-4 cycles.",
        },
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLED CONFIG EXPORT
# ─────────────────────────────────────────────────────────────────────────────

WICKING_CONFIG: dict = {
    "grow_type_id": "wicking",
    "version": "1.0.0",
    "stages": WICKING_STAGES,
    "equipment": WICKING_EQUIPMENT,
    "quick_reference": WICKING_QUICK_REFERENCE,
    "troubleshooting": WICKING_TROUBLESHOOTING,
    "capillary_system": WICKING_CAPILLARY_SYSTEM,
    "total_grow_days": {"min": 105, "max": 182, "typical": 140},
}
