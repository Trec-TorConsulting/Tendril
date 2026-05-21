## 1. Schema Extension
- [x] 1.1 Add `vpd`, `co2`, `lux`, `dew_point_f`, `par_ppfd`, `air_pressure`, `voc` columns to `TentSensorReading` model
- [x] 1.2 Create Alembic migration `0022_extend_tent_sensor_readings.py` with RLS-safe ALTER TABLE
- [x] 1.3 Update `_TENT_SENSOR_FIELDS` allowlist in `api/app/mqtt/handlers.py`
- [x] 1.4 Run migration and verify columns exist

## 2. Connector Implementation
- [x] 2.1 Create `api/app/integrations/connectors/pulse.py` with `PulseConnector(BaseConnector)`
- [x] 2.2 Implement `PulseConfig` Pydantic schema for config validation (api_key, base_url)
- [x] 2.3 Implement `poll()` — calls `GET /all-devices`, maps to `TentSensorReading` per device
- [x] 2.4 Implement Hub sensor polling — calls `GET /sensors/{id}/recent-data`, maps to `BucketSensorReading`
- [x] 2.5 Implement `handle_webhook()` — returns not-supported (Pulse is poll-only)
- [x] 2.6 Implement `discover_devices()` — fetches device + sensor lists for auto-discovery
- [x] 2.7 Register connector with `@register_connector` decorator
- [x] 2.8 Import connector in `__init__.py` for auto-registration

## 3. Auto-Discovery API
- [x] 3.1 Add `discover_devices()` optional method to `BaseConnector`
- [x] 3.2 Add `POST /v1/integrations/{id}/discover` route in `api/app/integrations/routes.py`
- [x] 3.3 Return structured device list with external_id, name, type, latest reading preview

## 4. Validation & Tests
- [x] 4.1 Unit tests for `PulseConnector.poll()` with mocked API responses (success, partial, error)
- [x] 4.2 Unit tests for Hub sensor polling with mocked responses
- [x] 4.3 Unit tests for `discover_devices()` with mocked responses
- [x] 4.4 Unit tests for `PulseConfig` validation (valid, missing key, invalid URL)
- [x] 4.5 Unit tests for rate limit / error handling (401, 429, 500, timeout)
- [ ] 4.6 Integration test: full poll cycle writes correct sensor readings to DB
- [x] 4.7 Verify extended `_TENT_SENSOR_FIELDS` allowlist works with MQTT handler
- [x] 4.8 Run full test suite — all existing tests still pass
