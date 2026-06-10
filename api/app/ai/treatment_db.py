"""Structured plant health treatment database — cannabis-specific diagnoses.

Provides a comprehensive reference for:
- Nutrient deficiencies and toxicities (N, P, K, Ca, Mg, Fe, Mn, Zn, S, B, Cu, Mo)
- Pests (spider mites, fungus gnats, thrips, aphids, whiteflies, root aphids)
- Diseases (powdery mildew, botrytis, root rot, fusarium, pythium, septoria)
- Environmental stress (light burn, heat stress, overwatering, pH lockout)

Each entry includes: symptoms, identification tips, causes, treatments by grow type,
prevention strategies, and severity assessment criteria.
"""
# ruff: noqa: E501

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TreatmentEntry:
    """A single diagnosis entry in the treatment database."""

    id: str
    category: str  # "deficiency", "toxicity", "pest", "disease", "environmental"
    name: str
    aka: list[str]  # alternate names
    summary: str  # 1-2 sentence description
    symptoms: list[str]
    identification_tips: list[str]
    causes: list[str]
    severity_criteria: dict[str, str]  # low/medium/high/critical -> description
    treatments: dict[str, list[str]]  # grow_category -> treatment steps
    prevention: list[str]
    recovery_time: str  # e.g., "3-7 days", "1-2 weeks"
    commonly_confused_with: list[str]


# ═══════════════════════════════════════════════════════════════════════
# NUTRIENT DEFICIENCIES
# ═══════════════════════════════════════════════════════════════════════

NITROGEN_DEFICIENCY = TreatmentEntry(
    id="nitrogen_deficiency",
    category="deficiency",
    name="Nitrogen Deficiency",
    aka=["N deficiency", "nitrogen starvation"],
    summary="Nitrogen is essential for vegetative growth. Deficiency causes yellowing of lower/older leaves that progresses upward.",
    symptoms=[
        "Lower leaves turn pale green then yellow",
        "Yellowing progresses from bottom up",
        "Affected leaves eventually die and fall off",
        "Stunted growth, small leaves",
        "Light green overall plant color",
        "Thin, weak stems",
    ],
    identification_tips=[
        "Starts at the BOTTOM (older leaves) — this distinguishes from light burn (top)",
        "Uniform yellowing across entire leaf (not spotty)",
        "No brown spots (distinguishes from calcium or pH issues)",
        "Leaves stay soft (don't curl or crisp initially)",
    ],
    causes=[
        "Insufficient feeding / too-dilute nutrient solution",
        "Rootbound plant (can't uptake enough)",
        "Cold root zone slowing uptake",
        "pH lockout (below 5.5 or above 7.0)",
        "Over-watering reducing root oxygen",
        "Late flower natural fade (normal/expected)",
    ],
    severity_criteria={
        "low": "1-2 lower leaves yellowing, plant still growing well",
        "medium": "Multiple lower leaves affected, growth slowing",
        "high": "Yellowing reaching middle of plant, significant leaf loss",
        "critical": "Entire plant pale, severe stunting, upper leaves affected",
    },
    treatments={
        "hydroponic": [
            "Increase base nutrient EC by 0.2-0.4",
            "Verify pH is 5.5-6.5 for proper N uptake",
            "Check reservoir temperature (66-68°F ideal, above 70°F = caution)",
            "Consider foliar spray with 1/4 strength veg nutrients as fast fix",
        ],
        "coco": [
            "Increase feed EC by 0.2-0.4",
            "Ensure 10-20% runoff to prevent salt lockout",
            "Verify pH 5.8-6.3",
            "Feed every watering (coco is inert, doesn't store N)",
        ],
        "soil": [
            "Top dress with blood meal, bat guano, or compost",
            "Water with dilute liquid fish fertilizer or kelp",
            "Check pH of soil (6.0-7.0 target)",
            "If in pot: may be rootbound, consider transplant",
        ],
        "living_soil": [
            "Apply compost tea (high-nitrogen: worm castings + kelp)",
            "Top dress with alfalfa meal or blood meal",
            "Check mulch layer — bare soil loses biology",
            "DO NOT add synthetic nitrogen — it kills soil biology",
        ],
    },
    prevention=[
        "Monitor EC/PPM regularly and increase through veg",
        "Don't let plants get rootbound",
        "Maintain proper pH for medium type",
        "In flower, some lower leaf yellowing is natural — don't panic",
    ],
    recovery_time="3-7 days for new growth to green up; damaged leaves won't recover",
    commonly_confused_with=["Sulfur deficiency (also yellow but starts newer leaves)", "Light stress", "Overwatering"],
)

PHOSPHORUS_DEFICIENCY = TreatmentEntry(
    id="phosphorus_deficiency",
    category="deficiency",
    name="Phosphorus Deficiency",
    aka=["P deficiency", "phosphorus starvation"],
    summary="Phosphorus is critical for root development, flowering, and energy transfer. Deficiency causes dark leaves with purple stems.",
    symptoms=[
        "Dark green to blue-green leaves",
        "Purple/red stems and petioles",
        "Lower leaves develop dark spots then die",
        "Slow growth, especially roots",
        "Delayed flowering onset",
        "Small, sparse buds in flower",
    ],
    identification_tips=[
        "Purple STEMS are the hallmark (not just cold-induced purple)",
        "Leaves get darker before dying (opposite of N def which gets lighter)",
        "Affects lower/older leaves first",
        "Dark necrotic patches (not brown-orange like Ca)",
    ],
    causes=[
        "Cold root zone (below 60°F locks out P)",
        "pH too high (above 7.0) or too low (below 5.5)",
        "Insufficient P in nutrient mix",
        "Overwatering compacting roots",
        "LED grows run cooler — root zone temp often overlooked",
    ],
    severity_criteria={
        "low": "Purple stems but leaves still green, growth normal",
        "medium": "Dark leaves, slow growth, obvious purple throughout",
        "high": "Leaf necrosis starting, flowering significantly delayed",
        "critical": "Severe necrosis, stunted buds, plant declining",
    },
    treatments={
        "hydroponic": [
            "Increase bloom nutrients (higher P-K ratio)",
            "Check pH is 5.5-6.5 (P locks out above 7)",
            "Warm reservoir if below 65°F",
            "Add mono potassium phosphate (MKP) as supplement",
        ],
        "coco": [
            "Increase bloom feed, ensure runoff EC isn't too low",
            "Check pH 5.8-6.3",
            "Warm root zone if cold (heat mat under pots)",
            "Flush then re-feed if salt buildup suspected",
        ],
        "soil": [
            "Add bone meal or bat guano (high P)",
            "Check soil pH — acidify if above 7.0",
            "Warm the root zone if cold outdoor nights",
            "Mycorrhizal inoculant helps P uptake dramatically",
        ],
        "living_soil": [
            "Top dress bone meal or rock phosphate",
            "Apply mycorrhizal fungi at root zone",
            "Ensure soil temp above 60°F",
            "Compost tea with high-phosphorus inputs (bone meal, guano)",
        ],
    },
    prevention=[
        "Use bloom-specific nutrients in flower",
        "Keep root zone above 62°F",
        "Maintain pH in proper range for medium",
        "Inoculate with mycorrhizae at transplant",
    ],
    recovery_time="1-2 weeks; purple stems may remain but new growth improves",
    commonly_confused_with=["Genetic purple stems (strain-specific)", "Cold stress", "Magnesium deficiency"],
)

