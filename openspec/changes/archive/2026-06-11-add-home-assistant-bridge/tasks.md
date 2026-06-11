## 1. Connector
- [x] 1.1 Create `api/app/integrations/connectors/home_assistant.py`
- [x] 1.2 Implement `discover_devices()` — fetch all HA entities, filter to sensor/switch/climate types
- [x] 1.3 Implement `poll()` — fetch mapped entity states and write to sensor tables
- [x] 1.4 Implement `call_service(domain, service, data)` — call HA services for automation triggers
- [x] 1.5 Map HA entity attributes to Tendril sensor columns (temperature, humidity, power, etc.)
- [x] 1.6 Implement `persist_readings()` — write polled data to TentSensorReading/BucketSensorReading
- [x] 1.7 Implement `handle_webhook()` — accept HA automation webhook pushes
- [x] 1.8 Implement `test_connection()` — verify HA URL and token
- [x] 1.9 Auto-map by device_class (temperature→ambient_temp_f, humidity→ambient_humidity, etc.)
- [x] 1.10 Handle °C→°F unit conversion for temperature entities

## 2. Frontend
- [x] 2.1 Add Home Assistant option to integration type selector (already present)
- [x] 2.2 Create HA config form (host URL, access token) — already present with field definitions
- [ ] 2.3 Create entity browser that shows all HA entities with type filtering
- [ ] 2.4 Create entity-to-tent/bucket mapping UI
- [ ] 2.5 Add HA action selector to automation rule actions (e.g., "Turn on HA switch")

## 3. Tests
- [x] 3.1 Unit tests for poll() — success, entity not found, unavailable state, celsius conversion
- [x] 3.2 Unit tests for handle_webhook() — matched entity, missing entity_id, unmatched entity
- [x] 3.3 Unit tests for call_service()
- [x] 3.4 Unit tests for discover_devices() — domain filtering
- [x] 3.5 Unit tests for test_connection()
- [x] 3.6 Unit tests for device_class auto-mapping
