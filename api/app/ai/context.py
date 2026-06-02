"""AI context builder — assembles grow-type-aware context for Ollama / Gemini prompts."""

from __future__ import annotations

import logging
from datetime import UTC

logger = logging.getLogger(__name__)


async def get_grow_type_profile_from_db(grow_type: str, session) -> dict | None:
    """Look up grow type profile from DB."""
    try:
        from app.config_management.service.grow_types import get_profile

        return await get_profile(session, grow_type)
    except Exception:
        logger.debug("DB profile lookup failed for %s", grow_type)
    return None


async def get_grow_type_config_from_db(grow_type: str, session) -> dict | None:
    """Look up the full config (with extended_config) from DB."""
    try:
        from app.config_management.service.grow_types import get_full_config

        return await get_full_config(session, grow_type)
    except Exception:
        logger.debug("DB config lookup failed for %s", grow_type)
    return None


# ── Helpers ──────────────────────────────────────────────────────────


def _fmt_sensors(sensors: dict) -> str:
    """Format a bucket's sensor dict as readable lines."""
    skip = {"recorded_at"}
    lines = []
    for k, v in sensors.items():
        if k in skip or v is None:
            continue
        label = k.replace("_", " ").replace("pct", "%").title()
        lines.append(f"  {label}: {v}")
    return "\n".join(lines)


def _fmt_bucket_list(buckets: list[dict]) -> str:
    parts = []
    for b in buckets:
        desc = f"  Position {b['position']}"
        if b.get("label"):
            desc += f' "{b["label"]}"'
        if b.get("strain_name"):
            desc += f" — strain: {b['strain_name']}"
        if b.get("volume_gallons"):
            desc += f", {b['volume_gallons']} gal"
        desc += f", stage: {b.get('growth_stage', '?')}, status: {b.get('status', '?')}"
        # Include strain profile if available
        sp = b.get("strain_profile")
        if sp:
            if sp.get("genetics"):
                desc += f"\n    Genetics: {sp['genetics']}"
            if sp.get("flowering_days"):
                desc += f"\n    Flowering days: {sp['flowering_days']}"
            if sp.get("thc_pct"):
                desc += f"\n    THC: {sp['thc_pct']}%"
            if sp.get("cbd_pct"):
                desc += f"\n    CBD: {sp['cbd_pct']}%"
            if sp.get("terpene_profile"):
                terps = ", ".join(f"{k}: {v}" for k, v in sp["terpene_profile"].items())
                desc += f"\n    Terpenes: {terps}"
            if sp.get("notes"):
                desc += f"\n    Strain notes: {sp['notes']}"
        parts.append(desc)
    return "\n".join(parts)


def _fmt_feeding(schedules: list[dict], current_stage: str, started_at: str | None = None) -> str:
    week = None
    if started_at:
        week = _current_grow_week({"started_at": started_at})
    parts = []
    for s in schedules:
        if week is not None and _week_matches_schedule(week, s["name"]):
            marker = " ← ACTIVE"
        elif s["stage"] == current_stage:
            marker = ""
        else:
            marker = ""
        line = f"  [{s['stage']}{marker}] {s['name']}"
        if s.get("target_ppm"):
            line += f" | Target PPM: {s['target_ppm']}"
        if s.get("target_ec"):
            line += f" | Target EC: {s['target_ec']}"
        if s.get("nutrients"):
            nuts = s["nutrients"]
            if isinstance(nuts, list):
                for n in nuts:
                    name = n.get("name", "?")
                    amt = n.get("ml_per_gallon", "?")
                    line += f"\n    - {name}: {amt}ml/gal"
        if s.get("notes"):
            line += f"\n    Notes: {s['notes']}"
        parts.append(line)
    return "\n".join(parts)


def _fmt_doses(profiles: list[dict]) -> str:
    return "\n".join(
        f"  {d['name']} ({d['dose_type']}): {d['dose_ml']}ml" + (" [enabled]" if d.get("enabled") else " [disabled]")
        for d in profiles
    )


def _fmt_journal(entries: list[dict]) -> str:
    parts = []
    for j in entries:
        date = j["created_at"][:10] if j.get("created_at") else "?"
        content = j.get("content") or ""
        line = f"  {date} [{j['event_type']}] {content}"
        # Include payload data (pH readings, EC values, nutrient amounts, etc.)
        payload = j.get("payload")
        if payload and isinstance(payload, dict):
            details = ", ".join(f"{k}: {v}" for k, v in payload.items() if v is not None and k != "bucket_id")
            if details:
                line += f"\n    Data: {details}"
            else:
                line += "\n    ⚠️ No measurement data logged"
        elif j["event_type"] in ("water_change", "reservoir_change", "feeding", "nutrient_adjustment"):
            line += "\n    ⚠️ No measurement data logged (missing pH, EC, volume, nutrients)"
        parts.append(line)
    return "\n".join(parts)


def _fmt_trends(trends: dict) -> str:
    lines = [f"  Period: {trends.get('period_hours', 24)}h ({trends.get('reading_count', 0)} readings)"]
    for field in (
        "ph",
        "ec",
        "ppm",
        "water_temp_f",
        "dissolved_oxygen",
        "water_level_pct",
        "soil_moisture",
        "soil_temp",
        "runoff_ph",
        "runoff_ec",
        "flow_rate",
        "mist_pressure",
    ):
        avg = trends.get(f"{field}_avg")
        if avg is not None:
            label = field.replace("_", " ").title()
            lo = trends.get(f"{field}_min")
            hi = trends.get(f"{field}_max")
            lines.append(f"  {label}: avg {avg}, range {lo}-{hi}")
    return "\n".join(lines)


def _fmt_prev_eval(prev: dict, *, filter_feeding: bool = False) -> str:
    parts = [
        f"  Date: {prev.get('created_at', '?')}",
        f"  Score: {prev.get('score', '?')}/100 ({prev.get('source', 'manual')})",
    ]
    if prev.get("issues"):
        issues = prev["issues"]
        if filter_feeding:
            issues = [i for i in issues if "schedule" not in i.lower() and "feeding" not in i.lower()]
        if issues:
            parts.append("  Issues:")
            for issue in issues:
                parts.append(f"    - {issue}")
    if prev.get("actions"):
        actions = prev["actions"]
        if filter_feeding:
            actions = [a for a in actions if "schedule" not in a.lower() and "feeding" not in a.lower()]
        if actions:
            parts.append("  Actions recommended:")
            for action in actions:
                parts.append(f"    - {action}")
    return "\n".join(parts)


def _fmt_tent_equipment(equipment: list[dict] | None) -> str:
    """Format a tent's equipment list as readable lines."""
    if not equipment:
        return ""
    lines = []
    for item in equipment:
        etype = item.get("type", "unknown").replace("_", " ").title()
        qty = item.get("quantity", 1)
        desc = f"  {etype}"
        if qty > 1:
            desc += f" (x{qty})"
        brand = item.get("brand")
        model = item.get("model")
        if brand:
            desc += f" — {brand}"
        if model:
            desc += f" {model}"
        specs = item.get("specs")
        if specs:
            desc += f" [{specs}]"
        lines.append(desc)
    return "\n".join(lines)


