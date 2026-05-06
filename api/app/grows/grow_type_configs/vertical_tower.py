"""Vertical Tower — Complete grow type configuration.

Enterprise-grade configuration for vertical tower / tower garden growing.
Aeroponic or NFT-based vertical columns that maximize space efficiency.

KEY DIFFERENCES FROM OTHER HYDRO:
  - Vertical orientation — plants grow outward from a central column
  - Extremely space-efficient (10-40 plants per tower, 1 sq ft footprint)
  - Low pressure aeroponics (spray inside tower) OR trickle/NFT
  - Smaller root zones — suited to smaller plants or aggressive training
  - Gravity-fed drainage — pump lifts water to top, drains down through roots
  - Light distribution challenge — center/bottom plants get less light
  - Not ideal for large cannabis plants without heavy training
  - Popular for lettuce, herbs, strawberries — cannabis requires adaptation
  - Tower rotation (manual or motorized) helps with even light distribution

Data sources:
  - Tower Garden (aeroponic tower) specifications
  - ZipGrow (NFT tower) commercial systems
  - Cannabis vertical farming community practices
  - Indoor vertical agriculture research
"""

from __future__ import annotations

VERTICAL_TOWER_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Start seeds in rockwool cubes or net pot inserts. Tower system doesn't need to run during germination. Keep seeds warm and dark.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Germinate separately from tower. Seeds need consistent warmth and darkness.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.0, "target": 5.8},
            "ec": 0.0,
            "notes": "No tower operation needed. Plain water for starter cubes only.",
        },
        "nutrients": {"strength_pct": 0, "approach": "None — seeds self-sustaining."},
        "tasks": [
            {
                "name": "Germinate seeds",
                "description": "Paper towel method or direct in rockwool cubes. Keep warm (78°F) and dark.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check daily",
                "description": "Look for taproot emergence.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Seeds cracked?", "Taproot emerging?", "Temperature consistent?"],
        "common_problems": [
            {"issue": "Slow germination", "cause": "Too cold", "solution": "Heat mat at 78°F."},
        ],
        "training": [],
        "transition_signals": ["Cotyledons emerging", "Taproot 0.5-1 inch"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Always germinate indoors for temperature control."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse propagation area works well."},
                "extra_tasks": [],
            },
        },
    },
    # ── 2. SEEDLING ───────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Grow seedlings until roots are well-developed enough to hold in tower ports. Small plants work better in towers — don't let seedlings get too large before transplanting.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 60, "max": 75, "target": 68},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 150, "max": 300, "target": 200},
            "light_dli": {"min": 10, "max": 19, "target": 13},
            "notes": "Once roots are 2-3 inches and 3 sets of true leaves, transplant into tower net pots.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.4, "max": 0.8, "target": 0.6},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "notes": "Once in tower, start pump on timer. 15 min on, 15 min off cycle typical for low-pressure aeroponics.",
        },
        "nutrients": {
            "strength_pct": 25,
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 2.5,
            "flora_bloom_ml_per_gal": 0.6,
            "calmag_ml_per_gal": 1.0,
        },
        "tasks": [
            {
                "name": "Transplant to tower",
                "description": "Place seedling in net pot with neoprene collar. Position in tower port with roots facing inside.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Start pump cycle",
                "description": "Timer: 15 min on / 15 min off. Water cascades from top down through roots.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check all ports",
                "description": "Verify water reaching all levels. Top ports get most flow, bottom ports may need adjustment.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Monitor root development",
                "description": "Roots should grow inward toward water column. If drying, increase pump on-time.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "All tower levels receiving water?",
            "Seedlings stable in net pots?",
            "Roots growing into tower interior?",
            "No light leaks into tower (algae)?",
        ],
        "common_problems": [
            {
                "issue": "Plants falling out of ports",
                "cause": "Root mass not developed enough to hold",
                "solution": "Use neoprene collars or foam inserts. Wait until roots are longer before transplanting.",
            },
            {
                "issue": "Lower levels getting less water",
                "cause": "Gravity and upper-level absorption",
                "solution": "Increase pump time. Some towers have multiple spray points at different heights.",
            },
            {
                "issue": "Algae in tower",
                "cause": "Light entering through empty ports or translucent material",
                "solution": "Cover unused ports. Use opaque tower material. Block any light leaks.",
            },
        ],
        "training": [],
        "transition_signals": ["Roots established inside tower", "Vigorous new growth", "3-4 true leaf sets"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor towers need shade from intense afternoon sun to prevent overheating. Wind protection important (towers are top-heavy)."
                },
                "extra_tasks": [
                    {
                        "name": "Secure tower from wind",
                        "description": "Stake or weight base. Towers are top-heavy when full of plants.",
                        "interval_days": 7,
                        "priority": "high",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse towers benefit from supplemental side-lighting."},
                "extra_tasks": [],
            },
        },
    },
    # ── 3. VEGETATIVE ─────────────────────────────────────────────────────
    {
        "id": "vegetative",
        "name": "Vegetative",
        "order": 3,
        "duration_days": {"min": 21, "max": 42, "typical": 28},
        "description": "Growth phase — but keep plants SMALL. Tower growing requires aggressive training to prevent plants from shading lower levels. Think bonsai-style — compact and wide, not tall.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 300, "max": 600, "target": 450},
            "light_dli": {"min": 20, "max": 39, "target": 29},
            "notes": "Light distribution is the #1 challenge. Use 360° lighting (multiple light bars around tower) or motorized tower rotation. Veg phase should be SHORT to keep plants compact.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 1.0, "max": 1.6, "target": 1.2},
            "ppm_500": {"min": 500, "max": 800, "target": 600},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "change_interval_days": 7,
            "notes": "Tower reservoirs are often small (5-20 gal). Monitor levels closely — many plants sharing one reservoir depletes fast.",
        },
        "nutrients": {
            "strength_pct": 60,
            "flora_micro_ml_per_gal": 3.0,
            "flora_gro_ml_per_gal": 5.0,
            "flora_bloom_ml_per_gal": 1.5,
            "calmag_ml_per_gal": 2.5,
        },
        "tasks": [
            {
                "name": "Aggressive training",
                "description": "Top early (3rd-4th node). LST all branches horizontally. Keep plant profile flat and wide, not tall.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Rotate tower (if not motorized)",
                "description": "Quarter turn daily ensures even light exposure on all sides.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Check reservoir level",
                "description": "Many plants sharing small reservoir = rapid depletion. May need daily top-off.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor pH/EC",
                "description": "Small reservoirs swing faster than large ones. Check every other day minimum.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Check spray nozzles",
                "description": "Mineral buildup clogs tower spray jets. Clean or replace monthly.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Defoliate inner growth",
                "description": "Tower plants need open structure for air circulation. Remove inner fan leaves blocking airflow.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "All levels growing evenly (not just top)?",
            "Plants staying compact (not stretching toward light)?",
            "Spray reaching all root zones?",
            "No clogged nozzles?",
            "Reservoir not depleting too fast?",
        ],
        "common_problems": [
            {
                "issue": "Upper plants shading lower",
                "cause": "Insufficient training or plants too large",
                "solution": "Aggressive topping and LST. Consider fewer plants per tower. Supplement with vertical light bars.",
            },
            {
                "issue": "Rapid pH/EC swings",
                "cause": "Small reservoir shared by many plants",
                "solution": "Increase reservoir size. Or check/adjust twice daily. Auto-dosing systems help at scale.",
            },
            {
                "issue": "Dry roots on lower levels",
                "cause": "Upper levels absorbing most water",
                "solution": "Increase pump on-time. Add secondary spray point at mid-tower. Ensure drainage holes not clogged.",
            },
            {
                "issue": "Root mass blocking tower interior",
                "cause": "Roots filling the inside of the column",
                "solution": "Trim roots that are blocking water flow. Or accept reduced efficiency and increase pump time.",
            },
        ],
        "training": [
            {
                "name": "Early topping",
                "when": "3rd-4th node (earlier than typical)",
                "description": "Keep VERY short. Multiple toppings may be needed. Goal: flat canopy, not vertical growth.",
            },
            {
                "name": "Aggressive LST",
                "when": "Continuous",
                "description": "All branches trained horizontally. Nothing grows upward or inward. Think flat disc shape.",
            },
            {
                "name": "Lollipop early",
                "when": "Before flip",
                "description": "Remove all lower/inner growth. Tower plants need open structure for airflow.",
            },
        ],
        "transition_signals": [
            "Plants compact with trained flat canopy",
            "Tower ports filled but not overcrowded",
            "Healthy root development at all levels",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor towers work in warm climates. Rotate for sun exposure. Wind is a concern for stability."
                },
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Supplemental vertical lighting around tower greatly improves lower-level growth."
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
        "duration_days": {"min": 49, "max": 70, "typical": 56},
        "description": "Flip to 12/12. Tower cannabis produces many small-medium colas rather than few large ones. Focus on even light distribution and airflow. Shorter flowering strains (indica-dominant) work best in towers.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 79, "target": 75},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 40, "max": 55, "target": 45},
            "vpd_kpa": {"min": 1.0, "max": 1.5, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 800, "target": 650},
            "light_dli": {"min": 22, "max": 35, "target": 28},
            "notes": "360° lighting essential in flower. All bud sites need light. Tower rotation (if manual) should continue. Smaller yields per plant but many plants per sq ft.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.3, "target": 6.0},
            "ec": {"min": 1.2, "max": 2.0, "target": 1.6},
            "ppm_500": {"min": 600, "max": 1000, "target": 800},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "change_interval_days": 7,
            "notes": "Bloom nutrients. Water demand peaks in mid-flower.",
        },
        "nutrients": {
            "strength_pct": 85,
            "flora_micro_ml_per_gal": 4.25,
            "flora_gro_ml_per_gal": 2.0,
            "flora_bloom_ml_per_gal": 6.5,
            "calmag_ml_per_gal": 3.0,
        },
        "tasks": [
            {
                "name": "Monitor reservoir",
                "description": "Flowering towers drink heavily. Check level and top off daily.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Rotate tower",
                "description": "Quarter turn daily if not motorized.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Check spray nozzles",
                "description": "Clogged nozzles during flower = dead roots = dead buds.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Monitor bud development",
                "description": "Check all levels — lower levels may mature at different rates than upper.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Inspect for bud rot",
                "description": "Tower airflow can be poor between closely-spaced plants. Check all colas.",
                "interval_days": 3,
                "priority": "high",
            },
        ],
        "health_checks": [
            "All spray levels working?",
            "Buds developing at all tower heights?",
            "No bud rot (check lower/inner colas)?",
            "Reservoir level adequate?",
        ],
        "common_problems": [
            {
                "issue": "Uneven ripening",
                "cause": "Light variation between tower levels/sides",
                "solution": "Harvest in stages — top first, let lower ripen longer. Or improve lighting uniformity.",
            },
            {
                "issue": "Small buds on lower levels",
                "cause": "Light deprivation",
                "solution": "Accept as a limitation of vertical growing, or add vertical LED strips between tower and outer lights.",
            },
            {
                "issue": "Root mass causing pump issues",
                "cause": "Roots blocking internal drainage",
                "solution": "Trim roots carefully. Increase pump power if flow is restricted.",
            },
        ],
        "training": [
            {
                "name": "Leaf tucking",
                "when": "Throughout flower",
                "description": "Tuck fan leaves behind buds rather than removing. Maintains energy production while exposing bud sites.",
            },
        ],
        "transition_signals": ["Trichomes milky/amber", "Pistils darkened", "Buds mature at most tower levels"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor towers flower with natural photoperiod. May harvest levels separately as they ripen."
                },
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Supplemental lighting around tower maximizes greenhouse tower yields."
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
        "description": "Harvest and hang. Tower grows produce many small branches — can hang easily on drying lines.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "light_hours": 0,
        },
        "tasks": [
            {
                "name": "Check drying conditions",
                "description": "60-65°F, 55-62% RH.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Stem snap test",
                "description": "Small stems snap = ready.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Clean tower system",
                "description": "Flush all internal spray nozzles with H2O2. Scrub tower sections. Prepare for next cycle.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Temp/humidity correct?", "No mold?"],
        "common_problems": [
            {
                "issue": "Small buds drying too fast",
                "cause": "Airier buds from lower tower levels",
                "solution": "Keep humidity at 60%. Monitor smaller branches separately.",
            }
        ],
        "training": [],
        "transition_signals": ["Stems snap", "Ready for jars"],
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
        "description": "Jar cure. Tower buds are typically smaller and airier — may cure slightly faster than dense indoor buds.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "light_hours": 0,
        },
        "tasks": [
            {
                "name": "Burp jars",
                "description": "Daily for 2 weeks, then less frequently.",
                "interval_days": 1,
                "priority": "high",
            },
            {"name": "Check humidity", "description": "58-62% in jars.", "interval_days": 1, "priority": "medium"},
        ],
        "health_checks": ["Humidity correct?", "No mold?"],
        "common_problems": [
            {
                "issue": "Overly dry",
                "cause": "Smaller buds dried too much",
                "solution": "Boveda 62% pack to rehydrate slightly.",
            }
        ],
        "training": [],
        "transition_signals": ["Smooth flavor", "Proper moisture level stable"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
        },
    },
]

