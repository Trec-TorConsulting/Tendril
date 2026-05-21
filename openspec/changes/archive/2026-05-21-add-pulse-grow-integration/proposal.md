# Change: Add Pulse Grow Integration

## Why
Pulse Grow monitors (Pulse One, Pulse Pro, Pulse Hub) are the most popular grow room monitors with 1000+ reviews. Their free REST API at `api.pulsegrow.com` provides temperature, humidity, VPD, CO2, lux, PAR/PPFD, dew point, air pressure, VOC, and spectral data. This is the first concrete connector implementation for the integrations framework — it establishes the enterprise-grade pattern all future connectors will follow.

## What Changes
- **Alembic migration**: Extend `tent_sensor_readings` with `vpd`, `co2`, `lux`, `dew_point_f`, `par_ppfd`, `air_pressure`, `voc` columns
- **Pulse connector**: `api/app/integrations/connectors/pulse.py` implementing `BaseConnector`
- **Auto-discovery endpoint**: `POST /v1/integrations/{id}/discover` fetches Pulse devices/sensors for user mapping
- **Pydantic config schema**: Validates Pulse-specific config (API key required)
- **Hub sensor support**: Maps Pulse Hub external sensors (VWC, pH, EC) to `BucketSensorReading`
- **Rate limit awareness**: Default 5-min poll interval, user-configurable (min 60s), respects tier limits
- **Comprehensive test suite**: Unit tests with mocked API responses

## Impact
- Affected specs: `integrations-framework` (MODIFIED: extended sensor columns)
- Affected code: `api/app/grows/models.py`, `api/app/integrations/connectors/`, `api/app/mqtt/handlers.py`
- Depends on: `add-integrations-framework` (already implemented)
- **Additive migration** — no breaking changes, all new columns nullable

## Integration Details

### Pulse API (v1) — https://api.pulsegrow.com
- **Auth**: `x-api-key` header. Keys scoped per-grow (one key = one grow room). Generated at `app.pulsegrow.com/account`.
- **Rate Limits**: Hobbyist 4,800 dp/day, Enthusiast 24,000, Pro 120,000. Each datapoint counts.

### Endpoints Used
| Endpoint | Purpose |
|----------|---------|
| `GET /all-devices` | Discovery — lists all Pulse devices + Hub sensors with latest data |
| `GET /devices/ids` | List device IDs for the grow |
| `GET /devices/details` | Device metadata (name, type, thresholds, day/night schedule) |
| `GET /devices/{id}/recent-data` | Latest reading for one device (1 dp) |
| `GET /sensors/ids` | List Hub sensor IDs |
| `GET /sensors/{id}/recent-data` | Latest Hub sensor reading (1 dp) |
| `GET /sensors/{id}/details` | Sensor metadata (name, type, hub assignment) |

### Data Fields — Pulse Device (Pulse One / Pro)
| Pulse Field | Type | Tendril Column | Table |
|-------------|------|---------------|-------|
| `temperatureF` | float | `ambient_temp_f` | TentSensorReading |
| `humidityRh` | float | `ambient_humidity` | TentSensorReading |
| `vpd` | float | `vpd` | TentSensorReading (NEW) |
| `co2` | int | `co2` | TentSensorReading (NEW) |
| `lightLux` | float | `lux` | TentSensorReading (NEW) |
| `dpF` | float | `dew_point_f` | TentSensorReading (NEW) |
| `par` | float | `par_ppfd` | TentSensorReading (NEW) |
| `airPressure` | float | `air_pressure` | TentSensorReading (NEW) |
| `voc` | int | `voc` | TentSensorReading (NEW) |

### Data Fields — Hub Sensors (VWC Kit, pH/EC probes)
Hub sensors use the `/sensors/` API and map to `BucketSensorReading` via `sensor_mapping` in `IntegrationDeviceMap`.

### Polling Strategy
- Default interval: 300s (5 min) — uses ~576 dp/day for 2 devices (well within Hobbyist tier)
- User-configurable: minimum 60s
- Uses `GET /all-devices` for bulk poll (1 call gets all devices with latest data) vs per-device calls
- Efficient: single HTTP call per poll cycle, parse response for all mapped devices
