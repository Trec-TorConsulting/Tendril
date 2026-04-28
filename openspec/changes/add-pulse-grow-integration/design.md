## Context
Pulse Grow is the first concrete connector implementation for the integrations framework. This design establishes patterns that all future connectors will follow. It also requires extending the `tent_sensor_readings` schema to accommodate richer environmental data beyond temperature and humidity.

## Goals / Non-Goals
- **Goals**: Working Pulse connector with auto-discovery, extended sensor schema, comprehensive tests, rate-limit-aware polling
- **Non-Goals**: Frontend UI (separate proposal), historical data backfill, real-time WebSocket streaming, Pulse webhook support (they don't offer it)

## Decisions

### 1. Schema Extension: New TentSensorReading Columns
**Decision**: Add 7 nullable float columns to `tent_sensor_readings` via Alembic migration.

| Column | Type | Source | Why |
|--------|------|--------|-----|
| `vpd` | Float | Pulse, future sensors | VPD is the #1 optimization metric for growers |
| `co2` | Float | Pulse Pro/Hub, CO2 sensors | Critical for sealed room grows |
| `lux` | Float | Pulse, light sensors | Light intensity tracking |
| `dew_point_f` | Float | Pulse, calculated | Mold/condensation prevention |
| `par_ppfd` | Float | Pulse Pro, PAR meters | Photosynthetic light measurement |
| `air_pressure` | Float | Pulse, weather stations | Barometric pressure affects VPD calculations |
| `voc` | Float | Pulse, air quality sensors | Volatile organic compound levels |

**Why not JSONB?** These are core environmental metrics that need indexing, aggregation queries (AVG, MIN, MAX for charts), and typed validation. Every future tent sensor integration will produce the same fields. JSONB would require `->>'field'::float` casts everywhere.

**Why not a separate table?** These readings are temporally and logically co-located with temp/humidity. A single INSERT per reading is simpler and faster than INSERT + INSERT across two tables.

### 2. Polling Strategy: Bulk /all-devices Endpoint
**Decision**: Use `GET /all-devices` for polling instead of per-device calls.

- Single HTTP request returns all devices with latest readings
- Parse response, match `deviceId` to `IntegrationDeviceMap.external_id`
- Write one `TentSensorReading` per mapped device
- **Cost**: 1 API call + N datapoints (where N = number of devices) per poll cycle
- At 5-min intervals: ~288 calls/day + ~576 dp/day for 2 devices (well within Hobbyist 4,800 dp/day)

### 3. Hub Sensors: Separate /sensors/ API Path
**Decision**: Hub sensors (VWC probes, pH/EC) use different API endpoints. Poll them alongside devices in the same cycle.

- `GET /sensors/ids` → list sensor IDs
- `GET /sensors/{id}/recent-data` → latest reading
- Hub sensors map to `BucketSensorReading` via `IntegrationDeviceMap` with `bucket_id` set
- Sensor type determines which columns to write (VWC → `soil_moisture`, pH → `ph`, EC → `ec`)

### 4. Auto-Discovery Endpoint
**Decision**: Add `POST /v1/integrations/{id}/discover` — a reusable pattern for all connectors.

- Calls Pulse API to fetch device + sensor lists
- Returns structured response with `external_id`, `name`, `type`, `latest_reading`
- Frontend uses this to present a device mapping UI
- Implemented in `BaseConnector.discover_devices()` (optional abstract method)
- Not all connectors support discovery; returns 501 if not implemented

### 5. Config Schema Validation
**Decision**: Each connector type defines a Pydantic model for its config fields. Validated on create/update.

```python
class PulseConfig(BaseModel):
    api_key: str = Field(..., min_length=10, description="Pulse Grow API key")

    # Optional overrides
    base_url: str = Field(default="https://api.pulsegrow.com", description="API base URL")
```

The `IntegrationConfig.config` column stores the encrypted JSON of this model. Decrypted and validated at runtime.

### 6. Error Handling & Retry
**Decision**: Follow defensive patterns:
- `httpx.AsyncClient` with 30s timeout, connection pooling
- HTTP 401 → log "invalid API key", increment `error_count`, do NOT retry
- HTTP 429 → respect `Retry-After` header if present, log warning
- HTTP 5xx / network error → increment `error_count`, retry on next poll cycle
- After 10 consecutive errors, log a WARN but do NOT auto-disable (user must manually disable)
- All errors captured in `ConnectorResult.errors` and persisted in `IntegrationSyncLog`

### 7. MQTT Handler Field Allowlist Update
**Decision**: Extend `_TENT_SENSOR_FIELDS` in `handlers.py` to include the new columns so ESP32 devices can also report these fields via MQTT.

```python
_TENT_SENSOR_FIELDS = {
    "ambient_temp_f", "ambient_humidity",
    "vpd", "co2", "lux", "dew_point_f", "par_ppfd", "air_pressure", "voc",
}
```

## Risks / Trade-offs
- **Schema migration on production**: All new columns are nullable with no defaults, so `ALTER TABLE ADD COLUMN` is fast and non-locking in PostgreSQL.
- **Pulse API stability**: No versioning visible — the API is at `/` not `/v1/`. We pin to current response shapes and validate defensively.
- **Rate limit enforcement**: We trust user-configured interval but enforce minimum 60s server-side. We do NOT track actual datapoint consumption (Pulse does that).

## Migration Plan
1. Alembic migration `0021_extend_tent_sensor_readings.py` adds 7 columns
2. Update `TentSensorReading` model with new mapped columns
3. Update `_TENT_SENSOR_FIELDS` allowlist
4. Deploy connector — no flag needed, connector only activates when user creates a Pulse integration
5. Rollback: drop columns (no data loss for existing readings)

## Open Questions
- None. Pulse API is well-documented and publicly accessible.
