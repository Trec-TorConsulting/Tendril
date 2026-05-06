"""Wicking Bed — Complete grow type configuration.

Enterprise-grade configuration for wicking bed / sub-irrigated planter (SIP)
growing. Passive capillary action draws water from sub-surface reservoir up
through media to plant roots. Zero pumps, zero electricity, low maintenance.

KEY DIFFERENCES FROM OTHER METHODS:
  - Completely passive — no pumps, no timers, no electricity
  - Sub-surface water reservoir with capillary wicking upward
  - Self-watering: roots access water on demand via capillary action
  - Very low maintenance (refill reservoir every 3-7 days)
  - Overflow drain prevents waterlogging
  - Soil-based growing medium on top of wicking layer
  - Cannot overwater (overflow handles excess)
  - Salt buildup on surface is the main challenge (top-water periodically to flush)
  - Ideal for outdoor, balcony, and low-tech grows
  - Works with organic or synthetic nutrients

Data sources:
  - Sub-irrigated planter research (Cornell, extension services)
  - Wicking bed community best practices
  - Cannabis SIP/wicking growers (forums, YouTube)
  - Capillary irrigation science
"""

from __future__ import annotations

WICKING_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Germinate separately from wicking bed. Paper towel or starter plug in propagation tray. Transfer to bed once seedling is established.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Standard germination — darkness, warmth, moisture. Wicking bed not involved yet.",
        },
        "reservoir": {
            "notes": "Fill wicking bed reservoir with plain water now to let media saturate evenly before planting."
        },
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Germinate seeds",
                "description": "Paper towel or starter plug. Warm (78°F), dark, moist.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Pre-saturate wicking bed",
                "description": "Fill reservoir to overflow level. Let media wick upward and saturate. Takes 24-48h for full saturation.",
                "interval_days": None,
                "priority": "medium",
            },
            {"name": "Check germination", "description": "Look for taproot.", "interval_days": 1, "priority": "high"},
        ],
        "health_checks": ["Seed cracking?", "Wicking bed media saturating evenly from below?"],
        "common_problems": [
            {
                "issue": "Media not wicking evenly",
                "cause": "Air pockets in wicking layer or media too coarse",
                "solution": "Ensure wicking layer (perlite, gravel) is packed evenly. Media above should be fine enough for capillary action.",
            },
        ],
        "training": [],
        "transition_signals": ["Taproot emerged", "Wicking bed fully saturated and ready"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Germinate indoors. Wicking bed can be outdoors saturating while seeds start inside."
                },
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Greenhouse propagation works well."}, "extra_tasks": []},
        },
    },
    # ── 2. SEEDLING ───────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Transplant seedling into wicking bed. Roots grow downward toward the moisture zone. Top-water for first few days to help roots establish, then let wicking take over.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 60, "max": 75, "target": 68},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 300, "target": 200},
            "light_dli": {"min": 6, "max": 19, "target": 13},
            "notes": "After transplant, top-water lightly for 3-5 days until roots reach the wicking zone. Then switch to reservoir-only watering.",
        },
        "reservoir": {
            "fill_method": "Fill pipe or access tube to reservoir",
            "level_indicator": "Sight tube or dipstick to check water level",
            "refill_when": "Reservoir at 25% (don't let it fully empty — air gaps break capillary action)",
            "notes": "Keep reservoir filled. Initial phase requires top-watering to bridge the gap between seedling roots and the capillary moisture zone.",
        },
        "nutrients": {
            "approach": "Light feeding through reservoir water OR top-dress organic amendments in soil layer",
            "strength_pct": 25,
            "notes": "If using liquid nutrients: add to reservoir at 1/4 strength. If organic: mix amendments into top 4 inches of soil before planting (slow release).",
        },
        "tasks": [
            {
                "name": "Transplant to wicking bed",
                "description": "Plant seedling in top soil layer. Roots will grow down toward moisture zone.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Top-water for establishment",
                "description": "Light top-watering for 3-5 days until roots reach wicking zone. Don't rely on reservoir alone yet.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check reservoir level",
                "description": "Use sight tube or dipstick. Refill before empty — air break kills capillary action.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Mulch surface",
                "description": "Add 1-2 inch mulch layer to prevent surface evaporation and salt crust formation.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Seedling growing new leaves?",
            "Reservoir level adequate?",
            "Soil surface not too wet (over-wicking)?",
            "Mulch layer in place?",
        ],
        "common_problems": [
            {
                "issue": "Seedling wilting despite full reservoir",
                "cause": "Roots haven't reached wicking zone yet",
                "solution": "Top-water until roots establish (3-7 days). Patience.",
            },
            {
                "issue": "Surface too wet",
                "cause": "Wicking action bringing too much water to surface",
                "solution": "Normal initially. Add more mulch. Coarser top layer of soil helps.",
            },
            {
                "issue": "Mosquitoes in reservoir",
                "cause": "Standing water accessible to mosquitoes",
                "solution": "Seal fill pipe with screen mesh. Add BTI dunks to reservoir (safe for plants).",
            },
        ],
        "training": [],
        "transition_signals": [
            "Seedling growing vigorously without top-watering",
            "3-4 sets of true leaves",
            "Roots reaching moisture zone (plant no longer wilts between top-waters)",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Wicking beds are IDEAL for outdoor growing — self-watering reduces maintenance dramatically."
                },
                "extra_tasks": [
                    {
                        "name": "Mosquito prevention",
                        "description": "Seal reservoir access points. Add BTI dunks. Screen any openings.",
                        "interval_days": 14,
                        "priority": "medium",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse wicking beds reduce watering labor significantly."},
                "extra_tasks": [],
            },
        },
    },
    # ── 3. VEGETATIVE ─────────────────────────────────────────────────────
    {
        "id": "vegetative",
        "name": "Vegetative",
        "order": 3,
        "duration_days": {"min": 21, "max": 56, "typical": 35},
        "description": "Plants grow vigorously once roots reach the constant moisture zone. Wicking beds provide incredibly consistent moisture — no wet/dry cycles. Just keep the reservoir filled. Extremely low maintenance.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 700, "target": 550},
            "light_dli": {"min": 25, "max": 45, "target": 35},
            "notes": "Once established, wicking beds are nearly hands-off. Main job: refill reservoir every 3-7 days. Top-water once every 2-3 weeks to flush surface salts.",
        },
        "reservoir": {
            "refill_interval_days": {"min": 3, "max": 7, "typical": 5},
            "notes": "Large plants drink 0.5-2 gallons per day. Size reservoir accordingly (minimum 5 gallon per plant). Check level twice per week.",
        },
        "nutrients": {
            "approach": "Add liquid nutrients to reservoir water, OR top-dress organic amendments, OR both",
            "strength_pct": 50,
            "notes": "Wicking delivers nutrients steadily from below. Top-dress every 2-3 weeks with worm castings + kelp meal for organic approach. For synthetic: 50-75% strength in reservoir.",
        },
        "tasks": [
            {
                "name": "Refill reservoir",
                "description": "Check level 2x per week. Refill before it empties completely. Large plants in flower may need daily refills.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Top-water flush",
                "description": "Every 2-3 weeks, water from the TOP with plain water until it flows into reservoir. This flushes salt buildup from the soil surface.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Check for salt crust",
                "description": "White crusty layer on soil surface = mineral salts wicking up and depositing. Scrape off and top-water flush.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Top-dress amendments (organic)",
                "description": "If organic: add worm castings, kelp, or neem meal to surface every 2-3 weeks. Water in.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Train canopy",
                "description": "Wicking bed plants grow vigorous and healthy due to consistent moisture. Train to manage size.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Reservoir level OK?",
            "No salt crust on surface (or recently flushed)?",
            "Soil surface not too wet or too dry?",
            "Plant growing vigorously?",
            "Overflow drain functioning (test with top-water)?",
        ],
        "common_problems": [
            {
                "issue": "Salt crust on soil surface",
                "cause": "Minerals from nutrient solution wick up and deposit on evaporation",
                "solution": "Top-water flush every 2-3 weeks. Mulch layer reduces surface evaporation and salt formation.",
            },
            {
                "issue": "Reservoir emptying too fast",
                "cause": "Large plant, hot weather, or reservoir too small",
                "solution": "Increase reservoir size. Add automated float valve from water line. Check twice daily in peak summer.",
            },
            {
                "issue": "Anaerobic reservoir (stinky)",
                "cause": "Stagnant water with organic matter decomposing without oxygen",
                "solution": "Flush and refill reservoir. Add small aquarium air stone in reservoir. Use clean water only (no organic teas in reservoir).",
            },
            {
                "issue": "Root rot",
                "cause": "Media staying too saturated (wicking zone too high)",
                "solution": "Ensure overflow drain is at correct height. Top 4-6 inches of soil should not be in the saturated zone.",
            },
        ],
        "training": [
            {
                "name": "LST",
                "when": "5-6 nodes",
                "description": "Consistent moisture = consistent growth = easy training response.",
            },
            {
                "name": "Topping",
                "when": "5th-6th node",
                "description": "Wicking bed plants handle topping well — no drought stress to complicate recovery.",
            },
            {
                "name": "SCROG",
                "when": "Mid-veg",
                "description": "Excellent combination — constant moisture + even canopy = great yields.",
            },
        ],
        "transition_signals": [
            "Canopy 50-60% full",
            "Plant healthy and vigorous",
            "Reservoir consumption is predictable and routine",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor wicking beds are a game-changer — self-watering through heat waves, vacations, and busy weeks. Size reservoir for hot days (plants may drink 2+ gal/day)."
                },
                "extra_tasks": [
                    {
                        "name": "Check reservoir daily in heat",
                        "description": "Hot days increase water consumption dramatically. May need daily refills.",
                        "interval_days": 1,
                        "priority": "high",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse wicking beds = minimal labor, consistent growth. Ideal for part-time growers."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 4. FLOWERING ──────────────────────────────────────────────────────
    {
        "id": "flowering",
        "name": "Flowering",
        "order": 4,
        "duration_days": {"min": 49, "max": 77, "typical": 63},
        "description": "Flip to 12/12. Wicking bed provides incredibly consistent moisture through flower — no wet/dry stress cycles. Continue refilling reservoir and flushing surface salts. Switch to bloom nutrients if using synthetic.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 79, "target": 75},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 40, "max": 55, "target": 45},
            "vpd_kpa": {"min": 1.0, "max": 1.5, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 1000, "target": 800},
            "light_dli": {"min": 25, "max": 43, "target": 35},
            "notes": "Wicking bed flower is low maintenance. Main change: switch to bloom nutrients and monitor reservoir more frequently (flowering plants drink more).",
        },
        "reservoir": {
            "refill_interval_days": {"min": 2, "max": 5, "typical": 3},
            "notes": "Flowering plants drink more. Check every 2-3 days. Don't let reservoir empty — breaks capillary continuity.",
        },
        "nutrients": {
            "approach": "Bloom nutrients in reservoir (synthetic) or bone meal + langbeinite top-dress (organic)",
            "strength_pct": 75,
            "notes": "Switch to higher P/K. If organic: top-dress bone meal + kelp + worm castings. If synthetic: bloom formula at 75% in reservoir.",
        },
        "tasks": [
            {
                "name": "Refill reservoir",
                "description": "Check every 2-3 days. Flowering plants drink more.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Top-water flush",
                "description": "Every 2-3 weeks to flush accumulated salts from surface.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Monitor bud development",
                "description": "Check trichomes. Watch for bud rot.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Remove leaves blocking buds. Good airflow prevents bud rot.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Reservoir level?",
            "Buds healthy (no rot)?",
            "Surface salt buildup managed?",
            "Plants not showing deficiency?",
        ],
        "common_problems": [
            {
                "issue": "Bud rot",
                "cause": "Wicking beds can increase local humidity around base of plant",
                "solution": "Good airflow. Don't let reservoir overflow onto soil surface. Keep humidity below 50%.",
            },
            {
                "issue": "Surface salt lockout",
                "cause": "Accumulated salts from wicking",
                "solution": "Top-water flush. Scrape off white crust. Mulch to reduce surface evaporation.",
            },
            {
                "issue": "Nutrient deficiency late flower",
                "cause": "Reservoir nutrients depleted between fills",
                "solution": "Refill more frequently. Increase nutrient concentration slightly. Top-dress organic amendments.",
            },
        ],
        "training": [
            {
                "name": "Defoliation",
                "when": "Week 3 and 6 of flower",
                "description": "Standard defoliation for light penetration and airflow.",
            },
        ],
        "transition_signals": ["Trichomes milky/amber", "Pistils receding", "Buds dense and mature"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor wicking beds in flower — watch for rain filling reservoir too high (overflow should handle this). Rain on buds = rot risk."
                },
                "extra_tasks": [
                    {
                        "name": "Rain protection for buds",
                        "description": "Cover tops during rain events.",
                        "interval_days": 1,
                        "priority": "high",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse provides ideal rain protection while wicking bed handles watering."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 5. DRYING ─────────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Standard hang dry in controlled environment. Wicking bed can be emptied and composted or rested for next cycle.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "light_hours": 0,
            "notes": "60/60 rule for drying.",
        },
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
            {
                "name": "Rest or refill wicking bed",
                "description": "Empty reservoir. Amend soil for next cycle or plant cover crop.",
                "interval_days": None,
                "priority": "low",
            },
        ],
        "health_checks": ["Drying conditions correct?", "No mold?"],
        "common_problems": [
            {"issue": "Mold", "cause": "Humidity too high", "solution": "Lower humidity. More airflow."}
        ],
        "training": [],
        "transition_signals": ["Stems snap", "Buds ready for jars"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Dry indoors."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Dry indoors."}, "extra_tasks": []},
        },
    },
    # ── 6. CURING ─────────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 6,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Standard jar cure.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "light_hours": 0,
        },
        "tasks": [
            {"name": "Burp jars", "description": "Daily for 2 weeks.", "interval_days": 1, "priority": "high"},
            {
                "name": "Monitor humidity",
                "description": "58-62%. Boveda 62% packs.",
                "interval_days": 1,
                "priority": "medium",
            },
        ],
        "health_checks": ["Humidity correct?", "No ammonia/mold?"],
        "common_problems": [{"issue": "Too dry", "cause": "Over-dried", "solution": "Boveda pack."}],
        "training": [],
        "transition_signals": ["Smooth smoke", "Full terpene profile"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
        },
    },
]

