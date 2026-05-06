"""Aquaponics — Complete grow type configuration.

Enterprise-grade configuration covering every aspect of aquaponics from
system cycling through harvest. Fish and plants in symbiosis — fish waste
provides nitrogen, plants filter the water for fish.

Supports three environment types:
  - indoor (default — full environmental control, grow lights)
  - outdoor (natural light, exposed to weather)
  - greenhouse (partial climate control, natural + supplemental light)

KEY DIFFERENCES FROM OTHER HYDRO:
  - NO synthetic fertilizers — toxic to fish
  - pH compromise between fish (6.8-7.2) and plants (5.5-6.5) → target 6.5-7.0
  - Nitrogen cycle: ammonia → nitrite → nitrate (fish → bacteria → plants)
  - Must CYCLE system before adding plants (4-6 weeks of establishing bacteria)
  - Fish health is priority — stressed fish stop producing waste
  - Never do full water changes — destroys beneficial bacteria
  - Temperature must suit BOTH fish and plants simultaneously
  - Supplemental iron/potassium often needed (fish waste lacks these)

Data sources:
  - University of the Virgin Islands aquaponics research (Dr. James Rakocy)
  - Aquaponic Gardening by Sylvia Bernstein
  - Cannabis aquaponics community practices
  - FAO Technical Paper on small-scale aquaponic food production
"""

from __future__ import annotations

