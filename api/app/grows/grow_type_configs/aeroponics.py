"""Aeroponics — Complete grow type configuration.

Enterprise-grade configuration for aeroponic systems — the highest-performance
and highest-risk hydroponic method. Roots are suspended in air inside a sealed,
light-tight chamber and misted with fine nutrient spray at precise intervals.
Aeroponics produces the fastest growth rates of any grow method but has
**ZERO margin for error** — roots begin dying within minutes of mist failure.

The defining features are **mist cycle precision** (seconds on / minutes off),
**nozzle management** (the #1 failure mode — clogs kill plants in minutes),
**root chamber environment** (light-tight, temperature-controlled, humidity
managed), **pressure system reliability** (pump/compressor/accumulator), and
**failure mode awareness** (every component failure is an emergency).

High-Pressure Aeroponics (HPA) vs Low-Pressure Aeroponics (LPA):
  - HPA: 80+ PSI, 50-micron droplets, accumulator tank, solenoid valves.
    Maximum oxygen absorption. Fastest growth. Most complex and fragile.
  - LPA: 20-60 PSI, larger droplets, spray nozzles or misters.
    Simpler, more forgiving, still excellent growth. Most home growers use LPA.
  - This config covers BOTH with notes where they diverge.

Key Aeroponics differences from all other methods:
  - Roots are NEVER submerged — they hang in air and receive mist
  - Mist timing is in SECONDS (on) and MINUTES (off) — not hours
  - Nozzle clog = plant death in minutes (not hours or days)
  - Power failure = plant death in minutes (not hours or days)
  - Lower EC than any other hydro method (mist absorption is ultra-efficient)
  - NO organic nutrients (they clog nozzles)
  - Root chamber must be 100% light-tight (light = algae = clogged nozzles)
  - Backup systems are not optional — they are survival equipment
  - The fastest vegetative growth of any method when working correctly

Supports three environment types (matching Tent.environment_type):
  - indoor  (default — full environmental control, artificial light)
  - outdoor (NOT recommended — too many failure points)
  - greenhouse (possible but challenging — temperature control of root chamber)

Base stage values target indoor/tent growing.  Each stage carries an
``environment_variants`` dict with ``outdoor`` and ``greenhouse`` keys.
The frontend merges base + variant at render time.

Data sources:
- NASA aeroponic research (original HPA development)
- AeroFarms and vertical farming industry practices
- Cannabis aeroponic cultivation guides
- General Hydroponics Flora Trio feeding charts (reduced for aero efficiency)
- Root zone oxygenation and mist droplet size research
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in an Aeroponics grow
# ─────────────────────────────────────────────────────────────────────────────

AERO_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Seed cracks open and taproot emerges. For aeroponics, start seeds in neoprene collars with Rapid Rooters or rockwool cubes inside a humidity dome — NOT in the aero chamber yet. Seeds need consistent moisture, not mist cycles.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Keep seeds in darkness. Heat mat at 78°F. No light until sprout emerges. Humidity dome over propagation tray. Do NOT put seeds in the aero chamber.",
        },
        "mist_system": {
            "mist_on_sec": 0,
            "mist_off_sec": 0,
            "pressure_psi": 0,
            "nozzle_type": None,
            "day_cycle": None,
            "night_cycle": None,
            "root_chamber_temp_f": None,
            "droplet_size_microns": None,
            "notes": "Aero system NOT running yet. Germinate seeds off-system. While seeds germinate: pressure-test the entire system, verify all nozzles spray evenly, check for leaks, test timer/solenoid cycling.",
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
                "name": "Start seeds",
                "description": "Soak seeds 12-24 hours in plain pH 6.0 water, then place in Rapid Rooters or rockwool cubes inside neoprene collars. Place in humidity dome.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for taproot",
                "description": "After 24-72 hours, look for white taproot emerging. Do not disturb the seed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Pressure-test aero system",
                "description": "While seeds germinate: run the entire mist system. Check every nozzle for spray pattern, every fitting for leaks, every solenoid for cycling. Fix ALL leaks now — you cannot fix them with plants installed.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Verify timer resolution",
                "description": "Aeroponics requires second-resolution timers (not minute-resolution). Test that the timer can do 3-5 seconds ON and 3-5 minutes OFF reliably. Cycle it 50+ times to verify consistency.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Test backup systems",
                "description": "Test the backup pump/power supply/UPS. Simulate a power failure and verify the backup engages within 60 seconds. In aeroponics, backup is NOT optional.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check root chamber light-tightness",
                "description": "Close the chamber, turn off room lights, then shine a flashlight around every seal and fitting from outside. Any light leak = future algae problem = clogged nozzles.",
                "interval_days": None,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Has the seed cracked open?",
            "Is the taproot visible and white?",
            "Is the starter medium moist but not soaking?",
            "Temperature at 75-80°F?",
            "Is the aero system pressure-tested and leak-free?",
            "Do all nozzles spray evenly?",
            "Is the root chamber 100% light-tight?",
        ],
        "common_problems": [
            {
                "issue": "Seed not germinating",
                "cause": "Too cold, too wet, or bad seed",
                "solution": "Ensure 75-80°F. Starter medium should be moist not soaking. Try a different seed after 7 days.",
            },
            {
                "issue": "Nozzle spray uneven during testing",
                "cause": "Clogged or defective nozzle, or pressure variation",
                "solution": "Replace uneven nozzles now. Clean all nozzles (H2O2 soak). Verify pressure is consistent across all zones. Fix before plants go in.",
            },
            {
                "issue": "Timer can't do second-resolution cycles",
                "cause": "Using a minute-resolution timer meant for drip or ebb/flow",
                "solution": "Get a proper aero timer: CT-2 cycle timer, Arduino/ESP32 controller, or commercial aero controller. Minute-resolution timers cannot run aeroponics.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Taproot visible through starter medium",
            "Sprout emerging",
            "First cotyledon leaves visible",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Aeroponics outdoors is NOT recommended. Temperature control of the root chamber is nearly impossible. If you must: germinate indoors."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor aeroponics is extremely challenging. Germinate indoors regardless.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse germination: use heat mat and humidity dome. Root chamber temperature will be challenging to maintain in a greenhouse — plan insulation and cooling."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse aero: root chamber temp control is the primary challenge.",
            },
        },
    },
    # ── 2. SEEDLING ──────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Seedling develops first true leaves. Transfer seedlings in neoprene collars into the aero chamber once roots are 1-2 inches long. Start with gentle, frequent mist cycles — seedling roots are fragile and need consistent moisture. LPA is more forgiving at this stage than HPA.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 65, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 250, "target": 200},
            "light_dli": {"min": 6, "max": 16, "target": 13},
            "notes": "Gentle light. Seedling roots are just entering the mist zone. Keep mist cycles frequent — roots must NEVER dry out. If roots look dry between mists, increase frequency.",
        },
        "mist_system": {
            "mist_on_sec": {"min": 4, "max": 8, "target": 5},
            "mist_off_sec": {"min": 120, "max": 240, "target": 180},
            "pressure_psi": {"hpa": {"min": 80, "max": 100, "target": 90}, "lpa": {"min": 30, "max": 50, "target": 40}},
            "nozzle_type": "Anti-drip mist nozzles preferred. Standard mist nozzles acceptable for LPA.",
            "day_cycle": {
                "on_sec": 5,
                "off_sec": 180,
                "notes": "5 seconds on, 3 minutes off during lights-on. Seedling roots are short — keep them wet.",
            },
            "night_cycle": {
                "on_sec": 5,
                "off_sec": 300,
                "notes": "5 seconds on, 5 minutes off at night. Reduced transpiration at night means roots stay wet longer.",
            },
            "root_chamber_temp_f": {"min": 62, "max": 68, "target": 65},
            "droplet_size_microns": {
                "hpa": {"min": 30, "max": 80, "target": 50},
                "lpa": {"min": 100, "max": 500, "target": 200},
            },
            "notes": "Frequent, short mist bursts. Roots should glisten with moisture between mists — never dry, never dripping. Observe roots after installing seedlings: if tips dry out before next mist, shorten the off period. Root chamber temp 65-72°F is critical for oxygen absorption.",
        },
        "nutrients": {
            "strength_pct": 20,
            "approach": "Very low strength. Aero roots absorb nutrients 3-5x more efficiently than submerged roots. What would be quarter-strength in DWC is full-strength in aero. Start very light.",
            "flora_micro_ml_per_gal": 0.5,
            "flora_gro_ml_per_gal": 0.5,
            "flora_bloom_ml_per_gal": 0.25,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root protection. Aero root chambers are warm and humid — ideal for Pythium. Hydroguard is essential.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Transfer seedlings to aero chamber",
                "description": "Insert neoprene collars with seedlings into the chamber lid. Roots should hang 1-2 inches into the mist zone. Ensure the collar seals around the stem — no light leaks.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Start mist cycles",
                "description": "Program timer for 5s ON / 180s OFF during day, 5s ON / 300s OFF at night. Run and watch the first 3-4 cycles. Verify all nozzles are misting the root zone evenly.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Observe root moisture between mists",
                "description": "Open the chamber between mist cycles and check root moisture. Roots should be glistening, not dripping, not dry. Adjust off-time up or down based on what you see.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check root chamber temperature",
                "description": "Root zone temp must be 65-72°F. Above 72°F = low dissolved oxygen in mist, pathogen risk. Below 60°F = slow growth. Use a chiller or chamber insulation as needed.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Nozzle check",
                "description": "Verify ALL nozzles are spraying. Even one clogged nozzle means one plant's roots are drying. In aero, this is a 30-minute emergency, not a 2-day problem.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check reservoir pH/EC",
                "description": "Small aero reservoirs swing fast. Check pH/EC daily. Top off with plain pH'd water to maintain volume. Full change every 5-7 days.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "All nozzles misting evenly?",
            "Roots glistening between mist cycles (not dry, not dripping)?",
            "Root chamber temp 65-72°F?",
            "Root chamber 100% light-tight?",
            "First true leaves appearing?",
            "No slime or discoloration on roots?",
            "pH/EC stable?",
        ],
        "common_problems": [
            {
                "issue": "Roots drying between mist cycles",
                "cause": "Off-time too long, or nozzle not reaching this plant's roots",
                "solution": "Shorten off-time by 30-60 seconds. Verify nozzle spray pattern covers all root zones. Reposition nozzle if needed. In aero, dry roots = dead roots within minutes.",
            },
            {
                "issue": "Roots constantly dripping wet",
                "cause": "Off-time too short, or nozzle dripping between cycles",
                "solution": "Increase off-time by 30-60 seconds. Check for dripping nozzles (anti-drip nozzles solve this). Roots need air exposure between mists — that's the entire point of aeroponics.",
            },
            {
                "issue": "Root tips browning",
                "cause": "Root chamber too warm (>72°F), Pythium, or light leak causing algae",
                "solution": "Check chamber temp — cool below 72°F. Add Hydroguard. Check for light leaks. Brown tips in the first week = environmental problem. Address immediately.",
            },
            {
                "issue": "Seedling falling through collar",
                "cause": "Neoprene collar too large or stem too thin",
                "solution": "Use smaller collar insert. Pack a small piece of rockwool around the stem inside the collar. The collar MUST support the plant and block light.",
            },
        ],
        "training": [],
        "transition_signals": [
            "2-3 sets of true leaves",
            "Roots 4-6 inches long and bright white",
            "Vigorous root branching visible",
            "Seedling stable in collar",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor aero seedlings: root chamber temperature is nearly impossible to control. Insulate the chamber heavily. Have a chiller."
                },
                "extra_tasks": [
                    {
                        "name": "Insulate root chamber",
                        "description": "Wrap root chamber in reflective insulation. Direct sun on the chamber will cook roots. Shade the entire chamber.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Root chamber overheating in sun",
                        "cause": "Direct sun on chamber",
                        "solution": "Shade the chamber completely. Insulate. Use a chiller. Root zone above 75°F = root death in aero.",
                    },
                ],
                "notes": "Outdoor aero: chamber temperature control is critical and difficult.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: insulate root chamber. Greenhouse temps can spike, overheating the root zone rapidly."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse aero: insulate chamber, consider chiller.",
            },
        },
    },
    # ── 3. EARLY VEGETATIVE ──────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Rapid root and leaf expansion. Aeroponics produces the fastest vegetative growth of any method — roots can grow 1-2 inches per DAY when conditions are optimal. Mist cycles can begin to lengthen (more off-time) as the root mass increases and retains moisture better. This is when aero's advantage becomes visible.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 60, "max": 75, "target": 65},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 300, "max": 500, "target": 400},
            "light_dli": {"min": 19, "max": 32, "target": 26},
            "notes": "Ramp up light intensity. Aero plants grow FAST — be ready for rapid vertical growth. VPD management matters: higher VPD = more transpiration = roots absorb mist faster.",
        },
        "mist_system": {
            "mist_on_sec": {"min": 3, "max": 5, "target": 3},
            "mist_off_sec": {"min": 240, "max": 360, "target": 300},
            "pressure_psi": {"hpa": {"min": 80, "max": 100, "target": 90}, "lpa": {"min": 30, "max": 50, "target": 40}},
            "nozzle_type": "Anti-drip mist nozzles. For HPA: Tefen or Dramm fogger nozzles.",
            "day_cycle": {
                "on_sec": 3,
                "off_sec": 300,
                "notes": "3 seconds on, 5 minutes off. Root mass is larger now and retains moisture better. Shorter on-time = finer mist coat (better oxygenation).",
            },
            "night_cycle": {
                "on_sec": 3,
                "off_sec": 480,
                "notes": "3 seconds on, 8 minutes off at night. Reduced transpiration. Roots stay wet longer. Longer off-time prevents waterlogging.",
            },
            "root_chamber_temp_f": {"min": 62, "max": 68, "target": 65},
            "droplet_size_microns": {
                "hpa": {"min": 30, "max": 80, "target": 50},
                "lpa": {"min": 100, "max": 500, "target": 200},
            },
            "notes": "Shorter on-time, longer off-time compared to seedling stage. The growing root mass retains more moisture between cycles. Observe roots: they should go from glistening (just after mist) to slightly damp (just before next mist) — NOT dry. If roots dry before the next cycle, shorten the off-time.",
        },
        "nutrients": {
            "strength_pct": 35,
            "approach": "Still low by other-method standards. Aero roots absorb mist nutrients ultra-efficiently. EC 0.6-0.8. What looks like half-strength in DWC is full feeding in aero.",
            "flora_micro_ml_per_gal": 0.875,
            "flora_gro_ml_per_gal": 0.875,
            "flora_bloom_ml_per_gal": 0.4375,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root zone protection. Non-negotiable in aero.",
                },
                {
                    "name": "Silica (Armor Si)",
                    "dose_ml_per_gal": 0.5,
                    "purpose": "Strengthen rapidly growing stems. Add FIRST before other nutrients. WARNING: silica can precipitate and clog nozzles — use low dose and monitor.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Adjust mist cycle",
                "description": "Transition to 3s ON / 5min OFF day cycle. Observe roots for 2-3 cycles after adjusting. If roots dry before next mist, reduce off-time. If roots are dripping, increase off-time.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Daily nozzle inspection",
                "description": "EVERY DAY. Check every nozzle. In veg, plants can survive a clogged nozzle for a few hours. In flower, minutes. Build the daily check habit now.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check reservoir pH/EC",
                "description": "Aero reservoirs are typically smaller and swing faster. Check daily. pH 5.5-5.8 for aero (slightly lower than DWC for better mist absorption).",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Monitor root growth rate",
                "description": "Aero roots grow fast. Check that roots are not hitting the chamber bottom or tangling in nozzles. Trim if necessary (rare).",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Clean inline filter",
                "description": "The filter between pump and nozzles catches precipitates. Clean it weekly minimum. A clogged filter = reduced pressure = poor atomization = poor growth.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Flush nozzles",
                "description": "Run plain pH'd water through the system for 5 minutes to clear any nutrient buildup in nozzles. Do this before every reservoir change.",
                "interval_days": 7,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "All nozzles spraying fine mist (not streams)?",
            "Roots bright white and branching rapidly?",
            "Root chamber temp 65-72°F?",
            "No algae visible inside chamber?",
            "pH/EC stable between checks?",
            "Rapid new leaf growth visible daily?",
        ],
        "common_problems": [
            {
                "issue": "Root growth slowing despite good top growth",
                "cause": "Root chamber too warm, or mist cycle not optimal",
                "solution": "Check chamber temp — must be under 72°F. Adjust mist timing. Consider adding a small fan inside the chamber for air circulation (controversial but effective in some setups).",
            },
            {
                "issue": "Nozzle producing stream instead of mist",
                "cause": "Partial clog, or pressure dropped below atomization threshold",
                "solution": "Clean nozzle immediately. Check pump pressure. For HPA: verify accumulator is charged. A stream instead of mist dramatically reduces oxygen in the root zone.",
            },
            {
                "issue": "Algae in root chamber",
                "cause": "Light leak somewhere in the chamber",
                "solution": "Find and seal the light leak immediately. Algae clogs nozzles and creates slime on roots. Clean chamber with H2O2. Re-seal all joints with opaque tape or silicone.",
            },
            {
                "issue": "Silica clogging nozzles",
                "cause": "Silica precipitating in nutrient solution or nozzle",
                "solution": "Reduce or eliminate silica. If using: add first, pH down, wait 30 min, then add other nutrients. Clean nozzles more frequently. Some growers skip silica entirely in aero — the fast growth compensates.",
            },
        ],
        "training": [
            {
                "technique": "LST (low stress training)",
                "description": "Begin bending and tying down branches. Aero plants grow FAST — start training early or they'll outgrow your space. 4-5 nodes is ideal to start.",
                "timing": "After 4-5 nodes",
            },
            {
                "technique": "Topping",
                "description": "Top above 4th or 5th node. Aero recovery is extremely fast — expect 2-3 day recovery vs 5-7 in soil. The plant barely notices.",
                "timing": "At 5-6 nodes",
            },
        ],
        "transition_signals": [
            "5-6 nodes of growth",
            "Roots 12+ inches and branching heavily",
            "Visible daily growth",
            "Plant drinking reservoir noticeably",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor aero veg: hot days will overheat root chamber. Chiller is mandatory, not optional."
                },
                "extra_tasks": [
                    {
                        "name": "Monitor root chamber temp in afternoon heat",
                        "description": "Peak outdoor temps can push root chamber to 80°F+ which is lethal for aero roots. Check at 2-3 PM daily.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Root chamber overheating",
                        "cause": "Ambient temperature warming chamber",
                        "solution": "Chiller, insulation, shade structure. If chamber consistently exceeds 75°F, aeroponics outdoors may not be viable in your climate.",
                    },
                ],
                "notes": "Outdoor aero: viable only with excellent temperature control.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: root chamber insulation and possibly a chiller. Greenhouse temps spike fast."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse aero: chiller recommended for summer months.",
            },
        },
    },
    # ── 4. LATE VEGETATIVE ───────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Plant reaches target size before flip. Aero plants grow so fast that veg time is often 30-50% shorter than other methods. The root mass is now substantial — mist off-time can be extended further. Final system checks before flower: clean all nozzles, verify backup systems, prepare for the highest-demand period.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 55, "max": 70, "target": 60},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 600, "target": 500},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Full veg light intensity. Plants may be significantly larger than expected — aero veg is fast. Flip earlier than you would with other methods (plant at 33-50% of target height vs 50-66% for other methods, because aero stretch is more aggressive).",
        },
        "mist_system": {
            "mist_on_sec": {"min": 3, "max": 5, "target": 3},
            "mist_off_sec": {"min": 300, "max": 480, "target": 360},
            "pressure_psi": {"hpa": {"min": 80, "max": 100, "target": 90}, "lpa": {"min": 30, "max": 50, "target": 40}},
            "nozzle_type": "Anti-drip mist nozzles.",
            "day_cycle": {
                "on_sec": 3,
                "off_sec": 360,
                "notes": "3 seconds on, 6 minutes off. Large root mass retains moisture well. Longer off-time = more oxygen to roots.",
            },
            "night_cycle": {
                "on_sec": 3,
                "off_sec": 600,
                "notes": "3 seconds on, 10 minutes off at night. Plant transpires less at night. Roots need less frequent misting.",
            },
            "root_chamber_temp_f": {"min": 62, "max": 68, "target": 65},
            "droplet_size_microns": {
                "hpa": {"min": 30, "max": 80, "target": 50},
                "lpa": {"min": 100, "max": 500, "target": 200},
            },
            "notes": "Extended off-times. The root mass is substantial and retains moisture between cycles. More off-time = more oxygen exposure = faster nutrient uptake. But never let roots go fully dry. Pre-flip: clean ALL nozzles, flush lines, verify backup systems.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half strength by other-method standards. EC 0.8-1.2. Aero absorption efficiency means you need less. Watch for tip burn — it comes fast in aero.",
            "flora_micro_ml_per_gal": 1.25,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 0.625,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection throughout veg."},
            ],
        },
        "tasks": [
            {
                "name": "Pre-flip nozzle cleaning",
                "description": "Remove and clean ALL nozzles. Soak in H2O2 (3%) for 30 minutes. Rinse and reinstall. You do NOT want a nozzle failure during flower — fix everything now.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Test backup systems",
                "description": "Simulate power failure. Verify backup pump/UPS engages within 60 seconds. Test backup timer. In flower, a 5-minute mist failure can damage roots permanently.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Pre-flip reservoir change",
                "description": "Fresh reservoir with transition nutrients. Clean reservoir and pump intake. Replace inline filter if needed.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Canopy management",
                "description": "Aero plants grow fast — final topping, LST, SCROG net filling. Flip at 33-50% of target height (aero stretch is aggressive).",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Root mass inspection",
                "description": "Check for tangling, browning, or slime. Trim any dead root tips. Healthy aero roots are brilliant white and fluffy (not matted).",
                "interval_days": 3,
                "priority": "medium",
            },
            {
                "name": "Deep clean root chamber",
                "description": "If accessible: wipe down chamber walls with H2O2. Remove any biofilm or mineral deposits. Last chance before flower.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "All nozzles freshly cleaned and spraying fine mist?",
            "Backup systems tested and functional?",
            "Roots white, fluffy, and healthy?",
            "No algae or biofilm in chamber?",
            "Plant at 33-50% of target height?",
            "Canopy level and ready for flip?",
        ],
        "common_problems": [
            {
                "issue": "Plant too tall already (grew faster than expected)",
                "cause": "Aero veg is 30-50% faster than other methods — common mistake to veg too long",
                "solution": "Flip now. Supercrop tall branches. Next grow: flip earlier. Aero plants need less veg time than you think.",
            },
            {
                "issue": "Root mass tangled in nozzles",
                "cause": "Roots grew into the nozzle zone",
                "solution": "Gently untangle. Consider repositioning nozzles or using root guides/barriers. Roots blocking nozzles = uneven mist distribution.",
            },
            {
                "issue": "Tip burn appearing",
                "cause": "EC too high for aero efficiency — plant is getting more than it can use",
                "solution": "Reduce EC by 0.2-0.3. Aero doesn't need as much nutrition as other methods. Err on the side of less — you can always increase.",
            },
        ],
        "training": [
            {
                "technique": "SCROG net",
                "description": "Install screen at canopy height. Weave branches through. Fill 70-80% of squares before flipping. Aero plants fill the net faster than other methods.",
                "timing": "1 week before flip",
            },
            {
                "technique": "Lollipop",
                "description": "Remove lower 1/3 of growth. Redirect energy to top canopy.",
                "timing": "3-5 days before flip",
            },
        ],
        "transition_signals": [
            "Plant at 33-50% of target height",
            "Canopy filled",
            "All nozzles cleaned and verified",
            "Backup systems tested",
            "Root mass healthy and untangled",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor aero: natural photoperiod triggers flowering. Aero stretch outdoors can be extreme — plan for it."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: flip timing is nature's decision.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: light dep gives control over flip timing."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse aero: light dep recommended for photoperiod control.",
            },
        },
    },
    # ── 5. TRANSITION ────────────────────────────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 10, "max": 21, "typical": 14},
        "description": "Light cycle flipped to 12/12. Explosive stretch — aero plants can TRIPLE in height during stretch (more aggressive than other methods due to the massive healthy root system). Mist cycles need careful adjustment: the plant is transpiring heavily and roots are demanding more nutrients. This is the most dangerous period for nozzle failures.",
        "environment": {
            "temp_day_f": {"min": 74, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 72, "target": 68},
            "humidity_pct": {"min": 50, "max": 65, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 500, "max": 700, "target": 600},
            "light_dli": {"min": 22, "max": 30, "target": 26},
            "notes": "Flip to 12/12. Temperature DIF (day-night difference) of 10°F helps control stretch. Aero stretch is MORE aggressive than other methods — plan for 2-3x height increase.",
        },
        "mist_system": {
            "mist_on_sec": {"min": 3, "max": 5, "target": 4},
            "mist_off_sec": {"min": 240, "max": 360, "target": 300},
            "pressure_psi": {"hpa": {"min": 80, "max": 100, "target": 90}, "lpa": {"min": 30, "max": 50, "target": 40}},
            "nozzle_type": "Anti-drip mist nozzles.",
            "day_cycle": {
                "on_sec": 4,
                "off_sec": 300,
                "notes": "4 seconds on, 5 minutes off. Increase on-time slightly — plant is transpiring heavily during stretch and needs more moisture. Heavy root demand.",
            },
            "night_cycle": {
                "on_sec": 3,
                "off_sec": 480,
                "notes": "3 seconds on, 8 minutes off at night. Night cycle stays similar to late veg.",
            },
            "root_chamber_temp_f": {"min": 62, "max": 68, "target": 65},
            "droplet_size_microns": {
                "hpa": {"min": 30, "max": 80, "target": 50},
                "lpa": {"min": 100, "max": 500, "target": 200},
            },
            "notes": "Slightly more mist (longer on-time or shorter off-time) to support explosive growth. The plant is drinking heavily — reservoir level drops fast. Top off daily. Nozzle failures during stretch are CRITICAL — check twice daily.",
        },
        "nutrients": {
            "strength_pct": 60,
            "approach": "Transition formula. Shift from grow-heavy to bloom-heavy ratio. EC 1.0-1.4. Increase CalMag — stretch demands calcium for rapid cell wall construction.",
            "flora_micro_ml_per_gal": 1.5,
            "flora_gro_ml_per_gal": 1.0,
            "flora_bloom_ml_per_gal": 1.0,
            "calmag_ml_per_gal": 2.0,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root protection. Warm flower temps increase pathogen risk.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Flip light cycle to 12/12",
                "description": "Ensure ZERO light leaks during dark period. Even brief light exposure can cause hermaphrodites. Aero plants are sensitive to stress.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Nozzle check — TWICE daily during stretch",
                "description": "Stretch is the highest-demand period. A clogged nozzle during stretch = permanent damage to that plant's root zone within an hour. Morning and evening checks.",
                "interval_days": 0.5,
                "priority": "high",
            },
            {
                "name": "Top off reservoir daily",
                "description": "The plant is drinking heavily during stretch. Reservoir may drop significantly in 24 hours. Top off with plain pH'd water to maintain volume and prevent EC spike.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Transition nutrient ratio",
                "description": "Shift from veg to bloom formula over 3-5 days. Increase CalMag for calcium-hungry stretch growth.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Manage stretch height",
                "description": "Supercrop, tuck into SCROG net. Aero stretch is aggressive — stay on top of it daily.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Check for preflowers / sex",
                "description": "Remove males immediately. Hermaphrodites from stress are possible — check every 2 days.",
                "interval_days": 2,
                "priority": "high",
            },
        ],
        "health_checks": [
            "ALL nozzles spraying fine mist (check twice daily)?",
            "Roots still white and healthy?",
            "Stretch height manageable?",
            "No hermaphrodite signs?",
            "Reservoir level adequate?",
            "No light leaks during dark period?",
            "Root chamber temp under 72°F?",
        ],
        "common_problems": [
            {
                "issue": "Extreme stretch (plant hitting lights)",
                "cause": "Aero root systems drive more aggressive stretch than other methods",
                "solution": "Supercrop immediately. Raise lights to maximum height. Increase negative DIF (cooler days, warmer nights temporarily). Next grow: flip earlier.",
            },
            {
                "issue": "Nozzle clog during stretch",
                "cause": "High nutrient concentration or biofilm in lines",
                "solution": "EMERGENCY. Replace nozzle immediately. Run backup mist for affected zone. Clean all nozzles within 24 hours. Check inline filter.",
            },
            {
                "issue": "Reservoir depleting rapidly",
                "cause": "Explosive growth consuming massive amounts of water",
                "solution": "Normal for aero stretch. Top off 1-2x daily with plain pH'd water. Consider a larger reservoir. Automated float valve is ideal.",
            },
            {
                "issue": "Calcium deficiency during stretch",
                "cause": "Rapid growth demanding more calcium than supplied",
                "solution": "Increase CalMag to 2-3 ml/gal. Brown spots on new growth = calcium deficiency. Very common during stretch in all methods, especially aero due to growth speed.",
            },
        ],
        "training": [
            {
                "technique": "Supercropping",
                "description": "Crush and bend tall stems 90°. Aero plants heal supercrop injuries in 2-3 days (vs 5-7 for other methods) due to the powerful root system.",
                "timing": "First 2 weeks of stretch",
            },
            {
                "technique": "SCROG tucking",
                "description": "Continue tucking into net daily. Aero growth is fast — miss a day and branches escape the net.",
                "timing": "Throughout stretch",
            },
        ],
        "transition_signals": [
            "Stretch slowing",
            "White pistils at bud sites",
            "Flower sites forming",
            "Vertical growth stopping",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: natural photoperiod triggers stretch. Light pollution is a hermaphrodite risk — audit the area."
                },
                "extra_tasks": [
                    {
                        "name": "Check for light pollution",
                        "description": "Any external light during the dark period risks hermaphrodites. Especially critical for stress-sensitive aero plants.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor aero stretch: expect extreme height gain.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: light dep tarps give photoperiod control. Pull consistently."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: light dep recommended.",
            },
        },
    },
    # ── 6. EARLY FLOWER ──────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Stretch has ended. Buds forming and fattening. Mist cycle optimization is critical: slightly longer off-times give roots more oxygen, pushing energy into flower production (analogous to generative steering in drip). EC increases to support bud development. Nozzle reliability is now a SURVIVAL issue — a clog during flower development means permanent yield loss.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 62, "max": 70, "target": 66},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Peak light intensity. Humidity dropping to prevent bud rot. Day/night DIF of 10-12°F. CO2 to 1000-1200 ppm if supplementing.",
        },
        "mist_system": {
            "mist_on_sec": {"min": 3, "max": 5, "target": 4},
            "mist_off_sec": {"min": 300, "max": 480, "target": 360},
            "pressure_psi": {"hpa": {"min": 80, "max": 100, "target": 90}, "lpa": {"min": 30, "max": 50, "target": 40}},
            "nozzle_type": "Anti-drip mist nozzles.",
            "day_cycle": {
                "on_sec": 4,
                "off_sec": 360,
                "notes": "4 seconds on, 6 minutes off. Slightly longer off-time pushes generative response (more oxygen = more flower energy). Don't go too long — roots must never dry.",
            },
            "night_cycle": {
                "on_sec": 3,
                "off_sec": 600,
                "notes": "3 seconds on, 10 minutes off at night. Flower-stage night cycles can be extended as transpiration is minimal.",
            },
            "root_chamber_temp_f": {"min": 62, "max": 68, "target": 65},
            "droplet_size_microns": {
                "hpa": {"min": 30, "max": 80, "target": 50},
                "lpa": {"min": 100, "max": 500, "target": 200},
            },
            "notes": "Generative misting: longer off-times give roots more air exposure, driving energy into flower production. This is the aero equivalent of dryback/crop steering in drip systems. But NEVER let roots dry — in aero, dry roots = dead roots in minutes. Monitor root tips: glistening = perfect. Dry = emergency. Dripping = too much mist.",
        },
        "nutrients": {
            "strength_pct": 70,
            "approach": "Full bloom formula. EC 1.4-1.8. Higher PK for flower development. Still lower than DWC/drip equivalent due to aero efficiency.",
            "flora_micro_ml_per_gal": 1.75,
            "flora_gro_ml_per_gal": 0.7,
            "flora_bloom_ml_per_gal": 1.75,
            "calmag_ml_per_gal": 2.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection throughout flower."},
                {
                    "name": "Liquid Kool Bloom",
                    "dose_ml_per_gal": 0.75,
                    "purpose": "PK booster for early flower. Start conservative — aero absorbs supplements efficiently.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Extend mist off-time for generative push",
                "description": "Increase off-time to 6 minutes day / 10 minutes night. This gives roots more oxygen, pushing energy into flowers. Monitor root tips — they must stay moist.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Nozzle check — daily minimum",
                "description": "A clogged nozzle during flower = permanent yield loss for that plant. Check every nozzle daily. Replace or clean any suspect nozzle immediately.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Root zone temp check",
                "description": "Flower stage: keep root chamber at 64-70°F. Cooler roots during flower improve terpene production and bud density. Warmer roots = pathogen risk.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Defoliate for airflow",
                "description": "Remove large fan leaves blocking bud sites. Open up the canopy interior. Critical for bud rot prevention.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check for bud rot / PM",
                "description": "Dense canopy + high humidity in root chamber nearby = risk. Inspect flower sites every 2 days.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Reservoir change",
                "description": "Full reservoir change every 5-7 days during flower. Clean reservoir. Fresh bloom nutrients.",
                "interval_days": 7,
                "priority": "high",
            },
        ],
        "health_checks": [
            "ALL nozzles spraying fine mist?",
            "Roots still white and fluffy (not matted or brown)?",
            "Root chamber temp 64-70°F?",
            "Buds forming at all flower sites?",
            "No bud rot or powdery mildew?",
            "Good airflow through canopy?",
            "Backup systems still functional?",
        ],
        "common_problems": [
            {
                "issue": "Root tips turning brown in flower",
                "cause": "Chamber too warm, Pythium, or nozzle partially clogged (reduced mist coverage)",
                "solution": "Check chamber temp (must be under 70°F). Increase Hydroguard. Check every nozzle. Brown roots in aero = emergency. Healthy aero roots are WHITE.",
            },
            {
                "issue": "Nutrient burn (tip burn)",
                "cause": "EC too high for aero efficiency — plant is getting more than it needs",
                "solution": "Reduce EC by 0.2. Aero nutrient burn appears faster than in other methods because absorption is more efficient. Err on the side of less.",
            },
            {
                "issue": "Bud rot starting",
                "cause": "Humidity too high near the canopy (root chamber humidity escaping)",
                "solution": "Ensure root chamber is sealed properly. Lower ambient humidity to 45%. Defoliate aggressively. Remove affected buds immediately.",
            },
            {
                "issue": "Nozzle clog during early flower",
                "cause": "Nutrient precipitate, biofilm, or mineral deposit",
                "solution": "Replace immediately with spare. Clean all nozzles within 24 hours. Flush lines. Check inline filter. This is why spare nozzles are mandatory in aero.",
            },
        ],
        "training": [
            {
                "technique": "Defoliation",
                "description": "Remove blocking fan leaves. One defoliation at start of early flower. Then only individual leaves as needed. Never more than 20% at once.",
                "timing": "Day 1-3 of early flower",
            },
            {
                "technique": "Lollipopping",
                "description": "Remove all growth below SCROG net or lower 1/3. These sites won't produce quality buds in aero either.",
                "timing": "First week of early flower only",
            },
        ],
        "transition_signals": [
            "Buds visibly fattening daily",
            "White pistils thickening",
            "Trichomes appearing on sugar leaves",
            "Strong flower aroma",
            "Stretch completely stopped",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor aero flower: bud rot risk is extreme with moisture from root chamber + outdoor humidity. Seal chamber meticulously."
                },
                "extra_tasks": [
                    {
                        "name": "Shake plants after rain/dew",
                        "description": "Moisture + outdoor humidity + aero root chamber moisture = bud rot cocktail. Shake plants and improve airflow.",
                        "interval_days": None,
                        "priority": "high",
                    },
                ],
                "extra_problems": [
                    {
                        "issue": "Extreme bud rot risk",
                        "cause": "Root chamber humidity + outdoor humidity + rain",
                        "solution": "Seal root chamber perfectly. Cover plants during rain. Defoliate aggressively. Consider whether outdoor aero flower is viable in your climate.",
                    },
                ],
                "notes": "Outdoor aero flower: highest bud rot risk of any method/environment combo.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: manage humidity aggressively. Root chamber adds significant moisture to the growing environment."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse aero: dehumidification critical during flower.",
            },
        },
    },
    # ── 7. MID FLOWER ────────────────────────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid Flower (Peak Bloom)",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Peak bud development. Buds fattening rapidly, trichome production accelerating. Mist cycles optimized for maximum generative push: extended off-times for root oxygenation. EC at its highest (still lower than other methods). Nozzle reliability is life-or-death — a failure now means catastrophic yield loss.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 78, "target": 76},
            "temp_night_f": {"min": 60, "max": 68, "target": 64},
            "humidity_pct": {"min": 40, "max": 50, "target": 45},
            "vpd_kpa": {"min": 1.4, "max": 1.6, "target": 1.5},
            "light_hours": 12,
            "light_ppfd": {"min": 700, "max": 1000, "target": 850},
            "light_dli": {"min": 30, "max": 43, "target": 37},
            "notes": "Peak light intensity. Humidity under 50% — dense buds trap moisture. Day/night DIF of 12°F+ for terpene production. CO2 at 1200-1500 ppm if supplementing.",
        },
        "mist_system": {
            "mist_on_sec": {"min": 3, "max": 5, "target": 4},
            "mist_off_sec": {"min": 360, "max": 600, "target": 480},
            "pressure_psi": {"hpa": {"min": 80, "max": 100, "target": 90}, "lpa": {"min": 30, "max": 50, "target": 40}},
            "nozzle_type": "Anti-drip mist nozzles.",
            "day_cycle": {
                "on_sec": 4,
                "off_sec": 480,
                "notes": "4 seconds on, 8 minutes off. Maximum generative push — longest off-time of the grow. Roots get extended air exposure between mists, driving flower production. Monitor root tips obsessively.",
            },
            "night_cycle": {
                "on_sec": 3,
                "off_sec": 720,
                "notes": "3 seconds on, 12 minutes off at night. Very long off-times at night are safe because transpiration is minimal. Roots stay moist longer.",
            },
            "root_chamber_temp_f": {"min": 62, "max": 68, "target": 65},
            "droplet_size_microns": {
                "hpa": {"min": 30, "max": 80, "target": 50},
                "lpa": {"min": 100, "max": 500, "target": 200},
            },
            "notes": "PEAK GENERATIVE MISTING. Longest off-times of the entire grow. Extended air exposure drives root oxygenation and pushes energy into bud production. But root tips must NEVER go dry — check between cycles. If any root tips look dry or papery, reduce off-time immediately. Cooler root chamber (62-68°F) during mid-flower improves terpene retention.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Peak bloom. EC 1.6-2.0. This is the highest EC in aero — still lower than DWC/drip peak (2.6-3.0) due to mist absorption efficiency. PK-heavy.",
            "flora_micro_ml_per_gal": 1.875,
            "flora_gro_ml_per_gal": 0.5,
            "flora_bloom_ml_per_gal": 1.875,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {
                    "name": "Hydroguard",
                    "dose_ml_per_gal": 2,
                    "purpose": "Root protection. Non-negotiable through harvest.",
                },
                {
                    "name": "Liquid Kool Bloom",
                    "dose_ml_per_gal": 1.5,
                    "purpose": "PK booster at peak dose. Conservative vs drip/DWC because aero absorbs more efficiently.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Peak generative mist cycle",
                "description": "8 minutes off during day, 12 minutes off at night. This is the limit — monitor root tips twice daily. Any drying = reduce off-time.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Nozzle check — daily, non-negotiable",
                "description": "Check EVERY nozzle EVERY day. Mid-flower nozzle failure = catastrophic. Have spare nozzles within arm's reach of the grow.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Root health inspection",
                "description": "Open chamber and inspect roots. Should be white, fluffy, extensive. Any brown, slimy, or matted sections = immediate action. Healthy aero roots look like cotton candy.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Inspect buds for mold daily",
                "description": "Pull apart largest colas gently. Dense aero buds + root chamber humidity = bud rot risk. Catch it early.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Reservoir change",
                "description": "Full change every 5-7 days. At peak EC, nutrient balance drifts faster. Fresh reservoir = balanced nutrition.",
                "interval_days": 7,
                "priority": "high",
            },
            {
                "name": "Support heavy branches",
                "description": "Aero produces heavy, dense buds. Trellis nets, yo-yos, or stakes to prevent branch snapping.",
                "interval_days": 3,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "ALL nozzles spraying fine mist?",
            "Root tips moist between cycles (never dry)?",
            "Roots white and fluffy (not brown/slimy/matted)?",
            "Root chamber temp 62-68°F?",
            "No bud rot in any cola?",
            "Trichomes developing (milky under magnification)?",
            "Heavy branches supported?",
        ],
        "common_problems": [
            {
                "issue": "Root tips drying between extended mist cycles",
                "cause": "Off-time too long for current conditions (temp, humidity, root mass)",
                "solution": "Reduce off-time by 60-120 seconds. Different plants/genetics tolerate different off-times. If even one plant's roots are drying, the cycle is too long for that plant.",
            },
            {
                "issue": "Root mass matting together",
                "cause": "Dense root growth compacting. Mist not penetrating to inner roots",
                "solution": "Gently separate matted sections. Ensure nozzles are positioned to spray into (not across) the root mass. Consider additional nozzle for coverage.",
            },
            {
                "issue": "Bud rot despite low humidity",
                "cause": "Root chamber humidity escaping near plant stems, creating a moisture microclimate around buds",
                "solution": "Seal collar-to-chamber junction better. Add small fan blowing across the top of the chamber (where stems exit). This creates a dry boundary between root chamber humidity and the canopy.",
            },
            {
                "issue": "Nozzle clog during peak flower",
                "cause": "High-EC nutrients precipitating, biofilm, or mineral buildup",
                "solution": "EMERGENCY. Replace nozzle instantly. The affected plant's roots start dying in 5-10 minutes. Clean all nozzles within 24 hours. Flush lines. This is why spare nozzles MUST be on hand.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Buds dense and firm",
            "Trichomes mostly milky",
            "Pistils turning orange/brown",
            "Lower fan leaves yellowing naturally",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor aero mid-flower: if you've made it this far, maintain vigilance. Autumn weather can be unpredictable."
                },
                "extra_tasks": [
                    {
                        "name": "Monitor for storms",
                        "description": "Power outages kill aero plants in minutes. Have battery backup or generator ready during storm season.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor aero: power reliability is critical during mid-flower.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse: maintain aggressive dehumidification. Root chamber + greenhouse humidity = dangerous combo."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse aero: dehumidifier at full capacity during mid-flower.",
            },
        },
    },
    # ── 8. LATE FLOWER ───────────────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower (Ripening)",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Buds ripening. Trichomes transitioning from milky to amber. Begin reducing EC and mist frequency. The plant is finishing — it needs less. Mist off-times can extend further as the plant's water demand decreases. Some yellowing of fan leaves is natural and desired.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 78, "target": 75},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.4, "max": 1.8, "target": 1.6},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Slightly reduced light. Cooler night temps (58-62°F) bring out colors. Humidity at 35-45% — mature dense buds are highest rot risk.",
        },
        "mist_system": {
            "mist_on_sec": {"min": 3, "max": 5, "target": 3},
            "mist_off_sec": {"min": 420, "max": 720, "target": 600},
            "pressure_psi": {"hpa": {"min": 80, "max": 100, "target": 90}, "lpa": {"min": 30, "max": 50, "target": 40}},
            "nozzle_type": "Anti-drip mist nozzles.",
            "day_cycle": {
                "on_sec": 3,
                "off_sec": 600,
                "notes": "3 seconds on, 10 minutes off. Plant is drinking less. Extended off-times are safe — root mass is large and retains moisture well.",
            },
            "night_cycle": {
                "on_sec": 3,
                "off_sec": 900,
                "notes": "3 seconds on, 15 minutes off at night. Very long off-times as plant winds down. Monitor root tips but expect slower drying.",
            },
            "root_chamber_temp_f": {"min": 62, "max": 68, "target": 65},
            "droplet_size_microns": {
                "hpa": {"min": 30, "max": 80, "target": 50},
                "lpa": {"min": 100, "max": 500, "target": 200},
            },
            "notes": "Tapering mist cycles. Plant is finishing and drinking less. Longer off-times are fine — the large root mass retains moisture well and the plant's transpiration rate is decreasing. Root tips should still never go dry, but they'll stay moist longer between cycles now.",
        },
        "nutrients": {
            "strength_pct": 60,
            "approach": "Reducing. EC 1.2-1.6. Taper nitrogen. Maintain PK for final ripening. Plant is consuming stored nutrients — fan leaf yellowing is normal.",
            "flora_micro_ml_per_gal": 1.5,
            "flora_gro_ml_per_gal": 0.375,
            "flora_bloom_ml_per_gal": 1.5,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection through finish."},
                {
                    "name": "Liquid Kool Bloom",
                    "dose_ml_per_gal": 0.75,
                    "purpose": "Reduced PK. Tapering down from peak.",
                },
            ],
        },
        "tasks": [
            {
                "name": "Reduce EC and mist frequency",
                "description": "Drop EC to 1.2-1.6. Extend off-time to 10 min day / 15 min night. Plant is finishing.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Trichome checks with magnification",
                "description": "60-100x loupe on buds (not sugar leaves). Clear → milky → amber. Target harvest ratio depends on desired effect.",
                "interval_days": 2,
                "priority": "high",
            },
            {
                "name": "Continue daily nozzle checks",
                "description": "Still checking daily. A late-flower nozzle failure is still catastrophic — buds can't recover lost development.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Continue bud rot inspection",
                "description": "Risk remains high through harvest. Daily inspection of largest colas.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Plan harvest date",
                "description": "Based on trichome progression, estimate harvest. Plan flush to start 7-10 days before target.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Trichomes progressing toward amber?",
            "Fan leaves yellowing naturally?",
            "No bud rot?",
            "All nozzles still functioning?",
            "Root tips healthy despite reduced misting?",
        ],
        "common_problems": [
            {
                "issue": "Foxtailing on tops",
                "cause": "Light too intense or too close. Heat stress.",
                "solution": "Raise or dim lights by 10-15%. Late-flower buds are light-sensitive. Foxtails reduce bag appeal.",
            },
            {
                "issue": "Trichomes not progressing",
                "cause": "Temps too warm, or slow-finishing genetics",
                "solution": "Drop day temps to 73-75°F. Check breeder's stated flowering time. Some cultivars take 10-12 weeks. Patience.",
            },
            {
                "issue": "Root mass starting to brown at edges",
                "cause": "Natural senescence — plant is finishing and roots are aging",
                "solution": "Some browning at root tips is normal in late flower as the plant reallocates energy to buds. If the core root mass is still white, you're fine. If all roots are brown/slimy = Pythium, treat with H2O2 flush.",
            },
        ],
        "training": [],
        "transition_signals": [
            "30-50% pistils orange/brown",
            "Trichomes mostly milky with 5-15% amber",
            "Fan leaves dropping",
            "Plant drinking noticeably less",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor: frost kills cannabis. Monitor overnight lows. Be ready to harvest early."
                },
                "extra_tasks": [
                    {
                        "name": "Monitor frost forecasts",
                        "description": "Frost = instant death. Below 40°F = severe stress. Have emergency harvest plan.",
                        "interval_days": 1,
                        "priority": "high",
                    },
                ],
                "extra_problems": [],
                "notes": "Outdoor: weather dictates harvest timing.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: supplemental heating for cold nights. 60°F minimum."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: heating during cold nights.",
            },
        },
    },
    # ── 9. FLUSH ─────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush (Pre-Harvest)",
        "order": 9,
        "duration_days": {"min": 5, "max": 10, "typical": 7},
        "description": "Final flush before harvest. Run plain pH'd water through the mist system — no nutrients. Aero flush is faster than media-based methods (5-7 days vs 7-14) because there's no media holding salts. The roots are misted with pure water and the plant consumes stored nutrients rapidly. Fan leaf yellowing accelerates dramatically.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 76, "target": 73},
            "temp_night_f": {"min": 58, "max": 66, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 17, "max": 30, "target": 26},
            "notes": "Reduced light. Low humidity. Plant is finishing. Cooler temps are fine.",
        },
        "mist_system": {
            "mist_on_sec": {"min": 3, "max": 5, "target": 3},
            "mist_off_sec": {"min": 480, "max": 720, "target": 600},
            "pressure_psi": {"hpa": {"min": 80, "max": 100, "target": 90}, "lpa": {"min": 30, "max": 50, "target": 40}},
            "nozzle_type": "Anti-drip mist nozzles.",
            "day_cycle": {
                "on_sec": 3,
                "off_sec": 600,
                "notes": "3 seconds on, 10 minutes off. Plain water only. Maintain root moisture for nutrient transport out of tissues.",
            },
            "night_cycle": {
                "on_sec": 3,
                "off_sec": 900,
                "notes": "3 seconds on, 15 minutes off. Minimal night misting — just enough to keep roots alive.",
            },
            "root_chamber_temp_f": {"min": 62, "max": 68, "target": 65},
            "droplet_size_microns": {
                "hpa": {"min": 30, "max": 80, "target": 50},
                "lpa": {"min": 100, "max": 500, "target": 200},
            },
            "notes": "PLAIN WATER MISTING. No nutrients. Keep roots alive and moist so the plant can transport stored nutrients from leaves to buds. Aero flush is faster than media-based flushes because there's no salt-loaded media to leach. 5-7 days is typically sufficient.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "Plain pH'd water only (pH 5.5-5.8). Zero nutrients. Flush is faster in aero than any other method.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Switch to plain water",
                "description": "Drain nutrient reservoir. Clean reservoir. Fill with plain pH'd water (5.5-5.8). Run through entire mist system.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Flush nozzles and lines",
                "description": "Run clean water through the system for 10+ minutes continuously to clear all nutrient residue from nozzles and lines.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Continue trichome checks",
                "description": "Monitor daily. Harvest window approaching: mostly milky with 10-20% amber.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Continue nozzle checks",
                "description": "Even with plain water, nozzles can clog from mineral deposits. Check daily.",
                "interval_days": 1,
                "priority": "medium",
            },
            {
                "name": "Stop misting 12-24 hours before harvest",
                "description": "Let roots dry slightly before chop. Less water weight in the plant. Some believe final stress pushes trichome production.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Fan leaves yellowing dramatically (desired)?",
            "Buds still healthy (no rot)?",
            "Trichomes at target ratio?",
            "Roots still receiving mist (still alive)?",
        ],
        "common_problems": [
            {
                "issue": "Plant dying too fast during flush",
                "cause": "Roots drying out, or flush started too early",
                "solution": "Ensure mist system is still running (plain water). If leaves are crispy and buds look underdeveloped, the plant died rather than flushed. Keep roots moist.",
            },
            {
                "issue": "Bud rot during flush",
                "cause": "Weakened plant defenses + humidity",
                "solution": "Harvest immediately rather than risk more rot. A shorter flush is better than a moldy harvest.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Heavy fan leaf yellowing/drop",
            "Trichomes at target ratio",
            "Buds firm and sticky",
            "Most pistils brown/orange",
            "5-7 days elapsed",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor flush: stop nutrient solution, run plain water. Monitor weather for harvest window."
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: weather may force early harvest during flush.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: maintain humidity management through flush."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: keep environment controlled through flush.",
            },
        },
    },
    # ── 10. HARVEST ──────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 3, "typical": 1},
        "description": "Chop day. Shut down the mist system. Cut plants, wet trim or whole-plant hang. Clean and store all nozzles, lines, pump, and root chamber. Aero systems are cleaner at harvest than media-based methods — no media to dispose of.",
        "environment": {
            "temp_day_f": {"min": 65, "max": 75, "target": 70},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Some growers give 24-48 hours of darkness before chop. Harvest in the morning. Room light only for working.",
        },
        "mist_system": {
            "mist_on_sec": 0,
            "mist_off_sec": 0,
            "pressure_psi": 0,
            "nozzle_type": None,
            "day_cycle": None,
            "night_cycle": None,
            "root_chamber_temp_f": None,
            "droplet_size_microns": None,
            "notes": "System OFF. After harvest: remove all nozzles, soak in H2O2 for 1 hour, rinse, dry, store. Flush all lines with H2O2 then plain water. Clean root chamber thoroughly. Dry everything before storage.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None. System shut down.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Final trichome check",
                "description": "Confirm target ratio before chopping. 70-80% milky, 10-20% amber, minimal clear.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Harvest the plant",
                "description": "Cut main stem at the collar. For wet trim: remove fan leaves and trim sugar leaves now. For dry trim: remove fan leaves only, hang whole plant.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Clean all nozzles",
                "description": "Remove every nozzle. Soak in 3% H2O2 for 1 hour. Rinse with clean water. Dry completely. Store in a clean container.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Flush and clean lines",
                "description": "Run H2O2 solution through all lines for 15 minutes. Then flush with plain water. Drain completely. Coil and store dry.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Clean root chamber",
                "description": "Remove root debris. Scrub chamber with H2O2 or dilute bleach. Rinse thoroughly. Dry completely. Biofilm and mineral deposits must be removed.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Clean reservoir and pump",
                "description": "Drain, scrub, sanitize. Clean pump impeller and intake screen. Store dry.",
                "interval_days": None,
                "priority": "medium",
            },
        ],
        "health_checks": [
            "Trichome ratio at target?",
            "No bud rot discovered during trim?",
            "All nozzles cleaned and stored?",
            "All lines flushed and stored?",
            "Root chamber cleaned and dry?",
        ],
        "common_problems": [
            {
                "issue": "Bud rot discovered during trim",
                "cause": "Hidden rot inside dense colas",
                "solution": "Cut away rotted sections plus 1 inch margin. Salvage clean buds. Do not dry or cure rotted material.",
            },
            {
                "issue": "Nozzles corroded or degraded",
                "cause": "Long-term exposure to nutrient solution and pressure cycling",
                "solution": "Replace degraded nozzles before next grow. Nozzles are consumables in aero — budget for replacements every 1-2 grows.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Plant chopped",
            "All material hung or in drying room",
            "Aero system cleaned and stored",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Outdoor: harvest before frost. Have drying space ready."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Outdoor: weather may force harvest timing.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Greenhouse: controlled harvest timing."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse: use space for drying if possible.",
            },
        },
    },
    # ── 11. DRYING ───────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Slow, controlled drying. 60°F / 60% humidity / darkness (the '60/60 rule'). 10-14 days is ideal. Faster drying destroys terpenes. Aero-grown buds can be denser than average — they may take slightly longer to dry through.",
        "environment": {
            "temp_day_f": {"min": 58, "max": 65, "target": 60},
            "temp_night_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK. 60°F. 60% humidity. Gentle airflow (not on buds directly). Hay smell = drying too fast.",
        },
        "mist_system": {
            "mist_on_sec": 0,
            "mist_off_sec": 0,
            "pressure_psi": 0,
            "nozzle_type": None,
            "day_cycle": None,
            "night_cycle": None,
            "root_chamber_temp_f": None,
            "droplet_size_microns": None,
            "notes": "No aero system involvement. Drying is purely environmental control.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None. Plant is harvested.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Hang whole plants or branches",
                "description": "Hang upside down. Space so plants don't touch. Air must circulate around all sides.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Maintain 60/60 environment",
                "description": "60°F, 60% humidity, darkness. Monitor with hygrometer.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Check drying progress",
                "description": "Bend a small stem. Snaps cleanly = ready for cure. Bends = keep drying. Aero buds may be denser — allow extra time.",
                "interval_days": 1,
                "priority": "high",
            },
            {
                "name": "Inspect for mold",
                "description": "Mold can appear during drying. Dense aero-grown buds are higher risk. Inspect daily.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "Temperature 58-65°F?",
            "Humidity 55-65%?",
            "No direct airflow on buds?",
            "Room completely dark?",
            "No mold?",
            "Smells like cannabis (not hay)?",
        ],
        "common_problems": [
            {
                "issue": "Drying too fast",
                "cause": "Humidity too low, temp too high, too much airflow",
                "solution": "Raise humidity to 60-65%. Lower temp to 60°F. Reduce fan speed. Whole-plant hang slows drying.",
            },
            {
                "issue": "Mold on dense aero-grown buds",
                "cause": "Density + moisture trapped inside",
                "solution": "Remove moldy buds. Lower humidity to 55%. Increase gentle airflow. Break dense buds into smaller pieces if needed.",
            },
            {
                "issue": "Hay smell",
                "cause": "Drying too fast — chlorophyll trapped",
                "solution": "Slow down. Long cure (4-8 weeks) can partially recover.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Small stems snap cleanly",
            "Outer buds dry but not crunchy",
            "Larger stems have slight flex",
            "7-14 days at proper conditions",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Dry indoors regardless of grow method."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Always dry indoors.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Too warm and light for drying. Move to a separate dark room."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Do not dry in greenhouse.",
            },
        },
    },
    # ── 12. CURING ───────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 60, "typical": 30},
        "description": "Slow cure in airtight containers. Terpenes develop, harshness mellows, quality finalizes. Minimum 2 weeks, ideal 4-8 weeks. Aero-grown flower is often noted for exceptional terpene profiles when properly cured — the high-oxygen root environment during growth promotes terpene precursor production.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 60, "max": 70, "target": 65},
            "humidity_pct": {"min": 58, "max": 62, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Inside jar: 58-62% RH (Boveda 62 packs). Store in dark, cool place. Light degrades THC.",
        },
        "mist_system": {
            "mist_on_sec": 0,
            "mist_off_sec": 0,
            "pressure_psi": 0,
            "nozzle_type": None,
            "day_cycle": None,
            "night_cycle": None,
            "root_chamber_temp_f": None,
            "droplet_size_microns": None,
            "notes": "No aero system involvement. Post-harvest processing.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "None. Post-harvest.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [],
        },
        "tasks": [
            {
                "name": "Trim and jar buds",
                "description": "Trim sugar leaves. Place buds loosely in mason jars (75% full, not packed). If wet-trimmed: jar directly.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Burp jars — first 2 weeks",
                "description": "Open jars 10-15 min, 2-3x/day first week. Once/day second week. Exchanges air and releases moisture.",
                "interval_days": None,
                "priority": "high",
            },
            {
                "name": "Add Boveda packs",
                "description": "Boveda 62% RH, 1 per oz. Maintains perfect humidity passively.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Reduce burping after 2 weeks",
                "description": "Every 2-3 days after 2 weeks. Once/week after 4 weeks. Seal long-term after 8 weeks.",
                "interval_days": None,
                "priority": "medium",
            },
            {
                "name": "Monitor for mold",
                "description": "Inspect when burping. White fuzz = remove affected buds immediately.",
                "interval_days": 1,
                "priority": "high",
            },
        ],
        "health_checks": [
            "In-jar humidity 58-62%?",
            "No mold or ammonia smell?",
            "Buds improving in smell and smoothness?",
            "Jars in darkness at 60-70°F?",
        ],
        "common_problems": [
            {
                "issue": "Ammonia smell",
                "cause": "Buds too wet when jarred — anaerobic decomposition",
                "solution": "Remove buds, dry 12-24 hours on screen, rejar. If smell persists, buds may be compromised.",
            },
            {
                "issue": "Buds too dry",
                "cause": "Over-dried or too much burping",
                "solution": "Add Boveda 62 pack. Reduce burping. Tortilla trick for emergency rehydration (remove promptly).",
            },
            {
                "issue": "Mold in jars",
                "cause": "Too wet when jarred, or insufficient burping",
                "solution": "Discard moldy buds. Dry remaining 12 hours. Sanitize jar. Rejar with more frequent burping.",
            },
        ],
        "training": [],
        "transition_signals": [
            "Rich complex aroma (not grassy)",
            "Smooth smoke",
            "Slight stickiness",
            "Jar humidity stable at 58-62%",
            "Minimum 2 weeks elapsed",
        ],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {"notes": "Same curing process. Store indoors."},
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Curing is identical for all grow methods.",
            },
            "greenhouse": {
                "environment_overrides": {"notes": "Do not cure in greenhouse. Move to stable indoor location."},
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
        "description": "Post-cure long-term storage. Aeroponics produces some of the highest quality flower due to maximum oxygenation and precise nutrient delivery — storage must preserve that premium quality. Rapid aero growth cycles mean inventory accumulates fast. Proper storage preserves potency and terpenes for 6-12+ months.",
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
        "mist_system": None,
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
                "description": "Strain, harvest date, storage date, weight, batch number. Commercial: seed-to-sale, FIFO rotation.",
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
# EQUIPMENT — everything needed for an Aeroponics grow
# ─────────────────────────────────────────────────────────────────────────────

AERO_EQUIPMENT: list[dict] = [
    # -- Mist system core --
    {
        "name": "Mist nozzles (anti-drip preferred)",
        "category": "mist_system",
        "required": True,
        "notes": "1-2 per plant depending on root zone coverage. Anti-drip nozzles prevent continuous dripping between cycles. HPA: Tefen/Dramm fogger nozzles (50-micron droplets). LPA: standard mist nozzles.",
    },
    {
        "name": "High-pressure pump (HPA) or submersible pump (LPA)",
        "category": "mist_system",
        "required": True,
        "notes": "HPA: diaphragm pump rated for 80-100 PSI continuous duty. LPA: submersible pump rated for 30-50 PSI. Size for total nozzle flow rate + 20% headroom.",
    },
    {
        "name": "Accumulator tank (HPA only)",
        "category": "mist_system",
        "required": False,
        "notes": "HPA ONLY. Pre-pressurized tank that delivers instant pressure on demand. Prevents pump cycling every mist event. Size: 1-2 gallons for most home setups.",
    },
    {
        "name": "Solenoid valve(s)",
        "category": "mist_system",
        "required": True,
        "notes": "Electrically actuated valve controlled by timer. Opens for mist, closes between cycles. Must be rated for your operating pressure. Food-safe materials. Normally-closed type (fails safe = no mist, not continuous mist).",
    },
    {
        "name": "Cycle timer (SECOND resolution)",
        "category": "mist_system",
        "required": True,
        "notes": "NON-NEGOTIABLE. Must handle seconds on / minutes off. CT-2 cycle timer, Arduino/ESP32 controller, or commercial aero controller. Standard minute-resolution timers CANNOT run aeroponics. Day/night separate programming preferred.",
    },
    {
        "name": "Inline filter (fine mesh, 100-200+)",
        "category": "mist_system",
        "required": True,
        "notes": "Between pump and nozzles. Catches precipitates before they reach nozzles. This alone prevents 80% of nozzle clogs. Clean weekly minimum. HPA: finer mesh (200+).",
    },
    {
        "name": "Pressure gauge",
        "category": "mist_system",
        "required": True,
        "notes": "Monitor system pressure. Pressure drop = clogged filter, failing pump, or leak. Essential for diagnosing problems before they become emergencies.",
    },
    {
        "name": "Pressure regulator",
        "category": "mist_system",
        "required": False,
        "notes": "Maintains consistent pressure regardless of pump output variations. More important for HPA. LPA can often operate without one.",
    },
    {
        "name": "Spare nozzles (20-30% of total)",
        "category": "mist_system",
        "required": True,
        "notes": "NON-NEGOTIABLE. More spares than any other method because nozzle failure is more catastrophic. Keep them within arm's reach of the grow. A clogged nozzle is a 5-minute emergency.",
    },
    # -- Root chamber --
    {
        "name": "Root chamber (light-tight, food-safe)",
        "category": "root_chamber",
        "required": True,
        "notes": "Must be 100% light-tight. Any light = algae = clogged nozzles. Food-safe plastic or stainless steel. Drain at bottom for runoff return to reservoir. Size for your root mass — roots grow FAST in aero.",
    },
    {
        "name": "Neoprene collars / net pot lids",
        "category": "root_chamber",
        "required": True,
        "notes": "Seal around plant stems in the chamber lid. Must block ALL light. Neoprene is flexible and reusable. Have extra sizes for different stem diameters.",
    },
    {
        "name": "Root chamber thermometer",
        "category": "root_chamber",
        "required": True,
        "notes": "Monitor root zone temperature continuously. Target 65-68°F. Above 72°F = pathogen risk. Below 60°F = slow growth. Wireless sensor is ideal.",
    },
    # -- Reservoir --
    {
        "name": "Reservoir (opaque)",
        "category": "reservoir",
        "required": True,
        "notes": "Light-proof. Catches drain-back from root chamber. Size: minimum 2-3 gallons per plant. Aero reservoirs cycle faster than DWC — larger is more stable.",
    },
    {
        "name": "Air pump + air stone (for reservoir)",
        "category": "reservoir",
        "required": False,
        "notes": "Oxygenates nutrient solution in reservoir. Helpful but less critical than in DWC — the mist process itself oxygenates the solution.",
    },
    {
        "name": "Water chiller (strongly recommended)",
        "category": "reservoir",
        "required": False,
        "notes": "Keeps reservoir and root chamber cool. 65-68°F target. Strongly recommended for any climate where ambient temps exceed 75°F. In aero, warm roots = dead roots faster than any other method.",
    },
    # -- Backup systems (NON-OPTIONAL in aero) --
    {
        "name": "UPS / battery backup for pump + timer",
        "category": "backup",
        "required": True,
        "notes": "NON-NEGOTIABLE. A 5-minute power outage kills aero plants. UPS must power pump and timer for minimum 30-60 minutes. This is not optional — it is survival equipment.",
    },
    {
        "name": "Backup pump",
        "category": "backup",
        "required": True,
        "notes": "Pre-plumbed or ready to swap in under 5 minutes. If the primary pump fails, you have minutes, not hours. Test the backup monthly.",
    },
    {
        "name": "Audible alarm (pump failure / pressure loss)",
        "category": "backup",
        "required": False,
        "notes": "Pressure switch + buzzer that alerts you if pressure drops below operating threshold. For unattended grows, this can save the entire crop.",
    },
    # -- Monitoring --
    {
        "name": "pH meter (accurate to 0.1)",
        "category": "monitoring",
        "required": True,
        "notes": "Calibrate weekly. Aero pH range is 5.5-5.8 (tighter than DWC). Bluelab or Apera recommended.",
    },
    {
        "name": "EC/TDS meter",
        "category": "monitoring",
        "required": True,
        "notes": "Aero EC is lower than other methods. Precise measurement matters more. Calibrate monthly.",
    },
    {
        "name": "Jeweler's loupe (60-100x)",
        "category": "monitoring",
        "required": True,
        "notes": "Trichome inspection during late flower/harvest.",
    },
    # -- Environment --
    {
        "name": "Grow light (LED preferred)",
        "category": "environment",
        "required": True,
        "notes": "Size for canopy. 30-40 watts/sq ft LED. Dimmable for stage-appropriate PPFD.",
    },
    {
        "name": "Exhaust fan + carbon filter",
        "category": "environment",
        "required": True,
        "notes": "Odor control and air exchange. Size for room volume.",
    },
    {
        "name": "Oscillating fan(s)",
        "category": "environment",
        "required": True,
        "notes": "Canopy airflow. Don't blow directly on buds during flower.",
    },
    {
        "name": "Temperature/humidity controller",
        "category": "environment",
        "required": True,
        "notes": "AC Infinity or Inkbird. Climate control is critical — especially with a root chamber adding humidity to the room.",
    },
    {
        "name": "Dehumidifier",
        "category": "environment",
        "required": True,
        "notes": "Root chamber adds significant humidity to the grow space. Dehumidifier is essential during flower. Size for your room + root chamber moisture output.",
    },
    # -- Nutrients --
    {
        "name": "Base nutrient system (Flora Trio or equivalent)",
        "category": "nutrients",
        "required": True,
        "notes": "SYNTHETIC ONLY for aero. No organic nutrients — they clog nozzles. Flora Trio, Athena Pro, Jacks 321. Clean-dissolving formulas.",
    },
    {
        "name": "CalMag supplement",
        "category": "nutrients",
        "required": True,
        "notes": "Recommended for all aero grows. Clean synthetic CalMag only.",
    },
    {
        "name": "pH Up/Down solutions",
        "category": "nutrients",
        "required": True,
        "notes": "Maintain pH 5.5-5.8. Tighter range than DWC.",
    },
    {
        "name": "Hydroguard (beneficial bacteria)",
        "category": "nutrients",
        "required": True,
        "notes": "Root zone protection. Essential in aero — warm, humid root chambers are Pythium incubators.",
    },
    {
        "name": "Hydrogen peroxide (3%)",
        "category": "maintenance",
        "required": True,
        "notes": "Nozzle cleaning, line flushing, chamber sanitization. Use between grows and for emergency cleaning.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE — cheat-sheet values for daily operations
# ─────────────────────────────────────────────────────────────────────────────

AERO_QUICK_REFERENCE: dict = {
    "ph_range": {
        "min": 5.5,
        "max": 5.8,
        "sweet_spot": 5.6,
        "notes": "Tighter pH range than DWC/drip. Aero mist absorption is pH-sensitive. Stay in the sweet spot.",
    },
    "ec_by_stage": {
        "germination": 0.0,
        "seedling": 0.3,
        "early_veg": 0.6,
        "late_veg": 1.0,
        "transition": 1.2,
        "early_flower": 1.6,
        "mid_flower": 1.8,
        "late_flower": 1.4,
        "flush": 0.0,
    },
    "mist_cycle_by_stage": {
        "description": "Mist timing is the core of aeroponics. These are starting points — adjust based on root observation.",
        "seedling": {"day": "5s on / 3min off", "night": "5s on / 5min off"},
        "early_veg": {"day": "3s on / 5min off", "night": "3s on / 8min off"},
        "late_veg": {"day": "3s on / 6min off", "night": "3s on / 10min off"},
        "transition": {"day": "4s on / 5min off", "night": "3s on / 8min off"},
        "early_flower": {"day": "4s on / 6min off", "night": "3s on / 10min off"},
        "mid_flower": {"day": "4s on / 8min off", "night": "3s on / 12min off"},
        "late_flower": {"day": "3s on / 10min off", "night": "3s on / 15min off"},
        "flush": {"day": "3s on / 10min off", "night": "3s on / 15min off"},
    },
    "hpa_vs_lpa": {
        "description": "High-Pressure vs Low-Pressure Aeroponics — fundamentally different systems.",
        "hpa": {
            "pressure_psi": "80-100+",
            "droplet_size": "30-80 microns",
            "equipment": "Diaphragm pump, accumulator tank, solenoid valves, fine-mesh filters",
            "pros": "Maximum oxygenation, fastest growth, highest efficiency",
            "cons": "Most complex, most expensive, most fragile, smallest margin for error",
            "best_for": "Experienced growers, commercial operations, maximum performance",
        },
        "lpa": {
            "pressure_psi": "20-60",
            "droplet_size": "100-500 microns",
            "equipment": "Submersible pump, standard mist nozzles, basic filter",
            "pros": "Simpler, cheaper, more forgiving, still excellent growth",
            "cons": "Larger droplets = less oxygenation, slightly slower growth than HPA",
            "best_for": "Home growers, first-time aero, still want aero performance",
        },
    },
    "root_observation_guide": {
        "description": "Your roots tell you everything. Learn to read them.",
        "glistening_moist": "Perfect. Roots are coated in fine mist droplets. Ideal state.",
        "dripping_wet": "Too much mist. Increase off-time. Roots need air exposure.",
        "dry_papery": "EMERGENCY. Roots are drying. Decrease off-time immediately. Check for clogged nozzle.",
        "white_fluffy": "Healthy. Dense, branching root system with fine root hairs visible.",
        "brown_slimy": "Pythium / root rot. Treat with H2O2 flush, increase Hydroguard, check chamber temp.",
        "matted_tangled": "Root mass too dense for nozzle coverage. Reposition nozzles or add nozzles.",
    },
    "failure_response_times": {
        "description": "In aeroponics, every failure is time-critical. Know your response windows.",
        "nozzle_clog": {
            "severity": "HIGH",
            "time_to_damage": "5-30 minutes",
            "action": "Replace nozzle immediately. Have spares within arm's reach.",
        },
        "pump_failure": {
            "severity": "CRITICAL",
            "time_to_damage": "5-10 minutes",
            "action": "Switch to backup pump. If no backup, hand-mist roots with spray bottle while diagnosing.",
        },
        "power_outage": {
            "severity": "CRITICAL",
            "time_to_damage": "5-10 minutes",
            "action": "UPS should engage automatically. If no UPS: hand-mist roots immediately.",
        },
        "solenoid_stuck_closed": {
            "severity": "HIGH",
            "time_to_damage": "5-10 minutes",
            "action": "Manually open valve. Replace solenoid.",
        },
        "solenoid_stuck_open": {
            "severity": "MEDIUM",
            "time_to_damage": "1-2 hours",
            "action": "Continuous mist suffocates roots over time. Close valve manually. Replace solenoid.",
        },
        "timer_failure": {
            "severity": "CRITICAL",
            "time_to_damage": "5-10 minutes",
            "action": "Run pump manually on short cycles while replacing timer.",
        },
    },
    "nozzle_maintenance": {
        "description": "Nozzle management is the #1 maintenance task in aeroponics.",
        "check_frequency": "Daily minimum. Twice daily during flower.",
        "cleaning_method": "Soak in 3% H2O2 for 30 min. For mineral deposits: pH 3.0 citric acid soak 1 hour.",
        "replacement_schedule": "Replace all nozzles every 1-2 grows even if they appear functional. Degraded nozzles produce larger droplets.",
        "spare_rule": "Keep 20-30% spare nozzles on hand at ALL times. More than any other spare part.",
        "no_organics": "NEVER use organic nutrients in aero. They clog nozzles within days. Synthetic only.",
    },
    "reservoir_change_schedule": "Every 5-7 days. Aero reservoirs are smaller and cycle faster. pH/EC drifts faster than DWC.",
    "nutrient_mixing_order": "1) CalMag → 2) Flora Micro → 3) Flora Gro → 4) Flora Bloom → 5) pH adjust. NO silica unless proven safe with your nozzles. NO organics.",
    "golden_rules": [
        "Nozzle check EVERY day. A clogged nozzle = dead plant in minutes.",
        "Backup pump and UPS are NON-OPTIONAL. Not recommended — required.",
        "Root chamber must be 100% light-tight. Any light = algae = clogged nozzles.",
        "Root zone temp 65-68°F. Above 72°F = pathogen risk. Above 75°F = root death.",
        "SYNTHETIC nutrients ONLY. Organic nutrients clog nozzles within days.",
        "Spare nozzles within arm's reach at ALL times. 20-30% of total count.",
        "Timer must handle SECONDS, not minutes. Standard timers cannot run aero.",
        "Read your roots: glistening = perfect, dripping = too wet, dry = emergency.",
        "Aero EC is lower than every other method. What's half-strength in DWC is full-strength in aero.",
        "Power failure = 5-10 minutes to root damage. UPS is survival equipment.",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# TROUBLESHOOTING — categorised quick-diagnosis tables
# ─────────────────────────────────────────────────────────────────────────────

AERO_TROUBLESHOOTING: list[dict] = [
    {
        "category": "Nozzle & Mist Problems",
        "issues": [
            {
                "symptom": "One plant wilting, others fine",
                "cause": "Clogged nozzle serving that plant",
                "fix": "Replace nozzle IMMEDIATELY (5-minute emergency). Clean all nozzles within 24 hours. Check inline filter.",
            },
            {
                "symptom": "Nozzles producing streams instead of mist",
                "cause": "Pressure too low, or nozzles partially clogged",
                "fix": "Check pump pressure on gauge. Clean nozzles. For HPA: verify accumulator is charged. Streams = dramatically reduced oxygen absorption.",
            },
            {
                "symptom": "Nozzles dripping between mist cycles",
                "cause": "Standard nozzles without anti-drip feature, or worn anti-drip valve",
                "fix": "Replace with anti-drip nozzles. Continuous dripping waterlogged roots and defeats the purpose of cycle timing.",
            },
            {
                "symptom": "Uneven mist coverage in chamber",
                "cause": "Nozzle positioning, pressure variation, or partially clogged nozzles",
                "fix": "Test each nozzle individually. Reposition for even coverage. Add nozzles to dead zones. All roots must receive mist.",
            },
            {
                "symptom": "Nozzles clogging every few days",
                "cause": "No inline filter, or using organic/incompatible nutrients",
                "fix": "Install/clean inline filter (200+ mesh for HPA). Switch to synthetic-only nutrients. Clean reservoir. Some nutrient brands are worse than others for nozzle compatibility.",
            },
        ],
    },
    {
        "category": "Root Zone & Chamber Problems",
        "issues": [
            {
                "symptom": "Roots turning brown and slimy",
                "cause": "Pythium (root rot) from warm chamber or contamination",
                "fix": "Flush system with H2O2 (3%). Cool root chamber below 70°F. Increase Hydroguard. Remove dead root material. Severe cases: may need to restart.",
            },
            {
                "symptom": "Algae in root chamber",
                "cause": "Light leak in chamber",
                "fix": "Find and seal light leak. Clean chamber with H2O2. Algae clogs nozzles and promotes pathogens. Every seal, fitting, and collar must be checked.",
            },
            {
                "symptom": "Roots drying between cycles",
                "cause": "Off-time too long, nozzle clogged, or root mass outgrew coverage",
                "fix": "Reduce off-time. Verify all nozzles. Add nozzles if root mass has expanded beyond current spray pattern.",
            },
            {
                "symptom": "Root chamber temperature rising",
                "cause": "Ambient heat, pump heat, or insufficient insulation",
                "fix": "Insulate chamber. Add water chiller to reservoir. Move pump outside chamber if possible. Hot root zone is the #1 killer in aero.",
            },
            {
                "symptom": "Roots matting and tangling together",
                "cause": "Dense root growth in confined space",
                "fix": "Gently separate. Ensure nozzles can penetrate the root mass. Consider larger chamber for next grow. Matted roots block mist penetration to inner roots.",
            },
        ],
    },
    {
        "category": "System Failure & Emergency",
        "issues": [
            {
                "symptom": "Pump stopped working",
                "cause": "Pump failure, power loss, or clogged intake",
                "fix": "EMERGENCY (5-10 min to damage). Switch to backup pump. If no backup: hand-mist roots with spray bottle every 2-3 minutes while diagnosing. Check power, intake screen, pump impeller.",
            },
            {
                "symptom": "Power outage",
                "cause": "Grid failure, tripped breaker",
                "fix": "EMERGENCY. UPS should engage automatically. If no UPS: hand-mist roots. Run generator. Do NOT leave aero plants without mist for more than 10 minutes.",
            },
            {
                "symptom": "Timer malfunctioning (continuous mist or no mist)",
                "cause": "Timer failure or programming error",
                "fix": "Continuous mist: open solenoid manually on a schedule. No mist: run pump manually. Replace timer. Test new timer 50+ cycles before trusting it.",
            },
            {
                "symptom": "Solenoid not opening (no mist despite pump running)",
                "cause": "Solenoid failure or electrical connection issue",
                "fix": "EMERGENCY. Manually open the solenoid valve. Check wiring. Replace solenoid. Keep a spare solenoid on hand.",
            },
            {
                "symptom": "Pressure dropping over time",
                "cause": "Leak in system, pump degrading, or accumulator losing charge",
                "fix": "Check all fittings for leaks (spray soapy water on connections, look for bubbles). Test pump output directly. Recharge or replace accumulator.",
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# MIST ENGINEERING — Aeroponics' core differentiator
# ─────────────────────────────────────────────────────────────────────────────

AERO_MIST_ENGINEERING: dict = {
    "hpa_vs_lpa": {
        "high_pressure_aeroponics": {
            "pressure_psi": {"min": 80, "max": 120, "target": 100},
            "droplet_size_microns": {"min": 5, "max": 50, "target": 30},
            "description": "True aeroponics — atomizes water into fine mist. Maximum oxygen exposure to roots.",
            "equipment": [
                "High-pressure pump (diaphragm or piston)",
                "Accumulator tank",
                "Pressure switch",
                "Solenoid valves",
                "Mist nozzles (brass or stainless)",
            ],
            "pros": [
                "Fastest root growth possible",
                "Highest DO exposure",
                "Lowest water usage",
                "Best nutrient uptake efficiency",
            ],
            "cons": [
                "Expensive",
                "Complex maintenance",
                "Nozzle clog sensitivity",
                "Zero failure tolerance (roots dry in minutes)",
            ],
            "best_for": "Experienced growers, commercial operations, cloning/propagation",
        },
        "low_pressure_aeroponics": {
            "pressure_psi": {"min": 2, "max": 40, "target": 20},
            "droplet_size_microns": {"min": 50, "max": 200},
            "description": "Uses standard pump with spray nozzles. Larger droplets — technically 'fogponics' or spray culture.",
            "equipment": [
                "Standard submersible or inline pump",
                "Spray/mist heads",
                "Cycle timer (seconds precision)",
                "Manifold",
            ],
            "pros": ["Much cheaper", "Simpler setup", "Standard parts", "More forgiving on timing"],
            "cons": [
                "Less efficient nutrient delivery",
                "Roots stay wetter (closer to NFT)",
                "Larger droplets = less oxygen",
            ],
            "best_for": "Hobbyists, first-time aero growers, budget builds",
        },
    },
    "mist_cycle_timing": {
        "by_stage": {
            "seedling": {
                "on_seconds": 5,
                "off_seconds": 300,
                "cycles_per_hour": 12,
                "notes": "Very light misting. Roots just emerging. Too much = stem rot.",
            },
            "early_veg": {
                "on_seconds": 5,
                "off_seconds": 180,
                "cycles_per_hour": 20,
                "notes": "Increasing frequency as root mass develops.",
            },
            "late_veg": {
                "on_seconds": 5,
                "off_seconds": 120,
                "cycles_per_hour": 30,
                "notes": "Aggressive root growth demands more frequent misting.",
            },
            "transition": {
                "on_seconds": 5,
                "off_seconds": 90,
                "cycles_per_hour": 40,
                "notes": "Peak demand approaching.",
            },
            "early_flower": {
                "on_seconds": 5,
                "off_seconds": 60,
                "cycles_per_hour": 60,
                "notes": "Peak mist demand. Roots are massive.",
            },
            "mid_flower": {
                "on_seconds": 5,
                "off_seconds": 60,
                "cycles_per_hour": 60,
                "notes": "Maintain peak. Heavy feeders now.",
            },
            "late_flower": {
                "on_seconds": 3,
                "off_seconds": 90,
                "cycles_per_hour": 40,
                "notes": "Slightly reduce as plant matures.",
            },
            "flush": {
                "on_seconds": 5,
                "off_seconds": 60,
                "cycles_per_hour": 60,
                "notes": "Maximum misting with plain water to flush salts.",
            },
        },
        "day_vs_night": {
            "daytime": "Use standard cycle timing above.",
            "nighttime": "Reduce frequency by 30-50%. Example: 5s on / 180s off at night vs 5s on / 120s off during day.",
            "reasoning": "Transpiration drops at night. Roots need less water. Over-misting at night = root rot risk.",
        },
        "optimization_signs": {
            "too_much_mist": [
                "Roots look waterlogged/saturated",
                "Algae forming on roots",
                "Stem rot at base",
                "Slow growth despite good roots",
            ],
            "too_little_mist": [
                "Root tips drying/browning",
                "Wilting between cycles",
                "Roots reaching for nozzles",
                "Nutrient burn (concentrated spray)",
            ],
            "perfect": [
                "White, fluffy root mass",
                "Roots hang freely with fine branching",
                "Rapid growth",
                "No wet/dry stress signs",
            ],
        },
    },
    "nozzle_management": {
        "types": {
            "brass_mist": {
                "psi": "60-120",
                "flow_gph": "0.5-2.0",
                "clog_resistance": "low",
                "cost": "low",
                "notes": "Standard for HPA. Replace frequently.",
            },
            "stainless_steel": {
                "psi": "80-120",
                "flow_gph": "0.5-2.0",
                "clog_resistance": "medium",
                "cost": "high",
                "notes": "More durable. Less mineral buildup.",
            },
            "anti_drip": {
                "psi": "40-100",
                "flow_gph": "1.0-3.0",
                "clog_resistance": "medium",
                "cost": "medium",
                "notes": "Stops dripping between cycles. Cleaner operation.",
            },
            "ceramic_disc": {
                "psi": "20-60",
                "flow_gph": "2.0-5.0",
                "clog_resistance": "high",
                "cost": "medium",
                "notes": "LPA only. Larger droplets but very clog-resistant.",
            },
        },
        "clog_prevention": [
            "Inline filter (50-100 micron) between pump and nozzles — MANDATORY",
            "Use synthetic nutrients ONLY (no organics — they clog nozzles immediately)",
            "Reservoir filter sock over pump intake",
            "Weekly nozzle soak in pH-down solution (citric acid) or vinegar to dissolve mineral deposits",
            "Run plain water flush cycle for 5 minutes after every reservoir change",
            "Keep backup nozzles ready — swap and clean offline rather than downtime",
        ],
        "cleaning_protocol": [
            "Remove nozzles from manifold",
            "Soak in white vinegar or pH 3.0 solution for 1-2 hours",
            "Use ultrasonic cleaner if available (best method)",
            "Clear orifice with soft bristle brush or compressed air (never wire — damages orifice)",
            "Test spray pattern before reinstalling — should be even cone/fan",
            "Replace if spray pattern is uneven after cleaning",
        ],
        "inspection_schedule": "Visual check daily. Remove and soak weekly. Replace every 2-3 grows or when spray pattern degrades.",
    },
    "root_chamber_design": {
        "light_exclusion": "100% light-proof. ANY light leaks = algae on roots. Use black containers with white/reflective exterior.",
        "temperature": {
            "target_f": 68,
            "max_f": 72,
            "notes": "Chamber temp tends to be cooler than ambient due to mist evaporation (evaporative cooling effect).",
        },
        "drain_design": "Sloped floor (1-2% grade) toward drain port. No standing water — roots must hang freely in air.",
        "material": "Food-safe plastic (HDPE). No metal (corrosion). Smooth interior (easy to clean, no biofilm anchors).",
        "sizing": "Minimum 12 inches vertical space below net pots for root development. 18-24 inches preferred for large plants.",
        "humidity_inside": "95-100% during mist cycles. Drops between cycles (this is the oxygen exposure window).",
    },
    "failure_modes": [
        {
            "failure": "Nozzle clog (single nozzle)",
            "severity": "high",
            "time_to_damage": "15-30 minutes (roots dry rapidly without mist)",
            "detection": [
                "One plant wilting while others fine",
                "Dry roots at one position",
                "Flow meter shows reduced output",
            ],
            "immediate_response": [
                "Swap nozzle with backup immediately",
                "Manually mist affected roots with spray bottle while fixing",
            ],
            "prevention": "Inline filter. Weekly soak. Keep 2x backup nozzles ready.",
        },
        {
            "failure": "Pump failure (all mist stops)",
            "severity": "critical",
            "time_to_damage": "5-15 minutes in hot/dry conditions, 30-60 min in cool/humid",
            "detection": ["No mist visible", "All plants wilting simultaneously", "Pressure gauge at zero"],
            "immediate_response": [
                "Switch to backup pump immediately",
                "If no backup: submerge roots in bucket of nutrient water (emergency DWC conversion)",
                "Mist manually with spray bottle",
            ],
            "prevention": "Backup pump wired to float switch or pressure sensor. UPS on pump circuit.",
        },
        {
            "failure": "Solenoid stuck closed (HPA)",
            "severity": "critical",
            "time_to_damage": "Same as pump failure — no mist reaching roots",
            "detection": ["Pressure builds but no mist", "Pump running normally but nozzles dry"],
            "immediate_response": [
                "Manually open solenoid (override)",
                "Swap solenoid",
                "Run continuous mist until fixed",
            ],
            "prevention": "Quality solenoids rated for cycling. Spare on hand. Test monthly.",
        },
        {
            "failure": "Power outage",
            "severity": "critical",
            "time_to_damage": "10-30 minutes depending on ambient humidity",
            "detection": ["All systems off"],
            "immediate_response": [
                "UPS kicks in (if installed)",
                "Manually mist roots every 5 min with spray bottle",
                "Cover root chamber to trap humidity (buys time)",
            ],
            "prevention": "UPS rated for pump wattage × 2 hours minimum. Generator for extended outages.",
        },
    ],
    "nutrient_approach": {
        "ec_targets": {
            "seedling": {"min": 0.2, "max": 0.5},
            "veg": {"min": 0.5, "max": 1.0},
            "flower": {"min": 0.8, "max": 1.4},
            "notes": "LOWER than all other hydro methods. Fine mist = high absorption efficiency. Less is more.",
        },
        "synthetic_only": True,
        "organic_warning": "NEVER use organic nutrients in aeroponics. Organic particles clog nozzles within hours. No exceptions.",
        "particle_filtration": "100-micron inline filter minimum. 50-micron preferred for HPA. Clean/replace filter weekly.",
        "reservoir_change_frequency": "Every 5 days in veg, every 3-4 days in flower. Aero systems have smaller reservoirs that concentrate faster.",
        "ph_range": {"min": 5.5, "max": 6.2, "target": 5.8},
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — the single export consumed by the API/frontend
# ─────────────────────────────────────────────────────────────────────────────

AERO_CONFIG: dict = {
    "grow_type_id": "aeroponics",
    "version": "1.0.0",
    "stages": AERO_STAGES,
    "equipment": AERO_EQUIPMENT,
    "quick_reference": AERO_QUICK_REFERENCE,
    "troubleshooting": AERO_TROUBLESHOOTING,
    "mist_engineering": AERO_MIST_ENGINEERING,
    "total_grow_days": {"min": 84, "max": 168, "typical": 117},
}
