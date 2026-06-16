"""OpenWeather connector — polls OpenWeather API 3.0 for weather data.

An **optional upgrade** over the free Open-Meteo baseline.  Provides
air-quality data, minute-level precipitation nowcasts, and government
weather alerts when available.  Requires an OpenWeather API key
(free tier = 1 000 calls / day).

Data is written to the ``weather_readings`` table so the existing alert
evaluation, GDD engine, and AI context pipelines pick it up seamlessly.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import WeatherReading
from app.integrations.connectors.base import BaseConnector, ConnectorResult, register_connector
from app.integrations.connectors.retry import retry_request
from app.integrations.models import IntegrationDeviceMap

logger = logging.getLogger("tendril.integrations.openweather")

_TIMEOUT = 15.0
_DEFAULT_BASE_URL = "https://api.openweathermap.org"


# ---------------------------------------------------------------------------
# Config schema
# ---------------------------------------------------------------------------


class OpenWeatherConfig(BaseModel):
    """Validated config shape for OpenWeather integrations."""

    api_key: str = Field(..., min_length=10, description="OpenWeather API key")
    base_url: str = Field(default=_DEFAULT_BASE_URL, description="OpenWeather API base URL")
    use_onecall_30: bool = Field(
        default=False,
        description="Use One Call 3.0 (requires subscription) instead of 2.5 free endpoint",
    )


# ---------------------------------------------------------------------------
# Discovery response
# ---------------------------------------------------------------------------


class DiscoveredDevice(BaseModel):
    external_id: str
    name: str
    device_type: str  # "weather_location"
    latest_reading: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


@register_connector
class OpenWeatherConnector(BaseConnector):
    """Connector for OpenWeather REST API.

    Each ``IntegrationDeviceMap`` represents a (tent_id → lat/lng) pair.
    The ``external_id`` encodes coordinates as ``"lat,lng"`` and the
    ``tent_id`` links to the target grow tent.
    """

    integration_type = "openweather"

    def _client(self) -> httpx.AsyncClient:
        base_url = self.decrypted_config.get("base_url", _DEFAULT_BASE_URL)
        return httpx.AsyncClient(base_url=base_url, timeout=_TIMEOUT)

    # ── Poll ─────────────────────────────────────────────────────

    async def poll(self) -> ConnectorResult:
        """Fetch weather for every mapped tent location."""
        result = ConnectorResult()

        tent_maps = [dm for dm in self.device_maps if dm.tent_id]
        if not tent_maps:
            return result

        async with self._client() as client:
            for dm in tent_maps:
                await self._poll_location(client, dm, result)

        return result

    async def _poll_location(
        self,
        client: httpx.AsyncClient,
        dm: IntegrationDeviceMap,
        result: ConnectorResult,
    ) -> None:
        """Poll a single lat,lng location for current + forecast."""
        coords = dm.external_id  # "lat,lng"
        parts = coords.split(",")
        if len(parts) != 2:
            result.errors.append(f"Invalid external_id format: {coords} (expected 'lat,lng')")
            return

        lat, lng = parts[0].strip(), parts[1].strip()
        api_key = self.decrypted_config["api_key"]
        use_30 = self.decrypted_config.get("use_onecall_30", False)

        try:
            if use_30:
                data = await self._fetch_onecall_30(client, lat, lng, api_key)
            else:
                data = await self._fetch_weather_25(client, lat, lng, api_key)
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc, result)
            return
        except httpx.RequestError as exc:
            result.errors.append(f"Network error fetching weather for {coords}: {exc}")
            return

        if data:
            data["tent_id"] = str(dm.tent_id)
            data["tenant_id"] = str(self.config.tenant_id)
            data["external_id"] = coords
            result.readings.append(data)

    async def _fetch_weather_25(self, client: httpx.AsyncClient, lat: str, lng: str, api_key: str) -> dict[str, Any]:
        """Fetch using free Weather API 2.5 (current + 5-day forecast)."""
        # Current weather
        resp = await retry_request(
            lambda: client.get(
                "/data/2.5/weather",
                params={"lat": lat, "lon": lng, "appid": api_key, "units": "metric"},
            ),
            description="openweather.weather_2_5",
        )
        resp.raise_for_status()
        current_data = resp.json()

        # 5-day / 3-hour forecast
        resp_fc = await retry_request(
            lambda: client.get(
                "/data/2.5/forecast",
                params={"lat": lat, "lon": lng, "appid": api_key, "units": "metric", "cnt": 40},
            ),
            description="openweather.forecast_2_5",
        )
        resp_fc.raise_for_status()
        forecast_data = resp_fc.json()

        main = current_data.get("main", {})
        wind = current_data.get("wind", {})
        weather_list = current_data.get("weather", [{}])
        weather_code = weather_list[0].get("id") if weather_list else None

        # Build daily summary from 3-hour forecast
        forecast = self._build_daily_forecast(forecast_data)

        return {
            "temperature_c": main.get("temp"),
            "humidity_pct": main.get("humidity"),
            "precipitation_mm": current_data.get("rain", {}).get("1h", 0.0),
            "wind_speed_kmh": (wind.get("speed", 0) * 3.6) if wind.get("speed") else None,
            "uv_index": None,  # Not in 2.5 free
            "weather_code": weather_code,
            "dew_point_c": self._calc_dew_point(main.get("temp"), main.get("humidity")),
            "pressure_hpa": main.get("pressure"),
            "soil_temp_c": None,  # Not in OpenWeather
            "forecast": forecast,
        }

    async def _fetch_onecall_30(self, client: httpx.AsyncClient, lat: str, lng: str, api_key: str) -> dict[str, Any]:
        """Fetch using One Call API 3.0 (current + daily + minutely + alerts)."""
        resp = await retry_request(
            lambda: client.get(
                "/data/3.0/onecall",
                params={"lat": lat, "lon": lng, "appid": api_key, "units": "metric"},
            ),
            description="openweather.onecall_3_0",
        )
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        weather_list = current.get("weather", [{}])
        weather_code = weather_list[0].get("id") if weather_list else None

        forecast = []
        for day in data.get("daily", [])[:7]:
            temp = day.get("temp", {})
            forecast.append(
                {
                    "date": datetime.fromtimestamp(day["dt"], tz=UTC).strftime("%Y-%m-%d") if "dt" in day else None,
                    "temp_max_c": temp.get("max"),
                    "temp_min_c": temp.get("min"),
                    "precipitation_mm": day.get("rain", 0),
                    "wind_max_kmh": (day.get("wind_speed", 0) * 3.6) if day.get("wind_speed") else None,
                    "uv_max": day.get("uvi"),
                    "weather_code": day.get("weather", [{}])[0].get("id") if day.get("weather") else None,
                }
            )

        return {
            "temperature_c": current.get("temp"),
            "humidity_pct": current.get("humidity"),
            "precipitation_mm": current.get("rain", {}).get("1h", 0.0)
            if isinstance(current.get("rain"), dict)
            else 0.0,
            "wind_speed_kmh": (current.get("wind_speed", 0) * 3.6) if current.get("wind_speed") else None,
            "uv_index": current.get("uvi"),
            "weather_code": weather_code,
            "dew_point_c": current.get("dew_point"),
            "pressure_hpa": current.get("pressure"),
            "soil_temp_c": None,
            "forecast": forecast,
        }

    def _build_daily_forecast(self, forecast_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Aggregate 3-hour forecast slots into daily summaries."""
        daily: dict[str, dict[str, Any]] = {}

        for item in forecast_data.get("list", []):
            dt_txt = item.get("dt_txt", "")
            date = dt_txt[:10] if len(dt_txt) >= 10 else None
            if not date:
                continue

            main = item.get("main", {})
            temp = main.get("temp")
            wind_speed = item.get("wind", {}).get("speed", 0)
            rain = item.get("rain", {}).get("3h", 0)

            if date not in daily:
                daily[date] = {
                    "date": date,
                    "temp_max_c": temp,
                    "temp_min_c": temp,
                    "precipitation_mm": 0.0,
                    "wind_max_kmh": 0.0,
                    "uv_max": None,
                    "weather_code": item.get("weather", [{}])[0].get("id") if item.get("weather") else None,
                }

            d = daily[date]
            if temp is not None:
                d["temp_max_c"] = max(d["temp_max_c"] or temp, temp)
                d["temp_min_c"] = min(d["temp_min_c"] or temp, temp)
            d["precipitation_mm"] += rain or 0
            d["wind_max_kmh"] = max(d["wind_max_kmh"] or 0, (wind_speed * 3.6))

        return list(daily.values())[:7]

    # ── Persistence ─────────────────────────────────────────────

    async def persist_readings(
        self,
        session: AsyncSession,
        result: ConnectorResult,
    ) -> int:
        """Write polled readings to WeatherReading."""
        return await write_openweather_readings(session, result.readings)

    # ── Webhook (not supported) ──────────────────────────────────

    async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
        """OpenWeather does not push data; return error."""
        result = ConnectorResult()
        result.errors.append("OpenWeather does not support webhooks. Use polling instead.")
        return result

    # ── Discovery ────────────────────────────────────────────────

    async def discover_devices(self) -> list[DiscoveredDevice]:
        """OpenWeather uses lat/lng from tents — no hardware to discover.

        Returns an empty list; device maps are created manually by
        specifying ``external_id`` = ``"lat,lng"`` from the tent's location.
        """
        return []

    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _calc_dew_point(temp_c: float | None, humidity: float | None) -> float | None:
        """Approximate dew point using Magnus formula."""
        if temp_c is None or humidity is None or humidity <= 0:
            return None
        import math

        a, b = 17.27, 237.7
        alpha = (a * temp_c) / (b + temp_c) + math.log(humidity / 100.0)
        return round((b * alpha) / (a - alpha), 1)

    def _handle_http_error(self, exc: httpx.HTTPStatusError, result: ConnectorResult) -> None:
        """Record an HTTP error in the result."""
        status = exc.response.status_code
        if status == 401:
            result.errors.append("OpenWeather API authentication failed — check your API key")
        elif status == 429:
            result.errors.append("OpenWeather API rate limit exceeded (1000 calls/day on free tier)")
        else:
            result.errors.append(f"OpenWeather API error: HTTP {status}")


