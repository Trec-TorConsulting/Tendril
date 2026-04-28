"""Outdoor Soil — Complete grow type configuration.

Enterprise-grade configuration for outdoor in-ground soil growing — the most
natural and oldest method of cultivation.  Outdoor soil growing is fundamentally
different from indoor: nature controls the schedule, weather dictates decisions,
and the scale can be massive.

The defining features are **GDD-based stage transitions** (Growing Degree Days
replace calendar days — the plant follows heat accumulation, not the calendar),
**natural photoperiod triggering** (the sun controls flowering — no flip switch),
**companion planting** (beneficial plants that deter pests and improve soil),
**weather integration** (rain, wind, frost, hail — outdoor growers fight nature),
**in-ground soil building** (amending native soil vs containers), and **seasonal
planning** (one shot per year — outdoor grows are single-harvest annual cycles).

Key Outdoor Soil differences from every other method:
  - GDD (Growing Degree Days) replaces calendar days for stage transitions
  - Natural photoperiod triggers flowering — no 12/12 switch
  - Weather is uncontrollable — rain, wind, frost, hail, drought
  - Companion planting provides pest control, nitrogen fixation, and more
  - Scale can be enormous (100+ plants in ground vs 4-8 indoors)
  - One harvest per year (outdoor season) — no perpetual harvests
  - In-ground soil must be built over time (cover crops, amendments, compost)
  - Wildlife pressure: deer, rabbits, birds, insects at scale
  - Light dep (light deprivation) can force early flowering
  - Hardiness zones determine growing season length
  - Soil testing is essential for in-ground growing
  - Irrigation is different: drip lines, soaker hoses, rain dependence

Supports three environment types (matching Tent.environment_type):
  - outdoor (default — in-ground, full sun, natural photoperiod)
  - greenhouse (with light dep for flowering control)
  - indoor (not applicable — see indoor soil config)

Data sources:
- USDA Plant Hardiness Zone Map
- Growing Degree Day models for cannabis (base 50°F)
- Companion planting research (Rodale Institute)
- Regenerative agriculture practices
- Cannabis-specific outdoor growing guides
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in an Outdoor Soil grow
# ─────────────────────────────────────────────────────────────────────────────

OUTDOOR_SOIL_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3, "gdd_trigger": None},
        "description": "Start seeds INDOORS regardless of outdoor plan. Outdoor germination is unreliable — temperature fluctuations, pests, moisture inconsistency. Germinate in controlled conditions, then harden off seedlings before moving outside.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "INDOORS. Heat mat, humidity dome. Seeds need consistent 78°F.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": None,
            "companion_plants": [],
            "weather_triggers": [],
            "notes": "Start in solo cups with quality seed-starting mix indoors. While seeds germinate: prepare the outdoor site (soil testing, amendment, bed prep). The in-ground soil needs weeks of prep.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None — seeds contain all energy. Use seed-starting mix.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Start seeds indoors",
                "description": "Soak 12-24 hours, plant in pre-moistened seed-starting mix in solo cups. Heat mat at 78°F. Humidity dome.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Prepare outdoor site",
                "description": "While seeds germinate: test native soil pH and nutrients (soil test kit or send to lab). Begin amending: compost, worm castings, perlite, lime if needed. Build raised beds or prepare in-ground holes. This takes 2-6 weeks to 'cook.'",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Plan companion planting",
                "description": "Decide on companion plants: basil (repels aphids/mites), marigolds (nematodes), clover (nitrogen fixation), lavender (pollinators + pest deterrent). Start companion plants at the same time.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Check local last frost date",
                "description": "Plants cannot go outside until 2 weeks AFTER last frost date. Know your zone.",
                "interval_days": None,
                "priority": "high",
            },
        ],
        "health_checks": ["Seeds cracking?", "Indoor conditions stable?", "Outdoor site prep underway?"],
        "common_problems": [
            {
                "issue": "Starting seeds too early",
                "cause": "Excited grower starts in January for a June plant-out",
                "solution": "Count backward from last frost date. Start seeds 4-6 weeks before last frost. Starting too early = leggy, root-bound seedlings.",
            },
        ],
        "training": [],
        "transition_signals": ["Taproot visible", "Sprout emerging"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Start indoors. Always."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor germination.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse germination works with heat mat."},
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
        "duration_days": {"min": 14, "max": 28, "typical": 21, "gdd_trigger": None},
        "description": "Seedlings develop indoors under grow lights. Longer seedling phase than indoor grows — you're waiting for weather to be safe. Begin hardening off 1-2 weeks before target plant-out date. Hardening off = gradually exposing seedlings to outdoor conditions.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 60, "max": 75, "target": 65},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 200, "max": 400, "target": 300},
            "light_dli": {"min": 13, "max": 26, "target": 19},
            "notes": "Indoor grow lights. Keep on 18/6 or 20/4 schedule. Seedlings need consistent light to prevent premature flowering when moved outside.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": None,
            "companion_plants": [],
            "weather_triggers": [
                {
                    "trigger": "last_frost_date",
                    "action": "Begin hardening off 2 weeks before safe plant-out date (2 weeks after last frost)",
                },
            ],
            "notes": "Seedlings in solo cups or small pots indoors. Continue preparing outdoor site. Hardening off protocol: Day 1-3: 2 hours outside in shade. Day 4-6: 4 hours with some sun. Day 7-9: 6 hours full sun. Day 10-14: full day outside, bring in at night. Then plant out.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Seed-starting mix provides base nutrition. No supplemental feeding yet.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Grow seedlings under lights",
                "description": "18/6 light schedule. Prevent stretch. Build strong stems.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Begin hardening off",
                "description": "2 weeks before plant-out: gradually expose to outdoor conditions. Increase sun exposure daily. Reduce watering slightly to toughen stems.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Continue site prep",
                "description": "Final amendments. Dig planting holes 2x2x2 feet minimum. Fill with amended soil mix. Water in.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Install companion plants",
                "description": "Plant basil, marigolds, clover around planned cannabis locations. Established companions before cannabis arrives.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Install irrigation",
                "description": "Drip lines, soaker hoses, or irrigation plan. Outdoor plants need reliable water.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Seedlings healthy and stocky (not stretched)?",
            "Hardening off on schedule?",
            "Outdoor site prepared?",
            "Irrigation installed?",
        ],
        "common_problems": [
            {
                "issue": "Seedlings stretching indoors",
                "cause": "Light too far away or too dim",
                "solution": "Lower light. Increase intensity. Brush stems gently daily to stimulate thickness.",
            },
            {
                "issue": "Premature flowering after moving outside",
                "cause": "Outdoor day length shorter than indoor 18/6 triggered flowering",
                "solution": "Don't move outside until day length is 14+ hours. Supplement with outdoor lights for first 1-2 weeks if needed.",
            },
        ],
        "training": [],
        "transition_signals": [
            "2-4 sets of true leaves",
            "Hardening off complete",
            "Night temps consistently above 50°F",
            "2+ weeks past last frost",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Seedlings indoors, hardening off into outdoor conditions."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Harden off before plant-out.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Seedlings can stay in greenhouse. Still harden off if moving to open ground."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse seedlings.",
            },
        },
    },
    # ── 3. EARLY VEGETATIVE ──────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Vegetative (Plant-Out)",
        "order": 3,
        "duration_days": {
            "min": 21,
            "max": 42,
            "typical": 30,
            "gdd_trigger": {"accumulated": 200, "notes": "200 GDD accumulated from plant-out date"},
        },
        "description": "PLANT OUT into prepared ground. The plant transitions from indoor conditions to full outdoor growing. Roots expand into native/amended soil. Growth accelerates dramatically with full sun (1000+ PPFD, 40+ DLI). Outdoor plants can grow 2-6 inches per DAY in ideal conditions.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 90, "target": 78},
            "temp_night_f": {"min": 50, "max": 70, "target": 60},
            "humidity_pct": {"min": 40, "max": 80, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 2.0, "target": 1.2},
            "light_hours": {"min": 14, "max": 16, "notes": "Natural photoperiod. Long days keep plant in veg."},
            "light_ppfd": {
                "min": 800,
                "max": 2000,
                "target": 1200,
                "notes": "Full sun. Way more than any indoor light.",
            },
            "light_dli": {
                "min": 40,
                "max": 65,
                "target": 50,
                "notes": "Full sun outdoor DLI is 40-65 — double indoor targets.",
            },
            "notes": "Full sun outdoors. The plant now receives more light than any indoor setup can provide. Growth will explode. Temperature and humidity are uncontrolled — the plant must adapt.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": {
                "notes": "Determines growing season length. Zone 5: ~150 days. Zone 7: ~200 days. Zone 9+: ~270 days."
            },
            "companion_plants": [
                {
                    "name": "Basil",
                    "benefit": "Repels aphids, whiteflies, spider mites. Aromatic companion.",
                    "spacing": "12 inches from cannabis",
                },
                {
                    "name": "Marigolds",
                    "benefit": "Repels nematodes, whiteflies. Traps aphids (sacrificial).",
                    "spacing": "Around perimeter",
                },
                {
                    "name": "White clover (ground cover)",
                    "benefit": "Nitrogen fixation. Living mulch. Retains moisture.",
                    "spacing": "Between plants",
                },
                {"name": "Lavender", "benefit": "Attracts pollinators. Repels fleas, moths.", "spacing": "Perimeter"},
            ],
            "weather_triggers": [
                {
                    "trigger": "heavy_rain",
                    "action": "Check drainage. Amend with perlite if pooling. Cover if prolonged.",
                },
                {
                    "trigger": "heat_wave_above_95f",
                    "action": "Mulch heavily. Water early morning. Shade cloth if sustained.",
                },
                {"trigger": "unexpected_cold_below_50f", "action": "Cover with row cover or frost cloth overnight."},
            ],
            "notes": "In-ground planting. Dig hole 2x2x2 feet. Fill with amended soil mix (native soil + compost + perlite + worm castings + dry amendments). Mulch 3-4 inches around plant (straw, wood chips). Mulch retains moisture, suppresses weeds, and regulates soil temp. Install drip irrigation.",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "In amended ground: soil provides most nutrition. Supplement with compost tea 1-2x/month. If using synthetic: very light feeding (1/4 strength) through drip.",
            "flora_micro_ml_per_gal": 0.625,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 0.3125,
            "calmag_ml_per_gal": 0,
            "supplements": [
                {
                    "name": "Mycorrhizae",
                    "dose_ml_per_gal": None,
                    "purpose": "Apply to root ball at plant-out. Establishes critical fungal network for outdoor growing.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Plant out",
                "description": "Transplant hardened seedling into prepared ground hole. Water in heavily. Apply mycorrhizae to root ball. Mulch 3-4 inches around plant. Install drip emitter.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Install plant support",
                "description": "Stake or cage immediately. Outdoor plants get HUGE — support from day 1.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Mulch",
                "description": "3-4 inches of straw or wood chip mulch. Retains moisture, suppresses weeds, feeds soil biology.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Establish irrigation schedule",
                "description": "Drip irrigation: 1-2 gallons per plant per day initially. Adjust based on rain and heat. Deep infrequent watering > frequent shallow watering.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor for transplant shock",
                "description": "Wilting is normal for 2-3 days after plant-out. If persistent: shade cloth for a few days.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Begin training",
                "description": "Start LST, topping once established (2 weeks after plant-out). Outdoor plants respond well to aggressive training.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Install pest barriers",
                "description": "Deer fencing if in area. Chicken wire for rabbits. Row cover available for emergency.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Plant recovering from transplant?",
            "New growth visible?",
            "Irrigation working?",
            "Mulch in place?",
            "No pest damage?",
        ],
        "common_problems": [
            {
                "issue": "Transplant shock (wilting, yellowing)",
                "cause": "Root disturbance, sun shock, temperature change",
                "solution": "Normal for 2-5 days. Shade cloth if severe. Water well. Do NOT fertilize during shock. Mycorrhizae helps recovery.",
            },
            {
                "issue": "Deer/rabbit damage",
                "cause": "Wildlife browsing young plants",
                "solution": "Fencing. Deer: 8-foot fence minimum. Rabbits: 2-foot chicken wire. Repellent sprays (temporary).",
            },
            {
                "issue": "Premature flowering (single cola, no branching)",
                "cause": "Planted out too early when days were too short",
                "solution": "Next year: wait until days are 14+ hours. This year: the plant may reveg (confusing) or stay small.",
            },
        ],
        "training": [
            {
                "technique": "Topping",
                "description": "Top at 5-6 nodes once established. Outdoor plants benefit from wide, bushy structure.",
                "timing": "2-3 weeks after plant-out",
            },
            {
                "technique": "LST",
                "description": "Bend branches outward for bush shape. More light penetration.",
                "timing": "After topping recovery",
            },
        ],
        "transition_signals": [
            "Rapid daily growth visible",
            "2+ inches/day growth",
            "Root system expanding (plant drinking more)",
            "200+ GDD accumulated",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Default outdoor environment."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Standard outdoor.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: protected from weather. May need supplemental airflow."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Weather-protected.",
            },
        },
    },
    # ── 4. LATE VEGETATIVE ───────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Vegetative (Summer Growth)",
        "order": 4,
        "duration_days": {
            "min": 30,
            "max": 60,
            "typical": 45,
            "gdd_trigger": {"accumulated": 600, "notes": "600 GDD from plant-out. Plant at full vegetative pace."},
        },
        "description": "Peak summer growth. The longest stage outdoors — often 6-8 weeks of explosive vegetative growth under full sun. Plants can reach 6-10 feet tall and 4-8 feet wide. This is where outdoor growing shows its advantage: unlimited light and root space produce plants that dwarf any indoor grow.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 95, "target": 82},
            "temp_night_f": {"min": 55, "max": 75, "target": 65},
            "humidity_pct": {"min": 40, "max": 80, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 2.0, "target": 1.4},
            "light_hours": {"min": 14, "max": 16, "notes": "Long summer days. Plant stays vegetative."},
            "light_ppfd": {"min": 800, "max": 2000, "target": 1500},
            "light_dli": {"min": 40, "max": 65, "target": 55},
            "notes": "Peak summer. Full sun. Plant may need 5-10 gallons of water per day at peak. Shade cloth at 95°F+.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": {"notes": "Zone determines how long this stage lasts. Longer season = bigger plants."},
            "companion_plants": [
                {
                    "name": "Cover crop (clover, vetch)",
                    "benefit": "Nitrogen fixation + living mulch between plants",
                    "spacing": "Between rows",
                },
                {
                    "name": "Sunflowers",
                    "benefit": "Attract pollinators, provide partial shade, attract aphids away from cannabis (trap crop)",
                    "spacing": "Perimeter or end rows",
                },
            ],
            "weather_triggers": [
                {"trigger": "drought_7_plus_days", "action": "Double irrigation. Deep soak. Mulch heavily."},
                {
                    "trigger": "heat_wave_above_100f",
                    "action": "Shade cloth. Morning-only watering. Foliar spray evening.",
                },
                {
                    "trigger": "hail",
                    "action": "Assess damage. Remove broken branches cleanly. Plants recover well in veg.",
                },
                {"trigger": "heavy_wind", "action": "Reinforce stakes. Check supports. Supercrop broken branches."},
            ],
            "notes": "Peak water demand. In-ground plants develop massive root systems — 3-4 foot deep taproots. Water deeply and infrequently (every 2-3 days at 5-10 gallons) rather than shallowly and daily. Deep watering encourages deep roots. Topdress with compost monthly. Maintain mulch layer — it breaks down and needs refreshing.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "In amended ground: monthly compost top dress + biweekly compost tea. Synthetic: 1/2 strength through drip every other irrigation.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Maintain irrigation",
                "description": "5-10 gallons per plant per day at peak summer. Drip system or deep hand watering. Early morning watering preferred.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monthly compost top dress",
                "description": "1-2 inches of compost around base. Scratch in lightly. Water in. Refresh mulch on top.",
                "interval_days": 30,
                "priority": "high",
            },
            {
                "name": "Training and canopy management",
                "description": "Continue topping, LST. Open interior for airflow. Outdoor plants get DENSE — defoliate interior.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Pest scouting",
                "description": "Weekly inspection: aphids (undersides of leaves), caterpillars (frass/droppings), spider mites (stippling), grasshoppers, Japanese beetles.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Weed management",
                "description": "Pull weeds around plants. Companion cover crops help suppress weeds.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Reinforce supports",
                "description": "Plants getting heavy. Add stakes, cages, or trellis netting.",
                "interval_days": 14,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Plant growing vigorously?",
            "Irrigation adequate?",
            "No pest infestations?",
            "Supports adequate for plant size?",
            "Mulch maintained?",
        ],
        "common_problems": [
            {
                "issue": "Heat stress (taco leaves, wilting in afternoon)",
                "cause": "Temps above 95°F — plant can't transpire fast enough",
                "solution": "Shade cloth (30-50%). Morning watering. Mulch. Foliar spray in evening (water only). Plants recover overnight.",
            },
            {
                "issue": "Caterpillar damage (holes in leaves, frass)",
                "cause": "Caterpillars (budworms are the outdoor enemy)",
                "solution": "BT (Bacillus thuringiensis) spray weekly. Hand-pick caterpillars. Inspect INSIDE developing buds — budworms hide inside and cause rot.",
            },
            {
                "issue": "Plant too tall",
                "cause": "Sativa genetics + unlimited light + in-ground roots",
                "solution": "Supercrop tall branches. Top aggressively. Some outdoor plants reach 10-12 feet — this may be a neighbor/visibility issue.",
            },
        ],
        "training": [
            {
                "technique": "Topping (multiple rounds)",
                "description": "Outdoor plants can be topped 3-4 times for wide bushy structure.",
                "timing": "Monthly through mid-summer",
            },
            {
                "technique": "Supercropping",
                "description": "Bend tall branches. Creates knuckles that strengthen.",
                "timing": "As needed for height control",
            },
        ],
        "transition_signals": [
            "Day length dropping below 14.5 hours",
            "Plant at target size",
            "Pre-flower pistils appearing at nodes",
            "Late July - early August (Northern Hemisphere)",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Standard outdoor. Full sun."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Peak summer management.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: can use light dep to trigger early flowering."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Light dep option.",
            },
        },
    },
    # ── 5. TRANSITION ────────────────────────────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Natural Trigger)",
        "order": 5,
        "duration_days": {
            "min": 14,
            "max": 28,
            "typical": 21,
            "gdd_trigger": {
                "accumulated": 1000,
                "notes": "~1000 GDD. Natural photoperiod triggers flowering as days shorten.",
            },
        },
        "description": "Natural photoperiod triggers flowering as day length drops below ~14 hours. The stretch begins. Outdoor stretch can be DRAMATIC — plants may add 50-100% height. This is the most critical transition outdoors: the plant shifts from vegetative to reproductive, and you can't control the timing (unless using light dep).",
        "environment": {
            "temp_day_f": {"min": 70, "max": 90, "target": 80},
            "temp_night_f": {"min": 50, "max": 65, "target": 58},
            "humidity_pct": {"min": 40, "max": 70, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.6, "target": 1.3},
            "light_hours": {
                "min": 12.5,
                "max": 14,
                "notes": "Dropping below 14 hours triggers transition. Gradual — not instant like indoor 12/12.",
            },
            "light_ppfd": {
                "min": 600,
                "max": 1800,
                "target": 1200,
                "notes": "Sun angle lowering. Slightly less intensity than peak summer.",
            },
            "light_dli": {"min": 30, "max": 50, "target": 40},
            "notes": "Late summer → early fall. Days getting shorter. Nights getting cooler. Humidity may be rising. This is when outdoor growing gets interesting — you're racing against fall weather.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": {
                "notes": "Zone determines how much time you have before frost. Zone 5: flower must finish by mid-October. Zone 9: November-December."
            },
            "companion_plants": [
                {
                    "name": "Marigolds (still blooming)",
                    "benefit": "Continue pest deterrence through flower.",
                    "spacing": "Around plants",
                },
            ],
            "weather_triggers": [
                {
                    "trigger": "first_frost_warning",
                    "action": "Cover plants with frost cloth. Cannabis dies at 28°F. Damaged below 40°F.",
                },
                {
                    "trigger": "rain_forecast_3_plus_days",
                    "action": "Pre-treat with anti-fungal. Prepare tarps. Bud rot season begins.",
                },
                {
                    "trigger": "humidity_above_70_pct",
                    "action": "Defoliate heavily for airflow. This is critical for bud rot prevention.",
                },
            ],
            "notes": "Shift to bloom feeding. Top dress with bloom amendments (bone meal, bat guano, langbeinite) or switch synthetic ratio. The plant's water needs may actually DECREASE as days shorten and temps drop. Adjust irrigation. Monitor weather forecasts obsessively — fall weather determines outdoor harvest quality.",
        },
        "nutrients": {
            "strength_pct": 65,
            "approach": "Transition ratio. Reduce N, increase PK. Top dress with bloom amendments. Through drip: transition feed.",
            "flora_micro_ml_per_gal": 1.625,
            "flora_gro_ml_per_gal": 1.0,
            "flora_bloom_ml_per_gal": 1.25,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Shift to bloom feeding",
                "description": "Top dress: bone meal + bat guano + langbeinite. Synthetic: transition ratio through drip.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Manage stretch",
                "description": "Outdoor stretch can add 3-5 feet. Supercrop, reinforce supports.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Defoliate for airflow",
                "description": "CRITICAL outdoors. Dense canopy + fall humidity = bud rot. Open up the interior.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Scout for caterpillars intensely",
                "description": "Budworms are the #1 outdoor flower pest. BT spray weekly. Inspect buds.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Monitor weather forecasts",
                "description": "Track frost dates, rain forecasts, humidity. Plan harvest timing.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Prepare harvest supplies",
                "description": "Drying space ready. Trim supplies. The harvest may be forced by weather.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Stretch manageable?",
            "Bud sites forming?",
            "No caterpillar damage?",
            "Airflow good (canopy opened)?",
            "Frost protection available?",
        ],
        "common_problems": [
            {
                "issue": "Extreme stretch (plant too tall for support)",
                "cause": "Sativa genetics + vigor",
                "solution": "Supercrop aggressively. Add taller supports. You cannot top during stretch — too late.",
            },
            {
                "issue": "Caterpillars in forming buds",
                "cause": "Corn earworm / budworm laying eggs on buds",
                "solution": "BT spray weekly. Hand-inspect every bud. Remove caterpillars. Cut out damaged bud sections. This is THE outdoor battle.",
            },
            {
                "issue": "Light pollution preventing flower",
                "cause": "Street lights, porch lights, nearby buildings",
                "solution": "Any light during dark period disrupts flowering. Move plants if possible. Screen with opaque barriers.",
            },
        ],
        "training": [
            {
                "technique": "Supercropping",
                "description": "Aggressive bending for height control.",
                "timing": "First 2 weeks of stretch",
            },
        ],
        "transition_signals": ["Stretch slowing", "Pistils at bud sites", "Day length below 13 hours"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Natural photoperiod triggers transition."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Standard outdoor.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Light dep triggers flowering earlier — more time before frost."},
                "extra_tasks": [
                    {
                        "name": "Light dep schedule",
                        "description": "Pull tarps to enforce 12/12 starting 4-6 weeks before natural trigger. Gives more time for flowering before fall weather.",
                        "interval_days": 1,
                        "priority": "high",
                    }
                ],
                "extra_problems": [],
                "notes": "Light dep is the greenhouse advantage.",
            },
        },
    },
    # ── 6. EARLY FLOWER ──────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14, "gdd_trigger": {"accumulated": 1200}},
        "description": "Buds forming. The race against fall weather begins in earnest. Bud rot prevention becomes the #1 priority. Every rain event, every humid night, every morning dew is a potential disaster. Outdoor flower quality depends almost entirely on weather management.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 85, "target": 75},
            "temp_night_f": {"min": 45, "max": 60, "target": 52},
            "humidity_pct": {"min": 40, "max": 70, "target": 50},
            "vpd_kpa": {"min": 1.0, "max": 1.6, "target": 1.3},
            "light_hours": {"min": 11.5, "max": 12.5, "notes": "Continuing to shorten."},
            "light_ppfd": {"min": 500, "max": 1500, "target": 1000, "notes": "Sun lower in sky. Fewer peak hours."},
            "light_dli": {"min": 25, "max": 40, "target": 30},
            "notes": "Early fall. Cooler nights bringing out colors. But humidity and rain bring bud rot. Every grower decision from here is about protecting buds from weather.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": {"notes": "Track first frost date. You need 6-10 more weeks of frost-free weather."},
            "companion_plants": [],
            "weather_triggers": [
                {
                    "trigger": "rain_event",
                    "action": "Shake plants after rain to remove water from buds. Inspect for rot 24-48 hours after every rain.",
                },
                {
                    "trigger": "frost_warning",
                    "action": "Cover with frost cloth or harvest if frost is hard (below 28°F).",
                },
                {"trigger": "dew_heavy_morning", "action": "Shake plants at sunrise to remove dew from buds."},
            ],
            "notes": "Bloom feeding continues. Reduce irrigation as temps drop — plants drinking less. Watch for overwatering in cool weather. In-ground plants may need no irrigation if getting rain (but rain brings rot risk — the eternal outdoor tradeoff).",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Full bloom. Heavy PK. Top dress or synthetic through drip.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Full bloom feeding",
                "description": "Top dress bloom amendments. Synthetic through drip.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Bud rot prevention protocol",
                "description": "Defoliate heavily. Shake plants after rain/dew. Inspect buds every 2 days. Remove ANY suspicious buds immediately. One rotten bud can destroy a cola in 24 hours.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "BT spray for caterpillars",
                "description": "Weekly BT spray. Budworms cause bud rot by damaging buds from the inside. Stop BT 2 weeks before harvest.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Shake plants after rain/dew",
                "description": "Remove standing water from buds. Do this every morning with heavy dew.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Support heavy branches",
                "description": "Stakes, trellis, netting. Outdoor buds get heavy.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Buds forming?",
            "No bud rot?",
            "No caterpillar damage?",
            "Weather forecast favorable for next 2 weeks?",
            "Support adequate?",
        ],
        "common_problems": [
            {
                "issue": "Bud rot (Botrytis)",
                "cause": "Rain + humidity + dense buds. THE outdoor problem.",
                "solution": "Remove affected bud + 2 inches of healthy tissue. Increase airflow. Spray with potassium bicarbonate or Regalia. If widespread: consider early harvest to save what you can.",
            },
            {
                "issue": "Caterpillar damage inside buds",
                "cause": "Budworms hiding inside buds, causing internal rot",
                "solution": "BT spray. Hand-inspect by gently pulling buds apart. Brown frass (caterpillar droppings) = budworm present. Remove immediately.",
            },
            {
                "issue": "Cold stress (purple stems, slow growth)",
                "cause": "Night temps below 50°F",
                "solution": "Some purple is genetic. But if growth slows dramatically: cover overnight with row cover. The plant can handle brief cold but sustained cold slows ripening.",
            },
        ],
        "training": [
            {
                "technique": "Heavy defoliation",
                "description": "Remove more leaves than you would indoors. Airflow is critical outdoor.",
                "timing": "Every 2 weeks through flower",
            },
        ],
        "transition_signals": ["Buds fattening", "Trichomes forming", "Flower aroma strong"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Standard outdoor. Weather management is everything."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Bud rot prevention is #1.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: protected from rain. Major advantage."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Rain protection is the greenhouse advantage in flower.",
            },
        },
    },
    # ── 7. MID FLOWER ────────────────────────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Peak Bloom)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 14, "gdd_trigger": {"accumulated": 1400}},
        "description": "Peak bud development outdoors. The most anxious time for outdoor growers — buds are fattening beautifully but weather threats are maximum. Every day the buds survive is a win. Bud rot, caterpillars, and early frost are the three threats.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 80, "target": 72},
            "temp_night_f": {"min": 40, "max": 55, "target": 48},
            "humidity_pct": {"min": 40, "max": 70, "target": 50},
            "vpd_kpa": {"min": 1.0, "max": 1.6, "target": 1.3},
            "light_hours": {"min": 11, "max": 12, "notes": "Fall. Days continuing to shorten."},
            "light_ppfd": {"min": 400, "max": 1200, "target": 800},
            "light_dli": {"min": 20, "max": 35, "target": 25},
            "notes": "Fall weather. Cooler nights developing colors. Morning dew is heavy. Rain events are high-anxiety. Every sunny day is a gift.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": {"notes": "Track days until first frost. You need 3-5 more weeks."},
            "companion_plants": [],
            "weather_triggers": [
                {
                    "trigger": "rain_3_plus_days",
                    "action": "Consider tarping plants or early harvest. Extended rain during peak bloom = guaranteed rot.",
                },
                {
                    "trigger": "frost_warning",
                    "action": "Cover or harvest. Hard frost (28°F) kills. Light frost (32-35°F) damages.",
                },
                {"trigger": "morning_dew", "action": "Shake plants at sunrise. Every morning. Non-negotiable."},
            ],
            "notes": "Reduce irrigation significantly. Plants drinking less. Cool temps + rain may provide all water needed. Overwatering in fall causes root issues. Continue bloom feeding but at reduced strength. The plant is finishing.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Peak bloom. Reducing as plant finishes. Top dress winding down.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.5,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Daily bud rot inspection",
                "description": "Inspect every bud on every plant. Pull apart large colas gently. Brown, mushy spots = rot. Remove immediately + 2 inches of healthy tissue.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Shake plants at sunrise",
                "description": "Remove dew from buds. Every morning. This simple act prevents enormous amounts of rot.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "BT spray (final weeks)",
                "description": "Last BT spray 2 weeks before expected harvest.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Weather-based harvest planning",
                "description": "Track extended forecasts. If 3+ day rain event is coming and buds are close to done: harvest early. Better to harvest slightly early than lose to rot.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Support branches",
                "description": "Heavy buds + wet from rain = branch breaks.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["No bud rot?", "No caterpillar damage?", "Trichomes developing?", "Frost protection ready?"],
        "common_problems": [
            {
                "issue": "Bud rot spreading fast",
                "cause": "Rain + humidity + dense outdoor buds",
                "solution": "Remove all affected material. If more than 20% of buds are affected: HARVEST NOW. Save what you can. Outdoor bud rot can destroy an entire crop in 48 hours of rain.",
            },
            {
                "issue": "Early frost damage",
                "cause": "Unexpected frost before buds are ready",
                "solution": "Light frost (32-35°F): cover with frost cloth, plants survive. Hard frost (below 28°F): harvest immediately. Frost-damaged buds degrade rapidly.",
            },
        ],
        "training": [],
        "transition_signals": ["Buds dense", "Trichomes milky", "Pistils turning orange", "Fan leaves yellowing"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Standard outdoor. Weather anxiety is normal."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Bud rot prevention is everything.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: rain protection. Huge advantage."},
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
        "duration_days": {"min": 14, "max": 21, "typical": 14, "gdd_trigger": {"accumulated": 1600}},
        "description": "Buds ripening. Nature is putting on the fall show — colors, aromas, and trichome development peak. But so do weather risks. Many outdoor growers harvest during this stage rather than waiting for perfect trichome ratios — weather decides, not the grower.",
        "environment": {
            "temp_day_f": {"min": 55, "max": 75, "target": 68},
            "temp_night_f": {"min": 35, "max": 50, "target": 45},
            "humidity_pct": {"min": 40, "max": 70, "target": 50},
            "vpd_kpa": {"min": 0.8, "max": 1.4, "target": 1.1},
            "light_hours": {"min": 10.5, "max": 11.5},
            "light_ppfd": {"min": 300, "max": 1000, "target": 700},
            "light_dli": {"min": 15, "max": 30, "target": 20},
            "notes": "Late fall. Cool nights producing colors. Frost risk increasing daily.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": {"notes": "Frost imminent in zones 5-6. Zones 8-9 have more time."},
            "companion_plants": [],
            "weather_triggers": [
                {"trigger": "frost_imminent", "action": "Harvest. Don't gamble."},
                {"trigger": "extended_rain", "action": "Harvest if buds are close. Rain + late flower = rot."},
            ],
            "notes": "Minimal irrigation. Plants barely drinking. Natural senescence — fan leaves dropping. This is beautiful and natural. Stop all feeding. Plain water only if soil is very dry.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Stop feeding. Let the plant use stored nutrients. Natural outdoor senescence.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Daily bud rot inspection",
                "description": "Critical. Every day.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Trichome checks",
                "description": "Track milky → amber. But be ready to harvest based on weather, not trichomes.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Frost watch",
                "description": "Monitor forecasts twice daily. Have frost cloth and harvest supplies ready.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Harvest decision point",
                "description": "Outdoor harvest timing: trichome readiness vs weather threat. If frost or rain threatens: harvest. Better 90% ready than 100% rotten.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Trichomes progressing?", "No bud rot?", "Frost cloth ready?", "Drying space prepared?"],
        "common_problems": [
            {
                "issue": "Weather forcing early harvest",
                "cause": "Frost or extended rain before trichomes are ready",
                "solution": "Harvest. An early harvest at 80% milky trichomes is vastly better than a rotted or frost-killed crop. This is the outdoor reality.",
            },
        ],
        "training": [],
        "transition_signals": ["Trichomes milky with amber", "Fan leaves dropping", "Frost approaching"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Weather controls harvest timing."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Nature decides.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: more time before weather forces harvest."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Extended window.",
            },
        },
    },
    # ── 9. FLUSH ─────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush (Natural Senescence)",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 7, "gdd_trigger": None},
        "description": "Outdoor soil often doesn't need a formal flush — the plant naturally stops feeding as it senesces. In amended ground, there are no synthetic salts to flush. The plant consumes stored nutrients. Many outdoor growers simply stop all inputs and let nature finish.",
        "environment": {
            "temp_day_f": {"min": 50, "max": 70, "target": 62},
            "temp_night_f": {"min": 32, "max": 48, "target": 42},
            "humidity_pct": {"min": 40, "max": 70, "target": 55},
            "vpd_kpa": None,
            "light_hours": {"min": 10, "max": 11},
            "light_ppfd": {"min": 200, "max": 800, "target": 500},
            "light_dli": {"min": 10, "max": 20, "target": 15},
            "notes": "Late fall. Plant finishing. Frost very close.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": {"notes": "Flush may be cut short by weather."},
            "companion_plants": [],
            "weather_triggers": [
                {"trigger": "frost_imminent", "action": "Harvest immediately. Flush is secondary to saving the crop."},
            ],
            "notes": "No inputs. Just water if bone dry. Outdoor organic in-ground plants flush themselves naturally. Synthetic outdoor grows: rain often provides natural flush. Don't stress about flush timing outdoors — weather controls everything.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None. Natural senescence.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Stop all inputs",
                "description": "No feeding. Water only if soil is very dry.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Continue daily bud rot checks",
                "description": "Still the #1 risk.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Prepare for harvest",
                "description": "Drying space ready. Trim supplies. Frost cloth on standby.",
                "interval_days": None,
                "priority": "high",
            },
        ],
        "health_checks": ["Dramatic natural yellowing?", "Trichomes at target?", "No bud rot?"],
        "common_problems": [
            {
                "issue": "Can't flush long enough (weather forcing harvest)",
                "cause": "Frost or rain approaching",
                "solution": "Harvest. Outdoor flush is a luxury, not a requirement. In-ground organic plants don't need formal flushing.",
            },
        ],
        "training": [],
        "transition_signals": ["Trichomes at target", "Frost imminent", "Natural senescence complete"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Natural senescence."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Nature's flush.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: more time for natural finish."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Extended window.",
            },
        },
    },
    # ── 10. HARVEST ──────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 7, "typical": 2, "gdd_trigger": None},
        "description": "Outdoor harvest is a multi-day event for large plants. A single outdoor plant can yield 1-5+ pounds — you can't process that in an afternoon. Plan for 2-3 day harvest windows. Weather may force staggered harvests — take the most vulnerable/ripe plants first.",
        "environment": {
            "temp_day_f": {"min": 45, "max": 70, "target": 60},
            "temp_night_f": {"min": 30, "max": 50, "target": 42},
            "humidity_pct": {"min": 40, "max": 70, "target": 55},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Harvest in morning after dew evaporates. Dry day preferred.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": None,
            "companion_plants": [],
            "weather_triggers": [],
            "notes": "After harvest: chop plant at base. Leave roots in ground — they decompose and add organic matter. Plant cover crop (crimson clover, winter rye) immediately in the vacated ground for off-season soil building.",
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
                "name": "Harvest plants",
                "description": "Cut at base or branch by branch. Large outdoor plants: harvest in sections. Most ripe branches first.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Inspect every bud for rot",
                "description": "Outdoor buds MUST be inspected during trim. Hidden rot is common.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Plant cover crop",
                "description": "Immediately after harvest: scatter cover crop seed (crimson clover, winter rye, vetch). Water in. This builds soil for next season.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Clean up site",
                "description": "Remove stakes, cages, irrigation. Chop remaining stalks. Leave roots to decompose in ground.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["All plants harvested before frost?", "Rot-free buds separated?", "Cover crop planted?"],
        "common_problems": [
            {
                "issue": "Too much material to process at once",
                "cause": "Large outdoor plants yield pounds, not ounces",
                "solution": "Stagger harvest over 2-3 days. Hang whole branches rather than trimming immediately. Wet trim is faster for large volumes.",
            },
        ],
        "training": [],
        "transition_signals": ["All plants chopped", "Material hung", "Cover crop planted"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Harvest before frost."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Weather dictates.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "More controlled timing."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "More flexibility.",
            },
        },
    },
    # ── 11. DRYING ───────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10, "gdd_trigger": None},
        "description": "Dry indoors. The volume from outdoor plants demands dedicated drying space. Garages, spare rooms, or dedicated dry rooms. 60°F / 60% RH / dark. Outdoor-grown flower may have more stem moisture and take slightly longer to dry.",
        "environment": {
            "temp_day_f": {"min": 58, "max": 65, "target": 60},
            "temp_night_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "INDOORS. Dark. 60/60. Large volume needs good airflow planning.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": None,
            "companion_plants": [],
            "weather_triggers": [],
            "notes": "No outdoor involvement. Drying is indoor environmental control.",
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
                "description": "Space so they don't touch. Large volume needs planning.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Maintain 60/60",
                "description": "Dehumidifier and AC/heater as needed. Large volumes release lots of moisture.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check drying progress",
                "description": "Bend stems. Snap = ready.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Inspect for mold",
                "description": "Outdoor buds have more exposure to mold spores. Check daily.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Temp 58-65°F?", "Humidity 55-65%?", "Dark?", "No mold?"],
        "common_problems": [
            {
                "issue": "Drying space too humid from volume",
                "cause": "Pounds of wet material releasing moisture",
                "solution": "Bigger dehumidifier. Stage the hanging (don't hang everything at once). Increase airflow.",
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
                "environment_overrides": {"notes": "Greenhouse can work for drying if dark and temp-controlled."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Possible if controlled.",
            },
        },
    },
    # ── 12. CURING ───────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30, "gdd_trigger": None},
        "description": "Mason jar cure. Outdoor-grown, soil-fed flower often has exceptional terpene profiles that develop beautifully during cure. Many connoisseurs consider outdoor organic soil-grown flower the gold standard for flavor.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "In-jar 58-62% RH. Dark, cool. Large volume may need turkey bags or grove bags instead of jars.",
        },
        "medium": {
            "gdd_base_temp": 50,
            "hardiness_zone": None,
            "companion_plants": [],
            "weather_triggers": [],
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
                "name": "Trim and jar/bag",
                "description": "Large volume: grove bags or turkey bags may be more practical than mason jars.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Burp containers",
                "description": "2-3x/day week 1, 1x/day week 2.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor for mold",
                "description": "Outdoor buds: extra mold vigilance.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["58-62% RH in containers?", "No mold/ammonia?", "Improving aroma?"],
        "common_problems": [
            {"issue": "Ammonia smell", "cause": "Too wet when jarred", "solution": "Remove, dry 12-24 hours, rejar."},
            {
                "issue": "Hidden mold from outdoor exposure",
                "cause": "Mold spores from outdoor growing surviving into cure",
                "solution": "Inspect carefully when burping. Remove affected buds immediately.",
            },
        ],
        "training": [],
        "transition_signals": ["Rich complex aroma", "Smooth smoke", "Stable humidity"],
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
                "notes": "Stable indoor space.",
            },
        },
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT
# ─────────────────────────────────────────────────────────────────────────────

OUTDOOR_SOIL_EQUIPMENT: list[dict] = [
    # -- Site prep --
    {
        "name": "Soil test kit (or lab test)",
        "category": "site_prep",
        "required": True,
        "notes": "Test native soil pH, NPK, and micronutrients BEFORE amending. Lab tests are $15-30 and worth every penny.",
    },
    {
        "name": "Compost (bulk)",
        "category": "site_prep",
        "required": True,
        "notes": "High-quality compost for bed building. Buy by the cubic yard for outdoor scale.",
    },
    {
        "name": "Worm castings",
        "category": "site_prep",
        "required": True,
        "notes": "Best amendment for soil biology. Mix into planting holes and use as top dress.",
    },
    {
        "name": "Perlite / pumice",
        "category": "site_prep",
        "required": False,
        "notes": "For drainage in heavy clay soils.",
    },
    {
        "name": "Dry amendments",
        "category": "site_prep",
        "required": False,
        "notes": "Neem, kelp, alfalfa, bone meal, bat guano, langbeinite, azomite. For building soil.",
    },
    {
        "name": "Cover crop seed",
        "category": "site_prep",
        "required": True,
        "notes": "Crimson clover, winter rye, vetch. Plant after harvest for off-season soil building.",
    },
    # -- Irrigation --
    {
        "name": "Drip irrigation system",
        "category": "irrigation",
        "required": True,
        "notes": "Timer + mainline + emitters. Essential for outdoor scale. Hand watering 20+ plants is unsustainable.",
    },
    {
        "name": "Soaker hoses (alternative)",
        "category": "irrigation",
        "required": False,
        "notes": "Simpler than drip. Lay under mulch.",
    },
    {
        "name": "Rain gauge",
        "category": "irrigation",
        "required": True,
        "notes": "Know how much rain your plants received. Adjust irrigation accordingly.",
    },
    # -- Support --
    {
        "name": "Stakes / cages / trellis",
        "category": "support",
        "required": True,
        "notes": "Outdoor plants get MASSIVE. Heavy-duty support from day 1. T-posts + wire for large operations.",
    },
    {
        "name": "Frost cloth / row cover",
        "category": "support",
        "required": True,
        "notes": "Emergency frost protection. Keep on hand from September onward.",
    },
    {"name": "Shade cloth (30-50%)", "category": "support", "required": False, "notes": "For heat waves above 95°F."},
    # -- Fencing --
    {
        "name": "Deer fencing (8 foot)",
        "category": "fencing",
        "required": False,
        "notes": "Essential in deer country. 8-foot minimum — deer jump 6 feet easily.",
    },
    {
        "name": "Chicken wire (rabbit)",
        "category": "fencing",
        "required": False,
        "notes": "2-foot ring around plants for rabbit protection.",
    },
    # -- Pest control --
    {
        "name": "BT (Bacillus thuringiensis)",
        "category": "pest_control",
        "required": True,
        "notes": "THE outdoor caterpillar/budworm control. Spray weekly during flower. Organic. Safe.",
    },
    {
        "name": "Neem oil",
        "category": "pest_control",
        "required": True,
        "notes": "Veg only — don't spray on buds. Aphids, mites, whiteflies.",
    },
    {"name": "Yellow sticky traps", "category": "pest_control", "required": False, "notes": "Monitoring tool."},
    # -- Monitoring --
    {
        "name": "Weather station or app",
        "category": "monitoring",
        "required": True,
        "notes": "Track temperature, humidity, rain, frost forecasts. THE outdoor monitoring tool.",
    },
    {
        "name": "Soil moisture meter",
        "category": "monitoring",
        "required": False,
        "notes": "In-ground moisture monitoring.",
    },
    {"name": "Jeweler's loupe (60-100x)", "category": "monitoring", "required": True, "notes": "Trichome inspection."},
    # -- Mulch --
    {
        "name": "Straw or wood chip mulch",
        "category": "mulch",
        "required": True,
        "notes": "3-4 inches around plants. Retains moisture, suppresses weeds, regulates soil temp, feeds biology. The outdoor secret weapon.",
    },
    # -- Companion plants --
    {
        "name": "Companion plant starts/seeds",
        "category": "companion",
        "required": False,
        "notes": "Basil, marigolds, clover, lavender. Started at same time as cannabis or before.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

OUTDOOR_SOIL_QUICK_REFERENCE: dict = {
    "ph_range": {
        "min": 6.0,
        "max": 7.0,
        "sweet_spot": 6.5,
        "notes": "Same as indoor soil. Test native soil and amend to range.",
    },
    "gdd_guide": {
        "description": "Growing Degree Days (GDD) track heat accumulation. More accurate than calendar days for predicting plant development. Cannabis base temp: 50°F.",
        "formula": "GDD = ((daily_high + daily_low) / 2) - base_temp. Negative values = 0.",
        "example": "Day with high 85°F, low 55°F: GDD = ((85+55)/2) - 50 = 20 GDD",
        "milestones": {
            "200_gdd": "Early veg established",
            "600_gdd": "Peak vegetative growth",
            "1000_gdd": "Flowering transition begins",
            "1200_gdd": "Early flower",
            "1400_gdd": "Peak bloom",
            "1600_gdd": "Ripening",
        },
    },
    "hardiness_zone_guide": {
        "description": "USDA Hardiness zones determine growing season length.",
        "zone_4_5": {
            "season_days": "120-150",
            "start_outdoor": "Late May - Early June",
            "harvest": "Early-Mid October",
            "notes": "Short season. Choose fast-finishing cultivars (8-9 week flower).",
        },
        "zone_6_7": {
            "season_days": "150-200",
            "start_outdoor": "Mid May",
            "harvest": "Mid-Late October",
            "notes": "Good season length. Most cultivars work.",
        },
        "zone_8_9": {
            "season_days": "200-270",
            "start_outdoor": "April",
            "harvest": "November",
            "notes": "Long season. Can grow sativas. Multiple harvests possible with light dep.",
        },
        "zone_10_plus": {
            "season_days": "300+",
            "start_outdoor": "March",
            "harvest": "November-December",
            "notes": "Near year-round. Pest pressure higher.",
        },
    },
    "companion_planting_guide": {
        "basil": {
            "benefit": "Repels aphids, whiteflies, spider mites",
            "spacing": "12 inches from cannabis",
            "notes": "The #1 companion plant for cannabis.",
        },
        "marigolds": {
            "benefit": "Repels nematodes, whiteflies. Trap crop for aphids.",
            "spacing": "Perimeter",
            "notes": "Plant around beds.",
        },
        "white_clover": {
            "benefit": "Nitrogen fixation, living mulch, moisture retention",
            "spacing": "Between plants as ground cover",
            "notes": "Plant as living mulch.",
        },
        "lavender": {
            "benefit": "Attracts pollinators, repels fleas/moths",
            "spacing": "Perimeter",
            "notes": "Aromatic deterrent.",
        },
        "dill": {
            "benefit": "Attracts beneficial insects (ladybugs, lacewings)",
            "spacing": "Nearby",
            "notes": "Beneficial insect habitat.",
        },
        "sunflowers": {
            "benefit": "Trap crop for aphids, attracts pollinators, windbreak",
            "spacing": "End of rows or perimeter",
            "notes": "Multi-purpose.",
        },
    },
    "seasonal_calendar": {
        "description": "Northern Hemisphere outdoor cannabis calendar.",
        "february_march": "Plan. Order seeds. Indoor germination. Soil test. Order amendments.",
        "april": "Start seeds indoors 4-6 weeks before plant-out. Begin site prep.",
        "may": "Harden off seedlings. Plant out after last frost + 2 weeks. Install irrigation.",
        "june_july": "Peak vegetative growth. Training, feeding, pest management. Water heavily.",
        "august": "Transition begins as days shorten. Shift to bloom feeding. Caterpillar season starts.",
        "september": "Early-mid flower. Bud rot prevention. BT spray. Frost watch begins.",
        "october": "Peak-late flower. Harvest most cultivars. Frost protection. Cover crop planting.",
        "november": "Late-season harvest (warm climates). Cover crop growing. Soil building.",
        "december_january": "Rest. Plan next year. Review what worked.",
    },
    "water_requirements": {
        "seedling": "0.5-1 gallon/day",
        "early_veg": "1-3 gallons/day",
        "late_veg_peak_summer": "5-10 gallons/day",
        "flower": "3-7 gallons/day (decreasing)",
        "notes": "In-ground plants with deep roots need less frequent watering than containers. Deep and infrequent > shallow and daily.",
    },
    "golden_rules": [
        "Start seeds indoors. Always. Outdoor germination is unreliable.",
        "Harden off seedlings before plant-out. 2 weeks of gradual outdoor exposure.",
        "Don't plant out until 2 weeks after last frost AND day length is 14+ hours.",
        "Soil test before amending. Know what you're starting with.",
        "Mulch 3-4 inches. The single best thing you can do for outdoor soil growing.",
        "Companion plant. Basil and marigolds are non-negotiable outdoor companions.",
        "Deep, infrequent watering. Encourage deep roots. Not daily shallow watering.",
        "BT spray weekly during flower. Budworms are the #1 outdoor flower pest.",
        "Shake plants after every rain and every dewy morning. Prevents bud rot.",
        "Weather decides harvest timing, not trichomes. Be ready to harvest early.",
        "Plant cover crop after harvest. Build soil for next year.",
        "One outdoor plant can yield 1-5+ pounds. Plan your drying space accordingly.",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING
# ─────────────────────────────────────────────────────────────────────────────

OUTDOOR_SOIL_TROUBLESHOOTING: list[dict] = [
    {
        "category": "Weather & Environment",
        "issues": [
            {
                "symptom": "Bud rot (brown mushy buds)",
                "cause": "Rain + humidity + dense outdoor buds. THE outdoor problem.",
                "fix": "Remove affected material + 2 inches. Defoliate for airflow. Shake after rain/dew. If widespread: harvest early. Prevention > cure.",
            },
            {
                "symptom": "Frost damage (black/wilted leaves)",
                "cause": "Temperature below 32°F",
                "fix": "Light frost: cover with frost cloth. Hard frost (below 28°F): harvest immediately. Frost-damaged buds degrade fast.",
            },
            {
                "symptom": "Heat stress (taco leaves, wilting)",
                "cause": "Temps above 95°F",
                "fix": "Shade cloth (30-50%). Morning watering. Mulch heavily. Plants recover overnight.",
            },
            {
                "symptom": "Wind damage (broken branches)",
                "cause": "Strong wind or storms",
                "fix": "Reinforce supports. Supercrop broken branches if possible. Stake everything.",
            },
        ],
    },
    {
        "category": "Pests (Outdoor-Specific)",
        "issues": [
            {
                "symptom": "Caterpillar damage / budworms",
                "cause": "Corn earworm, cabbage looper, or other caterpillars",
                "fix": "BT spray weekly. Hand-inspect buds. Remove caterpillars. Cut out damaged bud sections. THE outdoor pest battle.",
            },
            {
                "symptom": "Deer browsing",
                "cause": "Deer eating plants",
                "fix": "8-foot fence. Repellent sprays (temporary). Young plants are most vulnerable.",
            },
            {
                "symptom": "Aphid infestation (sticky leaves, curling)",
                "cause": "Aphid colony on undersides of leaves",
                "fix": "Blast with water hose. Neem oil. Ladybugs (release at dusk). Companion plants (basil, marigolds).",
            },
            {
                "symptom": "Grasshopper damage (ragged holes)",
                "cause": "Grasshoppers — worse in dry years",
                "fix": "Nosema locustae (biological control). Row cover for small plants. Difficult to control at scale.",
            },
        ],
    },
    {
        "category": "Soil & Nutrition",
        "issues": [
            {
                "symptom": "Poor growth in native soil",
                "cause": "Native soil too clay, too sandy, wrong pH, or nutrient-depleted",
                "fix": "Soil test first. Amend heavily: compost, perlite for clay, vermiculite for sand. Build raised beds if native soil is hopeless.",
            },
            {
                "symptom": "Nutrient deficiency despite amending",
                "cause": "Soil pH out of range locking out nutrients",
                "fix": "Check pH. Add lime if too acidic (<6.0). Add sulfur if too alkaline (>7.0). pH is the #1 soil nutrition issue.",
            },
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

OUTDOOR_SOIL_CONFIG: dict = {
    "grow_type_id": "outdoor_soil",
    "version": "1.0.0",
    "stages": OUTDOOR_SOIL_STAGES,
    "equipment": OUTDOOR_SOIL_EQUIPMENT,
    "quick_reference": OUTDOOR_SOIL_QUICK_REFERENCE,
    "troubleshooting": OUTDOOR_SOIL_TROUBLESHOOTING,
    "total_grow_days": {"min": 120, "max": 240, "typical": 180},
}