POTASSIUM_DEFICIENCY = TreatmentEntry(
    id="potassium_deficiency",
    category="deficiency",
    name="Potassium Deficiency",
    aka=["K deficiency", "potash deficiency"],
    summary="Potassium regulates water, enzyme activation, and photosynthesis. Deficiency causes brown leaf edges and weak stems.",
    symptoms=[
        "Brown, crispy leaf edges (leaf margin burn)",
        "Yellowing between veins on older leaves",
        "Weak, hollow stems that break easily",
        "Slow growth and stretching",
        "Curling leaf tips (burnt look)",
        "Reduced bud density in flower",
    ],
    identification_tips=[
        "Brown EDGES specifically (not spots in middle = Ca, not tip = N burn)",
        "Starts on older/lower leaves first",
        "Stems feel hollow or weak when squeezed",
        "Often appears in heavy flower (high K demand)",
    ],
    causes=[
        "Insufficient K in feed (common in late flower)",
        "Excess calcium or magnesium blocking K uptake",
        "pH lockout (K locks out below 5.0 and above 7.5)",
        "High sodium in water competing with K",
        "Under-feeding during flower stretch",
    ],
    severity_criteria={
        "low": "Minor leaf edge browning on 1-2 old leaves",
        "medium": "Multiple leaves affected, growth slowing",
        "high": "Widespread leaf margin burn, stems weak",
        "critical": "Severe necrosis, buds not fattening, structure failing",
    },
    treatments={
        "hydroponic": [
            "Increase bloom nutrients or add potassium sulfate",
            "Check Ca:Mg:K ratio isn't K-deficient",
            "Verify pH 5.5-6.5",
            "Reduce calcium supplement if excessive",
        ],
        "coco": [
            "Increase bloom feed concentration",
            "Add potassium sulfate or seaweed extract",
            "Check pH and runoff — flush if EC very high",
            "Coco binds K — always feed more than soil",
        ],
        "soil": [
            "Add kelp meal, wood ash, or potassium sulfate",
            "Banana peel tea (organic option)",
            "Check pH — acidify if too alkaline",
            "Avoid excess lime (Ca competes with K)",
        ],
        "living_soil": [
            "Top dress kelp meal or langbeinite",
            "Compost tea with kelp and seaweed",
            "Wood ash (use sparingly — raises pH)",
            "Ensure diverse mineral amendments in soil recipe",
        ],
    },
    prevention=[
        "Use bloom nutrients with adequate K in flower",
        "Monitor Ca:Mg:K ratios",
        "Don't over-supplement calcium/magnesium",
        "Increase feed as flower progresses (demand rises)",
    ],
    recovery_time="5-10 days for new growth; burnt edges don't recover",
    commonly_confused_with=[
        "Nutrient burn (tip burn vs edge burn)",
        "Calcium deficiency (spots vs edges)",
        "Heat stress",
    ],
)

CALCIUM_DEFICIENCY = TreatmentEntry(
    id="calcium_deficiency",
    category="deficiency",
    name="Calcium Deficiency",
    aka=["Ca deficiency", "cal-mag issue"],
    summary="Calcium is immobile — once symptoms appear on new growth, the problem is already established. Causes brown spots and distorted new leaves.",
    symptoms=[
        "Brown/tan spots on newer/upper leaves",
        "Distorted, crinkled new growth",
        "Leaf tips hook downward",
        "Hollow stems (similar to K)",
        "Bud sites develop brown edges",
        "Root tips die back (in hydro)",
    ],
    identification_tips=[
        "Affects NEWER growth (immobile nutrient) — KEY differentiator",
        "Spots are irregular tan/brown (not uniform yellow like N)",
        "New leaves crinkle or curl (not smooth yellowing)",
        "In DWC, root tips turn brown before leaf symptoms",
    ],
    causes=[
        "Using RO/distilled water without cal-mag supplement",
        "LED grows increase Ca demand (less radiant heat)",
        "pH too low (below 5.5) locks out calcium",
        "Excess potassium or magnesium blocking Ca",
        "Humidity too high reducing transpiration (Ca moves via transpiration)",
    ],
    severity_criteria={
        "low": "Few spots on new leaves, growth rate normal",
        "medium": "Multiple new leaves spotty, some distortion",
        "high": "Severe new growth distortion, spreading fast",
        "critical": "Growing tips dying, bud sites browning",
    },
    treatments={
        "hydroponic": [
            "Add cal-mag supplement (3-5 mL/gal)",
            "If using RO water, always add cal-mag first",
            "Check pH 5.8-6.5 for optimal Ca uptake",
            "Lower humidity to increase transpiration",
        ],
        "coco": [
            "Cal-mag is MANDATORY in coco (cation exchange steals Ca)",
            "Add 3-5 mL/gal cal-mag every watering",
            "Ensure pH 5.8-6.3",
            "Coco: feed cal-mag first, then base nutrients, then pH",
        ],
        "soil": [
            "Add dolomite lime (slow release Ca + Mg)",
            "Gypsum for Ca without raising pH",
            "Liquid cal-mag as fast-acting supplement",
            "Ensure pH 6.2-7.0",
        ],
        "living_soil": [
            "Amend with gypsum or oyster shell flour",
            "Glacial rock dust provides Ca + trace minerals",
            "Ensure soil pH isn't too low (add lime if <6.0)",
            "Avoid over-watering (reduces transpiration-driven Ca uptake)",
        ],
    },
    prevention=[
        "Always use cal-mag with RO/distilled water",
        "Coco growers: cal-mag every single feed",
        "Maintain proper pH for medium",
        "Don't let humidity stay above 70% in veg",
    ],
    recovery_time="5-10 days; existing spots won't heal but new growth normalizes",
    commonly_confused_with=["pH fluctuation damage", "Manganese deficiency", "Septoria leaf spot"],
)

