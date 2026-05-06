"""Dutch Bucket (Bato Bucket) — Complete grow type configuration.

Enterprise-grade configuration for Dutch bucket / Bato bucket growing.
Recirculating drip-to-waste or recirculating system with individual
containers connected to a shared reservoir and drain line.

KEY DIFFERENCES FROM OTHER HYDRO:
  - Individual buckets with their own media (perlite, hydroton, or coco)
  - Top-feed drip emitters from shared reservoir
  - Drain-to-waste OR recirculating (commercial prefers DTW for disease control)
  - Each bucket is independent — can grow different strains/stages
  - Scalable from 4 buckets to 400+ in commercial operations
  - Media provides root support + buffer zone (more forgiving than NFT/aeroponics)
  - Siphon elbow in each bucket maintains reservoir height for root zone
  - Well-suited to large plants (tomatoes, peppers, cannabis)

Data sources:
  - Commercial Dutch bucket greenhouse operations
  - Cannabis production facility designs
  - Hydroponic supply company technical guides (CropKing, FarmTek)
"""

from __future__ import annotations

DUTCH_BUCKET_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Germinate in starter cubes (rockwool or rapid rooters). System doesn't need to run yet — seedlings stay in propagation tray until ready for buckets.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Seeds in darkness on heat mat. Transfer to light once cotyledons emerge.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.0, "max": 0.0, "target": 0.0},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "notes": "No reservoir needed yet. Seeds germinate in moist starter cubes only.",
        },
        "nutrients": {"strength_pct": 0, "approach": "None — plain water on starter cubes."},
        "tasks": [
            {
                "name": "Soak seeds",
                "description": "12-24 hours in room temp water until they sink.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Plant in starter cube",
                "description": "Place germinated seed (taproot down) in moist rockwool or rapid rooter.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for emergence",
                "description": "Watch for cotyledons breaking through cube surface.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Seed cracked?", "Taproot visible?", "Starter cube moist but not soaking?"],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Too cold or too wet",
                "solution": "Heat mat at 78°F. Cube moist not saturated.",
            },
        ],
        "training": [],
        "transition_signals": ["Cotyledons open", "Taproot emerging from bottom of cube"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Start seedlings indoors regardless of final grow location."},
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Propagation area in greenhouse is fine with consistent temps."},
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
        "description": "Seedlings grow in propagation until 3-4 true leaf sets. Then transplant into Dutch buckets filled with media (perlite, hydroton, or coco). Start drip system at low frequency.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 76},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 60, "max": 75, "target": 68},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 150, "max": 300, "target": 200},
            "light_dli": {"min": 10, "max": 19, "target": 13},
            "notes": "Gentle light until transplanted into Dutch bucket. Drip system runs 2-4 times per day for 3-5 minutes each cycle once transplanted.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.4, "max": 0.8, "target": 0.6},
            "ppm_500": {"min": 200, "max": 400, "target": 300},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "notes": "Light nutrient solution. Start drip cycles short and infrequent — media should be moist but roots need oxygen between irrigations.",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "1/4 strength veg formula. Dutch buckets are forgiving — media buffers nutrient concentration.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 2.5,
            "flora_bloom_ml_per_gal": 0.6,
            "calmag_ml_per_gal": 1.0,
        },
        "tasks": [
            {
                "name": "Transplant to Dutch bucket",
                "description": "Place rockwool cube in center of bucket filled with perlite/hydroton. Position drip emitter near stem base.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Set drip schedule",
                "description": "Timer: 3-5 min ON, 2-4 times per day. Adjust based on media drainage.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check runoff",
                "description": "Verify drain line flowing. Each bucket should drain freely through siphon elbow.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Monitor EC and pH",
                "description": "Check reservoir and runoff. Runoff EC should be within 0.3 of input.",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "All drip emitters flowing evenly?",
            "Drain line not clogged?",
            "Seedlings adjusting to Dutch bucket?",
            "No salt buildup on media surface?",
        ],
        "common_problems": [
            {
                "issue": "Uneven watering between buckets",
                "cause": "Drip emitter clogged or line not level",
                "solution": "Clean emitters. Ensure supply line is level. Use compensating drippers for long runs.",
            },
            {
                "issue": "Root zone too wet",
                "cause": "Siphon elbow set too high, or drip cycles too frequent",
                "solution": "Lower siphon height or reduce drip frequency. Media should drain between cycles.",
            },
            {
                "issue": "Wilting after transplant",
                "cause": "Transplant shock",
                "solution": "Increase drip frequency for 2-3 days. Shade from intense light temporarily.",
            },
        ],
        "training": [],
        "transition_signals": [
            "4 sets of true leaves",
            "Roots emerging from starter cube into media",
            "Vigorous new growth",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor Dutch buckets work well in greenhouses and covered structures. Full outdoor requires rain management (dilutes nutrient)."
                },
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Dutch buckets were designed for greenhouse use. Ideal combination."
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
        "description": "Rapid growth phase. Increase drip frequency and nutrient concentration. Dutch bucket media provides excellent root zone buffering — very forgiving system. Plants can grow very large (5-8 ft) in this system.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 77},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 800, "target": 600},
            "light_dli": {"min": 25, "max": 50, "target": 39},
            "notes": "Dutch bucket plants grow large. Ensure adequate space between buckets (24-36 inches for cannabis). Support stakes or trellis may be needed.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 1.0, "max": 1.8, "target": 1.4},
            "ppm_500": {"min": 500, "max": 900, "target": 700},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "change_interval_days": 7,
            "notes": "Full veg strength. Monitor runoff EC — if significantly higher than input, media is accumulating salts. Flush with plain pH water periodically.",
        },
        "nutrients": {
            "strength_pct": 75,
            "flora_micro_ml_per_gal": 3.75,
            "flora_gro_ml_per_gal": 6.25,
            "flora_bloom_ml_per_gal": 1.9,
            "calmag_ml_per_gal": 3.0,
        },
        "drip_schedule": {
            "frequency": "4-8 times per day",
            "duration_min": 3,
            "notes": "Increase frequency as plant grows. Large plants in flower may need 8-12 irrigations per day. Monitor media moisture — should be moist but not waterlogged between cycles.",
        },
        "tasks": [
            {
                "name": "Check reservoir",
                "description": "Top off daily (large plants drink heavily). Full change weekly.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor pH and EC",
                "description": "Check input AND runoff. Runoff EC > input by 0.5+ means salt buildup — flush.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Clean drip emitters",
                "description": "Remove and soak in vinegar water if flow decreasing. Mineral deposits clog over time.",
                "interval_days": 14,
                "priority": "medium",
            },
            {
                "name": "Check drain lines",
                "description": "Verify all buckets draining freely. Root intrusion into drain lines is common.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Train canopy",
                "description": "LST, topping, SCROG. Dutch bucket plants get BIG — train to manage height.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Flush media if needed",
                "description": "If runoff EC is 0.5+ above input, run plain pH water for 1 cycle to wash out accumulated salts.",
                "interval_days": 14,
                "priority": "low",
            },
        ],
        "health_checks": [
            "All emitters flowing evenly?",
            "Runoff EC within 0.3 of input?",
            "No root mass blocking drain?",
            "Plants growing vigorously?",
            "No salt crust on media surface?",
        ],
        "common_problems": [
            {
                "issue": "Salt buildup in media",
                "cause": "Drain-to-waste concentrates salts if not flushing",
                "solution": "Flush with plain pH water once per week or when runoff EC exceeds input by 0.5.",
            },
            {
                "issue": "Root clogging drain",
                "cause": "Roots grow into siphon elbow drain",
                "solution": "Use mesh/screen over drain inlet. Trim roots at drain periodically.",
            },
            {
                "issue": "Uneven growth between buckets",
                "cause": "Uneven drip distribution or clogged emitters",
                "solution": "Check all emitters flow rate. Replace any that are dripping slow.",
            },
            {
                "issue": "Pythium (root rot)",
                "cause": "Media staying too wet, high root zone temps",
                "solution": "Reduce drip frequency. Add Hydroguard to reservoir. Ensure drain is functioning (standing water = root rot).",
            },
        ],
        "training": [
            {
                "name": "Topping",
                "when": "5th-6th node",
                "description": "Top to manage height. Dutch bucket plants can easily reach 6-8ft without topping.",
            },
            {
                "name": "LST",
                "when": "After topping",
                "description": "Bend branches to create even canopy. Tie to bucket edge or support stakes.",
            },
            {
                "name": "SCROG / Trellis",
                "when": "Mid-veg",
                "description": "Install trellis net above buckets. Weave branches through as they grow.",
            },
        ],
        "transition_signals": [
            "Canopy 50-60% full",
            "Plants healthy and vigorous",
            "Root system well-established in media",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor Dutch buckets need rain cover to prevent nutrient dilution. Timer-controlled drip works well with solar-powered pumps."
                },
                "extra_tasks": [
                    {
                        "name": "Check rain protection",
                        "description": "Ensure rain isn't entering buckets/reservoir. Dilution crashes EC.",
                        "interval_days": 3,
                        "priority": "medium",
                    }
                ],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Dutch buckets were invented for greenhouse commercial production. This is their ideal environment."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 4. FLOWERING ──────────────────────────────────────────────────────
    {
        "id": "flowering",
        "name": "Flowering",
        "order": 4,
        "duration_days": {"min": 49, "max": 77, "typical": 63},
        "description": "Light flip to 12/12. Switch to bloom nutrients. Increase drip frequency as water demand peaks. Dutch bucket flowers can be massive due to robust root zone and consistent feeding.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 79, "target": 75},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 40, "max": 55, "target": 45},
            "vpd_kpa": {"min": 1.0, "max": 1.5, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 1000, "target": 800},
            "light_dli": {"min": 25, "max": 43, "target": 35},
            "notes": "Large plants in Dutch buckets produce heavy yields. Support buds with trellis netting. May need multiple trellis layers.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.3, "target": 6.0},
            "ec": {"min": 1.4, "max": 2.2, "target": 1.8},
            "ppm_500": {"min": 700, "max": 1100, "target": 900},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "change_interval_days": 7,
            "notes": "Bloom formula. Monitor water consumption — large flowering plants can drink 1-2 gallons per day per bucket.",
        },
        "nutrients": {
            "strength_pct": 100,
            "flora_micro_ml_per_gal": 5.0,
            "flora_gro_ml_per_gal": 2.5,
            "flora_bloom_ml_per_gal": 7.5,
            "calmag_ml_per_gal": 3.0,
        },
        "drip_schedule": {
            "frequency": "6-12 times per day",
            "duration_min": 3,
            "notes": "Peak water demand. Large plants may need irrigation every 1-2 hours during lights-on. Monitor runoff — should always be some drainage after each cycle.",
        },
        "tasks": [
            {
                "name": "Monitor reservoir daily",
                "description": "Large plants drink heavily. Top off or change as needed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check pH/EC input and runoff",
                "description": "Monitor for salt accumulation. Flush if runoff EC > input by 0.5+.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Support heavy buds",
                "description": "Add trellis layers as buds develop. Dutch bucket yields can be very heavy.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Remove leaves blocking light/air to buds. Critical for bud rot prevention.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Inspect for pests",
                "description": "Check undersides of leaves. Spider mites love the warm dry conditions of flower.",
                "interval_days": 3,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Drip system running reliably?",
            "Buds developing evenly?",
            "No bud rot?",
            "Runoff EC stable?",
            "All drain lines clear?",
        ],
        "common_problems": [
            {
                "issue": "Water demand exceeds reservoir",
                "cause": "Large plants in peak flower drink massively",
                "solution": "Upgrade to larger reservoir. Add float valve for auto top-off. Consider multiple daily reservoir checks.",
            },
            {
                "issue": "Bud rot",
                "cause": "Dense canopy + humidity",
                "solution": "Defoliate aggressively. Lower humidity. Increase air movement. Space buckets further apart.",
            },
            {
                "issue": "Salt lockout late flower",
                "cause": "Accumulated salts in media blocking uptake",
                "solution": "Flush with plain pH water for 1-2 full irrigation cycles. Resume at 50% strength, ramp back up.",
            },
        ],
        "training": [
            {
                "name": "Defoliation",
                "when": "Week 3 and week 6 of flower",
                "description": "Remove fan leaves blocking bud sites. Dutch bucket's robust root zone handles defoliation stress well.",
            },
        ],
        "transition_signals": [
            "Trichomes milky + amber",
            "Pistils darkened",
            "Buds dense and firm",
            "Natural leaf senescence",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Protect from rain. Outdoor Dutch bucket cannabis can produce enormous plants (8ft+) if started early enough in season."
                },
                "extra_tasks": [],
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Commercial cannabis in Dutch bucket greenhouses is a proven production model."
                },
                "extra_tasks": [],
            },
        },
    },
    # ── 5. DRYING ─────────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Hang harvested branches in controlled environment. Dutch bucket yields can be very heavy — ensure adequate drying space and support.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "light_hours": 0,
            "notes": "60/60 rule. Dutch bucket plants produce dense buds — may need longer drying time (12-14 days).",
        },
        "tasks": [
            {
                "name": "Check drying conditions",
                "description": "60-65°F, 55-62% RH. No light.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Stem snap test",
                "description": "Small stems snap = ready for jars.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Clean system for next run",
                "description": "Flush all lines with H2O2 solution. Clean reservoir. Replace or rinse media.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": ["Proper temp/humidity?", "No mold?"],
        "common_problems": [
            {
                "issue": "Dense buds drying too slow on inside",
                "cause": "Very dense buds from Dutch bucket grow",
                "solution": "Break larger buds apart slightly. Ensure airflow around all sides.",
            },
        ],
        "training": [],
        "transition_signals": ["Small stems snap", "Weight reduced ~75%"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Dry indoors always."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Dry indoors in controlled space."}, "extra_tasks": []},
        },
    },
    # ── 6. CURING ─────────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 6,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Jar cure for flavor and smoothness development.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "light_hours": 0,
        },
        "tasks": [
            {
                "name": "Burp jars",
                "description": "Daily for 2 weeks, then 2-3 times per week.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor humidity",
                "description": "58-62% in jars. Boveda 62% for consistency.",
                "interval_days": 1,
                "priority": "medium",
            },
        ],
        "health_checks": ["Humidity correct?", "No mold/ammonia?"],
        "common_problems": [
            {"issue": "Ammonia smell", "cause": "Jarred too wet", "solution": "Remove, dry 12-24h more."},
        ],
        "training": [],
        "transition_signals": ["Smooth smoke", "Full flavor developed"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
            "greenhouse": {"environment_overrides": {"notes": "Cure indoors."}, "extra_tasks": []},
        },
    },
]

