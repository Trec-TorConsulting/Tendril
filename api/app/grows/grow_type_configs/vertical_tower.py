"""Vertical Tower (Tower Garden) — Complete grow type configuration.

Enterprise-grade configuration for vertical tower / aeroponic tower growing.
Plants grow from multiple stacked sites around a central column with nutrient
solution pumped to the top and cascading down via gravity.

Data sources:
  - Tower Garden / Juice Plus commercial systems
  - DIY PVC tower garden builds
  - Vertical farming research
  - Cannabis vertical growing community experience
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES
# ─────────────────────────────────────────────────────────────────────────────

VERTICAL_TOWER_STAGES: list[dict] = [
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Germinate in net pot inserts or starter plugs. Tower system not running yet — seedlings develop in propagation tray.",
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
        "nutrients": {"strength_pct": 0, "approach": "Plain water for germination."},
        "tasks": [
            {
                "name": "Soak starter plugs",
                "description": "pH 5.5 water. Rapid rooters or rockwool.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Plant seeds",
                "description": "One per plug, pointed end down.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check germination",
                "description": "Look for taproot emergence.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Seeds cracking?", "Plugs staying moist?", "Temperature adequate?"],
        "common_problems": [
            {
                "issue": "Low germination rate",
                "cause": "Temperature too low",
                "solution": "Heat mat under propagation tray. 78°F target.",
            },
        ],
        "transition_signals": ["Taproot visible", "Cotyledons emerging from plug"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Germinate indoors for control."}, "extra_tasks": []},
            "greenhouse": {
                "environment_overrides": {"notes": "Propagation area in greenhouse works well."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Seedlings in plugs under mild light. Once roots emerge from plug, transplant to tower sites. Start system on gentle cycle. Lower sites preferred for seedlings (more moisture).",
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
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "notes": "Light feed. Pump on 15/60 cycle.",
        },
        "nutrients": {"strength_pct": 25, "approach": "1/4 strength veg nutrients."},
        "tasks": [
            {
                "name": "Place seedlings in tower",
                "description": "Lower sites preferred — more moisture from gravity flow.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Start pump cycle",
                "description": "15 min on / 60 min off. Gentle flow.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Verify all sites getting moisture",
                "description": "Check that solution reaches all levels. Lower = more, upper = less.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check pH/EC",
                "description": "Small reservoir changes fast. Monitor closely.",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": ["All sites receiving flow?", "Seedlings not drying?", "Roots developing?"],
        "common_problems": [
            {
                "issue": "Upper sites drying out",
                "cause": "Gravity pulls solution to lower sites faster",
                "solution": "Increase pump cycle. Ensure distribution cap on top is clear. Consider only using lower sites for seedlings.",
            },
            {
                "issue": "Seedling falling out of site",
                "cause": "Net pot too small or plant not rooted enough",
                "solution": "Use clay pebbles to stabilize. Wait until roots are more developed before transplanting.",
            },
        ],
        "transition_signals": ["Roots visible at net pot edges", "3-4 true leaves", "Stable in tower site"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Protect from wind (towers are top-heavy)."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Ideal environment for tower systems."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Plants establishing in tower sites. Roots growing into central column. Increase feed strength. Vertical canopy management becomes critical — lower sites get less light.",
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
            "notes": "Half strength. More frequent cycles.",
        },
        "nutrients": {"strength_pct": 50, "approach": "Half-strength veg. High nitrogen."},
        "tasks": [
            {
                "name": "Increase feed cycles",
                "description": "15 on / 30 off. Roots need consistent moisture in tower.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Rotate tower (if applicable)",
                "description": "Rotate 90° every 2-3 days for even light exposure.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Manage vertical canopy",
                "description": "Train plants outward, not upward. LST to prevent upper sites shading lower.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Check for root clogs",
                "description": "Roots growing into central column can block flow to lower sites.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": ["All sites growing evenly?", "Lower sites getting light?", "Central column flowing freely?"],
        "common_problems": [
            {
                "issue": "Lower sites growing slower",
                "cause": "Shaded by upper sites + less direct light",
                "solution": "Aggressive training of upper plants outward. Side lighting. Rotate tower.",
            },
            {
                "issue": "Roots blocking central column",
                "cause": "Aggressive root growth fills the internal space",
                "solution": "Trim roots that extend into central flow path. More frequent pump cycles.",
            },
        ],
        "transition_signals": ["Plants filling out from all sites", "Roots established", "Even growth across levels"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Natural light from multiple angles helps vertical distribution."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Supplement lower sites with side lighting if needed."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 14, "max": 35, "typical": 21},
        "description": "Plants growing aggressively from all tower sites. Vertical canopy management critical. Light distribution is the main challenge. Reservoir consumption increases significantly.",
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
            "notes": "Full veg strength. Monitor consumption — towers deplete fast.",
        },
        "nutrients": {"strength_pct": 75, "approach": "3/4 strength veg. High nitrogen for rapid growth."},
        "tasks": [
            {
                "name": "Monitor reservoir daily",
                "description": "Tower systems have small reservoirs. Multiple plants deplete fast.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Aggressive canopy management",
                "description": "Train all plants outward and downward. Keep center column clear.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Check pump and lines",
                "description": "Root debris can clog pump intake.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Consider removing weak sites",
                "description": "Better yield from fewer strong plants than many struggling ones.",
                "interval_days": None,
                "priority": "low",
            },
        ],
        "health_checks": [
            "Reservoir adequate?",
            "All sites producing?",
            "Light reaching all levels?",
            "Pump running properly?",
        ],
        "common_problems": [
            {
                "issue": "Reservoir depleting in hours",
                "cause": "Multiple large plants in veg drink heavily from small reservoir",
                "solution": "Larger external reservoir. Float valve auto-top-off. Consider fewer plants per tower.",
            },
            {
                "issue": "Tower top-heavy and tipping",
                "cause": "Large plants creating imbalanced weight",
                "solution": "Ballast base. Tether to wall/ceiling. Prune to maintain balance.",
            },
        ],
        "transition_signals": ["All sites filled with canopy", "Ready for flip", "Balanced growth across tower"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Secure tower against wind. Stake or tether."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Peak growth. Ventilate well."}, "extra_tasks": []},
        },
    },
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Flip to 12/12. Plants stretch 50-100%. Critical to manage — vertical tower stretch can create massive shading issues. Aggressive training essential.",
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
            "notes": "Transition formula.",
        },
        "nutrients": {"strength_pct": 75, "approach": "50% veg + 50% bloom transition."},
        "tasks": [
            {
                "name": "Flip light schedule",
                "description": "Switch to 12/12.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Aggressive stretch management",
                "description": "Bend/tie all growth outward. Supercrop if necessary. Shading kills lower sites.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Transition nutrients",
                "description": "Begin bloom formula.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Add side lighting (optional)",
                "description": "LED strips on sides illuminate lower sites during stretch.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Stretch controlled?", "All sites still getting light?", "No shading issues?"],
        "common_problems": [
            {
                "issue": "Upper sites completely shading lower sites",
                "cause": "Stretch creates a canopy ceiling blocking light below",
                "solution": "Supercrop upper sites. Add vertical side lighting. Consider removing top sites.",
            },
        ],
        "transition_signals": ["Stretch slowing", "Pre-flowers visible", "All sites still productive"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Natural photoperiod. Sun angle helps vertical light distribution."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Supplement with side lighting."}, "extra_tasks": []},
        },
    },
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Bud sites forming at all tower levels. Full bloom nutrients. Tower advantage: 360° access for inspection. Challenge: even light distribution to all bud sites.",
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
            "notes": "Full bloom nutrients.",
        },
        "nutrients": {"strength_pct": 100, "approach": "Full bloom. High P-K."},
        "tasks": [
            {
                "name": "Full bloom nutrients",
                "description": "Switch completely to flower formula.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Defoliate for light penetration",
                "description": "Remove fan leaves blocking bud sites on inner canopy.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Maintain tower rotation",
                "description": "Rotate for even light. Or use multiple light sources.",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": ["Bud sites at all levels?", "Light reaching inner buds?", "Humidity controlled?"],
        "common_problems": [
            {
                "issue": "Lower buds significantly smaller",
                "cause": "Light not reaching lower tower sites",
                "solution": "Side lighting (LED strips). Aggressive defoliation of upper canopy. Supercrop upper branches to let light through.",
            },
        ],
        "transition_signals": ["Buds forming all sites", "Pistils abundant", "Stretch complete"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Sun angle changes help light distribution."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Good natural light from multiple angles."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "mid_flower",
        "name": "Mid Flower (Bulk Phase)",
        "order": 7,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Peak bud development across all tower levels. Maximum water/nutrient demand. Tower challenge: maintaining even bud development despite varying light exposure per level.",
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
            "notes": "Peak demand. Reservoir may need daily top-offs.",
        },
        "nutrients": {"strength_pct": 100, "approach": "Full bloom + PK booster."},
        "tasks": [
            {
                "name": "Monitor reservoir 2x daily",
                "description": "Peak consumption from multiple flowering plants. Depletes fast.",
                "interval_days": 1,
                "priority": "high",
            },
            {"name": "PK booster", "description": "Weeks 4-6 of flower.", "interval_days": None, "priority": "medium"},
            {
                "name": "Support buds",
                "description": "Net or ties to prevent buds from pulling plant out of tower site.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Monitor for bud rot",
                "description": "Dense buds + internal tower humidity = risk.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": ["Buds developing at all levels?", "Reservoir keeping up?", "No rot?", "Tower stable?"],
        "common_problems": [
            {
                "issue": "Buds pulling plants out of tower",
                "cause": "Heavy buds + gravity + small net pots",
                "solution": "Support nets. Trellis rings around tower. Yo-yo supports from ceiling.",
            },
            {
                "issue": "Internal humidity high (rot risk)",
                "cause": "Dense canopy trapping moisture inside tower structure",
                "solution": "Oscillating fan directed at tower. Defoliate aggressively. Space plants wider.",
            },
        ],
        "transition_signals": ["Buds dense", "Trichomes milky", "Pistils browning"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Rain cover essential. Wind support."}, "extra_tasks": []},
            "greenhouse": {
                "environment_overrides": {"notes": "Dehumidify. Good circulation around tower."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Final ripening. Reduce nutrients. Tower allows 360° trichome inspection — easy access to all bud sites for maturity assessment.",
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
            "notes": "Reducing strength.",
        },
        "nutrients": {"strength_pct": 75, "approach": "75% bloom. Stop PK booster."},
        "tasks": [
            {
                "name": "Check trichomes all levels",
                "description": "Tower advantage: easy 360° access. Check upper and lower sites.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Reduce nutrients",
                "description": "Drop EC. Preparing for flush.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Plan harvest order",
                "description": "Upper sites may ripen faster (more light). Plan staggered harvest.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["Trichomes maturing?", "No rot?", "Even ripening across levels?"],
        "common_problems": [
            {
                "issue": "Uneven ripening (upper done, lower not)",
                "cause": "Light differential between levels",
                "solution": "Staggered harvest — take upper sites first. Leave lower to finish.",
            },
        ],
        "transition_signals": ["Trichomes 70-80% milky", "Pistils mostly orange", "Calyxes swollen"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Fall temps help ripening."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Drop night temps."}, "extra_tasks": []},
        },
    },
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Switch to plain water. Tower systems flush fast — no media (or minimal media) means roots are directly exposed to solution. Clean flush in 5-7 days.",
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
            "notes": "Plain water. Clean reservoir.",
        },
        "nutrients": {"strength_pct": 0, "approach": "Plain pH'd water only."},
        "tasks": [
            {
                "name": "Switch to plain water",
                "description": "Drain nutrient reservoir. Refill clean.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Maintain pump cycles",
                "description": "Keep running to flush roots.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor fade",
                "description": "Yellowing fan leaves = good sign.",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": ["Plants fading?", "Buds still healthy?", "Flush complete?"],
        "common_problems": [
            {
                "issue": "Plants wilting during flush",
                "cause": "Sudden nutrient removal + continued high light",
                "solution": "Normal response. Reduce light intensity slightly. Maintain pump cycle.",
            },
        ],
        "transition_signals": ["Fan leaves yellowed", "7-10 days complete", "Trichomes at target"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Continue pump cycle with plain water."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Standard flush."}, "extra_tasks": []},
        },
    },
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Remove plants from tower sites. Can harvest level by level (upper first if they ripened earlier). Easy access from all sides — tower advantage for harvest.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
        },
        "reservoir": {"notes": "Turn off pump. Drain system."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Remove plants from tower",
                "description": "Pull from net pots. Start with upper sites.",
                "interval_days": None,
                "priority": "high",
            },
            {"name": "Trim", "description": "Wet or dry trim.", "interval_days": None, "priority": "high"},
            {
                "name": "Clean tower",
                "description": "Remove all root material. H2O2 flush through tower.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Inspect pump and lines",
                "description": "Clean for next cycle.",
                "interval_days": None,
                "priority": "low",
            },
        ],
        "health_checks": ["Trichomes at target?", "All sites harvested?"],
        "common_problems": [
            {
                "issue": "Roots stuck in tower column",
                "cause": "Root mass grew into and around internal structure",
                "solution": "Soak tower. Roots soften and pull out. Enzyme cleaner helps.",
            },
        ],
        "transition_signals": ["All plants removed", "Tower cleaned", "Branches hung"],
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
        "description": "Standard hang dry. 60°F, 60% RH, complete darkness.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "light_hours": 0,
        },
        "reservoir": {"notes": "Tower system cleaned and ready for next cycle."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Hang branches",
                "description": "Standard hang dry in controlled environment.",
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
                "description": "Small stems snap = ready.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": ["Conditions in range?", "No mold?", "Even drying?"],
        "common_problems": [
            {
                "issue": "Drying too fast",
                "cause": "Humidity too low or temp too high",
                "solution": "Lower temp, raise humidity, whole-plant hangs.",
            },
        ],
        "transition_signals": ["Stems snap", "Outside crispy, inside moist"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Dry indoors."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Dry in separate controlled space."}, "extra_tasks": []},
        },
    },
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Jar cure. Standard process. Tower-grown buds may be smaller but denser from aeroponic root exposure.",
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
        "health_checks": ["Humidity in range?", "No ammonia smell?", "No mold?"],
        "common_problems": [
            {"issue": "Ammonia smell", "cause": "Jarred too wet", "solution": "Remove, dry 12-24h more, re-jar."},
        ],
        "transition_signals": ["Smooth smoke", "Full terpene profile", "No hay smell"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT
# ─────────────────────────────────────────────────────────────────────────────

VERTICAL_TOWER_EQUIPMENT: list[dict] = [
    {
        "name": "Vertical tower structure",
        "category": "essential",
        "essential": True,
        "description": "Commercial tower garden or DIY PVC tower with stacked plant sites around central column.",
    },
    {
        "name": "Reservoir (20-50 gal)",
        "category": "essential",
        "essential": True,
        "description": "Base reservoir. Smaller than other hydro due to tower's compact footprint.",
    },
    {
        "name": "Submersible pump",
        "category": "essential",
        "essential": True,
        "description": "Pumps solution from reservoir to tower top. Gravity returns it down through sites.",
    },
    {
        "name": "Net pots (3-inch)",
        "category": "essential",
        "essential": True,
        "description": "Fit into tower sites. Hold plant + minimal media or clay pebbles.",
    },
    {
        "name": "Distribution cap/shower head",
        "category": "essential",
        "essential": True,
        "description": "Top of tower distributes solution evenly to all sides before gravity flow.",
    },
    {
        "name": "Timer",
        "category": "essential",
        "essential": True,
        "description": "Controls pump cycles. Critical for vertical flow management.",
    },
    {
        "name": "Growing media (clay pebbles)",
        "category": "essential",
        "essential": True,
        "description": "Minimal media in net pots for support. Hydroton/clay pebbles standard.",
    },
    {
        "name": "pH/EC meters",
        "category": "essential",
        "essential": True,
        "description": "Monitor solution. Small reservoirs change fast.",
    },
    {
        "name": "Side lighting (LED strips)",
        "category": "recommended",
        "essential": False,
        "description": "Vertical LED strips illuminate lower tower levels. Critical for even development.",
    },
    {
        "name": "Trellis rings",
        "category": "recommended",
        "essential": False,
        "description": "Circular trellis at each level supports outward-growing branches.",
    },
    {
        "name": "Rotation motor/base",
        "category": "optional",
        "essential": False,
        "description": "Slow rotation (1 RPM or less) ensures even light exposure.",
    },
    {
        "name": "Air pump + stone",
        "category": "recommended",
        "essential": False,
        "description": "Aerate reservoir for dissolved oxygen.",
    },
    {
        "name": "Ballast weight/base",
        "category": "recommended",
        "essential": False,
        "description": "Stabilizes tower. Prevents tipping from plant weight.",
    },
    {
        "name": "Float valve",
        "category": "optional",
        "essential": False,
        "description": "Auto-top-off for small reservoir.",
    },
    {
        "name": "Plant supports (yo-yos)",
        "category": "recommended",
        "essential": False,
        "description": "Support heavy buds from above. Prevent plants pulling from sites.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

VERTICAL_TOWER_QUICK_REFERENCE: dict = {
    "method_summary": "Plants grow from stacked sites around a vertical column. Solution pumped to top, flows down via gravity past all root zones. Maximizes plants per square foot.",
    "difficulty": "advanced",
    "maintenance_level": "Medium-high — light management is ongoing challenge. Small reservoirs need frequent attention.",
    "key_advantages": [
        "Maximum plants per square foot",
        "Space efficient (vertical footprint)",
        "360° access for maintenance",
        "Dramatic visual appeal",
        "Fast growth (aeroponic root exposure)",
    ],
    "key_challenges": [
        "Uneven light distribution (top vs bottom)",
        "Small reservoir depletes fast",
        "Canopy management complex",
        "Tower stability with heavy plants",
        "Lower sites often underperform",
    ],
    "feed_schedule": {
        "seedling": "15 min on / 60 min off",
        "veg": "15 min on / 30 min off",
        "flower": "15 min on / 15 min off or continuous",
    },
    "critical_rules": [
        "Side lighting is almost mandatory for even bud development",
        "Rotate tower (or use multiple light angles) for even exposure",
        "Train plants OUTWARD — never let them grow straight up (shading)",
        "Small reservoir = check twice daily in flower",
        "Fewer plants with better light > more plants starving for light",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING
# ─────────────────────────────────────────────────────────────────────────────

VERTICAL_TOWER_TROUBLESHOOTING: list[dict] = [
    {
        "category": "flow_system",
        "issues": [
            {
                "symptom": "Upper sites getting all the water, lower sites dry",
                "cause": "Distribution cap clogged or uneven",
                "solution": "Clean distribution cap. Ensure even flow to all sides. Check for root blockages.",
            },
            {
                "symptom": "No flow from top",
                "cause": "Pump clogged or line kinked",
                "solution": "Clean pump intake filter. Check for kinks in delivery line. Verify pump is submerged.",
            },
            {
                "symptom": "Solution leaking from tower joints",
                "cause": "Seals degraded or tower shifted",
                "solution": "Re-seat sections. Apply food-grade silicone sealant. Check O-rings.",
            },
        ],
    },
    {
        "category": "light_distribution",
        "issues": [
            {
                "symptom": "Lower sites producing tiny buds",
                "cause": "Insufficient light reaching lower levels",
                "solution": "Add side LED lighting. Aggressive upper defoliation. Consider using fewer levels.",
            },
            {
                "symptom": "Stretchy/etiolated growth on one side",
                "cause": "Uneven light — tower not being rotated",
                "solution": "Rotate tower 90° every 2-3 days. Or add light from multiple angles.",
            },
            {
                "symptom": "Plants growing toward light (phototropism) pulling from pots",
                "cause": "Strong directional light source",
                "solution": "More frequent rotation. Support plants with trellis rings. Multi-directional lighting.",
            },
        ],
    },
    {
        "category": "structural",
        "issues": [
            {
                "symptom": "Tower tipping/unstable",
                "cause": "Top-heavy from plant growth or wind",
                "solution": "Ballast base with water/sand. Tether to wall or ceiling. Prune to balance weight.",
            },
            {
                "symptom": "Plants falling out of sites",
                "cause": "Net pots too small or roots not established",
                "solution": "Pack with clay pebbles. Use larger net pots. Support with plant ties.",
            },
            {
                "symptom": "Roots completely blocking central column",
                "cause": "Aggressive root growth filling interior space",
                "solution": "Root trim through sites. Consider fewer plants for root space. More frequent pump cycles to prevent root desiccation.",
            },
        ],
    },
    {
        "category": "nutrient_issues",
        "issues": [
            {
                "symptom": "Rapid pH/EC swings",
                "cause": "Small reservoir with many plants = fast changes",
                "solution": "Larger external reservoir. More frequent monitoring. Auto-dosing system.",
            },
            {
                "symptom": "Lower sites showing deficiency, upper fine",
                "cause": "Nutrients absorbed by upper roots first, depleted by lower",
                "solution": "Increase nutrient strength. More pump cycles. Consider bottom-up feed supplement.",
            },
            {
                "symptom": "Algae growth on tower exterior",
                "cause": "Light hitting wet surfaces",
                "solution": "Block light from tower surface. Use opaque tower material. Wrap with reflective material.",
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# VERTICAL TOWER SYSTEM — Core differentiator
# ─────────────────────────────────────────────────────────────────────────────

VERTICAL_TOWER_SYSTEM: dict = {
    "tower_construction": {
        "commercial_options": [
            {
                "name": "Tower Garden (Juice Plus)",
                "sites": 20,
                "height_ft": 5,
                "notes": "Proven design. Expensive. Good support community.",
            },
            {
                "name": "Mr. Stacky / GreenStalk",
                "sites": 30,
                "height_ft": 4,
                "notes": "Affordable. Soil-based (not true aero). Multiple tiers.",
            },
            {
                "name": "Lettuce Grow Farmstand",
                "sites": 36,
                "height_ft": 5,
                "notes": "Modern design. Modular. Subscription model.",
            },
        ],
        "diy_options": {
            "pvc_tower": {
                "materials": [
                    "4-6 inch PVC pipe (outer)",
                    "2-3 inch PVC pipe (inner delivery)",
                    "3-inch net pot cups",
                    "Hole saw (3-inch)",
                    "End caps and fittings",
                ],
                "sites_per_foot": 3,
                "max_recommended_height_ft": 6,
                "notes": "Most common DIY approach. Cut holes at 120° rotation per level for optimal spacing.",
            },
            "bucket_stack": {
                "materials": ["5-gallon buckets (stacked)", "Net pots in bucket sides", "Central pipe for delivery"],
                "sites_per_bucket": 4,
                "notes": "Easier to build. Modular. Can add/remove sections.",
            },
        },
    },
    "flow_dynamics": {
        "pump_to_top": {
            "delivery": "Pump pushes solution from base reservoir up through central pipe to distribution cap at top.",
            "distribution_cap": "Spreads solution evenly to all sides of tower. Critical for uniform coverage.",
            "gravity_return": "Solution cascades down through tower interior, passing over roots at each level, and returns to reservoir at base.",
        },
        "flow_rate_gph": {"min": 100, "max": 400, "recommended": 200},
        "cycle_timing": {
            "seedling": {"on_min": 15, "off_min": 60},
            "veg": {"on_min": 15, "off_min": 30},
            "flower": {"on_min": 15, "off_min": 15},
            "notes": "Roots in tower have minimal media — need frequent moisture. Can go continuous in flower.",
        },
        "gravity_distribution_challenge": {
            "issue": "Lower sites receive more solution (gravity accumulation). Upper sites can dry faster.",
            "solutions": [
                "More frequent pump cycles",
                "Larger distribution cap for upper coverage",
                "Absorbent collar inserts at each level",
                "Mist rather than drip at top",
            ],
        },
    },
    "lighting_strategy": {
        "primary_overhead": {
            "coverage": "Mainly hits top 1-2 levels. Diminishes rapidly below.",
            "ppfd_at_levels": {"top": "100%", "middle": "40-60%", "bottom": "20-30%"},
        },
        "side_lighting": {
            "importance": "Critical for even development. Without it, lower 50% of tower underperforms.",
            "options": [
                "LED strip lights running vertically",
                "Multiple small panels at each level",
                "Ring lights at each tier",
            ],
            "placement": "One vertical strip every 90° around tower (4 strips total) is ideal.",
        },
        "rotation": {
            "method": "Manual 90° turn every 2-3 days, or motorized slow rotation (< 1 RPM)",
            "benefit": "Ensures all plant faces receive equal light over time.",
        },
        "optimal_setup": "Overhead HPS/LED for intensity + 4 vertical LED strips for side coverage + rotation",
    },
    "space_efficiency": {
        "footprint_sqft": {"tower_garden": 4, "diy_pvc_6inch": 2, "notes": "Tiny footprint for 20-30+ plant sites."},
        "plants_per_sqft": {
            "traditional_flat": "1-4",
            "vertical_tower": "8-15",
            "notes": "3-4x density per square foot.",
        },
        "yield_reality": "Per-plant yield is lower (less light per site), but yield per square foot can be higher with proper lighting.",
        "best_use_cases": [
            "Small spaces (closets, balconies)",
            "High-plant-count legal limits (more plants = more advantage)",
            "Ornamental/display growing",
            "Leafy greens (lettuce, herbs — ideal for towers)",
        ],
        "cannabis_specific_challenges": [
            "Cannabis gets too large for typical tower sites",
            "Light intensity requirements exceed what side-lighting can provide",
            "Better for SOG (Sea of Green) with many small plants than few large plants",
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLED CONFIG EXPORT
# ─────────────────────────────────────────────────────────────────────────────

VERTICAL_TOWER_CONFIG: dict = {
    "grow_type_id": "vertical_tower",
    "version": "1.0.0",
    "stages": VERTICAL_TOWER_STAGES,
    "equipment": VERTICAL_TOWER_EQUIPMENT,
    "quick_reference": VERTICAL_TOWER_QUICK_REFERENCE,
    "troubleshooting": VERTICAL_TOWER_TROUBLESHOOTING,
    "vertical_tower_system": VERTICAL_TOWER_SYSTEM,
    "total_grow_days": {"min": 105, "max": 210, "typical": 150},
}
