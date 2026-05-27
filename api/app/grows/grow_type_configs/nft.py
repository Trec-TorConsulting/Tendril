"""NFT (Nutrient Film Technique) — Complete grow type configuration.

Enterprise-grade configuration for NFT systems where plants sit in sloped
channels with a thin, continuously flowing film of nutrient solution.  The
defining characteristic is **zero buffer time** — pump failure means roots
dry in 2-5 minutes, making system reliability and redundancy the #1 concern.

Key NFT differences from DWC/RDWC:
  - Thin nutrient film (2-4mm depth) flows continuously through channels
  - Pump failure = death in minutes (no standing water reservoir at roots)
  - Root mat management (roots can block channel flow — the #1 NFT problem)
  - Channel slope engineering (1:30 to 1:40 gradient)
  - Salt accumulation along channel length (end-of-channel plants get higher EC)
  - Seedlings started in rockwool cubes, transferred to channel when roots are ready
  - Multi-channel balancing and flow uniformity
  - Channel length limits (10-12 ft max for even EC distribution)

Supports three environment types (matching Tent.environment_type):
  - indoor  (default — full environmental control, artificial light)
  - outdoor (no climate control, natural photoperiod, weather exposure)
  - greenhouse (partial climate control, natural + supplemental light)
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in an NFT grow
# ─────────────────────────────────────────────────────────────────────────────

NFT_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Seed cracks open and taproot emerges. For NFT, always start seeds in rockwool cubes (not directly in channels). The cube will travel with the plant into the channel later. Use 1.5-inch rockwool starter cubes, pre-soaked in pH 5.5 water.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Keep seeds in darkness. Heat mat at 78°F. No light until sprout emerges. Rockwool cubes in a humidity dome.",
        },
        "channel": {
            "flow_rate_lpm": 0,
            "film_depth_mm": 0,
            "channel_slope": None,
            "notes": "Seeds are NOT in channels yet. They are in rockwool cubes in a propagation tray. Do not place seeds directly in NFT channels.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 5.8, "target": 5.5},
            "ec": {"min": 0.0, "max": 0.0, "target": 0.0},
            "ppm_500": {"min": 0, "max": 0, "target": 0},
            "water_temp_f": {"min": 68, "max": 75, "target": 72},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "notes": "No reservoir running yet. Pre-soak rockwool cubes in pH 5.5 plain water. System should be assembled, leak-tested, and slope-verified while seeds germinate.",
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
                "name": "Soak rockwool cubes",
                "description": "Pre-soak 1.5-inch starter cubes in pH 5.5 water for 1 hour. Shake out excess — cubes should be moist, not dripping. Never squeeze rockwool.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Plant seeds",
                "description": "Place one seed per cube, pointy end down, 1/4 inch deep. Cover with a small piece of torn rockwool. Place cubes in propagation tray with humidity dome.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for taproot",
                "description": "After 24-72 hours, look for white taproot emerging from bottom of cube. Do NOT disturb the cube — just look.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Leak-test NFT system",
                "description": "While seeds germinate: run the pump, verify slope, check for leaks at channel joints and end caps. Fix everything now — you cannot fix leaks with plants in channels.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Verify channel slope",
                "description": "Use a level. Target 1:30 to 1:40 slope (approximately 1 inch drop per 3 feet). Too steep = film too thin. Too flat = pooling and root drowning.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Has the seed cracked open?",
            "Is the taproot visible and white?",
            "Is the rockwool cube moist but not dripping?",
            "Temperature at 75-80°F?",
            "Is the NFT system leak-tested and slope-verified?",
        ],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Too cold, rockwool too wet, or bad seed",
                "solution": "Ensure 75-80°F. Rockwool should be moist not soaking. Try a different seed after 7 days.",
            },
            {
                "issue": "Rockwool pH too high",
                "cause": "Rockwool is naturally alkaline (~7.0)",
                "solution": "Pre-soak in pH 5.5 water for at least 1 hour. This is mandatory for NFT rockwool starts.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Taproot visible through bottom of cube",
            "Sprout emerging from top of cube",
            "First set of cotyledon leaves visible",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Start seeds indoors regardless. NFT seedlings are too fragile for outdoor conditions. Transfer to outdoor channels only after roots are well established.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always germinate indoors for NFT.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse germination: use a heat mat and humidity dome. Greenhouse temps may swing too much without supplemental heating.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Use heat mat in greenhouse for consistent germ temps.",
            },
        },
    },
    # ── 2. SEEDLING (PROPAGATION TRAY) ───────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling (Propagation Tray)",
        "order": 2,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Seedling grows in rockwool cube on a propagation tray with gentle nutrient film or hand-watering. NOT in main NFT channels yet. Roots must grow through the bottom of the cube and be at least 3 inches long before channel placement. This propagation phase is critical for NFT — placing seedlings in channels too early means roots can't reach the film.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 65, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 250, "target": 200},
            "light_dli": {"min": 6, "max": 16, "target": 13},
            "notes": "Keep under gentle light (T5 fluorescent or LED at low power). Humidity dome for first 3-5 days, then remove to harden off. Seedling needs to develop strong roots BEFORE entering the channel.",
        },
        "channel": {
            "flow_rate_lpm": 0,
            "film_depth_mm": 0,
            "channel_slope": None,
            "notes": "Seedlings are NOT in main channels yet. They stay on the propagation tray until roots are 3+ inches through the cube bottom. Some growers use a small nursery NFT channel for propagation.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.2, "max": 0.5, "target": 0.3},
            "ppm_500": {"min": 100, "max": 250, "target": 150},
            "water_temp_f": {"min": 68, "max": 75, "target": 72},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "If hand-watering cubes: use very dilute nutrient solution. If using a nursery tray with recirculating film: run at 0.3 EC. Main system reservoir should be mixed and ready for when seedlings are transferred.",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "Very light feeding. Seedlings are tiny and in rockwool — they need almost nothing. Hand-water cubes with dilute solution every 1-2 days, or run a gentle recirculating nursery tray.",
            "flora_micro_ml_per_gal": 0.625,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 0.3125,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Protect young roots from Pythium. Critical even at propagation stage.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Water/feed cubes",
                "description": "Hand-water rockwool cubes with 1/4 strength nutrient solution when top of cube feels dry. Do NOT let cubes sit in standing water.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check root growth",
                "description": "Gently lift cube and check for roots emerging from the bottom. Roots must be 3+ inches before channel placement.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Harden off from dome",
                "description": "Days 3-5: crack the humidity dome lid. Days 5-7: remove dome entirely. Seedlings need to acclimate to ambient humidity before channel life.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Monitor for stretch",
                "description": "If seedlings are stretching (tall thin stems), light is too far away. Lower light or increase intensity.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Run main NFT system empty",
                "description": "Run pump and flow through main channels with plain pH'd water. Verify flow rate at each channel. Fix any issues before adding plants.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are roots emerging from the bottom of the rockwool cube?",
            "Are cotyledon leaves healthy and green?",
            "First true leaves appearing?",
            "Stem sturdy (not thin and stretching)?",
            "Rockwool cube moist but not waterlogged?",
        ],
        "common_problems": [
            {
                "issue": "Seedling stretching (tall, thin stem)",
                "cause": "Light too far away or too dim",
                "solution": "Lower light to 6-8 inches. Increase intensity. Support stretched seedlings with a small stake.",
            },
            {
                "issue": "Roots not emerging from cube",
                "cause": "Cube too wet (roots don't need to search for water) or too dry",
                "solution": "Let cube dry slightly between waterings. Roots grow when searching for moisture. Check cube isn't sitting in standing water.",
            },
            {
                "issue": "Algae on rockwool surface",
                "cause": "Light hitting wet rockwool",
                "solution": "Cover cube tops with hydroton or a small piece of black plastic. Block light from reaching wet surfaces.",
            },
            {
                "issue": "Damping off (stem collapses at soil line)",
                "cause": "Fungal infection from too much moisture",
                "solution": "Improve airflow. Reduce watering. Remove dome if still on. Discard affected seedlings — damping off is fatal.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Roots 3+ inches through bottom of cube",
            "2-3 sets of true leaves",
            "Stem sturdy enough to handle",
            "Seedling 3-4 inches tall",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Keep seedlings indoors until they have strong root systems. Outdoor NFT channels have more temperature variation — seedlings need robust roots to survive.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Propagate indoors, transfer to outdoor channels only when roots are well developed.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse propagation works well. Use shade cloth if light is too intense for seedlings.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse propagation: protect from intense midday sun.",
            },
        },
    },
    # ── 3. EARLY VEG (CHANNEL PLACEMENT) ─────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Veg (Channel Placement)",
        "order": 3,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Transfer seedlings from propagation tray into NFT channels. This is the most critical transition in NFT growing. Roots must immediately contact the nutrient film. Place rockwool cube into net pot, set in channel hole. Roots grow into the film and begin rapid vegetative growth. Flow rate starts low and increases as root mass develops.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 55, "max": 70, "target": 65},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 250, "max": 450, "target": 350},
            "light_dli": {"min": 16, "max": 29, "target": 23},
            "notes": "Ramp up light intensity as plants establish in channels. Slightly higher humidity during first few days after transplant helps reduce transplant shock.",
        },
        "channel": {
            "flow_rate_lpm": {"min": 0.5, "max": 1.0, "target": 0.75},
            "film_depth_mm": {"min": 2, "max": 4, "target": 3},
            "channel_slope": "1:30 to 1:40 (1 inch drop per 30-40 inches of channel length)",
            "notes": "Start with lower flow rate. Young roots are delicate — too much flow can wash them down-channel. Film should just barely cover the bottom of the channel. Verify that the film reaches each plant position.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.6, "max": 1.0, "target": 0.8},
            "ppm_500": {"min": 300, "max": 500, "target": 400},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "First time running system with plants. Monitor pH closely — will swing more with young plants. Aerate reservoir heavily. NFT reservoir should be 2-3x the volume of the total channel capacity for stability.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half strength. Plants are establishing in channels and ramping up nutrient uptake. Too strong = burns delicate new root tips touching the film for the first time.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root protection during the vulnerable transplant phase.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Place seedlings in channels",
                "description": "Set rockwool cube into net pot → into channel hole. Roots MUST hang below the net pot and touch the flowing film. If roots are too short, wait longer in propagation.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Verify film contact at all positions",
                "description": "After placement, check every plant position. The film must flow past each set of roots. Adjust flow rate if any position is dry.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check pH/EC",
                "description": "Daily. New plants in channels will cause pH and EC swings. Adjust gently at the reservoir.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor transplant stress",
                "description": "Some wilting in the first 24-48 hours is normal. If wilting persists beyond 48 hours, check that roots are in the film and flow is adequate.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Reservoir change",
                "description": "Full change every 7 days. Drain reservoir, clean if needed, refill with fresh solution.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Check flow at end of channel",
                "description": "Verify nutrient solution is flowing out the drain end of every channel. If flow stops, roots may already be blocking.",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Are all plant positions receiving film flow?",
            "New growth visible within 3-5 days of channel placement?",
            "Root tips extending into the film?",
            "Any signs of transplant shock beyond 48 hours?",
            "pH stable within range?",
        ],
        "common_problems": [
            {
                "issue": "Seedling wilting after channel placement",
                "cause": "Roots not reaching the film, or flow too low at that position",
                "solution": "Check root contact with film. Increase flow slightly. Verify slope is correct — flat spots cause flow gaps.",
            },
            {
                "issue": "Film not reaching all plant positions",
                "cause": "Flow rate too low, channel not level side-to-side, or slope issues",
                "solution": "Increase pump output. Level channel side-to-side (must be perfectly flat laterally). Check for leaks reducing flow.",
            },
            {
                "issue": "Roots washing down-channel",
                "cause": "Flow rate too high for young roots",
                "solution": "Reduce flow rate. Young roots need gentle flow. Increase gradually as roots establish.",
            },
            {
                "issue": "Algae growing in channels",
                "cause": "Light reaching the nutrient film through channel holes or gaps",
                "solution": "Block all light entry. Use neoprene inserts around net pots. Cover unused holes. Use opaque channel material.",
            },
        ],
        "training": [
            {
                "technique": "Low-Stress Training (LST)",
                "when": "Once plant has 4-5 nodes",
                "description": "Bend and tie down main stem to expose lower branches to light. Start gentle — NFT plants are anchored only by the net pot, not buried media.",
            },
        ],
        "transition_signals": [
            "Plant showing vigorous new growth",
            "Roots visibly growing along channel bottom",
            "4-5 nodes on main stem",
            "No signs of transplant stress",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor channel placement: do this in the evening or on a cloudy day to reduce transplant shock. Protect channels from direct rain — rain dilutes the film and disrupts flow.",
                },
                "extra_tasks": [
                    {
                        "name": "Shade new transplants",
                        "description": "Provide shade cloth for 2-3 days after channel placement. Full sun + transplant shock can kill seedlings.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Rain flooding channels",
                        "cause": "Outdoor rain entering open channel holes",
                        "solution": "Use rain covers over channels. Neoprene collars around net pots help. Never run NFT channels without rain protection outdoors.",
                    },
                ],
                "notes": "Outdoor NFT: rain protection for channels is mandatory.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse channel placement: good environment for transplant. Temperature may be warmer — ensure adequate ventilation.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse NFT: ideal transplant environment with natural light.",
            },
        },
    },
    # ── 4. LATE VEG ──────────────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Veg",
        "order": 4,
        "duration_days": {"min": 14, "max": 35, "typical": 21},
        "description": "Rapid vegetative growth. Plants double or triple in size. Root mats develop along channel bottoms — this is where NFT gets tricky. Roots will naturally form a mat that can restrict or block flow entirely. Monitor flow at the drain end of every channel. Increase flow rate as root mass grows.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 65, "target": 55},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 600, "target": 500},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Full veg light. Plants growing fast. Channel root mats becoming significant. Watch for flow restriction.",
        },
        "channel": {
            "flow_rate_lpm": {"min": 1.0, "max": 2.0, "target": 1.5},
            "film_depth_mm": {"min": 2, "max": 4, "target": 3},
            "channel_slope": "1:30 to 1:40",
            "notes": "Increase flow rate as root mass grows. Root mats will restrict flow — you may need to increase pump output to maintain target flow at the drain end. Check drain flow rate DAILY. If flow at the drain drops below 50% of inlet flow, roots are blocking.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.8, "max": 1.4, "target": 1.0},
            "ppm_500": {"min": 400, "max": 700, "target": 500},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "Plants consuming more now. EC will drop faster between checks. Reservoir size matters — larger reservoir = more stability. Change weekly. Aerate heavily.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Three-quarter strength for active vegetative growth. Nitrogen-heavy ratio. Plants in NFT channels have direct root contact with nutrients — they feed efficiently.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 1.875,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root zone protection. Root mats in NFT are dense — perfect environment for Pythium if water temp rises.",
                },
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Strengthen stems. NFT plants can grow fast and may be less structurally strong without heavy media anchoring.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check drain flow (all channels)",
                "description": "MOST IMPORTANT NFT TASK. Measure or visually verify flow at the drain end of every channel. If flow is reduced, root mats are blocking. Immediate action needed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check pH/EC",
                "description": "Daily at reservoir. Vigorous veg = high nutrient consumption.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Reservoir change",
                "description": "Full change every 7 days.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Check for root mat blockage",
                "description": "Gently lift a net pot and check roots. Healthy root mat is white and flows along the channel. Brown/slimy roots or standing water behind the root mass = problem.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "EC inlet vs drain check",
                "description": "Measure EC at inlet and drain end of each channel. If drain EC is significantly higher than inlet (>0.3 EC difference), salt is accumulating along the channel.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Training (LST/topping)",
                "description": "Top plants and train horizontal to fill the channel canopy. NFT plants have less anchoring than soil — use plant ties and clips, not weights.",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Check pump and backup",
                "description": "Verify pump running at rated capacity. Test backup pump monthly. Pump failure = root death in minutes.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Is flow reaching the drain end of every channel?",
            "Roots white and healthy (not brown or slimy)?",
            "Vigorous new growth visible?",
            "EC difference between inlet and drain acceptable (<0.3)?",
            "Pump running reliably?",
        ],
        "common_problems": [
            {
                "issue": "Reduced flow at drain end of channel",
                "cause": "Root mat blocking flow — the #1 NFT problem",
                "solution": "Gently lift root mat and flush debris. Increase pump flow rate. For severe blockage: temporarily remove plants, flush channel, replace. Consider root trimming for aggressive root growers.",
            },
            {
                "issue": "Standing water pooling behind root mass",
                "cause": "Root mat acting as a dam",
                "solution": "This is dangerous — standing water in NFT leads to root rot. Clear the blockage immediately. Lift roots, restore flow. May need to trim roots.",
            },
            {
                "issue": "Salt crusting at end of channels",
                "cause": "Nutrient concentration increasing along channel length",
                "solution": "Flush channels with plain pH'd water every 3-4 days. Reduce channel length if persistent. Move to bi-directional flow if available.",
            },
            {
                "issue": "Plant falling over in channel",
                "cause": "NFT provides no structural support — plant anchored only by net pot and roots",
                "solution": "Use plant yoyos, clips, or a trellis net over the channels. Silica supplement strengthens stems.",
            },
        ],
        "training": [
            {
                "technique": "Topping",
                "when": "At 5th-6th node",
                "description": "Cut main stem above 5th node to create two main colas. NFT's even nutrient delivery grows both colas equally.",
            },
            {
                "technique": "LST (Low-Stress Training)",
                "when": "Ongoing throughout veg",
                "description": "Bend and tie branches to spread canopy along the channel. Use soft plant ties — do not weight branches (no media to anchor weights).",
            },
            {
                "technique": "SCROG Net",
                "when": "Once plants reach trellis height",
                "description": "Trellis net above channels provides structural support NFT plants need and creates even canopy.",
            },
        ],
        "transition_signals": [
            "Desired height/spread reached",
            "Strong branching structure established",
            "Root mat healthy but manageable",
            "Ready for 12/12 light switch",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor veg: natural photoperiod controls veg length (will flower when days shorten below ~14 hours). Monitor weather — heavy rain can flood channels.",
                },
                "extra_tasks": [
                    {
                        "name": "Check channel covers after rain",
                        "description": "Verify rain hasn't entered channels and diluted nutrient solution. Check reservoir EC after any rain event.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Insects entering channels",
                        "cause": "Open channel holes attract pests seeking moisture",
                        "solution": "Neoprene collars on all net pot holes. Inspect channels for pests weekly. Diatomaceous earth around channel supports.",
                    },
                ],
                "notes": "Outdoor NFT: rain and pest protection for channels is essential.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse veg: excellent growth with natural light. Supplemental lighting extends veg period if desired. Ventilate to prevent excessive heat near channel surfaces.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse NFT: ventilation prevents heat buildup at channel level.",
            },
        },
    },
    # ── 5. TRANSITION (FLIP TO FLOWER) ───────────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Flip to Flower)",
        "order": 5,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Light flips to 12/12. The plant stretches 50-200% in height during this period. In NFT, the stretch phase is when root mats grow most aggressively — channel flow management becomes critical. Root mass can double during transition. Nutrient ratio shifts from nitrogen-heavy to phosphorus/potassium-heavy.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 64, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 60, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 550},
            "light_dli": {"min": 17, "max": 30, "target": 24},
            "notes": "Switch to 12/12. Dark period must be UNINTERRUPTED — any light leak during dark period can cause hermaphrodites or revert to veg. Stretch will be dramatic. Have support structures ready.",
        },
        "channel": {
            "flow_rate_lpm": {"min": 1.5, "max": 2.0, "target": 1.75},
            "film_depth_mm": {"min": 2, "max": 4, "target": 3},
            "channel_slope": "1:30 to 1:40",
            "notes": "Root mass grows aggressively during stretch. Increase flow rate proactively — don't wait for blockage. Check drain flow twice daily during transition. This is the peak period for root mat development.",
        },
        "reservoir": {
            "ph": {"min": 5.6, "max": 6.2, "target": 5.9},
            "ec": {"min": 0.8, "max": 1.4, "target": 1.1},
            "ppm_500": {"min": 400, "max": 700, "target": 550},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 7,
            "hydroguard_ml_per_gal": 2,
            "notes": "Transition nutrient mix — shift from grow to bloom. Plants consuming heavily during stretch. Monitor EC closely. Reservoir changes every 7 days.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Shift ratio: reduce nitrogen (FloraGro), increase phosphorus/potassium (FloraBloom). Not full bloom strength yet — transition is gradual.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root mat density peaks during transition — Pythium risk increases.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Switch to 12/12 light",
                "description": "Set timer to 12 hours on / 12 hours off. Verify dark period is complete darkness — check for indicator LEDs, light leaks through vents, etc.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check drain flow (all channels)",
                "description": "TWICE daily during transition. Root mass growth accelerates dramatically. Flow restriction can develop in hours during peak stretch.",
                "interval_days": 0.5,
                "priority": "high",
            },
            {
                "name": "Increase flow rate proactively",
                "description": "Bump pump output 20-30% at the start of transition. Root mats will grow into this extra capacity within days.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check pH/EC",
                "description": "Daily. Nutrient ratio is shifting. pH may swing more during transition.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Support stretching branches",
                "description": "Plants can grow 2-4 inches per day during stretch. Trellis net or plant yoyos are essential.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Reservoir change",
                "description": "Transition from veg to bloom nutrient ratio.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Root mat inspection",
                "description": "Lift net pots and check root health. White and branching = good. Brown, slimy, or matted solid = problem.",
                "interval_days": 3,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Is the stretch progressing normally (50-200% height increase)?",
            "Flow reaching drain end of all channels?",
            "Roots white and healthy despite rapid mat growth?",
            "No light leaks during dark period?",
            "Support structures adequate for stretch growth?",
        ],
        "common_problems": [
            {
                "issue": "Flow stopped at one channel during stretch",
                "cause": "Root mat completely blocked the channel",
                "solution": "IMMEDIATE action: gently lift root mass and restore flow. If root mat is too dense, carefully trim roots at channel bottom (never more than 20%). Consider upgrading to wider channels for future grows.",
            },
            {
                "issue": "Extreme stretch (3x height)",
                "cause": "Genetics (sativa-dominant) or too much difference between light and dark temps",
                "solution": "Supercrop: gently pinch and bend stems at 90 degrees. They'll recover and form a knuckle. Works well in NFT with trellis support.",
            },
            {
                "issue": "Pre-flowers not appearing after 2 weeks of 12/12",
                "cause": "Light leak during dark period, or plant still acclimating",
                "solution": "Check EVERY light source during dark period — indicator LEDs, phone charging lights, light through cracks. Even brief light exposure can prevent flowering.",
            },
        ],
        "training": [
            {
                "technique": "Supercropping",
                "when": "If plants stretch excessively",
                "description": "Pinch and bend stems at 90 degrees. The stem heals with a reinforced knuckle and the height is controlled.",
            },
            {
                "technique": "Lollipop (lower defoliation)",
                "when": "End of stretch (day 10-14)",
                "description": "Remove all growth below the bottom 1/3 of the plant. These sites won't produce quality buds. Directs energy to top buds and improves airflow in channels.",
            },
        ],
        "transition_signals": [
            "Stretch slowing down",
            "Pre-flowers (pistils) visible at nodes",
            "Nutrient demand shifting to bloom",
            "Root mat growth rate stabilizing",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor NFT: photoperiod plants flower naturally as days shorten. No light switch needed. Transition happens over 2-3 weeks instead of abruptly. Monitor root growth closely during this period.",
                },
                "extra_tasks": [
                    {
                        "name": "Protect from light pollution",
                        "description": "Street lights, porch lights, even a bright moon can disrupt flowering. Shield channels and plants from any artificial light at night.",
                        "interval_days": 3,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor: natural photoperiod triggers transition more gradually.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse transition: use blackout curtains for 12-hour dark periods if greenhouse has any light leaks.",
                },
                "extra_tasks": [
                    {
                        "name": "Deploy blackout curtains",
                        "description": "Ensure 12 hours of complete darkness. Greenhouse light leaks from nearby structures or passing cars can prevent flowering.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse: blackout system critical for reliable flowering.",
            },
        },
    },
    # ── 6. EARLY FLOWER ──────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Stretch ends, bud sites established, first pistils (white hairs) visible at every node. Nutrient demand shifts fully to bloom (P/K heavy). Root mats are now at their maximum density in NFT channels — flow management is critical. NFT's continuous nutrient delivery produces excellent early bud development.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 80, "target": 77},
            "temp_night_f": {"min": 62, "max": 72, "target": 67},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 800, "target": 650},
            "light_dli": {"min": 22, "max": 35, "target": 28},
            "notes": "Increase light intensity for flower. Drop humidity below 55% — bud rot prevention starts now. Temperature differential (day vs night) enhances terpene development.",
        },
        "channel": {
            "flow_rate_lpm": {"min": 1.5, "max": 2.0, "target": 2.0},
            "film_depth_mm": {"min": 2, "max": 4, "target": 3},
            "channel_slope": "1:30 to 1:40",
            "notes": "Maximum flow rate. Root mats are at peak density. If you haven't already increased pump output, do it NOW. Flow restriction during flower means nutrient deficiencies that directly impact bud development.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 1.0, "max": 1.6, "target": 1.3},
            "ppm_500": {"min": 500, "max": 800, "target": 650},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "notes": "Switch to 5-day reservoir changes during flower. Bloom nutrients cause more salt buildup in channels. Aerate reservoir heavily — O2 demand increases with root mass.",
        },
        "nutrients": {
            "strength_pct": 80,
            "approach": "Full bloom transition. Heavy phosphorus and potassium. Reduce nitrogen. NFT delivers nutrients directly to roots — plants respond quickly to ratio changes.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.625,
            "flora_bloom_ml_per_gal": 2.5,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Dense root mats + warm temps + bloom organics = high Pythium risk.",
                },
                {
                    "name": "PK Booster (Liquid Koolbloom)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Start PK supplementation as bud sites develop. Begin at half dose.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check drain flow (all channels)",
                "description": "Daily. Root mats at maximum density. Any flow reduction = immediate attention. Bud development depends on consistent nutrient delivery.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check pH/EC",
                "description": "Daily. Bloom nutrients and heavy feeding cause faster pH and EC swings.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Reservoir change",
                "description": "Every 5 days during flower. Flush channels with plain water during each change to remove salt buildup.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Inspect roots at 2-3 channel positions",
                "description": "Lift net pots. Roots should be white with branching. Brown/slimy = rot starting. Act immediately if any site shows rot.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Defoliation (Day 21)",
                "description": "Day 21 of flower: remove large fan leaves blocking bud sites. Improves light penetration and airflow through the channel canopy.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Flush channels with plain water",
                "description": "At each reservoir change, run plain pH'd water through channels for 15-30 minutes before adding nutrient solution. Clears salt deposits.",
                "interval_days": 5,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Bud sites developing at all nodes?",
            "White pistils visible at every bud site?",
            "Flow reaching all channel positions?",
            "Root mats healthy (white, not brown)?",
            "Humidity consistently below 55%?",
        ],
        "common_problems": [
            {
                "issue": "Uneven bud development along channel",
                "cause": "EC gradient — plants at channel end receiving higher concentration",
                "solution": "Flush channels more frequently. Increase flow rate. Reduce channel length for future grows. Monitor EC at inlet vs drain.",
            },
            {
                "issue": "Root rot in one channel position",
                "cause": "Local flow restriction creating stagnant zone behind root mat",
                "solution": "Clear blockage immediately. Treat system with H2O2 (3ml/gal of 3%) for 24 hours, then re-dose Hydroguard. Monitor all other positions.",
            },
            {
                "issue": "Salt crust on channel walls",
                "cause": "Bloom nutrients depositing between the film line and channel edge",
                "solution": "Flush channels during every reservoir change. Use a soft brush to clean channel walls at res changes.",
            },
            {
                "issue": "Plant toppling over",
                "cause": "Heavy flower development with no structural support from media",
                "solution": "SCROG net is essential for NFT flower. Plant yoyos for individual branches. Silica supplement strengthens stems.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation (Day 21)",
                "when": "Day 21 of flower (~week 3)",
                "description": "Remove large fan leaves blocking bud sites. Opens canopy for light and airflow. Don't over-defoliate — leave sugar leaves near buds.",
            },
        ],
        "transition_signals": [
            "Buds forming at all sites",
            "Pistils clustering densely",
            "Stretch fully stopped",
            "Nutrient demand increasing",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor early flower: protect buds from rain. NFT channels must have rain covers. Wet buds + warm temps = bud rot.",
                },
                "extra_tasks": [
                    {
                        "name": "Install rain covers",
                        "description": "Cover channels and canopy to prevent rain from hitting bud sites. This is mandatory for outdoor NFT in flower.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Caterpillars/budworms in outdoor buds",
                        "cause": "Moths laying eggs on flowers",
                        "solution": "BT (Bacillus thuringiensis) spray weekly. Inspect buds for frass (caterpillar droppings).",
                    },
                ],
                "notes": "Outdoor NFT in flower: rain protection is non-negotiable.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse early flower: run dehumidifier to keep humidity below 55%. Greenhouse traps moisture from multiple transpiring plants.",
                },
                "extra_tasks": [
                    {
                        "name": "Run dehumidifier",
                        "description": "Keep humidity below 55% during flower. Dense NFT canopies above channels trap moisture.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Greenhouse NFT in flower: dehumidification is critical.",
            },
        },
    },
    # ── 7. MID FLOWER (BULK PHASE) ────────────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Bulk Phase)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 21},
        "description": "Peak bud production. Buds swell rapidly and pack on weight. NFT's continuous nutrient delivery produces excellent bud density. Water and nutrient consumption hits maximum. Root mats are fully established — flow management is a daily battle. Salt accumulation in channels accelerates with heavy bloom nutrients.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 78, "target": 76},
            "temp_night_f": {"min": 60, "max": 70, "target": 66},
            "humidity_pct": {"min": 40, "max": 50, "target": 45},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
            "notes": "Maximum light intensity. Drop humidity to 45% to prevent bud rot. Temperature differential (day/night) enhances terpene and color production.",
        },
        "channel": {
            "flow_rate_lpm": {"min": 1.5, "max": 2.5, "target": 2.0},
            "film_depth_mm": {"min": 2, "max": 5, "target": 3},
            "channel_slope": "1:30 to 1:40",
            "notes": "Peak flow demand. Root mats may need flow rates above the standard 2 LPM range. If drain flow drops below 50% of inlet, increase pump output immediately. Salt deposits accelerate — flush channels at every reservoir change.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 1.2, "max": 1.8, "target": 1.5},
            "ppm_500": {"min": 600, "max": 900, "target": 750},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "notes": "Peak consumption. Multiple large flowering plants can consume reservoir quickly. Top off between changes. Reservoir change every 5 days — flush channels with plain water during each change.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full bloom strength. Maximum phosphorus and potassium. NFT delivers peak nutrition directly to roots. Watch for slight tip burn — that means plants are at maximum capacity (optimal).",
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
                    "purpose": "Peak PK supplementation for bud density.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Check drain flow (all channels)",
                "description": "Daily — CRITICAL. Root mats + salt buildup + heavy bloom nutrients = maximum flow restriction risk. Any reduction = immediate action.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check pH/EC",
                "description": "Daily at reservoir. Peak consumption means fast EC drops.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Top off reservoir",
                "description": "May need daily top-offs. Multiple large flowering plants consume heavily.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Reservoir change + channel flush",
                "description": "Every 5 days. Run plain pH'd water through channels for 30 minutes before refilling with nutrient solution.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "EC inlet vs drain check",
                "description": "Measure EC at both ends of each channel. If drain EC is >0.5 higher than inlet, salt accumulation is excessive — flush more frequently.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Bud rot inspection",
                "description": "Check all bud sites for brown/gray rot. Dense NFT canopies trap humidity. Part dense buds and look inside.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Support heavy branches",
                "description": "NFT plants have zero media anchoring. Heavy buds will topple plants without SCROG net or yoyos. Check support daily.",
                "interval_days": 2,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Flow reaching drain end of all channels?",
            "Buds swelling uniformly across all channel positions?",
            "Trichomes milky/clear under loupe?",
            "Root mats healthy (white, not brown)?",
            "Any signs of bud rot?",
            "Branches adequately supported?",
        ],
        "common_problems": [
            {
                "issue": "Reservoir depleting within hours",
                "cause": "Peak flower consumption from multiple large plants",
                "solution": "Install auto-top-off float valve. Upgrade to a larger reservoir (3-5x channel volume minimum).",
            },
            {
                "issue": "Salt crust severely restricting flow",
                "cause": "Heavy bloom nutrients depositing in channels, especially at root mat edges",
                "solution": "Flush channels with plain water at EVERY reservoir change. Use soft brush during changes. Consider mid-week flush.",
            },
            {
                "issue": "Bud rot at one channel position",
                "cause": "Humidity pocket, dense bud, poor airflow at that position",
                "solution": "Remove ALL affected material (cut 2 inches below rot). Increase airflow. Lower room humidity. Check all other positions.",
            },
            {
                "issue": "Plant toppling in channel",
                "cause": "Heavy buds + no structural media support",
                "solution": "SCROG net is mandatory for NFT in mid flower. Add individual plant yoyos. Silica supplement strengthens stems.",
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
                    "notes": "Outdoor mid flower: rain protection over channels and canopy is absolutely mandatory. Rain + dense buds = bud rot.",
                },
                "extra_tasks": [
                    {
                        "name": "Shake plants after rain/dew",
                        "description": "Gently shake each plant in the morning to remove dew from buds.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Morning dew causing bud rot",
                        "cause": "Outdoor humidity + dew on dense flower clusters",
                        "solution": "Shake plants mornings. Add fans if power available. Defoliate for airflow.",
                    },
                ],
                "notes": "Outdoor NFT mid flower: dew and rain are the primary threats.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: run dehumidifier 24/7 during mid flower.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse NFT mid flower: dehumidification is critical.",
            },
        },
    },
    # ── 8. LATE FLOWER (RIPENING) ─────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Final bud maturation and trichome ripening. Reduce nutrients. Trichomes transition from clear→cloudy→amber. In NFT, reduced nutrient strength means less salt accumulation — channels stay cleaner. Flow management eases slightly as plants consume less.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 74},
            "temp_night_f": {"min": 58, "max": 68, "target": 64},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 800},
            "light_dli": {"min": 26, "max": 39, "target": 35},
            "notes": "Cooler temps + large day/night differential enhances color and terpene production. NFT's continuous delivery helps all plants ripen at similar rates.",
        },
        "channel": {
            "flow_rate_lpm": {"min": 1.5, "max": 2.0, "target": 2.0},
            "film_depth_mm": {"min": 2, "max": 4, "target": 3},
            "channel_slope": "1:30 to 1:40",
            "notes": "Maintain flow. Root mats are established but stable. Reduced nutrients mean less salt buildup. Continue monitoring drain flow.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 0.8, "max": 1.2, "target": 1.0},
            "ppm_500": {"min": 400, "max": 600, "target": 500},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "notes": "Reduce nutrient strength. Plants are finishing. Water consumption decreases slightly. Continue 5-day reservoir changes.",
        },
        "nutrients": {
            "strength_pct": 60,
            "approach": "Reduced strength. Taper down nutrients. Stop PK boosters. Allow plant to use internal reserves. Yellowing fan leaves is normal and desired.",
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
                "description": "Daily. Reduced nutes, but pH management continues.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check drain flow",
                "description": "Daily. Root mats are stable but still need monitoring.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Reservoir change + channel flush",
                "description": "Continue 5-day changes with channel flushing.",
                "interval_days": 5,
                "priority": "high",
            },
            {
                "name": "Bud rot patrol",
                "description": "Dense, mature buds are most susceptible. Check all positions daily.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Remove dying fan leaves",
                "description": "Yellow/dying fan leaves are normal now. Remove to prevent mold and improve airflow.",
                "interval_days": 3,
                "priority": "low",
            },
        ],
        "health_checks": [
            "Trichome maturity progressing? (Clear → milky → amber)",
            "Fan leaves yellowing naturally?",
            "Any bud rot? Check daily.",
            "Flow stable at all channel positions?",
        ],
        "common_problems": [
            {
                "issue": "Uneven ripening along channel",
                "cause": "EC gradient effect — plants at end of channel received slightly different nutrition over time",
                "solution": "NFT: harvest by position. Cut ready plants first, leave others to ripen longer. Cap their channel holes.",
            },
            {
                "issue": "Foxtailing (new growth on buds)",
                "cause": "Light stress (too close) or heat stress",
                "solution": "Raise light slightly. Lower room temp.",
            },
            {
                "issue": "Bud rot in final week",
                "cause": "Dense mature buds + any humidity spike",
                "solution": "Harvest immediately if rot is spreading. Better slightly early than losing buds.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Trichomes 70-90% milky with 10-20% amber",
            "Pistils 70-80% brown/orange",
            "Fan leaves mostly yellow",
            "Bud growth visibly slowed",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor late flower: watch for early frost. NFT channels and plumbing freeze before air temp reaches 32°F due to thin water film. Harvest before first frost.",
                },
                "extra_tasks": [
                    {
                        "name": "Monitor frost forecast",
                        "description": "NFT is extremely frost-vulnerable — the thin film freezes quickly. Harvest before first frost. No recovery if channels freeze.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Early frost threatens system",
                        "cause": "Late-season temperature drop",
                        "solution": "Harvest immediately. NFT's thin film freezes faster than any other hydro method. No insulation can protect a running NFT system from a hard freeze.",
                    },
                ],
                "notes": "Outdoor NFT: harvest timing is frost-date-dependent.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: cool fall nights enhance colors and terpenes. Monitor for frost if unheated.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse NFT: cool nights beneficial if above freezing.",
            },
        },
    },
    # ── 9. FLUSH ──────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Run plain pH'd water through the NFT system. No nutrients. NFT is the MOST effective system for flushing — the continuous thin film washes salts from roots faster than any other method. Plants use remaining internal nutrient stores, producing cleaner-burning, better-tasting flower.",
        "environment": {
            "temp_day_f": {"min": 66, "max": 76, "target": 74},
            "temp_night_f": {"min": 58, "max": 68, "target": 64},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 800, "target": 650},
            "light_dli": {"min": 22, "max": 35, "target": 28},
            "notes": "Maintain 12/12. Environment stays the same. Continue monitoring for bud rot.",
        },
        "channel": {
            "flow_rate_lpm": {"min": 1.5, "max": 2.5, "target": 2.0},
            "film_depth_mm": {"min": 2, "max": 4, "target": 3},
            "channel_slope": "1:30 to 1:40",
            "notes": "Keep flow running at full rate. The continuous film actively washes salts from roots and channel surfaces. NFT flush is faster and more thorough than any reservoir-based system.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.2, "target": 6.0},
            "ec": {"min": 0.0, "max": 0.2, "target": 0.0},
            "ppm_500": {"min": 0, "max": 100, "target": 0},
            "water_temp_f": {"min": 65, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": {"min": 6.0, "target": 8.0},
            "change_interval_days": 3,
            "hydroguard_ml_per_gal": 2,
            "notes": "Plain pH'd water only. Change every 3 days. Continue Hydroguard — root health matters until harvest day. Monitor EC of return water — it should drop rapidly with NFT's continuous flow.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Zero nutrients. Plain pH'd water. NFT's continuous film delivers the most thorough flush of any hydro method.",
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
                "description": "Drain reservoir, refill with plain pH'd water. Run pump to flush all channels. NFT's continuous flow flushes faster than standing systems.",
                "interval_days": 3,
                "priority": "high",
            },
            {
                "name": "Monitor EC of drain water",
                "description": "Check EC of water returning from channels. Should drop rapidly toward 0. NFT typically flushes in 7 days vs 10-14 for DWC.",
                "interval_days": 2,
                "priority": "medium",
            },
            {
                "name": "Continue trichome checks",
                "description": "Plants continue maturing during flush. Check trichomes to time harvest.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor for bud rot",
                "description": "Continue daily checks. Flush period is still high-risk.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Prepare harvest equipment",
                "description": "Sharp trimming scissors, drying rack/lines, mason jars, hygrometers, Boveda packs.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Fan leaves yellowing/fading? (Expected during flush.)",
            "EC of drain water dropping?",
            "Trichomes reaching target maturity?",
            "Any bud rot?",
        ],
        "common_problems": [
            {
                "issue": "EC not dropping during flush",
                "cause": "Severe salt buildup in channel walls or root mat trapping salts",
                "solution": "Increase flow rate. Drain and refill more frequently (every 2 days). Gently agitate roots if accessible.",
            },
            {
                "issue": "Plant wilting during flush",
                "cause": "Root function declining naturally near end of life",
                "solution": "Normal. Ensure flow continues. Don't add nutrients.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Flush duration reached (7-14 days)",
            "EC of drain water near 0",
            "Trichomes at target maturity (10-20% amber)",
            "Fan leaves mostly yellow/fallen",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor flush: rain actually helps. Let rain supplement the flushing process."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: rain acceptable during flush.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse flush: maintain ventilation. Dying leaves can harbor mold."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: remove fallen leaves promptly.",
            },
        },
    },
    # ── 10. HARVEST ───────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Cut plants, trim, and hang to dry. NFT harvest advantage: plants lift cleanly from channel holes — no digging or pot removal. You can harvest individual channel positions at different times if ripeness varies (due to EC gradient along channel). Stop pump, cut plants, clean system.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Optional 24-48 hours of darkness before harvest. Cut at base. NFT plants lift out of channels easily.",
        },
        "channel": {
            "flow_rate_lpm": 0,
            "film_depth_mm": 0,
            "channel_slope": None,
            "notes": "Stop pump after last plant is harvested. Clean channels thoroughly — root mats leave debris and salt deposits.",
        },
        "reservoir": {
            "ph": None,
            "ec": None,
            "ppm_500": None,
            "water_temp_f": None,
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "notes": "Drain reservoir after last harvest. Run H2O2 solution (5ml/gal of 3%) through all channels for cleaning.",
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
                "name": "Harvest plants",
                "description": "Cut at base. Lift plant + net pot from channel — comes out clean. If channel positions are at different maturities, harvest ready ones and cap their holes.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Wet trim or whole-plant hang",
                "description": "Wet trim: trim immediately. Dry trim: hang whole plants. Wet is faster; dry often produces better flavor.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Clean NFT channels",
                "description": "Remove all root debris from channels. Flush with H2O2 solution (5ml/gal of 3%). Scrub channel walls to remove salt deposits. Rinse with plain water. Dry completely.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Clean pump and reservoir",
                "description": "Disassemble pump, clean impeller. Scrub reservoir. Run H2O2 through all tubing.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Inspect channel slope and fittings",
                "description": "Check for warping, cracks, or worn seals. Replace degraded end caps. NFT channels take more abuse from root pressure than reservoir systems.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Were trichomes at target maturity when cut?",
            "Any bud rot discovered during trimming?",
            "Are channels fully cleaned of root debris?",
            "End caps and fittings intact?",
        ],
        "common_problems": [
            {
                "issue": "Root mat stuck in channel",
                "cause": "Dense root growth bonded to channel walls over months of growth",
                "solution": "Soak with H2O2 solution for several hours. Use a long-handled brush. For PVC channels, a pressure washer on low works well.",
            },
            {
                "issue": "Bud rot discovered during trim",
                "cause": "Hidden rot inside dense colas",
                "solution": "Cut at least 1 inch beyond visible rot. Discard affected material. Inspect remaining buds carefully.",
            },
        ],
        "training": [],
        "transition_signals": ["All plants cut and hanging", "NFT system cleaned"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Harvest before frost. Bring plants inside to trim in a clean environment."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: harvest timing may be forced by weather.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse can serve as drying space if humidity is controllable."},
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
        "description": "Hang whole plants or branches in a dark, cool, ventilated space. Target slow dry over 10-14 days. NFT produces dense buds that may need slightly longer drying time.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 58, "max": 65, "target": 62},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Complete darkness. Gentle airflow (not blowing directly on buds). 60°F / 60% humidity is the sweet spot. Slower dry = better cure.",
        },
        "channel": {
            "flow_rate_lpm": 0,
            "film_depth_mm": 0,
            "channel_slope": None,
            "notes": "System cleaned and stored.",
        },
        "reservoir": {
            "ph": None,
            "ec": None,
            "ppm_500": None,
            "water_temp_f": None,
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "notes": "System cleaned and stored.",
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
                "description": "Small stems should snap (not bend) when dry. Large stems still slightly flexible. Takes 7-14 days. Do NOT rush with fans or heat.",
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
                "description": "Inspect hanging buds daily. Dense buds are especially mold-prone. Remove affected buds immediately.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Are small stems snapping yet?",
            "Any mold or off-smell?",
            "Drying room holding 60°F / 60% RH?",
        ],
        "common_problems": [
            {
                "issue": "Buds drying too fast",
                "cause": "Temp too high, humidity too low, fans on buds",
                "solution": "Lower temp. Raise humidity. No direct airflow on buds.",
            },
            {
                "issue": "Mold during drying",
                "cause": "Humidity too high, poor airflow, or hidden bud rot",
                "solution": "Remove moldy material. Increase ventilation. Lower humidity.",
            },
        ],
        "training": [],
        "transition_signals": ["Small stems snap cleanly", "Outside of bud dry to touch", "7-14 days elapsed"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Dry indoors in a controlled environment. Never dry outdoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always dry indoors.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse is NOT ideal for drying — too much humidity fluctuation. Dry indoors if possible."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Avoid drying in greenhouse.",
            },
        },
    },
    # ── 12. CURING ────────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Place dried buds in mason jars. Burp daily for first 2 weeks, then weekly. Curing converts chlorophyll into smooth-smoking compounds and develops terpene profiles. Minimum 2-week cure; 4-8 weeks is ideal.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 58, "max": 68, "target": 62},
            "humidity_pct": {"min": 58, "max": 65, "target": 62},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Store jars in a cool, dark place. Boveda 62% packs maintain perfect humidity. Light degrades THC.",
        },
        "channel": {"flow_rate_lpm": 0, "film_depth_mm": 0, "channel_slope": None, "notes": "N/A."},
        "reservoir": {
            "ph": None,
            "ec": None,
            "ppm_500": None,
            "water_temp_f": None,
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "notes": "N/A.",
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
                "description": "Open jars 5-15 min. Week 1-2: daily. Week 3-4: every 2-3 days. After week 4: weekly. Ammonia smell = too wet, leave lid off 1 hour.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check jar humidity",
                "description": "Use mini hygrometer in each jar. Target 58-65%. Above 65% = too wet. Below 55% = add Boveda 62%.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Inspect for mold",
                "description": "Check buds visually when burping. Any mold = remove immediately.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": ["Jar humidity at 58-65%?", "Smell improving (less hay, more terpenes)?", "Any mold?"],
        "common_problems": [
            {
                "issue": "Hay/grass smell",
                "cause": "Chlorophyll still breaking down. Normal first 1-2 weeks.",
                "solution": "Continue curing. Terpenes emerge after 2-3 weeks.",
            },
            {
                "issue": "Ammonia smell",
                "cause": "Buds jarred too wet. Anaerobic bacteria.",
                "solution": "Remove buds, lay on paper bag 12-24 hours. Re-jar when drier.",
            },
            {
                "issue": "Buds too dry",
                "cause": "Over-dried or jar humidity too low",
                "solution": "Add Boveda 62% pack. Rehydrates in 3-5 days.",
            },
        ],
        "training": [],
        "transition_signals": ["Cure complete (minimum 2 weeks, ideal 4-8)", "Rich terpene aroma", "Smooth smoke"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Cure indoors. Identical process regardless of grow environment."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Curing is environment-independent.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Do not cure in greenhouse — temp swings degrade quality."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Cure indoors.",
            },
        },
    },
    # ── 13. STORAGE ──────────────────────────────────────────────────────
    {
        "id": "storage",
        "name": "Long-Term Storage",
        "order": 13,
        "duration_days": {"min": 30, "max": 365, "typical": 180},
        "description": "Post-cure long-term storage. NFT systems with their fast growth cycles may produce multiple harvests per year — storage planning is critical for inventory management. Proper storage preserves potency and terpenes for 6-12+ months.",
        "environment": {
            "temp_day_f": {"min": 55, "max": 65, "target": 60},
            "temp_night_f": {"min": 55, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK. Cool. Stable. Zero light — UV destroys cannabinoids and terpenes. Commercial: 58-62°F, 55-60% RH, nitrogen atmosphere.",
        },
        "channel": None,
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
                "description": "Home: mason jars with Boveda 58-62%. Commercial: nitrogen-sealed grove bags, CVault, or nitrogen-flushed drums.",
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
                "description": "Monitor vault temp/humidity. No light leaks. Commercial: automated alerts.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Rotate stock (FIFO)",
                "description": "First in, first out. Flag batches approaching 12 months.",
                "interval_days": 30,
                "priority": "medium",
            },
            {
                "name": "Compliance testing holds",
                "description": "Commercial: retain samples per regulations.",
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
                "cause": "Temps above 70°F, oxygen, frequent opening",
                "solution": "Below 65°F. Nitrogen-sealed. Minimize opening.",
            },
            {
                "issue": "Mold in storage",
                "cause": "Humidity above 65% or improper cure",
                "solution": "Verify 58-62% RH before sealing. Remove affected material.",
            },
            {
                "issue": "Weight loss",
                "cause": "Normal moisture equilibration",
                "solution": "Boveda packs. Sealed containers.",
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

NFT_EQUIPMENT: list[dict] = [
    # Essentials
    {
        "name": "NFT Channels (PVC, corrugated, or commercial rail)",
        "category": "essential",
        "description": "Food-safe, opaque channels. 4-inch wide for leafy greens, 6-inch for large plants. PVC pipe (4-6 inch split lengthwise), corrugated roofing channels, or purpose-built NFT rails. Max 10-12 feet per channel for even EC distribution.",
    },
    {
        "name": "Channel End Caps",
        "category": "essential",
        "description": "Seal the high end of each channel. Must be watertight. PVC caps, silicone-sealed flat stock, or commercial NFT end caps.",
    },
    {
        "name": "Channel Support / Stand",
        "category": "essential",
        "description": "Holds channels at correct slope (1:30 to 1:40). Must be rigid and level side-to-side. PVC frame, 2x4 lumber frame, or commercial NFT table.",
    },
    {
        "name": "Reservoir (20-50 gal)",
        "category": "essential",
        "description": "Collects return flow from all channels. Size at 2-3x total channel volume for stability. Food-safe, opaque, dark-colored.",
    },
    {
        "name": "Water Pump (submersible)",
        "category": "essential",
        "description": "Pumps from reservoir to channel inlets. Size at 2x total flow demand. Must run 24/7 — pump failure = plant death in minutes.",
    },
    {
        "name": "Backup Pump",
        "category": "essential",
        "description": "NOT optional for NFT — it's essential. Pump failure kills plants faster than any other hydro method. Keep a tested backup ready to swap in <5 minutes.",
    },
    {
        "name": "Supply Tubing + Manifold",
        "category": "essential",
        "description": "Distributes flow from pump to each channel. Use a manifold with individual valves per channel for flow balancing.",
    },
    {
        "name": "Return Drains",
        "category": "essential",
        "description": "Channel drain ends feed back to reservoir. Use screen filters on returns to catch root debris.",
    },
    {
        "name": "Net Pots (3-inch or 6-inch)",
        "category": "essential",
        "description": "Sit in channel holes. Hold rockwool cube + plant. 3-inch for leafy greens, 6-inch for large plants.",
    },
    {
        "name": "Rockwool Cubes",
        "category": "essential",
        "description": "Starting medium for NFT. 1.5-inch starter cubes for germination, transfer cube-and-all into net pot for channel placement.",
    },
    {"name": "pH Pen", "category": "essential", "description": "Measure at reservoir. Apera or BlueLab recommended."},
    {
        "name": "EC/TDS Meter",
        "category": "essential",
        "description": "Measure at reservoir AND at channel drain ends to check for EC gradient.",
    },
    {"name": "pH Up & pH Down", "category": "essential", "description": "Adjust at reservoir."},
    {
        "name": "Nutrients (GH Flora Trio)",
        "category": "essential",
        "description": "Mix in reservoir. Continuous flow distributes to all channels.",
    },
    {
        "name": "Hydroguard",
        "category": "essential",
        "description": "Root protection. Dense root mats in NFT channels are susceptible to Pythium.",
    },
    {
        "name": "Air Pump + Air Stone (for reservoir)",
        "category": "essential",
        "description": "Oxygenate reservoir water. NFT film is thin and oxygenated by exposure, but reservoir water needs aeration.",
    },
    {"name": "Grow Light", "category": "essential", "description": "Size for total canopy area across all channels."},
    {"name": "Light Timer", "category": "essential", "description": "Reliable timer for 18/6 → 12/12."},
    {"name": "Thermometer / Hygrometer", "category": "essential", "description": "Monitor grow room conditions."},
    # Recommended
    {
        "name": "Flow Rate Meter / Sight Tube",
        "category": "recommended",
        "description": "Measure flow rate at each channel inlet and drain. Essential for diagnosing flow restriction from root mats.",
    },
    {
        "name": "Neoprene Collars",
        "category": "recommended",
        "description": "Seal around net pots in channel holes. Blocks light (prevents algae) and prevents splashing.",
    },
    {
        "name": "Inline Screen Filters (return lines)",
        "category": "recommended",
        "description": "Catch root fragments and debris before they reach the pump.",
    },
    {
        "name": "SCROG / Trellis Net",
        "category": "recommended",
        "description": "NFT plants have no structural media support. Trellis net is nearly mandatory for flowering — supports heavy buds and creates even canopy.",
    },
    {
        "name": "Silica Supplement",
        "category": "recommended",
        "description": "Strengthens stems. NFT plants lack the structural support of media-grown plants.",
    },
    {
        "name": "CalMag Supplement",
        "category": "recommended",
        "description": "Essential with RO water. Add to reservoir.",
    },
    {
        "name": "Water Chiller",
        "category": "recommended",
        "description": "Controls reservoir temp. NFT film warms up in channels under lights — chilled reservoir water compensates.",
    },
    {
        "name": "Oscillating Fans",
        "category": "recommended",
        "description": "Air movement above channels prevents humidity pockets between plants.",
    },
    {
        "name": "Exhaust Fan + Carbon Filter",
        "category": "recommended",
        "description": "Odor and humidity control. Size for grow room.",
    },
    # Optional
    {
        "name": "UPS / Battery Backup (for pump)",
        "category": "optional",
        "description": "Keeps pump running during power outages. NFT plants die in minutes without flow — this is the most important backup for any NFT system.",
    },
    {
        "name": "Auto-Top-Off (float valve)",
        "category": "optional",
        "description": "Maintains reservoir level automatically. Helpful with multiple large flowering plants consuming heavily.",
    },
    {
        "name": "pH/EC Controller (auto-dosing)",
        "category": "optional",
        "description": "Automatically maintains pH and EC in reservoir.",
    },
    {
        "name": "Slope Level / Laser Level",
        "category": "optional",
        "description": "Precision slope setting for channels. Especially useful for multi-tier or long-channel setups.",
    },
    {
        "name": "Root Guards / Channel Screens",
        "category": "optional",
        "description": "Mesh inserts in channel bottom to keep root mat elevated slightly above channel floor. Helps maintain film flow under the mat.",
    },
    {
        "name": "Water Temp Alarm",
        "category": "optional",
        "description": "Alerts if reservoir temp exceeds 72°F. High water temp + NFT root mats = rapid Pythium development.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE CHARTS
# ─────────────────────────────────────────────────────────────────────────────

NFT_QUICK_REFERENCE = {
    "ph_range": {"min": 5.5, "max": 6.2, "ideal": "5.8 seedling/veg, 6.0 flower"},
    "ec_by_stage": {
        "seedling": {"min": 0.2, "max": 0.5},
        "early_veg": {"min": 0.6, "max": 1.0},
        "late_veg": {"min": 0.8, "max": 1.4},
        "transition": {"min": 0.8, "max": 1.4},
        "early_flower": {"min": 1.0, "max": 1.6},
        "mid_flower": {"min": 1.2, "max": 1.8},
        "late_flower": {"min": 0.8, "max": 1.2},
        "flush": {"min": 0.0, "max": 0.2},
    },
    "water_temp_f": {"min": 65, "max": 72, "ideal": 68},
    "flow_rate_guide": {
        "per_channel_lpm": {"min": 0.5, "max": 2.5, "seedling": 0.75, "veg": 1.5, "flower": 2.0},
        "film_depth_mm": {"target": 3, "min": 2, "max": 5},
        "pump_sizing": "2x total channel demand. E.g., 4 channels × 2 LPM = 8 LPM demand → use 16+ LPM pump.",
    },
    "channel_engineering": {
        "slope": "1:30 to 1:40 (1 inch drop per 30-40 inches of channel length)",
        "max_length_ft": 12,
        "width_large_plants_inches": 6,
        "width_leafy_greens_inches": 4,
        "material": "PVC pipe (split), corrugated roofing, or commercial NFT rail. Must be opaque and food-safe.",
    },
    "reservoir_change_schedule": "Every 7 days in veg, every 5 days in flower, every 3 days during flush",
    "hydroguard_dose": "2 ml/gal at every reservoir change AND every top-off",
    "nutrient_mixing_order": [
        "Silica (if using)",
        "CalMag",
        "FloraMicro",
        "FloraGro",
        "FloraBloom",
        "Supplements",
        "pH adjust last",
    ],
    "top_off_rule": "EC rising = top off with plain pH'd water. EC dropping = top off with 1/4 strength nutrient water.",
    "pump_failure_protocol": {
        "time_to_death_minutes": "2-5 minutes without flow in warm conditions",
        "immediate_action": "Switch to backup pump. If no backup, manually pour nutrient water into channel inlets.",
        "prevention": "Keep tested backup pump ready. UPS/battery backup for pump circuit. Pump failure alarm if available.",
    },
    "golden_rules": [
        "Pump runs 24/7 — pump failure kills plants in MINUTES, not hours",
        "ALWAYS have a backup pump tested and ready",
        "Check drain flow at every channel DAILY — root mats block flow",
        "Channel slope: 1:30 to 1:40. Too steep = thin film. Too flat = pooling",
        "Max channel length 10-12 feet — longer channels get EC gradient problems",
        "Start seedlings in rockwool cubes OFF the channels — never plant directly in NFT",
        "Roots must be 3+ inches before channel placement",
        "Monitor EC at inlet AND drain end — difference reveals salt accumulation",
        "Flush channels with plain water at every reservoir change",
        "NFT plants have NO structural support — SCROG net is mandatory for flower",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING GUIDE
# ─────────────────────────────────────────────────────────────────────────────

NFT_TROUBLESHOOTING: list[dict] = [
    {
        "category": "Flow & Pump Issues",
        "problems": [
            {
                "symptom": "Pump stopped — plants wilting rapidly",
                "diagnosis": "Pump failure — EMERGENCY",
                "severity": "critical",
                "causes": ["Pump motor burned out", "Power outage", "Debris jammed impeller", "Breaker tripped"],
                "solutions": [
                    "IMMEDIATE: Switch to backup pump (<5 min response time)",
                    "EMERGENCY: If no backup, manually pour nutrient solution into channel inlets every 5 minutes until pump is replaced",
                    "Diagnose: Check power, check impeller for debris, check breaker",
                    "PREVENT: UPS/battery backup for pump circuit. Pump failure alarm. Always have a tested backup pump.",
                ],
            },
            {
                "symptom": "Reduced or no flow at drain end of channel",
                "diagnosis": "Root mat blocking flow",
                "severity": "high",
                "causes": [
                    "Root mass forming a dam across channel",
                    "Root debris caught at channel restriction point",
                    "Salt buildup narrowing channel",
                ],
                "solutions": [
                    "Gently lift root mass at the blockage point to restore flow",
                    "Increase pump flow rate to push through partial restriction",
                    "For severe blockage: temporarily remove plants, flush channel with pressurized water, replace",
                    "Trim roots carefully if mat is too dense (never remove more than 20%)",
                    "Install root guards/screens to keep mat elevated above channel floor",
                ],
            },
            {
                "symptom": "Uneven flow between channels",
                "diagnosis": "Flow distribution imbalance",
                "severity": "medium",
                "causes": [
                    "Manifold valves not balanced",
                    "One channel partially clogged",
                    "Air lock in supply line",
                    "Pump losing capacity",
                ],
                "solutions": [
                    "Adjust manifold valves until all channels have equal flow",
                    "Check each supply line for air locks or kinks",
                    "Flush individual channels",
                    "Clean pump intake and impeller",
                ],
            },
        ],
    },
    {
        "category": "Root & Channel Issues",
        "problems": [
            {
                "symptom": "Brown/slimy roots in channel",
                "diagnosis": "Root rot (Pythium)",
                "severity": "critical",
                "causes": [
                    "Water temp too high (>72°F)",
                    "No beneficial bacteria",
                    "Stagnant zone behind root mat",
                    "Contaminated reservoir",
                ],
                "solutions": [
                    "Treat with H2O2 (3ml/gal of 3%) for 24 hours — kills all bacteria",
                    "After 24 hours: full drain, clean, refill, re-dose Hydroguard at 3ml/gal",
                    "Lower water temp below 70°F (chiller may be needed)",
                    "Clear any flow restrictions that created stagnant zones",
                    "Maintain Hydroguard at every res change going forward",
                ],
            },
            {
                "symptom": "Algae growing in channels",
                "diagnosis": "Light reaching nutrient film",
                "severity": "medium",
                "causes": [
                    "Light leaking through channel holes or gaps",
                    "Transparent or translucent channel material",
                    "Neoprene collars missing",
                ],
                "solutions": [
                    "Block ALL light entry into channels",
                    "Install neoprene collars around every net pot",
                    "Cover unused channel holes",
                    "Use opaque black channel material only",
                ],
            },
        ],
    },
    {
        "category": "Salt Accumulation Issues",
        "problems": [
            {
                "symptom": "Plants at end of channel showing nutrient burn while inlet plants are fine",
                "diagnosis": "EC gradient along channel (salt accumulation)",
                "severity": "medium",
                "causes": [
                    "Channel too long",
                    "Flow rate too low",
                    "Insufficient flushing",
                    "Heavy bloom nutrients concentrating",
                ],
                "solutions": [
                    "Flush channels with plain water at every reservoir change",
                    "Increase flow rate to reduce concentration gradient",
                    "Reduce channel length for future grows (max 10-12 feet)",
                    "Consider bi-directional flow (alternating inlet/drain ends)",
                    "Monitor EC at inlet vs drain regularly",
                ],
            },
            {
                "symptom": "White salt crust on channel walls and net pot edges",
                "diagnosis": "Salt deposit from nutrient film evaporation at the waterline",
                "severity": "low",
                "causes": [
                    "Normal evaporation at film edges",
                    "High EC solution",
                    "Warm channel temps accelerating evaporation",
                ],
                "solutions": [
                    "Clean during every reservoir change with a soft brush",
                    "Reduce EC if excessive",
                    "Keep channel temps stable (reservoir chiller helps)",
                ],
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# CHANNEL ENGINEERING — NFT's core differentiator
# ─────────────────────────────────────────────────────────────────────────────

NFT_CHANNEL_ENGINEERING: dict = {
    "channel_specifications": {
        "slope_percent": {
            "min": 1,
            "max": 3,
            "target": 2,
            "notes": "1:30 to 1:50 ratio. Too steep = roots dry. Too flat = pooling.",
        },
        "channel_width_inches": {
            "small_plants": 3,
            "medium_plants": 4,
            "large_plants": 6,
            "notes": "Width determines root mat spread and nutrient film coverage.",
        },
        "channel_length_ft": {
            "max_recommended": 12,
            "notes": "Beyond 12 ft, nutrient depletion at far end becomes an issue. Use multiple shorter channels.",
        },
        "channel_material": [
            "PVC gutter (food-safe)",
            "NFT-specific extruded channels",
            "DIY vinyl fence post",
            "Commercial NFT troughs",
        ],
        "cover_requirement": "Light-proof covers mandatory. Light exposure = algae. Use opaque lids with net pot holes.",
    },
    "flow_rate_management": {
        "target_lpm": {
            "min": 1.0,
            "max": 2.0,
            "optimal": 1.5,
            "notes": "Liters per minute per channel. Measured at drain end.",
        },
        "film_depth_mm": {
            "min": 1,
            "max": 3,
            "target": 2,
            "notes": "The 'Nutrient Film' should be 1-3mm deep. Deeper = roots submerged = less oxygen.",
        },
        "flow_uniformity": "All channels must receive equal flow. Use manifold with individual channel valves for balancing.",
        "flow_check_frequency": "Daily visual check. Weekly measured check with graduated container + timer.",
        "adjustment_by_stage": {
            "seedling": {"flow_lpm": 0.5, "notes": "Gentle flow. Root tips just touching film."},
            "veg": {"flow_lpm": 1.0, "notes": "Roots establishing in channel. Moderate flow."},
            "flower": {"flow_lpm": 1.5, "notes": "Full flow. Root mat developed. Heavy feeding."},
            "flush": {"flow_lpm": 2.0, "notes": "Maximum flow with plain water to flush salt buildup."},
        },
    },
    "root_mat_management": {
        "healthy_root_mat": "White/cream colored, thin mat along channel floor. Does NOT dam the flow.",
        "problematic_root_mat": "Thick, dense mat that blocks flow to downstream plants. Brown sections = rot.",
        "dam_prevention": [
            "Channel slope maintained precisely (no flat spots where roots accumulate)",
            "Periodic root trimming if mat blocks >50% of channel cross-section",
            "Wider channels for large plants (6-inch minimum for aggressive rooters)",
            "Shorter channel runs (fewer plants per channel = less mat buildup)",
        ],
        "root_rot_in_nft": {
            "cause": "Stagnant pools behind root dams. Lack of oxygen in pooled sections.",
            "signs": [
                "Brown/slimy roots",
                "Foul smell from channel",
                "Flow slowing or stopping",
                "Downstream plants wilting",
            ],
            "treatment": [
                "Clear the root dam immediately",
                "Flush channel with H2O2 solution (3ml/gal)",
                "Increase flow rate temporarily",
                "Add Hydroguard to reservoir",
            ],
        },
    },
    "pump_failure_protocol": {
        "time_to_damage": "15-60 minutes depending on ambient temp and root mat moisture retention",
        "detection": ["No flow visible at drain end", "Plants wilting", "Reservoir not circulating"],
        "immediate_actions": [
            "Switch to backup pump",
            "If no backup: manually pour nutrient solution through channels every 10 min",
            "Seal channel ends to create temporary DWC (emergency — holds water in channel)",
            "Cover channels to trap humidity and slow root drying",
        ],
        "backup_system_recommendations": [
            "Dedicated backup pump, pre-plumbed with valves (manual switchover in <1 min)",
            "UPS on primary pump (30-60 min runtime minimum)",
            "Float switch alarm on reservoir (alerts if pump stops returning water)",
            "Battery-powered backup pump for extended outages",
        ],
    },
    "salt_accumulation": {
        "where_it_builds": [
            "Channel edges above waterline (white crust)",
            "Net pot bottoms",
            "Channel inlets (reduced flow)",
            "Root mat surface",
        ],
        "problems_caused": ["Nutrient lockout", "pH instability", "Reduced flow rates", "Root burn at channel edges"],
        "prevention": [
            "Weekly flush with plain pH'd water (run for 1 hour, drain, refill with nutrients)",
            "Maintain proper flow rate (too slow = more evaporation = more salt deposits)",
            "Full channel clean between grows (disassemble, scrub, flush with vinegar or pH-down solution)",
        ],
        "cleaning_protocol": [
            "End of grow: remove all plants and net pots",
            "Run plain water flush for 30 minutes",
            "Drain completely",
            "Fill channels with pH 3.0 solution (citric acid). Soak 2 hours",
            "Scrub interior with soft brush",
            "Flush with clean water until runoff is pH neutral",
            "Inspect for algae, biofilm, or residue. Repeat if needed.",
        ],
    },
    "propagation_to_nft_transfer": {
        "ideal_root_length_inches": {
            "min": 2,
            "max": 4,
            "notes": "Roots must be long enough to reach the nutrient film from net pot.",
        },
        "starter_methods": ["Rockwool cubes (most popular)", "Rapid Rooter plugs", "Neoprene collars with hydroton"],
        "transfer_protocol": [
            "Start seedling/clone in starter plug under dome",
            "Once roots are 2-4 inches, place in net pot with hydroton support",
            "Insert net pot into NFT channel",
            "Temporarily increase flow rate for first 24h (ensures roots contact film)",
            "Verify root-to-film contact within 24h (gently lift cover and check)",
            "If roots aren't touching: shim net pot lower, or increase flow briefly",
        ],
        "acclimation_period": "3-5 days for roots to establish in channel. Growth may pause temporarily. Normal.",
        "common_mistakes": [
            "Transferring too early (roots too short to reach film)",
            "Not checking root contact after transfer",
            "Reducing flow rate during establishment",
            "Removing starter plug (leave it — roots grow through it)",
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLED CONFIG EXPORT
# ─────────────────────────────────────────────────────────────────────────────

NFT_CONFIG: dict = {
    "grow_type_id": "nft",
    "version": "1.0.0",
    "stages": NFT_STAGES,
    "equipment": NFT_EQUIPMENT,
    "quick_reference": NFT_QUICK_REFERENCE,
    "troubleshooting": NFT_TROUBLESHOOTING,
    "channel_engineering": NFT_CHANNEL_ENGINEERING,
    "total_grow_days": {
        "min": 90,
        "max": 150,
        "typical_photo": 120,
        "typical_auto": 80,
        "breakdown": "Germination (3-7d) + Seedling/Propagation (7-14d) + Veg (24-56d) + Flower (56-70d) + Dry (7-14d) + Cure (14-60d)",
    },
}
