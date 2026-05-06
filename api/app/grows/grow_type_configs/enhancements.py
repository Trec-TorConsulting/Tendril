"""Shared grow type configuration enhancements.

Adds scale tiers, strain adjustments, monitoring thresholds, advanced techniques,
and nutrient brand alternatives to all grow type configs.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# SCALE TIERS — Universal across all grow types
# ─────────────────────────────────────────────────────────────────────────────

SCALE_TIERS: list[dict] = [
    {
        "id": "solo",
        "name": "Solo / Single Plant",
        "plant_count": {"min": 1, "max": 1},
        "description": "First-time grower or single-plant hobbyist. Manual management, learning-focused.",
        "monitoring": "manual",
        "labor_hours_per_week": 2,
        "automation_level": "none",
        "notes": "Hands-on learning experience. Manual checks 1-2x daily. Ideal for beginners.",
    },
    {
        "id": "small_tent",
        "name": "Small Tent (2-8 plants)",
        "plant_count": {"min": 2, "max": 8},
        "description": "Hobbyist tent grow. Light automation helpful but not required.",
        "monitoring": "basic_sensors",
        "labor_hours_per_week": 4,
        "automation_level": "environmental",
        "notes": "Timer-controlled lights, humidity controller. Sensor monitoring recommended.",
    },
    {
        "id": "multi_tent",
        "name": "Multi-Tent (9-24 plants)",
        "plant_count": {"min": 9, "max": 24},
        "description": "Dedicated grower with multiple tents/rooms. Automation saves significant time.",
        "monitoring": "full_sensor_suite",
        "labor_hours_per_week": 8,
        "automation_level": "semi_automated",
        "notes": "Multiple environments to manage. Automated alerts essential. Consider perpetual harvest.",
    },
    {
        "id": "commercial_room",
        "name": "Commercial Room (25-100 plants)",
        "plant_count": {"min": 25, "max": 100},
        "description": "Licensed commercial operation. Full automation, compliance tracking, batch management.",
        "monitoring": "industrial_sensors",
        "labor_hours_per_week": 20,
        "automation_level": "fully_automated",
        "compliance": {
            "batch_tracking": True,
            "seed_to_sale": True,
            "testing_required": True,
            "environmental_logging": True,
        },
        "notes": "SOPs required. Staff training. Regulatory compliance. Insurance requirements.",
    },
    {
        "id": "warehouse",
        "name": "Warehouse Scale (100+ plants)",
        "plant_count": {"min": 100, "max": None},
        "description": "Large-scale production facility. Enterprise automation, SCADA integration, dedicated staff.",
        "monitoring": "scada_integration",
        "labor_hours_per_week": 60,
        "automation_level": "enterprise",
        "compliance": {
            "batch_tracking": True,
            "seed_to_sale": True,
            "testing_required": True,
            "environmental_logging": True,
            "chain_of_custody": True,
            "regulatory_reporting": True,
        },
        "notes": "Multiple rooms, dedicated HVAC, industrial nutrient dosing, video surveillance.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# STRAIN ADJUSTMENTS — Autoflower vs Photoperiod
# ─────────────────────────────────────────────────────────────────────────────

STRAIN_ADJUSTMENTS: dict = {
    "photoperiod": {
        "name": "Photoperiod",
        "description": "Standard cannabis strains that require 12/12 light to flower. Grower controls timing.",
        "veg_duration_days": {"min": 28, "max": 63, "typical": 42},
        "flower_duration_days": {"min": 56, "max": 77, "typical": 63},
        "light_schedule": {
            "veg": "18/6 or 20/4",
            "flower": "12/12",
            "transition": "Switch to 12/12 when plant is ~50% of desired final height",
        },
        "training_suitability": {
            "topping": "excellent",
            "LST": "excellent",
            "SCROG": "excellent",
            "mainlining": "excellent",
            "super_cropping": "good",
            "defoliation": "good",
        },
        "nutrient_strength": "full",
        "yield_per_plant_oz": {"min": 2, "max": 16, "typical": 6},
        "notes": "Can be vegged as long as desired. Cloneable. More forgiving of stress (can extend veg to recover).",
    },
    "autoflower": {
        "name": "Autoflower",
        "description": "Ruderalis-hybrid strains that flower automatically regardless of light schedule. Fixed timeline.",
        "veg_duration_days": {"min": 14, "max": 28, "typical": 21},
        "flower_duration_days": {"min": 42, "max": 63, "typical": 49},
        "light_schedule": {
            "veg": "20/4 or 18/6 (entire life)",
            "flower": "20/4 or 18/6 (same as veg — no change needed)",
            "transition": "Automatic — plant decides when to flower (usually week 3-4)",
        },
        "training_suitability": {
            "topping": "risky — only if plant is vigorous",
            "LST": "excellent — preferred training method",
            "SCROG": "difficult — unpredictable stretch",
            "mainlining": "not recommended",
            "super_cropping": "risky",
            "defoliation": "light only — auto can't recover from heavy defol",
        },
        "nutrient_strength": "75% of photoperiod",
        "yield_per_plant_oz": {"min": 1, "max": 8, "typical": 3},
        "notes": "Fixed timeline — stress cannot be recovered by extending veg. Start in final pot (no transplant shock). LST preferred over HST.",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# MONITORING THRESHOLDS — Alert levels for automation
# ─────────────────────────────────────────────────────────────────────────────

MONITORING_THRESHOLDS: dict = {
    "temperature_f": {
        "info": {"low": 68, "high": 82},
        "warning": {"low": 65, "high": 85},
        "alert": {"low": 60, "high": 88},
        "critical": {"low": 55, "high": 95},
        "response_time_minutes": {"warning": 30, "alert": 15, "critical": 5},
    },
    "humidity_pct": {
        "info": {"low": 40, "high": 70},
        "warning": {"low": 35, "high": 75},
        "alert": {"low": 30, "high": 80},
        "critical": {"low": 25, "high": 90},
        "response_time_minutes": {"warning": 30, "alert": 15, "critical": 5},
    },
    "vpd_kpa": {
        "info": {"low": 0.6, "high": 1.4},
        "warning": {"low": 0.4, "high": 1.6},
        "alert": {"low": 0.3, "high": 1.8},
        "critical": {"low": 0.2, "high": 2.2},
        "response_time_minutes": {"warning": 60, "alert": 30, "critical": 15},
    },
    "ph": {
        "info": {"low": 5.8, "high": 6.5},
        "warning": {"low": 5.5, "high": 6.8},
        "alert": {"low": 5.0, "high": 7.2},
        "critical": {"low": 4.5, "high": 7.5},
        "response_time_minutes": {"warning": 60, "alert": 30, "critical": 15},
    },
    "ec_ms_cm": {
        "info": {"low": 0.8, "high": 2.4},
        "warning": {"low": 0.5, "high": 2.8},
        "alert": {"low": 0.3, "high": 3.2},
        "critical": {"low": 0.1, "high": 3.8},
        "response_time_minutes": {"warning": 60, "alert": 30, "critical": 15},
    },
    "water_temp_f": {
        "info": {"low": 64, "high": 72},
        "warning": {"low": 60, "high": 75},
        "alert": {"low": 56, "high": 78},
        "critical": {"low": 50, "high": 82},
        "response_time_minutes": {"warning": 30, "alert": 15, "critical": 5},
    },
    "co2_ppm": {
        "info": {"low": 400, "high": 1200},
        "warning": {"low": 300, "high": 1500},
        "alert": {"low": 200, "high": 1800},
        "critical": {"low": 150, "high": 2500},
        "response_time_minutes": {"warning": 30, "alert": 15, "critical": 5},
    },
    "light_ppfd": {
        "info": {"low": 200, "high": 1000},
        "warning": {"low": 100, "high": 1200},
        "alert": {"low": 50, "high": 1500},
        "critical": {"low": 0, "high": 1800},
        "response_time_minutes": {"warning": 60, "alert": 30, "critical": 15},
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# ADVANCED TECHNIQUES — CO2, crop steering, foliar, silica, beneficials
# ─────────────────────────────────────────────────────────────────────────────

ADVANCED_TECHNIQUES: list[dict] = [
    {
        "id": "co2_supplementation",
        "name": "CO2 Supplementation",
        "category": "environmental",
        "description": "Elevating CO2 from ambient (400ppm) to 1000-1500ppm increases photosynthesis rate by 20-40% when light and temperature are also increased.",
        "requirements": [
            "Sealed grow space (CO2 escapes quickly from leaky rooms)",
            "High light intensity (>600 PPFD — plants can't use extra CO2 without sufficient light)",
            "Higher temperature tolerance (82-86°F optimal with CO2 vs 75-80°F without)",
            "CO2 controller or timer",
        ],
        "ppfd_co2_correlation": [
            {"ppfd": 200, "optimal_co2_ppm": 400, "notes": "Ambient CO2 sufficient at low light"},
            {"ppfd": 400, "optimal_co2_ppm": 600, "notes": "Slight benefit from supplementation"},
            {"ppfd": 600, "optimal_co2_ppm": 800, "notes": "Moderate benefit — cost-effective threshold"},
            {"ppfd": 800, "optimal_co2_ppm": 1000, "notes": "Strong benefit — diminishing returns above this"},
            {"ppfd": 1000, "optimal_co2_ppm": 1200, "notes": "Maximum practical benefit for most grows"},
            {"ppfd": 1200, "optimal_co2_ppm": 1500, "notes": "Commercial intensity — requires perfect environment"},
        ],
        "stages_applicable": ["late_veg", "flower_transition", "early_flower", "mid_flower"],
        "not_applicable": ["germination", "seedling", "late_flower", "flush", "drying", "curing"],
        "methods": [
            {
                "method": "CO2 tank + regulator",
                "cost": "medium",
                "precision": "high",
                "notes": "Most common. Tank refills every 2-4 weeks for a tent.",
            },
            {
                "method": "CO2 burner (propane/natural gas)",
                "cost": "low_per_unit",
                "precision": "medium",
                "notes": "Produces heat and humidity — better for large rooms with AC.",
            },
            {
                "method": "CO2 bags (mushroom mycelium)",
                "cost": "low",
                "precision": "very_low",
                "notes": "Produces ~100-200ppm boost. Only useful for small sealed spaces. Not worth it for most.",
            },
        ],
    },
    {
        "id": "crop_steering",
        "name": "Crop Steering",
        "category": "advanced_cultivation",
        "description": "Manipulating environmental and irrigation parameters to push the plant toward vegetative or generative (flowering/fruiting) growth.",
        "vegetative_steering": {
            "goal": "More leaf/stem growth, larger plant framework",
            "strategies": [
                "Higher humidity (65-75%)",
                "Smaller temperature differential (day/night within 5°F)",
                "More frequent irrigation (keep substrate saturated)",
                "Lower EC (0.8-1.2)",
                "Blue-spectrum light emphasis",
                "Longer day length",
            ],
        },
        "generative_steering": {
            "goal": "More flower/fruit production, denser buds",
            "strategies": [
                "Lower humidity (40-55%)",
                "Larger temperature differential (day/night 10-15°F drop)",
                "Less frequent irrigation (allow dryback 10-20%)",
                "Higher EC (1.8-2.4)",
                "Red-spectrum light emphasis",
                "Shorter day length (12/12)",
            ],
        },
        "stages_applicable": ["late_veg", "flower_transition", "early_flower", "mid_flower"],
        "notes": "Crop steering is most effective in hydro/coco where irrigation frequency is highly controllable. Soil growers have less precision due to soil buffering.",
    },
    {
        "id": "foliar_feeding",
        "name": "Foliar Feeding",
        "category": "nutrition",
        "description": "Spraying nutrient solution directly onto leaves for rapid uptake. Bypasses root zone entirely.",
        "best_practices": [
            "Spray during lights-off or first/last 30 minutes of light cycle (stomata open, no light burn)",
            "Use fine mist sprayer — coverage is key",
            "pH foliar solution to 6.2-6.5 (leaf surface slightly higher pH than root zone)",
            "EC should be very low (0.2-0.5) — leaves burn easily",
            "Never foliar spray during flower (moisture in buds → mold/bud rot)",
            "Best for micronutrient deficiency correction (CalMag, iron, magnesium)",
        ],
        "common_foliar_products": [
            {
                "product": "CalMag spray",
                "use": "Calcium/magnesium deficiency correction",
                "frequency": "2-3x/week in veg",
            },
            {
                "product": "Silica spray",
                "use": "Strengthens cell walls, pest resistance",
                "frequency": "1-2x/week in veg",
            },
            {"product": "Kelp extract", "use": "Growth hormones, stress resistance", "frequency": "1x/week"},
            {
                "product": "IPM (neem/spinosad)",
                "use": "Pest prevention",
                "frequency": "Weekly preventive, 3-day intervals for active infestations",
            },
        ],
        "stages_applicable": ["seedling", "early_veg", "late_veg"],
        "not_applicable": ["flower_transition", "early_flower", "mid_flower", "late_flower", "flush"],
    },
    {
        "id": "silica_supplementation",
        "name": "Silica (Potassium Silicate)",
        "category": "nutrition",
        "description": "Strengthens cell walls, increases stem thickness, improves heat/drought/pest resistance.",
        "dosing": {"veg": "0.5-1 ml/gal", "flower": "0.5 ml/gal or discontinue"},
        "important_notes": [
            "ALWAYS add silica to water FIRST before other nutrients (raises pH significantly)",
            "Let silica mix for 5-10 minutes before adding base nutrients",
            "Silica is incompatible with concentrated nutrient solutions — never mix undiluted",
            "Discontinue in late flower (last 2-3 weeks)",
        ],
        "products": ["Armor Si (GH)", "Pro-TeKt", "Power Si", "Silica Blast (Botanicare)"],
        "stages_applicable": ["seedling", "early_veg", "late_veg", "flower_transition", "early_flower"],
    },
    {
        "id": "beneficial_microbes",
        "name": "Beneficial Microbes & Root Inoculants",
        "category": "root_health",
        "description": "Introduces beneficial bacteria/fungi to the root zone to outcompete pathogens, improve nutrient uptake, and protect against root diseases.",
        "products": [
            {
                "name": "Hydroguard",
                "type": "Bacillus amyloliquefaciens",
                "use": "Root rot prevention in hydro",
                "dosing": "2 ml/gal",
                "notes": "The standard for DWC/RDWC. Add at every res change.",
            },
            {
                "name": "Great White",
                "type": "Mycorrhizae + trichoderma + bacteria",
                "use": "Root colonization in soil/coco",
                "dosing": "1 tsp/gal (water-in) or dust roots at transplant",
                "notes": "Best for soil/coco. Less effective in pure hydro.",
            },
            {
                "name": "Recharge",
                "type": "Mycorrhizae + trichoderma + kelp + molasses",
                "use": "Soil biology booster",
                "dosing": "1/2 tsp/gal every 1-2 weeks",
                "notes": "Feeds existing soil microbes. Great for living soil.",
            },
            {
                "name": "Mammoth P",
                "type": "Phosphorus-solubilizing bacteria",
                "use": "Unlocks bound phosphorus in flower",
                "dosing": "0.16 ml/gal",
                "notes": "Most effective in flower when P demand is highest.",
            },
        ],
        "important_notes": [
            "Do NOT use hydrogen peroxide (H2O2) with beneficial microbes — it kills them",
            "Choose either sterile (H2O2) OR beneficial (Hydroguard) approach — not both",
            "Beneficials need warmish water (65-75°F) to thrive",
            "Reapply after any reservoir change or system cleaning",
        ],
    },
    {
        "id": "defoliation",
        "name": "Defoliation (Strategic Leaf Removal)",
        "category": "training",
        "description": "Removing select fan leaves to improve light penetration, airflow, and direct energy to bud sites.",
        "timing": [
            {"stage": "late_veg", "method": "Remove lower leaves that get no light (lollipop)", "intensity": "light"},
            {
                "stage": "flower_transition",
                "method": "Major defoliation day 1 and day 21 of flower (schwazzing)",
                "intensity": "heavy",
            },
            {
                "stage": "mid_flower",
                "method": "Selective tuck or remove leaves blocking bud sites",
                "intensity": "light",
            },
        ],
        "rules": [
            "Never remove more than 20-30% of leaves at once (except schwazze technique)",
            "Only defoliate healthy, vigorous plants — never stressed ones",
            "Autoflowers: very light defoliation only — they can't recover from heavy removal",
            "Always leave the top 2-3 fan leaves on each branch (they feed the bud below)",
        ],
        "stages_applicable": ["late_veg", "flower_transition", "early_flower", "mid_flower"],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# NUTRIENT BRAND ALTERNATIVES
# ─────────────────────────────────────────────────────────────────────────────

NUTRIENT_BRANDS: list[dict] = [
    {
        "id": "gh_flora_trio",
        "name": "General Hydroponics Flora Trio",
        "type": "3-part",
        "components": ["FloraMicro", "FloraGro", "FloraBloom"],
        "mixing_order": "Micro → Gro → Bloom (always Micro first)",
        "cost": "budget",
        "availability": "everywhere",
        "best_for": ["hydro", "coco", "soil"],
        "dosing_by_stage": {
            "seedling": {"micro": 1.25, "gro": 1.25, "bloom": 0.5, "unit": "ml/gal"},
            "early_veg": {"micro": 2.5, "gro": 2.5, "bloom": 1.0, "unit": "ml/gal"},
            "late_veg": {"micro": 3.75, "gro": 3.75, "bloom": 1.25, "unit": "ml/gal"},
            "flower_transition": {"micro": 3.75, "gro": 2.5, "bloom": 3.75, "unit": "ml/gal"},
            "early_flower": {"micro": 3.75, "gro": 1.25, "bloom": 5.0, "unit": "ml/gal"},
            "mid_flower": {"micro": 3.75, "gro": 0.625, "bloom": 6.25, "unit": "ml/gal"},
            "late_flower": {"micro": 2.5, "gro": 0, "bloom": 5.0, "unit": "ml/gal"},
            "flush": {"micro": 0, "gro": 0, "bloom": 0, "unit": "ml/gal"},
        },
    },
    {
        "id": "jacks_321",
        "name": "Jack's 321",
        "type": "2-part + Epsom",
        "components": ["Jack's Part A (5-12-26)", "Calcium Nitrate (Part B)", "Epsom Salt"],
        "mixing_order": "Part A → Epsom → Part B (dissolve each fully before adding next)",
        "cost": "very_budget",
        "availability": "online",
        "best_for": ["hydro", "coco"],
        "dosing_by_stage": {
            "seedling": {"part_a_g_per_gal": 0.9, "cal_nit_g_per_gal": 0.6, "epsom_g_per_gal": 0.3},
            "early_veg": {"part_a_g_per_gal": 1.8, "cal_nit_g_per_gal": 1.2, "epsom_g_per_gal": 0.6},
            "late_veg": {"part_a_g_per_gal": 3.6, "cal_nit_g_per_gal": 2.4, "epsom_g_per_gal": 1.2},
            "flower_transition": {"part_a_g_per_gal": 3.6, "cal_nit_g_per_gal": 2.4, "epsom_g_per_gal": 1.2},
            "early_flower": {"part_a_g_per_gal": 3.6, "cal_nit_g_per_gal": 2.4, "epsom_g_per_gal": 1.2},
            "mid_flower": {"part_a_g_per_gal": 3.6, "cal_nit_g_per_gal": 2.4, "epsom_g_per_gal": 1.2},
            "late_flower": {"part_a_g_per_gal": 2.7, "cal_nit_g_per_gal": 1.8, "epsom_g_per_gal": 0.9},
            "flush": {"part_a_g_per_gal": 0, "cal_nit_g_per_gal": 0, "epsom_g_per_gal": 0},
        },
        "notes": "Jack's 321 is 3.6g Part A, 2.4g Cal Nit, 1.2g Epsom per gallon at full strength. Extremely cost-effective for large grows.",
    },
    {
        "id": "athena",
        "name": "Athena Pro Line",
        "type": "2-part",
        "components": ["Athena Core", "Athena Bloom"],
        "mixing_order": "Core → Bloom",
        "cost": "premium",
        "availability": "online/hydro_stores",
        "best_for": ["hydro", "coco", "rockwool"],
        "dosing_by_stage": {
            "seedling": {"core_ml_per_gal": 1.5, "bloom_ml_per_gal": 0},
            "early_veg": {"core_ml_per_gal": 3.0, "bloom_ml_per_gal": 0},
            "late_veg": {"core_ml_per_gal": 4.5, "bloom_ml_per_gal": 0},
            "flower_transition": {"core_ml_per_gal": 3.0, "bloom_ml_per_gal": 3.0},
            "early_flower": {"core_ml_per_gal": 2.0, "bloom_ml_per_gal": 5.0},
            "mid_flower": {"core_ml_per_gal": 1.5, "bloom_ml_per_gal": 6.0},
            "late_flower": {"core_ml_per_gal": 1.0, "bloom_ml_per_gal": 4.0},
            "flush": {"core_ml_per_gal": 0, "bloom_ml_per_gal": 0},
        },
        "notes": "Commercial-grade. Simple 2-part with integrated CalMag. Popular in commercial cannabis facilities.",
    },
    {
        "id": "advanced_nutrients_ph_perfect",
        "name": "Advanced Nutrients pH Perfect (Sensi)",
        "type": "2-part",
        "components": ["Sensi Grow A+B", "Sensi Bloom A+B"],
        "mixing_order": "A → B (separate for veg and bloom)",
        "cost": "premium",
        "availability": "hydro_stores",
        "best_for": ["hydro", "coco"],
        "dosing_by_stage": {
            "seedling": {"a_ml_per_L": 1.0, "b_ml_per_L": 1.0, "line": "grow"},
            "early_veg": {"a_ml_per_L": 2.0, "b_ml_per_L": 2.0, "line": "grow"},
            "late_veg": {"a_ml_per_L": 4.0, "b_ml_per_L": 4.0, "line": "grow"},
            "flower_transition": {"a_ml_per_L": 2.0, "b_ml_per_L": 2.0, "line": "bloom"},
            "early_flower": {"a_ml_per_L": 4.0, "b_ml_per_L": 4.0, "line": "bloom"},
            "mid_flower": {"a_ml_per_L": 4.0, "b_ml_per_L": 4.0, "line": "bloom"},
            "late_flower": {"a_ml_per_L": 2.0, "b_ml_per_L": 2.0, "line": "bloom"},
            "flush": {"a_ml_per_L": 0, "b_ml_per_L": 0, "line": "none"},
        },
        "notes": "Self-adjusting pH technology (claims no pH adjustment needed). Expensive but popular for beginners who struggle with pH.",
    },
    {
        "id": "flora_nova",
        "name": "General Hydroponics FloraNova",
        "type": "1-part (two bottles — one for veg, one for bloom)",
        "components": ["FloraNova Grow", "FloraNova Bloom"],
        "mixing_order": "Shake VERY well before use (thick concentrate settles). One bottle at a time.",
        "cost": "budget",
        "availability": "everywhere",
        "best_for": ["hydro", "coco", "soil"],
        "dosing_by_stage": {
            "seedling": {"grow_ml_per_gal": 1.9, "bloom_ml_per_gal": 0},
            "early_veg": {"grow_ml_per_gal": 3.75, "bloom_ml_per_gal": 0},
            "late_veg": {"grow_ml_per_gal": 5.6, "bloom_ml_per_gal": 0},
            "flower_transition": {"grow_ml_per_gal": 2.8, "bloom_ml_per_gal": 3.75},
            "early_flower": {"grow_ml_per_gal": 0, "bloom_ml_per_gal": 5.6},
            "mid_flower": {"grow_ml_per_gal": 0, "bloom_ml_per_gal": 7.5},
            "late_flower": {"grow_ml_per_gal": 0, "bloom_ml_per_gal": 3.75},
            "flush": {"grow_ml_per_gal": 0, "bloom_ml_per_gal": 0},
        },
        "notes": "Simplest option — one bottle per phase. Great for beginners. Shake well — concentrate separates.",
    },
    {
        "id": "megacrop",
        "name": "Greenleaf Nutrients Mega Crop",
        "type": "1-part powder",
        "components": [
            "Mega Crop (all-in-one)",
            "Bud Explosion (flower booster, optional)",
            "Sweet Candy (flavor enhancer, optional)",
        ],
        "mixing_order": "Dissolve powder in warm water, stir well",
        "cost": "very_budget",
        "availability": "online",
        "best_for": ["hydro", "coco", "soil"],
        "dosing_by_stage": {
            "seedling": {"megacrop_g_per_gal": 1.0, "bud_explosion_g_per_gal": 0},
            "early_veg": {"megacrop_g_per_gal": 2.5, "bud_explosion_g_per_gal": 0},
            "late_veg": {"megacrop_g_per_gal": 4.0, "bud_explosion_g_per_gal": 0},
            "flower_transition": {"megacrop_g_per_gal": 4.5, "bud_explosion_g_per_gal": 0.5},
            "early_flower": {"megacrop_g_per_gal": 5.0, "bud_explosion_g_per_gal": 1.0},
            "mid_flower": {"megacrop_g_per_gal": 5.0, "bud_explosion_g_per_gal": 1.5},
            "late_flower": {"megacrop_g_per_gal": 3.0, "bud_explosion_g_per_gal": 0.5},
            "flush": {"megacrop_g_per_gal": 0, "bud_explosion_g_per_gal": 0},
        },
        "notes": "One powder does everything — includes CalMag. Incredibly cost-effective at ~$0.02/gal. Community favorite on r/microgrowery.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# WATER SOURCE PROFILES
# ─────────────────────────────────────────────────────────────────────────────

WATER_SOURCE_PROFILES: list[dict] = [
    {
        "id": "ro_water",
        "name": "Reverse Osmosis (RO) Water",
        "starting_ec": 0.0,
        "starting_ppm": 0,
        "ph": "6.5-7.0 (no buffering capacity)",
        "calmag_required": True,
        "calmag_dose_ml_per_gal": 2.0,
        "pros": [
            "Blank slate — total control over mineral content",
            "No chlorine/chloramine",
            "Consistent batch-to-batch",
        ],
        "cons": [
            "Must add CalMag (no natural minerals)",
            "pH unstable (no buffering)",
            "RO system cost and waste water",
        ],
        "notes": "Gold standard for precision growing. Always add CalMag first when using RO.",
    },
    {
        "id": "tap_water",
        "name": "Municipal Tap Water",
        "starting_ec": "0.2-0.5 (varies by city)",
        "starting_ppm": "100-250",
        "ph": "7.0-8.0 (often high, needs pH down)",
        "calmag_required": False,
        "calmag_dose_ml_per_gal": 0.5,
        "pros": ["Free/cheap", "Contains some minerals naturally", "Better pH buffering than RO"],
        "cons": [
            "Chlorine/chloramine must be removed",
            "Mineral content varies seasonally",
            "May contain heavy metals",
        ],
        "dechlorination": {
            "chlorine": "Let sit uncovered 24 hours (gasses off) or use dechlorinator drops",
            "chloramine": "Does NOT gas off — must use Campden tablets or activated carbon filter",
            "how_to_tell": "Check city water report. Most modern cities use chloramine.",
        },
        "notes": "Good enough for most grows. Dechlorinate and pH-adjust. Get a water report from your city.",
    },
    {
        "id": "well_water",
        "name": "Well Water",
        "starting_ec": "0.3-1.0+ (highly variable)",
        "starting_ppm": "150-500+",
        "ph": "6.5-8.5 (varies by geology)",
        "calmag_required": False,
        "calmag_dose_ml_per_gal": 0,
        "pros": ["Free", "No chlorine treatment", "Often rich in calcium/magnesium"],
        "cons": ["Highly variable mineral content", "May contain iron, sulfur, or heavy metals", "Must get tested"],
        "notes": "MUST get a water test before using. High iron or sulfur can cause lockout. Great if your well has clean water with moderate minerals.",
    },
    {
        "id": "distilled",
        "name": "Distilled Water",
        "starting_ec": 0.0,
        "starting_ppm": 0,
        "ph": "7.0 (no buffering)",
        "calmag_required": True,
        "calmag_dose_ml_per_gal": 2.0,
        "pros": ["Pure — identical to RO", "Available at any grocery store"],
        "cons": ["Expensive at scale ($1/gallon)", "Not practical for large grows", "No minerals — must add CalMag"],
        "notes": "Same as RO but purchased instead of filtered. Only practical for 1-2 plant grows.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# HARVEST DECISION MATRIX
# ─────────────────────────────────────────────────────────────────────────────

HARVEST_DECISION_MATRIX: dict = {
    "trichome_ratios": [
        {
            "effect": "Energetic / Uplifting / Cerebral",
            "clear_pct": 10,
            "milky_pct": 80,
            "amber_pct": 10,
            "notes": "Harvest early for more THC-dominant, less CBN. Energetic, racy high. Slight reduction in yield.",
        },
        {
            "effect": "Balanced / Most Common",
            "clear_pct": 5,
            "milky_pct": 70,
            "amber_pct": 25,
            "notes": "Standard harvest window. Mix of THC and CBN. Full-spectrum effects.",
        },
        {
            "effect": "Sedative / Body / Couch-lock",
            "clear_pct": 0,
            "milky_pct": 50,
            "amber_pct": 50,
            "notes": "Extended harvest for max CBN conversion. Heavy body high. Good for pain/sleep. Slightly degraded THC.",
        },
    ],
    "other_harvest_indicators": [
        "Most pistils (hairs) have darkened and curled in",
        "Calyxes are swollen and dense",
        "Fan leaves are yellowing and falling off naturally",
        "Trichome stalks are visible and heads are enlarged",
        "Breeder's recommended flowering time has passed",
    ],
    "flush_timing": {
        "hydro": "7-10 days plain water before harvest",
        "coco": "7-14 days reduced nutrients → plain water last 3-5 days",
        "soil": "14-21 days plain water (soil holds nutrients longer)",
        "notes": "Flushing is debated — some studies show no difference. At minimum, reduce nutrients in final week.",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# POST-HARVEST DETAILED GUIDE
# ─────────────────────────────────────────────────────────────────────────────

POST_HARVEST_GUIDE: dict = {
    "drying": {
        "environment": {
            "temp_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "airflow": "Gentle circulation — fan NOT pointed at buds. Just keep air moving.",
            "light": "Complete darkness (light degrades THC)",
            "duration_days": {"min": 7, "max": 14, "target": 10},
        },
        "method": [
            "Cut branches 12-18 inches long",
            "Optionally remove large fan leaves (wet trim) or leave intact (dry trim)",
            "Hang upside down on line/rack with 6+ inches between branches",
            "Small branches should snap (not bend) when done — 5-7 days minimum",
            "Stems should snap cleanly; if they bend, keep drying",
        ],
        "common_mistakes": [
            "Drying too fast (>3 days) — harsh smoke, hay smell, terpene loss",
            "Drying too slow (>14 days) — mold risk, diminishing returns",
            "Fan blowing directly on buds — uneven drying, crispy exterior/moist interior",
            "Temperature too high (>70°F) — terpene evaporation, harsh taste",
        ],
    },
    "curing": {
        "environment": {
            "temp_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 65, "target": 62},
            "container": "Glass mason jars (quart size). Fill 75% full.",
            "duration_days": {"min": 14, "max": 180, "ideal": 60},
        },
        "method": [
            "Trim buds to final shape (dry trim or finish wet trim)",
            "Place in mason jars — fill 3/4 full to allow air exchange",
            "Week 1: burp 2-3x daily for 10-15 minutes (release moisture and gases)",
            "Week 2-4: burp 1x daily for 5-10 minutes",
            "Month 2+: burp 1x weekly or seal completely",
            "Cure for minimum 2 weeks, ideal is 4-8 weeks. Some strains improve for 6+ months.",
        ],
        "humidity_packs": {
            "boveda_62": "Maintains 62% RH. Set-and-forget. Replace when crispy.",
            "boveda_58": "For drier preference or long-term storage.",
            "grove_bags": "Heat-sealed bags with built-in humidity regulation. No burping needed.",
        },
        "indicators_of_good_cure": [
            "Smooth, flavorful smoke — no harshness or hay smell",
            "Buds are slightly sticky but not wet",
            "Strong terpene aroma when jar is opened",
            "Ash burns to white/light gray (not black)",
        ],
    },
    "long_term_storage": {
        "method": "Sealed mason jars or vacuum-sealed bags with Boveda 58% in dark, cool place",
        "temp_f": {"min": 55, "max": 65, "target": 60},
        "humidity_pct": 58,
        "duration_months": {"good_quality": 12, "acceptable": 24},
        "degradation": "THC slowly converts to CBN over time. Light, heat, air, and moisture accelerate degradation.",
        "notes": "Properly cured and stored cannabis can remain excellent for 12+ months. Freezing is debated — can damage trichomes if not done carefully.",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# METHOD-SPECIFIC ENHANCEMENT SECTIONS
# ─────────────────────────────────────────────────────────────────────────────

HYDRO_RESERVOIR_MANAGEMENT: dict = {
    "description": "Reservoir management for active hydroponic systems (DWC, RDWC, NFT, Ebb & Flow, Drip, Aeroponics).",
    "sizing_guidelines": {
        "minimum_gallons_per_plant": 5,
        "recommended_gallons_per_plant": 10,
        "notes": "Larger reservoirs = more stable pH/EC, less frequent changes, more forgiving of mistakes.",
    },
    "change_schedule": {
        "full_change_interval_days": 7,
        "top_off": "Daily with plain pH'd water when EC rises. With dilute nutrient when EC drops.",
        "top_off_rule": "EC rising = plants drinking more water than nutrients → top off with plain water. EC dropping = plants eating more nutrients than water → top off with dilute nutrient mix.",
    },
    "water_temperature": {
        "target_f": 68,
        "range_f": {"min": 62, "max": 72},
        "too_warm_risk": "Root rot, low dissolved oxygen, pathogen growth",
        "too_cold_risk": "Slowed metabolism, nutrient lockout, stunted growth",
        "solutions_warm": [
            "Water chiller",
            "Frozen bottles (temporary)",
            "Insulate reservoir",
            "Move air pump outside tent",
        ],
        "solutions_cold": ["Aquarium heater (set to 68°F)", "Insulate reservoir"],
    },
    "dissolved_oxygen": {
        "target_ppm": 8.0,
        "minimum_ppm": 6.0,
        "how_to_increase": [
            "Larger air pump",
            "More/bigger air stones",
            "Waterfall return (RDWC)",
            "Lower water temperature",
        ],
        "why_important": "Roots need oxygen to function. Low DO → root rot, nutrient lockout, slow growth.",
    },
    "sterile_vs_beneficial": {
        "sterile": {
            "method": "Hydrogen peroxide (H2O2) at 3ml/gal of 3% solution",
            "pros": "Kills all pathogens. Clean roots. No biofilm.",
            "cons": "Must reapply every 2-3 days. Kills beneficial microbes too. Degrades in hours.",
        },
        "beneficial": {
            "method": "Hydroguard (Bacillus amyloliquefaciens) at 2ml/gal",
            "pros": "Continuous protection. Outcompetes pathogens. Set-and-forget per res change.",
            "cons": "Slightly cloudy water (normal). Doesn't work above 75°F water.",
        },
        "recommendation": "Beneficial approach (Hydroguard) for most growers. Sterile only if you have persistent issues.",
    },
}

COCO_SPECIFIC: dict = {
    "description": "Coco-specific management sections for coco coir grows.",
    "calmag_science": {
        "why_needed": "Coco coir's cation exchange sites naturally bind calcium and magnesium, making them unavailable to plants. Every watering must include CalMag.",
        "cec_explanation": "Coco has a high cation exchange capacity (CEC). The negatively-charged coco fiber attracts positively-charged Ca²⁺ and Mg²⁺ ions, locking them away from roots.",
        "led_increases_demand": "LED grow lights lack the infrared heat of HPS, making plants work harder to transpire. This reduces calcium transport (which moves passively with water flow), increasing CalMag demand by ~30%.",
        "ro_water_compounds": "RO water has zero minerals — combined with coco's CEC, plants get ZERO calcium without supplementation.",
        "dosing": {
            "new_unbuffered_coco": "5 ml/gal CalMag soak for 24h before first use",
            "pre_buffered_coco": "2 ml/gal at every feeding",
            "ro_water": "2-3 ml/gal at every feeding",
            "tap_water": "0.5-1 ml/gal (tap provides some Ca/Mg naturally)",
        },
        "deficiency_symptoms": [
            "Brown/rust spots on lower-mid leaves (calcium)",
            "Yellowing between leaf veins while veins stay green (magnesium)",
            "Stunted/slow new growth",
            "Leaf edges curling up",
        ],
    },
    "buffering_protocol": {
        "why": "Raw/new coco must be buffered to pre-saturate the CEC sites with calcium. Otherwise, plants will show CalMag deficiency for weeks.",
        "steps": [
            "Rinse coco thoroughly (remove dust, salts, shipping residue)",
            "Soak in CalMag solution (5 ml/gal) for 8-24 hours",
            "Drain and rinse again with plain water",
            "Soak again in light nutrient solution (EC 0.5-0.8) for 4-8 hours",
            "Drain to field capacity — ready to use",
        ],
        "pre_buffered_brands": ["Canna Coco Professional Plus", "Mother Earth Coco", "Royal Gold Tupur"],
        "needs_buffering": [
            "Generic coco bricks",
            "Bulk coco from garden centers",
            "Any coco that doesn't say 'pre-buffered'",
        ],
    },
    "fertigation_frequency": {
        "principle": "In coco, every watering is a feeding. More frequent smaller feedings = better results than infrequent large ones.",
        "by_stage": {
            "seedling": {
                "times_per_day": 1,
                "volume": "small (10-20% of pot volume)",
                "notes": "Keep coco moist but not soaked",
            },
            "early_veg": {
                "times_per_day": "1-2",
                "volume": "until 10-15% runoff",
                "notes": "As roots establish, increase frequency",
            },
            "late_veg": {
                "times_per_day": "2-3",
                "volume": "until 10-20% runoff each time",
                "notes": "Roots filling pot = more frequent feeds",
            },
            "flower_transition": {
                "times_per_day": "3-4",
                "volume": "until 10-20% runoff",
                "notes": "Plants drink more in flower",
            },
            "early_flower": {
                "times_per_day": "3-5",
                "volume": "until 10-20% runoff",
                "notes": "Peak water demand approaching",
            },
            "mid_flower": {
                "times_per_day": "4-6",
                "volume": "until 15-20% runoff",
                "notes": "Maximum water/nutrient demand. High frequency essential.",
            },
            "late_flower": {
                "times_per_day": "3-4",
                "volume": "reduce volume slightly",
                "notes": "Tapering down as harvest approaches",
            },
            "flush": {
                "times_per_day": "2-3",
                "volume": "plain pH'd water until runoff",
                "notes": "Flush with plain water for 3-7 days",
            },
        },
        "automation": "Automated drip/pump timers make high-frequency fertigation practical. Manual watering 5x/day is unsustainable — invest in automation.",
    },
    "dryback_monitoring": {
        "description": "Dryback % = how much the pot weight decreases between feedings. The #1 crop steering tool in coco.",
        "how_to_measure": "Weigh pot immediately after feeding (saturated weight) and before next feeding (dry weight). Dryback% = (saturated - dry) / saturated x 100",
        "targets": {
            "vegetative_steering": {
                "dryback_pct": "5-10%",
                "effect": "Keeps substrate wet = vegetative growth (leaves, stems)",
            },
            "generative_steering": {
                "dryback_pct": "10-20%",
                "effect": "Allows dryback = generative growth (flowers, fruits)",
            },
            "danger_zone": {
                "dryback_pct": ">30%",
                "effect": "Salt concentration dangerous, anaerobic conditions possible, hydrophobic surface",
            },
        },
        "never_let_coco_dry_fully": "Unlike soil, coco should NEVER fully dry out. Dry coco becomes hydrophobic (repels water), concentrates salts to toxic levels, and kills beneficial microbes.",
    },
    "runoff_management": {
        "description": "Input EC vs Runoff EC is the #1 diagnostic tool in coco growing.",
        "target_runoff_pct": "10-20% of input volume",
        "interpretation": {
            "runoff_ec_higher_than_input": "Salt accumulation in media. Solutions: increase runoff percentage, do a flush feed, reduce input EC.",
            "runoff_ec_lower_than_input": "Plant is eating more than you're providing. Solution: increase input EC.",
            "runoff_ec_matches_input": "Perfect balance — nutrients in = nutrients consumed. Ideal state.",
        },
        "when_to_flush": "Runoff EC is >0.5 higher than input EC consistently, or visible salt buildup on pot surface.",
    },
    "pot_sizing": {
        "progression": [
            {
                "stage": "seedling",
                "pot_size": "Solo cup or 0.5L",
                "notes": "Small pot encourages roots to fill quickly",
            },
            {
                "stage": "early_veg",
                "pot_size": "1 gallon / 4L",
                "notes": "Transplant when roots visible at drain holes",
            },
            {
                "stage": "final_pot",
                "pot_size": "3-7 gallon / 11-26L",
                "notes": "Final pot for flower. 5gal most common.",
            },
        ],
        "fabric_pots_recommended": True,
        "fabric_pot_benefits": [
            "Air pruning prevents root circling",
            "Better drainage",
            "Cools root zone through evaporation",
            "Prevents overwatering",
        ],
        "autoflower_exception": "Start autoflowers in final pot — they don't recover well from transplant shock.",
    },
    "reuse": {
        "can_reuse": True,
        "max_reuses": 3,
        "reuse_protocol": [
            "Remove old root mass (shake/pull out large pieces)",
            "Soak in enzyme solution (Hygrozyme, SLF-100) for 24h to break down dead roots",
            "Rinse thoroughly",
            "Re-buffer with CalMag solution (5ml/gal, soak 8-24h)",
            "Drain and mix with 20-30% fresh coco to restore structure",
        ],
        "when_to_discard": "After 3 uses, heavy salt damage, pest contamination, or foul smell.",
    },
}

SOIL_SPECIFIC: dict = {
    "description": "Soil-specific management for traditional soil grows.",
    "organic_vs_synthetic": {
        "organic": {
            "description": "Feed the soil, not the plant. Build a living ecosystem of microbes that break down organic matter into plant-available nutrients.",
            "pros": [
                "Better terpene profile (many growers report)",
                "Sustainable/environmentally friendly",
                "Builds soil life over time",
                "Harder to over-feed",
            ],
            "cons": [
                "Slower to correct deficiencies",
                "Less precise control",
                "Harder to dial in for max yield",
                "Can attract pests (gnats love organic matter)",
            ],
            "products": ["Dr. Earth", "Gaia Green", "Down To Earth", "BuildASoil", "Roots Organic"],
        },
        "synthetic": {
            "description": "Feed the plant directly with mineral salts. Fast-acting, precise, measurable with EC meter.",
            "pros": [
                "Precise control",
                "Fast deficiency correction",
                "Measurable with instruments",
                "Higher potential yield",
            ],
            "cons": [
                "Can burn plants easily",
                "Kills soil life over time",
                "Salt buildup requires flushing",
                "Environmental impact",
            ],
            "products": ["Fox Farm Trio", "General Hydroponics Flora series", "Dyna-Gro"],
        },
    },
    "living_soil": {
        "description": "A self-sustaining soil ecosystem where you water only — the soil provides all nutrients through microbial activity.",
        "components": [
            "Base soil (1/3 peat or coco, 1/3 aeration, 1/3 compost/EWC)",
            "Dry amendments (kelp meal, neem meal, crab meal, bone meal, rock dust)",
            "Microbial inoculants (mycorrhizae, trichoderma)",
            "Cover crop or mulch layer (straw, rice hulls)",
            "Earthworm castings (vermicompost) — 20-30% of mix",
        ],
        "water_only": True,
        "re_amend_schedule": "Top-dress with dry amendments every 3-4 weeks. Let soil biology break down amendments into plant-available form.",
        "popular_recipes": [
            {"name": "Coots Mix", "ratio": "1:1:1 peat:pumice:compost + minerals", "notes": "The OG water-only recipe"},
            {"name": "BuildASoil 3.0", "ratio": "Pre-mixed living soil", "notes": "Buy ready-made, just add water"},
            {"name": "KIS Organics", "ratio": "Pre-mixed biochar-based", "notes": "High-performance living soil"},
        ],
    },
    "wet_dry_cycle": {
        "description": "Soil grows benefit from a wet/dry cycle — water thoroughly, then let the top 1-2 inches dry before watering again.",
        "how_to_check": "Lift the pot — heavy = still wet, light = time to water. Or finger test: top inch dry = water.",
        "overwatering_signs": [
            "Droopy leaves that feel heavy/thick",
            "Slow growth",
            "Fungus gnats",
            "Green algae on soil surface",
        ],
        "underwatering_signs": [
            "Droopy leaves that feel thin/papery",
            "Dry/crusty soil pulling away from pot edges",
            "Leaves curling upward",
        ],
        "frequency_guidelines": {
            "seedling": "Every 2-3 days (small pot dries fast)",
            "veg_small_pot": "Every 1-2 days",
            "veg_final_pot": "Every 2-4 days",
            "flower": "Every 1-3 days (high water demand)",
        },
    },
    "compost_tea": {
        "description": "Brewed aerated compost tea (ACT) is a microbial inoculant that boosts soil biology.",
        "recipe": {
            "water_gallons": 5,
            "ewc_cups": 2,
            "molasses_tbsp": 1,
            "kelp_meal_tbsp": 1,
            "fish_hydrolysate_tbsp": 0.5,
        },
        "method": "Brew with air pump for 24-48 hours. Use immediately (microbes die without oxygen). Apply as soil drench.",
        "frequency": "Every 2-4 weeks during veg and early flower.",
        "notes": "Only useful for organic/living soil grows. Synthetic nutrients kill the microbes in the tea.",
    },
    "top_dressing": {
        "description": "Applying dry organic amendments to the soil surface. Microbes and watering break them down over 2-4 weeks.",
        "common_amendments": [
            {
                "product": "Earthworm castings",
                "npk": "1-0-0",
                "use": "General fertility, microbial boost",
                "rate": "1 cup per 5gal pot",
            },
            {
                "product": "Kelp meal",
                "npk": "1-0-2",
                "use": "Potassium, growth hormones, stress resistance",
                "rate": "2 tbsp per 5gal pot",
            },
            {
                "product": "Neem meal",
                "npk": "6-1-2",
                "use": "Nitrogen, pest deterrent (soil gnats)",
                "rate": "2 tbsp per 5gal pot",
            },
            {"product": "Bone meal", "npk": "3-15-0", "use": "Phosphorus for flower", "rate": "2 tbsp per 5gal pot"},
            {
                "product": "Gypsum",
                "npk": "0-0-0 (23% Ca, 18% S)",
                "use": "Calcium without raising pH",
                "rate": "1 tbsp per 5gal pot",
            },
        ],
        "schedule": "Top-dress every 3-4 weeks. Adjust recipe based on growth stage (more N in veg, more P/K in flower).",
    },
}

OUTDOOR_SPECIFIC: dict = {
    "description": "Outdoor-specific guidance for both soil and container grows.",
    "photoperiod_timing": {
        "northern_hemisphere": {
            "start_indoors": "March-April (start seeds under lights)",
            "transplant_outdoor": "May-June (after last frost)",
            "veg_period": "June-August (long days keep plants in veg)",
            "flower_trigger": "Mid-August to September (days shorten below 14 hours)",
            "harvest": "October-November (strain dependent)",
        },
        "southern_hemisphere": {
            "start_indoors": "September-October",
            "transplant_outdoor": "November-December",
            "veg_period": "December-February",
            "flower_trigger": "February-March",
            "harvest": "April-May",
        },
    },
    "light_deprivation": {
        "description": "Manually reducing light hours to force flowering earlier than natural photoperiod.",
        "method": "Cover plants with lightproof tarp at the same time daily (e.g., 8pm → 8am = 12 hours dark)",
        "benefits": [
            "Earlier harvest (avoid fall rain/mold)",
            "Multiple outdoor harvests per season",
            "Control timing precisely",
        ],
        "challenges": ["Must be consistent — one missed day can reveg", "Need lightproof material", "Labor intensive"],
    },
    "pest_management": {
        "common_outdoor_pests": [
            {
                "pest": "Caterpillars/budworms",
                "damage": "Bore into buds, cause rot from inside",
                "prevention": "BT (Bacillus thuringiensis) spray weekly",
                "treatment": "BT spray + manual removal",
            },
            {
                "pest": "Spider mites",
                "damage": "Yellow speckles on leaves, webbing",
                "prevention": "Neem oil weekly, predator mites",
                "treatment": "Spinosad, insecticidal soap, predator mites",
            },
            {
                "pest": "Aphids",
                "damage": "Clustered on stems/undersides, honeydew residue",
                "prevention": "Ladybugs, neem oil",
                "treatment": "Insecticidal soap, blast with water",
            },
            {
                "pest": "Powdery mildew",
                "damage": "White powder on leaves",
                "prevention": "Good airflow, defoliation, potassium bicarbonate spray",
                "treatment": "Remove affected leaves, sulfur spray, PM Wash",
            },
            {
                "pest": "Bud rot (Botrytis)",
                "damage": "Gray mold inside buds",
                "prevention": "Airflow, defoliation, harvest before extended rain",
                "treatment": "Remove affected buds immediately, increase airflow",
            },
        ],
        "ipm_schedule": {
            "preventive": "Weekly neem oil or BT spray during veg. Biweekly during early flower. Stop all sprays 2-3 weeks before harvest.",
            "active_infestation": "Every 3 days until controlled. Rotate products to prevent resistance.",
        },
    },
    "weather_challenges": {
        "rain": "Extended rain during flower = bud rot risk. Shake plants after rain, increase airflow, consider light dep for early harvest.",
        "wind": "Stake/cage tall plants. Strong wind can snap branches. Wind also dries out soil faster.",
        "heat_wave": "Shade cloth (30-50%), extra watering, mulch to retain moisture. Plants struggle above 95°F.",
        "frost": "Cover with frost cloth if unexpected frost. Harvest immediately if hard freeze coming. Plants die below 28°F.",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# ENHANCEMENT APPLICATION — Applies shared sections to a config dict
# ─────────────────────────────────────────────────────────────────────────────


def apply_enhancements(config: dict, grow_type_id: str) -> dict:
    """Apply shared enhancement sections to a grow type config dict.

    Adds scale_tiers, strain_adjustments, monitoring_thresholds, advanced_techniques,
    nutrient_brands, water_source_profiles, harvest_decision_matrix, post_harvest_guide,
    and method-specific sections based on the grow type category.
    """
    config["scale_tiers"] = SCALE_TIERS
    config["strain_adjustments"] = STRAIN_ADJUSTMENTS
    config["monitoring_thresholds"] = MONITORING_THRESHOLDS
    config["advanced_techniques"] = ADVANCED_TECHNIQUES
    config["nutrient_brands"] = NUTRIENT_BRANDS
    config["water_source_profiles"] = WATER_SOURCE_PROFILES
    config["harvest_decision_matrix"] = HARVEST_DECISION_MATRIX
    config["post_harvest_guide"] = POST_HARVEST_GUIDE

    # Method-specific sections based on grow type category
    hydro_types = {"dwc", "rdwc", "nft", "ebb_flow", "drip", "aeroponics"}
    if grow_type_id in hydro_types:
        config["reservoir_management"] = HYDRO_RESERVOIR_MANAGEMENT

    if grow_type_id == "coco":
        config["coco_specific"] = COCO_SPECIFIC

    if grow_type_id in ("soil", "outdoor_soil"):
        config["soil_specific"] = SOIL_SPECIFIC

    if grow_type_id in ("outdoor_soil", "outdoor_container"):
        config["outdoor_specific"] = OUTDOOR_SPECIFIC

    # Rockwool gets a subset of coco guidance (similar inert media management)
    if grow_type_id == "rockwool":
        config["substrate_management"] = {
            "description": "Rockwool-specific substrate management.",
            "conditioning": {
                "why": "Rockwool is naturally alkaline (pH 7.5-8.0). Must be soaked in pH 5.5 solution for 24h before use.",
                "steps": [
                    "Soak cubes/slabs in pH 5.5 nutrient solution (EC 0.5) for 24 hours",
                    "Drain and squeeze gently — do NOT wring out (damages fiber structure)",
                    "Check runoff pH — should be 5.5-6.0. If still high, soak again.",
                ],
            },
            "irrigation": COCO_SPECIFIC["fertigation_frequency"],
            "dryback": COCO_SPECIFIC["dryback_monitoring"],
            "runoff": COCO_SPECIFIC["runoff_management"],
            "disposal": "Rockwool is NOT biodegradable. Do not compost. Landfill or repurpose as insulation/drainage material.",
        }

    # Kratky gets a simplified version (passive — no pump/res management)
    if grow_type_id == "kratky":
        config["kratky_specific"] = {
            "description": "Kratky-specific passive hydroponic management.",
            "principle": "Plants grow roots into a static nutrient solution. As plants drink, an air gap forms above the water line — roots in the air gap absorb oxygen. No pump, no air stone, no electricity needed.",
            "critical_rules": [
                "NEVER refill to original level — the air gap roots will drown",
                "Top off only 50% of consumed volume if plants are struggling",
                "Solution should be consumed by harvest — if not, container was too large",
                "Start with correct container size: 1-5 gallon per plant depending on grow duration",
            ],
            "container_sizing": {
                "lettuce_herbs": "0.5-1 gallon",
                "small_cannabis_auto": "3-5 gallons",
                "large_cannabis_photo": "5-10 gallons (but DWC is better for large plants)",
            },
            "limitations": [
                "Best for short grows (lettuce, herbs, autoflowers)",
                "Long photo period grows may outdrink the container",
                "No way to adjust EC/pH mid-grow without disturbing roots",
                "Single-use solution — can't recirculate or top off easily",
            ],
        }

    return config