WICKING_CONFIG: dict = {
    "id": "wicking",
    "name": "Wicking Bed (Sub-Irrigated Planter)",
    "description": "Passive self-watering system using capillary action from a sub-surface reservoir. Zero pumps, zero electricity, extremely low maintenance. Perfect for outdoor, balcony, and hands-off growers.",
    "category": "soil",
    "difficulty": "beginner",
    "stages": WICKING_STAGES,
    "equipment": [
        "Wicking bed container (DIY or commercial SIP)",
        "Reservoir layer (gravel, perlite, or purpose-built false floor)",
        "Geotextile fabric (separates reservoir from soil)",
        "Wicking material (fabric wick or capillary matting, or media itself wicks)",
        "Overflow drain (prevents waterlogging — positioned at top of reservoir)",
        "Fill pipe/tube (PVC to refill reservoir without disturbing soil)",
        "Sight tube or dipstick (to check water level)",
        "Growing medium (good potting soil or living soil mix)",
        "Mulch (straw, wood chips, or cover crop)",
        "Nutrients (organic amendments or liquid feed for reservoir)",
    ],
    "key_principles": [
        "Completely passive — gravity and capillary action do all the work",
        "NEVER let reservoir fully empty — breaks capillary continuity (hard to re-establish)",
        "Overflow drain is critical — prevents soil waterlogging from over-filling",
        "Top-water flush every 2-3 weeks to prevent salt crust buildup on surface",
        "Mulch layer reduces surface evaporation and salt migration",
        "Top 4-6 inches of soil should be ABOVE the saturated zone (roots need air)",
        "Bigger reservoir = less frequent refilling = more hands-off",
        "Works with organic or synthetic nutrients (add to reservoir water)",
        "Ideal for vacation growing — large reservoir can last 1-2 weeks unattended",
        "Screen all openings against mosquitoes (standing water = breeding ground)",
    ],
}
