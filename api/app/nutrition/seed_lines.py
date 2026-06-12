"""Nutrition seed data — coco coir and soil/organic nutrient lines.

Sources:
- CocoForCannabis.com (Dr. Coco) — Canna Coco research-based grow guides
- GrowWeedEasy.com — Fox Farm soil trio, documented grow journals
- BuildASoil YouTube/blog — living soil methodology
- Down to Earth product labels — OMRI-listed amendment analysis
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
# NUTRIENT LINES — COCO COIR SPECIFIC
# Compatible with: coco, drip (coco media)
# Note: Most hydro lines also work in coco — these are COCO-OPTIMIZED lines
# ═══════════════════════════════════════════════════════════════════════════════

COCO_GROW_TYPES = ["coco", "drip", "ebb_flow", "rockwool"]

COCO_LINES = [
    {
        "brand_slug": "canna",
        "slug": "canna-coco",
        "name": "Canna Coco A+B",
        "description": "The gold standard for coco coir. Developed and tested on cannabis for 30 years by Dutch researchers. 2-part system formulated specifically for coco's unique cation exchange properties. Crowd favorite among coco growers.",
        "line_type": "synthetic",
        "part_count": 2,
        "format": "liquid",
        "difficulty": "beginner",
        "ph_buffered": False,
        "grow_type_slugs": COCO_GROW_TYPES,
        "products": [
            {"slug": "coco-a", "name": "Canna Coco A", "product_type": "base", "npk": "5-0-3", "description": "Part A — calcium, nitrogen, iron. Specifically pH-balanced for coco coir's buffering. Always use equal parts A+B.", "is_required": True, "sort_order": 1},
            {"slug": "coco-b", "name": "Canna Coco B", "product_type": "base", "npk": "1-4-2", "description": "Part B — phosphorus, potassium, magnesium, sulfur, trace minerals. Same concentration throughout grow, just increase dose.", "is_required": True, "sort_order": 2},
            {"slug": "cannazym", "name": "Cannazym", "product_type": "supplement", "npk": "0-0-0", "description": "Enzyme solution that breaks down dead root material. Keeps coco clean, prevents pythium. 2.5ml/L throughout cycle.", "is_required": False, "sort_order": 3},
            {"slug": "pk-13-14", "name": "PK 13/14", "product_type": "booster", "npk": "0-13-14", "description": "Phosphorus/potassium booster for weeks 4-5 of flower only. One week on, then stop. Increases bud density.", "is_required": False, "sort_order": 4},
            {"slug": "boost", "name": "Canna Boost", "product_type": "booster", "npk": "0-0-0", "description": "Metabolism stimulator for weeks 3-7 of flower. Not a nutrient — enhances photosynthesis efficiency.", "is_required": False, "sort_order": 5},
        ],
    },
    {
        "brand_slug": "house-and-garden",
        "slug": "hg-coco",
        "name": "House & Garden Coco A+B",
        "description": "Premium Dutch coco nutrient. Founded by ex-Canna head researcher. Made in-house near Amsterdam. Tested on cannabis directly. Higher cost but consistent results.",
        "line_type": "synthetic",
        "part_count": 2,
        "format": "liquid",
        "difficulty": "intermediate",
        "ph_buffered": False,
        "grow_type_slugs": COCO_GROW_TYPES,
        "products": [
            {"slug": "coco-a", "name": "Cocos A", "product_type": "base", "npk": "5-0-2", "description": "Part A — nitrogen and calcium foundation formulated for coco coir's unique properties.", "is_required": True, "sort_order": 1},
            {"slug": "coco-b", "name": "Cocos B", "product_type": "base", "npk": "1-4-5", "description": "Part B — phosphorus, potassium, magnesium, and full trace element suite.", "is_required": True, "sort_order": 2},
            {"slug": "roots-excelurator", "name": "Roots Excelurator", "product_type": "supplement", "npk": "0-0-0", "description": "Premium root stimulator. Creates explosive root growth in first 3 weeks. One of the most effective root products available.", "is_required": False, "sort_order": 3},
            {"slug": "top-booster", "name": "Top Booster", "product_type": "booster", "npk": "0-13-14", "description": "PK booster for peak flower weeks. Similar to Canna PK 13/14 but slightly different mineral form.", "is_required": False, "sort_order": 4},
        ],
    },
    {
        "brand_slug": "advanced-nutrients",
        "slug": "ph-perfect-sensi-coco",
        "name": "pH Perfect Sensi Coco Grow/Bloom",
        "description": "Auto-pH system specifically formulated for coco coir. Extra calcium and magnesium built into the base — no separate CalMag needed. pH Perfect buffers automatically.",
        "line_type": "synthetic",
        "part_count": 2,
        "format": "liquid",
        "difficulty": "beginner",
        "ph_buffered": True,
        "grow_type_slugs": COCO_GROW_TYPES,
        "products": [
            {"slug": "sensi-coco-grow-a", "name": "Sensi Coco Grow A", "product_type": "base", "npk": "4-0-0", "description": "Coco-specific vegetative Part A with added calcium. pH Perfect auto-buffers to 5.6.", "is_required": True, "sort_order": 1},
            {"slug": "sensi-coco-grow-b", "name": "Sensi Coco Grow B", "product_type": "base", "npk": "1-2-7", "description": "Coco-specific vegetative Part B with added magnesium for coco's high cal/mag demand.", "is_required": True, "sort_order": 2},
            {"slug": "sensi-coco-bloom-a", "name": "Sensi Coco Bloom A", "product_type": "base", "npk": "4-0-0", "description": "Coco flowering Part A. Switch from Grow when flowers appear.", "is_required": True, "sort_order": 3},
            {"slug": "sensi-coco-bloom-b", "name": "Sensi Coco Bloom B", "product_type": "base", "npk": "1-3-6", "description": "Coco flowering Part B. Higher PK for bud development with coco-optimized calcium.", "is_required": True, "sort_order": 4},
        ],
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# NUTRIENT LINES — SOIL (Synthetic liquid for soil)
# Compatible with: soil, outdoor_soil, outdoor_container
# ═══════════════════════════════════════════════════════════════════════════════

SOIL_GROW_TYPES = ["soil", "outdoor_soil", "outdoor_container", "wicking_bed"]

SOIL_LINES = [
    {
        "brand_slug": "fox-farm",
        "slug": "fox-farm-trio-soil",
        "name": "Fox Farm Trio (Soil)",
        "description": "Most popular cannabis nutrient among home growers per GrowWeedEasy survey. Contains earthworm castings, bat guano, and kelp for enhanced terpene production. Use at half manufacturer strength.",
        "line_type": "hybrid",
        "part_count": 3,
        "format": "liquid",
        "difficulty": "beginner",
        "ph_buffered": False,
        "grow_type_slugs": SOIL_GROW_TYPES,
        "products": [
            {"slug": "grow-big-soil", "name": "Grow Big (Soil)", "product_type": "base", "npk": "6-4-4", "description": "Vegetative growth formula with earthworm castings and Norwegian kelp. Use from first true leaves through transition.", "is_required": True, "sort_order": 1},
            {"slug": "big-bloom", "name": "Big Bloom", "product_type": "base", "npk": "0.01-0.3-0.7", "description": "Organic micronutrient and beneficial compounds. Used throughout entire grow cycle. Contains bat guano, earthworm castings, and rock phosphate.", "is_required": True, "sort_order": 2},
            {"slug": "tiger-bloom", "name": "Tiger Bloom", "product_type": "base", "npk": "2-8-4", "description": "Flowering formula with high phosphorus. Replace Grow Big with Tiger Bloom when buds form. Very concentrated.", "is_required": True, "sort_order": 3},
            {"slug": "sledgehammer", "name": "Sledgehammer", "product_type": "flush", "npk": "0-0-0", "description": "Salt-clearing flush. Use every 2-3 weeks to prevent salt buildup in soil, and for final flush.", "is_required": False, "sort_order": 4},
            {"slug": "open-sesame", "name": "Open Sesame", "product_type": "booster", "npk": "5-45-19", "description": "Early flower booster. High phosphorus triggers bloom. Use weeks 1-2 of flower only.", "is_required": False, "sort_order": 5},
            {"slug": "beastie-bloomz", "name": "Beastie Bloomz", "product_type": "booster", "npk": "0-50-30", "description": "Peak flower booster for maximum bud weight. Weeks 4-6 of flower.", "is_required": False, "sort_order": 6},
        ],
    },
    {
        "brand_slug": "fox-farm",
        "slug": "fox-farm-trio-hydro",
        "name": "Fox Farm Trio (Hydro/Coco)",
        "description": "Hydroponic version of the Fox Farm trio. Same Big Bloom and Tiger Bloom, but Grow Big is reformulated with additional micronutrients that soil normally provides. For coco and soilless.",
        "line_type": "hybrid",
        "part_count": 3,
        "format": "liquid",
        "difficulty": "beginner",
        "ph_buffered": False,
        "grow_type_slugs": ["coco", "drip", "ebb_flow", "rockwool"],
        "products": [
            {"slug": "grow-big-hydro", "name": "Grow Big Hydro", "product_type": "base", "npk": "3-2-6", "description": "Hydroponic vegetative formula with extra micronutrients (copper, manganese, zinc) not found in soilless media.", "is_required": True, "sort_order": 1},
            {"slug": "big-bloom", "name": "Big Bloom", "product_type": "base", "npk": "0.01-0.3-0.7", "description": "Same organic micronutrient formula as soil version. Used throughout entire cycle.", "is_required": True, "sort_order": 2},
            {"slug": "tiger-bloom", "name": "Tiger Bloom", "product_type": "base", "npk": "2-8-4", "description": "Same flowering formula for all versions. High P for bud development.", "is_required": True, "sort_order": 3},
        ],
    },
    {
        "brand_slug": "dyna-gro",
        "slug": "dyna-gro-soil",
        "name": "Dyna-Gro Foliage Pro + Bloom (Soil)",
        "description": "Simplest nutrient system period. 2 bottles, complete nutrition, any medium. GrowWeedEasy recommends as #1 for new growers. Originally for orchids but proven excellent for cannabis.",
        "line_type": "synthetic",
        "part_count": 2,
        "format": "liquid",
        "difficulty": "beginner",
        "ph_buffered": False,
        "grow_type_slugs": SOIL_GROW_TYPES + ["coco"],
        "products": [
            {"slug": "foliage-pro", "name": "Foliage Pro 9-3-6", "product_type": "base", "npk": "9-3-6", "description": "Complete vegetative formula. All 16 essential nutrients in one bottle. Use 1/4 to 1 tsp per gallon.", "is_required": True, "sort_order": 1},
            {"slug": "bloom", "name": "Bloom 3-12-6", "product_type": "base", "npk": "3-12-6", "description": "Complete flowering formula. Low nitrogen, high phosphorus. Switch when buds begin forming.", "is_required": True, "sort_order": 2},
        ],
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# NUTRIENT LINES — ORGANIC / LIVING SOIL
# For: soil, outdoor_soil, living_soil, outdoor_container
# ═══════════════════════════════════════════════════════════════════════════════

ORGANIC_GROW_TYPES = ["soil", "outdoor_soil", "outdoor_container", "living_soil", "wicking_bed"]

ORGANIC_LINES = [
    {
        "brand_slug": "natures-living-soil",
        "slug": "natures-living-soil-concentrate",
        "name": "Nature's Living Soil Concentrate",
        "description": "Just-add-water super soil. Mix concentrate into bottom 1/3 of container, fill rest with quality base soil, plant, and only give plain water. Nutrients release on demand via soil biology. Simplest organic method possible.",
        "line_type": "organic",
        "part_count": 1,
        "format": "dry_amendment",
        "difficulty": "beginner",
        "ph_buffered": True,
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "products": [
            {"slug": "super-soil-concentrate", "name": "Super Soil Concentrate", "product_type": "base", "npk": "varies", "description": "Living soil concentrate with worm castings, bat guano, blood meal, bone meal, kelp, mycorrhizae, and beneficial bacteria. 3lbs per 5-gallon pot.", "is_required": True, "sort_order": 1},
            {"slug": "flower-amendment", "name": "Flower Top Dress", "product_type": "booster", "npk": "varies", "description": "Optional top dress for heavy-feeding strains in flower. Sprinkle on soil surface and water in at week 4-5 of flower.", "is_required": False, "sort_order": 2},
        ],
    },
    {
        "brand_slug": "down-to-earth",
        "slug": "dte-dry-amendments",
        "name": "Down to Earth Dry Amendments",
        "description": "OMRI-listed organic dry amendments. Industry standard for cannabis living soil. Top-dress every 3-4 weeks for slow-release organic nutrition. Mix Bio-Live into soil at potting, top-dress with specific amendments per stage.",
        "line_type": "organic",
        "part_count": 4,
        "format": "dry_amendment",
        "difficulty": "intermediate",
        "ph_buffered": False,
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "products": [
            {"slug": "bio-live", "name": "Bio-Live 5-4-2", "product_type": "base", "npk": "5-4-2", "description": "All-purpose organic fertilizer for soil building. Mix 1/2 cup per cubic foot into base soil at potting. Contains fish bone meal, alfalfa, kelp, and beneficial microbes.", "is_required": True, "sort_order": 1},
            {"slug": "veg-mix", "name": "All Purpose Mix 4-4-4", "product_type": "base", "npk": "4-4-4", "description": "Balanced vegetative top dress. 2-3 tablespoons per gallon of soil every 3-4 weeks during veg. Fish meal, alfalfa meal, bone meal base.", "is_required": True, "sort_order": 2},
            {"slug": "bloom-mix", "name": "Rose & Flower Mix 4-8-4", "product_type": "base", "npk": "4-8-4", "description": "High-phosphorus flowering top dress. 2-3 tablespoons per gallon every 3-4 weeks in flower. Bone meal, langbeinite, kelp.", "is_required": True, "sort_order": 3},
            {"slug": "neem-meal", "name": "Neem Seed Meal 6-1-2", "product_type": "supplement", "npk": "6-1-2", "description": "Slow-release nitrogen + natural pest deterrent (fungus gnats, root aphids). 1 tablespoon per gallon at each top dress.", "is_required": False, "sort_order": 4},
            {"slug": "kelp-meal", "name": "Kelp Meal 1-0.1-2", "product_type": "supplement", "npk": "1-0.1-2", "description": "Growth hormones (cytokinins), potassium, and 60+ trace minerals. 1 tablespoon per gallon at each top dress. Enhances stress resistance.", "is_required": False, "sort_order": 5},
        ],
    },
    {
        "brand_slug": "gaia-green",
        "slug": "gaia-green-organic",
        "name": "Gaia Green All Purpose + Power Bloom",
        "description": "Canadian organic dry amendments. Simple 2-product system: All Purpose in veg, Power Bloom in flower. Top-dress every 3-4 weeks. Extremely popular in Canadian cannabis cultivation.",
        "line_type": "organic",
        "part_count": 2,
        "format": "dry_amendment",
        "difficulty": "beginner",
        "ph_buffered": False,
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "products": [
            {"slug": "all-purpose", "name": "All Purpose 4-4-4", "product_type": "base", "npk": "4-4-4", "description": "Balanced organic fertilizer for vegetative growth. Top-dress 2-4 tablespoons per gallon of soil every 3-4 weeks. Alfalfa, bone meal, kelp, glacial rock dust.", "is_required": True, "sort_order": 1},
            {"slug": "power-bloom", "name": "Power Bloom 2-8-4", "product_type": "base", "npk": "2-8-4", "description": "High-phosphorus flowering fertilizer. Same application rate as All Purpose. Switch 1-2 weeks before flip, or blend 50/50 during transition.", "is_required": True, "sort_order": 2},
            {"slug": "worm-castings", "name": "Worm Castings 2-0-0", "product_type": "supplement", "npk": "2-0-0", "description": "Earthworm castings add beneficial biology, humic acid, and gentle nitrogen. Top-dress 1/4 inch layer at each amendment application.", "is_required": False, "sort_order": 3},
        ],
    },
    {
        "brand_slug": "buildasoil",
        "slug": "buildasoil-system",
        "name": "BuildASoil Living Soil System",
        "description": "Complete craft living soil system. Build once, re-use forever (no-till). Premium inputs, cover crops, and biology. The gold standard for quality-focused organic cannabis cultivation.",
        "line_type": "organic",
        "part_count": 3,
        "format": "dry_amendment",
        "difficulty": "advanced",
        "ph_buffered": True,
        "grow_type_slugs": ["soil", "living_soil", "outdoor_soil"],
        "products": [
            {"slug": "craft-blend", "name": "Craft Blend 3-3-3", "product_type": "base", "npk": "3-3-3", "description": "All-in-one soil amendment with neem, karanja, kelp, crustacean meal, fish bone meal, and malted barley. Mix into soil at build or top-dress.", "is_required": True, "sort_order": 1},
            {"slug": "buildaflower", "name": "BuildAFlower Top Dress", "product_type": "base", "npk": "2-8-4", "description": "Flowering top dress with bat guano, bone meal, langbeinite, and kelp. Apply 2 weeks before and 2 weeks after flip.", "is_required": True, "sort_order": 2},
            {"slug": "rootwise-mycrobe", "name": "Rootwise Mycrobe Complete", "product_type": "supplement", "npk": "0-0-0", "description": "Concentrated biology inoculant — mycorrhizae, trichoderma, and bacterial species. Apply at transplant and monthly to maintain soil food web.", "is_required": True, "sort_order": 3},
            {"slug": "build-a-bloom", "name": "Build-A-Bloom 0-2-1", "product_type": "booster", "npk": "0-2-1", "description": "Soluble flower enhancer for compost tea or top dress. Fish bone meal, langbeinite, and soft rock phosphate.", "is_required": False, "sort_order": 4},
            {"slug": "cover-crop", "name": "Cover Crop Blend", "product_type": "supplement", "npk": "varies", "description": "Living mulch: clover, fenugreek, and grass. Fixes nitrogen, prevents evaporation, feeds soil biology. Sow on soil surface.", "is_required": False, "sort_order": 5},
        ],
    },
    {
        "brand_slug": "roots-organics",
        "slug": "terp-tea",
        "name": "Roots Organics Terp Tea",
        "description": "Organic dry powder brewed into aerated teas. Known for terpene-enhancing formulations. Brew with air pump for 24h then apply. Can also be top-dressed dry.",
        "line_type": "organic",
        "part_count": 2,
        "format": "dry_amendment",
        "difficulty": "intermediate",
        "ph_buffered": False,
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "products": [
            {"slug": "terp-tea-grow", "name": "Terp Tea Grow", "product_type": "base", "npk": "7-3-1", "description": "Vegetative formula. Brew 2 tablespoons per gallon with air pump for 24 hours, or top-dress dry. Contains kelp, fish bone meal, soybean meal.", "is_required": True, "sort_order": 1},
            {"slug": "terp-tea-bloom", "name": "Terp Tea Bloom", "product_type": "base", "npk": "3-7-4", "description": "Flowering formula. Same brew method. High phosphorus from bat guano and bone meal. Langbeinite for potassium and sulfur.", "is_required": True, "sort_order": 2},
            {"slug": "terp-tea-microbe-charge", "name": "Terp Tea Microbe Charge", "product_type": "supplement", "npk": "0-0-0", "description": "Beneficial microbe inoculant to add to brews. Mycorrhizae, trichoderma, and bacillus strains.", "is_required": False, "sort_order": 3},
        ],
    },
]
