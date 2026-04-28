"""Indoor Soil — Complete grow type configuration.

Enterprise-grade configuration for indoor soil growing — the most traditional
and accessible method for home growers.  Soil provides a natural buffer that
makes it the most forgiving medium, but also the least precise.

The defining features are **DUAL feeding tracks** (organic AND synthetic — the
user chooses or blends), **living soil biology** (beneficial microbes, mycorrhizae,
fungi that don't exist in hydro), **wet/dry watering cycle** (the OPPOSITE of
coco — soil MUST dry between waterings), **compost tea and top dressing** (organic
inputs that feed the soil food web, not just the plant), and **natural pest
management** (soil hosts both beneficial and harmful organisms).

Key Soil differences from other methods:
  - Wet/dry cycle: soil MUST dry between waterings (opposite of coco/hydro)
  - pH range is 6.0-7.0 (higher than hydro's 5.5-6.0)
  - DUAL feeding tracks: organic (teas, top dress, slow release) and synthetic (bottled)
  - Living soil biology: microbes, mycorrhizae, beneficial fungi
  - "Water-only" super soil is possible (amendments pre-loaded)
  - Slower nutrient response (2-3 days vs hours in hydro)
  - Most forgiving method — soil buffers pH and nutrient errors
  - Heaviest containers — weight increases dramatically when wet
  - Soil reuse and composting are possible
  - Pest ecology includes soil-dwelling organisms (fungus gnats, root aphids)
  - Terpene development often considered superior to hydro by many growers

Supports three environment types (matching Tent.environment_type):
  - indoor  (default — full environmental control)
  - outdoor (see outdoor_soil config for dedicated outdoor soil)
  - greenhouse (excellent for soil growing)

Data sources:
- Teaming with Microbes (Jeff Lowenfels) — soil food web science
- True Living Organics (The Rev) — organic cannabis methodology
- General Hydroponics Flora Trio feeding charts (soil-adjusted)
- BuildASoil methodology
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in an Indoor Soil grow
# ─────────────────────────────────────────────────────────────────────────────

SOIL_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Seed cracks open and taproot emerges. Start seeds in Rapid Rooters, paper towels, or directly in pre-moistened soil in solo cups. Soil germination is the simplest — just plant the seed and keep it moist.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Seeds in darkness or very dim light. Heat mat at 78°F. Humidity dome.",
        },
        "medium": {
            "watering_method": "mist or light pour",
            "organic_track": {
                "description": "Use pre-amended soil (Fox Farm Ocean Forest, BuildASoil, or homemade super soil). No nutrients needed — the soil is the nutrient.",
                "inputs": [],
            },
            "synthetic_track": {
                "description": "Use any quality potting mix (Fox Farm Happy Frog, ProMix HP). No nutrients yet — seeds don't need them.",
                "inputs": [],
            },
            "notes": "Pre-moisten soil before planting seed. Soil should be damp like a wrung-out sponge — not soaking, not dry. In solo cups, make sure there are drain holes. Soil temperature matters more than air temp for germination.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None — seeds contain all energy needed. Soil provides gentle background nutrition.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Prepare soil",
                "description": "Pre-moisten soil. If using super soil: mix base soil layer + hot soil layer in final pot (hot soil on bottom, base on top — roots grow into nutrients). For solo cup starts: use mild base soil only (Ocean Forest or lighter).",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Plant seed",
                "description": "1/4 inch deep in pre-moistened soil. Pointed end down. Cover lightly. Humidity dome.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check daily",
                "description": "Mist soil surface if drying. Don't overwater — soil germination's biggest risk is drowning the seed.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Soil moist but not saturated?",
            "Temperature at 75-80°F?",
            "Seed planted at correct depth?",
        ],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Soil too wet (drowning), too cold, or planted too deep",
                "solution": "Soil should be damp, not waterlogged. Ensure 75-80°F. Seed only 1/4 inch deep. 1/2 inch is too deep.",
            },
            {
                "issue": "Damping off (seedling falls over at soil line)",
                "cause": "Too wet, poor airflow, Pythium or Fusarium in soil",
                "solution": "Reduce watering. Improve airflow. Use clean or sterilized soil. Inoculate with mycorrhizae.",
            },
        ],
        "training": [],
        "transition_signals": ["Taproot visible", "Sprout emerging", "Cotyledon leaves opening"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Start seeds indoors. Outdoor soil germination is unreliable."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always start seeds indoors.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse germination works with heat mat and dome."},
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
        "description": "First true leaves develop. Seedling in solo cup or small pot with mild soil. The WET/DRY cycle begins here — soil MUST dry between waterings. Lift the pot to check weight. Water when light (dry), skip when heavy (wet). This is the fundamental soil skill.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 65, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 250, "target": 200},
            "light_dli": {"min": 6, "max": 16, "target": 13},
            "notes": "Gentle light. Remove humidity dome gradually over 3-5 days. Seedlings in soil need LESS watering than coco or hydro — the soil holds moisture longer.",
        },
        "medium": {
            "watering_method": "circle pour around stem, water when pot is light",
            "organic_track": {
                "description": "In pre-amended soil, the soil IS the food. No additional feeding for the first 2-4 weeks. Just water. This is the beauty of soil.",
                "inputs": [
                    {
                        "name": "Mycorrhizae inoculant",
                        "application": "dust on roots at transplant",
                        "purpose": "Establish beneficial fungal network. Must contact roots directly.",
                    },
                ],
            },
            "synthetic_track": {
                "description": "In mild potting mix, soil has 2-4 weeks of base nutrition. No feeding yet unless leaves are pale.",
                "inputs": [],
            },
            "notes": "THE RULE: water when the pot is light, skip when heavy. Soil seedlings need to dry between waterings — overwatering is the #1 soil mistake. Root development is BETTER in a wet/dry cycle: roots grow searching for water during the dry period. Water in a small ring around the stem, not the entire soil surface.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None for either track — soil provides base nutrition. If leaves yellow early, add 1/4 strength (synthetic track only).",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Learn the wet/dry cycle",
                "description": "Lift pot daily. Heavy = wet, skip. Light = dry, water. THE most important soil skill. Soil should dry ~1 inch deep between waterings.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Water correctly",
                "description": "When watering: pour slowly in a ring around the stem. Stop when you see runoff from the bottom. Do NOT water every day — only when the pot is light.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Remove humidity dome gradually",
                "description": "Crack dome day 1, remove for hours day 2, full remove by day 3-5.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Watch for fungus gnats",
                "description": "Moist soil surface = fungus gnat breeding ground. Let top inch dry completely between waterings. Yellow sticky traps near pots.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "First true leaves appearing?",
            "Soil drying between waterings (wet/dry cycle)?",
            "No overwatering signs (droopy dark leaves)?",
            "No fungus gnats?",
        ],
        "common_problems": [
            {
                "issue": "Overwatering (droopy, dark green leaves)",
                "cause": "Watering too often — soil hasn't dried between waterings",
                "solution": "STOP watering. Let the soil dry until the pot is noticeably lighter. Soil needs to dry — roots need oxygen. This is the #1 soil mistake and the #1 beginner mistake in all of growing.",
            },
            {
                "issue": "Fungus gnats (tiny flies around soil)",
                "cause": "Soil surface staying wet — gnats breed in top 1 inch",
                "solution": "Let top inch dry completely. Yellow sticky traps. BTI (Mosquito Bits) in water. Diatomaceous earth on soil surface. This is a soil-specific problem.",
            },
            {
                "issue": "Stretching (tall thin stem)",
                "cause": "Light too far away or too dim",
                "solution": "Lower light or increase intensity. Support stem with toothpick.",
            },
        ],
        "training": [],
        "transition_signals": [
            "2-3 sets of true leaves",
            "Roots visible at drain holes",
            "Solo cup drying every 2-3 days",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Outdoor: harden off before placing outside."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Harden seedlings before outdoor placement.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: watch for heat drying."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: good environment for soil seedlings.",
            },
        },
    },
    # ── 3. EARLY VEGETATIVE ──────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Rapid growth begins. Transplant from solo cup to 1-3 gallon pot. Then transplant to final pot (3-7 gallon) when roots fill intermediate pot. Soil grows run longer in veg than hydro — soil is slower but produces different plant structure. Begin feeding at 3-4 weeks (synthetic track) or begin teas/top dress (organic track).",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 55, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 300, "max": 500, "target": 400},
            "light_dli": {"min": 19, "max": 32, "target": 26},
            "notes": "Ramp up light. Soil grows are slightly slower than hydro but produce robust plants.",
        },
        "medium": {
            "watering_method": "full pot drench when light, wait until dry",
            "organic_track": {
                "description": "In super soil or living soil: the soil feeds the plant. Supplemental inputs are teas and top dressings that feed the SOIL BIOLOGY, not the plant directly. The microbes make nutrients plant-available.",
                "inputs": [
                    {
                        "name": "Compost tea (aerated)",
                        "application": "1x/week as soil drench",
                        "purpose": "Feeds microbial population. Brew 24-48 hours with compost + molasses + air pump.",
                    },
                    {
                        "name": "Top dress (dry amendments)",
                        "application": "Every 2-3 weeks",
                        "purpose": "Slow-release nutrition. Neem meal, kelp meal, alfalfa meal, bone meal. Scratch into top inch, water in. Takes 1-2 weeks to break down.",
                    },
                    {
                        "name": "Mycorrhizae",
                        "application": "At transplant — dust on roots",
                        "purpose": "Extends root reach. Mycorrhizal fungi create a secondary root network.",
                    },
                ],
            },
            "synthetic_track": {
                "description": "Begin bottled nutrients when soil's base nutrition runs out (usually 3-4 weeks). Start at 1/4 strength, ramp to 1/2. Feed every other watering — alternate feed/water/feed/water.",
                "inputs": [],
            },
            "notes": "Wet/dry cycle continues — more critical as pots get larger. Larger pots take longer to dry. Water only when pot is noticeably lighter. Overwatering in large soil pots is the most common veg mistake. ORGANIC TRACK: feed the soil, not the plant. SYNTHETIC TRACK: feed every other watering (not every watering like coco).",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "Synthetic track: 1/4 strength every other watering. Organic track: teas and top dress. Soil pH: 6.0-7.0.",
            "flora_micro_ml_per_gal": 0.625,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 0.3125,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {
                    "name": "Mycorrhizae",
                    "dose_ml_per_gal": None,
                    "purpose": "Apply directly to roots at transplant. Not a liquid nutrient.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Transplant to intermediate pot",
                "description": "When roots fill solo cup, transplant to 1-3 gallon pot. Handle root ball gently. Don't break roots. If using super soil: put hot soil on bottom, mild base soil on top.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Continue wet/dry cycle",
                "description": "Larger pots = longer dry-down time. May go 3-5 days between waterings in a 3-gallon pot. This is NORMAL in soil.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Begin feeding (if needed)",
                "description": "Synthetic: start at 1/4 strength when lower leaves lighten. Organic: first compost tea at week 3-4. Top dress every 2-3 weeks.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Transplant to final pot",
                "description": "When roots fill intermediate pot (drying in 2-3 days), transplant to final 3-7 gallon pot.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Begin training",
                "description": "LST, topping at 4-5 nodes. Soil plants recover from training slower than hydro — allow extra time.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Fungus gnat prevention",
                "description": "Yellow sticky traps. BTI in every watering. Let top inch dry. This is ongoing in soil.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Wet/dry cycle properly managed?",
            "Roots expanding into new pot?",
            "No signs of overwatering?",
            "No fungus gnats?",
            "Growth rate accelerating?",
        ],
        "common_problems": [
            {
                "issue": "Overwatering in large pot",
                "cause": "Watering the entire soil volume when roots only occupy a fraction",
                "solution": "Water only the root zone initially. As roots expand, gradually water more of the pot. A 5-gallon pot with a solo-cup-sized root ball should NOT be fully drenched.",
            },
            {
                "issue": "Nutrient deficiency (pale leaves)",
                "cause": "Soil's base nutrition depleted (3-4 weeks in mild mixes)",
                "solution": "Synthetic: begin 1/4 strength feeding. Organic: top dress and/or compost tea.",
            },
            {
                "issue": "Fungus gnats escalating",
                "cause": "Top inch of soil staying moist, organic matter in soil",
                "solution": "BTI (Mosquito Bits) in EVERY watering. Yellow sticky traps. Let top inch go fully dry. Diatomaceous earth. Nematodes (Stratiolaelaps scimitus) for biological control.",
            },
            {
                "issue": "Slow growth compared to hydro",
                "cause": "Normal — soil is slower than hydro/coco",
                "solution": "Expected. Soil grows run 1-2 weeks longer in veg. The tradeoff is simpler management and often better terpene profiles.",
            },
        ],
        "training": [
            {"technique": "LST", "description": "Bend and tie. Start at 4-5 nodes.", "timing": "After 4-5 nodes"},
            {
                "technique": "Topping",
                "description": "Cut above 4th-5th node. Recovery 3-5 days in soil (slower than hydro).",
                "timing": "At 5-6 nodes",
            },
        ],
        "transition_signals": ["5-6 nodes", "Roots filling final pot", "Vigorous daily growth"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "See outdoor_soil config for outdoor-specific guidance."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor soil is a separate grow type.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse soil: excellent. Watch drying rate in warm conditions."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse is great for soil.",
            },
        },
    },
    # ── 4. LATE VEGETATIVE ───────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 7, "max": 21, "typical": 14},
        "description": "Plant reaches target size in final pot. Full veg feeding on either track. Soil grows have a longer veg than hydro but build robust root systems. Pre-flip: no flush needed in soil (unlike hydro) — just reduce nitrogen in the last feeding before flip.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 50, "max": 65, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 600, "target": 500},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Full veg intensity. Plant transpiring well. Soil drying faster as root system expands.",
        },
        "medium": {
            "watering_method": "full pot drench to 10-15% runoff when light",
            "organic_track": {
                "description": "Peak organic feeding. Top dress every 2 weeks with veg amendments (high N: alfalfa, neem, kelp). Weekly compost tea. The soil biology should be fully established now — you're feeding the microbes, they feed the plant.",
                "inputs": [
                    {
                        "name": "Top dress (veg blend)",
                        "application": "Every 2 weeks",
                        "purpose": "Alfalfa meal + neem meal + kelp meal. Scratch in, water in.",
                    },
                    {"name": "Compost tea", "application": "1x/week", "purpose": "Maintain microbial population."},
                    {
                        "name": "Malted barley top dress",
                        "application": "Every 2 weeks",
                        "purpose": "Enzymes that support nutrient cycling. Unique to organic soil.",
                    },
                ],
            },
            "synthetic_track": {
                "description": "Half to three-quarter strength. Feed every other watering. Water/feed/water/feed. Never feed every watering in soil — the soil holds nutrients longer than coco.",
                "inputs": [],
            },
            "notes": "The plant should be drinking the entire pot volume now. Full drenches to runoff. In a 5-gallon fabric pot, expect 3-5 day wet/dry cycles. If the pot takes more than 5 days to dry, the plant is underwatered or root-bound. Pre-flip: last top dress should be bloom-oriented (bone meal, bat guano) for organic. Synthetic: reduce Gro in last feeding.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Synthetic track: half strength every other watering. Organic track: soil biology does the work. pH: 6.2-6.8.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 0.5,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Establish full wet/dry cycle",
                "description": "Full drench when light. Wait until dry. 3-5 day cycles typical in 5-gal pots.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Feed on schedule",
                "description": "Synthetic: every other watering. Organic: weekly tea + biweekly top dress.",
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
            {
                "name": "Pre-flip preparation",
                "description": "Organic: final top dress with bloom amendments (bone meal, bat guano). Synthetic: reduce Gro in last feeding.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Plant at target size?",
            "Wet/dry cycle consistent (3-5 day)?",
            "Canopy filled?",
            "No pest issues?",
        ],
        "common_problems": [
            {
                "issue": "Root-bound (pot drying in 1-2 days)",
                "cause": "Roots completely fill the pot — root-bound",
                "solution": "If still in veg: transplant to larger pot. If ready to flip: accept it and flip. Root-bound plants drink fast but grow slow.",
            },
            {
                "issue": "pH lockout (multiple deficiency symptoms)",
                "cause": "Soil pH drifting from synthetic fertilizer salts",
                "solution": "Check runoff pH. Should be 6.0-7.0. If low: flush with pH 6.8 water. Organic track rarely has pH issues — soil biology self-regulates.",
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
            "Healthy root system",
            "3-5 day wet/dry cycle",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "See outdoor_soil config."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor soil: separate config.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse soil: excellent."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Great for soil late veg.",
            },
        },
    },
    # ── 5. TRANSITION ────────────────────────────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Flipped to 12/12. Stretch phase. Soil plants stretch less aggressively than hydro but still double in height for some cultivars. Transition nutrient ratio from veg to bloom. Organic track: bloom top dress should be breaking down now.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 60, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 700, "target": 600},
            "light_dli": {"min": 22, "max": 30, "target": 26},
            "notes": "Flip to 12/12. DIF of 10°F helps control stretch.",
        },
        "medium": {
            "watering_method": "full drench to runoff when pot is light",
            "organic_track": {
                "description": "Bloom top dress (applied pre-flip) should be breaking down. Continue weekly compost tea. Add bloom-specific inputs.",
                "inputs": [
                    {
                        "name": "Compost tea (bloom)",
                        "application": "1x/week",
                        "purpose": "Continue feeding soil biology. Can add bat guano to tea for PK.",
                    },
                    {
                        "name": "Bloom top dress",
                        "application": "If not done pre-flip, do now",
                        "purpose": "Bone meal, bat guano, kelp. Scratch in, water in.",
                    },
                ],
            },
            "synthetic_track": {
                "description": "Transition ratio: reduce Gro, increase Bloom. Feed every other watering at 3/4 strength.",
                "inputs": [],
            },
            "notes": "Wet/dry cycle continues. Plant drinking more during stretch. Pots may dry faster (every 2-3 days now). This is good — the plant is transpiring heavily. Don't fight the faster cycle by watering less — just water to saturation when dry.",
        },
        "nutrients": {
            "strength_pct": 65,
            "approach": "Transition ratio. Reduce N, increase PK. Synthetic: every other watering. Organic: soil biology handles the transition naturally.",
            "flora_micro_ml_per_gal": 1.625,
            "flora_gro_ml_per_gal": 1.0,
            "flora_bloom_ml_per_gal": 1.25,
            "calmag_ml_per_gal": 0.5,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Flip to 12/12",
                "description": "Zero light leaks during dark period.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Transition nutrients",
                "description": "Synthetic: shift ratio over 5-7 days. Organic: bloom top dress + bloom tea.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Water to demand",
                "description": "Stretch increases water uptake. Pots dry faster. Water when light — don't skip because 'it hasn't been 3 days yet.'",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Manage stretch",
                "description": "Supercrop, tuck into SCROG.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check for preflowers/sex",
                "description": "Watch nodes. Remove males.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Stretch height manageable?",
            "Watering frequency increasing (good sign)?",
            "No light leaks?",
            "No hermaphrodite signs?",
        ],
        "common_problems": [
            {
                "issue": "Nitrogen excess during transition (dark green, clawing)",
                "cause": "Too much nitrogen at flip — soil holds nitrogen longer than hydro",
                "solution": "Reduce or stop N. Soil buffers nutrients — excess N takes 1-2 weeks to clear. Flush if severe.",
            },
            {
                "issue": "Slow flower onset",
                "cause": "Light leaks, or residual nitrogen pushing veg growth",
                "solution": "Check for ANY light during dark period. Even indicator LEDs can disrupt flowering.",
            },
        ],
        "training": [
            {"technique": "Supercropping", "description": "Bend tall stems.", "timing": "First 2 weeks of stretch"},
            {"technique": "SCROG tucking", "description": "Daily tucking.", "timing": "Throughout stretch"},
        ],
        "transition_signals": ["Stretch slowing", "Pistils at bud sites", "Vertical growth stopping"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "See outdoor_soil config."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Separate config.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: light dep for flip control."},
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
        "description": "Buds forming. Full bloom feeding on either track. Soil-grown flower develops terpenes differently — many growers consider soil-grown flower to have superior flavor/aroma. Continue wet/dry cycle.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 62, "max": 70, "target": 66},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Peak light. Low humidity. CO2 1000-1200 ppm if available.",
        },
        "medium": {
            "watering_method": "full drench to 10-15% runoff when pot is light",
            "organic_track": {
                "description": "Peak organic bloom feeding. Top dress + teas. Some growers add compost worm castings as a top mulch layer.",
                "inputs": [
                    {
                        "name": "Bloom top dress",
                        "application": "Every 2 weeks",
                        "purpose": "Bat guano (high P), bone meal, langbeinite (0-0-22). Scratch in, water in.",
                    },
                    {
                        "name": "Compost tea (bloom-boosted)",
                        "application": "1x/week",
                        "purpose": "Add bat guano or bloom nutrients to tea. Feeds biology + provides PK.",
                    },
                    {
                        "name": "Worm castings mulch",
                        "application": "1-inch layer on soil surface",
                        "purpose": "Slow-release nutrition + moisture retention + microbial activity.",
                    },
                ],
            },
            "synthetic_track": {
                "description": "Full bloom strength. Feed every other watering. High PK. EC 1.8-2.2 for input solution.",
                "inputs": [],
            },
            "notes": "Wet/dry cycle continues. Flower development in soil is steady but not as fast as hydro — buds develop density over a longer period. Trust the process. Organic soil: the microbial network is delivering a broader spectrum of minerals than any bottle can provide.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Full bloom. Heavy PK. Synthetic: every other watering at 3/4 strength. Organic: soil biology + teas + top dress.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {"name": "Liquid Kool Bloom (synthetic track)", "dose_ml_per_gal": 1.25, "purpose": "PK booster."},
            ],
        },
        "tasks": [
            {
                "name": "Full bloom feeding",
                "description": "Synthetic: 3/4 strength every other watering. Organic: bloom top dress + weekly bloom tea.",
                "interval_days": None,
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
                "description": "Soil grows can have higher humidity at soil surface — check plant base too.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Continue wet/dry cycle",
                "description": "Water to runoff when pot is light. Don't over- or under-water during flower.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor for pests",
                "description": "Fungus gnats, root aphids, spider mites. Soil grows have more pest pressure than hydro.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Buds forming?",
            "Wet/dry cycle consistent?",
            "No bud rot / PM?",
            "No pest problems?",
            "Healthy root system (pot not root-bound)?",
        ],
        "common_problems": [
            {
                "issue": "Slow bud development",
                "cause": "Normal for soil — slower than hydro but often denser/terper final product",
                "solution": "Patience. Soil-grown flower develops differently. Trust the timeline.",
            },
            {
                "issue": "Root aphids (white insects on roots/soil surface)",
                "cause": "Soil-dwelling pest — more common in soil than any other method",
                "solution": "BTI won't work on root aphids. Use Botanigard (Beauveria bassiana) as a drench. Nematodes (Stratiolaelaps). Severe: pyrethrin drench. Root aphids are the most devastating soil pest.",
            },
            {
                "issue": "pH drift from synthetic feeding",
                "cause": "Synthetic salts accumulating in soil",
                "solution": "Check runoff pH. If below 6.0: flush with pH 6.8 water. Organic track almost never has this issue.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation",
                "description": "Remove blocking fan leaves. Max 20% at once.",
                "timing": "Day 1-3 of early flower",
            },
            {"technique": "Lollipopping", "description": "Remove lower 1/3.", "timing": "First week of early flower"},
        ],
        "transition_signals": ["Buds fattening", "Trichomes appearing", "Strong flower aroma"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "See outdoor_soil config."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Separate config.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: manage humidity carefully."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Humidity control critical.",
            },
        },
    },
    # ── 7. MID FLOWER ────────────────────────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Peak Bloom)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Peak bud development. Maximum bloom feeding. Soil-grown buds may be denser and terper than hydro at this stage. Continue wet/dry cycle — don't overwater chasing bigger buds. The soil food web is at full capacity delivering a complex mineral profile.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 78, "target": 76},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 40, "max": 50, "target": 45},
            "vpd_kpa": {"min": 1.4, "max": 1.6, "target": 1.5},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
            "notes": "Peak light. Low humidity. CO2 1200-1500 ppm if available.",
        },
        "medium": {
            "watering_method": "full drench to 10-15% runoff when pot is light",
            "organic_track": {
                "description": "Continue bloom tea + top dress. The soil is at peak biological activity.",
                "inputs": [
                    {
                        "name": "Bloom top dress",
                        "application": "Every 2 weeks",
                        "purpose": "Bat guano, bone meal, langbeinite.",
                    },
                    {"name": "Bloom tea", "application": "1x/week", "purpose": "High-P compost tea."},
                ],
            },
            "synthetic_track": {
                "description": "Full bloom at 75-100% strength. Feed every other watering. PK booster.",
                "inputs": [],
            },
            "notes": "Wet/dry cycle unchanged. Don't increase watering frequency to 'push' buds — soil doesn't work that way. The wet/dry cycle is what drives root health and microbial activity. More water ≠ bigger buds in soil.",
        },
        "nutrients": {
            "strength_pct": 85,
            "approach": "Peak bloom. High PK. Synthetic: 85% every other watering. Organic: soil biology at peak.",
            "flora_micro_ml_per_gal": 2.125,
            "flora_gro_ml_per_gal": 0.5,
            "flora_bloom_ml_per_gal": 2.125,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {"name": "Liquid Kool Bloom (synthetic)", "dose_ml_per_gal": 2.5, "purpose": "PK booster at peak."},
            ],
        },
        "tasks": [
            {
                "name": "Peak bloom feeding",
                "description": "Synthetic: 85% every other watering + PK booster. Organic: top dress + bloom tea.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Daily bud rot inspection",
                "description": "Soil-grown buds can be dense. Check daily.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Support heavy branches",
                "description": "Trellis, yo-yos, stakes.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Continue wet/dry cycle",
                "description": "Don't change what's working.",
                "interval_days": None,
                "priority": "high",
            },
        ],
        "health_checks": ["Buds fattening?", "No bud rot?", "Wet/dry cycle consistent?", "Trichomes developing?"],
        "common_problems": [
            {
                "issue": "Nutrient burn (leaf tips)",
                "cause": "Synthetic: too strong. Organic: too much top dress breaking down at once",
                "solution": "Synthetic: reduce strength. Organic: flush with plain water once, then resume teas only (no top dress for 2 weeks).",
            },
            {
                "issue": "Bud rot in dense colas",
                "cause": "Humidity + density",
                "solution": "Remove affected buds + 1 inch margin. Lower humidity. Improve airflow. Defoliate.",
            },
        ],
        "training": [],
        "transition_signals": ["Buds dense", "Trichomes milky", "Pistils turning orange", "Fan leaves yellowing"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "See outdoor_soil config."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Separate config.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: dehumidification maximum."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Humidity control.",
            },
        },
    },
    # ── 8. LATE FLOWER ───────────────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Buds ripening. Fan leaf yellowing is natural and desired. Reduce feeding. Organic track: stop top dressing, continue light teas. Synthetic: reduce strength.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 78, "target": 75},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.4, "max": 1.8, "target": 1.6},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Cooler nights for color. Low humidity.",
        },
        "medium": {
            "watering_method": "full drench when light, plant drinking less",
            "organic_track": {
                "description": "Stop top dressing. Light compost tea only. Let the plant consume stored nutrients and soil reserves. Natural senescence.",
                "inputs": [
                    {
                        "name": "Light compost tea (no amendments)",
                        "application": "Every 10 days",
                        "purpose": "Keep biology alive but don't push nutrition.",
                    },
                ],
            },
            "synthetic_track": {
                "description": "Reduce to 50% strength. Still feed every other watering. Tapering toward flush.",
                "inputs": [],
            },
            "notes": "Plant drinking less. Wet/dry cycle may extend to 4-6 days. This is normal — the plant is finishing. Don't increase watering. Fan leaf yellowing = natural nutrient fade.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Reducing. Synthetic: 50% every other watering. Organic: light tea only.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 0.3125,
            "flora_bloom_ml_per_gal": 1.25,
            "calmag_ml_per_gal": 0.5,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Reduce feeding",
                "description": "Synthetic: 50%. Organic: teas only, no top dress.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Trichome checks",
                "description": "60-100x loupe. Track milky → amber.",
                "interval_days": 2,
                "priority": "high",
            },
            {"name": "Continue bud rot inspection", "description": "Daily.", "interval_days": 1, "priority": "high"},
            {
                "name": "Plan flush timing",
                "description": "Soil flush debate: organic growers often don't flush at all (soil already clean). Synthetic: flush 7-14 days before harvest.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Trichomes progressing?", "Natural yellowing (not sudden death)?", "No bud rot?"],
        "common_problems": [
            {
                "issue": "Sudden leaf death",
                "cause": "pH lockout or root issue, not natural fade",
                "solution": "Check: gradual yellowing from bottom up = good. Sudden browning or spotting = problem.",
            },
        ],
        "training": [],
        "transition_signals": ["30-50% pistils brown", "Trichomes milky with 5-15% amber", "Heavy yellowing"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "See outdoor_soil config."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Separate config.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: maintain control."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Continue climate control.",
            },
        },
    },
    # ── 9. FLUSH ─────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush (Pre-Harvest)",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Pre-harvest flush. THE GREAT DEBATE: organic soil growers often skip the flush entirely (the soil is already 'clean' — no synthetic salts to flush). Synthetic track: flush with plain water for 7-14 days. The plant consumes stored nutrients either way.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 76, "target": 73},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 17, "max": 30, "target": 26},
            "notes": "Reduced light.",
        },
        "medium": {
            "watering_method": "plain water to runoff when pot is light",
            "organic_track": {
                "description": "OPTIONAL for organic. Many organic growers just water normally — the soil has no synthetic salts to flush. If you want to flush: plain water for the final 7 days.",
                "inputs": [],
            },
            "synthetic_track": {
                "description": "Plain pH'd water only. No nutrients. Water to 20-30% runoff. Flush until runoff EC drops below 0.5.",
                "inputs": [],
            },
            "notes": "Soil flush debate: organic soil often doesn't need flushing (no synthetic salts). Synthetic soil should be flushed. The plant will consume stored nutrients either way — flush just removes excess salts from the root zone. Continue wet/dry cycle during flush.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Plain pH'd water. No nutrients. pH 6.5.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Switch to plain water",
                "description": "pH 6.5 plain water. No nutrients.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor runoff EC (synthetic)",
                "description": "Flush complete when runoff EC <0.5.",
                "interval_days": 2,
                "priority": "high",
            },
            {"name": "Trichome checks daily", "description": "Harvest window.", "interval_days": 1, "priority": "high"},
            {"name": "Bud rot inspection", "description": "Daily.", "interval_days": 1, "priority": "high"},
        ],
        "health_checks": ["Dramatic yellowing?", "Trichomes at target?", "No bud rot?"],
        "common_problems": [
            {
                "issue": "Soil not flushing (runoff EC stays high)",
                "cause": "Soil holds salts more than coco/rockwool",
                "solution": "More volume per flush. Soil flushes slower than soilless media — allow 10-14 days.",
            },
        ],
        "training": [],
        "transition_signals": ["Runoff EC low", "Heavy yellowing", "Trichomes at target"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "See outdoor_soil config."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Separate config.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: maintain control."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Continue.",
            },
        },
    },
    # ── 10. HARVEST ──────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Chop day. Spent soil can be recycled — add to compost, re-amend and reuse (organic), or dispose (synthetic). Living soil can be reused indefinitely with re-amending.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Optional 24-48 hours darkness before chop.",
        },
        "medium": {
            "watering_method": "none",
            "organic_track": {
                "description": "Spent living soil is REUSABLE. Re-amend with compost, dry amendments, and worm castings. Let 'cook' for 2-4 weeks. Indefinitely reusable — the biology only gets better with age.",
                "inputs": [],
            },
            "synthetic_track": {
                "description": "Spent synthetic soil is depleted and salt-laden. Compost it or dispose. Not ideal for reuse without heavy flushing and re-amending.",
                "inputs": [],
            },
            "notes": "Organic living soil gets BETTER with reuse. The mycorrhizal network, beneficial bacteria, and fungal hyphae persist and strengthen. This is the organic advantage — your soil improves every cycle.",
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
                "description": "Confirm target.",
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
                "name": "Process spent soil",
                "description": "Organic: re-amend and reuse. Synthetic: compost or dispose.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Trichomes at target?", "No bud rot found during trim?"],
        "common_problems": [
            {
                "issue": "Bud rot found during trim",
                "cause": "Hidden rot",
                "solution": "Cut away + 1 inch. Salvage clean buds.",
            }
        ],
        "training": [],
        "transition_signals": ["Plant chopped", "Hung for drying", "Soil processed"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "N/A."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "N/A.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "N/A."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "N/A.",
            },
        },
    },
    # ── 11. DRYING ───────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Slow controlled drying. 60°F / 60% humidity / darkness. Soil-grown flower is often slightly less dense than hydro-grown, which can actually make drying easier and more even.",
        "environment": {
            "temp_day_f": {"min": 58, "max": 65, "target": 60},
            "temp_night_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK. 60°F. 60% RH. Gentle airflow not on buds.",
        },
        "medium": {
            "watering_method": "none",
            "organic_track": {"description": "N/A — drying.", "inputs": []},
            "synthetic_track": {"description": "N/A — drying.", "inputs": []},
            "notes": "No soil involvement.",
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
                "cause": "Dense buds + humidity",
                "solution": "Remove moldy buds. Lower humidity.",
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
                "environment_overrides": {"notes": "Too warm. Separate dark room."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Dark room.",
            },
        },
    },
    # ── 12. CURING ───────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Mason jar cure. Soil-grown flower often has superior terpene development during cure. Minimum 2 weeks, ideal 4-8 weeks.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "In-jar 58-62% RH (Boveda 62). Dark, cool.",
        },
        "medium": {
            "watering_method": "none",
            "organic_track": {"description": "N/A — curing.", "inputs": []},
            "synthetic_track": {"description": "N/A — curing.", "inputs": []},
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
            {"name": "Trim and jar", "description": "Jars 75% full.", "interval_days": None, "priority": "high"},
            {
                "name": "Burp jars",
                "description": "2-3x/day week 1, 1x/day week 2.",
                "interval_days": None,
                "priority": "high",
            },
            {"name": "Add Boveda packs", "description": "Boveda 62%.", "interval_days": None, "priority": "medium"},
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
                "notes": "Stable space.",
            },
        },
    },

    # ── 13. STORAGE ──────────────────────────────────────────────────────
    {
        "id": "storage",
        "name": "Long-Term Storage",
        "order": 13,
        "duration_days": {"min": 30, "max": 365, "typical": 180},
        "description": "Post-cure long-term storage. Soil-grown flower — especially organic soil — is prized for complex terpene profiles that continue to develop in early storage. Many connoisseurs consider properly stored organic soil flower the gold standard. Proper storage preserves potency and terpenes for 6-12+ months.",
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
            {"name": "Label and track batches", "description": "Strain, harvest date, storage date, weight, batch number, soil type (organic/synthetic). Commercial: seed-to-sale, FIFO rotation.", "interval_days": None, "priority": "high"},
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

SOIL_EQUIPMENT: list[dict] = [
    # -- Soil/media --
    {
        "name": "Quality potting soil",
        "category": "media",
        "required": True,
        "notes": "Fox Farm Ocean Forest, Happy Frog, BuildASoil 3.0, or homemade super soil. Quality soil is the foundation.",
    },
    {
        "name": "Perlite (for mixing)",
        "category": "media",
        "required": False,
        "notes": "Add 20-30% perlite to heavy soils for drainage. Not needed in already-aerated mixes.",
    },
    {
        "name": "Compost / worm castings",
        "category": "media",
        "required": False,
        "notes": "Organic track: essential for soil biology. Top dress and tea ingredient.",
    },
    {
        "name": "Dry amendments (organic)",
        "category": "media",
        "required": False,
        "notes": "Neem meal, kelp meal, alfalfa meal, bone meal, bat guano, langbeinite. For top dressing. Organic track.",
    },
    # -- Containers --
    {"name": "Solo cups for seedlings", "category": "containers", "required": True, "notes": "Drill drain holes."},
    {
        "name": "1-3 gallon intermediate pots",
        "category": "containers",
        "required": True,
        "notes": "Intermediate step. Fabric or plastic.",
    },
    {
        "name": "3-7 gallon final pots (fabric preferred)",
        "category": "containers",
        "required": True,
        "notes": "Fabric pots for air pruning. 3-gal autos, 5-gal standard, 7-gal large photos.",
    },
    {
        "name": "Saucers / drip trays",
        "category": "containers",
        "required": True,
        "notes": "Catch runoff. Don't let pots sit in standing water.",
    },
    # -- Watering --
    {
        "name": "Watering can",
        "category": "watering",
        "required": True,
        "notes": "For hand watering. Soil doesn't need pumps or drip systems at home scale.",
    },
    # -- Monitoring --
    {
        "name": "pH meter",
        "category": "monitoring",
        "required": True,
        "notes": "Less critical in organic (soil self-buffers) but essential for synthetic track. Soil pH: 6.0-7.0.",
    },
    {
        "name": "EC/TDS meter",
        "category": "monitoring",
        "required": False,
        "notes": "Useful for synthetic track. Less relevant for organic (teas have low EC but high nutrition).",
    },
    {"name": "Jeweler's loupe (60-100x)", "category": "monitoring", "required": True, "notes": "Trichome inspection."},
    # -- Environment --
    {"name": "Grow light (LED preferred)", "category": "environment", "required": True, "notes": "LED or HPS."},
    {"name": "Exhaust fan + carbon filter", "category": "environment", "required": True, "notes": "Odor control."},
    {"name": "Oscillating fan(s)", "category": "environment", "required": True, "notes": "Airflow."},
    {
        "name": "Temperature/humidity controller",
        "category": "environment",
        "required": True,
        "notes": "Climate control.",
    },
    {"name": "Dehumidifier", "category": "environment", "required": True, "notes": "Essential in flower."},
    # -- Nutrients --
    {
        "name": "Base nutrient system (synthetic track)",
        "category": "nutrients",
        "required": False,
        "notes": "GH Flora Trio or equivalent. Only for synthetic track. Organic track uses soil amendments.",
    },
    {"name": "pH Up/Down", "category": "nutrients", "required": True, "notes": "pH 6.0-7.0 for soil."},
    # -- Organic track --
    {
        "name": "Compost tea brewing kit",
        "category": "organic",
        "required": False,
        "notes": "5-gallon bucket + air pump + air stone + compost + molasses. For organic track.",
    },
    {
        "name": "Mycorrhizae inoculant",
        "category": "organic",
        "required": False,
        "notes": "Apply directly to roots at transplant. Xtreme Gardening Mykos or equivalent.",
    },
    # -- Pest control --
    {
        "name": "Yellow sticky traps",
        "category": "pest_control",
        "required": True,
        "notes": "Fungus gnat monitoring. Soil grows WILL have gnat pressure — be ready.",
    },
    {
        "name": "BTI (Mosquito Bits)",
        "category": "pest_control",
        "required": True,
        "notes": "Add to water for fungus gnat larvae control. The #1 soil pest defense.",
    },
    {
        "name": "Diatomaceous earth",
        "category": "pest_control",
        "required": False,
        "notes": "Dust on soil surface for gnat control.",
    },
    {"name": "Neem oil", "category": "pest_control", "required": False, "notes": "Foliar spray for mites, aphids."},
]

# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

SOIL_QUICK_REFERENCE: dict = {
    "ph_range": {
        "min": 6.0,
        "max": 7.0,
        "sweet_spot": 6.5,
        "notes": "Higher than hydro (5.5-6.0). Soil buffers pH naturally — less drift than soilless media.",
    },
    "ec_by_stage": {
        "description": "EC targets for SYNTHETIC track only. Organic track doesn't use EC — teas have low EC but high nutrition.",
        "seedling": 0.0,
        "early_veg": 0.6,
        "late_veg": 1.0,
        "transition": 1.4,
        "early_flower": 1.8,
        "mid_flower": 2.0,
        "late_flower": 1.5,
        "flush": 0.0,
    },
    "watering_guide": {
        "description": "THE fundamental soil skill: the wet/dry cycle.",
        "rule": "Water when the pot is LIGHT. Skip when HEAVY. Lift to check weight.",
        "how_much": "Water until 10-15% runoff from the bottom. Stop. Wait until pot is light again.",
        "frequency_by_stage": {
            "seedling_solo_cup": "Every 2-3 days",
            "early_veg_1_gal": "Every 2-3 days",
            "late_veg_5_gal": "Every 3-5 days",
            "flower_5_gal": "Every 2-4 days",
        },
        "overwatering_signs": "Droopy dark green leaves, slow growth, fungus gnats",
        "underwatering_signs": "Wilting, dry crispy leaves, pot extremely light",
    },
    "organic_vs_synthetic": {
        "organic_pros": [
            "Superior terpene development",
            "Self-buffering pH",
            "Reusable soil",
            "Simpler (just water after setup)",
            "Broader mineral spectrum",
            "Living soil biology",
        ],
        "organic_cons": [
            "Slower nutrient response (2-3 days)",
            "Harder to correct deficiencies fast",
            "Pest attraction (gnats, etc)",
            "Requires planning (top dress takes weeks)",
        ],
        "synthetic_pros": [
            "Fast nutrient response (hours)",
            "Precise control over ratios",
            "Easier deficiency correction",
            "Higher potential yield",
        ],
        "synthetic_cons": [
            "pH drift from salt buildup",
            "Must flush before harvest",
            "Soil degradation over time",
            "No biological benefits",
        ],
        "recommendation": "For beginners: start synthetic (simpler feedback loop). For flavor chasers: go organic. For best of both: start organic soil, supplement with light synthetic if deficiency appears.",
    },
    "soil_pest_management": {
        "fungus_gnats": {
            "threat": "Common",
            "prevention": "Let top inch dry. BTI in every watering. Yellow sticky traps.",
            "treatment": "BTI + diatomaceous earth + nematodes. Severe: hydrogen peroxide drench (3% H2O2, 1:4 ratio with water).",
        },
        "root_aphids": {
            "threat": "Devastating",
            "prevention": "Quarantine new plants. Inspect roots at transplant.",
            "treatment": "Botanigard (Beauveria bassiana), beneficial nematodes (Stratiolaelaps), pyrethrin drench. Root aphids are the hardest soil pest to eliminate.",
        },
        "spider_mites": {
            "threat": "Common",
            "prevention": "Keep humidity up in veg. Inspect undersides of leaves.",
            "treatment": "Neem oil, Spinosad, predatory mites (Phytoseiulus persimilis).",
        },
        "thrips": {
            "threat": "Moderate",
            "prevention": "Blue sticky traps. Inspect new growth.",
            "treatment": "Spinosad, beneficial insects (Orius, Amblyseius cucumeris).",
        },
    },
    "super_soil_recipe": {
        "description": "DIY super soil / water-only soil recipe. Mix and 'cook' (compost) for 30 days before use.",
        "base": "8 large bags (1.5 cu ft) high-quality base soil (Light Warrior, Roots Original)",
        "amendments": [
            "25-50 lbs worm castings",
            "5 lbs bone meal (P)",
            "5 lbs blood meal (N)",
            "5 lbs bat guano",
            "3/4 cup Epsom salt (Mg)",
            "1/2 cup sweet lime (dolomite)",
            "1/2 cup azomite (trace minerals)",
            "2 tbsp humic acid",
        ],
        "cooking": "Mix thoroughly. Moisten. Cover. Let sit 30 days, turning weekly. Microbes need time to break down amendments.",
        "usage": "Place in bottom 1/3 of final pot. Top 2/3 with mild base soil. Roots grow down into hot soil as they mature. Water only — no additional feeding needed for 60-90 days.",
    },
    "golden_rules": [
        "Water when the pot is LIGHT. Skip when heavy. The wet/dry cycle is everything in soil.",
        "Overwatering is the #1 soil mistake. Roots need oxygen. Let the soil dry.",
        "Organic: feed the soil, not the plant. Synthetic: feed the plant directly.",
        "Soil pH: 6.0-7.0. Higher than hydro. Soil naturally buffers.",
        "Soil is slower than hydro. Nutrient response takes 2-3 days. Plan ahead.",
        "Fungus gnats are a soil fact of life. BTI in every watering. Yellow sticky traps always.",
        "Living soil gets BETTER with reuse. The biology strengthens each cycle.",
        "Trust the process. Soil-grown flower often has superior terpenes and flavor.",
        "Synthetic: feed every OTHER watering. Not every watering (that's coco).",
        "The soil IS the nutrient (organic track). Good soil = easy grow.",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING
# ─────────────────────────────────────────────────────────────────────────────

SOIL_TROUBLESHOOTING: list[dict] = [
    {
        "category": "Watering & Root Health",
        "issues": [
            {
                "symptom": "Droopy dark green leaves (overwatering)",
                "cause": "Watering too frequently — soil not drying between waterings",
                "fix": "STOP watering. Wait until pot is noticeably light. Roots need oxygen. This is the #1 soil problem.",
            },
            {
                "symptom": "Wilting dry leaves",
                "cause": "Underwatering — soil too dry",
                "fix": "Water to runoff. If soil is hydrophobic (water runs off surface): add water slowly in stages. Let absorb between pours.",
            },
            {
                "symptom": "Slow growth, root rot smell",
                "cause": "Chronic overwatering leading to anaerobic conditions and root rot",
                "fix": "Transplant to dry soil. Cut dead roots. Treat with Hydroguard. Fix watering schedule.",
            },
        ],
    },
    {
        "category": "Nutrient Issues",
        "issues": [
            {
                "symptom": "Yellowing lower leaves (nitrogen deficiency)",
                "cause": "Soil base nutrition depleted (3-4 weeks in)",
                "fix": "Synthetic: begin feeding. Organic: top dress with high-N amendment (alfalfa, blood meal) + compost tea.",
            },
            {
                "symptom": "pH lockout (multiple deficiency symptoms)",
                "cause": "Synthetic salts accumulating, lowering pH below 6.0",
                "fix": "Check runoff pH. Flush with pH 6.8 water until runoff is 6.0+. Resume feeding at lower strength. Organic track rarely has this issue.",
            },
            {
                "symptom": "Nutrient burn (leaf tip browning)",
                "cause": "Too-strong synthetic feeding, or super soil too 'hot'",
                "fix": "Synthetic: reduce strength. Super soil: transplant to milder soil layer, or flush with plain water.",
            },
        ],
    },
    {
        "category": "Soil Pests",
        "issues": [
            {
                "symptom": "Tiny flies around soil (fungus gnats)",
                "cause": "Moist soil surface — gnats breed in top 1 inch",
                "fix": "BTI (Mosquito Bits) in every watering. Yellow sticky traps. Let top inch dry. Diatomaceous earth on surface. Nematodes for severe infestations.",
            },
            {
                "symptom": "White insects on roots/soil (root aphids)",
                "cause": "Root aphid infestation — the most damaging soil pest",
                "fix": "Botanigard drench (Beauveria bassiana). Beneficial nematodes. Pyrethrin drench for severe cases. May need to discard soil. Quarantine affected plants immediately.",
            },
            {
                "symptom": "Tiny dots on leaf undersides (spider mites)",
                "cause": "Spider mite infestation",
                "fix": "Neem oil spray. Spinosad. Predatory mites (P. persimilis). Raise humidity in veg. Daily inspection.",
            },
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — the single export consumed by the API/frontend
# ─────────────────────────────────────────────────────────────────────────────

SOIL_CONFIG: dict = {
    "grow_type_id": "indoor_soil",
    "version": "1.0.0",
    "stages": SOIL_STAGES,
    "equipment": SOIL_EQUIPMENT,
    "quick_reference": SOIL_QUICK_REFERENCE,
    "troubleshooting": SOIL_TROUBLESHOOTING,
    "total_grow_days": {"min": 105, "max": 210, "typical": 150},
}