MAGNESIUM_DEFICIENCY = TreatmentEntry(
    id="magnesium_deficiency",
    category="deficiency",
    name="Magnesium Deficiency",
    aka=["Mg deficiency", "interveinal chlorosis"],
    summary="Magnesium is the center atom of chlorophyll. Deficiency causes yellowing between leaf veins while veins stay green (interveinal chlorosis).",
    symptoms=[
        "Yellowing between veins (veins stay green) on older leaves",
        "Lower leaves affected first (mobile nutrient)",
        "Leaves may curl upward",
        "Purple or red coloring on undersides",
        "Eventually full leaf yellowing and necrosis",
    ],
    identification_tips=[
        "INTERVEINAL chlorosis is the key — yellow between GREEN veins",
        "Starts on LOWER leaves (Mg is mobile, moves to new growth)",
        "Distinguished from Fe def: Fe affects NEW growth, Mg affects OLD",
        "Check leaf undersides for purple/red hue",
    ],
    causes=[
        "Cal-mag supplement needed (especially coco/RO)",
        "pH lockout below 5.8",
        "Excess potassium competing with Mg uptake",
        "Cold root zone reducing uptake",
        "Overwatering / root problems",
    ],
    severity_criteria={
        "low": "Mild interveinal yellowing on 1-2 old leaves",
        "medium": "Multiple leaves showing pattern, spreading upward",
        "high": "Widespread chlorosis, leaves browning",
        "critical": "Severe deficiency affecting canopy, leaf die-off",
    },
    treatments={
        "hydroponic": [
            "Add cal-mag (2-4 mL/gal)",
            "Epsom salt foliar spray (1 tsp/quart) for fast relief",
            "Check pH 5.8-6.5",
            "Reduce K if excessively high",
        ],
        "coco": [
            "Increase cal-mag to 3-5 mL/gal",
            "Foliar spray Epsom salt for immediate relief",
            "Flush then re-feed at proper ratios",
            "pH 5.8-6.3",
        ],
        "soil": [
            "Epsom salt drench (1 tbsp/gal)",
            "Dolomite lime (provides Ca + Mg, raises pH)",
            "Liquid cal-mag supplement",
            "pH should be 6.0-7.0",
        ],
        "living_soil": [
            "Top dress dolomite or langbeinite",
            "Epsom salt foliar spray as fast fix",
            "Compost tea with kelp (trace minerals)",
            "Ensure soil recipe has adequate Mg source",
        ],
    },
    prevention=[
        "Use cal-mag with RO/soft water",
        "Maintain proper pH",
        "Don't over-dose potassium in bloom",
        "Monitor interveinal yellowing early",
    ],
    recovery_time="3-7 days after foliar spray; 7-14 days via root feeding",
    commonly_confused_with=["Iron deficiency (new growth vs old)", "Zinc deficiency", "Early nitrogen deficiency"],
)

IRON_DEFICIENCY = TreatmentEntry(
    id="iron_deficiency",
    category="deficiency",
    name="Iron Deficiency",
    aka=["Fe deficiency", "iron chlorosis"],
    summary="Iron is immobile — deficiency shows as yellowing of newest leaves with bright green veins. Often pH-related.",
    symptoms=[
        "Bright yellow/white NEW growth with green veins",
        "Upper/newest leaves affected (immobile)",
        "Leaves may appear almost white in severe cases",
        "Overall pale, bleached top canopy",
        "Interveinal chlorosis on young leaves",
    ],
    identification_tips=[
        "NEW growth affected — key differentiator from Mg (old growth)",
        "Very bright/pale yellow — almost white in severe cases",
        "Veins stay distinctly green (sharper contrast than Mg)",
        "pH above 6.5-7.0 is the #1 cause (pH lockout, not actual deficiency)",
    ],
    causes=[
        "pH too HIGH (above 6.5 in hydro, above 7.0 in soil)",
        "Excess calcium or phosphorus competing",
        "Overwatering reducing root oxygen (Fe needs O2 for uptake)",
        "Cold root zone",
    ],
    severity_criteria={
        "low": "Slight yellowing on newest leaves, veins still green",
        "medium": "New growth distinctly yellow, growth slowing",
        "high": "New leaves near-white, severe stunting",
        "critical": "Growing tips dying, no new healthy growth",
    },
    treatments={
        "hydroponic": [
            "FIRST: Check pH — almost always too high. Lower to 5.5-6.0",
            "Add chelated iron (Fe-DTPA for hydro)",
            "Reduce calcium if excessive",
            "Ensure adequate dissolved oxygen (air stones)",
        ],
        "coco": [
            "Lower pH to 5.8-6.0",
            "Flush with pH'd water, then re-feed",
            "Add chelated iron supplement",
            "Ensure proper drainage (waterlogged coco locks out Fe)",
        ],
        "soil": [
            "Lower pH if above 7.0 (sulfur amendment, acidic fertilizer)",
            "Chelated iron foliar spray for fast fix",
            "Improve drainage if overwatering",
            "Avoid excess lime or alkaline amendments",
        ],
        "living_soil": [
            "Check soil pH — add sulfur if too alkaline",
            "Compost tea with kelp and humic acid",
            "Ensure good aeration (don't compact soil)",
            "Mycorrhizae help Fe uptake dramatically",
        ],
    },
    prevention=[
        "Maintain pH below 6.5 (hydro) or 7.0 (soil)",
        "Don't over-lime soil",
        "Ensure adequate drainage and aeration",
        "Use chelated iron in nutrient mix",
    ],
    recovery_time="5-7 days once pH is corrected; existing yellow leaves won't fully recover",
    commonly_confused_with=["Magnesium deficiency (old vs new)", "Sulfur deficiency", "Light burn (bleaching)"],
)

# ═══════════════════════════════════════════════════════════════════════
# PESTS
# ═══════════════════════════════════════════════════════════════════════

