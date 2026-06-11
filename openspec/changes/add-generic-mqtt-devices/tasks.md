## 1. Connector Implementation
- [x] 1.1 Create `api/app/integrations/connectors/mqtt_generic.py` with `@register_connector` decorator
- [x] 1.2 Implement `handle_webhook()` — parse incoming MQTT payload using device map's `sensor_mapping`
- [x] 1.3 Implement field mapping engine: flat JSON, dot-notation nested paths, numeric coercion, unit conversion hooks
- [x] 1.4 Implement `persist_readings()` — route mapped fields to `TentSensorReading` or `BucketSensorReading`
- [x] 1.5 Implement `discover_devices()` — no-op (generic devices aren't discoverable)
- [x] 1.6 Implement `poll()` — no-op (MQTT is push, not poll)

## 2. MQTT Subscription Management
- [x] 2.1 Create `api/app/integrations/mqtt_subscriptions.py` — load active mqtt_generic topics from DB
- [x] 2.2 Update MQTT client to subscribe to generic device topics on startup
- [x] 2.3 Add message routing: match incoming topic → integration config → device map → connector
- [x] 2.4 Handle dynamic topic changes (new integration created/deleted → update subscriptions)

## 3. API Enhancements
- [x] 3.1 Add topic validation on integration create/update (prevent dangerous wildcards like `#`)
- [ ] 3.2 Add `POST /v1/integrations/{id}/test-mqtt` endpoint — subscribe to topic, return last message

## 4. Frontend
- [x] 4.1 Add "Generic MQTT" option to integration type selector
- [x] 4.2 Create config form: topic pattern, payload preview, field mapper UI
- [x] 4.3 Add device map form with sensor_mapping field builder (source field → Tendril field dropdown)

## 5. Tests
- [x] 5.1 Unit tests for field mapping engine (flat, nested, coercion, missing fields, invalid JSON)
- [x] 5.2 Unit tests for topic matching and message routing
- [x] 5.3 Integration test: mock MQTT message → persist to sensor table
- [x] 5.4 API test: create mqtt_generic integration, verify config validation
