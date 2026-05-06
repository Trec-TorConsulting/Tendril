"""Auto-task generation engine — creates grow-type and stage-aware tasks.

v2: Routine-based grouping, timezone-aware scheduling, accurate intervals
per grow type, estimated durations, automation suppression, and progressive
disclosure (brief/detail descriptions).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.commercial.models import Task
from app.grows.models import Bucket, FeedingSchedule, GrowCycle, Strain, Tent, WeatherReading
from app.tenants.models import TenantMembership, TenantRole, User

logger = logging.getLogger("tendril.tasks.autogen")

# ── Grow type groups ────────────────────────────────────────────────

HYDRO_TYPES = {
    "dwc",
    "rdwc",
    "nft",
    "ebb_flow",
    "drip",
    "aeroponics",
    "kratky",
    "aquaponics",
    "dutch_bucket",
    "vertical_tower",
}
ACTIVE_HYDRO_TYPES = {
    "dwc",
    "rdwc",
    "nft",
    "ebb_flow",
    "drip",
    "aeroponics",
    "aquaponics",
    "dutch_bucket",
    "vertical_tower",
}
PASSIVE_HYDRO_TYPES = {"kratky", "wicking"}
SOIL_TYPES = {"soil", "outdoor_soil", "outdoor_container", "living_soil"}
COCO_TYPES = {"coco", "rockwool"}
OUTDOOR_TYPES = {"outdoor_soil", "outdoor_container"}
ALL_INDOOR = HYDRO_TYPES | COCO_TYPES | {"soil", "living_soil", "wicking"}


# ── Task template dataclass ─────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TaskTemplate:
    """Definition of an auto-generated task type."""

    category: str
    title: str
    brief: str  # 1-2 sentence actionable checklist (shown by default)
    detail: str | None  # Educational context (shown on expand / first time)
    interval_days: int  # 0 = one-shot (stage transition), >0 = recurring
    priority: str  # low, medium, high, urgent
    routine: str  # morning, evening, weekly, biweekly, monthly, on_demand
    estimated_minutes: int
    grow_types: set[str] | None  # None = all types
    stages: set[str] | None  # None = all stages


# ── Task Templates ──────────────────────────────────────────────────

TASK_TEMPLATES: list[TaskTemplate] = [
    # ═══════════════════════════════════════════════════════════════
    # MORNING ROUTINE — Quick daily checks at lights-on
    # ═══════════════════════════════════════════════════════════════
    # ── pH Check (varies by type) ────────────────────────────────
    TaskTemplate(
        "ph_check",
        "Check reservoir pH",
        brief="Test pH → target 5.5-6.2. Adjust with pH Down/Up if outside range.",
        detail="pH swings are the #1 issue in DWC/RDWC. Roots submerged 24/7 absorb nutrients unevenly, causing drift. Check daily at lights-on for consistent readings.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=3,
        grow_types={"dwc", "rdwc"},
        stages=None,
    ),
    TaskTemplate(
        "ph_check",
        "Check reservoir pH",
        brief="Test pH → target 5.5-6.5. Verify pump is running before testing.",
        detail="NFT delivers a thin film over bare roots — pH accuracy matters more because there's less solution to buffer.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=3,
        grow_types={"nft"},
        stages=None,
    ),
    TaskTemplate(
        "ph_check",
        "Check reservoir pH",
        brief="Test pH → target 5.5-6.5.",
        detail=None,
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=3,
        grow_types={"ebb_flow", "drip", "aeroponics"},
        stages=None,
    ),
    TaskTemplate(
        "ph_check",
        "Check solution pH",
        brief="Test pH → target 5.5-6.5. Only adjust if far out of range — minimal intervention.",
        detail="Kratky pH drifts as nutrients are consumed. The design is passive — only intervene if pH is below 5.0 or above 7.0.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=3,
        grow_types={"kratky"},
        stages=None,
    ),
    TaskTemplate(
        "ph_check",
        "Check runoff pH",
        brief="Fertigate, collect runoff → target 5.8-6.2. Input-to-runoff delta reveals salt buildup.",
        detail="Coco is inert and doesn't buffer pH like soil. If runoff pH drifts more than 0.3 from input, flush to reset.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=3,
        grow_types={"coco"},
        stages=None,
    ),
    TaskTemplate(
        "ph_check",
        "Check slab pH",
        brief="Measure slab pH → target 5.5-6.0. Check drip stake runoff.",
        detail="Rockwool holds solution longer than coco. EC/pH steering is the primary growth control method.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=3,
        grow_types={"rockwool"},
        stages=None,
    ),
    TaskTemplate(
        "ph_check",
        "Check soil runoff pH",
        brief="Water to slight runoff → test pH → target 6.0-7.0.",
        detail="Soil naturally buffers pH. Only check twice per week unless you notice deficiency symptoms (yellowing, purpling).",
        interval_days=3,
        priority="medium",
        routine="morning",
        estimated_minutes=3,
        grow_types={"soil"},
        stages=None,
    ),
    TaskTemplate(
        "ph_check",
        "Check runoff pH",
        brief="Water to runoff → test pH → target 6.0-7.0.",
        detail="Container grows drift faster than in-ground because there's less soil mass to buffer.",
        interval_days=3,
        priority="medium",
        routine="morning",
        estimated_minutes=3,
        grow_types={"outdoor_container"},
        stages=None,
    ),
    TaskTemplate(
        "ph_check",
        "Soil pH test (if supplementing)",
        brief="Test soil pH if actively fertilizing → target 6.0-7.0.",
        detail="In-ground outdoor soil rarely needs pH monitoring unless you're adding synthetic fertilizers that can acidify.",
        interval_days=7,
        priority="low",
        routine="weekly",
        estimated_minutes=5,
        grow_types={"outdoor_soil"},
        stages=None,
    ),
    # ── EC Check (varies by type) ───────────────────────────────
    TaskTemplate(
        "ec_check",
        "Check reservoir EC/PPM",
        brief="Measure EC → compare to target for current stage. Top off with plain water if EC is rising.",
        detail="Rising EC means plants are drinking more water than nutrients. Falling EC means they're hungry. Track the trend daily.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=2,
        grow_types=ACTIVE_HYDRO_TYPES,
        stages=None,
    ),
    TaskTemplate(
        "ec_check",
        "Check solution EC",
        brief="Measure EC — only check weekly. Kratky EC naturally rises as water is consumed.",
        detail="Don't panic at rising EC in Kratky — it's normal. Only intervene if plants show burn tips.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=2,
        grow_types={"kratky"},
        stages=None,
    ),
    TaskTemplate(
        "ec_check",
        "Check runoff EC",
        brief="Measure input EC vs runoff EC. If runoff > input by 0.5+, do a heavy flush.",
        detail="Salt buildup in coco/rockwool restricts nutrient uptake. The input-to-runoff delta is your early warning.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=2,
        grow_types=COCO_TYPES,
        stages=None,
    ),
    # ── Water Temperature (hydro only) ──────────────────────────
    TaskTemplate(
        "water_temp",
        "Check water temperature",
        brief="Verify reservoir temp 65-72°F (18-22°C). Above 72°F = root rot risk.",
        detail="Warm water holds less dissolved oxygen and promotes pythium. If temps run high, add Hydroguard (2 ml/gal) and consider a water chiller.",
        interval_days=1,
        priority="medium",
        routine="morning",
        estimated_minutes=2,
        grow_types={"dwc", "rdwc", "nft", "aeroponics"},
        stages=None,
    ),
    # ── Visual Health Inspection (universal) ────────────────────
    TaskTemplate(
        "health_check",
        "Visual health inspection",
        brief="Quick scan: leaf color, new growth, canopy shape. Note anything abnormal.",
        detail="Catching issues early is the difference between a quick fix and a lost plant. Look at leaf tips (burn), undersides (pests), stems (rot), and new growth (deficiency).",
        interval_days=1,
        priority="medium",
        routine="morning",
        estimated_minutes=3,
        grow_types=None,
        stages=None,
    ),
    # ── Circulation / Pump Check (system-critical) ──────────────
    TaskTemplate(
        "circulation_check",
        "Check circulation pump & flow",
        brief="Verify all sites have equal flow. Listen for pump strain. Check return lines for blockage.",
        detail="RDWC shares one solution across all sites. Uneven flow = uneven nutrition = inconsistent results.",
        interval_days=2,
        priority="high",
        routine="morning",
        estimated_minutes=3,
        grow_types={"rdwc"},
        stages=None,
    ),
    TaskTemplate(
        "circulation_check",
        "Verify pump & channel flow",
        brief="CRITICAL: Confirm all channels are flowing. NFT pump failure kills roots in minutes.",
        detail="Bare roots in NFT have zero moisture buffer. Even 10 minutes without flow causes irreversible root damage at the tips.",
        interval_days=1,
        priority="urgent",
        routine="morning",
        estimated_minutes=3,
        grow_types={"nft"},
        stages=None,
    ),
    TaskTemplate(
        "nozzle_check",
        "Check mist nozzles & pressure",
        brief="CRITICAL: Verify all nozzles misting. Check system pressure. Clear any clogs.",
        detail="Aero roots have zero buffer — nozzle failure kills roots in under a minute. This is the most failure-critical check in any grow system.",
        interval_days=1,
        priority="urgent",
        routine="morning",
        estimated_minutes=5,
        grow_types={"aeroponics"},
        stages=None,
    ),
    # ── Watering (coco/soil/outdoor) ────────────────────────────
    TaskTemplate(
        "watering",
        "Fertigate coco (multiple times today)",
        brief="Feed to 10-20% runoff. In flower: 3-5x daily. Never let coco dry out completely.",
        detail="Coco is inert — every watering is a feeding. Frequency increases with plant size and flower development. Track pot weight: heavy = saturated, light = time to feed.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=10,
        grow_types={"coco"},
        stages={"flowering", "late_flower"},
    ),
    TaskTemplate(
        "watering",
        "Fertigate coco",
        brief="Feed to 10-20% runoff. 1-2x daily in veg. Never let coco fully dry.",
        detail="Coco should always stay moist. In veg, once or twice daily is usually sufficient depending on pot size and plant size.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=10,
        grow_types={"coco"},
        stages={"seedling", "vegetative"},
    ),
    TaskTemplate(
        "watering",
        "Irrigate rockwool",
        brief="Run irrigation cycles per crop steering strategy. Check slab saturation level.",
        detail="Rockwool irrigation is about steering: generative (more dry-back) for flower development, vegetative (stay wet) for growth. Adjust shot timing, not just volume.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=5,
        grow_types={"rockwool"},
        stages=None,
    ),
    TaskTemplate(
        "watering",
        "Check soil moisture & water if needed",
        brief='Finger test at 2-3" depth. Water deeply when dry. Allow proper wet/dry cycle.',
        detail="Soil needs a wet/dry cycle to drive root growth. Constantly wet soil = root rot and fungus gnats. Let it dry back between waterings.",
        interval_days=1,
        priority="medium",
        routine="morning",
        estimated_minutes=5,
        grow_types={"soil"},
        stages=None,
    ),
    TaskTemplate(
        "watering",
        "Check container moisture",
        brief="Lift pot (light = dry). Water deeply until runoff. Containers dry faster than in-ground.",
        detail="Outdoor containers overheat in sun and dry quickly. Dark containers especially. On hot days, may need morning AND evening watering.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=10,
        grow_types={"outdoor_container"},
        stages=None,
    ),
    TaskTemplate(
        "watering",
        "Check soil moisture (supplement rain if dry)",
        brief='Check moisture at 4-6" depth. Only water if dry — rain usually handles it.',
        detail="Deep, infrequent watering encourages deep root growth. Frequent shallow watering makes roots lazy and surface-dependent.",
        interval_days=2,
        priority="medium",
        routine="morning",
        estimated_minutes=5,
        grow_types={"outdoor_soil"},
        stages=None,
    ),
    # ── Top Off (DWC/RDWC) ──────────────────────────────────────
    TaskTemplate(
        "top_off",
        "Top off reservoir",
        brief="Add plain pH'd water to maintain level. Do NOT add nutrients — EC rises as water evaporates.",
        detail="Between full changes, just top off with pH'd water. Adding nutrients on top of concentrated solution causes burn. Track how fast the level drops — it increases as plants grow.",
        interval_days=2,
        priority="medium",
        routine="morning",
        estimated_minutes=5,
        grow_types={"dwc", "rdwc"},
        stages=None,
    ),
    # ── Water Level (Kratky) ────────────────────────────────────
    TaskTemplate(
        "water_level",
        "Check water level & air gap",
        brief="Check level. NEVER refill to top — the air gap provides oxygen. Only add water if roots are drying.",
        detail="Kratky's air gap IS the design. As plants drink, roots develop above the water line to breathe. Refilling to top drowns air roots.",
        interval_days=3,
        priority="high",
        routine="morning",
        estimated_minutes=2,
        grow_types={"kratky"},
        stages=None,
    ),
    # ── Dry-back Monitoring (coco/rockwool) ─────────────────────
    TaskTemplate(
        "dryback_check",
        "Monitor dry-back %",
        brief="Track pot/slab weight: morning vs evening. Target controlled dry-back — enough to drive roots, not enough to stress.",
        detail="Coco/rockwool dry-back drives root exploration. In flower, slightly more dry-back encourages generative growth (bigger buds). In veg, stay wetter for vegetative push.",
        interval_days=1,
        priority="medium",
        routine="evening",
        estimated_minutes=3,
        grow_types=COCO_TYPES,
        stages={"vegetative", "flowering", "late_flower"},
    ),
    # ── CalMag (coco specific) ──────────────────────────────────
    TaskTemplate(
        "calmag",
        "CalMag supplement check",
        brief="Verify CalMag in every feed. Watch for interveinal yellowing (Ca) or leaf edge browning (Mg).",
        detail="Coco coir has a natural cation exchange that strips calcium and magnesium from solution. Always include CalMag — it's not optional in coco.",
        interval_days=3,
        priority="medium",
        routine="morning",
        estimated_minutes=2,
        grow_types={"coco"},
        stages=None,
    ),
    # ── Weather (outdoor) ───────────────────────────────────────
    TaskTemplate(
        "weather_check",
        "Check weather forecast",
        brief="Review 7-day forecast. Note storms, frost risk, or heatwaves. Prepare protection if needed.",
        detail="Outdoor grows are weather-dependent. Frost kills, heatwaves stress, heavy rain causes bud rot in flower. Plan protection (covers, shade cloth) a day ahead.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=3,
        grow_types=OUTDOOR_TYPES,
        stages=None,
    ),
    # ═══════════════════════════════════════════════════════════════
    # EVENING ROUTINE — End-of-day checks
    # ═══════════════════════════════════════════════════════════════
    TaskTemplate(
        "light_check",
        "Check light distance & intensity",
        brief="Measure canopy-to-light distance. Adjust if new growth is reaching or bleaching.",
        detail="Light stress shows as bleaching (white tips) or stretching (too far). As plants grow, raise lights to maintain target PPFD. Use a PAR meter if available.",
        interval_days=3,
        priority="low",
        routine="evening",
        estimated_minutes=3,
        grow_types=ALL_INDOOR,
        stages={"vegetative", "flowering"},
    ),
    # ── Runoff Check (drip systems) ─────────────────────────────
    TaskTemplate(
        "runoff_check",
        "Check runoff percentage",
        brief="Target 10-20% runoff. Too little = salt buildup. Too much = waste. Adjust flow/duration.",
        detail="Measure runoff volume vs input volume. Under 10% means salts accumulate in the media. Over 20% is wasteful and can overwork the drain system.",
        interval_days=3,
        priority="medium",
        routine="evening",
        estimated_minutes=3,
        grow_types={"drip"},
        stages=None,
    ),
    # ── Root Check ──────────────────────────────────────────────
    TaskTemplate(
        "root_check",
        "Inspect root health",
        brief="Check roots: white/cream = healthy. Brown/slimy = rot. Ensure air stones bubbling vigorously.",
        detail="Root rot (pythium) is the #1 killer in DWC. Prevention: keep water 65-72°F, use Hydroguard (2 ml/gal), replace air stones every 3 months, and maintain dissolved oxygen.",
        interval_days=3,
        priority="high",
        routine="evening",
        estimated_minutes=5,
        grow_types={"dwc", "rdwc"},
        stages=None,
    ),
    TaskTemplate(
        "root_check",
        "Check bare root condition",
        brief="Inspect root tips for drying or browning. Verify full mist coverage in chamber.",
        detail="Aero roots should be white and fuzzy. Brown tips mean coverage gaps or nozzle issues. Biofilm on nozzles degrades spray pattern over time.",
        interval_days=2,
        priority="high",
        routine="evening",
        estimated_minutes=5,
        grow_types={"aeroponics"},
        stages=None,
    ),
    # ═══════════════════════════════════════════════════════════════
    # WEEKLY ROUTINE — Maintenance day
    # ═══════════════════════════════════════════════════════════════
    # ── Reservoir Change ────────────────────────────────────────
    TaskTemplate(
        "flush_and_fill",
        "Flush & Fill reservoir",
        brief="Drain, rinse, refill with fresh nutrient solution. pH to 5.8-6.2 after mixing.",
        detail=None,
        interval_days=7,
        priority="high",
        routine="weekly",
        estimated_minutes=45,
        grow_types={"dwc", "rdwc", "ebb_flow", "drip"},
        stages=None,
    ),
    TaskTemplate(
        "flush_and_fill",
        "Flush & Fill reservoir",
        brief="Drain, rinse, refill with fresh solution. NFT uses less volume — mix carefully.",
        detail=None,
        interval_days=7,
        priority="high",
        routine="weekly",
        estimated_minutes=30,
        grow_types={"nft"},
        stages=None,
    ),
    TaskTemplate(
        "flush_and_fill",
        "Flush & Fill reservoir",
        brief="Drain, sanitize chamber, refill. Aero requires cleaner solution — change every 5 days.",
        detail="Aeroponics reservoirs foul faster because fine mist aerosolizes bacteria. Shorter change intervals and occasional peroxide flush prevent biofilm.",
        interval_days=5,
        priority="high",
        routine="weekly",
        estimated_minutes=40,
        grow_types={"aeroponics"},
        stages=None,
    ),
    # ── Pest Management (IPM) ──────────────────────────────────
    TaskTemplate(
        "ipm_spray",
        "IPM preventive spray",
        brief="Apply preventive spray (rotate products: neem → spinosad → BT → pyrethrin). Spray at lights-off.",
        detail="Integrated Pest Management works on rotation to prevent resistance. Never use the same product twice in a row. Spray undersides of leaves where pests hide. Always spray at lights-off to prevent leaf burn.",
        interval_days=3,
        priority="medium",
        routine="evening",
        estimated_minutes=10,
        grow_types=ALL_INDOOR | {"outdoor_container"},
        stages={"vegetative", "flowering"},
    ),
    TaskTemplate(
        "ipm_spray",
        "IPM preventive spray (outdoor)",
        brief="Apply preventive spray. Rotate products. Check for caterpillars, aphids, mites. Spray at dusk.",
        detail="Outdoor grows face more pest pressure. BT (Bacillus thuringiensis) for caterpillars, neem for soft-bodied insects, spinosad for thrips. Spray at dusk so beneficials aren't harmed.",
        interval_days=5,
        priority="medium",
        routine="evening",
        estimated_minutes=15,
        grow_types={"outdoor_soil"},
        stages={"vegetative", "flowering"},
    ),
    # ── Pest Inspection ─────────────────────────────────────────
    TaskTemplate(
        "pest_check",
        "Inspect for pests & mold",
        brief="Check leaf undersides, stems, medium surface. Look for webbing, spots, gnats, mold.",
        detail="Common indoor pests: spider mites (webs on undersides), thrips (silver streaks on leaves), fungus gnats (larvae in wet media). Early detection = easy fix. Late detection = disaster.",
        interval_days=3,
        priority="medium",
        routine="evening",
        estimated_minutes=5,
        grow_types=ALL_INDOOR,
        stages=None,
    ),
    TaskTemplate(
        "pest_check",
        "Check for pests & animal damage",
        brief="Inspect for caterpillars, aphids, mites, deer, rabbits. Check for damage since last visit.",
        detail="Outdoor grows face insects AND animals. Caterpillars burrow into buds (bud rot follows). Deer browse tops. Set up physical barriers and check daily during flower.",
        interval_days=2,
        priority="high",
        routine="morning",
        estimated_minutes=10,
        grow_types=OUTDOOR_TYPES,
        stages=None,
    ),
    # ── Equipment Checks ────────────────────────────────────────
    TaskTemplate(
        "equipment_check",
        "Check pumps, fans & air stones",
        brief="Verify: air pump running, stones bubbling evenly, circulation pump quiet, exhaust fan pulling.",
        detail="Air stone output degrades over months as pores clog. Replace every 3 months. Pump noise increase means wear. Exhaust fan CFM drops as carbon filter loads.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=10,
        grow_types=ACTIVE_HYDRO_TYPES,
        stages=None,
    ),
    TaskTemplate(
        "equipment_check",
        "Check fans, timers & irrigation",
        brief="Verify: oscillating fans running, light timer correct, drip/pump timers firing, no leaks.",
        detail="Equipment failures during lights-off go unnoticed for hours. Check timers weekly and after any power interruption.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=10,
        grow_types=COCO_TYPES | {"soil"},
        stages=None,
    ),
    # ── Meter Calibration ───────────────────────────────────────
    TaskTemplate(
        "meter_calibration",
        "Calibrate pH & EC meters",
        brief="Calibrate pH probe with 4.0 & 7.0 buffers. Calibrate EC with standard solution. Rinse between.",
        detail="Uncalibrated meters give false confidence. pH probes drift 0.1-0.3 per week. A meter reading 6.5 that's actually 6.8 causes silent lockout. Calibrate biweekly minimum.",
        interval_days=14,
        priority="medium",
        routine="weekly",
        estimated_minutes=15,
        grow_types=ACTIVE_HYDRO_TYPES | COCO_TYPES,
        stages=None,
    ),
    TaskTemplate(
        "meter_calibration",
        "Calibrate pH meter",
        brief="Calibrate pH probe with 4.0 & 7.0 buffers. Less critical for soil but still matters.",
        detail="Soil growers check pH less often, but when you do check, accuracy matters. Monthly calibration is sufficient.",
        interval_days=30,
        priority="low",
        routine="monthly",
        estimated_minutes=10,
        grow_types=SOIL_TYPES,
        stages=None,
    ),
    # ── Photo Documentation ─────────────────────────────────────
    TaskTemplate(
        "photo_documentation",
        "Take weekly progress photos",
        brief="Photograph from consistent angle for time-lapse comparison. Include full canopy + close-ups of any issues.",
        detail="Weekly photos are invaluable for tracking growth rate, identifying slow-developing problems, and sharing progress. Same angle, same lighting, same distance = useful comparison.",
        interval_days=7,
        priority="low",
        routine="weekly",
        estimated_minutes=5,
        grow_types=None,
        stages={"vegetative", "flowering", "late_flower"},
    ),
    # ── Algae Check (light-sensitive media) ─────────────────────
    TaskTemplate(
        "algae_check",
        "Check for algae growth",
        brief="Inspect container/slab surfaces for green/brown growth. Cover any exposed areas.",
        detail="Algae = light + moisture + nutrients. It competes for oxygen and can clog drip lines. Cover all exposed rockwool/reservoir surfaces with opaque material.",
        interval_days=7,
        priority="low",
        routine="weekly",
        estimated_minutes=3,
        grow_types={"kratky", "rockwool"},
        stages=None,
    ),
    # ── Nutrient Prep (day before res change) ───────────────────
    TaskTemplate(
        "nutrient_prep",
        "Pre-mix nutrients for tomorrow's res change",
        brief="Mix nutrient solution tonight. Let it aerate overnight for stable pH reading tomorrow.",
        detail="Pre-mixing allows: pH to stabilize (fresh mixes drift for 12-24h), chlorine to off-gas from tap water, and temperature to equalize. Measure and record the recipe.",
        interval_days=7,
        priority="low",
        routine="evening",
        estimated_minutes=15,
        grow_types=ACTIVE_HYDRO_TYPES,
        stages=None,
    ),
    # ═══════════════════════════════════════════════════════════════
    # BIWEEKLY / MONTHLY ROUTINE
    # ═══════════════════════════════════════════════════════════════
    # ── Soil Amendments ─────────────────────────────────────────
    TaskTemplate(
        "top_dress",
        "Top dress nutrients / amendments",
        brief="Apply dry amendments to soil surface. Water in lightly. Record what you applied.",
        detail="Organic soil relies on slow-release dry amendments and microbial activity to break them down. Top dress every 2 weeks during active growth. Worm castings, kelp meal, bone meal are common.",
        interval_days=14,
        priority="low",
        routine="biweekly",
        estimated_minutes=15,
        grow_types={"soil"},
        stages={"vegetative", "flowering"},
    ),
    TaskTemplate(
        "soil_amendment",
        "Apply amendments / compost",
        brief="Top dress compost, worm castings, or dry amendments. Water in deeply.",
        detail="Outdoor in-ground benefits from regular organic matter. Monthly applications feed the soil biology which feeds the plant.",
        interval_days=30,
        priority="low",
        routine="monthly",
        estimated_minutes=20,
        grow_types={"outdoor_soil"},
        stages={"vegetative", "flowering"},
    ),
    # ── Carbon Filter ───────────────────────────────────────────
    TaskTemplate(
        "carbon_filter",
        "Check/replace carbon filter",
        brief="Sniff test at exhaust. If odor passes through, filter is spent. Replace or recharge.",
        detail="Carbon filters last 12-18 months for light use, 6-9 months for heavy flower odor. In late flower, even a good filter works hard. Pre-filters extend life — wash them monthly.",
        interval_days=30,
        priority="low",
        routine="monthly",
        estimated_minutes=15,
        grow_types=ALL_INDOOR,
        stages={"flowering", "late_flower"},
    ),
    # ── Air Stone Replacement ───────────────────────────────────
    TaskTemplate(
        "air_stone",
        "Inspect air stones (replace if clogged)",
        brief="Check air stone bubble output. Uneven/weak bubbles = clogged. Replace every 3 months.",
        detail="Mineral deposits and biofilm clog air stone pores over time, reducing dissolved oxygen. Boiling in vinegar can extend life, but replacement is cheap insurance.",
        interval_days=90,
        priority="low",
        routine="monthly",
        estimated_minutes=10,
        grow_types={"dwc", "rdwc"},
        stages=None,
    ),
    # ── Deep Clean ──────────────────────────────────────────────
    TaskTemplate(
        "deep_clean",
        "Deep clean grow space",
        brief="Wipe surfaces, clean trays, check for mold in corners. Sanitize any standing water areas.",
        detail="A clean environment prevents pest and pathogen buildup. Monthly wipe-down of walls, trays, and equipment reduces spore/egg counts significantly.",
        interval_days=30,
        priority="low",
        routine="monthly",
        estimated_minutes=30,
        grow_types=ALL_INDOOR,
        stages=None,
    ),
    # ═══════════════════════════════════════════════════════════════
    # STAGE-SPECIFIC (generated when stage matches)
    # ═══════════════════════════════════════════════════════════════
    # ── Defoliation (veg) ───────────────────────────────────────
    TaskTemplate(
        "defoliation",
        "Defoliation / canopy management",
        brief="Remove large fan leaves blocking bud sites. LST/HST as needed. Open canopy for light & airflow.",
        detail="Strategic defoliation in veg builds the structure for flower. Remove leaves that block lower growth, redirect energy to tops, and improve airflow to prevent mold.",
        interval_days=7,
        priority="low",
        routine="weekly",
        estimated_minutes=15,
        grow_types=None,
        stages={"vegetative"},
    ),
    # ── Trichome Check (late flower) ────────────────────────────
    TaskTemplate(
        "trichome_check",
        "Check trichomes (harvest timing)",
        brief="Loupe/microscope check: clear = early, cloudy = peak, amber = past peak. Target mostly cloudy + 20-30% amber.",
        detail="Trichome color is the only reliable harvest indicator. Breeder 'flowering days' is a rough estimate. Actual readiness depends on phenotype, environment, and your preference (more amber = more sedative).",
        interval_days=2,
        priority="high",
        routine="morning",
        estimated_minutes=10,
        grow_types=None,
        stages={"late_flower", "ripening"},
    ),
    # ── Flush Stage ─────────────────────────────────────────────
    TaskTemplate(
        "flush",
        "Flush with plain water only",
        brief="Plain pH'd water only — no nutrients. Check runoff clarity. Continue until EC < 0.3.",
        detail="Proper pre-harvest flush removes residual salts for a cleaner, smoother final product. Duration: hydro 3-7 days, coco 5-7 days, soil 7-14 days.",
        interval_days=1,
        priority="urgent",
        routine="morning",
        estimated_minutes=10,
        grow_types=None,
        stages={"flush"},
    ),
    # ── Harvest Check (outdoor flower) ──────────────────────────
    TaskTemplate(
        "harvest_check",
        "Assess harvest readiness",
        brief="Check trichomes + weather forecast. Plan harvest window around dry weather.",
        detail="Outdoor harvest timing balances trichome ripeness with weather risk. Rain during harvest = bud rot. If storms are coming and trichomes are mostly cloudy, harvest early rather than risk the crop.",
        interval_days=2,
        priority="high",
        routine="morning",
        estimated_minutes=10,
        grow_types=OUTDOOR_TYPES,
        stages={"flowering", "late_flower", "ripening"},
    ),
    # ── Outdoor Field Scouting ──────────────────────────────────
    TaskTemplate(
        "pest_scout",
        "Field scout with photo documentation",
        brief="Walk the garden. Document any pest activity, disease, or beneficials. Log in Field Scout tab with photos + grid location.",
        detail="Systematic scouting catches problems before they spread. Walk a consistent path, check representative plants in each zone, photograph anything unusual.",
        interval_days=3,
        priority="medium",
        routine="morning",
        estimated_minutes=15,
        grow_types={"outdoor_soil"},
        stages={"vegetative", "flowering"},
    ),
    TaskTemplate(
        "companion_check",
        "Check companion plant health",
        brief="Inspect companions — thriving or struggling? Replace any that bolted or died.",
        detail="Companion plants deter pests and attract beneficials. Basil repels thrips, marigolds deter whiteflies, clover fixes nitrogen. Replace dead ones to maintain the defense perimeter.",
        interval_days=7,
        priority="low",
        routine="weekly",
        estimated_minutes=5,
        grow_types={"outdoor_soil"},
        stages={"vegetative", "flowering"},
    ),
    TaskTemplate(
        "rain_gauge",
        "Log rain gauge measurement",
        brief="Check rain gauge, log reading, reset. Accurate rainfall data optimizes supplemental irrigation.",
        detail=None,
        interval_days=1,
        priority="low",
        routine="morning",
        estimated_minutes=2,
        grow_types={"outdoor_soil"},
        stages=None,
    ),
    # ═══════════════════════════════════════════════════════════════
    # AQUAPONICS — Fish health + water chemistry
    # ═══════════════════════════════════════════════════════════════
    TaskTemplate(
        "fish_feed",
        "Feed fish",
        brief="Feed fish appropriate amount. Remove uneaten food after 5 min. Observe feeding response.",
        detail="Overfeeding is the #1 cause of ammonia spikes. Fish should consume all food within 3-5 minutes. Uneaten food decomposes and overwhelms the biofilter.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=5,
        grow_types={"aquaponics"},
        stages=None,
    ),
    TaskTemplate(
        "fish_feed_evening",
        "Evening fish feed",
        brief="Second daily feeding (lighter portion). Check fish behavior — active and responsive = healthy.",
        detail=None,
        interval_days=1,
        priority="medium",
        routine="evening",
        estimated_minutes=5,
        grow_types={"aquaponics"},
        stages=None,
    ),
    TaskTemplate(
        "nitrogen_cycle_check",
        "Test ammonia / nitrite / nitrate",
        brief="Test ammonia (target 0), nitrite (target 0), nitrate (target 20-60 ppm). Ammonia or nitrite above 0.5 ppm = immediate action.",
        detail="The nitrogen cycle converts toxic ammonia → nitrite → nitrate (plant food). Any detectable ammonia or nitrite means the biofilter is overwhelmed or not yet cycled. Reduce feeding and add aeration.",
        interval_days=2,
        priority="high",
        routine="morning",
        estimated_minutes=10,
        grow_types={"aquaponics"},
        stages=None,
    ),
    TaskTemplate(
        "fish_health_check",
        "Observe fish health",
        brief="Watch for: surface gasping (low O2), clamped fins (stress), white spots (ich), erratic swimming. Count fish.",
        detail="Fish are the canary in the coal mine. Behavioral changes precede water chemistry problems. Surface gasping = add aeration immediately. Lethargy = check temperature and ammonia.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=5,
        grow_types={"aquaponics"},
        stages=None,
    ),
    TaskTemplate(
        "biofilter_check",
        "Inspect biofilter media",
        brief="Check biofilter flow, rinse if clogged (use system water ONLY — never chlorinated tap). Verify even distribution.",
        detail="Biofilter houses nitrifying bacteria. Chlorinated water kills them instantly, crashing the nitrogen cycle. Only rinse in dechlorinated system water.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=15,
        grow_types={"aquaponics"},
        stages=None,
    ),
    TaskTemplate(
        "water_top_off",
        "Top off system water",
        brief="Add dechlorinated water to maintain level. Mark level line. Evaporation loss is normal.",
        detail="Use dechlorinated or aged water only. Chlorine/chloramine kills both fish and beneficial bacteria. A 10% top-off is normal weekly in warm weather.",
        interval_days=3,
        priority="medium",
        routine="morning",
        estimated_minutes=10,
        grow_types={"aquaponics"},
        stages=None,
    ),
    # ═══════════════════════════════════════════════════════════════
    # LIVING SOIL / NO-TILL — Minimal intervention
    # ═══════════════════════════════════════════════════════════════
    TaskTemplate(
        "watering",
        "Water beds (water only)",
        brief='Water gently until soil is moist at 4-6" depth. Never water to runoff — protects soil biology.',
        detail="Living soil is a WATER ONLY system. The soil food web (fungi, bacteria, worms) provides nutrition. Overwatering drowns aerobic microbes and compacts soil. Let top inch dry between waterings.",
        interval_days=2,
        priority="high",
        routine="morning",
        estimated_minutes=10,
        grow_types={"living_soil"},
        stages=None,
    ),
    TaskTemplate(
        "soil_biology_check",
        "Check soil surface activity",
        brief="Look for: fungal hyphae (white threads), worm castings, beneficial insect activity. Healthy signs = thriving biology.",
        detail="Visible mycelium on the soil surface means your fungal network is healthy. Worm castings indicate active decomposition. If the surface is lifeless and crusty, add mulch and a compost tea.",
        interval_days=3,
        priority="medium",
        routine="morning",
        estimated_minutes=5,
        grow_types={"living_soil"},
        stages=None,
    ),
    TaskTemplate(
        "top_dress",
        "Top dress with amendments",
        brief="Apply thin layer of compost + worm castings + dry amendments. Do NOT dig in — let biology incorporate it.",
        detail="Top dressing feeds the soil, not the plant directly. Microbes and worms break it down into plant-available form over 1-2 weeks. Never till or dig into living soil — it destroys fungal networks.",
        interval_days=21,
        priority="medium",
        routine="morning",
        estimated_minutes=20,
        grow_types={"living_soil"},
        stages=None,
    ),
    TaskTemplate(
        "compost_tea",
        "Brew and apply compost tea",
        brief="Brew actively aerated compost tea (24-48h). Apply as soil drench. Boosts microbial diversity.",
        detail="AACT (Actively Aerated Compost Tea) multiplies beneficial microbes. Brew with worm castings, kelp, molasses, and vigorous aeration. Apply within 4 hours of finishing — microbes die quickly without oxygen.",
        interval_days=14,
        priority="low",
        routine="morning",
        estimated_minutes=30,
        grow_types={"living_soil"},
        stages=None,
    ),
    TaskTemplate(
        "mulch_check",
        "Check mulch layer",
        brief='Maintain 2-3" mulch layer (straw, leaves, or cover crop chop). Replenish bare spots.',
        detail="Mulch protects soil biology from UV, retains moisture, feeds worms, and prevents compaction from watering. Bare soil = dead soil surface. Always keep covered.",
        interval_days=7,
        priority="low",
        routine="weekly",
        estimated_minutes=10,
        grow_types={"living_soil"},
        stages=None,
    ),
    TaskTemplate(
        "cover_crop",
        "Manage cover crop",
        brief="If between cycles: maintain cover crop (clover, rye, vetch). If growing: chop-and-drop around plants as mulch.",
        detail="Cover crops fix nitrogen, prevent erosion, feed soil biology, and break up compaction with roots. Chop at flowering for maximum nutrient return — never pull roots out of no-till beds.",
        interval_days=7,
        priority="low",
        routine="weekly",
        estimated_minutes=10,
        grow_types={"living_soil"},
        stages=None,
    ),
    # ═══════════════════════════════════════════════════════════════
    # DUTCH BUCKET — Drain-to-waste drip
    # ═══════════════════════════════════════════════════════════════
    TaskTemplate(
        "ph_check",
        "Check reservoir pH and EC",
        brief="Test pH → target 5.5-6.5. Test EC → adjust for stage. Check runoff EC from a sample bucket.",
        detail="Dutch buckets are drain-to-waste — fresh solution every feed. Monitor input vs runoff EC delta. If runoff EC exceeds input by 0.5+, run an extra feed cycle to flush salts.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=5,
        grow_types={"dutch_bucket"},
        stages=None,
    ),
    TaskTemplate(
        "emitter_check",
        "Verify all emitters flowing",
        brief="Run a manual feed cycle. Visually confirm every bucket's emitter is dripping. Clear any clogs.",
        detail="One stuck emitter = one dead plant within hours (perlite holds almost no water). Check daily during hot weather. Keep spare emitters on hand.",
        interval_days=2,
        priority="high",
        routine="morning",
        estimated_minutes=10,
        grow_types={"dutch_bucket"},
        stages=None,
    ),
    TaskTemplate(
        "drain_line_check",
        "Check drain lines",
        brief="Verify all drain lines flowing freely. Check for root intrusion or salt buildup at drain fittings.",
        detail="Blocked drain lines cause the bucket to flood, drowning roots in perlite. Root tips grow toward drain openings — trim any visible root mass at the drain fitting.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=10,
        grow_types={"dutch_bucket"},
        stages=None,
    ),
    # ═══════════════════════════════════════════════════════════════
    # VERTICAL TOWER — Flow and light management
    # ═══════════════════════════════════════════════════════════════
    TaskTemplate(
        "ph_check",
        "Check reservoir pH and EC",
        brief="Test pH → target 5.5-6.5. Test EC → adjust for stage. Towers use solution fast — top off as needed.",
        detail="Towers have many plants sharing one reservoir — nutrient depletion and pH drift happen faster than single-bucket systems. Check more frequently in flower.",
        interval_days=1,
        priority="high",
        routine="morning",
        estimated_minutes=5,
        grow_types={"vertical_tower"},
        stages=None,
    ),
    TaskTemplate(
        "flow_check",
        "Verify tower flow — all ports receiving solution",
        brief="Run pump and check: top ports dripping? Bottom ports not pooling? No root blockage mid-tower?",
        detail="Gravity-fed towers rely on even flow from top to bottom. Root mass in upper ports can block flow to lower plants. Trim roots if they're clogging the channel.",
        interval_days=2,
        priority="high",
        routine="morning",
        estimated_minutes=10,
        grow_types={"vertical_tower"},
        stages=None,
    ),
    TaskTemplate(
        "light_rotation",
        "Rotate towers (if not auto-rotating)",
        brief="Rotate each tower 90° to ensure even light exposure on all sides.",
        detail="Plants on the side facing away from the light stretch and produce less. Quarter-turn daily gives even growth. Skip if you have auto-rotating towers.",
        interval_days=1,
        priority="low",
        routine="morning",
        estimated_minutes=5,
        grow_types={"vertical_tower"},
        stages=None,
    ),
    # ═══════════════════════════════════════════════════════════════
    # WICKING — Passive sub-irrigation
    # ═══════════════════════════════════════════════════════════════
    TaskTemplate(
        "reservoir_check",
        "Check sub-reservoir level",
        brief="Check fill tube or indicator — refill if below 25%. Use dilute nutrient solution.",
        detail="Wicking beds self-regulate water delivery, but only if the reservoir has water. Running dry breaks the capillary connection and may require top-watering to re-establish wicking.",
        interval_days=2,
        priority="high",
        routine="morning",
        estimated_minutes=5,
        grow_types={"wicking"},
        stages=None,
    ),
    TaskTemplate(
        "surface_salt_check",
        "Check for surface salt buildup",
        brief="Look for white crust on soil surface. If present, top-water once to flush salts down past root zone.",
        detail="Capillary action draws water up but leaves dissolved salts at the evaporation point (surface). Periodic top-watering pushes salts back down. This is the one time you water from above in a wicking system.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=10,
        grow_types={"wicking"},
        stages=None,
    ),
    TaskTemplate(
        "soil_moisture_check",
        "Check soil moisture at root zone",
        brief='Probe at 3-4" depth — should be consistently moist (not soggy). If dry, the wick may be broken.',
        detail="Wicking works best when media maintains even moisture throughout. Dry pockets mean the capillary connection is broken (air gap). Top-water once to re-establish, then let wicking resume.",
        interval_days=3,
        priority="medium",
        routine="morning",
        estimated_minutes=3,
        grow_types={"wicking"},
        stages=None,
    ),
]


# ── Automation suppressions ─────────────────────────────────────────

AUTOMATION_SUPPRESSIONS: dict[str, list[str]] = {
    "auto_ph_dosing": ["ph_check"],
    "auto_ec_dosing": ["ec_check"],
    "auto_irrigation": ["watering"],
    "chiller_heater": ["water_temp"],
    "inline_monitor": ["ph_check", "ec_check"],
}

AUTOMATION_VERIFY_TASKS: dict[str, TaskTemplate] = {
    "auto_ph_dosing": TaskTemplate(
        "verify_automation",
        "Verify pH auto-doser calibration",
        brief="Check auto-doser reservoir levels. Verify probe reading matches handheld meter. Refill pH solutions.",
        detail="Auto-dosers drift over time. Weekly verification against a handheld reading ensures the automation isn't silently dosing to wrong targets.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=10,
        grow_types=None,
        stages=None,
    ),
    "auto_ec_dosing": TaskTemplate(
        "verify_automation",
        "Verify EC auto-doser calibration",
        brief="Check nutrient stock levels. Verify EC reading matches handheld meter. Check for line clogs.",
        detail="Nutrient stock solutions can crystallize and clog dosing pumps. Weekly verification prevents silent failure.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=10,
        grow_types=None,
        stages=None,
    ),
    "auto_irrigation": TaskTemplate(
        "verify_automation",
        "Verify irrigation timer & emitters",
        brief="Run a manual cycle. Check all emitters flowing. Verify timer schedule matches current stage needs.",
        detail="Clogged emitters cause dry spots that kill roots silently. One stuck-off emitter during a weekend = one dead plant.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=10,
        grow_types=None,
        stages=None,
    ),
    "chiller_heater": TaskTemplate(
        "verify_automation",
        "Verify chiller/heater operation",
        brief="Check water temp with handheld thermometer. Compare to chiller display. Clean intake filter.",
        detail="Chillers lose efficiency as filters clog. A chiller reading 68°F while actual water is 74°F means a dirty heat exchanger or low coolant.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=5,
        grow_types=None,
        stages=None,
    ),
    "inline_monitor": TaskTemplate(
        "verify_automation",
        "Verify inline monitor calibration",
        brief="Compare inline readings to handheld meter. Calibrate probes if drift > 0.2 pH or > 0.1 EC.",
        detail="Inline probes foul faster than handheld because they're constantly submerged. Weekly comparison catches drift before it causes problems.",
        interval_days=7,
        priority="medium",
        routine="weekly",
        estimated_minutes=10,
        grow_types=None,
        stages=None,
    ),
}


# ── Stage transition tasks ──────────────────────────────────────────

STAGE_TRANSITION_TASKS: dict[str, list[tuple[str, str, str, str, int, set[str] | None]]] = {
    # stage: [(title, brief, priority, routine, est_minutes, grow_types_or_None)]
    "vegetative": [
        (
            "Increase light hours to 18/6",
            "Switch light schedule to 18 on / 6 off for maximum vegetative growth.",
            "medium",
            "on_demand",
            5,
            None,
        ),
        (
            "Begin vegetative nutrient schedule",
            "Transition to veg nutrients. Increase nitrogen ratio for leaf and stem development.",
            "medium",
            "on_demand",
            10,
            None,
        ),
        (
            "Start LST / training plan",
            "Begin low-stress training while stems are flexible. Open the canopy early for better structure.",
            "low",
            "on_demand",
            15,
            None,
        ),
    ],
    "flowering": [
        (
            "Switch light schedule to 12/12",
            "Change light timer to 12 on / 12 off to trigger bloom.",
            "high",
            "on_demand",
            5,
            ALL_INDOOR - OUTDOOR_TYPES,
        ),
        (
            "Transition to bloom nutrients",
            "Switch from veg to bloom formula. Increase P and K, reduce N.",
            "high",
            "on_demand",
            15,
            None,
        ),
        (
            "Remove male plants / check for hermies",
            "Inspect all plants for pollen sacs or hermaphrodite traits. Remove immediately.",
            "urgent",
            "on_demand",
            20,
            None,
        ),
        (
            "Adjust reservoir EC for bloom",
            "Increase EC to flower range. Bloom nutrients need higher concentration.",
            "high",
            "on_demand",
            10,
            ACTIVE_HYDRO_TYPES | COCO_TYPES,
        ),
        (
            "Increase coco watering frequency",
            "Coco in flower needs 3-5x daily fertigation. Set timers now.",
            "high",
            "on_demand",
            10,
            {"coco"},
        ),
        (
            "Prepare for outdoor flowering",
            "Natural photoperiod is triggering flower. Ensure no light pollution at night. Install support stakes.",
            "high",
            "on_demand",
            30,
            OUTDOOR_TYPES,
        ),
    ],
    "late_flower": [
        (
            "Begin daily trichome monitoring",
            "Use loupe/microscope daily. Target: mostly cloudy with 20-30% amber.",
            "high",
            "on_demand",
            5,
            None,
        ),
        (
            "Lower temperature for terpene preservation",
            "Drop temps to 65-70°F during dark period. Cooler late flower = better terpenes.",
            "high",
            "on_demand",
            5,
            ALL_INDOOR - OUTDOOR_TYPES,
        ),
        (
            "Reduce humidity to 40-45%",
            "Lower RH to prevent bud rot and encourage resin production.",
            "high",
            "on_demand",
            5,
            None,
        ),
        (
            "Stop heavy defoliation",
            "Late flower: only remove leaves directly blocking bud sites. Let the plant focus on resin.",
            "medium",
            "on_demand",
            5,
            None,
        ),
    ],
    "flush": [
        (
            "Begin plain water flush",
            "Switch to plain pH'd water only. No nutrients. Goal: flush salts for clean result.",
            "urgent",
            "on_demand",
            10,
            None,
        ),
        (
            "Prepare harvest tools and drying space",
            "Gather trimming scissors, set up dark drying room at 60°F / 60% RH.",
            "medium",
            "on_demand",
            60,
            None,
        ),
        (
            "Monitor runoff EC until below 0.3",
            "Keep flushing until runoff EC drops below 0.3.",
            "high",
            "on_demand",
            5,
            ACTIVE_HYDRO_TYPES | COCO_TYPES,
        ),
    ],
    "drying": [
        (
            "Set drying room to 60°F / 60% humidity",
            "Slow dry for 10-14 days. No fans directly on buds. Dark room.",
            "high",
            "on_demand",
            15,
            None,
        ),
        (
            "Check for mold daily during drying",
            "Inspect all branches daily for mold or rot. Remove affected areas immediately.",
            "high",
            "on_demand",
            10,
            None,
        ),
        (
            "Check stem snap test",
            "Bend stems daily. Small stems snap (not bend) = ready for jars.",
            "medium",
            "on_demand",
            3,
            None,
        ),
    ],
    "curing": [
        (
            "Begin jar curing — burp jars daily",
            "Place in mason jars at 58-62% RH. Open for 15 min daily for first 2 weeks.",
            "medium",
            "on_demand",
            10,
            None,
        ),
        (
            "Monitor jar humidity",
            "Target 58-62% RH inside jars. Too high = mold. Too low = add Boveda pack.",
            "medium",
            "on_demand",
            3,
            None,
        ),
    ],
}


# ── Helpers ─────────────────────────────────────────────────────────


async def _get_tenant_owner(session: AsyncSession, tenant_id: UUID) -> UUID | None:
    """Find the owner (admin) user for a tenant."""
    result = await session.execute(
        select(TenantMembership.user_id)
        .where(TenantMembership.tenant_id == tenant_id, TenantMembership.role == TenantRole.admin)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _get_user_timezone(session: AsyncSession, user_id: UUID) -> ZoneInfo:
    """Get user's configured timezone, fallback to UTC."""
    user = await session.get(User, user_id)
    if user and user.preferences:
        tz_str = user.preferences.get("timezone")
        if tz_str:
            try:
                return ZoneInfo(tz_str)
            except (KeyError, ValueError):
                pass
    return ZoneInfo("UTC")