SPIDER_MITES = TreatmentEntry(
    id="spider_mites",
    category="pest",
    name="Spider Mites",
    aka=["Two-spotted spider mite", "red spider mite"],
    summary="Microscopic sap-sucking arachnids that create tiny yellow dots (stippling) on leaves and spin fine webbing in severe cases.",
    symptoms=[
        "Tiny yellow/white dots (stippling) on leaf tops",
        "Fine webbing on undersides of leaves (advanced)",
        "Leaves turn yellow/bronze and dry out",
        "Tiny moving dots visible with magnification on leaf undersides",
        "Plants lose vigor, growth slows",
        "In severe cases, webbing covers entire buds",
    ],
    identification_tips=[
        "Use a loupe (60x) — look at UNDERSIDE of affected leaves",
        "Stippling pattern is distinctive: tiny random dots across leaf surface",
        "Webbing = advanced infestation (they breed exponentially)",
        "Shake leaf over white paper — see tiny dots moving",
        "They LOVE dry, warm environments (low humidity = higher risk)",
    ],
    causes=[
        "Brought in on clones, clothes, pets, outdoor shoes",
        "Low humidity (below 40%) accelerates reproduction",
        "Hot temperatures speed lifecycle",
        "Reusing contaminated soil/media",
        "Adjacent infested plants",
    ],
    severity_criteria={
        "low": "Few stipple marks on 1-2 leaves, mites found with loupe",
        "medium": "Multiple leaves affected, mites visible without loupe",
        "high": "Webbing present, multiple leaves browning",
        "critical": "Webbing on buds, leaves dying en masse, mites everywhere",
    },
    treatments={
        "hydroponic": [
            "Raise humidity to 60%+ (slows reproduction)",
            "Apply insecticidal soap or neem oil (lights off)",
            "Introduce predatory mites (Phytoseiulus persimilis)",
            "Spray every 3 days for 2 weeks (lifecycle disruption)",
            "Remove heavily infested leaves",
            "In flower: Beauveria bassiana or Spinosad (safer for buds)",
        ],
        "coco": [
            "Same as hydroponic treatments",
            "Drench with SNS-209 or similar systemic (veg only)",
            "Top-dress with diatomaceous earth",
            "Maintain 50-60% RH to slow reproduction",
        ],
        "soil": [
            "Neem oil drench + foliar spray",
            "Introduce predatory mites",
            "Diatomaceous earth on soil surface",
            "Insecticidal soap spray every 3 days",
            "Remove worst leaves, isolate plant if possible",
        ],
        "living_soil": [
            "Predatory mites (Persimilis, Californicus, Andersoni)",
            "Neem oil foliar spray (won't harm soil biology)",
            "Increase humidity and diversity of insects",
            "AVOID synthetic miticides (kill soil life)",
            "Companion plant with chrysanthemums (natural pyrethrin)",
        ],
    },
    prevention=[
        "Keep humidity above 50% in veg",
        "Inspect clones with a loupe before introducing",
        "Change clothes after visiting other grows",
        "Preventive predatory mite sachets (Californicus)",
        "Weekly leaf inspections with magnification",
    ],
    recovery_time="2-4 weeks of consistent treatment to eliminate; population doubles every 3-5 days if untreated",
    commonly_confused_with=["Thrips damage (silvery vs stippled)", "Calcium deficiency (spots vs stippling)"],
)

FUNGUS_GNATS = TreatmentEntry(
    id="fungus_gnats",
    category="pest",
    name="Fungus Gnats",
    aka=["Sciaridae", "soil gnats", "dark-winged fungus gnats"],
    summary="Small black flies whose larvae feed on roots and organic matter in wet soil. Adults are harmless but larvae damage roots.",
    symptoms=[
        "Small black flies hovering around soil surface",
        "Larvae (tiny white worms) visible in top inch of soil",
        "Slow growth / wilting despite adequate watering",
        "Yellow sticky traps catching many small flies",
        "Seedlings or clones dying suddenly (root damage)",
    ],
    identification_tips=[
        "Adults are small (2-3mm), black, weak flyers near soil",
        "Larvae are white/translucent, 5mm, in top 2 inches of soil",
        "They love WET conditions — overwatering is the root cause",
        "Yellow sticky traps near soil surface confirm population",
        "Disturb soil surface and watch for adults flying up",
    ],
    causes=[
        "Overwatering (wet soil surface = breeding ground)",
        "Poor drainage",
        "Organic matter in soil attracting females",
        "Contaminated soil/compost",
        "Stagnant water in saucers",
    ],
    severity_criteria={
        "low": "Few adults seen, plants healthy",
        "medium": "Noticeable population, some growth slowdown",
        "high": "Large population, seedlings affected, root damage visible",
        "critical": "Massive infestation, plants wilting, seedlings dying",
    },
    treatments={
        "hydroponic": [
            "N/A — fungus gnats are a soil/media problem",
            "If in hydroton/rockwool: let surface dry between feeds",
            "Yellow sticky traps to catch adults",
        ],
        "coco": [
            "Let top inch of coco dry between waterings",
            "Top-dress with sand or diatomaceous earth (physical barrier)",
            "BTi (Mosquito Bits/Dunks) in water — kills larvae",
            "Yellow sticky traps for adults",
            "Hydrogen peroxide drench (1:4 H2O2:water) kills larvae on contact",
        ],
        "soil": [
            "STOP overwatering — let top 2 inches dry",
            "BTi (Mosquito Bits) — the gold standard for larvae",
            "Diatomaceous earth on soil surface",
            "Yellow sticky traps everywhere",
            "Bottom-water only to keep surface dry",
            "Neem oil drench for soil-dwelling larvae",
        ],
        "living_soil": [
            "BTi is safe for soil biology (targets only gnat larvae)",
            "Sand or perlite top-dress as physical barrier",
            "Predatory nematodes (Steinernema feltiae)",
            "Rove beetles (natural gnat predators)",
            "Ensure mulch isn't staying too wet",
            "DO NOT use hydrogen peroxide (kills beneficial microbes)",
        ],
    },
    prevention=[
        "Don't overwater — #1 prevention",
        "Allow soil surface to dry between waterings",
        "Use well-draining media",
        "Preventive BTi in water monthly",
        "Cover soil surface with mulch, sand, or perlite",
    ],
    recovery_time="1-2 weeks with BTi; lifecycle is 3 weeks so full elimination takes one generation",
    commonly_confused_with=["Shore flies (stouter, stronger flyers)", "Drain flies (larger, fuzzy wings)"],
)

