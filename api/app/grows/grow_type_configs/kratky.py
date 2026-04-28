"""Kratky (Passive Hydro) — Complete grow type configuration.

Enterprise-grade, production-ready configuration covering every aspect of
Kratky passive hydroponics from germination through harvest, drying, and curing.

Supports three environment types (matching Tent.environment_type):
  - indoor  (default — full environmental control, artificial light)
  - outdoor (no climate control, natural photoperiod, weather exposure)
  - greenhouse (partial climate control, natural + supplemental light)

Base stage values target indoor/tent growing.  Each stage carries an
``environment_variants`` dict with ``outdoor`` and ``greenhouse`` keys
that contain **overrides** and **additional** tasks, problems, equipment,
and notes.  The frontend merges base + variant at render time.

KEY DIFFERENCES FROM DWC:
  - NO air pump, NO air stone — completely passive, zero electricity
  - Oxygen comes from an AIR GAP that forms as the water level drops
  - "Set and forget" — ideally one initial nutrient mix lasts the whole grow
  - NEVER refill above the air gap line — air roots will drown
  - Modified Kratky for cannabis: top-off IS needed (plants drink 1-3 gal/day)
  - Top-off rule: add water/nutes to halfway between current level and air root line
  - pH drift is a bigger challenge — no aeration to stabilize
  - Higher initial EC since nutrients deplete over time without changes
  - Container MUST be opaque and sealed — stagnant water + light = algae disaster
  - Simpler nutrient approach: MaxiGro/MaxiBloom powder or GH Flora Trio
  - Larger reservoir preferred (10+ gal) to minimize top-off frequency

Data sources:
  - B.A. Kratky, University of Hawaii (original research papers)
  - Cannabis Kratky community best practices (Reddit, Grasscity, 420Magazine)
  - General Hydroponics feeding charts adapted for passive systems
  - Root zone oxygen management in non-circulating systems
"""
from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STAGES — ordered list of every phase in a Kratky grow
# ─────────────────────────────────────────────────────────────────────────────