VERTICAL_TOWER_CONFIG: dict = {
    "id": "vertical_tower",
    "name": "Vertical Tower",
    "description": "Space-efficient vertical growing with aeroponic or NFT-based towers. Maximum plants per square foot. Requires aggressive training to manage light distribution.",
    "category": "hydroponic",
    "difficulty": "advanced",
    "stages": VERTICAL_TOWER_STAGES,
    "equipment": [
        "Vertical tower system (Tower Garden, ZipGrow, DIY PVC)",
        "Reservoir (10-20 gallon per tower)",
        "Submersible pump (lifts water to tower top)",
        "Timer (minute-resolution for pump cycles)",
        "Net pots + neoprene collars",
        "360° lighting (multiple bars around tower, or rotation motor)",
        "pH meter + EC meter",
        "Nutrients (GH Flora or equivalent)",
        "CalMag",
        "Support stakes (for plants growing outward)",
        "Rotation motor (optional — motorized 360° turn)",
    ],
    "key_principles": [
        "Keep plants SMALL and COMPACT — tower is not for growing trees",
        "Light distribution is the #1 challenge — 360° lighting or rotation mandatory",
        "Aggressive training (early topping, heavy LST) is non-negotiable",
        "Many small plants > few large plants in a tower",
        "Short-flowering indica-dominant strains work best",
        "Small reservoirs swing fast — monitor pH/EC frequently",
        "Harvest levels separately if ripening unevenly",
        "Upper levels always outperform lower — accept or add supplemental light",
        "Tower growing trades per-plant yield for per-square-foot efficiency",
    ],
}