THRIPS = TreatmentEntry(
    id="thrips",
    category="pest",
    name="Thrips",
    aka=["Western flower thrips", "cannabis thrips", "thunder flies"],
    summary="Tiny elongated insects that rasp leaf cells and suck sap, leaving silvery/bronze trails and black fecal dots.",
    symptoms=[
        "Silvery/bronze streaks or patches on leaves",
        "Tiny black dots (frass/feces) on leaf surface",
        "Distorted new growth (thrips love growing tips)",
        "Flower damage — brown/dead patches on buds",
        "Tiny elongated insects (1-2mm) visible — pale yellow to brown",
    ],
    identification_tips=[
        "Silvery RASPING damage is distinctive (not dots like mites)",
        "Look for tiny black pepper-like fecal spots on leaves",
        "Blow on the plant — thrips move when disturbed",
        "Blue/yellow sticky traps catch adults",
        "They hide in crevices, leaf folds, and inside buds",
    ],
    causes=[
        "Carried in by wind, on clones, or on clothing",
        "Outdoor grows heavily exposed",
        "Can overwinter in soil as pupae",
        "Thrive in warm, dry conditions",
    ],
    severity_criteria={
        "low": "Minor silvery marks on a few leaves",
        "medium": "Widespread leaf damage, thrips easily found",
        "high": "New growth distorted, buds affected",
        "critical": "Severe damage, viral transmission possible (TSWV)",
    },
    treatments={
        "hydroponic": [
            "Spinosad (organic, effective, safe in veg — avoid in late flower)",
            "Predatory mites: Amblyseius cucumeris or swirskii",
            "Blue sticky traps (thrips attracted to blue > yellow)",
            "Spray every 3-4 days for 2+ weeks",
            "In flower: Beauveria bassiana",
        ],
        "coco": [
            "Spinosad drench + foliar (kills larvae in media too)",
            "Predatory mites on plant surfaces",
            "Let media surface dry (pupae in soil)",
            "Insecticidal soap between Spinosad applications",
        ],
        "soil": [
            "Spinosad soil drench + foliar spray",
            "Diatomaceous earth on soil (pupae stage in soil)",
            "Predatory mites (Cucumeris sachets)",
            "Neem oil as preventive",
            "Remove heavily damaged leaves",
        ],
        "living_soil": [
            "Predatory mites (Cucumeris, Swirskii) — biological control",
            "Spinosad is safe for soil biology",
            "Neem oil foliar spray",
            "Encourage rove beetles and minute pirate bugs",
            "Mulch helps trap pupae (predators find them)",
        ],
    },
    prevention=[
        "Blue sticky traps for early detection",
        "Inspect clones thoroughly before introducing",
        "Preventive predatory mite sachets",
        "Maintain cleanliness — remove dead plant material",
        "Screen intake vents in indoor grows",
    ],
    recovery_time="2-3 weeks of consistent treatment; pupae in soil take 1 week to emerge",
    commonly_confused_with=["Spider mite stippling (dots vs streaks)", "Wind damage", "Calcium deficiency spots"],
)

# ═══════════════════════════════════════════════════════════════════════
# DISEASES
# ═══════════════════════════════════════════════════════════════════════

POWDERY_MILDEW = TreatmentEntry(
    id="powdery_mildew",
    category="disease",
    name="Powdery Mildew (PM)",
    aka=["WPM", "white powdery mildew", "Golovinomyces cichoracearum"],
    summary="White powdery fungal coating on leaf surfaces. Thrives in stagnant air with temperature swings. Can devastate entire crops.",
    symptoms=[
        "White/gray powdery patches on leaf surfaces",
        "Starts as small circular spots, spreads to cover leaves",
        "Can appear on stems and buds",
        "Leaves yellow and die under heavy coating",
        "Reduced photosynthesis, stunted growth",
    ],
    identification_tips=[
        "Rub suspect area — PM wipes off like powder (trichomes don't)",
        "Starts on upper leaf surfaces (unlike most fungi that prefer undersides)",
        "Thrives at 68-77°F with 50-65% humidity AND poor airflow",
        "Check shaded lower canopy first — often starts there",
        "UV light can reveal PM before visible to naked eye",
    ],
    causes=[
        "Stagnant air / poor circulation (THE #1 cause)",
        "Large day/night temperature swing causing dew point condensation",
        "Overcrowded canopy preventing airflow",
        "Genetics — some strains highly susceptible",
        "Spores carried in air, on clothes, from outdoor plants",
    ],
    severity_criteria={
        "low": "Few small spots on 1-2 leaves",
        "medium": "Multiple leaves affected, spreading",
        "high": "Large patches, reaching stems or sugar leaves",
        "critical": "On buds — HARVEST RISK. Entire crop at stake.",
    },
    treatments={
        "hydroponic": [
            "Improve airflow IMMEDIATELY (oscillating fans, defoliate)",
            "Potassium bicarbonate spray (1 tbsp/gal + wetting agent)",
            "Remove affected leaves and dispose outside grow",
            "Lower humidity below 50% during lights off",
            "Increase plant spacing",
            "In veg: neem oil, Lost Coast Plant Therapy, or JMS Stylet Oil",
            "In flower: Dr. Zymes or Regalia (safe on buds)",
        ],
        "coco": [
            "Same foliar treatments as hydroponic",
            "Ensure grow space has adequate fans",
            "Defoliate to improve airflow through canopy",
        ],
        "soil": [
            "Potassium bicarbonate or baking soda spray",
            "Improve air circulation",
            "Reduce watering (lower ambient humidity)",
            "Sulfur burner (veg only, never in flower)",
            "UV-C supplemental lighting",
        ],
        "living_soil": [
            "Compost tea (competitive microbes outcompete PM)",
            "Potassium bicarbonate spray (won't harm biology)",
            "Improve airflow, thin canopy",
            "Bacillus subtilis (Serenade) — biological fungicide",
            "AVOID synthetic fungicides",
        ],
    },
    prevention=[
        "Strong oscillating fans creating constant leaf flutter",
        "Don't let humidity spike above 60% during lights off",
        "Defoliate for airflow (especially lower canopy)",
        "Preventive potassium bicarbonate sprays weekly in veg",
        "UVC supplemental lighting destroys spores",
        "Keep day/night temp swing under 15°F",
    ],
    recovery_time="Ongoing management; can't 'cure' — only suppress. Infected plants remain carriers.",
    commonly_confused_with=["Trichomes (don't wipe off, on buds specifically)", "Mineral residue from foliar spray"],
)

