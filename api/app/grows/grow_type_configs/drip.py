"""Drip / Top Feed — Complete grow type configuration.

Enterprise-grade configuration for drip irrigation systems — the commercial
indoor workhorse and most common system in licensed cannabis facilities.
The defining features are **emitter management** (clog detection, uniform
distribution), **runoff monitoring** (input EC vs runoff EC delta as the
primary health indicator, 10-20% runoff target), **drain-to-waste vs
recirculating** decision, **media-dependent irrigation scheduling** (coco,
rockwool, perlite — each with different frequency, volume, and dryback
targets), and **crop steering via irrigation strategy** (generative vs
vegetative steering through shot timing and dryback %).

Drip differs fundamentally from flood/recirculating systems:
  - Nutrients are delivered ON TOP of the media, not from below
  - Runoff EC vs input EC delta is the #1 diagnostic tool
  - Media choice dramatically changes irrigation frequency and dryback targets
  - Crop steering (generative vs vegetative) is done via irrigation timing
  - Emitter clogs are the #1 failure mode — every plant must be checked
  - Drain-to-waste is simpler (no pathogen risk) but uses more water
  - Recirculating saves 30-40% water but needs UV/ozone sterilization
  - Scale ranges from 1 plant (hand watering) to 10,000+ (automated)

Supports three environment types (matching Tent.environment_type):
  - indoor  (default — full environmental control, artificial light)
  - outdoor (no climate control, natural photoperiod, weather exposure)
  - greenhouse (partial climate control, natural + supplemental light)

Base stage values target indoor/tent growing.  Each stage carries an
``environment_variants`` dict with ``outdoor`` and ``greenhouse`` keys
that contain **overrides** and **additional** tasks, problems, equipment,
and notes.  The frontend merges base + variant at render time.

Data sources:
- Precision irrigation best practices (Aroya, Grodan, Athena)
- General Hydroponics Flora Trio feeding charts
- Cannabis cultivation best practices (pH, EC, VPD, PPFD, DLI)
- Crop steering guides (Aroya, Toro)
- Emitter management and runoff analysis techniques
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in a Drip / Top Feed grow
# ─────────────────────────────────────────────────────────────────────────────

DRIP_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Seed cracks open and taproot emerges. For drip systems, start seeds in Rapid Rooters, rockwool starter cubes, or coco plugs inside a humidity dome. Seeds are NOT under drip emitters yet — germinate separately.",
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
        "medium": {
            "drip_rate_ml_min": 0,
            "runoff_pct": 0,
            "dryback_pct": 0,
            "shots_per_day": 0,
            "shot_volume_ml": 0,
            "first_shot_timing": None,
            "last_shot_timing": None,
            "drain_to_waste": True,
            "crop_steering": None,
            "media_specific": {},
            "notes": "Seeds are NOT under drip emitters yet. Germinate off-system in humidity dome.",
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
                "description": "Soak seeds 12-24 hours in plain pH 6.0 water, then place in Rapid Rooters, pre-soaked rockwool cubes, or coco plugs inside a humidity dome.",
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
                "name": "Prepare drip system",
                "description": "While seeds germinate: assemble manifold, run emitters, flush lines with plain water, verify all emitters flow evenly, check for leaks.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Prepare growing media",
                "description": "Buffer coco coir with CalMag (EC 0.8, soak 8+ hours). Pre-soak rockwool slabs in pH 5.5 water for 1 hour. Rinse perlite to remove dust.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Test emitter uniformity",
                "description": "Run all emitters into cups for 5 minutes. Measure output per emitter — should be within 10% of each other. Replace any outliers.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Has the seed cracked open?",
            "Is the taproot visible and white?",
            "Is the starter medium moist but not soaking?",
            "Temperature at 75-80°F?",
            "Are all drip lines flushed and leak-free?",
        ],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Too cold, too wet, or bad seed",
                "solution": "Ensure 75-80°F. Starter medium should be moist not soaking. Try a different seed after 7 days.",
            },
            {
                "issue": "Coco not buffered",
                "cause": "Skipped CalMag pre-soak step",
                "solution": "Coco MUST be buffered before use. Soak in CalMag solution (EC 0.8) for 8+ hours, drain, repeat. Unbuffered coco steals calcium from nutrients.",
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
                    "notes": "Start seeds indoors. Outdoor drip systems face rain dilution and temperature swings — seedlings are too fragile."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always germinate indoors.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse germination: use heat mat and humidity dome. Greenhouse temp swings may slow germination without supplemental heating."
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
        "description": "Seedling develops first true leaves. Transplant into final media and place under drip emitters. Start with very low-volume, infrequent irrigations — the root zone is tiny and overwatering is the #1 killer at this stage. Hand watering may be easier than drip for 1-10 plants.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 65, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 250, "target": 200},
            "light_dli": {"min": 6, "max": 16, "target": 13},
            "notes": "Gentle light. Remove humidity dome gradually over 3-5 days. If hand watering, water in a small ring around the stem — do NOT soak the entire container.",
        },
        "medium": {
            "drip_rate_ml_min": {"min": 10, "max": 30, "target": 20},
            "runoff_pct": {"min": 5, "max": 10, "target": 5},
            "dryback_pct": {"min": 5, "max": 15, "target": 10},
            "shots_per_day": {"min": 1, "max": 2, "target": 1},
            "shot_volume_ml": {"min": 50, "max": 150, "target": 100},
            "first_shot_timing": "1 hour after lights on",
            "last_shot_timing": "4 hours before lights off",
            "drain_to_waste": True,
            "crop_steering": "vegetative",
            "media_specific": {
                "coco": {
                    "shots_per_day": 1,
                    "shot_volume_ml": 100,
                    "dryback_pct": 10,
                    "notes": "Coco holds moisture well. 1 small shot per day. Never let coco dry completely — it becomes hydrophobic. CalMag in every feeding.",
                },
                "rockwool": {
                    "shots_per_day": 1,
                    "shot_volume_ml": 75,
                    "dryback_pct": 8,
                    "notes": "Rockwool retains heavily. 1 small shot per day. Over-irrigating rockwool drowns seedling roots. Let slab settle to 60-65% saturation before next shot.",
                },
                "perlite": {
                    "shots_per_day": 2,
                    "shot_volume_ml": 75,
                    "dryback_pct": 15,
                    "notes": "Perlite drains fast. 2 small shots per day. Roots dry quickly — monitor for wilting between irrigations.",
                },
            },
            "notes": "Tiny root zone — less is more. Water only where roots are (small ring around stem). Runoff should be minimal at this stage. Check emitter placement: drip stake should deliver water 1-2 inches from the stem, NOT directly on it.",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "Quarter strength. Seedlings are tiny. Each drip event delivers a small dose — no continuous feeding needed.",
            "flora_micro_ml_per_gal": 0.625,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 0.3125,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Protect young roots. Warm, moist media is ideal for Pythium.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Transplant into final media",
                "description": "Place seedling in starter plug into final container with chosen media (coco, rockwool slab, perlite). Position drip stake 1-2 inches from stem. Emitter should NOT drip directly on the stem.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "First drip irrigation",
                "description": "Run drip manually. Verify emitter delivers solution where roots are. Watch for runoff — at this stage, minimal or no runoff is fine.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Set irrigation timer",
                "description": "Program timer for 1-2 irrigations per day during lights-on period only. Each shot should be small (50-150ml depending on media and container size).",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check emitter flow",
                "description": "Verify every emitter is flowing. A single clogged emitter = one dead plant. This is the #1 drip system failure mode.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Monitor runoff",
                "description": "Collect runoff from saucers. Check runoff EC vs input EC. Runoff EC should be close to input EC at this stage. If runoff EC is much higher, you have salt buildup — flush.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Check media moisture",
                "description": "Lift container to gauge weight. Heavy = saturated (reduce irrigation). Light = dry (increase irrigation). With experience, weight tells you everything.",
                "interval_days": 1,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Seedlings standing upright?",
            "First true leaves appearing?",
            "Emitter delivering solution near (not on) the stem?",
            "No standing water in saucers after drain?",
            "Media drying appropriately between irrigations?",
            "Runoff EC within 0.3 of input EC?",
        ],
        "common_problems": [
            {
                "issue": "Overwatering (droopy, dark green leaves)",
                "cause": "Too many shots per day, too much volume per shot, or media staying saturated",
                "solution": "Reduce shot frequency or volume. Lift pots to check weight. If heavy, skip next irrigation. Seedlings need very little water.",
            },
            {
                "issue": "Clogged emitter — plant wilting while neighbors are fine",
                "cause": "Nutrient salt or biofilm blocking the emitter",
                "solution": "Check emitter immediately. Replace or clean (soak in pH 3.0 solution or H2O2). Every emitter check should compare flow rates.",
            },
            {
                "issue": "Stem rot at media surface",
                "cause": "Drip stake too close to stem, or media staying too wet at surface",
                "solution": "Move emitter 1-2 inches from stem. Add dry media (perlite, hydroton) on top to keep the stem-media junction dry.",
            },
            {
                "issue": "Salt crust on media surface",
                "cause": "Evaporation concentrating salts on top of media",
                "solution": "Normal in drip systems. Flush periodically (3x normal volume). If severe, top-dress with perlite to reduce evaporation.",
            },
        ],
        "training": [],
        "transition_signals": [
            "2-3 sets of true leaves",
            "Seedling 3-4 inches tall",
            "Root tips visible at container edges or bottom",
            "Sturdy stem",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor drip: rain dilutes nutrient solution and throws off runoff EC readings. Cover plants or account for rain in irrigation schedule."
                },
                "extra_tasks": [
                    {
                        "name": "Install rain cover or monitor weather",
                        "description": "Rain disrupts drip irrigation scheduling and dilutes nutrients. Cover containers or pause drip during rain.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Rain diluting nutrients",
                        "cause": "Uncovered outdoor containers",
                        "solution": "Cover containers during rain or accept that outdoor drip requires manual adjustment after rain events.",
                    },
                ],
                "notes": "Outdoor drip is viable but rain management is essential.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: higher light levels may increase transpiration, requiring more frequent irrigations than pure indoor."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Monitor dryback more closely — greenhouse light spikes can dry media faster than expected.",
            },
        },
    },
    # ── 3. EARLY VEGETATIVE ──────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Rapid root and leaf expansion. The plant is now established and drinking more — increase irrigation frequency and volume. Vegetative steering: keep dryback low, irrigate more frequently to push green growth. Begin monitoring runoff EC closely as nutrient demand rises.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 60, "max": 75, "target": 65},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 300, "max": 500, "target": 400},
            "light_dli": {"min": 19, "max": 32, "target": 26},
            "notes": "Plants are actively growing. VPD rising as humidity drops and temperature is maintained. Light intensity increasing toward full veg levels.",
        },
        "medium": {
            "drip_rate_ml_min": {"min": 20, "max": 60, "target": 40},
            "runoff_pct": {"min": 10, "max": 15, "target": 10},
            "dryback_pct": {"min": 5, "max": 12, "target": 8},
            "shots_per_day": {"min": 2, "max": 4, "target": 3},
            "shot_volume_ml": {"min": 100, "max": 300, "target": 200},
            "first_shot_timing": "1 hour after lights on",
            "last_shot_timing": "3 hours before lights off",
            "drain_to_waste": True,
            "crop_steering": "vegetative",
            "media_specific": {
                "coco": {
                    "shots_per_day": 3,
                    "shot_volume_ml": 200,
                    "dryback_pct": 8,
                    "notes": "Coco: 3 shots/day, keep dryback under 10% for vegetative steering. CalMag every feeding. Never let coco dry below 50% saturation.",
                },
                "rockwool": {
                    "shots_per_day": 2,
                    "shot_volume_ml": 150,
                    "dryback_pct": 6,
                    "notes": "Rockwool: 2 shots/day. Monitor slab weight — target 70-80% saturation. Dryback under 8% for vegetative push.",
                },
                "perlite": {
                    "shots_per_day": 4,
                    "shot_volume_ml": 150,
                    "dryback_pct": 12,
                    "notes": "Perlite: 4 shots/day. Drains fast — roots dry quickly. More frequent, smaller shots. Monitor for wilting between irrigations.",
                },
            },
            "notes": "Vegetative steering: keep the plant well-watered with low dryback to push leaf and root growth. First shot should arrive shortly after lights on to replenish overnight dryback. Last shot early enough to allow some dryback before lights off. Runoff EC should be within 0.5 of input EC.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half strength. Plant is growing fast but roots are still expanding. Ramp up gradually — watch runoff EC to gauge if the plant is eating what you feed.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 2.0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root protection. Especially important in warm media.",
                },
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Strengthen stems and cell walls. Add FIRST, before other nutrients, and pH down to 5.8 before adding Flora series.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Increase irrigation frequency",
                "description": "Ramp from 1-2 shots/day to 2-4 shots/day based on media type. Plant is drinking more — watch for faster dryback as signal to increase.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check runoff EC",
                "description": "Collect runoff from 2-3 representative plants. Compare runoff EC to input EC. Delta > 0.5 = salt accumulating, run a flush. Delta < 0 (runoff lower) = plant is hungry, increase strength.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Check every emitter",
                "description": "Walk the room and verify every single emitter is flowing. One clogged emitter = one stunted plant. This takes 2 minutes and prevents disasters.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Flush drip lines",
                "description": "Run plain pH'd water through the entire system at 3x normal volume to clear salt buildup in lines and emitters.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Monitor dryback",
                "description": "Lift containers to judge weight change between irrigations. If using substrate sensors (Teros, Aroya), monitor dryback % directly. Target low dryback for vegetative steering.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Top dress or mulch",
                "description": "Add a thin layer of perlite or hydroton on top of coco/media to reduce surface evaporation and salt crusting.",
                "interval_days": None,
                "priority": "low",
            },
        ],
        "health_checks": [
            "All emitters flowing evenly?",
            "Runoff EC within 0.5 of input EC?",
            "Rapid new leaf growth?",
            "Roots expanding to fill container?",
            "Dryback within target range for the media?",
            "No salt crust building on media surface?",
        ],
        "common_problems": [
            {
                "issue": "Runoff EC much higher than input EC",
                "cause": "Salt accumulation in media — plant not taking up all nutrients",
                "solution": "Flush with plain pH'd water at 3x container volume. Reduce nutrient strength 10-20%. Increase runoff target to 15-20% temporarily.",
            },
            {
                "issue": "Runoff EC lower than input EC",
                "cause": "Plant is eating more than you're feeding — hungry plant",
                "solution": "Increase nutrient strength 10-20%. Increase shot volume. The plant is using everything and wants more.",
            },
            {
                "issue": "Uneven growth across plants",
                "cause": "Emitter flow rate variation — some plants getting more water than others",
                "solution": "Test all emitters. Replace pressure-compensating emitters that are out of spec. Check for kinked lines or partial clogs.",
            },
            {
                "issue": "Slow growth despite good conditions",
                "cause": "Root zone too wet (overwatering) or pH drift in media",
                "solution": "Check media pH via runoff. Increase dryback slightly. Roots need oxygen — if media is constantly saturated, roots suffocate.",
            },
        ],
        "training": [
            {
                "technique": "LST (low stress training)",
                "description": "Begin bending main stem and branches to create an even canopy. Start when plant has 4-5 nodes. Tie down branches with plant wire or clips.",
                "timing": "After 4-5 nodes",
            },
            {
                "technique": "Topping",
                "description": "Cut the main stem above the 4th or 5th node to create two main colas. Do this once, early in veg. Let the plant recover 3-5 days before further training.",
                "timing": "At 5-6 nodes, if desired",
            },
        ],
        "transition_signals": [
            "5-6 nodes of growth",
            "Vigorous daily growth visible",
            "Root ball filling 50%+ of container",
            "Stems thickening",
            "Drinking noticeably more water each day",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: natural light provides excellent DLI in summer. Irrigation must account for rain and ambient temperature. Hot days = more frequent irrigations."
                },
                "extra_tasks": [
                    {
                        "name": "Adjust irrigation for weather",
                        "description": "Hot/dry days: increase shot frequency. Rainy days: reduce or skip irrigations. Monitor media weight daily.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Media drying too fast in heat",
                        "cause": "High ambient temperature and wind",
                        "solution": "Increase irrigation frequency. Mulch surface of containers. Consider shade cloth during extreme heat (>95°F).",
                    },
                ],
                "notes": "Outdoor drip: daily weather adjustment is mandatory.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: excellent light but temperature spikes can dry media faster than expected. Automate irrigation if possible."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse drip: watch for mid-day temperature spikes drying media.",
            },
        },
    },
    # ── 4. LATE VEGETATIVE ───────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 7, "max": 21, "typical": 14},
        "description": "Plant reaches target size before flip. Irrigation at full vegetative capacity — maximum frequency and volume for vegetative steering. This is the last stage to push green growth before transition. Canopy should be filled and level. Root zone management is critical now — the plant is drinking heavily.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 55, "max": 70, "target": 60},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 600, "target": 500},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Full vegetative intensity. VPD rising toward flower levels. Plant is transpiring heavily — irrigation demand is highest in late veg.",
        },
        "medium": {
            "drip_rate_ml_min": {"min": 30, "max": 80, "target": 60},
            "runoff_pct": {"min": 10, "max": 20, "target": 15},
            "dryback_pct": {"min": 5, "max": 10, "target": 7},
            "shots_per_day": {"min": 3, "max": 6, "target": 4},
            "shot_volume_ml": {"min": 150, "max": 400, "target": 300},
            "first_shot_timing": "30 min after lights on",
            "last_shot_timing": "2-3 hours before lights off",
            "drain_to_waste": True,
            "crop_steering": "vegetative",
            "media_specific": {
                "coco": {
                    "shots_per_day": 4,
                    "shot_volume_ml": 300,
                    "dryback_pct": 7,
                    "notes": "Coco: 4 shots/day. Keep dryback under 10%. CalMag every feeding (1.5-2 ml/gal). First shot within 30 min of lights on to replenish overnight dryback.",
                },
                "rockwool": {
                    "shots_per_day": 3,
                    "shot_volume_ml": 250,
                    "dryback_pct": 6,
                    "notes": "Rockwool: 3 shots/day. Monitor slab weight and EC. Target 65-75% saturation. Dryback under 8% for continued vegetative push.",
                },
                "perlite": {
                    "shots_per_day": 6,
                    "shot_volume_ml": 200,
                    "dryback_pct": 10,
                    "notes": "Perlite: 6 shots/day. Drains very fast at this size — plant is drinking heavily. Monitor constantly for wilting. Consider mixing with coco for better retention.",
                },
            },
            "notes": "Maximum vegetative irrigation. Low dryback, frequent shots, plenty of runoff (15-20%) to prevent salt accumulation. First shot should arrive shortly after lights on. Last shot early enough to allow 2-3 hours of dryback before dark period. Monitor runoff EC religiously — plant is eating everything.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Three-quarter strength. Full veg formula, heavy on nitrogen. Plant is eating aggressively — watch runoff EC to confirm uptake.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 1.875,
            "flora_bloom_ml_per_gal": 0.9375,
            "calmag_ml_per_gal": 2.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection throughout veg."},
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 1.0,
                    "purpose": "Strengthen stems for heavy flower weight. Add FIRST before other nutrients.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Full irrigation capacity",
                "description": "Ramp up to full veg irrigation schedule. 3-6 shots/day depending on media. First shot within 30 min of lights on.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Runoff EC comparison — every 2 days",
                "description": "Collect runoff from multiple plants. Input EC vs runoff EC delta is your most important number. Keep delta under 0.5. If runoff EC creeps up, flush before flipping to flower.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Pre-flip flush",
                "description": "Flush all containers 2-3 days before flipping to flower. Run plain pH'd water at 3x volume. This resets the root zone and prevents salt stress during transition.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check and clean emitters",
                "description": "Remove and inspect emitters. Soak in H2O2 (3%) or pH 3.0 citric acid solution for 30 minutes. Rinse and reinstall. Do this before flip — you don't want emitter failures during flower.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Canopy management",
                "description": "Defoliate lower growth that won't receive light. Level the canopy with LST. The goal is an even canopy ready for flower.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Final training",
                "description": "Complete all topping, LST, and SCROG net filling before flip. No heavy training after flip.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "All emitters flowing at rated output?",
            "Runoff EC within 0.5 of input EC?",
            "Plant at target size (50-66% of final desired height)?",
            "Canopy even and level?",
            "No nutrient deficiencies visible?",
            "Root zone reset (flushed) before flip?",
        ],
        "common_problems": [
            {
                "issue": "Runoff EC climbing steadily",
                "cause": "Salt accumulation in media over weeks of feeding",
                "solution": "Flush with 3x container volume of plain pH'd water. Then resume at slightly lower strength or higher runoff target (20%). This is normal — drip systems accumulate salts and need periodic flushes.",
            },
            {
                "issue": "Plant too tall (stretched) for the space",
                "cause": "Vegged too long or insufficient light intensity",
                "solution": "Flip to flower now — plant will stretch 50-100% more during flower stretch. Supercrop (bend and tape) any branches that are too tall.",
            },
            {
                "issue": "Emitter clog during heavy feeding",
                "cause": "Concentrated nutrient solution precipitating in lines or emitters",
                "solution": "Clean all emitters with H2O2 soak. Run acid flush through lines. Consider inline filter before manifold. Use pressure-compensating emitters rated for nutrient solutions.",
            },
            {
                "issue": "Media pH drifting despite correct input pH",
                "cause": "Salt accumulation changing media buffering, or coco not properly buffered initially",
                "solution": "Flush and re-buffer. Check runoff pH — if drifting above 6.5, run extra flushes. Persistent pH drift in coco usually means insufficient initial buffering.",
            },
        ],
        "training": [
            {
                "technique": "SCROG net",
                "description": "Install screen/net at canopy height. Weave branches through to create perfectly even canopy. Fill 70-80% of squares before flipping to flower.",
                "timing": "1-2 weeks before flip",
            },
            {
                "technique": "Lollipop / defoliate",
                "description": "Remove lower 1/3 of growth that won't reach the canopy. This redirects energy to top colas and improves airflow.",
                "timing": "3-5 days before flip",
            },
        ],
        "transition_signals": [
            "Plant at 50-66% of target height",
            "Canopy filled and level",
            "Roots filling container",
            "Drinking heavily (containers light within hours of last shot)",
            "Pre-flip flush complete",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: natural photoperiod change triggers flowering. No manual flip. Late veg ends when daylight drops below 14 hours."
                },
                "extra_tasks": [
                    {
                        "name": "Monitor daylight hours",
                        "description": "Outdoor flowering is triggered by photoperiod. Know your local sunset times. Late veg ends as days shorten.",
                        "interval_days": 7,
                        "priority": "medium",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor: pre-flip flush still recommended as photoperiod shifts.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: can use light deprivation to force flip, or let natural photoperiod trigger flowering."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: light dep gives control over flip timing.",
            },
        },
    },
    # ── 5. TRANSITION ────────────────────────────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Light cycle flipped to 12/12. Explosive vertical growth (stretch — plant may double in height). Irrigation strategy transitions from pure vegetative steering toward generative. Begin increasing dryback slightly while maintaining high frequency. The plant needs heavy feeding during stretch to support rapid growth. Switch nutrient ratio toward bloom.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 65, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 700, "target": 600},
            "light_dli": {"min": 22, "max": 30, "target": 26},
            "notes": "Flip to 12/12. Temperature differential (DIF) between day/night helps control stretch: keep day temps steady, drop night temps 8-10°F. VPD climbing. Humidity dropping toward flower targets.",
        },
        "medium": {
            "drip_rate_ml_min": {"min": 40, "max": 80, "target": 60},
            "runoff_pct": {"min": 10, "max": 20, "target": 15},
            "dryback_pct": {"min": 8, "max": 15, "target": 10},
            "shots_per_day": {"min": 3, "max": 6, "target": 4},
            "shot_volume_ml": {"min": 200, "max": 400, "target": 300},
            "first_shot_timing": "30 min after lights on",
            "last_shot_timing": "2 hours before lights off",
            "drain_to_waste": True,
            "crop_steering": "transitioning — vegetative early in stretch, shifting generative",
            "media_specific": {
                "coco": {
                    "shots_per_day": 4,
                    "shot_volume_ml": 300,
                    "dryback_pct": 10,
                    "notes": "Coco: maintain 4 shots/day during stretch. Increase dryback slightly (8-12%) as transition progresses. Heavy CalMag — stretch demands calcium.",
                },
                "rockwool": {
                    "shots_per_day": 3,
                    "shot_volume_ml": 250,
                    "dryback_pct": 8,
                    "notes": "Rockwool: 3 shots/day. Allow slightly more dryback (8-10%) as you transition to generative. Monitor slab EC — stretch is a heavy feeding period.",
                },
                "perlite": {
                    "shots_per_day": 5,
                    "shot_volume_ml": 200,
                    "dryback_pct": 12,
                    "notes": "Perlite: 5 shots/day during stretch. Rapid growth means rapid water demand. Don't let dryback exceed 15% or you'll stress the plant during its most critical growth phase.",
                },
            },
            "notes": "Transition irrigation: still frequent (plant is growing explosively) but begin increasing dryback to start the shift toward generative steering. The goal is to maintain enough water for stretch growth while signaling the plant to shift from vegetative to reproductive mode. Runoff EC monitoring is critical — stretch is when salt problems can spiral.",
        },
        "nutrients": {
            "strength_pct": 85,
            "approach": "Near full strength. Transition from grow-heavy to bloom-heavy ratio. Increase CalMag — stretch demands extra calcium for rapid cell wall construction.",
            "flora_micro_ml_per_gal": 2.125,
            "flora_gro_ml_per_gal": 1.5,
            "flora_bloom_ml_per_gal": 1.5,
            "calmag_ml_per_gal": 3.0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root protection. Warm flowering temps promote pathogens.",
                },
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 1.0,
                    "purpose": "Structural support for rapidly elongating stems. Add FIRST.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Flip light cycle to 12/12",
                "description": "Change timer to 12 hours on / 12 hours off. Ensure ZERO light leaks during dark period — even brief light exposure can cause hermaphrodites.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Transition nutrient ratio",
                "description": "Shift from veg ratio (high Gro) to bloom ratio (high Bloom). Increase CalMag for stretch calcium demand. Do this gradually over 3-5 days.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor runoff EC daily during stretch",
                "description": "Stretch is the highest-demand period. Runoff EC can swing rapidly. Check daily and adjust. Input EC 2.0-2.4, runoff should be within 0.5.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Manage stretch height",
                "description": "Supercrop (bend and tape) any branches growing too tall. Tuck branches into SCROG net. This is your last chance to control height.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Check for preflowers / sex",
                "description": "Watch for male pollen sacs or female pistils at nodes. Remove any males immediately. Hermaphrodite plants (male + female) should be removed unless you want seeds.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Check emitters under canopy",
                "description": "As canopy fills in, emitter access becomes harder. Verify flow now — a clogged emitter during flower development is devastating.",
                "interval_days": 3,
                "priority": "high",
            },
        ],
        "health_checks": [
            "All emitters flowing under the thickening canopy?",
            "Runoff EC stable and within 0.5 of input?",
            "Stretch height manageable?",
            "No hermaphrodite signs (pollen sacs)?",
            "Dryback increasing slightly as planned?",
            "No light leaks during dark period?",
        ],
        "common_problems": [
            {
                "issue": "Excessive stretch (plant too tall)",
                "cause": "Genetics, too much day/night temperature difference, or insufficient light intensity",
                "solution": "Supercrop tall branches (bend stem 90°, tape to support). Reduce DIF (day-night temp gap) to 5°F. Increase light intensity. Some strains just stretch — plan for it.",
            },
            {
                "issue": "Hermaphrodite flowers appearing",
                "cause": "Light leaks during dark period, stress, or genetic predisposition",
                "solution": "Fix light leaks immediately. Remove pollen sacs with tweezers. If severe, remove the plant. Hermaphrodites pollinate the room.",
            },
            {
                "issue": "Calcium deficiency during stretch",
                "cause": "Rapid growth demanding more calcium than you're supplying",
                "solution": "Increase CalMag to 3-4 ml/gal. Calcium deficiency shows as brown spots on new growth. This is extremely common during stretch.",
            },
            {
                "issue": "Salt accumulation spike",
                "cause": "Heavy feeding + reduced water uptake as plant adjusts to new light cycle",
                "solution": "Flush with plain pH'd water. Increase runoff target to 20% for a few days. Then return to normal schedule.",
            },
        ],
        "training": [
            {
                "technique": "Supercropping",
                "description": "Gently crush and bend tall stems 90° to control height. The stem heals into a knuckle that's actually stronger. Tape to support if needed.",
                "timing": "During first 2 weeks of stretch only",
            },
            {
                "technique": "SCROG tucking",
                "description": "Continue tucking new growth under the net to maintain even canopy. Stop tucking when stretch ends.",
                "timing": "Throughout stretch",
            },
        ],
        "transition_signals": [
            "Stretch slowing (vertical growth stopping)",
            "White pistils appearing at bud sites",
            "Flower sites visible at branch tips",
            "Plant focus shifting from vertical growth to bud development",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: natural photoperiod triggers stretch. No manual flip. Watch for light pollution from street lights or neighbors — can cause revegging or hermaphrodites."
                },
                "extra_tasks": [
                    {
                        "name": "Check for light pollution",
                        "description": "Any light during the dark period (street lights, porch lights, even moonlight through clouds in extreme cases) can cause hermaphrodites. Audit the grow area.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Revegging or hermaphrodites from light pollution",
                        "cause": "External light sources disrupting dark period",
                        "solution": "Block light sources, move plants, or accept the risk. Outdoor grows near buildings are high-risk for light pollution.",
                    },
                ],
                "notes": "Outdoor: stretch timing depends on latitude and photoperiod.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: light dep tarps can control photoperiod precisely. Pull tarps at the same time daily — consistency matters."
                },
                "extra_tasks": [
                    {
                        "name": "Pull light dep tarps consistently",
                        "description": "If using light deprivation, pull tarps at the same time every day. Inconsistent timing confuses the plant.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse: light dep tarps give photoperiod control.",
            },
        },
    },
    # ── 6. EARLY FLOWER ──────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Stretch has ended. Buds forming and fattening. Shift irrigation strategy to generative steering: increase dryback, reduce shot frequency slightly, and increase EC. The goal is to stress the plant mildly to push energy into flower production rather than vegetative growth. This is where crop steering separates amateur from professional results.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 62, "max": 70, "target": 66},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Peak light intensity. Humidity dropping to prevent bud rot. Day/night temperature differential (DIF) of 10-12°F promotes terpene production and tight flower structure. CO2 supplementation to 1000-1200 ppm if available.",
        },
        "medium": {
            "drip_rate_ml_min": {"min": 40, "max": 80, "target": 60},
            "runoff_pct": {"min": 10, "max": 20, "target": 15},
            "dryback_pct": {"min": 12, "max": 20, "target": 15},
            "shots_per_day": {"min": 3, "max": 5, "target": 4},
            "shot_volume_ml": {"min": 200, "max": 400, "target": 300},
            "first_shot_timing": "1 hour after lights on — allow morning dryback",
            "last_shot_timing": "3 hours before lights off",
            "drain_to_waste": True,
            "crop_steering": "generative",
            "media_specific": {
                "coco": {
                    "shots_per_day": 4,
                    "shot_volume_ml": 300,
                    "dryback_pct": 15,
                    "notes": "Coco: 4 shots/day but push dryback to 12-18% for generative steering. First shot delayed 1 hour after lights on (let the plant work for it). Higher EC (1.6-2.0) supports quality flower development. CalMag still every feed.",
                },
                "rockwool": {
                    "shots_per_day": 3,
                    "shot_volume_ml": 250,
                    "dryback_pct": 12,
                    "notes": "Rockwool: 3 shots/day. Increase dryback to 10-15%. This is precision crop steering territory — substrate sensors (Teros/Aroya) give you exact dryback data. Target slab weight dropping to 55-65% before first shot.",
                },
                "perlite": {
                    "shots_per_day": 5,
                    "shot_volume_ml": 200,
                    "dryback_pct": 18,
                    "notes": "Perlite: 5 shots/day. Perlite makes generative steering harder — it dries too fast. Consider mixing with 30% coco for better moisture retention during flower.",
                },
            },
            "notes": "GENERATIVE STEERING: The key shift. Delay first shot to 1 hour after lights on (allow morning dryback). Increase overall dryback target (12-20% depending on media). Increase EC (push harder). Reduce overnight moisture. The plant responds to mild drought stress by pushing energy into flower production. This is the difference between average and exceptional yields. Monitor closely — too much dryback = stressed plant, too little = continued vegetative growth instead of flowering.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full strength bloom formula. Heavy phosphorus and potassium for flower development. Maintain CalMag. EC 2.4-2.8 for generative push.",
            "flora_micro_ml_per_gal": 2.5,
            "flora_gro_ml_per_gal": 1.0,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 3.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection throughout flower."},
                {
                    "name": "Liquid Kool Bloom",
                    "dose_ml_per_gal": 1.25,
                    "purpose": "PK booster for early flower development. Start light, increase in mid-flower.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Shift to generative steering",
                "description": "Delay first irrigation to 1 hour after lights on. Increase dryback targets. Increase EC by 0.2-0.4. This signals the plant to push energy into flowers.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor runoff EC closely",
                "description": "Generative steering with higher EC means salt buildup risk is higher. Check runoff EC every 2 days minimum. Flush if runoff EC exceeds input by more than 0.5.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Remove large fan leaves blocking bud sites and airflow. Open up the interior of the canopy. This is critical for bud rot prevention.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for bud rot / PM",
                "description": "Inspect flowers for gray mold (botrytis) or white powdery mildew. With humidity at 45-55% and good airflow, risk is manageable. Catch problems early.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Emitter check under dense canopy",
                "description": "Canopy is now very dense. Get under it and verify every emitter is flowing. Use a flashlight. A failed emitter during flower = major yield loss from that plant.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Flush drip lines",
                "description": "Flush entire system with plain pH'd water at 3x volume. High-EC feeding during flower increases clog risk.",
                "interval_days": 10,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "All emitters flowing under dense canopy?",
            "Runoff EC within 0.5 of input EC?",
            "Buds forming at all flower sites?",
            "No bud rot or powdery mildew?",
            "Dryback hitting generative targets?",
            "No nutrient burn (leaf tip browning)?",
            "Good airflow through canopy?",
        ],
        "common_problems": [
            {
                "issue": "Nutrient burn (brown/crispy leaf tips)",
                "cause": "EC too high for the plant's tolerance, or salt accumulation in media",
                "solution": "Reduce EC by 0.2-0.4. Flush with plain pH'd water. Then resume at lower strength. Some cultivars are more sensitive than others.",
            },
            {
                "issue": "Foxtailing / stretchy buds",
                "cause": "Still steering too vegetative — dryback too low, EC too low, or temperature too high",
                "solution": "Increase dryback. Increase EC. Drop day temps to 77-78°F. More aggressive generative steering.",
            },
            {
                "issue": "Bud rot (botrytis)",
                "cause": "Humidity too high, poor airflow, or dense buds trapping moisture",
                "solution": "Remove affected buds immediately (cut 2 inches below the rot). Lower humidity to 45%. Increase airflow. Defoliate to open canopy. Prevention is everything — once rot is inside a bud, that bud is lost.",
            },
            {
                "issue": "Emitter clogged during peak flower",
                "cause": "High-EC nutrient solution precipitating in emitter",
                "solution": "Replace emitter immediately. Clean all emitters with H2O2 soak during next flush. Consider inline sediment filter. This is why spare emitters should always be on hand.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation",
                "description": "Remove fan leaves blocking bud sites and airflow. Do ONE defoliation at the start of early flower, then only remove individual leaves as needed. Never strip more than 20% of leaves at once.",
                "timing": "Day 1-3 of early flower",
            },
            {
                "technique": "Lollipopping",
                "description": "Remove all growth below the SCROG net or lower 1/3 of the plant. These sites won't produce quality buds and divert energy from top colas.",
                "timing": "First week of early flower only",
            },
        ],
        "transition_signals": [
            "Buds visibly fattening daily",
            "White pistils thickening",
            "Trichomes appearing on sugar leaves",
            "Strong flower aroma developing",
            "Stretch completely stopped",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: natural humidity fluctuations make bud rot prevention harder. Airflow is weather-dependent. Consider shade cloth on extreme heat days."
                },
                "extra_tasks": [
                    {
                        "name": "Shake plants after rain or heavy dew",
                        "description": "Water trapped inside developing buds = bud rot. Gently shake plants to remove moisture from flower sites. Improve drainage around plants.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Bud rot from rain/dew",
                        "cause": "Outdoor moisture trapped in flower sites",
                        "solution": "Shake plants after rain. Defoliate aggressively for airflow. Cover plants during extended rain if possible. Inspect daily.",
                    },
                ],
                "notes": "Outdoor flower: weather awareness is critical for bud rot prevention.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: excellent for flower quality if humidity is managed. Use dehumidifier or exhaust fans to keep humidity under 55%."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: humidity management is key during flower.",
            },
        },
    },
    # ── 7. MID FLOWER ────────────────────────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Peak Bloom)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Peak bud development. Buds fattening rapidly, trichome production accelerating. Full generative steering: maximum dryback, highest EC of the entire grow. This is where yields are made or lost. Runoff management is critical — high EC means salt buildup accelerates. Emitter reliability is non-negotiable.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 78, "target": 76},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 40, "max": 50, "target": 45},
            "vpd_kpa": {"min": 1.4, "max": 1.6, "target": 1.5},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
            "notes": "Peak light intensity. Humidity must stay under 50% — dense buds trap moisture and bud rot risk is highest now. Day/night DIF of 12°F+ enhances terpene production. CO2 at 1200-1500 ppm if supplementing.",
        },
        "medium": {
            "drip_rate_ml_min": {"min": 40, "max": 80, "target": 60},
            "runoff_pct": {"min": 15, "max": 25, "target": 20},
            "dryback_pct": {"min": 15, "max": 25, "target": 20},
            "shots_per_day": {"min": 3, "max": 5, "target": 4},
            "shot_volume_ml": {"min": 200, "max": 500, "target": 350},
            "first_shot_timing": "1-2 hours after lights on — maximum morning dryback",
            "last_shot_timing": "3-4 hours before lights off",
            "drain_to_waste": True,
            "crop_steering": "generative — maximum",
            "media_specific": {
                "coco": {
                    "shots_per_day": 4,
                    "shot_volume_ml": 350,
                    "dryback_pct": 20,
                    "notes": "Coco: 4 shots/day with 18-22% dryback. Peak generative steering. EC 2.6-3.0. First shot delayed 1-2 hours after lights on. Higher runoff (20%) to manage salt accumulation. CalMag every feed.",
                },
                "rockwool": {
                    "shots_per_day": 3,
                    "shot_volume_ml": 300,
                    "dryback_pct": 15,
                    "notes": "Rockwool: 3 shots/day. Dryback 12-18%. Substrate sensors are invaluable here — slab weight should drop to 50-55% before first shot. EC 2.6-3.0. This is precision agriculture.",
                },
                "perlite": {
                    "shots_per_day": 5,
                    "shot_volume_ml": 250,
                    "dryback_pct": 22,
                    "notes": "Perlite: 5 shots/day. Aggressive dryback is easy in perlite (too easy). Watch for over-stressing — wilting between shots means you've gone too far. Back off dryback 2-3%.",
                },
            },
            "notes": "PEAK GENERATIVE STEERING. Maximum dryback, highest EC, delayed first shot. The plant is working hardest now — every calorie goes to bud production. Runoff at 20%+ to prevent salt lockout at these high EC levels. Flush every 7-10 days. This is the highest-risk, highest-reward period of the grow.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom strength. Peak PK (phosphorus/potassium). EC 2.6-3.0. This is the heaviest feeding of the entire grow.",
            "flora_micro_ml_per_gal": 2.5,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 2.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root protection. Warm media + high nutrients = pathogen risk.",
                },
                {
                    "name": "Liquid Kool Bloom",
                    "dose_ml_per_gal": 2.5,
                    "purpose": "PK booster at peak dose. Drives bud density and weight.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Maximum generative steering",
                "description": "Delay first shot 1-2 hours after lights on. Dryback 15-25%. EC 2.6-3.0. This is aggressive — monitor plant response daily.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Runoff EC monitoring — every other day",
                "description": "At this EC, salt accumulation is rapid. Runoff EC exceeding input by >0.5 means flush immediately. Do not let it spiral.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Full system flush",
                "description": "Flush all containers with plain pH'd water at 3x volume. Reset salt accumulation. Resume feeding next irrigation.",
                "interval_days": 10,
                "priority": "high",
            },
            {
                "name": "Inspect buds for mold daily",
                "description": "Dense buds in mid-flower are prime bud rot targets. Pull apart the largest colas gently and inspect inside. Catch rot early = lose one bud. Catch it late = lose the plant.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Emitter check",
                "description": "Verify all emitters under the now-dense canopy. At this stage, losing an emitter for even 2 days means significant yield loss from that plant.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Support heavy branches",
                "description": "Buds are heavy. Use trellis nets, yo-yos, or bamboo stakes to support branches. A snapped branch at this stage is devastating.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "All emitters flowing?",
            "Runoff EC within 0.5 of input EC?",
            "No bud rot in any cola?",
            "Trichomes developing (milky/cloudy under magnification)?",
            "Dryback hitting 15-25% targets?",
            "Heavy branches supported?",
            "Humidity consistently under 50%?",
        ],
        "common_problems": [
            {
                "issue": "Salt lockout (yellowing, brown spots, stunted growth)",
                "cause": "Runoff EC far above input EC — salts have accumulated beyond plant tolerance",
                "solution": "Emergency flush: 3-5x container volume of plain pH 5.8 water. Resume at 80% previous EC. Increase runoff target to 25%. More frequent flushes.",
            },
            {
                "issue": "Bud rot inside dense colas",
                "cause": "Humidity too high, insufficient airflow inside canopy, or water splashing on buds",
                "solution": "Remove affected bud plus 2 inches below it. Lower humidity to 40%. Add oscillating fan aimed at canopy. Defoliate to improve airflow. Inspect remaining buds daily.",
            },
            {
                "issue": "Nutrient burn escalating",
                "cause": "EC too high for this cultivar's tolerance",
                "solution": "Some cultivars can't handle EC 3.0. Drop to 2.4-2.6. Better to have slightly lower EC than burnt plants. Watch leaf tips — crispy tips are the early warning.",
            },
            {
                "issue": "Drooping despite adequate irrigation",
                "cause": "Root zone issues — overwatering, root rot, or pH lockout",
                "solution": "Check runoff pH (should be 5.8-6.2). Check for root rot smell. If roots are brown/slimy, add Hydroguard and reduce irrigation frequency. Healthy roots are white.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Buds dense and firm",
            "Trichomes mostly milky under magnification",
            "Pistils starting to turn orange/brown",
            "Vertical growth completely stopped",
            "Lower fan leaves yellowing naturally",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: humidity control is impossible. Focus on airflow, defoliation, and daily bud inspection. Autumn rain is the enemy."
                },
                "extra_tasks": [
                    {
                        "name": "Shake plants after rain/dew",
                        "description": "Water in buds = rot within 48 hours. Shake every morning and after every rain. No exceptions.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Autumn rain destroying buds",
                        "cause": "Extended wet weather during peak bloom",
                        "solution": "Cover plants if possible. Harvest early if forecast shows extended rain. A slightly early harvest is better than a moldy one.",
                    },
                ],
                "notes": "Outdoor mid-flower: weather is the primary risk factor.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: dehumidification is critical. Vent during dry periods, close up during rain. Target 40-45% RH."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: dehumidifier running constantly during mid-flower.",
            },
        },
    },
    # ── 8. LATE FLOWER ───────────────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Buds ripening. Trichomes transitioning from clear to milky to amber. Begin reducing EC and irrigation frequency. The plant is finishing — it needs less food and less water. Reduce generative stress. Some growers begin a pre-flush reduction here, dropping EC gradually before the full flush stage.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 78, "target": 75},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.4, "max": 1.8, "target": 1.6},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Slightly reduced light intensity — plant is winding down. Cooler night temps (58-62°F) can bring out purple/red colors in some cultivars. Humidity at 35-45% — bud rot risk remains high with these dense, mature buds.",
        },
        "medium": {
            "drip_rate_ml_min": {"min": 30, "max": 60, "target": 50},
            "runoff_pct": {"min": 15, "max": 20, "target": 15},
            "dryback_pct": {"min": 15, "max": 25, "target": 18},
            "shots_per_day": {"min": 2, "max": 4, "target": 3},
            "shot_volume_ml": {"min": 150, "max": 350, "target": 250},
            "first_shot_timing": "1-2 hours after lights on",
            "last_shot_timing": "4 hours before lights off",
            "drain_to_waste": True,
            "crop_steering": "generative — tapering",
            "media_specific": {
                "coco": {
                    "shots_per_day": 3,
                    "shot_volume_ml": 250,
                    "dryback_pct": 18,
                    "notes": "Coco: reduce to 3 shots/day. EC dropping to 2.0-2.4. Dryback 15-20%. Plant is drinking less — overwatering now delays ripening. CalMag reduced to 1.5 ml/gal.",
                },
                "rockwool": {
                    "shots_per_day": 2,
                    "shot_volume_ml": 200,
                    "dryback_pct": 15,
                    "notes": "Rockwool: 2 shots/day. EC 2.0-2.4. Slab weight dropping as plant drinks less. Allow more time between shots. Rockwool retains — don't overwater a finishing plant.",
                },
                "perlite": {
                    "shots_per_day": 4,
                    "shot_volume_ml": 200,
                    "dryback_pct": 20,
                    "notes": "Perlite: 4 shots/day (reduced from 5). Lower volume per shot. Plant is drinking less but perlite still drains fast.",
                },
            },
            "notes": "Tapering down. The plant is finishing — reduce shot frequency, reduce EC, maintain moderate dryback. Some yellowing of fan leaves is normal and desirable (plant is consuming stored nutrients). Watch for over-drying — a completely dry root zone at this stage can cause premature death and harsh, unripened buds.",
        },
        "nutrients": {
            "strength_pct": 80,
            "approach": "Reducing. Drop EC to 2.0-2.4. Reduce nitrogen (lower Flora Micro/Gro). Maintain PK for final bud ripening. Some growers begin the taper here.",
            "flora_micro_ml_per_gal": 2.0,
            "flora_gro_ml_per_gal": 0.5,
            "flora_bloom_ml_per_gal": 2.0,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection through finish."},
                {
                    "name": "Liquid Kool Bloom",
                    "dose_ml_per_gal": 1.25,
                    "purpose": "Reduced PK booster. Tapering down from peak.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Reduce EC and irrigation",
                "description": "Drop EC to 2.0-2.4. Reduce shots per day by 1. Plant is finishing and needs less. Watch for fan leaf yellowing — that's normal nutrient fade.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Trichome checks with magnification",
                "description": "Use 60-100x jeweler's loupe or digital microscope on buds (not sugar leaves). Track trichome progression: clear → milky → amber. Harvest timing depends on this.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Continue bud rot inspection",
                "description": "Risk remains high through harvest. Daily inspection of largest colas. Squeeze gently — rot feels soft/hollow inside.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Runoff monitoring",
                "description": "Continue monitoring but less aggressively. Goal is to draw down nutrients in the media before flush stage.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Plan harvest date",
                "description": "Based on trichome progression, estimate harvest date. Plan flush stage to start 7-14 days before target harvest.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Trichomes progressing from milky toward amber?",
            "Fan leaves yellowing naturally (nutrient fade)?",
            "No bud rot or PM?",
            "Buds firm and dense?",
            "Plant drinking less than mid-flower (normal)?",
        ],
        "common_problems": [
            {
                "issue": "Premature leaf death (not gradual fade)",
                "cause": "pH lockout, over-drying, or root problems — not natural senescence",
                "solution": "Check runoff pH. Ensure irrigation hasn't been reduced too aggressively. Gradual yellowing = good. Sudden browning/crisping = problem.",
            },
            {
                "issue": "Foxtailing on tops",
                "cause": "Light stress (too close or too intense) or heat stress",
                "solution": "Raise lights or dim by 10-15%. Late flower buds are sensitive to light/heat stress. Foxtails reduce bag appeal but don't ruin potency.",
            },
            {
                "issue": "Trichomes not progressing",
                "cause": "Temperatures too warm, or genetics are slow-finishing",
                "solution": "Drop day temps to 73-75°F. Some cultivars take 10-12 weeks of flower. Check breeder's stated flowering time. Patience.",
            },
        ],
        "training": [],
        "transition_signals": [
            "30-50% of pistils orange/brown",
            "Trichomes mostly milky with some amber (5-15%)",
            "Lower fan leaves yellowing and falling",
            "Buds feel dense and firm",
            "Plant drinking noticeably less",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: late season cold snaps can damage buds. Cover plants on frost nights. Be ready to harvest early if freeze is forecast."
                },
                "extra_tasks": [
                    {
                        "name": "Monitor frost forecasts",
                        "description": "Frost kills cannabis instantly. If overnight temps will drop below 32°F, cover plants or harvest. Below 40°F, plant metabolism slows dramatically.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Early frost damage",
                        "cause": "Overnight temperatures below freezing",
                        "solution": "Harvest immediately if frost hits. Cover plants with tarps or blankets on borderline nights. Move containers indoors overnight if possible.",
                    },
                ],
                "notes": "Outdoor: late season weather dictates harvest timing.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: supplemental heating may be needed for cool nights. Target 60-65°F minimum."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: heating during cold nights enhances color development.",
            },
        },
    },
    # ── 9. FLUSH ─────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush (Pre-Harvest)",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Final flush before harvest. Run plain pH'd water only — no nutrients. The goal is to force the plant to consume stored nutrients in the leaves and media, resulting in cleaner-burning, smoother-smoking flower. The flush debate is ongoing (some studies show no difference), but industry standard practice is 7-14 days of plain water. In drip systems, flush is straightforward: replace nutrient solution with plain pH'd water.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 76, "target": 73},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 17, "max": 30, "target": 26},
            "notes": "Reduce light intensity slightly. Maintain low humidity for bud rot prevention. Cooler temps are fine — plant is finishing.",
        },
        "medium": {
            "drip_rate_ml_min": {"min": 30, "max": 60, "target": 50},
            "runoff_pct": {"min": 20, "max": 30, "target": 25},
            "dryback_pct": {"min": 15, "max": 25, "target": 20},
            "shots_per_day": {"min": 2, "max": 4, "target": 3},
            "shot_volume_ml": {"min": 200, "max": 400, "target": 300},
            "first_shot_timing": "1 hour after lights on",
            "last_shot_timing": "4 hours before lights off",
            "drain_to_waste": True,
            "crop_steering": None,
            "media_specific": {
                "coco": {
                    "shots_per_day": 3,
                    "shot_volume_ml": 300,
                    "dryback_pct": 20,
                    "notes": "Coco: 3 shots/day of plain pH 5.8-6.0 water. Higher runoff (25-30%) to leach salts. Monitor runoff EC — when it drops below 0.3-0.5, the media is flushed.",
                },
                "rockwool": {
                    "shots_per_day": 2,
                    "shot_volume_ml": 250,
                    "dryback_pct": 18,
                    "notes": "Rockwool: 2 shots/day of plain water. Rockwool holds salts stubbornly — may need extra days to flush. Monitor runoff EC and keep flushing until <0.5.",
                },
                "perlite": {
                    "shots_per_day": 3,
                    "shot_volume_ml": 250,
                    "dryback_pct": 22,
                    "notes": "Perlite: 3 shots/day. Perlite flushes fast — salts rinse out quickly. Runoff EC should drop to <0.3 within 3-5 days.",
                },
            },
            "notes": "PLAIN WATER ONLY. pH 5.8-6.0. No nutrients. High runoff (25-30%) to leach accumulated salts from media. Monitor runoff EC — flush is complete when runoff EC drops below 0.3-0.5. Fan leaf yellowing will accelerate dramatically — this is desired. The plant is consuming stored nutrients.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Plain pH'd water only. Zero nutrients. Some growers use a flushing agent (Flora Kleen, Clearex) — optional.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [
                {
                    "name": "Flora Kleen (optional)",
                    "dose_ml_per_gal": 1.5,
                    "purpose": "Chelating agent that helps dissolve salt deposits in media. Optional — plain water works fine.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Switch to plain water",
                "description": "Drain nutrient reservoir. Clean reservoir. Fill with plain pH'd water (5.8-6.0). Run through entire drip system.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Flush drip lines",
                "description": "Run clean water through all lines for 15+ minutes to clear nutrient residue from manifold and emitters.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor runoff EC",
                "description": "Check runoff EC from multiple plants daily. The flush is working when runoff EC drops below 0.5. Some media (rockwool) takes longer.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Continue trichome checks",
                "description": "Monitor trichome color daily. Harvest window is approaching: mostly milky with 10-20% amber = peak potency/flavor.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Stop flush 24-48 hours before harvest",
                "description": "Final dryback: stop all irrigation 24-48 hours before planned chop. Let the media dry down. Some believe this final stress pushes trichome production. At minimum, it makes the plant easier to handle (less water weight).",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Runoff EC dropping toward 0.3-0.5?",
            "Fan leaves yellowing/fading (desired)?",
            "Buds still healthy (no rot)?",
            "Trichomes progressing toward target ratio?",
            "No nutrient solution accidentally mixed in?",
        ],
        "common_problems": [
            {
                "issue": "Runoff EC not dropping",
                "cause": "Media heavily loaded with salts (especially rockwool)",
                "solution": "Increase runoff to 30%+. More frequent irrigations. Consider flushing agent. Rockwool can take 10-14 days to fully flush.",
            },
            {
                "issue": "Plant dying too fast (all leaves brown/crispy)",
                "cause": "Flush started too early, or plant was already stressed",
                "solution": "Check pH of runoff. If the plant has weeks of flower left, resume light feeding (EC 0.5-0.8) and flush later.",
            },
            {
                "issue": "Bud rot during flush period",
                "cause": "Continued moisture in dense buds with weakened plant defenses",
                "solution": "Harvest immediately if rot is spreading. The flush can be shortened if bud rot is the alternative. Clean flower > perfectly flushed flower with rot.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Runoff EC below 0.5",
            "Heavy fan leaf yellowing/drop",
            "Trichomes at target ratio (milky + 10-20% amber)",
            "Buds feel firm and sticky",
            "Most pistils brown/orange",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: flush by stopping nutrient feedings. If using drip, switch to plain water. Rain during flush is actually helpful — nature's flush."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: rain helps flush. Monitor harvest window closely — weather can force early harvest.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: maintain low humidity during flush. Plant defenses are weakened during this stage."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: keep humidity management active through flush.",
            },
        },
    },
    # ── 10. HARVEST ──────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Chop day. Cut plants, wet trim or whole-plant hang. The drip system is shut off. All emitters should be cleaned and stored. The most important thing: harvest at the right trichome ratio for desired effects (more milky = cerebral, more amber = sedative).",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Some growers give 24-48 hours of darkness before chop (unproven but common practice). Harvest in the morning when terpenes are theoretically highest. Room light only needed for working.",
        },
        "medium": {
            "drip_rate_ml_min": 0,
            "runoff_pct": 0,
            "dryback_pct": 0,
            "shots_per_day": 0,
            "shot_volume_ml": 0,
            "first_shot_timing": None,
            "last_shot_timing": None,
            "drain_to_waste": True,
            "crop_steering": None,
            "media_specific": {},
            "notes": "Drip system OFF. No irrigation. Clean and store all emitters, lines, and manifold after harvest.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None. System shut down.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Final trichome check",
                "description": "Confirm trichome ratio is at target before chopping. Once you cut, there's no going back. Most growers target 70-80% milky, 10-20% amber, minimal clear.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Harvest the plant",
                "description": "Cut the main stem at the base. For wet trim: remove fan leaves and trim sugar leaves close to buds now. For dry trim: remove fan leaves only, leave sugar leaves, hang whole plant or branches.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Clean drip system",
                "description": "Remove all emitters. Soak in H2O2 (3%) for 1 hour. Flush all lines with H2O2 solution then plain water. Drain completely. Store dry.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Dispose of media",
                "description": "Coco can be reused (flush heavily, re-buffer with CalMag). Rockwool is single-use (dispose). Perlite can be rinsed and reused.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Clean reservoir and equipment",
                "description": "Drain, scrub, sanitize reservoir, pumps, filters, saucers. Biofilm builds up over a grow cycle — remove it now.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Trichome ratio at target?",
            "No bud rot discovered during trim?",
            "Drip system cleaned and stored?",
            "All equipment sanitized?",
        ],
        "common_problems": [
            {
                "issue": "Bud rot discovered during trim",
                "cause": "Hidden rot inside dense colas",
                "solution": "Cut away rotted sections plus 1 inch margin. Salvage clean buds. Do not dry or cure rotted material — it contaminates everything.",
            },
            {
                "issue": "Harvested too early (mostly clear trichomes)",
                "cause": "Impatience or misreading trichomes",
                "solution": "Check trichomes on buds, NOT sugar leaves (sugar leaves mature faster). If most are still clear, potency and weight are not maximized. Lesson for next grow.",
            },
            {
                "issue": "Emitters clogged with dried nutrients after shutdown",
                "cause": "Didn't flush system before shutdown",
                "solution": "Soak in H2O2 or citric acid solution for several hours. Flush with warm water. Prevention: always flush lines before shutting down.",
            },
        ],
        "training": [],
        "transition_signals": ["Plant chopped", "All material hung or in drying room", "Drip system cleaned"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: harvest timing may be forced by weather. Have drying space prepared in advance."
                },
                "extra_tasks": [
                    {
                        "name": "Harvest before rain/frost",
                        "description": "If rain or frost is forecast, harvest early rather than risk losing the crop. Early harvest is better than no harvest.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor: weather can force harvest timing.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: controlled harvest timing. Excellent conditions for wet trimming in the greenhouse."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: use the space for drying if possible.",
            },
        },
    },
    # ── 11. DRYING ───────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Slow, controlled drying. The goal is 10-14 days in a dark room at 60°F / 60% humidity (the '60/60 rule'). Faster drying destroys terpenes and produces harsh smoke. Slower is almost always better. No drip system involvement — this is purely environmental control.",
        "environment": {
            "temp_day_f": {"min": 58, "max": 65, "target": 60},
            "temp_night_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK. 60°F. 60% humidity. Gentle airflow (not blowing directly on buds). The drying room should smell like fresh cannabis, not hay. Hay smell = drying too fast.",
        },
        "medium": {
            "drip_rate_ml_min": 0,
            "runoff_pct": 0,
            "dryback_pct": 0,
            "shots_per_day": 0,
            "shot_volume_ml": 0,
            "first_shot_timing": None,
            "last_shot_timing": None,
            "drain_to_waste": True,
            "crop_steering": None,
            "media_specific": {},
            "notes": "No drip system involvement. Drying is purely environmental control.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None. Plant is harvested.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Hang whole plants or branches",
                "description": "Hang upside down on lines or hangers. Space plants so they don't touch each other. Air must circulate around all sides.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Maintain 60/60 environment",
                "description": "60°F, 60% humidity, darkness. Use AC/heater for temp, humidifier/dehumidifier for RH. Monitor with hygrometer — buy a good one.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check drying progress",
                "description": "Bend a small stem. If it snaps cleanly (not bends), buds are ready for trim and cure. If it bends without snapping, keep drying. Outer buds will feel dry but stems should still have slight flex.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Inspect for mold during drying",
                "description": "Mold can still appear during drying, especially in dense buds. Inspect daily. Remove any moldy material immediately.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Temperature stable at 58-65°F?",
            "Humidity stable at 55-65%?",
            "No direct airflow on buds?",
            "Room completely dark?",
            "No mold visible on drying buds?",
            "Smells like cannabis (not hay)?",
        ],
        "common_problems": [
            {
                "issue": "Drying too fast (3-5 days)",
                "cause": "Humidity too low, temperature too high, or too much airflow",
                "solution": "Raise humidity to 60-65%. Lower temp to 60°F. Reduce fan speed. Whole-plant hang (no wet trim) slows drying. If buds are already dry, jar them and begin burping — moisture from stems will redistribute.",
            },
            {
                "issue": "Mold appearing on drying buds",
                "cause": "Humidity too high, insufficient airflow, or buds were wet at harvest",
                "solution": "Remove moldy buds. Lower humidity to 55%. Increase gentle airflow. Separate dense buds from each other.",
            },
            {
                "issue": "Hay smell (chlorophyll not breaking down)",
                "cause": "Drying too fast — chlorophyll trapped in buds",
                "solution": "Slow down future dries. For this batch: a long cure (4-8 weeks) can partially recover the situation. Chlorophyll breaks down slowly during cure.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Small stems snap cleanly when bent",
            "Outer buds feel dry but not crunchy",
            "Larger stems still have slight flex",
            "7-14 days elapsed at proper conditions",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: must dry indoors. Outdoor drying is too uncontrolled. Any indoor space with environmental control works."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always dry indoors regardless of grow method.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: too warm and too much light for drying. Move to a separate dark room."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Do not dry in the greenhouse — move to a controlled dark room.",
            },
        },
    },
    # ── 12. CURING ───────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Slow cure in airtight containers. This is where terpenes develop, harshness mellows, and the final product quality is determined. A proper cure is the difference between good and great cannabis. Minimum 2 weeks, ideal 4-8 weeks. Some connoisseurs cure for 6+ months.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Inside the jar: 58-62% RH (use Boveda 62 packs as insurance). Store jars in a dark, cool place. Light degrades THC into CBN. Heat accelerates degradation.",
        },
        "medium": {
            "drip_rate_ml_min": 0,
            "runoff_pct": 0,
            "dryback_pct": 0,
            "shots_per_day": 0,
            "shot_volume_ml": 0,
            "first_shot_timing": None,
            "last_shot_timing": None,
            "drain_to_waste": True,
            "crop_steering": None,
            "media_specific": {},
            "notes": "No drip system involvement. Curing is purely post-harvest processing.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None. Post-harvest.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Trim and jar buds",
                "description": "If dry-trimmed: trim sugar leaves now. Place trimmed buds loosely in mason jars (fill 75%, not packed). If wet-trimmed: buds are ready to jar directly.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Burp jars — first 2 weeks",
                "description": "Open each jar for 10-15 minutes, 2-3 times per day for the first week. Second week: once per day. This exchanges stale air and releases excess moisture. If buds feel wet when you open, leave lids off for 1 hour.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Add Boveda packs",
                "description": "Place Boveda 62% RH packs in each jar (1 per 28g/1oz). They maintain perfect humidity passively. Replace when they feel crunchy/hard.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Reduce burping after 2 weeks",
                "description": "After 2 weeks: burp once every 2-3 days. After 4 weeks: once per week. After 8 weeks: jars can be sealed long-term.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Monitor for mold during cure",
                "description": "Inspect buds when burping. Any white fuzzy mold = remove affected buds immediately and increase burping frequency for that jar.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "In-jar humidity at 58-62%?",
            "No mold or ammonia smell when opening jars?",
            "Buds gradually improving in smell and smoothness?",
            "Jars stored in darkness at 60-70°F?",
            "Boveda packs still pliable?",
        ],
        "common_problems": [
            {
                "issue": "Ammonia smell when opening jars",
                "cause": "Buds were too wet when jarred — anaerobic bacteria decomposing",
                "solution": "Immediately remove buds from jars. Spread on screen and dry for 12-24 hours. Rejar. If smell persists, the buds may be compromised.",
            },
            {
                "issue": "Buds too dry (crunchy, no stickiness)",
                "cause": "Over-dried before jarring, or too much burping",
                "solution": "Add Boveda 62 pack — it will slowly rehydrate. Reduce burping. A tortilla in the jar for a few hours is a folk remedy (adds moisture, remove promptly to avoid mold).",
            },
            {
                "issue": "Mold in jars",
                "cause": "Buds too wet when jarred, or not burping enough",
                "solution": "Remove all buds from jar. Discard moldy buds (do NOT smoke). Dry remaining buds for 12 hours. Sanitize jar. Rejar and burp more frequently.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Buds smell rich and complex (not grassy or hay-like)",
            "Smoke is smooth, not harsh",
            "Buds have slight stickiness",
            "Jar humidity stabilized at 58-62% without Boveda",
            "Minimum 2 weeks elapsed",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Same curing process regardless of grow method. Store jars indoors in a cool, dark place."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Curing is identical for all grow methods.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Do not cure in the greenhouse — temperature fluctuations degrade quality. Move to a stable indoor location."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Cure indoors, not in greenhouse.",
            },
        },
    },
    # ── 13. STORAGE ──────────────────────────────────────────────────────
    {
        "id": "storage",
        "name": "Long-Term Storage",
        "order": 13,
        "duration_days": {"min": 30, "max": 365, "typical": 180},
        "description": "Post-cure long-term storage. Drip systems — especially commercial operations with crop steering — produce premium flower that commands top dollar. Proper storage preserves that premium quality. Commercial drip farms may store hundreds of pounds across multiple strain batches. FIFO inventory and degradation tracking are essential.",
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
                "description": "Strain, harvest date, storage date, weight, batch number, crop steering profile used. Commercial: seed-to-sale, FIFO rotation.",
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
# EQUIPMENT — everything needed for a Drip / Top Feed grow
# ─────────────────────────────────────────────────────────────────────────────

DRIP_EQUIPMENT: list[dict] = [
    # -- Drip system core --
    {
        "name": "Drip emitters / drip stakes",
        "category": "drip_system",
        "required": True,
        "notes": "Pressure-compensating emitters preferred. 1 per plant minimum, 2 for larger plants. Match flow rate to media type. Spare emitters are MANDATORY — emitter failure is the #1 drip system problem.",
    },
    {
        "name": "Drip manifold / mainline tubing",
        "category": "drip_system",
        "required": True,
        "notes": "1/2 inch or 3/4 inch mainline. Size for your plant count. Include shut-off valves for sections.",
    },
    {
        "name": "Drip spaghetti lines (1/4 inch)",
        "category": "drip_system",
        "required": True,
        "notes": "Individual feed lines from manifold to each emitter. Keep runs under 6 feet to maintain even pressure.",
    },
    {
        "name": "Water pump (submersible)",
        "category": "drip_system",
        "required": True,
        "notes": "Size pump for total flow rate: sum of all emitter flow rates + 20% headroom. Submersible pump sits in the reservoir.",
    },
    {
        "name": "Irrigation timer / controller",
        "category": "drip_system",
        "required": True,
        "notes": "Digital timer with minute-resolution for shot timing. Commercial grows: use Trolmaster, Grodan, or Aroya controllers with substrate sensor integration.",
    },
    {
        "name": "Inline filter (sediment)",
        "category": "drip_system",
        "required": True,
        "notes": "100-200 mesh inline filter between pump and manifold. Catches precipitates before they clog emitters. Clean weekly. This alone prevents 80% of emitter clogs.",
    },
    {
        "name": "Pressure regulator",
        "category": "drip_system",
        "required": False,
        "notes": "Maintains consistent pressure across all emitters. Essential for larger systems (20+ emitters). Without it, emitters closest to pump get more flow.",
    },
    {
        "name": "Spare emitters (10-20% of total)",
        "category": "drip_system",
        "required": True,
        "notes": "NON-NEGOTIABLE. Emitters clog. When one fails mid-flower, you need an instant replacement. Keep spares on hand at all times.",
    },
    # -- Reservoir --
    {
        "name": "Reservoir (opaque)",
        "category": "reservoir",
        "required": True,
        "notes": "Light-proof to prevent algae. Size: minimum 2 gallons per plant. Larger is more stable. Include drain valve for easy changes.",
    },
    {
        "name": "Air pump + air stone (for reservoir)",
        "category": "reservoir",
        "required": False,
        "notes": "Keeps nutrient solution oxygenated and prevents stagnation. Especially helpful for recirculating systems.",
    },
    # -- Runoff management --
    {
        "name": "Saucers / runoff trays",
        "category": "runoff",
        "required": True,
        "notes": "Collect runoff from each plant for measurement and disposal. Size to catch maximum shot volume. For DTW: must be emptied to prevent root sitting in stagnant water.",
    },
    {
        "name": "Wet/dry vacuum or runoff pump",
        "category": "runoff",
        "required": False,
        "notes": "For larger grows: pump or vacuum runoff from saucers rather than emptying by hand. Essential at 20+ plant scale.",
    },
    {
        "name": "Runoff collection tray (sloped)",
        "category": "runoff",
        "required": False,
        "notes": "Sloped table or tray that channels all runoff to a single drain point. Commercial standard — eliminates individual saucer emptying.",
    },
    # -- Monitoring --
    {
        "name": "pH meter (accurate to 0.1)",
        "category": "monitoring",
        "required": True,
        "notes": "Calibrate weekly with 4.0 and 7.0 buffer solutions. Bluelab or Apera recommended. Cheap meters drift.",
    },
    {
        "name": "EC/TDS meter",
        "category": "monitoring",
        "required": True,
        "notes": "Measures input AND runoff EC. The input-vs-runoff EC delta is your most important diagnostic number. Calibrate monthly.",
    },
    {
        "name": "Substrate sensor (Teros, Aroya)",
        "category": "monitoring",
        "required": False,
        "notes": "Measures volumetric water content (VWC), EC, and temperature inside the media in real time. Game-changer for crop steering. Essential for precision agriculture. Expensive but transformative.",
    },
    {
        "name": "Measuring cups/syringes",
        "category": "monitoring",
        "required": True,
        "notes": "For measuring emitter output, runoff volume, and nutrient mixing. Graduated cylinders for accuracy.",
    },
    {
        "name": "Jeweler's loupe (60-100x)",
        "category": "monitoring",
        "required": True,
        "notes": "For trichome inspection during late flower/harvest. Digital USB microscope works too.",
    },
    # -- Environment --
    {
        "name": "Grow light (LED preferred)",
        "category": "environment",
        "required": True,
        "notes": "Size for your canopy. Target 30-40 watts/sq ft for LED. Must support dimming for stage-appropriate PPFD.",
    },
    {
        "name": "Exhaust fan + carbon filter",
        "category": "environment",
        "required": True,
        "notes": "Odor control and air exchange. Size for your room volume — exchange air every 1-3 minutes.",
    },
    {
        "name": "Oscillating fan(s)",
        "category": "environment",
        "required": True,
        "notes": "Airflow through canopy prevents mold and strengthens stems. Don't blow directly on buds during flower.",
    },
    {
        "name": "Temperature/humidity controller",
        "category": "environment",
        "required": True,
        "notes": "AC Infinity controller or Inkbird for automated climate control. VPD management is critical for drip efficiency.",
    },
    {
        "name": "Dehumidifier",
        "category": "environment",
        "required": True,
        "notes": "Essential during flower. Target 40-50% RH. Size for your room. Dump dehumidifier water — don't reuse.",
    },
    # -- Growing media --
    {
        "name": "Growing media (coco, rockwool, or perlite)",
        "category": "media",
        "required": True,
        "notes": "Choose ONE: Coco (most forgiving, needs CalMag, reusable). Rockwool (precision steering, single-use). Perlite (cheap, drains fast, needs frequent irrigation).",
    },
    {
        "name": "Containers / pots",
        "category": "media",
        "required": True,
        "notes": "Fabric pots (air pruning), plastic pots, or grow bags. Size: 3-5 gallon for indoor. Ensure adequate drainage holes.",
    },
    # -- Nutrients --
    {
        "name": "Base nutrient system (Flora Trio or equivalent)",
        "category": "nutrients",
        "required": True,
        "notes": "Flora Micro, Flora Gro, Flora Bloom. Or Athena Pro, Jacks 321, etc. Consistency matters more than brand.",
    },
    {
        "name": "CalMag supplement",
        "category": "nutrients",
        "required": True,
        "notes": "MANDATORY for coco coir. Recommended for all media. Coco steals calcium — CalMag in every feeding.",
    },
    {
        "name": "pH Up/Down solutions",
        "category": "nutrients",
        "required": True,
        "notes": "Maintain pH 5.8-6.2 for all media types. pH Down (phosphoric acid) used more often than pH Up.",
    },
    {
        "name": "Hydroguard (beneficial bacteria)",
        "category": "nutrients",
        "required": True,
        "notes": "Root zone protection. Especially important in warm environments and recirculating systems.",
    },
    {
        "name": "PK booster (Liquid Kool Bloom or equivalent)",
        "category": "nutrients",
        "required": False,
        "notes": "Phosphorus/potassium supplement for flower. Start light in early flower, peak in mid-flower, taper in late flower.",
    },
    {
        "name": "Hydrogen peroxide (3% or 29%)",
        "category": "maintenance",
        "required": True,
        "notes": "Emitter cleaning, line flushing, sterilization. 3% for routine cleaning, 29% food-grade diluted for heavy cleaning. Safety: 29% is caustic — handle with gloves and goggles.",
    },
    {
        "name": "Citric acid",
        "category": "maintenance",
        "required": False,
        "notes": "Alternative emitter cleaning solution. pH 3.0 soak dissolves mineral deposits. Cheap and effective.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE — cheat-sheet values for daily operations
# ─────────────────────────────────────────────────────────────────────────────

DRIP_QUICK_REFERENCE: dict = {
    "ph_range": {
        "min": 5.5,
        "max": 6.2,
        "sweet_spot": 5.8,
        "notes": "Measure input AND runoff pH. Runoff pH tells you what's happening in the root zone.",
    },
    "ec_by_stage": {
        "germination": 0.0,
        "seedling": 0.3,
        "early_veg": 0.8,
        "late_veg": 1.4,
        "transition": 1.8,
        "early_flower": 2.4,
        "mid_flower": 2.8,
        "late_flower": 2.2,
        "flush": 0.0,
    },
    "runoff_ec_interpretation": {
        "description": "Input EC vs Runoff EC is the #1 diagnostic tool in drip systems.",
        "runoff_higher_by_0_to_0_3": "Healthy — plant is consuming nutrients well.",
        "runoff_higher_by_0_3_to_0_5": "Caution — salts starting to accumulate. Increase runoff % or flush soon.",
        "runoff_higher_by_0_5_plus": "Problem — flush immediately. Salts are building up beyond plant tolerance.",
        "runoff_lower_than_input": "Hungry plant — increase EC or shot volume. Plant is consuming more than you provide.",
    },
    "dryback_targets": {
        "description": "Dryback % = how much the media dries between irrigations. Key crop steering lever.",
        "vegetative_steering": {
            "dryback_pct": "5-10%",
            "effect": "Low dryback pushes vegetative growth (leaves, stems, roots).",
        },
        "generative_steering": {
            "dryback_pct": "15-25%",
            "effect": "High dryback pushes generative growth (flowers, fruits, terpenes).",
        },
        "transition": {"dryback_pct": "10-15%", "effect": "Moderate dryback during the shift from veg to flower."},
    },
    "crop_steering_guide": {
        "description": "Crop steering uses irrigation timing and volume to control plant behavior.",
        "vegetative_strategy": {
            "first_shot": "Early (within 30 min of lights on)",
            "last_shot": "Late (2 hours before lights off)",
            "dryback": "Low (5-10%)",
            "ec": "Lower (0.8-1.4)",
            "shot_frequency": "High (many small shots)",
            "effect": "Pushes leaf growth, root expansion, vegetative vigor.",
        },
        "generative_strategy": {
            "first_shot": "Delayed (1-2 hours after lights on)",
            "last_shot": "Early (3-4 hours before lights off)",
            "dryback": "High (15-25%)",
            "ec": "Higher (1.6-2.2)",
            "shot_frequency": "Lower (fewer larger shots)",
            "effect": "Pushes flower development, terpene production, bud density.",
        },
    },
    "irrigation_timing_guide": {
        "description": "Shot timing through the day follows a P1-P2-P3 pattern.",
        "P1_morning": "First 1-2 shots replenish overnight dryback. Largest volume shots of the day.",
        "P2_midday": "Maintenance shots. Keep media at target saturation. Moderate volume.",
        "P3_afternoon": "Last shots of the day. Smaller volume. Set up overnight dryback.",
    },
    "media_comparison": {
        "coco": {
            "water_retention": "high",
            "irrigation_frequency": "moderate",
            "calmag_required": True,
            "reusable": True,
            "cost": "low",
            "best_for": "Beginners, forgiving, most popular for drip.",
        },
        "rockwool": {
            "water_retention": "very_high",
            "irrigation_frequency": "low",
            "calmag_required": False,
            "reusable": False,
            "cost": "moderate",
            "best_for": "Precision crop steering, commercial facilities.",
        },
        "perlite": {
            "water_retention": "low",
            "irrigation_frequency": "high",
            "calmag_required": False,
            "reusable": True,
            "cost": "very_low",
            "best_for": "Budget grows, fast-draining, mix with coco for best results.",
        },
    },
    "emitter_management": {
        "description": "Emitter clogs are the #1 failure mode in drip systems.",
        "check_frequency": "Every 2-3 days during active grow. Daily during flower.",
        "cleaning_method": "Soak in 3% H2O2 for 30 min, or pH 3.0 citric acid solution for 1 hour.",
        "prevention": "Inline filter (100-200 mesh). Clean filter weekly. Use pressure-compensating emitters.",
        "spare_rule": "Keep 10-20% spare emitters on hand at ALL times.",
    },
    "reservoir_change_schedule": "Every 7-10 days, or when EC drifts >0.3 from target. For DTW, top off daily, full change weekly.",
    "nutrient_mixing_order": "1) Silica (if using) → pH down to 5.8 → 2) CalMag → 3) Flora Micro → 4) Flora Gro → 5) Flora Bloom → 6) Supplements → 7) pH adjust final",
    "golden_rules": [
        "Check EVERY emitter, EVERY 2-3 days. A clogged emitter = a dead plant.",
        "Runoff EC vs Input EC is your most important number. Check it religiously.",
        "Never let coco dry completely — it becomes hydrophobic and repels water.",
        "CalMag in EVERY feeding for coco. Non-negotiable.",
        "Flush every 7-14 days to prevent salt lockout.",
        "Generative steering (high dryback + high EC) starts in early flower, not before.",
        "First shot timing matters: early = vegetative push, delayed = generative push.",
        "Spare emitters on hand at ALL times. You will need them.",
        "Inline filter before the manifold prevents 80% of emitter clogs.",
        "Lift your pots — weight tells you more than any sensor (until you have sensors).",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING — categorised quick-diagnosis tables
# ─────────────────────────────────────────────────────────────────────────────

DRIP_TROUBLESHOOTING: list[dict] = [
    {
        "category": "Emitter & Flow Problems",
        "issues": [
            {
                "symptom": "One plant wilting while others are fine",
                "cause": "Clogged emitter on that plant",
                "fix": "Check emitter immediately. Replace or clean (H2O2 soak). This is the most common drip system problem.",
            },
            {
                "symptom": "Uneven growth across plants",
                "cause": "Flow rate variation between emitters",
                "fix": "Test all emitters into cups for 5 min. Replace outliers. Use pressure-compensating emitters. Add pressure regulator for large systems.",
            },
            {
                "symptom": "Emitters clogging repeatedly",
                "cause": "No inline filter, or high-EC solution precipitating",
                "fix": "Install 100-200 mesh inline filter. Clean filter weekly. Lower nutrient concentration slightly. Use nutrient brands designed for drip systems.",
            },
            {
                "symptom": "Low flow from all emitters",
                "cause": "Pump failing, filter clogged, or airline kinked",
                "fix": "Check pump output. Clean filter. Inspect all tubing for kinks. Check pump intake for debris.",
            },
            {
                "symptom": "Emitters dripping after pump off (siphon)",
                "cause": "Gravity siphon through emitters below reservoir level",
                "fix": "Install anti-siphon valve or check valve after pump. Or raise emitters above reservoir water level.",
            },
        ],
    },
    {
        "category": "Runoff & Salt Management",
        "issues": [
            {
                "symptom": "Runoff EC much higher than input (delta > 0.5)",
                "cause": "Salt accumulation in media",
                "fix": "Flush with 3x container volume of plain pH'd water. Increase runoff target to 20-25%. Reduce nutrient strength 10-15%.",
            },
            {
                "symptom": "Runoff EC lower than input",
                "cause": "Plant consuming more nutrients than provided",
                "fix": "Increase nutrient strength. Increase shot volume. Plant is hungry — this is good news, it means rapid growth.",
            },
            {
                "symptom": "Runoff pH very different from input pH",
                "cause": "Media buffering exhausted, or salt buildup altering pH",
                "fix": "Flush media. Re-buffer coco with CalMag soak if pH is high. Check for root rot if pH is very low (<5.0).",
            },
            {
                "symptom": "White salt crust on media surface",
                "cause": "Evaporation concentrating salts at surface",
                "fix": "Normal in drip systems. Top-dress with perlite/hydroton. Increase runoff %. Flush more frequently. Surface salts don't directly harm roots but indicate overall salt load.",
            },
            {
                "symptom": "No runoff at all",
                "cause": "Shot volume too low, or media absorbing everything",
                "fix": "Increase shot volume until 10-20% runs off. Without runoff, you have no diagnostic data and salts accumulate unchecked.",
            },
        ],
    },
    {
        "category": "Crop Steering & Irrigation Timing",
        "issues": [
            {
                "symptom": "Plant still growing vegetatively during flower",
                "cause": "Dryback too low, EC too low — still steering vegetative",
                "fix": "Increase dryback to 15-20%. Increase EC. Delay first shot. Widen the gap between last shot and lights off.",
            },
            {
                "symptom": "Buds small and airy despite good genetics",
                "cause": "Insufficient generative steering, or light intensity too low",
                "fix": "Push dryback higher (20-25%). Increase EC. Check light — PPFD 700-1000 needed for dense buds. CO2 helps.",
            },
            {
                "symptom": "Plant stressed/wilting between irrigations",
                "cause": "Dryback too aggressive, or media dried too much overnight",
                "fix": "Reduce dryback target by 3-5%. Add one more shot per day. Don't over-steer — stressed plants don't produce well either.",
            },
            {
                "symptom": "Slow growth in veg despite good conditions",
                "cause": "Overwatering or root zone staying too wet",
                "fix": "Reduce shot frequency. Increase dryback slightly. Lift pots — if heavy for hours after last shot, you're overwatering.",
            },
            {
                "symptom": "Inconsistent dryback day-to-day",
                "cause": "Environmental changes (temp/humidity swings) affecting transpiration rate",
                "fix": "Stabilize environment first. Use substrate sensors for real-time monitoring. Adjust irrigation schedule to match environmental conditions.",
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# IRRIGATION MANAGEMENT — Drip system's core differentiator
# ─────────────────────────────────────────────────────────────────────────────

DRIP_IRRIGATION_MANAGEMENT: dict = {
    "emitter_types_and_selection": {
        "pressure_compensating": {
            "flow_rate_gph": "0.5-2.0",
            "pressure_range_psi": "10-40",
            "description": "Delivers consistent flow regardless of pressure variations or line length.",
            "best_for": "Multi-plant systems with varying line lengths. Commercial setups.",
            "pros": ["Uniform delivery to all plants", "Long run lengths OK", "Handles elevation changes"],
            "cons": ["More expensive", "Can clog if not filtered", "Minimum operating pressure required"],
        },
        "non_compensating": {
            "flow_rate_gph": "0.5-4.0 (varies with pressure)",
            "pressure_range_psi": "5-30",
            "description": "Flow rate changes with pressure. Simpler, cheaper, but less uniform.",
            "best_for": "Small systems with equal line lengths. Budget builds.",
            "pros": ["Cheap", "Simple", "Low minimum pressure"],
            "cons": ["Uneven flow if lines differ in length", "Pressure-dependent", "End-of-line plants get less"],
        },
        "drip_stakes": {
            "flow_rate_gph": "0.5-2.0",
            "description": "Emitter mounted on a stake inserted into media. Directs water to root zone.",
            "best_for": "Pots, grow bags, individual containers. Most common hobby setup.",
            "notes": "Use arrow/barbed stakes for stability. One per small pot, 2-4 per large pot.",
        },
        "drip_rings": {
            "flow_rate_gph": "2.0-5.0 (distributed)",
            "description": "Ring around stem base with multiple drip points. Even distribution around root zone.",
            "best_for": "Large containers (5+ gal). Ensures entire root ball is wetted, not just one spot.",
            "notes": "Especially important in coco/perlite where lateral water movement is limited.",
        },
    },
    "runoff_monitoring": {
        "target_runoff_percent": {
            "standard": {"min": 10, "max": 20, "notes": "10-20% runoff ensures full media saturation without waste."},
            "heavy_feed": {
                "min": 20,
                "max": 30,
                "notes": "During heavy feeding stages, extra runoff helps prevent salt lockout.",
            },
            "flush": {"min": 30, "max": 50, "notes": "Heavy runoff during flush to leach accumulated salts."},
        },
        "runoff_ec_analysis": {
            "runoff_ec_close_to_input": "Media is balanced. Nutrients flowing through without accumulation. Good.",
            "runoff_ec_higher_than_input": "Salt buildup in media. Increase runoff % or flush. Common issue.",
            "runoff_ec_lower_than_input": "Plant consuming heavily. May need to increase feed strength.",
            "action_threshold": "If runoff EC is >0.5 above input EC consistently, perform a flush.",
        },
        "runoff_ph_analysis": {
            "target_range": {"min": 5.5, "max": 6.5},
            "runoff_ph_dropping": "Media becoming acidic. Often from over-feeding ammoniacal nitrogen. Raise input pH slightly.",
            "runoff_ph_rising": "Media becoming alkaline. Could be calcium carbonate buildup. Lower input pH slightly.",
        },
        "collection_method": "Saucers under pots or elevated pot stands with collection trays. Measure immediately — don't let runoff sit (evaporation concentrates it).",
    },
    "drain_to_waste_vs_recirculating": {
        "drain_to_waste": {
            "description": "Feed → runoff discarded. Fresh solution every irrigation.",
            "pros": [
                "No pathogen recirculation",
                "No salt accumulation in reservoir",
                "Simple — no return plumbing",
                "Best for coco/perlite",
            ],
            "cons": ["Higher water/nutrient usage", "Runoff disposal needed", "Environmental impact"],
            "best_for": "Coco, perlite, small hobby grows, organic nutrients.",
            "ec_management": "Input EC is all that matters. Target EC based on stage.",
        },
        "recirculating": {
            "description": "Runoff collected and returned to reservoir. Solution reused until changed.",
            "pros": ["Less waste", "Lower ongoing cost", "Better for large systems"],
            "cons": [
                "pH/EC drift faster",
                "Disease can spread plant-to-plant",
                "More monitoring required",
                "Reservoir maintenance",
            ],
            "best_for": "Rockwool slabs, commercial operations, environmentally-conscious growers.",
            "ec_management": "Monitor reservoir EC constantly. Top off with adjusted solution. Full change every 5-7 days.",
        },
        "recommendation": "Drain-to-waste for hobby growers using coco/perlite. Recirculating for commercial rockwool slab systems.",
    },
    "media_profiles_for_drip": {
        "coco_coir": {
            "irrigation_events_per_day": {"veg": "3-5", "flower": "5-8"},
            "shot_size_ml": "Calculate: container volume × 3-5% per irrigation event",
            "dry_back_target_percent": 5,
            "notes": "Coco wants frequent, small irrigations. Never let it dry out completely. High-frequency fertigation is ideal.",
        },
        "rockwool": {
            "irrigation_events_per_day": {"veg": "2-4", "flower": "4-6"},
            "shot_size_ml": "Calculate: slab volume × 2-4% per event",
            "dry_back_target_percent": 10,
            "notes": "Rockwool holds water well. Less frequent than coco. Watch for over-saturation.",
        },
        "perlite": {
            "irrigation_events_per_day": {"veg": "4-6", "flower": "6-10"},
            "shot_size_ml": "Smaller shots, more frequent. Perlite drains fast.",
            "dry_back_target_percent": 3,
            "notes": "Very low retention. Needs most frequent irrigation of all media. Perfect for crop steering.",
        },
        "soil_soilless": {
            "irrigation_events_per_day": {"veg": "1-2", "flower": "2-3"},
            "shot_size_ml": "Larger shots, less frequent. Let dry back significantly.",
            "dry_back_target_percent": 30,
            "notes": "Soil retains heavily. Drip in soil acts more like automated hand-watering. Longer intervals.",
        },
    },
    "crop_steering_with_drip": {
        "description": "Manipulating irrigation timing and volume to steer plant behavior (vegetative vs generative).",
        "vegetative_steering": {
            "strategy": "Keep media wet. Frequent irrigations. Small dry-back.",
            "irrigation_start": "Early (at lights-on or before)",
            "irrigation_stop": "Late (1h before lights-off)",
            "dry_back_percent": {"max": 5},
            "ec_input": "Lower range for stage",
            "effect": "Promotes stretching, leaf development, vegetative growth.",
        },
        "generative_steering": {
            "strategy": "Allow dry-back. Fewer irrigations. Higher EC. Stress the plant slightly.",
            "irrigation_start": "Delayed (2-4h after lights-on)",
            "irrigation_stop": "Early (3-4h before lights-off)",
            "dry_back_percent": {"target": 10, "max": 15},
            "ec_input": "Higher range for stage (+0.2-0.5 above normal)",
            "effect": "Promotes flowering, fruit set, tighter internodes, terpene production.",
        },
        "p1_p2_strategy": {
            "p1_first_irrigation": "Critical. Should be timed to catch the dry-back at its lowest acceptable point. Too early = vegetative. Too late = stress.",
            "p2_subsequent_irrigations": "Smaller, frequent shots to maintain moisture without over-saturating.",
            "overnight_dry_back": "Generative: let media dry back 10-15% overnight. Vegetative: maintain moisture (last irrigation closer to lights-off).",
        },
        "sensor_requirements": [
            "Substrate moisture sensor (capacitance-based for coco/rockwool)",
            "Weight-based sensor (scale under pot — gold standard for precision)",
            "Drain/runoff EC sensor (inline for recirculating)",
            "Environmental sensors (VPD drives transpiration which drives dry-back rate)",
        ],
    },
    "scheduling_strategies": {
        "timer_based": {
            "description": "Fixed schedule. Irrigations at set times for set duration.",
            "pros": ["Simple", "Reliable", "No sensors needed"],
            "cons": ["Not responsive to plant needs or environment changes", "Over/under-waters on hot/cold days"],
            "best_for": "Simple setups, stable environments, beginners.",
        },
        "sensor_driven": {
            "description": "Irrigations triggered by substrate moisture readings.",
            "pros": ["Responsive to actual plant needs", "Optimal for crop steering", "Adapts to environment"],
            "cons": ["Requires sensors", "More complex", "Sensor calibration needed"],
            "best_for": "Advanced growers, crop steering, commercial.",
        },
        "hybrid": {
            "description": "Timer-based with sensor guardrails. Timer sets schedule, sensor prevents over/under-watering.",
            "pros": ["Best of both", "Failsafe if sensor fails", "Easy to understand"],
            "cons": ["Two systems to manage"],
            "best_for": "Most hobbyist systems aiming for precision without full automation.",
        },
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — the single export consumed by the API/frontend
# ─────────────────────────────────────────────────────────────────────────────

DRIP_CONFIG: dict = {
    "grow_type_id": "drip",
    "version": "1.0.0",
    "stages": DRIP_STAGES,
    "equipment": DRIP_EQUIPMENT,
    "quick_reference": DRIP_QUICK_REFERENCE,
    "troubleshooting": DRIP_TROUBLESHOOTING,
    "irrigation_management": DRIP_IRRIGATION_MANAGEMENT,
    "total_grow_days": {"min": 98, "max": 189, "typical": 135},
}
