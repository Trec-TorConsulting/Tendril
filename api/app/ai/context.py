"""AI context builder — assembles grow-type-aware context for Ollama prompts."""
from __future__ import annotations

from app.grows.grow_types import GROW_TYPE_PROFILES


def get_grow_type_profile(grow_type: str) -> dict | None:
    """Look up the grow type profile by ID."""
    for p in GROW_TYPE_PROFILES:
        if p["id"] == grow_type:
            return p
    return None


def build_chat_context(
    grow_type: str,
    stage: str | None = None,
    recent_sensors: dict | None = None,
    weather: dict | None = None,
) -> str:
    """Build a system prompt context string with grow-type-specific info."""
    profile = get_grow_type_profile(grow_type)
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

    if stage:
        parts.append(f"Current growth stage: {stage}")

    if recent_sensors:
        sensor_lines = [f"  {k}: {v}" for k, v in recent_sensors.items() if v is not None]
        if sensor_lines:
            parts.append("Latest sensor readings:\n" + "\n".join(sensor_lines))

    if weather:
        weather_lines = [f"  {k}: {v}" for k, v in weather.items() if v is not None]
        if weather_lines:
            parts.append("Current weather conditions:\n" + "\n".join(weather_lines))

    parts.extend([
        "Respond concisely and practically. Focus on actionable advice.",
        "Use the grow-type terminology the user would expect.",
    ])

    return "\n\n".join(parts)


def build_health_check_prompt(
    grow_type: str,
    stage: str,
    observations: dict[str, str],
    sensors: dict | None = None,
    weather: dict | None = None,
) -> list[dict]:
    """Build messages for an AI health check analysis."""
    profile = get_grow_type_profile(grow_type)
    type_name = profile["name"] if profile else grow_type
    context = profile["ai_prompt_context"] if profile else ""
    common = ", ".join(profile["common_problems"]) if profile else ""

    system = (
        f"You are a plant health diagnostic AI for {type_name} grows. "
        f"{context} "
        f"The plant is in the {stage} stage. "
        f"Common problems for this grow type: {common}. "
        "Analyze the observations and sensor data. "
        "Provide: 1) Health score (1-10), 2) Issues detected, 3) Recommended actions. "
        "Be specific and actionable. Format as JSON with keys: score, issues, actions."
    )

    obs_text = "\n".join(f"- {k}: {v}" for k, v in observations.items())
    user_content = f"Plant observations:\n{obs_text}"

    if sensors:
        sensor_text = "\n".join(f"- {k}: {v}" for k, v in sensors.items() if v is not None)
        if sensor_text:
            user_content += f"\n\nSensor readings:\n{sensor_text}"

    if weather:
        weather_text = "\n".join(f"- {k}: {v}" for k, v in weather.items() if v is not None)
        if weather_text:
            user_content += f"\n\nWeather conditions:\n{weather_text}"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]


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
