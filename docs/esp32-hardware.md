# ESP32 Hardware Guide

Complete guide to building, wiring, calibrating, and deploying a Tendril sensor kit.

## Overview

The Tendril Soil Sensor Kit v1 is an ESP32-based device that monitors:

- **Ambient temperature** (°F) via BME680
- **Ambient humidity** (%) via BME680
- **Barometric pressure** (hPa) via BME680
- **Gas resistance** (kΩ) via BME680 — indicates air quality
- **Soil moisture** (%) via capacitive probe

Data is published to the Tendril API over MQTT every 30 seconds, with a heartbeat every 60 seconds.

## Bill of Materials

| Component | Quantity | Approx. Cost | Notes |
|-----------|----------|-------------|-------|
| ESP32-WROOM-32 dev board | 1 | $5–10 | Any ESP32-DevKitC or equivalent. Must have ADC1 pins available. |
| BME680 breakout board | 1 | $10–15 | Adafruit, CJMCU, or GY-BME680. I2C interface. |
| Capacitive soil moisture sensor v1.2/v2.0 | 1 | $2–5 | **Capacitive only** — do not use resistive probes (they corrode). |
| Jumper wires (F-F or F-M) | 6–8 | $2 | For connecting sensors to ESP32. |
| Micro-USB cable | 1 | $2 | For power and programming. |
| USB power supply (5V 1A+) | 1 | $5 | For permanent deployment. Phone charger works fine. |
| Enclosure (optional) | 1 | $5–10 | 3D printed or small project box. Keep sensors exposed to air. |

**Total cost: ~$25–45** per sensor kit.

## Wiring Diagram

```
                    ESP32-WROOM-32
                   ┌──────────────┐
                   │              │
    BME680 SDA ────┤ GPIO 21 (SDA)│
    BME680 SCL ────┤ GPIO 22 (SCL)│
                   │              │
    Soil Signal ───┤ GPIO 34      │
                   │              │
    BME680 VCC ────┤ 3.3V         │
    Soil VCC ──────┤ 3.3V         │
                   │              │
    BME680 GND ────┤ GND          │
    Soil GND ──────┤ GND          │
                   │              │
                   │        USB   │ ← Power + Programming
                   └──────────────┘
```

### Pin Assignments

| ESP32 Pin | Function | Connected To |
|-----------|----------|-------------|
| GPIO 21 | I2C SDA | BME680 SDA/SDI |
| GPIO 22 | I2C SCL | BME680 SCL/SCK |
| GPIO 34 | ADC1 Channel 6 | Soil moisture sensor AOUT/SIG |
| 3.3V | Power | Both sensors VCC/VIN |
| GND | Ground | Both sensors GND |

### Important Notes

- **GPIO 34** is an input-only pin on ESP32 — perfect for analog reads, no pull-up needed for capacitive sensors.
- **Do not use ADC2 pins** (GPIO 0, 2, 4, 12, 13, 14, 15, 25, 26, 27) — they conflict with WiFi.
- **BME680 address**: Default is `0x77`. If yours uses `0x76` (some CJMCU boards), the firmware auto-detects both.
- **Power**: The ESP32 needs a stable 5V supply. Cheap USB cables with thin wires can cause brownout resets.

## Assembly Steps

1. **Connect the BME680:**
   - VCC → 3.3V
   - GND → GND
   - SDA → GPIO 21
   - SCL → GPIO 22

2. **Connect the soil moisture sensor:**
   - VCC → 3.3V
   - GND → GND
   - AOUT (analog output) → GPIO 34

3. **Verify connections** before powering on. Double-check no pins are shorted.

4. **Power the ESP32** via USB. The onboard LED should light up.

## Firmware Setup

### Prerequisites

