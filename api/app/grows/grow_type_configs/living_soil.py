"""Living Soil — Complete grow type configuration.

Enterprise-grade configuration for no-till, organic living soil growing.
Focus on soil biology, cover crops, and minimal intervention — let the
soil food web do the work.

KEY DIFFERENCES FROM REGULAR SOIL:
  - NO bottled nutrients — soil microbes provide everything
  - NO pH adjustment of water — biology buffers itself
  - Built-in worm population (vermicompost in-situ)
  - Top-dress amendments instead of liquid feeds
  - Mulch layer mandatory (straw, cover crop chop)
  - "Water only" after initial soil build — just add water
  - Takes 30-60 days to BUILD the soil before planting (cook time)
  - Re-use soil cycle after cycle — it gets BETTER with age
  - Cover crops between cycles to maintain biology

Data sources:
  - The Rev (True Living Organics)
  - BuildASoil methodology
  - Elaine Ingham's Soil Food Web approach
  - KIS Organics soil building guides
"""

from __future__ import annotations

LIVING_SOIL_STAGES: list[dict] = [
    # ── 1. SOIL BUILD / COOK ──────────────────────────────────────────────
    {
        "id": "soil_build",
        "name": "Soil Build (Cook)",
        "order": 1,
        "duration_days": {"min": 30, "max": 60, "typical": 45},
        "description": "Mix and 'cook' (thermophilic composting) the living soil. Amendments break down, microbes colonize, worms establish. Soil is ready when it smells earthy (not ammonia) and holds moisture well.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 80, "target": 72},
            "humidity_pct": {"min": 50, "max": 70, "target": 60},
            "notes": "Keep soil moist (wrung-out sponge test) in a warm area. Cover with tarp or burlap. Turn every 7-10 days for aeration.",
        },
        "soil": {
            "ph": {"min": 6.2, "max": 7.0, "target": 6.5},
            "moisture": "60-70% field capacity (wrung-out sponge)",
            "temperature_f": {
                "min": 90,
                "max": 140,
                "target": 120,
                "notes": "Internal temp during hot composting. Thermophilic phase kills pathogens and weed seeds.",
            },
            "notes": "Base mix: 1/3 sphagnum peat or coco coir, 1/3 aeration (pumice/perlite/rice hulls), 1/3 compost (worm castings + thermal compost). Amend with: neem/karanja meal, kelp meal, crab meal, gypsum, basalt rock dust, malted barley.",
        },
        "amendments": {
            "base_recipe_per_cf": [
                {
                    "name": "Sphagnum peat or coco coir",
                    "amount": "1/3 volume",
                    "purpose": "Water retention, base structure",
                },
                {
                    "name": "Pumice or perlite",
                    "amount": "1/3 volume",
                    "purpose": "Aeration, drainage, permanent structure",
                },
                {
                    "name": "High-quality compost + EWC",
                    "amount": "1/3 volume",
                    "purpose": "Biology, slow-release nutrients",
                },
                {"name": "Neem meal", "amount": "1/2 cup/cf", "purpose": "Nitrogen, pest deterrent, fungal food"},
                {"name": "Kelp meal", "amount": "1/2 cup/cf", "purpose": "Potassium, growth hormones, trace minerals"},
                {
                    "name": "Crab/crustacean meal",
                    "amount": "1/2 cup/cf",
                    "purpose": "Chitin (triggers plant defense), calcium, nitrogen",
                },
                {"name": "Gypsum", "amount": "1/2 cup/cf", "purpose": "Calcium + sulfur without changing pH"},
                {
                    "name": "Basalt rock dust",
                    "amount": "2 cups/cf",
                    "purpose": "Trace minerals, paramagnetism, slow-release silica",
                },
                {
                    "name": "Malted barley grain (whole)",
                    "amount": "1/4 cup/cf",
                    "purpose": "Enzymes, growth hormones when activated by moisture",
                },
            ],
            "notes": "Mix thoroughly, moisten to 60% field capacity, cover, and let cook 30-60 days. Turn every 7-10 days. Ready when temp drops to ambient and smells like forest floor.",
        },
        "tasks": [
            {
                "name": "Check soil temperature",
                "description": "Insert compost thermometer 12 inches deep. Should be 90-140°F during active cooking, dropping to ambient when done.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Check moisture",
                "description": "Squeeze handful — should hold together without dripping. Add water if crumbly/dry.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Turn/aerate soil",
                "description": "Mix pile thoroughly to distribute heat, moisture, and microbes evenly.",
                "interval_days": 10,
                "priority": "medium",
            },
            {
                "name": "Smell test",
                "description": "Ammonia = still cooking. Sweet earthy smell = getting close. Sour = anaerobic (needs turning).",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Soil temperature declining toward ambient?",
            "Earthy forest-floor smell (no ammonia)?",
            "Moisture level consistent?",
            "Visible fungal threads (white mycelium)?",
            "Worms present and active (if added)?",
        ],
        "common_problems": [
            {
                "issue": "Ammonia smell persists",
                "cause": "Too much nitrogen, not enough carbon, or too wet",
                "solution": "Add more carbon (straw, leaves). Turn for aeration. Reduce moisture if soggy.",
            },
            {
                "issue": "Soil not heating up",
                "cause": "Not enough nitrogen, too dry, or pile too small",
                "solution": "Add nitrogen source (alfalfa meal). Moisten. Pile needs to be at least 3x3x3 ft to self-heat.",
            },
            {
                "issue": "Foul/sour smell",
                "cause": "Anaerobic conditions — too wet, too compacted",
                "solution": "Turn immediately. Add perlite for aeration. Let surface dry slightly.",
            },
            {
                "issue": "Fungus gnats during cook",
                "cause": "Normal — attracted to decomposing matter",
                "solution": "Not a concern during cook. They'll regulate once soil matures. Yellow sticky traps if excessive.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Internal temperature has dropped to ambient (no more self-heating)",
            "Sweet earthy smell — no ammonia, no sour odors",
            "Visible white fungal mycelium throughout",
            "Worms active throughout the pile",
            "Been cooking for minimum 30 days",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Cook soil in a shaded area. Rain cover prevents waterlogging. Sun exposure dries surface too fast."
                },
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse heat accelerates cooking. May be ready in 25-30 days vs 45 days outdoors."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 2. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 2,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Germinate seeds in moist paper towel or directly in a small container of the living soil mix. No nutrients needed — seed contains all energy.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Darkness until taproot emerges. Paper towel method or direct sow into moist living soil (1/4 inch deep).",
        },
        "soil": {
            "notes": "If direct sowing, use top 1 inch of plain seedling mix or lightly amended living soil. Full-strength living soil can burn seedlings."
        },
        "tasks": [
            {
                "name": "Check germination progress",
                "description": "Look for taproot emergence (paper towel) or sprout breaking soil surface (direct sow).",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Maintain moisture",
                "description": "Keep medium moist but not soaking. Spray with plain water if needed.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Seed cracked and taproot visible?",
            "Medium moist but not waterlogged?",
            "Temperature 75-82°F?",
        ],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Too cold, too wet, or old seed",
                "solution": "Use heat mat. Ensure medium is moist not soggy. Try new seed after 7 days.",
            },
            {
                "issue": "Damping off",
                "cause": "Overwatering, fungal pathogens",
                "solution": "Less water. Sprinkle cinnamon or chamomile tea on soil surface (natural antifungals).",
            },
        ],
        "training": [],
        "transition_signals": ["Cotyledons open and reaching for light", "Taproot established"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Start indoors for consistent temperature. Transplant to outdoor living soil bed after seedling stage."
                },
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse warmth is ideal for germination."},
                "extra_tasks": [],
            },
        },
    },
    # ── 3. SEEDLING ───────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 3,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "First true leaves develop. Transplant into final living soil container or bed. Plant establishes mycorrhizal connections with soil biology.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 60, "max": 75, "target": 68},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 300, "target": 200},
            "light_dli": {"min": 6, "max": 19, "target": 13},
            "notes": "Gentle light. Add mycorrhizal inoculant directly to root zone at transplant — this is CRITICAL for living soil performance.",
        },
        "soil": {
            "ph": "Self-buffering — do NOT adjust",
            "moisture": "Keep evenly moist. Living soil should never fully dry out (kills microbes) or be waterlogged (kills aerobic biology).",
            "notes": "Transplant into final container with living soil. Add handful of worm castings in transplant hole. Dust roots with mycorrhizal powder.",
        },
        "watering": {
            "method": "Plain water only — dechlorinated or rain water",
            "ph_adjustment": "NONE — biology buffers pH. Adjusting pH kills microbes.",
            "frequency": "When top 1-2 inches dry. Living soil containers usually every 2-4 days for seedlings.",
            "notes": "NEVER use chlorinated tap water directly — chlorine kills beneficial microbes. Let sit 24h, use carbon filter, or collect rain water.",
        },
        "tasks": [
            {
                "name": "Transplant to living soil",
                "description": "Place in final container with cooked living soil. Add mycorrhizal inoculant to root zone. Water in gently.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Water with plain dechlorinated water",
                "description": "Water when top 1-2 inches dry. No nutrients, no pH adjustment.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Apply mulch layer",
                "description": "Add 1-2 inch layer of straw, rice hulls, or cover crop chop to soil surface. Keeps moisture, feeds biology, prevents top crust.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Check soil moisture",
                "description": "Insert finger 2 inches deep. Should be moist but not wet. Living soil microbes die if too dry or waterlogged.",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Seedling upright and growing new leaves?",
            "No signs of nutrient burn (hot soil)?",
            "Soil surface has mulch layer?",
            "Moisture even throughout (not pooling)?",
        ],
        "common_problems": [
            {
                "issue": "Nutrient burn on seedling",
                "cause": "Soil too hot (not fully cooked) or too concentrated for young roots",
                "solution": "Top layer should be milder. Let soil cook longer next time. Water more frequently to dilute.",
            },
            {
                "issue": "Fungus gnats",
                "cause": "Organic matter in soil attracts them",
                "solution": "Yellow sticky traps. Add layer of diatomaceous earth on surface. Nematodes (Sf) drench. Don't overwater.",
            },
            {
                "issue": "Slow growth",
                "cause": "Soil biology still establishing relationship with roots",
                "solution": "Normal — living soil starts slow but accelerates dramatically in veg. Ensure mycorrhizae was added.",
            },
        ],
        "training": [],
        "transition_signals": [
            "3-4 sets of true leaves",
            "Roots starting to establish (new growth accelerating)",
            "Plant height 4-6 inches",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Harden off seedling over 5-7 days before placing in outdoor living soil bed."
                },
                "extra_tasks": [
                    {
                        "name": "Harden off",
                        "description": "Gradually increase outdoor time: 2h day 1, 4h day 2, etc. Full sun by day 5-7.",
                        "interval_days": 1,
                        "priority": "high",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse transition is easier — already partial outdoor environment."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 4. VEGETATIVE ─────────────────────────────────────────────────────
    {
        "id": "vegetative",
        "name": "Vegetative",
        "order": 4,
        "duration_days": {"min": 21, "max": 56, "typical": 35},
        "description": "Explosive growth phase. Living soil kicks into gear — mycorrhizal network delivers nutrients on demand. Top-dress amendments every 2-3 weeks for sustained feeding. This is where 'water only' living soil shines.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 700, "target": 550},
            "light_dli": {"min": 25, "max": 45, "target": 35},
            "notes": "Plants may seem to grow slowly at first then EXPLODE once mycorrhizal network is established (usually week 2-3 of veg). Patience — biology takes time but delivers.",
        },
        "soil": {
            "ph": "Self-buffering — 6.2-7.0 naturally",
            "notes": "Top-dress with amendments every 2-3 weeks. Worm castings, kelp meal, neem meal. Scratch into top inch under mulch. Water in gently.",
        },
        "watering": {
            "method": "Plain dechlorinated water. Optional: aloe vera, coconut water, or compost tea as biological boosts.",
            "frequency": "Every 2-4 days depending on plant size and container size. Living soil in 10+ gallon pots may only need water every 3-5 days.",
            "notes": "Some growers add weekly compost tea or aloe vera water (1 tsp aloe per gallon) for growth boost. NOT required — just a bonus.",
        },
        "top_dress_schedule": [
            {
                "week": 2,
                "amendments": "Worm castings (1/2 inch layer) + malted barley (tablespoon, crushed)",
                "purpose": "Fresh biology + enzymes",
            },
            {
                "week": 4,
                "amendments": "Neem meal + kelp meal (1 tbsp each, scratched in)",
                "purpose": "Nitrogen + potassium + pest deterrent",
            },
            {
                "week": 6,
                "amendments": "Worm castings + crab meal (1 tbsp)",
                "purpose": "Biology refresh + calcium + chitin immune boost",
            },
        ],
        "tasks": [
            {
                "name": "Water (plain, dechlorinated)",
                "description": "Water when top 2 inches dry. Drench until 10-20% runoff. Use rain water, dechlorinated tap, or RO.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Top-dress amendments",
                "description": "Every 2-3 weeks: add worm castings + kelp/neem meal. Scratch into top inch under mulch layer. Water in.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Maintain mulch layer",
                "description": "Keep 1-2 inch mulch (straw, leaves, cover crop chop). Replenish if thin spots appear.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Compost tea (optional)",
                "description": "Brew actively aerated compost tea (AACT) for 24-48h. Apply as soil drench for biology boost.",
                "interval_days": 14,
                "priority": "low",
            },
            {
                "name": "Train canopy",
                "description": "LST, topping, or SCROG. Living soil plants are vigorous — training helps manage growth.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Check for pests",
                "description": "Inspect undersides of leaves. Living soil may attract fungus gnats — use yellow sticky traps and beneficial nematodes.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Leaves vibrant green with healthy new growth?",
            "Soil surface has visible life (worms, springtails, mites)?",
            "Mulch layer intact?",
            "No pest pressure beyond manageable?",
            "Growth rate accelerating (mycorrhizal network established)?",
        ],
        "common_problems": [
            {
                "issue": "Slow growth compared to synthetic",
                "cause": "Normal — living soil ramps up, doesn't start at max",
                "solution": "Patience. Once mycorrhizal network is established (week 2-3), growth rate often matches or exceeds synthetic.",
            },
            {
                "issue": "Fungus gnats",
                "cause": "Organic matter in soil",
                "solution": "Yellow sticky traps, Bacillus thuringiensis (Bti) drench, beneficial nematodes (Steinernema feltiae), layer of diatomaceous earth on surface.",
            },
            {
                "issue": "Leaf yellowing (nitrogen deficiency)",
                "cause": "Soil not fully cooked, or plant outpacing biology",
                "solution": "Top-dress worm castings + neem meal. Apply compost tea. In emergency: dilute fish hydrolysate (2ml/gal).",
            },
            {
                "issue": "Salt buildup on surface (white crust)",
                "cause": "Using tap water with high TDS",
                "solution": "Switch to rain water or RO. Scrape off crust gently. Flush with extra plain water.",
            },
        ],
        "training": [
            {
                "name": "LST",
                "when": "Once 5-6 nodes",
                "description": "Bend main stem to open canopy. Living soil plants respond well — steady nutrition prevents stress.",
            },
            {
                "name": "Topping",
                "when": "5th-6th node",
                "description": "Top for bushier growth. Living soil recovers fast from topping due to robust biology.",
            },
            {
                "name": "SCROG",
                "when": "Canopy reaches net",
                "description": "Living soil + SCROG is a popular combination for even canopy and maximum light utilization.",
            },
        ],
        "transition_signals": [
            "Canopy 50-60% full",
            "Plant well-established and growing vigorously",
            "Healthy root zone (worms active at surface when watering)",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "light_hours": "Natural photoperiod (14+ hours = veg)",
                    "notes": "Outdoor living soil beds are legendary. Raised beds with living soil can be no-till for years. Cover crop between cycles.",
                },
                "extra_tasks": [
                    {
                        "name": "Pest patrol",
                        "description": "Outdoor = more pest pressure. Companion planting (basil, marigolds) helps. BT spray for caterpillars.",
                        "interval_days": 3,
                        "priority": "medium",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse living soil combines best of both: natural light + protection from weather and pests."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 5. FLOWERING ──────────────────────────────────────────────────────
    {
        "id": "flowering",
        "name": "Flowering",
        "order": 5,
        "duration_days": {"min": 49, "max": 77, "typical": 63},
        "description": "Light flip to 12/12. Plants shift to bud production. Top-dress with phosphorus/potassium-heavy amendments. Living soil terpene production is often superior to synthetic grows due to diverse mineral availability.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 79, "target": 75},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 40, "max": 55, "target": 45},
            "vpd_kpa": {"min": 1.0, "max": 1.5, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 1000, "target": 800},
            "light_dli": {"min": 25, "max": 43, "target": 35},
            "notes": "Lower humidity to prevent bud rot. Living soil buds are often more aromatic due to diverse micronutrient availability. No flush needed — soil biology self-regulates.",
        },
        "soil": {
            "notes": "Top-dress shifts to P/K heavy amendments. Worm castings + bone meal + langbeinite. Maintain mulch. Keep soil biology alive through harvest."
        },
        "watering": {
            "method": "Plain dechlorinated water. Continue exactly as in veg.",
            "frequency": "Every 2-4 days. Plants drink more in flower due to transpiration.",
            "notes": "NO FLUSH NEEDED for living soil. The soil biology self-cleanses. Flushing destroys the soil food web. Just water normally through harvest.",
        },
        "top_dress_schedule": [
            {
                "week": 1,
                "amendments": "Worm castings + bone meal (1 tbsp) + kelp",
                "purpose": "Transition support + phosphorus ramp-up",
            },
            {
                "week": 3,
                "amendments": "Langbeinite (1 tbsp) or wood ash + worm castings",
                "purpose": "Potassium + sulfur for flower/terpene development",
            },
            {
                "week": 5,
                "amendments": "Bone meal + gypsum + worm castings",
                "purpose": "Peak P/K demand + calcium for cell walls",
            },
            {
                "week": 7,
                "amendments": "Light worm castings only",
                "purpose": "Maintenance biology — don't overfeed late flower",
            },
        ],
        "tasks": [
            {
                "name": "Water (plain dechlorinated)",
                "description": "Continue regular watering. No flush, no pH adjustment, no additives.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Top-dress for flower",
                "description": "Shift amendments to P/K heavy: bone meal, langbeinite, wood ash. Every 2 weeks.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Monitor bud development",
                "description": "Check trichomes with loupe. Watch for bud rot.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Maintain airflow",
                "description": "Defoliate selectively. Good airflow prevents bud rot.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Check soil life",
                "description": "Worms still active? Mulch decomposing? Biology should remain active through flower.",
                "interval_days": 7,
                "priority": "low",
            },
        ],
        "health_checks": [
            "Buds swelling and frosty?",
            "No bud rot?",
            "Soil still alive (worms, fungal threads)?",
            "No nutrient deficiency (some late-flower yellowing is NORMAL senescence)?",
            "Terpene smell developing strongly?",
        ],
        "common_problems": [
            {
                "issue": "Phosphorus deficiency (purple stems)",
                "cause": "High P demand in flower, cold temps lock out P",
                "solution": "Top-dress bone meal. Ensure night temps stay above 60°F. Fish hydrolysate (low dose) in emergency.",
            },
            {
                "issue": "Bud rot",
                "cause": "Dense buds + humidity",
                "solution": "Lower humidity. Defoliate around buds. Remove infected buds completely. Increase fan speed.",
            },
            {
                "issue": "Premature yellowing (not senescence)",
                "cause": "Soil N running low, biology struggling",
                "solution": "Top-dress worm castings. One dose of fish hydrolysate (2ml/gal). Should only happen in undersized containers.",
            },
        ],
        "training": [
            {
                "name": "Defoliation",
                "when": "Day 21 and 42",
                "description": "Remove fan leaves blocking buds and reducing airflow. Important for bud rot prevention.",
            },
            {
                "name": "Lollipop",
                "when": "First 2 weeks of flower",
                "description": "Remove lower growth that won't produce quality buds.",
            },
        ],
        "transition_signals": [
            "Trichomes milky with some amber",
            "Pistils receding and darkening",
            "Fan leaves yellowing naturally (senescence)",
            "Calyxes swelling",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor living soil flower is spectacular. Rain protection for buds is essential. Mulch layer keeps soil biology alive even as temps drop."
                },
                "extra_tasks": [
                    {
                        "name": "Rain cover",
                        "description": "Protect buds from rain. Temporary hoop house or canopy.",
                        "interval_days": 1,
                        "priority": "high",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Vent for humidity control. Greenhouse living soil = terpene powerhouse."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 6. DRYING ─────────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 6,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Hang whole plants or branches in dark, cool, controlled environment. Living soil buds often dry slightly faster due to lower retained moisture from lack of synthetic salts.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "light_hours": 0,
            "notes": "Complete darkness. 60/60 rule (60°F, 60% RH) for best terpene preservation.",
        },
        "tasks": [
            {
                "name": "Check drying conditions",
                "description": "Maintain 60-65°F and 55-62% RH. Adjust dehumidifier/AC as needed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Stem snap test",
                "description": "Small stems should snap cleanly. Main stems slightly flexible. Takes 7-14 days.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Maintain living soil for next cycle",
                "description": "Don't let soil dry out. Add cover crop seeds. The soil gets BETTER with each cycle.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Drying room at proper temp/humidity?",
            "No mold on buds?",
            "Living soil being maintained for next run?",
        ],
        "common_problems": [
            {
                "issue": "Too fast drying",
                "cause": "Humidity too low",
                "solution": "Raise humidity. Hang whole plants (not trimmed) for slower dry.",
            },
            {
                "issue": "Mold",
                "cause": "Humidity too high or dense untrimmed buds",
                "solution": "Lower humidity. Improve airflow. Check dense colas daily.",
            },
        ],
        "training": [],
        "transition_signals": ["Small stems snap", "Buds feel dry outside, slightly moist inside"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Always dry indoors in controlled environment."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Dry indoors. Greenhouse not suitable for drying."},
                "extra_tasks": [],
            },
        },
    },
    # ── 7. CURING ─────────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 7,
        "duration_days": {"min": 14, "max": 90, "typical": 30},
        "description": "Mason jar cure. Living soil buds typically develop exceptional flavor during cure due to diverse terpene profiles from full-spectrum mineral availability.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "light_hours": 0,
            "notes": "Dark, cool. Boveda 62% packs help maintain consistency.",
        },
        "tasks": [
            {
                "name": "Burp jars",
                "description": "Open 15-30 min daily for first 2 weeks. Then 2-3 times per week.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check humidity",
                "description": "58-62% in jar. Use mini hygrometer.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Sow cover crop on living soil",
                "description": "Plant clover, rye, or mix on resting living soil. Feeds biology between cycles.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Jar humidity correct?", "No mold/ammonia smell?", "Living soil resting with cover crop?"],
        "common_problems": [
            {"issue": "Ammonia smell", "cause": "Too wet when jarred", "solution": "Remove, dry 12-24h more, re-jar."},
            {
                "issue": "Hay smell persisting",
                "cause": "Chlorophyll still breaking down",
                "solution": "Continue curing 2-4 more weeks.",
            },
        ],
        "training": [],
        "transition_signals": ["Smooth smoke", "Terpene profile fully developed", "No harshness or hay smell"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Cure indoors always."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Cure indoors always."}, "extra_tasks": []},
        },
    },
]

LIVING_SOIL_CONFIG: dict = {
    "id": "living_soil",
    "name": "Living Soil (No-Till Organic)",
    "description": "Organic, biology-driven growing. Build a living soil ecosystem once, reuse forever. Water-only after initial build. Superior terpene profiles and sustainability.",
    "category": "soil",
    "difficulty": "intermediate",
    "stages": LIVING_SOIL_STAGES,
    "equipment": [
        "Large fabric pots (10-20 gallon minimum, 30+ ideal for no-till)",
        "Sphagnum peat or coco coir (base)",
        "Pumice or perlite (aeration)",
        "High-quality compost + worm castings",
        "Amendment kit (neem, kelp, crab, gypsum, rock dust, malted barley)",
        "Mulch material (straw, rice hulls, or cover crop seed)",
        "Compost thermometer",
        "Dechlorination method (carbon filter, open bucket 24h, or rain barrel)",
        "Worms (red wigglers — optional but highly recommended)",
        "Mycorrhizal inoculant (Great White, Dynomyco, etc.)",
        "Yellow sticky traps (fungus gnat management)",
        "Compost tea brewer (optional — bucket + air pump + compost)",
        "Cover crop seed mix (clover, rye, fenugreek)",
    ],
    "key_principles": [
        "Feed the SOIL, not the plant — microbes deliver nutrients on demand",
        "NEVER add synthetic fertilizers — they kill soil biology",
        "NEVER pH your water — biology self-buffers. pH adjustment kills microbes",
        "NEVER flush — destroys the soil food web. No flush needed with organic",
        "Use dechlorinated water ONLY — chlorine is antimicrobial (it's designed to kill biology)",
        "Soil gets BETTER with each cycle — never throw it away",
        "Mulch is mandatory — protects surface biology from light and evaporation",
        "Patience — living soil starts slow but produces superior results",
        "Cover crop between cycles to maintain and improve biology",
        "Top-dress amendments every 2-3 weeks rather than liquid feeding",
    ],
}
