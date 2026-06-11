# Change: Add ESPHome MQTT Templates

## Why
ESPHome is the most popular YAML-configured firmware for ESP32/ESP8266. Users can flash sensor rigs with zero coding. Tendril already has full MQTT infrastructure via EMQX. By publishing ESPHome YAML templates that publish to Tendril's topic structure, users can build $30 sensor rigs and connect instantly — zero API changes needed.

## What Changes
- ESPHome YAML templates in `tendril/esphome-templates/` for common grow sensors
- Templates for: pH (Atlas Scientific), EC (Atlas Scientific), temperature (DS18B20), humidity (BME280/DHT22), soil moisture (capacitive analog)
- Documentation for wiring, flashing, and connecting to Tendril
- MQTT topic structure compatible with existing handler

## Impact
- Affected specs: `integrations-framework`
- No API changes — leverages existing MQTT worker
- No breaking changes
- Templates are documentation/config files only

## Sensor Kits Covered
- **DWC Kit**: Atlas pH + EC + DS18B20 water temp + BME280 ambient
- **Soil Kit**: Capacitive soil moisture + DS18B20 soil temp + BME280 ambient
- **Ambient-Only Kit**: BME280 temp/humidity (cheapest, ~$8)
- **Advanced Hydro Kit**: Atlas pH + EC + DO + DS18B20 + BME280 + float switch (water level)
