## 1. Documentation
- [x] 1.1 Create `docs/atlas-scientific/README.md` — overview, BOM, wiring diagrams
- [x] 1.2 Create wiring guide for ESP32 + Atlas EZO I2C daisy chain (in README.md)
- [x] 1.3 Create calibration guide — `docs/atlas-scientific/calibration.md` (pH 3-point, EC 2-point, DO, RTD)

## 2. Templates
- [x] 2.1 Create ESPHome YAML for Atlas pH + EC + RTD — `docs/atlas-scientific/esphome-template.md` + API template `atlas_ph_ec_rtd`
- [x] 2.2 Create ESPHome YAML for Atlas DO sensor (full suite variant) — API template `atlas_full_suite`
- [x] 2.3 Create Arduino/PlatformIO header — `esp32/hydro-monitor/src/atlas_sensors.h`
- [x] 2.4 All templates publish to Tendril MQTT topic structure (`t/{tenant}/d/{device}/sensor/hydro`)

## 3. Validation
- [x] 3.1 ESPHome templates registered in API (`reference/esphome_templates.py`) and generate valid YAML
- [x] 3.2 MQTT payload format matches Tendril handler expectations (JSON with ph, ec, ppm, water_temp_f, do_mg_l)