DUTCH_BUCKET_CONFIG: dict = {
    "id": "dutch_bucket",
    "name": "Dutch Bucket (Bato Bucket)",
    "description": "Individual buckets with media, fed by shared reservoir via drip emitters. Scalable from hobby (4 buckets) to commercial (400+). Forgiving and productive.",
    "category": "hydroponic",
    "difficulty": "intermediate",
    "stages": DUTCH_BUCKET_STAGES,
    "equipment": [
        "Dutch/Bato buckets (3-5 gallon, with siphon elbows)",
        "Reservoir (sized for plant count — 2-3 gal per bucket minimum)",
        "Water pump (submersible, sized for total flow)",
        "Drip manifold + emitters (pressure-compensating preferred)",
        "Timer (digital, minute-resolution for drip cycles)",
        "Drain line (PVC or flexible tubing — gravity return to reservoir or waste)",
        "Growing media (perlite, hydroton, or 70/30 perlite/vermiculite)",
        "pH meter and EC/TDS meter",
        "Net pots or starter cube holders",
        "Support stakes or trellis netting",
        "Nutrients (GH Flora series or equivalent)",
        "CalMag supplement",
    ],
    "key_principles": [
        "Each bucket is independent — can run different strains/stages on same line",
        "Media provides root zone buffering — more forgiving than DWC/NFT/aeroponics",
        "Siphon elbow maintains minimum water level for bottom root zone moisture",
        "Drain-to-waste prevents disease spread between buckets (commercial standard)",
        "Recirculating saves water/nutrients but risks pathogen spread",
        "Monitor runoff EC to catch salt accumulation before it causes lockout",
        "Drip frequency increases as plants grow — 2x/day seedling → 12x/day peak flower",
        "Clean emitters regularly — mineral deposits clog over time",
        "Scale easily: add more buckets to the same supply line",
    ],
}
