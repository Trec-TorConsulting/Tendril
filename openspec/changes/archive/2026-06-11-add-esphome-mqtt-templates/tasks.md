## 1. Templates
- [ ] 1.1 Create `tendril/esphome-templates/ambient-kit.yaml` — BME280 temp/humidity
- [ ] 1.2 Create `tendril/esphome-templates/dwc-kit.yaml` — Atlas pH + EC + DS18B20 + BME280
- [ ] 1.3 Create `tendril/esphome-templates/soil-kit.yaml` — Capacitive moisture + DS18B20 + BME280
- [ ] 1.4 Create `tendril/esphome-templates/advanced-hydro-kit.yaml` — Full hydro sensor suite
- [ ] 1.5 Create shared `tendril/esphome-templates/common/mqtt-base.yaml` for MQTT connection + topic structure

## 2. Documentation
- [ ] 2.1 Create `tendril/esphome-templates/README.md` with setup guide
- [ ] 2.2 Include wiring diagrams (text-based pin descriptions)
- [ ] 2.3 Document how to register device in Tendril and pair

## 3. MQTT Compatibility
- [ ] 3.1 Verify ESPHome templates publish to `t/{tenant_id}/d/{device_id}/sensor/readings` topic
- [ ] 3.2 Verify payload JSON matches existing MQTT handler expected format
- [ ] 3.3 Test end-to-end: ESPHome device → EMQX → Tendril sensor tables

## 4. Frontend
- [ ] 4.1 Add "ESPHome Device" option to device registration flow
- [ ] 4.2 Show MQTT credentials and topic info for copy/paste into ESPHome config
