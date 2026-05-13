"""Outdoor Container — Complete grow type configuration.

Enterprise-grade configuration for outdoor container growing — the method that
combines outdoor growing's unlimited light with container growing's mobility and
control.  This is the most flexible outdoor method.

The defining features are **container heat management** (the #1 challenge — black
pots in direct sun reach 120°F+, killing roots), **mobility** (the killer advantage
— move plants for weather, light optimization, stealth, and staging), **accelerated
drying** (containers outdoors dry 2-3x faster than in-ground due to sun/wind on pot
walls), **root binding in large outdoor plants** (outdoor container plants push root
zone limits), and **pot material/color selection** (critical for thermal management).

Key Outdoor Container differences from outdoor soil (in-ground):
  - MOBILITY: move plants for weather protection, light, stealth
  - Container heat is the #1 problem (not bud rot like in-ground)
  - Pots dry 2-3x faster than in-ground — water demand is extreme
  - Root space limits plant size (15-25 gal max practical outdoor)
  - No deep taproot — must provide all water/nutrients from surface
  - Soil/medium can be optimized per plant (unlike native ground)
  - Wind is more dangerous (top-heavy plants in pots tip over)
  - Easy to bring inside for weather emergencies
  - Good for balcony, patio, rooftop, and stealth grows
  - Can use any medium: soil, coco, peat, or blends

Supports three environment types (matching Tent.environment_type):
  - outdoor  (default — patio, balcony, yard, rooftop)
  - greenhouse (excellent — combines protection with container flexibility)
  - indoor  (not applicable — see indoor configs)

Data sources:
- Container gardening science (pot thermal dynamics)
- Smart Pot / Root Pouch specifications
- Outdoor cannabis container growing methodology
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in an Outdoor Container grow
# ─────────────────────────────────────────────────────────────────────────────

OUTDOOR_CONTAINER_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Start seeds INDOORS. Same as outdoor soil — germinate in controlled conditions, then harden off. While seeds germinate: select containers, prepare medium, plan outdoor placement.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "INDOORS. Heat mat, humidity dome.",
        },
        "medium": {
            "pot_material": None,
            "pot_size_gal": None,
            "heat_management": None,
            "mobility_plan": "N/A — seeds indoors",
            "notes": "Start seeds in solo cups with seed-starting mix indoors. While germinating: prepare final containers — select pot material/color/size, fill with medium, stage in planned outdoor location to test sun exposure.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None — seeds contain all energy.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Start seeds indoors",
                "description": "Same as outdoor soil. Soak, plant, heat mat, dome.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Select containers",
                "description": "Choose pot material: fabric (best heat management, air pruning), light-colored plastic (reflects heat), or Air-Pots (excellent aeration). AVOID: black plastic pots — they absorb massive heat and cook roots.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Size containers",
                "description": "Final pot size: 10-15 gallon for moderate plants, 15-25 gallon for large plants, 25-30+ gallon for maximum production. Bigger = more water buffer = less frequent watering.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Prepare medium",
                "description": "Fill containers with chosen medium (super soil, coco/perlite, peat blend). Pre-moisten. Stage in planned outdoor location.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Plan placement",
                "description": "Map sun exposure: minimum 6 hours direct sun, ideal 8-10+. South-facing is best (Northern Hemisphere). Note shade patterns throughout the day.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Seeds germinating?", "Containers selected and prepared?", "Outdoor placement planned?"],
        "common_problems": [
            {
                "issue": "Choosing black pots",
                "cause": "Black plastic absorbs maximum solar heat — pot surface can reach 120°F+",
                "solution": "Use fabric pots (tan/white preferred), light-colored plastic, or wrap black pots in reflective material. Container heat is THE #1 outdoor container problem.",
            },
        ],
        "training": [],
        "transition_signals": ["Taproot visible", "Sprout emerging", "Containers prepared"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Start indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor germination.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse germination works."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Good option.",
            },
        },
    },
    # ── 2. SEEDLING ──────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Seedlings develop indoors or in greenhouse. Harden off before moving containers outside. Same hardening off protocol as outdoor soil: gradual sun exposure over 2 weeks.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 60, "max": 75, "target": 65},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 200, "max": 400, "target": 300},
            "light_dli": {"min": 13, "max": 26, "target": 19},
            "notes": "Indoor grow lights on 18/6. Keep on long light schedule to prevent premature flowering when moved outside.",
        },
        "medium": {
            "pot_material": "solo cup (any material)",
            "pot_size_gal": 0.125,
            "heat_management": "N/A — indoors",
            "mobility_plan": "Move seedlings outside gradually during hardening off. Bring in at night.",
            "notes": "Seedlings in solo cups indoors. Begin hardening off 2 weeks before plant-out. Same protocol as outdoor soil: gradually increase outdoor time. With containers, the advantage is you can bring them in easily.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Seed-starting mix provides base nutrition.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Grow seedlings under lights",
                "description": "18/6 schedule. Strong stems.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Harden off",
                "description": "2 weeks before plant-out. Gradually increase outdoor exposure. Container advantage: easy to move in/out.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Test container placement",
                "description": "Set empty containers in planned locations. Observe sun exposure, wind, and access for watering. Adjust placement before plants are in them.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Seedlings stocky and healthy?", "Hardening off on schedule?"],
        "common_problems": [
            {
                "issue": "Premature flowering after moving outside",
                "cause": "Day length shorter than indoor 18/6",
                "solution": "Don't move out until days are 14+ hours.",
            },
        ],
        "training": [],
        "transition_signals": ["2-4 sets of true leaves", "Hardening complete", "Night temps above 50°F consistently"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Harden off into outdoor conditions."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Standard.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse seedlings may not need full hardening off if staying in greenhouse."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Easier transition.",
            },
        },
    },
    # ── 3. EARLY VEGETATIVE ──────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Vegetative (Move Outside)",
        "order": 3,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Transplant to intermediate pots and move outside. Or transplant directly to final containers if using autoflowers. Containers are NOW in full sun — heat management begins immediately. Root zone temperature is the critical factor.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 90, "target": 78},
            "temp_night_f": {"min": 50, "max": 70, "target": 60},
            "humidity_pct": {"min": 40, "max": 80, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 2.0, "target": 1.2},
            "light_hours": {"min": 14, "max": 16, "notes": "Natural photoperiod."},
            "light_ppfd": {"min": 800, "max": 2000, "target": 1200},
            "light_dli": {"min": 40, "max": 65, "target": 50},
            "notes": "Full sun outdoors. Container surfaces absorb heat — monitor root zone temp.",
        },
        "medium": {
            "pot_material": {
                "recommended": "fabric (tan/white)",
                "acceptable": "light-colored plastic, Air-Pot",
                "avoid": "black plastic in direct sun",
            },
            "pot_size_gal": {
                "intermediate": "1-3 gallon",
                "notes": "Transplant to intermediate. Final pot move in late veg.",
            },
            "heat_management": {
                "description": "Container heat is the #1 outdoor container problem. Root zone above 85°F causes stress. Above 95°F kills roots.",
                "strategies": [
                    "Use fabric pots (air cooling on all surfaces)",
                    "Use white/tan/light-colored containers (reflect heat)",
                    "Pot-in-pot: set container inside a larger container with air gap",
                    "Elevate on bricks/stand for bottom airflow",
                    "Mulch top of soil (3-4 inches)",
                    "Shade cloth on containers (not plants) during heat waves",
                    "Group containers to shade each other's sides",
                    "Water early morning — evaporation cools root zone",
                ],
            },
            "mobility_plan": "Keep containers on plant caddies/dollies for easy moving. Can move for sun optimization, weather protection, or stealth. The container advantage.",
            "notes": "Containers in direct sun: the pot surface reaches ambient temp + 20-40°F. A black pot at 90°F air temp = 120-130°F pot surface = cooked roots. Heat management is NON-NEGOTIABLE. Fabric pots are 10-20°F cooler than plastic. White fabric is coolest.",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "Quarter strength. Container medium depletes faster than in-ground — begin light feeding earlier.",
            "flora_micro_ml_per_gal": 0.625,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 0.3125,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {"name": "Mycorrhizae", "dose_ml_per_gal": None, "purpose": "Apply to roots at transplant."},
            ],
        },
        "tasks": [
            {
                "name": "Transplant and move outside",
                "description": "Transplant to intermediate pots. Place in planned outdoor location. Implement heat management immediately.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Implement heat management",
                "description": "Elevate pots. Mulch top. Group for side shading. Use fabric/light colored pots. This is day-1 outdoor container work.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Establish watering schedule",
                "description": "Containers outdoors dry FAST. Check twice daily in hot weather. Water when top 1-2 inches dry. May need daily watering even in small pots.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Secure containers",
                "description": "Wind tips top-heavy plants in pots. Weight containers (rocks in saucers), use plant caddies, or stake to fixed objects.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Begin training",
                "description": "Top, LST at 4-5 nodes. Keep bushy, not tall — top-heavy outdoor containers tip in wind.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Root zone temp below 85°F?",
            "Heat management implemented?",
            "Watering adequate (containers dry fast)?",
            "Containers secured against wind?",
        ],
        "common_problems": [
            {
                "issue": "Root zone overheating (wilting in afternoon, slow growth)",
                "cause": "Container absorbing solar heat — root zone above 85°F",
                "solution": "Implement ALL heat management strategies. Switch to fabric pots if using plastic. Elevate. Shade pot surfaces. Water early morning for evaporative cooling. This is the #1 outdoor container problem.",
            },
            {
                "issue": "Container drying too fast (wilting daily)",
                "cause": "Small pot + sun + wind = extreme evaporation",
                "solution": "Transplant to larger pot sooner. Mulch top. Water twice daily if needed. Larger containers = more water buffer.",
            },
            {
                "issue": "Wind tipping containers",
                "cause": "Top-heavy plant in lightweight pot",
                "solution": "Weight the saucer (rocks/bricks). Stake to fixed object. Use wider, lower pots. Keep plants bushy, not tall.",
            },
        ],
        "training": [
            {
                "technique": "Topping",
                "description": "Top at 4-5 nodes. Keep bushy for wind stability.",
                "timing": "After 4-5 nodes",
            },
            {"technique": "LST", "description": "Bend outward for wide, low profile.", "timing": "After topping"},
        ],
        "transition_signals": [
            "Rapid growth established",
            "Roots filling intermediate pot",
            "Plant adapted to outdoor conditions",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Standard outdoor."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Heat management critical.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: less heat stress on containers, less wind."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Protected environment.",
            },
        },
    },
    # ── 4. LATE VEGETATIVE ───────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Vegetative (Peak Growth)",
        "order": 4,
        "duration_days": {"min": 21, "max": 45, "typical": 30},
        "description": "Transplant to final container (10-25 gallon). Peak summer growth. Container plants are smaller than in-ground (limited root space) but still impressive — 4-8 feet tall in 15-25 gallon pots. Water demand peaks — may need twice-daily watering in 15+ gallon pots during heat waves.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 95, "target": 82},
            "temp_night_f": {"min": 55, "max": 75, "target": 65},
            "humidity_pct": {"min": 40, "max": 80, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 2.0, "target": 1.4},
            "light_hours": {"min": 14, "max": 16},
            "light_ppfd": {"min": 800, "max": 2000, "target": 1500},
            "light_dli": {"min": 40, "max": 65, "target": 55},
            "notes": "Peak summer. Maximum water demand. Heat management is a daily task.",
        },
        "medium": {
            "pot_material": {
                "recommended": "fabric 15-25 gallon (tan/white)",
                "notes": "Fabric pots air-prune roots and stay cooler. The outdoor container standard.",
            },
            "pot_size_gal": {
                "final": "10-25 gallon",
                "notes": "10-gal for autos/small plants. 15-gal standard. 25-gal for maximum production. Bigger = more water buffer.",
            },
            "heat_management": {
                "description": "Peak heat season. All strategies must be active.",
                "strategies": [
                    "Fabric pots are 10-20°F cooler than plastic",
                    "Water early morning for evaporative cooling",
                    "Mulch top 3-4 inches",
                    "Elevate for bottom airflow",
                    "Group containers for side shading",
                    "Move to partial afternoon shade during heat waves (>95°F)",
                    "Pot-in-pot with insulating gap",
                ],
            },
            "mobility_plan": "MOBILITY ADVANTAGE: move to afternoon shade during heat waves. Move under cover before rain. Move inside during cold snaps. Rotate for even sun exposure. This is why outdoor containers exist.",
            "notes": "Water demand at peak: 1-3 gallons per plant per day for 15-gallon pots. During heat waves: 3-5 gallons or twice-daily watering. Containers dry from ALL surfaces (top, sides, bottom) unlike in-ground which only dries from top. This is 2-3x faster drying than in-ground. Drip irrigation strongly recommended at this stage.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half strength. Container medium depletes faster than in-ground. Feed more frequently than outdoor soil (in-ground). Every other watering or through drip.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 0.5,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Transplant to final container",
                "description": "Move to final 10-25 gallon pot. Pre-moisten medium. Apply mycorrhizae to root ball.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Daily (or twice-daily) watering",
                "description": "Containers dry fast. Check twice daily in hot weather. Water when top 1-2 inches dry. Deep drench to 10-15% runoff each time.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Active heat management",
                "description": "Monitor root zone temp. Move to shade during heat waves. Water early morning.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Feed every other watering",
                "description": "Container medium depletes fast. Half-strength nutrients every other watering.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Training and canopy management",
                "description": "Keep bushy and low for wind stability. Top multiple times. LST.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Secure containers for storms",
                "description": "Check forecasts. Move or anchor containers before wind/rain events.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Root zone temp below 85°F?",
            "Watering adequate?",
            "Plant not wilting in afternoon?",
            "Containers secure?",
            "Feeding schedule maintained?",
        ],
        "common_problems": [
            {
                "issue": "Root binding (plant stunted, rootball circling)",
                "cause": "Container too small for vigorous outdoor plant",
                "solution": "Transplant to larger container if still in veg. Fabric pots air-prune and reduce circling. Once root-bound: the plant's maximum size is limited.",
            },
            {
                "issue": "Chronic wilting despite watering",
                "cause": "Root zone overheating, or root-bound plant can't absorb enough water",
                "solution": "Check root zone temp (feel pot sides — if hot to touch, roots are stressed). Move to shade. Increase pot size. Water twice daily.",
            },
            {
                "issue": "Salt buildup (leaf tip burn)",
                "cause": "Container medium concentrates salts faster than in-ground",
                "solution": "Flush with plain water at 3x pot volume. Resume feeding at lower strength. This is common in containers — less soil volume means faster salt accumulation.",
            },
        ],
        "training": [
            {
                "technique": "Multiple topping",
                "description": "Top 2-3 times for wide bushy structure.",
                "timing": "Every 2-3 weeks through veg",
            },
            {
                "technique": "LST",
                "description": "Bend branches outward. Keep plant wider than tall.",
                "timing": "Ongoing",
            },
        ],
        "transition_signals": ["Day length dropping below 14.5 hours", "Plant at target size", "Pre-flower pistils"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Peak summer management."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Heat management daily.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: less heat stress, can use light dep."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "More control.",
            },
        },
    },
    # ── 5. TRANSITION ────────────────────────────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Natural Trigger)",
        "order": 5,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Natural photoperiod triggers flowering. Container plants stretch less than in-ground (root space limits overall size) but still add 50-100% height. MOBILITY ADVANTAGE: can move containers to optimize light exposure during shorter fall days. Move to catch maximum sun.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 90, "target": 80},
            "temp_night_f": {"min": 50, "max": 65, "target": 58},
            "humidity_pct": {"min": 40, "max": 70, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.6, "target": 1.3},
            "light_hours": {"min": 12.5, "max": 14},
            "light_ppfd": {"min": 600, "max": 1800, "target": 1200},
            "light_dli": {"min": 30, "max": 50, "target": 40},
            "notes": "Late summer → early fall. Days shortening. Move containers to maximize remaining sun hours.",
        },
        "medium": {
            "pot_material": {"notes": "Final pot. Heat management easing as temps drop."},
            "pot_size_gal": {"notes": "Final 10-25 gallon."},
            "heat_management": {
                "description": "Heat stress easing. Container temp management shifts from cooling to warming in late fall.",
                "strategies": [
                    "Heat management less critical as temps drop",
                    "May need to warm containers as nights cool (dark-colored pots become an advantage in fall)",
                ],
            },
            "mobility_plan": "Move containers to maximize sun exposure. As sun angle drops, buildings/trees cast longer shadows — reposition for maximum light. This is the killer container advantage in fall.",
            "notes": "Shift to bloom feeding. Water demand may decrease slightly as temps drop. But container drying continues — wind accelerates fall drying. Don't assume cooler = less watering.",
        },
        "nutrients": {
            "strength_pct": 65,
            "approach": "Transition ratio. Every other watering.",
            "flora_micro_ml_per_gal": 1.625,
            "flora_gro_ml_per_gal": 1.0,
            "flora_bloom_ml_per_gal": 1.25,
            "calmag_ml_per_gal": 0.5,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Shift to bloom feeding",
                "description": "Transition nutrient ratio. Every other watering.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Reposition for sun optimization",
                "description": "As shadows lengthen, move containers to catch maximum sun. South-facing walls reflect additional light.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Manage stretch",
                "description": "Supercrop, reinforce supports. Top-heavy stretching plants in pots are a wind hazard.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Open canopy. Bud rot prevention starts now.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "BT spray for caterpillars",
                "description": "Weekly during flower initiation.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Prepare for weather events",
                "description": "Have a plan to move containers under cover for rain/frost.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Stretch manageable?",
            "Bud sites forming?",
            "Containers positioned for max sun?",
            "Supports adequate?",
        ],
        "common_problems": [
            {
                "issue": "Container tipping from stretch + wind",
                "cause": "Tall stretching plant caught by wind",
                "solution": "Stake to fixed object. Weight saucer. Keep plants bushy.",
            },
            {
                "issue": "Light pollution from nearby sources",
                "cause": "Street lights, porch lights during dark period",
                "solution": "Move containers to dark area during night. Or use opaque cover. MOBILITY ADVANTAGE.",
            },
        ],
        "training": [
            {
                "technique": "Supercropping",
                "description": "Bend tall stems for height control.",
                "timing": "First 2 weeks of stretch",
            },
        ],
        "transition_signals": ["Stretch slowing", "Pistils at bud sites", "Day length below 13 hours"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Natural trigger."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Standard.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Light dep for early trigger."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Light dep advantage.",
            },
        },
    },
    # ── 6. EARLY FLOWER ──────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Buds forming. Container advantage: can bring plants inside or under cover during rain events. This is a MASSIVE advantage over in-ground growing for bud rot prevention. Every rain event is a decision: cover/move the containers or risk the rain.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 85, "target": 75},
            "temp_night_f": {"min": 45, "max": 60, "target": 52},
            "humidity_pct": {"min": 40, "max": 70, "target": 50},
            "vpd_kpa": {"min": 1.0, "max": 1.6, "target": 1.3},
            "light_hours": {"min": 11.5, "max": 12.5},
            "light_ppfd": {"min": 500, "max": 1500, "target": 1000},
            "light_dli": {"min": 25, "max": 40, "target": 30},
            "notes": "Early fall. Cooler. Move containers to maximize sun and avoid rain.",
        },
        "medium": {
            "pot_material": {"notes": "Final pot."},
            "pot_size_gal": {"notes": "Final 10-25 gallon."},
            "heat_management": {
                "description": "Less critical. Nights getting cool.",
                "strategies": [
                    "Warming may become needed — dark pots absorb heat",
                    "Move against south-facing wall for thermal mass",
                ],
            },
            "mobility_plan": "RAIN PROTECTION: move containers under cover (garage, porch, overhang) during rain events. This is the #1 outdoor container advantage during flower. One rain dodge can save your entire crop.",
            "notes": "Full bloom feeding. Container medium depleting — may need more frequent feeding than in-ground. Water demand moderate (not peak summer levels). Rain protection via mobility is the defining container strategy during flower.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Full bloom. Every other watering.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 0.5,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Full bloom feeding",
                "description": "Every other watering at 3/4 strength.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Rain protection protocol",
                "description": "Monitor forecast. Move containers under cover before rain. Move back to full sun after rain. This is the container advantage.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Bud rot prevention",
                "description": "Defoliate. Shake after any moisture exposure. Inspect every 2 days.",
                "interval_days": 2,
                "priority": "high",
            },
            {"name": "BT spray", "description": "Weekly for caterpillars.", "interval_days": 7, "priority": "high"},
            {
                "name": "Support branches",
                "description": "Stakes, cages. Top-heavy buds + wind.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Buds forming?",
            "No bud rot?",
            "Rain protection plan active?",
            "Containers positioned for max sun?",
        ],
        "common_problems": [
            {
                "issue": "Can't move large containers (too heavy)",
                "cause": "15-25 gallon pots with wet soil weigh 50-100+ lbs",
                "solution": "Plant caddies with wheels. Dolly. Position containers near cover from the start. Or use lighter medium (coco/perlite instead of soil).",
            },
            {
                "issue": "Bud rot from rain exposure",
                "cause": "Didn't move containers before rain, or can't move them",
                "solution": "Use tarps over containers if too heavy to move. Shake plants after rain. Defoliate heavily.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation",
                "description": "Aggressive defoliation for airflow.",
                "timing": "Every 2 weeks through flower",
            },
        ],
        "transition_signals": ["Buds fattening", "Trichomes forming", "Flower aroma"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Rain dodge with mobility."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Mobility is everything.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: already rain-protected."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Already protected.",
            },
        },
    },
    # ── 7. MID FLOWER ────────────────────────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Peak Bloom)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Peak bud development. Container mobility is your weapon against weather. Every rain event: decide — move or cover. Every frost warning: bring inside or cover. Container growers lose far less to weather than in-ground growers.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 80, "target": 72},
            "temp_night_f": {"min": 40, "max": 55, "target": 48},
            "humidity_pct": {"min": 40, "max": 70, "target": 50},
            "vpd_kpa": {"min": 1.0, "max": 1.6, "target": 1.3},
            "light_hours": {"min": 11, "max": 12},
            "light_ppfd": {"min": 400, "max": 1200, "target": 800},
            "light_dli": {"min": 20, "max": 35, "target": 25},
            "notes": "Fall weather. Move containers to maximize sun angle. South-facing walls reflect extra light.",
        },
        "medium": {
            "pot_material": {"notes": "Final pot."},
            "pot_size_gal": {"notes": "Final 10-25 gallon."},
            "heat_management": {
                "description": "Heat not the issue now — cold nights becoming concern.",
                "strategies": [
                    "Move against south-facing wall for overnight thermal mass",
                    "Dark pots now an advantage — absorb daytime heat",
                ],
            },
            "mobility_plan": "CRITICAL: move for rain, frost, and sun optimization. Heavy pots: use dollies or have a partner. Plan routes from sun position to cover.",
            "notes": "Reduce watering. Plants drinking less in fall. Container drying slower in cooler temps. But don't let them dry out completely — roots still active. Feed at reduced strength.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Peak bloom reducing. Every other watering.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.5,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Daily bud inspection",
                "description": "Check every bud for rot. Container plants may have better airflow than in-ground but still vulnerable.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Weather-based moves",
                "description": "Rain: move under cover. Frost: bring inside or cover with frost cloth. Sun: position for maximum exposure.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Harvest planning",
                "description": "Track weather and trichomes. Container advantage: you can bring plants inside to finish if weather turns bad.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Support branches",
                "description": "Heavy buds in wind-exposed containers.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["No bud rot?", "Trichomes developing?", "Frost protection ready?", "Move plan in place?"],
        "common_problems": [
            {
                "issue": "Can't move heavy containers fast enough before storm",
                "cause": "Wet 20-gallon pots weigh 80-100+ lbs",
                "solution": "Pre-position near cover from start of flower. Keep dollies under pots. Have tarps ready. A tarp over containers in place is faster than moving them.",
            },
            {
                "issue": "Bud rot despite mobility",
                "cause": "Humidity, morning dew",
                "solution": "Shake plants at sunrise. Defoliate aggressively. Move to area with morning sun (faster dew evaporation).",
            },
        ],
        "training": [],
        "transition_signals": ["Buds dense", "Trichomes milky", "Pistils turning"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Mobility is the advantage."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Move for weather.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Already protected."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Protected.",
            },
        },
    },
    # ── 8. LATE FLOWER ───────────────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Ripening. Container advantage: if frost threatens, bring plants INSIDE to finish. This alone can save an entire harvest that in-ground growers would lose. Many outdoor container growers finish the last 1-2 weeks inside under lights.",
        "environment": {
            "temp_day_f": {"min": 55, "max": 75, "target": 68},
            "temp_night_f": {"min": 35, "max": 50, "target": 45},
            "humidity_pct": {"min": 40, "max": 70, "target": 50},
            "vpd_kpa": {"min": 0.8, "max": 1.4, "target": 1.1},
            "light_hours": {"min": 10.5, "max": 11.5},
            "light_ppfd": {"min": 300, "max": 1000, "target": 700},
            "light_dli": {"min": 15, "max": 30, "target": 20},
            "notes": "Late fall. Frost risk high. Container mobility is critical.",
        },
        "medium": {
            "pot_material": {"notes": "Final pot."},
            "pot_size_gal": {"notes": "Final 10-25 gallon."},
            "heat_management": {
                "description": "Cold protection now, not heat.",
                "strategies": [
                    "Move against warm south wall",
                    "Bring inside for cold nights",
                    "Dark pots absorb daytime heat — now beneficial",
                ],
            },
            "mobility_plan": "BRING INSIDE if frost threatens. Move to garage, basement, or spare room with a shop light on 11/13 schedule. Finish indoors for 1-2 weeks if needed. THE container endgame advantage.",
            "notes": "Minimal watering. Plants barely drinking. Stop all feeding.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Stop feeding. Plain water only if needed.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {"name": "Daily bud rot inspection", "description": "Critical.", "interval_days": 1, "priority": "high"},
            {"name": "Trichome checks", "description": "Track milky → amber.", "interval_days": 2, "priority": "high"},
            {
                "name": "Frost protocol",
                "description": "Bring inside or cover at night when temps drop below 35°F. Container advantage: you CAN bring them inside.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Indoor finish decision",
                "description": "If extended cold/rain forecast: bring inside, set up a light on 11/13, finish last 1-2 weeks indoors.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Trichomes progressing?", "No rot?", "Indoor finish space ready?"],
        "common_problems": [
            {
                "issue": "Plant too large to bring inside",
                "cause": "6-8 foot plant in 20-gallon pot",
                "solution": "Bring in sideways through wide doors. Or prune lower branches to fit. Or set up in garage with shop light.",
            },
        ],
        "training": [],
        "transition_signals": ["Trichomes milky/amber", "Fan leaves dropping", "Frost imminent"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Move inside if needed."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Mobility saves crops.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Frost protection built in."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Protected.",
            },
        },
    },
    # ── 9. FLUSH ─────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 7},
        "description": "Container flush is more effective than in-ground because you can actually flush the limited volume of medium. Run 3x pot volume of plain water through to remove salts. Organic/amended medium: skip formal flush, just stop feeding.",
        "environment": {
            "temp_day_f": {"min": 50, "max": 70, "target": 62},
            "temp_night_f": {"min": 35, "max": 50, "target": 42},
            "humidity_pct": {"min": 40, "max": 70, "target": 55},
            "vpd_kpa": None,
            "light_hours": {"min": 10, "max": 11},
            "light_ppfd": {"min": 200, "max": 800, "target": 500},
            "light_dli": {"min": 10, "max": 20, "target": 15},
            "notes": "Late fall or indoors if moved inside.",
        },
        "medium": {
            "pot_material": {"notes": "Final pot."},
            "pot_size_gal": {"notes": "Final 10-25 gallon."},
            "heat_management": None,
            "mobility_plan": "Flush outdoors if weather allows (water runoff). Or flush in bathtub/shower if brought inside.",
            "notes": "Synthetic feeding: flush 3x pot volume of plain water through container. Organic/amended: just stop inputs. Container flush is more controllable than in-ground.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Plain water flush.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Flush containers",
                "description": "Run 3x pot volume of plain water through each container. 15-gallon pot = 45 gallons of water. Do in batches.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Continue bud checks",
                "description": "Still checking for rot.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Runoff EC dropping?", "Natural yellowing?", "No rot?"],
        "common_problems": [
            {
                "issue": "Overwatering during flush (root rot)",
                "cause": "Excessive water sitting in saucer",
                "solution": "Elevate containers for drainage. Empty saucers after flushing. Allow some dryback between flush events.",
            },
        ],
        "training": [],
        "transition_signals": ["Dramatic yellowing", "Trichomes at target"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Flush outside for drainage."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Good drainage.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Flush in greenhouse."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Standard.",
            },
        },
    },
    # ── 10. HARVEST ──────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Container harvest is easier than in-ground — bring the plant inside to a comfortable work area. No hunching in the garden. Smaller yields than in-ground (root space limited) but still impressive: 0.5-3 lbs per 15-25 gallon container.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 40, "max": 60, "target": 50},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Move containers inside for comfortable processing.",
        },
        "medium": {
            "pot_material": {"notes": "After harvest: medium can be reused."},
            "pot_size_gal": {"notes": "N/A."},
            "heat_management": None,
            "mobility_plan": "Bring containers to processing area. Comfortable indoor work.",
            "notes": "After harvest: remove root ball. Compost spent medium (if organic) or recondition (if coco/peat). Clean containers for next season. Fabric pots can be machine washed.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Move containers inside",
                "description": "Bring to processing area. Work comfortably.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Harvest plants",
                "description": "Cut at base or branch by branch.",
                "interval_days": None,
                "priority": "high",
            },
            {"name": "Inspect for rot", "description": "Check every bud.", "interval_days": None, "priority": "high"},
            {
                "name": "Clean containers",
                "description": "Remove root ball. Wash fabric pots. Store for next season.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["All plants harvested?", "Rot-free buds separated?", "Containers cleaned?"],
        "common_problems": [
            {
                "issue": "Root ball stuck in hard plastic pot",
                "cause": "Root-bound plant in rigid container",
                "solution": "Fabric pots: peel off. Plastic: squeeze sides, invert, tap bottom. Air-Pots: unclip sides.",
            },
        ],
        "training": [],
        "transition_signals": ["All plants chopped", "Material hung"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Bring inside."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor processing.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Process in greenhouse."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Comfortable.",
            },
        },
    },
    # ── 11. DRYING ───────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Standard indoor dry. 60°F / 60% RH / dark. Container yields are more manageable than in-ground — less volume to dry at once.",
        "environment": {
            "temp_day_f": {"min": 58, "max": 65, "target": 60},
            "temp_night_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Standard 60/60 indoor dry.",
        },
        "medium": {
            "pot_material": None,
            "pot_size_gal": None,
            "heat_management": None,
            "mobility_plan": "N/A — drying is indoor.",
            "notes": "Post-harvest. Containers being cleaned/stored.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Hang branches",
                "description": "Standard. 60/60 dark.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor conditions",
                "description": "Dehumidifier/AC as needed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check progress",
                "description": "Bend stems. Snap = ready.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["60/60?", "Dark?", "No mold?"],
        "common_problems": [
            {
                "issue": "Drying too fast",
                "cause": "Low humidity",
                "solution": "Add humidity. Wet towel in room. Humidifier.",
            },
        ],
        "training": [],
        "transition_signals": ["Small stems snap", "7-14 days"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Dry indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always indoors.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Can dry in dark greenhouse if temp-controlled."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Possible.",
            },
        },
    },
    # ── 12. CURING ───────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Standard mason jar cure. Container-grown outdoor flower cures beautifully — outdoor terpene profiles from real sun + container-optimized root zone. Manageable volume compared to in-ground monsters.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "In-jar 58-62% RH. Dark, cool.",
        },
        "medium": {
            "pot_material": None,
            "pot_size_gal": None,
            "heat_management": None,
            "mobility_plan": "N/A — curing is indoor.",
            "notes": "Post-harvest.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Trim and jar",
                "description": "Standard. Mason jars or grove bags.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Burp containers",
                "description": "2-3x/day week 1, 1x/day week 2.",
                "interval_days": None,
                "priority": "high",
            },
            {"name": "Monitor for mold", "description": "Daily inspection.", "interval_days": 1, "priority": "high"},
        ],
        "health_checks": ["58-62% RH?", "No mold/ammonia?", "Improving aroma?"],
        "common_problems": [
            {"issue": "Ammonia smell", "cause": "Too wet when jarred", "solution": "Remove, dry 12-24 hours, rejar."},
        ],
        "training": [],
        "transition_signals": ["Rich aroma", "Smooth smoke", "Stable humidity"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Cure indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor cure.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Cure indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Standard.",
            },
        },
    },
    # ── 13. STORAGE ──────────────────────────────────────────────────────
    {
        "id": "storage",
        "name": "Long-Term Storage",
        "order": 13,
        "duration_days": {"min": 30, "max": 365, "typical": 180},
        "description": "Post-cure long-term storage. Outdoor container yields are smaller than in-ground (root space limited) but still substantial — 0.5-3 lbs per 15-25 gallon container. Storage is manageable. Container-grown outdoor flower benefits from both sun-driven terpene development and container-optimized root zones. Extra mold vigilance for outdoor-exposed flower.",
        "environment": {
            "temp_day_f": {"min": 55, "max": 65, "target": 60},
            "temp_night_f": {"min": 55, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK. Cool. Stable. Zero light — UV destroys cannabinoids and terpenes. Commercial: 58-62°F, 55-60% RH, nitrogen atmosphere.",
        },
        "medium": None,
        "nutrients": {
            "strength_pct": 0,
            "approach": "None.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Transfer to long-term containers",
                "description": "Home: mason jars with Boveda 58-62%. Commercial: nitrogen-sealed grove bags, CVault, or nitrogen-flushed drums. Container yields are more manageable than in-ground.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Extra mold inspection for outdoor flower",
                "description": "Outdoor flower had environmental mold spore exposure. Inspect more frequently first month.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Label and track batches",
                "description": "Strain, harvest date, storage date, weight, batch number, container size/medium. Commercial: seed-to-sale, FIFO.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monthly quality checks",
                "description": "Inspect for mold, off odors. Check humidity packs. Commercial: potency/terpene testing at 30/90/180 days.",
                "interval_days": 30,
                "priority": "high",
            },
            {
                "name": "Maintain environment",
                "description": "Monitor vault temp/humidity. No light leaks. Commercial: automated alerts.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Rotate stock (FIFO)",
                "description": "First in, first out. Flag batches approaching 12 months.",
                "interval_days": 30,
                "priority": "medium",
            },
            {
                "name": "Compliance testing holds",
                "description": "Commercial: retain samples per regulations.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Temp 55-65°F?",
            "Humidity 55-62%?",
            "Complete darkness?",
            "No mold/off odors?",
            "Humidity packs active?",
            "FIFO maintained?",
        ],
        "common_problems": [
            {
                "issue": "Mold from outdoor spore exposure",
                "cause": "Outdoor flower carries more environmental mold spores",
                "solution": "Extra inspection first 30 days. Nitrogen-sealed containers reduce risk.",
            },
            {
                "issue": "THC degrading to CBN",
                "cause": "Heat, light, oxygen, or time",
                "solution": "Darkness, cool temps (60°F), minimal oxygen. ~5%/year baseline.",
            },
            {
                "issue": "Terpene loss",
                "cause": "Temps above 70°F, oxygen, frequent opening",
                "solution": "Below 65°F. Nitrogen-sealed. Minimize opening.",
            },
            {
                "issue": "Weight loss",
                "cause": "Normal moisture equilibration",
                "solution": "Boveda packs. Sealed containers.",
            },
        ],
        "training": [],
        "transition_signals": ["N/A — terminal stage"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Storage is always indoor. Extra mold checks for outdoor flower."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor controlled environment.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Do NOT store in greenhouse."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Climate-controlled indoor space only.",
            },
        },
        "commercial_scale": {
            "container_progression": {
                "home_small": "Mason jars with Boveda packs",
                "home_large": "Grove bags or CVault containers",
                "commercial_small": "Nitrogen-sealed grove bags (1 lb units)",
                "commercial_medium": "Turkey bags in sealed bins, nitrogen-flushed",
                "commercial_large": "Nitrogen-flushed drums (5-50 lb) in vault",
                "industrial": "Climate-controlled vault, nitrogen generators, automated monitoring",
            },
            "degradation_timeline": {
                "0_3_months": "Peak quality. Outdoor sun-driven terps at their best.",
                "3_6_months": "Slight terpene reduction (~10-15%). Potency stable.",
                "6_12_months": "Noticeable terpene loss (~20-30%). THC down ~5%.",
                "12_18_months": "Significant decline. Process into extracts.",
                "18_plus_months": "Convert to extracts, edibles, or topicals.",
            },
            "testing_schedule": {
                "initial": "Full panel at harvest (extra microbial testing for outdoor)",
                "30_days": "Potency + terpenes + microbials (post-cure baseline)",
                "90_days": "Potency + terpenes + microbials",
                "180_days": "Full panel retest",
                "360_days": "Full panel — sell, process, or destroy decision",
            },
        },
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT
# ─────────────────────────────────────────────────────────────────────────────

OUTDOOR_CONTAINER_EQUIPMENT: list[dict] = [
    # -- Containers --
    {
        "name": "Fabric pots (15-25 gallon)",
        "category": "containers",
        "required": True,
        "notes": "THE outdoor container choice. Air-prune roots, 10-20°F cooler than plastic, breathable. Tan or white preferred for heat reflection. Smart Pot, Root Pouch, GeoPot are quality brands.",
    },
    {
        "name": "Air-Pots (alternative)",
        "category": "containers",
        "required": False,
        "notes": "Excellent aeration and air-pruning. More expensive. Work well outdoors.",
    },
    {
        "name": "Saucers (heavy-duty)",
        "category": "containers",
        "required": True,
        "notes": "Catch runoff. Use plant caddies underneath saucers.",
    },
    {
        "name": "Plant caddies / dollies",
        "category": "containers",
        "required": True,
        "notes": "ESSENTIAL for mobility. Heavy-duty rolling platforms for 15-25 gallon pots. The mobility tool. Budget for one per plant.",
    },
    # -- Growing medium --
    {
        "name": "Quality potting soil or super soil",
        "category": "medium",
        "required": True,
        "notes": "Pre-mixed or build your own. Must be well-draining. Add 30% perlite for outdoor containers (drainage is critical).",
    },
    {
        "name": "Perlite (extra)",
        "category": "medium",
        "required": True,
        "notes": "30% perlite minimum in outdoor containers. Drainage + aeration.",
    },
    {
        "name": "Mulch (straw or cover crop)",
        "category": "medium",
        "required": True,
        "notes": "Top of container. 3-4 inches. Retains moisture, reduces heat, suppresses weeds. Living mulch (clover) also works.",
    },
    # -- Irrigation --
    {
        "name": "Drip irrigation (per-container)",
        "category": "irrigation",
        "required": True,
        "notes": "Drip ring or stake emitters for each container. Timer. Essential at outdoor container scale — hand watering daily is unsustainable.",
    },
    {
        "name": "Watering wand (backup)",
        "category": "irrigation",
        "required": False,
        "notes": "For manual watering and flushing.",
    },
    # -- Protection --
    {
        "name": "Frost cloth / row cover",
        "category": "protection",
        "required": True,
        "notes": "For covering containers in place when too heavy to move.",
    },
    {
        "name": "Tarps",
        "category": "protection",
        "required": True,
        "notes": "Quick rain protection. Throw over plants/containers.",
    },
    {
        "name": "Shade cloth (30-50%)",
        "category": "protection",
        "required": False,
        "notes": "For heat waves above 95°F.",
    },
    {
        "name": "Wind stakes / guy wires",
        "category": "protection",
        "required": True,
        "notes": "Secure tall plants in containers against wind. Tip-over prevention.",
    },
    # -- Support --
    {
        "name": "Tomato cages or bamboo stakes",
        "category": "support",
        "required": True,
        "notes": "Branch support. Top-heavy outdoor container plants need reinforcement.",
    },
    {
        "name": "Trellis netting",
        "category": "support",
        "required": False,
        "notes": "ScrOG for outdoor containers if space allows.",
    },
    # -- Pest control --
    {
        "name": "BT (Bacillus thuringiensis)",
        "category": "pest_control",
        "required": True,
        "notes": "Weekly in flower for caterpillars.",
    },
    {"name": "Neem oil", "category": "pest_control", "required": True, "notes": "Veg only."},
    # -- Monitoring --
    {
        "name": "Weather app / station",
        "category": "monitoring",
        "required": True,
        "notes": "Forecasts drive mobility decisions.",
    },
    {
        "name": "Soil moisture meter",
        "category": "monitoring",
        "required": True,
        "notes": "Critical for containers — they dry fast.",
    },
    {"name": "Jeweler's loupe (60-100x)", "category": "monitoring", "required": True, "notes": "Trichome inspection."},
    {
        "name": "Infrared thermometer",
        "category": "monitoring",
        "required": False,
        "notes": "Check container surface temp and root zone temp. Very useful for heat management.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

OUTDOOR_CONTAINER_QUICK_REFERENCE: dict = {
    "ph_range": {
        "min": 6.0,
        "max": 7.0,
        "sweet_spot": 6.5,
        "notes": "Same as indoor soil. Adjust if using coco (5.5-6.5) or peat (5.8-6.5).",
    },
    "pot_material_guide": {
        "description": "Container material selection is the first and most important decision for outdoor container growing.",
        "fabric": {
            "brands": "Smart Pot, Root Pouch, GeoPot",
            "pros": "Air-prunes roots, 10-20°F cooler than plastic, excellent drainage, lightweight dry, folds for storage",
            "cons": "Dries faster (more watering), can tip in wind, less structural rigidity",
            "best_for": "Hot climates, any outdoor container grow",
            "colors": "Tan > White > Gray >> Brown >> Black. AVOID BLACK FABRIC — still absorbs significant heat.",
            "rating": "BEST for outdoor",
        },
        "air_pot": {
            "pros": "Excellent air-pruning, good drainage, rigid structure",
            "cons": "Expensive, harder to find large sizes, can dry fast",
            "best_for": "Premium grows, windy locations (rigid)",
            "rating": "Excellent",
        },
        "light_plastic": {
            "pros": "Cheap, retains moisture longer, easy to find",
            "cons": "No air-pruning, root circling, hotter than fabric",
            "best_for": "Budget grows in mild climates",
            "colors": "White > Tan > Green >> Brown >> Black. NEVER black plastic in sun.",
            "rating": "Acceptable",
        },
        "terracotta_ceramic": {
            "pros": "Thermal mass (slower temp swings), beautiful, heavy (wind-stable)",
            "cons": "Heavy (hard to move — defeats mobility purpose), fragile, expensive at large sizes",
            "best_for": "Patio aesthetics where mobility is secondary",
            "rating": "Not recommended for serious grows (mobility loss)",
        },
    },
    "pot_sizing_guide": {
        "description": "Pot size determines plant size, yield, and watering frequency.",
        "5_gallon": {
            "plant_height": "2-3 feet",
            "yield": "2-6 oz",
            "watering": "1-2x daily in summer",
            "best_for": "Autoflowers, stealth, balcony",
            "notes": "Small but manageable.",
        },
        "10_gallon": {
            "plant_height": "3-5 feet",
            "yield": "4-12 oz",
            "watering": "1x daily",
            "best_for": "Good all-around for limited space",
        },
        "15_gallon": {
            "plant_height": "4-6 feet",
            "yield": "8-24 oz",
            "watering": "1x daily (maybe 2x in heat)",
            "best_for": "SWEET SPOT. Good size, still moveable.",
        },
        "20_gallon": {
            "plant_height": "5-7 feet",
            "yield": "12-36 oz",
            "watering": "Every 1-2 days",
            "best_for": "Serious production. Getting heavy to move.",
        },
        "25_gallon": {
            "plant_height": "6-8 feet",
            "yield": "1-3 lbs",
            "watering": "Every 1-2 days",
            "best_for": "Maximum production. Needs dolly to move.",
        },
        "30_plus_gallon": {
            "plant_height": "6-10 feet",
            "yield": "2-5 lbs",
            "watering": "Every 2-3 days",
            "best_for": "Stationary grows (too heavy for mobility). Approaching in-ground yields.",
        },
    },
    "heat_management_guide": {
        "description": "Container heat management is THE #1 outdoor container challenge. Root zone above 85°F = stress. Above 95°F = root death.",
        "problem": "Containers in direct sun absorb massive heat. A black plastic pot in 90°F air = 120-130°F pot surface. Even fabric pots reach 100-110°F in extreme heat.",
        "strategies": {
            "tier_1_essential": [
                "Use fabric pots (tan/white)",
                "Mulch top of container (3-4 inches)",
                "Water early morning (evaporative cooling)",
                "Elevate containers for bottom airflow",
            ],
            "tier_2_recommended": [
                "Group containers (mutual shading of pot sides)",
                "Position against walls for afternoon shade on pots",
                "Pot-in-pot: nest in larger container with air gap or insulation",
            ],
            "tier_3_extreme_heat": [
                "Move to afternoon shade during heat waves (>95°F)",
                "Shade cloth on containers (not plants) during heat waves",
                "Wrap pots in reflective material (emergency)",
                "Ice water for extreme events (temporary)",
            ],
        },
        "temperature_benchmarks": {
            "ideal_root_zone": "65-80°F",
            "stress_begins": "85°F",
            "significant_damage": "90°F sustained",
            "root_death": "95°F+ sustained",
        },
    },
    "mobility_strategies": {
        "description": "Container mobility is the defining advantage of outdoor container growing.",
        "use_cases": [
            "Rain protection: move under cover before rain (bud rot prevention)",
            "Frost protection: bring inside for cold nights",
            "Sun optimization: reposition as shadows shift seasonally",
            "Light dep: move to dark space for early flowering",
            "Stealth: move out of sight when needed",
            "Wind protection: move to sheltered area before storms",
            "Pest isolation: move affected plant away from others",
            "Indoor finish: bring inside last 1-2 weeks if weather turns",
        ],
        "tools": [
            "Plant caddies with wheels (essential)",
            "Dollies for heavy pots",
            "Furniture sliders on hard surfaces",
            "Two-person lift for 20+ gallon wet pots",
        ],
        "planning": "Map your routes: sun position → cover position → indoor position. Keep paths clear. Test with full (wet) pots before flower.",
    },
    "watering_guide": {
        "description": "Outdoor containers dry 2-3x faster than in-ground. The #2 challenge after heat.",
        "why_faster": "Containers lose moisture from ALL surfaces: top (evaporation), sides (sun heating, wind), bottom (gravity). In-ground only loses from top.",
        "frequency_by_temp": {
            "below_70F": "Every 2-3 days",
            "70_80F": "Daily",
            "80_90F": "Daily, possibly twice",
            "above_90F": "Twice daily, or install drip irrigation",
        },
        "tips": [
            "Drip irrigation with timer is nearly essential at scale",
            "Mulch top 3-4 inches to reduce evaporation",
            "Water early morning — evaporative cooling + full water for hot day",
            "Larger pots = more water buffer = less frequent watering",
            "Fabric pots dry fastest (trade-off for root health benefits)",
        ],
    },
    "golden_rules": [
        "Fabric pots in tan/white. The #1 equipment decision.",
        "Heat management from day 1. Root zone below 85°F always.",
        "Plant caddies under every container. Mobility is the advantage.",
        "Drip irrigation with timer. Hand-watering daily is unsustainable.",
        "Mulch the top of every container. 3-4 inches.",
        "Keep plants bushy, not tall. Wind tips top-heavy containers.",
        "Map your mobility routes: sun → cover → inside.",
        "Rain coming during flower? MOVE. One rain dodge can save a crop.",
        "Frost warning? Bring inside. In-ground growers can't do this.",
        "15-gallon fabric pot is the sweet spot: good yield, still mobile.",
        "30% perlite in container mix. Drainage is non-negotiable.",
        "Budget for plant caddies. One per plant. Non-negotiable equipment.",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING
# ─────────────────────────────────────────────────────────────────────────────

OUTDOOR_CONTAINER_TROUBLESHOOTING: list[dict] = [
    {
        "category": "Container Heat",
        "issues": [
            {
                "symptom": "Wilting in afternoon despite wet soil",
                "cause": "Root zone overheating. Pot surface absorbing solar radiation.",
                "fix": "Feel pot sides — hot to touch = root stress. Implement all heat management: fabric pots, elevate, mulch, shade pot surfaces, water early AM. This is the #1 outdoor container problem.",
            },
            {
                "symptom": "Stunted growth, roots brown/mushy",
                "cause": "Root death from sustained heat above 95°F",
                "fix": "Move to shade immediately. Cool root zone with water. May need to transplant to new medium if roots are dead. Prevention is everything.",
            },
            {
                "symptom": "Salt crust on pot sides (fabric)",
                "cause": "Mineral deposits from evaporation through fabric sides",
                "fix": "Normal with fabric pots. Cosmetic only. Rinse off if extreme.",
            },
        ],
    },
    {
        "category": "Watering & Drying",
        "issues": [
            {
                "symptom": "Wilting every afternoon (not heat — just dry)",
                "cause": "Container drying too fast. Outdoor conditions accelerate moisture loss 2-3x.",
                "fix": "Larger pot. Mulch. Drip irrigation. Water twice daily in heat. Saucers hold some water (but don't let roots sit).",
            },
            {
                "symptom": "Root rot (mushy roots, slow growth)",
                "cause": "Poor drainage or container sitting in standing water",
                "fix": "Elevate container. Empty saucers after watering. Add perlite to mix. Ensure drainage holes are clear.",
            },
        ],
    },
    {
        "category": "Wind & Stability",
        "issues": [
            {
                "symptom": "Container tipped over",
                "cause": "Top-heavy plant caught by wind",
                "fix": "Weight saucer with rocks/bricks. Stake to fixed object. Use wider, lower containers. Keep plants bushy via training. Group containers for mutual stability.",
            },
            {
                "symptom": "Broken branches from wind",
                "cause": "Unsupported branches in exposed container location",
                "fix": "Cage or stake all branches. Move to sheltered location before storms. Supercrop if still in veg.",
            },
        ],
    },
    {
        "category": "Root Zone",
        "issues": [
            {
                "symptom": "Root-bound (slow growth, roots circling out drainage holes)",
                "cause": "Container too small for plant",
                "fix": "Transplant to larger container if in veg. If in flower: too late, manage with more frequent feeding. Fabric pots reduce this (air-pruning).",
            },
            {
                "symptom": "Nutrient deficiency despite feeding (container-specific)",
                "cause": "Small soil volume depletes fast. Salt buildup from concentrated feeding.",
                "fix": "Flush with 3x volume, resume at lower strength. Feed more frequently at lower dose. Container medium exhausts faster than in-ground.",
            },
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

OUTDOOR_CONTAINER_CONFIG: dict = {
    "grow_type_id": "outdoor_container",
    "version": "1.0.0",
    "stages": OUTDOOR_CONTAINER_STAGES,
    "equipment": OUTDOOR_CONTAINER_EQUIPMENT,
    "quick_reference": OUTDOOR_CONTAINER_QUICK_REFERENCE,
    "troubleshooting": OUTDOOR_CONTAINER_TROUBLESHOOTING,
    "total_grow_days": {"min": 120, "max": 240, "typical": 170},
}