def _fmt_settings(settings: dict | None, grow_type: str) -> str:
    """Format grow settings into human-readable lines for AI context.

    Maps raw setting keys to descriptive labels so the AI understands
    the grower's exact setup — equipment, configuration, targets, etc.
    """
    if not settings:
        return ""
    labels = {
        # Reservoir / Container
        "reservoir_liters": "Reservoir Size",
        "container_size_liters": "Container Size",
        "bucket_type": "Bucket Type",
        "container_type": "Container Type",
        "pot_type": "Pot Type",
        "pot_size_gal": "Pot Size",
        "tray_size": "Tray Size",
        "slab_size": "Slab/Cube Size",
        "connected_sites": "Connected Sites",
        "plot_size_sqft": "Plot Size",
        "plot_type": "Plot Type",
        "container_color": "Container Color",
        "mobility": "Container Mobility",
        "saucer": "Saucer/Drip Tray",
        # Equipment / Hardware
        "air_pump_brand": "Air Pump",
        "air_pump_watts": "Air Pump Wattage",
        "air_stones": "Air Stone Type",
        "circulation_pump": "Circulation Pump",
        "return_line_size": "Return Line Size",
        "pump_brand": "Pump Brand/Model",
        "water_chiller": "Water Chiller",
        "nozzle_count": "Nozzle Count",
        "emitter_count": "Emitter Count",
        "channel_count": "Channel Count",
        "channel_length": "Channel Length",
        "scale_for_weight": "Weight Tracking Scale",
        # Media / Soil
        "media_type": "Growing Media",
        "soil_mix": "Soil Mix/Brand",
        "soil_type": "Soil Type",
        "coco_brand": "Coco Brand",
        "perlite_ratio": "Perlite Mix Ratio",
        "organic_or_synthetic": "Nutrient Approach",
        "amendments": "Amendments",
        "beneficial_microbes": "Beneficial Microbes",
        "compost_tea": "Compost Tea",
        "mulch_cover": "Mulch/Cover Crop",
        "slab_covered": "Slab Covered",
        # Watering / Irrigation
        "watering_method": "Watering Method",
        "watering_schedule": "Watering Schedule",
        "fertigation_frequency": "Fertigation Frequency",
        "drip_frequency": "Drip Frequency",
        "drip_duration_sec": "Drip Duration (sec)",
        "water_change_days": "Reservoir Change Interval (days)",
        "top_feed": "Top Feed (Seedling)",
        "recirculating": "Recirculating",
        "irrigation": "Irrigation Method",
        "flood_interval_min": "Flood Interval (min)",
        "flood_duration_min": "Flood Duration (min)",
        "spray_interval_sec": "Spray Interval (sec)",
        "spray_duration_sec": "Spray Duration (sec)",
        "nozzle_psi": "Nozzle Pressure (PSI)",
        "flow_rate_lph": "Flow Rate (L/hr)",
        "refill_strategy": "Refill Strategy",
        "shots_per_day": "Irrigation Shots/Day",
        "shot_volume_ml": "Shot Volume (ml)",
        "target_dryback_pct": "Target Dry-back %",
        # Runoff / Targets
        "target_ph": "Target pH",
        "target_ec": "Target EC (mS/cm)",
        "target_runoff_pct": "Target Runoff %",
        "runoff_target_pct": "Target Runoff %",
        "target_vpd": "Target VPD (kPa)",
        # Light
        "light_type": "Light Type",
        "light_brand": "Light Brand/Model",
        "light_wattage": "Light Wattage (W)",
        "light_schedule": "Light Schedule",
        "light_height_in": "Light Height (in)",
        # Nutrients / Water Source
        "nutrient_line": "Nutrient Brand/Line",
        "calmag_brand": "CalMag Product",
        "ph_up_product": "pH Up Product",
        "ph_down_product": "pH Down Product",
        "water_source": "Water Source",
        "water_source_ppm": "Source Water PPM",
        # Environment
        "ventilation": "Ventilation",
        "exhaust_fan": "Exhaust Fan",
        "carbon_filter": "Carbon Filter",
        "humidifier_dehumidifier": "Humidity Control",
        "controller_system": "Controller/Automation System",
        # Outdoor
        "sun_exposure": "Sun Exposure",
        "companion_plants": "Companion Plants",
        "pest_deterrent": "Pest Deterrent",
        "frost_protection": "Frost Protection",
        "hardiness_zone": "USDA Hardiness Zone",
        "light_proof": "Light-Proof Container",
    }
    lines = []
    for key, value in settings.items():
        if value is None or value == "":
            continue
        label = labels.get(key, key.replace("_", " ").title())
        lines.append(f"  {label}: {value}")
    return "\n".join(lines)


# ── Chat context ─────────────────────────────────────────────────────


