"""AI context builder — assembles grow-type-aware context for Ollama / Gemini prompts."""
from __future__ import annotations

from app.grows.grow_types import GROW_TYPE_PROFILES


def get_grow_type_profile(grow_type: str) -> dict | None:
    """Look up the grow type profile by ID."""
    for p in GROW_TYPE_PROFILES:
        if p["id"] == grow_type:
            return p
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
            desc += f" \"{b['label']}\""
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


def _fmt_feeding(schedules: list[dict], current_stage: str) -> str:
    parts = []
    for s in schedules:
        marker = " ← CURRENT" if s["stage"] == current_stage else ""
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
        f"  {d['name']} ({d['dose_type']}): {d['dose_ml']}ml"
        + (" [enabled]" if d.get("enabled") else " [disabled]")
        for d in profiles
    )


def _fmt_journal(entries: list[dict]) -> str:
    parts = []
    for j in entries:
        date = j["created_at"][:10] if j.get("created_at") else "?"
        line = f"  {date} [{j['event_type']}] {j.get('content', '')}"
        # Include payload data (pH readings, EC values, nutrient amounts, etc.)
        payload = j.get("payload")
        if payload and isinstance(payload, dict):
            details = ", ".join(f"{k}: {v}" for k, v in payload.items() if v is not None and k != "bucket_id")
            if details:
                line += f"\n    Data: {details}"
        parts.append(line)
    return "\n".join(parts)


def _fmt_trends(trends: dict) -> str:
    lines = [f"  Period: {trends.get('period_hours', 24)}h ({trends.get('reading_count', 0)} readings)"]
    for field in ("ph", "ec", "ppm", "water_temp_f", "dissolved_oxygen", "water_level_pct",
                  "soil_moisture", "soil_temp",
                  "runoff_ph", "runoff_ec", "flow_rate", "mist_pressure"):
        avg = trends.get(f"{field}_avg")
        if avg is not None:
            label = field.replace("_", " ").title()
            lo = trends.get(f"{field}_min")
            hi = trends.get(f"{field}_max")
            lines.append(f"  {label}: avg {avg}, range {lo}–{hi}")
    return "\n".join(lines)


def _fmt_prev_eval(prev: dict) -> str:
    parts = [
        f"  Date: {prev.get('created_at', '?')}",
        f"  Score: {prev.get('score', '?')}/100 ({prev.get('source', 'manual')})",
    ]
    if prev.get("issues"):
        parts.append("  Issues:")
        for issue in prev["issues"]:
            parts.append(f"    - {issue}")
    if prev.get("actions"):
        parts.append("  Actions recommended:")
        for action in prev["actions"]:
            parts.append(f"    - {action}")
    return "\n".join(parts)