KRATKY_STAGES: list[dict] = [
    # ── 1. GERMINATION ────────────────────────────────────────────────────
    {
        "id": "germination",
        "name": "Germination",
        "order": 1,
        "duration_days": {"min": 2, "max": 7, "typical": 3},
        "description": "Seed cracks open and taproot emerges. Use Rapid Rooters, paper towel method, or direct-in-cube. Keep warm, moist, and dark. Identical to DWC — the Kratky difference starts at seedling stage.",
        "environment": {
            "temp_day_f": {"min": 75, "max": 82, "target": 78},
            "temp_night_f": {"min": 70, "max": 78, "target": 74},
            "humidity_pct": {"min": 70, "max": 90, "target": 80},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Keep seeds in darkness. A heat mat at 78°F speeds germination. No direct light until sprout emerges.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.0, "max": 0.0, "target": 0.0},
            "ppm_500": {"min": 0, "max": 0, "target": 0},
            "water_temp_f": {"min": 65, "max": 75, "target": 70},
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 0,
            "notes": "No reservoir needed yet. If pre-filling container, use plain pH'd water only. No air stone needed — this is Kratky.",
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
            {"name": "Soak seeds", "description": "Place seeds in cup of room-temperature water for 12-24 hours until they sink. Transfer to Rapid Rooter or paper towel.", "interval_days": None, "priority": "high"},
            {"name": "Check for taproot", "description": "After 24-72 hours, look for white taproot emerging from seed shell. Transfer to net pot once taproot is 0.5-1 inch.", "interval_days": 1, "priority": "high"},
            {"name": "Prepare Kratky container", "description": "Fill opaque container with plain pH'd water (5.8). Set water level to just touch the bottom of the net pot. NO air stone — leave the lid sealed tight.", "interval_days": None, "priority": "medium"},
        ],
        "health_checks": [
            "Has the seed cracked open?",
            "Is the taproot visible and white?",
            "Is the Rapid Rooter moist but not soaking wet?",
            "Temperature at 75-80°F?",
        ],
        "common_problems": [
            {"issue": "Seed not germinating", "cause": "Too cold, too dry, or bad seed", "solution": "Ensure 75-80°F. Keep medium moist. Try a different seed after 7 days."},
            {"issue": "Damping off", "cause": "Too wet, no air circulation", "solution": "Reduce moisture. Ensure Rapid Rooter is moist not soaked."},
        ],
        "training": [],
        "transition_signals": ["Taproot is 0.5-1 inch long", "Seed shell has cracked and cotyledons are emerging"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Germinate indoors or in a sheltered area even for outdoor grows. Seeds need consistent warmth that outdoor temps rarely provide. Start indoors, transplant to outdoor Kratky once seedling has 2-3 true leaf sets.",
                },
                "extra_tasks": [
                    {"name": "Plan outdoor timing", "description": "Outdoor Kratky must start after last frost. Photoperiod plants flower when daylight drops below ~14 hours. In northern hemisphere, start seeds indoors in April-May for outdoor transplant in May-June.", "interval_days": None, "priority": "high"},
                ],
                "extra_problems": [],
                "notes": "Always germinate indoors regardless of final grow location.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Germinate inside the greenhouse on a heat mat. Greenhouses provide enough shelter for germination. Ensure overnight temps stay above 65°F — use a seedling heat mat if nights are cool.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse germination works well with a heat mat and humidity dome.",
            },
        },
    },

    # ── 2. SEEDLING ───────────────────────────────────────────────────────
    {
        "id": "seedling",
        "name": "Seedling",
        "order": 2,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "First true leaves develop. Roots grow down from net pot into the nutrient solution. The initial air gap begins to form as the seedling drinks. This is where Kratky diverges from DWC — there is no air stone, so the forming air gap is the ONLY oxygen source for roots.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 68, "max": 75, "target": 72},
            "humidity_pct": {"min": 65, "max": 80, "target": 70},
            "vpd_kpa": {"min": 0.4, "max": 0.8, "target": 0.6},
            "light_hours": 18,
            "light_ppfd": {"min": 100, "max": 300, "target": 200},
            "light_dli": {"min": 6, "max": 19, "target": 13},
            "notes": "Keep light at 24-30 inches above canopy. Seedlings are fragile — too much light causes bleaching.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.0, "target": 5.8},
            "ec": {"min": 0.2, "max": 0.6, "target": 0.4},
            "ppm_500": {"min": 100, "max": 300, "target": 200},
            "water_temp_f": {"min": 65, "max": 75, "target": 70},
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 2,
            "notes": "Water level should START touching the bottom of the net pot. As the seedling drinks, the water drops and an air gap forms. Do NOT refill to the top — this air gap is critical. Add Hydroguard at initial fill to prevent stagnant water issues.",
        },
        "nutrients": {
            "strength_pct": 25,
            "approach": "Very light nutrients in initial fill. Kratky philosophy: set the initial mix right and don't touch it. For cannabis seedlings, 1/4 strength is safe.",
            "flora_micro_ml_per_gal": 0.6,
            "flora_gro_ml_per_gal": 0.6,
            "flora_bloom_ml_per_gal": 0.3,
            "calmag_ml_per_gal": 0.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Beneficial bacteria — critical in stagnant Kratky water. Prevents root rot without aeration."},
            ],
        },
        "tasks": [
            {"name": "Check water level", "description": "Verify water is touching net pot bottom. Seedling roots are short and need direct contact. Once roots are 2+ inches into water, the air gap can begin forming.", "interval_days": 2, "priority": "high"},
            {"name": "Mark initial water line", "description": "Use a marker to draw a line on the outside of the container at the current water level. This is your 'never refill above' line. As water drops, mark the air root zone.", "interval_days": None, "priority": "high"},
            {"name": "Check for root growth", "description": "Briefly lift the lid to check if roots are growing down through the net pot into the water. You should see white roots within 5-7 days.", "interval_days": 3, "priority": "high"},
            {"name": "Monitor pH", "description": "pH tends to drift UP in Kratky (no aeration stabilizing it). Check every 2-3 days. Adjust with pH Down if above 6.2.", "interval_days": 2, "priority": "high"},
            {"name": "Ensure container is sealed and dark", "description": "Check for light leaks around the lid and net pot. Stagnant water + light = algae explosion. Cover any gaps with tape or neoprene collar.", "interval_days": None, "priority": "high"},
        ],
        "health_checks": [
            "Are roots growing down into the water?",
            "Is the water level dropping (air gap forming)?",
            "Any algae visible on the water surface?",
            "Do roots smell clean (no foul odor)?",
            "Are cotyledons still green? First true leaves appearing?",
        ],
        "common_problems": [
            {"issue": "Roots not reaching water", "cause": "Water level too low or Rapid Rooter dried out", "solution": "Raise water level to just touch the bottom of the net pot. Use a wick (strip of felt or cotton) from the net pot down to the water to bridge the gap."},
            {"issue": "Algae forming on water surface", "cause": "Light leaking into container through gaps", "solution": "Seal ALL light leaks. Cover net pot gap with neoprene collar or hydroton. Use opaque/black container. Algae competes with roots for oxygen in stagnant water — more dangerous in Kratky than DWC."},
            {"issue": "Foul smell from container", "cause": "Anaerobic bacteria in stagnant water", "solution": "Drain, clean, refill with fresh pH'd nutrient solution + Hydroguard. Ensure container is sealed properly. This is the biggest Kratky risk — no aeration means anaerobic bacteria can establish quickly."},
            {"issue": "pH rising rapidly", "cause": "Normal Kratky behavior — no aeration to stabilize pH", "solution": "Adjust with small amounts of pH Down. In Kratky, pH naturally drifts up. Check every 2-3 days. Don't over-correct."},
        ],
        "training": [],
        "transition_signals": ["2-3 sets of true leaves", "Roots visible 2+ inches below net pot", "Air gap beginning to form (water level has dropped 1+ inch)", "Seedling drinking noticeably"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Keep seedlings indoors or in sheltered area. They're too fragile for direct outdoor sun. Begin hardening off at the end of this stage — 1-2 hours of morning sun, increasing daily over a week.",
                },
                "extra_tasks": [
                    {"name": "Begin hardening off (end of stage)", "description": "Start exposing seedling to outdoor conditions gradually. Day 1-2: 1 hour morning sun. Day 3-4: 2-3 hours. Day 5-7: 4-6 hours. Bring inside at night.", "interval_days": 1, "priority": "medium"},
                    {"name": "Insulate container for outdoor use", "description": "Wrap Kratky container in Reflectix or white material. Outdoor sun heats containers much faster with no circulation to dissipate heat.", "interval_days": None, "priority": "high"},
                ],
                "extra_problems": [
                    {"issue": "Container overheating in sun", "cause": "Stagnant Kratky water heats up faster than aerated DWC water", "solution": "Insulate container. Keep in shade while plant gets partial sun. Bury lower half in ground. Kratky without aeration is more sensitive to heat — above 75°F water promotes bacteria."},
                ],
                "notes": "Outdoor Kratky seedlings need extra protection. No aeration means water quality degrades faster in heat.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse provides good seedling conditions. Ensure container stays cool — greenhouses can overheat. Place container on ground (thermal mass) rather than on a bench in direct sun.",
                },
                "extra_tasks": [
                    {"name": "Shade the container", "description": "Place the container where it gets shade even though the plant gets light. Kratky containers must stay cool — no circulation to manage heat.", "interval_days": None, "priority": "medium"},
                ],
                "extra_problems": [],
                "notes": "Keep Kratky container shaded in the greenhouse. Plant gets light, container stays cool.",
            },
        },
    },

    # ── 3. EARLY VEGETATIVE ───────────────────────────────────────────────
    {
        "id": "early_veg",
        "name": "Early Vegetative",
        "order": 3,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Rapid leaf and root growth. The air gap is actively forming as the plant drinks. You should see two distinct root zones developing: submerged 'water roots' (white, slimy-smooth) and exposed 'air roots' (fuzzy, branching laterally in the humid air gap). Both are healthy and essential. This dual root system is the core of Kratky.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 55, "max": 70, "target": 60},
            "vpd_kpa": {"min": 0.8, "max": 1.2, "target": 1.0},
            "light_hours": 18,
            "light_ppfd": {"min": 300, "max": 600, "target": 450},
            "light_dli": {"min": 19, "max": 39, "target": 29},
            "notes": "Increase light intensity as plant grows. Can bring light closer (18-24 inches). Watch for light stress — if leaf edges curl up, raise light.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 0.6, "max": 1.2, "target": 0.8},
            "ppm_500": {"min": 300, "max": 600, "target": 400},
            "water_temp_f": {"min": 62, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 2,
            "notes": "Air gap should be 2-4 inches and growing. The fuzzy air roots in this gap are oxygen roots — they MUST stay in humid air, NOT submerged. If you top off, NEVER go above the lowest air roots. Add Hydroguard to any top-off water.",
        },
        "nutrients": {
            "strength_pct": 50,
            "approach": "Half-strength veg nutrients. In true Kratky you don't touch the reservoir. For cannabis (a heavy feeder), use 'modified Kratky' — top off when water gets low but never above air roots. Mix top-off water at half strength.",
            "flora_micro_ml_per_gal": 2.5,
            "flora_gro_ml_per_gal": 2.5,
            "flora_bloom_ml_per_gal": 1.0,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Essential in stagnant Kratky water. Add at initial fill AND every top-off."},
                {"name": "Silica (Armor Si)", "dose_ml_per_gal": 1.0, "purpose": "Strengthens cell walls. Add first, before other nutrients. Especially useful in Kratky where roots have less oxygen support."},
            ],
        },
        "tasks": [
            {"name": "Check water level & air gap", "description": "Verify the air gap is growing. Mark the current water line. You should see fuzzy air roots above the water and white water roots below. Both are healthy.", "interval_days": 2, "priority": "high"},
            {"name": "Monitor pH", "description": "pH drifts up in Kratky. Check every 2-3 days. Adjust gently with pH Down. Large swings are worse than slightly high pH. Range 5.5-6.5 is acceptable.", "interval_days": 2, "priority": "high"},
            {"name": "First top-off (if needed)", "description": "If water level has dropped more than 50% of original volume, top off to halfway between current level and the lowest air roots. Use half-strength nutrients + Hydroguard. Mark the new 'never fill above' line.", "interval_days": None, "priority": "medium"},
            {"name": "Inspect roots", "description": "Briefly lift lid. Healthy Kratky roots: white/cream water roots below waterline, fuzzy lateral air roots above. Bad signs: brown slime, foul smell, mushy roots.", "interval_days": 4, "priority": "high"},
            {"name": "Begin LST training", "description": "Low Stress Training is ideal for Kratky. Bend and tie branches to spread the canopy. More even light = better yields without pushing the root system harder.", "interval_days": 3, "priority": "medium"},
        ],
        "health_checks": [
            "Can you see both air roots (fuzzy, above water) and water roots (smooth, below)?",
            "Is the air gap growing as the plant drinks?",
            "Any foul smell when you open the lid?",
            "Is pH staying in the 5.5-6.5 range?",
            "Are leaves a healthy green with no yellowing?",
        ],
        "common_problems": [
            {"issue": "No air roots forming", "cause": "Water level hasn't dropped enough or container isn't sealed (humidity escaping)", "solution": "Ensure lid is sealed tightly. The air gap must be humid (near 100% RH inside the container). If water hasn't dropped, the plant may be too small — give it time."},
            {"issue": "Air roots dying/drying out", "cause": "Container lid not sealed — humid air escaping", "solution": "Seal the container better. Air roots need humid air (near 100% RH). If the container breathes, the air gap dries out and air roots die. Use tape or gasket material around the lid."},
            {"issue": "Root rot in stagnant water", "cause": "Water too warm, no Hydroguard, organic debris", "solution": "Keep water below 72°F. Add Hydroguard at 2 ml/gal. Remove any dead plant material from water. In severe cases, do a full water change (this breaks pure Kratky philosophy but saves the plant)."},
            {"issue": "pH climbing above 6.5", "cause": "Normal Kratky pH drift — nutrient uptake creates alkaline byproducts", "solution": "Add pH Down carefully. Phosphoric acid-based pH Down also adds phosphorus. Don't chase pH — a slow drift from 5.8 to 6.5 over a week is acceptable. Only correct if above 6.5."},
        ],
        "training": [
            {"method": "LST (Low Stress Training)", "description": "Bend main stem and tie to container edge or use plant clips. Opens canopy for even light. Start when plant has 4-5 nodes. Ideal for Kratky — doesn't stress the root system.", "when": "4-5 nodes, when stem is still flexible"},
            {"method": "Topping", "description": "Cut the main stem above the 4th or 5th node. Creates two main colas. Let plant recover for 5-7 days before additional training. Topping is fine in Kratky — the root system handles it.", "when": "5-6 nodes, healthy growth"},
        ],
        "transition_signals": ["Plant has 5-6+ nodes", "Air gap is 3-5+ inches", "Distinct air root and water root zones visible", "Plant is 8-12 inches tall"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "light_hours": "Natural daylight (14-18+ hours in summer)",
                    "notes": "Full sun drives fast growth. Kratky containers outdoors are MORE vulnerable to heat than DWC — no aeration cooling. Double-insulate: Reflectix wrap + paint container white. Consider burying lower half in ground for thermal mass.",
                },
                "reservoir_overrides": {
                    "water_temp_f": {"min": 58, "max": 72, "target": 66},
                    "notes": "Outdoor Kratky water temp is the #1 concern. Without aeration, warm stagnant water goes anaerobic FAST. Keep below 72°F at all costs. Insulate, shade, or bury the container.",
                },
                "extra_tasks": [
                    {"name": "Insulate & shade container", "description": "Wrap in Reflectix. Keep container in shade while plant gets sun. Bury lower half in ground. Kratky has zero tolerance for overheated water — no bubbles to add oxygen.", "interval_days": None, "priority": "critical"},
                    {"name": "Pest scouting", "description": "Check for aphids, spider mites, caterpillars, slugs. Outdoor grows face constant pest pressure. Inspect both sides of leaves.", "interval_days": 2, "priority": "high"},
                    {"name": "Rain protection for container", "description": "Cover the gap around the stem and net pot. Rain diluting the reservoir is worse in Kratky — you can't just 'change the res' without disrupting the air gap.", "interval_days": None, "priority": "high"},
                ],
                "extra_problems": [
                    {"issue": "Stagnant water going anaerobic in heat", "cause": "No aeration + warm temps = bacteria bloom", "solution": "If water smells bad, do an emergency change. Refill to the air root line (NOT to top). Add extra Hydroguard (3 ml/gal). Insulate better. If chronic, consider adding a small solar-powered air pump (breaks pure Kratky but saves the plant)."},
                    {"issue": "Wind toppling container", "cause": "As water level drops, container gets top-heavy", "solution": "Place rocks or weights at the base. Use a wider, lower-profile container (storage tote vs tall bucket). Anchor to the ground."},
                ],
                "notes": "Outdoor Kratky is higher risk than outdoor DWC due to no aeration. Temperature management is absolutely critical.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse Kratky works well — protected from rain and wind. Main concern is heat buildup heating the stagnant water. Place container on ground (thermal mass), not on a bench in sun.",
                },
                "reservoir_overrides": {
                    "notes": "Greenhouse warmth heats Kratky water fast. Floor placement + insulation is critical. Consider a shade cloth over the container area (not the plant).",
                },
                "extra_tasks": [
                    {"name": "Manage greenhouse ventilation", "description": "Open vents when temp exceeds 80°F. Kratky water has no aeration buffer — the whole system depends on stable temps.", "interval_days": 1, "priority": "high"},
                    {"name": "Check for greenhouse pests", "description": "Greenhouses attract whiteflies, fungus gnats, and spider mites. Use sticky traps. Fungus gnats are especially attracted to stagnant Kratky water surfaces.", "interval_days": 3, "priority": "medium"},
                ],
                "extra_problems": [
                    {"issue": "Fungus gnats in Kratky container", "cause": "Stagnant water surface attracts egg-laying gnats", "solution": "Seal container lid completely — no gaps. Add a layer of hydroton on top of net pot. Use yellow sticky traps. Mosquito dunks (BTI) in the water are safe and effective."},
                ],
                "notes": "Greenhouse Kratky is a solid choice — weather protection with good natural light. Seal the container tight to prevent pests.",
            },
        },
    },

    # ── 4. LATE VEGETATIVE ────────────────────────────────────────────────
    {
        "id": "late_veg",
        "name": "Late Vegetative",
        "order": 4,
        "duration_days": {"min": 14, "max": 42, "typical": 21},
        "description": "Full vegetative growth. Plant is drinking heavily — in Kratky, this means the water level drops fast and top-offs become routine. The air gap is well-established (4-8+ inches). You should see a thick mass of fuzzy air roots in the gap and a healthy mat of water roots below. This is 'modified Kratky' territory for cannabis — pure set-and-forget won't sustain a plant this thirsty.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 65, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 18,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 26, "max": 45, "target": 39},
            "notes": "Maximum veg light intensity. LED at 16-20 inches. Plants should be vigorously growing with 5-6+ nodes.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 0.8, "max": 1.4, "target": 1.0},
            "ppm_500": {"min": 400, "max": 700, "target": 500},
            "water_temp_f": {"min": 62, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 2,
            "notes": "Water consumption increases dramatically. Top-off when water level drops to 25-30% of container capacity. ALWAYS top off BELOW the air root zone. Mix top-off at 75% strength. Add Hydroguard to every top-off. The air gap should be maintained — never reduce it.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Three-quarter strength veg nutrients for top-offs. Cannabis in late veg drinks 0.5-1.5 gal/day depending on size. In a 5-gal bucket, you may top off every 2-3 days. In a 10-gal, every 4-5 days. Larger container = less maintenance = true Kratky spirit.",
            "flora_micro_ml_per_gal": 3.75,
            "flora_gro_ml_per_gal": 3.75,
            "flora_bloom_ml_per_gal": 1.25,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Every top-off. Non-negotiable in Kratky."},
                {"name": "Silica (Armor Si)", "dose_ml_per_gal": 1.5, "purpose": "Strengthens stems for heavy flower. Add first before other nutrients."},
            ],
        },
        "tasks": [
            {"name": "Top off reservoir", "description": "When water drops to 25-30% of container, add nutrient solution to halfway between current level and lowest air roots. Never submerge air roots. Add Hydroguard.", "interval_days": 3, "priority": "high"},
            {"name": "Check pH at top-off", "description": "Check pH of existing water before and after adding top-off. Adjust entire volume if needed. pH Down is your friend in Kratky.", "interval_days": 3, "priority": "high"},
            {"name": "Inspect roots", "description": "Healthy air roots: fuzzy, white/cream, branching laterally. Healthy water roots: white/cream, may be slightly stained from nutrients. Bad: brown mush, foul smell, slimy.", "interval_days": 5, "priority": "medium"},
            {"name": "Continue LST / training", "description": "Keep bending and tying new growth. In Kratky, an even canopy is even more important — you need maximum efficiency from a root system with less oxygen than DWC.", "interval_days": 3, "priority": "medium"},
            {"name": "Consider container upgrade", "description": "If using a 5-gal bucket and topping off daily, switch to a 10-gal tote. Larger reservoir = more stable pH/EC, less frequent top-offs, and more Kratky-like behavior.", "interval_days": None, "priority": "low"},
            {"name": "Plan for flower transition", "description": "Stop topping/training 1-2 weeks before planned flip. Let plant recover before the stretch.", "interval_days": None, "priority": "medium"},
        ],
        "health_checks": [
            "How quickly is water level dropping? (Indicates plant health and size)",
            "Is the air gap maintained at 4-8+ inches?",
            "Are air roots still fuzzy and healthy?",
            "Any bad smell from the container?",
            "Is pH drifting excessively (more than 0.5 in 2 days)?",
            "Are leaves showing any deficiency signs?",
        ],
        "common_problems": [
            {"issue": "Water level dropping too fast (daily top-off)", "cause": "Container too small for the plant size", "solution": "Upgrade to a larger container (10-15 gal). Transplant carefully — keep the air root zone intact. Match the water level to the existing air gap line. Larger container = more stable system."},
            {"issue": "EC rising in reservoir", "cause": "Plant drinking water faster than nutrients — evaporation concentrating salts", "solution": "Top off with PLAIN pH'd water (no nutrients) when EC is rising. Only add nutrients when EC is dropping. This is the same rule as DWC."},
            {"issue": "EC dropping in reservoir", "cause": "Plant consuming nutrients faster than water", "solution": "Top off with full-strength nutrient solution. The plant is hungry. This usually means healthy, vigorous growth."},
            {"issue": "Air roots turning brown/dying", "cause": "Container not sealed — humid air escaping, or water level rose above air roots during top-off", "solution": "Check seal on container lid. NEVER top off above the air root zone. If you accidentally submerged air roots, drain water back down immediately. Air roots that were submerged may die but new ones will form."},
            {"issue": "Thick biofilm on water surface", "cause": "Stagnant water + warm temps + organic matter", "solution": "Carefully remove biofilm with a paper towel. Add extra Hydroguard. If severe, do a full reservoir change — fill to the existing air gap line, not to top. Add Hydroguard immediately."},
        ],
        "training": [
            {"method": "LST (Low Stress Training)", "description": "Continue bending and tying. Kratky plants benefit more from LST than DWC — the root system has less oxygen support, so keeping an efficient canopy matters more.", "when": "Ongoing throughout veg"},
            {"method": "SCROG (Screen of Green)", "description": "Install trellis net 8-12 inches above container. Tuck branches under net as they grow through. Excellent for Kratky — maximizes yield per plant.", "when": "2-3 weeks before flip"},
            {"method": "Defoliation (light)", "description": "Remove lower leaves and small branches that won't reach the canopy. Redirect energy to top growth. Don't overdo it — the plant needs leaves to drink and drive the Kratky cycle.", "when": "1 week before flip"},
        ],
        "transition_signals": ["Plant is 1/3-1/2 of desired final height", "Canopy is full and even", "Ready to flip light schedule to 12/12", "Root system is well-established with healthy air and water roots"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor Kratky plants veg until natural daylight drops below ~14 hours. The plant can get very large — plan accordingly with container size. A 10-gal minimum is recommended for outdoor Kratky cannabis. Autoflowers bypass photoperiod concerns.",
                },
                "reservoir_overrides": {
                    "notes": "Large outdoor plants may drink 1-3+ gal/day in peak summer. Use the largest container possible. Top off at least daily in heat. EC and pH management is harder outdoors — check at every top-off.",
                },
                "extra_tasks": [
                    {"name": "Top off daily (or twice daily in heat)", "description": "Large outdoor Kratky plants drink fast. Check morning and evening. Never let the water level reach zero — the water roots will die. Maintain at least 2 inches of water at all times.", "interval_days": 0.5, "priority": "critical"},
                    {"name": "Structural support", "description": "Outdoor Kratky plants grow tall. Install a tomato cage, bamboo stakes, or trellis. The container gets lighter as water drops — brace it.", "interval_days": None, "priority": "high"},
                    {"name": "IPM spray (preventive)", "description": "Apply neem oil or insecticidal soap every 7-10 days during veg. Stop all sprays 2+ weeks before flower.", "interval_days": 7, "priority": "medium"},
                ],
                "extra_problems": [
                    {"issue": "Container runs dry", "cause": "Hot day, large plant, missed top-off", "solution": "Refill immediately to the air gap line. If water roots dried for less than a few hours, the plant will recover. If the air gap dried out too, mist the air roots to rehydrate. Prevention: use the largest container possible."},
                    {"issue": "Animal damage", "cause": "Deer, rabbits, or rodents", "solution": "Fence or chicken wire around the plant. Container is portable — move to sheltered area if needed."},
                ],
                "notes": "Outdoor Kratky in late veg needs daily attention. The passive system's simplicity breaks down when the plant is a heavy drinker in summer heat.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse Kratky can use light deprivation tarps to control flowering time. Without light dep, plants follow natural photoperiod. Keep container on ground for thermal mass. Ventilate to prevent overheating.",
                },
                "extra_tasks": [
                    {"name": "Consider light deprivation", "description": "Install blackout tarps if you want to control flowering time. 12 hours of uninterrupted darkness required. Must be done consistently every day.", "interval_days": None, "priority": "medium"},
                    {"name": "Manage greenhouse heat", "description": "Shade cloth, exhaust fans, open vents. Kratky water temps must stay below 72°F — monitor closely in summer.", "interval_days": 1, "priority": "high"},
                ],
                "extra_problems": [
                    {"issue": "Inconsistent light dep schedule", "cause": "Missing coverage interrupts the dark period", "solution": "Automate with motorized tarps. One missed day can revert to veg or cause hermaphroditism."},
                ],
                "notes": "Greenhouse Kratky is excellent for veg — protected from weather with good natural light. Light dep gives indoor-like control.",
            },
        },
    },

    # ── 5. TRANSITION (Pre-Flower / Stretch) ─────────────────────────────
    {
        "id": "transition",
        "name": "Transition (Stretch)",
        "order": 5,
        "duration_days": {"min": 7, "max": 21, "typical": 14},
        "description": "Light flipped to 12/12. Plant stretches 50-200% in height. Water consumption spikes during the stretch — this is the most demanding phase for Kratky maintenance. The plant may drink 1-2+ gallons/day. Top-off discipline is critical: keep the air gap sacred, never submerge air roots, and switch nutrient mix toward bloom ratios.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 82, "target": 78},
            "temp_night_f": {"min": 65, "max": 75, "target": 70},
            "humidity_pct": {"min": 50, "max": 60, "target": 55},
            "vpd_kpa": {"min": 1.0, "max": 1.4, "target": 1.2},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 600},
            "light_dli": {"min": 17, "max": 30, "target": 26},
            "notes": "Flip to 12/12. Light intensity stays high. The 12 hours of uninterrupted darkness must be ABSOLUTE — light leaks cause hermaphroditism. This is even more critical in Kratky since you may need to open the container for top-offs during the dark period — use a green headlamp only.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 6.0},
            "ec": {"min": 0.8, "max": 1.4, "target": 1.0},
            "ppm_500": {"min": 400, "max": 700, "target": 500},
            "water_temp_f": {"min": 62, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 2,
            "notes": "Begin transitioning nutrient mix from veg to bloom ratios. Water consumption peaks during stretch — top off more frequently. Consider doing a full reservoir swap to bloom nutrients: drain to air gap line, refill with bloom-ratio mix. This is the one time a full change is recommended in Kratky.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Transition mix: reduce Gro, increase Bloom. Some growers do a full reservoir swap here — drain existing veg solution (keeping the air gap intact), refill with bloom-ratio nutrients to the air gap line. This gives the plant a clean start for flower.",
            "flora_micro_ml_per_gal": 2.5,
            "flora_gro_ml_per_gal": 1.25,
            "flora_bloom_ml_per_gal": 3.75,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Every top-off and reservoir swap. Non-negotiable."},
                {"name": "Silica (Armor Si)", "dose_ml_per_gal": 1.5, "purpose": "Last week to add silica — stop before mid-flower."},
            ],
        },
        "tasks": [
            {"name": "Flip light schedule to 12/12", "description": "Set timer to 12 hours on / 12 hours off. Ensure complete darkness during off period — check for indicator lights, light leaks, and timer reliability.", "interval_days": None, "priority": "critical"},
            {"name": "Consider full reservoir swap", "description": "Drain existing veg solution down to just above the water roots (keeping air gap intact). Refill to the air root line with bloom-ratio nutrients + Hydroguard. This gives a clean nutritional start for flower.", "interval_days": None, "priority": "high"},
            {"name": "Top off frequently (stretch demand)", "description": "Plant may drink 1-2+ gal/day during stretch. Check water level daily. Top off with bloom-ratio nutrients below the air root zone. Add Hydroguard to every top-off.", "interval_days": 1, "priority": "high"},
            {"name": "Support stretching branches", "description": "The stretch can double plant height. Use plant ties, bamboo stakes, or trellis net. Branches that aren't supported will bend or break under future bud weight.", "interval_days": 2, "priority": "medium"},
            {"name": "Lollipop bottom growth", "description": "Remove small lower branches and leaves that won't get light. This redirects energy to top colas. In Kratky, efficiency matters — the root system has less oxygen support than DWC.", "interval_days": None, "priority": "medium"},
        ],
        "health_checks": [
            "Is the plant stretching? (Should be gaining 1-2 inches/day at peak)",
            "Are pistils (white hairs) appearing at nodes?",
            "Is water level dropping fast? (Normal — stretch = peak water demand)",
            "Are air roots still healthy and undisturbed?",
            "Any signs of stress from the light flip?",
        ],
        "common_problems": [
            {"issue": "Water runs out overnight", "cause": "Heavy stretch drinking + undersized container", "solution": "Top off to the air root line before lights out. If this keeps happening, upgrade to a larger container. Emergency: refill to air root line immediately. Roots that dry out completely will die."},
            {"issue": "Hermaphrodite signs (bananas/nanners)", "cause": "Light leak during dark period, or stress from dried-out roots", "solution": "Check for ANY light leaks. If you must open the container during dark period for top-off, use a green headlamp only. If hermie is confirmed, remove pollen sacs immediately."},
            {"issue": "Nutrient burn (brown leaf tips)", "cause": "Concentrated nutrients from evaporation or too-strong mix", "solution": "Top off with plain pH'd water (no nutrients) until EC drops. Kratky concentrates nutrients as water evaporates — monitor EC at every top-off."},
        ],
        "training": [
            {"method": "Final SCROG tucking", "description": "Tuck branches under the trellis net as they stretch through. Keep canopy even. Stop tucking once buds start forming (usually end of week 2 of 12/12).", "when": "First 2 weeks of 12/12"},
            {"method": "Supercropping (advanced)", "description": "Gently crush and bend tall branches to even the canopy without cutting. Creates a knuckle that strengthens the branch. Use carefully — Kratky plants may recover slower than DWC due to less oxygen.", "when": "During stretch for branches outgrowing the canopy"},
        ],
        "transition_signals": ["Stretch has slowed/stopped", "White pistils clearly visible at most nodes", "Bud sites forming at branch tips"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "light_hours": "Decreasing natural daylight (~12-14 hours, triggering flower)",
                    "notes": "Outdoor transition happens naturally as days shorten in late summer. Kratky container maintenance intensifies — the plant drinks the most during stretch. Check for light pollution from street lights or porch lights that could interrupt the dark period.",
                },
                "extra_tasks": [
                    {"name": "Eliminate light pollution", "description": "Ensure no artificial light reaches the plant during dark hours. Move container if needed — Kratky containers are portable.", "interval_days": None, "priority": "critical"},
                    {"name": "Final pest prevention", "description": "Last chance for preventive sprays. Apply BT (Bacillus thuringiensis) for caterpillars. After buds form, no more spraying.", "interval_days": None, "priority": "high"},
                    {"name": "Reinforce supports", "description": "Stretch + future bud weight requires strong support. Add stakes, cage, or trellis.", "interval_days": None, "priority": "high"},
                    {"name": "Top off twice daily", "description": "Outdoor stretch in summer heat = peak water demand. Check morning and evening. Never let water level reach zero.", "interval_days": 0.5, "priority": "critical"},
                ],
                "extra_problems": [
                    {"issue": "Light pollution preventing flower", "cause": "Street lights or porch lights nearby", "solution": "Move the container to a darker location. Kratky portability is an advantage here."},
                    {"issue": "Container runs dry in heat", "cause": "Stretch + high temps + no aeration cooling", "solution": "Top off immediately. Use a larger container (15+ gal). Add frozen water bottles to cool the refill water."},
                ],
                "notes": "Outdoor Kratky transition is the most maintenance-intensive period. Top-off discipline is critical. Consider the switch to a larger container before this stage.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "If using light dep, cover greenhouse with blackout tarp at the same time every evening. 12 hours of total darkness required. If following natural light, transition happens same as outdoor but with better weather protection.",
                },
                "extra_tasks": [
                    {"name": "Light dep schedule (if using)", "description": "Cover greenhouse at the same time every evening. 12 hours of TOTAL darkness. Even small light leaks through tarp edges matter.", "interval_days": 1, "priority": "critical"},
                ],
                "extra_problems": [
                    {"issue": "Heat buildup under light dep tarp", "cause": "Covering greenhouse traps heat", "solution": "Cover in evening when temps drop. Ensure some passive ventilation under the tarp. Kratky water temps spike in trapped heat."},
                ],
                "notes": "Greenhouse with light dep gives indoor-like control. Kratky water temp management under tarps is the main challenge.",
            },
        },
    },

    # ── 6. EARLY FLOWER ───────────────────────────────────────────────────
    {
        "id": "early_flower",
        "name": "Early Flower",
        "order": 6,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Buds are forming and stacking. Trichome production begins. Water consumption remains high but stabilizes after the stretch. In Kratky, this is when nutrient management matters most — the plant needs heavy P and K for bud production, and the stagnant reservoir concentrates salts over time. Monitor EC closely at every top-off.",
        "environment": {
            "temp_day_f": {"min": 72, "max": 80, "target": 77},
            "temp_night_f": {"min": 64, "max": 72, "target": 68},
            "humidity_pct": {"min": 45, "max": 55, "target": 50},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 900, "target": 750},
            "light_dli": {"min": 26, "max": 39, "target": 32},
            "notes": "Maximum light intensity during flower. Lower humidity to prevent bud rot. The 4-6°F day/night temperature difference helps terpene and trichome production.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.3, "target": 6.0},
            "ec": {"min": 1.0, "max": 1.6, "target": 1.2},
            "ppm_500": {"min": 500, "max": 800, "target": 600},
            "water_temp_f": {"min": 62, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 2,
            "notes": "Bloom-ratio nutrients. Check EC at every top-off: if EC is rising, top off with plain pH'd water. If EC is dropping, top off with full-strength bloom nutrients. The air gap should be well-established and stable (6-10+ inches). Maintain it.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full-strength bloom nutrients. The plant is focused entirely on bud production now. Heavy phosphorus (P) and potassium (K) drive bud size and density. Reduce nitrogen. In Kratky, nutrients concentrate as water evaporates — watch EC carefully.",
            "flora_micro_ml_per_gal": 2.5,
            "flora_gro_ml_per_gal": 0.6,
            "flora_bloom_ml_per_gal": 5.0,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Every top-off. Stagnant flower-stage water is nutrient-rich and warm — prime rot conditions."},
                {"name": "Liquid Koolbloom (optional)", "dose_ml_per_gal": 1.25, "purpose": "PK booster for early flower. Increases bud density. Use for first 3-4 weeks of flower only."},
            ],
        },
        "tasks": [
            {"name": "Top off with bloom nutrients", "description": "Check water level every 1-2 days. Top off below air roots with bloom-ratio nutrients. Check EC first — if rising, use plain water. If dropping, use nutrients.", "interval_days": 2, "priority": "high"},
            {"name": "Monitor EC carefully", "description": "Kratky concentrates nutrients as water evaporates. EC above 1.8 = too concentrated. Dilute by topping off with plain pH'd water. EC below 0.8 = plant is hungry, top off with full-strength nutrients.", "interval_days": 2, "priority": "high"},
            {"name": "Defoliation (targeted)", "description": "Remove fan leaves that are blocking light to bud sites. Don't remove more than 20% of leaves at once. Kratky plants recover from defoliation slower than DWC — be conservative.", "interval_days": None, "priority": "medium"},
            {"name": "Inspect for bud rot", "description": "Check dense bud sites for any gray/brown rot. Bud rot in Kratky grows can be worse because the grower is already fighting humidity from the stagnant reservoir. Good airflow is critical.", "interval_days": 2, "priority": "high"},
            {"name": "Support heavy buds", "description": "Use plant yoyos, string, or bamboo to support branches as buds gain weight. Kratky containers lose weight as water drops — anchor the container too.", "interval_days": None, "priority": "medium"},
        ],
        "health_checks": [
            "Are buds visibly growing and forming?",
            "Trichome development starting (frosty appearance)?",
            "Any yellowing or burnt tips? (Adjust EC accordingly)",
            "Is airflow adequate around buds?",
            "Container sealed? Any algae or smell?",
        ],
        "common_problems": [
            {"issue": "Nutrient concentration (EC climbing)", "cause": "Water evaporating faster than plant drinks — concentrating salts in stagnant reservoir", "solution": "Top off with plain pH'd water only until EC drops to target range. In Kratky, evaporation concentration is more severe than DWC because there's no water movement."},
            {"issue": "Bud rot starting", "cause": "Humidity too high, poor airflow, dense buds", "solution": "Remove affected bud + 1 inch of healthy tissue. Increase airflow with fans. Lower humidity below 50%. In Kratky, the sealed container adds ambient humidity to the grow space — ensure good room ventilation."},
            {"issue": "Root zone smell during flower", "cause": "Nutrient-rich stagnant water + warm temps", "solution": "Add extra Hydroguard (3 ml/gal for one top-off). If smell is severe, do a partial water swap: drain to just above water roots, refill with fresh bloom nutrients to the air gap line. Add Hydroguard immediately."},
        ],
        "training": [],
        "transition_signals": ["Buds filling in and starting to stack", "Trichomes covering buds and sugar leaves", "Pistils starting to change from white to orange"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "humidity_pct": {"min": 30, "max": 80, "target": 50},
                    "notes": "Humidity is uncontrollable outdoors. In humid climates, space plants apart, defoliate for airflow, and inspect for bud rot after every rain. Kratky containers add localized humidity — keep container sealed tight so moisture doesn't escape upward into the buds.",
                },
                "extra_tasks": [
                    {"name": "Post-rain bud inspection", "description": "After rain, shake water off buds. Inspect for gray mold within 24-48 hours. Kratky moisture + rain = double humidity risk.", "interval_days": None, "priority": "critical"},
                    {"name": "Caterpillar patrol (BT spray)", "description": "Budworms bore into buds and cause rot from inside. Inspect for frass (dark droppings). Apply BT if found — safe up to harvest.", "interval_days": 3, "priority": "critical"},
                    {"name": "Shake off morning dew", "description": "Gently shake plant each morning to remove dew from buds.", "interval_days": 1, "priority": "medium"},
                ],
                "extra_problems": [
                    {"issue": "Bud rot after rain", "cause": "Water trapped in dense buds + stagnant Kratky humidity", "solution": "Cut affected area + 1 inch. Improve airflow. Consider harvesting early if persistent rain is forecast."},
                    {"issue": "Caterpillar damage", "cause": "Moths lay eggs on buds", "solution": "Apply BT (Bacillus thuringiensis). Check buds for frass. Remove affected buds by hand."},
                    {"issue": "Early frost threat", "cause": "Fall temperatures dropping", "solution": "Cover with frost cloth at night. Move Kratky container to shelter — portability is a key advantage."},
                ],
                "notes": "Outdoor early flower faces weather pressure. Kratky's portability is an advantage — you can move the container to shelter.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse provides rain protection — huge advantage during flower. Control humidity by ventilating during the day. Kratky containers in greenhouses need extra attention — the enclosed space + stagnant water = high humidity environment. Run fans.",
                },
                "extra_tasks": [
                    {"name": "Humidity management", "description": "Open vents during day. Run HAF fans constantly. Use dehumidifier if RH consistently above 55% during flower. Kratky sealed containers contribute moisture.", "interval_days": 1, "priority": "high"},
                ],
                "extra_problems": [
                    {"issue": "Condensation on glazing dripping on buds", "cause": "Temperature differential + Kratky humidity contribution", "solution": "Increase air circulation. Open vents briefly in morning. Consider anti-drip greenhouse film."},
                ],
                "notes": "Greenhouse flower is excellent. Monitor humidity closely — Kratky containers release some moisture into the enclosed space.",
            },
        },
    },

    # ── 7. MID/PEAK FLOWER (Bulk Phase) ──────────────────────────────────
    {
        "id": "mid_flower",
        "name": "Mid/Peak Flower",
        "order": 7,
        "duration_days": {"min": 14, "max": 21, "typical": 21},
        "description": "Buds are bulking and packing on weight. Trichome production is at maximum. This is where Kratky simplicity pays off — the root system is mature, the air gap is stable, and the plant has settled into a steady drinking pattern. Top-offs become routine and predictable. The biggest risk is nutrient concentration from evaporation.",
        "environment": {
            "temp_day_f": {"min": 70, "max": 80, "target": 76},
            "temp_night_f": {"min": 62, "max": 72, "target": 66},
            "humidity_pct": {"min": 40, "max": 50, "target": 45},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 600, "max": 1000, "target": 800},
            "light_dli": {"min": 26, "max": 43, "target": 35},
            "notes": "Peak light intensity. The 8-12°F day/night temp swing enhances terpene production and can bring out purple/red colors. Keep humidity below 50% — bud density creates moisture traps.",
        },
        "reservoir": {
            "ph": {"min": 5.8, "max": 6.3, "target": 6.0},
            "ec": {"min": 1.2, "max": 1.8, "target": 1.4},
            "ppm_500": {"min": 600, "max": 900, "target": 700},
            "water_temp_f": {"min": 62, "max": 72, "target": 68},
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 2,
            "notes": "Peak bloom nutrients. The plant has a predictable drinking pattern now. Top off on the same schedule. EC management is crucial — Kratky concentrates nutrients with no water movement to dilute. If EC creeps above 1.8, dilute with plain water.",
        },
        "nutrients": {
            "strength_pct": 100,
            "approach": "Full-strength bloom. Heavy P and K for bud density. This is the feeding peak — the plant is eating and drinking at maximum capacity. Watch for the natural fade to begin near the end of this stage (lower fan leaves yellowing).",
            "flora_micro_ml_per_gal": 2.5,
            "flora_gro_ml_per_gal": 0.6,
            "flora_bloom_ml_per_gal": 5.0,
            "calmag_ml_per_gal": 1.5,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Every top-off. Bloom-stage water is nutrient-rich and perfect for bacteria — Hydroguard keeps the good ones dominant."},
                {"name": "Liquid Koolbloom (optional)", "dose_ml_per_gal": 1.25, "purpose": "PK booster through mid-flower. Stop 2 weeks before harvest."},
            ],
        },
        "tasks": [
            {"name": "Routine top-off", "description": "By now you know the drinking pattern. Top off on schedule. Check EC first: rising = plain water, dropping = nutrients. Add Hydroguard every time.", "interval_days": 2, "priority": "high"},
            {"name": "Check trichomes weekly", "description": "Use jeweler's loupe or digital microscope. Clear = not ready. Milky/cloudy = peak THC. Amber = more CBN (couch-lock). Most growers harvest at mostly milky with 10-20% amber.", "interval_days": 7, "priority": "medium"},
            {"name": "Remove yellowing fan leaves", "description": "Lower fan leaves naturally yellow as the plant redirects nutrients to buds. Remove them to improve airflow and prevent rot. This is normal.", "interval_days": 3, "priority": "low"},
            {"name": "Monitor for pests", "description": "Flower stage attracts thrips and spider mites. In Kratky, fungus gnats are attracted to the container's moisture. Check undersides of leaves and bud sites.", "interval_days": 3, "priority": "medium"},
        ],
        "health_checks": [
            "Are buds still growing and packing on weight?",
            "Trichomes milky or still clear? (Check with loupe)",
            "Any signs of bud rot or mold in dense colas?",
            "Is the natural fade beginning (lower leaves yellowing)?",
            "EC in the reservoir stable or climbing?",
        ],
        "common_problems": [
            {"issue": "Foxtailing (buds growing wispy towers)", "cause": "Light too close / too intense, or heat stress", "solution": "Raise light 2-4 inches. Check leaf surface temperature. In Kratky, root stress from warm stagnant water can compound heat stress from above — fix both."},
            {"issue": "Salt buildup in reservoir", "cause": "Weeks of top-offs concentrating mineral salts in stagnant water", "solution": "If EC is chronically high (above 2.0), do a partial water swap: drain to just above water roots, refill to air gap line with half-strength bloom nutrients + Hydroguard. This resets salt levels."},
            {"issue": "Slow bud development", "cause": "Insufficient light, low P/K, or root issues", "solution": "Check light intensity (target 800+ PPFD). Ensure bloom nutrients are heavy on P and K. Inspect roots — if brown and smelly, root health is compromising nutrient uptake. Add Hydroguard and consider a water swap."},
        ],
        "training": [],
        "transition_signals": ["Most pistils turning orange/brown", "Buds feeling dense and heavy", "Trichomes transitioning from clear to milky", "Leaf yellowing beginning (natural fade)"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Mid-flower outdoors is typically September-October. Cooler nights enhance terpenes but watch for fall rain and humidity. Kratky portability lets you move the container under cover during rain events — use it.",
                },
                "extra_tasks": [
                    {"name": "Weather monitoring (critical)", "description": "Check 10-day forecast daily. If prolonged rain is coming and buds are close to ready, consider early harvest. Move Kratky container under cover for rain events.", "interval_days": 1, "priority": "critical"},
                    {"name": "Rain cover / move container", "description": "When rain is forecast, move the Kratky container under an overhang, carport, or tarp. The plant can handle a day of lower light — it can't handle bud rot.", "interval_days": None, "priority": "high"},
                    {"name": "Caterpillar patrol continues", "description": "Caterpillars are still active. Check daily — their damage causes bud rot from inside.", "interval_days": 1, "priority": "high"},
                ],
                "extra_problems": [
                    {"issue": "Multi-day rain during peak flower", "cause": "Fall weather patterns", "solution": "Move container to covered area. Kratky's biggest advantage is portability. A slightly early harvest beats a moldy crop."},
                    {"issue": "Cool nights below 50°F", "cause": "Fall approaching", "solution": "Move container indoors at night. Cool enhances colors but below 40°F risks damage. Kratky portability is the key advantage here."},
                ],
                "notes": "Outdoor mid-flower benefits from Kratky portability. Move the container to protect from weather — something you can't do with in-ground grows.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse mid-flower is ideal. Rain protection with natural light. Fall temp drops are moderated. May need supplemental heating if overnight temps drop below 55°F consistently.",
                },
                "extra_tasks": [
                    {"name": "Consider supplemental heating", "description": "If overnight greenhouse temps drop below 55°F, use a small space heater. Kratky water will also cool down — check water temp.", "interval_days": 1, "priority": "medium"},
                ],
                "extra_problems": [],
                "notes": "Greenhouse mid-flower is straightforward. The structure does the work.",
            },
        },
    },

    # ── 8. LATE FLOWER / RIPENING ─────────────────────────────────────────
    {
        "id": "late_flower",
        "name": "Late Flower / Ripening",
        "order": 8,
        "duration_days": {"min": 14, "max": 21, "typical": 14},
        "description": "Buds are ripening and finishing. Trichomes maturing from clear → milky → amber. The plant's water consumption slows as it finishes. In Kratky, this is a calm phase — the air gap is stable, top-offs are less frequent, and the plant is winding down. Begin planning the flush.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 78, "target": 74},
            "temp_night_f": {"min": 58, "max": 68, "target": 62},
            "humidity_pct": {"min": 35, "max": 50, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.8, "target": 1.5},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 800, "target": 650},
            "light_dli": {"min": 17, "max": 35, "target": 28},
            "notes": "Can reduce light intensity slightly as plant finishes. Wider day/night temp swing (10-15°F) enhances terpene development and brings out colors. Keep humidity low — dense buds trap moisture.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 0.8, "max": 1.2, "target": 1.0},
            "ppm_500": {"min": 400, "max": 600, "target": 500},
            "water_temp_f": {"min": 62, "max": 70, "target": 66},
            "dissolved_oxygen_ppm": None,
            "change_interval_days": None,
            "hydroguard_ml_per_gal": 2,
            "notes": "Reduce nutrient strength. The plant is finishing and doesn't need heavy feeding. Water consumption slows. Top-offs become less frequent. Begin planning the flush — you'll need to swap to plain water soon.",
        },
        "nutrients": {
            "strength_pct": 75,
            "approach": "Reduce to 3/4 strength bloom. Stop all supplements except Hydroguard. The plant is finishing and excess nutrients will remain in the buds (harsh smoke). Begin the fade — the plant should start yellowing fan leaves naturally.",
            "flora_micro_ml_per_gal": 2.0,
            "flora_gro_ml_per_gal": 0.0,
            "flora_bloom_ml_per_gal": 3.75,
            "calmag_ml_per_gal": 1.0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Continue until flush. Root protection doesn't stop."},
            ],
        },
        "tasks": [
            {"name": "Check trichomes (daily now)", "description": "Trichome maturity determines harvest timing. Watch for milky → amber transition. Your target amber percentage is personal preference: 10% amber = energetic high, 30% = more sedative.", "interval_days": 1, "priority": "critical"},
            {"name": "Reduced top-offs", "description": "Plant drinks less as it finishes. Top off less frequently but still maintain water above the root zone. Never let roots dry completely.", "interval_days": 3, "priority": "medium"},
            {"name": "Remove dead/dying fan leaves", "description": "The natural fade accelerates. Yellow and dead fan leaves can fall into the reservoir — remove them. In Kratky, organic debris in stagnant water is especially problematic.", "interval_days": 2, "priority": "medium"},
            {"name": "Plan flush timing", "description": "Most growers flush 7-14 days before harvest. In Kratky, flush = drain to above water roots, refill to air gap line with plain pH'd water. Mark your calendar.", "interval_days": None, "priority": "high"},
        ],
        "health_checks": [
            "Trichome ratio: what percentage is milky vs amber?",
            "Is the natural fade progressing (fan leaves yellowing)?",
            "Any bud rot in dense colas?",
            "Reservoir smell okay?",
            "Are buds feeling dense and sticky?",
        ],
        "common_problems": [
            {"issue": "Buds not finishing (still throwing white pistils)", "cause": "Strain is slow, light leaks, or environmental stress", "solution": "Check for light leaks. Some strains take 10-12 weeks. If light leak is causing re-vegging, fix immediately. Patience."},
            {"issue": "Excessive leaf yellowing too early", "cause": "Nutrient deficiency or too much flushing too soon", "solution": "If trichomes aren't ready yet, don't start flushing. Maintain light feeding. The fade should be gradual, not sudden."},
            {"issue": "Nutrient taste concern", "cause": "Salts accumulated in stagnant Kratky water over weeks", "solution": "A proper flush (7-14 days of plain water) resolves this. Kratky actually makes flushing easy — just swap the water and let the plant finish."},
        ],
        "training": [],
        "transition_signals": ["10-30% amber trichomes (personal preference)", "Most pistils are orange/brown", "Fan leaves significantly faded", "Buds feel dense and sticky"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Late flower outdoors is October-November in many regions. First frost is the hard deadline. Kratky's portability is your biggest asset — you can bring the container inside overnight or during weather events. The natural temperature swings of fall produce exceptional terpene profiles.",
                },
                "extra_tasks": [
                    {"name": "Frost watch", "description": "Monitor forecasts for first frost. Move Kratky container inside overnight if temps below 45°F. A hard freeze kills the plant and ruins buds.", "interval_days": 1, "priority": "critical"},
                    {"name": "Daily bud rot check", "description": "Cool, damp fall mornings are prime bud rot conditions. Check every dense cola daily.", "interval_days": 1, "priority": "critical"},
                    {"name": "Move container inside at night", "description": "If nighttime temps drop below 45°F, bring the Kratky container inside a garage or shed overnight. This is the #1 advantage of Kratky over DWC — true portability.", "interval_days": 1, "priority": "high"},
                ],
                "extra_problems": [
                    {"issue": "First frost before trichomes are ready", "cause": "Growing season too short", "solution": "Harvest immediately before frost. Next season, choose faster-finishing strains or start earlier. Autoflowers avoid this problem entirely."},
                    {"issue": "Persistent damp/fog", "cause": "Fall weather patterns", "solution": "Move container to drier area. Increase airflow. Consider early harvest of lower buds while tops finish."},
                ],
                "notes": "Late flower outdoors is a race against frost. Kratky portability lets you move the plant to safety — use this advantage aggressively.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse provides frost protection. The structure buys you 2-4 extra weeks vs fully outdoor. Use supplemental heating on cold nights to maintain above 55°F.",
                },
                "extra_tasks": [
                    {"name": "Supplemental heating", "description": "Thermostat-controlled heater set to 55°F minimum overnight. Kratky water also cools — check water temp.", "interval_days": 1, "priority": "high"},
                    {"name": "End-of-season humidity watch", "description": "Fall greenhouse humidity rises. Run dehumidifier or ventilate during warmest part of day.", "interval_days": 1, "priority": "high"},
                ],
                "extra_problems": [
                    {"issue": "Greenhouse condensation on buds", "cause": "Warm inside, cool outside = condensation", "solution": "Ventilate briefly each morning. Use HAF fans. Anti-drip greenhouse film helps."},
                ],
                "notes": "Greenhouse extends the season significantly. Supplemental heating is the key investment.",
            },
        },
    },

    # ── 9. FLUSH ────────────────────────────────────────────────────────
    {
        "id": "flush",
        "name": "Flush",
        "order": 9,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Remove all nutrients and let the plant use up stored reserves. In Kratky, this is straightforward: drain the nutrient solution down to just above the water roots, refill to the air gap line with plain pH'd water. The plant will consume stored nutrients from its tissues over the next 7-14 days, resulting in cleaner, smoother smoke.",
        "environment": {
            "temp_day_f": {"min": 68, "max": 78, "target": 74},
            "temp_night_f": {"min": 58, "max": 68, "target": 62},
            "humidity_pct": {"min": 35, "max": 45, "target": 40},
            "vpd_kpa": {"min": 1.2, "max": 1.6, "target": 1.4},
            "light_hours": 12,
            "light_ppfd": {"min": 400, "max": 700, "target": 550},
            "light_dli": {"min": 17, "max": 30, "target": 24},
            "notes": "Reduce light intensity slightly. Plant is finishing — no need to push growth anymore.",
        },
        "reservoir": {
            "ph": {"min": 5.5, "max": 6.2, "target": 5.8},
            "ec": {"min": 0.0, "max": 0.2, "target": 0.0},
            "ppm_500": {"min": 0, "max": 100, "target": 0},
            "water_temp_f": {"min": 62, "max": 70, "target": 66},
            "dissolved_oxygen_ppm": None,
            "change_interval_days": 5,
            "hydroguard_ml_per_gal": 2,
            "notes": "Drain existing nutrient solution to just above water roots. Refill to the air gap line with plain pH'd water + Hydroguard. Repeat every 5 days for a thorough flush. The plant will yellow and fade — this is expected and desired.",
        },
        "nutrients": {
            "strength_pct": 0,
            "approach": "No nutrients. Plain pH'd water only. Some growers add FloraKleen to help dissolve residual salts in the stagnant reservoir. The Kratky flush is actually very effective — the still water allows salts to settle and the plant can clean itself out efficiently.",
            "flora_micro_ml_per_gal": 0,
            "flora_gro_ml_per_gal": 0,
            "flora_bloom_ml_per_gal": 0,
            "calmag_ml_per_gal": 0,
            "supplements": [
                {"name": "Hydroguard", "dose_ml_per_gal": 2, "purpose": "Root protection even during flush. Stagnant water still needs beneficial bacteria."},
                {"name": "FloraKleen (optional)", "dose_ml_per_gal": 2.5, "purpose": "Flushing agent that dissolves residual mineral salts. Especially useful in Kratky where salts accumulate over the grow."},
            ],
        },
        "tasks": [
            {"name": "Drain and refill with plain water", "description": "Carefully drain nutrient solution to just above water roots (don't disturb air roots). Refill to the air gap line with plain pH'd water (5.8) + Hydroguard. Mark the water line.", "interval_days": 5, "priority": "high"},
            {"name": "Monitor trichomes (daily)", "description": "Continue daily trichome checks. Harvest when ratio is where you want it. Don't extend flush past 14 days — diminishing returns.", "interval_days": 1, "priority": "critical"},
            {"name": "Prepare harvest equipment", "description": "Clean trimming scissors, set up drying area, prepare drying rack/lines. Ensure drying space can maintain 60°F / 60% RH in darkness.", "interval_days": None, "priority": "medium"},
            {"name": "48-hour darkness (optional)", "description": "Some growers give 48 hours of total darkness before harvest. Believed to increase trichome production. Not scientifically proven but widely practiced.", "interval_days": None, "priority": "low"},
        ],
        "health_checks": [
            "Are fan leaves yellowing and fading? (Good — plant is using stored nutrients)",
            "Are buds still developing or have they stopped growing?",
            "Trichomes at desired milky/amber ratio?",
            "Any last-minute bud rot?",
        ],
        "common_problems": [
            {"issue": "Plant looks sick/dying during flush", "cause": "Normal — plant is cannibalizing fan leaves for remaining nutrients", "solution": "No action needed. This is expected and desired. The yellowing and fading IS the flush working."},
            {"issue": "Foul smell from reservoir during flush", "cause": "Stagnant plain water + decomposing root material", "solution": "Do more frequent water changes (every 3 days instead of 5). Add extra Hydroguard. Remove any fallen leaves from the water."},
        ],
        "training": [],
        "transition_signals": ["Trichomes at desired harvest ratio", "Fan leaves mostly yellowed", "Plant has used up stored nutrients"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Outdoor flush is simple — drain nutrients, refill with plain water. If frost or heavy rain is imminent, skip the flush and harvest immediately. A clean harvest beats a moldy one. Kratky portability means you can move the container to shelter for the flush period.",
                },
                "extra_tasks": [
                    {"name": "Weather-contingent harvest plan", "description": "If a hard frost, multi-day rain, or storm is forecast within 3-5 days, harvest now regardless of flush status. Move container inside for the flush if weather is marginal.", "interval_days": 1, "priority": "critical"},
                ],
                "extra_problems": [
                    {"issue": "Weather forces early harvest during flush", "cause": "Incoming frost/rain", "solution": "Harvest immediately. A shorter flush won't noticeably affect quality — but mold will ruin everything."},
                ],
                "notes": "Outdoor flush may be shortened or skipped based on weather. Move the Kratky container inside to finish flushing if needed.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Greenhouse flush proceeds like indoor — weather protected. Maintain ventilation to prevent humidity buildup.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse provides stable conditions for a full flush.",
            },
        },
    },

    # ── 10. HARVEST ───────────────────────────────────────────────────────
    {
        "id": "harvest",
        "name": "Harvest",
        "order": 10,
        "duration_days": {"min": 1, "max": 2, "typical": 1},
        "description": "Cut plant, remove from container, trim, and hang to dry. Kratky harvest is simpler than DWC — no air pump to disconnect, no air stone to clean. Just pull the net pot from the container, drain, and clean.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 58, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Harvest in darkness or minimal light. Some growers harvest at end of dark period for highest trichome content.",
        },
        "reservoir": None,
        "nutrients": None,
        "tasks": [
            {"name": "Cut plant at base", "description": "Cut main stem at base. If wet trimming, trim fan leaves and sugar leaves immediately. If dry trimming, leave sugar leaves on for slower, higher-quality dry.", "interval_days": None, "priority": "critical"},
            {"name": "Remove from Kratky container", "description": "Pull net pot from container. No air stone or pump to disconnect — just lift and drain. The root mass (both air roots and water roots) will be impressive.", "interval_days": None, "priority": "high"},
            {"name": "Clean container for next grow", "description": "Drain all water. Scrub container and lid with hydrogen peroxide or dilute bleach solution. Rinse thoroughly. Kratky containers accumulate more mineral deposits than DWC — soak in vinegar solution to dissolve.", "interval_days": None, "priority": "medium"},
            {"name": "Wet trim or whole-plant hang", "description": "Wet trim: remove all fan leaves, most sugar leaves, hang individual branches. Dry trim: hang whole plant or large branches. Dry trim = slower dry = better quality.", "interval_days": None, "priority": "high"},
            {"name": "Record harvest details", "description": "Note: date, wet weight, days in flower, strain, trichome ratio, container size, total top-offs performed, any issues. This data improves future Kratky grows.", "interval_days": None, "priority": "medium"},
        ],
        "health_checks": [],
        "common_problems": [
            {"issue": "Cutting too much during trim", "cause": "Over-trimming removes trichome-covered sugar leaves", "solution": "For personal use, leave some sugar leaves. For appearance, trim tight but save trim for edibles/hash."},
            {"issue": "Root mass stuck in container", "cause": "Roots grew through net pot and anchored to container walls", "solution": "Gently work the root mass free. Kratky air roots can grip container walls. If stuck, cut roots near the wall — you're done growing anyway."},
        ],
        "training": [],
        "transition_signals": ["Plant is cut, trimmed, and hanging"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Harvest outdoors then bring everything INSIDE for drying and curing. Never dry outdoors. Bud washing is highly recommended for outdoor Kratky harvests.",
                },
                "extra_tasks": [
                    {"name": "Harvest at dawn", "description": "Outdoor plants are best harvested at first light, before the sun warms terpenes. Cooler temps preserve trichome quality.", "interval_days": None, "priority": "medium"},
                    {"name": "Clean container for storage", "description": "Scrub, sanitize, and store container for next season. Kratky containers need thorough cleaning — stagnant water leaves more mineral deposits.", "interval_days": None, "priority": "low"},
                ],
                "extra_problems": [
                    {"issue": "Pests in harvested buds", "cause": "Outdoor buds may contain insects or eggs", "solution": "Bud washing: dip branches in 3 buckets — H2O2 solution, lemon juice + baking soda water, plain water rinse. Shake off excess and hang."},
                ],
                "notes": "Bud washing is especially recommended for outdoor Kratky harvests. Removes pests, dust, and any spray residue.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Harvest inside the greenhouse, then move to a dedicated drying space. Don't dry in the greenhouse — too variable.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse harvest is straightforward. Move to indoor drying space.",
            },
        },
    },

    # ── 11. DRYING ────────────────────────────────────────────────────────
    {
        "id": "drying",
        "name": "Drying",
        "order": 11,
        "duration_days": {"min": 7, "max": 14, "typical": 10},
        "description": "Hang trimmed buds in a dark room at 60°F and 60% humidity. The slow dry preserves terpenes and chlorophyll breaks down properly. Identical process regardless of grow method — drying is drying.",
        "environment": {
            "temp_day_f": {"min": 58, "max": 65, "target": 60},
            "temp_night_f": {"min": 55, "max": 62, "target": 58},
            "humidity_pct": {"min": 55, "max": 65, "target": 60},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "60°F / 60% RH — the 60/60 rule. Total darkness. Gentle air circulation (not directly on buds). A 10-14 day dry is ideal. Faster = hay smell. Slower = better flavor.",
        },
        "reservoir": None,
        "nutrients": None,
        "tasks": [
            {"name": "Hang buds to dry", "description": "Hang branches on drying lines or use a drying rack. Space buds so air circulates between them. Darkness is essential — light degrades THC.", "interval_days": None, "priority": "critical"},
            {"name": "Monitor temperature and humidity", "description": "60°F/60% RH target. Use humidifier if too dry, dehumidifier if too humid. Small adjustments matter. Check twice daily.", "interval_days": 0.5, "priority": "high"},
            {"name": "Check drying progress", "description": "After day 5, start checking daily. Small stems should snap (not bend). Buds should feel dry on outside but slightly spongy when squeezed. Don't over-dry.", "interval_days": 1, "priority": "high"},
            {"name": "Maintain gentle airflow", "description": "Use a small fan pointed at the wall (not at buds). Air should circulate without directly blowing on buds. No oscillating fans aimed at drying buds.", "interval_days": None, "priority": "medium"},
        ],
        "health_checks": [
            "Is room staying at 60°F/60% RH?",
            "Are buds drying evenly?",
            "Any smell of ammonia? (Too wet/fast = chlorophyll not breaking down)",
        ],
        "common_problems": [
            {"issue": "Drying too fast (crispy outside, wet inside)", "cause": "Too warm, too dry, or too much airflow", "solution": "Lower temp. Raise humidity. Remove direct fan on buds. Aim for 10-14 day dry."},
            {"issue": "Hay/grass smell", "cause": "Dried too fast — chlorophyll didn't break down", "solution": "Prevention only — can't fix after. Slow, cool, dark drying prevents this. Curing may help slightly."},
            {"issue": "Mold during drying", "cause": "Humidity too high, dense buds, poor airflow", "solution": "Remove affected buds. Lower humidity. Increase gentle air circulation."},
        ],
        "training": [],
        "transition_signals": ["Small stems snap when bent (don't bend)", "Buds feel dry on outside but slightly spongy when squeezed", "Typical drying time: 7-14 days"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Dry INDOORS in a controlled space — never outdoors. A closet, spare room, or basement with 60°F/60% RH works.",
                },
                "extra_tasks": [
                    {"name": "Bud wash before hanging (recommended)", "description": "Dip harvested branches in 3 buckets: 1) H2O2 solution, 2) lemon + baking soda water, 3) plain rinse. Shake off excess and hang. Removes outdoor contaminants.", "interval_days": None, "priority": "high"},
                ],
                "extra_problems": [
                    {"issue": "Drying space too warm (fall HVAC)", "cause": "Home heating system drying the air", "solution": "Use a room away from heating vents. Add a humidifier. Monitor closely."},
                ],
                "notes": "Drying is the same regardless of grow method. Bud washing is the main extra step for outdoor harvests.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Do NOT dry in the greenhouse. Move to a proper indoor drying space with controlled temp and humidity.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "Greenhouse-grown buds dry the same as indoor. Use a proper drying room.",
            },
        },
    },

    # ── 12. CURING ────────────────────────────────────────────────────────
    {
        "id": "curing",
        "name": "Curing",
        "order": 12,
        "duration_days": {"min": 14, "max": 180, "typical": 30},
        "description": "Buds placed in sealed glass jars. Moisture equalizes. Chlorophyll breaks down. Terpenes mature. Flavor and smoothness dramatically improve over 2-8+ weeks. Identical process regardless of grow method.",
        "environment": {
            "temp_day_f": {"min": 60, "max": 70, "target": 65},
            "temp_night_f": {"min": 55, "max": 65, "target": 60},
            "humidity_pct": {"min": 58, "max": 65, "target": 62},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "Store jars in cool, dark place. Room temperature is fine but cooler is better for long cures. Never let jars get direct sunlight — UV degrades THC.",
        },
        "reservoir": None,
        "nutrients": None,
        "tasks": [
            {"name": "Jar buds", "description": "Place dried buds loosely in wide-mouth mason jars (fill 75% full). Don't pack tight — buds need air space. Close lids.", "interval_days": None, "priority": "critical"},
            {"name": "Burp jars (week 1-2)", "description": "Open jars for 5-15 minutes, 2-3 times per day for first 2 weeks. This releases moisture and prevents mold. If buds feel wet, leave jars open for 1 hour.", "interval_days": 0.5, "priority": "high"},
            {"name": "Burp jars (week 3-4)", "description": "Reduce burping to once per day for 5-10 minutes. Buds should feel consistently dry on outside.", "interval_days": 1, "priority": "medium"},
            {"name": "Long-term cure (week 5+)", "description": "Burp once per week. Add Boveda 62% pack for hands-off humidity control. Buds continue improving for months. Peak quality at 6-8 weeks.", "interval_days": 7, "priority": "low"},
        ],
        "health_checks": [
            "When you open a jar, do you smell terpenes (good) or ammonia (bad)?",
            "Are buds maintaining the right moisture (slightly springy, not wet)?",
            "Any white fuzz (mold) on any buds?",
            "Are buds getting smoother to smoke each week?",
        ],
        "common_problems": [
            {"issue": "Mold in jars", "cause": "Buds weren't dry enough before jarring", "solution": "Remove affected buds. Remove all buds from jar, dry for 12-24 more hours, rejar."},
            {"issue": "Ammonia smell when opening jar", "cause": "Too much moisture — anaerobic bacteria starting", "solution": "Leave jar open for several hours. May need to lay buds on drying rack for 12-24 hours."},
            {"issue": "Buds too dry in jar", "cause": "Over-dried before jarring or jar left open too long", "solution": "Add Boveda 62% humidity pack. It will slowly restore moisture."},
        ],
        "training": [],
        "transition_signals": ["2+ weeks cured — smokeable", "4+ weeks cured — good quality", "8+ weeks cured — premium quality"],
        "environment_variants": {
            "outdoor": {
                "environment_overrides": {
                    "notes": "Curing is identical regardless of grow environment. Store jars in cool, dark, indoor space. Kratky-grown flower from outdoor grows often develops unique terpene profiles from the passive root system's interaction with natural temperature swings.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "No outdoor-specific curing differences. All curing happens indoors in jars.",
            },
            "greenhouse": {
                "environment_overrides": {
                    "notes": "Curing is identical regardless of grow environment. Store jars in a cool, dark indoor space — not in the greenhouse.",
                },
                "extra_tasks": [],
                "extra_problems": [],
                "notes": "No greenhouse-specific curing differences.",
            },
        },
    },

    # ── 13. STORAGE ──────────────────────────────────────────────────────
    {
        "id": "storage",
        "name": "Long-Term Storage",
        "order": 13,
        "duration_days": {"min": 30, "max": 365, "typical": 180},
        "description": "Post-cure long-term storage. After 4-8 weeks of active curing, flower transitions to storage. Kratky's simplicity ends at harvest — storage is identical across all grow methods. Proper storage preserves potency and terpenes for 6-12+ months. THC degrades to CBN (~5%/year under ideal conditions, much faster with heat/light/oxygen).",
        "environment": {
            "temp_day_f": {"min": 55, "max": 65, "target": 60},
            "temp_night_f": {"min": 55, "max": 65, "target": 60},
            "humidity_pct": {"min": 55, "max": 62, "target": 58},
            "vpd_kpa": None,
            "light_hours": 0,
            "light_ppfd": 0,
            "light_dli": 0,
            "notes": "DARK. Cool. Stable. Zero light — UV destroys cannabinoids and terpenes. Commercial: 58-62°F, 55-60% RH, complete darkness, nitrogen atmosphere. Home: dark closet, cool room.",
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
            {"name": "Transfer to long-term containers", "description": "Home: mason jars with Boveda 58-62% packs. Commercial: nitrogen-sealed grove bags, CVault containers, or nitrogen-flushed drums for bulk. Remove oxygen — it degrades cannabinoids.", "interval_days": None, "priority": "high"},
            {"name": "Label and track batches", "description": "Strain, harvest date, storage date, weight, batch number. Commercial: full seed-to-sale tracking, FIFO rotation.", "interval_days": None, "priority": "high"},
            {"name": "Monthly quality checks", "description": "Inspect for mold, off odors. Check humidity packs. Spot-check trichomes (amber increase = degradation). Commercial: potency/terpene testing at 30/90/180 days.", "interval_days": 30, "priority": "high"},
            {"name": "Maintain environment", "description": "Monitor temp/humidity. No light leaks. Commercial: environmental monitoring with alerts.", "interval_days": 1, "priority": "high"},
            {"name": "Rotate stock (FIFO)", "description": "First in, first out. Flag batches approaching 12 months for priority sale or processing.", "interval_days": 30, "priority": "medium"},
            {"name": "Compliance testing holds", "description": "Commercial: retain testing samples per regulations. Track chain of custody.", "interval_days": None, "priority": "medium"},
        ],
        "health_checks": ["Temp 55-65°F?", "Humidity 55-62%?", "Complete darkness?", "No mold/off odors?", "Humidity packs active?", "FIFO maintained?"],
        "common_problems": [
            {"issue": "THC degrading to CBN", "cause": "Heat, light, oxygen, or time", "solution": "Ensure darkness, cool temps (60°F), minimal oxygen. ~5%/year loss is baseline under ideal conditions."},
            {"issue": "Terpene loss", "cause": "Temps above 70°F, oxygen, frequent opening", "solution": "Keep below 65°F. Nitrogen-sealed containers. Minimize opening."},
            {"issue": "Mold in storage", "cause": "Humidity above 65% or improper dry/cure", "solution": "Check humidity. Remove affected material. Ensure 58-62% RH before sealing."},
            {"issue": "Weight loss", "cause": "Normal moisture equilibration (1-3% first month)", "solution": "Boveda packs minimize loss. Sealed containers reduce ongoing loss."},
        ],
        "training": [],
        "transition_signals": ["N/A — terminal stage"],
        "environment_variants": {
            "outdoor": {"environment_overrides": {"notes": "Storage is always indoor."}, "extra_tasks": [], "extra_problems": [], "notes": "Indoor controlled environment."},
            "greenhouse": {"environment_overrides": {"notes": "Do NOT store in greenhouse — temp swings."}, "extra_tasks": [], "extra_problems": [], "notes": "Store in climate-controlled indoor space."},
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
                "12_18_months": "Significant decline. Consider processing into extracts.",
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


# ═══════════════════════════════════════════════════════════════════════════
# EQUIPMENT CHECKLIST
# ═══════════════════════════════════════════════════════════════════════════

KRATKY_EQUIPMENT = [
    # ── Essential ─────────────────────────────────────────────────────────
    {"name": "Opaque Container (5-10 gal)", "category": "essential", "description": "Must be completely light-proof to prevent algae. Black or dark-colored buckets, totes, or storage bins. 5 gal for small plants, 10+ gal for large. No transparent or translucent containers — even white can let light through."},
    {"name": "Net Pot (6 inch)", "category": "essential", "description": "Sits in lid opening. Holds the plant and growing medium above the reservoir. Must fit snugly in the container lid — no light gaps."},
    {"name": "Container Lid (with net pot hole)", "category": "essential", "description": "Must seal tightly. Cut or drill a hole for the net pot. Seal all gaps — light entering the reservoir causes algae and root damage."},
    {"name": "Hydroton / Clay Pebbles", "category": "essential", "description": "Inert growing medium in the net pot. Supports the plant and wicks moisture to young roots. Rinse thoroughly before use to remove dust."},
    {"name": "pH Pen or Test Kit", "category": "essential", "description": "Accurate pH measurement is critical. Digital pen preferred (calibrate monthly). Liquid test kits work but are less precise. Target range: 5.5-6.2."},
    {"name": "EC/TDS Meter", "category": "essential", "description": "Measures nutrient concentration. Essential for Kratky because stagnant water concentrates nutrients as it evaporates. Check EC at every top-off."},
    {"name": "pH Up & pH Down", "category": "essential", "description": "GH pH Up (potassium hydroxide) and pH Down (phosphoric acid). Kratky pH drifts up over time — you'll use pH Down more often."},
    {"name": "Nutrients (GH Flora Trio)", "category": "essential", "description": "FloraMicro, FloraGro, FloraBloom — 3-part nutrient system. Mix in order: Micro first, then Gro, then Bloom. Never mix concentrates directly together."},
    {"name": "Hydroguard", "category": "essential", "description": "Beneficial bacteria (Bacillus amyloliquefaciens). CRITICAL for Kratky — no air pump means stagnant water. Hydroguard prevents root rot. 2 ml/gal at every fill and top-off. Non-negotiable."},
    {"name": "Grow Light", "category": "essential", "description": "Full-spectrum LED recommended. Size depends on canopy area. Minimum 30 watts/sq ft actual draw for flower. Quantum boards (Samsung LM301B/H diodes) are efficient and cool-running."},
    {"name": "Light Timer", "category": "essential", "description": "Reliable timer for photoperiod control. Digital preferred over mechanical. 18/6 for veg, 12/12 for flower. Timer failure during flower causes hermaphroditism."},
    {"name": "Thermometer / Hygrometer", "category": "essential", "description": "Monitor air temp and humidity. Digital with min/max recording. Place at canopy level. Consider one with probe for reservoir water temp too."},
    {"name": "Neoprene Collar / Seal", "category": "essential", "description": "Fills the gap between the plant stem and net pot opening. Blocks light from entering the reservoir. Also prevents evaporation and mosquito access. Kratky-specific essential item."},

    # ── Recommended ───────────────────────────────────────────────────────
    {"name": "CalMag Supplement", "category": "recommended", "description": "Calcium and magnesium supplement. Needed with most LED lights and RO/soft water. 1-2 ml/gal depending on stage."},
    {"name": "Rapid Rooters", "category": "recommended", "description": "Starter plugs for germination. Place seed in Rapid Rooter, then into net pot with hydroton when taproot emerges."},
    {"name": "Water Thermometer", "category": "recommended", "description": "Separate thermometer for reservoir water. Kratky water temp creeps up because there's no air pump cooling. Keep 62-72°F."},
    {"name": "Jeweler's Loupe (60x)", "category": "recommended", "description": "For checking trichome maturity during flower. 60x minimum magnification. Digital USB microscopes work even better."},
    {"name": "Exhaust Fan + Carbon Filter", "category": "recommended", "description": "Odor control and air exchange. Essential if growing in a tent or enclosed space. Size to exchange room volume every 1-3 minutes."},
    {"name": "Circulation Fan", "category": "recommended", "description": "Air movement strengthens stems and prevents mold. Don't blow directly on plants — aim at walls for indirect circulation."},
    {"name": "Silica Supplement (Armor Si)", "category": "recommended", "description": "Strengthens cell walls and stems. Add first when mixing nutrients (before anything else). Stop during mid-to-late flower."},
    {"name": "Marker / Tape for Water Lines", "category": "recommended", "description": "Mark the initial fill line and the air gap line on the container. Kratky-specific: knowing exactly where the air gap starts is critical for proper top-offs."},
    {"name": "Syringe Set (1ml, 5ml, 10ml)", "category": "recommended", "description": "Accurate nutrient measurement. Small containers in Kratky mean small volumes — precision matters."},

    # ── Optional ──────────────────────────────────────────────────────────
    {"name": "Wick Material (for seedling stage)", "category": "optional", "description": "Cotton rope or felt strip to bridge the gap between net pot bottom and water level during seedling stage. Keeps medium moist until roots reach the water. Remove once roots touch."},
    {"name": "Frozen Water Bottles", "category": "optional", "description": "Drop into reservoir to lower water temp in hot conditions. Cheap alternative to a water chiller. Replace every 12 hours."},
    {"name": "FloraKleen", "category": "optional", "description": "Flushing agent that dissolves mineral salt buildup. Useful in Kratky where salts accumulate over the grow cycle."},
    {"name": "PK Booster (Liquid Koolbloom)", "category": "optional", "description": "Phosphorus/potassium booster for early-to-mid flower. Increases bud density. Use for 3-4 weeks then stop."},
    {"name": "Trellis Net (SCROG)", "category": "optional", "description": "Support and canopy management. Stretch over the canopy at the start of flower. Tuck branches through during the stretch."},
    {"name": "Plant Yoyos", "category": "optional", "description": "Retractable plant supports. Hook to branches and hang from above. Support heavy buds during flower."},
    {"name": "Mason Jars + Boveda Packs (62%)", "category": "optional", "description": "Wide-mouth quart mason jars for curing. Boveda 62% packs maintain perfect humidity hands-free."},
    {"name": "Backup Container + Lid", "category": "optional", "description": "If the reservoir develops issues (light leak, crack, smell), you can swap the net pot to a fresh container. Kratky makes this easy — just lift and move."},
]


# ═══════════════════════════════════════════════════════════════════════════
# QUICK REFERENCE
# ═══════════════════════════════════════════════════════════════════════════

KRATKY_QUICK_REFERENCE = {
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

    "water_temp_f": {"min": 62, "max": 72, "ideal": 68},

    "reservoir_change_schedule": "Kratky does NOT use scheduled reservoir changes. Top off only — never refill above the air gap line. Exceptions: full swap at transition to bloom nutrients, and at flush. Partial swap if EC is chronically above 2.0 or root zone smells.",

    "hydroguard_dose": "2 ml/gal at every fill and every top-off. Non-negotiable in Kratky — no air pump means no dissolved oxygen, making Hydroguard the primary defense against root rot.",

    "nutrient_mixing_order": [
        "1. Fill container with water to target level",
        "2. Add Silica (Armor Si) — stir and wait 15 min",
        "3. Add CalMag — stir",
        "4. Add FloraMicro — stir",
        "5. Add FloraGro — stir",
        "6. Add FloraBloom — stir",
        "7. Add supplements (Hydroguard, Koolbloom, etc.)",
        "8. Check and adjust pH last (target 5.8)",
    ],

    "top_off_rule": "Check EC before every top-off. EC rising = water evaporating, concentrating salts → top off with plain pH'd water. EC dropping = plant consuming nutrients → top off with nutrients at stage-appropriate strength. NEVER refill above the air root zone. Add Hydroguard to every top-off.",

    "golden_rules": [
        "1. NEVER submerge air roots. Once the air gap forms, it's sacred. Top off BELOW the air root zone only.",
        "2. Hydroguard at EVERY fill and EVERY top-off. No exceptions. Stagnant water without beneficial bacteria = root rot.",
        "3. Container must be 100% light-proof. Even small light leaks cause algae that chokes roots.",
        "4. Check EC before topping off. Rising EC = use plain water. Dropping EC = use nutrients.",
        "5. pH will drift UP in Kratky (no bubbles to stabilize). Check and adjust at every top-off.",
        "6. Start with a FULL reservoir. The initial water level sets the air gap as the plant drinks down.",
        "7. Don't panic when water level drops. The air gap forming IS Kratky working correctly.",
        "8. Keep the container sealed. Evaporation wastes water, raises EC, and lets pests in.",
        "9. Use opaque containers ONLY. No clear, no white, no translucent. Black or dark-colored.",
        "10. Kratky's biggest advantage is simplicity and portability. Don't over-complicate it.",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# TROUBLESHOOTING
# ═══════════════════════════════════════════════════════════════════════════

KRATKY_TROUBLESHOOTING = [
    {
        "category": "Root Issues",
        "problems": [
            {
                "symptom": "Brown, slimy, foul-smelling roots",
                "diagnosis": "Root rot (pythium or similar pathogen)",
                "severity": "critical",
                "causes": [
                    "No Hydroguard in stagnant water",
                    "Water temperature above 75°F",
                    "Light leak allowing algae to colonize roots",
                    "Organic debris (dead leaves) decomposing in reservoir",
                ],
                "solutions": [
                    "Add Hydroguard immediately (3 ml/gal for emergency dose)",
                    "Do a partial water swap: drain to above water roots, refill with fresh pH'd water + Hydroguard to the air gap line",
                    "Cool the water — frozen water bottles if needed",
                    "Seal all light leaks in the container",
                    "Remove any fallen leaves or debris from reservoir",
                    "If severe, trim off dead brown roots (leave healthy white ones)",
                ],
            },
            {
                "symptom": "Brown-stained but firm roots",
                "diagnosis": "Nutrient staining — NOT root rot",
                "severity": "info",
                "causes": [
                    "FloraMicro and other nutrients naturally stain roots brown",
                    "More visible in Kratky because roots sit in the same solution longer",
                ],
                "solutions": [
                    "No action needed — this is cosmetic",
                    "Healthy roots are firm and slightly fuzzy even when stained",
                    "Root rot roots are SLIMY and SMELL — stained roots are neither",
                ],
            },
            {
                "symptom": "Roots not reaching water / slow root growth",
                "diagnosis": "Seedling roots haven't bridged the gap to the water surface",
                "severity": "high",
                "causes": [
                    "Water level too far below the net pot",
                    "No wicking material to bridge the gap",
                    "Humidity too low around the root zone",
                ],
                "solutions": [
                    "Ensure water level is 1 inch below the net pot bottom during seedling stage",
                    "Use a wick (cotton rope) from the net pot to the water",
                    "Ensure the container lid is sealed to trap humidity around the root zone",
                    "Some growers hand-water the hydroton from above until roots reach the water",
                ],
            },
        ],
    },
    {
        "category": "pH Issues",
        "problems": [
            {
                "symptom": "pH constantly rising (drifts up to 7.0+)",
                "diagnosis": "Normal Kratky pH behavior, but needs management",
                "severity": "medium",
                "causes": [
                    "Plants consuming nutrients causes pH to rise — normal in all hydro but worse in Kratky because no air bubbles to stabilize pH",
                    "Low buffering capacity in the solution",
                    "Alkaline source water",
                ],
                "solutions": [
                    "Check and adjust pH at every top-off (use pH Down)",
                    "Use RO water if source water is very alkaline",
                    "Accept slight drift between top-offs — plants tolerate 5.5-6.5 range",
                    "Don't chase pH daily if you can't top off — adjust at each top-off event",
                ],
            },
            {
                "symptom": "pH crashing (drops below 5.0)",
                "diagnosis": "Uncommon in Kratky — indicates a serious issue",
                "severity": "high",
                "causes": [
                    "Root rot releasing organic acids",
                    "Contaminated source water",
                    "Over-application of pH Down",
                ],
                "solutions": [
                    "Check roots for rot (slimy = rot, firm = healthy)",
                    "If root rot: treat root issue first (see Root Issues above)",
                    "Do a full water swap with fresh, properly mixed nutrients + Hydroguard",
                    "Check source water pH before adding anything",
                ],
            },
        ],
    },
    {
        "category": "Nutrient / EC Issues",
        "problems": [
            {
                "symptom": "EC climbing above 2.0 between top-offs",
                "diagnosis": "Nutrient concentration from evaporation",
                "severity": "high",
                "causes": [
                    "Water evaporating faster than plant uptake — concentrating dissolved salts",
                    "Container not sealed properly (excess evaporation)",
                    "Hot environment accelerating evaporation",
                ],
                "solutions": [
                    "Top off with plain pH'd water (no nutrients) until EC drops to target",
                    "Seal container lid tightly to reduce evaporation",
                    "If chronic (EC above 2.0 repeatedly): do a partial water swap — drain to above water roots, refill with half-strength nutrients + Hydroguard",
                    "Move container to cooler location if possible",
                ],
            },
            {
                "symptom": "Brown crispy leaf tips (nutrient burn)",
                "diagnosis": "EC too high — salts burning leaf margins",
                "severity": "medium",
                "causes": [
                    "EC climbed due to evaporation concentration (most common in Kratky)",
                    "Nutrients mixed too strong",
                    "Insufficient top-offs with plain water",
                ],
                "solutions": [
                    "Top off with plain pH'd water to dilute",
                    "If EC is above 2.0, do a partial water swap",
                    "Reduce nutrient strength at next mix",
                    "Damaged tips won't heal — watch for progression on new growth",
                ],
            },
            {
                "symptom": "Yellowing lower leaves in veg (not during flush)",
                "diagnosis": "Nitrogen deficiency",
                "severity": "medium",
                "causes": [
                    "Nutrient solution too dilute (EC too low)",
                    "pH out of range preventing nitrogen uptake",
                    "Plant outgrowing the available nutrients in the reservoir",
                ],
                "solutions": [
                    "Check EC — if low, top off with full-strength nutrients",
                    "Check pH — nitrogen absorption drops above 6.5",
                    "In large plants with small containers, top-offs may not provide enough nitrogen — consider a partial water swap with fresh veg nutrients",
                ],
            },
        ],
    },
    {
        "category": "Container / Environment Issues",
        "problems": [
            {
                "symptom": "Green algae growth in reservoir or on roots",
                "diagnosis": "Light reaching the water",
                "severity": "high",
                "causes": [
                    "Container not fully opaque",
                    "Light gaps around the net pot or lid",
                    "Using a white or translucent container",
                ],
                "solutions": [
                    "Wrap container in black duct tape or aluminum foil",
                    "Seal all gaps around the net pot with neoprene collar or tape",
                    "Replace with a proper opaque container",
                    "Algae competes with roots for oxygen and nutrients — more damaging in Kratky than DWC because there's no aeration to offset it",
                ],
            },
            {
                "symptom": "Reservoir water too warm (above 75°F)",
                "diagnosis": "Heat stress risk + increased pathogen risk",
                "severity": "high",
                "causes": [
                    "Hot grow room or direct sunlight on container",
                    "No air pump cooling (DWC's air pump provides evaporative cooling that Kratky lacks)",
                    "Dark container absorbing heat from grow light",
                ],
                "solutions": [
                    "Frozen water bottles in the reservoir (replace every 12 hours)",
                    "Move container away from light heat",
                    "Insulate container with reflective material (Reflectix)",
                    "Increase Hydroguard dose to 3 ml/gal when water is warm",
                    "If chronic: consider a small water chiller or move to a cooler room",
                ],
            },
        ],
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# CONFIG EXPORT
# ═══════════════════════════════════════════════════════════════════════════

KRATKY_CONFIG = {
    "grow_type_id": "kratky",
    "version": "1.0.0",
    "stages": KRATKY_STAGES,
    "equipment": KRATKY_EQUIPMENT,
    "quick_reference": KRATKY_QUICK_REFERENCE,
    "troubleshooting": KRATKY_TROUBLESHOOTING,
    "total_grow_days": {
        "min": 90,
        "max": 150,
        "typical_photo": 120,
        "typical_auto": 75,
        "breakdown": "Germination (3-7d) + Seedling (7-14d) + Veg (28-63d) + Flower (56-70d) + Dry (7-14d) + Cure (14-60d)",
    },
}