async def build_chat_context(
    grow_data: dict,
    session=None,
) -> str:
    """Build a comprehensive system prompt for Ollama chat using all available data."""
    grow_type = grow_data.get("grow_type", "")
    profile = None
    if session and grow_type:
        profile = await get_grow_type_profile_from_db(grow_type, session)
    if not profile:
        return "You are Tendril, an AI grow assistant."

    # ai_context_prompt is a top-level DB column; extended_config fields are merged in
    ai_prompt = profile.get("ai_context_prompt") or ""
    parts = [
        f"You are Tendril, an expert cannabis cultivation AI — think master grower with 20+ years of "
        f"experience across every grow style. You specialize in {profile['name']} cannabis cultivation "
        f"with deep expertise in cannabinoid and terpene production, plant physiology, nutrient chemistry, "
        f"environmental optimization, phenotype expression, and strain-specific growing techniques.\n\n"
        f"You speak like a knowledgeable grower — direct, practical, and passionate about growing top-shelf "
        f"cannabis. You understand the plant at a molecular level: how VPD drives transpiration and nutrient "
        f"uptake, how light spectrum affects cannabinoid synthesis, how stress hormones trigger resin production, "
        f"and how microbial interactions in the rhizosphere affect terpene expression.",
        f"Grow method context: {ai_prompt}",
        f"Feeding approach: {profile.get('feeding_approach', '')}",
        f"Nutrient strength: {profile.get('nutrient_strength', '')}",
    ]
    ph_range = profile.get("ph_range")
    if ph_range:
        parts.append(f"pH range: {ph_range.get('min', '?')}-{ph_range.get('max', '?')}")
    common_problems = profile.get("common_problems", [])
    if common_problems:
        parts.append(f"Common problems: {', '.join(common_problems)}")
    health_questions = profile.get("health_check_questions", [])
    if health_questions:
        parts.append(f"Health check questions to consider: {', '.join(health_questions)}")

    # Add terminology so the AI uses the right words for this grow type
    terminology = profile.get("terminology", {})
    if terminology:
        term_str = ", ".join(f"{k}='{v}'" for k, v in terminology.items())
        parts.append(f"Use these terms when talking to the grower: {term_str}")

    # Grow details
    tent_size = grow_data.get("tent_size")
    tent_line = f"  Tent: {grow_data.get('tent_name', '?')}"
    if tent_size:
        tent_line += f" ({tent_size})"
    tent_line += f" [{grow_data.get('environment_type', 'indoor')}]"
    parts.append(
        f"\n=== Active Grow ===\n"
        f"  Name: {grow_data.get('grow_name', '?')}\n"
        f"  Type: {profile['name']}\n"
        f"  Stage: {grow_data.get('stage', '?')}\n"
        f"  Status: {grow_data.get('status', '?')}\n"
        f"  Started: {grow_data.get('started_at', '?')}\n" + tent_line
    )

    # Tent equipment (physical hardware attached to the tent)
    tent_equip_text = _fmt_tent_equipment(grow_data.get("tent_equipment"))
    if tent_equip_text:
        parts.append(
            "\n=== Tent Equipment ===\n" + tent_equip_text + "\n\nThis is the physical hardware in the grower's tent. "
            "Reference specific equipment by brand/model when giving advice "
            "(e.g., light height recommendations for their exact light, fan speed settings for their controller)."
        )
    tent_notes = grow_data.get("tent_notes")
    if tent_notes:
        parts.append(f"  Tent Notes: {tent_notes}")

    # Equipment & Setup (from grow settings)
    settings = grow_data.get("settings")
    settings_text = _fmt_settings(settings, grow_data.get("grow_type", ""))
    if settings_text:
        parts.append(
            "\n=== Grower's Equipment & Setup ===\n"
            + settings_text
            + "\n\nIMPORTANT: Use this equipment info to tailor ALL advice. "
            "Reference the user's specific gear by name when relevant "
            "(e.g., 'With your Spider Farmer SF-4000, I'd set it to...' or "
            "'Your AC Infinity Controller 69 can automate VPD targeting...'). "
            "If the user has a controller system, suggest how to leverage its features."
        )

    # Grower's notes
    notes = grow_data.get("notes")
    if notes:
        parts.append(f"\n=== Grower's Notes ===\n  {notes}")

    # Scale & strain-type context from profile's extended_config
    # (scale_tiers, strain_adjustments already merged into profile from extended_config)
    if profile.get("scale_tiers"):
        buckets_list = grow_data.get("buckets") or []
        bucket_count = len(buckets_list)
        # Infer scale from bucket count
        if bucket_count >= 100:
            scale_id = "warehouse"
        elif bucket_count >= 25:
            scale_id = "commercial_room"
        elif bucket_count >= 9:
            scale_id = "multi_tent"
        elif bucket_count >= 2:
            scale_id = "small_tent"
        else:
            scale_id = "solo"
        scale_tiers = profile.get("scale_tiers", [])
        scale_info = next((t for t in scale_tiers if t["id"] == scale_id), None)
        if scale_info:
            parts.append(
                f"\n=== Scale Context ===\n"
                f"  Scale tier: {scale_info['name']} ({bucket_count} plants)\n"
                f"  Automation level: {scale_info.get('automation_level', 'unknown')}\n"
                f"  Notes: {scale_info.get('notes', '')}"
            )

        # Detect strain type (auto vs photo) from bucket strain profiles
        strain_types_seen = set()
        for b in buckets_list:
            sp = b.get("strain_profile") or {}
            if sp.get("strain_type"):
                strain_types_seen.add(sp["strain_type"])
            elif sp.get("autoflower") is True:
                strain_types_seen.add("autoflower")
            elif sp.get("flowering_type"):
                strain_types_seen.add(sp["flowering_type"])
        if strain_types_seen:
            strain_adj = profile.get("strain_adjustments", {})
            for st in strain_types_seen:
                adj = strain_adj.get(st)
                if adj:
                    parts.append(
                        f"\n=== Strain Type: {adj.get('name', st)} ===\n"
                        f"  {adj.get('description', '')}\n"
                        f"  Nutrient strength: {adj.get('nutrient_strength', 'standard')}"
                    )

    # Buckets
    buckets = grow_data.get("buckets") or []
    if buckets:
        parts.append(f"\n=== Plants/Buckets ({len(buckets)}) ===\n" + _fmt_bucket_list(buckets))

    # Latest sensors
    bucket_sensors = grow_data.get("bucket_sensors") or {}
    if bucket_sensors:
        sensor_section = "\n=== Latest Sensor Readings ==="
        for pos, readings in bucket_sensors.items():
            sensor_section += f"\n  Bucket {pos}:\n" + _fmt_sensors(readings)
        parts.append(sensor_section)

    # Tent ambient (shared across all buckets)
    tent_ambient = grow_data.get("tent_ambient")
    if tent_ambient:
        ambient_lines = []
        if tent_ambient.get("ambient_temp_f") is not None:
            ambient_lines.append(f"  Ambient Temp: {tent_ambient['ambient_temp_f']}°F")
        if tent_ambient.get("ambient_humidity") is not None:
            ambient_lines.append(f"  Ambient Humidity: {tent_ambient['ambient_humidity']}%")
        if tent_ambient.get("recorded_at"):
            ambient_lines.append(f"  Recorded: {tent_ambient['recorded_at']}")
        if ambient_lines:
            parts.append("\n=== Tent Environment (shared) ===\n" + "\n".join(ambient_lines))

    # Sensor trends
    trends = grow_data.get("sensor_trends")
    if trends:
        parts.append("\n=== Bucket Sensor Trends ===\n" + _fmt_trends(trends))

    # Ambient trends (tent-level)
    ambient_trends = grow_data.get("ambient_trends")
    if ambient_trends:
        ambient_trend_lines = [
            f"  Period: {ambient_trends.get('period_hours', 24)}h ({ambient_trends.get('reading_count', 0)} readings)"
        ]
        for field in ("ambient_temp_f", "ambient_humidity"):
            avg = ambient_trends.get(f"{field}_avg")
            if avg is not None:
                label = field.replace("_", " ").title()
                lo = ambient_trends.get(f"{field}_min")
                hi = ambient_trends.get(f"{field}_max")
                ambient_trend_lines.append(f"  {label}: avg {avg}, range {lo}–{hi}")
        parts.append("\n=== Tent Ambient Trends ===\n" + "\n".join(ambient_trend_lines))

    # Feeding schedules
    feeds = grow_data.get("feeding_schedules") or []
    if feeds:
        parts.append(
            "\n=== Feeding Schedules ===\n"
            + _fmt_feeding(feeds, grow_data.get("stage", ""), grow_data.get("started_at"))
            + "\n\nIMPORTANT: These schedules are the FULL feed chart for the entire grow cycle. "
            "Only the schedule marked ← ACTIVE is what the grower should follow right now. "
            "Do NOT tell the grower they are using the wrong schedule — the other entries are future/past phases, not mistakes."
        )

    # Dose profiles
    doses = grow_data.get("dose_profiles") or []
    if doses:
        parts.append("\n=== Dose Profiles ===\n" + _fmt_doses(doses))

    # Journal
    journals = grow_data.get("journal_entries") or []
    if journals:
        parts.append("\n=== Recent Journal Entries ===\n" + _fmt_journal(journals))

    # Previous health eval
    prev = grow_data.get("previous_eval")
    if prev:
        parts.append("\n=== Last Health Evaluation ===\n" + _fmt_prev_eval(prev, filter_feeding=True))

    # Weather
    weather = grow_data.get("weather")
    if weather:
        w_lines = "\n".join(f"  {k}: {v}" for k, v in weather.items() if v is not None)
        parts.append(f"\n=== Weather ===\n{w_lines}")

    # Milestones
    milestones = grow_data.get("milestones")
    if milestones:
        m_lines = "\n".join(f"  {k}: {v}" for k, v in milestones.items() if v)
        parts.append(f"\n=== Milestones ===\n{m_lines}")

    # Pending tasks
    pending_tasks = grow_data.get("pending_tasks") or []
    if pending_tasks:
        task_lines = []
        for t in pending_tasks:
            line = f"  [{t.get('priority', 'medium')}] {t['title']}"
            if t.get("due_date"):
                line += f" (due: {t['due_date'][:10]})"
            if t.get("category"):
                line += f" [{t['category']}]"
            if t.get("source") == "auto":
                line += " [auto]"
            task_lines.append(line)
        parts.append("\n=== Pending Tasks ===\n" + "\n".join(task_lines))

    # Recently completed tasks
    completed_tasks = grow_data.get("completed_tasks") or []
    if completed_tasks:
        done_lines = [f"  ✓ {t['title']} ({t.get('completed_at', '?')[:10]})" for t in completed_tasks]
        parts.append("\n=== Recently Completed Tasks (7d) ===\n" + "\n".join(done_lines))

    parts.extend(
        [
            "\nYou can update the user's grow, buckets, feeding schedules, tent, and journal entries using the available tools.",
            "Respond concisely and practically. Focus on actionable advice grounded in cannabis science.",
            "Use the grow-type terminology the user would expect. Talk like a grower, not a textbook.",
            "\n=== CORE PHILOSOPHY: Craft Cannabis — Quality Is Everything ===",
            "This grower is here to produce the BEST flower possible — top-shelf, dispensary-grade cannabis.",
            "Every recommendation you make should optimize for quality over yield:",
            "- Terpene preservation is paramount: lower temps (60-68°F) in final 2 weeks, UV-B exposure in late flower, gentle air movement to protect trichome heads.",
            "- Proper flush/fade timing: allow natural senescence for clean, smooth smoke. A beautiful fade is a sign of a dialed grow.",
            "- Trichome maturity over speed: guide toward the grower's desired effect (clear = energetic, milky = peak THC, amber = sedative/CBN). Never rush harvest.",
            "- Stress management: healthy, unstressed plants channel energy into resin production. Avoid late-flower defoliation. Low-stress training (LST) over high-stress (HST) unless the grower is experienced.",
            "- Optimal harvest windows: track pistil recession (70%+), trichome cloudiness, and swollen calyxes. Patience = potency + flavor.",
            "- VPD management is key: dial VPD for maximum transpiration in veg (0.8-1.2 kPa), moderate in early flower (1.0-1.4 kPa), and lower in late flower (0.8-1.0 kPa) to protect volatiles.",
            "- Day/night temperature differential (DIF): 10-15°F drop at night in flower triggers anthocyanin production and enhances terpene retention.",
            "- Light spectrum matters: full spectrum with red emphasis in flower drives cannabinoid synthesis; far-red initiates shade avoidance for stretch; UV-B in final weeks boosts THC.",
            "- When in doubt, prioritize plant health → resin production → bag appeal → yield (in that order).",
            "\n=== Cannabis-Specific Expertise ===",
            "You understand:",
            "- Cannabinoid biosynthesis: CBGA → THC/CBD/CBC pathways, and how environment affects ratios.",
            "- Terpene science: monoterpenes (myrcene, limonene, pinene) vs sesquiterpenes (caryophyllene, humulene), their boiling points, and how to preserve them.",
            "- The entourage effect and why full-spectrum terpene profiles matter more than THC percentage alone.",
            "- Photoperiodism: critical dark period for flowering initiation, light leak sensitivity, and DLI optimization.",
            "- Cannabis nutrient demands by stage: high N in veg, P/K ramp in flower, calcium/magnesium needs under LED, silica for stem strength.",
            "- Training techniques: LST, HST, mainlining, manifolding, ScrOG, SOG, lollipopping, defoliation timing.",
            "- IPM (Integrated Pest Management): preventative sprays (neem, spinosad, BT), beneficial insects (ladybugs, predator mites), and organic solutions.",
            "- Drying & curing principles: 60°F/60% RH slow dry (10-14 days), proper cure in jars (burping schedule), and how this affects final terp/cannabinoid profile.",
            "\n=== Strain-Aware Guidelines ===",
            "When strain profile data is available for a bucket:",
            "- Use flowering_days to estimate harvest window — but always verify with trichome checks. Breeder times are usually optimistic by 1-2 weeks.",
            "- Reference terpene profiles for environment tuning (e.g., if dominant terp is myrcene, keep late-flower temps below 70°F to prevent volatilization).",
            "- Adjust pH/EC based on genetics: sativas generally prefer lighter feeds, indicas can handle heavier EC. Hybrids vary — watch the plant.",
            "- Note strain-specific traits: purple coloring on certain genetics (e.g., Purple Punch, GDP) is NORMAL anthocyanin expression, NOT a deficiency.",
            "- Factor in THC/CBD ratios when advising on harvest timing (more amber = more CBN/sedative, clear/milky = peak THC/energetic).",
            "- Recognize phenotype variation: same strain can express differently — always go by what the plant is telling you, not just the breeder's description.",
            "\n=== ACCURACY & HONESTY — NON-NEGOTIABLE ===",
            "You MUST be 100% accurate and honest in every response. This grower's plants and harvest depend on correct information.",
            "- Only state facts you are confident are true. If you are not sure, say 'I'm not sure' or 'I don't know' — that is always an acceptable answer.",
            "- Never guess, fabricate, or hallucinate information. Wrong advice can kill plants or ruin a harvest.",
            "- Base ALL recommendations on the actual sensor data, equipment, and settings provided above. Do not assume data that isn't there.",
            "- If sensor data is missing or stale, explicitly say so — don't fill in the gaps with assumptions.",
            "- If a question is outside your expertise, say so honestly rather than giving a potentially wrong answer.",
            "- When citing numbers (pH, EC, PPM, temperatures), use the exact values from the provided data.",
            "- Distinguish between established cannabis science and personal opinion/bro-science. Label opinions as such.",
        ]
    )

    return "\n".join(parts)