# ---------------------------------------------------------------------------
# Utility: write weather readings to DB
# ---------------------------------------------------------------------------


async def write_openweather_readings(
    session: AsyncSession,
    readings: list[dict[str, Any]],
) -> int:
    """Persist polled OpenWeather readings as WeatherReading rows.

    Returns the number of readings written.
    """
    count = 0
    now = datetime.now(UTC)

    for reading in readings:
        tent_id = reading.pop("tent_id", None)
        tenant_id = reading.pop("tenant_id", None)
        reading.pop("external_id", None)
        if not tent_id or not tenant_id:
            continue

        forecast = reading.pop("forecast", None)
        row = WeatherReading(
            tenant_id=tenant_id,
            tent_id=tent_id,
            temperature_c=reading.get("temperature_c"),
            humidity_pct=reading.get("humidity_pct"),
            precipitation_mm=reading.get("precipitation_mm"),
            wind_speed_kmh=reading.get("wind_speed_kmh"),
            uv_index=reading.get("uv_index"),
            weather_code=reading.get("weather_code"),
            dew_point_c=reading.get("dew_point_c"),
            pressure_hpa=reading.get("pressure_hpa"),
            soil_temp_c=reading.get("soil_temp_c"),
            forecast=forecast,
            source="openweather",
            recorded_at=now,
        )
        session.add(row)
        count += 1

    return count
