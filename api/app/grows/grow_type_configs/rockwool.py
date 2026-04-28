"""Rockwool — Complete grow type configuration.

Enterprise-grade configuration for rockwool growing — the commercial cannabis
industry standard.  Rockwool is the most data-driven, precision-oriented
growing method, used by the majority of large-scale operations.

The defining features are **crop steering** (the most advanced technique —
controlling vegetative vs generative growth through dryback, EC, and irrigation
timing), **shot-based irrigation** (discrete, timed doses rather than continuous
watering), **slab weight tracking** (weight = water content = the #1 metric),
**pH conditioning** (new rockwool is pH 7-8, MUST be pre-soaked to 5.5), and
**cube-to-slab propagation** (seedlings in cubes → transplant to slabs).

Key Rockwool differences from other methods:
  - Irrigation is in discrete "shots" — volume and timing are precisely controlled
  - Slab weight is the primary metric (like weighing coco pots, but more precise)
  - Crop steering is THE technique — dryback controls veg vs generative growth
  - New rockwool pH is 7-8 (too high) — must condition before use
  - Not reusable (unlike coco) — one grow per slab, then dispose
  - P1/P2/P3 shot phases define the daily irrigation curve
  - Commercial operations use substrate sensors (Aroya, Grodan GroSens)
  - Cube-to-slab propagation pathway (unique to rockwool)
  - Rockwool fibers irritate skin/lungs — wear gloves/mask when dry
  - Not compostable — landfill or specialized recycling

Supports three environment types (matching Tent.environment_type):
  - indoor  (default — full environmental control, artificial light)
  - outdoor (not common — rockwool is an indoor/greenhouse method)
  - greenhouse (excellent — commercial standard for greenhouse cannabis)

Data sources:
- Grodan precision growing guides
- Aroya crop steering methodology
- Commercial rockwool SOPs
- Hugo/Expert slab specifications
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in a Rockwool grow
# ─────────────────────────────────────────────────────────────────────────────

ROCKWOOL_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Seed cracks open and taproot emerges. Start seeds in pre-soaked 1-inch rockwool starter cubes (pH conditioned to 5.5). Humidity dome. Darkness until sprout emerges.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Seeds in darkness. Heat mat at 78°F. Humidity dome over starter cubes.",
        },
        "medium": {
            "shot_volume_ml": 0,
            "shots_per_day": 0,
            "dryback_pct": 0,
            "slab_weight_pct": None,
            "steering_mode": None,
            "notes": "Seeds are in 1-inch starter cubes, not on slabs yet. Pre-soak cubes in pH 5.5 nutrient solution (EC 0.4) before inserting seeds. Squeeze out excess — cubes should be moist, not dripping.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Seeds contain all energy. Pre-soak cubes with very light nutrient solution (EC 0.4, pH 5.5) before inserting seeds.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Condition starter cubes",
                "description": "Soak 1-inch rockwool cubes in pH 5.5 nutrient solution (EC 0.4) for 30-60 minutes. Gently squeeze out excess. Should be evenly moist. New rockwool is pH 7-8 — conditioning is NON-NEGOTIABLE.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Insert seeds",
                "description": "Place seed in cube hole, pointed end down. Cover lightly with a torn piece of rockwool. Do NOT push seed deep.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Humidity dome",
                "description": "Place cubes in tray under humidity dome. Heat mat at 78°F.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for taproot",
                "description": "After 24-72 hours, look for white taproot emerging from cube bottom.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Cubes properly pH conditioned (test runoff pH < 6.0)?",
            "Seeds cracking?",
            "Temperature at 75-80°F?",
            "Cubes moist but not saturated?",
        ],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Cube too wet (saturated), too cold, or bad seed",
                "solution": "Squeeze out excess water. Cubes should be moist, not dripping. Ensure heat mat at 78°F. Try new seed after 7 days.",
            },
            {
                "issue": "Cube pH too high",
                "cause": "Insufficient conditioning — new rockwool pH is 7-8",
                "solution": "Re-soak cubes in pH 5.0 solution for 1 hour. Test runoff. Repeat until below 6.0. This is the #1 rockwool mistake.",
            },
        ],
        "training": [],
        "transition_signals": ["Taproot visible", "Sprout emerging from cube", "Cotyledon leaves opening"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Not recommended. Rockwool is an indoor/greenhouse method."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Start indoors always.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse germination: heat mat + dome. Temperature swings may slow germination."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Heat mat essential in greenhouse.",
            },
        },
    },
    # ── 2. SEEDLING ──────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "First true leaves develop. Seedling in 1-inch cube, transplant to 4-inch cube when roots emerge from starter cube. Begin light hand-watering of the 4-inch cube. No slabs yet.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 65, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 250, "target": 200},
            "light_dli": {"min": 6, "max": 16, "target": 13},
            "notes": "Gentle light. Gradually remove humidity dome over 3-5 days.",
        },
        "medium": {
            "shot_volume_ml": {
                "min": 20,
                "max": 50,
                "target": 30,
                "notes": "Hand-water 4-inch cube. Small volume — just enough to moisten.",
            },
            "shots_per_day": 1,
            "dryback_pct": {"min": 5, "max": 15, "target": 10},
            "slab_weight_pct": None,
            "steering_mode": "none",
            "notes": "Seedling in 4-inch cube. Hand-water when cube feels light. 1x/day is usually enough. DO NOT overwater cubes — seedling roots need oxygen. The 4-inch cube should feel damp but not saturated. Lift to check weight.",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "Quarter strength. pH 5.5-5.8. Low EC for tender seedlings.",
            "flora_micro_ml_per_gal": 0.625,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 0.3125,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection in moist rockwool."},
            ],
        },
        "tasks": [
            {
                "name": "Transplant to 4-inch cube",
                "description": "When roots emerge from 1-inch cube, place it on top of a pre-conditioned 4-inch cube. The 1-inch cube sits in the hole of the 4-inch cube. Roots grow down into the larger cube.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Condition 4-inch cubes",
                "description": "Soak in pH 5.5, EC 0.6 solution for 1 hour. Drain but don't squeeze. Should be evenly moist.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Daily weight check",
                "description": "Lift 4-inch cube. Heavy = still wet. Light = time to water. The rockwool skill starts here.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Remove humidity dome gradually",
                "description": "Crack day 1, remove for hours day 2, fully remove by day 3-5.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "First true leaves appearing?",
            "Roots growing into 4-inch cube?",
            "Cube not oversaturated?",
            "pH of runoff below 6.0?",
        ],
        "common_problems": [
            {
                "issue": "Damping off (stem rots at cube surface)",
                "cause": "Cube too wet, poor airflow",
                "solution": "Reduce watering. Improve airflow. Cube should dry slightly between waterings. Treat with Hydroguard.",
            },
            {
                "issue": "Slow root growth into 4-inch cube",
                "cause": "4-inch cube too dry or poor contact with starter cube",
                "solution": "Ensure starter cube sits flush in the 4-inch cube hole. Moisten the contact area.",
            },
        ],
        "training": [],
        "transition_signals": [
            "2-3 sets of true leaves",
            "Roots emerging from 4-inch cube sides/bottom",
            "Seedling 3-4 inches tall",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Keep seedlings indoors or in greenhouse."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Rockwool seedlings: indoor only.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse seedlings: watch temperature swings."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: heat mat recommended.",
            },
        },
    },
    # ── 3. EARLY VEGETATIVE ──────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Transplant 4-inch cube to slab. This is where rockwool's precision irrigation begins. Condition slabs, cut drainage slits, place cubes, install drip stakes. Begin shot-based irrigation on the slab. Vegetative steering: low dryback, frequent shots.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 60, "max": 75, "target": 65},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 300, "max": 500, "target": 400},
            "light_dli": {"min": 19, "max": 32, "target": 26},
            "notes": "Ramp light. Humidity moderate. Plant growing rapidly on slab.",
        },
        "medium": {
            "shot_volume_ml": {
                "min": 50,
                "max": 100,
                "target": 75,
                "notes": "Per drip stake per shot. Volume depends on slab size and plant count per slab.",
            },
            "shots_per_day": {"min": 2, "max": 4, "target": 3},
            "dryback_pct": {"min": 5, "max": 10, "target": 8},
            "slab_weight_pct": {
                "target": 70,
                "range": "65-80",
                "notes": "Vegetative: keep slab wet. 70% field capacity. Weight is the metric.",
            },
            "steering_mode": "vegetative",
            "notes": "VEGETATIVE STEERING on slab. Low dryback (5-10%), frequent shots, lower EC. This pushes vegetative growth. First shot 30 min after lights on (early — don't let morning dryback go too far). Last shot 2-3 hours before lights off. P1 phase (morning ramp-up): restore slab to field capacity. P2 (midday): maintenance shots. P3 (afternoon): allow dryback before dark.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half strength. Veg ratio (more nitrogen). EC 0.8-1.2.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection in warm rockwool."},
                {"name": "Silica (Armor Si)", "dose_ml_per_gal": 0.5, "purpose": "Stem strength. Add FIRST."},
            ],
        },
        "tasks": [
            {
                "name": "Condition slabs",
                "description": "Soak new slabs in pH 5.0-5.5 nutrient solution (EC 1.0) for 24 hours. Drain. Re-soak 8 hours. Test runoff pH — must be below 6.0. This is NON-NEGOTIABLE. New rockwool pH is 7-8.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Cut drainage slits",
                "description": "Cut 2-3 slits in the bottom of the slab wrap, off-center (not directly below cubes). Slits allow drainage but not too fast.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Place cubes on slab",
                "description": "Place 4-inch cubes on slab surface. 1-2 plants per standard slab. Cube bottom in full contact with slab top.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Install drip stakes",
                "description": "One drip stake per cube, inserted into the cube top. Connected to pump/timer system.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Begin shot-based irrigation",
                "description": "Program timer: 3 shots/day. First shot 30 min after lights on, last shot 2-3 hours before lights off, middle shot(s) evenly spaced.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Weigh slabs daily",
                "description": "Weigh slab at saturation (= 100% field capacity). Track daily weight to calculate dryback. Commercial: use substrate sensors (Aroya, GroSens). Home: kitchen scale under slab.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Begin training",
                "description": "Start LST, topping at 4-5 nodes. Rockwool plants grow fast with precision irrigation.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Slab pH below 6.0?",
            "Roots growing from cube into slab?",
            "Slab weight at 65-80% field capacity?",
            "Dryback within vegetative target (5-10%)?",
            "Drainage slits draining properly?",
        ],
        "common_problems": [
            {
                "issue": "Slab pH too high (>6.5)",
                "cause": "Insufficient conditioning",
                "solution": "Re-condition: run pH 5.0 solution through slab at 3x volume. Let sit 8 hours. Test runoff. Repeat.",
            },
            {
                "issue": "Roots not growing into slab",
                "cause": "Cube-slab contact poor, or slab too dry/wet",
                "solution": "Ensure cube bottom is flat against slab. Moisten contact zone. Don't oversaturate slab — roots grow toward moisture gradient.",
            },
            {
                "issue": "Algae on slab surface",
                "cause": "Light reaching wet rockwool surface",
                "solution": "Cover slab with opaque wrap. No light on rockwool. Algae competes for nutrients and hosts fungus gnats.",
            },
        ],
        "training": [
            {
                "technique": "LST",
                "description": "Bend and tie branches. Start at 4-5 nodes.",
                "timing": "After 4-5 nodes",
            },
            {"technique": "Topping", "description": "Cut above 4th or 5th node.", "timing": "At 5-6 nodes"},
        ],
        "transition_signals": [
            "5-6 nodes",
            "Roots visible in slab (check by lifting cube)",
            "Rapid daily growth",
            "Slab drying faster each day",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor rockwool not recommended. Rain destroys irrigation precision."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Keep rockwool indoors or in greenhouse.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse rockwool is the commercial standard. Excellent."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: ideal for rockwool.",
            },
        },
    },
    # ── 4. LATE VEGETATIVE ───────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 7, "max": 21, "typical": 14},
        "description": "Plant reaches target size on slab. Ramp shot count. Continue vegetative steering. Root system now established throughout slab. Pre-flip: saturate slab (reset to field capacity) and flush salts.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 55, "max": 70, "target": 60},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 600, "target": 500},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Full veg intensity. Heavy transpiration.",
        },
        "medium": {
            "shot_volume_ml": {"min": 75, "max": 150, "target": 100, "notes": "Larger shots as plant drinks more."},
            "shots_per_day": {"min": 4, "max": 6, "target": 5},
            "dryback_pct": {"min": 5, "max": 10, "target": 7},
            "slab_weight_pct": {"target": 75, "range": "70-85", "notes": "Keep slab wet for veg push."},
            "steering_mode": "vegetative",
            "notes": "Continue vegetative steering. 5 shots/day, low dryback. P1 (morning): 2-3 shots to restore field capacity quickly. P2 (midday): 1-2 maintenance shots. P3 (afternoon): 1 shot, then allow overnight dryback. Pre-flip: run a saturation event — flood slab to field capacity, flush with low-EC solution to reset salts.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Three-quarter strength. Veg ratio. EC 1.2-1.6.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 1.875,
            "flora_bloom_ml_per_gal": 0.9375,
            "calmag_ml_per_gal": 2.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection."},
                {"name": "Silica (Armor Si)", "dose_ml_per_gal": 1.0, "purpose": "Stem strength."},
            ],
        },
        "tasks": [
            {
                "name": "Ramp shot count to 5/day",
                "description": "P1: 2-3 morning shots. P2: 1-2 midday. P3: 1 afternoon. First shot 30 min after lights on.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Daily slab weight tracking",
                "description": "Track dryback overnight. Should be 5-10% for veg steering. Commercial: substrate sensor graphs.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check slab runoff EC/pH",
                "description": "Collect from drainage slits. EC delta <0.3, pH 5.5-6.0.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Pre-flip saturation flush",
                "description": "2-3 days before flip: run low-EC solution (EC 0.4) through slabs until runoff EC matches input. Then saturate to field capacity.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Final training",
                "description": "Complete topping, LST, SCROG filling.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Canopy management",
                "description": "Defoliate lower growth. Lollipop lower 1/3.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Slab weight within veg targets?",
            "Runoff EC delta <0.3?",
            "Canopy filled and even?",
            "Roots throughout slab?",
        ],
        "common_problems": [
            {
                "issue": "Runoff EC climbing",
                "cause": "Salt accumulation in slab",
                "solution": "Increase shot volume for more runoff. Or flush with low-EC solution.",
            },
            {
                "issue": "Uneven slab moisture",
                "cause": "Drip stake not centered, or slab tilted wrong",
                "solution": "Check stake position. Level slab with slight tilt toward drainage slits.",
            },
        ],
        "training": [
            {
                "technique": "SCROG net",
                "description": "Install and fill 70-80% before flip.",
                "timing": "1-2 weeks before flip",
            },
            {"technique": "Lollipop", "description": "Remove lower 1/3.", "timing": "3-5 days before flip"},
        ],
        "transition_signals": [
            "Plant at 50-66% target height",
            "Canopy filled",
            "Pre-flip flush complete",
            "Heavy daily water uptake",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Not recommended outdoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Keep indoor/greenhouse.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: excellent for late veg rockwool."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Commercial standard.",
            },
        },
    },
    # ── 5. TRANSITION ────────────────────────────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Flipped to 12/12. Explosive stretch. BEGIN transitioning from vegetative to generative steering. Gradually increase dryback, increase EC, reduce shot frequency slightly while maintaining slab at adequate moisture. This transition is THE art of rockwool growing.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 65, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 700, "target": 600},
            "light_dli": {"min": 22, "max": 30, "target": 26},
            "notes": "Flip to 12/12. DIF of 10°F helps control stretch.",
        },
        "medium": {
            "shot_volume_ml": {"min": 75, "max": 150, "target": 100},
            "shots_per_day": {"min": 4, "max": 8, "target": 6},
            "dryback_pct": {"min": 8, "max": 15, "target": 12},
            "slab_weight_pct": {
                "target": 65,
                "range": "55-75",
                "notes": "Transitioning: slab running slightly drier than veg.",
            },
            "steering_mode": "transition",
            "notes": "TRANSITION from veg to generative. Over 7-14 days: increase overnight dryback from 8% to 15%. Delay first shot from 30 min to 1 hour after lights on. Slightly increase EC. P1: delayed start, restore to 65% (not full field capacity). P2: maintenance. P3: allow deeper dryback. The goal: signal the plant to shift energy from vegetative growth to flower production.",
        },
        "nutrients": {
            "strength_pct": 85,
            "approach": "Transition ratio. Reduce Gro, increase Bloom. EC 1.6-2.0.",
            "flora_micro_ml_per_gal": 2.125,
            "flora_gro_ml_per_gal": 1.5,
            "flora_bloom_ml_per_gal": 1.5,
            "calmag_ml_per_gal": 2.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection."},
                {"name": "Silica (Armor Si)", "dose_ml_per_gal": 1.0, "purpose": "Support stretching stems."},
            ],
        },
        "tasks": [
            {
                "name": "Flip to 12/12",
                "description": "Zero light leaks. Rockwool operations don't change — just the photoperiod.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Begin steering transition",
                "description": "Gradually increase overnight dryback: day 1-3 = 8-10%, day 4-7 = 10-12%, day 8-14 = 12-15%. Delay first shot timing by 10 min every 2-3 days.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Transition nutrient ratio",
                "description": "Shift from veg to bloom ratio over 5-7 days. Increase EC by 0.1 every 2-3 days.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Track slab weight daily",
                "description": "Morning pre-first-shot weight = overnight dryback. This number drives your steering decisions.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Manage stretch",
                "description": "Supercrop, SCROG tuck daily.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Dryback increasing on schedule?",
            "First shot timing delaying on schedule?",
            "Stretch manageable?",
            "No hermaphrodite signs?",
        ],
        "common_problems": [
            {
                "issue": "Wilting from too-aggressive dryback transition",
                "cause": "Increased dryback too fast",
                "solution": "Ease back. Increase dryback by 1-2% every 2-3 days, not all at once. The plant needs to adapt.",
            },
            {
                "issue": "Excessive stretch despite steering",
                "cause": "Genetics, or transition too slow",
                "solution": "Accelerate generative steering (increase dryback faster). Supercrop. Some cultivars stretch regardless.",
            },
        ],
        "training": [
            {
                "technique": "Supercropping",
                "description": "Bend tall stems. Recovery 2-3 days.",
                "timing": "First 2 weeks of stretch",
            },
            {"technique": "SCROG tucking", "description": "Daily tucking under net.", "timing": "Throughout stretch"},
        ],
        "transition_signals": [
            "Stretch slowing",
            "Pistils at bud sites",
            "Overnight dryback at 12-15%",
            "Flower sites forming",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Not recommended."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor/greenhouse only.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: light dep triggers flip."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Light dep recommended.",
            },
        },
    },
    # ── 6. EARLY FLOWER ──────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Stretch ended. Buds forming. Full generative steering now: maximum dryback, highest EC, delayed first shot, lower slab weight targets. This is where rockwool's precision pays off — every parameter is optimized for flower production.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 62, "max": 70, "target": 66},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Peak light. Low humidity. CO2 to 1000-1200 ppm if available.",
        },
        "medium": {
            "shot_volume_ml": {"min": 75, "max": 150, "target": 100},
            "shots_per_day": {"min": 6, "max": 10, "target": 8},
            "dryback_pct": {"min": 15, "max": 25, "target": 20},
            "slab_weight_pct": {
                "target": 55,
                "range": "45-65",
                "notes": "Generative: slab running drier. But never let it go below 40% — roots die.",
            },
            "steering_mode": "generative",
            "notes": "FULL GENERATIVE STEERING. Dryback 15-25%. First shot delayed 1-2 hours after lights on (morning dryback is the strongest generative signal). EC 2.2-2.6. Slab weight 45-65%. P1: delayed start, restore to 55-65% (NOT full field capacity). P2: frequent small maintenance shots. P3: stop shots 3 hours before lights off, allow deep overnight dryback. The slab is your precision tool — every % of dryback drives generative response.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom. Heavy PK. EC 2.2-2.6.",
            "flora_micro_ml_per_gal": 2.5,
            "flora_gro_ml_per_gal": 1.0,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 2.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection."},
                {"name": "Liquid Kool Bloom", "dose_ml_per_gal": 1.25, "purpose": "PK booster for bud formation."},
            ],
        },
        "tasks": [
            {
                "name": "Full generative steering",
                "description": "Dryback 15-25%. First shot 1-2 hours after lights on. EC 2.2-2.6. Slab weight target 55%.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Track morning dryback precisely",
                "description": "Weigh slab at lights-on, before first shot. This is your generative signal. Target: 15-25% dryback from yesterday's final weight.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor runoff EC/pH",
                "description": "High EC + generative stress = fast salt accumulation. Check every 2 days. Flush if delta >0.5.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Remove fan leaves blocking bud sites. Open canopy interior.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for bud rot / PM",
                "description": "Dense buds in humid environments = risk.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Morning dryback hitting 15-25% target?",
            "Slab weight 45-65%?",
            "Runoff EC delta <0.5?",
            "Buds forming at all sites?",
            "No bud rot or PM?",
        ],
        "common_problems": [
            {
                "issue": "Wilt from over-aggressive dryback",
                "cause": "Slab weight dropped below 40% — root damage",
                "solution": "EMERGENCY: run a saturation event. Slab to field capacity. Resume at 50-55% weight target. Roots in dry rockwool die fast.",
            },
            {
                "issue": "Nutrient burn",
                "cause": "EC too high for cultivar",
                "solution": "Reduce EC by 0.2-0.3. Some cultivars can't handle 2.6.",
            },
            {
                "issue": "Uneven bud development",
                "cause": "Uneven irrigation — some roots getting more than others",
                "solution": "Check drip stakes. Ensure even flow. May need slab leveling.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation",
                "description": "Remove blocking fan leaves. Max 20% at once.",
                "timing": "Day 1-3 of early flower",
            },
            {
                "technique": "Lollipopping",
                "description": "Remove growth below net/lower 1/3.",
                "timing": "First week of early flower",
            },
        ],
        "transition_signals": ["Buds fattening", "Trichomes appearing", "Strong flower aroma", "Stretch fully stopped"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Not recommended."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor/greenhouse.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: excellent for rockwool flower with climate control."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Ideal environment.",
            },
        },
    },
    # ── 7. MID FLOWER ────────────────────────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Peak Bloom)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Peak bud development. Maximum generative steering: deepest dryback, highest EC, most aggressive morning delay. Every parameter optimized for bud density and weight. This is where rockwool's precision separates it from every other method.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 78, "target": 76},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 40, "max": 50, "target": 45},
            "vpd_kpa": {"min": 1.4, "max": 1.6, "target": 1.5},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
            "notes": "Peak light. Low humidity. CO2 at 1200-1500 ppm if available.",
        },
        "medium": {
            "shot_volume_ml": {"min": 75, "max": 150, "target": 100},
            "shots_per_day": {"min": 8, "max": 12, "target": 10},
            "dryback_pct": {"min": 20, "max": 30, "target": 25},
            "slab_weight_pct": {
                "target": 50,
                "range": "40-60",
                "notes": "Peak generative. Slab at lowest safe moisture. NEVER below 35%.",
            },
            "steering_mode": "generative",
            "notes": "PEAK GENERATIVE. Deepest dryback (20-30%). Longest morning delay (1.5-2 hours after lights on). Highest EC (2.4-2.8). Many small shots to maintain the 40-60% slab weight without ever saturating. P1: delayed start, small shots to restore to 50-55%. P2: frequent tiny maintenance shots. P3: stop 3-4 hours before lights off for deep overnight dryback. The morning pre-first-shot weight is your #1 daily metric.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom. Peak PK. EC 2.4-2.8.",
            "flora_micro_ml_per_gal": 2.5,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 2.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection."},
                {"name": "Liquid Kool Bloom", "dose_ml_per_gal": 2.5, "purpose": "PK booster at peak."},
            ],
        },
        "tasks": [
            {
                "name": "Peak generative steering",
                "description": "Dryback 20-30%, delay first shot 1.5-2 hours, EC 2.4-2.8. Monitor plant response daily — wilting means back off.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Morning weight check",
                "description": "Weigh slab at lights-on before first shot. This number drives all decisions.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Runoff EC/pH every 2 days",
                "description": "High EC + deep dryback = rapid salt concentration. Flush if delta >0.5.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Daily bud rot inspection",
                "description": "Dense buds. High risk.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Support heavy branches",
                "description": "Trellis, yo-yos, stakes.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Morning dryback 20-30%?",
            "Slab weight 40-60%?",
            "Runoff EC delta <0.5?",
            "No bud rot?",
            "Trichomes developing?",
        ],
        "common_problems": [
            {
                "issue": "Root death from over-dry slab",
                "cause": "Slab weight dropped below 35% — rockwool below 35% kills roots",
                "solution": "EMERGENCY saturation event. This is the rockwool danger zone. Roots in dry rockwool die faster than in any other medium.",
            },
            {
                "issue": "Salt lockout (multiple deficiencies)",
                "cause": "EC concentrated in dry slab",
                "solution": "Flush with low-EC solution. Resume at 80% previous EC.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Buds dense and firm",
            "Trichomes mostly milky",
            "Pistils turning orange",
            "Fan leaves yellowing naturally",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Not recommended."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor/greenhouse.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: peak production."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Ideal.",
            },
        },
    },
    # ── 8. LATE FLOWER ───────────────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Buds ripening. Reduce EC and ease back on generative steering slightly. Fan leaf yellowing is natural. Taper toward flush.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 78, "target": 75},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.4, "max": 1.8, "target": 1.6},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Slightly reduced light. Cooler nights. Low humidity.",
        },
        "medium": {
            "shot_volume_ml": {"min": 75, "max": 125, "target": 100},
            "shots_per_day": {"min": 6, "max": 8, "target": 7},
            "dryback_pct": {"min": 15, "max": 22, "target": 18},
            "slab_weight_pct": {"target": 55, "range": "45-65", "notes": "Easing back slightly from peak."},
            "steering_mode": "generative",
            "notes": "Still generative but tapering. Reduce EC. Fewer shots. Plant is finishing — it needs less. Natural leaf yellowing = plant consuming stored nutrients.",
        },
        "nutrients": {
            "strength_pct": 80,
            "approach": "Reducing. EC 2.0-2.4. Lower nitrogen. Maintain PK.",
            "flora_micro_ml_per_gal": 2.0,
            "flora_gro_ml_per_gal": 0.5,
            "flora_bloom_ml_per_gal": 2.0,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection."},
                {"name": "Liquid Kool Bloom", "dose_ml_per_gal": 1.25, "purpose": "Reduced PK."},
            ],
        },
        "tasks": [
            {
                "name": "Reduce EC and shot count",
                "description": "EC 2.0-2.4. 7 shots/day. Plant drinking less.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Trichome checks",
                "description": "60-100x loupe. Track clear → milky → amber.",
                "interval_days": 2,
                "priority": "high",
            },
            {"name": "Continue bud rot inspection", "description": "Daily.", "interval_days": 1, "priority": "high"},
            {
                "name": "Plan flush timing",
                "description": "Start flush 7-14 days before target harvest.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Trichomes progressing?",
            "Fan leaves yellowing naturally?",
            "No bud rot?",
            "Plant drinking less?",
        ],
        "common_problems": [
            {
                "issue": "Sudden leaf death",
                "cause": "pH lockout or root issues, not natural fade",
                "solution": "Check runoff pH. Gradual yellowing = good. Sudden browning = problem.",
            },
            {"issue": "Foxtailing", "cause": "Light stress", "solution": "Raise/dim lights."},
        ],
        "training": [],
        "transition_signals": [
            "30-50% pistils brown",
            "Trichomes mostly milky with 5-15% amber",
            "Fan leaves dropping",
            "Lower water uptake",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Not recommended."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor/greenhouse.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: maintain environment control."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Continue precision.",
            },
        },
    },
    # ── 9. FLUSH ─────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush (Pre-Harvest)",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Pre-harvest flush. Run low-EC solution (pH 5.8, EC 0.0-0.2) through slabs to leach salts. Rockwool flushes efficiently — salts leach readily with high-volume shots. Saturate slab and maintain high moisture during flush.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 76, "target": 73},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 17, "max": 30, "target": 26},
            "notes": "Reduced light. Low humidity.",
        },
        "medium": {
            "shot_volume_ml": {"min": 150, "max": 300, "target": 200, "notes": "Large flush shots. High runoff."},
            "shots_per_day": {"min": 3, "max": 5, "target": 4},
            "dryback_pct": {"min": 5, "max": 10, "target": 8},
            "slab_weight_pct": {"target": 80, "range": "70-90", "notes": "Keep slab saturated for flushing."},
            "steering_mode": "none",
            "notes": "FLUSH MODE. Saturate slab. Large shots with high runoff (30%+) to leach salts. Monitor runoff EC — flush is done when runoff EC drops below 0.3-0.5. Rockwool flushes efficiently.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Plain pH'd water only (pH 5.8). EC 0.0-0.2. No nutrients.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Switch to flush solution",
                "description": "Plain pH 5.8 water. No nutrients (rockwool doesn't have cation exchange like coco — no CalMag needed during flush).",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor runoff EC daily",
                "description": "Flush complete when runoff EC drops below 0.3-0.5.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Trichome checks daily",
                "description": "Harvest window approaching.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Bud rot inspection",
                "description": "High slab moisture during flush increases risk.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Runoff EC dropping?",
            "Fan leaves yellowing dramatically?",
            "No bud rot?",
            "Trichomes at target?",
        ],
        "common_problems": [
            {
                "issue": "Runoff EC not dropping",
                "cause": "Insufficient flush volume",
                "solution": "Increase shot volume. More runoff.",
            },
        ],
        "training": [],
        "transition_signals": ["Runoff EC below 0.5", "Heavy yellowing", "Trichomes at target ratio"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "N/A."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor/greenhouse.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Manage humidity from saturated slabs."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Watch humidity spike.",
            },
        },
    },
    # ── 10. HARVEST ──────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Chop day. Cut plants, trim, hang to dry. Dispose of spent slabs — rockwool is NOT reusable (unlike coco). One grow per slab.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Some growers give 24-48 hours darkness before chop.",
        },
        "medium": {
            "shot_volume_ml": 0,
            "shots_per_day": 0,
            "dryback_pct": 0,
            "slab_weight_pct": None,
            "steering_mode": None,
            "notes": "No more irrigation. Dispose of spent slabs — NOT compostable. Landfill or specialized rockwool recycling programs (Grodan). Wear gloves when handling dry rockwool — fibers irritate skin.",
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
                "name": "Final trichome check",
                "description": "Confirm target ratio.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Harvest",
                "description": "Cut main stem. Wet trim or whole-plant hang.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Dispose of slabs",
                "description": "Spent rockwool → landfill or recycling. NOT compostable. Wear gloves for dry handling.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Clean equipment",
                "description": "Clean drip system, lines, stakes. Sanitize with H2O2.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Trichomes at target?", "No bud rot found during trim?"],
        "common_problems": [
            {
                "issue": "Bud rot found during trim",
                "cause": "Hidden rot in dense colas",
                "solution": "Cut away rot + 1 inch. Salvage clean buds.",
            },
        ],
        "training": [],
        "transition_signals": ["Plant chopped", "Material hung", "Slabs disposed"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "N/A."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "N/A.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Use greenhouse space for drying."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Drying space.",
            },
        },
    },
    # ── 11. DRYING ───────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Slow controlled drying. 60°F / 60% humidity / darkness. Rockwool-grown flower dries similarly to hydro-grown.",
        "environment": {
            "temp_day_f": {"min": 58, "max": 65, "target": 60},
            "temp_night_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK. 60°F. 60% RH. Gentle airflow not directly on buds.",
        },
        "medium": {
            "shot_volume_ml": 0,
            "shots_per_day": 0,
            "dryback_pct": 0,
            "slab_weight_pct": None,
            "steering_mode": None,
            "notes": "No rockwool involvement. Drying is environmental control.",
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
                "name": "Hang plants/branches",
                "description": "Space so they don't touch.",
                "interval_days": None,
                "priority": "high",
            },
            {"name": "Maintain 60/60", "description": "60°F, 60% RH, dark.", "interval_days": None, "priority": "high"},
            {
                "name": "Check drying progress",
                "description": "Bend stem — snaps = ready.",
                "interval_days": 1,
                "priority": "high",
            },
            {"name": "Inspect for mold", "description": "Daily.", "interval_days": 1, "priority": "high"},
        ],
        "health_checks": ["Temp 58-65°F?", "Humidity 55-65%?", "Dark?", "No mold?"],
        "common_problems": [
            {"issue": "Drying too fast", "cause": "Low humidity, high temp", "solution": "Raise humidity, lower temp."},
            {
                "issue": "Mold during drying",
                "cause": "Dense buds + high humidity",
                "solution": "Remove moldy buds. Lower humidity.",
            },
        ],
        "training": [],
        "transition_signals": ["Small stems snap", "Outer buds dry not crunchy", "7-14 days"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Dry indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always indoors.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Too warm/bright. Dry in dark room."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Separate dark room.",
            },
        },
    },
    # ── 12. CURING ───────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Mason jar cure. Minimum 2 weeks, ideal 4-8 weeks.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "In-jar: 58-62% RH (Boveda 62). Dark, cool storage.",
        },
        "medium": {
            "shot_volume_ml": 0,
            "shots_per_day": 0,
            "dryback_pct": 0,
            "slab_weight_pct": None,
            "steering_mode": None,
            "notes": "Post-harvest processing.",
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
                "description": "Trim sugar leaves. Jars 75% full.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Burp jars",
                "description": "2-3x/day week 1, 1x/day week 2.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Add Boveda packs",
                "description": "Boveda 62%, 1 per oz.",
                "interval_days": None,
                "priority": "medium",
            },
            {"name": "Monitor for mold", "description": "Check when burping.", "interval_days": 1, "priority": "high"},
        ],
        "health_checks": ["In-jar 58-62% RH?", "No mold/ammonia?", "Improving smell?"],
        "common_problems": [
            {"issue": "Ammonia smell", "cause": "Too wet when jarred", "solution": "Remove, dry 12-24 hours, rejar."},
            {"issue": "Too dry", "cause": "Over-dried", "solution": "Boveda 62 to rehydrate."},
        ],
        "training": [],
        "transition_signals": ["Rich aroma", "Smooth smoke", "Stable 58-62% RH"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Cure indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Same process.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Cure indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Stable indoor space.",
            },
        },
    },

    # ── 13. STORAGE ──────────────────────────────────────────────────────
    {
        "id": "storage",
        "name": "Long-Term Storage",
        "order": 13,
        "duration_days": {"min": 30, "max": 365, "typical": 180},
        "description": "Post-cure long-term storage. Rockwool's precision crop steering produces premium, dense flower — that quality investment must be protected in storage. Commercial rockwool operations (the dominant commercial indoor method) often store hundreds of pounds. Proper storage preserves potency and terpenes for 6-12+ months.",
        "environment": {
            "temp_day_f": {"min": 55, "max": 65, "target": 60},
            "temp_night_f": {"min": 55, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "vpd_kpa": None,
            "light_hours": 0, "light_ppfd": 0, "light_dli": 0,
            "notes": "DARK. Cool. Stable. Zero light — UV destroys cannabinoids and terpenes. Commercial: 58-62°F, 55-60% RH, nitrogen atmosphere.",
        },
        "medium": None,
        "nutrients": {"strength_pct": 0, "approach": "None.", "flora_micro_ml_per_gal": 0, "flora_gro_ml_per_gal": 0, "flora_bloom_ml_per_gal": 0, "calmag_ml_per_gal": 0, "supplements": []},
        "tasks": [
            {"name": "Transfer to long-term containers", "description": "Home: mason jars with Boveda 58-62%. Commercial: nitrogen-sealed grove bags, CVault, or nitrogen-flushed drums.", "interval_days": None, "priority": "high"},
            {"name": "Label and track batches", "description": "Strain, harvest date, storage date, weight, batch number, steering profile. Commercial: seed-to-sale, FIFO rotation.", "interval_days": None, "priority": "high"},
            {"name": "Monthly quality checks", "description": "Inspect for mold, off odors. Check humidity packs. Commercial: potency/terpene testing at 30/90/180 days.", "interval_days": 30, "priority": "high"},
            {"name": "Maintain environment", "description": "Monitor vault temp/humidity. No light leaks. Commercial: automated alerts.", "interval_days": 1, "priority": "high"},
            {"name": "Rotate stock (FIFO)", "description": "First in, first out. Flag batches approaching 12 months.", "interval_days": 30, "priority": "medium"},
            {"name": "Compliance testing holds", "description": "Commercial: retain samples per regulations.", "interval_days": None, "priority": "medium"},
        ],
        "health_checks": ["Temp 55-65°F?", "Humidity 55-62%?", "Complete darkness?", "No mold/off odors?", "Humidity packs active?", "FIFO maintained?"],
        "common_problems": [
            {"issue": "THC degrading to CBN", "cause": "Heat, light, oxygen, or time", "solution": "Darkness, cool temps (60°F), minimal oxygen. ~5%/year baseline."},
            {"issue": "Terpene loss", "cause": "Temps above 70°F, oxygen, frequent opening", "solution": "Below 65°F. Nitrogen-sealed. Minimize opening."},
            {"issue": "Mold in storage", "cause": "Humidity above 65% or improper cure", "solution": "Verify 58-62% RH before sealing. Remove affected material."},
            {"issue": "Weight loss", "cause": "Normal moisture equilibration", "solution": "Boveda packs. Sealed containers."},
        ],
        "training": [],
        "transition_signals": ["N/A — terminal stage"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Storage is always indoor."}, "extra_tasks": [], "extra_problems": [], "notes": "Indoor controlled environment."},
            "greenhouse": {"environment_overrides": {"notes": "Do NOT store in greenhouse."}, "extra_tasks": [], "extra_problems": [], "notes": "Climate-controlled indoor space only."},
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
                "0_3_months": "Peak quality. Minimal degradation.",
                "3_6_months": "Slight terpene reduction (~10-15%). Potency stable.",
                "6_12_months": "Noticeable terpene loss (~20-30%). THC down ~5%.",
                "12_18_months": "Significant decline. Process into extracts.",
                "18_plus_months": "Convert to extracts, edibles, or topicals.",
            },
            "testing_schedule": {
                "initial": "Full panel at harvest",
                "30_days": "Potency + terpenes (post-cure baseline)",
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

ROCKWOOL_EQUIPMENT: list[dict] = [
    # -- Rockwool media --
    {
        "name": "1-inch starter cubes",
        "category": "media",
        "required": True,
        "notes": "For germination. Pre-soak in pH 5.5 solution.",
    },
    {
        "name": "4-inch grow cubes",
        "category": "media",
        "required": True,
        "notes": "Seedling to early veg. Condition before use.",
    },
    {
        "name": "Rockwool slabs (Hugo or Expert)",
        "category": "media",
        "required": True,
        "notes": "6x36 inch standard. Hugo (larger pores) for cannabis preferred. Condition 24 hours before use. ONE GROW per slab.",
    },
    # -- Irrigation system --
    {
        "name": "Drip stakes (1 per plant)",
        "category": "irrigation",
        "required": True,
        "notes": "Insert into top of 4-inch cube on slab. Delivers shots.",
    },
    {
        "name": "Irrigation timer (multi-event)",
        "category": "irrigation",
        "required": True,
        "notes": "Must support 10-15 events per day in flower. Galcon, Titan, or Netafim. Simple on/off timers won't work.",
    },
    {
        "name": "Pump (submersible)",
        "category": "irrigation",
        "required": True,
        "notes": "Sized for your plant count. Consistent pressure.",
    },
    {
        "name": "Reservoir (opaque)",
        "category": "irrigation",
        "required": True,
        "notes": "Mix nutrients. Opaque to prevent algae. Size for 1-2 days.",
    },
    {
        "name": "Drip tubing + fittings",
        "category": "irrigation",
        "required": True,
        "notes": "1/2 inch main line, 1/4 inch to stakes.",
    },
    {
        "name": "Drain-to-waste trays/channels",
        "category": "irrigation",
        "required": True,
        "notes": "Slabs sit in trays that catch runoff. Drain to waste — rockwool runoff is not recirculated.",
    },
    # -- Monitoring --
    {
        "name": "pH meter (accurate to 0.1)",
        "category": "monitoring",
        "required": True,
        "notes": "Bluelab or Apera. Calibrate weekly.",
    },
    {
        "name": "EC/TDS meter",
        "category": "monitoring",
        "required": True,
        "notes": "Input AND runoff. Delta is critical.",
    },
    {
        "name": "Scale (under slab)",
        "category": "monitoring",
        "required": True,
        "notes": "THE rockwool metric. Weigh slabs to track dryback. Commercial: Aroya Teros or Grodan GroSens substrate sensors. Home: kitchen scale under slab.",
    },
    {"name": "Jeweler's loupe (60-100x)", "category": "monitoring", "required": True, "notes": "Trichome inspection."},
    # -- Environment --
    {"name": "Grow light (LED preferred)", "category": "environment", "required": True, "notes": "LED or HPS."},
    {
        "name": "Exhaust fan + carbon filter",
        "category": "environment",
        "required": True,
        "notes": "Odor control and air exchange.",
    },
    {"name": "Oscillating fan(s)", "category": "environment", "required": True, "notes": "Canopy airflow."},
    {
        "name": "Temperature/humidity controller",
        "category": "environment",
        "required": True,
        "notes": "Climate control.",
    },
    {"name": "Dehumidifier", "category": "environment", "required": True, "notes": "Essential in flower."},
    # -- Nutrients --
    {
        "name": "Base nutrient system",
        "category": "nutrients",
        "required": True,
        "notes": "GH Flora Trio, Athena Pro, Canna, etc.",
    },
    {
        "name": "CalMag supplement",
        "category": "nutrients",
        "required": True,
        "notes": "Rockwool has no cation exchange (unlike coco), but CalMag is still needed for LED grows and RO water.",
    },
    {"name": "pH Up/Down", "category": "nutrients", "required": True, "notes": "pH 5.5-6.0 for rockwool."},
    {
        "name": "Hydroguard",
        "category": "nutrients",
        "required": True,
        "notes": "Root protection in warm moist rockwool.",
    },
    {"name": "PK booster", "category": "nutrients", "required": False, "notes": "Flower supplement."},
    # -- Safety --
    {
        "name": "Gloves (nitrile)",
        "category": "safety",
        "required": True,
        "notes": "Rockwool fibers irritate skin. Wear when handling dry rockwool.",
    },
    {
        "name": "Dust mask",
        "category": "safety",
        "required": True,
        "notes": "Rockwool dust irritates lungs. Wear when cutting or handling dry slabs/cubes.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

ROCKWOOL_QUICK_REFERENCE: dict = {
    "ph_range": {
        "min": 5.5,
        "max": 6.0,
        "sweet_spot": 5.8,
        "notes": "Rockwool pH range is tighter than coco. New rockwool is 7-8 — MUST condition.",
    },
    "ec_by_stage": {
        "germination": 0.0,
        "seedling": 0.4,
        "early_veg": 1.0,
        "late_veg": 1.4,
        "transition": 1.8,
        "early_flower": 2.4,
        "mid_flower": 2.6,
        "late_flower": 2.2,
        "flush": 0.0,
    },
    "crop_steering_guide": {
        "description": "Crop steering is THE rockwool technique. Control vegetative vs generative growth through dryback, EC, and irrigation timing.",
        "vegetative": {
            "dryback_pct": "5-10%",
            "ec": "0.8-1.6",
            "first_shot_delay": "30 min after lights on",
            "slab_weight_target": "70-85%",
            "effect": "Pushes vegetative growth: bigger leaves, taller stems, more branching.",
        },
        "generative": {
            "dryback_pct": "15-30%",
            "ec": "2.2-2.8",
            "first_shot_delay": "1-2 hours after lights on",
            "slab_weight_target": "40-60%",
            "effect": "Pushes flowering: denser buds, more trichomes, faster ripening.",
        },
        "transition": {
            "dryback_pct": "8-15%",
            "ec": "1.6-2.2",
            "first_shot_delay": "45-90 min after lights on",
            "slab_weight_target": "55-75%",
            "effect": "Gradual shift from veg to flower over 7-14 days.",
        },
    },
    "shot_phases": {
        "description": "Daily irrigation is divided into three phases.",
        "P1_morning": "Ramp-up — restore slab to target weight after overnight dryback. Multiple small shots.",
        "P2_midday": "Maintenance — keep slab at target weight during peak transpiration.",
        "P3_afternoon": "Dryback setup — reduce/stop shots to allow overnight dryback.",
    },
    "slab_conditioning_protocol": {
        "step_1": "Unwrap slab from packaging. Wear gloves.",
        "step_2": "Prepare conditioning solution: pH 5.0-5.5, EC 1.0.",
        "step_3": "Submerge or flood slab in solution for 24 hours.",
        "step_4": "Drain completely. Flip slab. Re-flood for 8 hours.",
        "step_5": "Drain. Test runoff pH — must be below 6.0.",
        "step_6": "Cut drainage slits in bottom wrap (off-center, 2-3 slits).",
        "step_7": "Slab is ready for cube placement.",
        "why": "New rockwool pH is 7.0-8.0 (too alkaline for cannabis). The lime binder used in manufacturing raises pH. Conditioning neutralizes this. Skipping conditioning is the #1 rockwool mistake.",
    },
    "slab_weight_guide": {
        "field_capacity_100_pct": "Weight of fully saturated slab after draining (this is your 100% baseline)",
        "dry_slab_0_pct": "Weight of brand new dry slab (before conditioning)",
        "formula": "dryback_pct = (1 - (current_weight - dry_weight) / (field_capacity_weight - dry_weight)) * 100",
        "danger_zone": "Below 35% slab weight — roots begin dying",
        "optimal_veg": "65-85%",
        "optimal_flower": "40-65%",
    },
    "cube_to_slab_guide": {
        "1_inch_cube": "Germination → seedling (first 7-10 days)",
        "4_inch_cube": "Seedling → early veg (7-14 days)",
        "slab": "Early veg → harvest (rest of grow)",
        "transplant_1_to_4": "When roots emerge from 1-inch cube bottom. Place on top of 4-inch cube hole.",
        "transplant_4_to_slab": "When roots emerge from 4-inch cube sides. Place cube on conditioned slab surface.",
    },
    "golden_rules": [
        "Condition rockwool before use. New rockwool pH is 7-8. Non-negotiable.",
        "Slab weight is your #1 metric. Weigh daily. Everything flows from this number.",
        "Morning pre-first-shot weight determines your dryback and steering strategy.",
        "Never let slab weight drop below 35% — roots die fast in dry rockwool.",
        "Crop steering is THE technique — master dryback and you master rockwool.",
        "P1/P2/P3 shot phases structure your daily irrigation curve.",
        "Shot-based irrigation: many small precise doses, not one big watering.",
        "Rockwool is not reusable. One grow per slab. Dispose responsibly.",
        "Wear gloves and mask when handling dry rockwool — fibers irritate.",
        "Drain to waste — rockwool runoff should not be recirculated.",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING
# ─────────────────────────────────────────────────────────────────────────────

ROCKWOOL_TROUBLESHOOTING: list[dict] = [
    {
        "category": "Slab Conditioning & pH",
        "issues": [
            {
                "symptom": "Slow growth, nutrient lockout",
                "cause": "Slab pH too high — conditioning was insufficient",
                "fix": "Check runoff pH. Re-condition: flush with pH 5.0 solution at 5x slab volume. Let sit 8 hours. Retest. This is the #1 rockwool problem.",
            },
            {
                "symptom": "pH drift upward over time",
                "cause": "Lime in rockwool slowly raising pH",
                "fix": "Lower input pH to 5.5. Flush periodically with pH 5.0 solution. Normal in rockwool — requires ongoing management.",
            },
        ],
    },
    {
        "category": "Crop Steering & Irrigation",
        "issues": [
            {
                "symptom": "Airy buds despite high EC",
                "cause": "Dryback too low — still steering vegetative in flower",
                "fix": "Increase overnight dryback to 20-25%. Delay first shot. Run slab drier.",
            },
            {
                "symptom": "Wilt/droop in morning before first shot",
                "cause": "Dryback too aggressive — slab too dry overnight",
                "fix": "Reduce dryback target. Add a late-afternoon shot. Never let slab weight below 40%.",
            },
            {
                "symptom": "Root death (brown, slimy roots at cube-slab interface)",
                "cause": "Slab weight dropped below 35% — oxygen stress and desiccation",
                "fix": "EMERGENCY saturation event. Restore to field capacity. Treat with Hydroguard. Resume at higher slab weight target. Rockwool below 35% kills roots faster than any other medium.",
            },
            {
                "symptom": "Uneven moisture in slab",
                "cause": "Drip stake placement wrong, slab tilted incorrectly, or drainage slits blocked",
                "fix": "Check stake position (centered over plant). Ensure slight tilt toward drainage slits. Clear blocked slits.",
            },
        ],
    },
    {
        "category": "Nutrients & Salt Management",
        "issues": [
            {
                "symptom": "Runoff EC climbing despite good input",
                "cause": "Salt accumulation in slab from high-EC feeding with insufficient runoff",
                "fix": "Increase shot volume for more runoff (target 20%+). Or flush with low-EC solution.",
            },
            {
                "symptom": "Multiple deficiency symptoms simultaneously",
                "cause": "Salt lockout — concentrated salts blocking uptake",
                "fix": "Flush with low-EC solution (EC 0.2) until runoff matches input. Resume at 80% previous EC.",
            },
            {
                "symptom": "Algae on slab surface",
                "cause": "Light reaching wet rockwool",
                "fix": "Cover ALL exposed rockwool with opaque material. No light on rockwool. Algae hosts pests and competes for nutrients.",
            },
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — the single export consumed by the API/frontend
# ─────────────────────────────────────────────────────────────────────────────

ROCKWOOL_CONFIG: dict = {
    "grow_type_id": "rockwool",
    "version": "1.0.0",
    "stages": ROCKWOOL_STAGES,
    "equipment": ROCKWOOL_EQUIPMENT,
    "quick_reference": ROCKWOOL_QUICK_REFERENCE,
    "troubleshooting": ROCKWOOL_TROUBLESHOOTING,
    "total_grow_days": {"min": 98, "max": 189, "typical": 135},
}