# ── Health-check prompt (Gemini) ─────────────────────────────────────


async def build_health_check_prompt(
    grow_data: dict,
    observations: dict[str, str],
    session=None,
) -> list[dict]:
    """Build messages for a Gemini-powered health check using ALL available data."""
    grow_type = grow_data.get("grow_type", "")
    stage = grow_data.get("stage", "?")
    profile = await get_grow_type_profile_from_db(grow_type, session) if session else None
    type_name = profile["name"] if profile else grow_type
    context = profile.get("ai_context_prompt", "") if profile else ""
    common = ", ".join(profile.get("common_problems", [])) if profile else ""
    ph_range = profile.get("ph_range", {}) if profile else {}
    feeding_approach = profile.get("feeding_approach", "") if profile else ""

    has_camera = grow_data.get("camera_image") is not None

    system = (
        f"You are an expert cannabis plant health diagnostician with 20+ years of cultivation experience. "
        f"You work for Tendril, a cannabis cultivation platform. "
        f"You specialize in {type_name} cannabis grows and can identify issues from sensor data, visual symptoms, "
        f"and environmental conditions with the precision of a master grower. "
        f"{context} "
        f"Feeding approach: {feeding_approach}. "
        f"The plant is in the **{stage}** stage. "
        f"Optimal pH range: {ph_range.get('min', '?')}-{ph_range.get('max', '?')}. "
        f"Common problems for this grow type: {common}.\n\n"
    )

    # Include health check questions for this grow type
    health_questions = profile.get("health_check_questions", []) if profile else []
    if health_questions:
        system += "Key diagnostic questions for this grow type:\n"
        for q in health_questions:
            system += f"- {q}\n"
        system += "\n"

    system += (
        "CORE PHILOSOPHY: Craft cannabis — quality is everything. The grower wants top-shelf flower with "
        "maximum terpene expression, proper cannabinoid maturity, and pristine bag appeal. "
        "All recommendations should prioritize terpene preservation (low late-flower temps, gentle airflow), "
        "proper flush/fade timing (beautiful senescence = clean smoke), "
        "trichome maturity (milky/amber ratio for desired effect), "
        "stress reduction (healthy plants = more resin), and optimal harvest windows (patience = potency). "
        "Optimize environment for resin production and terpene retention — not maximum biomass.\n\n"
    )

    if has_camera:
        system += (
            "A live camera image from the grow space is attached. Analyze the image like a master grower would:\n"
            "- Leaf color and health: nitrogen toxicity (dark/clawing), deficiencies (yellowing patterns — interveinal vs tip burn vs uniform), light stress (bleaching, taco-ing)\n"
            "- Trichome development if visible: clear (immature), milky/cloudy (peak THC), amber (degrading to CBN)\n"
            "- Bud structure and development: foxtailing, airy buds, proper calyx swelling\n"
            "- Root health if visible: bright white = healthy, brown/slimy = root rot, tan = pythium\n"
            "- Canopy health: even canopy, light penetration, signs of over/under-defoliation\n"
            "- Pest/pathogen indicators: thrips damage (silver spots), spider mites (stippling), PM (white powder), bud rot (grey/brown spots on buds)\n"
            "- Overall vigor and internode spacing (too stretchy = not enough light, too compact = too much light or genetics)\n\n"
        )

    system += (
        "Perform the MOST thorough health evaluation possible — think like a master grower doing a full plant inspection. "
        "Analyze ALL provided data — observations, sensor readings, sensor trends, "
        "feeding schedules, journal history, and the camera image.\n\n"
        "When strain profile data is available:\n"
        "- Consider strain genetics (indica/sativa/hybrid) when evaluating symptoms — indicas are more compact and dark-leaved naturally.\n"
        "- Purple coloring may be NORMAL anthocyanin expression for certain genetics (GDP, Purple Punch, etc.) — check before flagging.\n"
        "- Use flowering_days to assess timeline — but breeder times are usually 1-2 weeks optimistic.\n"
        "- Factor terpene profiles into environment recommendations (protect dominant terps with appropriate temps).\n"
        "- Adjust pH/EC expectations based on strain sensitivity — OG lineage tends to be calcium-hungry, hazes prefer lighter feeds.\n\n"
        "Your report must cover:\n"
        "1. **Overall Health Score** (0-100): Factor in ALL data. "
        "Weight sensor readings, visual assessment, trends, and stage-appropriate expectations. "
        "A healthy cannabis plant in the right conditions with proper feeding = 85+. Deduct for each confirmed issue.\n"
        "2. **Issues Found**: List EVERY problem detected, from minor to critical. "
        "Be specific about what's wrong and why — cite exact readings, visual symptoms, and the cannabis-specific diagnosis. "
        "Differentiate between deficiency, toxicity, environmental stress, pests, and pathogens.\n"
        "3. **Recommended Actions**: These become TASKS the grower will check off. "
        "Each action must be a concrete, actionable step with specific values "
        "(e.g., 'Lower pH to 5.8 — add 2ml pH Down per gallon', 'Drop room temp to 68°F nights to preserve myrcene/linalool', "
        "'Increase CalMag to 5ml/gal — LED grows need extra calcium'). "
        "Reference the user's current feeding schedule and dose profiles when recommending changes. "
        "Prioritize quality-focused actions: terpene preservation, proper fading, trichome development.\n\n"
        "Be thorough and specific. Tie recommendations to the exact grow type, current stage, "
        "and the user's actual setup. Reference their specific equipment, nutrient line, and controller "
        "when making recommendations. If sensor trends show drift, flag it. "
        "If the previous health check noted issues, check whether they've been resolved.\n\n"
        "ACCURACY & HONESTY — NON-NEGOTIABLE:\n"
        "- You MUST be 100% accurate. This grower's harvest depends on correct information.\n"
        "- Only report issues you can confirm from the provided data. Do not invent problems.\n"
        "- If sensor data is missing or stale, say so explicitly — do not assume values.\n"
        "- If you cannot determine something from the available data, state that clearly.\n"
        "- When citing readings, use the EXACT numbers provided. Do not round or approximate.\n"
        "- 'I don't have enough data to assess this' is always a valid statement.\n"
        "- Distinguish between confirmed issues (backed by data) and potential concerns (educated guesses). Label each clearly.\n\n"
        "IMPORTANT: Respond ONLY with valid JSON. No markdown, no code fences.\n"
        'Format: {"score": <int 0-100>, "issues": ["issue1", ...], "actions": ["action1", ...]}'
    )

    # ── User message with ALL data ───────────────────────────────
    sections = []

    # Observations
    obs_text = "\n".join(f"- {k}: {v}" for k, v in observations.items())
    sections.append(f"=== Plant Observations ===\n{obs_text}")

    # Grow details
    tent_size = grow_data.get("tent_size")
    tent_line = f"  Tent: {grow_data.get('tent_name', '?')}"
    if tent_size:
        tent_line += f" ({tent_size})"
    tent_line += f" [{grow_data.get('environment_type', 'indoor')}]"
    sections.append(
        f"=== Grow Details ===\n"
        f"  Name: {grow_data.get('grow_name', '?')}\n"
        f"  Type: {type_name}\n"
        f"  Stage: {stage}\n"
        f"  Started: {grow_data.get('started_at', '?')}\n" + tent_line
    )

    # Tent equipment (physical hardware)
    tent_equip_text = _fmt_tent_equipment(grow_data.get("tent_equipment"))
    if tent_equip_text:
        sections.append(
            "=== Tent Equipment ===\n" + tent_equip_text + "\n\nThis is the physical hardware in the grower's tent. "
            "Factor this into your diagnosis — reference specific equipment by brand/model."
        )
    tent_notes = grow_data.get("tent_notes")
    if tent_notes:
        sections.append(f"=== Tent Notes ===\n  {tent_notes}")

    # Equipment & Setup
    settings = grow_data.get("settings")
    settings_text = _fmt_settings(settings, grow_data.get("grow_type", ""))
    if settings_text:
        sections.append(
            "=== Grower's Equipment & Setup ===\n"
            + settings_text
            + "\n\nUse this equipment info for specific recommendations "
            "(e.g., reference their exact nutrient line, light brand, controller features)."
        )

    # Grower's notes
    notes = grow_data.get("notes")
    if notes:
        sections.append(f"=== Grower's Notes ===\n  {notes}")

    # Buckets
    buckets = grow_data.get("buckets") or []
    if buckets:
        sections.append(f"=== Plants/Buckets ({len(buckets)}) ===\n" + _fmt_bucket_list(buckets))

    # Data freshness warning
    sensor_age = grow_data.get("sensor_data_age_hours")
    if grow_data.get("sensor_data_stale"):
        if sensor_age is not None:
            days_old = sensor_age / 24
            age_str = f"{days_old:.1f} days ({sensor_age:.0f} hours)" if days_old >= 1 else f"{sensor_age:.1f} hours"
            sections.append(
                f"=== ⚠️ DATA FRESHNESS WARNING ===\n"
                f"  Sensor data is STALE — last reading was {age_str} ago.\n"
                f"  Sensors may be offline or disconnected. The readings below are NOT current.\n"
                f"  Do NOT treat these as the plant's current state. Factor this data gap into your assessment.\n"
                f"  Any tasks completed AFTER the sensor timestamp cannot be validated against sensor data."
            )
        else:
            sections.append(
                "=== ⚠️ DATA FRESHNESS WARNING ===\n"
                "  NO sensor data available at all. Sensors may be offline or not configured.\n"
                "  Assessment will be limited to observations, journal entries, and task history only."
            )

    # Sensors
    bucket_sensors = grow_data.get("bucket_sensors") or {}
    if bucket_sensors:
        s = "=== Latest Sensor Readings ==="
        if sensor_age and sensor_age > 6:
            s += f" [⚠️ STALE: {sensor_age:.0f}h old]"
        for pos, readings in bucket_sensors.items():
            s += f"\n  Bucket {pos}:\n" + _fmt_sensors(readings)
        sections.append(s)

    # Trends
    trends = grow_data.get("sensor_trends")
    if trends:
        sections.append("=== Sensor Trends (24h) ===\n" + _fmt_trends(trends))

    # Tent ambient environment
    tent_ambient = grow_data.get("tent_ambient")
    if tent_ambient:
        amb_lines = []
        if tent_ambient.get("ambient_temp_f") is not None:
            amb_lines.append(f"  Ambient Temp: {tent_ambient['ambient_temp_f']}°F")
        if tent_ambient.get("ambient_humidity") is not None:
            amb_lines.append(f"  Ambient Humidity: {tent_ambient['ambient_humidity']}%")
        if tent_ambient.get("recorded_at"):
            amb_lines.append(f"  Recorded: {tent_ambient['recorded_at']}")
        if tent_ambient.get("hours_old") and tent_ambient["hours_old"] > 6:
            amb_lines.append(f"  ⚠️ STALE: {tent_ambient['hours_old']:.0f} hours old")
        if amb_lines:
            sections.append("=== Tent Environment ===\n" + "\n".join(amb_lines))
    else:
        sections.append(
            "=== Tent Environment ===\n"
            "  ⚠️ No ambient temperature/humidity data available.\n"
            "  VPD cannot be calculated. Environment sensors may be offline or not configured."
        )

    # Ambient trends
    ambient_trends = grow_data.get("ambient_trends")
    if ambient_trends:
        amb_trend_lines = [
            f"  Period: {ambient_trends.get('period_hours', 24)}h ({ambient_trends.get('reading_count', 0)} readings)"
        ]
        for field in ("ambient_temp_f", "ambient_humidity"):
            avg = ambient_trends.get(f"{field}_avg")
            if avg is not None:
                label = "Temp" if "temp" in field else "Humidity"
                unit = "°F" if "temp" in field else "%"
                lo = ambient_trends.get(f"{field}_min")
                hi = ambient_trends.get(f"{field}_max")
                amb_trend_lines.append(f"  {label}: avg {avg}{unit} (range {lo}-{hi}{unit})")
        sections.append("=== Ambient Trends (24h) ===\n" + "\n".join(amb_trend_lines))

    # Feeding
    feeds = grow_data.get("feeding_schedules") or []
    if feeds:
        sections.append("=== Feeding Schedules ===\n" + _fmt_feeding(feeds, stage, grow_data.get("started_at")))

    # Doses
    doses = grow_data.get("dose_profiles") or []
    if doses:
        sections.append("=== Dose Profiles ===\n" + _fmt_doses(doses))

    # Journal
    journals = grow_data.get("journal_entries") or []
    if journals:
        sections.append("=== Recent Journal Entries ===\n" + _fmt_journal(journals))

    # Weather
    weather = grow_data.get("weather")
    if weather:
        w_lines = "\n".join(f"  {k}: {v}" for k, v in weather.items() if v is not None)
        sections.append(f"=== Weather ===\n{w_lines}")

    # Milestones
    milestones = grow_data.get("milestones")
    if milestones:
        m_lines = "\n".join(f"  {k}: {v}" for k, v in milestones.items() if v)
        sections.append(f"=== Milestones ===\n{m_lines}")

    # Tasks context
    pending = grow_data.get("pending_tasks") or []
    if pending:
        task_lines = [
            f"  [{t.get('priority')}] {t['title']}" + (f" (due: {t['due_date'][:10]})" if t.get("due_date") else "")
            for t in pending[:10]
        ]
        sections.append("=== Pending Tasks ===\n" + "\n".join(task_lines))

    completed = grow_data.get("completed_tasks") or []
    if completed:
        done_lines = [f"  ✓ {t['title']} ({t.get('completed_at', '?')[:10]})" for t in completed[:5]]
        sections.append("=== Recently Completed Tasks ===\n" + "\n".join(done_lines))

    # Previous eval (full, not truncated)
    prev = grow_data.get("previous_eval")
    if prev:
        sections.append(
            "=== Previous Health Evaluation ===\n"
            + _fmt_prev_eval(prev, filter_feeding=True)
            + "\n\nCompare current state to this previous evaluation. "
            "Note improvements, regressions, and whether recommended actions were followed."
        )

    if has_camera:
        sections.append(
            "=== Camera Image ===\n"
            "A live camera snapshot from the grow space is attached to this message. "
            "Analyze the visual condition of the plants carefully."
        )

    user_content = "\n\n".join(sections)

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]


