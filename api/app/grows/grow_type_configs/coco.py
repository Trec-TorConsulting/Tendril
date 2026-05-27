"""Coco Coir — Complete grow type configuration.

Enterprise-grade configuration for coco coir growing — the bridge between
hydroponic precision and the physical simplicity of potted plants.  Coco is
a soilless media that requires hydroponic-style nutrient management but with
the hands-on growing experience of traditional container gardening.

The defining features are **mandatory CalMag supplementation** (coco's cation
exchange sites lock out calcium and magnesium), **every watering is a feeding**
(never plain water in coco — the only exception is flush), **high-frequency
fertigation** (multiple times daily in flower), **dryback monitoring** (the
primary crop steering tool), and **buffering/pre-treatment** (raw coco MUST
be rinsed and CalMag-buffered before use).

Key Coco differences from other methods:
  - Every watering includes nutrients (never "just water" except flush)
  - CalMag in EVERY feeding — coco steals Ca/Mg via cation exchange
  - High-frequency, low-volume feeding beats low-frequency, high-volume
  - Dryback % is the primary steering tool (like drip/rockwool)
  - Coco holds ~70% water / 30% air at saturation — excellent air-to-water ratio
  - Never let coco dry completely — it becomes hydrophobic
  - Reusable for 2-3 grows with proper re-buffering
  - Most forgiving hydro-style method — excellent for beginners
  - LED lights increase CalMag demand (less infrared = less heat = less transpiration)
  - RO water makes CalMag deficiency worse (no baseline minerals)

Supports three environment types (matching Tent.environment_type):
  - indoor  (default — full environmental control, artificial light)
  - outdoor (viable but rain disrupts fertigation schedule)
  - greenhouse (excellent — good light + environmental control)

Data sources:
- Coco for Cannabis (cocoforcannabis.com) — best coco-specific resource
- General Hydroponics Flora Trio feeding charts (coco-adjusted)
- Crop steering best practices (Aroya, Athena)
- Cation exchange science for coco media
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in a Coco Coir grow
# ─────────────────────────────────────────────────────────────────────────────

COCO_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Seed cracks open and taproot emerges. Start seeds in Rapid Rooters, rockwool starter cubes, or directly in pre-buffered coco in solo cups. If using coco: the coco MUST be buffered with CalMag before the seed touches it.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Keep seeds in darkness. Heat mat at 78°F. Humidity dome. No light until sprout emerges.",
        },
        "medium": {
            "feed_frequency": 0,
            "runoff_ec_ratio": None,
            "dryback_pct": 0,
            "calmag_mandatory": True,
            "pot_size": "solo cup (16 oz) or starter plug",
            "coco_perlite_ratio": "70/30 recommended",
            "notes": "Seeds are in a humidity dome, not being fertigated yet. While seeds germinate: prepare coco by buffering with CalMag solution (EC 0.8, soak 8+ hours, drain, repeat). This step is NON-NEGOTIABLE for raw coco.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None — seeds contain all energy needed to germinate. But the coco itself must be pre-buffered with CalMag.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Buffer coco coir",
                "description": "Rinse raw coco thoroughly to remove salts and dust. Soak in CalMag solution (EC 0.8, pH 5.8) for 8-24 hours. Drain. Repeat soak. Drain. This charges the cation exchange sites so coco won't steal calcium from your nutrient solution. Pre-buffered brands (Canna, Mother Earth) need less prep but still benefit from a CalMag rinse.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Mix coco and perlite",
                "description": "Mix 70% coco and 30% perlite by volume. This provides ideal drainage and air-to-water ratio. Some growers use straight coco — it works but drains slower.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Start seeds",
                "description": "Soak seeds 12-24 hours in plain pH 6.0 water. Place in Rapid Rooters, pre-soaked rockwool cubes, or directly in pre-buffered coco in solo cups. Cover with humidity dome.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for taproot",
                "description": "After 24-72 hours, look for white taproot. Do not disturb.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Has the seed cracked open?",
            "Is the taproot visible and white?",
            "Is the coco properly buffered (CalMag soaked)?",
            "Is the coco/perlite mix prepared?",
            "Temperature at 75-80°F?",
        ],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Too cold, too wet, or bad seed",
                "solution": "Ensure 75-80°F. Starter medium moist not soaking. Try different seed after 7 days.",
            },
            {
                "issue": "Coco not buffered",
                "cause": "Skipped or rushed CalMag pre-soak",
                "solution": "Coco MUST be buffered. Unbuffered coco will steal calcium from every feeding, causing persistent deficiency that looks like every other problem. Buffer before ANY plant touches the coco.",
            },
        ],
        "training": [],
        "transition_signals": ["Taproot visible", "Sprout emerging", "Cotyledon leaves visible"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Start seeds indoors. Outdoor coco dries unpredictably."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always germinate indoors.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse germination: heat mat + humidity dome. Temp swings may slow germination."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Heat mat recommended.",
            },
        },
    },
    # ── 2. SEEDLING ──────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "First true leaves develop. Seedling is in solo cup with buffered coco/perlite. Begin very light fertigation — every watering includes nutrients in coco (never plain water). One feeding per day is enough. Water in a small ring around the stem, not the entire cup — encourage roots to search outward.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 65, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 250, "target": 200},
            "light_dli": {"min": 6, "max": 16, "target": 13},
            "notes": "Gentle light. Remove humidity dome gradually over 3-5 days. Seedlings in coco dry faster than in soil — check daily.",
        },
        "medium": {
            "feed_frequency": {
                "times_per_day": 1,
                "notes": "Once per day. Water in a small ring around the stem. Feed until you see slight runoff from the bottom of the solo cup.",
            },
            "runoff_ec_ratio": {
                "target_delta": 0.3,
                "notes": "Runoff EC should be within 0.3 of input EC. If higher, flush.",
            },
            "dryback_pct": {"min": 5, "max": 15, "target": 10},
            "calmag_mandatory": True,
            "pot_size": "solo cup (16 oz)",
            "coco_perlite_ratio": "70/30",
            "notes": "EVERY watering includes nutrients in coco. Never plain water (except during flush). Water until slight runoff. Lift the cup to judge weight — heavy = wet, light = time to feed. Coco in solo cups dries fast.",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "Quarter strength with CalMag in every feeding. Coco seedlings need less than soil seedlings because nutrients are delivered more efficiently.",
            "flora_micro_ml_per_gal": 0.625,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 0.3125,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root protection. Warm moist coco is a Pythium environment.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Begin fertigation",
                "description": "First feeding with quarter-strength nutrients + CalMag. Water in a ring around the stem. Feed until slight runoff from bottom.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Daily weight check",
                "description": "Lift the solo cup. Heavy = still wet, skip feeding. Light = dry, time to feed. This is the most important coco skill.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check runoff EC",
                "description": "Collect runoff and check EC. Should be within 0.3 of input. Higher = salt building up.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Remove humidity dome gradually",
                "description": "Crack dome day 1, remove for a few hours day 2, full remove by day 3-5.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "First true leaves appearing?",
            "Seedling not drooping (overwater) or wilting (underwater)?",
            "Runoff EC close to input EC?",
            "CalMag in every feeding?",
            "No brown spots on cotyledons (CalMag deficiency)?",
        ],
        "common_problems": [
            {
                "issue": "Brown spots on cotyledons/first leaves",
                "cause": "CalMag deficiency — coco is stealing calcium despite buffering",
                "solution": "Increase CalMag to 1.5 ml/gal. This is the most common coco problem. If using LED lights and/or RO water, CalMag demand is even higher.",
            },
            {
                "issue": "Overwatering (droopy dark leaves)",
                "cause": "Feeding too often or too much volume for the tiny root zone",
                "solution": "Let the solo cup dry down more between feedings. Lift to check weight. Seedlings in solo cups should dry in 1-2 days.",
            },
            {
                "issue": "Coco drying too fast (wilting daily)",
                "cause": "Solo cup too small, or environment too dry/hot",
                "solution": "Normal as roots fill the cup. Transplant to 1-gallon when roots reach the bottom. Water more frequently if needed before transplant.",
            },
        ],
        "training": [],
        "transition_signals": [
            "2-3 sets of true leaves",
            "Roots visible at bottom drain holes",
            "Cup drying in less than 24 hours",
            "Seedling 3-4 inches tall",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor coco seedlings: rain disrupts fertigation schedule. Cover or bring inside during rain."
                },
                "extra_tasks": [],
                "extra_problems": [
                    {
                        "issue": "Rain diluting nutrients",
                        "cause": "Uncovered outdoor containers",
                        "solution": "Cover containers during rain. Rain washes out nutrients and CalMag — you'll need to re-feed after rain.",
                    },
                ],
                "notes": "Outdoor coco: rain management is essential from day 1.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: excellent for coco seedlings. Watch for heat-driven drying."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse coco: monitor drying rate in warm conditions.",
            },
        },
    },
    # ── 3. EARLY VEGETATIVE ──────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Rapid growth phase. Transplant from solo cup to 1-gallon pot when roots fill the cup. Increase fertigation frequency — coco should be fed 1-2 times per day now. Vegetative steering: keep dryback low (5-10%) with frequent feedings to push green growth. CalMag at every feeding.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 60, "max": 75, "target": 65},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 300, "max": 500, "target": 400},
            "light_dli": {"min": 19, "max": 32, "target": 26},
            "notes": "Ramp up light. VPD rising. Plant growing rapidly in coco — expect faster growth than soil due to better air-to-water ratio.",
        },
        "medium": {
            "feed_frequency": {
                "times_per_day": {"min": 1, "max": 2, "target": 2},
                "notes": "2x/day as roots establish in the new pot. Feed to 10-15% runoff each time. Multiple small feedings > one big watering.",
            },
            "runoff_ec_ratio": {"target_delta": 0.3, "notes": "Runoff EC within 0.3 of input. Monitor every 3 days."},
            "dryback_pct": {"min": 5, "max": 10, "target": 8},
            "calmag_mandatory": True,
            "pot_size": "1 gallon → transplant to 3-5 gallon final pot late in this stage",
            "coco_perlite_ratio": "70/30",
            "notes": "Vegetative steering: low dryback, frequent feedings. Never let coco in 1-gallon pots dry more than 10%. Multiple small feedings are better than one large one — this keeps EC stable in the root zone. Transplant to final pot (3-5 gal) when roots fill the 1-gallon.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half strength. Plant is growing fast but root zone is still expanding. CalMag at every feeding — increase if using LED + RO water.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection in warm coco."},
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Strengthen stems. Add FIRST before other nutrients. pH down to 5.8 before adding Flora series.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Transplant to 1-gallon",
                "description": "When roots are visible at solo cup drain holes, transplant to 1-gallon pot with pre-buffered coco/perlite mix. Water in with quarter-strength nutrient + CalMag.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Increase fertigation frequency",
                "description": "Ramp to 2x/day in the 1-gallon pot. Each feeding: nutrient solution to 10-15% runoff. Never plain water.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check runoff EC",
                "description": "Collect runoff from representative plants. Input EC vs runoff EC delta should be <0.3. Rising runoff EC = flush needed.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Transplant to final pot (3-5 gal)",
                "description": "When roots fill the 1-gallon (pot dries in less than a day), transplant to final 3-5 gallon fabric pot. Pre-wet the coco in the new pot with CalMag solution.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Begin training",
                "description": "Start LST and/or topping once plant has 4-5 nodes. Coco plants recover from training quickly.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Rapid new growth visible?",
            "Roots expanding into new pot?",
            "Runoff EC within 0.3 of input?",
            "No CalMag deficiency signs (brown spots on new growth)?",
            "Coco not drying below target dryback?",
        ],
        "common_problems": [
            {
                "issue": "CalMag deficiency despite supplementing",
                "cause": "LED lights + RO water + coco = triple CalMag demand. Or coco wasn't fully buffered.",
                "solution": "Increase CalMag to 2.0 ml/gal. If persistent: re-buffer the coco (flush with CalMag solution at EC 1.0). LED + RO + coco is the highest CalMag demand combination.",
            },
            {
                "issue": "Salt buildup (runoff EC rising)",
                "cause": "Insufficient runoff at each feeding — salts accumulating",
                "solution": "Feed to 15-20% runoff for 2-3 days to flush salts. Then return to 10-15% runoff. Never feed without generating some runoff in coco.",
            },
            {
                "issue": "Slow growth after transplant",
                "cause": "Transplant shock or root zone too wet in oversized pot",
                "solution": "Water only around the root ball initially, not the entire pot. Roots need to grow into the new coco. Over-wetting the entire pot before roots reach it creates an anaerobic zone.",
            },
        ],
        "training": [
            {
                "technique": "LST",
                "description": "Bend and tie branches. Start at 4-5 nodes. Coco plants respond fast to training.",
                "timing": "After 4-5 nodes",
            },
            {
                "technique": "Topping",
                "description": "Cut above 4th or 5th node. Recovery is 2-4 days in coco — faster than soil.",
                "timing": "At 5-6 nodes",
            },
        ],
        "transition_signals": [
            "5-6 nodes",
            "Root ball filling 50%+ of final pot",
            "Rapid daily growth",
            "Drinking heavily (pot light within hours)",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor coco: rain events flush nutrients and disrupt EC. Feed after every rain."
                },
                "extra_tasks": [
                    {
                        "name": "Re-feed after rain",
                        "description": "Rain washes nutrients from coco. After any rain event, fertigate with normal-strength solution to restore EC.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor coco: rain is your biggest enemy.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: excellent for coco veg. Good light + protected from rain."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse is ideal for coco growing.",
            },
        },
    },
    # ── 4. LATE VEGETATIVE ───────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 7, "max": 21, "typical": 14},
        "description": "Plant reaches target size in final pot (3-5 gal). Full vegetative fertigation: 2-3 times per day, feed to runoff every time. Dryback stays low (5-10%) for maximum vegetative push. Pre-flip flush to reset root zone salts. Last chance for heavy training.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 55, "max": 70, "target": 60},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 600, "target": 500},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Full veg intensity. Plant transpiring heavily. Coco drying faster now — may need 3x/day feedings.",
        },
        "medium": {
            "feed_frequency": {
                "times_per_day": {"min": 2, "max": 3, "target": 3},
                "notes": "3x/day for vigorous late-veg plants. Each feeding to 10-15% runoff. First feed within 1 hour of lights on.",
            },
            "runoff_ec_ratio": {
                "target_delta": 0.3,
                "notes": "Check every 2 days. Pre-flip flush when runoff EC delta exceeds 0.3 persistently.",
            },
            "dryback_pct": {"min": 5, "max": 10, "target": 7},
            "calmag_mandatory": True,
            "pot_size": "3-5 gallon final pot (fabric pot preferred)",
            "coco_perlite_ratio": "70/30",
            "notes": "Maximum vegetative fertigation. Low dryback, frequent feedings. Plants in coco drink heavily in late veg — if pots are light within 6-8 hours, add another feeding. Pre-flip flush: run plain pH'd water + CalMag (no base nutrients) at 3x pot volume to reset salts before flower.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Three-quarter strength. Heavy nitrogen for veg growth. CalMag at every feeding.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 1.875,
            "flora_bloom_ml_per_gal": 0.9375,
            "calmag_ml_per_gal": 2.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection."},
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 1.0,
                    "purpose": "Stem strength for flower weight. Add FIRST.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Ramp to 3x/day fertigation",
                "description": "Three feedings per day: within 1 hour of lights on, midday, and 2-3 hours before lights off. Each to 10-15% runoff.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Runoff EC monitoring",
                "description": "Check every 2 days. Delta should be <0.3. Climbing runoff EC = salt accumulation.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Pre-flip flush",
                "description": "2-3 days before flipping to 12/12: run plain pH'd water + CalMag (1 ml/gal, no base nutrients) through pots at 3x pot volume. This resets root zone salt load.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Final training",
                "description": "Complete topping, LST, SCROG net filling. No heavy training after flip.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Canopy management",
                "description": "Defoliate lower growth. Level the canopy. Lollipop lower 1/3.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Plant at target size (50-66% of final)?",
            "Runoff EC delta <0.3?",
            "Canopy even and filled?",
            "No nutrient deficiencies?",
            "Root zone flushed before flip?",
        ],
        "common_problems": [
            {
                "issue": "Runoff EC climbing despite good input",
                "cause": "Salt accumulation from weeks of feeding",
                "solution": "Flush with plain water + CalMag at 3x pot volume. Normal in coco — needs periodic flushes. Increase runoff target to 20% temporarily.",
            },
            {
                "issue": "Plant too tall for space",
                "cause": "Vegged too long — coco grows fast",
                "solution": "Flip now. Supercrop tall branches. Plan shorter veg next time.",
            },
            {
                "issue": "Roots circling at pot bottom",
                "cause": "Root-bound in plastic pot",
                "solution": "Use fabric pots for air pruning. If already in plastic: transplant to larger pot or accept slightly constrained growth.",
            },
        ],
        "training": [
            {
                "technique": "SCROG net",
                "description": "Install screen. Weave branches. Fill 70-80% before flip.",
                "timing": "1-2 weeks before flip",
            },
            {
                "technique": "Lollipop / defoliate",
                "description": "Remove lower 1/3 of growth.",
                "timing": "3-5 days before flip",
            },
        ],
        "transition_signals": [
            "Plant at 50-66% of target height",
            "Canopy filled",
            "Pre-flip flush complete",
            "Drinking heavily",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: natural photoperiod triggers flip. No manual control unless using light dep."
                },
                "extra_tasks": [
                    {
                        "name": "Monitor daylight hours",
                        "description": "Flower triggers when daylight drops below ~14 hours. Know your local sunset times.",
                        "interval_days": 7,
                        "priority": "medium",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor coco: photoperiod controls the flip.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: light dep gives flip control."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: light dep recommended for coco.",
            },
        },
    },
    # ── 5. TRANSITION ────────────────────────────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Flipped to 12/12. Explosive stretch — plant may double in height. Maintain high fertigation frequency (3-4x/day) to support explosive growth. Begin transitioning nutrient ratio from veg to bloom. CalMag demand peaks during stretch (rapid cell wall construction). Begin increasing dryback slightly as you transition toward generative steering.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 65, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 700, "target": 600},
            "light_dli": {"min": 22, "max": 30, "target": 26},
            "notes": "Flip to 12/12. DIF of 10°F helps control stretch. Humidity dropping toward flower targets.",
        },
        "medium": {
            "feed_frequency": {
                "times_per_day": {"min": 3, "max": 4, "target": 4},
                "notes": "4x/day during stretch. Plant is growing explosively and drinking heavily. Each feeding to 10-15% runoff.",
            },
            "runoff_ec_ratio": {
                "target_delta": 0.5,
                "notes": "Stretch is heavy-demand. Allow slightly larger delta (0.5) before flushing.",
            },
            "dryback_pct": {"min": 8, "max": 12, "target": 10},
            "calmag_mandatory": True,
            "pot_size": "3-5 gallon final pot",
            "coco_perlite_ratio": "70/30",
            "notes": "Transitioning from vegetative to generative steering. Increase dryback slightly (8-12%) while maintaining high frequency. This signals the plant to start shifting energy toward flower production. CalMag peaks during stretch — increase to 2.5-3 ml/gal.",
        },
        "nutrients": {
            "strength_pct": 85,
            "approach": "Near full strength. Transition ratio: reduce Gro, increase Bloom. CalMag at peak — stretch demands maximum calcium for rapid cell wall construction.",
            "flora_micro_ml_per_gal": 2.125,
            "flora_gro_ml_per_gal": 1.5,
            "flora_bloom_ml_per_gal": 1.5,
            "calmag_ml_per_gal": 2.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection through flower."},
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 1.0,
                    "purpose": "Support rapidly elongating stems. Add FIRST.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Flip to 12/12",
                "description": "Zero light leaks during dark period. Even brief light causes hermaphrodites.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Transition nutrient ratio",
                "description": "Shift from veg to bloom over 3-5 days. Increase CalMag to 2.5 ml/gal for stretch calcium demand.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Maintain 4x/day fertigation",
                "description": "Stretch is the highest water-demand period. 4 feedings per day, each to runoff.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor runoff EC",
                "description": "Check daily during stretch. EC swings are rapid in this high-demand period.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Manage stretch height",
                "description": "Supercrop, tuck into SCROG net. Stay on top of it daily.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check for preflowers",
                "description": "Watch for sex expression. Remove males immediately.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Stretch height manageable?",
            "Runoff EC within 0.5 of input?",
            "No hermaphrodite signs?",
            "CalMag deficiency signs during stretch?",
            "No light leaks?",
        ],
        "common_problems": [
            {
                "issue": "Calcium deficiency during stretch",
                "cause": "Rapid growth outpacing CalMag supply — extremely common in coco during stretch",
                "solution": "Increase CalMag to 3 ml/gal. Brown spots on new growth = calcium deficiency. In coco, CalMag is ALWAYS the first suspect.",
            },
            {
                "issue": "Excessive stretch",
                "cause": "Genetics or environment (too much DIF)",
                "solution": "Supercrop tall branches. Reduce day/night temp difference to 5°F. Increase light intensity.",
            },
            {
                "issue": "Salt spike during transition",
                "cause": "Heavy feeding + ratio change concentrating certain salts",
                "solution": "Flush with pH'd water + CalMag (no base nutrients) at 2x pot volume. Resume at 80% strength.",
            },
        ],
        "training": [
            {
                "technique": "Supercropping",
                "description": "Bend tall stems 90°. Coco plants recover fast — 2-3 days.",
                "timing": "First 2 weeks of stretch",
            },
            {
                "technique": "SCROG tucking",
                "description": "Tuck daily. Coco growth is aggressive.",
                "timing": "Throughout stretch",
            },
        ],
        "transition_signals": [
            "Stretch slowing",
            "Pistils at bud sites",
            "Flower sites forming",
            "Vertical growth stopping",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: natural photoperiod triggers stretch. Watch for light pollution."
                },
                "extra_tasks": [
                    {
                        "name": "Check for light pollution",
                        "description": "External light during dark period = hermaphrodites.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor coco: stretch timing follows the sun.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: light dep tarps control timing."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: light dep for flip control.",
            },
        },
    },
    # ── 6. EARLY FLOWER ──────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Stretch ended. Buds forming and fattening. Switch to full generative steering: increase dryback to 12-18%, increase EC, feed 3-5x/day. This is where coco shines — the ability to steer the plant through fertigation frequency and dryback is coco's greatest advantage over soil.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 62, "max": 70, "target": 66},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Peak light. Humidity dropping for bud rot prevention. DIF of 10-12°F for terpenes. CO2 to 1000-1200 ppm if available.",
        },
        "medium": {
            "feed_frequency": {
                "times_per_day": {"min": 3, "max": 5, "target": 4},
                "notes": "4x/day. First feed delayed 1 hour after lights on (allow morning dryback for generative push). Last feed 3 hours before lights off.",
            },
            "runoff_ec_ratio": {
                "target_delta": 0.5,
                "notes": "Higher EC feeding = faster salt buildup. Check every 2 days. Flush if delta >0.5.",
            },
            "dryback_pct": {"min": 12, "max": 18, "target": 15},
            "calmag_mandatory": True,
            "pot_size": "3-5 gallon final pot",
            "coco_perlite_ratio": "70/30",
            "notes": "GENERATIVE STEERING. Increase dryback to 12-18%. Delay first feed 1 hour after lights on. Increase EC to 2.2-2.6. The plant responds to mild drought stress by pushing energy into flowers. This is coco's greatest advantage — precise control over vegetative vs generative growth through fertigation timing and volume. Never let coco go fully dry (hydrophobic risk).",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom. Heavy PK. EC 2.2-2.6. CalMag maintained at every feeding.",
            "flora_micro_ml_per_gal": 2.5,
            "flora_gro_ml_per_gal": 1.0,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 2.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection."},
                {"name": "Liquid Kool Bloom", "dose_ml_per_gal": 1.25, "purpose": "PK booster for early flower."},
            ],
        },
        "tasks": [
            {
                "name": "Switch to generative steering",
                "description": "Delay first fertigation to 1 hour after lights on. Increase dryback target to 12-18%. Increase EC. This pushes energy into flowers.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor runoff EC every 2 days",
                "description": "High EC = fast salt buildup. Flush immediately if runoff EC exceeds input by >0.5.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Remove fan leaves blocking bud sites. Open canopy interior. Critical for bud rot prevention in dense coco-grown plants.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for bud rot / PM",
                "description": "Inspect flowers every 2 days. Dense coco-grown buds are susceptible.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Flush every 10-14 days",
                "description": "Run plain pH'd water + CalMag at 2-3x pot volume to reset salts. Resume normal feeding next irrigation.",
                "interval_days": 14,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Buds forming at all flower sites?",
            "Runoff EC within 0.5 of input?",
            "No bud rot or PM?",
            "Dryback hitting generative targets (12-18%)?",
            "No nutrient burn (leaf tip browning)?",
            "CalMag maintained in every feeding?",
        ],
        "common_problems": [
            {
                "issue": "Nutrient burn (crispy leaf tips)",
                "cause": "EC too high for this cultivar, or salt accumulation",
                "solution": "Reduce EC by 0.2-0.4. Flush. Resume at lower strength. Coco delivers nutrients efficiently — less is often more.",
            },
            {
                "issue": "Buds airy/foxtailing",
                "cause": "Still steering vegetative — dryback too low, EC too low",
                "solution": "Increase dryback to 15-18%. Increase EC. Delay first feed. More aggressive generative steering.",
            },
            {
                "issue": "Coco going hydrophobic (water sitting on top)",
                "cause": "Coco dried out completely at some point",
                "solution": "Add a drop of wetting agent (yucca extract). Water slowly from multiple angles. Once coco goes hydrophobic, it takes 3-5 slow waterings to fully re-wet. PREVENTION: never let coco dry completely.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation",
                "description": "Remove blocking fan leaves. One session at start of early flower. Max 20% of leaves at once.",
                "timing": "Day 1-3 of early flower",
            },
            {
                "technique": "Lollipopping",
                "description": "Remove growth below SCROG net or lower 1/3.",
                "timing": "First week of early flower",
            },
        ],
        "transition_signals": [
            "Buds fattening daily",
            "Pistils thickening",
            "Trichomes appearing",
            "Strong flower aroma",
            "Stretch stopped",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor coco flower: rain during flower is dangerous — dilutes nutrients, promotes bud rot. Cover containers."
                },
                "extra_tasks": [
                    {
                        "name": "Cover containers during rain",
                        "description": "Rain washes nutrients from coco AND promotes bud rot. Cover or move containers under shelter during rain events.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Rain during flower",
                        "cause": "Unprotected outdoor containers",
                        "solution": "Cover containers. Re-feed after rain to restore EC. Shake plants to remove moisture from buds. Defoliate for airflow.",
                    },
                ],
                "notes": "Outdoor coco flower: rain management is critical.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: protected from rain, excellent for coco flower. Manage humidity."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: ideal for coco flower if humidity is controlled.",
            },
        },
    },
    # ── 7. MID FLOWER ────────────────────────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Peak Bloom)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Peak bud development. Maximum generative steering: highest dryback (15-22%), highest EC (2.4-2.8), 4-5 feedings per day. Coco delivers nutrients efficiently so yields can match or exceed hydro. Flush every 7-10 days to prevent salt lockout at these high EC levels.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 78, "target": 76},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 40, "max": 50, "target": 45},
            "vpd_kpa": {"min": 1.4, "max": 1.6, "target": 1.5},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
            "notes": "Peak light. Humidity under 50%. DIF 12°F+ for terpenes. CO2 at 1200-1500 ppm if supplementing.",
        },
        "medium": {
            "feed_frequency": {
                "times_per_day": {"min": 4, "max": 5, "target": 4},
                "notes": "4-5x/day. Delay first feed 1-2 hours after lights on for maximum morning dryback. Last feed 3-4 hours before lights off.",
            },
            "runoff_ec_ratio": {
                "target_delta": 0.5,
                "notes": "At peak EC, salt buildup is rapid. Flush if delta exceeds 0.5. Check every 2 days.",
            },
            "dryback_pct": {"min": 15, "max": 22, "target": 18},
            "calmag_mandatory": True,
            "pot_size": "3-5 gallon final pot",
            "coco_perlite_ratio": "70/30",
            "notes": "PEAK GENERATIVE STEERING. Maximum dryback (15-22%), highest EC (2.4-2.8), delayed first feed. Every calorie goes to bud production. Flush every 7-10 days — at these EC levels, salts accumulate fast. Never let coco go completely dry — hydrophobic coco during peak flower is catastrophic.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom. Peak PK. EC 2.4-2.8. CalMag at every feeding.",
            "flora_micro_ml_per_gal": 2.5,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 2.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection."},
                {
                    "name": "Liquid Kool Bloom",
                    "dose_ml_per_gal": 2.5,
                    "purpose": "PK booster at peak. Drives bud density.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Peak generative steering",
                "description": "Dryback 15-22%, EC 2.4-2.8, first feed delayed 1-2 hours. Monitor plant response daily.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Flush every 7-10 days",
                "description": "Run plain pH'd water + CalMag (1 ml/gal) at 3x pot volume. Reset salt accumulation. Resume normal feeding next irrigation.",
                "interval_days": 10,
                "priority": "high",
            },
            {
                "name": "Runoff EC monitoring",
                "description": "At peak EC, check every 2 days. Delta >0.5 = emergency flush.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Daily bud inspection",
                "description": "Dense coco-grown buds are rot targets. Pull apart large colas gently.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Support heavy branches",
                "description": "Trellis, yo-yos, or stakes. Heavy coco-grown buds snap branches.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Runoff EC within 0.5 of input?",
            "No bud rot?",
            "Trichomes developing (milky)?",
            "Dryback hitting 15-22% targets?",
            "No salt lockout symptoms?",
            "Heavy branches supported?",
        ],
        "common_problems": [
            {
                "issue": "Salt lockout (multiple deficiency symptoms)",
                "cause": "EC too high + insufficient flushing",
                "solution": "Emergency flush: 3-5x pot volume plain water + CalMag. Resume at 80% previous EC. More frequent flushes.",
            },
            {
                "issue": "Coco going hydrophobic mid-flower",
                "cause": "Dryback went too far — coco dried completely",
                "solution": "EMERGENCY. Add yucca extract wetting agent. Water very slowly from multiple angles. May take 3-5 slow waterings to fully re-wet. This is why you never let coco dry completely.",
            },
            {
                "issue": "Nutrient burn escalating",
                "cause": "EC too high for cultivar's tolerance",
                "solution": "Reduce EC by 0.3-0.4. Some cultivars can't handle 2.8. Better slightly lower EC than burned plants.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Buds dense and firm",
            "Trichomes mostly milky",
            "Pistils turning orange",
            "Lower fan leaves yellowing naturally",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor coco mid-flower: rain + dense buds = extreme rot risk. Shelter containers."
                },
                "extra_tasks": [
                    {
                        "name": "Shelter containers during rain",
                        "description": "Move under cover or use tarps. Rain during peak bloom destroys crops.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor: shelter is critical during mid-flower.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: dehumidification at maximum during mid-flower."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: humidity management is key.",
            },
        },
    },
    # ── 8. LATE FLOWER ───────────────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Buds ripening. Trichomes transitioning milky to amber. Reduce EC and feeding frequency. The plant is finishing — it needs less. Some fan leaf yellowing is normal and desired (nutrient fade). Begin tapering toward flush.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 78, "target": 75},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.4, "max": 1.8, "target": 1.6},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Slightly reduced light. Cooler nights bring out colors. Low humidity for rot prevention.",
        },
        "medium": {
            "feed_frequency": {
                "times_per_day": {"min": 3, "max": 4, "target": 3},
                "notes": "Reduce to 3x/day. Plant is drinking less. Each feeding to 10-15% runoff.",
            },
            "runoff_ec_ratio": {"target_delta": 0.5, "notes": "Continue monitoring. Drawing down salts before flush."},
            "dryback_pct": {"min": 15, "max": 20, "target": 18},
            "calmag_mandatory": True,
            "pot_size": "3-5 gallon final pot",
            "coco_perlite_ratio": "70/30",
            "notes": "Tapering. Plant is finishing. Reduce feeding frequency and EC. Fan leaf yellowing is natural — plant is consuming stored nutrients. Don't panic-feed a yellowing late-flower plant.",
        },
        "nutrients": {
            "strength_pct": 80,
            "approach": "Reducing. EC 2.0-2.4. Lower nitrogen. Maintain PK for final ripening. CalMag reduced to 1.5 ml/gal.",
            "flora_micro_ml_per_gal": 2.0,
            "flora_gro_ml_per_gal": 0.5,
            "flora_bloom_ml_per_gal": 2.0,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection through finish."},
                {"name": "Liquid Kool Bloom", "dose_ml_per_gal": 1.25, "purpose": "Reduced PK. Tapering."},
            ],
        },
        "tasks": [
            {
                "name": "Reduce EC and frequency",
                "description": "Drop EC to 2.0-2.4. Reduce to 3x/day. Plant is finishing.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Trichome checks",
                "description": "60-100x loupe on buds. Track clear → milky → amber.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Continue bud rot inspection",
                "description": "Risk remains high. Daily checks on dense colas.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Plan flush timing",
                "description": "Start flush 7-14 days before target harvest based on trichome progression.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Trichomes progressing toward amber?",
            "Fan leaves yellowing naturally?",
            "No bud rot?",
            "Plant drinking less than mid-flower?",
        ],
        "common_problems": [
            {
                "issue": "Sudden leaf death (not gradual fade)",
                "cause": "pH lockout or root problems, not natural senescence",
                "solution": "Check runoff pH. Gradual yellowing = good. Sudden browning = problem. Flush if pH is off.",
            },
            {
                "issue": "Foxtailing",
                "cause": "Light stress or heat",
                "solution": "Raise/dim lights 10-15%. Late-flower buds are light-sensitive.",
            },
        ],
        "training": [],
        "transition_signals": [
            "30-50% pistils brown",
            "Trichomes mostly milky with 5-15% amber",
            "Fan leaves dropping",
            "Drinking less",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Outdoor: monitor frost forecasts. Frost kills cannabis."},
                "extra_tasks": [
                    {
                        "name": "Monitor frost forecasts",
                        "description": "Below 32°F = death. Cover or harvest.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor: late season weather controls harvest timing.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: heating for cold nights."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: supplemental heat during cold nights.",
            },
        },
    },
    # ── 9. FLUSH ─────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush (Pre-Harvest)",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Pre-harvest flush. Run plain pH'd water + CalMag ONLY (CalMag even during flush in coco to prevent lockout from cation exchange). The exception to 'every watering is a feeding.' Goal: force the plant to consume stored nutrients. Fan leaf yellowing accelerates. Coco flushes well — salts leach efficiently with 20-30% runoff.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 76, "target": 73},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 17, "max": 30, "target": 26},
            "notes": "Reduced light. Low humidity. Cooler temps fine.",
        },
        "medium": {
            "feed_frequency": {
                "times_per_day": {"min": 2, "max": 3, "target": 2},
                "notes": "2x/day plain pH'd water + CalMag (0.5 ml/gal). Feed to 20-30% runoff to leach salts.",
            },
            "runoff_ec_ratio": {
                "target_delta": None,
                "notes": "Monitor runoff EC — flush is complete when runoff EC drops below 0.3-0.5.",
            },
            "dryback_pct": {"min": 15, "max": 25, "target": 20},
            "calmag_mandatory": True,
            "pot_size": "3-5 gallon final pot",
            "coco_perlite_ratio": "70/30",
            "notes": "COCO FLUSH RULE: plain water + minimal CalMag (0.5 ml/gal). Even during flush, coco's cation exchange steals CalMag. Without it, you get lockout symptoms during flush that look like deficiency and confuse growers. High runoff (20-30%) to leach salts. Flush is complete when runoff EC drops below 0.5.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Plain pH'd water + CalMag only (0.5 ml/gal). No base nutrients. The CalMag during flush is unique to coco — it prevents cation exchange lockout.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0.5,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Switch to flush solution",
                "description": "Plain pH'd water (5.8-6.0) + CalMag (0.5 ml/gal). NO base nutrients. This is the one exception to 'always feed in coco.'",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor runoff EC daily",
                "description": "Collect runoff. Flush is working when EC drops below 0.5. Coco flushes efficiently — usually done in 7-10 days.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Trichome checks daily",
                "description": "Harvest window approaching. 70-80% milky + 10-20% amber = peak.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Continue bud rot inspection",
                "description": "Plant defenses weakened during flush. Daily checks.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Runoff EC dropping toward 0.3-0.5?",
            "Fan leaves yellowing dramatically (desired)?",
            "No bud rot?",
            "Trichomes at target ratio?",
        ],
        "common_problems": [
            {
                "issue": "Lockout symptoms during flush (brown spots, leaf death)",
                "cause": "Flushing without CalMag in coco — cation exchange strips calcium from plant tissue",
                "solution": "ADD CalMag back at 0.5 ml/gal. This is why coco flush is different — you always include minimal CalMag.",
            },
            {
                "issue": "Runoff EC not dropping",
                "cause": "Insufficient runoff volume",
                "solution": "Increase runoff to 30%+. More frequent flushes. Coco usually flushes well — if not, the salt load was extreme.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Runoff EC below 0.5",
            "Heavy fan leaf yellowing",
            "Trichomes at target ratio",
            "Buds firm and sticky",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Outdoor: rain helps flush coco. Monitor harvest window."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: rain during flush is actually helpful.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: maintain humidity control through flush."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: keep environment controlled.",
            },
        },
    },
    # ── 10. HARVEST ──────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Chop day. Cut plants, trim, hang to dry. Spent coco can be reused — flush heavily, re-buffer with CalMag, and it's good for another 2-3 grows.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Some growers give 24-48 hours darkness before chop. Harvest in morning.",
        },
        "medium": {
            "feed_frequency": 0,
            "runoff_ec_ratio": None,
            "dryback_pct": 0,
            "calmag_mandatory": False,
            "pot_size": "N/A — harvesting",
            "coco_perlite_ratio": "N/A",
            "notes": "No more feeding. After harvest: spent coco can be reused. Flush heavily with plain water + CalMag (re-buffer), remove root debris, let dry, store for next grow. Good for 2-3 reuses.",
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
                "description": "Confirm target: 70-80% milky, 10-20% amber.",
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
                "name": "Process spent coco",
                "description": "If reusing: remove root debris, flush with plain water + CalMag at high volume, let drain, store dry. If composting: add to compost pile — coco is an excellent compost amendment.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Clean equipment",
                "description": "Clean pots, saucers, reservoir, pump. Sanitize with H2O2.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Trichome ratio at target?", "No bud rot discovered during trim?"],
        "common_problems": [
            {
                "issue": "Bud rot found during trim",
                "cause": "Hidden rot in dense colas",
                "solution": "Cut away rot + 1 inch margin. Salvage clean buds.",
            },
        ],
        "training": [],
        "transition_signals": ["Plant chopped", "Material hung for drying", "Spent coco processed"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Harvest before frost."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: weather can force harvest timing.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: controlled harvest timing."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: use space for drying if possible.",
            },
        },
    },
    # ── 11. DRYING ───────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Slow controlled drying. 60°F / 60% humidity / darkness. 10-14 days ideal. Coco-grown flower dries similarly to hydro-grown — may be slightly denser than soil-grown.",
        "environment": {
            "temp_day_f": {"min": 58, "max": 65, "target": 60},
            "temp_night_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK. 60°F. 60% humidity. Gentle airflow not on buds. Hay smell = too fast.",
        },
        "medium": {
            "feed_frequency": 0,
            "runoff_ec_ratio": None,
            "dryback_pct": 0,
            "calmag_mandatory": False,
            "pot_size": "N/A",
            "coco_perlite_ratio": "N/A",
            "notes": "No coco involvement. Drying is environmental control.",
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
                "description": "Space so they don't touch. Air circulates all sides.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Maintain 60/60",
                "description": "60°F, 60% RH, dark. Monitor with hygrometer.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check drying progress",
                "description": "Bend stem — snaps = ready. Bends = keep drying.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Inspect for mold",
                "description": "Daily mold checks on dense buds.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Temp 58-65°F?", "Humidity 55-65%?", "Dark?", "No mold?", "Cannabis smell not hay?"],
        "common_problems": [
            {
                "issue": "Drying too fast",
                "cause": "Low humidity, high temp, too much airflow",
                "solution": "Raise humidity, lower temp, reduce fan speed.",
            },
            {
                "issue": "Mold during drying",
                "cause": "Dense buds + high humidity",
                "solution": "Remove moldy buds. Lower humidity to 55%. Improve airflow.",
            },
        ],
        "training": [],
        "transition_signals": ["Small stems snap", "Outer buds dry not crunchy", "7-14 days elapsed"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Dry indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always dry indoors.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Too warm/bright. Move to dark room."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Dry in separate dark room.",
            },
        },
    },
    # ── 12. CURING ───────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Slow cure in mason jars. Terpenes develop, harshness mellows. Minimum 2 weeks, ideal 4-8 weeks. Coco-grown flower cures identically to other methods.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "In-jar: 58-62% RH (Boveda 62). Dark, cool storage. Light degrades THC.",
        },
        "medium": {
            "feed_frequency": 0,
            "runoff_ec_ratio": None,
            "dryback_pct": 0,
            "calmag_mandatory": False,
            "pot_size": "N/A",
            "coco_perlite_ratio": "N/A",
            "notes": "No coco involvement. Post-harvest processing.",
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
                "description": "Trim sugar leaves. Jars 75% full, not packed.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Burp jars",
                "description": "2-3x/day first week, 1x/day second week. Exchange air, release moisture.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Add Boveda packs",
                "description": "Boveda 62%, 1 per oz.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Reduce burping",
                "description": "Every 2-3 days after 2 weeks. Weekly after 4 weeks.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Monitor for mold",
                "description": "Check when burping. Remove affected buds immediately.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["In-jar 58-62% RH?", "No mold/ammonia?", "Improving smell?", "Dark cool storage?"],
        "common_problems": [
            {"issue": "Ammonia smell", "cause": "Too wet when jarred", "solution": "Remove, dry 12-24 hours, rejar."},
            {"issue": "Too dry", "cause": "Over-dried or over-burped", "solution": "Boveda 62 pack to rehydrate."},
            {
                "issue": "Mold in jars",
                "cause": "Too wet when jarred",
                "solution": "Discard moldy buds. Dry rest 12 hours. Rejar.",
            },
        ],
        "training": [],
        "transition_signals": ["Rich complex aroma", "Smooth smoke", "Slight stickiness", "Stable 58-62% RH in jar"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Same curing process. Store indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Cure identically.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Cure indoors, not greenhouse."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Cure in stable indoor space.",
            },
        },
    },
    # ── 13. STORAGE ──────────────────────────────────────────────────────
    {
        "id": "storage",
        "name": "Long-Term Storage",
        "order": 13,
        "duration_days": {"min": 30, "max": 365, "typical": 180},
        "description": "Post-cure long-term storage. Coco-grown flower cures and stores exceptionally well due to clean root zone during growth. Fast coco growth cycles (especially with high-frequency fertigation) produce multiple harvests per year — storage capacity planning is critical. Proper storage preserves potency and terpenes for 6-12+ months.",
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
                "description": "Home: mason jars with Boveda 58-62%. Commercial: nitrogen-sealed grove bags, CVault, or nitrogen-flushed drums.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Label and track batches",
                "description": "Strain, harvest date, storage date, weight, batch number. Commercial: seed-to-sale, FIFO rotation.",
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
                "issue": "Mold in storage",
                "cause": "Humidity above 65% or improper cure",
                "solution": "Verify 58-62% RH before sealing. Remove affected material.",
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
                "environment_overrides": {"notes": "Storage is always indoor."},
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
# EQUIPMENT — everything needed for a Coco Coir grow
# ─────────────────────────────────────────────────────────────────────────────

COCO_EQUIPMENT: list[dict] = [
    # -- Coco media --
    {
        "name": "Coco coir (pre-buffered preferred)",
        "category": "media",
        "required": True,
        "notes": "Canna Coco, Mother Earth, or equivalent. Pre-buffered brands save the CalMag soaking step. Raw bricks need full buffering. Budget: ~$15-25 per bag.",
    },
    {
        "name": "Perlite",
        "category": "media",
        "required": True,
        "notes": "Mix 30% perlite with 70% coco for ideal drainage. Coarse perlite preferred over fine.",
    },
    # -- Containers --
    {
        "name": "Solo cups (16 oz) for seedlings",
        "category": "containers",
        "required": True,
        "notes": "Drill drain holes in bottom. First home for seedlings in coco.",
    },
    {
        "name": "1-gallon pots (intermediate)",
        "category": "containers",
        "required": True,
        "notes": "Intermediate pot for early veg. Transplant from solo cup when roots fill it.",
    },
    {
        "name": "3-5 gallon fabric pots (final)",
        "category": "containers",
        "required": True,
        "notes": "Fabric pots (Smart Pots, Root Pouch) for air pruning. 3-gal for small plants/autos, 5-gal for full-size photos. Fabric pots prevent root circling.",
    },
    {
        "name": "Saucers / drip trays",
        "category": "containers",
        "required": True,
        "notes": "Catch runoff from every pot. Size to hold maximum feeding volume. Empty after feeding — don't let pots sit in runoff.",
    },
    # -- Feeding system --
    {
        "name": "Watering can or pump sprayer",
        "category": "feeding",
        "required": True,
        "notes": "For hand watering 1-20 plants. Pump sprayer makes even distribution easier.",
    },
    {
        "name": "Drip system (optional for 10+ plants)",
        "category": "feeding",
        "required": False,
        "notes": "Timer + pump + emitters for automated fertigation. Essential at scale. See drip grow type config for details.",
    },
    {
        "name": "Reservoir (opaque)",
        "category": "feeding",
        "required": True,
        "notes": "Mix nutrients in advance. Opaque to prevent algae. Size for 1-2 days of feeding.",
    },
    # -- Monitoring --
    {
        "name": "pH meter (accurate to 0.1)",
        "category": "monitoring",
        "required": True,
        "notes": "Calibrate weekly. Coco pH range: 5.8-6.2. Bluelab or Apera recommended.",
    },
    {
        "name": "EC/TDS meter",
        "category": "monitoring",
        "required": True,
        "notes": "Input AND runoff EC. The delta is your most important number.",
    },
    {
        "name": "Kitchen scale",
        "category": "monitoring",
        "required": False,
        "notes": "Weigh pots to track dryback precisely. The poor man's substrate sensor.",
    },
    {"name": "Jeweler's loupe (60-100x)", "category": "monitoring", "required": True, "notes": "Trichome inspection."},
    # -- Environment --
    {
        "name": "Grow light (LED preferred)",
        "category": "environment",
        "required": True,
        "notes": "LED lights increase CalMag demand in coco (less infrared heat = less transpiration). Account for this.",
    },
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
    {"name": "Dehumidifier", "category": "environment", "required": True, "notes": "Essential during flower."},
    # -- Nutrients --
    {
        "name": "Base nutrient system (coco-specific preferred)",
        "category": "nutrients",
        "required": True,
        "notes": "Canna Coco A+B, GH Flora Trio, or Athena. Coco-specific formulas have boosted CalMag.",
    },
    {
        "name": "CalMag supplement",
        "category": "nutrients",
        "required": True,
        "notes": "NON-NEGOTIABLE in coco. Every feeding, every time. 1-3 ml/gal depending on stage, water source, and light type.",
    },
    {"name": "pH Up/Down solutions", "category": "nutrients", "required": True, "notes": "pH 5.8-6.2 for coco."},
    {"name": "Hydroguard", "category": "nutrients", "required": True, "notes": "Root protection in warm moist coco."},
    {"name": "Silica (Armor Si)", "category": "nutrients", "required": False, "notes": "Stem strength. Add FIRST."},
    {
        "name": "PK booster (Liquid Kool Bloom)",
        "category": "nutrients",
        "required": False,
        "notes": "Flower supplement.",
    },
    {
        "name": "Yucca extract (wetting agent)",
        "category": "nutrients",
        "required": False,
        "notes": "Emergency: rewets hydrophobic coco. Preventive: improves water distribution. Thermo-stable, food-safe.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE — cheat-sheet values for daily operations
# ─────────────────────────────────────────────────────────────────────────────

COCO_QUICK_REFERENCE: dict = {
    "ph_range": {
        "min": 5.8,
        "max": 6.2,
        "sweet_spot": 5.9,
        "notes": "Coco is naturally pH-stable around 5.8-6.2. Less drift than other hydro methods.",
    },
    "ec_by_stage": {
        "germination": 0.0,
        "seedling": 0.4,
        "early_veg": 0.8,
        "late_veg": 1.4,
        "transition": 1.8,
        "early_flower": 2.4,
        "mid_flower": 2.6,
        "late_flower": 2.2,
        "flush": 0.0,
    },
    "fertigation_frequency_by_stage": {
        "description": "Coco feeding frequency ramps throughout the grow. More frequent = better.",
        "seedling": "1x/day",
        "early_veg": "1-2x/day",
        "late_veg": "2-3x/day",
        "transition": "3-4x/day",
        "early_flower": "3-5x/day",
        "mid_flower": "4-5x/day",
        "late_flower": "3-4x/day",
        "flush": "2-3x/day",
    },
    "calmag_guide": {
        "description": "CalMag is NON-NEGOTIABLE in coco. Dose depends on water source and light type.",
        "tap_water_hps": {
            "dose_ml_per_gal": "1.0-1.5",
            "notes": "Tap water has baseline minerals. HPS lights drive more transpiration.",
        },
        "tap_water_led": {
            "dose_ml_per_gal": "1.5-2.0",
            "notes": "LED = less transpiration = plant moves less CalMag through tissues. Supplement more.",
        },
        "ro_water_hps": {
            "dose_ml_per_gal": "2.0-2.5",
            "notes": "RO water has zero baseline minerals. Must supplement heavily.",
        },
        "ro_water_led": {
            "dose_ml_per_gal": "2.5-3.0",
            "notes": "Worst case: RO + LED + coco = maximum CalMag demand. Start high.",
        },
    },
    "dryback_targets": {
        "vegetative": {"dryback_pct": "5-10%", "effect": "Low dryback pushes vegetative growth."},
        "generative": {"dryback_pct": "15-22%", "effect": "High dryback pushes flower production."},
        "transition": {"dryback_pct": "8-12%", "effect": "Moderate dryback during shift."},
    },
    "coco_buffering_protocol": {
        "description": "Raw coco MUST be buffered before use. Pre-buffered brands still benefit from a rinse.",
        "step_1": "Rinse coco thoroughly with plain water to remove dust, salt, and shipping chemicals.",
        "step_2": "Soak in CalMag solution (EC 0.8, pH 5.8) for 8-24 hours.",
        "step_3": "Drain completely.",
        "step_4": "Repeat soak with fresh CalMag solution for another 8 hours.",
        "step_5": "Drain. Coco is now buffered and ready to use.",
        "why": "Coco's cation exchange sites are loaded with sodium and potassium from the ocean. Buffering replaces these with calcium and magnesium. Without buffering, the coco steals CalMag from every feeding.",
    },
    "pot_sizing_guide": {
        "solo_cup": {"volume": "16 oz", "stage": "germination → seedling", "duration": "1-2 weeks"},
        "one_gallon": {"volume": "1 gal", "stage": "early veg", "duration": "1-2 weeks"},
        "final_pot": {"volume": "3-5 gal", "stage": "late veg → harvest", "duration": "rest of grow"},
        "autoflower": {"volume": "3 gal final", "notes": "Autos don't need large pots."},
        "photo_large": {"volume": "5-7 gal", "notes": "For large photoperiod plants with long veg."},
    },
    "runoff_ec_interpretation": {
        "delta_0_to_0_3": "Healthy. Plant is consuming well.",
        "delta_0_3_to_0_5": "Watch. Salts starting to accumulate. Increase runoff % or flush soon.",
        "delta_above_0_5": "Flush now. Salt buildup beyond safe levels.",
        "runoff_lower": "Hungry plant. Increase EC.",
    },
    "coco_reuse_protocol": {
        "description": "Coco can be reused 2-3 grows with proper cleaning.",
        "step_1": "Remove root debris by hand or sieving.",
        "step_2": "Flush with plain water at 3x volume to remove old nutrients.",
        "step_3": "Re-buffer with CalMag solution (same as new coco buffering).",
        "step_4": "Optional: treat with enzyme product (Sensizym, Cannazym) to break down remaining root material.",
        "step_5": "Dry and store, or use immediately.",
    },
    "nutrient_mixing_order": "1) Silica (if using) → pH to 5.8 → 2) CalMag → 3) Flora Micro → 4) Flora Gro → 5) Flora Bloom → 6) Supplements → 7) pH adjust final",
    "golden_rules": [
        "CalMag in EVERY feeding. Non-negotiable. The #1 coco mistake is insufficient CalMag.",
        "Every watering is a feeding (except flush). Never plain water in coco.",
        "Feed to 10-20% runoff every time. Without runoff, salts accumulate unchecked.",
        "Never let coco dry completely — it becomes hydrophobic and repels water.",
        "Buffer new coco before ANY plant touches it. Raw coco steals calcium.",
        "Lift your pots. Weight = water content. The best moisture meter is your hand.",
        "Multiple small feedings > one big watering. Frequency is king in coco.",
        "Input EC vs Runoff EC delta is your #1 diagnostic. Check every 2-3 days.",
        "Coco flush still includes CalMag (0.5 ml/gal). Coco never stops exchanging cations.",
        "Fabric pots for air pruning. No root circling. Better drainage. The coco standard.",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING — categorised quick-diagnosis tables
# ─────────────────────────────────────────────────────────────────────────────

COCO_TROUBLESHOOTING: list[dict] = [
    {
        "category": "CalMag & Cation Exchange",
        "issues": [
            {
                "symptom": "Brown spots on new growth",
                "cause": "Calcium deficiency — coco's cation exchange stealing Ca",
                "fix": "Increase CalMag to 2-3 ml/gal. If using LED + RO water, go to 3 ml/gal. This is the #1 coco issue.",
            },
            {
                "symptom": "Yellowing between leaf veins (interveinal chlorosis)",
                "cause": "Magnesium deficiency — coco stealing Mg",
                "fix": "Increase CalMag. Also check pH — Mg lockout occurs above pH 6.5 in coco.",
            },
            {
                "symptom": "Persistent deficiency despite high CalMag",
                "cause": "Coco was not properly buffered before use",
                "fix": "Re-buffer: flush with CalMag solution (EC 1.0) at 5x pot volume. Let sit 8 hours. Flush again. Stubborn coco needs multiple rounds.",
            },
            {
                "symptom": "Deficiency symptoms during flush",
                "cause": "Flushing without CalMag — coco's cation exchange strips plant of Ca/Mg",
                "fix": "ALWAYS include 0.5 ml/gal CalMag during coco flush. This is unique to coco.",
            },
        ],
    },
    {
        "category": "Watering & Dryback",
        "issues": [
            {
                "symptom": "Droopy dark green leaves (overwatering)",
                "cause": "Feeding too frequently or too much volume for root zone size",
                "fix": "Reduce frequency. Smaller shots. Lift pot to check weight. In small pots (solo cup), once/day may be enough.",
            },
            {
                "symptom": "Coco repelling water (hydrophobic)",
                "cause": "Coco dried out completely — surface tension prevents reabsorption",
                "fix": "Add yucca extract wetting agent. Water very slowly from multiple angles. Multiple slow passes. NEVER let coco dry completely.",
            },
            {
                "symptom": "Runoff EC climbing steadily",
                "cause": "Salt accumulation from insufficient runoff",
                "fix": "Increase runoff to 20%. Flush with 3x pot volume. Resume at slightly lower EC. This is normal — coco needs periodic flushes.",
            },
            {
                "symptom": "Slow growth despite correct EC and pH",
                "cause": "Root zone staying too wet (overwatering) or dryback too aggressive",
                "fix": "Check dryback range. Roots need oxygen — constant saturation suffocates. Increase perlite ratio to 40% for better drainage.",
            },
        ],
    },
    {
        "category": "Feeding & Nutrients",
        "issues": [
            {
                "symptom": "Tip burn (nutrient burn)",
                "cause": "EC too high or salt accumulation",
                "fix": "Reduce EC by 0.2-0.3. Flush. Coco delivers efficiently — less is often more.",
            },
            {
                "symptom": "Pale new growth (nitrogen deficiency)",
                "cause": "EC too low, or nitrogen locked out by pH drift",
                "fix": "Check pH (should be 5.8-6.2). Increase EC. Nitrogen uptake drops above pH 6.3 in coco.",
            },
            {
                "symptom": "Purple stems and slow growth",
                "cause": "Phosphorus deficiency — often pH or temperature related",
                "fix": "Check pH (P lockout below 5.5 or above 6.5). Check root zone temp — cold roots can't absorb P. Ensure P in nutrient formula.",
            },
            {
                "symptom": "Rust spots on mid-leaves",
                "cause": "Calcium or potassium deficiency, or pH instability",
                "fix": "Check pH. Check CalMag dose. Check runoff EC — rising EC can lock out individual nutrients.",
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# FERTIGATION MANAGEMENT — Coco's core differentiator expansion
# ─────────────────────────────────────────────────────────────────────────────

COCO_FERTIGATION_MANAGEMENT: dict = {
    "high_frequency_fertigation": {
        "concept": "Coco thrives on frequent, small irrigations with nutrients in every watering. Never plain water.",
        "always_feed": True,
        "plain_water_rule": "In coco, EVERY watering should contain nutrients. Plain water causes calcium/magnesium deficiencies because coco's CEC releases bound Ca/Mg when fresh water passes through (buffering effect).",
        "frequency_by_stage": {
            "seedling": {"events_per_day": 1, "notes": "Once daily. Small container stays moist. Light feed (0.4 EC)."},
            "early_veg": {"events_per_day": "1-2", "notes": "1-2 times daily. Increasing as roots fill container."},
            "late_veg": {
                "events_per_day": "2-4",
                "notes": "Multiple daily fertigations. Roots established. Push growth.",
            },
            "flower": {"events_per_day": "3-6", "notes": "High frequency. Peak demand. Smaller shot sizes."},
            "late_flower": {
                "events_per_day": "3-5",
                "notes": "Slightly reduce if plant is finishing. Still never plain water.",
            },
        },
        "shot_size_calculation": {
            "method": "Target 3-5% of container volume per irrigation event.",
            "example_1_gal": "113-189 ml per shot (1 gal = 3785 ml × 3-5%)",
            "example_3_gal": "340-568 ml per shot",
            "example_5_gal": "568-946 ml per shot",
        },
        "dry_back_targets": {
            "vegetative_steering": {
                "percent": 5,
                "notes": "Keep coco wet. Minimal dry-back. Promotes stretching/growth.",
            },
            "generative_steering": {
                "percent": 10,
                "notes": "Allow more dry-back overnight. Promotes flowering/ripening.",
            },
            "danger_zone": {
                "percent": 20,
                "notes": "NEVER let coco dry more than 20%. Causes salt concentration spike and root damage.",
            },
        },
    },
    "calcium_magnesium_buffering": {
        "why_coco_needs_calmag": "Coco coir has high Cation Exchange Capacity (CEC). It naturally binds calcium and magnesium ions, making them unavailable to plants. You must 'buffer' (pre-load) the CEC sites and continuously supplement.",
        "initial_buffering_protocol": [
            "Mix CalMag solution at 150 ppm calcium (approximately 5ml/gal of most CalMag products)",
            "Soak coco in CalMag solution for 8-24 hours",
            "Drain. DO NOT rinse after buffering (you want those CEC sites loaded).",
            "This pre-loads the exchange sites so they don't steal calcium from your nutrient solution.",
        ],
        "ongoing_supplementation": {
            "dose": "Add CalMag to EVERY feeding at 1-3 ml/gal (200-400 ppm Ca target in final solution)",
            "when_to_increase": "If seeing calcium deficiency (brown spots on lower/middle leaves) despite adequate EC, increase CalMag.",
            "led_consideration": "LED lights increase calcium demand. Add 1 ml/gal extra CalMag under LEDs vs HPS.",
            "soft_water_consideration": "If using RO or soft water (<100 ppm base), use maximum CalMag (3 ml/gal). Hard water (>200 ppm) may need less.",
        },
        "calmag_products": [
            {
                "product": "Botanicare Cal-Mag Plus",
                "ca_ppm_per_ml_gal": 47,
                "mg_ppm_per_ml_gal": 15,
                "notes": "Industry standard. Contains iron.",
            },
            {
                "product": "General Hydroponics CaliMAGic",
                "ca_ppm_per_ml_gal": 54,
                "mg_ppm_per_ml_gal": 18,
                "notes": "Concentrated. Less volume needed.",
            },
            {
                "product": "Canna CalMag Agent",
                "ca_ppm_per_ml_gal": 40,
                "mg_ppm_per_ml_gal": 12,
                "notes": "Designed for coco specifically.",
            },
        ],
    },
    "coco_preparation": {
        "brick_vs_loose": {
            "brick": {
                "pros": ["Cheap", "Compact storage", "Sterile when new"],
                "cons": ["Must rehydrate", "Can be high-salt if unbuffered", "Quality varies wildly"],
            },
            "loose_bagged": {
                "pros": ["Ready to use", "Often pre-buffered", "Consistent quality"],
                "cons": ["Bulkier", "More expensive", "Check buffer date"],
            },
        },
        "washing_protocol": [
            "Place coco in large container",
            "Rinse with plain water 3-5 times until runoff EC is below 0.5",
            "This removes excess sodium and potassium salts from manufacturing",
            "THEN proceed to CalMag buffering (above)",
        ],
        "perlite_ratio": {
            "pure_coco": {
                "retention": "highest",
                "aeration": "lowest",
                "best_for": "Autopot/bottom-feed systems where drainage doesn't matter as much",
            },
            "70_30_coco_perlite": {
                "retention": "high",
                "aeration": "good",
                "best_for": "MOST grows. The gold standard ratio. High frequency fertigation.",
            },
            "50_50_coco_perlite": {
                "retention": "medium",
                "aeration": "high",
                "best_for": "Very high frequency fertigation. Fast dry-back. Aggressive crop steering.",
            },
        },
    },
    "runoff_management": {
        "target_runoff_percent": {"min": 10, "max": 20},
        "why_runoff_matters": "Runoff flushes accumulated salts from CEC sites. Without runoff, EC builds in media regardless of input EC.",
        "runoff_ec_monitoring": {
            "ideal": "Runoff EC within 0.3 of input EC. Balanced.",
            "warning": "Runoff EC 0.3-0.8 above input. Salt building. Increase runoff % next irrigation.",
            "critical": "Runoff EC >1.0 above input. Flush immediately. Multiple high-runoff irrigations until equalized.",
        },
        "flushing_protocol": [
            "Use nutrient solution at 50% strength (never plain water in coco)",
            "Irrigate until 50-80% runoff volume achieved",
            "Check runoff EC. Repeat if still high.",
            "Resume normal feeding once runoff EC within 0.3 of input",
        ],
    },
    "reuse_and_recycling": {
        "can_reuse": True,
        "max_reuses": 3,
        "reconditioning_protocol": [
            "Remove old root mass (shake/pull large roots, don't stress about fine roots)",
            "Rinse thoroughly with plain water (3-5 times, target EC < 0.5 in runoff)",
            "Re-buffer with CalMag solution (8-24h soak)",
            "Add fresh perlite to replace any that was removed/degraded (coco compresses over time)",
            "Mix in 10-20% fresh coco to restore structure",
            "Ready for next grow",
        ],
        "when_to_replace": [
            "After 3 uses (fiber breaks down, compacts)",
            "If persistent pH issues despite proper input",
            "If root disease occurred in previous grow (start fresh)",
            "If coco is visibly degraded/muddy in texture",
        ],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — the single export consumed by the API/frontend
# ─────────────────────────────────────────────────────────────────────────────

COCO_CONFIG: dict = {
    "grow_type_id": "coco_coir",
    "version": "1.0.0",
    "stages": COCO_STAGES,
    "equipment": COCO_EQUIPMENT,
    "quick_reference": COCO_QUICK_REFERENCE,
    "troubleshooting": COCO_TROUBLESHOOTING,
    "fertigation_management": COCO_FERTIGATION_MANAGEMENT,
    "total_grow_days": {"min": 98, "max": 189, "typical": 135},
}
