"""Nutrient knowledge base — DIY recipes, emergency substitutions, pH management, methodology guides."""

from __future__ import annotations

# ─── DIY / Homemade Nutrient Recipes ──────────────────────────────────────────

DIY_RECIPES: list[dict] = [
    {
        "id": "diy-masterblend-tomato",
        "name": "Masterblend Tomato 4-18-38 System",
        "category": "complete_base",
        "difficulty": "easy",
        "cost_rating": "very_low",
        "description": (
            "The most popular DIY hydro nutrient. Cheap, effective, and proven. Three dry salts mixedby weight."
        ),
        "medium": ["hydro", "coco", "kratky"],
        "ingredients": [
            {
                "name": "Masterblend 4-18-38 Tomato Formula",
                "amount": "2.4g",
                "per": "gallon",
                "source": "amazon/greenhouse_megastore",
            },
            {"name": "Calcium Nitrate (15.5-0-0)", "amount": "2.4g", "per": "gallon", "source": "amazon/hydro_store"},
            {"name": "Epsom Salt (Magnesium Sulfate)", "amount": "1.2g", "per": "gallon", "source": "grocery_store"},
        ],
        "mixing_instructions": [
            "1. Fill reservoir with water",
            "2. Dissolve Masterblend 4-18-38 first (mix well until clear)",
            "3. Dissolve Epsom salt next",
            "4. Dissolve Calcium Nitrate last (NEVER mix dry CalNit directly with Masterblend)",
            "5. Adjust pH to 5.8-6.2",
        ],
        "expected_ec": {"seedling": 0.8, "veg": 1.4, "flower": 1.8},
        "notes": "Adjust ratio for flower: some growers reduce to 2:1.2:2 ratio. Total cost ~$0.02/gallon.",
        "warnings": ["Never pre-mix calcium nitrate and masterblend dry — they react and lock out calcium."],
    },
    {
        "id": "diy-jacks-321",
        "name": "Jack's 3-2-1 Formula",
        "category": "complete_base",
        "difficulty": "easy",
        "cost_rating": "very_low",
        "description": (
            "Professional-grade dry nutrient system at DIY prices. Used by commercial operations. 3parts by weight."
        ),
        "medium": ["hydro", "coco", "rdwc", "dwc"],
        "ingredients": [
            {"name": "Jack's 5-12-26 Part A", "amount": "3.6g", "per": "gallon", "source": "jrpeters.com"},
            {"name": "Calcium Nitrate 15.5-0-0", "amount": "2.4g", "per": "gallon", "source": "jrpeters.com"},
            {"name": "Epsom Salt (MgSO4)", "amount": "1.2g", "per": "gallon", "source": "grocery_store"},
        ],
        "mixing_instructions": [
            "1. Fill reservoir with water",
            "2. Add Part A first, stir until dissolved",
            "3. Add Epsom salt, stir",
            "4. Add Calcium Nitrate last, stir thoroughly",
            "5. pH to 5.8-6.0 (usually lands close naturally)",
        ],
        "expected_ec": {"veg": 1.3, "flower": 1.6},
        "notes": "Named 3-2-1 for the gram ratio. Scale linearly. Some skip Epsom if water has Mg.",
        "warnings": ["Same as all calcium nitrate systems: never dry-mix CalNit with sulfate-containing fertilizers."],
    },
    {
        "id": "diy-compost-tea",
        "name": "Actively Aerated Compost Tea (AACT)",
        "category": "microbial_inoculant",
        "difficulty": "medium",
        "cost_rating": "low",
        "description": (
            "Living microbial tea brewed from compost. Introduces billions of beneficial organisms to"
            "root zone and foliage."
        ),
        "medium": ["soil", "coco", "living_soil"],
        "ingredients": [
            {
                "name": "Quality compost or worm castings",
                "amount": "1 cup",
                "per": "5_gallons",
                "source": "garden_store",
            },
            {
                "name": "Unsulphured blackstrap molasses",
                "amount": "1 tbsp",
                "per": "5_gallons",
                "source": "grocery_store",
            },
            {"name": "Kelp meal (optional)", "amount": "1 tsp", "per": "5_gallons", "source": "garden_store"},
            {"name": "Fish hydrolysate (optional)", "amount": "1 tsp", "per": "5_gallons", "source": "garden_store"},
        ],
        "mixing_instructions": [
            "1. Fill 5-gal bucket with dechlorinated water (let tap sit 24h or use RO)",
            "2. Place compost in mesh bag (paint strainer works great)",
            "3. Submerge bag, add molasses and amendments",
            "4. Run a strong air pump with air stone for 24-48 hours",
            "5. Use immediately within 4 hours of turning off the pump",
        ],
        "expected_ec": None,
        "notes": (
            "Brew at 65-80°F. Smells earthy when done. If it smells bad, toss it (anaerobic = harmful). Apply"
            "as soil drench or foliar spray."
        ),
        "warnings": [
            "Use within 4 hours — microbes die fast without oxygen.",
            "Do NOT use in sterile hydro systems.",
            "Never use treated/chlorinated water — it kills the microbes you're trying to grow.",
        ],
    },
    {
        "id": "diy-knf-fpj",
        "name": "Fermented Plant Juice (FPJ) — Korean Natural Farming",
        "category": "growth_stimulant",
        "difficulty": "medium",
        "cost_rating": "free",
        "description": (
            "Lacto-fermented plant extract rich in growth enzymes, hormones, and minerals. TraditionalKorean technique."
        ),
        "medium": ["soil", "coco", "living_soil"],
        "ingredients": [
            {
                "name": "Fast-growing plant tips (alfalfa, comfrey, or actively growing weeds)",
                "amount": "enough to fill jar",
                "per": "1_quart_jar",
                "source": "your_garden",
            },
            {
                "name": "Brown sugar (or jaggery)",
                "amount": "equal weight to plant material",
                "per": "1_quart_jar",
                "source": "grocery_store",
            },
        ],
        "mixing_instructions": [
            "1. Harvest plant tips at dawn (highest enzyme content)",
            "2. Weigh plant material, mix with equal weight brown sugar",
            "3. Pack into jar at 2/3 full, cover with breathable cloth",
            "4. Ferment 7-10 days in cool dark place",
            "5. Strain liquid. Stores 6+ months in cool dark place",
            "6. Dilute 1:1000 with water for application",
        ],
        "expected_ec": None,
        "notes": (
            "Use different plants for different effects: comfrey (K, P), nettle (N, Fe), horsetail (Si),"
            "banana stems (K)."
        ),
        "warnings": ["Not for sterile hydro. Smells like wine/vinegar when done. Discard if smells rotten."],
    },
    {
        "id": "diy-water-soluble-fertilizer",
        "name": "DIY Complete Water-Soluble Mix",
        "category": "complete_base",
        "difficulty": "advanced",
        "cost_rating": "very_low",
        "description": (
            "Custom-mixed from raw salts for ultimate control. Requires a scale and some chemistryknowledge."
        ),
        "medium": ["hydro", "coco", "rdwc"],
        "ingredients": [
            {"name": "Calcium Nitrate Ca(NO3)2", "amount": "varies", "per": "gallon", "source": "chemical_supplier"},
            {"name": "Potassium Nitrate KNO3", "amount": "varies", "per": "gallon", "source": "chemical_supplier"},
            {
                "name": "Monopotassium Phosphate (MKP) KH2PO4",
                "amount": "varies",
                "per": "gallon",
                "source": "chemical_supplier",
            },
            {
                "name": "Magnesium Sulfate MgSO4 (Epsom Salt)",
                "amount": "varies",
                "per": "gallon",
                "source": "grocery_store",
            },
            {
                "name": "Trace element mix (EDTA chelated)",
                "amount": "varies",
                "per": "gallon",
                "source": "chemical_supplier",
            },
        ],
        "mixing_instructions": [
            "1. Use a nutrient calculator (HydroBuddy is free and excellent)",
            "2. Input your target PPMs for each element by growth stage",
            "3. Input your water analysis (get it tested)",
            "4. Mix two stock solutions: A (calcium-containing) and B (sulfate/phosphate-containing)",
            "5. Never combine calcium and sulfate in concentrate — precipitates gypsum",
        ],
        "expected_ec": {"veg": 1.2, "flower": 1.6},
        "notes": (
            "This is how commercial greenhouses do it. Stock solutions last months. Total control over everyelement."
        ),
        "warnings": [
            "Requires water quality testing to be accurate.",
            "Separate A/B concentrate tanks mandatory.",
            "Some raw salts are hazardous — wear gloves/mask when handling.",
        ],
    },
    {
        "id": "diy-living-soil-recipe",
        "name": "Coots Living Soil Mix (Water-Only Super Soil)",
        "category": "soil_recipe",
        "difficulty": "medium",
        "cost_rating": "medium",
        "description": (
            "The gold standard living soil recipe. Once built, just add water — the soil biology feedsthe plants."
        ),
        "medium": ["living_soil"],
        "ingredients": [
            {"name": "Sphagnum peat moss", "amount": "1/3 by volume", "per": "total_mix", "source": "garden_store"},
            {
                "name": "Aeration (pumice or perlite)",
                "amount": "1/3 by volume",
                "per": "total_mix",
                "source": "garden_store",
            },
            {
                "name": "Quality compost/worm castings",
                "amount": "1/3 by volume",
                "per": "total_mix",
                "source": "garden_store",
            },
            {"name": "Neem meal", "amount": "0.5 cup", "per": "cubic_foot", "source": "garden_store"},
            {"name": "Kelp meal", "amount": "0.5 cup", "per": "cubic_foot", "source": "garden_store"},
            {
                "name": "Crustacean meal (crab/shrimp)",
                "amount": "0.5 cup",
                "per": "cubic_foot",
                "source": "garden_store",
            },
            {
                "name": "Rock dust (glacial or basalt)",
                "amount": "4 cups",
                "per": "cubic_foot",
                "source": "garden_store",
            },
            {"name": "Gypsum", "amount": "2 cups", "per": "cubic_foot", "source": "garden_store"},
            {"name": "Oyster shell flour", "amount": "1 cup", "per": "cubic_foot", "source": "garden_store"},
        ],
        "mixing_instructions": [
            "1. Combine base (1/3 peat, 1/3 pumice, 1/3 compost)",
            "2. Add all dry amendments and mix thoroughly",
            "3. Moisten to 'wrung-out sponge' consistency",
            "4. Let cook (compost) for 4-6 weeks minimum",
            "5. Keep moist and covered. Beneficial microbes will colonize",
            "6. After cooking, just plant and water — no bottle nutrients needed",
        ],
        "expected_ec": None,
        "notes": "Re-amend between cycles at 50% of original amendment rate. Top-dress with worm castings monthly.",
        "warnings": ["Must cook 4+ weeks before planting or it will burn plants.", "Not for hydro systems."],
    },
]

