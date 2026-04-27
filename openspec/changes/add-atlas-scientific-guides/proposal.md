# Change: Add Atlas Scientific Sensor Guides

## Why
Atlas Scientific makes the gold-standard pH, EC, dissolved oxygen, and ORP probes for hydroponics. Their probes connect via I2C to ESP32 boards. Tendril already supports ESP32 over MQTT. We provide wiring guides and ESPHome/Arduino configs so users can build lab-grade sensor rigs that feed directly into Tendril.

## What Changes
- Wiring guides and pin diagrams in `tendril/docs/atlas-scientific/`
- ESPHome YAML templates for Atlas EZO circuits (pH, EC, DO, RTD temperature)
- Arduino/PlatformIO sketch alternative for users not using ESPHome
- Documentation for calibration procedures
- Bill of materials with recommended parts

## Impact
- Affected specs: `integrations-framework`
- No API changes — documentation and templates only
- No breaking changes

## Hardware Covered
- Atlas Scientific EZO pH Circuit + Consumer/Lab Grade pH Probe ($50-85)
- Atlas Scientific EZO EC Circuit + K1.0 Conductivity Probe ($110-140)
- Atlas Scientific EZO DO Circuit + Dissolved Oxygen Probe ($150-260)
- Atlas Scientific EZO RTD Circuit + PT-1000 Temperature Probe ($24-70)
- ESP32 DevKit (~$8)
- Total: ~$250-500 for full hydro sensor suite
