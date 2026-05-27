"""Living Soil (No-Till) — Complete grow type configuration.

Enterprise-grade configuration for living soil / no-till growing.
Focuses on building and maintaining a thriving soil ecosystem rather than
feeding the plant directly. Minimal inputs, maximum biology.

Data sources:
  - No-till/living soil community (BuildASoil, KIS Organics)
  - Korean Natural Farming (KNF) methodology
  - Soil food web research (Dr. Elaine Ingham)
  - Regenerative agriculture principles adapted for controlled environment
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES
# ─────────────────────────────────────────────────────────────────────────────

LIVING_SOIL_STAGES: list[dict] = [
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Germinate in moist paper towel or directly in living soil. Soil should have been cooking (composting) for 2-4 weeks minimum before planting. Microbes are already active.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
        },
        "soil": {"notes": "Soil should have been built and cooking 2-4 weeks prior. Biology active. No hot spots."},
        "nutrients": {
            "strength_pct": 0,
            "approach": "None needed — soil provides. Germinate in plain water or directly in soil.",
        },
        "tasks": [
            {
                "name": "Verify soil readiness",
                "description": "Soil has been cooking. No ammonia smell. Worms active if present.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Germinate seeds",
                "description": "Paper towel method or direct sow in soil at 1/4 inch depth.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Moisten surface",
                "description": "Light mist. Don't disturb soil structure.",
                "interval_days": 1,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Seed cracking?",
            "Soil temp safe (not hot from composting)?",
            "No fungal problems on surface?",
        ],
        "common_problems": [
            {
                "issue": "Seed burned by hot soil",
                "cause": "Soil still actively composting (too fresh)",
                "solution": "Let soil cook longer. Test: plant lettuce seed — if it grows, soil is ready.",
            },
            {
                "issue": "Damping off",
                "cause": "Too wet + fungal imbalance in new soil",
                "solution": "Add more aeration. Reduce watering. Dust seed with mycorrhizae.",
            },
        ],
        "transition_signals": ["Taproot emerged", "Cotyledons above soil"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Direct sow in established bed works great."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Living soil beds thrive in greenhouses."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Seedling grows in living soil. Mycorrhizal colonization beginning. Only water — no feeding needed. Soil biology does the work.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 60, "max": 75, "target": 68},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 300, "target": 200},
            "light_dli": {"min": 6, "max": 19, "target": 13},
        },
        "soil": {"notes": "Water only. Soil provides all nutrition via microbial activity."},
        "nutrients": {"strength_pct": 0, "approach": "Water only. Soil biology feeds the plant."},
        "tasks": [
            {
                "name": "Water gently",
                "description": "Small amounts around seedling. Don't flood. Maintain even moisture.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Observe soil surface",
                "description": "Healthy soil shows white mycelium threads. Good sign!",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Mulch lightly",
                "description": "Thin layer of straw or leaves. Protects biology.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Avoid disturbing soil",
                "description": "No tilling, poking, or compacting. Let biology establish.",
                "interval_days": None,
                "priority": "high",
            },
        ],
        "health_checks": ["Seedling growing?", "White mycelium on surface (good)?", "Soil moisture even?"],
        "common_problems": [
            {
                "issue": "Slow initial growth",
                "cause": "Normal for living soil — biology establishing",
                "solution": "Patience. Living soil starts slow but accelerates in veg. Don't add synthetic fertilizer.",
            },
            {
                "issue": "Fungus gnats",
                "cause": "Organic matter attracting gnats",
                "solution": "Yellow sticky traps. Top layer of pumice/perlite. BTI. Predatory mites.",
            },
        ],
        "transition_signals": ["3-4 true leaf sets", "Mycelium visible on surface", "Growing without any feeding"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Natural soil biology enhanced by outdoor conditions."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Protected environment for biology establishment."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Mycorrhizal network fully colonized. Plant growth accelerates. Still water-only in well-built soil. Can add botanical teas or KNF inputs as supplemental biology boosts.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 600, "target": 500},
            "light_dli": {"min": 25, "max": 39, "target": 32},
        },
        "soil": {"notes": "Biology in full swing. Mycorrhizae extending root network 100x. Water-only or light teas."},
        "nutrients": {
            "strength_pct": 0,
            "approach": "Water only in well-built soil. Optional: compost tea or aloe vera foliar.",
        },
        "tasks": [
            {
                "name": "Water to maintain moisture",
                "description": "Wet-dry cycle: water when top inch dry. Let biology breathe.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Compost tea (optional)",
                "description": "Aerated compost tea as soil drench. Boosts biology.",
                "interval_days": 14,
                "priority": "low",
            },
            {
                "name": "Observe cover crop",
                "description": "If cover crop growing, let it. Feeds soil. Chop and drop before it competes.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Begin training",
                "description": "Gentle LST. Avoid high-stress techniques that damage biology recovery.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Vigorous growth?",
            "Soil smells earthy (good)?",
            "Mycelium still active?",
            "No deficiency signs?",
        ],
        "common_problems": [
            {
                "issue": "Slow growth compared to synthetic",
                "cause": "Normal — living soil is slower in early veg",
                "solution": "Trust the process. Growth explodes in late veg. Don't add salts.",
            },
            {
                "issue": "Yellowing lower leaves",
                "cause": "Soil may need more nitrogen — microbes not mineralizing enough",
                "solution": "Neem meal top-dress. Alfalfa tea. Don't panic — minor yellowing is normal.",
            },
        ],
        "transition_signals": ["5-6 nodes", "Growth visibly accelerating", "Healthy deep green color"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Outdoor living soil benefits from natural rainfall diversity."},
                "extra_tasks": [
                    {
                        "name": "Collect rainwater",
                        "description": "Rainwater ideal for living soil — microbe-friendly.",
                        "interval_days": None,
                        "priority": "low",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Controlled watering ideal for wet-dry cycles."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 14, "max": 35, "typical": 21},
        "description": "Explosive growth. Living soil plants catch up and often surpass synthetic-fed plants at this stage. Mycorrhizal network at peak. Optional top-dress for heavy feeders.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 65, "target": 58},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 500, "max": 700, "target": 600},
            "light_dli": {"min": 32, "max": 45, "target": 39},
        },
        "soil": {"notes": "Peak biological activity. Optional top-dress if heavy feeder strain."},
        "nutrients": {
            "strength_pct": 0,
            "approach": "Water only. Optional: neem/kelp/crustacean meal top-dress for heavy feeders.",
        },
        "tasks": [
            {
                "name": "Water wet-dry cycles",
                "description": "Water thoroughly, then let dry to top inch. Oxygen for roots + microbes.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Top-dress (if needed)",
                "description": "1-2 tbsp neem + kelp meal per gallon of soil. Only if plant shows hunger.",
                "interval_days": 21,
                "priority": "low",
            },
            {
                "name": "Chop and drop cover crop",
                "description": "Cut cover crop at soil level. Leave on surface as mulch. Feeds soil.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Train canopy",
                "description": "Gentle LST/SCROG. Living soil plants are vigorous.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Explosive growth?",
            "No deficiencies?",
            "Soil biology thriving?",
            "Worms active (if present)?",
        ],
        "common_problems": [
            {
                "issue": "Over-watering killing biology",
                "cause": "No wet-dry cycle — anaerobic conditions",
                "solution": "Let soil dry between waterings. Biology needs oxygen. Add perlite if soil too dense.",
            },
            {
                "issue": "Nutrient lockout despite rich soil",
                "cause": "pH issue or biology crash from fungicide/H2O2",
                "solution": "NEVER use H2O2, fungicides, or synthetic in living soil. Re-inoculate with compost tea.",
            },
        ],
        "transition_signals": ["Canopy filling out", "Ready for flip", "Vigorous, healthy growth"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Peak growing season. Living soil at its best outdoors."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Ventilate well in late veg."}, "extra_tasks": []},
        },
    },
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Flip to 12/12. Plants stretch. In living soil, transition is smooth — biology adapts to plant's changing demands. Optional bloom top-dress.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 64, "max": 72, "target": 68},
            "humidity_pct": {"min": 45, "max": 60, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.3, "target": 1.1},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 800, "target": 700},
            "light_dli": {"min": 25, "max": 35, "target": 30},
        },
        "soil": {"notes": "Top-dress bloom amendments now. Microbes will mineralize by the time buds form."},
        "nutrients": {
            "strength_pct": 0,
            "approach": "Top-dress: bone meal + langbeinite (or bloom dry amendment). Water only otherwise.",
        },
        "tasks": [
            {
                "name": "Flip light schedule",
                "description": "Switch to 12/12.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Bloom top-dress",
                "description": "Bone meal (P), langbeinite (K-Mg-S), or all-purpose bloom dry amendment.",
                "interval_days": None,
                "priority": "medium",
            },
            {"name": "Manage stretch", "description": "LST as needed.", "interval_days": 2, "priority": "medium"},
            {
                "name": "Water increase",
                "description": "Stretching plants drink more. Maintain wet-dry cycle.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": ["Stretch managed?", "Soil staying moist enough?", "No deficiency onset?"],
        "common_problems": [
            {
                "issue": "Phosphorus deficiency at flip",
                "cause": "Soil phosphorus locked or depleted",
                "solution": "Bone meal top-dress takes 1-2 weeks. Liquid fish bone meal for faster availability.",
            },
        ],
        "transition_signals": ["Stretch slowing", "Pre-flowers visible", "Top-dress breaking down into soil"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Natural photoperiod. Top-dress as days shorten."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Blackout covers if needed."}, "extra_tasks": []},
        },
    },
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Bud sites forming. Living soil delivers broad-spectrum nutrition — terpene profiles are often superior due to diverse mineral availability from biological breakdown.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 79, "target": 75},
            "temp_night_f": {"min": 62, "max": 70, "target": 66},
            "humidity_pct": {"min": 40, "max": 55, "target": 48},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 25, "max": 39, "target": 32},
        },
        "soil": {"notes": "Bloom amendments mineralizing. Biology delivering P-K to roots on demand."},
        "nutrients": {
            "strength_pct": 0,
            "approach": "Water only. Soil provides. Optional: coconut water (natural cytokinins) as drench.",
        },
        "tasks": [
            {
                "name": "Water consistently",
                "description": "Flowering plants need consistent moisture. Don't over-dry.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Coconut water drench (optional)",
                "description": "1 tbsp/gal raw coconut water. Natural cytokinins boost flower sites.",
                "interval_days": 7,
                "priority": "low",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Remove lower fan leaves. Light defoliation only.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": ["Bud sites forming?", "Soil biology still active?", "Humidity controlled?"],
        "common_problems": [
            {
                "issue": "Calcium deficiency in flower",
                "cause": "Calcium demand spikes in flower, biology slow to deliver",
                "solution": "Gypsum top-dress. Dolomite lime. Cal-mag foliar (organic).",
            },
        ],
        "transition_signals": ["Buds at all sites", "Pistils abundant", "Stretch complete"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Watch for caterpillars in buds."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Airflow critical as buds develop."}, "extra_tasks": []},
        },
    },
    {
        "id": "mid_flower",
        "name": "Mid Flower (Bulk Phase)",
        "order": 7,
        "duration_days": {"min": 14, "max": 28, "typical": 21},
        "description": "Peak bud development. Living soil shows its strength — complex terpene profiles from diverse mineral availability. Soil biology at peak activity supporting heavy feeding.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 78, "target": 74},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 38, "max": 50, "target": 44},
            "vpd_kpa": {"min": 1.2, "max": 1.5, "target": 1.3},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
        },
        "soil": {"notes": "Peak demand. Biology working hard. May need supplemental tea if soil is first cycle."},
        "nutrients": {
            "strength_pct": 0,
            "approach": "Water only in established beds. First-cycle soil may benefit from compost tea or top-dress.",
        },
        "tasks": [
            {
                "name": "Water consistently",
                "description": "Don't let soil dry excessively during peak flower. Every 2-3 days.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Monitor bud development",
                "description": "Dense buds = bud rot risk. Defoliate for airflow.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Compost tea (if needed)",
                "description": "Only if plant showing hunger. Aerated compost tea as booster.",
                "interval_days": 14,
                "priority": "low",
            },
            {
                "name": "Support heavy colas",
                "description": "Stakes or trellis for large buds.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": ["Buds swelling?", "No bud rot?", "Trichomes developing?", "Soil still has earthy smell?"],
        "common_problems": [
            {
                "issue": "Fade too early",
                "cause": "Soil depleted — first cycle or undersized pot",
                "solution": "Top-dress bloom amendments. Larger pot next cycle (15+ gal for no-till). Build soil richer.",
            },
            {
                "issue": "Bud rot from dense canopy",
                "cause": "Living soil + mulch = higher humidity near soil surface",
                "solution": "Defoliate. Good airflow. Remove mulch from directly under buds if humidity high.",
            },
        ],
        "transition_signals": ["Buds dense", "Trichomes milky", "Pistils browning"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Rain = bud rot risk. Cover in rain."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Monitor humidity carefully."}, "extra_tasks": []},
        },
    },
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Final ripening. Living soil plants often produce superior terpene profiles during this phase due to slow, balanced nutrient release from biology.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 72},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 48, "target": 42},
            "vpd_kpa": {"min": 1.2, "max": 1.5, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 800},
            "light_dli": {"min": 25, "max": 39, "target": 35},
        },
        "soil": {"notes": "Biology slowing as plant demands decrease. Natural fade from soil depletion."},
        "nutrients": {"strength_pct": 0, "approach": "Water only. Let plant and soil reach natural equilibrium."},
        "tasks": [
            {
                "name": "Check trichomes",
                "description": "60x loupe. 70-80% milky, 10-20% amber.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Reduce watering slightly",
                "description": "Slight drought stress can enhance terpene production.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Inspect for rot",
                "description": "Daily check of dense buds.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Trichomes maturing?", "Natural fade occurring?", "No rot?"],
        "common_problems": [
            {
                "issue": "No fade (plant still green)",
                "cause": "Rich soil still feeding plant",
                "solution": "This is fine — living soil doesn't need traditional flush. Quality is already excellent.",
            },
        ],
        "transition_signals": ["Trichomes at target", "Natural fade", "Pistils receded"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Cool nights enhance color development."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Drop night temps for color/terpenes."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 7},
        "description": "Living soil doesn't require traditional flushing. The soil IS the flush — biology self-regulates. Just water only (which you've been doing anyway). Many growers skip this entirely.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 72},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 48, "target": 42},
            "vpd_kpa": {"min": 1.2, "max": 1.5, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 17, "max": 30, "target": 26},
        },
        "soil": {"notes": "No flush needed in living soil — this IS water-only growing. Continue as normal."},
        "nutrients": {
            "strength_pct": 0,
            "approach": "Same as always: water only. Living soil doesn't accumulate synthetic salts.",
        },
        "tasks": [
            {
                "name": "Continue water only",
                "description": "Same as you've been doing. No change needed.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Monitor trichomes",
                "description": "Continue checking ripeness daily.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Prep for harvest",
                "description": "Gather trimming supplies. Plan harvest day.",
                "interval_days": None,
                "priority": "low",
            },
        ],
        "health_checks": ["Plant still healthy?", "Trichomes at target?", "Ready to chop?"],
        "common_problems": [
            {
                "issue": "Grower worried about not flushing",
                "cause": "Habit from synthetic growing",
                "solution": "Living soil doesn't need flush. No salt buildup. Smoke is already smooth from organic growing.",
            },
        ],
        "transition_signals": ["Trichomes at target maturity", "Natural fade progressing", "Harvest window open"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Harvest before frost. Don't wait too long."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Harvest at optimal trichome maturity."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Chop plant. In no-till living soil: leave roots in soil! They decompose and feed the next cycle. Immediately plant cover crop or let soil rest.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
        },
        "soil": {
            "notes": "DO NOT remove roots. Cut at soil surface. Roots decompose and become food for next cycle. This is the no-till principle."
        },
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Cut plant at soil surface",
                "description": "LEAVE ROOTS IN SOIL. Cut stem at base, don't pull.",
                "interval_days": None,
                "priority": "high",
            },
            {"name": "Trim", "description": "Wet or dry trim preference.", "interval_days": None, "priority": "high"},
            {
                "name": "Plant cover crop immediately",
                "description": "Scatter clover/rye/radish seed on surface. Keeps soil alive between cycles.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Top-dress for next cycle",
                "description": "Add fresh amendments (neem, kelp, crustacean, compost) for next plant.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Trichomes at target?", "Cover crop seed down?", "Soil protected (mulched)?"],
        "common_problems": [
            {
                "issue": "Grower pulls roots out",
                "cause": "Habit from other methods",
                "solution": "ALWAYS leave roots in no-till. They are food for the next cycle's microbes.",
            },
        ],
        "transition_signals": ["Plant chopped", "Cover crop planted", "Branches hung for drying"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Harvest before frost. Cover crop protects soil over winter."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Immediate cover crop for year-round cycling."},
                "extra_tasks": [],
            },
        },
    },
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Standard slow dry. Living soil flower is known for exceptionally smooth smoke when dried and cured properly.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "light_hours": 0,
        },
        "soil": {"notes": "Soil resting with cover crop growing. Preparing for next cycle."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Hang whole plant or branches",
                "description": "Slow dry. 60-65°F, 55-62% RH, complete darkness.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monitor conditions",
                "description": "Check daily. Adjust if drying too fast/slow.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Stem snap test",
                "description": "Small stems snap cleanly = ready.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": ["Temp/humidity in range?", "No mold?", "Slow enough (7+ days)?"],
        "common_problems": [
            {
                "issue": "Hay smell",
                "cause": "Dried too fast (chlorophyll not broken down)",
                "solution": "Slower dry next time. Can still recover with long cure (4-8 weeks).",
            },
        ],
        "transition_signals": ["Small stems snap", "Buds slightly crispy outside, moist inside"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Always dry indoors in controlled environment."},
                "extra_tasks": [],
            },
            "greenhouse": {"environment_overrides": {"notes": "Dry indoors, not in greenhouse."}, "extra_tasks": []},
        },
    },
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Living soil flower benefits enormously from extended cure (6-8 weeks). The complex terpene profiles from biological growing continue developing in the jar.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "light_hours": 0,
        },
        "soil": {"notes": "Soil cycling with cover crop. Top-dress breakdown continuing."},
        "nutrients": {"strength_pct": 0, "approach": "None."},
        "tasks": [
            {
                "name": "Burp jars",
                "description": "Daily 2 weeks, then weekly. Living soil flower improves dramatically with time.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor humidity",
                "description": "58-62%. Boveda 62 packs.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Extended cure",
                "description": "Living soil flower peaks at 6-8 weeks cure. Don't rush.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Humidity 58-62%?", "Smell improving weekly?", "No mold?"],
        "common_problems": [
            {
                "issue": "Impatient — smoking too early",
                "cause": "Living soil flower needs longer cure for full expression",
                "solution": "Set aside a jar for 8 weeks. Compare to week-2 jar. You'll never rush again.",
            },
        ],
        "transition_signals": ["Smooth smoke", "Complex terpene profile", "No chlorophyll taste"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Cure indoors in stable environment."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT
# ─────────────────────────────────────────────────────────────────────────────

LIVING_SOIL_EQUIPMENT: list[dict] = [
    {
        "name": "Large fabric pots (15-30 gal) or raised bed",
        "category": "essential",
        "essential": True,
        "description": "Bigger = better for living soil. No-till beds or large fabric pots (minimum 15 gal for no-till).",
    },
    {
        "name": "Living soil base mix",
        "category": "essential",
        "essential": True,
        "description": "High-quality compost + peat/coco + aeration. BuildASoil, KIS, or custom mix.",
    },
    {
        "name": "Dry amendments (neem, kelp, crustacean)",
        "category": "essential",
        "essential": True,
        "description": "Slow-release organic inputs that biology breaks down. Applied as top-dress.",
    },
    {
        "name": "Worm castings",
        "category": "essential",
        "essential": True,
        "description": "High-quality vermicompost. Microbial inoculant + slow-release nutrition.",
    },
    {
        "name": "Mulch material",
        "category": "essential",
        "essential": True,
        "description": "Straw, leaves, or cover crop residue. Protects soil surface and feeds biology.",
    },
    {
        "name": "Cover crop seeds",
        "category": "essential",
        "essential": True,
        "description": "Clover, crimson clover, tillage radish, rye. Fixes nitrogen, prevents erosion, feeds microbes.",
    },
    {
        "name": "Mycorrhizal inoculant",
        "category": "essential",
        "essential": True,
        "description": "Endo-mycorrhizae (Glomus intraradices). Apply at planting. Extends root network 100x.",
    },
    {
        "name": "Compost tea brewer",
        "category": "recommended",
        "essential": False,
        "description": "5-gallon bucket + air pump + air stone. Brews aerated compost tea in 24-48h.",
    },
    {
        "name": "Worm bin",
        "category": "recommended",
        "essential": False,
        "description": "Continuous supply of fresh castings. Red wigglers (Eisenia fetida).",
    },
    {
        "name": "Moisture meter",
        "category": "recommended",
        "essential": False,
        "description": "Probe to check soil moisture at depth. Avoid over/under watering.",
    },
    {
        "name": "Soil thermometer",
        "category": "recommended",
        "essential": False,
        "description": "Monitor soil temp during cooking phase. Below 70°F = safe to plant.",
    },
    {
        "name": "Microscope (400x)",
        "category": "optional",
        "essential": False,
        "description": "View soil biology: bacteria, fungi, protozoa, nematodes. Verify soil health.",
    },
    {
        "name": "KNF inputs (FPJ, FFJ, LAB)",
        "category": "optional",
        "essential": False,
        "description": "Korean Natural Farming ferments. Fermented plant juice, fruit juice, lactic acid bacteria.",
    },
    {
        "name": "Rock dust (glacial/basalt)",
        "category": "recommended",
        "essential": False,
        "description": "Broad-spectrum minerals. Slow-release via biological breakdown.",
    },
    {
        "name": "Biochar",
        "category": "optional",
        "essential": False,
        "description": "Charged biochar provides microbial habitat. Lasts decades in soil.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

LIVING_SOIL_QUICK_REFERENCE: dict = {
    "method_summary": "Feed the soil, not the plant. Build a thriving microbiome that delivers nutrition on demand. Water-only growing after initial soil build.",
    "difficulty": "intermediate",
    "maintenance_level": "Very low — water only during grow. Soil building is the investment.",
    "key_advantages": [
        "Water-only growing (zero mixing nutrients)",
        "Superior terpene profiles",
        "Self-sustaining ecosystem",
        "Soil improves with each cycle (no-till)",
        "No pH adjustment needed",
        "No nutrient burn possible",
        "Environmental sustainability",
    ],
    "key_challenges": [
        "2-4 week soil build/cook time before planting",
        "Slower start than synthetic",
        "Larger containers needed (15+ gal)",
        "Cannot correct deficiencies quickly",
        "Fungus gnats attracted to organic matter",
    ],
    "watering_approach": {
        "method": "Wet-dry cycle: water thoroughly, then let top inch dry before next watering",
        "frequency": "Every 2-4 days depending on pot size, plant size, and environment",
        "water_quality": "Dechlorinated, room temperature. Rainwater ideal.",
    },
    "critical_rules": [
        "NEVER use synthetic fertilizers, H2O2, or fungicides — kills biology",
        "NEVER pull roots out at harvest (no-till principle)",
        "Always keep soil covered (mulch or cover crop)",
        "Let soil cook 2-4 weeks before first planting",
        "Bigger pot = better results (minimum 15 gal for no-till)",
        "Trust the process — living soil starts slow but catches up",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING
# ─────────────────────────────────────────────────────────────────────────────

LIVING_SOIL_TROUBLESHOOTING: list[dict] = [
    {
        "category": "soil_biology",
        "issues": [
            {
                "symptom": "Soil smells bad (anaerobic/rotten)",
                "cause": "Over-watering killed aerobic biology. Anaerobic conditions.",
                "solution": "Let dry thoroughly. Aerate top layer gently. Add fresh compost on surface. May need to start over if severe.",
            },
            {
                "symptom": "No mycelium visible on surface",
                "cause": "Soil too dry, too hot, or biology crashed",
                "solution": "Maintain moisture. Add fresh mulch. Re-inoculate with quality compost. Mycelium returns when conditions right.",
            },
            {
                "symptom": "Soil biology crashed (sudden deficiencies)",
                "cause": "Chlorinated water, H2O2, fungicide, or excessive heat killed microbes",
                "solution": "Stop the cause. Compost tea drench. Re-inoculate with mycorrhizae. Fresh worm castings top-dress. Takes 1-2 weeks to recover.",
            },
        ],
    },
    {
        "category": "nutrient_issues",
        "issues": [
            {
                "symptom": "Nitrogen deficiency (yellowing lower leaves)",
                "cause": "Soil nitrogen depleted or biology slow to mineralize",
                "solution": "Neem meal or alfalfa meal top-dress. Compost tea. Larger pot next cycle.",
            },
            {
                "symptom": "Phosphorus deficiency (purple stems, slow flowering)",
                "cause": "Cold soil slowing P availability or soil P depleted",
                "solution": "Bone meal top-dress. Ensure soil temp > 65°F (biology needs warmth). Mycorrhizae help P access.",
            },
            {
                "symptom": "Overall slow growth despite rich soil",
                "cause": "pH too extreme, compacted soil, or root-bound in small pot",
                "solution": "Living soil should self-buffer pH. Aerate gently. Transplant to larger pot if root-bound.",
            },
        ],
    },
    {
        "category": "pest_management",
        "issues": [
            {
                "symptom": "Fungus gnats everywhere",
                "cause": "Organic matter + moisture = gnat paradise",
                "solution": "Top layer of coarse pumice (deters egg laying). Yellow sticky traps. BTI (Mosquito Bits). Stratiolaelaps predatory mites.",
            },
            {
                "symptom": "Thrips or aphids",
                "cause": "Lack of beneficial predators",
                "solution": "Introduce beneficial insects (ladybugs, lacewings). Neem oil foliar (doesn't harm soil biology). IPM focus.",
            },
            {
                "symptom": "Root aphids",
                "cause": "Contaminated soil or pots from previous grow",
                "solution": "Beneficial nematodes drench (Steinernema feltiae). Neem cake in soil. Fresh clean soil for worst cases.",
            },
        ],
    },
    {
        "category": "soil_management",
        "issues": [
            {
                "symptom": "Soil compacting over cycles",
                "cause": "Peat breaking down, insufficient aeration amendment",
                "solution": "Top-dress with pumice or rice hulls. Add more perlite/pumice in rebuild. Cover crop roots help aerate.",
            },
            {
                "symptom": "Water running off surface (hydrophobic)",
                "cause": "Peat-heavy soil dried out too much",
                "solution": "Add aloe vera or yucca extract as wetting agent. Water slowly. Re-wet surface layer.",
            },
            {
                "symptom": "Soil volume decreasing over cycles",
                "cause": "Organic matter decomposing (normal)",
                "solution": "Top up with fresh compost + castings each cycle. Add 1-2 inches on top. This is normal maintenance.",
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# LIVING SOIL ECOSYSTEM — Core differentiator
# ─────────────────────────────────────────────────────────────────────────────

LIVING_SOIL_ECOSYSTEM: dict = {
    "no_till_methodology": {
        "principle": "Never disturb the soil. Build once, improve forever. Each cycle adds to the ecosystem.",
        "cycle_workflow": [
            "1. Harvest: cut plant at soil surface, leave roots",
            "2. Top-dress: add fresh amendments (neem, kelp, crustacean, compost)",
            "3. Plant cover crop: scatter seed on surface, water in",
            "4. Rest: 2-4 weeks while amendments break down and cover crop grows",
            "5. Chop cover crop: cut at soil surface, leave as mulch",
            "6. Plant: transplant next cannabis seedling directly",
        ],
        "soil_improvement_over_time": {
            "cycle_1": "Good. Soil cooking period establishes baseline biology.",
            "cycle_2": "Better. Previous roots decomposed. Biology more diverse.",
            "cycle_3_plus": "Excellent. Self-sustaining ecosystem. Water-only with no issues.",
        },
        "minimum_pot_size_gal": 15,
        "ideal_pot_size_gal": {"indoor": 30, "outdoor": "raised bed (unlimited)"},
    },
    "soil_food_web": {
        "bacteria": {
            "role": "Decompose fresh organic matter. Mineralize nutrients. First responders.",
            "feed_with": "Compost, alfalfa meal, molasses (compost tea)",
        },
        "fungi": {
            "role": "Decompose woody/complex organics. Mycorrhizae extend root network. Move nutrients long distances.",
            "feed_with": "Woody mulch, humic acids, old growth forest duff",
        },
        "protozoa": {
            "role": "Eat bacteria, releasing plant-available nutrients (bacterial grazing cycle).",
            "feed_with": "They follow bacteria — feed bacteria and protozoa come.",
        },
        "nematodes": {
            "role": "Eat bacteria/fungi/other nematodes. Release nutrients. Beneficial species dominate healthy soil.",
            "feed_with": "Healthy biology attracts beneficial nematodes.",
        },
        "mycorrhizae": {
            "role": "Symbiotic root fungi. Trade phosphorus and water to plant in exchange for sugars. Extend root reach 100-1000x.",
            "feed_with": "Plant alive! They feed off root exudates. Don't use excessive P fertilizer (reduces colonization).",
        },
        "earthworms": {
            "role": "Aerate soil. Produce castings (perfect balanced fertilizer). Mix layers.",
            "feed_with": "Organic matter on surface. They self-regulate population.",
        },
    },
    "soil_recipe": {
        "base_mix": {
            "components": [
                {
                    "ingredient": "Sphagnum peat moss (or coco coir)",
                    "ratio_pct": 33,
                    "purpose": "Water retention, structure",
                },
                {"ingredient": "High-quality compost", "ratio_pct": 33, "purpose": "Biology, nutrition, buffering"},
                {
                    "ingredient": "Aeration (pumice, perlite, rice hulls)",
                    "ratio_pct": 33,
                    "purpose": "Oxygen to roots, drainage, prevents compaction",
                },
            ],
        },
        "amendments_per_cubic_foot": [
            {"ingredient": "Neem meal", "amount": "1/2 cup", "purpose": "Slow-release N, pest deterrent, biology food"},
            {"ingredient": "Kelp meal", "amount": "1/2 cup", "purpose": "Potassium, growth hormones, trace minerals"},
            {
                "ingredient": "Crustacean meal",
                "amount": "1/2 cup",
                "purpose": "Chitin (triggers plant immune response), slow-release N-P-Ca",
            },
            {"ingredient": "Gypsum", "amount": "1/2 cup", "purpose": "Calcium + sulfur without raising pH"},
            {"ingredient": "Glacial rock dust", "amount": "1 cup", "purpose": "Broad-spectrum trace minerals"},
            {
                "ingredient": "Worm castings",
                "amount": "1-2 cups",
                "purpose": "Microbial inoculant, balanced slow-release nutrition",
            },
        ],
        "cooking_instructions": {
            "method": "Mix all components. Moisten to 'wrung-out sponge' consistency. Cover loosely. Let sit 2-4 weeks.",
            "temperature": "Soil may heat to 100-130°F during cooking (composting action). Wait until it cools to < 80°F before planting.",
            "readiness_test": "Plant a lettuce seed. If it grows normally, soil is ready. If it burns/dies, wait longer.",
        },
    },
    "knf_inputs": {
        "FPJ": {
            "name": "Fermented Plant Juice",
            "ingredients": "Fresh plant growth tips + brown sugar",
            "use": "Foliar or soil drench. Growth stimulant.",
            "frequency": "Weekly in veg",
        },
        "FFJ": {
            "name": "Fermented Fruit Juice",
            "ingredients": "Ripe fruits + brown sugar",
            "use": "Soil drench in flower. P-K boost + beneficial microbes.",
            "frequency": "Weekly in flower",
        },
        "LAB": {
            "name": "Lactic Acid Bacteria",
            "ingredients": "Rice wash water → ferment → milk separation",
            "use": "Soil inoculant. Powerful decomposer. Suppresses pathogens.",
            "frequency": "Bi-weekly",
        },
        "OHN": {
            "name": "Oriental Herbal Nutrient",
            "ingredients": "Garlic, ginger, licorice, cinnamon, angelica in alcohol",
            "use": "Plant immune booster. Pest deterrent.",
            "frequency": "As needed for IPM",
        },
    },
    "cover_cropping": {
        "purpose": "Keeps soil alive between cycles. Fixes nitrogen. Prevents erosion. Feeds biology. Aerates with roots.",
        "recommended_blend": [
            "White clover (N-fixer)",
            "Crimson clover (N-fixer + biomass)",
            "Tillage radish (breaks compaction)",
            "Winter rye (massive root mass)",
        ],
        "management": "Let grow 2-4 weeks. Chop at soil surface before planting cannabis. Leave residue as mulch. Never pull roots.",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLED CONFIG EXPORT
# ─────────────────────────────────────────────────────────────────────────────

LIVING_SOIL_CONFIG: dict = {
    "grow_type_id": "living_soil",
    "version": "1.0.0",
    "stages": LIVING_SOIL_STAGES,
    "equipment": LIVING_SOIL_EQUIPMENT,
    "quick_reference": LIVING_SOIL_QUICK_REFERENCE,
    "troubleshooting": LIVING_SOIL_TROUBLESHOOTING,
    "living_soil_ecosystem": LIVING_SOIL_ECOSYSTEM,
    "total_grow_days": {"min": 105, "max": 182, "typical": 140},
}