# ─── Emergency Substitutions ─────────────────────────────────────────────────

EMERGENCY_SUBSTITUTIONS: list[dict] = [
    {
        "id": "emergency-nitrogen",
        "problem": "Nitrogen deficiency — no nutrients available",
        "symptoms": "Lower leaves yellowing from bottom up, pale green overall, stunted growth",
        "emergency_solutions": [
            {
                "name": "Urine (diluted)",
                "ratio": "1:10 with water (1 part urine, 10 parts water)",
                "npk_approx": "11-1-2.5",
                "duration": "1-2 applications max",
                "notes": "Human urine is sterile and high in urea nitrogen. Must dilute. Only for soil/outdoor.",
                "suitable_for": ["soil", "outdoor"],
            },
            {
                "name": "Fish tank water",
                "ratio": "Use directly (undiluted)",
                "npk_approx": "trace amounts",
                "duration": "Ongoing if available",
                "notes": "Contains nitrogen, beneficial bacteria, and trace minerals. Essentially aquaponics.",
                "suitable_for": ["soil", "coco"],
            },
            {
                "name": "Grass clippings tea",
                "ratio": "Fill bucket 2/3 with clippings, cover with water, steep 3 days",
                "npk_approx": "2-0.5-2",
                "duration": "Use within 5 days",
                "notes": "Stinks but works. Strain well before use. Rich in nitrogen.",
                "suitable_for": ["soil", "outdoor"],
            },
            {
                "name": "Instant coffee (used grounds tea)",
                "ratio": "1 tbsp grounds per gallon, steeped 24h",
                "npk_approx": "2-0.3-0.5",
                "duration": "1-2 applications",
                "notes": "Mildly acidic. Contains nitrogen and trace minerals.",
                "suitable_for": ["soil"],
            },
        ],
    },
    {
        "id": "emergency-phosphorus",
        "problem": "Phosphorus deficiency — no P/K booster available",
        "symptoms": "Purple stems/petioles, dark leaves with purple tints, slow flowering, small buds",
        "emergency_solutions": [
            {
                "name": "Bone meal tea",
                "ratio": "1 tbsp bone meal per gallon, steep 24-48h",
                "npk_approx": "3-15-0",
                "duration": "Weekly application",
                "notes": "Slow-release even as a tea. Takes days to become available.",
                "suitable_for": ["soil", "coco"],
            },
            {
                "name": "Banana peel tea",
                "ratio": "3-4 peels per gallon, soak 48h or simmer 30min",
                "npk_approx": "0-3-11",
                "duration": "Weekly",
                "notes": "More potassium than phosphorus but helps in a pinch. Won't fully fix P deficiency alone.",
                "suitable_for": ["soil", "coco"],
            },
            {
                "name": "Match heads (unlit) dissolved",
                "ratio": "10-15 match heads soaked in 1 gallon water 24h",
                "npk_approx": "trace P",
                "duration": "Single emergency application",
                "notes": "Match heads contain potassium chlorate and phosphorus. Absolute last resort.",
                "suitable_for": ["soil"],
            },
        ],
    },
    {
        "id": "emergency-potassium",
        "problem": "Potassium deficiency — no K supplement available",
        "symptoms": "Brown/burnt leaf edges, leaf curling, weak stems, poor bud density",
        "emergency_solutions": [
            {
                "name": "Wood ash",
                "ratio": "1 tsp per gallon (use sparingly — very alkaline)",
                "npk_approx": "0-1-5",
                "duration": "Single application",
                "notes": "High in potassium carbonate. Raises pH significantly. Only for acidic soil.",
                "suitable_for": ["soil"],
            },
            {
                "name": "Banana peel tea",
                "ratio": "3-4 peels per gallon, steep 48h",
                "npk_approx": "0-3-11",
                "duration": "Weekly",
                "notes": "Best DIY potassium source. Can also dry and powder peels for top-dressing.",
                "suitable_for": ["soil", "coco"],
            },
            {
                "name": "Kelp extract / seaweed",
                "ratio": "Fresh seaweed rinse salt off, chop, soak in water 2 weeks",
                "npk_approx": "1-0.5-2.5",
                "duration": "Ongoing",
                "notes": "Rich in potassium, trace minerals, and growth hormones.",
                "suitable_for": ["soil", "coco", "living_soil"],
            },
        ],
    },
    {
        "id": "emergency-calcium",
        "problem": "Calcium deficiency — no cal-mag available",
        "symptoms": "Brown spots on new growth, distorted/curling new leaves, hollow stems",
        "emergency_solutions": [
            {
                "name": "Crushed eggshells (vinegar extraction)",
                "ratio": (
                    "Crush 6 eggshells, dissolve in 1 cup white vinegar until fizzing stops (~24h), dilute to1 gallon"
                ),
                "npk_approx": "pure calcium + trace",
                "duration": "Weekly",
                "notes": (
                    "Vinegar dissolves calcium carbonate into calcium acetate (water-soluble). Fastest DIYcalcium."
                ),
                "suitable_for": ["soil", "coco", "hydro_emergency"],
            },
            {
                "name": "Dolomite lime (pre-mixed in soil)",
                "ratio": "1 tbsp per gallon of soil",
                "npk_approx": "calcium + magnesium",
                "duration": "Lasts entire grow",
                "notes": "Best as preventative mixed into soil before planting. Slow-release calcium and magnesium.",
                "suitable_for": ["soil", "coco"],
            },
            {
                "name": "Tums/antacid tablets (calcium carbonate)",
                "ratio": "2 tablets crushed, dissolved in 1 gallon water + splash of vinegar to dissolve",
                "npk_approx": "calcium only",
                "duration": "Single emergency dose",
                "notes": "In a pinch, cheap calcium carbonate. Better than nothing.",
                "suitable_for": ["soil"],
            },
        ],
    },
    {
        "id": "emergency-magnesium",
        "problem": "Magnesium deficiency — no cal-mag or epsom salt",
        "symptoms": "Interveinal chlorosis on older/mid leaves (veins stay green, tissue yellows)",
        "emergency_solutions": [
            {
                "name": "Epsom salt (from any pharmacy/grocery)",
                "ratio": "1 tsp per gallon",
                "npk_approx": "0-0-0 (Mg 9.8%, S 13%)",
                "duration": "1-2 applications usually fixes it",
                "notes": (
                    "The go-to solution. Available at any grocery store for $3-5. Also great as foliar spray"
                    "at 1 tbsp/gallon."
                ),
                "suitable_for": ["all"],
            },
        ],
    },
    {
        "id": "emergency-iron",
        "problem": "Iron deficiency — no micro-nutrients available",
        "symptoms": "New growth emerges yellow/white with green veins (interveinal chlorosis on NEW leaves)",
        "emergency_solutions": [
            {
                "name": "Rusty nail water",
                "ratio": "Place several rusty nails in gallon of water + splash of vinegar, soak 3-7 days",
                "npk_approx": "iron only",
                "duration": "Ongoing slow release",
                "notes": "Old farmer's trick. Vinegar helps convert iron oxide to water-soluble form.",
                "suitable_for": ["soil", "coco"],
            },
            {
                "name": "Steel wool (fine) + vinegar",
                "ratio": "Dissolve fine steel wool in vinegar until brown, dilute 1 tsp solution per gallon",
                "npk_approx": "iron only",
                "duration": "1-2 applications",
                "notes": "Creates iron acetate — much more available than rust. Use sparingly.",
                "suitable_for": ["soil", "coco", "hydro_emergency"],
            },
        ],
    },
]