def _get_routine_time(routine: str, tz: ZoneInfo) -> time:
    """Get the local time for a routine."""
    routine_times = {
        "morning": time(7, 0),
        "evening": time(19, 0),
        "weekly": time(9, 0),
        "biweekly": time(9, 0),
        "monthly": time(9, 0),
        "on_demand": time(9, 0),
    }
    return routine_times.get(routine, time(9, 0))


def _local_to_utc(local_time: time, date: datetime, tz: ZoneInfo) -> datetime:
    """Convert a local time on a given date to UTC datetime."""
    local_dt = datetime(
        date.year,
        date.month,
        date.day,
        local_time.hour,
        local_time.minute,
        0,
        tzinfo=tz,
    )
    return local_dt.astimezone(UTC)


async def _task_exists(
    session: AsyncSession,
    tenant_id: UUID,
    category: str,
    grow_cycle_id: UUID,
    due_date: datetime,
) -> bool:
    """Check if an auto-task already exists for this category+grow+date."""
    day_start = due_date.replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(Task.id)
        .where(
            Task.tenant_id == tenant_id,
            Task.category == category,
            Task.grow_cycle_id == grow_cycle_id,
            Task.source == "auto",
            Task.due_date >= day_start,
            Task.due_date < day_start + timedelta(days=1),
        )
        .limit(1)
    )
    return result.scalar_one_or_none() is not None