AQUAPONICS_STAGES: list[dict] = [
    # ── 1. SYSTEM CYCLING ─────────────────────────────────────────────────
    {
        "id": "cycling",
        "name": "System Cycling",
        "order": 1,
        "duration_days": {"min": 21, "max": 42, "typical": 30},
        "description": "Establish beneficial bacteria colony (Nitrosomonas & Nitrobacter) that convert toxic ammonia from fish waste into plant-available nitrate. System is not ready for plants until ammonia and nitrite both read 0 ppm with rising nitrate.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 50, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "No plants yet — focus on water chemistry. Bacteria colonize media beds, biofilter, and pipe surfaces. Keep water warm to speed colonization.",
        },
        "water": {
            "ph": {"min": 7.0, "max": 7.5, "target": 7.2},
            "ammonia_ppm": {
                "target_end": 0,
                "notes": "Start high (2-4 ppm from fish-less cycling with pure ammonia), drops to 0 when cycled",
            },
            "nitrite_ppm": {"target_end": 0, "notes": "Spikes mid-cycle, must drop to 0"},
            "nitrate_ppm": {"min": 5, "target": 20, "notes": "Rising nitrate = system cycling"},
            "water_temp_f": {"min": 75, "max": 82, "target": 78},
            "dissolved_oxygen_ppm": {"min": 5, "max": 8, "target": 6},
            "notes": "Bacteria multiply fastest at 77-86°F. Keep pH above 7 during cycling (bacteria prefer alkaline). Will lower pH once plants go in.",
        },
        "fish": {
            "species": "None yet (fishless cycling) or hardy feeder goldfish",
            "stocking_density": "If fish-in cycling: 1 small fish per 10 gallons",
            "feeding_rate": "Minimal — just enough to produce ammonia",
            "notes": "Fishless cycling is safer and faster. Add pure ammonia to 2-4 ppm, let bacteria process it. Fish-in cycling risks fish death from ammonia/nitrite spikes.",
        },
        "nutrients": {
            "approach": "Ammonia source only — pure ammonia (no surfactants) or fish food decomposition",
            "supplements": [],
            "notes": "No plant nutrients needed. System will self-produce NPK once cycled and fish are added.",
        },
        "tasks": [
            {
                "name": "Test water chemistry",
                "description": "Test ammonia, nitrite, nitrate, and pH daily. Log all values. Watch for nitrite spike (sign bacteria are establishing).",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Add ammonia source",
                "description": "If fishless cycling: add pure ammonia to maintain 2-4 ppm until bacteria can process it in 24 hours.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Check water temperature",
                "description": "Maintain 75-82°F for optimal bacteria growth. Use aquarium heater if needed.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Verify pump and aeration",
                "description": "Ensure water pump flowing to grow beds and air stones bubbling. Bacteria need oxygen.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off evaporation",
                "description": "Add dechlorinated water to maintain water level. Chlorine kills beneficial bacteria.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Is ammonia decreasing day over day?",
            "Has nitrite appeared (sign of first bacterial colony)?",
            "Is nitrate rising (sign of full cycle)?",
            "Water temperature stable at 75-82°F?",
            "All pumps and air stones running?",
        ],
        "common_problems": [
            {
                "issue": "Cycle stalling",
                "cause": "pH too low (<6.5), temperature too cold, or chlorine in water",
                "solution": "Raise pH with potassium carbonate. Ensure 75°F+ water temp. Use dechlorinator.",
            },
            {
                "issue": "Ammonia not dropping",
                "cause": "Insufficient bacteria surface area or pH crash",
                "solution": "Add more bio-media. Check pH is above 6.8. Patience — can take 2-4 weeks.",
            },
            {
                "issue": "Nitrite stuck high",
                "cause": "Nitrobacter colony still establishing",
                "solution": "Continue cycling. Nitrite-eating bacteria take longer than ammonia-eating bacteria. Ensure oxygen saturation.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Ammonia drops from 2+ ppm to 0 within 24 hours",
            "Nitrite drops from spike to 0 within 24 hours",
            "Nitrate reading above 10 ppm and rising",
            "System can process 2 ppm ammonia to 0 in under 12 hours",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor cycling is slower in cool weather. Use a greenhouse cover or wait for warm season (water temp 70°F+). Sun exposure may cause algae — shade the fish tank."
                },
                "extra_tasks": [
                    {
                        "name": "Check for algae growth",
                        "description": "Sunlight + nutrients = algae. Cover fish tank sides with shade cloth or paint.",
                        "interval_days": 3,
                        "priority": "medium",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse provides warmth for faster cycling. Ensure adequate ventilation to prevent condensation on electrical equipment."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 2. SEEDLING ───────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Start seeds in inert media (rockwool, rapid rooters) separately. Transfer to aquaponic system once roots are established and system is fully cycled. First true leaves emerge.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 60, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 300, "target": 200},
            "light_dli": {"min": 6, "max": 19, "target": 13},
            "notes": "Start seedlings under gentle light away from the system. Transfer to aquaponic grow bed once 2-3 sets of true leaves and root mass visible.",
        },
        "water": {
            "ph": {"min": 6.2, "max": 6.8, "target": 6.5},
            "ammonia_ppm": {"max": 0.25, "target": 0},
            "nitrite_ppm": {"max": 0.25, "target": 0},
            "nitrate_ppm": {"min": 10, "max": 80, "target": 40},
            "water_temp_f": {"min": 68, "max": 78, "target": 72},
            "dissolved_oxygen_ppm": {"min": 5, "max": 8, "target": 6},
            "notes": "Lower pH from cycling levels (7.2) toward 6.5 compromise zone. Do this gradually — 0.2 per day max. Fish prefer 6.8-7.2, plants prefer 5.5-6.5, so we split the difference.",
        },
        "fish": {
            "species": "Tilapia, Koi, Goldfish, or Catfish (warm water) / Trout (cold water)",
            "stocking_density": "1 lb fish per 5-7 gallons (for adequate nutrient production)",
            "feeding_rate": "1-2% body weight per day, 2-3 feedings",
            "notes": "Add fish now if not already present. Start with fewer fish and scale up. Overfeeding = ammonia spike = plant burn AND fish stress.",
        },
        "nutrients": {
            "approach": "Fish waste only — do NOT add synthetic fertilizers",
            "supplements": [
                {
                    "name": "Chelated Iron (DTPA)",
                    "dose": "2 mg/L if leaves yellowing between veins",
                    "notes": "Fish waste lacks iron. Use DTPA form (stable at aquaponic pH). EDDHA also works.",
                },
                {
                    "name": "Potassium carbonate",
                    "dose": "pH up only — raises K and pH simultaneously",
                    "notes": "If potassium deficiency appears and pH needs raising, this solves both.",
                },
            ],
            "notes": "Resist the urge to add bottled nutrients. They will harm fish. Only supplement iron and potassium if deficiency confirmed visually.",
        },
        "tasks": [
            {
                "name": "Test water chemistry",
                "description": "Ammonia and nitrite must stay at 0. Nitrate 20-60 ppm is ideal. pH 6.2-6.8.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Feed fish",
                "description": "Feed 1-2% body weight. Remove uneaten food after 5 minutes to prevent ammonia spike.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check seedling roots",
                "description": "Ensure roots are reaching grow media and accessing water flow. Adjust water level if roots are dry.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Monitor fish behavior",
                "description": "Active swimming, good appetite, no gasping at surface. Gasping = low oxygen.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off water",
                "description": "Add dechlorinated, temperature-matched water to maintain level. Mark optimal level on tank.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are seedlings establishing in grow bed?",
            "Fish active and eating normally?",
            "Ammonia and nitrite at 0?",
            "Water clear (not green/cloudy)?",
            "Roots reaching water flow?",
        ],
        "common_problems": [
            {
                "issue": "Ammonia spike after adding fish",
                "cause": "Too many fish added at once, overfeeding",
                "solution": "Reduce feeding. Add fish gradually (2-3 per week). Do 10% water change if ammonia >1 ppm.",
            },
            {
                "issue": "Seedlings wilting in grow bed",
                "cause": "Roots not reaching water, or transplant shock",
                "solution": "Ensure water level touches net pot bottoms. Shade seedlings for 2-3 days after transplant.",
            },
            {
                "issue": "pH swinging wildly",
                "cause": "System not buffered, or too few plants",
                "solution": "Add crushed coral or shell grit to buffer. More plants = more stable pH.",
            },
        ],
        "training": [],
        "transition_signals": [
            "3-4 sets of true leaves with vigorous growth",
            "Roots visible in grow media, reaching water flow",
            "Plant height 4-6 inches",
            "No signs of nutrient deficiency",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "light_hours": "Natural photoperiod",
                    "notes": "Outdoor seedlings may need shade cloth (50%) for first week. Protect from wind and pests.",
                },
                "extra_tasks": [
                    {
                        "name": "Pest inspection",
                        "description": "Check for aphids, caterpillars, and slugs attracted to young tender growth.",
                        "interval_days": 2,
                        "priority": "medium",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse warmth accelerates seedling growth. Monitor for damping off in humid conditions."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 3. VEGETATIVE ─────────────────────────────────────────────────────
    {
        "id": "vegetative",
        "name": "Vegetative",
        "order": 3,
        "duration_days": {"min": 21, "max": 56, "typical": 35},
        "description": "Rapid growth phase. Plants fill the canopy while fish population matures. Heavy nitrogen demand met by fish waste. This is where aquaponics shines — healthy fish = healthy plants with zero nutrient cost.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 700, "target": 550},
            "light_dli": {"min": 25, "max": 45, "target": 35},
            "notes": "Plants will grow rapidly. Veg phase is flexible — flip to flower when canopy is 50-60% full (plants will stretch 2x in flower).",
        },
        "water": {
            "ph": {"min": 6.2, "max": 6.8, "target": 6.5},
            "ammonia_ppm": {"max": 0, "target": 0},
            "nitrite_ppm": {"max": 0, "target": 0},
            "nitrate_ppm": {"min": 20, "max": 80, "target": 40},
            "water_temp_f": {"min": 68, "max": 78, "target": 72},
            "dissolved_oxygen_ppm": {"min": 5, "max": 8, "target": 6},
            "notes": "Nitrate should be 20-80 ppm. Below 20 = not enough fish/feeding. Above 80 = too many fish or not enough plants. Balance the ratio.",
        },
        "fish": {
            "stocking_density": "1 lb fish per 5-7 gallons",
            "feeding_rate": "2-3% body weight per day, split into 2-3 feedings",
            "notes": "Fish should be growing alongside plants. Larger fish = more waste = more nitrogen. Monitor fish growth and adjust stocking if plants show N deficiency.",
        },
        "nutrients": {
            "approach": "Fish waste provides N-P-K. Supplement only iron and potassium as needed.",
            "supplements": [
                {
                    "name": "Chelated Iron (DTPA)",
                    "dose": "2 mg/L every 2-3 weeks",
                    "notes": "Most common aquaponic deficiency. Yellow leaves with green veins = iron.",
                },
                {
                    "name": "Potassium carbonate",
                    "dose": "As needed for pH up + K supplementation",
                    "notes": "Also raises pH. Use potassium sulfate if pH is already good.",
                },
                {
                    "name": "Seaweed extract (kelp)",
                    "dose": "Very dilute — 1ml/10gal weekly",
                    "notes": "Provides trace minerals and natural growth hormones. Safe for fish at low concentrations.",
                },
            ],
            "notes": "If plants show P deficiency (purple stems/leaves), increase fish feeding rate rather than adding phosphorus. More fish food = more P in waste.",
        },
        "tasks": [
            {
                "name": "Feed fish",
                "description": "2-3% body weight split into 2-3 daily feedings. Remove uneaten food.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Test water",
                "description": "pH, ammonia, nitrite, nitrate. Ammonia and nitrite must be 0. Adjust pH if drifting.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Check fish health",
                "description": "Active swimming, good appetite, clear eyes, no white spots (ich). Count fish — missing fish = dead fish polluting system.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Inspect plant health",
                "description": "Check for iron deficiency (interveinal chlorosis), potassium deficiency (leaf edges browning), or nitrogen excess (dark green, clawing).",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Clean pump intake",
                "description": "Remove debris from pump screen. Fish waste solids can clog pump.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Top off water",
                "description": "Add dechlorinated water to maintain level. Large plants transpire heavily.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Train canopy",
                "description": "LST, topping, or SCROG as appropriate. Even canopy = even light = even fish-fed nutrition.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Leaves vibrant green (not yellow or dark/clawing)?",
            "New growth vigorous?",
            "Fish eating well and active?",
            "Water clear and not smelly?",
            "Nitrate in 20-80 ppm range?",
            "No ammonia or nitrite detected?",
        ],
        "common_problems": [
            {
                "issue": "Iron deficiency",
                "cause": "Fish waste lacks chelated iron",
                "solution": "Add DTPA chelated iron at 2 mg/L. Repeat every 2-3 weeks.",
            },
            {
                "issue": "Slow growth / nitrogen deficiency",
                "cause": "Not enough fish, underfeeding, or too many plants for fish load",
                "solution": "Increase feeding rate. Add more fish. Or reduce plant count to match fish output.",
            },
            {
                "issue": "Algae in system",
                "cause": "Light reaching fish tank or high nitrate + light",
                "solution": "Cover fish tank from light. Add floating duckweed to out-compete algae. Reduce light exposure on water.",
            },
            {
                "issue": "Fish dying",
                "cause": "Ammonia spike, pH crash, temperature swing, or disease",
                "solution": "Test immediately. Partial water change (10-20%) if ammonia detected. Isolate sick fish.",
            },
            {
                "issue": "Root rot",
                "cause": "Insufficient oxygen in root zone or anaerobic spots in media",
                "solution": "Increase aeration. Ensure flood-and-drain cycle isn't waterlogging media. Clean any dead spots.",
            },
        ],
        "training": [
            {
                "name": "LST (Low Stress Training)",
                "when": "Once 5-6 nodes tall",
                "description": "Gently bend main stem to expose lower branches to light. Use soft ties, not wire.",
            },
            {
                "name": "Topping",
                "when": "At 5th-6th node",
                "description": "Cut main stem above 4th-5th node to create 2 main colas. Promotes bushy growth.",
            },
            {
                "name": "SCROG",
                "when": "Once canopy reaches net",
                "description": "Weave branches through net to create even canopy. Works excellently with aquaponics' steady nutrition.",
            },
        ],
        "transition_signals": [
            "Canopy is 50-60% full (will double in stretch)",
            "Plant height appropriate for space (considering 2x stretch)",
            "Root system well-established in grow media",
            "Fish population producing adequate nitrogen (nitrate 30+ ppm steady)",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "light_hours": "Natural photoperiod (must be 14+ hours to prevent premature flowering)",
                    "notes": "Outdoor aquaponics in veg requires long days. Supplement with light if days are <14 hours. Watch for predators (herons, raccoons) targeting fish.",
                },
                "extra_tasks": [
                    {
                        "name": "Check fish predator protection",
                        "description": "Ensure netting over fish tank to prevent herons, cats, raccoons.",
                        "interval_days": 7,
                        "priority": "medium",
                    },
                    {
                        "name": "Monitor water temperature",
                        "description": "Hot sun can overheat fish tank (>82°F is danger zone for most species). Shade tank if needed.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse aquaponics is ideal — thermal mass of fish tank stabilizes temperature. Vent on hot days to prevent overheating."
                },
                "extra_tasks": [
                    {
                        "name": "Vent greenhouse",
                        "description": "Open vents/doors if temp exceeds 85°F. Fish tank thermal mass helps but can still overheat.",
                        "interval_days": 1,
                        "priority": "medium",
                    }
                ],
            },
        },
    },
    # ── 4. FLOWERING ──────────────────────────────────────────────────────
    {
        "id": "flowering",
        "name": "Flowering",
        "order": 4,
        "duration_days": {"min": 49, "max": 77, "typical": 63},
        "description": "Light flip to 12/12 triggers flowering. Plants shift from vegetative growth to bud production. Phosphorus and potassium demand increases — fish waste may need supplementation. Fish feeding rate unchanged but plant uptake shifts.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 79, "target": 75},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 40, "max": 55, "target": 45},
            "vpd_kpa": {"min": 1.0, "max": 1.5, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 1000, "target": 800},
            "light_dli": {"min": 25, "max": 43, "target": 35},
            "notes": "Lower humidity to prevent bud rot. Increase air circulation. Temperature differential (10°F day/night) enhances terpene production in late flower.",
        },
        "water": {
            "ph": {"min": 6.0, "max": 6.5, "target": 6.2},
            "ammonia_ppm": {"max": 0, "target": 0},
            "nitrite_ppm": {"max": 0, "target": 0},
            "nitrate_ppm": {"min": 10, "max": 60, "target": 30},
            "water_temp_f": {"min": 65, "max": 75, "target": 70},
            "dissolved_oxygen_ppm": {"min": 5, "max": 8, "target": 6},
            "notes": "Lower nitrate is OK in flower — less N prevents N toxicity in buds. Slightly lower pH (6.0-6.5) improves P/K uptake. Don't crash below 6.0 or fish suffer.",
        },
        "fish": {
            "stocking_density": "Same as veg — do not change fish population",
            "feeding_rate": "Same 2-3% body weight. Plants need steady nutrition through flower.",
            "notes": "Do NOT reduce feeding to create a 'flush' effect — this crashes the nitrogen cycle. Aquaponics doesn't flush like hydro. The fish need to keep eating.",
        },
        "nutrients": {
            "approach": "Fish waste + targeted P/K supplementation if needed",
            "supplements": [
                {
                    "name": "Bone meal tea (fish-safe)",
                    "dose": "Very dilute — adds phosphorus without harming fish",
                    "notes": "Only if purple stems/poor bud development. Test P levels first.",
                },
                {
                    "name": "Potassium sulfate",
                    "dose": "Small amounts to raise K without affecting pH",
                    "notes": "Flower stage needs more K. Monitor for leaf edge yellowing = K deficiency.",
                },
                {
                    "name": "Chelated Iron (DTPA)",
                    "dose": "2 mg/L every 2-3 weeks",
                    "notes": "Continue iron supplementation through flower.",
                },
            ],
            "notes": "Aquaponic flower feeding is the trickiest part. Fish provide steady N which can cause N toxicity (dark leaves, foxtailing). If N is too high, add more plants or reduce fish feeding slightly (5-10%).",
        },
        "tasks": [
            {
                "name": "Feed fish",
                "description": "Continue regular feeding schedule. Fish health = plant health.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Test water",
                "description": "pH, ammonia, nitrite, nitrate. Watch for N creeping too high in flower.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Monitor bud development",
                "description": "Check trichomes with loupe. Watch for bud rot (brown spots, white fuzz inside buds).",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Defoliate selectively",
                "description": "Remove large fan leaves blocking bud sites. Don't overdo it — leaves feed the fish cycle indirectly.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Check fish health",
                "description": "Lower temps and pH shift may stress fish. Watch for lethargy or reduced appetite.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Inspect for pests",
                "description": "Flowering stage is most vulnerable to spider mites, thrips, and caterpillars. Cannot use most pesticides — would harm fish.",
                "interval_days": 3,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Buds developing properly (not foxtailing from N toxicity)?",
            "No bud rot or mold visible?",
            "Fish still healthy and eating well?",
            "Water chemistry stable?",
            "Leaves not too dark green (N excess)?",
            "Trichomes developing (clear → milky progression)?",
        ],
        "common_problems": [
            {
                "issue": "Nitrogen toxicity",
                "cause": "Fish waste provides constant N, plants need less in flower",
                "solution": "Add companion plants (lettuce, herbs) to soak up excess N. Reduce fish feeding by 5-10%. Do NOT remove fish.",
            },
            {
                "issue": "Phosphorus deficiency",
                "cause": "Fish waste lower in P relative to flower-stage demand",
                "solution": "Add fish-safe bone meal tea. Or add flowering companion plants that fix P.",
            },
            {
                "issue": "Bud rot (Botrytis)",
                "cause": "High humidity + dense buds + poor airflow",
                "solution": "Increase fans. Lower humidity to 40-45%. Selectively defoliate around buds. Remove any infected buds immediately.",
            },
            {
                "issue": "Pests (can't use chemicals)",
                "cause": "Aquaponics limits pest control options — most pesticides kill fish",
                "solution": "Use beneficial insects (ladybugs, lacewings). Neem oil ONLY on leaves, never in water. Sticky traps.",
            },
            {
                "issue": "Fish stressed by lower pH",
                "cause": "pH lowered for flower-stage plant uptake",
                "solution": "Don't go below 6.0. Tilapia tolerate 6.0-6.5 well. Trout prefer higher pH — may need species-specific adjustment.",
            },
        ],
        "training": [
            {
                "name": "Lollipop",
                "when": "First 2 weeks of flower",
                "description": "Remove lower branches that won't receive light. Directs energy to top colas.",
            },
            {
                "name": "Defoliation",
                "when": "Day 21 and day 42 of flower",
                "description": "Strategic leaf removal to improve light penetration and airflow. Critical for bud rot prevention.",
            },
        ],
        "transition_signals": [
            "Trichomes mostly milky with 10-30% amber (strain-dependent)",
            "Pistils 70-90% orange/brown and receding",
            "Buds feel dense and firm",
            "Fan leaves fading/yellowing naturally (senescence)",
            "Calyxes swelling",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "light_hours": "Natural photoperiod (<14h triggers flower)",
                    "notes": "Outdoor aquaponics flowering happens naturally as days shorten. Cannot control humidity — rely on airflow and plant spacing.",
                },
                "extra_tasks": [
                    {
                        "name": "Rain protection",
                        "description": "Cover buds during rain. Wet buds = bud rot. Use temporary canopy or move plants if possible.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                    {
                        "name": "Predator check",
                        "description": "Deer, rabbits, and birds may target mature plants. Fencing is essential.",
                        "interval_days": 7,
                        "priority": "medium",
                    },
                ],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse flower is ideal for aquaponics — rain protection + some climate control. Vent for humidity control, which is critical in flower."
                },
                "extra_tasks": [
                    {
                        "name": "Humidity management",
                        "description": "Open vents in afternoon to drop humidity below 50%. Critical for bud rot prevention.",
                        "interval_days": 1,
                        "priority": "high",
                    }
                ],
            },
        },
    },
    # ── 5. DRYING ─────────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Harvest and hang plants to dry. Fish system continues running for next crop or companion plants. Maintain drying room separate from grow space.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 58, "max": 65, "target": 62},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Dry in complete darkness. Low and slow is key — 60°F/60% RH for 10-14 days preserves terpenes. Keep drying room separate from aquaponics system (humidity/smell).",
        },
        "water": {
            "notes": "Fish system continues as normal. Add companion plants (lettuce, basil, herbs) to maintain nitrogen uptake now that cannabis is removed. Never let system sit with no plants — nitrate builds up.",
        },
        "fish": {
            "notes": "Continue feeding fish normally. The system doesn't stop just because you harvested. If no plants remain, reduce feeding to 50% and add fast-growing lettuce/herbs ASAP.",
        },
        "nutrients": {"approach": "N/A — drying stage. System maintains for fish and any companion plants."},
        "tasks": [
            {
                "name": "Check drying conditions",
                "description": "Maintain 60-65°F and 55-62% RH. Use dehumidifier or AC as needed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Feed fish",
                "description": "Continue feeding. System doesn't stop.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor drying progress",
                "description": "Check stem snap test — small stems should snap cleanly (not bend). Takes 7-14 days.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Plant companion crops",
                "description": "Add lettuce, basil, or herbs to system to maintain nitrogen cycle balance.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Drying room at proper temp/humidity?",
            "No mold on drying buds?",
            "Fish still healthy and fed?",
            "System has enough plants to uptake nitrate?",
        ],
        "common_problems": [
            {
                "issue": "Buds drying too fast",
                "cause": "Humidity too low or temperature too high",
                "solution": "Raise humidity, lower temp. Don't use fans directly on buds.",
            },
            {
                "issue": "Mold on drying buds",
                "cause": "Humidity too high or poor airflow",
                "solution": "Lower humidity. Add gentle air circulation (not pointed at buds). Remove moldy sections.",
            },
            {
                "issue": "Nitrate spiking in system",
                "cause": "Removed all plants but fish still producing waste",
                "solution": "Add fast-growing companion plants immediately. Reduce fish feeding temporarily.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Small stems snap cleanly when bent",
            "Buds feel dry on outside but slightly moist inside",
            "Weight reduced ~75% from fresh",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Dry indoors in a controlled environment. Never dry outdoors — humidity/temp uncontrollable."
                },
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Do not dry in greenhouse — temperature fluctuations and humidity too variable. Use a separate indoor space."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 6. CURING ─────────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 6,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Jar buds in mason jars. Burp daily for first 2 weeks, then weekly. Curing develops flavor, smoothness, and potency through chlorophyll breakdown and terpene maturation.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "light_hours": 0,
            "light_ppfd": 0,
            "notes": "Store jars in cool, dark place. Use Boveda 62% packs if struggling with humidity control.",
        },
        "tasks": [
            {
                "name": "Burp jars",
                "description": "Open jars for 15-30 minutes to exchange air. Smell for ammonia (too wet) or hay (needs more time).",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check humidity in jars",
                "description": "Use mini hygrometer in jar. Target 58-62%. Remove lids if above 65%.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Feed fish / maintain system",
                "description": "Aquaponic system continues for next grow cycle. Keep companion plants going.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Jar humidity at 58-62%?",
            "No ammonia smell (indicates mold risk)?",
            "Buds becoming smoother/less harsh?",
            "Fish system maintained for next cycle?",
        ],
        "common_problems": [
            {
                "issue": "Ammonia smell in jar",
                "cause": "Buds too wet when jarred",
                "solution": "Remove buds from jar, dry for 12-24 more hours, re-jar.",
            },
            {
                "issue": "Buds too dry",
                "cause": "Over-dried before jarring",
                "solution": "Add Boveda 62% pack. Or add a small piece of fresh fan leaf for 4-8 hours.",
            },
            {
                "issue": "Hay/grass smell",
                "cause": "Chlorophyll still breaking down — normal",
                "solution": "Continue curing. Takes 2-4 weeks for chlorophyll to fully degrade.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Smooth smoke, no harshness",
            "Distinct strain terpene profile developed",
            "Humidity stabilized at 60-62% without adjustment",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Cure indoors in controlled environment regardless of grow location."
                },
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Cure indoors in controlled environment. Greenhouse temperature swings will degrade quality."
                },
                "extra_tasks": [],
            },
        },
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# EXPORTED CONFIG
# ─────────────────────────────────────────────────────────────────────────────

AQUAPONICS_CONFIG: dict = {
    "id": "aquaponics",
    "name": "Aquaponics",
    "description": "Fish and plant symbiosis — fish waste feeds plants, plants filter water for fish. Zero fertilizer cost, sustainable, but requires balancing two living ecosystems.",
    "category": "hydroponic",
    "difficulty": "advanced",
    "stages": AQUAPONICS_STAGES,
    "equipment": [
        "Fish tank (100+ gallon recommended)",
        "Grow beds (media-based, NFT, or raft/DWC)",
        "Water pump (sized for tank volume turnover 1-2x/hour)",
        "Air pump + air stones (fish tank AND grow beds)",
        "Biofilter (if not using media beds as biofilter)",
        "Grow media (expanded clay, lava rock)",
        "API Freshwater Master Test Kit",
        "Heater (if needed for fish species)",
        "Net pots",
        "Fish food (high-quality pellets)",
        "Thermometer (water)",
        "pH meter",
        "Grow lights (indoor)",
        "Timer (lights + optional flood/drain cycle)",
    ],
    "fish_species_recommendations": [
        {
            "name": "Tilapia",
            "temp_range_f": "75-85",
            "ph_range": "6.5-8.0",
            "notes": "Best for beginners. Hardy, fast-growing, warm water. Illegal in some states.",
        },
        {
            "name": "Koi/Goldfish",
            "temp_range_f": "65-75",
            "ph_range": "7.0-8.0",
            "notes": "Ornamental only (not for eating). Very hardy. Good for cooler climates.",
        },
        {
            "name": "Catfish",
            "temp_range_f": "75-85",
            "ph_range": "6.5-8.0",
            "notes": "Hardy, edible, tolerate low oxygen better than most species.",
        },
        {
            "name": "Trout",
            "temp_range_f": "55-65",
            "ph_range": "6.5-7.5",
            "notes": "Cold water fish. Excellent for cool climates/seasons. Fast-growing and edible.",
        },
        {
            "name": "Bluegill",
            "temp_range_f": "65-80",
            "ph_range": "6.5-8.5",
            "notes": "Native to US. Hardy, edible, wide temperature tolerance.",
        },
    ],
    "key_principles": [
        "Fish health ALWAYS comes first — without healthy fish, the system collapses",
        "NEVER add synthetic fertilizers — they poison fish",
        "NEVER do full water changes — destroys beneficial bacteria",
        "pH is a compromise: fish want 7.0+, plants want 6.0-6.5, target 6.2-6.8",
        "The nitrogen cycle is everything: ammonia=0, nitrite=0, nitrate=20-80",
        "More fish food = more plant nutrition (but don't overfeed — uneaten food = ammonia spike)",
        "System must CYCLE (4-6 weeks) before adding plants",
        "Iron and potassium are the only common supplements needed",
        "Aquaponics doesn't flush — never stop feeding fish before harvest",
    ],
}