# ─── pH Management Without Commercial Products ───────────────────────────────

PH_ALTERNATIVES: list[dict] = [
    {
        "id": "ph-down-alternatives",
        "direction": "down",
        "problem": "pH too high (above 6.5 in hydro, above 7.0 in soil) and no pH Down available",
        "solutions": [
            {
                "name": "White vinegar (5% acetic acid)",
                "ratio": "1 ml per gallon (start low, measure)",
                "stability": "poor",
                "notes": (
                    "Cheap and available everywhere. pH drifts back up within 24-48h. Acceptable for soil,"
                    "not ideal for recirculating hydro."
                ),
                "suitable_for": ["soil", "coco", "drain_to_waste"],
                "not_recommended_for": ["dwc", "rdwc", "nft"],
            },
            {
                "name": "Citric acid powder",
                "ratio": "Pinch per gallon (1/8 tsp dissolves pH from 7 to ~6)",
                "stability": "moderate",
                "notes": (
                    "Organic acid. More stable than vinegar but still degrades. Grocery store baking aisle oramazon."
                ),
                "suitable_for": ["soil", "coco", "drain_to_waste"],
                "not_recommended_for": ["recirculating hydro"],
            },
            {
                "name": "Lemon juice",
                "ratio": "2-3 drops per gallon",
                "stability": "poor",
                "notes": (
                    "Contains citric acid. Same limitations as citric acid. Fresh lemon preferred over"
                    "bottled (preservatives)."
                ),
                "suitable_for": ["soil", "emergency_only"],
                "not_recommended_for": ["hydro"],
            },
            {
                "name": "Phosphoric acid (food grade)",
                "ratio": "1-2 drops per gallon of 10% solution",
                "stability": "excellent",
                "notes": (
                    "This IS what most 'pH Down' products are. Buy 85% food grade from chemical supply,"
                    "dilute to 10% for safe handling. Most stable option."
                ),
                "suitable_for": ["all"],
                "not_recommended_for": [],
            },
            {
                "name": "Sulfuric acid (battery acid)",
                "ratio": "Extremely small amounts — 1 drop per 5 gallons",
                "stability": "excellent",
                "notes": (
                    "Very dangerous to handle. Used commercially. Not recommended for home growers unless"
                    "experienced with acids."
                ),
                "suitable_for": ["commercial"],
                "not_recommended_for": ["home"],
            },
        ],
    },
    {
        "id": "ph-up-alternatives",
        "direction": "up",
        "problem": "pH too low (below 5.5 in hydro, below 6.0 in soil) and no pH Up available",
        "solutions": [
            {
                "name": "Baking soda (sodium bicarbonate)",
                "ratio": "1/4 tsp per gallon",
                "stability": "moderate",
                "notes": "Works quickly but adds sodium which can accumulate. OK for emergency use, not long-term.",
                "suitable_for": ["soil", "emergency_only"],
                "not_recommended_for": ["hydro_long_term"],
            },
            {
                "name": "Potassium bicarbonate (KHCO3)",
                "ratio": "1/4 tsp per gallon",
                "stability": "good",
                "notes": (
                    "Better than baking soda — adds potassium instead of sodium. Available as wine-making"
                    "supply or 'pH Up' alternative."
                ),
                "suitable_for": ["all"],
                "not_recommended_for": [],
            },
            {
                "name": "Potassium hydroxide (KOH) solution",
                "ratio": "1-2 drops of 10% solution per gallon",
                "stability": "excellent",
                "notes": (
                    "This IS what most 'pH Up' products are. Buy from chemical/soap-making supply. Caustic —"
                    "handle with care."
                ),
                "suitable_for": ["all"],
                "not_recommended_for": [],
            },
            {
                "name": "Calcium carbonate (garden lime / crushed coral)",
                "ratio": "1 tsp per gallon soil mix, or small mesh bag in reservoir",
                "stability": "slow/steady",
                "notes": (
                    "Very slow acting. Won't overshoot. Good for soil pre-amendment or aquarium-style passive"
                    "pH raise in DWC."
                ),
                "suitable_for": ["soil", "dwc_passive"],
                "not_recommended_for": [],
            },
            {
                "name": "Wood ash",
                "ratio": "1/2 tsp per gallon (dissolve and strain)",
                "stability": "moderate",
                "notes": "Contains potassium carbonate. Very alkaline. Also adds potassium and trace minerals.",
                "suitable_for": ["soil", "outdoor"],
                "not_recommended_for": ["hydro"],
            },
        ],
    },
]