def _get_grow_automations(grow: GrowCycle) -> set[str]:
    """Extract automation flags from grow settings."""
    settings = grow.settings if hasattr(grow, "settings") and isinstance(grow.settings, dict) else {}
    automations = settings.get("automations", [])
    if isinstance(automations, list):
        return set(automations)
    return set()


def _is_suppressed(category: str, automations: set[str]) -> bool:
    """Check if a task category is suppressed by active automation."""
    for automation, suppressed_categories in AUTOMATION_SUPPRESSIONS.items():
        if automation in automations and category in suppressed_categories:
            return True
    return False


# Rain threshold in mm for skipping watering tasks (0.5 inches ≈ 12.7mm)
RAIN_SKIP_THRESHOLD_MM = 12.7


async def _should_skip_watering(session: AsyncSession, tent_id: UUID | None, due_date: datetime) -> bool:
    """Check if watering should be skipped due to sufficient rainfall forecast.

    Returns True if forecast precipitation exceeds RAIN_SKIP_THRESHOLD_MM
    for the day the task is due.
    """
    if tent_id is None:
        return False

    tent = await session.get(Tent, tent_id)
    if tent is None or tent.environment_type not in ("outdoor", "greenhouse"):
        return False

    # Check latest weather reading with forecast data
    from sqlalchemy import desc

    result = await session.execute(
        select(WeatherReading)
        .where(
            WeatherReading.tent_id == tent_id,
            WeatherReading.forecast.isnot(None),
        )
        .order_by(desc(WeatherReading.recorded_at))
        .limit(1)
    )
    reading = result.scalar_one_or_none()
    if reading is None or not reading.forecast:
        return False

    # Check forecast for the due date
    due_day = due_date.date() if hasattr(due_date, "date") else due_date
    forecast = reading.forecast if isinstance(reading.forecast, list) else []
    for day_forecast in forecast:
        forecast_date = day_forecast.get("date")
        if forecast_date and forecast_date == due_day.isoformat():
            precip_mm = day_forecast.get("precipitation_mm", 0) or 0
            if precip_mm >= RAIN_SKIP_THRESHOLD_MM:
                logger.debug(
                    "Rain skip: %.1fmm forecast for %s (threshold %.1fmm)",
                    precip_mm,
                    due_day,
                    RAIN_SKIP_THRESHOLD_MM,
                )
                return True
    return False


