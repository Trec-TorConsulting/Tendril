"""Aquaponics — Complete grow type configuration.

Enterprise-grade configuration for aquaponics growing. Fish and plants in
symbiosis: fish waste provides nutrients for plants, plants filter water for
fish. Combines aquaculture and hydroponics.

Data sources:
  - University of Virgin Islands aquaponics research
  - Nelson and Pade aquaponics systems
  - Cannabis aquaponics community experience
  - FAO aquaponics technical manual
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES
# ─────────────────────────────────────────────────────────────────────────────

AQUAPONICS_STAGES: list[dict] = [
    {
        "id": "germination",
        "name": "Germination (System Cycling)",
        "order": 1,
        "duration_days": {"min": 14, "max": 42, "typical": 28},
        "description": "Unique to aquaponics: system must be cycled (nitrogen cycle established) before planting. Ammonia→Nitrite→Nitrate bacteria colonies take 2-6 weeks. Germinate seeds separately during this period.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
        },
        "water_params": {
            "ammonia_ppm": {"cycling_start": 2.0, "safe_for_fish": 0.25, "safe_for_plants": 0.5},
            "nitrite_ppm": {"peak_during_cycle": 5.0, "safe": 0.5},
            "nitrate_ppm": {"target": {"min": 20, "max": 80}},
            "ph": {"min": 6.8, "max": 7.2, "target": 7.0},
            "temp_f": {"min": 72, "max": 80, "target": 76},
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Fish waste provides all nutrition once cycled. No synthetic nutrients in aquaponics.",
        },
        "tasks": [
            {
                "name": "Add ammonia source",
                "description": "Fishless cycling: add pure ammonia to 2-4 ppm. Or add hardy fish.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Test water daily",
                "description": "Ammonia, nitrite, nitrate, pH. Track cycling progress.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Germinate seeds separately",
                "description": "Paper towel or starter plugs. System not ready for plants yet.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Monitor bacterial colonization",
                "description": "Ammonia drops → nitrite rises → nitrite drops → nitrate rises = CYCLED.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Ammonia converting to nitrite?",
            "Nitrite converting to nitrate?",
            "pH stable?",
            "Water clear?",
        ],
        "common_problems": [
            {
                "issue": "Cycling stalled (no progress)",
                "cause": "Temperature too low, pH too extreme, or chlorine in water",
                "solution": "Ensure water 72-80°F. pH 7.0-7.5. Dechlorinate all water. Add bacteria starter.",
            },
            {
                "issue": "Ammonia spike killing fish",
                "cause": "Added fish before cycle complete",
                "solution": "50% water change immediately. Stop feeding. Add bacteria. Wait for cycle to complete.",
            },
        ],
        "transition_signals": [
            "Ammonia 0 ppm",
            "Nitrite 0 ppm",
            "Nitrate present (20+ ppm)",
            "System cycled — ready for full stocking",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor cycling is slower in cool weather. Shade tank from direct sun."
                },
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse warmth helps cycling speed."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "System cycled. Transplant seedlings to grow beds. Fish stocked and feeding. Bacteria converting waste to plant food. Start with light fish feeding.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 60, "max": 75, "target": 68},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 300, "target": 200},
            "light_dli": {"min": 6, "max": 19, "target": 13},
        },
        "water_params": {
            "ammonia_ppm": {"max": 0.5},
            "nitrite_ppm": {"max": 0.5},
            "nitrate_ppm": {"target": {"min": 20, "max": 60}},
            "ph": {"min": 6.5, "max": 7.0, "target": 6.8},
            "temp_f": {"min": 72, "max": 78, "target": 75},
        },
        "nutrients": {"strength_pct": 0, "approach": "Fish waste only. Light feeding schedule. System still maturing."},
        "tasks": [
            {
                "name": "Transplant seedlings to grow beds",
                "description": "Place in net pots with clay pebbles. Roots will reach water.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Feed fish lightly",
                "description": "2x daily, only what they eat in 5 minutes. Avoid overfeeding.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Test water parameters",
                "description": "Ammonia, nitrite, nitrate, pH daily. System still stabilizing.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Observe fish health",
                "description": "Active, eating, no gasping at surface.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Ammonia < 0.5?", "Fish eating well?", "Seedlings growing?", "Water clear?"],
        "common_problems": [
            {
                "issue": "Seedlings yellowing",
                "cause": "System too new — not enough nitrate yet",
                "solution": "Patience. Increase fish feeding slightly. Add supplemental seaweed extract (safe for fish).",
            },
            {
                "issue": "Fish not eating",
                "cause": "Stress from new environment or water quality issue",
                "solution": "Check ammonia/nitrite. Partial water change if high. Give fish 24h to acclimate.",
            },
        ],
        "transition_signals": [
            "Seedlings showing new growth",
            "Fish feeding normally",
            "Water params stable",
            "3-4 true leaves",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Protect from predators (birds, raccoons)."},
                "extra_tasks": [
                    {
                        "name": "Predator protection",
                        "description": "Net over fish tank. Fencing if needed.",
                        "interval_days": None,
                        "priority": "high",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Ideal controlled environment for aquaponics."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Plants establishing. Roots reaching water. Fish growing and eating more = more nutrients for plants. System reaching biological equilibrium. Increase fish feeding to boost plant nutrition.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 600, "target": 500},
            "light_dli": {"min": 25, "max": 39, "target": 32},
        },
        "water_params": {
            "ammonia_ppm": {"max": 0.25},
            "nitrite_ppm": {"max": 0.25},
            "nitrate_ppm": {"target": {"min": 40, "max": 80}},
            "ph": {"min": 6.4, "max": 7.0, "target": 6.8},
            "temp_f": {"min": 72, "max": 78, "target": 75},
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Fish waste provides NPK. May supplement iron (chelated Fe safe for fish) and potassium (potassium hydroxide for pH up doubles as K supplement).",
        },
        "tasks": [
            {
                "name": "Increase fish feeding",
                "description": "3x daily. As much as they eat in 5 min.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Test water 3x/week",
                "description": "Ammonia, nitrite, nitrate, pH. System should be stable now.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Supplement iron if needed",
                "description": "Chelated iron (DTPA) is fish-safe. Add if yellowing between veins.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Begin training",
                "description": "LST or topping. Aquaponics plants grow vigorously.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Nitrate in target range?",
            "Fish healthy and growing?",
            "Plants vigorous?",
            "Water clear (not green)?",
        ],
        "common_problems": [
            {
                "issue": "Iron deficiency (interveinal chlorosis)",
                "cause": "Fish waste low in iron. Most common aquaponics deficiency.",
                "solution": "Chelated iron (DTPA form is fish-safe). 2-3 ppm target in water.",
            },
            {
                "issue": "Algae bloom (green water)",
                "cause": "Excess light on water + high nutrients",
                "solution": "Shade fish tank. Increase plant mass to consume nutrients. Reduce fish feeding slightly.",
            },
        ],
        "transition_signals": [
            "5-6 nodes",
            "Plants growing vigorously",
            "Fish growing noticeably",
            "System in balance",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Shade fish tank from direct sun. Plants can take full sun."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Monitor water temp — greenhouse heat can warm fish tank too much."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 14, "max": 35, "typical": 21},
        "description": "System in full balance. Fish providing ample nutrition. Plants consuming nitrate aggressively. Aquaponics excels in veg — unlimited nitrogen from fish waste. Vigorous growth.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 65, "target": 58},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 500, "max": 700, "target": 600},
            "light_dli": {"min": 32, "max": 45, "target": 39},
        },
        "water_params": {
            "ammonia_ppm": {"max": 0.25},
            "nitrite_ppm": {"max": 0},
            "nitrate_ppm": {"target": {"min": 40, "max": 120}},
            "ph": {"min": 6.4, "max": 7.0, "target": 6.8},
            "temp_f": {"min": 70, "max": 78, "target": 74},
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Fish waste provides abundant N. Supplement Fe and K as needed. Consider banana peel tea for K (fish-safe).",
        },
        "tasks": [
            {
                "name": "Feed fish generously",
                "description": "Max sustainable feeding. More fish food = more plant nutrition.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor nitrate",
                "description": "If nitrate > 120 ppm, too many fish or too few plants.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Fish tank maintenance",
                "description": "Remove solid waste from tank bottom. Clean biofilter media gently.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Train canopy",
                "description": "Aquaponics plants are often extra vigorous. Train aggressively.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["Nitrate in balance?", "Fish happy?", "Plants explosive growth?", "Water volume stable?"],
        "common_problems": [
            {
                "issue": "Nitrate too high (>150 ppm)",
                "cause": "Too many fish for plant mass",
                "solution": "Add more plants. Reduce fish numbers. Reduce feeding. Partial water change.",
            },
            {
                "issue": "pH dropping rapidly",
                "cause": "Nitrification is acidifying. Normal in aquaponics.",
                "solution": "Buffer with potassium hydroxide (adds K!) or calcium carbonate. Never use pH down chemicals.",
            },
        ],
        "transition_signals": ["Canopy filled", "Ready for flip", "System fully balanced"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Peak outdoor growing. Monitor water temp in heat."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "May need cooling for fish tank in hot greenhouse."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Flip to 12/12. Plants stretch. Aquaponics challenge: fish don't change with light cycle. Maintain fish feeding consistently. Begin phosphorus supplementation for flower.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 64, "max": 72, "target": 68},
            "humidity_pct": {"min": 45, "max": 60, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.3, "target": 1.1},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 800, "target": 700},
            "light_dli": {"min": 25, "max": 35, "target": 30},
        },
        "water_params": {
            "ammonia_ppm": {"max": 0.25},
            "nitrite_ppm": {"max": 0},
            "nitrate_ppm": {"target": {"min": 40, "max": 100}},
            "ph": {"min": 6.4, "max": 7.0, "target": 6.8},
            "temp_f": {"min": 70, "max": 78, "target": 74},
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Fish waste + supplemental P (bone meal tea, rock phosphate in biofilter). K supplementation via pH management.",
        },
        "tasks": [
            {
                "name": "Flip light schedule",
                "description": "12/12. Fish don't care — they're on their own schedule.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Supplement phosphorus",
                "description": "Fish waste is N-heavy, P-light. Add bone meal in biofilter bag or rock phosphate.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Maintain fish feeding",
                "description": "Don't reduce fish food — plants still need N during stretch.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Manage stretch",
                "description": "LST/supercrop as needed.",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": ["Stretch managed?", "Fish still healthy under reduced light?", "P deficiency signs?"],
        "common_problems": [
            {
                "issue": "Purple stems (P deficiency)",
                "cause": "Fish waste insufficient in phosphorus for flowering",
                "solution": "Supplement with bone meal tea bags in system. Rock phosphate in biofilter.",
            },
        ],
        "transition_signals": ["Stretch slowing", "Pre-flowers visible", "Pistils forming"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Natural photoperiod. Fish unaffected."}, "extra_tasks": []},
            "greenhouse": {
                "environment_overrides": {"notes": "Blackout covers if needed. Fish tank stays lit normally."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Bud sites forming. Aquaponics challenge: sufficient P and K from fish alone is difficult. Supplementation needed without harming fish. Flower quality can match hydro with proper management.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 79, "target": 75},
            "temp_night_f": {"min": 62, "max": 70, "target": 66},
            "humidity_pct": {"min": 40, "max": 55, "target": 48},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 25, "max": 39, "target": 32},
        },
        "water_params": {
            "ammonia_ppm": {"max": 0.25},
            "nitrite_ppm": {"max": 0},
            "nitrate_ppm": {"target": {"min": 30, "max": 80}},
            "ph": {"min": 6.4, "max": 7.0, "target": 6.8},
            "temp_f": {"min": 68, "max": 76, "target": 72},
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Fish waste + P supplement + K supplement. Kelp extract (fish-safe) provides micronutrients and natural growth hormones.",
        },
        "tasks": [
            {
                "name": "Maintain P/K supplementation",
                "description": "Bone meal bag + potassium hydroxide for pH up.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Monitor bud development",
                "description": "Compare to hydro expectations. May be smaller but quality is excellent.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Remove lower fans. Aquaponics humidity can be high.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Fish feeding maintained",
                "description": "Don't reduce. Plants still using N.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Bud sites forming?", "Fish healthy?", "No deficiency signs?", "Water quality stable?"],
        "common_problems": [
            {
                "issue": "Slow bud development vs hydro",
                "cause": "Insufficient P-K from fish waste alone",
                "solution": "This is normal for aquaponics. Supplement P-K. Accept slightly smaller yields for superior terpene/flavor quality.",
            },
        ],
        "transition_signals": ["Buds at all sites", "Pistils abundant", "Stretch complete"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Pest management — no pesticides in aquaponics!"},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Humidity management critical with water volume."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "mid_flower",
        "name": "Mid Flower (Bulk Phase)",
        "order": 7,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Peak bud development. Maximum P-K demand. Fish-powered nutrients produce unique terpene profiles — many aquaponics growers report exceptional flavor and smoothness.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 78, "target": 74},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 38, "max": 50, "target": 44},
            "vpd_kpa": {"min": 1.2, "max": 1.5, "target": 1.3},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
        },
        "water_params": {
            "ammonia_ppm": {"max": 0.25},
            "nitrite_ppm": {"max": 0},
            "nitrate_ppm": {"target": {"min": 30, "max": 80}},
            "ph": {"min": 6.4, "max": 7.0, "target": 6.8},
            "temp_f": {"min": 68, "max": 76, "target": 72},
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Fish waste + P-K supplements. Consider worm casting tea (fish-safe) for micronutrient boost.",
        },
        "tasks": [
            {
                "name": "Maintain system balance",
                "description": "Fish feeding, water testing, supplement P-K.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor water temp",
                "description": "Flowering prefers cooler — may need to cool fish tank.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Support heavy buds",
                "description": "Trellis or stakes.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Inspect for bud rot",
                "description": "Aquaponics = high humidity environment. Be vigilant.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": ["Buds developing?", "Fish healthy?", "Water quality?", "No rot (high humidity system)?"],
        "common_problems": [
            {
                "issue": "Bud rot from system humidity",
                "cause": "Large water volume in grow room raises ambient humidity",
                "solution": "Dehumidifier. Separate fish tank room from grow room if possible. Excellent airflow.",
            },
            {
                "issue": "Fish stressed from cooling",
                "cause": "Lowering water temp for flower hurts tropical fish",
                "solution": "Choose fish species that tolerate cooler water (trout, goldfish). Or separate fish and plant water temps.",
            },
        ],
        "transition_signals": ["Buds dense", "Trichomes milky", "Pistils browning"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Water temp follows ambient. Choose fish accordingly."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Ventilation critical with water mass."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Final ripening. Reduce fish feeding slightly to lower nitrogen availability. This encourages natural fade. Fish adjust easily to reduced feeding.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 72},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 48, "target": 42},
            "vpd_kpa": {"min": 1.2, "max": 1.5, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 800},
            "light_dli": {"min": 25, "max": 39, "target": 35},
        },
        "water_params": {
            "ammonia_ppm": {"max": 0.25},
            "nitrite_ppm": {"max": 0},
            "nitrate_ppm": {"target": {"min": 20, "max": 60}},
            "ph": {"min": 6.4, "max": 7.0, "target": 6.8},
            "temp_f": {"min": 66, "max": 74, "target": 70},
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Reduce fish feeding 25-50% to lower N. Stop P-K supplements. Let plant use stored nutrients.",
        },
        "tasks": [
            {
                "name": "Reduce fish feeding",
                "description": "Cut to 50-75% normal. Lowers N for natural fade.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Check trichomes",
                "description": "60x loupe. 70-80% milky, 10-20% amber target.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Stop supplements",
                "description": "No more P-K additions. Let system deplete.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Monitor fish at reduced feeding",
                "description": "Fish handle reduced food fine. Won't harm them.",
                "interval_days": 1,
                "priority": "medium",
            },
        ],
        "health_checks": ["Trichomes maturing?", "Fish handling reduced feed?", "Natural fade beginning?"],
        "common_problems": [
            {
                "issue": "No fade (still green)",
                "cause": "Fish waste still providing too much N",
                "solution": "Reduce feeding more. Fish are fine on 1x/day. Or accept it — aquaponics often finishes green.",
            },
        ],
        "transition_signals": ["Trichomes 70-80% milky", "Pistils receded", "Some fade visible"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Fall temps help. Monitor fish in cooling water."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Night temp drops beneficial for ripening."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Aquaponics doesn't flush traditionally — no salt buildup. Reduce fish feeding to minimum. Some growers temporarily move plants to plain water for final days. Others harvest without any flush (already organic).",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 72},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 48, "target": 42},
            "vpd_kpa": {"min": 1.2, "max": 1.5, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 17, "max": 30, "target": 26},
        },
        "water_params": {
            "ammonia_ppm": {"max": 0.25},
            "nitrite_ppm": {"max": 0},
            "nitrate_ppm": {"target": {"min": 10, "max": 40}},
            "ph": {"min": 6.4, "max": 7.0, "target": 6.8},
            "temp_f": {"min": 66, "max": 74, "target": 70},
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Minimal fish feeding. No supplements. System naturally depletes. No salt flush needed.",
        },
        "tasks": [
            {
                "name": "Minimal fish feeding",
                "description": "Once daily, small amount. Just enough to keep fish healthy.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Monitor trichomes",
                "description": "Continue checking ripeness.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Optional: move to plain water",
                "description": "Some remove plants from system to plain water tub for final 3-5 days.",
                "interval_days": None,
                "priority": "low",
            },
        ],
        "health_checks": ["Trichomes at target?", "Fish okay on reduced food?", "Plant fading?"],
        "common_problems": [
            {
                "issue": "Worried about not flushing",
                "cause": "Habit from synthetic grows",
                "solution": "Aquaponics is organic. No synthetic salts to flush. Smoke is already clean/smooth. Flush optional.",
            },
        ],
        "transition_signals": ["Trichomes at target", "Ready to harvest", "7-10 days reduced feeding"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Harvest timing based on weather, not flush schedule."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Standard procedure."}, "extra_tasks": []},
        },
    },
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Remove plants from grow beds. Fish continue as normal — resume regular feeding. System keeps running. Can replant immediately for continuous cycling.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
        },
        "water_params": {"notes": "Resume normal fish feeding. System continues without plants temporarily."},
        "nutrients": {"strength_pct": 0, "approach": "None for plants. Resume normal fish feeding."},
        "tasks": [
            {
                "name": "Remove plants from grow beds",
                "description": "Pull from net pots. Remove all root material from beds.",
                "interval_days": None,
                "priority": "high",
            },
            {"name": "Trim", "description": "Wet or dry trim.", "interval_days": None, "priority": "high"},
            {
                "name": "Resume fish feeding",
                "description": "Back to normal schedule. Fish need consistent nutrition.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Plant next cycle (or companion plants)",
                "description": "System needs plants to consume nitrate. Plant lettuce/herbs as gap crop if not ready for next cannabis.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["All plants removed?", "Fish feeding resumed?", "Nitrate won't spike without plants?"],
        "common_problems": [
            {
                "issue": "Nitrate spiking after harvest",
                "cause": "No plants consuming the fish waste nitrogen",
                "solution": "CRITICAL: plant something immediately. Lettuce, basil, or next cannabis. Fish waste doesn't stop.",
            },
        ],
        "transition_signals": ["Plants removed", "Fish feeding normal", "Next crop planned"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Harvest before frost. Plan for fish over winter."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Year-round cycling possible."}, "extra_tasks": []},
        },
    },
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Standard hang dry. Aquaponics-grown flower often dries slightly differently due to organic nutrient profile — takes well to slow dry.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "light_hours": 0,
        },
        "water_params": {
            "notes": "Fish system running independently. May need water changes if no plants consuming waste."
        },
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Hang branches",
                "description": "60-65°F, 55-62% RH, complete darkness.",
                "interval_days": None,
                "priority": "high",
            },
            {"name": "Monitor conditions", "description": "Check daily.", "interval_days": 1, "priority": "high"},
            {
                "name": "Stem snap test",
                "description": "Small stems snap = ready.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": ["Conditions in range?", "No mold?", "Even drying?"],
        "common_problems": [
            {
                "issue": "Drying too fast",
                "cause": "Humidity too low",
                "solution": "Raise humidity. Hang whole plants for slower dry.",
            },
        ],
        "transition_signals": ["Stems snap", "Outside crispy, inside moist"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Always dry indoors."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Dry in separate space."}, "extra_tasks": []},
        },
    },
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Jar cure. Aquaponics flower often has excellent flavor due to broad-spectrum organic nutrition from fish waste. Extended cure recommended.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "light_hours": 0,
        },
        "water_params": {"notes": "Fish system independent."},
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
        "health_checks": ["Humidity in range?", "No ammonia smell?", "No mold?"],
        "common_problems": [
            {"issue": "Ammonia smell", "cause": "Jarred too wet", "solution": "Remove, dry 12-24h, re-jar."},
        ],
        "transition_signals": ["Smooth smoke", "Excellent flavor", "No hay smell"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT
# ─────────────────────────────────────────────────────────────────────────────

AQUAPONICS_EQUIPMENT: list[dict] = [
    {
        "name": "Fish tank (100-300 gal)",
        "category": "essential",
        "essential": True,
        "description": "Main fish habitat. Size determines system capacity. 1 lb fish per 5-10 gal water.",
    },
    {
        "name": "Grow bed(s)",
        "category": "essential",
        "essential": True,
        "description": "Media bed (flood/drain), DWC raft, or NFT channel for plants. Media beds double as biofilter.",
    },
    {
        "name": "Water pump",
        "category": "essential",
        "essential": True,
        "description": "Moves water between fish tank and grow beds. Sized for system volume.",
    },
    {
        "name": "Air pump + stones",
        "category": "essential",
        "essential": True,
        "description": "Dissolved oxygen for fish AND nitrifying bacteria. Critical for both.",
    },
    {
        "name": "Biofilter media",
        "category": "essential",
        "essential": True,
        "description": "Surface area for nitrifying bacteria. K1 media, lava rock, or grow bed media serves this role.",
    },
    {
        "name": "Fish (tilapia, goldfish, trout, etc.)",
        "category": "essential",
        "essential": True,
        "description": "The nutrient source. Species chosen based on water temp and local regulations.",
    },
    {
        "name": "Fish food (high-quality pellets)",
        "category": "essential",
        "essential": True,
        "description": "Input that drives the entire system. Higher protein = more N output.",
    },
    {
        "name": "Water test kit (API Master)",
        "category": "essential",
        "essential": True,
        "description": "Ammonia, nitrite, nitrate, pH minimum. Test regularly.",
    },
    {
        "name": "Grow media (hydroton/lava rock)",
        "category": "essential",
        "essential": True,
        "description": "For media bed systems. Provides root support + bacterial surface area.",
    },
    {
        "name": "Bell siphon or timer",
        "category": "essential",
        "essential": True,
        "description": "Controls flood/drain cycle in media beds. Bell siphon is gravity-powered.",
    },
    {
        "name": "Chelated iron (DTPA)",
        "category": "recommended",
        "essential": False,
        "description": "Most common aquaponics deficiency. DTPA form is fish-safe.",
    },
    {
        "name": "Potassium hydroxide",
        "category": "recommended",
        "essential": False,
        "description": "Raises pH (nitrification is acidifying) AND supplements K. Dual purpose.",
    },
    {
        "name": "Thermometer (water)",
        "category": "recommended",
        "essential": False,
        "description": "Monitor fish tank temperature. Critical for fish health.",
    },
    {
        "name": "Net pots",
        "category": "recommended",
        "essential": False,
        "description": "For DWC/raft systems. Hold plants in floating rafts.",
    },
    {
        "name": "Solids filter/settling tank",
        "category": "recommended",
        "essential": False,
        "description": "Removes solid fish waste before grow beds. Prevents clogging.",
    },
    {
        "name": "Backup air pump",
        "category": "optional",
        "essential": False,
        "description": "Fish die within hours without oxygen. Battery backup air pump is insurance.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

AQUAPONICS_QUICK_REFERENCE: dict = {
    "method_summary": "Fish and plants in symbiosis. Fish waste → bacteria convert → plant food. Plants filter water → clean for fish. Closed-loop ecosystem.",
    "difficulty": "advanced",
    "maintenance_level": "High — living system requires daily fish care, water testing, and balancing two ecosystems simultaneously.",
    "key_advantages": [
        "Organic by nature (fish waste = fertilizer)",
        "Sustainable closed-loop system",
        "Dual harvest (fish + plants)",
        "Exceptional flavor/terpene profiles",
        "No nutrient mixing ever",
        "Educational and rewarding",
    ],
    "key_challenges": [
        "2-6 week cycling before first plant",
        "Cannot use pesticides (kills fish)",
        "P and K deficiency in flower (fish waste is N-heavy)",
        "Fish health adds complexity layer",
        "Higher humidity from water volume",
        "Cannot flush traditionally",
    ],
    "fish_feeding_schedule": {
        "cycling": "None or minimal (fishless cycling preferred)",
        "seedling_veg": "2-3x daily, 5-minute rule",
        "flower": "3x daily full feeding",
        "late_flower_flush": "Reduce to 1x daily",
    },
    "critical_rules": [
        "NEVER use pesticides, fungicides, or chemicals — kills fish",
        "NEVER let ammonia or nitrite exceed 1 ppm — fish die",
        "System MUST be cycled before adding fish at full density",
        "Always have backup aeration — fish die in hours without O2",
        "Plant something IMMEDIATELY after harvest — nitrate spikes without plants",
        "Supplement iron (chelated DTPA) — universal aquaponics deficiency",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING
# ─────────────────────────────────────────────────────────────────────────────

AQUAPONICS_TROUBLESHOOTING: list[dict] = [
    {
        "category": "water_chemistry",
        "issues": [
            {
                "symptom": "Ammonia spike",
                "cause": "Dead fish, overfeeding, or insufficient bacteria",
                "solution": "50% water change immediately. Stop feeding 24h. Check for dead fish. Add bacteria starter.",
            },
            {
                "symptom": "Nitrite spike",
                "cause": "System partially cycled or bacteria die-off",
                "solution": "50% water change. Add salt (1 ppt) to protect fish gills. Patience — nitrite bacteria will catch up.",
            },
            {
                "symptom": "pH crashing (dropping below 6.0)",
                "cause": "Nitrification produces acid. Normal over time.",
                "solution": "Buffer with potassium hydroxide or calcium carbonate. Small amounts frequently. Target 6.8.",
            },
            {
                "symptom": "pH too high (above 7.5)",
                "cause": "New system, alkaline water source, or limestone in media",
                "solution": "Patience — pH drops naturally from nitrification. Remove any limestone. Use rainwater.",
            },
        ],
    },
    {
        "category": "fish_health",
        "issues": [
            {
                "symptom": "Fish gasping at surface",
                "cause": "Low dissolved oxygen",
                "solution": "Emergency: add air stones immediately. Check air pump. Reduce feeding. Partial water change.",
            },
            {
                "symptom": "Fish not eating",
                "cause": "Stress, disease, or water quality issue",
                "solution": "Test all water params. Partial water change. Look for visible disease signs. Salt bath (1-3 ppt).",
            },
            {
                "symptom": "Fish dying suddenly",
                "cause": "Ammonia/nitrite spike, temperature shock, or oxygen crash",
                "solution": "Emergency water change (50%). Test everything. Check air pump. Don't add chemicals.",
            },
            {
                "symptom": "White spots on fish (ich)",
                "cause": "Ichthyophthirius (common parasite)",
                "solution": "Raise temp to 82°F slowly (1°F/day). Salt to 3 ppt. Do NOT use malachite green (kills plants).",
            },
        ],
    },
    {
        "category": "plant_nutrition",
        "issues": [
            {
                "symptom": "Yellow new growth (iron deficiency)",
                "cause": "Fish waste contains almost no iron",
                "solution": "Add chelated iron DTPA at 2-3 ppm. This is safe for fish. Most common aquaponics deficiency.",
            },
            {
                "symptom": "Purple stems, slow flowering",
                "cause": "Phosphorus deficiency — fish waste is N-heavy",
                "solution": "Bone meal in mesh bag placed in biofilter flow. Rock phosphate. Fish-safe P supplement.",
            },
            {
                "symptom": "Weak stems, poor bud structure",
                "cause": "Potassium deficiency",
                "solution": "Use potassium hydroxide as pH buffer (raises pH AND adds K). Kelp extract (fish-safe).",
            },
            {
                "symptom": "Overall slow growth despite fish",
                "cause": "Insufficient fish biomass for plant load",
                "solution": "More fish, larger fish, or reduce plant count. Rule: 1 lb fish per 1-2 sq ft grow space.",
            },
        ],
    },
    {
        "category": "system_balance",
        "issues": [
            {
                "symptom": "Nitrate too high (>150 ppm)",
                "cause": "More fish waste than plants can consume",
                "solution": "Add more plants. Reduce fish count. Reduce feeding. Partial water change.",
            },
            {
                "symptom": "Nitrate too low (<20 ppm)",
                "cause": "Too many plants for fish load",
                "solution": "Add more fish. Increase feeding. Supplement with fish-safe inputs.",
            },
            {
                "symptom": "Algae everywhere",
                "cause": "Light hitting water + excess nutrients",
                "solution": "Shade all water surfaces. Cover fish tank. More plants to consume nutrients.",
            },
            {
                "symptom": "Solids building up in grow beds",
                "cause": "Insufficient solids filtration",
                "solution": "Add settling tank before grow beds. Clean beds periodically. Worm composting in media beds helps.",
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# AQUAPONICS ECOSYSTEM — Core differentiator
# ─────────────────────────────────────────────────────────────────────────────

AQUAPONICS_ECOSYSTEM: dict = {
    "nitrogen_cycle": {
        "overview": "The nitrogen cycle is the ENGINE of aquaponics. Fish excrete ammonia → Nitrosomonas bacteria convert to nitrite → Nitrobacter bacteria convert to nitrate → Plants absorb nitrate as fertilizer.",
        "steps": [
            {
                "step": 1,
                "process": "Fish excrete ammonia (NH3/NH4+)",
                "location": "Fish tank",
                "notes": "Toxic to fish above 1 ppm. Must be converted quickly.",
            },
            {
                "step": 2,
                "process": "Nitrosomonas bacteria oxidize ammonia → nitrite (NO2-)",
                "location": "Biofilter / grow bed media",
                "notes": "Nitrite also toxic to fish. Intermediate step.",
            },
            {
                "step": 3,
                "process": "Nitrobacter bacteria oxidize nitrite → nitrate (NO3-)",
                "location": "Biofilter / grow bed media",
                "notes": "Nitrate is plant food! Safe for fish up to 200+ ppm.",
            },
            {
                "step": 4,
                "process": "Plants absorb nitrate through roots",
                "location": "Grow beds",
                "notes": "Plants clean the water. Returns to fish tank filtered.",
            },
        ],
        "cycling_methods": {
            "fishless": {
                "duration_weeks": "3-6",
                "method": "Add pure ammonia to 2-4 ppm. Feed bacteria with ammonia until conversion is instant. Then add fish.",
                "advantages": "No fish at risk during unstable period.",
            },
            "fish_in": {
                "duration_weeks": "4-8",
                "method": "Add hardy fish at low density. Monitor daily. Water changes if ammonia/nitrite spike.",
                "advantages": "Simpler setup. Fish from day one.",
                "risk": "Fish stress/death if not managed carefully.",
            },
        },
    },
    "fish_species": {
        "tilapia": {
            "temp_range_f": {"min": 72, "max": 86, "ideal": 80},
            "growth_rate": "Fast — harvest size in 6-9 months",
            "advantages": [
                "Hardy",
                "Fast growing",
                "Edible",
                "High waste production (more plant food)",
                "Tolerant of water quality fluctuations",
            ],
            "disadvantages": [
                "Need warm water (heater in winter)",
                "Illegal in some states",
                "Prolific breeders (population control needed)",
            ],
            "stocking_density": "1 lb per 3-5 gallons at maturity",
        },
        "goldfish_koi": {
            "temp_range_f": {"min": 50, "max": 78, "ideal": 68},
            "growth_rate": "Slow — ornamental, not for eating",
            "advantages": ["Cold tolerant", "Legal everywhere", "Hardy", "Beautiful", "Long-lived"],
            "disadvantages": ["Not edible", "Lower waste than tilapia", "Slower nutrient production"],
            "stocking_density": "1 fish per 10-20 gallons",
        },
        "trout": {
            "temp_range_f": {"min": 45, "max": 65, "ideal": 55},
            "growth_rate": "Moderate — harvest in 12-18 months",
            "advantages": ["Cold water (good for flower phase)", "Edible (excellent eating)", "High value"],
            "disadvantages": [
                "Need cold water (expensive to cool)",
                "Sensitive to water quality",
                "Need high dissolved oxygen",
            ],
            "stocking_density": "1 lb per 5-8 gallons",
        },
        "catfish": {
            "temp_range_f": {"min": 70, "max": 85, "ideal": 78},
            "growth_rate": "Moderate-fast — harvest in 12-18 months",
            "advantages": ["Very hardy", "Edible", "Tolerant of low oxygen", "Bottom feeders clean tank"],
            "disadvantages": ["Need warm water", "Can be aggressive", "Nocturnal (less visible)"],
            "stocking_density": "1 lb per 5-8 gallons",
        },
    },
    "system_types": {
        "media_bed": {
            "description": "Flood and drain grow beds filled with expanded clay or gravel. Serves as grow space AND biofilter.",
            "advantages": [
                "Simple",
                "Biofilter built-in",
                "Worm-friendly (adds composting)",
                "Good for cannabis (large root mass)",
            ],
            "disadvantages": ["Heavy", "Can clog", "Uneven moisture distribution"],
            "best_for": "Cannabis (root space + support for large plants)",
        },
        "dwc_raft": {
            "description": "Floating foam rafts with net pots. Roots dangle in nutrient-rich water.",
            "advantages": ["High plant density", "Easy harvest", "Consistent moisture"],
            "disadvantages": ["Needs separate biofilter", "Not ideal for large plants", "Root rot risk"],
            "best_for": "Leafy greens, herbs. Can work for cannabis with support.",
        },
        "nft_channel": {
            "description": "Thin film of water flowing through channels. Roots in channel.",
            "advantages": ["Space efficient", "Low water volume", "Easy to inspect roots"],
            "disadvantages": ["Clogs easily", "Needs separate biofilter", "Not for large plants"],
            "best_for": "Small plants. Not recommended for cannabis.",
        },
    },
    "system_balance": {
        "fish_to_plant_ratio": {
            "rule_of_thumb": "1 lb of fish feeds 1-2 sq ft of grow bed (media bed) or 2-4 sq ft of DWC raft",
            "for_cannabis": "Cannabis is a heavy feeder. Use 1 lb fish per 1 sq ft of grow space for flowering.",
            "feeding_rate_drives_nutrients": "Fish food is the ONLY input. More food = more waste = more plant nutrients.",
        },
        "stocking_density_limits": {
            "low": {"lbs_per_gal": 0.05, "notes": "Hobby. Forgiving. Less nutrients for plants."},
            "medium": {"lbs_per_gal": 0.1, "notes": "Balanced. Good for most setups."},
            "high": {"lbs_per_gal": 0.2, "notes": "Commercial density. Needs excellent aeration and filtration."},
        },
        "common_supplements": {
            "iron": {
                "form": "Chelated Fe-DTPA",
                "dosage_ppm": 2,
                "frequency": "Weekly or as needed",
                "fish_safe": True,
            },
            "potassium": {
                "form": "Potassium hydroxide (KOH)",
                "use": "pH buffer that doubles as K supplement",
                "fish_safe": True,
            },
            "calcium": {
                "form": "Calcium hydroxide or calcium carbonate",
                "use": "pH buffer + Ca supplement",
                "fish_safe": True,
            },
            "phosphorus": {"form": "Bone meal in mesh bags", "use": "Place in biofilter flow path", "fish_safe": True},
        },
    },
    "pest_management": {
        "constraint": "CANNOT use pesticides, fungicides, or any chemicals that will enter the water and harm fish.",
        "allowed_methods": [
            "Beneficial insects (ladybugs, lacewings, predatory mites)",
            "Physical removal (hand-pick pests)",
            "Sticky traps",
            "Neem oil foliar (ABOVE water only — never in system water)",
            "Diatomaceous earth (on soil surfaces, not in water)",
            "BT (Bacillus thuringiensis) for caterpillars (fish-safe)",
            "Companion planting for pest deterrence",
        ],
        "banned_methods": [
            "ALL synthetic pesticides",
            "Copper-based fungicides (toxic to fish)",
            "Hydrogen peroxide in system water",
            "Pyrethrin sprays near water",
            "Any systemic pesticide (enters plant tissue → falls in water)",
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLED CONFIG EXPORT
# ─────────────────────────────────────────────────────────────────────────────

AQUAPONICS_CONFIG: dict = {
    "grow_type_id": "aquaponics",
    "version": "1.0.0",
    "stages": AQUAPONICS_STAGES,
    "equipment": AQUAPONICS_EQUIPMENT,
    "quick_reference": AQUAPONICS_QUICK_REFERENCE,
    "troubleshooting": AQUAPONICS_TROUBLESHOOTING,
    "aquaponics_ecosystem": AQUAPONICS_ECOSYSTEM,
    "total_grow_days": {"min": 120, "max": 224, "typical": 168},
}