# ─── Sterile vs Organic Methodology ──────────────────────────────────────────

METHODOLOGY_GUIDES: list[dict] = [
    {
        "id": "sterile-hydro",
        "title": "Sterile Hydroponic Method",
        "approach": "sterile",
        "summary": (
            "Keep the root zone pathogen-free through sterilization and preventive chemicals. No living"
            "organisms in the reservoir."
        ),
        "philosophy": (
            "Kill everything — good and bad. Rely on synthetic nutrients delivered directly to roots in"
            "sterile solution."
        ),
        "when_to_use": [
            "DWC/RDWC systems where water temps exceed 68°F",
            "When you've had recurring root rot / pythium",
            "Commercial operations requiring consistency",
            "Growers who want predictable, measurable results",
        ],
        "key_products": [
            {
                "name": "Hydrogen Peroxide (H2O2) 29%",
                "dose": "1 ml per gallon every 3 days",
                "role": "Oxidizes organic matter and pathogens. Breaks down to water and oxygen.",
            },
            {
                "name": "Hypochlorous Acid (HOCl)",
                "dose": "2 ppm free chlorine",
                "role": "Powerful oxidizer. More effective than H2O2. Generated from UC Roots or HOCl generators.",
            },
            {
                "name": "UC Roots / Pool Shock (calcium hypochlorite)",
                "dose": "Per label — very concentrated",
                "role": "Generates hypochlorous acid in water. Kills all organic life.",
            },
            {
                "name": "Physan 20",
                "dose": "1 tsp per 10 gallons",
                "role": "Quaternary ammonium disinfectant. Used between grows for system sterilization.",
            },
        ],
        "incompatible_with": [
            "Beneficial bacteria (Hydroguard, Tribus, Great White)",
            "Mycorrhizae",
            "Organic nutrients (they become food for pathogens without microbes to compete)",
            "Molasses / carbohydrate supplements",
            "Compost teas",
        ],
        "pros": [
            "Completely eliminates root rot risk",
            "Predictable nutrient uptake (no microbial interference)",
            "Clean reservoirs, no biofilm",
            "Easier to diagnose issues (fewer variables)",
        ],
        "cons": [
            "Must maintain sterility constantly — one lapse and problems explode",
            "No beneficial organisms to buffer mistakes",
            "Requires regular dosing schedule",
            "Some argue it reduces terpene complexity (debated)",
            "H2O2 breaks down silica supplements",
        ],
        "maintenance_schedule": {
            "daily": "Check ppm of oxidizer (test strips or ORP meter)",
            "every_3_days": "Re-dose H2O2 (it breaks down)",
            "weekly": "Full reservoir change",
            "between_grows": "Sterilize entire system with Physan 20 or bleach solution",
        },
    },
    {
        "id": "beneficial-organic",
        "title": "Beneficial/Organic Method",
        "approach": "organic",
        "summary": (
            "Establish a thriving microbiome in the root zone. Beneficial organisms outcompete pathogens"
            "and enhance nutrient availability."
        ),
        "philosophy": (
            "Mimic nature — build a living ecosystem around the roots. Beneficial bacteria/fungi protect"
            "plants and unlock nutrients."
        ),
        "when_to_use": [
            "Living soil / no-till grows",
            "Coco coir with organic nutrients",
            "DWC when water temps stay below 68°F",
            "Growers prioritizing flavor/terpene profiles",
            "When you want to reduce bottle dependency",
        ],
        "key_products": [
            {
                "name": "Hydroguard (Bacillus)",
                "dose": "2 ml/gal",
                "role": "Colonizes roots, outcompetes pythium. The #1 organic root rot preventive.",
            },
            {
                "name": "Great White Mycorrhizae",
                "dose": "1 tsp per transplant",
                "role": "Fungal network extends root reach 100-1000x. Apply directly to roots at transplant.",
            },
            {
                "name": "Mammoth P",
                "dose": "0.16 ml/gal",
                "role": "Bacteria that liberate phosphorus from organic matter. Increases P availability 16%.",
            },
            {
                "name": "Recharge",
                "dose": "0.5 tsp/gal weekly",
                "role": "Microbe blend with mycorrhizae, trichoderma, kelp, molasses. All-in-one inoculant.",
            },
            {
                "name": "Molasses",
                "dose": "1 tsp/gal",
                "role": "Food source for beneficial bacteria. Keeps populations high.",
            },
            {
                "name": "Compost tea (AACT)",
                "dose": "Drench or foliar",
                "role": "Introduces billions of diverse beneficial organisms from quality compost.",
            },
        ],
        "incompatible_with": [
            "Hydrogen peroxide (H2O2)",
            "Hypochlorous acid / chlorine",
            "Any sterilizing agent",
            "Synthetic fungicides",
            "UV sterilizers in res loop",
        ],
        "pros": [
            "Self-regulating ecosystem (buffers mistakes)",
            "Enhanced terpene and flavor profiles (many growers report)",
            "Reduced risk of salt lockout",
            "Beneficial fungi extend effective root zone",
            "More resilient to environmental stress",
            "Lower long-term cost (living soil re-amends)",
        ],
        "cons": [
            "Cannot let water temps exceed 68-70°F (pathogens outcompete beneficials)",
            "Harder to diagnose issues (more variables)",
            "Cloudy reservoirs (cosmetic but alarming to new growers)",
            "Initial inoculant cost",
            "Must maintain microbial populations (re-dose after res changes)",
        ],
        "maintenance_schedule": {
            "every_res_change": "Re-inoculate with Hydroguard/Tribus (dilution kills populations)",
            "weekly": "Molasses or carbohydrate feed for microbes",
            "monthly": "Compost tea drench (soil/coco)",
            "per_transplant": "Mycorrhizae directly on roots",
        },
    },
    {
        "id": "hybrid-approach",
        "title": "Hybrid / Best-of-Both Method",
        "approach": "hybrid",
        "summary": (
            "Use synthetic nutrients for precision but add specific beneficial microbes that tolerate mildoxidation."
        ),
        "philosophy": (
            "You don't have to choose exclusively. Some products like Tribus and Hydroguard survive"
            "low-level oxidation. Keep the res mostly clean but allow targeted beneficials."
        ),
        "when_to_use": [
            "DWC growers who want some microbial protection without full organic commitment",
            "Coco growers using synthetic nutrients but wanting root protection",
            "Anyone wanting insurance against root issues",
        ],
        "key_products": [
            {
                "name": "Tribus Original",
                "dose": "1 ml/gal at res change",
                "role": "Hardy Bacillus strains that tolerate mild oxidation. Add after H2O2 has dissipated (24h).",
            },
            {
                "name": "Hydroguard",
                "dose": "2 ml/gal",
                "role": "Single-species Bacillus. Add fresh at each res change.",
            },
            {
                "name": "Power Si (mono-silicic acid)",
                "dose": "0.5 ml/gal",
                "role": "Strengthens cell walls. Compatible with both approaches.",
            },
        ],
        "incompatible_with": [
            "Running H2O2 AND beneficials simultaneously (space them 24h apart)",
            "High-dose chlorine with any microbe product",
        ],
        "pros": [
            "Some microbial protection without full commitment",
            "Synthetic nutrient precision",
            "Reduced pathogen risk vs pure synthetic",
        ],
        "cons": [
            "More complex dosing schedule",
            "Must time oxidizer and microbe additions carefully",
            "Not as robust a microbiome as full organic approach",
        ],
        "maintenance_schedule": {
            "res_change_day": "Fresh nutrients + wait 24h",
            "day_after_res_change": "Add Hydroguard/Tribus (after any residual oxidizer breaks down)",
            "mid_week": "Low-dose H2O2 if needed (0.5 ml/gal) — will reduce but not eliminate microbes",
        },
    },
    {
        "id": "water-quality",
        "title": "Water Quality & Treatment Guide",
        "approach": "fundamental",
        "summary": (
            "Understanding your source water is the foundation of all nutrient management. Everything else"
            "builds on this."
        ),
        "sections": [
            {
                "title": "Water Sources Ranked",
                "content": [
                    {
                        "source": "RO (Reverse Osmosis)",
                        "ec": "0.0-0.05",
                        "pros": "Blank slate. Full control.",
                        "cons": "Need to add back Cal-Mag. Equipment cost.",
                        "recommendation": "Gold standard for hydro.",
                    },
                    {
                        "source": "Distilled",
                        "ec": "0.0",
                        "pros": "Pure. No variables.",
                        "cons": "Expensive at scale. Same as RO nutritionally.",
                        "recommendation": "Small grows or propagation.",
                    },
                    {
                        "source": "Tap (municipal)",
                        "ec": "0.2-0.6",
                        "pros": "Free. Often contains some Cal/Mg.",
                        "cons": "Chlorine/chloramine, variable mineral content, possible heavy metals.",
                        "recommendation": "Fine for soil. Let sit 24h to off-gas chlorine. Won't remove chloramine.",
                    },
                    {
                        "source": "Well water",
                        "ec": "0.2-1.0+",
                        "pros": "Free. No chlorine.",
                        "cons": "Highly variable. May have iron, sulfur, hardness, high pH.",
                        "recommendation": "Get tested. May need RO filter if high EC or heavy metals.",
                    },
                    {
                        "source": "Rain water",
                        "ec": "0.0-0.1",
                        "pros": "Free, soft, plants love it.",
                        "cons": "Collection infrastructure. May contain pollutants near highways/industry.",
                        "recommendation": "Excellent for organic grows. Filter debris.",
                    },
                ],
            },
            {
                "title": "Chlorine vs Chloramine",
                "content": {
                    "chlorine": {
                        "removal": (
                            "Let water sit uncovered 24h, or bubble with air stone 2-4h, or use Vitamin C"
                            "(ascorbic acid) 1 tiny pinch per gallon instant removal"
                        ),
                        "concern_level": "low-moderate (kills beneficials)",
                    },
                    "chloramine": {
                        "removal": (
                            "Will NOT off-gas with time. Must use: Campden tablets (sodium metabisulfite)"
                            "1/4 tablet per 20 gallons, or activated carbon filter, or RO"
                        ),
                        "concern_level": "moderate (more persistent, toxic to microbes)",
                    },
                    "how_to_tell": (
                        "Call your water utility or check their annual report. If water smells like"
                        "chlorine at the tap, likely chlorine. If no smell but report shows"
                        "disinfection, likely chloramine."
                    ),
                },
            },
        ],
    },
]


def get_diy_recipes() -> list[dict]:
    """Return all DIY nutrient recipes."""
    return DIY_RECIPES


def get_emergency_substitutions() -> list[dict]:
    """Return all emergency nutrient substitution guides."""
    return EMERGENCY_SUBSTITUTIONS


def get_ph_alternatives() -> list[dict]:
    """Return all pH management alternatives."""
    return PH_ALTERNATIVES


def get_methodology_guides() -> list[dict]:
    """Return all methodology guides (sterile vs organic etc.)."""
    return METHODOLOGY_GUIDES


def get_all_knowledge() -> dict:
    """Return the complete nutrient knowledge base."""
    return {
        "diy_recipes": DIY_RECIPES,
        "emergency_substitutions": EMERGENCY_SUBSTITUTIONS,
        "ph_alternatives": PH_ALTERNATIVES,
        "methodology_guides": METHODOLOGY_GUIDES,
    }