def _fmt_settings(settings: dict | None, grow_type: str) -> str:
    """Format grow settings into human-readable lines for AI context.

    Maps raw setting keys to descriptive labels so the AI understands
    the grower's exact setup — equipment, configuration, targets, etc.
    """
    if not settings:
        return ""
    LABELS = {
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
        label = LABELS.get(key, key.replace("_", " ").title())
        lines.append(f"  {label}: {value}")
    return "\n".join(lines)


# ── Chat context ─────────────────────────────────────────────────────

def build_chat_context(
    grow_data: dict,
) -> str:
    """Build a comprehensive system prompt for Ollama chat using all available data."""
    profile = get_grow_type_profile(grow_data.get("grow_type", ""))
    if not profile:
        return "You are Tendril, an AI grow assistant."

    parts = [
        f"You are Tendril, an AI grow assistant specializing in {profile['name']}.",
        f"Context: {profile['ai_prompt_context']}",
        f"Feeding approach: {profile['feeding_approach']}",
        f"Nutrient strength: {profile['nutrient_strength']}",
        f"pH range: {profile['ph_range']['min']}-{profile['ph_range']['max']}",
        f"Common problems: {', '.join(profile['common_problems'])}",
        f"Health check questions to consider: {', '.join(profile.get('health_check_questions', []))}",
    ]

    # Add terminology so the AI uses the right words for this grow type
    terminology = profile.get("terminology", {})
    if terminology:
        term_str = ", ".join(f"{k}='{v}'" for k, v in terminology.items())
        parts.append(f"Use these terms when talking to the grower: {term_str}")

    # Grow details
    parts.append(
        f"\n=== Active Grow ===\n"
        f"  Name: {grow_data.get('grow_name', '?')}\n"
        f"  Type: {profile['name']}\n"
        f"  Stage: {grow_data.get('stage', '?')}\n"
        f"  Status: {grow_data.get('status', '?')}\n"
        f"  Started: {grow_data.get('started_at', '?')}\n"
        f"  Tent: {grow_data.get('tent_name', '?')} ({grow_data.get('environment_type', 'indoor')})"
    )

    # Equipment & Setup (from grow settings)
    settings = grow_data.get("settings")
    settings_text = _fmt_settings(settings, grow_data.get("grow_type", ""))
    if settings_text:
        parts.append(
            "\n=== Grower's Equipment & Setup ===\n" + settings_text
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
        ambient_trend_lines = [f"  Period: {ambient_trends.get('period_hours', 24)}h ({ambient_trends.get('reading_count', 0)} readings)"]
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
            + _fmt_feeding(feeds, grow_data.get("stage", ""))
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
        parts.append("\n=== Last Health Evaluation ===\n" + _fmt_prev_eval(prev))

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

    parts.extend([
        "\nYou can update the user's grow, buckets, feeding schedules, tent, and journal entries using the available tools.",
        "Respond concisely and practically. Focus on actionable advice.",
        "Use the grow-type terminology the user would expect.",

        "\n=== CORE PHILOSOPHY: Quality Over Quantity ===",
        "The grower's #1 priority is producing the BEST buds, not the biggest.",
        "Always optimize recommendations for quality:",
        "- Terpene preservation > maximum yield (suggest lower temps in late flower to preserve myrcene/linalool).",
        "- Proper flush timing > extended feeding (clean, smooth smoke matters more than extra grams).",
        "- Trichome maturity > speed (guide toward the right amber ratio, don't rush harvest).",
        "- Stress reduction > aggressive training (healthy plants produce better resin).",
        "- Optimal harvest windows > early chops (patience = potency).",
        "- Dial environment for resin production: VPD, light spectrum, day/night temp swings.",
        "- When in doubt, err on the side of plant health and bud quality.",

        "\n=== Strain-Aware Guidelines ===",
        "When strain profile data is available for a bucket:",
        "- Use flowering_days to estimate harvest window and adjust late-flower advice.",
        "- Reference terpene profiles for environment tuning (e.g., lower temps in final weeks to preserve myrcene/linalool).",
        "- Adjust pH/EC recommendations based on indica vs sativa genetics.",
        "- Note strain-specific characteristics (e.g., purple coloring on certain genetics is NORMAL, not deficiency).",
        "- Factor in THC/CBD ratios when advising on harvest timing (amber trichomes for higher CBD, clear for higher THC).",
    ])

    return "\n".join(parts)


# ── Health-check prompt (Gemini) ─────────────────────────────────────

def build_health_check_prompt(
    grow_data: dict,
    observations: dict[str, str],
) -> list[dict]:
    """Build messages for a Gemini-powered health check using ALL available data."""
    grow_type = grow_data.get("grow_type", "")
    stage = grow_data.get("stage", "?")
    profile = get_grow_type_profile(grow_type)
    type_name = profile["name"] if profile else grow_type
    context = profile["ai_prompt_context"] if profile else ""
    common = ", ".join(profile["common_problems"]) if profile else ""
    ph_range = profile["ph_range"] if profile else {}
    feeding_approach = profile.get("feeding_approach", "") if profile else ""

    has_camera = grow_data.get("camera_image") is not None

    system = (
        f"You are an expert plant health diagnostic AI specializing in {type_name} grows. "
        f"{context} "
        f"Feeding approach: {feeding_approach}. "
        f"The plant is in the {stage} stage. "
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
        "CORE PHILOSOPHY: Quality over quantity. The grower wants the BEST buds, not the biggest. "
        "All recommendations should prioritize terpene preservation, proper flush timing, "
        "trichome maturity, stress reduction, and optimal harvest windows. "
        "Dial environment for resin production — not maximum biomass.\n\n"
    )

    if has_camera:
        system += (
            "A live camera image from the grow space is attached. Analyze the image carefully for:\n"
            "- Leaf color, shape, and health (yellowing, spots, curling, wilting)\n"
            "- Root health if visible (color, slime, brown roots)\n"
            "- Overall plant structure and growth patterns\n"
            "- Any signs of pests, mold, or environmental stress\n"
            "- Light distance and coverage\n\n"
        )

    system += (
        "Perform the MOST thorough health evaluation possible. "
        "Analyze ALL provided data — observations, sensor readings, sensor trends, "
        "feeding schedules, journal history, and the camera image.\n\n"
        "When strain profile data is available:\n"
        "- Consider strain genetics (indica/sativa/hybrid) when evaluating symptoms.\n"
        "- Purple coloring may be NORMAL for certain genetics — check before flagging as deficiency.\n"
        "- Use flowering_days to assess whether the plant is on track for its expected timeline.\n"
        "- Factor terpene profiles into environment recommendations (temp/humidity adjustments).\n"
        "- Adjust pH/EC targets based on strain sensitivity.\n\n"
        "Your report must cover:\n"
        "1. **Overall Health Score** (0-100): Factor in ALL data. "
        "Weight sensor readings, visual assessment, trends, and stage-appropriate expectations.\n"
        "2. **Issues Found**: List EVERY problem detected, from minor to critical. "
        "Be specific about what's wrong and why. Cite exact readings/observations.\n"
        "3. **Recommended Actions**: These become TASKS the grower will check off. "
        "Each action must be a concrete, actionable step with specific values "
        "(e.g., 'Lower pH to 5.8 — add 2ml pH Down per gallon', 'Drop room temp to 68°F to preserve terpenes'). "
        "Reference the user's current feeding schedule and dose profiles when recommending changes. "
        "Prioritize quality-focused actions: terpene preservation, proper flushing, trichome development.\n\n"
        "Be thorough and specific. Tie recommendations to the exact grow type, current stage, "
        "and the user's actual setup. Reference their specific equipment, nutrient line, and controller "
        "when making recommendations. If sensor trends show drift, flag it. "
        "If the previous health check noted issues, check whether they've been resolved.\n\n"
        "IMPORTANT: Respond ONLY with valid JSON. No markdown, no code fences.\n"
        'Format: {"score": <int 0-100>, "issues": ["issue1", ...], "actions": ["action1", ...]}'
    )

    # ── User message with ALL data ───────────────────────────────
    sections = []

    # Observations
    obs_text = "\n".join(f"- {k}: {v}" for k, v in observations.items())
    sections.append(f"=== Plant Observations ===\n{obs_text}")

    # Grow details
    sections.append(
        f"=== Grow Details ===\n"
        f"  Name: {grow_data.get('grow_name', '?')}\n"
        f"  Type: {type_name}\n"
        f"  Stage: {stage}\n"
        f"  Started: {grow_data.get('started_at', '?')}\n"
        f"  Tent: {grow_data.get('tent_name', '?')} ({grow_data.get('environment_type', 'indoor')})"
    )

    # Equipment & Setup
    settings = grow_data.get("settings")
    settings_text = _fmt_settings(settings, grow_data.get("grow_type", ""))
    if settings_text:
        sections.append(
            "=== Grower's Equipment & Setup ===\n" + settings_text
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

    # Sensors
    bucket_sensors = grow_data.get("bucket_sensors") or {}
    if bucket_sensors:
        s = "=== Latest Sensor Readings ==="
        for pos, readings in bucket_sensors.items():
            s += f"\n  Bucket {pos}:\n" + _fmt_sensors(readings)
        sections.append(s)

    # Trends
    trends = grow_data.get("sensor_trends")
    if trends:
        sections.append("=== Sensor Trends (24h) ===\n" + _fmt_trends(trends))

    # Feeding
    feeds = grow_data.get("feeding_schedules") or []
    if feeds:
        sections.append(
            "=== Feeding Schedules ===\n"
            + _fmt_feeding(feeds, stage)
        )

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
        task_lines = [f"  [{t.get('priority')}] {t['title']}" + (f" (due: {t['due_date'][:10]})" if t.get("due_date") else "") for t in pending[:10]]
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
            + _fmt_prev_eval(prev)
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

def build_coach_tip_prompt(
    grow_type: str,
    stage: str,
    sensors: dict | None = None,
) -> list[dict]:
    """Build messages for generating a coach tip."""
    profile = get_grow_type_profile(grow_type)
    type_name = profile["name"] if profile else grow_type
    context = profile["ai_prompt_context"] if profile else ""
    feeding = profile["feeding_approach"] if profile else ""

    system = (
        f"You are a grow coach for {type_name}. {context} "
        f"Feeding approach: {feeding}. "
        f"The plant is in the {stage} stage. "
        "Give ONE concise, actionable tip for this exact situation. "
        "Keep it under 2 sentences. Be specific to this grow type and stage."
    )

    user_content = f"Give me a tip for my {type_name} grow in {stage} stage."
    if sensors:
        sensor_text = "\n".join(f"- {k}: {v}" for k, v in sensors.items() if v is not None)
        if sensor_text:
            user_content += f"\n\nCurrent readings:\n{sensor_text}"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]


# ── Insight prompt ───────────────────────────────────────────────────

def build_insight_prompt(
    insight_type: str,
    grow_type: str,
    data: dict,
) -> list[dict]:
    """Build messages for AI insights (harvest predict, nutrient advice, anomaly scan)."""
    profile = get_grow_type_profile(grow_type)
    type_name = profile["name"] if profile else grow_type

    prompts = {
        "harvest_predict": (
            f"Based on the following grow data for a {type_name} grow, predict the harvest date and expected yield. "
            "Consider the growth stage, sensor trends, and strain characteristics. "
            "Respond with JSON: {{estimated_harvest_date, estimated_yield_g, confidence, reasoning}}"
        ),
        "nutrient_advice": (
            f"Analyze the nutrient data for this {type_name} grow and provide feeding recommendations. "
            "Consider pH/EC trends, growth stage, and grow-type-specific requirements. "
            "Respond with JSON: {{adjustments: [{{nutrient, action, amount}}], reasoning}}"
        ),
        "anomaly_scan": (
            f"Scan the sensor data for this {type_name} grow for anomalies or concerning trends. "
            "Flag any readings outside normal ranges for this grow type and stage. "
            "Respond with JSON: {{anomalies: [{{sensor, value, expected_range, severity, recommendation}}]}}"
        ),
    }

    system = prompts.get(insight_type, f"Analyze this {type_name} grow data and provide insights.")
    data_str = "\n".join(f"- {k}: {v}" for k, v in data.items())

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Grow data:\n{data_str}"},
    ]
