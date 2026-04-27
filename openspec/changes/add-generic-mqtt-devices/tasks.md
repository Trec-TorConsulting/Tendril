## 1. Connector
- [ ] 1.1 Create `tendril/api/app/integrations/connectors/mqtt_generic.py`
- [ ] 1.2 Implement topic subscription management (add/remove topics when configs change)
- [ ] 1.3 Implement configurable JSON field mapping (e.g., `{"temperature": "ambient_temp_f"}`)
- [ ] 1.4 Update MQTT client to subscribe to generic device topics alongside Tendril device topics

## 2. Frontend
- [ ] 2.1 Add Generic MQTT option to integration type selector
- [ ] 2.2 Create config form (topic pattern, payload field mapper, target tent/bucket)
- [ ] 2.3 Add "Test" button that subscribes and shows last received message for verification

## 3. Validation
- [ ] 3.1 Test with Tasmota smart plug publishing power data
- [ ] 3.2 Test with custom ESP32 publishing arbitrary JSON
- [ ] 3.3 Verify data flows into correct tent/bucket sensor tables