async def _build_flush_fill_description(
    session: AsyncSession,
    grow: GrowCycle,
) -> str:
    """Build a nutrient recipe description for a flush & fill task."""
    lines = ["Drain reservoir completely, rinse, and refill with fresh nutrient solution."]

    vol_row = await session.execute(
        select(func.sum(Bucket.volume_gallons)).where(Bucket.grow_cycle_id == grow.id, Bucket.status == "active")
    )
    total_gallons = vol_row.scalar_one_or_none()

    feed = (
        await session.execute(
            select(FeedingSchedule)
            .where(
                FeedingSchedule.grow_cycle_id == grow.id,
                FeedingSchedule.stage == grow.stage,
            )
            .order_by(FeedingSchedule.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    if total_gallons:
        lines.append(f"\nTotal volume: {total_gallons:.1f} gal")

    if feed:
        lines.append(f"\n--- Nutrients ({feed.name} — {grow.stage}) ---")
        if feed.target_ppm:
            lines.append(f"Target PPM: {feed.target_ppm:.0f}")
        if feed.target_ec:
            lines.append(f"Target EC: {feed.target_ec:.2f}")

        nutrients = feed.nutrients if isinstance(feed.nutrients, list) else []
        for n in nutrients:
            name = n.get("name", "Unknown")
            ml_per_gal = n.get("ml_per_gallon", 0)
            brand = n.get("brand", "")
            strength = n.get("strength_pct")
            if total_gallons and ml_per_gal:
                total_ml = ml_per_gal * total_gallons
                line = f"  • {name}: {ml_per_gal} ml/gal x {total_gallons:.1f} gal = {total_ml:.1f} ml"
            else:
                line = f"  • {name}: {ml_per_gal} ml/gal"
            if brand:
                line += f" ({brand})"
            if strength and strength != 100:
                line += f" @ {strength}%"
            lines.append(line)

        if feed.notes:
            lines.append(f"\nNote: {feed.notes}")
    else:
        lines.append("\nNo feeding schedule found — mix per your usual recipe.")

    lines.append("\n--- Additives ---")
    lines.append("  • Hydroguard: 2 ml/gal")
    if total_gallons:
        lines.append(f"    → {2 * total_gallons:.1f} ml total")
    lines.append("\npH to 5.8-6.2 after mixing. Let solution aerate before adding.")
    return "\n".join(lines)


# ── Main generation logic ───────────────────────────────────────────


async def generate_tasks_for_grow(
    session: AsyncSession,
    grow: GrowCycle,
    horizon_days: int = 7,
) -> int:
    """Generate auto-tasks for a grow cycle up to horizon_days ahead.

    Returns number of tasks created.
    """
    owner_id = await _get_tenant_owner(session, grow.tenant_id)
    if not owner_id:
        logger.warning("No owner found for tenant %s — skipping task generation", grow.tenant_id)
        return 0

    tz = await _get_user_timezone(session, owner_id)
    automations = _get_grow_automations(grow)
    now = datetime.now(UTC)
    created = 0

    # Track which automation verify tasks we've already generated
    automation_verify_generated: set[str] = set()

    for tmpl in TASK_TEMPLATES:
        # Filter by grow type
        if tmpl.grow_types and grow.grow_type not in tmpl.grow_types:
            continue
        # Filter by stage
        if tmpl.stages and grow.stage not in tmpl.stages:
            continue
        # Check automation suppression
        if _is_suppressed(tmpl.category, automations):
            # Generate verification task instead (once per automation type)
            for automation, suppressed in AUTOMATION_SUPPRESSIONS.items():
                if (
                    automation in automations
                    and tmpl.category in suppressed
                    and automation not in automation_verify_generated
                ):
                    verify_tmpl = AUTOMATION_VERIFY_TASKS.get(automation)
                    if verify_tmpl:
                        for day_offset in range(0, horizon_days, verify_tmpl.interval_days):
                            due_date = now + timedelta(days=day_offset)
                            local_time = _get_routine_time(verify_tmpl.routine, tz)
                            due = _local_to_utc(local_time, due_date, tz)
                            cat = f"verify_{automation}"
                            if await _task_exists(session, grow.tenant_id, cat, grow.id, due):
                                continue
                            task = Task(
                                tenant_id=grow.tenant_id,
                                title=verify_tmpl.title,
                                description=verify_tmpl.brief,
                                status="pending",
                                priority=verify_tmpl.priority,
                                category=cat,
                                source="auto",
                                created_by=owner_id,
                                grow_cycle_id=grow.id,
                                tent_id=grow.tent_id,
                                due_date=due,
                                routine=verify_tmpl.routine,
                                estimated_minutes=verify_tmpl.estimated_minutes,
                            )
                            session.add(task)
                            created += 1
                    automation_verify_generated.add(automation)
            continue

        # Generate tasks for each interval within horizon
        for day_offset in range(0, horizon_days, tmpl.interval_days):
            due_date = now + timedelta(days=day_offset)
            local_time = _get_routine_time(tmpl.routine, tz)
            due = _local_to_utc(local_time, due_date, tz)

            if await _task_exists(session, grow.tenant_id, tmpl.category, grow.id, due):
                continue

            # Rain-skip: suppress outdoor watering tasks when rain is forecast
            if (
                tmpl.category == "watering"
                and grow.grow_type in OUTDOOR_TYPES
                and await _should_skip_watering(session, grow.tent_id, due)
            ):
                continue

            # Build description
            if tmpl.category == "flush_and_fill":
                description = await _build_flush_fill_description(session, grow)
            elif tmpl.detail:
                description = f"{tmpl.brief}\n\n---\n{tmpl.detail}"
            else:
                description = tmpl.brief

            task = Task(
                tenant_id=grow.tenant_id,
                title=tmpl.title,
                description=description,
                status="pending",
                priority=tmpl.priority,
                category=tmpl.category,
                source="auto",
                created_by=owner_id,
                grow_cycle_id=grow.id,
                tent_id=grow.tent_id,
                due_date=due,
                routine=tmpl.routine,
                estimated_minutes=tmpl.estimated_minutes,
            )
            session.add(task)
            created += 1

    # ── Strain-based harvest tasks ──────────────────────────────
    if grow.stage in ("flowering", "late_flower", "ripening"):
        milestones = grow.milestones or {}
        flowering_start_str = milestones.get("flowering") or milestones.get("flower")
        if flowering_start_str:
            flowering_start = datetime.fromisoformat(flowering_start_str)
            if flowering_start.tzinfo is None:
                flowering_start = flowering_start.replace(tzinfo=UTC)

            buckets = (
                (
                    await session.execute(
                        select(Bucket).where(
                            Bucket.grow_cycle_id == grow.id, Bucket.status == "active", Bucket.strain_id.isnot(None)
                        )
                    )
                )
                .scalars()
                .all()
            )

            for bucket in buckets:
                strain = bucket.strain or await session.get(Strain, bucket.strain_id)
                if not strain or not strain.flowering_days:
                    continue

                est_harvest = flowering_start + timedelta(days=strain.flowering_days)
                days_remaining = (est_harvest - now).days

                # Flush reminder at 10 days before harvest
                if 0 < days_remaining <= 10:
                    flush_due = est_harvest - timedelta(days=10)
                    flush_due_time = _local_to_utc(_get_routine_time("morning", tz), flush_due, tz)
                    if flush_due_time >= now and not await _task_exists(
                        session, grow.tenant_id, "flush_start", grow.id, flush_due_time
                    ):
                        task = Task(
                            tenant_id=grow.tenant_id,
                            title=f"Start flush — {strain.name}",
                            description=f"{strain.name} ({strain.flowering_days}d flower) estimated harvest in ~{days_remaining} days. Begin plain water flush.",
                            status="pending",
                            priority="high",
                            category="flush_start",
                            source="auto",
                            created_by=owner_id,
                            grow_cycle_id=grow.id,
                            bucket_id=bucket.id,
                            due_date=flush_due_time,
                            routine="on_demand",
                            estimated_minutes=15,
                        )
                        session.add(task)
                        created += 1

                # Harvest day task
                if -1 <= days_remaining <= 1:
                    harvest_due = _local_to_utc(_get_routine_time("morning", tz), est_harvest, tz)
                    if not await _task_exists(session, grow.tenant_id, "harvest", grow.id, harvest_due):
                        task = Task(
                            tenant_id=grow.tenant_id,
                            title=f"Harvest — {strain.name}",
                            description=f"{strain.name} has reached its {strain.flowering_days}-day flowering window. Check trichomes and harvest.",
                            status="pending",
                            priority="urgent",
                            category="harvest",
                            source="auto",
                            created_by=owner_id,
                            grow_cycle_id=grow.id,
                            bucket_id=bucket.id,
                            due_date=harvest_due,
                            routine="on_demand",
                            estimated_minutes=120,
                        )
                        session.add(task)
                        created += 1

    return created


async def generate_all_tasks(session: AsyncSession) -> int:
    """Generate auto-tasks for all active grows."""
    grows = (await session.execute(select(GrowCycle).where(GrowCycle.status == "active"))).scalars().all()

    total = 0
    for grow in grows:
        try:
            count = await generate_tasks_for_grow(session, grow)
            total += count
        except Exception:
            logger.exception("Task generation failed for grow %s", grow.id)

    await session.commit()
    return total


# ── Health eval → tasks ──────────────────────────────────────────────


async def create_tasks_from_health_eval(
    session: AsyncSession,
    grow: GrowCycle,
    score: int | None,
    issues: list[str],
    actions: list[str],
) -> int:
    """Create tasks from health evaluation results."""
    owner_id = await _get_tenant_owner(session, grow.tenant_id)
    if not owner_id:
        return 0

    now = datetime.now(UTC)
    tz = await _get_user_timezone(session, owner_id)
    created = 0

    if score is not None:
        if score < 50:
            priority = "urgent"
        elif score < 70:
            priority = "high"
        elif score < 85:
            priority = "medium"
        else:
            priority = "low"
    else:
        priority = "medium"

    existing_ai_tasks = (
        (
            await session.execute(
                select(Task.title).where(
                    Task.grow_cycle_id == grow.id,
                    Task.source == "ai",
                    Task.category == "health_response",
                    Task.status.in_(["pending", "in_progress"]),
                )
            )
        )
        .scalars()
        .all()
    )
    existing_titles = {t.lower().strip() for t in existing_ai_tasks}

    for action in actions:
        action_lower = action.lower().strip()
        if any(_similar(action_lower, existing) for existing in existing_titles):
            continue

        related_issues = [i for i in issues if _related(action, i)]
        desc_parts = [action]
        if related_issues:
            desc_parts.append("\nRelated issues:")
            for issue in related_issues:
                desc_parts.append(f"  • {issue}")
        if score is not None:
            desc_parts.append(f"\nHealth score: {score}/100")

        due_time = _local_to_utc(_get_routine_time("morning", tz), now + timedelta(days=1 if now.hour >= 9 else 0), tz)

        task = Task(
            tenant_id=grow.tenant_id,
            title=action[:500],
            description="\n".join(desc_parts),
            status="pending",
            priority=priority,
            category="health_response",
            source="ai",
            created_by=owner_id,
            grow_cycle_id=grow.id,
            tent_id=grow.tent_id,
            due_date=due_time,
            routine="on_demand",
            estimated_minutes=10,
        )
        session.add(task)
        existing_titles.add(action_lower)
        created += 1

    if created:
        await session.commit()
        logger.info("Created %d AI tasks from health eval (score=%s) for grow %s", created, score, grow.id)

    return created


def _similar(a: str, b: str) -> bool:
    """Quick similarity check — if first 40 chars match, consider duplicate."""
    return a[:40] == b[:40]


def _related(action: str, issue: str) -> bool:
    """Check if an action is related to an issue by keyword overlap."""
    action_words = set(action.lower().split())
    issue_words = set(issue.lower().split())
    common = action_words & issue_words - {"the", "a", "an", "to", "is", "in", "of", "for", "and", "or"}
    return len(common) >= 2


# ── Alert → urgent task ─────────────────────────────────────────────


async def create_task_from_alert(
    session: AsyncSession,
    tenant_id: UUID,
    grow_cycle_id: UUID | None,
    tent_id: UUID | None,
    severity: str,
    alert_type: str,
    message: str,
    sensor_value: float | None = None,
) -> Task | None:
    """Create an urgent task from an alert event."""
    owner_id = await _get_tenant_owner(session, tenant_id)
    if not owner_id:
        return None

    now = datetime.now(UTC)

    existing = (
        await session.execute(
            select(Task.id)
            .where(
                Task.tenant_id == tenant_id,
                Task.category == "alert_response",
                Task.source == "auto",
                Task.status.in_(["pending", "in_progress"]),
                Task.title.contains(alert_type),
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if existing:
        return None

    priority = "urgent" if severity == "critical" else "high"
    due = now if severity == "critical" else now + timedelta(hours=1)

    desc = message
    if sensor_value is not None:
        desc += f"\n\nSensor reading: {sensor_value}"

    task = Task(
        tenant_id=tenant_id,
        title=f"ALERT: {message[:480]}",
        description=desc,
        status="pending",
        priority=priority,
        category="alert_response",
        source="auto",
        created_by=owner_id,
        grow_cycle_id=grow_cycle_id,
        tent_id=tent_id,
        due_date=due,
        routine="on_demand",
        estimated_minutes=10,
    )
    session.add(task)
    await session.commit()
    return task


# ── Stage transition → preparation tasks ────────────────────────────


async def create_stage_transition_tasks(
    session: AsyncSession,
    grow: GrowCycle,
    new_stage: str,
) -> int:
    """Create preparation tasks when a grow transitions to a new stage."""
    tasks_for_stage = STAGE_TRANSITION_TASKS.get(new_stage, [])
    if not tasks_for_stage:
        return 0

    owner_id = await _get_tenant_owner(session, grow.tenant_id)
    if not owner_id:
        return 0

    tz = await _get_user_timezone(session, owner_id)
    now = datetime.now(UTC)
    created = 0

    for title, brief, priority, routine, est_minutes, grow_types in tasks_for_stage:
        if grow_types and grow.grow_type not in grow_types:
            continue

        existing = (
            await session.execute(
                select(Task.id)
                .where(
                    Task.grow_cycle_id == grow.id,
                    Task.title == title,
                    Task.status.in_(["pending", "in_progress"]),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if existing:
            continue

        due_time = _local_to_utc(_get_routine_time(routine, tz), now + timedelta(days=1 if now.hour >= 9 else 0), tz)

        task = Task(
            tenant_id=grow.tenant_id,
            title=title,
            description=brief,
            status="pending",
            priority=priority,
            category="stage_transition",
            source="auto",
            created_by=owner_id,
            grow_cycle_id=grow.id,
            tent_id=grow.tent_id,
            due_date=due_time,
            routine=routine,
            estimated_minutes=est_minutes,
        )
        session.add(task)
        created += 1

    if created:
        await session.commit()
        logger.info("Created %d stage-transition tasks for grow %s → %s", created, grow.id, new_stage)

    return created


# ── Journal event → follow-up tasks ─────────────────────────────────


async def create_journal_followup_tasks(
    session: AsyncSession,
    tenant_id: UUID,
    grow_cycle_id: UUID | None,
    bucket_id: UUID,
    event_type: str,
    content: str | None = None,
    payload: dict | None = None,
) -> int:
    """Create follow-up tasks after journal events."""
    owner_id = await _get_tenant_owner(session, tenant_id)
    if not owner_id:
        return 0

    tz = await _get_user_timezone(session, owner_id)
    now = datetime.now(UTC)
    created = 0
    followups: list[tuple[str, str, str, int, int]] = []  # (title, desc, priority, days_offset, est_minutes)

    if event_type == "feeding":
        followups.append(
            (
                "Verify pH & EC stability after feeding",
                "Check pH and EC 24h after feeding to ensure no drift.",
                "medium",
                1,
                3,
            )
        )
        followups.append(
            (
                "Check for nutrient burn (leaf tip browning)",
                "Inspect leaf tips for browning or curling — signs of overfeeding.",
                "medium",
                2,
                3,
            )
        )

    elif event_type == "water_change":
        followups.append(
            (
                "Monitor pH after reservoir change",
                "Fresh water causes pH drift in the first 12-24h. Check and adjust.",
                "medium",
                1,
                3,
            )
        )

    elif event_type in ("training", "topping", "defoliation"):
        recovery_days = 3
        if payload and isinstance(payload, dict):
            recovery_days = payload.get("recovery_expected_days", 3)
        followups.append(
            (
                f"Check recovery from {event_type}",
                f"Inspect {recovery_days} days post-{event_type}. Look for healthy new growth.",
                "medium",
                recovery_days,
                5,
            )
        )

    elif event_type == "transplant":
        followups.append(
            (
                "Monitor for transplant shock",
                "Watch for drooping/yellowing in 48h. Keep humidity high and light low if stressed.",
                "high",
                2,
                5,
            )
        )

    for title, desc, priority, days, est_minutes in followups:
        due = now + timedelta(days=days)
        due_time = _local_to_utc(_get_routine_time("morning", tz), due, tz)

        existing = (
            await session.execute(
                select(Task.id)
                .where(
                    Task.tenant_id == tenant_id,
                    Task.title == title,
                    Task.status.in_(["pending", "in_progress"]),
                    Task.due_date >= due_time - timedelta(days=1),
                    Task.due_date <= due_time + timedelta(days=1),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if existing:
            continue

        task = Task(
            tenant_id=tenant_id,
            title=title,
            description=desc,
            status="pending",
            priority=priority,
            category="followup",
            source="auto",
            created_by=owner_id,
            grow_cycle_id=grow_cycle_id,
            bucket_id=bucket_id,
            due_date=due_time,
            routine="on_demand",
            estimated_minutes=est_minutes,
        )
        session.add(task)
        created += 1

    if created:
        await session.commit()

    return created
