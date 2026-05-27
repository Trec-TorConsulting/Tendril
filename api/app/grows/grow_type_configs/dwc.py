"""DWC (Deep Water Culture) — Complete grow type configuration.

Enterprise-grade, production-ready configuration covering every aspect of
DWC growing from germination through harvest, drying, and curing.

Supports three environment types (matching Tent.environment_type):
  - indoor  (default — full environmental control, artificial light)
  - outdoor (no climate control, natural photoperiod, weather exposure)
  - greenhouse (partial climate control, natural + supplemental light)

Base stage values target indoor/tent growing.  Each stage carries an
``environment_variants`` dict with ``outdoor`` and ``greenhouse`` keys
that contain **overrides** and **additional** tasks, problems, equipment,
and notes.  The frontend merges base + variant at render time.

Data sources:
- GrowWeedEasy.com DWC guides
- General Hydroponics Flora Trio feeding charts
- Cannabis cultivation best practices (pH, EC, VPD, PPFD, DLI)
- Root zone management for submerged hydroponic systems
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in a DWC grow
# ─────────────────────────────────────────────────────────────────────────────

DWC_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Seed cracks open and taproot emerges. Use Rapid Rooters, paper towel method, or direct-in-cube. Keep warm, moist, and dark.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Keep seeds in darkness. A heat mat at 78°F speeds germination. No direct light until sprout emerges.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.0, "max": 0.0, "target": 0.0},
            "ppm_500": {"min": 0, "max": 0, "target": 0},
            "water_temp_f": {"min": 68, "max": 75, "target": 72},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "notes": "No reservoir needed yet. If pre-filling buckets, use plain pH'd water only.",
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
                "name": "Soak seeds",
                "description": "Place seeds in cup of room-temperature water for 12-24 hours until they sink. Transfer to Rapid Rooter or paper towel.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for taproot",
                "description": "After 24-72 hours, look for white taproot emerging from seed shell. Transfer to net pot once taproot is 0.5-1 inch.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Prepare DWC bucket",
                "description": "Fill bucket with plain pH'd water (5.8). Set water level 1 inch below net pot bottom. Turn on air stone.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Has the seed cracked open?",
            "Is the taproot visible and white?",
            "Is the Rapid Rooter moist but not soaking wet?",
            "Temperature at 75-80°F?",
        ],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Too cold, too dry, or bad seed",
                "solution": "Ensure 75-80°F. Keep medium moist. Try a different seed after 7 days.",
            },
            {
                "issue": "Damping off",
                "cause": "Too wet, no air circulation",
                "solution": "Reduce moisture. Ensure Rapid Rooter is moist not soaked.",
            },
        ],
        "training": [],
        "transition_signals": ["Taproot is 0.5-1 inch long", "Seed shell has cracked and cotyledons are emerging"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Germinate indoors or in a sheltered area even for outdoor grows. Seeds need consistent warmth that outdoor temps rarely provide. Start indoors, transplant to outdoor DWC once seedling has 2-3 true leaf sets.",
                },
                "extra_tasks": [
                    {
                        "name": "Plan outdoor timing",
                        "description": "Outdoor DWC must start after last frost. Photoperiod plants flower when daylight drops below ~14 hours. In northern hemisphere, start seeds indoors in April-May for outdoor transplant in May-June.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Always germinate indoors regardless of final grow location. Outdoor conditions are too unpredictable for delicate seeds.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Germinate inside the greenhouse on a heat mat. Greenhouses provide enough shelter for germination. Ensure overnight temps stay above 65°F — use a seedling heat mat if nights are cool.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse germination works well with a heat mat and humidity dome.",
            },
        },
    },
    # ── 2. SEEDLING ───────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "First true leaves develop. Roots reach down into reservoir. Keep light gentle, humidity high, nutrients very light.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 65, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 300, "target": 200},
            "light_dli": {"min": 6, "max": 19, "target": 13},
            "notes": "Keep light at 24-30 inches above canopy. Seedlings are fragile — too much light causes bleaching.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.2, "max": 0.5, "target": 0.4},
            "ppm_500": {"min": 100, "max": 250, "target": 200},
            "water_temp_f": {"min": 65, "max": 75, "target": 70},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 10,
            "hydroguard_ml_per_gal": 2,
            "notes": "Water level should be touching bottom of net pot to keep Rapid Rooter moist. Top-feed if roots haven't reached water.",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "Very light nutrients — 1/4 strength. Seedlings are extremely sensitive to overfeeding. When in doubt, use less.",
            "flora_micro_ml_per_gal": 0.625,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Beneficial bacteria to prevent root rot. Essential in DWC.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH",
                "description": "Test reservoir pH. Target 5.5-6.0. Seedlings are very pH-sensitive. Adjust with pH Up/Down as needed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check water level",
                "description": "Ensure water touches bottom of net pot. Top-feed with a turkey baster if roots haven't reached water yet.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check root progress",
                "description": "Peek through empty net pot holes. Look for white roots growing down from Rapid Rooter into water.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Check air stone",
                "description": "Verify air stone is bubbling vigorously. No bubbles = roots will drown.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor light distance",
                "description": "Keep light 24-30 inches above seedling. Watch for stretching (too far) or bleaching (too close).",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are the cotyledons (round leaves) still green and healthy?",
            "Are the first true leaves (serrated) developing?",
            "Is the stem strong and upright (not stretchy/leggy)?",
            "Are roots visible growing into the reservoir?",
            "Is the air stone bubbling?",
            "Water color clear (not cloudy/smelly)?",
        ],
        "common_problems": [
            {
                "issue": "Leggy / stretching seedling",
                "cause": "Light too far away or too dim",
                "solution": "Lower light to 20-24 inches. Increase intensity gradually.",
            },
            {
                "issue": "Yellowing cotyledons",
                "cause": "Normal — cotyledons deplete as true leaves take over. Only worry if true leaves yellow.",
                "solution": "No action needed unless true leaves affected.",
            },
            {
                "issue": "Damping off at stem base",
                "cause": "Stem sitting in water, too wet at base",
                "solution": "Lower water level so only roots touch water, not the stem. Maintain air gap.",
            },
            {
                "issue": "Roots not reaching water",
                "cause": "Normal for first few days. Net pot too high or water too low.",
                "solution": "Top-feed with turkey baster 2-3x daily until roots reach. Raise water level temporarily.",
            },
            {
                "issue": "Nutrient burn (brown leaf tips)",
                "cause": "EC too high for seedling",
                "solution": "Dilute reservoir. Use 1/4 strength max. Seedlings need almost nothing.",
            },
        ],
        "training": [],
        "transition_signals": [
            "3-4 sets of true leaves visible",
            "Roots dangling 2+ inches into reservoir",
            "Vigorous daily growth visible",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "light_hours": "Natural daylight (14-18 hours depending on season)",
                    "light_ppfd": "Variable — full sun is ~2000 PPFD but seedlings need shade",
                    "notes": "Keep seedling in partial shade outdoors. Direct summer sun is too intense for seedlings. Use a shade cloth (50%) or place bucket under a tree canopy for first 7-10 days. Gradually increase sun exposure.",
                },
                "reservoir_overrides": {
                    "water_temp_f": {"min": 60, "max": 75, "target": 68},
                    "notes": "Reservoir heats up fast in direct sun. Wrap bucket in reflective insulation (Reflectix). Place bucket in shaded area. Paint bucket white if dark-colored. Water temp is the #1 outdoor DWC challenge.",
                },
                "extra_tasks": [
                    {
                        "name": "Shade seedling from direct sun",
                        "description": "Use 50% shade cloth or natural shade. Gradually expose to more sun over 7-10 days (hardening off).",
                        "interval_days": 1,
                        "priority": "high",
                    },
                    {
                        "name": "Check reservoir temp (twice daily)",
                        "description": "Morning and afternoon check. Outdoor sun heats water rapidly. If above 75°F, add frozen water bottle or move to shade.",
                        "interval_days": 0.5,
                        "priority": "high",
                    },
                    {
                        "name": "Pest inspection",
                        "description": "Check for aphids, gnats, caterpillars. Outdoor seedlings are vulnerable. Use neem oil preventively.",
                        "interval_days": 1,
                        "priority": "medium",
                    },
                    {
                        "name": "Check weather forecast",
                        "description": "Plan for rain (cover reservoir to prevent dilution), wind (stake or protect seedling), and temperature swings.",
                        "interval_days": 1,
                        "priority": "medium",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Sun-scorched seedling",
                        "cause": "Too much direct sun too quickly",
                        "solution": "Move to shade immediately. Gradually increase sun exposure over a week.",
                    },
                    {
                        "issue": "Rain flooding reservoir",
                        "cause": "Uncovered bucket in rain",
                        "solution": "Always cover reservoir opening around the stem. Use a cut pool noodle or neoprene collar plus a rain shield.",
                    },
                    {
                        "issue": "Pests attacking seedling",
                        "cause": "Outdoor environment exposes plant to insects immediately",
                        "solution": "Use neem oil spray preventively. Check daily. Consider BT (Bacillus thuringiensis) for caterpillars.",
                    },
                ],
                "notes": "Outdoor seedlings need hardening off (gradual sun exposure). Most growers start seedlings indoors for 1-2 weeks before moving outside.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "light_hours": "Natural daylight through glazing (slightly reduced PPFD vs full sun)",
                    "notes": "Greenhouse provides good seedling conditions. The glazing naturally reduces light intensity ~10-30%. Open vents during hot days to prevent overheating. Use shade cloth if temps exceed 85°F.",
                },
                "extra_tasks": [
                    {
                        "name": "Monitor greenhouse temp",
                        "description": "Greenhouses heat up fast in sun. Open vents/doors when above 80°F. Seedlings prefer 72-80°F.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                    {
                        "name": "Check reservoir temp",
                        "description": "Greenhouse warmth heats water. Insulate bucket. Target 65-75°F.",
                        "interval_days": 1,
                        "priority": "medium",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Greenhouse overheating",
                        "cause": "Closed greenhouse in sun traps heat",
                        "solution": "Open vents, doors, or side panels. Use shade cloth (30-50%) on roof.",
                    },
                ],
                "notes": "Greenhouses are excellent for DWC seedlings — protected from weather and pests while getting natural light.",
            },
        },
    },
    # ── 3. EARLY VEGETATIVE ───────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Rapid leaf and root growth. Plant develops structure. Begin LST training. Ramp up nutrients. Roots should be a thick white mass.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 55, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 300, "max": 600, "target": 450},
            "light_dli": {"min": 19, "max": 39, "target": 29},
            "notes": "Plants can handle stronger light now. Lower light to 18-24 inches. Watch for light stress (leaves tacoing upward).",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 0.6, "max": 1.0, "target": 0.8},
            "ppm_500": {"min": 300, "max": 500, "target": 400},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "Start weekly reservoir changes. Plants drink fast now — top off every 1-2 days with 1/4 strength nutrient water.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half-strength nutrients. More nitrogen (Gro) for leaf/stem development. Always add Micro first when using GH Flora Trio.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.875,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root rot prevention. Add at every reservoir change AND every top-off.",
                },
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Strengthens stems and cell walls. Add BEFORE other nutrients. Raises pH.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH",
                "description": "Test reservoir pH daily. Target 5.5-6.2. pH swings are common in early veg as roots establish. Let it range naturally within bounds.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check EC",
                "description": "Measure EC/PPM. If EC rises between checks, plant is drinking more water than nutrients — top off with plain pH'd water. If EC drops, plant is hungry — top off with nutrient water.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off reservoir",
                "description": "Add pH'd water (with 1/4 strength nutes if EC is dropping) to maintain water level 1-2 inches below net pot. Add Hydroguard to new water.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Full reservoir change",
                "description": "Drain and refill with fresh nutrient solution. Add Hydroguard. This prevents salt buildup and nutrient imbalances.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Check water temp",
                "description": "Verify 65-72°F. If above 72°F, consider insulating bucket, adding frozen water bottles, or placing in cooler area. Warm water holds less dissolved oxygen.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Root inspection",
                "description": "Peek through empty net pot hole. Roots should be white and fluffy. Brown/slimy/smelly = root rot.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Begin LST training",
                "description": "Once plant has 4-5 nodes, begin gently bending main stem to side and securing with plant ties. This exposes lower branches to light.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are leaves a healthy deep green? (not lime/yellow = hungry, not dark green/clawing = overfed)",
            "Are roots white and fluffy?",
            "Is the stem thickening?",
            "Is growth noticeably faster than the seedling stage?",
            "Any signs of nutrient deficiency? (yellowing lower leaves = N deficiency, brown spots = CalMag)",
            "Any pests visible? Check undersides of leaves.",
        ],
        "common_problems": [
            {
                "issue": "pH swings wildly",
                "cause": "Small reservoir volume, rapid root growth changing chemistry",
                "solution": "Top off more frequently. Larger reservoir = more stable pH. Don't over-correct — small adjustments only.",
            },
            {
                "issue": "Brown/slimy roots",
                "cause": "Root rot (Pythium). Water too warm, not enough oxygen, no beneficial bacteria.",
                "solution": "Add/increase Hydroguard (2ml/gal). Reduce water temp below 72°F. Ensure air stone is vigorous. Trim dead roots.",
            },
            {
                "issue": "Nitrogen deficiency (yellow lower leaves)",
                "cause": "EC too low, reservoir depleted, or pH out of range locking out N",
                "solution": "Check pH first. If pH is fine, increase nutrient strength slightly. Change reservoir with fresh nutes.",
            },
            {
                "issue": "CalMag deficiency (brown spots, interveinal yellowing)",
                "cause": "RO/soft water lacks calcium and magnesium. DWC has no media to buffer.",
                "solution": "Add CalMag supplement (1-2 ml/gal). Always add CalMag first, before base nutrients.",
            },
        ],
        "training": [
            {
                "technique": "LST (Low Stress Training)",
                "when": "4-5 nodes",
                "description": "Gently bend main stem away from center and secure. This breaks apical dominance and creates multiple tops.",
            },
            {
                "technique": "Topping",
                "when": "5-6 nodes",
                "description": "Cut the main stem above the 3rd-5th node to create two main tops. Plant will recover in 2-3 days.",
            },
        ],
        "transition_signals": [
            "Plant has 5-6+ nodes",
            "Root mass is thick and white",
            "Daily visible growth",
            "Plant is 8-12 inches tall",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "light_hours": "Natural daylight (14-18+ hours in summer)",
                    "notes": "Full sun is ideal now — acclimated plants thrive in direct sunlight. Reservoir temperature management becomes critical. Insulate buckets with Reflectix wrap. Paint buckets white. Consider burying bucket partially in ground for thermal mass.",
                },
                "reservoir_overrides": {
                    "water_temp_f": {"min": 58, "max": 75, "target": 68},
                    "change_interval_days": 5,
                    "notes": "Outdoor reservoirs need more frequent changes — heat and sunlight accelerate bacterial growth. Increase Hydroguard to 2.5 ml/gal in summer. Top off more often — evaporation is faster outdoors.",
                },
                "extra_tasks": [
                    {
                        "name": "Insulate & shade reservoir",
                        "description": "Wrap bucket in Reflectix or white reflective material. Keep bucket in shade while plant gets sun. Bury lower half in ground for thermal stability.",
                        "interval_days": None,
                        "priority": "high",
                    },
                    {
                        "name": "Pest scouting",
                        "description": "Check for aphids, spider mites, caterpillars, slugs, and whiteflies. Inspect both sides of leaves. Outdoor grows face constant pest pressure.",
                        "interval_days": 2,
                        "priority": "high",
                    },
                    {
                        "name": "Weather check",
                        "description": "Monitor forecast for storms, heatwaves, and cold snaps. Have a plan to move or protect the bucket if severe weather hits.",
                        "interval_days": 1,
                        "priority": "medium",
                    },
                    {
                        "name": "Rain protection",
                        "description": "Cover the reservoir gap around the stem with a collar or cut pool noodle. Rain dilutes nutrients and raises water level.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Reservoir overheating (above 78°F)",
                        "cause": "Direct sun on bucket, high ambient temps",
                        "solution": "Insulate bucket, partially bury in ground, use frozen water bottles, consider a small aquarium chiller for persistent heat.",
                    },
                    {
                        "issue": "Caterpillar damage",
                        "cause": "Moths lay eggs on leaves; caterpillars eat foliage and bore into stems",
                        "solution": "Apply BT (Bacillus thuringiensis) spray weekly as prevention. Hand-pick caterpillars. Check inside stems if you see frass.",
                    },
                    {
                        "issue": "Wind damage",
                        "cause": "Strong gusts snap branches or topple buckets",
                        "solution": "Stake plant to bamboo supports. Place bucket in sheltered location or against a wall/fence. Use a tomato cage.",
                    },
                ],
                "notes": "Outdoor early veg is the prime growing season — long days and strong sun drive explosive growth. Focus on reservoir temp management and pest prevention.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Open vents and doors during hot days. Greenhouses can exceed 100°F if not ventilated. Use HAF (horizontal air flow) fans. 30% shade cloth on the roof prevents overheating while still allowing strong growth.",
                },
                "reservoir_overrides": {
                    "notes": "Greenhouse warmth heats reservoirs. Insulate bucket. Consider placing on a concrete floor (thermal mass) to keep water cooler.",
                },
                "extra_tasks": [
                    {
                        "name": "Manage greenhouse ventilation",
                        "description": "Open side vents, roof vents, or endwall doors when temp exceeds 80°F. Autovent openers are worth the investment.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                    {
                        "name": "Check for greenhouse pests",
                        "description": "Greenhouses attract whiteflies, fungus gnats, and spider mites. Use sticky traps for monitoring. Introduce beneficial insects (ladybugs, lacewings).",
                        "interval_days": 3,
                        "priority": "medium",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Greenhouse overheating",
                        "cause": "Insufficient ventilation in sunny weather",
                        "solution": "Add automatic vent openers. Use exhaust fans. Apply 30-50% shade cloth in peak summer.",
                    },
                ],
                "notes": "Greenhouses provide excellent early veg conditions — protected from weather while getting strong natural light.",
            },
        },
    },
    # ── 4. LATE VEGETATIVE ────────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 14, "max": 42, "typical": 21},
        "description": "Plant fills out canopy. Continue training. Increase nutrients to near full strength. Prepare for flip to flower by establishing structure.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 65, "target": 55},
            "vpd_kpa": {"min": 0.9, "max": 1.3, "target": 1.1},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 800, "target": 600},
            "light_dli": {"min": 26, "max": 52, "target": 39},
            "notes": "Maximum veg growth rate. Plants drink heavily — reservoir depletion is fast. May need daily top-offs.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 0.8, "max": 1.2, "target": 1.0},
            "ppm_500": {"min": 400, "max": 600, "target": 500},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "Plants drink 0.5-1+ gallon/day now. Top off daily. Change reservoir weekly without exception.",
        },
        "nutrients": {
            "strength_pct": 65,
            "approach": "65-75% strength. High nitrogen for vigorous vegetative growth. Plant should be deep green but not dark/clawing (nitrogen toxicity).",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 2.5,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Always. Every change, every top-off."},
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Stem strength. Add first before other nutes.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH & EC",
                "description": "Daily check. Reservoir chemistry changes fast with big root mass. EC rising = needs more water. EC dropping = needs more nutes.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off reservoir",
                "description": "Daily — plants drink heavily. Use 1/4 strength nutrient water for top-offs. Add Hydroguard.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Full reservoir change",
                "description": "Weekly. Drain, clean bucket, refill with fresh mix. Add Hydroguard 2ml/gal.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Continue LST / tucking",
                "description": "Keep canopy even by bending tall branches and tucking leaves. The goal is a flat, even canopy with many tops at the same height.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Defoliation (optional)",
                "description": "Remove large fan leaves blocking light to lower bud sites. Don't remove more than 20% at once. Healthy plants recover in 1-2 days.",
                "interval_days": 7,
                "priority": "low",
            },
            {
                "name": "Assess flip readiness",
                "description": "Plant will roughly double in height after flip. Flip when plant is 1/3 to 1/2 of desired final height. Consider flower stretch.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Check water temp",
                "description": "Monitor daily. Critical in late veg as lights + big plants generate heat.",
                "interval_days": 1,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Is the canopy even with multiple tops at the same height?",
            "Are leaves a healthy deep green? (not too dark = N toxicity)",
            "Roots still white and healthy?",
            "Is the plant drinking at a consistent rate?",
            "Any pest signs? (thrips, spider mites, fungus gnats)",
            "Is the plant at 1/3-1/2 of desired final height?",
        ],
        "common_problems": [
            {
                "issue": "Nitrogen toxicity (dark green leaves, clawing tips)",
                "cause": "EC too high, too much Gro in the mix",
                "solution": "Reduce nutrient strength by 10-15%. Reduce Gro relative to other bottles.",
            },
            {
                "issue": "Rapid reservoir depletion",
                "cause": "Normal in late veg — big plant drinks fast",
                "solution": "Top off daily. Use a larger reservoir (5-gal bucket minimum, 10-gal preferred for big plants).",
            },
            {
                "issue": "Algae growth",
                "cause": "Light reaching reservoir water through net pot or lid gaps",
                "solution": "Block all light to reservoir. Use dark bucket, cover net pot gaps with hydroton or neoprene collar.",
            },
            {
                "issue": "Heat stress (leaves tacoing/cupping)",
                "cause": "Light too close, temps too high, low humidity",
                "solution": "Raise light. Increase ventilation. Add humidity if below 40%.",
            },
        ],
        "training": [
            {
                "technique": "LST (ongoing)",
                "when": "Throughout late veg",
                "description": "Continue bending and tying branches to maintain flat canopy.",
            },
            {
                "technique": "Mainlining/Manifold",
                "when": "If started earlier",
                "description": "All tops should be at equal height by now. Last chance to even out canopy.",
            },
            {
                "technique": "Supercropping",
                "when": "2-3 weeks before flip",
                "description": "Gently crush and bend stems to create knuckles. Strengthens branches for heavy buds.",
            },
            {
                "technique": "Schwazzing / heavy defoliation",
                "when": "1-3 days before flip",
                "description": "Some growers strip all fan leaves before flip. Controversial but can increase light to bud sites.",
            },
        ],
        "transition_signals": [
            "Plant is 1/3-1/2 of desired final height",
            "Canopy is full and even",
            "Ready to flip light schedule to 12/12",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor photoperiod plants veg until natural daylight drops below ~14 hours (mid-late summer). You cannot control veg length — the sun decides when flowering starts. Autoflowers skip this and flower on their own timeline regardless of light. Plants can get VERY large outdoors — plan for 4-8+ foot tall plants.",
                },
                "reservoir_overrides": {
                    "change_interval_days": 5,
                    "notes": "Large outdoor plants may drink 2-3+ gallons/day in peak summer. Use the largest reservoir possible (10+ gal). Top off at least daily, sometimes twice in heat waves.",
                },
                "extra_tasks": [
                    {
                        "name": "Top off reservoir (twice daily in heat)",
                        "description": "Large outdoor plants in summer heat can drink 2-3+ gal/day. Check morning and evening. EC rising = add plain water.",
                        "interval_days": 0.5,
                        "priority": "high",
                    },
                    {
                        "name": "Structural support",
                        "description": "Outdoor DWC plants grow tall. Install tomato cage, bamboo stakes, or trellis. Plan for 4-8 foot plants with heavy branches.",
                        "interval_days": None,
                        "priority": "high",
                    },
                    {
                        "name": "IPM spray (preventive)",
                        "description": "Apply neem oil or insecticidal soap every 7-10 days during veg. Stop all sprays 2+ weeks before flower. This is your last chance for preventive spraying.",
                        "interval_days": 7,
                        "priority": "medium",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Plant too tall / unmanageable",
                        "cause": "Long outdoor veg period with unlimited root space in DWC",
                        "solution": "Top aggressively. Use aggressive LST or a SCROG frame. Consider starting seeds later (June) for shorter veg.",
                    },
                    {
                        "issue": "Animal damage (deer, rabbits)",
                        "cause": "Outdoor plants attract herbivores",
                        "solution": "Use fencing or chicken wire around plants. Consider companion planting with strong-smelling herbs.",
                    },
                ],
                "notes": "Late veg outdoors is the longest phase — the plant grows until nature triggers flowering. Focus on structure, support, and pest prevention.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse growers can use light deprivation (light dep) tarps to force flowering by covering the greenhouse to create 12/12. Without light dep, plants follow natural photoperiod like outdoor. Light dep gives you indoor-like control with natural light.",
                },
                "extra_tasks": [
                    {
                        "name": "Consider light deprivation",
                        "description": "If you want to control flowering time, install blackout tarps. Cover greenhouse to create 12 hours of uninterrupted darkness. Must be done consistently every day.",
                        "interval_days": None,
                        "priority": "medium",
                    },
                    {
                        "name": "Manage greenhouse heat",
                        "description": "Peak summer greenhouses can hit 110°F+. Use shade cloth, exhaust fans, evaporative cooling if available.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Inconsistent light dep schedule",
                        "cause": "Missing even one day of light dep can revert plant to veg or cause hermaphroditism",
                        "solution": "Automate with motorized tarps or timers. Be consistent — every single day.",
                    },
                ],
                "notes": "Greenhouse late veg is similar to outdoor but with better protection. Light dep is the key advantage for controlling flowering.",
            },
        },
    },
    # ── 5. TRANSITION (Pre-Flower / Stretch) ──────────────────────────────
    {
        "id": "transition",
        "name": "Transition / Stretch",
        "order": 5,
        "duration_days": {"min": 7, "max": 21, "typical": 14},
        "description": "First 1-3 weeks after flipping to 12/12. Plant stretches dramatically (can double in height). Begin transitioning nutrients from Gro to Bloom.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 64, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 60, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 900, "target": 700},
            "light_dli": {"min": 22, "max": 39, "target": 30},
            "notes": "Switch to 12/12 light schedule. Total darkness in the 12 off-hours is CRITICAL — any light leaks can prevent flowering or cause hermaphroditism.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.9},
            "ec": {"min": 0.8, "max": 1.4, "target": 1.1},
            "ppm_500": {"min": 400, "max": 700, "target": 550},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "Transition nutrients gradually. Plant still needs nitrogen during stretch but phosphorus demand is increasing.",
        },
        "nutrients": {
            "strength_pct": 65,
            "approach": "Transition mix — reduce Gro, increase Bloom gradually over 2 weeks. Plant still stretches and needs some nitrogen.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection."},
            ],
        },
        "tasks": [
            {
                "name": "Flip to 12/12",
                "description": "Switch light timer to 12 hours on, 12 hours off. Ensure ZERO light leaks during dark period. Even phone screens or indicator LEDs can cause issues.",
                "interval_days": None,
                "priority": "critical",
            },
            {
                "name": "Check for light leaks",
                "description": "Enter grow space during dark period after 30 min. You should see nothing — seal any light sources.",
                "interval_days": None,
                "priority": "critical",
            },
            {
                "name": "Check pH & EC",
                "description": "Daily check. Nutrient demand shifts during transition — watch for swings.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Manage stretch",
                "description": "Supercrop or tie down branches that are getting too tall. Keep canopy as even as possible for uniform bud development.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Watch for pre-flowers",
                "description": "Look for tiny white hairs (pistils) at branch nodes. These confirm female sex and onset of flowering.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Full reservoir change",
                "description": "Weekly with transition nutrient mix.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Top off reservoir",
                "description": "Daily. Plants drink even more during stretch.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Did the plant start stretching after flip?",
            "Any light leaks in the grow space during dark period?",
            "Are pre-flowers (white pistils) appearing at nodes?",
            "Any signs of male pollen sacs or hermaphroditism? (bananas, nanners)",
            "Is stretch manageable or does canopy need supercropping?",
        ],
        "common_problems": [
            {
                "issue": "Excessive stretch (too tall)",
                "cause": "Genetics, light too far, or too much N",
                "solution": "Supercrop tall branches. Raise PPFD. Reduce nitrogen slightly.",
            },
            {
                "issue": "Hermaphroditism (bananas/pollen sacs)",
                "cause": "Light leaks, stress, genetics",
                "solution": "Remove male parts immediately. Fix light leaks. Monitor closely.",
            },
            {
                "issue": "No signs of flowering after 2 weeks",
                "cause": "Light leaks preventing flower trigger",
                "solution": "Verify absolute darkness during 12-hour off period. Check for light leaks.",
            },
        ],
        "training": [
            {
                "technique": "Supercropping",
                "when": "During stretch",
                "description": "Pinch and bend tall branches to control height and create knuckles.",
            },
            {
                "technique": "Lollipop",
                "when": "Day 1-7 of flower",
                "description": "Remove lower 1/3 of growth that won't receive light. Directs energy to top buds.",
            },
            {
                "technique": "Defoliation",
                "when": "Day 21 of flower (end of stretch)",
                "description": "Remove large fan leaves blocking bud sites. Known as 'schwazze day 21'.",
            },
        ],
        "transition_signals": [
            "Stretch has slowed/stopped",
            "White pistils clearly visible at most nodes",
            "Bud sites forming at branch tips",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "light_hours": "Decreasing natural daylight (~12-14 hours, triggering flower)",
                    "notes": "Outdoor transition is triggered by shortening days in late summer (Aug-Sept in northern hemisphere). You don't 'flip' — nature does. The stretch is the same but watch for light pollution from street lights, porch lights, or neighbors that could interrupt the dark period and prevent proper flowering.",
                },
                "extra_tasks": [
                    {
                        "name": "Eliminate light pollution",
                        "description": "Ensure no artificial light reaches the plant during dark hours. Street lights, porch lights, even car headlights can prevent flowering. Move plant if needed.",
                        "interval_days": None,
                        "priority": "critical",
                    },
                    {
                        "name": "Final pest prevention",
                        "description": "Last chance for preventive sprays. Apply BT for caterpillars — they love to bore into forming buds. After buds form, no more spraying.",
                        "interval_days": None,
                        "priority": "high",
                    },
                    {
                        "name": "Reinforce supports",
                        "description": "Stretch + future bud weight means branches need strong support now. Add bamboo stakes, tomato cages, or trellis netting.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Light pollution preventing flower",
                        "cause": "Nearby artificial lights interrupting dark period",
                        "solution": "Move plant to dark location, block light source, or cover with light-dep tarp at night.",
                    },
                    {
                        "issue": "Early fall cold snap",
                        "cause": "Unexpected frost or near-freezing temps during transition",
                        "solution": "Cover plant with frost cloth at night. Move bucket indoors overnight if possible. DWC buckets are portable.",
                    },
                ],
                "notes": "Outdoor transition happens naturally. The biggest risks are light pollution and early fall weather. DWC's portability is an advantage — you can move buckets.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "If using light dep, you control the flip just like indoor. Cover greenhouse with blackout tarp to create 12/12. If following natural light, transition happens same as outdoor but with better weather protection.",
                },
                "extra_tasks": [
                    {
                        "name": "Light dep schedule (if using)",
                        "description": "Cover greenhouse at the same time every evening. 12 hours of TOTAL darkness required. Even small light leaks through tarp edges matter.",
                        "interval_days": 1,
                        "priority": "critical",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Heat buildup under light dep tarp",
                        "cause": "Covering greenhouse traps heat",
                        "solution": "Cover in evening when temps drop. Ensure some passive ventilation under the tarp.",
                    },
                ],
                "notes": "Greenhouse with light dep gives the best of both worlds — natural light + controlled flowering.",
            },
        },
    },
    # ── 6. EARLY FLOWER ───────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Weeks 3-5 of flower. Bud sites develop and begin filling in. White pistils everywhere. Switch to full bloom nutrients. Critical period for bud formation.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 80, "target": 76},
            "temp_night_f": {"min": 62, "max": 72, "target": 66},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.0, "max": 1.5, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 1000, "target": 800},
            "light_dli": {"min": 26, "max": 43, "target": 35},
            "notes": "Push light intensity — buds need energy to fatten. But don't cook them. Keep leaf surface temp under 85°F.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 6.0},
            "ec": {"min": 1.0, "max": 1.6, "target": 1.3},
            "ppm_500": {"min": 500, "max": 800, "target": 650},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "Full bloom nutrients. Phosphorus and potassium are now the priority. Change reservoir weekly without fail.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Full bloom mix. High P and K for bud development. Nitrogen is still needed but reduced. This is where buds pack on most of their mass.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection. Never skip."},
                {
                    "name": "Liquid Koolbloom (PK booster)",
                    "dose_ml_per_gal": 1.25,
                    "purpose": "Extra phosphorus and potassium for bud development. Optional but effective.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH & EC",
                "description": "Daily. Flowering plants are more sensitive to pH issues. Keep 5.5-6.2. Rotate pH within range to maximize nutrient uptake.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off reservoir",
                "description": "Daily with 1/4 strength bloom water. Buds are thirsty.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Full reservoir change",
                "description": "Weekly. Critical during flower — salt buildup causes lockouts and reduces bud quality.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Monitor bud development",
                "description": "Take photos to track bud growth week over week. Look for signs of growth stalling or deficiencies.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Lower humidity",
                "description": "Keep below 55% to prevent bud rot. Use dehumidifier if needed. Increase air circulation.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check trichome development",
                "description": "Use magnifying glass or jeweler's loupe. Trichomes should be forming on buds and sugar leaves.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are buds visibly growing week over week?",
            "Any signs of bud rot? (brown/mushy spots inside buds)",
            "Is humidity controlled below 55%?",
            "Any nutrient deficiency? (P deficiency = purple stems, K deficiency = brown leaf edges)",
            "Are roots still white and healthy?",
            "Trichomes visible on buds?",
        ],
        "common_problems": [
            {
                "issue": "Bud rot (Botrytis)",
                "cause": "Humidity too high, poor air circulation, dense buds",
                "solution": "Cut affected area plus 1 inch. Lower humidity below 50%. Increase fans. Space buds out.",
            },
            {
                "issue": "Phosphorus deficiency (purple stems, dark leaves)",
                "cause": "pH too high (above 6.2 locks out P), or insufficient P in reservoir",
                "solution": "Lower pH to 5.8-6.0. Increase Bloom nutrients. Consider PK booster.",
            },
            {
                "issue": "Potassium deficiency (brown/crispy leaf edges)",
                "cause": "EC too low, K locked out by pH",
                "solution": "Check pH. Increase bloom nutrients slightly.",
            },
            {
                "issue": "Fox-tailing buds",
                "cause": "Heat stress, light too intense/close",
                "solution": "Lower light intensity or raise light. Improve ventilation.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation",
                "when": "Once at start of this phase",
                "description": "Remove large fan leaves blocking bud sites. Do NOT defoliate after week 6 of flower.",
            },
        ],
        "transition_signals": [
            "Buds filling in and starting to stack",
            "Trichomes covering buds and sugar leaves",
            "Pistils starting to change from white to orange",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "humidity_pct": {"min": 30, "max": 80, "target": 50},
                    "notes": "You cannot control outdoor humidity — but you can manage airflow. If in a humid climate, space plants apart, remove inner leaves for airflow, and inspect for bud rot after every rain event. Dew-covered buds in the morning are normal but prolonged wetness causes mold.",
                },
                "extra_tasks": [
                    {
                        "name": "Post-rain bud inspection",
                        "description": "After rain, gently shake water off buds. Inspect for gray mold (botrytis) within 24-48 hours. Early detection saves the crop.",
                        "interval_days": None,
                        "priority": "critical",
                    },
                    {
                        "name": "Caterpillar patrol (BT spray)",
                        "description": "Budworms (caterpillars) are the #1 outdoor flower pest. They bore into buds and cause rot from inside. Inspect buds for frass (dark droppings). Apply BT spray if found — safe up to harvest.",
                        "interval_days": 3,
                        "priority": "critical",
                    },
                    {
                        "name": "Shake off morning dew",
                        "description": "Gently shake plant each morning to remove dew from buds. Prolonged moisture = bud rot.",
                        "interval_days": 1,
                        "priority": "medium",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Bud rot after rain",
                        "cause": "Water trapped inside dense buds, humid conditions",
                        "solution": "Cut affected area + 1 inch. Shake water off buds after rain. Improve airflow by selective defoliation. Consider harvesting early if persistent rain is forecast.",
                    },
                    {
                        "issue": "Caterpillar/budworm damage",
                        "cause": "Moths lay eggs on buds; larvae eat from inside",
                        "solution": "Apply BT (Bacillus thuringiensis) — safe and organic. Check buds for dark frass droppings. Remove affected buds and caterpillars by hand.",
                    },
                    {
                        "issue": "Early frost threat",
                        "cause": "Fall temperatures dropping",
                        "solution": "Cover with frost cloth at night. Move DWC bucket to sheltered area. A light frost won't kill but hard frost destroys buds.",
                    },
                ],
                "notes": "Outdoor flowering is a race against fall weather and pests. Stay vigilant with bud rot and caterpillar patrols.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse provides rain protection — huge advantage during flower. Control humidity by ventilating during the day and closing up at night (but ensure darkness for 12/12). Use HAF fans to keep air moving around buds.",
                },
                "extra_tasks": [
                    {
                        "name": "Humidity management",
                        "description": "Open vents during day for airflow. Close at dusk for light dep if needed. Use dehumidifier if greenhouse RH consistently above 60% during flower.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Condensation on greenhouse glazing dripping on buds",
                        "cause": "Temperature differential between inside and outside causes condensation",
                        "solution": "Increase air circulation. Use anti-drip greenhouse film. Open vents briefly in morning to equalize temps.",
                    },
                ],
                "notes": "Greenhouse flower is excellent — rain protection plus natural light. Humidity management is the main challenge.",
            },
        },
    },
    # ── 7. MID/PEAK FLOWER (Bulk Phase) ───────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Bulk)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Weeks 5-7. Buds swell and pack on most weight. Peak nutrient demand. Trichomes developing rapidly. This is where yield is made.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 78, "target": 75},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 40, "max": 50, "target": 45},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
            "notes": "Maximum light intensity but watch for bleaching on closest buds. A 5-10°F night temp drop can enhance terpene and color production.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 6.0},
            "ec": {"min": 1.2, "max": 1.8, "target": 1.5},
            "ppm_500": {"min": 600, "max": 900, "target": 750},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "notes": "Peak nutrient consumption. Change reservoir every 5-7 days. Plants may drink 1-2+ gallons per day.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Peak bloom. Maximum P and K. Some growers push EC higher here — watch for tip burn as upper limit signal.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection."},
                {
                    "name": "Liquid Koolbloom (PK booster)",
                    "dose_ml_per_gal": 1.875,
                    "purpose": "Peak P/K for maximum bud density.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH & EC",
                "description": "Daily. Peak nutrient demand means chemistry changes fast.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off reservoir",
                "description": "Daily with 1/4 strength bloom. In hot weather, may need twice daily.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Full reservoir change",
                "description": "Every 5-7 days. Don't skip — salt buildup kills bud quality.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Check trichomes",
                "description": "Use loupe. Trichomes should be mostly clear to milky. Not ready yet.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Support heavy branches",
                "description": "Install plant yoyos, trellis net, or bamboo stakes. Heavy buds can snap branches.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Bud rot patrol",
                "description": "Inspect densest buds for brown/gray spots. Check where buds meet stem.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Are buds noticeably heavier each week?",
            "Trichome coverage increasing?",
            "Any bud rot symptoms?",
            "Humidity controlled below 50%?",
            "Heavy branches supported?",
            "Roots still white? (Brown roots in late flower is more common — Hydroguard is critical now)",
        ],
        "common_problems": [
            {
                "issue": "Nutrient burn (brown crispy tips)",
                "cause": "EC too high",
                "solution": "Reduce EC by 10-15%. Some tip burn is acceptable — means you're near the max the plant can handle.",
            },
            {
                "issue": "Branch snapping",
                "cause": "Heavy buds without support",
                "solution": "Use trellis net (SCROG), bamboo stakes, or plant yoyos to support branches.",
            },
            {
                "issue": "Light bleaching (white/pale bud tops)",
                "cause": "Light too intense or too close",
                "solution": "Raise light. Reduce intensity by 10-15%.",
            },
            {
                "issue": "Foxtailing",
                "cause": "Heat/light stress at bud tips",
                "solution": "Lower temps. Raise light. Improve air circulation above canopy.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Most pistils turning orange/brown",
            "Buds feeling dense and heavy",
            "Trichomes transitioning from clear to milky",
            "Leaf yellowing beginning (natural fade)",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Mid-flower outdoors is typically September-October in northern hemisphere. Days are getting shorter and cooler. Night temps dropping is actually beneficial for terpene and color development. However, fall rain and humidity are the enemy. Be prepared for emergency harvest if prolonged rain is forecast.",
                },
                "extra_tasks": [
                    {
                        "name": "Weather monitoring (critical)",
                        "description": "Check 10-day forecast daily. If a multi-day rain event is coming and buds are close to ready, consider early harvest rather than risking total bud rot loss.",
                        "interval_days": 1,
                        "priority": "critical",
                    },
                    {
                        "name": "Rain cover / tarp",
                        "description": "Rig a simple tarp or clear plastic rain cover above the plant (not touching buds). Keeps rain off while allowing airflow. This single step saves many outdoor grows.",
                        "interval_days": None,
                        "priority": "high",
                    },
                    {
                        "name": "Continued caterpillar patrol",
                        "description": "Caterpillars are still active. Check daily as bud rot from caterpillar damage intensifies in dense mid-flower buds.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Multi-day rain event during peak flower",
                        "cause": "Fall weather patterns",
                        "solution": "Cover with tarp. If no cover available and buds are 80%+ ready, harvest early. A slightly early harvest is better than a moldy crop.",
                    },
                    {
                        "issue": "Cooling nighttime temps (below 50°F)",
                        "cause": "Fall approaching",
                        "solution": "Move DWC bucket to sheltered spot at night. Cold slows growth but enhances colors/terpenes. Below 40°F risks damage.",
                    },
                ],
                "notes": "Outdoor mid-flower is the most stressful period — balancing peak bud development against fall weather. Have an emergency harvest plan ready.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse mid-flower is ideal — rain protection with natural light. Fall temp drops are moderated by greenhouse thermal mass. May need supplemental heating if nighttime temps drop below 55°F consistently.",
                },
                "extra_tasks": [
                    {
                        "name": "Consider supplemental heating",
                        "description": "If overnight greenhouse temps drop below 55°F, use a small space heater or heat mat under the bucket to maintain warmth.",
                        "interval_days": 1,
                        "priority": "medium",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse mid-flower is straightforward. The structure does most of the work protecting buds from weather.",
            },
        },
    },
    # ── 8. LATE FLOWER / RIPENING ─────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower / Ripening",
        "order": 8,
        "duration_days": {"min": 7, "max": 21, "typical": 14},
        "description": "Weeks 7-9+. Buds ripen and mature. Trichomes transition from milky to amber. Natural leaf fade occurs. Begin reducing nutrients.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 76, "target": 73},
            "temp_night_f": {"min": 58, "max": 68, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Cooler temps (especially at night) can enhance colors and terpene production. A 10-15°F day/night swing is beneficial.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 6.0},
            "ec": {"min": 0.8, "max": 1.2, "target": 1.0},
            "ppm_500": {"min": 400, "max": 600, "target": 500},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "notes": "Reduce nutrient strength. Plant is nearing finish — less demand. Some yellowing of fan leaves is normal and desirable (natural fade).",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Reduce to 50% strength. Plant is winding down. Natural yellowing of fan leaves is expected — the plant is using stored nutrients.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Still protecting roots until the end."},
            ],
        },
        "tasks": [
            {
                "name": "Check trichomes daily",
                "description": "Use 60x loupe. Harvest window: mostly milky with 10-30% amber. More amber = more couch-lock. More milky = more uplifting.",
                "interval_days": 1,
                "priority": "critical",
            },
            {
                "name": "Check pH & EC",
                "description": "Daily. Keep in range but plant needs less now.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off reservoir",
                "description": "Still daily. Plant still drinks even as it fades.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Bud rot patrol",
                "description": "Critical now — dense, ripe buds are most vulnerable.",
                "interval_days": 1,
                "priority": "critical",
            },
            {
                "name": "Plan harvest date",
                "description": "Based on trichome readings, breeder's flowering time, and desired effect, set target harvest window.",
                "interval_days": 3,
                "priority": "high",
            },
        ],
        "health_checks": [
            "What percentage of trichomes are milky vs amber vs clear?",
            "Are pistils mostly orange/brown (70%+)?",
            "Natural fan leaf fade occurring? (yellowing from bottom up = normal)",
            "Any bud rot? Check dense buds daily.",
            "Does the grow space smell extremely strong? (peak terpene production)",
        ],
        "common_problems": [
            {
                "issue": "Premature harvest (clear trichomes)",
                "cause": "Harvesting too early based on pistil color alone",
                "solution": "Wait. Pistil color is unreliable. Only trichome color determines harvest readiness.",
            },
            {
                "issue": "Over-ripe buds (all amber trichomes)",
                "cause": "Waited too long",
                "solution": "Harvest immediately. THC degrades to CBN (sleepy effect) with excessive amber.",
            },
            {
                "issue": "Bud rot in final week",
                "cause": "Humidity spike, dense buds, poor circulation",
                "solution": "Cut affected buds immediately. Harvest early if widespread. Better to lose a few days than the whole crop.",
            },
            {
                "issue": "Rapid leaf die-off",
                "cause": "Overfeeding in late flower, salt lockout, or root issues",
                "solution": "Check pH. Consider flushing. If close to harvest window, harvest.",
            },
        ],
        "training": [],
        "transition_signals": [
            "10-30% amber trichomes (personal preference)",
            "Most pistils are orange/brown",
            "Fan leaves significantly faded",
            "Buds feel dense and sticky",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Late flower outdoors is October-November in many regions. First frost is the hard deadline — everything must be harvested before a hard freeze. Cool nights (50-60°F) enhance purple colors and terpene profiles. This is when outdoor DWC shines — the natural temp swings produce exceptional flavor.",
                },
                "extra_tasks": [
                    {
                        "name": "Frost watch",
                        "description": "Monitor forecasts for first frost date. A light frost (32°F briefly) is survivable but stresses the plant. A hard freeze kills it. Have a harvest plan 1-2 weeks before expected first frost.",
                        "interval_days": 1,
                        "priority": "critical",
                    },
                    {
                        "name": "Daily bud rot check",
                        "description": "Cool, damp fall mornings are prime bud rot conditions. Check every dense cola daily. Remove any affected buds immediately — it spreads fast.",
                        "interval_days": 1,
                        "priority": "critical",
                    },
                    {
                        "name": "Bring bucket in at night (optional)",
                        "description": "If nighttime temps are below 45°F, bring DWC bucket into garage or sheltered area overnight. This is a major advantage of DWC — portability.",
                        "interval_days": 1,
                        "priority": "medium",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "First frost before trichomes are ready",
                        "cause": "Growing season too short for the strain",
                        "solution": "Harvest immediately before frost. Next season, choose faster-finishing strains (8 week flower or autoflowers) or start earlier.",
                    },
                    {
                        "issue": "Persistent damp/fog in late season",
                        "cause": "Fall weather patterns",
                        "solution": "Increase airflow around buds. Remove lower, shaded buds that are rot-prone. Consider early harvest of lower buds while tops finish.",
                    },
                ],
                "notes": "Late flower outdoors is a race against frost. The natural temperature swings produce incredible terpene profiles but the weather risk is real.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse late flower benefits from frost protection. The structure buys you 2-4 extra weeks compared to fully outdoor. Use supplemental heating on cold nights to keep above 55°F.",
                },
                "extra_tasks": [
                    {
                        "name": "Supplemental heating",
                        "description": "As fall progresses, greenhouse overnight temps may drop below optimal. Use a thermostat-controlled heater set to 55°F minimum.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                    {
                        "name": "End-of-season humidity watch",
                        "description": "Fall greenhouse humidity rises as outside temps cool. Run dehumidifier or increase ventilation during warmest part of day.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Greenhouse condensation causing bud moisture",
                        "cause": "Warm inside, cool outside creates condensation that drips on plants",
                        "solution": "Ventilate briefly each morning. Use anti-drip greenhouse film. Increase air circulation.",
                    },
                ],
                "notes": "Greenhouse extends the season significantly. Supplemental heating is the key investment for late flower.",
            },
        },
    },
    # ── 9. FLUSH ──────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 3, "max": 10, "typical": 7},
        "description": "Final 3-10 days before harvest. Run plain pH'd water only. Allows plant to use up stored nutrients for smoother smoke. Controversial but widely practiced.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 76, "target": 73},
            "temp_night_f": {"min": 58, "max": 68, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 550},
            "light_dli": {"min": 17, "max": 30, "target": 24},
            "notes": "Reduce light intensity slightly. Plant is finishing — no need to push growth anymore.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 0.0, "max": 0.2, "target": 0.0},
            "ppm_500": {"min": 0, "max": 100, "target": 0},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 3,
            "hydroguard_ml_per_gal": 2,
            "notes": "Plain pH'd water only. No nutrients. Change every 3 days to keep water fresh. Still add Hydroguard to protect roots.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "No nutrients. Plain pH'd water. Some growers use a flushing agent (FloraKleen) to help mobilize residual salts.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection even during flush."},
                {
                    "name": "FloraKleen (optional)",
                    "dose_ml_per_gal": 2.5,
                    "purpose": "Flushing agent that helps dissolve residual mineral salts.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Drain & refill with plain water",
                "description": "Drain reservoir completely. Refill with plain pH'd water (5.8). Add Hydroguard. No nutrients.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Monitor trichomes",
                "description": "Continue daily checks. Harvest when trichome ratio is where you want it.",
                "interval_days": 1,
                "priority": "critical",
            },
            {
                "name": "Prepare harvest equipment",
                "description": "Clean trimming scissors, set up drying area, prepare drying rack/lines. Ensure drying space can maintain 60°F/60% humidity.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "48-hour darkness (optional)",
                "description": "Some growers give 48 hours of total darkness before harvest. Believed to increase trichome production. Not scientifically proven but widely practiced.",
                "interval_days": None,
                "priority": "low",
            },
        ],
        "health_checks": [
            "Are fan leaves yellowing and fading? (Good — plant is using stored nutes)",
            "Are buds still developing or have they stopped growing?",
            "Trichomes at desired milky/amber ratio?",
            "Any last-minute bud rot?",
        ],
        "common_problems": [
            {
                "issue": "Plant looks sick/dying during flush",
                "cause": "Normal — plant is cannibalizing fan leaves for remaining nutrients",
                "solution": "No action needed. This is expected and desired.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Trichomes at desired harvest ratio",
            "Fan leaves mostly yellowed",
            "Plant has used up stored nutrients",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor flush is simple — just switch to plain pH'd water in the reservoir. The plant continues to receive natural light while flushing. Watch weather — if frost or heavy rain is imminent, skip the flush and harvest immediately.",
                },
                "extra_tasks": [
                    {
                        "name": "Weather-contingent harvest plan",
                        "description": "If a hard frost, multi-day rain, or storm is forecast within 3-5 days, harvest now regardless of flush status. A clean harvest beats a moldy one.",
                        "interval_days": 1,
                        "priority": "critical",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Weather forces early harvest during flush",
                        "cause": "Incoming frost/rain",
                        "solution": "Harvest immediately. A shorter flush won't noticeably affect quality — but mold will ruin it.",
                    },
                ],
                "notes": "Outdoor flush may be shortened or skipped entirely based on weather. Don't risk the crop for a flush.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse flush proceeds like indoor — weather protected. Maintain ventilation to prevent humidity buildup during these final days.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse provides stable conditions for a full flush period.",
            },
        },
    },
    # ── 10. HARVEST ───────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 2, "typical": 1},
        "description": "Cut plant, remove from bucket, trim, and hang to dry. Technique matters — this is where months of work come together.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Harvest in darkness or minimal light. Some growers harvest at end of dark period for highest trichome content.",
        },
        "reservoir": None,
        "nutrients": None,
        "tasks": [
            {
                "name": "Cut plant at base",
                "description": "Cut main stem at base. If wet trimming, trim fan leaves and sugar leaves immediately. If dry trimming, leave sugar leaves on.",
                "interval_days": None,
                "priority": "critical",
            },
            {
                "name": "Remove from DWC bucket",
                "description": "Pull net pot from bucket. Drain. Clean bucket and air stone for next grow.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Wet trim or whole-plant hang",
                "description": "Wet trim: remove all fan leaves, most sugar leaves, hang individual branches. Dry trim: hang whole plant or large branches. Dry trim = slower dry = better quality.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Record harvest details",
                "description": "Note: date, wet weight, number of days in flower, strain, trichome ratio at harvest, any issues. This data improves future grows.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [],
        "common_problems": [
            {
                "issue": "Cutting too much during trim",
                "cause": "Over-trimming removes trichome-covered sugar leaves",
                "solution": "For personal use, leave some sugar leaves. For appearance, trim tight but save trim for edibles/hash.",
            },
        ],
        "training": [],
        "transition_signals": ["Plant is cut, trimmed, and hanging"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Harvest outdoors then bring everything INSIDE for drying and curing. Never dry outdoors — dust, pests, humidity, and UV degrade quality. A garage, shed, closet, or spare room with controlled conditions works.",
                },
                "extra_tasks": [
                    {
                        "name": "Harvest at dawn",
                        "description": "Outdoor plants are best harvested at first light, before the sun warms terpenes and causes them to volatilize. Cooler temps preserve trichome quality.",
                        "interval_days": None,
                        "priority": "medium",
                    },
                    {
                        "name": "Clean bucket for next season",
                        "description": "Scrub bucket, lid, net pot, and air stone with hydrogen peroxide or bleach solution. Rinse thoroughly. Store clean for next grow.",
                        "interval_days": None,
                        "priority": "low",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Pests in harvested buds",
                        "cause": "Outdoor buds may contain small insects, caterpillars, or eggs",
                        "solution": "Do a thorough inspection during trim. Water cure or gentle rinse (bud washing) removes pests, dust, and debris without harming trichomes.",
                    },
                ],
                "notes": "Bud washing (gentle H2O2/water rinse) is highly recommended for outdoor harvests. It removes pests, dust, spray residue, and bird droppings.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Harvest inside the greenhouse, then move to a dedicated drying space. Don't dry in the greenhouse — temperature and humidity are too variable and light degrades trichomes.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse harvest is straightforward. Move all drying/curing to a controlled indoor space.",
            },
        },
    },
    # ── 11. DRYING ────────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Hang-dry buds in dark, controlled environment. Slow drying = better flavor, smell, and smoothness. This step makes or breaks final quality.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 68, "target": 62},
            "temp_night_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK room. Gentle air circulation (not blowing directly on buds). 60°F / 60% RH is the gold standard. Slower = better.",
        },
        "reservoir": None,
        "nutrients": None,
        "tasks": [
            {
                "name": "Check drying progress",
                "description": "Bend a small stem. If it snaps cleanly, buds are dry enough. If it bends, keep drying. If it crumbles, over-dried.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor temp & humidity",
                "description": "Keep 60-68°F, 55-65% RH. Use hygrometer in drying area. Adjust dehumidifier/humidifier as needed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check for mold",
                "description": "Inspect hanging buds for any gray/white fuzzy mold. Remove affected buds immediately.",
                "interval_days": 1,
                "priority": "critical",
            },
        ],
        "health_checks": [
            "Is the drying room completely dark?",
            "Temperature 60-68°F?",
            "Humidity 55-65%?",
            "Air circulating gently (not blowing on buds directly)?",
            "Any smell of ammonia? (too wet/fast = chlorophyll not breaking down)",
        ],
        "common_problems": [
            {
                "issue": "Drying too fast (crispy outside, wet inside)",
                "cause": "Too warm, too dry, or too much airflow",
                "solution": "Lower temp. Raise humidity. Remove direct fan on buds. Aim for 10-14 day dry.",
            },
            {
                "issue": "Hay/grass smell",
                "cause": "Dried too fast — chlorophyll didn't break down properly",
                "solution": "Prevention only — can't fix after. Slow, cool, dark drying prevents this. Curing may help slightly.",
            },
            {
                "issue": "Mold during drying",
                "cause": "Humidity too high, dense buds, poor airflow",
                "solution": "Remove affected buds. Lower humidity. Increase gentle air circulation.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Small stems snap when bent (don't bend)",
            "Buds feel dry on outside but slightly spongy when squeezed",
            "Typical drying time: 7-14 days",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Dry INDOORS in a controlled space — never outdoors. A closet, spare room, or basement with 60°F/60% RH works. If in a hot/dry climate, drying may go too fast — use a humidifier. If humid climate, run a dehumidifier.",
                },
                "extra_tasks": [
                    {
                        "name": "Bud wash before hanging (recommended for outdoor)",
                        "description": "Dip harvested branches in 3 buckets: 1) H2O2 solution (1 cup 3% per 5 gal), 2) lemon juice + baking soda water, 3) plain water rinse. Shake off excess and hang. Removes outdoor contaminants.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Drying space too warm (fall HVAC)",
                        "cause": "Home heating system drying out the air",
                        "solution": "Use a room away from heating vents. Add a small humidifier to maintain 55-65% RH. Monitor closely.",
                    },
                ],
                "notes": "The drying environment is the same regardless of grow method — 60°F / 60% RH in darkness. Bud washing is the main extra step for outdoor harvests.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Do NOT dry in the greenhouse. Move to a proper indoor drying space with controlled temp and humidity. Greenhouses have too much temperature and humidity variation.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse-grown buds dry the same as indoor. Just use a proper indoor drying room.",
            },
        },
    },
    # ── 12. CURING ────────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 180, "typical": 30},
        "description": "Buds placed in sealed glass jars. Moisture equalizes. Chlorophyll breaks down. Terpenes mature. Flavor and smoothness dramatically improve over 2-8+ weeks.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 68, "target": 64},
            "temp_night_f": {"min": 58, "max": 65, "target": 62},
            "humidity_pct": {"min": 58, "max": 65, "target": 62},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Store jars in cool, dark place. 62% RH inside jars is ideal. Use Boveda 62% humidity packs for set-and-forget curing.",
        },
        "reservoir": None,
        "nutrients": None,
        "tasks": [
            {
                "name": "Jar buds",
                "description": "Place dried buds loosely in glass Mason jars. Fill 3/4 full. Add Boveda 62% pack. Close lid.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Burp jars (week 1-2)",
                "description": "Open jars for 5-15 minutes, 2-3 times per day for first 2 weeks. This releases excess moisture and gases. If ammonia smell, leave open longer — buds were too wet.",
                "interval_days": 0.5,
                "priority": "high",
            },
            {
                "name": "Burp jars (week 3-4)",
                "description": "Reduce to once daily for 5 minutes.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Burp jars (week 5+)",
                "description": "Once every few days or weekly. After 4+ weeks, buds are stable.",
                "interval_days": 3,
                "priority": "low",
            },
            {
                "name": "Check jar humidity",
                "description": "Use mini hygrometer in jar. Target 60-65% RH. If above 70%, leave open for an hour. If below 55%, buds are over-dried (add Boveda pack).",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Record final weights",
                "description": "Weigh dry, cured buds for final yield numbers. Compare to wet weight and growing conditions for future optimization.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Do buds smell better each week? (hay → floral/fruity/dank)",
            "Is jar RH staying at 60-65%?",
            "Any mold visible on buds in jars?",
            "Are buds getting smoother to smoke/vape each week?",
        ],
        "common_problems": [
            {
                "issue": "Mold in jars",
                "cause": "Buds weren't dry enough before jarring",
                "solution": "Remove affected buds. Remove all buds from jar, dry for 12-24 more hours, rejar.",
            },
            {
                "issue": "Ammonia smell when opening jar",
                "cause": "Too much moisture — anaerobic bacteria starting",
                "solution": "Leave jar open for several hours. May need to lay buds on drying rack for 12-24 hours.",
            },
            {
                "issue": "Buds too dry in jar",
                "cause": "Over-dried before jarring or jar left open too long",
                "solution": "Add Boveda 62% humidity pack. It will slowly restore moisture.",
            },
        ],
        "training": [],
        "transition_signals": [
            "2+ weeks cured — smokeable",
            "4+ weeks cured — good quality",
            "8+ weeks cured — premium quality",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Curing is identical regardless of grow environment. Store jars in cool, dark, indoor space. Outdoor-grown flower often develops exceptional terpene profiles from natural UV and temperature swings during the grow.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "No outdoor-specific curing differences. All curing happens indoors in jars.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Curing is identical regardless of grow environment. Store jars in a cool, dark indoor space — not in the greenhouse.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "No greenhouse-specific curing differences.",
            },
        },
    },
    # ── 13. STORAGE ──────────────────────────────────────────────────────
    {
        "id": "storage",
        "name": "Long-Term Storage",
        "order": 13,
        "duration_days": {"min": 30, "max": 365, "typical": 180},
        "description": "Post-cure long-term storage. After 4-8 weeks of active curing, flower transitions to storage. For home growers this is jars in a dark closet. For commercial operations this is climate-controlled vault storage with nitrogen-sealed containers, batch tracking, FIFO rotation, and compliance testing holds. Proper storage preserves potency and terpenes for 6-12+ months. Improper storage degrades THC to CBN (sedative), destroys terpenes, and invites mold.",
        "environment": {
            "temp_day_f": {"min": 55, "max": 65, "target": 60},
            "temp_night_f": {"min": 55, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK. Cool. Stable temperature. Zero light exposure — UV degrades cannabinoids and terpenes. Commercial vaults: 58-62°F, 55-60% RH, complete darkness. Home: dark closet, cool room. Never garage (temp swings) or fridge (humidity issues).",
        },
        "reservoir": None,
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
                "description": "Home: mason jars with Boveda 58% or 62% packs. Commercial: nitrogen-sealed bags (grove bags, turkey bags, CVault containers) or nitrogen-flushed drums for bulk. Remove as much oxygen as possible — oxygen degrades cannabinoids.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Label and track batches",
                "description": "Label every container: strain, harvest date, cure start date, storage date, weight, batch number. Commercial: full seed-to-sale tracking. FIFO rotation — oldest stock ships first.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monthly quality checks",
                "description": "Inspect for mold, smell for off odors (ammonia, mustiness). Check humidity packs — replace when exhausted. Spot-check trichome color (amber increase = degradation progressing). Commercial: test potency/terpenes at 30/90/180 day intervals.",
                "interval_days": 30,
                "priority": "high",
            },
            {
                "name": "Maintain environment",
                "description": "Monitor vault/storage room temp and humidity. Dehumidifier + AC as needed. No light leaks. Commercial: environmental monitoring with alerts.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Rotate stock (FIFO)",
                "description": "Commercial: first in, first out. Track storage duration per batch. Flag batches approaching 12 months for priority sale/processing.",
                "interval_days": 30,
                "priority": "medium",
            },
            {
                "name": "Compliance testing holds",
                "description": "Commercial: maintain testing hold samples per state/local regulations. Store separately. Track chain of custody.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Temperature stable 55-65°F?",
            "Humidity 55-62%?",
            "Complete darkness?",
            "No mold or off odors?",
            "Humidity packs still active?",
            "Batch labels current?",
            "FIFO rotation maintained?",
        ],
        "common_problems": [
            {
                "issue": "THC degrading to CBN (increased sedation, reduced potency)",
                "cause": "Heat, light, oxygen, or time. THC converts to CBN at ~5% per year under ideal conditions, much faster with heat/light.",
                "solution": "Ensure complete darkness, cool temps (60°F ideal), minimal oxygen (nitrogen flush). Accept ~5%/year loss as baseline. If faster: check for light leaks and temp spikes.",
            },
            {
                "issue": "Terpene loss (flat smell, reduced flavor)",
                "cause": "Temperature above 70°F volatilizes terpenes. Oxygen oxidizes them. Frequent container opening.",
                "solution": "Keep below 65°F. Minimize container opening. Nitrogen-sealed containers for long-term. Terpenes degrade faster than cannabinoids.",
            },
            {
                "issue": "Mold in storage",
                "cause": "Humidity above 65% or flower wasn't properly dried/cured before storage",
                "solution": "Check humidity immediately. Remove affected material. Increase airflow. Ensure flower is at 58-62% RH before sealing. Commercial: reject and destroy moldy batches per compliance requirements.",
            },
            {
                "issue": "Weight loss over time",
                "cause": "Normal moisture equilibration. 1-3% weight loss in first month of storage is typical.",
                "solution": "Account for in inventory. Boveda/Integra packs minimize loss. Sealed containers reduce ongoing loss.",
            },
        ],
        "training": [],
        "transition_signals": ["N/A — terminal stage"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Storage is always indoor. No outdoor-specific differences."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "All storage is indoor in controlled environment.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Do NOT store in greenhouse. Store in climate-controlled indoor space."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse temperature swings make it unsuitable for storage.",
            },
        },
        "commercial_scale": {
            "container_progression": {
                "home_small": "Mason jars (quart/half-gallon) with Boveda packs",
                "home_large": "Grove bags or CVault containers",
                "commercial_small": "Nitrogen-sealed grove bags (1 lb units)",
                "commercial_medium": "Turkey bags in sealed bins, nitrogen-flushed",
                "commercial_large": "Nitrogen-flushed drums (5-50 lb), sealed bins in vault",
                "industrial": "Climate-controlled vault rooms, nitrogen generators, automated monitoring",
            },
            "degradation_timeline": {
                "0_3_months": "Peak quality. Minimal degradation. Ideal consumption window.",
                "3_6_months": "Slight terpene reduction (~10-15%). Potency stable. Still premium.",
                "6_12_months": "Noticeable terpene loss (~20-30%). THC down ~5%. Still good quality.",
                "12_18_months": "Significant quality decline. Consider processing into extracts/edibles.",
                "18_plus_months": "Not recommended for flower sales. Convert to extracts, edibles, or topicals.",
            },
            "testing_schedule": {
                "initial": "Full panel at harvest (potency, terpenes, pesticides, heavy metals, microbials)",
                "30_days": "Potency + terpenes retest (post-cure baseline)",
                "90_days": "Potency + terpenes + microbials",
                "180_days": "Full panel retest",
                "360_days": "Full panel — decision point: sell, process, or destroy",
            },
            "inventory_management": {
                "fifo": "First in, first out. Oldest batches ship first.",
                "batch_tracking": "Seed-to-sale tracking per state regulations. Lot numbers, weights, test results.",
                "hold_requirements": "Retain testing samples per compliance. Typical: 10g per batch, stored 1 year minimum.",
                "insurance_storage": "Maintain documented temperature/humidity logs for insurance claims.",
            },
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT CHECKLIST
# ─────────────────────────────────────────────────────────────────────────────

DWC_EQUIPMENT: list[dict] = [
    # Essentials
    {
        "name": "DWC Bucket (5-10 gal)",
        "category": "essential",
        "description": "Food-safe bucket with lid and net pot hole. Dark colored to prevent algae. 5-gal minimum, 10-gal preferred for larger plants.",
    },
    {
        "name": "Net Pot (6 inch)",
        "category": "essential",
        "description": "Sits in bucket lid. Holds growing media and plant.",
    },
    {
        "name": "Air Pump",
        "category": "essential",
        "description": "Must run 24/7. Size depends on bucket count. Min 4W per bucket. EcoPlus and Vivosun are reliable.",
    },
    {
        "name": "Air Stone (large)",
        "category": "essential",
        "description": "Large disc or cylinder air stone. More bubbles = more dissolved oxygen. Replace every 1-2 grows.",
    },
    {
        "name": "Air Tubing",
        "category": "essential",
        "description": "Connects air pump to air stone. Standard 1/4 inch.",
    },
    {
        "name": "Hydroton / Clay Pebbles",
        "category": "essential",
        "description": "Fill net pot around Rapid Rooter. Rinse thoroughly before use to remove dust.",
    },
    {
        "name": "pH Pen or Test Kit",
        "category": "essential",
        "description": "Digital pH pen preferred. Calibrate regularly. Apera or BlueLab are reliable.",
    },
    {
        "name": "EC/TDS Meter",
        "category": "essential",
        "description": "Measures nutrient strength. Get one that reads EC and PPM.",
    },
    {
        "name": "pH Up & pH Down",
        "category": "essential",
        "description": "General Hydroponics pH Up and Down. Small amounts adjust pH. pH Down is much stronger than pH Up.",
    },
    {
        "name": "Nutrients (GH Flora Trio)",
        "category": "essential",
        "description": "FloraGro, FloraMicro, FloraBloom. Industry standard for DWC. Add Micro first, then Gro, then Bloom.",
    },
    {
        "name": "Hydroguard",
        "category": "essential",
        "description": "Beneficial bacteria (Bacillus amyloliquefaciens). Prevents root rot. Essential for DWC. 2 ml/gal at every res change and top-off.",
    },
    {
        "name": "Grow Light",
        "category": "essential",
        "description": "LED recommended. Size depends on grow space. Target 30-40 watts/sq ft for flower.",
    },
    {
        "name": "Light Timer",
        "category": "essential",
        "description": "Mechanical or digital timer for 18/6 → 12/12 light schedules. Must be reliable.",
    },
    {
        "name": "Thermometer / Hygrometer",
        "category": "essential",
        "description": "Monitor temp and humidity. Wireless with app is convenient.",
    },
    # Recommended
    {
        "name": "CalMag Supplement",
        "category": "recommended",
        "description": "Essential if using RO or soft water. Prevents calcium and magnesium deficiencies.",
    },
    {
        "name": "Rapid Rooters",
        "category": "recommended",
        "description": "Best germination method for DWC. Pre-moistened seed plugs.",
    },
    {
        "name": "Water Thermometer",
        "category": "recommended",
        "description": "Submersible thermometer for reservoir. Target 65-72°F.",
    },
    {
        "name": "Jeweler's Loupe (60x)",
        "category": "recommended",
        "description": "For checking trichome maturity at harvest. Digital microscope also works.",
    },
    {
        "name": "Exhaust Fan + Carbon Filter",
        "category": "recommended",
        "description": "Controls heat, humidity, and smell. Size to your grow space.",
    },
    {
        "name": "Circulation Fan",
        "category": "recommended",
        "description": "Oscillating fan for air movement. Strengthens stems and prevents hot spots.",
    },
    {
        "name": "Silica Supplement (Armor Si)",
        "category": "recommended",
        "description": "Strengthens cell walls and stems. Add before other nutrients. Raises pH.",
    },
    {
        "name": "Water Transfer Pump",
        "category": "recommended",
        "description": "Battery-operated siphon pump for easy reservoir changes.",
    },
    # Optional
    {
        "name": "Top-Feed Pump Kit",
        "category": "optional",
        "description": "Drip from reservoir to seedling until roots reach water. Saves 1-2 weeks in seedling stage.",
    },
    {
        "name": "Dissolved Oxygen Meter",
        "category": "optional",
        "description": "Measures DO levels. Target 6+ ppm. Nice to have but not necessary if air stone is strong.",
    },
    {
        "name": "Water Chiller",
        "category": "optional",
        "description": "Keeps reservoir at ideal temp. Only needed if grow room is hot (consistently above 80°F).",
    },
    {
        "name": "PK Booster (Liquid Koolbloom)",
        "category": "optional",
        "description": "Extra phosphorus and potassium during peak flower. Increases bud density.",
    },
    {
        "name": "Trellis Net (SCROG)",
        "category": "optional",
        "description": "Netting to spread canopy evenly. Great for maximizing light coverage.",
    },
    {
        "name": "Plant Yoyos",
        "category": "optional",
        "description": "Retractable hangers to support heavy branches in flower.",
    },
    {
        "name": "Mason Jars + Boveda Packs",
        "category": "optional",
        "description": "For curing. Wide-mouth quart jars. Boveda 62% humidity packs.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE CHARTS
# ─────────────────────────────────────────────────────────────────────────────

DWC_QUICK_REFERENCE = {
    "ph_range": {"min": 5.5, "max": 6.2, "ideal": "5.8 seedling/veg, 6.0 flower"},
    "ec_by_stage": {
        "seedling": {"min": 0.2, "max": 0.5},
        "early_veg": {"min": 0.6, "max": 1.0},
        "late_veg": {"min": 0.8, "max": 1.2},
        "transition": {"min": 0.8, "max": 1.4},
        "early_flower": {"min": 1.0, "max": 1.6},
        "mid_flower": {"min": 1.2, "max": 1.8},
        "late_flower": {"min": 0.8, "max": 1.2},
        "flush": {"min": 0.0, "max": 0.2},
    },
    "water_temp_f": {"min": 65, "max": 72, "ideal": 68},
    "reservoir_change_schedule": "Weekly in veg, every 5-7 days in flower, every 3 days during flush",
    "hydroguard_dose": "2 ml/gal at every reservoir change AND every top-off",
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
        "Air pump runs 24/7 — never turn off",
        "Check pH daily — #1 cause of DWC issues",
        "Hydroguard at every res change and top-off",
        "Water level 1-2 inches below net pot",
        "Weekly full reservoir changes minimum",
        "Start nutrients at 1/4 strength and work up",
        "If in doubt, less is more with nutrients",
        "Clean bucket at every reservoir change",
        "Keep reservoir dark — no light = no algae",
        "When EC rises between checks, plant wants water not food",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING GUIDE
# ─────────────────────────────────────────────────────────────────────────────

DWC_TROUBLESHOOTING: list[dict] = [
    {
        "category": "Root Issues",
        "problems": [
            {
                "symptom": "Brown, slimy, smelly roots",
                "diagnosis": "Root rot (Pythium)",
                "severity": "critical",
                "causes": [
                    "Water temp above 72°F",
                    "No beneficial bacteria",
                    "Insufficient aeration",
                    "Organic debris in reservoir",
                ],
                "solutions": [
                    "Add Hydroguard immediately (2 ml/gal)",
                    "Lower water temp below 72°F",
                    "Upgrade air stone or add second air stone",
                    "Trim dead/brown root material with clean scissors",
                    "Full reservoir change with fresh, clean solution",
                    "If severe, use hydrogen peroxide (H2O2) at 3ml/gal of 3% solution as emergency treatment — then switch to Hydroguard 24 hours later",
                ],
            },
            {
                "symptom": "Roots stained brown but not slimy",
                "diagnosis": "Nutrient staining (normal)",
                "severity": "info",
                "causes": ["Dark nutrients discolor roots over time"],
                "solutions": [
                    "No action needed if roots are firm and not slimy. Smell test — healthy roots have no bad odor."
                ],
            },
            {
                "symptom": "Roots not growing into reservoir",
                "diagnosis": "Seedling roots haven't reached water",
                "severity": "medium",
                "causes": ["Water level too low", "Rapid Rooter dried out", "Temperature too cold"],
                "solutions": [
                    "Raise water level to touch bottom of net pot",
                    "Top-feed with turkey baster 2-3x daily",
                    "Ensure 75-80°F ambient temp",
                    "Consider top-feed pump setup",
                ],
            },
        ],
    },
    {
        "category": "pH Issues",
        "problems": [
            {
                "symptom": "pH swings rapidly up and down",
                "diagnosis": "Reservoir too small or rapidly changing conditions",
                "severity": "high",
                "causes": ["Small reservoir volume", "Plants in rapid growth phase", "Using RO water (low buffering)"],
                "solutions": [
                    "Use larger reservoir (10-gal)",
                    "More frequent but smaller pH adjustments",
                    "Add a small amount of tap water for mineral buffering",
                    "Don't over-correct — let pH drift naturally within 5.5-6.2",
                ],
            },
            {
                "symptom": "pH constantly rising",
                "diagnosis": "Normal in DWC — aeration raises pH",
                "severity": "low",
                "causes": [
                    "Air bubbles naturally raise pH",
                    "Plants consuming nutrients at different rates",
                    "Evaporation concentrating alkalinity",
                ],
                "solutions": [
                    "Use pH Down to bring back into range",
                    "This is normal — just manage it",
                    "A small amount of pH Down goes a long way",
                ],
            },
        ],
    },
    {
        "category": "Nutrient Issues",
        "problems": [
            {
                "symptom": "Brown/crispy leaf tips (nutrient burn)",
                "diagnosis": "EC/PPM too high",
                "severity": "medium",
                "causes": [
                    "Too much nutrient added",
                    "Evaporation concentrating nutrients",
                    "Not topping off with plain water",
                ],
                "solutions": [
                    "Reduce EC by 15-20%",
                    "Top off with plain pH'd water when EC rises",
                    "Slight tip burn is actually optimal — means plant is near max capacity",
                ],
            },
            {
                "symptom": "Yellowing lower leaves (nitrogen deficiency)",
                "diagnosis": "Insufficient nitrogen or pH lockout",
                "severity": "medium",
                "causes": ["EC too low", "pH out of range blocking N uptake", "Reservoir depleted"],
                "solutions": [
                    "Check pH first (5.5-6.2)",
                    "Increase Gro portion of nutrients",
                    "Full reservoir change with fresh mix",
                ],
            },
            {
                "symptom": "Brown spots on leaves (CalMag deficiency)",
                "diagnosis": "Calcium or magnesium deficiency",
                "severity": "medium",
                "causes": [
                    "RO or soft water lacks minerals",
                    "LED lights increase CalMag demand",
                    "DWC has no media to buffer minerals",
                ],
                "solutions": [
                    "Add CalMag supplement (1-2 ml/gal)",
                    "Add CalMag before base nutrients when mixing",
                    "Almost all DWC growers need CalMag",
                ],
            },
        ],
    },
    {
        "category": "Environmental Issues",
        "problems": [
            {
                "symptom": "Algae growth (green slime on surfaces)",
                "diagnosis": "Light reaching reservoir water",
                "severity": "medium",
                "causes": [
                    "Light leaking through lid gaps",
                    "Clear or light-colored bucket",
                    "Net pot gaps exposing water",
                ],
                "solutions": [
                    "Use opaque dark-colored bucket",
                    "Cover net pot gaps with hydroton or neoprene collar",
                    "Seal any lid gaps with tape or neoprene",
                    "Keep reservoir completely dark",
                ],
            },
            {
                "symptom": "Reservoir water too warm (above 72°F)",
                "diagnosis": "Elevated water temperature",
                "severity": "high",
                "causes": ["Hot grow room", "Light hitting reservoir", "Air pump heating water slightly"],
                "solutions": [
                    "Insulate bucket with reflective material",
                    "Place frozen water bottles in reservoir",
                    "Use a water chiller (if chronic issue)",
                    "Move air pump outside grow space and pipe air in",
                    "Ensure Hydroguard is used — warm water + no beneficials = guaranteed root rot",
                ],
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# RESERVOIR MANAGEMENT — DWC's core differentiator deep dive
# ─────────────────────────────────────────────────────────────────────────────

DWC_RESERVOIR_MANAGEMENT: dict = {
    "top_off_decision_tree": {
        "description": "How to decide between plain water top-off vs nutrient top-off based on EC drift.",
        "ec_rising": {
            "meaning": "Plants drinking more water than nutrients. Solution is concentrating.",
            "action": "Top off with plain pH'd water only.",
            "target": "Bring EC back to starting level.",
        },
        "ec_stable": {
            "meaning": "Plants consuming water and nutrients at equal rates. Ideal balance.",
            "action": "Top off with 1/2 strength nutrient solution.",
            "target": "Maintain current EC.",
        },
        "ec_dropping": {
            "meaning": "Plants consuming more nutrients than water. Under-fed.",
            "action": "Top off with full-strength or slightly concentrated nutrient solution.",
            "target": "Bring EC back to target for current stage.",
        },
        "golden_rule": "When in doubt, top off with plain pH'd water. You can always add nutrients; removing them requires a full change.",
    },
    "change_schedule": {
        "seedling": {"interval_days": 10, "notes": "Low nutrient demand. Change less frequently."},
        "early_veg": {"interval_days": 7, "notes": "Weekly changes as plant establishes."},
        "late_veg": {"interval_days": 7, "notes": "Weekly. More aggressive feeders now."},
        "transition": {"interval_days": 7, "notes": "Weekly. Nutrient ratio shifting."},
        "early_flower": {"interval_days": 5, "notes": "More frequent. Heavy demand begins."},
        "mid_flower": {"interval_days": 5, "notes": "Peak demand. Consider every 4 days for large plants."},
        "late_flower": {"interval_days": 5, "notes": "Maintaining quality. Watch for lockout signs."},
        "flush": {"interval_days": 3, "notes": "Frequent plain water changes to clear salts."},
    },
    "emergency_drain_protocol": [
        {
            "trigger": "Root rot detected (brown, slimy roots, foul smell)",
            "action": "Immediate full drain. H2O2 root dip (3ml/gal 3%). Refill with fresh solution + double Hydroguard.",
        },
        {
            "trigger": "pH won't stabilize (swinging >1.0 in 24h)",
            "action": "Full drain. Scrub bucket. Refill with fresh calibrated solution.",
        },
        {
            "trigger": "EC spiked unexpectedly (>0.5 above target)",
            "action": "Drain 50%, refill with plain pH'd water to dilute.",
        },
        {
            "trigger": "Foul smell from reservoir",
            "action": "Immediate full drain. Clean bucket with H2O2. Fresh solution + Hydroguard.",
        },
        {
            "trigger": "Algae visible (green slime on roots/bucket walls)",
            "action": "Drain. Scrub bucket with H2O2. Ensure light exclusion. Refill. Add Hydroguard.",
        },
    ],
    "beneficial_microbes": {
        "primary_recommendation": {
            "product": "Hydroguard",
            "active_ingredient": "Bacillus amyloliquefaciens",
            "dose_ml_per_gal": 2,
            "frequency": "Every reservoir change AND every top-off",
            "notes": "The gold standard for DWC root protection. Colonizes root zone, outcompetes pathogens.",
        },
        "alternatives": [
            {
                "product": "Great White Premium Mycorrhizae",
                "dose": "1 tsp per 2 gal",
                "notes": "Powder. Contains mycorrhizae + trichoderma + bacteria. Apply at transplant.",
            },
            {
                "product": "Mammoth P",
                "dose": "0.16 ml/gal",
                "notes": "Phosphorus-liberating bacteria. Use in flower. Compatible with Hydroguard.",
            },
            {
                "product": "Recharge",
                "dose": "0.5 tsp/gal",
                "notes": "Mycorrhizae + trichoderma + bacteria. Organic. Can cloud water — use sparingly in DWC.",
            },
            {
                "product": "SLF-100",
                "dose": "1 ml/gal",
                "notes": "Enzyme-based. Breaks down dead root matter. Not alive — compatible with H2O2 if needed.",
            },
        ],
        "compatibility_notes": [
            "NEVER use H2O2 with beneficial bacteria — H2O2 kills ALL microbes (good and bad)",
            "Choose either H2O2 sterile approach OR beneficial microbe approach — not both",
            "Hydroguard is the standard DWC recommendation (beneficial approach)",
            "If you must use H2O2 (emergency rot treatment), wait 24h before re-adding beneficials",
            "Mammoth P is safe to combine with Hydroguard (different organisms, complementary)",
        ],
    },
    "dissolved_oxygen": {
        "minimum_ppm": 6.0,
        "target_ppm": 8.0,
        "critical_low_ppm": 4.0,
        "factors_that_reduce_do": [
            "Higher water temperature (above 72°F DO drops rapidly)",
            "Insufficient air stone output",
            "Clogged/mineral-encrusted air stones (replace every 2-3 grows)",
            "Long air hose runs (pressure loss)",
            "High nutrient concentration",
        ],
        "improvement_methods": [
            "Larger/more air stones (target 1 large stone or multiple small per bucket)",
            "Commercial air pump (minimum 4 LPM per bucket)",
            "Water chiller (68°F water holds ~8.5 ppm DO vs 75°F holds ~7.5 ppm)",
            "Replace air stones when bubbles become large/fewer (mineral buildup)",
            "Shorter air hose runs — air pump close to bucket",
        ],
    },
    "water_temperature_management": {
        "target_f": 68,
        "acceptable_range_f": {"min": 65, "max": 72},
        "danger_zone_f": {"above": 75, "notes": "Root rot risk increases exponentially above 75°F"},
        "cooling_methods": [
            {
                "method": "Water chiller",
                "effectiveness": "Best",
                "cost": "High ($150-$500)",
                "notes": "The only reliable method. Size: 1/10 HP per 5 gal bucket.",
            },
            {
                "method": "Frozen water bottles",
                "effectiveness": "Temporary",
                "cost": "Free",
                "notes": "Requires constant rotation. Causes pH/EC swings. Emergency only.",
            },
            {
                "method": "Insulate bucket",
                "effectiveness": "Moderate",
                "cost": "Low",
                "notes": "Reflective insulation wrap. Prevents room heat transfer.",
            },
            {
                "method": "Keep bucket off floor in tent",
                "effectiveness": "Low-Moderate",
                "cost": "Free",
                "notes": "Heat rises. Floor is often coolest spot — use elevated stand only if floor has radiant heat.",
            },
            {
                "method": "Run lights at night",
                "effectiveness": "Moderate",
                "cost": "Free",
                "notes": "Lower ambient temp during lights-on keeps water cooler.",
            },
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLED CONFIG EXPORT
# ─────────────────────────────────────────────────────────────────────────────

DWC_CONFIG: dict = {
    "grow_type_id": "dwc",
    "version": "1.0.0",
    "stages": DWC_STAGES,
    "equipment": DWC_EQUIPMENT,
    "quick_reference": DWC_QUICK_REFERENCE,
    "troubleshooting": DWC_TROUBLESHOOTING,
    "dwc_reservoir_management": DWC_RESERVOIR_MANAGEMENT,
    "total_grow_days": {
        "min": 90,
        "max": 150,
        "typical_photo": 120,
        "typical_auto": 80,
        "breakdown": "Germination (3-7d) + Seedling (7-14d) + Veg (28-63d) + Flower (56-70d) + Dry (7-14d) + Cure (14-60d)",
    },
}
