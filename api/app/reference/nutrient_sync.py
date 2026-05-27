"""Nutrient product database sync — imports seed data for common nutrient products."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import NutrientProduct

logger = logging.getLogger("tendril.reference.nutrients")

# Curated seed data for popular nutrient products
SEED_NUTRIENTS: list[dict] = [
    {
        "barcode": "0849953000018",
        "name": "Micro",
        "brand": "General Hydroponics Flora",
        "npk": "5-0-1",
        "nutrients": {
            "description": (
                "Base nutrient providing nitrogen, calcium, and essential micro-nutrients. Part of the"
                "Flora 3-part system."
            ),
            "type": "base",
            "calcium_pct": 5.0,
            "magnesium_pct": 1.5,
            "iron_ppm": 1000,
            "manganese_ppm": 500,
            "zinc_ppm": 150,
            "boron_ppm": 50,
            "copper_ppm": 10,
            "molybdenum_ppm": 8,
            "dosage_ml_per_gal": {"seedling": 1.25, "veg": 5.0, "flower": 5.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0849953000025",
        "name": "Gro",
        "brand": "General Hydroponics Flora",
        "npk": "2-1-6",
        "nutrients": {
            "description": "Promotes vigorous vegetative growth with higher nitrogen. Reduce during flowering.",
            "type": "base",
            "nitrogen_ammoniacal_pct": 1.0,
            "nitrogen_nitrate_pct": 1.0,
            "potassium_pct": 6.0,
            "magnesium_pct": 0.5,
            "dosage_ml_per_gal": {"seedling": 1.25, "veg": 5.0, "flower": 1.25},
        },
        "source": "seed",
    },
    {
        "barcode": "0849953000032",
        "name": "Bloom",
        "brand": "General Hydroponics Flora",
        "npk": "0-5-4",
        "nutrients": {
            "description": "Supplies phosphorus and potassium for flowering and fruiting. Increase during bloom phase.",
            "type": "base",
            "phosphorus_pct": 5.0,
            "potassium_pct": 4.0,
            "sulfur_pct": 1.0,
            "dosage_ml_per_gal": {"seedling": 1.25, "veg": 1.25, "flower": 5.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0849953000100",
        "name": "CALiMAGic",
        "brand": "General Hydroponics",
        "npk": "1-0-0",
        "nutrients": {
            "description": (
                "Calcium, magnesium, and iron supplement. Prevents deficiencies in RO water, coco, andLED grows."
            ),
            "type": "supplement",
            "calcium_pct": 5.0,
            "magnesium_pct": 1.5,
            "iron_ppm": 1000,
            "dosage_ml_per_gal": {"seedling": 2.5, "veg": 5.0, "flower": 5.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0793094014809",
        "name": "Big Bloom",
        "brand": "Fox Farm",
        "npk": "0.01-0.3-0.7",
        "nutrients": {
            "description": (
                "Organic bloom booster with earthworm castings, bat guano, and kelp. Gentle enough forseedlings."
            ),
            "type": "base",
            "organic": True,
            "ingredients": ["earthworm castings", "bat guano", "Norwegian kelp", "rock phosphate"],
            "dosage_ml_per_gal": {"seedling": 15.0, "veg": 15.0, "flower": 15.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0793094014816",
        "name": "Grow Big",
        "brand": "Fox Farm",
        "npk": "6-4-4",
        "nutrients": {
            "description": (
                "Liquid concentrate for vigorous vegetative growth. Contains earthworm castings andNorwegian kelp."
            ),
            "type": "base",
            "nitrogen_ammoniacal_pct": 1.0,
            "nitrogen_nitrate_pct": 5.0,
            "dosage_ml_per_gal": {"seedling": 5.0, "veg": 15.0, "flower": 0},
        },
        "source": "seed",
    },
    {
        "barcode": "0793094014823",
        "name": "Tiger Bloom",
        "brand": "Fox Farm",
        "npk": "2-8-4",
        "nutrients": {
            "description": (
                "High-phosphorus fertilizer for abundant fruit and flower production. Use from firstsigns of flowering."
            ),
            "type": "base",
            "phosphorus_pct": 8.0,
            "potassium_pct": 4.0,
            "dosage_ml_per_gal": {"seedling": 0, "veg": 0, "flower": 10.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0AN100001001",
        "name": "pH Perfect Micro",
        "brand": "Advanced Nutrients",
        "npk": "5-0-1",
        "nutrients": {
            "description": (
                "Auto-pH balancing micro nutrient base. Provides calcium, iron, and trace elements with"
                "pH Perfect technology."
            ),
            "type": "base",
            "calcium_pct": 4.0,
            "iron_ppm": 800,
            "ph_buffered": True,
            "dosage_ml_per_gal": {"seedling": 1.0, "veg": 4.0, "flower": 4.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0AN100001002",
        "name": "pH Perfect Grow",
        "brand": "Advanced Nutrients",
        "npk": "1-3-6",
        "nutrients": {
            "description": "Auto-pH balancing grow formula with higher potassium for structural development.",
            "type": "base",
            "ph_buffered": True,
            "potassium_pct": 6.0,
            "dosage_ml_per_gal": {"seedling": 1.0, "veg": 4.0, "flower": 1.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0AN100001003",
        "name": "pH Perfect Bloom",
        "brand": "Advanced Nutrients",
        "npk": "0-5-4",
        "nutrients": {
            "description": "Auto-pH balancing bloom formula delivering phosphorus and potassium for flower production.",
            "type": "base",
            "ph_buffered": True,
            "phosphorus_pct": 5.0,
            "potassium_pct": 4.0,
            "dosage_ml_per_gal": {"seedling": 1.0, "veg": 1.0, "flower": 4.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0AN100001010",
        "name": "Big Bud",
        "brand": "Advanced Nutrients",
        "npk": "0-1-3",
        "nutrients": {
            "description": (
                "Bloom booster with amino acids, phosphorus, potassium, and magnesium for larger,denser flowers."
            ),
            "type": "supplement",
            "phosphorus_pct": 1.0,
            "potassium_pct": 3.0,
            "magnesium_pct": 0.5,
            "amino_acids": True,
            "dosage_ml_per_gal": {"flower_wk3_6": 2.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0AN100001020",
        "name": "Overdrive",
        "brand": "Advanced Nutrients",
        "npk": "1-5-4",
        "nutrients": {
            "description": (
                "Late-flower finisher that pushes plants to pack on weight in the final weeks beforeharvest."
            ),
            "type": "supplement",
            "phosphorus_pct": 5.0,
            "potassium_pct": 4.0,
            "dosage_ml_per_gal": {"flower_final_weeks": 2.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0JN321010001",
        "name": "Jack's 3-2-1 Part A",
        "brand": "Jack's Nutrients",
        "npk": "5-12-26",
        "nutrients": {
            "description": (
                "Highly concentrated dry fertilizer base. Mix with Calcium Nitrate and Epsom Salt"
                "(3-2-1 ratio by weight)."
            ),
            "type": "base",
            "form": "dry",
            "phosphorus_pct": 12.0,
            "potassium_pct": 26.0,
            "sulfur_pct": 9.7,
            "magnesium_pct": 2.3,
            "dosage_g_per_gal": {"veg": 3.6, "flower": 3.6},
        },
        "source": "seed",
    },
    {
        "barcode": "0JN321010002",
        "name": "Calcium Nitrate",
        "brand": "Jack's Nutrients",
        "npk": "15.5-0-0",
        "nutrients": {
            "description": "Provides calcium and nitrogen. Part B of the Jack's 3-2-1 system.",
            "type": "base",
            "form": "dry",
            "calcium_pct": 19.0,
            "nitrogen_nitrate_pct": 14.4,
            "nitrogen_ammoniacal_pct": 1.1,
            "dosage_g_per_gal": {"veg": 2.4, "flower": 2.4},
        },
        "source": "seed",
    },
    {
        "barcode": "0JN321010003",
        "name": "Epsom Salt (Magnesium Sulfate)",
        "brand": "Jack's Nutrients",
        "npk": "0-0-0",
        "nutrients": {
            "description": "Magnesium and sulfur supplement. Part C of the 3-2-1 system at low dose.",
            "type": "supplement",
            "form": "dry",
            "magnesium_pct": 9.8,
            "sulfur_pct": 13.0,
            "dosage_g_per_gal": {"veg": 1.2, "flower": 1.2},
        },
        "source": "seed",
    },
    {
        "barcode": "0CR100001001",
        "name": "Canna A",
        "brand": "Canna Coco",
        "npk": "5-0-3",
        "nutrients": {
            "description": (
                "Two-part base nutrient (A) optimized for coco coir. Provides nitrogen, calcium, andtrace elements."
            ),
            "type": "base",
            "medium": "coco",
            "calcium_pct": 4.2,
            "iron_ppm": 700,
            "dosage_ml_per_gal": {"veg": 15.0, "flower": 15.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0CR100001002",
        "name": "Canna B",
        "brand": "Canna Coco",
        "npk": "1-4-2",
        "nutrients": {
            "description": "Two-part base nutrient (B) for coco coir. Supplies phosphorus, potassium, and sulfur.",
            "type": "base",
            "medium": "coco",
            "phosphorus_pct": 4.0,
            "potassium_pct": 2.0,
            "sulfur_pct": 1.5,
            "dosage_ml_per_gal": {"veg": 15.0, "flower": 15.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0CR100001010",
        "name": "PK 13/14",
        "brand": "Canna",
        "npk": "0-13-14",
        "nutrients": {
            "description": (
                "Concentrated phosphorus/potassium bloom booster for peak flowering. Use for 1 week"
                "only during mid-flower."
            ),
            "type": "supplement",
            "phosphorus_pct": 13.0,
            "potassium_pct": 14.0,
            "dosage_ml_per_gal": {"flower_peak_week": 1.5},
        },
        "source": "seed",
    },
    {
        "barcode": "0CR100001020",
        "name": "Cannazym",
        "brand": "Canna",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Enzyme formula that breaks down dead root material into usable sugars. Improves"
                "nutrient uptake and root zone health."
            ),
            "type": "supplement",
            "enzymes": True,
            "dosage_ml_per_gal": {"all_stages": 10.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0AM100001001",
        "name": "Sensi Grow A",
        "brand": "Advanced Nutrients Sensi",
        "npk": "5-0-1",
        "nutrients": {
            "description": (
                "pH Perfect 2-part grow base (A). Provides nitrogen, calcium, and iron with auto-pHbuffering."
            ),
            "type": "base",
            "ph_buffered": True,
            "calcium_pct": 3.8,
            "iron_ppm": 600,
            "dosage_ml_per_gal": {"veg": 4.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0AM100001002",
        "name": "Sensi Grow B",
        "brand": "Advanced Nutrients Sensi",
        "npk": "1-2-6",
        "nutrients": {
            "description": (
                "pH Perfect 2-part grow base (B). Delivers phosphorus, potassium, and magnesium withauto-pH buffering."
            ),
            "type": "base",
            "ph_buffered": True,
            "potassium_pct": 6.0,
            "magnesium_pct": 1.3,
            "dosage_ml_per_gal": {"veg": 4.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0AM100001003",
        "name": "Sensi Bloom A",
        "brand": "Advanced Nutrients Sensi",
        "npk": "4-0-3",
        "nutrients": {
            "description": (
                "pH Perfect 2-part bloom base (A). Tailored nutrient ratios for flowering with auto-pHtechnology."
            ),
            "type": "base",
            "ph_buffered": True,
            "calcium_pct": 3.2,
            "dosage_ml_per_gal": {"flower": 4.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0AM100001004",
        "name": "Sensi Bloom B",
        "brand": "Advanced Nutrients Sensi",
        "npk": "0-4-3",
        "nutrients": {
            "description": "pH Perfect 2-part bloom base (B). High phosphorus and potassium for flower development.",
            "type": "base",
            "ph_buffered": True,
            "phosphorus_pct": 4.0,
            "potassium_pct": 3.0,
            "dosage_ml_per_gal": {"flower": 4.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0BN100001001",
        "name": "Veg+Bloom Dirty",
        "brand": "Veg+Bloom",
        "npk": "9-13-27",
        "nutrients": {
            "description": (
                "One-part dry nutrient for hard/tap water. Contains fulvic acid and silica. 'Dirty'"
                "formulation for unfiltered water."
            ),
            "type": "base",
            "form": "dry",
            "water_type": "hard/tap",
            "silica": True,
            "fulvic_acid": True,
            "dosage_g_per_gal": {"all_stages": 6.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0BN100001002",
        "name": "Veg+Bloom RO/Soft",
        "brand": "Veg+Bloom",
        "npk": "11-14-27",
        "nutrients": {
            "description": (
                "One-part dry nutrient for RO or soft water. Added calcium and magnesium for"
                "demineralized water sources."
            ),
            "type": "base",
            "form": "dry",
            "water_type": "RO/soft",
            "calcium_pct": 5.0,
            "magnesium_pct": 2.0,
            "dosage_g_per_gal": {"all_stages": 6.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0MG100001001",
        "name": "Armor Si",
        "brand": "General Hydroponics",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Potassium silicate strengthens cell walls, improves heat/drought tolerance, and"
                "increases pest resistance."
            ),
            "type": "supplement",
            "silica_pct": 0.5,
            "potassium_pct": 3.7,
            "dosage_ml_per_gal": {"all_stages": 1.5},
            "notes": "Add first to fresh water before other nutrients. Stop 2 weeks before harvest.",
        },
        "source": "seed",
    },
    {
        "barcode": "0MG100001002",
        "name": "Hydroguard",
        "brand": "Botanicare",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Beneficial bacteria (Bacillus amyloliquefaciens) that colonizes roots and outcompetes"
                "pathogens like pythium. Essential for DWC."
            ),
            "type": "supplement",
            "beneficial_microbes": True,
            "organism": "Bacillus amyloliquefaciens",
            "dosage_ml_per_gal": {"all_stages": 2.0},
            "notes": "Safe from seedling through harvest. Not a nutrient — does not need to be flushed.",
        },
        "source": "seed",
    },
    {
        "barcode": "0MG100001003",
        "name": "Recharge",
        "brand": "Real Growers",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Beneficial microbe blend with mycorrhizae, trichoderma, and kelp for improved nutrientuptake."
            ),
            "type": "supplement",
            "beneficial_microbes": True,
            "organisms": ["mycorrhizae", "trichoderma", "bacillus"],
            "ingredients": ["kelp extract", "humic acid", "fulvic acid", "molasses"],
            "dosage_tsp_per_gal": {"weekly": 0.5},
            "notes": "Once per week as a drench. Best for soil and coco — can cloud DWC reservoirs.",
        },
        "source": "seed",
    },
    {
        "barcode": "0MG100001004",
        "name": "Mammoth P",
        "brand": "Mammoth Microbes",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Phosphorus-liberating microbial inoculant that increases available phosphorus by up to16%."
            ),
            "type": "supplement",
            "beneficial_microbes": True,
            "mechanism": "phosphorus liberation",
            "dosage_ml_per_gal": {"all_stages": 0.16},
            "notes": "From mid-veg through end of flower. Add at every reservoir change.",
        },
        "source": "seed",
    },
    {
        "barcode": "0ATHENA0001",
        "name": "Core",
        "brand": "Athena",
        "npk": "5-0-0",
        "nutrients": {
            "description": (
                "Nitrogen and calcium base applied throughout all growth phases. Foundation of theAthena Pro line."
            ),
            "type": "base",
            "calcium_pct": 6.0,
            "nitrogen_nitrate_pct": 5.0,
            "dosage_ml_per_gal": {"veg": 3.0, "flower": 2.5},
        },
        "source": "seed",
    },
    {
        "barcode": "0ATHENA0002",
        "name": "Grow A",
        "brand": "Athena",
        "npk": "4-0-1",
        "nutrients": {
            "description": (
                "Two-part vegetative formula (A). Provides nitrogen, calcium, and micro-nutrients for"
                "structural development."
            ),
            "type": "base",
            "calcium_pct": 4.5,
            "iron_ppm": 500,
            "dosage_ml_per_gal": {"veg": 4.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0ATHENA0003",
        "name": "Grow B",
        "brand": "Athena",
        "npk": "1-3-5",
        "nutrients": {
            "description": (
                "Two-part vegetative formula (B). Supplies phosphorus, potassium, and magnesium for"
                "robust vegetative growth."
            ),
            "type": "base",
            "potassium_pct": 5.0,
            "magnesium_pct": 1.5,
            "dosage_ml_per_gal": {"veg": 4.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0ATHENA0004",
        "name": "Bloom A",
        "brand": "Athena",
        "npk": "4-0-1",
        "nutrients": {
            "description": (
                "Two-part bloom formula (A). Delivers calcium and nitrogen at ratios optimized forflower production."
            ),
            "type": "base",
            "calcium_pct": 4.0,
            "dosage_ml_per_gal": {"flower": 5.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0ATHENA0005",
        "name": "Bloom B",
        "brand": "Athena",
        "npk": "1-4-5",
        "nutrients": {
            "description": (
                "Two-part bloom formula (B). High phosphorus and potassium for dense flower development"
                "and resin production."
            ),
            "type": "base",
            "phosphorus_pct": 4.0,
            "potassium_pct": 5.0,
            "dosage_ml_per_gal": {"flower": 5.0},
        },
        "source": "seed",
    },
    # ─── Sweeteners & Carbohydrate Supplements ────────────────────────────────
    {
        "barcode": "0SW100001001",
        "name": "Bud Candy",
        "brand": "Advanced Nutrients",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Carbohydrate and amino acid supplement. Feeds beneficial microbes, enhances flavor andaroma profiles."
            ),
            "type": "sweetener",
            "ingredients": ["molasses", "cranberry extract", "grape extract", "malt extract", "amino acids"],
            "dosage_ml_per_gal": {"flower": 2.0},
            "notes": "Use throughout flowering. Compatible with sterile reservoirs — does not introduce microbes.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001002",
        "name": "Sweet (Raw)",
        "brand": "Botanicare",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Carbohydrate and amino acid supplement with no added flavor profile. Enhances natural"
                "terpene expression."
            ),
            "type": "sweetener",
            "ingredients": ["magnesium sulfate", "citric acid", "amino acids", "carbohydrates"],
            "magnesium_pct": 1.0,
            "sulfur_pct": 1.3,
            "dosage_ml_per_gal": {"veg": 3.0, "flower": 3.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001003",
        "name": "Molasses (Unsulphured Blackstrap)",
        "brand": "Generic/DIY",
        "npk": "0-0-5",
        "nutrients": {
            "description": (
                "Natural carbohydrate source that feeds soil microbes. Rich in potassium, calcium,"
                "magnesium, and iron. NOT for sterile hydro."
            ),
            "type": "sweetener",
            "organic": True,
            "potassium_pct": 5.0,
            "calcium_pct": 1.5,
            "magnesium_pct": 1.0,
            "iron_ppm": 500,
            "dosage_ml_per_gal": {"flower": 5.0},
            "notes": (
                "Organic/soil only. Will cause biofilm in sterile hydro. Use 1 tsp/gal in soil, 0.5 tsp/gal"
                "in organic hydro."
            ),
            "compatible_methods": ["soil", "coco_organic", "living_soil"],
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001004",
        "name": "Liquid KoolBloom",
        "brand": "General Hydroponics",
        "npk": "0-10-10",
        "nutrients": {
            "description": "High-phosphorus bloom enhancer for flower development. Liquid form for early-mid flower.",
            "type": "bloom_booster",
            "phosphorus_pct": 10.0,
            "potassium_pct": 10.0,
            "dosage_ml_per_gal": {"flower_early": 1.25, "flower_mid": 2.5},
            "notes": "Switch to Dry KoolBloom for last 2 weeks.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001005",
        "name": "Dry KoolBloom",
        "brand": "General Hydroponics",
        "npk": "2-45-28",
        "nutrients": {
            "description": (
                "Ultra-concentrated ripening agent for final weeks. Forces plants to finish and pack onweight."
            ),
            "type": "bloom_booster",
            "form": "dry",
            "phosphorus_pct": 45.0,
            "potassium_pct": 28.0,
            "dosage_g_per_gal": {"flower_final_2wk": 1.1},
            "notes": "Last 2 weeks only. Extremely concentrated — do not overdose. Discontinue all other P/K boosters.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001006",
        "name": "Terpinator",
        "brand": "Rhizoflora",
        "npk": "0-0-4",
        "nutrients": {
            "description": (
                "Terpene and resin enhancer with potassium and plant-derived compounds that increase"
                "essential oil production."
            ),
            "type": "supplement",
            "potassium_pct": 4.0,
            "dosage_ml_per_gal": {"veg_late": 5.0, "flower": 10.0},
            "notes": "Safe at high doses. Use throughout flower for maximum terpene enhancement.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001007",
        "name": "Flawless Finish",
        "brand": "Advanced Nutrients",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Flushing agent that chelates and removes accumulated salts and heavy metals from plant"
                "tissue before harvest."
            ),
            "type": "flush",
            "dosage_ml_per_gal": {"flush_final_week": 2.0},
            "notes": "Use for final 3-7 days. Replace all nutrients with only this product and plain water.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001008",
        "name": "FloraKleen",
        "brand": "General Hydroponics",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Salt-clearing solution for pre-harvest flush and mid-grow maintenance. Dissolvesmineral buildup."
            ),
            "type": "flush",
            "dosage_ml_per_gal": {"flush": 5.0, "maintenance": 2.5},
            "notes": "Can use mid-grow for salt buildup issues or as final flush for 3-7 days before harvest.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001009",
        "name": "Floralicious Plus",
        "brand": "General Hydroponics",
        "npk": "2-0.8-0.02",
        "nutrients": {
            "description": (
                "Organic bioactivator with vitamins, plant extracts, and humic acids. Enhances flavor,"
                "aroma, and essential oils."
            ),
            "type": "supplement",
            "organic": True,
            "ingredients": ["sea kelp", "plant extracts", "humic acid", "vitamins", "amino acids"],
            "dosage_ml_per_gal": {"all_stages": 1.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001010",
        "name": "Bud Ignitor",
        "brand": "Advanced Nutrients",
        "npk": "0-2-4",
        "nutrients": {
            "description": (
                "Transition supplement that triggers earlier flowering and more bud sites when flippingto 12/12."
            ),
            "type": "bloom_booster",
            "phosphorus_pct": 2.0,
            "potassium_pct": 4.0,
            "dosage_ml_per_gal": {"transition_2wk": 2.0},
            "notes": "Use only first 2 weeks after flip to 12/12. Discontinue once flowers form.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001011",
        "name": "Nirvana",
        "brand": "Advanced Nutrients",
        "npk": "0-0-1",
        "nutrients": {
            "description": (
                "Organic bloom supplement with alfalfa, seaweed, and bat guano. Adds complexity toflavor and aroma."
            ),
            "type": "supplement",
            "organic": True,
            "ingredients": ["alfalfa extract", "seaweed extract", "bat guano", "earthworm castings"],
            "dosage_ml_per_gal": {"flower": 2.0},
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001012",
        "name": "Cha Ching",
        "brand": "Fox Farm",
        "npk": "9-50-10",
        "nutrients": {
            "description": (
                "Ultra-high phosphorus dry soluble for final flower phase. Part of the Fox Farm soluble"
                "trio (Open Sesame → Beastie Bloomz → Cha Ching)."
            ),
            "type": "bloom_booster",
            "form": "dry",
            "phosphorus_pct": 50.0,
            "potassium_pct": 10.0,
            "dosage_tsp_per_gal": {"flower_final_2wk": 0.5},
            "notes": "Weeks 6+ of flower. Last in the soluble series.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001013",
        "name": "Open Sesame",
        "brand": "Fox Farm",
        "npk": "5-45-19",
        "nutrients": {
            "description": (
                "Dry soluble bloom initiator. First in the Fox Farm soluble trio to trigger heavyflowering."
            ),
            "type": "bloom_booster",
            "form": "dry",
            "phosphorus_pct": 45.0,
            "potassium_pct": 19.0,
            "dosage_tsp_per_gal": {"transition_2wk": 0.5},
            "notes": "First 2 weeks of flower only.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001014",
        "name": "Beastie Bloomz",
        "brand": "Fox Farm",
        "npk": "0-50-30",
        "nutrients": {
            "description": "Dry soluble mid-flower booster. Second in the Fox Farm soluble trio for peak bloom.",
            "type": "bloom_booster",
            "form": "dry",
            "phosphorus_pct": 50.0,
            "potassium_pct": 30.0,
            "dosage_tsp_per_gal": {"flower_wk3_5": 0.5},
            "notes": "Weeks 3-5 of flower.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001015",
        "name": "Kelp Me Kelp You",
        "brand": "Fox Farm",
        "npk": "1-0.1-2",
        "nutrients": {
            "description": "Norwegian kelp extract with natural growth hormones, cytokinins, and trace minerals.",
            "type": "supplement",
            "organic": True,
            "ingredients": ["Ascophyllum nodosum kelp"],
            "dosage_tsp_per_gal": {"all_stages": 1.0},
            "notes": "Foliar or root drench. Natural source of cytokinins and auxins.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001016",
        "name": "Tribus Original",
        "brand": "Impello Biosciences",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Three-species bacterial inoculant (Bacillus subtilis, B. amyloliquefaciens, B."
                "pumilus). Increases nutrient availability and root mass."
            ),
            "type": "supplement",
            "beneficial_microbes": True,
            "organisms": ["Bacillus subtilis", "Bacillus amyloliquefaciens", "Bacillus pumilus"],
            "cfu_per_ml": 10_000_000_000,
            "dosage_ml_per_gal": {"all_stages": 1.0},
            "notes": "Compatible with sterile res when added at res change. Works in any medium.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001017",
        "name": "URB Natural",
        "brand": "URB",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Humic/fulvic acid concentrate with microbial metabolites. Increases nutrient uptake"
                "efficiency by up to 30%."
            ),
            "type": "supplement",
            "ingredients": ["humic acid", "fulvic acid", "microbial metabolites"],
            "dosage_ml_per_gal": {"all_stages": 1.5},
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001018",
        "name": "Diamond Nectar",
        "brand": "General Hydroponics",
        "npk": "0-1-1",
        "nutrients": {
            "description": (
                "Humic acid extracted from leonardite. Chelates and transports micro-nutrients into the"
                "plant more efficiently."
            ),
            "type": "supplement",
            "humic_acid": True,
            "dosage_ml_per_gal": {"all_stages": 2.5},
            "notes": "Especially useful in hydro where humic acid is otherwise absent.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001019",
        "name": "Hygrozyme",
        "brand": "Sipco",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Concentrated enzyme formula (cellulase, xylanase, hemicellulase, beta-glucanase)."
                "Breaks down dead root matter into usable sugars."
            ),
            "type": "supplement",
            "enzymes": True,
            "dosage_ml_per_gal": {"all_stages": 6.0},
            "notes": "Safe with beneficial microbes. Keeps root zone clean in all media.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001020",
        "name": "RapidStart",
        "brand": "General Hydroponics",
        "npk": "1-0.5-1",
        "nutrients": {
            "description": (
                "Root growth enhancer with plant-derived compounds for vigorous root development inearly stages."
            ),
            "type": "supplement",
            "dosage_ml_per_gal": {"seedling": 1.0, "clone": 1.0, "veg_early": 1.0},
            "notes": "Seedling through early veg only (first 3-4 weeks). Discontinue once root mass is established.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SW100001021",
        "name": "Clonex Clone Solution",
        "brand": "Hydrodynamics",
        "npk": "1-0.4-1",
        "nutrients": {
            "description": (
                "Low-strength nutrient solution designed for clones and seedlings. Contains vitamins"
                "and root-promoting compounds."
            ),
            "type": "base",
            "dosage_ml_per_gal": {"clone": 7.5, "seedling": 5.0},
            "notes": (
                "Use alone — do not mix with other base nutrients. Transition to regular feed after rootsestablish."
            ),
        },
        "source": "seed",
    },
    # ─── pH Management Products ───────────────────────────────────────────────
    {
        "barcode": "0PH100001001",
        "name": "pH Up (Potassium Hydroxide)",
        "brand": "General Hydroponics",
        "npk": "0-0-0",
        "nutrients": {
            "description": "Concentrated potassium hydroxide solution for raising nutrient solution pH.",
            "type": "ph_adjuster",
            "direction": "up",
            "active_ingredient": "potassium hydroxide (KOH)",
            "dosage_ml_per_gal": {"typical": 0.5},
            "notes": "Add drops at a time. Very concentrated. Always add to water, never water to acid/base.",
        },
        "source": "seed",
    },
    {
        "barcode": "0PH100001002",
        "name": "pH Down (Phosphoric Acid)",
        "brand": "General Hydroponics",
        "npk": "0-0-0",
        "nutrients": {
            "description": "Phosphoric acid solution for lowering nutrient solution pH. Most common hydro pH down.",
            "type": "ph_adjuster",
            "direction": "down",
            "active_ingredient": "phosphoric acid (H3PO4)",
            "dosage_ml_per_gal": {"typical": 0.5},
            "notes": "Adds a tiny amount of phosphorus. Fine for all stages. Add drops at a time.",
        },
        "source": "seed",
    },
    {
        "barcode": "0PH100001003",
        "name": "pH Down (Citric Acid)",
        "brand": "Generic/DIY",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Organic acid for pH reduction. Cheaper but less stable than phosphoric acid — pH tends"
                "to drift back up."
            ),
            "type": "ph_adjuster",
            "direction": "down",
            "active_ingredient": "citric acid",
            "organic": True,
            "dosage_g_per_gal": {"typical": 0.5},
            "notes": "Breaks down quickly in solution. Acceptable for soil but not ideal for recirculating hydro.",
            "compatible_methods": ["soil", "coco", "drain_to_waste"],
        },
        "source": "seed",
    },
    # ─── Silica & Plant Strengtheners ─────────────────────────────────────────
    {
        "barcode": "0SI100001001",
        "name": "Power Si Original",
        "brand": "Power Si",
        "npk": "0-0-0",
        "nutrients": {
            "description": (
                "Mono-silicic acid (plant-available form). More bioavailable than potassium silicate"
                "products. Strengthens cell walls, increases canopy weight."
            ),
            "type": "supplement",
            "silica_form": "mono-silicic acid",
            "bioavailability": "high",
            "dosage_ml_per_gal": {"all_stages": 0.5},
            "notes": "Does not raise pH like potassium silicate. Can be mixed in any order.",
        },
        "source": "seed",
    },
    {
        "barcode": "0SI100001002",
        "name": "Pro-TeKt",
        "brand": "Dyna-Gro",
        "npk": "0-0-3",
        "nutrients": {
            "description": (
                "Potassium silicate supplement. Builds stronger stems and leaves, improves resistance"
                "to heat, drought, and pests."
            ),
            "type": "supplement",
            "silica_pct": 3.7,
            "potassium_pct": 3.0,
            "dosage_ml_per_gal": {"all_stages": 1.5},
            "notes": "Add first to fresh water. Raises pH significantly — adjust after adding.",
        },
        "source": "seed",
    },
]


async def sync_seed_nutrients(session: AsyncSession) -> int:
    """Seed the nutrient_products table with curated data. Returns count of new nutrients added."""
    added = 0
    for nutrient_data in SEED_NUTRIENTS:
        existing = (
            await session.execute(select(NutrientProduct).where(NutrientProduct.barcode == nutrient_data["barcode"]))
        ).scalar_one_or_none()

        if existing:
            for key, value in nutrient_data.items():
                setattr(existing, key, value)
            existing.synced_at = datetime.now(UTC)
        else:
            product = NutrientProduct(
                **nutrient_data,
                synced_at=datetime.now(UTC),
            )
            session.add(product)
            added += 1

    await session.commit()
    logger.info("Nutrient sync complete: %d new, %d total", added, len(SEED_NUTRIENTS))
    return added
