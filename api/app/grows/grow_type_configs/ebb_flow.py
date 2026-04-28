"""Ebb & Flow (Flood and Drain) — Complete grow type configuration.

Enterprise-grade configuration for Ebb & Flow systems where trays or pots are
periodically flooded with nutrient solution then drained back to a reservoir.
The defining feature is **versatility** — works with many growing media (hydroton,
rockwool, perlite, coco) and container configurations (individual pots on a flood
table, or media-filled flood trays).

Key Ebb & Flow differences from DWC/NFT:
  - Flood/drain cycles (frequency and duration change by stage, media, and plant size)
  - Media selection dramatically changes flood frequency (hydroton 4-6x/day, rockwool 2-3x)
  - Tray engineering (level surface, overflow prevention, flood height)
  - Timer reliability is critical (timer stuck ON = overflow, stuck OFF = drought)
  - Roots experience wet/dry cycles — NOT continuously submerged
  - Excellent oxygenation (roots get air during drain periods)
  - More forgiving than NFT or aeroponics (plants survive hours without a flood)

Supports three environment types (matching Tent.environment_type):
  - indoor  (default — full environmental control, artificial light)
  - outdoor (no climate control, natural photoperiod, weather exposure)
  - greenhouse (partial climate control, natural + supplemental light)
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in an Ebb & Flow grow
# ─────────────────────────────────────────────────────────────────────────────

EBB_FLOW_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Seed cracks open and taproot emerges. For Ebb & Flow, start seeds in Rapid Rooters, rockwool cubes, or directly in the chosen media. Seeds are NOT on the flood table yet — germinate separately in a humidity dome.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Keep seeds in darkness. Heat mat at 78°F. No light until sprout emerges. Humidity dome over propagation tray.",
        },
        "flood_cycle": {
            "floods_per_day": 0,
            "flood_duration_min": 0,
            "drain_time_min": 0,
            "night_floods": False,
            "flood_height_inches": 0,
            "media_specific": {},
            "notes": "Seeds are NOT on the flood table yet. They are in a propagation tray with humidity dome. Germinate off-system.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 5.8, "target": 5.5},
            "ec": {"min": 0.0, "max": 0.0, "target": 0.0},
            "ppm_500": {"min": 0, "max": 0, "target": 0},
            "water_temp_f": {"min": 68, "max": 75, "target": 72},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "notes": "No reservoir running yet. Pre-soak growing media while seeds germinate. Leak-test the flood table, fittings, and pump.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None — seeds contain all energy needed to germinate.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Start seeds",
                "description": "Soak seeds 12-24 hours, then place in Rapid Rooters or pre-soaked rockwool cubes in a humidity dome. If using hydroton: start in Rapid Rooter first, transplant later.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for taproot",
                "description": "After 24-72 hours, look for white taproot emerging. Do not disturb the seed — just look.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Prepare flood table",
                "description": "While seeds germinate: set up flood table, verify it's PERFECTLY level, test pump and timer, check overflow fitting height, verify drain-back.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Level the flood table",
                "description": "Use a spirit level. The table must be perfectly level in BOTH directions. Even 1/8 inch slope means uneven flooding — one end floods deeper than the other.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Pre-soak growing media",
                "description": "Rinse hydroton thoroughly (pH 5.5 water). Soak rockwool in pH 5.5 water for 1 hour. Rinse perlite to remove dust.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Has the seed cracked open?",
            "Is the taproot visible and white?",
            "Is the starter medium moist but not soaking?",
            "Temperature at 75-80°F?",
            "Is the flood table level and leak-tested?",
        ],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Too cold, too wet, or bad seed",
                "solution": "Ensure 75-80°F. Starter medium should be moist not soaking. Try a different seed after 7 days.",
            },
            {
                "issue": "Flood table not level",
                "cause": "Surface or stand is uneven",
                "solution": "Shim the table or stand until a spirit level reads level in both directions. This is critical — fix it before any plants go on.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Taproot visible through starter medium",
            "Sprout emerging",
            "First cotyledon leaves visible",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Start seeds indoors. Outdoor flood tables are exposed to rain and temp swings — seedlings are too fragile."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always germinate indoors for Ebb & Flow.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse germination: use heat mat and humidity dome. Greenhouse temp swings may be too large without supplemental heating."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Heat mat recommended in greenhouse.",
            },
        },
    },
    # ── 2. SEEDLING ──────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Seedling develops first true leaves. Can be placed on the flood table in final media/pots now, with very gentle flood cycles. Alternatively, keep on propagation tray and hand-water until more established. If placing on the flood table: use very shallow, infrequent floods.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 65, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 250, "target": 200},
            "light_dli": {"min": 6, "max": 16, "target": 13},
            "notes": "Gentle light. Remove humidity dome after 3-5 days. First floods should be shallow — water must NOT touch the stem above the media line.",
        },
        "flood_cycle": {
            "floods_per_day": {"min": 1, "max": 2, "target": 1},
            "flood_duration_min": {"min": 10, "max": 15, "target": 12},
            "drain_time_min": {"min": 10, "max": 20, "target": 15},
            "night_floods": False,
            "flood_height_inches": {"min": 1.5, "max": 2.0, "target": 1.5},
            "media_specific": {
                "hydroton": {
                    "floods_per_day": 2,
                    "notes": "Hydroton drains fast. 2 floods/day for seedlings. Flood just enough to wet the bottom half of the pot.",
                },
                "rockwool": {
                    "floods_per_day": 1,
                    "notes": "Rockwool retains moisture well. 1 flood/day is sufficient. Over-flooding rockwool drowns seedlings.",
                },
                "perlite": {
                    "floods_per_day": 2,
                    "notes": "Perlite drains moderately. 2 floods/day. Similar to hydroton but retains slightly more moisture.",
                },
                "coco": {
                    "floods_per_day": 1,
                    "notes": "Coco holds moisture excellently. 1 flood/day maximum. Let coco dry slightly between floods.",
                },
            },
            "notes": "Very gentle floods. Water level should reach only 1.5-2 inches up the pot/media — just enough to wet the bottom root zone. No floods at night — seedlings don't need it and excess moisture promotes damping off.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.2, "max": 0.5, "target": 0.3},
            "ppm_500": {"min": 100, "max": 250, "target": 150},
            "water_temp_f": {"min": 68, "max": 75, "target": 72},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "Very dilute nutrient solution. Reservoir should be sized at minimum 2x the flood table volume. Read pH/EC 30 minutes after last flood (drain-back stabilizes readings).",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "Quarter strength. Seedlings are tiny. The flood cycle delivers nutrients to roots during each flood — no continuous feeding needed.",
            "flora_micro_ml_per_gal": 0.625,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 0.3125,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Protect young roots. Flood tables are warm and moist — ideal for Pythium.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Place seedlings on flood table",
                "description": "Transfer seedlings in their starter medium into net pots or pots filled with chosen media. Place on flood table. Ensure flood height does NOT reach the stem.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Run first test flood",
                "description": "Run pump manually. Verify flood height is correct (1.5-2 inches). Time the fill and drain. Verify complete drain-back to reservoir.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Set timer for floods",
                "description": "Program timer for 1-2 floods per day during lights-on only. Each flood = pump on for 10-15 minutes (enough to fill and soak).",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check pH/EC after drain-back",
                "description": "Read reservoir pH/EC 30 minutes after a flood. Drain-back carries information about root zone conditions.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Verify complete drainage",
                "description": "After each flood, all water must drain back to reservoir. Standing water on the table = level problem or clogged drain.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor seedling health",
                "description": "Watch for stretching, yellowing, or damping off. Reduce flood frequency if media stays too wet.",
                "interval_days": 1,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Seedlings standing upright after floods?",
            "No standing water on table after drain-back?",
            "First true leaves appearing?",
            "Flood height not touching stems?",
            "Media drying appropriately between floods?",
        ],
        "common_problems": [
            {
                "issue": "Damping off (stem collapse at media line)",
                "cause": "Flood height too high — water touching the stem, or too frequent floods keeping media soggy",
                "solution": "Lower flood height. Reduce flood frequency. Improve airflow. Remove affected seedlings — damping off is fatal.",
            },
            {
                "issue": "Seedlings falling over after flood",
                "cause": "Media not supporting the seedling, or flood turbulence knocking it over",
                "solution": "Pack media gently around seedling base. Use slower fill rate. Support with a small stake temporarily.",
            },
            {
                "issue": "Standing water on table after drain",
                "cause": "Table not level, or drain fitting clogged",
                "solution": "Re-level table. Clean drain fitting. Verify siphon break on overflow fitting.",
            },
            {
                "issue": "Algae on media surface / table",
                "cause": "Light reaching wet surfaces",
                "solution": "Cover exposed media surface with hydroton or perlite. Use opaque pots. Block light from reaching table surface.",
            },
        ],
        "training": [],
        "transition_signals": [
            "2-3 sets of true leaves",
            "Seedling 3-4 inches tall",
            "Roots visible at bottom of pot (if net pots)",
            "Sturdy stem",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: rain can flood the table uncontrollably. Cover the flood table or ensure drainage can handle rain volume."
                },
                "extra_tasks": [
                    {
                        "name": "Install rain cover over flood table",
                        "description": "Rain flooding the table dilutes nutrients and can overflow. Cover is mandatory for outdoor Ebb & Flow.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Rain overfilling flood table",
                        "cause": "Uncovered outdoor table",
                        "solution": "Install permanent rain cover. Ensure overflow fitting can handle sudden water influx.",
                    },
                ],
                "notes": "Outdoor Ebb & Flow: rain cover is mandatory.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: good environment for seedlings. Warmer temps may require more frequent floods if media dries faster."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: monitor media moisture more closely in warm conditions.",
            },
        },
    },
    # ── 3. EARLY VEG ─────────────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Veg",
        "order": 3,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Rapid early vegetative growth. Roots are expanding into the media. Flood frequency increases as roots grow and water demand rises. This is where the flood table's versatility shines — you can mix pot sizes and even media types on the same table.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 55, "max": 70, "target": 65},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 250, "max": 450, "target": 350},
            "light_dli": {"min": 16, "max": 29, "target": 23},
            "notes": "Increase light intensity for veg growth. Plants are establishing — flood frequency ramps up.",
        },
        "flood_cycle": {
            "floods_per_day": {"min": 2, "max": 4, "target": 3},
            "flood_duration_min": {"min": 10, "max": 15, "target": 12},
            "drain_time_min": {"min": 10, "max": 20, "target": 15},
            "night_floods": False,
            "flood_height_inches": {"min": 2, "max": 3, "target": 2.5},
            "media_specific": {
                "hydroton": {
                    "floods_per_day": 4,
                    "notes": "Hydroton drains completely. 4 floods/day during lights-on. Don't let hydroton dry out completely — roots are growing.",
                },
                "rockwool": {
                    "floods_per_day": 2,
                    "notes": "Rockwool still retains well. 2 floods/day. Watch for waterlogging — reduce to 1 if cubes feel heavy.",
                },
                "perlite": {
                    "floods_per_day": 3,
                    "notes": "Perlite dries moderately. 3 floods/day. Balanced between hydroton and rockwool.",
                },
                "coco": {
                    "floods_per_day": 2,
                    "notes": "Coco holds moisture. 2 floods/day. Let top of coco dry slightly between floods.",
                },
            },
            "notes": "Increase flood frequency from seedling stage. Flood height reaches 2-3 inches — about 2/3 up the media in the pot. Root zone gets fully saturated during floods, then oxygenated during drain. This wet/dry cycle is the core advantage of Ebb & Flow.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.6, "max": 1.0, "target": 0.8},
            "ppm_500": {"min": 300, "max": 500, "target": 400},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "Plants consuming more nutrients now. Read pH/EC 30 minutes after flood drain-back for most accurate readings. Aerate reservoir between floods.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half strength. Plants are actively growing and consuming nutrients during each flood. Ebb & Flow's periodic feeding is efficient — roots absorb during floods and oxygenate during drain.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root protection. Warm flood tables are prime territory for Pythium.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Increase flood frequency",
                "description": "Bump from seedling 1-2x to early veg 2-4x per day. Adjust based on media type — see media-specific recommendations.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check pH/EC after drain-back",
                "description": "Read reservoir 30 minutes after a flood. Adjust as needed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Verify complete drainage",
                "description": "After every flood, ALL water must drain back. Check for pooling. Check drain fitting for clogs.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Reservoir change",
                "description": "Full change every 7 days.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Check media moisture between floods",
                "description": "Media should be moist but not soaking between floods. If still soggy when next flood hits, reduce frequency. If bone dry, increase frequency.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Inspect roots",
                "description": "Lift a pot and check roots. White roots growing out the bottom = healthy. Brown/slimy = reduce flood frequency or treat.",
                "interval_days": 5,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Vigorous new growth visible?",
            "Media drying appropriately between floods?",
            "Complete drain-back to reservoir?",
            "Roots white and growing out pot bottoms?",
            "No standing water on table between floods?",
        ],
        "common_problems": [
            {
                "issue": "Media staying too wet between floods",
                "cause": "Flooding too frequently for the media type, or poor drainage",
                "solution": "Reduce flood frequency. Check that pots have adequate drainage holes. Verify table drains completely. Switch to a faster-draining media if persistent.",
            },
            {
                "issue": "Salt buildup on media surface",
                "cause": "Nutrient solution wicking up and evaporating, depositing salts on media surface",
                "solution": "Top-water with plain pH'd water occasionally to flush surface salts down. Happens more with perlite and coco.",
            },
            {
                "issue": "Uneven growth across table",
                "cause": "Table not perfectly level — some plants getting deeper floods than others",
                "solution": "Re-level the table. Even small variations (1/8 inch) cause uneven flood depth across a 4-foot table.",
            },
            {
                "issue": "Pump not filling table in time",
                "cause": "Pump undersized for table volume, or tubing too small",
                "solution": "Upgrade pump. Table should fill to target height in 5-10 minutes max. Use larger tubing if restricted.",
            },
        ],
        "training": [
            {
                "technique": "Low-Stress Training (LST)",
                "when": "Once plant has 4-5 nodes",
                "description": "Bend and tie down main stem. Ebb & Flow pots provide good anchoring — tie to pot rim.",
            },
        ],
        "transition_signals": [
            "Plant showing vigorous new growth",
            "4-5 nodes on main stem",
            "Roots growing through pot drainage holes",
            "No signs of over/under watering",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor early veg: natural photoperiod controls veg length. Rain cover over flood table is mandatory."
                },
                "extra_tasks": [
                    {
                        "name": "Check table after rain",
                        "description": "Verify rain hasn't overwhelmed the table. Check reservoir EC — rain dilutes it.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Insects breeding in flood table",
                        "cause": "Standing water, warm moist environment attracts fungus gnats",
                        "solution": "Ensure complete drainage. No standing water between floods. Yellow sticky traps. Mosquito dunks in reservoir if gnats persist.",
                    },
                ],
                "notes": "Outdoor Ebb & Flow: rain cover and pest management are essential.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: may need more frequent floods in warm conditions as media dries faster."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: adjust flood frequency based on temperature.",
            },
        },
    },
    # ── 4. LATE VEG ──────────────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Veg",
        "order": 4,
        "duration_days": {"min": 14, "max": 35, "typical": 21},
        "description": "Rapid vegetative growth. Plants double or triple in size. Flood frequency reaches peak veg levels. Root systems fill pots and start growing out drainage holes onto the table surface. This is normal for Ebb & Flow — roots on the table get fed during floods and oxygenated between them.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 65, "target": 55},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 600, "target": 500},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Full veg light intensity. Plants growing fast. Flood frequency at veg maximum. Monitor table drainage — roots growing on table can partially block the drain fitting.",
        },
        "flood_cycle": {
            "floods_per_day": {"min": 3, "max": 6, "target": 4},
            "flood_duration_min": {"min": 10, "max": 15, "target": 12},
            "drain_time_min": {"min": 10, "max": 20, "target": 15},
            "night_floods": False,
            "flood_height_inches": {"min": 2, "max": 3, "target": 2.5},
            "media_specific": {
                "hydroton": {
                    "floods_per_day": 6,
                    "notes": "Peak veg hydroton: flood every 3 hours during lights-on (6 floods/18hr). Hydroton dries fast with large plants.",
                },
                "rockwool": {
                    "floods_per_day": 3,
                    "notes": "Rockwool: 3 floods/day. Morning, midday, afternoon. Don't over-flood — rockwool stays wet.",
                },
                "perlite": {"floods_per_day": 4, "notes": "Perlite: 4 floods/day. Every 4.5 hours during lights-on."},
                "coco": {
                    "floods_per_day": 3,
                    "notes": "Coco: 3 floods/day. Coco holds moisture well but large veg plants drink heavily.",
                },
            },
            "notes": "Peak veg flood frequency. The exact number depends heavily on media type, pot size, plant size, and room temperature. Watch the media — if it's dry before the next flood, add a flood. If it's still soaking wet, remove one. No night floods in veg.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.8, "max": 1.4, "target": 1.0},
            "ppm_500": {"min": 400, "max": 700, "target": 500},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "Plants consuming more. Reservoir level drops faster between changes. Top off between changes. Read pH/EC after drain-back.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Three-quarter strength for active veg growth. Nitrogen-heavy ratio. Ebb & Flow's periodic feeding allows roots to absorb then breathe — very efficient nutrient uptake.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 1.875,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root zone protection. Flood tables stay warm and moist between floods.",
                },
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Strengthen stems for heavy flower later.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH/EC after drain-back",
                "description": "Daily. Read 30 minutes after flood. Vigorous veg = fast EC changes.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Verify complete drainage",
                "description": "Check after each flood. Roots growing on table can block drain fitting. Clear any root growth near the drain.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Adjust flood frequency",
                "description": "Watch media moisture. Increase floods if media is drying out between cycles. Decrease if staying too wet.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Reservoir change",
                "description": "Full change every 7 days. Flood table systems accumulate salt deposits on the table surface.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Clean table surface",
                "description": "Wipe down exposed table surface to remove salt deposits and algae during reservoir changes.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Training (LST/topping)",
                "description": "Top plants and train to fill the table canopy. Ebb & Flow pots provide good anchor points.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Check timer reliability",
                "description": "Verify timer is cycling correctly. Stuck ON = continuous flood (overflow risk). Stuck OFF = drought.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Plants growing vigorously?",
            "Media moisture appropriate between floods?",
            "Complete drain-back after every flood?",
            "Roots healthy (white, not brown)?",
            "Timer cycling reliably?",
            "No standing water on table between floods?",
        ],
        "common_problems": [
            {
                "issue": "Roots blocking drain fitting",
                "cause": "Roots growing out of pots and across the table toward the drain",
                "solution": "Gently trim roots near the drain fitting. Elevate pots on risers to keep root growth away from the drain. Install a drain guard screen.",
            },
            {
                "issue": "Timer stuck ON (continuous flooding)",
                "cause": "Mechanical timer tab broke, or digital timer glitch",
                "solution": "Install an overflow fitting as a failsafe — it prevents water from rising above a set height even if the pump runs continuously. Check timer weekly. Consider digital timer with backup.",
            },
            {
                "issue": "Timer stuck OFF (no floods)",
                "cause": "Timer malfunction, power outage, or tripped breaker",
                "solution": "Plants survive hours without a flood (Ebb & Flow advantage over NFT), but fix immediately. Run a manual flood while diagnosing. Check power and timer.",
            },
            {
                "issue": "pH swinging after each flood",
                "cause": "Media affecting pH during flood (especially new rockwool or hydroton), or small reservoir relative to table volume",
                "solution": "Pre-soak new media in pH 5.5 water. Use a larger reservoir (2-3x table volume). Let media stabilize over first few floods.",
            },
        ],
        "training": [
            {
                "technique": "Topping",
                "when": "At 5th-6th node",
                "description": "Cut main stem above 5th node. Creates two main colas.",
            },
            {
                "technique": "LST (Low-Stress Training)",
                "when": "Ongoing throughout veg",
                "description": "Bend and tie branches to pot rims. Ebb & Flow pots are excellent LST anchor points.",
            },
            {
                "technique": "SCROG Net",
                "when": "Once plants reach trellis height",
                "description": "Trellis net over flood table creates even canopy.",
            },
        ],
        "transition_signals": [
            "Desired height/spread reached",
            "Strong branching established",
            "Root systems filling pots",
            "Ready for 12/12 light switch",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor veg: natural photoperiod. May need more frequent floods on hot days as media dries faster."
                },
                "extra_tasks": [
                    {
                        "name": "Increase floods on hot days",
                        "description": "Above 85°F, add 1-2 extra floods. Media dries much faster in heat.",
                        "interval_days": 1,
                        "priority": "medium",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Fungus gnats from outdoor moisture",
                        "cause": "Outdoor environment + moist media = gnat paradise",
                        "solution": "Yellow sticky traps. Mosquito dunks (BT) in reservoir. Let media surface dry between floods.",
                    },
                ],
                "notes": "Outdoor: adjust flood frequency for weather conditions.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse veg: excellent growth. May need more frequent floods in warm conditions."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: monitor media moisture closely in warm weather.",
            },
        },
    },
    # ── 5. TRANSITION (FLIP TO FLOWER) ───────────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Flip to Flower)",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Light flips to 12/12. The plant stretches 50-200% in height. Flood frequency adjusts — water demand increases during stretch but you may want to start adding a night flood to support the rapid growth. Nutrient ratio shifts from nitrogen to phosphorus/potassium.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 64, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 60, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 550},
            "light_dli": {"min": 17, "max": 30, "target": 24},
            "notes": "Switch to 12/12. Dark period must be UNINTERRUPTED. Stretch will be dramatic — have support structures ready.",
        },
        "flood_cycle": {
            "floods_per_day": {"min": 3, "max": 5, "target": 4},
            "flood_duration_min": {"min": 10, "max": 15, "target": 12},
            "drain_time_min": {"min": 10, "max": 20, "target": 15},
            "night_floods": True,
            "night_flood_count": 1,
            "flood_height_inches": {"min": 2, "max": 3, "target": 2.5},
            "media_specific": {
                "hydroton": {
                    "floods_per_day": 5,
                    "night_floods": 1,
                    "notes": "Hydroton: 4 during lights-on + 1 night flood during stretch. Plants drink heavily.",
                },
                "rockwool": {
                    "floods_per_day": 3,
                    "night_floods": 0,
                    "notes": "Rockwool: 3 during lights-on. No night flood needed — rockwool retains enough.",
                },
                "perlite": {
                    "floods_per_day": 4,
                    "night_floods": 1,
                    "notes": "Perlite: 3 during lights-on + 1 night flood.",
                },
                "coco": {
                    "floods_per_day": 3,
                    "night_floods": 0,
                    "notes": "Coco: 3 during lights-on. Coco retains through the night.",
                },
            },
            "notes": "Transition introduces the first night flood for fast-draining media (hydroton, perlite). Stretching plants drink heavily. Adjust frequency based on media drying speed. Monitor media moisture at end of dark period — if bone dry, add a night flood.",
        },
        "reservoir": {
            "ph": {"min": 5.6, "max": 6.2, "target": 5.9},
            "ec": {"min": 0.8, "max": 1.4, "target": 1.1},
            "ppm_500": {"min": 400, "max": 700, "target": 550},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "Transition nutrient mix — shift from grow to bloom. Plants consuming heavily during stretch.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Shift ratio: reduce nitrogen (FloraGro), increase phosphorus/potassium (FloraBloom). Transition is gradual.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection through transition."},
            ],
        },
        "tasks": [
            {
                "name": "Switch to 12/12 light",
                "description": "Set timer to 12 on / 12 off. Verify dark period is complete darkness — any light leak can prevent flowering.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Consider adding night flood",
                "description": "For fast-draining media (hydroton, perlite): check media moisture at end of dark period. If bone dry, add one night flood 4-6 hours into dark period.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Check pH/EC",
                "description": "Daily. Nutrient ratio shifting. pH may swing more.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Support stretching branches",
                "description": "Plants grow 2-4 inches/day during stretch. Trellis net or yoyos essential.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Reservoir change",
                "description": "Transition from veg to bloom nutrient ratio.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Check timer programming",
                "description": "Verify timer is set correctly for the new flood schedule (including any night floods). Double-check dark period has no unintended floods with lights.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Stretch progressing normally (50-200% height increase)?",
            "Media moisture appropriate between floods?",
            "Night flood needed? (Check media at end of dark period)",
            "No light leaks during dark period?",
            "Timer cycling correctly with new schedule?",
        ],
        "common_problems": [
            {
                "issue": "Extreme stretch (3x height)",
                "cause": "Genetics (sativa-dominant) or too much light/dark temp difference",
                "solution": "Supercrop: gently pinch and bend stems at 90 degrees. Ebb & Flow pots provide good support for recovery.",
            },
            {
                "issue": "Media bone dry by morning",
                "cause": "Fast-draining media + large stretching plants + 12hr dark period",
                "solution": "Add one night flood 4-6 hours into dark period. This is normal for hydroton with large plants.",
            },
            {
                "issue": "Pre-flowers not appearing after 2 weeks",
                "cause": "Light leak during dark period",
                "solution": "Check EVERY light source during dark period. Indicator LEDs, timer LEDs, light leaks through vents. Even brief exposure prevents flowering.",
            },
        ],
        "training": [
            {
                "technique": "Supercropping",
                "when": "If plants stretch excessively",
                "description": "Pinch and bend stems at 90 degrees. Heals with reinforced knuckle.",
            },
            {
                "technique": "Lollipop (lower defoliation)",
                "when": "End of stretch (day 10-14)",
                "description": "Remove all growth below bottom 1/3 of plant. Directs energy to top buds.",
            },
        ],
        "transition_signals": [
            "Stretch slowing down",
            "Pre-flowers (pistils) visible at nodes",
            "Nutrient demand shifting to bloom",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: natural photoperiod triggers flowering. Transition is gradual over 2-3 weeks."
                },
                "extra_tasks": [
                    {
                        "name": "Protect from light pollution",
                        "description": "Street lights, porch lights can disrupt flowering. Shield plants from artificial light at night.",
                        "interval_days": 3,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor: natural photoperiod triggers transition more gradually.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: use blackout curtains for 12-hour dark periods."},
                "extra_tasks": [
                    {
                        "name": "Deploy blackout curtains",
                        "description": "Ensure 12 hours of complete darkness.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse: blackout system critical for reliable flowering.",
            },
        },
    },
    # ── 6. EARLY FLOWER ──────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Stretch ends, bud sites established, first pistils (white hairs) visible. Nutrient demand shifts fully to bloom. Flood frequency may decrease slightly from peak veg — flowering plants prefer slightly drier conditions between floods. Night floods continue for fast-draining media.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 80, "target": 77},
            "temp_night_f": {"min": 62, "max": 72, "target": 67},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 800, "target": 650},
            "light_dli": {"min": 22, "max": 35, "target": 28},
            "notes": "Increase light intensity. Drop humidity below 55% — bud rot prevention starts now. Ebb & Flow's wet/dry cycling keeps roots healthy and oxygenated during flower.",
        },
        "flood_cycle": {
            "floods_per_day": {"min": 3, "max": 5, "target": 4},
            "flood_duration_min": {"min": 10, "max": 15, "target": 12},
            "drain_time_min": {"min": 10, "max": 20, "target": 15},
            "night_floods": True,
            "night_flood_count": 1,
            "flood_height_inches": {"min": 2, "max": 3, "target": 2.5},
            "media_specific": {
                "hydroton": {
                    "floods_per_day": 5,
                    "night_floods": 1,
                    "notes": "Hydroton: 4 during lights-on + 1 night. Flowering plants drink heavily but prefer drier between floods than veg.",
                },
                "rockwool": {
                    "floods_per_day": 3,
                    "night_floods": 0,
                    "notes": "Rockwool: 3 during lights-on. No night flood. Rockwool retains plenty.",
                },
                "perlite": {"floods_per_day": 4, "night_floods": 1, "notes": "Perlite: 3 during lights-on + 1 night."},
                "coco": {
                    "floods_per_day": 3,
                    "night_floods": 0,
                    "notes": "Coco: 3 during lights-on. Coco retains through night.",
                },
            },
            "notes": "Flower flood frequency is similar to late veg but the goal shifts: allow more dryback between floods. Flowering plants prefer a slightly drier root zone — this stress-signal promotes flower production. Don't eliminate floods; just let media dry more between them.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 1.0, "max": 1.6, "target": 1.3},
            "ppm_500": {"min": 500, "max": 800, "target": 650},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "notes": "Switch to 5-day reservoir changes during flower. Bloom nutrients cause more salt buildup on table and media surfaces.",
        },
        "nutrients": {
            "strength_pct": 80,
            "approach": "Full bloom transition. Heavy phosphorus and potassium. Reduce nitrogen. Ebb & Flow's periodic feeding delivers nutrients then lets roots oxygenate — excellent for bud development.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection during flower."},
                {
                    "name": "PK Booster (Liquid Koolbloom)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Start PK supplementation as bud sites develop.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH/EC after drain-back",
                "description": "Daily. Bloom nutrients and heavy feeding cause faster pH/EC changes.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Verify complete drainage",
                "description": "Check after floods. Root growth on table may be blocking drain. Clear as needed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Reservoir change + table cleaning",
                "description": "Every 5 days. Wipe down table surface during change to remove salt deposits.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Inspect roots",
                "description": "Lift a pot. Roots should be white with healthy branching. Brown/slimy = root rot starting.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Defoliation (Day 21)",
                "description": "Day 21 of flower: remove large fan leaves blocking bud sites. Improves light penetration and airflow.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Check overflow fitting",
                "description": "Verify overflow fitting is clear and at correct height. A stuck-on pump during flower can damage plants.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Bud sites developing at all nodes?",
            "White pistils visible?",
            "Complete drain-back after every flood?",
            "Media drying appropriately between floods?",
            "Humidity consistently below 55%?",
        ],
        "common_problems": [
            {
                "issue": "Salt crust on table surface and pot rims",
                "cause": "Bloom nutrients depositing from flood/drain cycles",
                "solution": "Clean table during every reservoir change. Rinse pot rims. Top-water pots with plain pH'd water occasionally to flush salts through.",
            },
            {
                "issue": "Root rot in one pot",
                "cause": "That pot staying too wet (poor drainage), or sitting in a low spot on the table",
                "solution": "Check pot drainage holes. Re-level table. Treat reservoir with H2O2 (3ml/gal) for 24 hours, then re-dose Hydroguard.",
            },
            {
                "issue": "Drain fitting clogging during floods",
                "cause": "Root growth, media debris, or salt buildup in drain fitting",
                "solution": "Install a drain guard screen. Clear fitting at every reservoir change. Trim roots growing near drain.",
            },
            {
                "issue": "Flood height inconsistent",
                "cause": "Overflow fitting shifting, or pump performance changing",
                "solution": "Check overflow fitting is at correct height. Check pump output — impeller may need cleaning.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation (Day 21)",
                "when": "Day 21 of flower (~week 3)",
                "description": "Remove large fan leaves blocking bud sites. Opens canopy for light and airflow.",
            },
        ],
        "transition_signals": [
            "Buds forming at all sites",
            "Pistils clustering densely",
            "Stretch fully stopped",
            "Nutrient demand increasing",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor early flower: rain protection mandatory. Rain flooding the table disrupts nutrient levels and can cause overflow."
                },
                "extra_tasks": [
                    {
                        "name": "Check table after rain",
                        "description": "Rain on an outdoor flood table is a major problem — check reservoir EC and table drainage after any rain.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Caterpillars/budworms in outdoor buds",
                        "cause": "Moths laying eggs on flowers",
                        "solution": "BT (Bacillus thuringiensis) spray weekly. Inspect buds for frass.",
                    },
                ],
                "notes": "Outdoor Ebb & Flow in flower: rain protection is non-negotiable.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: run dehumidifier to keep humidity below 55%."},
                "extra_tasks": [
                    {
                        "name": "Run dehumidifier",
                        "description": "Keep humidity below 55% during flower.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse Ebb & Flow in flower: dehumidification is critical.",
            },
        },
    },
    # ── 7. MID FLOWER (BULK PHASE) ────────────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Bulk Phase)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 21},
        "description": "Peak bud production. Buds swell rapidly. Water and nutrient consumption hits maximum. Flood frequency stays at flower levels but water consumption per flood increases — reservoir depletes faster. Salt buildup on the table and media accelerates with heavy bloom nutrients.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 78, "target": 76},
            "temp_night_f": {"min": 60, "max": 70, "target": 66},
            "humidity_pct": {"min": 40, "max": 50, "target": 45},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
            "notes": "Maximum light intensity. Drop humidity to 45%. Temperature differential (day/night) enhances terpene and color production.",
        },
        "flood_cycle": {
            "floods_per_day": {"min": 3, "max": 5, "target": 4},
            "flood_duration_min": {"min": 10, "max": 15, "target": 12},
            "drain_time_min": {"min": 10, "max": 20, "target": 15},
            "night_floods": True,
            "night_flood_count": 1,
            "flood_height_inches": {"min": 2, "max": 3, "target": 2.5},
            "media_specific": {
                "hydroton": {
                    "floods_per_day": 5,
                    "night_floods": 1,
                    "notes": "Hydroton: 4 during lights-on + 1 night. Peak water demand. May need to top off reservoir between changes.",
                },
                "rockwool": {
                    "floods_per_day": 3,
                    "night_floods": 1,
                    "notes": "Rockwool: 2-3 during lights-on + 1 night flood. Even rockwool dries faster now with large flowering plants.",
                },
                "perlite": {"floods_per_day": 4, "night_floods": 1, "notes": "Perlite: 3 during lights-on + 1 night."},
                "coco": {
                    "floods_per_day": 3,
                    "night_floods": 1,
                    "notes": "Coco: 2-3 during lights-on + 1 night. Coco may finally need night floods during peak flower.",
                },
            },
            "notes": "Most media types now benefit from a night flood during peak flower. Plants are consuming heavily. Allow good dryback between daytime floods — flowering plants prefer periodic stress. Reservoir depletes faster — top off between changes.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 1.2, "max": 1.8, "target": 1.5},
            "ppm_500": {"min": 600, "max": 900, "target": 750},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "notes": "Peak consumption. Reservoir level drops fast between changes. Top off daily. Change every 5 days. Clean table surface at each change.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom strength. Maximum phosphorus and potassium. Slight tip burn = plants at maximum capacity (optimal).",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 3.125,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Non-negotiable during flower."},
                {
                    "name": "PK Booster (Liquid Koolbloom)",
                    "dose_ml_per_gal": 1.0,
                    "purpose": "Peak PK supplementation for bud density.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH/EC after drain-back",
                "description": "Daily. Peak consumption means fast EC drops.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off reservoir",
                "description": "May need daily top-offs. Large flowering plants consume heavily.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Reservoir change + table cleaning",
                "description": "Every 5 days. Wipe table surface to remove salt deposits. Bloom nutrients deposit heavily.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Bud rot inspection",
                "description": "Check all bud sites. Dense canopies trap humidity. Part dense buds and look inside.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Verify complete drainage",
                "description": "Daily. Root growth on table can block drain. Critical during flower — standing water causes root rot.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Support heavy branches",
                "description": "Install SCROG net, plant yoyos, or bamboo stakes. Heavy buds need support.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Top-water pots with plain water",
                "description": "Once per week, hand-water each pot from the top with plain pH'd water to flush salt buildup down through the media.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Buds swelling uniformly?",
            "Trichomes milky/clear under loupe?",
            "Complete drain-back after every flood?",
            "Any bud rot signs?",
            "Branches adequately supported?",
        ],
        "common_problems": [
            {
                "issue": "Reservoir depleting within hours",
                "cause": "Peak flower consumption from multiple large plants",
                "solution": "Top off daily. Consider a larger reservoir (3x table volume). Auto-top-off float valve helps.",
            },
            {
                "issue": "Heavy salt crust on table and pots",
                "cause": "Concentrated bloom nutrients depositing from repeated flood/drain cycles",
                "solution": "Clean table at every reservoir change. Top-water pots weekly with plain water. Flush between floods.",
            },
            {
                "issue": "Bud rot at one plant",
                "cause": "Humidity pocket, dense bud, poor airflow",
                "solution": "Remove ALL affected material (cut 2 inches below rot). Increase airflow. Lower humidity.",
            },
            {
                "issue": "Drain fitting completely blocked by roots",
                "cause": "Aggressive root growth on table reaching drain",
                "solution": "Install a drain guard cage. Trim roots near drain. Elevate pots slightly on risers.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation (Day 42)",
                "when": "Day 42 of flower (~week 6)",
                "description": "Final light defoliation. Remove only leaves blocking bud sites.",
            },
        ],
        "transition_signals": [
            "Pistils starting to darken (orange/brown)",
            "Trichomes becoming cloudy/milky",
            "Buds dense and heavy",
            "New pistil production slowing",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: rain protection mandatory. Rain on flood table disrupts nutrient levels."
                },
                "extra_tasks": [
                    {
                        "name": "Shake plants after rain/dew",
                        "description": "Remove moisture from buds each morning.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Morning dew causing bud rot",
                        "cause": "Outdoor humidity + dew on dense buds",
                        "solution": "Shake plants mornings. Add fans if power available.",
                    },
                ],
                "notes": "Outdoor mid flower: dew and rain are primary threats.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: run dehumidifier 24/7 during mid flower."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: dehumidification is critical.",
            },
        },
    },
    # ── 8. LATE FLOWER (RIPENING) ─────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Final bud maturation and trichome ripening. Reduce nutrients. Trichomes transition from clear→cloudy→amber. Flood frequency can decrease slightly — reduced nutrient strength means less salt buildup. Allow more dryback between floods.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 74},
            "temp_night_f": {"min": 58, "max": 68, "target": 64},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 800},
            "light_dli": {"min": 26, "max": 39, "target": 35},
            "notes": "Cooler temps + large day/night differential enhances color and terpene production.",
        },
        "flood_cycle": {
            "floods_per_day": {"min": 2, "max": 4, "target": 3},
            "flood_duration_min": {"min": 10, "max": 15, "target": 12},
            "drain_time_min": {"min": 10, "max": 20, "target": 15},
            "night_floods": True,
            "night_flood_count": 1,
            "flood_height_inches": {"min": 2, "max": 3, "target": 2.5},
            "media_specific": {
                "hydroton": {
                    "floods_per_day": 4,
                    "night_floods": 1,
                    "notes": "Hydroton: 3 during lights-on + 1 night. Slightly reduced from peak.",
                },
                "rockwool": {
                    "floods_per_day": 2,
                    "night_floods": 0,
                    "notes": "Rockwool: 2 during lights-on. Reduced nutes = less salt, rockwool retains well.",
                },
                "perlite": {"floods_per_day": 3, "night_floods": 1, "notes": "Perlite: 2 during lights-on + 1 night."},
                "coco": {
                    "floods_per_day": 2,
                    "night_floods": 0,
                    "notes": "Coco: 2 during lights-on. Coco retains through night at reduced nute levels.",
                },
            },
            "notes": "Reduce flood frequency slightly. Plants are finishing — they consume less. More dryback between floods promotes final trichome production. Continue night floods only for fast-draining media.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 0.8, "max": 1.2, "target": 1.0},
            "ppm_500": {"min": 400, "max": 600, "target": 500},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "notes": "Reduce nutrient strength. Plants finishing. Continue 5-day reservoir changes.",
        },
        "nutrients": {
            "strength_pct": 60,
            "approach": "Reduced strength. Taper down nutrients. Stop PK boosters. Yellowing fan leaves is normal and desired.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 0.0,
            "flora_bloom_ml_per_gal": 2.0,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Continue until flush begins."},
            ],
        },
        "tasks": [
            {
                "name": "Check trichomes daily",
                "description": "60x loupe or digital microscope. Clear = not ready. Milky = peak THC. Amber = more sedative. Most harvest at 10-20% amber.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check pH/EC after drain-back",
                "description": "Daily. Reduced nutes, pH management continues.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Reservoir change + table cleaning",
                "description": "Continue 5-day changes.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Bud rot patrol",
                "description": "Dense mature buds are most susceptible. Check all plants daily.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Remove dying fan leaves",
                "description": "Yellow/dying leaves are normal. Remove to prevent mold.",
                "interval_days": 3,
                "priority": "low",
            },
        ],
        "health_checks": [
            "Trichome maturity progressing?",
            "Fan leaves yellowing naturally?",
            "Any bud rot?",
            "Complete drain-back after floods?",
        ],
        "common_problems": [
            {
                "issue": "Foxtailing (new growth on buds)",
                "cause": "Light stress or heat stress",
                "solution": "Raise light slightly. Lower room temp.",
            },
            {
                "issue": "Bud rot in final week",
                "cause": "Dense buds + humidity spike",
                "solution": "Harvest immediately if rot spreads. Better slightly early than losing buds.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Trichomes 70-90% milky with 10-20% amber",
            "Pistils 70-80% brown/orange",
            "Fan leaves mostly yellow",
            "Bud growth visibly slowed",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Outdoor: watch for early frost. Harvest before first frost."},
                "extra_tasks": [
                    {
                        "name": "Monitor frost forecast",
                        "description": "Frost kills plants. Harvest before first frost or cover with row covers.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Early frost",
                        "cause": "Late-season temperature drop",
                        "solution": "Harvest immediately or protect with row covers. Bring pots inside if possible — Ebb & Flow pots are portable.",
                    },
                ],
                "notes": "Outdoor: Ebb & Flow advantage — pots can be brought inside for emergencies.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: cool fall nights enhance colors and terpenes."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: cool nights beneficial if above freezing.",
            },
        },
    },
    # ── 9. FLUSH ──────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Run plain pH'd water through the flood table. No nutrients. Ebb & Flow flush is effective — each flood/drain cycle washes salts from the media. Multiple floods per day with plain water progressively removes nutrients from root zone.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 74},
            "temp_night_f": {"min": 58, "max": 68, "target": 64},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 800, "target": 650},
            "light_dli": {"min": 22, "max": 35, "target": 28},
            "notes": "Maintain 12/12. Environment stays the same. Continue bud rot monitoring.",
        },
        "flood_cycle": {
            "floods_per_day": {"min": 3, "max": 5, "target": 4},
            "flood_duration_min": {"min": 10, "max": 15, "target": 12},
            "drain_time_min": {"min": 10, "max": 20, "target": 15},
            "night_floods": True,
            "night_flood_count": 1,
            "flood_height_inches": {"min": 2, "max": 3, "target": 2.5},
            "media_specific": {
                "hydroton": {
                    "floods_per_day": 5,
                    "night_floods": 1,
                    "notes": "Hydroton: increase floods during flush. More floods = faster salt removal from fast-draining media.",
                },
                "rockwool": {
                    "floods_per_day": 3,
                    "night_floods": 1,
                    "notes": "Rockwool: 3 floods/day + 1 night. More than usual to actively flush salts from the retentive media.",
                },
                "perlite": {"floods_per_day": 4, "night_floods": 1, "notes": "Perlite: 4 floods/day + 1 night."},
                "coco": {
                    "floods_per_day": 4,
                    "night_floods": 1,
                    "notes": "Coco: increase to 4 floods/day + 1 night. Coco holds salts — needs aggressive flushing.",
                },
            },
            "notes": "INCREASE flood frequency during flush — opposite of normal flower guidance. Each plain-water flood washes salts from the media. More floods = faster, more thorough flush. Also top-water pots with plain water every 2-3 days to flush from the top down.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 0.0, "max": 0.2, "target": 0.0},
            "ppm_500": {"min": 0, "max": 100, "target": 0},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 3,
            "hydroguard_ml_per_gal": 2,
            "notes": "Plain pH'd water only. Change every 3 days — drain-back water carries salts flushed from media. Monitor EC of reservoir after floods — rising EC means salts are being flushed out (good). Continue Hydroguard.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Zero nutrients. Plain pH'd water. Each flood/drain cycle progressively removes salts from media.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Continue through flush. Root rot in final week wastes the entire grow.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Drain and refill reservoir with plain water",
                "description": "Every 3 days. Drain reservoir, refill with plain pH'd water. The reservoir EC will rise as salts flush from media.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Top-water pots with plain water",
                "description": "Every 2-3 days, hand-water each pot from the top with plain pH'd water to flush salts from the upper media that floods don't reach.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Monitor reservoir EC",
                "description": "Check EC after floods — rising EC means salts flushing from media (good). When EC stops rising, flush is working.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Continue trichome checks",
                "description": "Plants continue maturing during flush.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor for bud rot",
                "description": "Continue daily checks.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Prepare harvest equipment",
                "description": "Sharp trimming scissors, drying rack/lines, mason jars, hygrometers, Boveda packs.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Fan leaves yellowing/fading? (Expected.)",
            "Reservoir EC rising after floods? (Salts flushing — good.)",
            "Trichomes reaching target maturity?",
            "Any bud rot?",
        ],
        "common_problems": [
            {
                "issue": "EC of reservoir not dropping to near-zero",
                "cause": "Salt deposits in media not fully flushing with floods alone",
                "solution": "Top-water pots from above with plain water. Increase flood frequency. Extend flush duration.",
            },
            {
                "issue": "Plant wilting during flush",
                "cause": "Normal — plant finishing its life cycle",
                "solution": "Normal. Maintain flood schedule. Don't add nutrients.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Flush duration reached (7-14 days)",
            "Reservoir EC stays low after floods",
            "Trichomes at target maturity",
            "Fan leaves mostly yellow/fallen",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Outdoor: rain actually helps during flush."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Rain acceptable during flush — aids flushing.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: maintain ventilation. Dying leaves harbor mold."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Remove fallen leaves promptly.",
            },
        },
    },
    # ── 10. HARVEST ───────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Cut plants, trim, and hang to dry. Ebb & Flow harvest advantage: individual pots can be removed from the table independently. You can harvest plants at different times — just remove the ready pots and keep flooding the rest. Very flexible harvest scheduling.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Optional 24-48 hours of darkness before harvest. Cut at base. Pots lift right off the table.",
        },
        "flood_cycle": {
            "floods_per_day": 0,
            "flood_duration_min": 0,
            "drain_time_min": 0,
            "night_floods": False,
            "flood_height_inches": 0,
            "media_specific": {},
            "notes": "Stop floods after last plant is removed. If harvesting in stages, continue flooding for remaining plants.",
        },
        "reservoir": {
            "ph": None,
            "ec": None,
            "ppm_500": None,
            "water_temp_f": None,
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "notes": "Drain reservoir after last harvest. Clean table, fittings, reservoir, and pump.",
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
                "name": "Optional dark period",
                "description": "24-48 hours of darkness before harvest.",
                "interval_days": None,
                "priority": "low",
            },
            {
                "name": "Harvest plants",
                "description": "Remove pots from table. Cut plants at base. Ebb & Flow advantage: pots are portable — harvest one at a time over multiple days if needed.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Wet trim or whole-plant hang",
                "description": "Wet trim: trim immediately. Dry trim: hang whole plants. Wet is faster; dry often produces better flavor.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Clean flood table",
                "description": "Remove all pots. Scrub table surface — salt deposits, root debris, and algae accumulate over the grow. Clean drain and overflow fittings.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Clean pump and reservoir",
                "description": "Disassemble pump, clean impeller. Scrub reservoir. Replace tubing if degraded.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Inspect fittings",
                "description": "Check drain fitting, overflow fitting, and pump connections for wear or cracks.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Trichomes at target maturity when cut?",
            "Any bud rot discovered during trimming?",
            "Flood table fully cleaned?",
        ],
        "common_problems": [
            {
                "issue": "Bud rot discovered during trim",
                "cause": "Hidden rot inside dense colas",
                "solution": "Cut 1+ inches beyond rot. Discard affected material. Inspect remaining buds.",
            },
            {
                "issue": "Table stained from salt deposits",
                "cause": "Months of bloom nutrients depositing",
                "solution": "Soak with vinegar solution for 1 hour. Scrub with brush. H2O2 solution for sanitization.",
            },
        ],
        "training": [],
        "transition_signals": ["All plants cut and hanging", "Table cleaned"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Harvest before frost. Ebb & Flow advantage: pots are portable — bring inside if frost threatens."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: pot portability is a major Ebb & Flow advantage.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse can serve as drying space if humidity is controllable."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: usable as drying space with ventilation.",
            },
        },
    },
    # ── 11. DRYING ────────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Hang whole plants or branches in a dark, cool, ventilated space. Target slow dry over 10-14 days.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 58, "max": 65, "target": 62},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Complete darkness. Gentle airflow (not on buds). 60°F / 60% humidity. Slower dry = better cure.",
        },
        "flood_cycle": {
            "floods_per_day": 0,
            "flood_duration_min": 0,
            "drain_time_min": 0,
            "night_floods": False,
            "flood_height_inches": 0,
            "media_specific": {},
            "notes": "System cleaned and stored.",
        },
        "reservoir": {
            "ph": None,
            "ec": None,
            "ppm_500": None,
            "water_temp_f": None,
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "notes": "System cleaned and stored.",
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
                "name": "Check drying progress",
                "description": "Small stems snap (not bend) when dry. Large stems still slightly flexible. 7-14 days. Do NOT rush.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor temp and humidity",
                "description": "Keep 60-65°F and 55-65% humidity.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check for mold",
                "description": "Inspect hanging buds daily.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Small stems snapping?", "Any mold or off-smell?", "Drying room at 60°F / 60% RH?"],
        "common_problems": [
            {
                "issue": "Buds drying too fast",
                "cause": "Temp too high, humidity too low, fans on buds",
                "solution": "Lower temp. Raise humidity. No direct airflow on buds.",
            },
            {
                "issue": "Mold during drying",
                "cause": "Humidity too high, poor airflow",
                "solution": "Remove moldy material. Increase ventilation. Lower humidity.",
            },
        ],
        "training": [],
        "transition_signals": ["Small stems snap cleanly", "Outside of bud dry to touch", "7-14 days elapsed"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Dry indoors. Never dry outdoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always dry indoors.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse NOT ideal for drying. Dry indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Avoid drying in greenhouse.",
            },
        },
    },
    # ── 12. CURING ────────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Place dried buds in mason jars. Burp daily for first 2 weeks, then weekly. Curing converts chlorophyll into smooth compounds and develops terpenes. Minimum 2-week cure; 4-8 weeks ideal.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 58, "max": 68, "target": 62},
            "humidity_pct": {"min": 58, "max": 65, "target": 62},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Cool, dark place. Boveda 62% packs. Light degrades THC.",
        },
        "flood_cycle": {
            "floods_per_day": 0,
            "flood_duration_min": 0,
            "drain_time_min": 0,
            "night_floods": False,
            "flood_height_inches": 0,
            "media_specific": {},
            "notes": "N/A.",
        },
        "reservoir": {
            "ph": None,
            "ec": None,
            "ppm_500": None,
            "water_temp_f": None,
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "notes": "N/A.",
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
                "name": "Burp jars",
                "description": "Open jars 5-15 min. Week 1-2: daily. Week 3-4: every 2-3 days. After week 4: weekly. Ammonia = too wet.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check jar humidity",
                "description": "Mini hygrometer per jar. Target 58-65%.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Inspect for mold",
                "description": "Check when burping. Any mold = remove immediately.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Jar humidity at 58-65%?", "Smell improving?", "Any mold?"],
        "common_problems": [
            {
                "issue": "Hay/grass smell",
                "cause": "Chlorophyll breaking down. Normal first 1-2 weeks.",
                "solution": "Continue curing. Terpenes emerge after 2-3 weeks.",
            },
            {
                "issue": "Ammonia smell",
                "cause": "Buds jarred too wet.",
                "solution": "Remove buds, dry on paper bag 12-24 hours. Re-jar.",
            },
            {
                "issue": "Buds too dry",
                "cause": "Over-dried or low jar humidity.",
                "solution": "Add Boveda 62% pack. Rehydrates in 3-5 days.",
            },
        ],
        "training": [],
        "transition_signals": ["Cure complete (min 2 weeks, ideal 4-8)", "Rich terpene aroma", "Smooth smoke"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Cure indoors. Same process regardless of grow environment."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Environment-independent.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Do not cure in greenhouse — temp swings degrade quality."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Cure indoors.",
            },
        },
    },

    # ── 13. STORAGE ──────────────────────────────────────────────────────
    {
        "id": "storage",
        "name": "Long-Term Storage",
        "order": 13,
        "duration_days": {"min": 30, "max": 365, "typical": 180},
        "description": "Post-cure long-term storage. Ebb & Flow systems produce consistent yields cycle after cycle — inventory accumulates fast with perpetual harvests. Storage planning is critical for commercial operations running continuous flood tables. Proper storage preserves potency and terpenes for 6-12+ months.",
        "environment": {
            "temp_day_f": {"min": 55, "max": 65, "target": 60},
            "temp_night_f": {"min": 55, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "vpd_kpa": None,
            "light_hours": 0, "light_ppfd": 0, "light_dli": 0,
            "notes": "DARK. Cool. Stable. Zero light — UV destroys cannabinoids and terpenes. Commercial: 58-62°F, 55-60% RH, nitrogen atmosphere.",
        },
        "flood_cycle": None,
        "nutrients": {"strength_pct": 0, "approach": "None.", "flora_micro_ml_per_gal": 0, "flora_gro_ml_per_gal": 0, "flora_bloom_ml_per_gal": 0, "calmag_ml_per_gal": 0, "supplements": []},
        "tasks": [
            {"name": "Transfer to long-term containers", "description": "Home: mason jars with Boveda 58-62%. Commercial: nitrogen-sealed grove bags, CVault, or nitrogen-flushed drums.", "interval_days": None, "priority": "high"},
            {"name": "Label and track batches", "description": "Strain, harvest date, storage date, weight, batch number. Commercial: seed-to-sale, FIFO rotation.", "interval_days": None, "priority": "high"},
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
# EQUIPMENT CHECKLIST
# ─────────────────────────────────────────────────────────────────────────────

EBB_FLOW_EQUIPMENT: list[dict] = [
    # Essentials
    {
        "name": "Flood Table / Tray (2x4 ft or 4x4 ft)",
        "category": "essential",
        "description": "Rigid, waterproof tray. Must be PERFECTLY level. ABS plastic or injection-molded. 2x4 ft for small grows (4-6 plants), 4x4 ft for larger (8-16 plants). Must have drain fitting hole and overflow fitting hole.",
    },
    {
        "name": "Table Stand / Frame",
        "category": "essential",
        "description": "Supports the flood table at working height. Must be rigid and level. Adjustable legs help achieve perfect leveling.",
    },
    {
        "name": "Drain Fitting + Extension",
        "category": "essential",
        "description": "Installed in table's drain hole. Connects via tubing to reservoir below. Screen/guard to prevent media and roots from entering.",
    },
    {
        "name": "Overflow Fitting",
        "category": "essential",
        "description": "Safety fitting set at maximum flood height. If pump sticks ON, overflow fitting prevents water from going higher. Set at 2/3 media height. NON-NEGOTIABLE.",
    },
    {
        "name": "Reservoir (20-50 gal)",
        "category": "essential",
        "description": "Sits below the flood table. Collects drain-back. Size at 2-3x the table flood volume for pH/EC stability. Food-safe, opaque, dark-colored.",
    },
    {
        "name": "Water Pump (submersible)",
        "category": "essential",
        "description": "Pumps from reservoir up to flood table. Size to fill table to target height in 5-10 minutes. Larger tables need bigger pumps.",
    },
    {
        "name": "Timer (digital preferred)",
        "category": "essential",
        "description": "Controls pump on/off cycles. Digital timers are more reliable than mechanical. Minimum 15-minute resolution. Must be programmed for media-specific flood frequency.",
    },
    {
        "name": "Growing Media (choose one)",
        "category": "essential",
        "description": "Hydroton (fast drain, frequent floods), Rockwool cubes/slabs (high retention, fewer floods), Perlite (moderate), or Coco in pots (high retention). Each media changes flood frequency dramatically.",
    },
    {
        "name": "Pots / Net Pots / Containers",
        "category": "essential",
        "description": "Individual pots sitting on the flood table. Net pots for hydroton (roots grow out bottom). Solid pots with drainage holes for coco/perlite. 1-3 gallon for small plants, 3-5 gallon for larger.",
    },
    {
        "name": "pH Pen",
        "category": "essential",
        "description": "Measure at reservoir 30 minutes after drain-back for most accurate readings.",
    },
    {
        "name": "EC/TDS Meter",
        "category": "essential",
        "description": "Measure at reservoir after drain-back. Also check EC of drain-back water to assess root zone conditions.",
    },
    {"name": "pH Up & pH Down", "category": "essential", "description": "Adjust at reservoir."},
    {
        "name": "Nutrients (GH Flora Trio)",
        "category": "essential",
        "description": "Mix in reservoir. Delivered to plants during each flood cycle.",
    },
    {
        "name": "Hydroguard",
        "category": "essential",
        "description": "Root protection. Flood tables are warm, moist environments ideal for Pythium.",
    },
    {
        "name": "Air Pump + Air Stone (for reservoir)",
        "category": "essential",
        "description": "Oxygenate reservoir water between floods.",
    },
    {"name": "Grow Light", "category": "essential", "description": "Size for table footprint canopy area."},
    {
        "name": "Light Timer",
        "category": "essential",
        "description": "Separate from flood timer. Reliable 18/6 → 12/12 scheduling.",
    },
    {"name": "Thermometer / Hygrometer", "category": "essential", "description": "Monitor grow room conditions."},
    {
        "name": "Spirit Level",
        "category": "essential",
        "description": "Verify table is perfectly level. Check BOTH directions. Re-check after loading with heavy pots.",
    },
    # Recommended
    {
        "name": "Drain Guard / Screen",
        "category": "recommended",
        "description": "Prevents roots and media from entering the drain fitting. Saves pump and prevents clogs.",
    },
    {
        "name": "Backup Timer",
        "category": "recommended",
        "description": "Timer failure = either constant flooding (overflow) or drought. Keep a spare timer ready.",
    },
    {"name": "SCROG / Trellis Net", "category": "recommended", "description": "Even canopy across the flood table."},
    {"name": "CalMag Supplement", "category": "recommended", "description": "Essential with RO water."},
    {
        "name": "Silica Supplement",
        "category": "recommended",
        "description": "Strengthen stems. Helpful for heavy flower support.",
    },
    {
        "name": "Oscillating Fans",
        "category": "recommended",
        "description": "Air movement above table prevents humidity pockets.",
    },
    {"name": "Exhaust Fan + Carbon Filter", "category": "recommended", "description": "Odor and humidity control."},
    {
        "name": "Pot Risers",
        "category": "recommended",
        "description": "Elevate pots slightly above table surface. Improves drainage and prevents roots from growing to drain fitting.",
    },
    # Optional
    {
        "name": "Auto-Top-Off (float valve in reservoir)",
        "category": "optional",
        "description": "Maintains reservoir level. Helpful with large plants consuming heavily.",
    },
    {"name": "pH/EC Controller", "category": "optional", "description": "Auto-dosing for reservoir pH and EC."},
    {
        "name": "Water Chiller",
        "category": "optional",
        "description": "Controls reservoir temp. Less critical than in DWC since roots get air between floods.",
    },
    {
        "name": "Multi-Tray Manifold",
        "category": "optional",
        "description": "Run multiple flood tables from one reservoir. Requires larger pump and sequencing valves.",
    },
    {
        "name": "Flood Alarm / Leak Sensor",
        "category": "optional",
        "description": "Alerts if water detected outside the table. Catches leaks and overflows.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE CHARTS
# ─────────────────────────────────────────────────────────────────────────────

EBB_FLOW_QUICK_REFERENCE = {
    "ph_range": {"min": 5.5, "max": 6.2, "ideal": "5.8 seedling/veg, 6.0 flower"},
    "ec_by_stage": {
        "seedling": {"min": 0.2, "max": 0.5},
        "early_veg": {"min": 0.6, "max": 1.0},
        "late_veg": {"min": 0.8, "max": 1.4},
        "transition": {"min": 0.8, "max": 1.4},
        "early_flower": {"min": 1.0, "max": 1.6},
        "mid_flower": {"min": 1.2, "max": 1.8},
        "late_flower": {"min": 0.8, "max": 1.2},
        "flush": {"min": 0.0, "max": 0.2},
    },
    "water_temp_f": {"min": 65, "max": 72, "ideal": 68},
    "flood_frequency_matrix": {
        "description": "Floods per day by media type and stage. Lights-on floods only unless noted.",
        "hydroton": {
            "seedling": 2,
            "early_veg": 4,
            "late_veg": 6,
            "transition": "4+1N",
            "early_flower": "4+1N",
            "mid_flower": "4+1N",
            "late_flower": "3+1N",
            "flush": "4+1N",
        },
        "rockwool": {
            "seedling": 1,
            "early_veg": 2,
            "late_veg": 3,
            "transition": 3,
            "early_flower": 3,
            "mid_flower": "2+1N",
            "late_flower": 2,
            "flush": "2+1N",
        },
        "perlite": {
            "seedling": 2,
            "early_veg": 3,
            "late_veg": 4,
            "transition": "3+1N",
            "early_flower": "3+1N",
            "mid_flower": "3+1N",
            "late_flower": "2+1N",
            "flush": "3+1N",
        },
        "coco": {
            "seedling": 1,
            "early_veg": 2,
            "late_veg": 3,
            "transition": 3,
            "early_flower": 3,
            "mid_flower": "2+1N",
            "late_flower": 2,
            "flush": "3+1N",
        },
        "legend": "+1N = plus 1 night flood",
    },
    "flood_engineering": {
        "flood_height": "2/3 up the media in the pot. NEVER above the stem line.",
        "fill_time": "Table should fill to target height in 5-10 minutes. Faster = pump too large (turbulence). Slower = pump too small.",
        "soak_time": "Once at target height, hold for 2-3 minutes for media saturation, then pump off and drain.",
        "drain_time": "Complete drain-back in 10-20 minutes. If slower, check drain fitting.",
        "overflow_fitting_height": "Set at 2/3 media height. This is your safety — if pump sticks ON, overflow prevents flooding above this line.",
    },
    "reservoir_change_schedule": "Every 7 days in veg, every 5 days in flower, every 3 days during flush",
    "ph_ec_reading_tip": "Read pH/EC at reservoir 30 minutes after drain-back for most accurate readings",
    "hydroguard_dose": "2 ml/gal at every reservoir change AND top-off",
    "nutrient_mixing_order": [
        "Silica (if using)",
        "CalMag",
        "FloraMicro",
        "FloraGro",
        "FloraBloom",
        "Supplements",
        "pH adjust last",
    ],
    "top_off_rule": "EC rising = top off with plain pH'd water. EC dropping = top off with 1/4 strength nutrient water.",
    "golden_rules": [
        "The flood table MUST be perfectly level — even 1/8 inch slope means uneven flooding",
        "Overflow fitting is NON-NEGOTIABLE — it's your safety if the pump sticks ON",
        "Match flood frequency to your media type — hydroton and rockwool are VERY different",
        "Read pH/EC 30 minutes AFTER drain-back for accurate readings",
        "Complete drain-back after EVERY flood — standing water causes root rot",
        "Timer reliability is critical — stuck ON = overflow, stuck OFF = drought",
        "Flood height: 2/3 up the media, NEVER touching the stem",
        "Clean the table surface at every reservoir change — salt deposits accumulate",
        "Top-water pots occasionally with plain pH'd water to flush surface salt buildup",
        "Ebb & Flow is forgiving — plants survive hours without a flood (unlike NFT)",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING GUIDE
# ─────────────────────────────────────────────────────────────────────────────

EBB_FLOW_TROUBLESHOOTING: list[dict] = [
    {
        "category": "Flooding & Drainage Issues",
        "problems": [
            {
                "symptom": "Table not draining completely — standing water after pump shuts off",
                "diagnosis": "Drainage obstruction or level issue",
                "severity": "high",
                "causes": [
                    "Table not level (water pools at low spots)",
                    "Drain fitting clogged with roots or media",
                    "Drain tubing kinked or blocked",
                    "Siphon lock in drain line",
                ],
                "solutions": [
                    "Re-level the table (check BOTH directions)",
                    "Clear drain fitting — remove root debris and media particles",
                    "Check drain tubing for kinks, fix routing",
                    "Install a siphon break on the drain line if gravity drain is slow",
                ],
            },
            {
                "symptom": "Flood height uneven across table",
                "diagnosis": "Table not level",
                "severity": "medium",
                "causes": [
                    "Table or stand not level",
                    "Heavy pots causing table to flex/sag",
                    "Stand settling over time",
                ],
                "solutions": [
                    "Re-level with spirit level in both directions",
                    "Add center support under table to prevent sag from heavy pots",
                    "Use shims to fine-tune level",
                ],
            },
            {
                "symptom": "Overflow fitting activating during normal floods",
                "diagnosis": "Flood height set too high, or overflow fitting too low",
                "severity": "medium",
                "causes": [
                    "Pump filling faster than expected",
                    "Overflow fitting positioned too low",
                    "Drain partially blocked causing water to rise higher",
                ],
                "solutions": [
                    "Reduce pump flow rate",
                    "Raise overflow fitting height (but never above 2/3 media level)",
                    "Clear drain fitting to improve outflow during fill",
                ],
            },
        ],
    },
    {
        "category": "Timer & Pump Failures",
        "problems": [
            {
                "symptom": "Timer stuck ON — pump running continuously",
                "diagnosis": "Timer malfunction — OVERFLOW RISK",
                "severity": "high",
                "causes": [
                    "Mechanical timer tab broke",
                    "Digital timer glitch",
                    "Power surge reset timer",
                    "Wrong mode programmed",
                ],
                "solutions": [
                    "Overflow fitting should prevent disaster (this is why it's required)",
                    "Replace timer immediately. Switch to digital if using mechanical",
                    "Check timer programming after any power outage",
                    "Keep a backup timer ready",
                ],
            },
            {
                "symptom": "Timer stuck OFF — no floods happening",
                "diagnosis": "Timer malfunction — DROUGHT",
                "severity": "medium",
                "causes": ["Timer malfunction", "Power outage", "Tripped breaker", "Timer unplugged"],
                "solutions": [
                    "Ebb & Flow plants survive hours without a flood (much more forgiving than NFT)",
                    "Run a manual flood immediately while diagnosing",
                    "Check power, breaker, timer. Replace timer if faulty",
                    "Consider a smart plug with monitoring that alerts on power loss",
                ],
            },
            {
                "symptom": "Pump not filling table to target height",
                "diagnosis": "Pump capacity issue",
                "severity": "medium",
                "causes": [
                    "Pump undersized for table",
                    "Pump impeller clogged",
                    "Air lock in supply line",
                    "Pump losing capacity with age",
                ],
                "solutions": [
                    "Clean pump impeller",
                    "Check for and bleed air locks in supply tubing",
                    "Upgrade to larger pump if undersized",
                    "Replace aging pump — they lose capacity over time",
                ],
            },
        ],
    },
    {
        "category": "Media-Specific Issues",
        "problems": [
            {
                "symptom": "Hydroton drying out too fast between floods",
                "diagnosis": "Not enough floods for hydroton, or pots too small",
                "severity": "medium",
                "causes": [
                    "Flood frequency too low for hydroton's fast drainage",
                    "Small pots with minimal media volume",
                    "Hot environment accelerating evaporation",
                ],
                "solutions": [
                    "Increase flood frequency (hydroton needs 4-6 floods/day in veg, plus night floods in flower)",
                    "Use larger pots (3-5 gallon) for more media buffer",
                    "Consider mixing perlite into hydroton for slightly better retention",
                ],
            },
            {
                "symptom": "Rockwool staying too wet, roots browning",
                "diagnosis": "Over-flooding for rockwool's high retention",
                "severity": "high",
                "causes": [
                    "Too many floods per day for rockwool",
                    "Rockwool cubes sitting in standing water on table",
                    "Flood height too high for rockwool's retention",
                ],
                "solutions": [
                    "Reduce flood frequency (rockwool needs only 1-3 floods/day)",
                    "Elevate rockwool on risers so it's not sitting in any residual water",
                    "Lower flood height — rockwool wicks water upward, doesn't need deep flooding",
                ],
            },
            {
                "symptom": "Coco developing salt crust on surface",
                "diagnosis": "Normal wicking action but needs management",
                "severity": "low",
                "causes": [
                    "Nutrients wicking up through coco and evaporating at surface",
                    "Common with flood-from-bottom systems",
                    "Higher EC solutions deposit more",
                ],
                "solutions": [
                    "Top-water with plain pH'd water every 3-5 days to flush surface salts down",
                    "Cover coco surface with a layer of hydroton to reduce evaporation",
                    "This is cosmetic unless severe — EC at root level is what matters",
                ],
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLED CONFIG EXPORT
# ─────────────────────────────────────────────────────────────────────────────

EBB_FLOW_CONFIG: dict = {
    "grow_type_id": "ebb_flow",
    "version": "1.0.0",
    "stages": EBB_FLOW_STAGES,
    "equipment": EBB_FLOW_EQUIPMENT,
    "quick_reference": EBB_FLOW_QUICK_REFERENCE,
    "troubleshooting": EBB_FLOW_TROUBLESHOOTING,
    "total_grow_days": {
        "min": 90,
        "max": 150,
        "typical_photo": 120,
        "typical_auto": 80,
        "breakdown": "Germination (3-7d) + Seedling (7-14d) + Veg (24-56d) + Flower (56-70d) + Dry (7-14d) + Cure (14-60d)",
    },
}