BOTRYTIS = TreatmentEntry(
    id="botrytis",
    category="disease",
    name="Botrytis (Bud Rot)",
    aka=["Bud rot", "gray mold", "Botrytis cinerea"],
    summary="Devastating fungal infection that rots buds from the inside out. By the time you see it externally, the inside is already destroyed.",
    symptoms=[
        "Gray/brown mushy area inside or on top of a cola",
        "Random yellow/brown/dying sugar leaves on a single bud",
        "Gray fuzzy mold visible when bud is pulled apart",
        "Buds feel wet or mushy when squeezed",
        "Distinctive musty/damp smell",
        "Dark brown/black interior when bud is broken open",
    ],
    identification_tips=[
        "If ONE sugar leaf on a bud randomly yellows/browns — SUSPECT BUD ROT",
        "Gently pull the suspect bud apart — gray mold inside confirms",
        "Usually starts in fattest/densest colas (trapped moisture)",
        "More common in late flower when buds are dense",
        "Appears after rain or humidity spikes above 60%",
    ],
    causes=[
        "High humidity (above 60%) during late flower",
        "Dense buds trapping moisture (genetics-related)",
        "Poor airflow through and around colas",
        "Rain or condensation on buds",
        "Caterpillar damage creating entry points",
        "Temperature drops causing condensation",
    ],
    severity_criteria={
        "low": "One small spot on one bud, caught early",
        "medium": "Multiple bud sites affected",
        "high": "Spreading rapidly, multiple colas compromised",
        "critical": "Widespread — consider emergency harvest of unaffected areas",
    },
    treatments={
        "hydroponic": [
            "CUT IT OUT — remove entire affected cola + 2 inches below visible rot",
            "Sterilize scissors between cuts (isopropyl alcohol)",
            "Lower humidity below 50% immediately",
            "Increase airflow through canopy aggressively",
            "Defoliate around remaining buds for airflow",
            "Consider early harvest if widespread",
            "DO NOT try to save affected buds — spores spread",
        ],
        "coco": ["Same as hydroponic — cut, dehumidify, airflow"],
        "soil": ["Same protocol — surgical removal, environmental control"],
        "living_soil": [
            "Remove affected material — no cure for active bud rot",
            "Bacillus subtilis spray on remaining buds (preventive only)",
            "Improve airflow, shake buds after rain/dew",
            "Consider early harvest if environment can't be controlled",
        ],
    },
    prevention=[
        "Keep flower room below 50% humidity after week 5",
        "Strong airflow through and around buds",
        "Defoliate in flower for air penetration",
        "Outdoor: shake plants after rain to remove droplets",
        "Check dense colas regularly by feel (soft = suspect)",
        "Caterpillar control (their damage is an entry point)",
        "Consider strains with airier bud structure for humid climates",
    ],
    recovery_time="No recovery — affected buds are lost. Focus on saving the rest.",
    commonly_confused_with=["Nutrient burn on sugar leaves", "Heat stress browning", "Normal senescence at harvest"],
)

ROOT_ROT = TreatmentEntry(
    id="root_rot",
    category="disease",
    name="Root Rot",
    aka=["Pythium", "Phytophthora", "brown root rot"],
    summary="Waterborne pathogen that destroys roots. In hydro, roots turn brown and slimy. In soil, roots become mushy and foul-smelling.",
    symptoms=[
        "Brown, slimy roots (hydro — should be white)",
        "Foul smell from root zone",
        "Wilting despite adequate moisture (roots can't uptake)",
        "Yellowing leaves across entire plant",
        "Slow/stopped growth",
        "In soil: stem base turns soft/brown (damping off)",
    ],
    identification_tips=[
        "Healthy roots = white/cream, firm. Root rot = brown, slimy, smelly",
        "Plant wilts even when well-watered (because roots are dead)",
        "In DWC: lift lid and check root color and smell",
        "Brown stain from nutrients ≠ root rot (healthy stained roots are still firm)",
        "Sour/anaerobic smell is the clearest confirmation",
    ],
    causes=[
        "Water temperature too HIGH (above 72°F / 22°C in hydro)",
        "Insufficient dissolved oxygen (too few air stones)",
        "Stagnant nutrient solution",
        "Light reaching root zone (algae → rot)",
        "In soil: chronic overwatering with poor drainage",
    ],
    severity_criteria={
        "low": "Few root tips brown, most still white, no smell",
        "medium": "Significant browning, slight smell, plant still growing",
        "high": "Mostly brown, slimy, foul smell, plant wilting",
        "critical": "All roots dead, plant near death",
    },
    treatments={
        "hydroponic": [
            "Lower water temp to 65-68°F (chiller or frozen water bottles)",
            "Add Hydroguard (Bacillus amyloliquefaciens) — competes with pathogens",
            "Increase aeration (more/larger air stones)",
            "Remove dead root mass (trim brown slimy roots with sterile scissors)",
            "H2O2 (3%) 3mL/gal as one-time nuclear option (kills everything)",
            "Then re-inoculate with beneficial bacteria (Hydroguard, Great White)",
            "Block ALL light from reservoir",
        ],
        "coco": [
            "Let coco dry more between waterings",
            "Add Hydroguard to nutrient solution",
            "Improve drainage (elevate pots, increase perlite ratio)",
            "Reduce watering frequency until roots recover",
        ],
        "soil": [
            "STOP watering until soil is dry 2 inches down",
            "Improve drainage (add perlite, elevate pot)",
            "Hydrogen peroxide drench (3%) once to kill anaerobic pathogens",
            "Then re-inoculate with mycorrhizae/beneficial bacteria",
            "Ensure pot has drainage holes",
        ],
        "living_soil": [
            "Improve drainage and reduce watering immediately",
            "Add compost tea (beneficial microbes compete with pathogens)",
            "Top dress with worm castings (biocontrol)",
            "Ensure cover crop / mulch isn't holding too much moisture at base",
            "DO NOT use hydrogen peroxide (kills beneficial soil life)",
        ],
    },
    prevention=[
        "Hydro: keep water below 70°F (water chiller)",
        "Hydro: adequate aeration (air pump rated 2x reservoir size)",
        "Block light from root zone / reservoir",
        "Don't overwater soil/coco",
        "Use beneficial bacteria preventively (Hydroguard weekly)",
        "Ensure proper pot drainage",
    ],
    recovery_time="1-3 weeks if caught early; severe cases may not recover",
    commonly_confused_with=["Nutrient stain on roots (firm = healthy)", "Overwatering symptoms (similar wilt)"],
)

# ═══════════════════════════════════════════════════════════════════════
# ENVIRONMENTAL STRESS
# ═══════════════════════════════════════════════════════════════════════

LIGHT_BURN = TreatmentEntry(
    id="light_burn",
    category="environmental",
    name="Light Burn / Light Stress",
    aka=["Light bleaching", "LED burn", "too much light"],
    summary="Excess light intensity bleaches top leaves white/yellow. Common with powerful LEDs at close distance.",
    symptoms=[
        "Top/closest leaves turn yellow or white (bleaching)",
        "Yellowing starts at the top and works DOWN (opposite of N def)",
        "Leaves don't look unhealthy otherwise — just pale/bleached",
        "Taco-ing (upward leaf curl) from heat/light combo",
        "Buds can bleach white and lose potency",
    ],
    identification_tips=[
        "ONLY affects top canopy closest to light",
        "Lower leaves remain green and healthy",
        "Distinguished from N def: light burn = top down, N def = bottom up",
        "May have taco-ing (leaves folding up like a taco)",
        "Check DLI/PPFD — above 1000 PPFD causes issues for most strains",
    ],
    causes=[
        "Light too close to canopy",
        "Light too powerful for the space (overpowered LED)",
        "Dimmer not used / set too high",
        "After defoliation: remaining leaves get more light",
        "Reflective walls concentrating light on certain spots",
    ],
    severity_criteria={
        "low": "Slight bleaching on a few top leaves",
        "medium": "Multiple top leaves affected, visible yellowing",
        "high": "Canopy significantly bleached, buds whitening",
        "critical": "Large sections bleached, bud potency compromised",
    },
    treatments={
        "hydroponic": [
            "Raise light 4-6 inches",
            "Dim light by 10-20%",
            "Supercrop tall colas to move them away from light",
            "Add another fan to cool canopy surface",
            "Bleached leaves won't recover — focus on prevention",
        ],
        "coco": ["Same as hydroponic"],
        "soil": ["Same as hydroponic"],
        "living_soil": ["Same — raise light, dim, or train plants lower"],
    },
    prevention=[
        "Use a PAR/PPFD meter to verify light levels (600-900 PPFD for flower)",
        "Follow manufacturer height recommendations",
        "Train/top plants to maintain even canopy",
        "Increase distance after defoliation",
        "Dim lights during early flower stretch (plants grow into light)",
    ],
    recovery_time="New growth normalizes in 3-5 days; bleached tissue doesn't recover",
    commonly_confused_with=["Nitrogen deficiency (bottom vs top)", "pH lockout", "Heat stress (curling + drooping)"],
)

