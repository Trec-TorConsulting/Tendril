"""Ecowitt connector — dual-mode (webhook push + cloud API polling).

Supports Ecowitt / Fine Offset weather stations and accessory sensors:
  - GW2000 / GW1100 gateways
  - WH51 soil moisture probes (up to 8 channels)
  - WH31 / WN30 temp & humidity sensors
  - WS90 / WS80 / WS68 weather stations (wind, rain, UV, pressure)
  - WN34 / WN35 leaf wetness sensors

**Webhook mode** (preferred): The gateway POSTs to Tendril via
``/api/v1/integrations/{id}/webhook?secret=<s>`` using its
*Customized Weather Service / Ecowitt* protocol.

**Cloud API polling**: Calls ``api.ecowitt.net/api/v3/device/real_time``
using application_key + api_key + device MAC.  Request units: metric
(``temp_unitid=1, rainfall_unitid=12, wind_speed_unitid=7,
  pressure_unitid=3, solar_irradiance_unitid=16``).

Data routes to:
  - ``WeatherReading`` for station-level weather (temp, humidity, wind,
    rain, UV, pressure, dew point)
  - ``BucketSensorReading`` for per-channel soil sensors mapped to buckets
  - ``TentSensorReading`` for ambient temp/humidity channels mapped to tents
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import BucketSensorReading, TentSensorReading, WeatherReading
from app.integrations.connectors.base import BaseConnector, ConnectorResult, register_connector

logger = logging.getLogger("tendril.integrations.ecowitt")

_TIMEOUT = 20.0
_ECOWITT_API_BASE = "https://api.ecowitt.net"


# ---------------------------------------------------------------------------
# Config schema
# ---------------------------------------------------------------------------


class EcowittConfig(BaseModel):
    """Validated config shape for Ecowitt integrations."""

    mode: str = Field(
        default="webhook",
        description="'webhook' (gateway pushes data) or 'cloud' (poll Ecowitt cloud API)",
    )
    # Cloud mode fields
    application_key: str | None = Field(default=None, description="Ecowitt application key (cloud mode)")
    api_key: str | None = Field(default=None, description="Ecowitt API key (cloud mode)")
    mac: str | None = Field(default=None, description="Device MAC address (cloud mode)")
    # Shared
    base_url: str = Field(default=_ECOWITT_API_BASE, description="Ecowitt API base URL")


# ---------------------------------------------------------------------------
# Discovery response
# ---------------------------------------------------------------------------


class DiscoveredDevice(BaseModel):
    external_id: str
    name: str
    device_type: str  # "weather_station", "soil_sensor", "temp_humidity", "leaf_wetness"
    latest_reading: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Ecowitt cloud API response helpers
# ---------------------------------------------------------------------------


def _extract_value(obj: dict[str, Any] | None, key: str = "value") -> float | None:
    """Safely extract a numeric value from an Ecowitt sensor object."""
    if obj is None:
        return None
    raw = obj.get(key)
    if raw is None:
        return None
    try:
        return float(raw)
    except (ValueError, TypeError):
        return None


def _f_to_c(f: float | None) -> float | None:
    """Convert Fahrenheit to Celsius."""
    if f is None:
        return None
    return round((f - 32) * 5 / 9, 2)


def _inhg_to_hpa(inhg: float | None) -> float | None:
    """Convert inHg to hPa."""
    if inhg is None:
        return None
    return round(inhg * 33.8639, 1)


def _mph_to_kmh(mph: float | None) -> float | None:
    """Convert mph to km/h."""
    if mph is None:
        return None
    return round(mph * 1.60934, 1)


def _in_to_mm(inches: float | None) -> float | None:
    """Convert inches to mm."""
    if inches is None:
        return None
    return round(inches * 25.4, 1)


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


@register_connector
class EcowittConnector(BaseConnector):
    """Dual-mode connector for Ecowitt weather stations and sensors.

    - **Webhook mode**: Parses the Ecowitt *custom server* POST payload.
    - **Cloud mode**: Polls ``api.ecowitt.net/api/v3/device/real_time``.

    Device maps use ``external_id`` to identify what data maps where:
    - ``"weather"`` → tent's WeatherReading (station-level)
    - ``"soil_ch1"`` through ``"soil_ch8"`` → BucketSensorReading
    - ``"temp_humidity_ch1"`` … → TentSensorReading
    - ``"leaf_ch1"`` … → TentSensorReading or BucketSensorReading
    """

    integration_type = "ecowitt"

    def _client(self) -> httpx.AsyncClient:
        base_url = self.decrypted_config.get("base_url", _ECOWITT_API_BASE)
        return httpx.AsyncClient(base_url=base_url, timeout=_TIMEOUT)

    # ── Poll (cloud mode) ────────────────────────────────────────

    async def poll(self) -> ConnectorResult:
        """Fetch latest data from Ecowitt cloud API."""
        result = ConnectorResult()
        mode = self.decrypted_config.get("mode", "webhook")

        if mode == "webhook":
            # In webhook mode, polling is a no-op — data arrives via handle_webhook
            logger.debug("Ecowitt integration %s is in webhook mode; skipping poll", self.config.id)
            return result

        app_key = self.decrypted_config.get("application_key")
        api_key = self.decrypted_config.get("api_key")
        mac = self.decrypted_config.get("mac")

        if not all([app_key, api_key, mac]):
            result.errors.append("Cloud mode requires application_key, api_key, and mac in config")
            return result

        async with self._client() as client:
            try:
                resp = await client.get(
                    "/api/v3/device/real_time",
                    params={
                        "application_key": app_key,
                        "api_key": api_key,
                        "mac": mac,
                        "call_back": "all",
                        "temp_unitid": "1",  # Celsius
                        "pressure_unitid": "3",  # hPa
                        "wind_speed_unitid": "7",  # km/h
                        "rainfall_unitid": "12",  # mm
                        "solar_irradiance_unitid": "16",  # W/m²
                    },
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                self._handle_http_error(exc, result)
                return result
            except httpx.RequestError as exc:
                result.errors.append(f"Network error polling Ecowitt cloud: {exc}")
                return result

            body = resp.json()
            code = body.get("code", -1)
            if code != 0:
                result.errors.append(f"Ecowitt API error: code={code}, msg={body.get('msg', 'unknown')}")
                return result

            data = body.get("data", {})
            self._parse_cloud_data(data, result, metric=True)

        return result

    # ── Webhook (gateway push) ───────────────────────────────────

    async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
        """Parse an Ecowitt custom-server webhook POST.

        The Ecowitt gateway sends form-encoded data with fields like:
        ``tempf``, ``humidity``, ``soilmoisture1``, ``soilbatt1``, etc.
        All temperatures are in °F; rain in inches; wind in mph; pressure in inHg.
        """
        result = ConnectorResult()
        self._parse_webhook_data(payload, result)
        return result

    # ── Persistence ─────────────────────────────────────────────

    async def persist_readings(
        self,
        session: AsyncSession,
        result: ConnectorResult,
    ) -> int:
        """Write polled/webhook readings to sensor tables."""
        return await write_ecowitt_readings(session, result.readings)

    # ── Discovery ────────────────────────────────────────────────

    async def discover_devices(self) -> list[DiscoveredDevice]:
        """Discover available sensor channels from cloud API."""
        devices: list[DiscoveredDevice] = []
        mode = self.decrypted_config.get("mode", "webhook")

        if mode == "webhook":
            # Can't discover from webhook mode — return common defaults
            devices.append(
                DiscoveredDevice(
                    external_id="weather",
                    name="Weather Station",
                    device_type="weather_station",
                )
            )
            for i in range(1, 9):
                devices.append(
                    DiscoveredDevice(
                        external_id=f"soil_ch{i}",
                        name=f"Soil Sensor CH{i}",
                        device_type="soil_sensor",
                    )
                )
            return devices

        app_key = self.decrypted_config.get("application_key")
        api_key = self.decrypted_config.get("api_key")
        mac = self.decrypted_config.get("mac")

        if not all([app_key, api_key, mac]):
            return devices

        async with self._client() as client:
            try:
                resp = await client.get(
                    "/api/v3/device/real_time",
                    params={
                        "application_key": app_key,
                        "api_key": api_key,
                        "mac": mac,
                        "call_back": "all",
                        "temp_unitid": "1",
                        "pressure_unitid": "3",
                        "wind_speed_unitid": "7",
                        "rainfall_unitid": "12",
                    },
                )
                resp.raise_for_status()
                body = resp.json()
                if body.get("code") != 0:
                    return devices
                data = body.get("data", {})
            except (httpx.HTTPStatusError, httpx.RequestError):
                return devices

        # Weather station is always present
        if data.get("outdoor") or data.get("wind") or data.get("rainfall"):
            devices.append(
                DiscoveredDevice(
                    external_id="weather",
                    name="Weather Station",
                    device_type="weather_station",
                )
            )

        # Soil channels
        for i in range(1, 17):
            key = f"soil_ch{i}"
            if data.get(key):
                devices.append(
                    DiscoveredDevice(
                        external_id=key,
                        name=f"Soil Sensor CH{i}",
                        device_type="soil_sensor",
                        latest_reading={"soil_moisture_pct": _extract_value(data[key].get("soilmoisture"))},
                    )
                )

        # Soil EC + temp channels
        for i in range(1, 17):
            key = f"ch_soil_ec_temp_hum{i}"
            if data.get(key):
                ch_data = data[key]
                devices.append(
                    DiscoveredDevice(
                        external_id=key,
                        name=f"Soil EC+Temp CH{i}",
                        device_type="soil_sensor",
                        latest_reading={
                            "soil_moisture_pct": _extract_value(ch_data.get("soilmoisture")),
                            "soil_temp_c": _extract_value(ch_data.get("temperature")),
                            "ec_us_cm": _extract_value(ch_data.get("ec")),
                        },
                    )
                )

        # Temp & humidity channels
        for i in range(1, 9):
            key = f"temp_and_humidity_ch{i}"
            if data.get(key):
                devices.append(
                    DiscoveredDevice(
                        external_id=key,
                        name=f"Temp & Humidity CH{i}",
                        device_type="temp_humidity",
                    )
                )

        # Leaf wetness channels
        for i in range(1, 9):
            key = f"leaf_ch{i}"
            if data.get(key):
                devices.append(
                    DiscoveredDevice(
                        external_id=key,
                        name=f"Leaf Wetness CH{i}",
                        device_type="leaf_wetness",
                    )
                )

        return devices

    # ── Cloud API data parsing ───────────────────────────────────

    def _parse_cloud_data(self, data: dict[str, Any], result: ConnectorResult, *, metric: bool) -> None:
        """Parse Ecowitt cloud ``/real_time`` response ``data`` object.

        When ``metric=True``, values are already in °C / hPa / km/h / mm.
        """
        dm_by_ext = {dm.external_id: dm for dm in self.device_maps if dm.enabled}

        # --- Weather station (maps to WeatherReading) ---
        weather_dm = dm_by_ext.get("weather")
        if weather_dm and weather_dm.tent_id:
            outdoor = data.get("outdoor", {})
            wind = data.get("wind", {})
            rainfall = data.get("rainfall", {}) or data.get("rainfall_piezo", {})
            solar = data.get("solar_and_uvi", {})
            pressure = data.get("pressure", {})

            temp_c = _extract_value(outdoor.get("temperature"))
            humidity = _extract_value(outdoor.get("humidity"))
            dew_c = _extract_value(outdoor.get("dew_point"))
            wind_kmh = _extract_value(wind.get("wind_speed"))
            rain_mm = _extract_value(rainfall.get("daily"))
            uvi = _extract_value(solar.get("uvi"))
            press_hpa = _extract_value(pressure.get("relative"))

            # If not metric, convert
            if not metric:
                temp_c = _f_to_c(temp_c)
                dew_c = _f_to_c(dew_c)
                wind_kmh = _mph_to_kmh(wind_kmh)
                rain_mm = _in_to_mm(rain_mm)
                press_hpa = _inhg_to_hpa(press_hpa)

            result.readings.append(
                {
                    "target": "weather",
                    "tent_id": str(weather_dm.tent_id),
                    "tenant_id": str(self.config.tenant_id),
                    "external_id": "weather",
                    "temperature_c": temp_c,
                    "humidity_pct": humidity,
                    "precipitation_mm": rain_mm,
                    "wind_speed_kmh": wind_kmh,
                    "uv_index": uvi,
                    "dew_point_c": dew_c,
                    "pressure_hpa": press_hpa,
                    "soil_temp_c": None,
                }
            )

        # --- Soil sensors (maps to BucketSensorReading) ---
        for ext_id, dm in dm_by_ext.items():
            if not dm.bucket_id:
                continue

            # Basic soil moisture channels: soil_ch1 .. soil_ch16
            if ext_id.startswith("soil_ch"):
                ch_data = data.get(ext_id, {})
                if not ch_data:
                    continue
                moisture = _extract_value(ch_data.get("soilmoisture"))
                if moisture is not None:
                    result.readings.append(
                        {
                            "target": "bucket",
                            "bucket_id": str(dm.bucket_id),
                            "tenant_id": str(self.config.tenant_id),
                            "external_id": ext_id,
                            "soil_moisture": moisture,
                        }
                    )

            # EC + temp + moisture channels: ch_soil_ec_temp_hum1 .. 16
            elif ext_id.startswith("ch_soil_ec_temp_hum"):
                ch_data = data.get(ext_id, {})
                if not ch_data:
                    continue
                fields: dict[str, Any] = {}
                sm = _extract_value(ch_data.get("soilmoisture"))
                if sm is not None:
                    fields["soil_moisture"] = sm
                temp_val = _extract_value(ch_data.get("temperature"))
                if temp_val is not None:
                    fields["soil_temp"] = temp_val if metric else _f_to_c(temp_val)
                ec_val = _extract_value(ch_data.get("ec"))
                if ec_val is not None:
                    fields["ec"] = ec_val
                if fields:
                    result.readings.append(
                        {
                            "target": "bucket",
                            "bucket_id": str(dm.bucket_id),
                            "tenant_id": str(self.config.tenant_id),
                            "external_id": ext_id,
                            **fields,
                        }
                    )

            # Leaf wetness mapped to a bucket
            elif ext_id.startswith("leaf_ch"):
                ch_data = data.get(ext_id, {})
                if not ch_data:
                    continue
                wetness = _extract_value(ch_data.get("leaf_wetness"))
                if wetness is not None:
                    result.readings.append(
                        {
                            "target": "bucket",
                            "bucket_id": str(dm.bucket_id),
                            "tenant_id": str(self.config.tenant_id),
                            "external_id": ext_id,
                            "soil_moisture": wetness,  # Closest BucketSensorReading field
                        }
                    )

        # --- Temp & humidity channels (maps to TentSensorReading) ---
        for ext_id, dm in dm_by_ext.items():
            if not (dm.tent_id and not dm.bucket_id):
                continue
            if ext_id == "weather":
                continue  # Already handled

            if ext_id.startswith("temp_and_humidity_ch"):
                ch_data = data.get(ext_id, {})
                if not ch_data:
                    continue
                temp_val = _extract_value(ch_data.get("temperature"))
                hum_val = _extract_value(ch_data.get("humidity"))
                if metric:
                    temp_f = (temp_val * 9 / 5 + 32) if temp_val is not None else None
                else:
                    temp_f = temp_val
                    temp_val = _f_to_c(temp_val)

                if temp_f is not None or hum_val is not None:
                    reading: dict[str, Any] = {
                        "target": "tent",
                        "tent_id": str(dm.tent_id),
                        "tenant_id": str(self.config.tenant_id),
                        "external_id": ext_id,
                    }
                    if temp_f is not None:
                        reading["ambient_temp_f"] = round(temp_f, 1)
                    if hum_val is not None:
                        reading["ambient_humidity"] = hum_val
                    result.readings.append(reading)

    # ── Webhook data parsing ─────────────────────────────────────

    def _parse_webhook_data(self, payload: dict[str, Any], result: ConnectorResult) -> None:
        """Parse Ecowitt gateway custom-server POST payload.

        The gateway sends form-encoded (or JSON) data with imperial units:
        tempf, humidity, soilmoisture1..8, windspeedmph, dailyrainin,
        baromrelin, uv, solarradiation, etc.
        """
        dm_by_ext = {dm.external_id: dm for dm in self.device_maps if dm.enabled}

        # --- Weather station ---
        weather_dm = dm_by_ext.get("weather")
        if weather_dm and weather_dm.tent_id:
            temp_f = self._safe_float(payload.get("tempf"))
            humidity = self._safe_float(payload.get("humidity"))
            wind_mph = self._safe_float(payload.get("windspeedmph"))
            daily_rain_in = self._safe_float(payload.get("dailyrainin"))
            uv_idx = self._safe_float(payload.get("uv"))
            baro_inhg = self._safe_float(payload.get("baromrelin"))
            dew_f = self._safe_float(payload.get("dewptf"))

            result.readings.append(
                {
                    "target": "weather",
                    "tent_id": str(weather_dm.tent_id),
                    "tenant_id": str(self.config.tenant_id),
                    "external_id": "weather",
                    "temperature_c": _f_to_c(temp_f),
                    "humidity_pct": humidity,
                    "precipitation_mm": _in_to_mm(daily_rain_in),
                    "wind_speed_kmh": _mph_to_kmh(wind_mph),
                    "uv_index": uv_idx,
                    "dew_point_c": _f_to_c(dew_f),
                    "pressure_hpa": _inhg_to_hpa(baro_inhg),
                    "soil_temp_c": None,
                }
            )

        # --- Soil sensors (webhook uses soilmoisture1..8) ---
        for i in range(1, 9):
            ext_id = f"soil_ch{i}"
            dm = dm_by_ext.get(ext_id)
            if not dm or not dm.bucket_id:
                continue
            moisture = self._safe_float(payload.get(f"soilmoisture{i}"))
            if moisture is not None:
                result.readings.append(
                    {
                        "target": "bucket",
                        "bucket_id": str(dm.bucket_id),
                        "tenant_id": str(self.config.tenant_id),
                        "external_id": ext_id,
                        "soil_moisture": moisture,
                    }
                )

        # --- Temp & humidity channels (webhook uses temp1f..temp8f, humidity1..humidity8) ---
        for i in range(1, 9):
            ext_id = f"temp_and_humidity_ch{i}"
            dm = dm_by_ext.get(ext_id)
            if not dm or not dm.tent_id or dm.bucket_id:
                continue
            temp_f = self._safe_float(payload.get(f"temp{i}f"))
            hum = self._safe_float(payload.get(f"humidity{i}"))
            if temp_f is not None or hum is not None:
                reading: dict[str, Any] = {
                    "target": "tent",
                    "tent_id": str(dm.tent_id),
                    "tenant_id": str(self.config.tenant_id),
                    "external_id": ext_id,
                }
                if temp_f is not None:
                    reading["ambient_temp_f"] = round(temp_f, 1)
                if hum is not None:
                    reading["ambient_humidity"] = hum
                result.readings.append(reading)

        # --- Leaf wetness (webhook uses leafwetness_ch1..leafwetness_ch8) ---
        for i in range(1, 9):
            ext_id = f"leaf_ch{i}"
            dm = dm_by_ext.get(ext_id)
            if not dm or not dm.bucket_id:
                continue
            wetness = self._safe_float(payload.get(f"leafwetness_ch{i}"))
            if wetness is not None:
                result.readings.append(
                    {
                        "target": "bucket",
                        "bucket_id": str(dm.bucket_id),
                        "tenant_id": str(self.config.tenant_id),
                        "external_id": ext_id,
                        "soil_moisture": wetness,
                    }
                )

    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _safe_float(val: Any) -> float | None:
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    def _handle_http_error(self, exc: httpx.HTTPStatusError, result: ConnectorResult) -> None:
        status = exc.response.status_code
        if status == 401:
            result.errors.append("Ecowitt cloud API authentication failed — check application_key and api_key")
        elif status == 429:
            result.errors.append("Ecowitt cloud API rate limit exceeded")
        else:
            result.errors.append(f"Ecowitt cloud API error: HTTP {status}")


# ---------------------------------------------------------------------------
# Utility: write Ecowitt readings to DB
# ---------------------------------------------------------------------------


async def write_ecowitt_readings(
    session: AsyncSession,
    readings: list[dict[str, Any]],
) -> int:
    """Persist Ecowitt readings to the appropriate sensor tables.

    Returns the number of readings written.
    """
    count = 0
    now = datetime.now(UTC)

    for reading in readings:
        target = reading.pop("target", None)
        external_id = reading.pop("external_id", None)
        tenant_id = reading.pop("tenant_id", None)

        if target == "weather":
            tent_id = reading.pop("tent_id", None)
            if not tent_id or not tenant_id:
                continue
            row = WeatherReading(
                tenant_id=tenant_id,
                tent_id=tent_id,
                temperature_c=reading.get("temperature_c"),
                humidity_pct=reading.get("humidity_pct"),
                precipitation_mm=reading.get("precipitation_mm"),
                wind_speed_kmh=reading.get("wind_speed_kmh"),
                uv_index=reading.get("uv_index"),
                dew_point_c=reading.get("dew_point_c"),
                pressure_hpa=reading.get("pressure_hpa"),
                soil_temp_c=reading.get("soil_temp_c"),
                source="ecowitt",
                recorded_at=now,
            )
            session.add(row)
            count += 1

        elif target == "tent":
            tent_id = reading.pop("tent_id", None)
            if not tent_id or not tenant_id:
                continue
            row = TentSensorReading(
                tenant_id=tenant_id,
                tent_id=tent_id,
                device_id=f"ecowitt:{external_id}",
                recorded_at=now,
                **{k: v for k, v in reading.items() if k in {"ambient_temp_f", "ambient_humidity"}},
            )
            session.add(row)
            count += 1

        elif target == "bucket":
            bucket_id = reading.pop("bucket_id", None)
            if not bucket_id or not tenant_id:
                continue
            allowed = {"soil_moisture", "soil_temp", "ec"}
            row = BucketSensorReading(
                tenant_id=tenant_id,
                bucket_id=bucket_id,
                device_id=f"ecowitt:{external_id}",
                recorded_at=now,
                **{k: v for k, v in reading.items() if k in allowed},
            )
            session.add(row)
            count += 1

    return count
