# Atlas Scientific ESPHome Template

ESPHome YAML config for Atlas Scientific EZO circuits on ESP32.
Copy this template and customize for your setup.

---

## Full Config (pH + EC + RTD)

```yaml
# ESPHome config for Atlas Scientific EZO sensors
# Publishes to Tendril MQTT: t/{tenant_id}/d/{device_id}/sensor/hydro

esphome:
  name: atlas-hydro-monitor
  friendly_name: "Atlas Hydro Monitor"

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "Atlas Monitor Fallback"
    password: "tendril-setup"

mqtt:
  broker: !secret mqtt_host
  port: 8883
  username: !secret mqtt_user
  password: !secret mqtt_password
  topic_prefix: "t/${tenant_id}/d/${device_id}"
  discovery: false
  # Publish sensor bundle as single JSON payload
  on_json_message:
    topic: "t/${tenant_id}/d/${device_id}/cmd"
    then:
      - lambda: |-
          // Handle calibration commands from Tendril
          std::string cmd = x["command"].as<std::string>();
          ESP_LOGI("atlas", "Received command: %s", cmd.c_str());

logger:
  level: INFO

ota:
  platform: esphome

i2c:
  sda: GPIO21
  scl: GPIO22
  scan: true

sensor:
  # ─── Atlas EZO RTD (Temperature) ───────────────────────────
  - platform: ezo
    id: atlas_rtd
    name: "Water Temperature"
    address: 0x66
    unit_of_measurement: "°C"
    accuracy_decimals: 1
    update_interval: 30s
    state_class: measurement

  # Convert to Fahrenheit for Tendril
  - platform: template
    name: "Water Temperature F"
    id: water_temp_f
    unit_of_measurement: "°F"
    accuracy_decimals: 1
    lambda: |-
      if (id(atlas_rtd).state == 0) return NAN;
      return id(atlas_rtd).state * 9.0 / 5.0 + 32.0;
    update_interval: 30s
    state_class: measurement

  # ─── Atlas EZO pH ──────────────────────────────────────────
  - platform: ezo
    id: atlas_ph
    name: "pH"
    address: 0x63
    unit_of_measurement: "pH"
    accuracy_decimals: 2
    update_interval: 30s
    state_class: measurement

  # ─── Atlas EZO EC ──────────────────────────────────────────
  - platform: ezo
    id: atlas_ec
    name: "EC"
    address: 0x64
    unit_of_measurement: "µS/cm"
    accuracy_decimals: 0
    update_interval: 30s
    state_class: measurement

  # Convert µS/cm to mS/cm and PPM for Tendril
  - platform: template
    name: "EC mS"
    id: ec_ms
    unit_of_measurement: "mS/cm"
    accuracy_decimals: 2
    lambda: |-
      return id(atlas_ec).state / 1000.0;
    update_interval: 30s

  - platform: template
    name: "PPM"
    id: ppm_500
    unit_of_measurement: "ppm"
    accuracy_decimals: 0
    lambda: |-
      return id(atlas_ec).state * 0.5;  // 500 scale
    update_interval: 30s

# ─── Publish combined JSON to Tendril ─────────────────────────
interval:
  - interval: 30s
    then:
      - mqtt.publish_json:
          topic: "t/${tenant_id}/d/${device_id}/sensor/hydro"
          payload: |-
            root["water_temp_f"] = id(water_temp_f).state;
            root["ph"] = id(atlas_ph).state;
            root["ec"] = id(ec_ms).state;
            root["ppm"] = (int)(id(ppm_500).state);

# ─── Temperature Compensation ─────────────────────────────────
# Send temperature to pH and EC circuits for automatic compensation
  - interval: 60s
    then:
      - lambda: |-
          if (!isnan(id(atlas_rtd).state)) {
            char cmd[20];
            snprintf(cmd, sizeof(cmd), "T,%.1f", id(atlas_rtd).state);
            // Send temp compensation to pH circuit
            id(atlas_ph).send_custom(cmd);
            // Send temp compensation to EC circuit
            id(atlas_ec).send_custom(cmd);
          }
```

---

## With Dissolved Oxygen (Add-on)

Add this sensor block for DO monitoring (aquaponics, RDWC):

```yaml
sensor:
  # ─── Atlas EZO DO (Dissolved Oxygen) ───────────────────────
  - platform: ezo
    id: atlas_do
    name: "Dissolved Oxygen"
    address: 0x61
    unit_of_measurement: "mg/L"
    accuracy_decimals: 2
    update_interval: 30s
    state_class: measurement
```

Update the JSON publish to include DO:

```yaml
      - mqtt.publish_json:
          topic: "t/${tenant_id}/d/${device_id}/sensor/hydro"
          payload: |-
            root["water_temp_f"] = id(water_temp_f).state;
            root["ph"] = id(atlas_ph).state;
            root["ec"] = id(ec_ms).state;
            root["ppm"] = (int)(id(ppm_500).state);
            root["do_mg_l"] = id(atlas_do).state;
```

---

## Secrets File

Create `secrets.yaml` next to your ESPHome config:

```yaml
wifi_ssid: "YourWiFi"
wifi_password: "YourPassword"
mqtt_host: "emqx.your-domain.com"
mqtt_user: "td-XXXXXXXXXXXX"
mqtt_password: "your-psk"
tenant_id: "your-tenant-uuid"
device_id: "td-XXXXXXXXXXXX"
```

---

## Flashing

```bash
pip install esphome
esphome run atlas-hydro-monitor.yaml
```

Or use the ESPHome Dashboard web UI for OTA updates after first flash.
