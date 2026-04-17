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
        parts.append(f"  {date} [{j['event_type']}] {j.get('content', '')}")
    return "\n".join(parts)


def _fmt_trends(trends: dict) -> str:
    lines = [f"  Period: {trends.get('period_hours', 24)}h ({trends.get('reading_count', 0)} readings)"]
    for field in ("ph", "ec", "ppm", "water_temp_f", "dissolved_oxygen", "water_level_pct"):
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
    ]

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

    # Sensor trends
    trends = grow_data.get("sensor_trends")
    if trends:
        parts.append("\n=== Sensor Trends ===\n" + _fmt_trends(trends))

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

    parts.extend([
        "\nYou can update the user's grow, buckets, feeding schedules, tent, and journal entries using the available tools.",
        "Respond concisely and practically. Focus on actionable advice.",
        "Use the grow-type terminology the user would expect.",
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
        "Your report must cover:\n"
        "1. **Overall Health Score** (0-100): Factor in ALL data. "
        "Weight sensor readings, visual assessment, trends, and stage-appropriate expectations.\n"
        "2. **Issues Found**: List EVERY problem detected, from minor to critical. "
        "Be specific about what's wrong and why. Cite exact readings/observations.\n"
        "3. **Recommended Actions**: Prioritized by urgency. "
        "Include specific values (e.g., 'lower pH to 5.8', 'add 2ml/gal CalMag'). "
        "Reference the user's current feeding schedule and dose profiles when recommending changes.\n\n"
        "Be thorough and specific. Tie recommendations to the exact grow type, current stage, "
        "and the user's actual setup. If sensor trends show drift, flag it. "
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
