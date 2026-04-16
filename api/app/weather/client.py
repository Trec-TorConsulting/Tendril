"""Open-Meteo weather client — fetch current + forecast data."""
from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger("tendril.weather")

OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"


async def fetch_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """Fetch current weather + 7-day forecast from Open-Meteo API."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,uv_index_max,weather_code",
        "timezone": "auto",
        "forecast_days": 7,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(OPEN_METEO_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()

    current = data.get("current", {})
    daily = data.get("daily", {})

    return {
        "current": {
            "temperature_c": current.get("temperature_2m"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "precipitation_mm": current.get("precipitation"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "uv_index": current.get("uv_index"),
            "weather_code": current.get("weather_code"),
        },
        "forecast": [
            {
                "date": daily["time"][i],
                "temp_max_c": daily["temperature_2m_max"][i],
                "temp_min_c": daily["temperature_2m_min"][i],
                "precipitation_mm": daily["precipitation_sum"][i],
                "wind_max_kmh": daily["wind_speed_10m_max"][i],
                "uv_max": daily["uv_index_max"][i],
                "weather_code": daily["weather_code"][i],
            }
            for i in range(len(daily.get("time", [])))
        ],
    }


def evaluate_weather_alerts(current: dict, forecast: list[dict]) -> list[dict]:
    """Evaluate weather data for alerts.

    Returns a list of alert dicts: [{type, severity, message}]
    """
    alerts: list[dict] = []
    temp_c = current.get("temperature_c")
    wind = current.get("wind_speed_kmh")
    uv = current.get("uv_index")
    precip = current.get("precipitation_mm")

    if temp_c is not None and temp_c < 4:
        alerts.append({"type": "frost", "severity": "critical", "message": f"Frost risk: {temp_c}°C"})
    if temp_c is not None and temp_c > 38:
        alerts.append({"type": "heat", "severity": "warning", "message": f"Heat stress: {temp_c}°C"})
    if precip is not None and precip > 25:
        alerts.append({"type": "rain", "severity": "warning", "message": f"Heavy rain: {precip}mm"})
    if wind is not None and wind > 50:
        alerts.append({"type": "wind", "severity": "warning", "message": f"High wind: {wind}km/h"})
    if uv is not None and uv > 8:
        alerts.append({"type": "uv", "severity": "info", "message": f"High UV index: {uv}"})

    # Check tomorrow's forecast for frost warning
    if forecast and len(forecast) > 0:
        tomorrow = forecast[0]
        if tomorrow.get("temp_min_c") is not None and tomorrow["temp_min_c"] < 4:
            alerts.append({
                "type": "frost_forecast",
                "severity": "warning",
                "message": f"Frost expected tomorrow: min {tomorrow['temp_min_c']}°C",
            })

    return alerts