Install [PlatformIO](https://platformio.org/):

```bash
# Via pip
pip install platformio

# Or via Homebrew
brew install platformio

# Or use the VS Code PlatformIO extension
```

### Configure

```bash
cd esp32
cp src/config.example.h src/config.h
```

Edit `src/config.h` with your settings:

```c
// WiFi
#define WIFI_SSID "YourNetworkName"
#define WIFI_PASS "YourPassword"

// MQTT — use your Tendril server's IP
#define MQTT_HOST "192.168.1.100"
#define MQTT_PORT 1883

// Device identity — get these from the Tendril API
#define MQTT_DEVICE_ID "td-XXXXXXXXXXXX"
#define MQTT_PSK "your-pre-shared-key"
#define TENANT_ID "your-tenant-uuid"
```

### Compile and Flash

```bash
# Compile only
pio run

# Compile and upload to connected ESP32
pio run -t upload

# Monitor serial output
pio device monitor
```

### Expected Serial Output

```
========================================
  Tendril Soil Sensor Kit v1
  Device: td-XXXXXXXXXXXX
========================================

Connecting to WiFi....
WiFi connected — IP: 192.168.1.42
MQTT connecting...
MQTT connected
BME680 initialized
Soil sensor initialized

Setup complete. Starting sensor loop...

Soil: 65%
BME680: 75.2°F, 52.3% RH, 1013.2 hPa, 45.7 kΩ gas
```

## Soil Moisture Calibration

The capacitive soil sensor outputs a raw ADC value (0–4095 on ESP32's 12-bit ADC). You need to calibrate for your specific sensor.

### Calibration Procedure

1. **Dry reading**: Hold the sensor in open air (not touching anything). Note the ADC value from serial output.
2. **Wet reading**: Submerge the sensor in a glass of water up to the line marked on the PCB. Note the ADC value.
3. **Update config.h**:

```c
#define SOIL_1_DRY_VALUE 2800   // Your dry air reading
#define SOIL_1_WET_VALUE 1200   // Your submerged reading
```

### Typical Values

| Sensor Version | Dry (air) | Wet (water) |
|---------------|-----------|-------------|
| Capacitive v1.2 | 2700–2900 | 1100–1300 |
| Capacitive v2.0 | 2500–2800 | 1000–1200 |

> **Tip**: Capacitive sensors read HIGH when dry and LOW when wet. The firmware inverts this to give 0% = dry, 100% = saturated.

### Accuracy Considerations

- The firmware averages 8 samples per reading to reduce noise.
- ADC readings can vary ±50 units between ESP32 boards.
- Soil moisture % is relative to your calibration — it's best used for trend monitoring rather than absolute measurement.
- For best results, calibrate with the actual growing medium (e.g., coco coir vs. soil).

## MQTT Topics

The device publishes to these topics:

| Topic | Payload | Interval |
|-------|---------|----------|
| `t/{tenant}/d/{device}/sensor/readings` | `{"soil_moisture": 65, "position": 1}` | 30s |
| `t/{tenant}/d/{device}/sensor/ambient` | `{"ambient_temp_f": 75.2, "ambient_humidity": 52.3, "pressure_hpa": 1013.2, "gas_kohms": 45.7}` | 30s |
| `t/{tenant}/d/{device}/status` | `{"status": "online"}` | 60s (heartbeat) |

**Last Will and Testament**: If the device disconnects unexpectedly, EMQX publishes `{"status": "offline"}` to the status topic (QoS 1, retained).

## Adding a Second Soil Sensor

The firmware supports a second soil probe. To enable it:

1. Wire a second capacitive sensor to **GPIO 35**
2. Uncomment in `config.h`:
   ```c
   #define SOIL_SENSOR_2_PIN 35
   ```
3. Add calibration values for the second sensor
4. Update `sensors.cpp` to read and publish from both pins

## Placement Tips

### Indoor (Tent / Grow Room)

- **BME680**: Mount at canopy height, away from lights and fans. Avoid placing directly above plants (transpiration humidity).
- **Soil sensor**: Insert into the growing medium at a 45° angle, burying just past the marked line. Keep the electronics above the soil.
- **ESP32**: Outside the grow tent if possible (heat from lights can affect WiFi). Run sensor wires through a vent port.

### Outdoor

- **BME680**: Shield from direct rain and sunlight. A radiation shield or small enclosure with ventilation works well.
- **Soil sensor**: Bury at root depth. For raised beds, insert vertically.
- **ESP32**: Must be in a waterproof enclosure. Ensure WiFi range from your router.

## Power Options

| Method | Pros | Cons |
|--------|------|------|
| USB wall adapter | Simple, reliable | Needs an outlet nearby |
| USB power bank | Portable, no wiring | Battery life varies (8–24h typical) |
| Solar + battery | Off-grid capable | More complex, weather dependent |
| POE splitter (5V) | Clean power over ethernet | Requires POE switch or injector |

The ESP32 draws ~80mA average (WiFi active), spiking to ~200mA during transmit.

## Troubleshooting

### WiFi won't connect

- Verify SSID and password in `config.h` (case-sensitive)
- ESP32 only supports **2.4 GHz WiFi** — not 5 GHz
- Check router for MAC filtering
- Move closer to the router for initial testing
- After 40 failed attempts (20 seconds), the device auto-restarts

### BME680 not found

- Check I2C wiring (SDA → 21, SCL → 22)
- Verify 3.3V power to the BME680
- The firmware tries both addresses (0x77 and 0x76)
- Use an I2C scanner sketch to verify the sensor is on the bus
- The device continues without BME680 — only soil moisture is reported

### Soil readings stuck at 0% or 100%

- Recalibrate dry/wet values for your specific sensor
- Check wiring to GPIO 34
- Verify the sensor is powered (3.3V)
- Try a different ADC1 pin (32, 33, 35, 36, 39)

### MQTT connection failed

- Verify `MQTT_HOST` is reachable from the ESP32's network
- Check that port 1883 (or 8883 for TLS) is open
- Verify device credentials in EMQX
- Check serial output for `rc=` error codes:
  - `rc=-2`: Network unreachable
  - `rc=-4`: Connection refused (bad credentials or ACL)
  - `rc=5`: Not authorized

### Frequent disconnects / reboots

- Use a quality USB cable and power supply (5V, 1A minimum)
- Check for brownout messages in serial output
- Reduce `SENSOR_POLL_MS` if power is constrained
- Add a 100µF capacitor across 3.3V and GND near the ESP32
