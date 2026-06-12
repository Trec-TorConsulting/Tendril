"""Nutrition seed data — standalone additives and known conflicts.

Sources:
- GrowWeedEasy.com additive recommendations (Hydroguard, CalMag, Silica)
- Botanicare Hydroguard label and independent root rot studies
- Cannabis-specific CalMag deficiency research (LED + coco correlation)
- Community-verified conflict data (H2O2 vs beneficial microbes)
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
# STANDALONE ADDITIVES
# These work alongside ANY nutrient brand — they're dosed independently
# ═══════════════════════════════════════════════════════════════════════════════

HYDRO_TYPES = ["dwc", "rdwc", "nft", "ebb_flow", "aeroponics", "drip", "kratky"]
ALL_TYPES = [*HYDRO_TYPES, "coco", "soil", "rockwool", "outdoor_soil", "outdoor_container", "living_soil", "wicking_bed"]

ADDITIVES = [
    # === ROOT HEALTH ===
    {
        "brand_slug": "botanicare",
        "slug": "hydroguard",
        "name": "Hydroguard",
        "category": "microbe",
        "description": "Bacillus amyloliquefaciens — beneficial bacteria that colonizes roots and outcompetes pythium/fusarium. The #1 recommended root rot prevention for hydroponic cannabis. Essential for DWC when water temps exceed 68°F.",
        "dose_ml_per_gallon": 2.0,
        "when_to_use": "Every reservoir change and top-off from seedling through harvest. Not a nutrient — does not need to be flushed. Works best when water temps are 65-75°F.",
        "grow_type_slugs": HYDRO_TYPES,
    },
    {
        "brand_slug": "general-hydroponics",
        "slug": "rapid-start",
        "name": "RapidStart",
        "category": "root_enhancer",
        "description": "Plant-derived root growth enhancer. Stimulates explosive root development in seedlings and transplants. Contains natural plant extracts that signal root cell division.",
        "dose_ml_per_gallon": 1.0,
        "when_to_use": "Seedling through early veg (first 3-4 weeks). Discontinue once root mass is well established. Particularly effective after transplant stress.",
        "grow_type_slugs": ALL_TYPES,
    },
    # === CALCIUM & MAGNESIUM ===
    {
        "brand_slug": "botanicare",
        "slug": "calmag-plus",
        "name": "Cal-Mag Plus",
        "category": "calmag",
        "description": "Calcium (3.2%), magnesium (1.2%), iron (0.1%), and nitrogen (2%). Prevents the most common cannabis deficiency under LED lights and in coco coir. Add FIRST to water before base nutrients.",
        "dose_ml_per_gallon": 5.0,
        "when_to_use": "Every feeding when: using RO/filtered water, growing in coco coir, using LED grow lights, or seeing calcium/magnesium deficiency (brown spots, interveinal chlorosis). Reduce to 2.5ml/gal in late flower.",
        "grow_type_slugs": ALL_TYPES,
    },
    {
        "brand_slug": "general-hydroponics",
        "slug": "calimagic",
        "name": "CaliMagic",
        "category": "calmag",
        "description": "GH's calcium-magnesium supplement. 1-0-0 with 5% Ca, 1.5% Mg, 0.1% Fe. Specifically formulated for use with Flora Series. Helps stabilize pH in RO water.",
        "dose_ml_per_gallon": 5.0,
        "when_to_use": "Every feeding with RO water, coco, or LEDs. Add first to water. 5ml/gal in veg, reduce to 2.5ml/gal in late flower. Optional with tap water (>150ppm).",
        "grow_type_slugs": ALL_TYPES,
    },
    # === SILICA ===
    {
        "brand_slug": "general-hydroponics",
        "slug": "armor-si",
        "name": "Armor Si (Silica)",
        "category": "silica",
        "description": "Potassium silicate strengthens cell walls, making stems thicker, leaves tougher, and plants more resistant to heat, drought, and pests. Increases weight-bearing capacity for heavy buds.",
        "dose_ml_per_gallon": 1.5,
        "when_to_use": "Every feeding from early veg through week 6 of flower. MUST add to fresh water FIRST before any other nutrients (raises pH significantly). Stop 2 weeks before harvest.",
        "grow_type_slugs": ALL_TYPES,
    },
    # === ENZYMES ===
    {
        "brand_slug": "botanicare",
        "slug": "slf-100",
        "name": "SLF-100",
        "category": "enzyme",
        "description": "Enzymatic formula that breaks down dead root matter, salt buildup, and organic debris. Keeps root zone and reservoir clean. Works synergistically with Hydroguard.",
        "dose_ml_per_gallon": 1.0,
        "when_to_use": "Every reservoir change throughout entire cycle including flush. Safe to use with beneficial microbes. Particularly important in recirculating systems.",
        "grow_type_slugs": [*HYDRO_TYPES, "coco"],
    },
    # === BENEFICIAL MICROBES (SOIL/COCO) ===
    {
        "brand_slug": "botanicare",
        "slug": "recharge",
        "name": "Real Growers Recharge",
        "category": "microbe",
        "description": "Beneficial microbe blend: mycorrhizae, trichoderma, bacillus, and kelp extract. Creates thriving rhizosphere in soil and coco. Can cloud DWC reservoirs — best for media grows.",
        "dose_grams_per_gallon": 0.5,
        "when_to_use": "Once per week as a soil/coco drench. Works best in soil and coco — NOT recommended for DWC/RDWC (clogs air stones, clouds water). Apply throughout veg and flower.",
        "grow_type_slugs": ["coco", "soil", "outdoor_soil", "outdoor_container", "living_soil", "wicking_bed"],
    },
    {
        "brand_slug": "botanicare",
        "slug": "mammoth-p",
        "name": "Mammoth P",
        "category": "microbe",
        "description": "Phosphorus-liberating microbial consortium. University-developed bacteria that break down bound phosphorus, making up to 16% more P available to roots. Peer-reviewed research published.",
        "dose_ml_per_gallon": 0.16,
        "when_to_use": "From mid-veg through end of flower. Add at every feeding/reservoir change. Works in all media including DWC. Very concentrated — less than 1ml per gallon.",
        "grow_type_slugs": ALL_TYPES,
    },
    # === PK BOOSTERS (universal) ===
    {
        "brand_slug": "general-hydroponics",
        "slug": "liquid-koolbloom",
        "name": "Liquid KoolBloom",
        "category": "pk_booster",
        "description": "0-10-10 PK booster for early-to-mid flower. Increases essential oil production and bud density. Use for 4-6 weeks during bud formation phase.",
        "dose_ml_per_gallon": 2.5,
        "when_to_use": "Weeks 2-6 of flower. Start at 1.25ml/gal and increase to 2.5ml/gal. Discontinue 2 weeks before harvest. Monitor EC — adds significantly.",
        "grow_type_slugs": ALL_TYPES,
    },
    # === FLUSH ===
    {
        "brand_slug": "general-hydroponics",
        "slug": "florakleen",
        "name": "FloraKleen",
        "category": "flush",
        "description": "Salt-dissolving flush agent. Removes mineral buildup from root zone and growing media without killing beneficial microbes. Use mid-grow for maintenance and pre-harvest for clean finish.",
        "dose_ml_per_gallon": 2.5,
        "when_to_use": "Maintenance: once between nutrient changes to clear salt buildup. Pre-harvest: final 2 days before chop. Also useful for emergency salt lockout recovery.",
        "grow_type_slugs": ALL_TYPES,
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# KNOWN CONFLICTS
# Critical interactions that the system must warn users about
# ═══════════════════════════════════════════════════════════════════════════════

CONFLICTS = [
    # === MICROBE KILLERS ===
    {
        "item_a_type": "additive",
        "item_a_slug": "hydroguard",
        "item_b_type": "additive",
        "item_b_slug": "h2o2",
        "severity": "critical",
        "reason": "Hydrogen peroxide (H2O2) is a sterilizer that kills ALL bacteria — including the beneficial Bacillus in Hydroguard. Using both simultaneously wastes money and provides zero root protection.",
        "recommendation": "Choose ONE approach: sterile reservoir (H2O2 every 3 days) OR beneficial bacteria (Hydroguard). Never combine. Hydroguard is preferred for cannabis as it provides lasting colonization.",
    },
    {
        "item_a_type": "additive",
        "item_a_slug": "recharge",
        "item_b_type": "additive",
        "item_b_slug": "h2o2",
        "severity": "critical",
        "reason": "H2O2 sterilizes all microorganisms including the mycorrhizae and trichoderma in Recharge. Complete waste of both products.",
        "recommendation": "Choose one approach: sterile (H2O2) or biological (Recharge). For soil/coco, biological is always preferred.",
    },
    {
        "item_a_type": "additive",
        "item_a_slug": "hydroguard",
        "item_b_type": "additive",
        "item_b_slug": "florakleen",
        "severity": "warning",
        "reason": "FloraKleen can reduce beneficial bacteria populations when used at full strength as a flush. Normal maintenance dosing is fine.",
        "recommendation": "If doing a full FloraKleen flush, re-dose Hydroguard after flushing. Regular maintenance doses (2.5ml/gal) are safe to use together.",
    },
    # === pH PERFECT CONFLICTS ===
    {
        "item_a_type": "product",
        "item_a_slug": "sensi-grow-a",
        "item_b_type": "additive",
        "item_b_slug": "armor-si",
        "severity": "warning",
        "reason": "pH Perfect technology works by maintaining a specific pH buffer. Adding silica (very alkaline, pH 11+) can overwhelm the buffering system and destabilize pH.",
        "recommendation": "Advanced Nutrients makes their own silica product (Rhino Skin) designed for pH Perfect compatibility. If using Armor Si, add 30 min before AN nutrients and test pH.",
    },
    {
        "item_a_type": "product",
        "item_a_slug": "sensi-bloom-a",
        "item_b_type": "additive",
        "item_b_slug": "armor-si",
        "severity": "warning",
        "reason": "pH Perfect technology works by maintaining a specific pH buffer. Adding silica (very alkaline, pH 11+) can overwhelm the buffering system and destabilize pH.",
        "recommendation": "Advanced Nutrients makes their own silica product (Rhino Skin) designed for pH Perfect compatibility. If using Armor Si, add 30 min before AN nutrients and test pH.",
    },
    # === MIXING ORDER ISSUES ===
    {
        "item_a_type": "additive",
        "item_a_slug": "calmag-plus",
        "item_b_type": "additive",
        "item_b_slug": "armor-si",
        "severity": "warning",
        "reason": "Both raise pH significantly. If added consecutively without mixing, calcium can precipitate out of solution (white cloudy residue) making it unavailable to plants.",
        "recommendation": "Add Silica FIRST to fresh water, stir thoroughly and wait 5 minutes. Then add CalMag second. Then base nutrients last. Never add both to concentrated solution.",
    },
    # === ORGANIC + SYNTHETIC CONFLICTS ===
    {
        "item_a_type": "additive",
        "item_a_slug": "recharge",
        "item_b_type": "product",
        "item_b_slug": "flora-micro",
        "severity": "warning",
        "reason": "High-EC synthetic nutrients can suppress beneficial microbial activity. Recharge microbes thrive best in lower-EC environments (soil/coco with moderate feeding).",
        "recommendation": "If using Recharge with synthetic nutrients, apply on alternating days. Give Recharge on a plain water day, and synthetics on feed days. This gives microbes time to establish.",
    },
    # === DWC-SPECIFIC ===
    {
        "item_a_type": "additive",
        "item_a_slug": "recharge",
        "item_b_type": "product",
        "item_b_slug": "part-a",
        "severity": "warning",
        "reason": "Recharge in DWC/RDWC systems can cause cloudy water, biofilm on air stones, and anaerobic pockets. The organic matter feeds unwanted organisms in stagnant water.",
        "recommendation": "Use Hydroguard instead of Recharge for DWC systems. Recharge is designed for soil and coco where organic matter is beneficial, not submerged root systems.",
    },
]