# ── Coach tip prompt ─────────────────────────────────────────────────


async def build_coach_tip_prompt(
    grow_type: str,
    stage: str,
    sensors: dict | None = None,
    session=None,
) -> list[dict]:
    """Build messages for generating a coach tip."""
    profile = await get_grow_type_profile_from_db(grow_type, session) if session else None
    type_name = profile["name"] if profile else grow_type
    context = profile.get("ai_context_prompt", "") if profile else ""
    feeding = profile.get("feeding_approach", "") if profile else ""

    system = (
        f"You are a master cannabis grower and cultivation coach for Tendril. "
        f"You specialize in {type_name} cannabis cultivation with deep knowledge of cannabinoid production, "
        f"terpene optimization, environmental controls, training techniques, and stage-specific growing strategies. "
        f"{context} "
        f"Feeding approach: {feeding}. "
        f"The plant is in the **{stage}** stage. "
        "Give ONE concise, actionable cannabis growing tip for this exact situation. "
        "Keep it under 2 sentences. Be specific to this grow type, stage, and what matters most right now "
        "(e.g., VPD targets, feeding adjustments, training timing, harvest indicators). "
        "Talk like a grower — practical and direct. "
        "Only state facts you are confident are true — never guess or make things up."
    )

    user_content = f"Give me a cannabis growing tip for my {type_name} grow in {stage} stage."
    if sensors:
        sensor_text = "\n".join(f"- {k}: {v}" for k, v in sensors.items() if v is not None)
        if sensor_text:
            user_content += f"\n\nCurrent readings:\n{sensor_text}"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]


