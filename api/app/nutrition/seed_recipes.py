"""Nutrition seed data — organic recipes (compost teas, amendments, KNF, foliar).

Sources:
- BuildASoil / Jeremy Silva — living soil methodology, documented on YouTube/blog
- "Teaming with Microbes" by Jeff Lowenfels — compost tea science
- Korean Natural Farming (KNF) Master Cho methodology
- Rev's True Living Organics (TLO) — cannabis-specific soil building
- Real-world living soil cannabis cultivation (documented grows)
"""

from __future__ import annotations

ORGANIC_GROW_TYPES = ["soil", "outdoor_soil", "outdoor_container", "living_soil", "wicking_bed"]
ALL_SOIL = [*ORGANIC_GROW_TYPES, "coco"]

ORGANIC_RECIPES = [
    # ═══════════════════════════════════════════════════════════════════════════
    # COMPOST TEAS
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "aerated-compost-tea-veg",
        "name": "Actively Aerated Compost Tea (Vegetative)",
        "category": "compost_tea",
        "description": "Aerobic compost tea designed to multiply beneficial bacteria and fungi for vegetative growth. The oxygen-rich environment favors bacterial populations that cycle nitrogen. 24-48 hour brew.",
        "ingredients": [
            {
                "name": "Quality compost / worm castings",
                "amount": "1/4",
                "unit": "cup per gallon",
                "notes": "Must be high-quality, earthy-smelling compost. Worm castings preferred.",
            },
            {
                "name": "Unsulfured blackstrap molasses",
                "amount": "1",
                "unit": "tablespoon per gallon",
                "notes": "Feeds bacteria. Do NOT use sulfured molasses — sulfur kills microbes.",
            },
            {
                "name": "Kelp meal or liquid kelp",
                "amount": "1",
                "unit": "teaspoon per gallon",
                "notes": "Provides growth hormones (cytokinins) and trace minerals for the biology.",
            },
            {
                "name": "Fish hydrolysate",
                "amount": "1",
                "unit": "teaspoon per gallon",
                "notes": "Optional — provides nitrogen and feeds fungi. Use hydrolysate NOT emulsion (emulsion is heat-processed).",
            },
        ],
        "instructions": "1. Fill container with dechlorinated water (let tap water sit 24h or use RO). 2. Add compost in a mesh bag or loose. 3. Add molasses, kelp, and fish hydrolysate. 4. Insert air pump with air stone — the tea MUST be actively aerated the entire brew time. 5. Brew 24-36 hours at 65-80°F. 6. Tea should smell sweet/earthy. If it smells rotten, discard — anaerobic bacteria indicate failed brew. 7. Apply immediately after brewing — organisms begin dying without oxygen within 4 hours.",
        "brew_time_hours": 24.0,
        "application_rate": "Apply full strength as soil drench. Can also dilute 1:4 for foliar spray (before lights on).",
        "frequency": "Every 1-2 weeks during vegetative growth. Weekly provides maximum biological activity.",
        "best_for_stages": ["vegetative"],
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "warnings": "Must be actively aerated entire time. Anaerobic tea (no air pump) grows harmful bacteria. Use within 4 hours of removing air pump. Do NOT use chlorinated water. Never brew longer than 48 hours.",
    },
    {
        "slug": "aerated-compost-tea-bloom",
        "name": "Actively Aerated Compost Tea (Flower/Bloom)",
        "category": "compost_tea",
        "description": "Bloom-focused AACT with high-phosphorus inputs. Fungal-dominant tea that enhances phosphorus cycling for bud development. Bat guano and bone meal fuel P-mobilizing fungi.",
        "ingredients": [
            {
                "name": "Quality compost / worm castings",
                "amount": "1/4",
                "unit": "cup per gallon",
                "notes": "Base biology source.",
            },
            {
                "name": "Unsulfured blackstrap molasses",
                "amount": "1",
                "unit": "tablespoon per gallon",
                "notes": "Feeds bacteria. Molasses also contains potassium.",
            },
            {
                "name": "Bat guano (high-P)",
                "amount": "1",
                "unit": "tablespoon per gallon",
                "notes": "Indonesian bat guano (0-7-0 or similar). Feeds phosphorus-cycling fungi.",
            },
            {
                "name": "Bone meal",
                "amount": "1",
                "unit": "teaspoon per gallon",
                "notes": "Slow-release phosphorus source for the biology to process.",
            },
            {
                "name": "Kelp meal",
                "amount": "1",
                "unit": "teaspoon per gallon",
                "notes": "Potassium and growth hormones.",
            },
        ],
        "instructions": "1. Dechlorinate water. 2. Place all dry inputs in mesh bag (keeps particles from clogging air stone). 3. Add molasses to water. 4. Submerge mesh bag, add air stone. 5. Brew 24-36 hours with vigorous aeration. 6. Tea should develop slight foam on surface (indicates active biology). 7. Remove bag, apply immediately as soil drench.",
        "brew_time_hours": 36.0,
        "application_rate": "Full strength soil drench. Drench until 10-20% runoff to reach entire root zone.",
        "frequency": "Weekly during flower for maximum bud development. Every 2 weeks minimum.",
        "best_for_stages": ["flowering"],
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "warnings": "Same aerobic requirements as veg tea. Bat guano can harbor pathogens — source from reputable suppliers. Do not foliar spray in flower (mold risk on buds).",
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # TOP DRESS / DRY AMENDMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "top-dress-veg",
        "name": "Vegetative Top Dress (All-Purpose)",
        "category": "top_dress",
        "description": "Balanced dry amendment top dress for vegetative growth. Provides slow-release nitrogen, phosphorus, and potassium over 3-4 weeks as soil biology breaks down the inputs.",
        "ingredients": [
            {
                "name": "All-purpose dry amendment (4-4-4)",
                "amount": "2-3",
                "unit": "tablespoons per gallon of soil",
                "notes": "Gaia Green 4-4-4, DTE Bio-Live, or similar balanced organic fertilizer.",
            },
            {
                "name": "Worm castings",
                "amount": "1/4",
                "unit": "inch layer on surface",
                "notes": "Provides biology to break down amendments and gentle immediate nitrogen.",
            },
            {
                "name": "Neem meal (6-1-2)",
                "amount": "1",
                "unit": "tablespoon per gallon of soil",
                "notes": "Optional — slow nitrogen + natural pest prevention (fungus gnats, root aphids).",
            },
            {
                "name": "Kelp meal (1-0.1-2)",
                "amount": "1",
                "unit": "tablespoon per gallon of soil",
                "notes": "Optional — growth hormones, potassium, 60+ trace minerals.",
            },
        ],
        "instructions": "1. Scratch top 1/2 inch of soil surface gently with fork (avoid disturbing roots). 2. Sprinkle dry amendments evenly across surface. 3. Cover with 1/4 inch worm castings. 4. Water thoroughly to activate. 5. Optional: add mulch layer (straw, cover crop) on top to retain moisture. 6. Re-apply every 3-4 weeks.",
        "brew_time_hours": None,
        "application_rate": "2-3 tablespoons per gallon of soil. A 5-gallon pot gets 10-15 tablespoons total.",
        "frequency": "Every 3-4 weeks during vegetative growth. First application 2-3 weeks after transplant (when soil nutrients deplete).",
        "best_for_stages": ["vegetative"],
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "warnings": "Do not over-apply — organic amendments can burn if applied too heavily. Takes 1-2 weeks to become available (plan ahead). Water thoroughly after application.",
    },
    {
        "slug": "top-dress-flower",
        "name": "Flowering Top Dress (High-P/K)",
        "category": "top_dress",
        "description": "Phosphorus and potassium heavy top dress for flower development. Low nitrogen to prevent leafy growth during bud formation. Apply 1-2 weeks before flip and again at week 3-4 of flower.",
        "ingredients": [
            {
                "name": "Bloom dry amendment (2-8-4 or 4-8-4)",
                "amount": "2-3",
                "unit": "tablespoons per gallon of soil",
                "notes": "Gaia Green Power Bloom, DTE Rose & Flower, or similar high-P organic.",
            },
            {
                "name": "Worm castings",
                "amount": "1/4",
                "unit": "inch layer",
                "notes": "Biology layer to process amendments.",
            },
            {
                "name": "Langbeinite (0-0-22)",
                "amount": "1",
                "unit": "teaspoon per gallon of soil",
                "notes": "Optional — sulfate of potash magnesia. Adds K, Mg, and S for terpene/resin production.",
            },
            {
                "name": "Bone meal (3-15-0)",
                "amount": "1",
                "unit": "tablespoon per gallon of soil",
                "notes": "Optional — extra phosphorus for heavy-feeding strains.",
            },
        ],
        "instructions": "1. Apply 1-2 weeks BEFORE flipping to 12/12 (amendments take time to break down). 2. Scratch surface, apply amendments, cover with castings. 3. Water thoroughly. 4. Re-apply once more at week 3-4 of flower if plants show hunger (yellowing before week 6 = too early). 5. Do NOT top dress after week 5 of flower — nutrients won't break down in time.",
        "brew_time_hours": None,
        "application_rate": "2-3 tablespoons per gallon of soil for each application.",
        "frequency": "Twice: once 1-2 weeks before flip, once at week 3-4 of flower. That's it for organic flower nutrition.",
        "best_for_stages": ["flowering"],
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "warnings": "Apply EARLY — dry amendments take 2+ weeks to break down and become plant-available. Late application is wasted. Do not top dress after week 5 of flower.",
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # KNF (Korean Natural Farming)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "knf-fpj",
        "name": "Fermented Plant Juice (FPJ)",
        "category": "knf",
        "description": "KNF Fermented Plant Juice — captures growth hormones and minerals from vigorous growing tips. Comfrey and nettle FPJ provides potassium, nitrogen, and natural growth stimulants. 7-day ferment.",
        "ingredients": [
            {
                "name": "Fresh plant growth tips (comfrey, nettle, or alfalfa)",
                "amount": "equal weight to sugar",
                "unit": "packed volume",
                "notes": "Harvest in early morning when hormone levels are highest. Use actively growing tips only.",
            },
            {
                "name": "Brown sugar (unrefined)",
                "amount": "equal weight",
                "unit": "to plant material",
                "notes": "Creates osmotic extraction. Must be brown/raw sugar — white sugar lacks minerals.",
            },
        ],
        "instructions": "1. Harvest plant tips in early morning (growth hormones peak at dawn). 2. Chop roughly. 3. Mix plant material and brown sugar 1:1 by weight in a container. 4. Press down firmly, cover with breathable cloth (not airtight). 5. Place weight on top to keep material submerged in extracted liquid. 6. Ferment 7 days in cool, dark place. 7. Strain liquid — this is your FPJ concentrate. 8. Store in dark bottle, refrigerate. Lasts 6-12 months. 9. Dilute 1:500 to 1:1000 for use.",
        "brew_time_hours": 168.0,
        "application_rate": "Dilute 1:500 (2ml per liter / 0.5 tsp per gallon). Apply as soil drench or foliar spray.",
        "frequency": "Weekly during vegetative growth. Can alternate with compost tea applications.",
        "best_for_stages": ["vegetative"],
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "warnings": "FPJ is high in nitrogen — reduce or stop in flower. Only use growth tips (not flowers or fruits). If ferment smells rotten or grows mold, discard and restart.",
    },
    {
        "slug": "knf-ffj",
        "name": "Fermented Fruit Juice (FFJ)",
        "category": "knf",
        "description": "KNF Fermented Fruit Juice — extracts phosphorus, potassium, and ripening hormones from ripe fruits. Used during flowering to signal the plant to produce fruits (buds). Banana FFJ is ideal for cannabis.",
        "ingredients": [
            {
                "name": "Ripe banana peels (or papaya, melon)",
                "amount": "equal weight to sugar",
                "unit": "by weight",
                "notes": "Must be fully ripe (brown spots on bananas). Ripeness = maximum potassium and enzymes.",
            },
            {
                "name": "Brown sugar (unrefined)",
                "amount": "equal weight",
                "unit": "to fruit material",
                "notes": "Same osmotic extraction process as FPJ.",
            },
        ],
        "instructions": "1. Use ripe-to-overripe fruit (bananas with brown spots are perfect — highest K). 2. Chop fruit into small pieces. 3. Layer fruit and sugar 1:1 by weight. 4. Cover with breathable cloth, add weight. 5. Ferment 7 days. 6. Strain and bottle. 7. Dilute 1:500 to 1:1000 for use. 8. Apply during flowering for phosphorus and potassium.",
        "brew_time_hours": 168.0,
        "application_rate": "Dilute 1:500 (2ml per liter). Apply as soil drench during flower.",
        "frequency": "Weekly during weeks 2-7 of flower. Alternating with bloom compost tea is excellent.",
        "best_for_stages": ["flowering"],
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "warnings": "Only use during flower — the ripening hormones can trigger premature flowering in veg. Fruit flies may be attracted — ferment in sealed area.",
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # SOIL BUILDING
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "living-soil-base-recipe",
        "name": "Living Soil Base Mix (Coots Mix)",
        "category": "dry_amendment",
        "description": "The cannabis community standard living soil recipe based on Clackamas Coots' proven formula. Equal parts peat/coco, compost, and aeration. Amended and 'cooked' for 2-4 weeks before planting. Can be re-used indefinitely with top dressing.",
        "ingredients": [
            {
                "name": "Peat moss (or coco coir)",
                "amount": "1/3",
                "unit": "of total volume",
                "notes": "Canadian sphagnum peat or pre-buffered coco coir. This is your water-holding component.",
            },
            {
                "name": "High-quality compost / worm castings",
                "amount": "1/3",
                "unit": "of total volume",
                "notes": "Mix of compost and worm castings. This provides biology and initial nutrition.",
            },
            {
                "name": "Aeration (perlite/pumice/lava rock)",
                "amount": "1/3",
                "unit": "of total volume",
                "notes": "Pumice or rice hulls preferred (don't float). Provides oxygen to roots and drainage.",
            },
            {
                "name": "Neem meal",
                "amount": "1/2",
                "unit": "cup per cubic foot",
                "notes": "Slow-release nitrogen + pest prevention.",
            },
            {
                "name": "Kelp meal",
                "amount": "1/2",
                "unit": "cup per cubic foot",
                "notes": "Growth hormones, potassium, trace minerals.",
            },
            {
                "name": "Crustacean meal (crab/shrimp)",
                "amount": "1/2",
                "unit": "cup per cubic foot",
                "notes": "Chitin triggers plant immune response. Also provides calcium and nitrogen.",
            },
            {
                "name": "Glacial rock dust (or basalt)",
                "amount": "1",
                "unit": "cup per cubic foot",
                "notes": "60+ trace minerals. Provides long-term mineral reserve.",
            },
            {
                "name": "Gypsum",
                "amount": "1/2",
                "unit": "cup per cubic foot",
                "notes": "Calcium and sulfur without changing pH.",
            },
            {
                "name": "Oyster shell flour",
                "amount": "1/2",
                "unit": "cup per cubic foot",
                "notes": "Slow-release calcium, pH buffer (prevents soil from becoming too acidic).",
            },
        ],
        "instructions": "1. Mix base components (peat, compost, aeration) in equal parts by volume. 2. Add all amendments per cubic foot, mix thoroughly. 3. Moisten to 'wrung-out sponge' moisture level. 4. Cover and let 'cook' for 2-4 weeks (biology breaks down amendments). 5. Soil should smell earthy and sweet when ready. 6. Plant directly — only add water from this point forward. 7. Top-dress every 3-4 weeks to replenish. 8. Re-use soil by re-amending between grows.",
        "brew_time_hours": 672.0,
        "application_rate": "Fill containers (minimum 7-gallon for photoperiod cannabis, 3-gallon for autos).",
        "frequency": "Mix once, re-use indefinitely with top dressing between cycles.",
        "best_for_stages": ["seedling", "vegetative", "flowering"],
        "grow_type_slugs": ["soil", "living_soil", "outdoor_container"],
        "warnings": "MUST cook 2-4 weeks minimum — fresh amendments will burn seedlings. Soil should not smell like ammonia when ready (ammonia = still composting). Use minimum 7-gallon containers for photos.",
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # FOLIAR
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "aloe-vera-foliar",
        "name": "Aloe Vera Foliar Spray",
        "category": "foliar",
        "description": "Fresh aloe vera contains salicylic acid (natural SAR trigger), saponins, amino acids, and over 75 active compounds. Triggers Systemic Acquired Resistance (SAR) — the plant's immune system activates against pests and pathogens.",
        "ingredients": [
            {
                "name": "Fresh aloe vera inner gel",
                "amount": "1/4",
                "unit": "cup per gallon",
                "notes": "Fresh fillet from leaf, or 1/8 tsp aloe vera powder (200x concentrate). Must be pure — no added ingredients.",
            },
            {
                "name": "Dechlorinated water",
                "amount": "1",
                "unit": "gallon",
                "notes": "Chlorine damages plant tissue when foliar applied. Let tap water sit 24h or use RO.",
            },
        ],
        "instructions": "1. Fillet fresh aloe leaf and scoop out clear inner gel (avoid green skin — contains latex). 2. Blend gel with water until smooth. 3. Strain through cloth to remove pulp (clogs sprayers). 4. Add to spray bottle. 5. Apply to all leaf surfaces (top AND bottom) until dripping. 6. Apply 30 minutes before lights on, or during lights-off period. 7. Use within 24 hours of blending (enzymes degrade quickly).",
        "brew_time_hours": None,
        "application_rate": "Spray until leaf surfaces are thoroughly wet. Apply to tops and undersides of leaves.",
        "frequency": "Weekly during veg. Stop foliar feeding once flowers form (mold risk).",
        "best_for_stages": ["vegetative"],
        "grow_type_slugs": ALL_SOIL,
        "warnings": "NEVER foliar spray during flower — moisture on buds = mold/botrytis risk. Apply before lights on (stomata open, UV won't degrade compounds). Do not apply in high humidity (>70%).",
    },
    {
        "slug": "malted-barley-top-dress",
        "name": "Malted Barley Grain (Enzyme Tea / Top Dress)",
        "category": "top_dress",
        "description": "Sprouted/malted barley is rich in enzymes that break down organic matter in soil, making nutrients immediately available. Contains chitinase (triggers plant immune response) and multiple growth enzymes. BuildASoil's #1 recommended biology activator.",
        "ingredients": [
            {
                "name": "Whole malted barley grain (2-row preferred)",
                "amount": "1/2",
                "unit": "cup per 5 gallons of soil (top dress) or 1/3 cup per gallon water (tea)",
                "notes": "Must be MALTED (sprouted and dried). Available at homebrew supply stores. Ground fresh is best.",
            },
        ],
        "instructions": "AS TOP DRESS: Grind malted barley in blender/coffee grinder. Sprinkle 1/2 cup per 5 gallons of soil on surface. Water in. Enzymes activate immediately on contact with moisture. AS TEA: Add 1/3 cup ground malted barley per gallon of water. Bubble with air pump for 6-8 hours (NOT 24h — you want enzymes, not microbes). Strain and apply as drench. Apply within hours of brewing.",
        "brew_time_hours": 8.0,
        "application_rate": "Top dress: 1/2 cup per 5-gallon container. Tea: 1/3 cup per gallon, apply full strength.",
        "frequency": "Every 1-2 weeks throughout entire grow cycle. Safe to use from seedling through flower.",
        "best_for_stages": ["seedling", "vegetative", "flowering"],
        "grow_type_slugs": ORGANIC_GROW_TYPES,
        "warnings": "Use MALTED barley only (not raw grain). Raw barley will sprout in your soil and compete with your plant. Ground fresh for maximum enzyme activity — pre-ground loses potency within weeks.",
    },
]