HEAT_STRESS = TreatmentEntry(
    id="heat_stress",
    category="environmental",
    name="Heat Stress",
    aka=["High temperature stress", "heat damage"],
    summary="Temperatures above 85°F (30°C) cause leaf curling, foxtailing in flower, and increased vulnerability to other issues.",
    symptoms=[
        "Leaves curl upward (taco-ing / canoeing)",
        "Leaf edges curl up and get crispy",
        "Foxtailing: buds growing tall spires instead of fattening",
        "Increased stretching between nodes",
        "Wilting despite adequate water",
        "Bleaching at top combined with curling",
    ],
    identification_tips=[
        "Taco-ing: leaves fold upward along the midrib like a taco",
        "Affects TOP of plant (closest to light/heat source)",
        "Foxtailing in flower is a telltale sign of chronic heat",
        "Combined with light burn symptoms in LED grows",
        "Feel the canopy — if it's hot on your hand, it's hot for the plant",
    ],
    causes=[
        "Ambient temperature above 85°F / 30°C",
        "Light producing excess radiant heat",
        "Inadequate exhaust / air exchange",
        "AC failure",
        "Heat from ballasts/drivers in grow space",
    ],
    severity_criteria={
        "low": "Mild taco-ing during hottest hours, recovers at night",
        "medium": "Persistent curl, early foxtailing signs",
        "high": "Severe curling, heavy foxtailing, crispy edges",
        "critical": "Plants wilting, severe foxtailing, buds airy and loose",
    },
    treatments={
        "hydroponic": [
            "Lower room temperature (AC, better exhaust, larger fan)",
            "Raise lights to reduce radiant heat at canopy",
            "Add silica supplement (potassium silicate) — increases heat tolerance",
            "Increase airflow across canopy",
            "Run lights during cooler periods (night cycle during day)",
            "Seaweed/kelp extract — natural stress resistance",
        ],
        "coco": [
            "Same as hydroponic",
            "Water more frequently in heat (coco dries faster)",
            "Mulch top of coco to insulate roots",
        ],
        "soil": [
            "Same cooling measures",
            "Mulch to insulate soil from heat",
            "Water in early morning or evening (not midday)",
            "Shade cloth for outdoor grows (30-50%)",
        ],
        "living_soil": [
            "Thick mulch layer protects soil biology from heat",
            "Water early morning before heat builds",
            "Shade cloth if outdoor",
            "Compost tea with kelp (stress resistance)",
            "Don't let soil biology die from excessive heat-drying",
        ],
    },
    prevention=[
        "Keep grow room below 82°F (28°C)",
        "Adequate exhaust and intake for air exchange",
        "Run lights at night during summer",
        "Silica supplement throughout grow (builds cell walls)",
        "Proper light height / dimmer settings",
    ],
    recovery_time="12-24 hours for leaf turgidity; foxtailing is irreversible",
    commonly_confused_with=["Overwatering (drooping vs curling)", "Light burn (bleaching vs curling)"],
)

OVERWATERING = TreatmentEntry(
    id="overwatering",
    category="environmental",
    name="Overwatering",
    aka=["Root suffocation", "waterlogging"],
    summary="Drowning roots by watering too frequently. Leaves droop heavily and soil stays wet for days. The #1 beginner mistake.",
    symptoms=[
        "Leaves droop / hang down (heavy, not crispy)",
        "Leaves feel thick and swollen (edema)",
        "Slow growth despite good conditions",
        "Soil stays wet for 3+ days between waterings",
        "Eventually: yellowing, root rot onset",
        "Fungus gnats attracted to wet surface",
    ],
    identification_tips=[
        "DROOPING: overwatering = limp/heavy droop. Underwatering = thin/papery/light droop",
        "Pick up the pot — if heavy, it's overwatered",
        "Soil is visibly wet on top between waterings",
        "Distinguished from underwatering: overwatered leaves are puffy, underwatered are crispy",
    ],
    causes=[
        "Watering on a schedule instead of by weight/feel",
        "Pot too large for plant size (soil retains too much)",
        "Poor drainage (no perlite, compacted soil, no drain holes)",
        "Saucers holding standing water",
        "Cold environment slowing evaporation",
    ],
    severity_criteria={
        "low": "Mild drooping, recovers within hours",
        "medium": "Persistent droop for 1-2 days, growth stalled",
        "high": "Severe droop, yellowing starting, fungus gnats present",
        "critical": "Root rot setting in, plant declining rapidly",
    },
    treatments={
        "hydroponic": [
            "N/A — overwatering is a soil/media issue",
            "In ebb/flow: reduce flood frequency",
            "In drip: reduce feed events per day",
        ],
        "coco": [
            "Allow top 1-2 inches to dry slightly between waterings",
            "Increase perlite ratio (aim for 70/30 coco/perlite)",
            "Ensure adequate drainage from bottom",
            "Reduce watering frequency (don't water on a schedule)",
        ],
        "soil": [
            "STOP watering until pot is light when lifted",
            "Add perlite to future mixes (30% minimum)",
            "Ensure drainage holes are clear",
            "Remove saucers (or empty them immediately after watering)",
            "Smaller pots for smaller plants",
            "Fabric pots allow air-pruning and faster drying",
        ],
        "living_soil": [
            "Let soil dry appropriately between waterings",
            "Avoid daily watering — living soil retains more moisture",
            "Ensure bed has proper drainage layer",
            "Reduce watering volume, not frequency (deep but less often)",
            "Worms and biology need oxygen — waterlogging kills them",
        ],
    },
    prevention=[
        "Lift the pot — water when LIGHT, not on a schedule",
        "Finger test: stick finger 2 inches in. Dry = water. Moist = wait.",
        "Use appropriate pot size (don't put seedling in 5 gallon)",
        "Add perlite for drainage (30%+ in soil mixes)",
        "Fabric pots over plastic (better aeration)",
    ],
    recovery_time="12-48 hours for drooping to resolve once you stop watering; root rot takes longer",
    commonly_confused_with=["Underwatering (similar droop but dry pot)", "Nitrogen deficiency", "Root rot"],
)