# ── Insight prompt ───────────────────────────────────────────────────


async def build_insight_prompt(
    insight_type: str,
    grow_type: str,
    data: dict,
    session=None,
) -> list[dict]:
    """Build messages for AI insights (harvest predict, nutrient advice, anomaly scan)."""
    profile = await get_grow_type_profile_from_db(grow_type, session) if session else None
    type_name = profile["name"] if profile else grow_type

    prompts = {
        "harvest_predict": (
            f"You are a master cannabis grower specializing in {type_name} cultivation harvest timing. "
            f"You have deep expertise in trichome development stages (clear → milky → amber), "
            f"pistil recession patterns, calyx swelling, and strain-specific flowering timelines. "
            f"Based on the following grow data, predict the optimal harvest window for maximum quality. "
            "Consider: trichome maturity (milky for peak THC, amber for CBN/couch-lock), "
            "strain flowering time (breeder times are usually 1-2 weeks optimistic), "
            "environmental conditions affecting ripening speed, and the grower's quality goals. "
            "Respond with JSON: {{estimated_date, days_remaining, confidence, trichome_target, notes}}"
        ),
        "nutrient_advice": (
            f"You are a master cannabis nutrient specialist for {type_name} cultivation. "
            f"You understand cannabis-specific nutrient demands: high N in veg, P/K ramp in flower, "
            f"calcium/magnesium needs under LED, silica for cell wall strength, and the importance of "
            f"proper EC/pH management for nutrient uptake and terpene production. "
            f"Analyze the nutrient data for this cannabis grow and provide feeding recommendations "
            f"optimized for quality flower production (terpenes, trichomes, cannabinoid content). "
            "Consider pH/EC trends, growth stage, strain sensitivity, and grow-type-specific requirements. "
            "Respond with JSON: {{adjustments: [{{nutrient, action, amount}}], reasoning}}"
        ),
        "anomaly_scan": (
            f"You are a cannabis cultivation monitoring specialist for {type_name} grows. "
            f"You have deep knowledge of optimal cannabis sensor ranges by stage, early warning signs "
            f"of deficiencies/toxicities/pathogens, and how environmental drift affects cannabinoid and terpene production. "
            f"Scan the sensor data for anomalies or concerning trends that could impact flower quality. "
            "Flag readings outside optimal cannabis ranges for this grow type and stage. "
            "Prioritize issues that threaten terpene profiles, trichome development, or could trigger hermaphroditism. "
            "Respond with JSON: {{anomalies: [{{sensor, value, expected_range, severity, recommendation}}]}}"
        ),
    }

    system = prompts.get(insight_type, f"Analyze this {type_name} cannabis grow data and provide insights.")
    system += " Be 100% accurate — only report what the data supports. If data is insufficient, say so."
    data_str = "\n".join(f"- {k}: {v}" for k, v in data.items())

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Grow data:\n{data_str}"},
    ]


