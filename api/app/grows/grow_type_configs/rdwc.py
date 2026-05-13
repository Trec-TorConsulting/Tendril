"""RDWC (Recirculating Deep Water Culture) — Complete grow type configuration.

Enterprise-grade configuration for RDWC systems where multiple buckets share
a central reservoir via plumbing (pumps + return lines).  The defining feature
is a **central control reservoir** that feeds nutrient solution to each
bucket site and drains back — giving uniform pH/EC across all sites but
introducing plumbing, flow-rate, and cross-contamination concerns that
single-bucket DWC does not have.

Key RDWC differences from DWC:
  - Central reservoir + site buckets connected via plumbing
  - Flow rate management (GPH per site)
  - Cross-contamination risk (one sick plant → all sites)
  - Plumbing maintenance (clogs, leaks, uneven flow)
  - Larger total water volume → more stable but slower to adjust
  - Chiller sized for total system volume

Supports three environment types (matching Tent.environment_type):
  - indoor  (default — full environmental control, artificial light)
  - outdoor (no climate control, natural photoperiod, weather exposure)
  - greenhouse (partial climate control, natural + supplemental light)
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in an RDWC grow
# ─────────────────────────────────────────────────────────────────────────────

RDWC_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Seed cracks open and taproot emerges. Use Rapid Rooters or paper towel method. RDWC system is not used yet — germinate separately, transplant to net pots once seedling is established.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Keep seeds in darkness on a heat mat at 78°F. The RDWC system should be assembled, leak-tested, and sterilized during this stage.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.0, "max": 0.0, "target": 0.0},
            "ppm_500": {"min": 0, "max": 0, "target": 0},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "total_system_volume_gal": None,
            "flow_rate_gph": 0,
            "notes": "No reservoir running yet. Use this time to leak-test plumbing, calibrate flow rates, and verify even distribution to all sites.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None — seeds contain all energy needed to germinate.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Soak seeds",
                "description": "Place seeds in cup of room-temp water for 12-24 hours. Transfer to Rapid Rooter once they sink.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for taproot",
                "description": "After 24-72 hours, look for white taproot. Transfer to net pot once taproot is 0.5-1 inch.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Leak-test RDWC system",
                "description": "Fill system with plain water. Run pump for 24 hours. Check every connection, bulkhead, and return line for leaks. Fix before adding nutrients.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Calibrate flow rates",
                "description": "Measure flow to each site bucket. All sites must receive equal flow. Adjust ball valves to balance. Uneven flow = uneven pH/EC.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Sterilize system",
                "description": "Run H2O2 (3ml/gal of 3%) through entire system for 4 hours. Drain and rinse. This kills any bacteria from previous grows.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Has the seed cracked open?",
            "Is the taproot visible and white?",
            "Is the RDWC system leak-free after 24-hour test?",
            "Are flow rates even across all site buckets?",
        ],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Too cold, too dry, or bad seed",
                "solution": "Ensure 75-80°F on heat mat. Keep Rapid Rooter moist. Try a different seed after 7 days.",
            },
            {
                "issue": "Plumbing leaks at bulkheads",
                "cause": "Improper seal, cross-threaded fittings",
                "solution": "Use Teflon tape on threaded connections. Uniseal or bulkhead fittings must be hand-tight plus 1/4 turn. Test with plain water first.",
            },
            {
                "issue": "Uneven flow to sites",
                "cause": "Air locks in lines, different line lengths, pump too weak",
                "solution": "Bleed air from lines. Use ball valves to balance flow. Ensure pump GPH exceeds total system demand by 2x.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Taproot is 0.5-1 inch long",
            "Seed shell cracked and cotyledons emerging",
            "RDWC system leak-tested and flow-balanced",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Germinate indoors regardless. RDWC plumbing must be UV-resistant for outdoor use. Test all connections under full sun exposure.",
                },
                "extra_tasks": [
                    {
                        "name": "UV-proof plumbing check",
                        "description": "Ensure all tubing, fittings, and exposed pipes are UV-resistant or wrapped in reflective insulation. UV degrades standard vinyl tubing.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Always germinate indoors. Outdoor RDWC plumbing requires UV-rated materials.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Germinate inside greenhouse on heat mat. Test system plumbing while seeds germinate.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse provides good shelter for RDWC plumbing.",
            },
        },
    },
    # ── 2. SEEDLING ───────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "First true leaves develop. Place seedlings in net pots in RDWC site buckets. Roots must reach the recirculating water. Keep nutrients very light — the large system volume makes it easy to overfeed seedlings.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 65, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 300, "target": 200},
            "light_dli": {"min": 6, "max": 19, "target": 13},
            "notes": "Keep light 24-30 inches above canopy. RDWC advantage: large water volume = very stable pH/EC for delicate seedlings.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.2, "max": 0.5, "target": 0.4},
            "ppm_500": {"min": 100, "max": 250, "target": 200},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 10,
            "hydroguard_ml_per_gal": 2,
            "total_system_volume_gal": "Calculate: central res + all site buckets + plumbing volume",
            "flow_rate_gph": {"min": 100, "max": 300, "target": 200},
            "notes": "Run pump 24/7. Water level in site buckets should touch bottom of net pots. Adjust float valves if installed. Monitor central reservoir level — it drops as site buckets fill.",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "1/4 strength in central reservoir. The large total volume means each seedling gets consistent, dilute nutrition. Mix in central reservoir only — never add nutrients to individual site buckets.",
            "flora_micro_ml_per_gal": 0.625,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Beneficial bacteria. Add to central reservoir — it distributes to all sites via recirculation.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH at central reservoir",
                "description": "Test pH at the central control reservoir. This is where you measure and adjust — not at individual sites. Target 5.5-6.0.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check EC at central reservoir",
                "description": "Measure EC at central res. RDWC advantage: one measurement covers all sites if flow is balanced.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Verify even flow",
                "description": "Check that water level is equal in all site buckets. Uneven levels = flow imbalance. Adjust ball valves.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Check for root progress",
                "description": "Look through net pot holes for white roots growing down. Top-feed seedlings whose roots haven't reached the water yet.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Monitor central res level",
                "description": "Top off central reservoir with plain pH'd water as needed. Evaporation + plant uptake drops the level.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Check water temp",
                "description": "Measure at central reservoir. One chiller controls temp for entire system. Target 65-72°F.",
                "interval_days": 1,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are cotyledons green and healthy?",
            "Are first true leaves developing?",
            "Is water level equal across all site buckets?",
            "Is the pump running and recirculating?",
            "Are roots growing toward the water in each site?",
            "Water temp below 72°F?",
        ],
        "common_problems": [
            {
                "issue": "Uneven seedling growth across sites",
                "cause": "Flow imbalance — some sites getting more/less nutrient solution",
                "solution": "Check and balance flow rates with ball valves. Verify all return lines are flowing freely.",
            },
            {
                "issue": "Central reservoir drops fast",
                "cause": "Site buckets filling to capacity, evaporation, or a slow leak",
                "solution": "Check for leaks at all connections. Verify float valves are working. Top off regularly.",
            },
            {
                "issue": "Roots not reaching water in some sites",
                "cause": "Water level too low in those site buckets",
                "solution": "Adjust site bucket water level. Top-feed those seedlings with a turkey baster 2-3x daily until roots reach water.",
            },
            {
                "issue": "Pump failure",
                "cause": "Pump clogged, power outage, or undersized pump",
                "solution": "Clean pump intake. Use a backup pump. Size pump at 2x total flow demand. Consider a battery backup for power outages.",
            },
        ],
        "training": [],
        "transition_signals": [
            "3-4 sets of true leaves visible",
            "Roots dangling into water in all site buckets",
            "Vigorous daily growth across all sites",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Keep seedlings in partial shade outdoors. RDWC plumbing must be insulated from sun to prevent algae and heating.",
                },
                "extra_tasks": [
                    {
                        "name": "Insulate plumbing",
                        "description": "Wrap all exposed tubing in reflective insulation. Sunlight on plumbing = algae growth + water heating.",
                        "interval_days": None,
                        "priority": "high",
                    },
                    {
                        "name": "Shade seedlings",
                        "description": "50% shade cloth over seedlings for first 7-10 days outdoors.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Algae in plumbing",
                        "cause": "Light penetrating clear/translucent tubing",
                        "solution": "Replace with black opaque tubing or wrap in light-proof insulation.",
                    },
                ],
                "notes": "Outdoor RDWC requires all plumbing to be opaque and insulated.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse light is naturally diffused. Good for seedlings. Monitor pump and res temps — greenhouses warm water fast.",
                },
                "extra_tasks": [
                    {
                        "name": "Monitor greenhouse temp",
                        "description": "Open vents above 80°F. Seedlings and water both suffer in overheated greenhouses.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse RDWC benefits from the shelter but watch water temps.",
            },
        },
    },
    # ── 3. EARLY VEGETATIVE ───────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Rapid leaf and root growth across all sites. Begin training. RDWC advantage: uniform conditions across sites produces consistent canopy height — critical for even light distribution.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 55, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 300, "max": 600, "target": 450},
            "light_dli": {"min": 19, "max": 39, "target": 29},
            "notes": "Lower light to 18-24 inches. All sites should be growing at similar rates if flow is balanced. Uneven growth = plumbing issue.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 0.6, "max": 1.0, "target": 0.8},
            "ppm_500": {"min": 300, "max": 500, "target": 400},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "flow_rate_gph": {"min": 200, "max": 400, "target": 300},
            "notes": "Weekly full system changes. Drain from central reservoir, flush sites, refill. Large volume means more nutrient cost but much more stability. Monitor consumption rate — RDWC systems drink fast with multiple plants.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half-strength. Mix in central reservoir only. RDWC distributes evenly to all sites. More nitrogen (Gro) for vegetative growth.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.875,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Add to central reservoir. Recirculation distributes to all sites.",
                },
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Strengthens stems. Add before other nutrients. Especially important in RDWC — strong stems handle the vigorous growth.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH at central res",
                "description": "Daily pH check at central reservoir. RDWC's large volume drifts slower than single-bucket DWC.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check EC at central res",
                "description": "Monitor EC. EC rising = top off with plain water. EC dropping = plants are hungry.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Full system reservoir change",
                "description": "Drain central res and all site buckets. Flush lines with plain water. Refill with fresh nutrient solution. Add Hydroguard.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Verify even flow",
                "description": "Check water levels are equal across all sites. Measure flow rate at each return line if possible.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Check plumbing for debris",
                "description": "Root fragments, hydroton dust, and biofilm can clog lines. Inspect intake screens and return line openings.",
                "interval_days": 7,
                "priority": "medium",
            },
            {
                "name": "Root inspection at each site",
                "description": "Check roots at every site bucket. One site with brown roots = cross-contamination risk to all sites.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Begin training (LST)",
                "description": "Once plants have 4-5 nodes, begin LST at all sites simultaneously for even canopy.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are all sites growing at similar rates?",
            "Are roots white and healthy at every site?",
            "Is flow even across all sites?",
            "Is the central reservoir level stable?",
            "Any signs of nutrient deficiency at any site?",
            "Are stems thickening?",
        ],
        "common_problems": [
            {
                "issue": "One site growing slower than others",
                "cause": "Reduced flow to that site, clogged line, or unhealthy roots at that site",
                "solution": "Check flow rate to slow site. Inspect return line for clogs. Check roots at that site for early rot.",
            },
            {
                "issue": "Root rot at one site spreading to others",
                "cause": "RDWC's shared water means pathogens spread to all sites",
                "solution": "This is the #1 RDWC risk. Isolate sick plant if possible (cap its lines). Dose Hydroguard heavily. Consider H2O2 emergency treatment for entire system. Remove dead root material.",
            },
            {
                "issue": "Clogged return line",
                "cause": "Root fragments, hydroton dust, or biofilm buildup",
                "solution": "Flush line with pressurized water. Install inline screen filters on return lines. Clean at every reservoir change.",
            },
            {
                "issue": "Pump noise or reduced flow",
                "cause": "Pump impeller clogged, air lock, or pump wearing out",
                "solution": "Clean pump intake and impeller. Bleed air from lines. Keep a backup pump ready.",
            },
        ],
        "training": [
            {
                "technique": "LST (Low Stress Training)",
                "when": "4-5 nodes",
                "description": "Train all sites simultaneously. RDWC's uniform conditions make training easier — all plants respond similarly.",
            },
            {
                "technique": "Topping",
                "when": "5-6 nodes",
                "description": "Top all plants at the same node for uniform canopy. RDWC's even nutrition supports fast recovery.",
            },
        ],
        "transition_signals": [
            "Plants have 5-6+ nodes at all sites",
            "Root mass thick and white at all sites",
            "Even canopy height across sites",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Full sun now. Insulate all plumbing. Central reservoir must be in shade or insulated — it's the thermal mass for the whole system.",
                },
                "extra_tasks": [
                    {
                        "name": "Shade central reservoir",
                        "description": "Central res must be in complete shade or heavily insulated. It controls temp for all sites.",
                        "interval_days": None,
                        "priority": "high",
                    },
                    {
                        "name": "Pest scouting all sites",
                        "description": "Check every plant for pests. Outdoor RDWC sites may have uneven pest pressure — wind-facing sites get hit first.",
                        "interval_days": 2,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Central reservoir overheating",
                        "cause": "Direct sun on reservoir, hot ambient temps",
                        "solution": "Move res to shade. Insulate with Reflectix. Add chiller if chronic. Res temp controls the whole system.",
                    },
                ],
                "notes": "Outdoor RDWC: the central reservoir is the thermal anchor. Keep it cool and shaded.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse RDWC grows fast in early veg. Ventilate to prevent overheating. Central reservoir should be shaded within the greenhouse.",
                },
                "extra_tasks": [
                    {
                        "name": "Ventilate greenhouse",
                        "description": "Open vents above 80°F. RDWC plants grow aggressively — they transpire heavily, raising humidity.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse RDWC: manage humidity from heavy transpiration of multiple plants.",
            },
        },
    },
    # ── 4. LATE VEGETATIVE ────────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 14, "max": 42, "typical": 21},
        "description": "Maximum vegetative growth. RDWC plants grow explosively — roots interconnect through plumbing creating a massive shared root system. This is when RDWC shows its biggest advantage over single-bucket DWC: uniform, aggressive growth across all sites.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 65, "target": 55},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 26, "max": 45, "target": 39},
            "notes": "Plants drink heavily now — monitor central reservoir level daily. RDWC systems with 4+ sites can consume 5-10+ gallons per day in late veg.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 0.8, "max": 1.2, "target": 1.0},
            "ppm_500": {"min": 400, "max": 600, "target": 500},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "flow_rate_gph": {"min": 300, "max": 500, "target": 400},
            "notes": "Water consumption accelerates dramatically. Top off central reservoir daily or multiple times daily. Consider an auto-top-off (float valve + reservoir) for large systems. Weekly full changes still critical.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "3/4 strength. Peak nitrogen phase. RDWC's large root mass absorbs nutrients efficiently. Watch EC closely — it can drop fast with multiple hungry plants.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 2.5,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Maintain at every change and top-off. More critical now — large root mass is more susceptible.",
                },
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 0.75,
                    "purpose": "Strong stems needed to support the heavy growth RDWC produces.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH",
                "description": "Daily at central reservoir. Large volume drifts slowly but multiple plants can swing pH faster than single DWC.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check EC",
                "description": "EC drops fast with multiple plants feeding. Top off with 1/4 strength if EC is dropping; plain water if rising.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off central reservoir",
                "description": "RDWC systems consume 5-10+ gal/day in late veg. Top off 1-2x daily. Add Hydroguard to top-off water.",
                "interval_days": 0.5,
                "priority": "high",
            },
            {
                "name": "Full system change",
                "description": "Drain, flush lines, refill. Clean any debris from site bucket screens.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Check plumbing",
                "description": "Roots may grow into return lines. Check flow at each site. Clear any root intrusions.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Root inspection all sites",
                "description": "Lift net pots and check roots at every site. One site with problems = threat to all sites.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Canopy management",
                "description": "RDWC grows an even canopy — maintain it with continued LST/SCROG. All sites should be at similar height.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Defoliation (light)",
                "description": "Remove lower growth that won't reach the canopy. Improves airflow around plumbing and bucket sites.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are all sites growing evenly?",
            "Root mass white and healthy at all sites?",
            "Central reservoir holding level between top-offs?",
            "Is flow balanced? (Check site bucket levels.)",
            "Any roots growing into plumbing lines?",
            "Canopy even across all sites?",
        ],
        "common_problems": [
            {
                "issue": "Roots growing into return lines",
                "cause": "Vigorous root growth in RDWC — roots follow water flow into plumbing",
                "solution": "Install root guards (mesh screens) at bucket drain ports. Trim roots that intrude into lines at reservoir changes. Check weekly.",
            },
            {
                "issue": "Central reservoir depletes too fast",
                "cause": "Multiple large plants consuming 5-10+ gallons/day",
                "solution": "Upgrade central reservoir size. Install auto-top-off with float valve and a separate top-off reservoir. Fill top-off with pH'd water.",
            },
            {
                "issue": "EC fluctuating wildly",
                "cause": "Multiple plants consuming at different rates",
                "solution": "More frequent, smaller top-offs. Consider auto-dosing (pH and EC controllers) for large systems.",
            },
            {
                "issue": "One site's roots browning",
                "cause": "Poor flow to that site, or localized issue",
                "solution": "CRITICAL: In RDWC this can spread to ALL sites. Increase flow. Add extra air stone to that site. Dose extra Hydroguard. If severe, isolate that site by capping its lines and treating separately.",
            },
        ],
        "training": [
            {
                "technique": "SCROG (Screen of Green)",
                "when": "Before flipping to flower",
                "description": "Install a trellis net over all sites. Weave branches through as they grow. RDWC's even growth makes SCROG very effective.",
            },
            {
                "technique": "Lollipop",
                "when": "1-2 weeks before flip",
                "description": "Remove all growth below the SCROG net. Redirects energy to top colas.",
            },
        ],
        "transition_signals": [
            "Canopy is 60-75% filled under SCROG",
            "Plants have been in veg 4-6+ weeks",
            "Root mass is enormous and filling site buckets",
            "Ready to flip to 12/12",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor RDWC in late veg: plants grow massive with full sun. Central res consumption is extreme — may need 10-20+ gal/day top-off. Auto-top-off is nearly mandatory.",
                },
                "extra_tasks": [
                    {
                        "name": "Check plumbing for heat degradation",
                        "description": "Hot sun degrades tubing over a full veg cycle. Inspect for soft spots, cracks, or discoloration.",
                        "interval_days": 7,
                        "priority": "medium",
                    },
                    {
                        "name": "Pest management",
                        "description": "Large outdoor RDWC plants attract more pests. Apply preventive neem oil. Scout every 2 days.",
                        "interval_days": 2,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "System consumes 15-20+ gal/day",
                        "cause": "Outdoor heat + full sun + multiple large plants",
                        "solution": "Install large (50+ gal) auto-top-off reservoir with float valve. Check daily.",
                    },
                ],
                "notes": "Outdoor RDWC in late veg is the most water-intensive grow method. Plan for massive consumption.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse RDWC in late veg: humidity soars from multiple plants transpiring. Dehumidifier may be needed. Ventilate aggressively.",
                },
                "extra_tasks": [
                    {
                        "name": "Manage humidity",
                        "description": "Multiple RDWC plants transpire heavily. Humidity above 65% in late veg risks mold. Use exhaust fans and dehumidifier.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse RDWC: humidity management becomes the primary challenge.",
            },
        },
    },
    # ── 5. TRANSITION (PRE-FLOWER) ────────────────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Pre-Flower)",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Light flip to 12/12. Plants stretch 50-100% in height. In RDWC, all sites stretch uniformly if flow is balanced — this is the payoff of good plumbing. Shift nutrients from grow to bloom. The stretch is aggressive in RDWC due to the massive root system driving rapid growth.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 60, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 800, "target": 650},
            "light_dli": {"min": 22, "max": 35, "target": 28},
            "notes": "Flip to 12/12. The stretch in RDWC is aggressive — plan canopy height accordingly. SCROG nets need to be in place before flip. Plants can gain 12-24 inches during stretch.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 0.8, "max": 1.4, "target": 1.1},
            "ppm_500": {"min": 400, "max": 700, "target": 550},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "flow_rate_gph": {"min": 300, "max": 500, "target": 400},
            "notes": "Begin shifting pH target slightly higher (6.0) for phosphorus/potassium availability. Plants drink even more during the stretch. Top off frequently.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Begin transitioning from grow to bloom ratios. Reduce nitrogen, increase phosphorus and potassium. RDWC's uniform delivery ensures even transition across all sites.",
            "flora_micro_ml_per_gal": 1.5,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Continue at every change and top-off."},
            ],
        },
        "tasks": [
            {
                "name": "Flip light schedule",
                "description": "Switch to 12/12. RDWC plants stretch aggressively — ensure adequate headroom. The shared root system drives faster stretching than single DWC.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check pH",
                "description": "Daily. Shift target to 6.0 for better P/K uptake in flower.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor stretch",
                "description": "Measure plant height daily. RDWC stretch can be 50-100%. Adjust SCROG weaving. Supercrop any branches threatening to reach the light.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Full system change with bloom nutrients",
                "description": "Transition to bloom ratio. Drain, flush lines, refill with new formula.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Check for light leaks",
                "description": "12/12 requires complete darkness during lights-off. Check for any light from equipment, indicators, or leaks around door/tent seams.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Defoliation (strategic)",
                "description": "Remove fan leaves blocking bud sites. Open up lower canopy for airflow around plumbing.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are all sites stretching at similar rates?",
            "Are pistils (white hairs) appearing at the nodes?",
            "Is the SCROG net filled 80-100%?",
            "Root mass still healthy across all sites?",
            "Any hermaphrodite signs (pollen sacs)? Check every plant.",
            "Central reservoir holding level?",
        ],
        "common_problems": [
            {
                "issue": "Uneven stretch across sites",
                "cause": "Flow imbalance or one site has root issues",
                "solution": "Check and balance flow rates. Inspect roots at the lagging site. May need to supercrop taller sites to level the canopy.",
            },
            {
                "issue": "Hermaphrodite showing at one site",
                "cause": "Stress, genetics, light leaks",
                "solution": "CRITICAL in RDWC: pollen contaminates ALL sites. Remove the hermaphrodite immediately. Check all other plants daily. Fix light leaks.",
            },
            {
                "issue": "pH swinging more than usual",
                "cause": "Nutrient formula change + heavy plant activity during stretch",
                "solution": "Normal during transition. Adjust gently. The pH will stabilize once stretch slows.",
            },
        ],
        "training": [
            {
                "technique": "Supercropping",
                "when": "During stretch",
                "description": "Pinch and bend overly tall branches. RDWC stretch is aggressive — supercropping controls height without removing growth.",
            },
            {
                "technique": "SCROG weaving",
                "when": "Ongoing",
                "description": "Continue weaving new growth through SCROG net for even canopy.",
            },
        ],
        "transition_signals": [
            "Stretch has slowed or stopped",
            "Pistils visible at all bud sites",
            "Flower clusters beginning to form",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: flowering triggers naturally when daylight drops below ~14 hours. In RDWC, all sites transition together. Monitor for pests — flowering plants attract different pests than veg.",
                },
                "extra_tasks": [
                    {
                        "name": "Verify dark period",
                        "description": "No artificial light should reach plants during dark period. Street lights, security lights, and even moonlight can cause revegging or hermaphrodites.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor RDWC transition: natural photoperiod controls timing.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse may need blackout curtains for 12/12 control. Natural photoperiod + supplemental light control gives flexibility.",
                },
                "extra_tasks": [
                    {
                        "name": "Deploy blackout curtains",
                        "description": "If forcing 12/12 before natural photoperiod, use blackout curtains. Must be complete — any light leak causes problems.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse RDWC: blackout curtains for light dep flowering.",
            },
        },
    },
    # ── 6. EARLY FLOWER ───────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Bud sites form and begin developing. The RDWC advantage shines: uniform nutrient delivery produces consistent bud development across all sites. Water consumption peaks. Cross-contamination vigilance is critical — any pathogen now risks the entire harvest.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 80, "target": 77},
            "temp_night_f": {"min": 62, "max": 72, "target": 68},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.0, "max": 1.5, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Lower humidity to prevent bud rot. RDWC grows dense canopies — airflow between sites is critical. Use oscillating fans pointing between plants.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 1.0, "max": 1.6, "target": 1.3},
            "ppm_500": {"min": 500, "max": 800, "target": 650},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "flow_rate_gph": {"min": 300, "max": 500, "target": 400},
            "notes": "Increase res change frequency to every 5 days. Plants are feeding heavily. More frequent changes = cleaner root zone = better bud production. Monitor for salt buildup in plumbing connections.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom strength. Heavy phosphorus and potassium for bud development. All sites receive identical nutrition from the central reservoir — this is RDWC's key advantage for consistent flower quality.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Continue religiously. Root rot during flower = catastrophic loss.",
                },
                {
                    "name": "PK Booster (Liquid Koolbloom)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Extra phosphorus and potassium. Start low and increase. Watch for tip burn.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH",
                "description": "Daily. Maintain 5.8-6.2 for optimal P/K uptake.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check EC",
                "description": "Daily. Full-strength bloom nutes — watch for tip burn (EC too high) or light green new growth (too low).",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Full system change",
                "description": "Every 5 days. Clean solution critical during flower. Flush plumbing at each change.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Root inspection all sites",
                "description": "Check every site for root health. Brown/slimy roots at ANY site require immediate action — the whole system is at risk.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Monitor bud development",
                "description": "All sites should show similar bud development if flow is balanced. Uneven buds = check flow to that site.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Check plumbing connections",
                "description": "Salt buildup at fittings during flower can restrict flow. Clean at reservoir changes.",
                "interval_days": 5,
                "priority": "medium",
            },
            {
                "name": "Defoliation (targeted)",
                "description": "Remove leaves blocking bud sites and impeding airflow. RDWC canopies get dense — airflow prevents mold.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are buds forming at all sites?",
            "Bud development even across sites?",
            "Root health good at all sites? (Critical check.)",
            "Humidity staying below 55%?",
            "Any signs of bud rot or PM at any site?",
            "Plumbing connections clear and flowing?",
        ],
        "common_problems": [
            {
                "issue": "Root rot detected at one site during flower",
                "cause": "The worst RDWC scenario — pathogen in shared system during flower",
                "solution": "EMERGENCY: Isolate affected site if possible (cap lines). Dose heavy Hydroguard to entire system. Add hydrogen peroxide (3ml/gal of 3%) as emergency treatment — then switch back to Hydroguard 24 hours later. Full system change. Monitor all other sites hourly for 48 hours.",
            },
            {
                "issue": "Bud rot at one site",
                "cause": "Humidity too high, airflow blocked, dense canopy",
                "solution": "Remove all affected bud material (cut 2 inches below visible rot). Increase airflow. Lower humidity to 45%. Inspect all other sites — bud rot spores spread. Defoliate for airflow.",
            },
            {
                "issue": "Salt buildup in plumbing",
                "cause": "Bloom nutrients are heavier and leave more mineral deposits",
                "solution": "Flush lines with plain pH'd water at every reservoir change. Use a pipe brush on accessible connections.",
            },
            {
                "issue": "Uneven bud development",
                "cause": "Flow imbalance, root issues at one site, or light distribution",
                "solution": "Balance flow. Check roots. Adjust light height/angle. Rotate plants if possible.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation",
                "when": "Day 1 and day 21 of flower",
                "description": "Strategic removal of fan leaves. First defoliation when flower starts. Second at week 3. Improves light penetration to lower buds.",
            },
        ],
        "transition_signals": [
            "Buds swelling and white pistils abundant",
            "Trichomes visible with naked eye",
            "Flower scent developing",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor RDWC in flower: rain is the biggest threat — water dilutes res and creates humidity. Build rain covers over sites. Central res must be covered.",
                },
                "extra_tasks": [
                    {
                        "name": "Rain protection",
                        "description": "Build covers over all site buckets and central reservoir. Rain dilutes nutrients and can overflow sites. A tarp roof works — just ensure airflow.",
                        "interval_days": None,
                        "priority": "high",
                    },
                    {
                        "name": "PM prevention",
                        "description": "Apply potassium bicarbonate spray weekly as PM prevention. Outdoor humidity swings are unavoidable.",
                        "interval_days": 7,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Rain event floods system",
                        "cause": "Uncovered sites overflow in heavy rain",
                        "solution": "Emergency drain of excess water. Check EC (diluted = add nutrients). Cover all open surfaces.",
                    },
                ],
                "notes": "Outdoor RDWC in flower: rain protection is non-negotiable.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse RDWC in flower: humidity control is the #1 challenge. Multiple plants transpiring heavily in an enclosed space. Dehumidifier is essential.",
                },
                "extra_tasks": [
                    {
                        "name": "Run dehumidifier",
                        "description": "Keep humidity below 55%. RDWC canopies in greenhouses trap moisture. Run dehumidifier during lights-off when humidity peaks.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse RDWC in flower: dehumidifier is mandatory.",
            },
        },
    },
    # ── 7. MID FLOWER (BULK PHASE) ────────────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Bulk Phase)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 21},
        "description": "Peak bud production. Buds swell rapidly and pack on weight. RDWC's uniform nutrient delivery produces remarkably consistent bud size across all sites. Water and nutrient consumption hits maximum. This is the most resource-intensive phase.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 78, "target": 76},
            "temp_night_f": {"min": 60, "max": 70, "target": 66},
            "humidity_pct": {"min": 40, "max": 50, "target": 45},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
            "notes": "Maximum light intensity. Drop humidity to 45% to prevent bud rot in dense RDWC canopies. Temperature differential (day/night) enhances terpene and color production.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 1.2, "max": 1.8, "target": 1.5},
            "ppm_500": {"min": 600, "max": 900, "target": 750},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "flow_rate_gph": {"min": 300, "max": 500, "target": 400},
            "notes": "Peak consumption. Multiple large flowering plants can drain 10-15+ gallons/day. Auto-top-off is strongly recommended. Change every 5 days — bloom nutrients leave more deposits.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom strength. Maximum phosphorus and potassium. RDWC delivers peak nutrition uniformly. Watch EC closely — slight tip burn is optimal (means plants are at max capacity).",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 3.125,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Non-negotiable during flower. Root rot now = total loss.",
                },
                {
                    "name": "PK Booster (Liquid Koolbloom)",
                    "dose_ml_per_gal": 1.0,
                    "purpose": "Peak PK supplementation for bud density. Increase to full dose.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check pH",
                "description": "Daily at central reservoir. Maintain 5.8-6.2.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check EC",
                "description": "Daily. Slight tip burn on newest growth = perfect EC. Heavy burn = reduce 10%. No burn = can push slightly higher.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off central reservoir",
                "description": "May need 2-3x daily during peak flower. RDWC systems with 4+ flowering plants are extremely thirsty.",
                "interval_days": 0.5,
                "priority": "high",
            },
            {
                "name": "Full system change",
                "description": "Every 5 days. Flush all lines at each change. Salt buildup accelerates with heavy bloom nutrients.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Root inspection all sites",
                "description": "Check every site. This is the highest-risk period for root rot — warm res + heavy organics + peak oxygen demand.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Bud rot inspection",
                "description": "Check all bud sites at all plants for brown/gray rot. Dense RDWC canopies trap humidity. Part dense buds and look inside.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Support heavy branches",
                "description": "RDWC produces heavy buds. Install plant yoyos or bamboo stakes. SCROG net helps distribute weight.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are buds swelling uniformly across all sites?",
            "Trichomes milky/clear under loupe?",
            "Root mass healthy and white at all sites?",
            "Any signs of bud rot (brown/mushy patches)?",
            "Humidity consistently below 50%?",
            "Are branches adequately supported?",
        ],
        "common_problems": [
            {
                "issue": "Central reservoir depletes within hours",
                "cause": "Peak flower consumption with multiple large plants",
                "solution": "Install auto-top-off. Upgrade central reservoir to largest possible. Some commercial RDWC runs a 50-100 gal central res for 8+ sites.",
            },
            {
                "issue": "Bud rot at one site",
                "cause": "Humidity pocket, dense bud, poor airflow at that site",
                "solution": "Remove ALL affected material (cut 2 inches below rot). Increase airflow to that site. Check all other sites. Lower room humidity.",
            },
            {
                "issue": "Salt crystallization at plumbing joints",
                "cause": "Heavy bloom nutrients depositing at connection points",
                "solution": "Clean at every reservoir change. Use a pipe brush. Run hot water through lines during changes.",
            },
            {
                "issue": "Pump struggles with flow",
                "cause": "Salt buildup in pump, root debris in intake",
                "solution": "Clean pump at every res change. Install pre-filter screen on intake. Consider upgrading pump for late flower demands.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation (Day 42)",
                "when": "Day 42 of flower (~week 6)",
                "description": "Final light defoliation. Remove only leaves directly blocking bud sites. Do not over-defoliate in late flower.",
            },
        ],
        "transition_signals": [
            "Pistils starting to darken (orange/brown)",
            "Trichomes becoming cloudy/milky",
            "Buds dense and heavy",
            "New pistil production slowing",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor mid flower: protect from rain at all costs. Rain + dense buds = guaranteed bud rot. Build permanent rain covers over all sites.",
                },
                "extra_tasks": [
                    {
                        "name": "Shake plants after rain/dew",
                        "description": "Gently shake each plant in the morning to remove dew. Moisture sitting on buds causes rot.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Morning dew causing bud rot",
                        "cause": "Outdoor humidity + dew on dense flower clusters",
                        "solution": "Shake plants gently each morning. Add oscillating fans if power available. Defoliate for airflow.",
                    },
                ],
                "notes": "Outdoor RDWC mid flower: rain and dew are the primary threats.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: run dehumidifier 24/7 during mid flower. Greenhouse traps moisture from multiple transpiring plants.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse RDWC mid flower: dehumidification is critical.",
            },
        },
    },
    # ── 8. LATE FLOWER (RIPENING) ─────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Final bud maturation and trichome ripening. Reduce nutrients. Buds swell their last 10-20%. Trichomes transition from clear→cloudy→amber. In RDWC, all sites ripen at similar rates if system has been balanced.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 74},
            "temp_night_f": {"min": 58, "max": 68, "target": 64},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 800},
            "light_dli": {"min": 26, "max": 39, "target": 35},
            "notes": "Cooler temps + large day/night differential enhances color and terpene production. Some growers drop to 35% humidity. RDWC's uniform environment helps all sites ripen together.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 0.8, "max": 1.2, "target": 1.0},
            "ppm_500": {"min": 400, "max": 600, "target": 500},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "flow_rate_gph": {"min": 300, "max": 500, "target": 400},
            "notes": "Reduce nutrient strength. Plants are finishing — they need less. Water consumption decreases slightly. Continue 5-day res changes to keep solution clean for the final stretch.",
        },
        "nutrients": {
            "strength_pct": 60,
            "approach": "Reduced strength. Taper down nutrients. Stop PK boosters. Allow plant to begin using internal reserves. Some yellowing of fan leaves is normal and desired — the plant is redirecting energy to buds.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 0.0,
            "flora_bloom_ml_per_gal": 2.0,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Continue until flush begins."},
            ],
        },
        "tasks": [
            {
                "name": "Check trichomes daily",
                "description": "Use 60x loupe or digital microscope. Clear = not ready. Milky/cloudy = peak THC. Amber = more sedative. Most growers harvest at 10-20% amber.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check pH/EC",
                "description": "Daily. Reduced nutes. pH management continues.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Full system change",
                "description": "Continue 5-day changes. Clean solution until flush.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Bud rot patrol (all sites)",
                "description": "Dense, mature buds are most susceptible. Check all sites daily. Part large colas and inspect inside.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check trichome maturity at all sites",
                "description": "RDWC advantage: if balanced, all sites ripen together. Check the lagging site to determine harvest timing.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Remove dying fan leaves",
                "description": "Yellow/dying fan leaves are normal now. Remove them to prevent mold and improve airflow.",
                "interval_days": 3,
                "priority": "low",
            },
        ],
        "health_checks": [
            "Trichome maturity progressing? (Clear → milky → amber)",
            "Fan leaves yellowing naturally? (Good sign — plant using reserves)",
            "Any bud rot? Check all sites daily.",
            "Roots still healthy? (Almost done — keep them clean.)",
            "All sites at similar ripeness?",
        ],
        "common_problems": [
            {
                "issue": "One site ripening faster than others",
                "cause": "Slight genetic variation or light distribution difference",
                "solution": "In RDWC, you can harvest individual sites at different times. Cap the harvested site's plumbing and continue running the system for remaining sites.",
            },
            {
                "issue": "Foxtailing (new growth on buds)",
                "cause": "Light stress (too close) or heat stress",
                "solution": "Raise light slightly. Lower room temp. Some foxtailing is genetic and harmless.",
            },
            {
                "issue": "Bud rot in final week",
                "cause": "Dense mature buds + any humidity spike",
                "solution": "Harvest immediately if rot is spreading. Better to harvest slightly early than lose buds to rot. Remove affected material before it spreads via shared system.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Trichomes 70-90% milky with 10-20% amber",
            "Pistils 70-80% brown/orange",
            "Fan leaves mostly yellow",
            "Bud growth has visibly slowed",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor late flower: watch for early frost. RDWC plumbing can freeze, cracking fittings. Harvest before first frost or bring system inside.",
                },
                "extra_tasks": [
                    {
                        "name": "Monitor frost forecast",
                        "description": "Frost kills plants and cracks plumbing. Harvest before first frost or protect with row covers. Have an emergency harvest plan.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Early frost threatens system",
                        "cause": "Late-season temperature drop",
                        "solution": "Harvest immediately or cover plants + insulate all plumbing. RDWC is especially vulnerable — water in plumbing expands when frozen.",
                    },
                ],
                "notes": "Outdoor RDWC: harvest timing is frost-date-dependent.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: cool fall nights enhance colors and terpenes. Monitor for frost if greenhouse is unheated.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse RDWC: cool nights are beneficial if above freezing.",
            },
        },
    },
    # ── 9. FLUSH ──────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Run plain pH'd water through the entire RDWC system. No nutrients. This allows plants to use remaining internal nutrient stores, producing cleaner-burning, better-tasting flower. RDWC advantage: the recirculating system flushes all sites simultaneously and thoroughly.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 74},
            "temp_night_f": {"min": 58, "max": 68, "target": 64},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 800, "target": 650},
            "light_dli": {"min": 22, "max": 35, "target": 28},
            "notes": "Maintain 12/12. Some growers reduce light slightly during flush. Continue monitoring environment — bud rot risk persists.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 0.0, "max": 0.2, "target": 0.0},
            "ppm_500": {"min": 0, "max": 100, "target": 0},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 3,
            "hydroguard_ml_per_gal": 2,
            "flow_rate_gph": {"min": 300, "max": 500, "target": 400},
            "notes": "Plain pH'd water only. Change every 3 days to flush accumulated salts. RDWC's recirculation rinses all sites continuously. Continue Hydroguard — root health matters until harvest day.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Zero nutrients. Plain pH'd water. The recirculating system flushes salts from all sites simultaneously — more efficient flush than single DWC.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Continue through flush. Root rot in final week wastes the entire grow.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Drain and refill with plain water",
                "description": "Drain entire system. Refill central res with plain pH'd water. No nutrients. Run pump to flush all lines and sites.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Monitor EC runoff",
                "description": "Check EC of water returning from sites. EC should drop toward 0 over the flush period. If EC stays high, extend flush.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Continue trichome checks",
                "description": "Plants continue maturing during flush. Check trichomes to time harvest precisely.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor for bud rot",
                "description": "Continue daily checks at all sites. Flush period is still high-risk for rot.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Prepare harvest equipment",
                "description": "Sharp trimming scissors, drying rack/lines, mason jars, hygrometers, Boveda packs. Have everything ready before harvest day.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Fan leaves yellowing/fading? (Expected during flush.)",
            "EC of return water dropping?",
            "Trichomes reaching target maturity?",
            "Any last-minute bud rot? (Inspect daily.)",
        ],
        "common_problems": [
            {
                "issue": "EC not dropping during flush",
                "cause": "Salt buildup in plumbing or site buckets not flushing completely",
                "solution": "Drain and refill more frequently (every 2 days). Manually flush each site bucket. Run pump at higher flow.",
            },
            {
                "issue": "Plant wilting during flush",
                "cause": "Root function declining naturally near end of life",
                "solution": "Normal — plant is finishing. Ensure water level is maintained. Don't add nutrients.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Flush duration reached (7-14 days)",
            "EC of return water near 0",
            "Trichomes at target maturity (10-20% amber)",
            "Fan leaves mostly yellow/fallen",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor flush: rain actually helps flush. Let rain dilute the system during this phase. Still monitor for rot.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: rain is acceptable during flush — it aids the flushing process.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse flush: maintain ventilation. Dying fan leaves can harbor mold in humid conditions.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: remove fallen leaves promptly to prevent mold.",
            },
        },
    },
    # ── 10. HARVEST ───────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Cut plants, trim, and hang to dry. RDWC harvest consideration: you can harvest individual sites at different times if they ripened unevenly — cap the harvested site's plumbing lines and continue running the system for remaining sites. Drain the entire system only after the last site is harvested.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Some growers give 24-48 hours of darkness before harvest to boost trichome production. Cut plant at base. Wet trim or dry trim based on preference.",
        },
        "reservoir": {
            "ph": None,
            "ec": None,
            "ppm_500": None,
            "water_temp_f": None,
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "flow_rate_gph": 0,
            "notes": "Drain system after last site harvested. Run plain water + H2O2 through all lines to clean. Disassemble and clean all components.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Optional dark period",
                "description": "24-48 hours of darkness before harvest. Debated but many growers report stickier trichomes.",
                "interval_days": None,
                "priority": "low",
            },
            {
                "name": "Harvest sites",
                "description": "Cut each plant at the base. If sites are at different maturities, harvest ready sites first — cap their plumbing and continue system for others.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Wet trim or whole-plant hang",
                "description": "Wet trim: trim leaves immediately after cutting. Dry trim: hang whole plants and trim after drying. Wet trim is faster; dry trim often produces better flavor.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Clean RDWC system",
                "description": "After last site is harvested: drain everything. Run H2O2 (5ml/gal of 3%) through all lines for 4 hours. Drain, rinse, disassemble, scrub all buckets. Dry completely before storage.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Inspect plumbing for damage",
                "description": "Check all tubing, bulkheads, and fittings. Replace anything degraded. Root intrusions may have weakened connections.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Were trichomes at target maturity when cut?",
            "Any bud rot discovered during trimming? (Remove affected areas.)",
            "Is the RDWC system fully cleaned and dried?",
        ],
        "common_problems": [
            {
                "issue": "Bud rot discovered during trim",
                "cause": "Hidden rot inside dense colas",
                "solution": "Cut at least 1 inch beyond visible rot. Discard affected material. Inspect remaining buds carefully.",
            },
            {
                "issue": "Plumbing stained/clogged after harvest",
                "cause": "Salt + root + biofilm buildup over the full grow cycle",
                "solution": "Soak all removable parts in H2O2 solution overnight. Use pipe brushes. Replace any tubing that won't come clean.",
            },
        ],
        "training": [],
        "transition_signals": ["All plants cut and hanging", "RDWC system cleaned"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Harvest before frost. Bring plants inside to trim in a clean, controlled environment."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: harvest timing may be forced by weather.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse can serve as drying space if humidity is manageable."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: usable as drying space with proper ventilation.",
            },
        },
    },
    # ── 11. DRYING ────────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Hang whole plants or branches in a dark, cool, ventilated space. Target slow dry over 10-14 days. RDWC yields tend to be larger — ensure adequate drying space for multi-site harvests.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 58, "max": 65, "target": 62},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Complete darkness. Gentle airflow (not blowing directly on buds). 60°F and 60% humidity is the sweet spot. Slower dry = better cure.",
        },
        "reservoir": {
            "ph": None,
            "ec": None,
            "ppm_500": None,
            "water_temp_f": None,
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "flow_rate_gph": 0,
            "notes": "System should be cleaned and stored.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Check drying progress",
                "description": "Small stems should snap (not bend) when dry. Large stems still slightly flexible. This takes 7-14 days. Do NOT rush with fans or heat.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor temp and humidity",
                "description": "Keep 60-65°F and 55-65% humidity. Too fast = harsh smoke. Too slow = mold risk.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check for mold",
                "description": "Inspect hanging buds daily. Dense RDWC colas are especially mold-prone during drying. Remove any affected buds immediately.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Are small stems snapping yet?",
            "Any mold or off-smell on drying buds?",
            "Is the drying room holding 60°F / 60% RH?",
        ],
        "common_problems": [
            {
                "issue": "Buds drying too fast (crispy outside, wet inside)",
                "cause": "Temp too high, humidity too low, fans blowing on buds",
                "solution": "Lower temp. Raise humidity (wet towel in room). No direct airflow on buds.",
            },
            {
                "issue": "Mold during drying",
                "cause": "Humidity too high, not enough airflow, or bud rot hidden from grow phase",
                "solution": "Remove moldy material immediately. Increase ventilation. Lower humidity. Inspect all remaining buds.",
            },
        ],
        "training": [],
        "transition_signals": ["Small stems snap cleanly", "Outside of bud is dry to touch", "7-14 days elapsed"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Dry indoors in a controlled environment. Never dry outdoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always dry indoors.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse is NOT ideal for drying — too much humidity fluctuation. Dry in a separate indoor space if possible."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Avoid drying in greenhouse if possible.",
            },
        },
    },
    # ── 12. CURING ────────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Place dried buds in mason jars. Burp daily for first 2 weeks, then weekly. Curing converts harsh chlorophyll into smooth-smoking compounds and develops terpene profiles. Minimum 2-week cure; 4-8 weeks is ideal.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 58, "max": 68, "target": 62},
            "humidity_pct": {"min": 58, "max": 65, "target": 62},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Store jars in a cool, dark place. Boveda 62% packs maintain perfect humidity. Light degrades THC — complete darkness.",
        },
        "reservoir": {
            "ph": None,
            "ec": None,
            "ppm_500": None,
            "water_temp_f": None,
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "flow_rate_gph": 0,
            "notes": "N/A — system cleaned and stored.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Burp jars",
                "description": "Open jars for 5-15 minutes. Week 1-2: daily. Week 3-4: every 2-3 days. After week 4: weekly. If ammonia smell when opening = too wet, leave lid off for 1 hour.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check jar humidity",
                "description": "Use mini hygrometer in each jar. Target 58-65%. Above 65% = too wet (leave lid off). Below 55% = add Boveda 62% pack.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Inspect for mold",
                "description": "Check buds visually when burping. Any mold = remove affected buds immediately. Discard the whole jar if mold is widespread.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Jar humidity at 58-65%?",
            "Buds smell improving (less hay, more terpenes)?",
            "Any mold or off-smell?",
        ],
        "common_problems": [
            {
                "issue": "Hay/grass smell",
                "cause": "Chlorophyll still breaking down. Normal in first 1-2 weeks.",
                "solution": "Continue curing. The hay smell fades and terpenes emerge after 2-3 weeks.",
            },
            {
                "issue": "Ammonia smell when burping",
                "cause": "Buds were jarred too wet. Anaerobic bacteria breaking down plant material.",
                "solution": "Remove buds from jar immediately. Lay on paper bag or drying rack for 12-24 hours. Re-jar when drier.",
            },
            {
                "issue": "Buds too dry (crumble when squeezed)",
                "cause": "Over-dried before jarring, or jar humidity too low",
                "solution": "Add Boveda 62% pack. It slowly rehydrates buds to perfect humidity. Takes 3-5 days to stabilize.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Cure complete (minimum 2 weeks, ideal 4-8 weeks)",
            "Buds have rich terpene aroma",
            "Smooth smoke test passed",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Cure indoors in a cool, dark space. Identical process regardless of grow environment."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Curing is environment-independent.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Do not cure in the greenhouse — temperature swings degrade quality. Cure indoors."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Cure indoors, not in greenhouse.",
            },
        },
    },
    # ── 13. STORAGE ──────────────────────────────────────────────────────
    {
        "id": "storage",
        "name": "Long-Term Storage",
        "order": 13,
        "duration_days": {"min": 30, "max": 365, "typical": 180},
        "description": "Post-cure long-term storage for commercial and home operations. RDWC produces heavy yields — plan storage capacity accordingly. A 4-site RDWC system can produce 2-4+ lbs per cycle. Proper storage preserves potency and terpenes for 6-12+ months. THC degrades to CBN at ~5%/year under ideal conditions, much faster with heat, light, or oxygen exposure.",
        "environment": {
            "temp_day_f": {"min": 55, "max": 65, "target": 60},
            "temp_night_f": {"min": 55, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK. Cool. Stable. Zero light — UV destroys cannabinoids and terpenes. Commercial vaults: 58-62°F, 55-60% RH, complete darkness, nitrogen atmosphere.",
        },
        "reservoir": None,
        "nutrients": {
            "strength_pct": 0,
            "approach": "None.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Transfer to long-term containers",
                "description": "Home: mason jars with Boveda 58-62% packs. Commercial: nitrogen-sealed grove bags, CVault containers, or nitrogen-flushed drums. RDWC yields are high — plan container volume accordingly.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Label and track batches",
                "description": "Strain, harvest date, storage date, weight, batch number. Commercial: seed-to-sale tracking, FIFO rotation.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Monthly quality checks",
                "description": "Inspect for mold, off odors. Check humidity packs. Commercial: potency/terpene testing at 30/90/180 days.",
                "interval_days": 30,
                "priority": "high",
            },
            {
                "name": "Maintain environment",
                "description": "Monitor vault temp/humidity. No light leaks. Commercial: automated environmental monitoring with alerts.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Rotate stock (FIFO)",
                "description": "First in, first out. Flag batches approaching 12 months for priority sale or extraction.",
                "interval_days": 30,
                "priority": "medium",
            },
            {
                "name": "Compliance testing holds",
                "description": "Commercial: retain testing samples per regulations. Track chain of custody.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Temp 55-65°F?",
            "Humidity 55-62%?",
            "Complete darkness?",
            "No mold/off odors?",
            "Humidity packs active?",
            "FIFO maintained?",
        ],
        "common_problems": [
            {
                "issue": "THC degrading to CBN",
                "cause": "Heat, light, oxygen, or time",
                "solution": "Darkness, cool temps (60°F), minimal oxygen. ~5%/year baseline.",
            },
            {
                "issue": "Terpene loss",
                "cause": "Temps above 70°F, oxygen exposure, frequent opening",
                "solution": "Keep below 65°F. Nitrogen-sealed containers. Minimize opening.",
            },
            {
                "issue": "Mold in storage",
                "cause": "Humidity above 65% or improper dry/cure",
                "solution": "Verify 58-62% RH before sealing. Remove affected material immediately.",
            },
            {
                "issue": "Weight loss",
                "cause": "Normal moisture equilibration (1-3% first month)",
                "solution": "Boveda/Integra packs minimize loss. Sealed containers essential.",
            },
        ],
        "training": [],
        "transition_signals": ["N/A — terminal stage"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Storage is always indoor."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Indoor controlled environment.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Do NOT store in greenhouse."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Climate-controlled indoor space only.",
            },
        },
        "commercial_scale": {
            "container_progression": {
                "home_small": "Mason jars with Boveda packs",
                "home_large": "Grove bags or CVault containers",
                "commercial_small": "Nitrogen-sealed grove bags (1 lb units)",
                "commercial_medium": "Turkey bags in sealed bins, nitrogen-flushed",
                "commercial_large": "Nitrogen-flushed drums (5-50 lb) in vault",
                "industrial": "Climate-controlled vault, nitrogen generators, automated monitoring",
            },
            "degradation_timeline": {
                "0_3_months": "Peak quality. Minimal degradation.",
                "3_6_months": "Slight terpene reduction (~10-15%). Potency stable.",
                "6_12_months": "Noticeable terpene loss (~20-30%). THC down ~5%.",
                "12_18_months": "Significant decline. Process into extracts.",
                "18_plus_months": "Convert to extracts, edibles, or topicals.",
            },
            "testing_schedule": {
                "initial": "Full panel at harvest",
                "30_days": "Potency + terpenes (post-cure baseline)",
                "90_days": "Potency + terpenes + microbials",
                "180_days": "Full panel retest",
                "360_days": "Full panel — sell, process, or destroy decision",
            },
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT CHECKLIST
# ─────────────────────────────────────────────────────────────────────────────

RDWC_EQUIPMENT: list[dict] = [
    # Essentials
    {
        "name": "Central Control Reservoir (20-50 gal)",
        "category": "essential",
        "description": "The heart of RDWC. Where you mix nutrients, adjust pH/EC, and manage the entire system. Larger = more stable. Food-safe, opaque, dark-colored.",
    },
    {
        "name": "Site Buckets (5-10 gal each)",
        "category": "essential",
        "description": "One per plant. Connected to central res via supply and return plumbing. 5-gal minimum, 10-gal preferred.",
    },
    {
        "name": "Water Pump (submersible)",
        "category": "essential",
        "description": "Pumps from central res to site buckets. Size at 2x total flow demand. Example: 4 sites × 100 GPH = 400 GPH demand → use 800+ GPH pump.",
    },
    {
        "name": "Plumbing (PVC or vinyl tubing)",
        "category": "essential",
        "description": "Supply lines (pump → sites) and return lines (sites → central res). Use opaque black tubing. PVC is more durable. Vinyl is easier to install.",
    },
    {
        "name": "Bulkhead Fittings or Uniseals",
        "category": "essential",
        "description": "Waterproof connections through bucket walls. Bulkheads are more reliable. Uniseals are cheaper. Must be leak-proof.",
    },
    {
        "name": "Ball Valves (per site)",
        "category": "essential",
        "description": "Control flow to each site individually. Essential for balancing flow and isolating sick sites.",
    },
    {
        "name": "Net Pots (6 inch)",
        "category": "essential",
        "description": "One per site bucket. Holds media and plant.",
    },
    {
        "name": "Air Pump + Air Stones",
        "category": "essential",
        "description": "Air stone in central res AND each site bucket. DO levels critical across entire system. Size air pump for total stone count.",
    },
    {"name": "Hydroton / Clay Pebbles", "category": "essential", "description": "Fill net pots. Rinse thoroughly."},
    {
        "name": "pH Pen",
        "category": "essential",
        "description": "Measure at central reservoir. Apera or BlueLab recommended.",
    },
    {"name": "EC/TDS Meter", "category": "essential", "description": "Measure at central reservoir."},
    {"name": "pH Up & pH Down", "category": "essential", "description": "Adjust at central reservoir only."},
    {
        "name": "Nutrients (GH Flora Trio)",
        "category": "essential",
        "description": "Mix in central reservoir. Recirculation distributes to all sites.",
    },
    {
        "name": "Hydroguard",
        "category": "essential",
        "description": "Add to central reservoir. Even more critical than single DWC — root rot spreads to all sites.",
    },
    {
        "name": "Grow Light",
        "category": "essential",
        "description": "Size for total canopy area (all sites combined). Target 30-40W/sqft for flower.",
    },
    {"name": "Light Timer", "category": "essential", "description": "Reliable timer for 18/6 → 12/12 schedule."},
    {"name": "Thermometer / Hygrometer", "category": "essential", "description": "Monitor grow room conditions."},
    # Recommended
    {
        "name": "Water Chiller",
        "category": "recommended",
        "description": "Controls temp for entire system from central res. Size for total system volume. Almost essential for systems >4 sites.",
    },
    {
        "name": "Auto-Top-Off System",
        "category": "recommended",
        "description": "Float valve in central res connected to a plain-water reservoir. RDWC systems consume enormous volumes — manual top-off is tedious with 4+ sites.",
    },
    {
        "name": "Inline Screen Filters",
        "category": "recommended",
        "description": "Install on return lines to catch root fragments and debris before they reach the pump.",
    },
    {
        "name": "Backup Pump",
        "category": "recommended",
        "description": "Pump failure = dead plants within hours. Keep a spare pump ready.",
    },
    {
        "name": "CalMag Supplement",
        "category": "recommended",
        "description": "Essential with RO water. Add to central reservoir.",
    },
    {
        "name": "Silica Supplement",
        "category": "recommended",
        "description": "Strengthens stems to support heavy RDWC growth.",
    },
    {"name": "SCROG Net", "category": "recommended", "description": "Trellis net spanning all sites for even canopy."},
    {
        "name": "Oscillating Fans",
        "category": "recommended",
        "description": "Air movement between sites prevents humidity pockets.",
    },
    {
        "name": "Exhaust Fan + Carbon Filter",
        "category": "recommended",
        "description": "Odor and humidity control. Size for grow room.",
    },
    # Optional
    {
        "name": "pH/EC Controller (auto-dosing)",
        "category": "optional",
        "description": "Automatically maintains pH and EC in central reservoir. Expensive but saves daily manual adjustment on large systems.",
    },
    {
        "name": "Water Level Sensor",
        "category": "optional",
        "description": "Alerts when central reservoir is low. Prevents pump running dry.",
    },
    {
        "name": "UPS/Battery Backup",
        "category": "optional",
        "description": "Keeps pump and air running during power outages. RDWC plants die faster than DWC without circulation.",
    },
    {
        "name": "Dissolved Oxygen Meter",
        "category": "optional",
        "description": "Monitor DO across the system. Target 6+ ppm.",
    },
    {
        "name": "Root Guards/Screens",
        "category": "optional",
        "description": "Mesh screens at bucket drain ports to prevent roots entering plumbing.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE CHARTS
# ─────────────────────────────────────────────────────────────────────────────

RDWC_QUICK_REFERENCE = {
    "ph_range": {"min": 5.5, "max": 6.2, "ideal": "5.8 seedling/veg, 6.0 flower"},
    "ec_by_stage": {
        "seedling": {"min": 0.2, "max": 0.5},
        "early_veg": {"min": 0.6, "max": 1.0},
        "late_veg": {"min": 0.8, "max": 1.2},
        "transition": {"min": 0.8, "max": 1.4},
        "early_flower": {"min": 1.0, "max": 1.6},
        "mid_flower": {"min": 1.2, "max": 1.8},
        "late_flower": {"min": 0.8, "max": 1.2},
        "flush": {"min": 0.0, "max": 0.2},
    },
    "water_temp_f": {"min": 65, "max": 72, "ideal": 68},
    "reservoir_change_schedule": "Every 7 days in veg, every 5 days in flower, every 3 days during flush",
    "flow_rate_guide": "100-200 GPH per site in seedling/veg, 300-500 GPH per site in flower. Pump should be 2x total demand.",
    "hydroguard_dose": "2 ml/gal at every reservoir change AND every top-off — add to central reservoir",
    "nutrient_mixing_order": [
        "Silica (if using)",
        "CalMag",
        "FloraMicro",
        "FloraGro",
        "FloraBloom",
        "Supplements",
        "pH adjust last",
    ],
    "top_off_rule": "EC rising = top off with plain pH'd water. EC dropping = top off with 1/4 strength nutrient water. Always add Hydroguard to top-off water.",
    "golden_rules": [
        "ALL adjustments at the central reservoir — never dose individual sites",
        "Flow balance is everything — check site bucket levels regularly",
        "Root rot at one site threatens ALL sites — inspect every site at every res change",
        "Pump runs 24/7 — pump failure kills plants faster than DWC (no individual air stones as backup)",
        "Air stones in central res AND every site bucket",
        "Keep a backup pump ready at all times",
        "Leak-test the entire system before every grow",
        "Ball valves on every site line — you must be able to isolate any site",
        "Auto-top-off is nearly mandatory for systems with 4+ sites",
        "Clean plumbing at every reservoir change — bloom nutrients deposit heavily",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING GUIDE
# ─────────────────────────────────────────────────────────────────────────────

RDWC_TROUBLESHOOTING: list[dict] = [
    {
        "category": "Plumbing & Flow Issues",
        "problems": [
            {
                "symptom": "Uneven water levels across site buckets",
                "diagnosis": "Flow imbalance",
                "severity": "high",
                "causes": [
                    "Ball valves not balanced",
                    "One line partially clogged",
                    "Air lock in a line",
                    "Pump losing capacity",
                ],
                "solutions": [
                    "Adjust ball valves until all site levels are equal",
                    "Flush each line individually with pressurized water",
                    "Bleed air from highest points in plumbing",
                    "Clean pump intake and impeller",
                ],
            },
            {
                "symptom": "Pump running but no flow to sites",
                "diagnosis": "Complete blockage or pump failure",
                "severity": "critical",
                "causes": ["Root mass blocking pump intake", "Main supply line clogged", "Pump impeller broken"],
                "solutions": [
                    "Check pump intake immediately — root debris is the #1 cause",
                    "Clear main supply line",
                    "Swap to backup pump (you should have one ready)",
                    "Install inline pre-filter screen to prevent future blockages",
                ],
            },
            {
                "symptom": "Leak at bulkhead fitting",
                "diagnosis": "Failed seal",
                "severity": "high",
                "causes": ["Gasket degraded", "Over-tightened and cracked the bucket", "Root pressure from inside"],
                "solutions": [
                    "Drain system and reseal with new gasket",
                    "Apply marine-grade silicone if gasket replacement isn't enough",
                    "If bucket is cracked, replace the bucket",
                ],
            },
        ],
    },
    {
        "category": "Cross-Contamination Issues",
        "problems": [
            {
                "symptom": "Root rot spreading from one site to all sites",
                "diagnosis": "Pathogen contamination via shared water",
                "severity": "critical",
                "causes": [
                    "Root rot (Pythium) at one site spread through recirculating water",
                    "Water temp too high",
                    "No beneficial bacteria",
                ],
                "solutions": [
                    "ISOLATE: Cap the affected site's lines immediately to stop circulation",
                    "TREAT: Emergency H2O2 dose (3ml/gal of 3%) to entire system — kills pathogens AND beneficial bacteria",
                    "REBUILD: After 24 hours, do full system drain and refill. Re-dose Hydroguard at 3ml/gal (50% extra)",
                    "PREVENT: Lower water temp below 70°F. Maintain Hydroguard religiously. Install a chiller if you don't have one",
                    "MONITOR: Check roots at all sites daily for 2 weeks after incident",
                ],
            },
            {
                "symptom": "Pest or mold spreading between sites",
                "diagnosis": "Shared environment + proximity",
                "severity": "high",
                "causes": [
                    "Sites close together in same tent",
                    "Shared airflow carrying spores",
                    "One infected plant touching neighbors",
                ],
                "solutions": [
                    "Treat ALL plants, not just affected ones — shared environment means all are exposed",
                    "Increase airflow between sites",
                    "Remove severely affected plants entirely — they threaten the whole system",
                ],
            },
        ],
    },
    {
        "category": "Nutrient & pH Issues",
        "problems": [
            {
                "symptom": "pH swings larger than expected",
                "diagnosis": "Normal for RDWC — large root mass drives bigger swings",
                "severity": "medium",
                "causes": [
                    "Multiple plants consuming nutrients at different rates",
                    "Large root surface area affecting water chemistry",
                    "CO2 from roots",
                ],
                "solutions": [
                    "Adjust pH gently — don't over-correct",
                    "More frequent, smaller pH adjustments",
                    "Consider a pH controller for auto-dosing on large systems",
                ],
            },
            {
                "symptom": "EC dropping rapidly between checks",
                "diagnosis": "Multiple hungry plants depleting nutrients fast",
                "severity": "medium",
                "causes": ["Multiple plants in peak growth or flower", "Under-concentrated nutrient solution"],
                "solutions": [
                    "Top off with nutrient water (1/4 to 1/2 strength) instead of plain water",
                    "More frequent reservoir changes with fresh full-strength solution",
                    "Increase central reservoir size for more buffer",
                ],
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLED CONFIG EXPORT
# ─────────────────────────────────────────────────────────────────────────────

RDWC_CONFIG: dict = {
    "grow_type_id": "rdwc",
    "version": "1.0.0",
    "stages": RDWC_STAGES,
    "equipment": RDWC_EQUIPMENT,
    "quick_reference": RDWC_QUICK_REFERENCE,
    "troubleshooting": RDWC_TROUBLESHOOTING,
    "total_grow_days": {
        "min": 90,
        "max": 150,
        "typical_photo": 120,
        "typical_auto": 80,
        "breakdown": "Germination (3-7d) + Seedling (7-14d) + Veg (28-63d) + Flower (56-70d) + Dry (7-14d) + Cure (14-60d)",
    },
}
