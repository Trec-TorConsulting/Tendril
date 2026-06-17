# Tendril ESP32 Firmware — Agent Guide

PlatformIO-based firmware for seven battery-powered sensor kits. Every kit ships **WiFi (MQTT)**, **Zigbee 3.0**, and **Matter** variants from the same source tree.

> Cross-references: [`README.md`](README.md) for kit catalog and hardware, [`docs/esp32-hardware.md`](../docs/esp32-hardware.md) for power budgets.

## Layout

```
esp32/
  platformio.ini           # Top-level (legacy single-board build under src/)
  src/                     # Legacy reference firmware — DO NOT add new kits here
  shared/lib/
    TendrilMQTT/           # MQTT client w/ Tendril topic conventions, LWT, TLS-PSK
    TendrilPower/          # Battery / deep-sleep helpers
  <kit-name>/              # One per kit — copy an existing kit to add a new one
    platformio.ini         # Defines wifi-esp32, wifi-esp32c6, zigbee-esp32c6, matter-esp32c6
    src/
      config.example.h     # Pin map + credentials template — checked in
      config.h             # User-filled, GITIGNORED — never commit
      sensors.h / sensors.cpp
      main_wifi.cpp        # Arduino framework, PubSubClient
      main_zigbee.cpp      # ESP-IDF + Zigbee 3.0
      main_matter.cpp      # ESP-IDF + Matter over Thread
```

Existing kits: `soil-basic/`, `soil-pro/`, `hydro-monitor/`, `aero-monitor/`, `multi-zone-soil/`, `environment-monitor/`, `water-reservoir/`.

## Conventions

### Per-kit `platformio.ini`
Every kit defines four envs and a `[common]` section that pulls in `../shared/lib`:

```ini
[common]
lib_extra_dirs = ../shared/lib
build_flags =
    -DTENDRIL_KIT="\"<kit-name>\""
    -DTENDRIL_FW_VERSION="\"1.0.0\""

[env:wifi-esp32]        # ESP32-WROOM-32E — Arduino framework
[env:wifi-esp32c6]      # ESP32-C6        — Arduino framework
[env:zigbee-esp32c6]    # ESP32-C6        — ESP-IDF + Zigbee
[env:matter-esp32c6]    # ESP32-C6        — ESP-IDF + Matter
```

Pin assignments differ per board variant and are passed as `-D` flags (e.g. `-DI2C_SDA=6 -DI2C_SCL=7` for C6, `-DI2C_SDA=21 -DI2C_SCL=22` for classic). The same `sensors.cpp` reads them.

`build_src_filter` picks the correct `main_*.cpp` per env so the wrong transport's code never compiles in.

### MQTT topic conventions
Use [`shared/lib/TendrilMQTT`](shared/lib/TendrilMQTT) — never re-roll. Topic shape:

```
t/{tenant_id}/d/{device_id}/sensor/{subtopic}   # telemetry
t/{tenant_id}/d/{device_id}/status              # online/offline (retained, LWT)
t/{tenant_id}/d/{device_id}/diag                # diagnostics
```

- Device authenticates with `device_id` as both clientId and username, PSK as password.
- LWT publishes `{"status":"offline"}` retained on the status topic.
- Production must use TLS (port 8883). `tendril::Mqtt` defaults to `use_tls=true`; the `setInsecure()` in `tendril_mqtt.cpp` is a TODO for CA pinning.

### Credentials & secrets
- **Never commit `config.h`.** Each kit's `.gitignore` excludes it.
- `config.example.h` is the canonical template — keep it in sync when you add a field.
- WiFi PSK + `MQTT_PSK` are baked at flash time. There is no runtime provisioning for WiFi today.
- Zigbee/Matter use BLE provisioning via their respective stacks.

## Commands

```bash
# Flash WiFi variant of a kit
cd esp32/soil-basic
cp src/config.example.h src/config.h    # edit credentials
pio run -e wifi-esp32 -t upload

# ESP32-C6 (Arduino)
pio run -e wifi-esp32c6 -t upload

# Zigbee / Matter (ESP-IDF — first build is slow)
pio run -e zigbee-esp32c6 -t upload
pio run -e matter-esp32c6 -t upload

# Serial monitor
pio device monitor -b 115200

# Clean a single env
pio run -e wifi-esp32 -t clean

# Build only (no upload) — useful in CI
pio run -e wifi-esp32
```

## Adding a new kit

1. Copy the closest existing kit folder (e.g. `cp -r soil-basic new-kit`).
2. Rename `-DTENDRIL_KIT="\"...\""` in the new `platformio.ini`.
3. Adjust `lib_deps`, pin `-D` flags, and `build_src_filter`.
4. Update `src/sensors.cpp` for the new hardware; keep `main_*.cpp` thin.
5. Add the kit row to [`esp32/README.md`](README.md) (kit table + grow-type mapping).
6. Build all four envs locally before pushing.

## Gotchas

- **Pin assignments are board-specific.** The classic ESP32 and ESP32-C6 do not share a pin map. Always check the env's `build_flags`.
- ADC pins on ESP32 classic: use **ADC1** (GPIO 32–39) when WiFi is active. ADC2 conflicts with the WiFi radio.
- `PubSubClient` default buffer is 256 B — `tendril::Mqtt` bumps to 512. Larger payloads silently fail to publish; bump again if needed.
- Deep sleep wipes RTC RAM unless declared `RTC_DATA_ATTR`. Persist sensor calibration / cycle counters there.
- Zigbee/Matter builds require the **ESP-IDF** framework, not Arduino — they have a separate, much larger build cache.
- `monitor_filters = esp32_exception_decoder` is only set in some kits. Add it to your env when debugging crashes.
- The top-level `esp32/src/` directory is the legacy reference firmware. New work lives in a kit folder.