PH_LOCKOUT = TreatmentEntry(
    id="ph_lockout",
    category="environmental",
    name="pH Lockout",
    aka=["Nutrient lockout", "pH-induced deficiency"],
    summary="Nutrients present in solution but unavailable to roots due to incorrect pH. Mimics multiple deficiencies simultaneously.",
    symptoms=[
        "Multiple deficiency symptoms appearing at once",
        "Doesn't respond to adding more nutrients",
        "Leaf discoloration (yellowing, browning, purpling)",
        "Stunted growth despite adequate feeding",
        "Burnt tips + deficiency symptoms simultaneously (confusing)",
    ],
    identification_tips=[
        "KEY SIGN: multiple deficiencies at once (N + Ca + Fe symptoms together)",
        "Adding more nutrients makes it WORSE (excess builds up)",
        "Check pH — if way out of range, this is likely the cause",
        "Hydro: pH below 5.0 or above 7.0",
        "Soil: pH below 5.5 or above 7.5",
    ],
    causes=[
        "Not checking/adjusting pH",
        "pH meter not calibrated",
        "Mineral buildup in media shifting pH over time",
        "Tap water with extreme pH",
        "Using wrong pH range for medium type",
    ],
    severity_criteria={
        "low": "Mild deficiency symptoms, pH slightly out of range",
        "medium": "Multiple visible deficiencies, pH significantly off",
        "high": "Severe multi-symptom presentation, growth stalled",
        "critical": "Plant declining rapidly, won't recover without flush",
    },
    treatments={
        "hydroponic": [
            "Drain and replace entire reservoir with fresh, pH'd solution",
            "Target pH 5.5-6.5 (ideal 5.8-6.2)",
            "Calibrate pH meter",
            "Start at lower EC and build back up over a few days",
        ],
        "coco": [
            "Flush with 3x pot volume of pH'd water (5.8-6.0)",
            "Then re-feed at proper pH and moderate EC",
            "Check runoff pH — should match input within 0.3",
            "If runoff pH is way off, flush again",
        ],
        "soil": [
            "Flush with 3x pot volume of pH 6.5 water",
            "Check runoff pH to confirm correction",
            "Resume feeding at half strength, proper pH (6.0-7.0)",
            "If soil is extremely acidic: dolomite lime. If alkaline: sulfur.",
        ],
        "living_soil": [
            "Living soil naturally buffers pH — true lockout is rare",
            "If pH is extreme: gentle flush with plain dechlorinated water",
            "Add limestone (raise) or sulfur (lower) as amendment",
            "Re-establish biology with compost tea after flush",
            "Check water source pH — very acidic/alkaline water can overwhelm buffer",
        ],
    },
    prevention=[
        "CHECK pH EVERY TIME you mix nutrients",
        "Calibrate pH meter monthly (or use drops as backup)",
        "Know your medium's target range (hydro 5.5-6.5, soil 6.0-7.0)",
        "Monitor runoff pH/EC weekly in coco/soil",
        "Don't let reservoir/feed sit for days (pH drifts)",
    ],
    recovery_time="3-7 days for new growth to normalize after flush; existing damage stays",
    commonly_confused_with=[
        "Actual nutrient deficiencies (but lockout shows MULTIPLE at once)",
        "Root problems",
        "Overfeeding/nutrient burn",
    ],
)

# ═══════════════════════════════════════════════════════════════════════
# FULL DATABASE
# ═══════════════════════════════════════════════════════════════════════

TREATMENT_DATABASE: list[TreatmentEntry] = [
    # Deficiencies
    NITROGEN_DEFICIENCY,
    PHOSPHORUS_DEFICIENCY,
    POTASSIUM_DEFICIENCY,
    CALCIUM_DEFICIENCY,
    MAGNESIUM_DEFICIENCY,
    IRON_DEFICIENCY,
    # Pests
    SPIDER_MITES,
    FUNGUS_GNATS,
    THRIPS,
    # Diseases
    POWDERY_MILDEW,
    BOTRYTIS,
    ROOT_ROT,
    # Environmental
    LIGHT_BURN,
    HEAT_STRESS,
    OVERWATERING,
    PH_LOCKOUT,
]

# Index by ID for fast lookup
_DB_INDEX: dict[str, TreatmentEntry] = {e.id: e for e in TREATMENT_DATABASE}


def get_treatment(issue_id: str) -> TreatmentEntry | None:
    """Look up a treatment entry by ID."""
    return _DB_INDEX.get(issue_id)


def search_treatments(query: str) -> list[TreatmentEntry]:
    """Search treatments by name, category, or symptoms (case-insensitive)."""
    q = query.lower()
    results = []
    for entry in TREATMENT_DATABASE:
        if (
            q in entry.name.lower()
            or q in entry.category.lower()
            or any(q in s.lower() for s in entry.symptoms)
            or any(q in a.lower() for a in entry.aka)
        ):
            results.append(entry)
    return results


def list_by_category(category: str) -> list[TreatmentEntry]:
    """List all treatments in a category."""
    return [e for e in TREATMENT_DATABASE if e.category == category]


def get_treatments_for_grow_type(grow_type: str) -> dict[str, list[str]]:
    """Get grow-type-appropriate treatments for all entries.

    Maps grow_type to treatment category key:
    - DWC, RDWC, NFT, ebb_flow, drip, aeroponics, aquaponics, dutch_bucket, vertical_tower -> 'hydroponic'
    - coco, rockwool -> 'coco'
    - soil, outdoor_soil, outdoor_container -> 'soil'
    - living_soil -> 'living_soil'
    - wicking, kratky -> 'hydroponic' (closest match)
    """
    hydro_types = {
        "dwc",
        "rdwc",
        "nft",
        "ebb_flow",
        "drip",
        "aeroponics",
        "aquaponics",
        "dutch_bucket",
        "vertical_tower",
        "kratky",
        "wicking",
    }
    coco_types = {"coco", "rockwool"}
    soil_types = {"soil", "outdoor_soil", "outdoor_container"}

    if grow_type == "living_soil":
        key = "living_soil"
    elif grow_type in coco_types:
        key = "coco"
    elif grow_type in soil_types:
        key = "soil"
    elif grow_type in hydro_types:
        key = "hydroponic"
    else:
        key = "hydroponic"  # default fallback

    return {entry.id: entry.treatments.get(key, []) for entry in TREATMENT_DATABASE}