# ── Feeding advice prompt ────────────────────────────────────────────


def _current_grow_week(grow_data: dict) -> int | None:
    """Return the 1-based overall week number since the grow started."""
    from datetime import datetime

    started = grow_data.get("started_at")
    if not started:
        return None
    if isinstance(started, str):
        started = datetime.fromisoformat(started)
    now = datetime.now(UTC)
    days = (now - started).days
    return max(1, days // 7 + 1)


def _week_matches_schedule(week: int, schedule_name: str) -> bool:
    """Check if *week* falls within the (Wk …) range in a schedule name."""
    import re

    m = re.search(r"\(Wk\s+(\d+)(?:\s*[–-]\s*(\d+))?\)", schedule_name)
    if not m:
        return False
    lo = int(m.group(1))
    hi = int(m.group(2)) if m.group(2) else lo
    return lo <= week <= hi


async def build_feeding_advice_prompt(grow_data: dict, session=None) -> list[dict]:
    """Build messages for AI feeding advice using full grow context."""
    import json as _json

    stage = grow_data.get("stage", "unknown")
    grow_type = grow_data.get("grow_type", "unknown")
    current_week = _current_grow_week(grow_data)
    profile = await get_grow_type_profile_from_db(grow_type, session) if session else None
    type_name = profile["name"] if profile else grow_type
    feeding_approach = profile.get("feeding_approach", "") if profile else ""
    ec_range = profile.get("ec_range", {}) if profile else {}

    system = (
        f"You are a master cannabis nutrient specialist — the kind of grower who dials in feed charts "
        f"to produce award-winning flower. You specialize in {type_name} cannabis cultivation "
        f"with deep expertise in nutrient chemistry, plant uptake dynamics, feed chart optimization, "
        f"and stage-specific EC/pH management for maximum cannabinoid and terpene production. "
        f"The grow is currently in the **{stage}** stage.\n\n"
        f"Grow-type feeding approach: {feeding_approach}\n"
        f"Recommended EC ranges: {_json.dumps(ec_range) if ec_range else 'not specified'}\n\n"
        "Your goal: optimize this feeding program for TOP-SHELF cannabis quality — dense, frosty buds "
        "with full terpene profiles and proper cannabinoid maturity.\n\n"
        "Cannabis-specific feeding principles:\n"
        "- Veg: high N drives vegetative growth, moderate P/K, CalMag essential under LED\n"
        "- Transition (flip): begin ramping P/K, reduce N by 20-30%, increase K for stem strength\n"
        "- Early flower (wk 1-3): P/K ramp begins, maintain moderate N for stretch, boost CalMag\n"
        "- Mid flower (wk 4-6): peak P/K for bud development, reduce N significantly, potassium drives resin\n"
        "- Late flower (wk 7+): begin reducing overall EC, some growers flush 1-2 weeks before harvest\n"
        "- Ripening/flush: plain water or very light feed to allow natural senescence (the fade)\n"
        "- LED grows need 20-30% more CalMag than HPS grows\n"
        "- Water temp affects DO and nutrient uptake — flag if above 72°F\n"
        "- pH drift in hydro indicates nutrient uptake patterns — rising pH = plant eating more N (nutes), falling = eating more K (water)\n\n"
        "Analyze ALL of the following data and produce a JSON response with this exact schema:\n"
        "{\n"
        '  "current_stage_advice": "1-2 sentence summary of what to feed right now for best quality",\n'
        '  "adjustments": [\n'
        '    {"schedule_name": "name of existing schedule", "change": "what to adjust", "reason": "why — tie to quality/terps/cannabinoids"}\n'
        "  ],\n"
        '  "alerts": [\n'
        '    {"severity": "high|medium|low", "message": "actionable alert", "type": "nutrient|ph|ec|deficiency|toxicity|transition"}\n'
        "  ],\n"
        '  "next_transition": {"stage": "next stage name", "action": "what to prepare for quality flower", "estimated_timing": "when based on milestones/dates"},\n'
        '  "health_impact": "how latest health check should influence feeding (or null if no health data)"\n'
        "}\n\n"
        "Rules:\n"
        "- The feeding schedules below represent the FULL feed chart for the entire grow cycle. Only the schedule marked ← ACTIVE is what the grower should be following right now.\n"
        "- Do NOT flag other schedules in the chart as 'incorrect' — they are future/past phases, not mistakes.\n"
        "- ADJUST the ACTIVE schedule based on sensor readings, health score, and growth progress.\n"
        "- Factor in any standalone additives the user has selected (e.g. Hydroguard, Cal-Mag). Confirm they are being used correctly and flag if any should be added or removed based on conditions.\n"
        "- If sensor pH/EC are drifting, recommend corrections with specific products/amounts.\n"
        "- If health score is low or issues mention nutrient problems, flag them as high-severity alerts.\n"
        "- Use milestone dates to estimate stage transitions and recommend pre-transition feeding changes.\n"
        "- If data is insufficient for a field, set it to null rather than guessing.\n"
        "- Keep advice specific and actionable. Reference actual product names and ml/gal amounts.\n"
        "- Always frame recommendations in terms of flower quality impact (terpenes, density, trichome production).\n"
        "- Only state facts supported by the data."
    )

    # Build detailed user context
    sections = []

    # Grow info
    sections.append(f"## Grow Info\n- Type: {type_name}\n- Stage: {stage}\n- Status: {grow_data.get('status')}")
    if grow_data.get("started_at"):
        sections.append(f"- Started: {grow_data['started_at']}")
    if current_week is not None:
        sections.append(f"- Current overall week: {current_week}")
    if grow_data.get("milestones"):
        ms_lines = [f"  - {k}: {v}" for k, v in grow_data["milestones"].items() if v]
        if ms_lines:
            sections.append("- Milestones:\n" + "\n".join(ms_lines))
    if grow_data.get("settings"):
        settings_lines = [f"  - {k}: {v}" for k, v in grow_data["settings"].items() if v]
        if settings_lines:
            sections.append("- Grow Settings:\n" + "\n".join(settings_lines))

    # User-selected standalone additives
    additive_ids = (grow_data.get("settings") or {}).get("additive_ids") or []
    if additive_ids:
        # Known additive reference (synced with client-side STANDALONE_ADDITIVES)
        ADDITIVE_REF = {
            "botanicare-hydroguard": (
                "Hydroguard",
                "Botanicare",
                2,
                "Beneficial bacteria for root health. Essential when water temps > 68°F.",
            ),
            "botanicare-calmag-plus": ("Cal-Mag Plus", "Botanicare", 5, "Calcium, magnesium, iron supplement."),
            "gh-armor-si": ("Armor Si", "General Hydroponics", 1.5, "Potassium silicate for stronger cell walls."),
            "gh-rapidstart": ("RapidStart", "General Hydroponics", 1, "Root enhancer for early growth."),
            "slf100": ("SLF-100", "SLF-100", 1, "Enzymatic formula to break down dead roots and salt buildup."),
            "mammoth-p": ("Mammoth P", "Mammoth Microbes", 0.16, "Phosphorus-liberating microbial inoculant."),
            "recharge": ("Recharge", "Real Growers", 0.5, "Mycorrhizae and trichoderma blend for soil/coco."),
        }
        add_lines = []
        for aid in additive_ids:
            ref = ADDITIVE_REF.get(aid)
            if ref:
                add_lines.append(f"  - {ref[0]} ({ref[1]}) — {ref[2]} ml/gal: {ref[3]}")
            else:
                add_lines.append(f"  - {aid} (unknown additive)")
        sections.append("## User-Selected Additives (used alongside brand nutrients)\n" + "\n".join(add_lines))

    # Current feeding schedules (full feed chart — only one is ACTIVE)
    if grow_data.get("feeding_schedules"):
        feed_lines = []
        for fs in grow_data["feeding_schedules"]:
            if current_week is not None and _week_matches_schedule(current_week, fs["name"]):
                current_marker = " ← ACTIVE"
            else:
                current_marker = ""
            line = f"  - {fs['name']} ({fs['stage']}{current_marker})"
            if fs.get("target_ppm"):
                line += f" PPM:{fs['target_ppm']}"
            if fs.get("target_ec"):
                line += f" EC:{fs['target_ec']}"
            if fs.get("nutrients"):
                for n in fs["nutrients"]:
                    line += f"\n    • {n.get('name', '?')}"
                    if n.get("brand"):
                        line += f" ({n['brand']})"
                    if n.get("ml_per_gallon"):
                        line += f" — {n['ml_per_gallon']} ml/gal"
            if fs.get("notes"):
                line += f"\n    Note: {fs['notes']}"
            feed_lines.append(line)
        sections.append("## Current Feeding Schedules\n" + "\n".join(feed_lines))
    else:
        sections.append("## Current Feeding Schedules\nNone configured yet.")

    # Sensor readings
    if grow_data.get("bucket_sensors"):
        sensor_lines = []
        for pos, readings in grow_data["bucket_sensors"].items():
            sensor_lines.append(f"  Bucket #{pos}: " + ", ".join(f"{k}={v}" for k, v in readings.items()))
        sections.append("## Latest Sensor Readings\n" + "\n".join(sensor_lines))

    if grow_data.get("sensor_trends"):
        trends = grow_data["sensor_trends"]
        trend_lines = [f"  - {k}: {v}" for k, v in trends.items()]
        sections.append("## Sensor Trends (24h)\n" + "\n".join(trend_lines))

    # Tent environment
    if grow_data.get("tent_ambient"):
        amb = grow_data["tent_ambient"]
        sections.append(
            f"## Tent Environment\n  - Temp: {amb.get('ambient_temp_f', '?')}°F, Humidity: {amb.get('ambient_humidity', '?')}%"
        )

    # Health check — include score only; full issues/actions are from a
    # separate AI model and may contain stale schedule conclusions.
    if grow_data.get("previous_eval"):
        ev = grow_data["previous_eval"]
        score_line = f"  - Score: {ev.get('score', '?')}/100"
        # Only pass non-schedule issues (filter out stale feeding conclusions)
        raw_issues = ev.get("issues") or []
        filtered = [i for i in raw_issues if "schedule" not in i.lower() and "feeding" not in i.lower()]
        issues_line = f"  - Issues: {', '.join(filtered) or 'None'}"
        sections.append(f"## Latest Health Check\n{score_line}\n{issues_line}")

    # Strains
    if grow_data.get("buckets"):
        strain_lines = []
        for b in grow_data["buckets"]:
            if b.get("strain_profile"):
                sp = b["strain_profile"]
                strain_lines.append(
                    f"  - #{b['position']} {sp.get('name', '?')}: "
                    f"genetics={sp.get('genetics', '?')}, "
                    f"flowering_days={sp.get('flowering_days', '?')}"
                )
        if strain_lines:
            sections.append("## Strains\n" + "\n".join(strain_lines))

    user_content = "\n\n".join(sections)

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]
