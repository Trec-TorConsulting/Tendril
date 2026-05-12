# Tendril Water Reservoir — Sensor Kit

Battery-powered **reservoir and irrigation** monitor. Tracks water level,
temperature, and flow rate for tanks, cisterns, and irrigation lines.

---

## Supported Grow Types

| Grow Type | Use Case |
|-----------|----------|
| DWC / RDWC | Reservoir level + top-off flow tracking |
| NFT / Ebb & Flow | Central reservoir monitoring |
| Drip | Tank level + irrigation flow metering |
| Aeroponics | High-pressure reservoir level |
| Aquaponics | Sump tank level + flow rate |
| Dutch Bucket | Reservoir level + drip flow |
| Outdoor Soil / Container | Rain barrel / irrigation cistern |

---

## What It Measures

| Metric | Sensor | Range | MQTT Topic |
|--------|--------|-------|------------|
| Water level (cm / %) | JSN-SR04T ultrasonic | 25-450 cm | `sensor/reservoir` |
| Water temperature | DS18B20 waterproof | -55 to +125 °C | `sensor/reservoir` |
| Flow rate (L/min) | YF-S201 Hall-effect | 1-30 L/min | `sensor/reservoir` |
| Total volume (L) | Calculated from flow | Cumulative | `sensor/reservoir` |
| Battery | ADC divider | 2.5-4.3 V | `status` |

---

## Bill of Materials

| # | Component | Specification | Qty | ~USD | Source |
|---|-----------|---------------|-----|------|--------|
| 1 | ESP32-WROOM-32E DevKit (or C6) | USB-C | 1 | $8-10 | Amazon |
| 2 | **JSN-SR04T** Waterproof Ultrasonic | 5V, UART/trigger-echo, IP67 probe | 1 | $8 | Amazon |
| 3 | **DS18B20** Waterproof Probe (1 m) | Stainless steel, 3-wire | 1 | $4 | Amazon |
| 4 | **YF-S201** Water Flow Sensor | G1/2" thread, Hall-effect, 1-30 L/min | 1 | $5 | Amazon |
| 5 | 4.7 KΩ Resistor | 1-Wire pull-up | 1 | $0.05 | Any |
| 6 | 10 KΩ Resistor | Flow sensor pull-up | 1 | $0.05 | Any |
| 7 | MT3608 Boost Converter | 3.3V → 5V for JSN-SR04T | 1 | $2 | Amazon |
| 8 | N-Channel MOSFET (2N7000) | Power gating for 5V rail | 1 | $0.30 | Any |
| 9 | 18650 Li-Ion Cell (protected) | 3000+ mAh | 2 | $10 | Amazon |
| 10 | 18650 Battery Holder | Dual cell in parallel | 1 | $2 | Amazon |
| 11 | TP4056 USB-C Charger | With protection IC | 1 | $2 | Amazon |
| 12 | HT7333 LDO | 3.3V 250 mA | 1 | $0.50 | AliExpress |
| 13 | Resistors / caps | 100KΩ ×2, 47KΩ, 100KΩ voltage divider, caps | — | $1 | Any |
| 14 | IP65 Enclosure | Waterproof, near-tank mounting | 1 | $8 | Amazon |
| 15 | PG7 Cable Glands | Sensor cable entry | 4 | $3 | Amazon |
| 16 | PCB + hookup wire | 5×7 cm proto board | — | $4 | Amazon |
| | **Total** | | | **~$60** | |

---

## Wiring

### Power Circuit

| From | To | Notes |
|------|----|-------|
| 2× 18650 (parallel) | TP4056 BAT+/BAT− | 3.7V / 6000 mAh combined |
| TP4056 OUT+ | HT7333 VIN | |
| TP4056 OUT+ | MT3608 VIN | |
| HT7333 VOUT | **3.3V rail** | DS18B20, MCU |
| MT3608 VOUT | **5V rail** | JSN-SR04T, YF-S201 |
| GPIO25 | 10KΩ → 2N7000 gate | MOSFET source → GND, drain → MT3608 EN |
| VBAT | 100KΩ → **GPIO36** → 100KΩ → GND | Battery voltage divider |

### ESP32 — Sensor Connections

| GPIO | Direction | Connects To | Signal | Power Rail |
|------|-----------|-------------|--------|------------|
| GPIO25 | → | MOSFET gate (10KΩ) | Digital — controls 5V rail | — |
| GPIO13 | → | JSN-SR04T TRIG | Digital trigger | **5V** |
| GPIO12 | ← | JSN-SR04T ECHO | Digital pulse | **5V** |
| GPIO4 | ↔ | DS18B20 DATA | 1-Wire + 4.7KΩ pull-up to 3V3 | 3.3V |
| GPIO14 | ← | YF-S201 signal | Interrupt (RISING) + 10KΩ pull-up to 3V3 | **5V** |
| GPIO36 | ← | Battery voltage divider midpoint | Analog | — |
| 3V3 | → | DS18B20 VDD | Power | 3.3V |
| GND | — | All sensor GND, MOSFET source | Common ground | — |

### ECHO Voltage Divider (required)

JSN-SR04T ECHO outputs 5V pulses. A voltage divider makes it 3.3V-safe:

| From | Through | To |
|------|---------|----|
| JSN-SR04T ECHO | **47KΩ** resistor | Midpoint (GPIO12) |
| Midpoint (GPIO12) | **100KΩ** resistor | GND |

### ESP32-C6 Pin Mapping

| Function | GPIO |
|----------|------|
| MOSFET gate (5V power) | GPIO10 |
| JSN-SR04T TRIG | GPIO2 |
| JSN-SR04T ECHO | GPIO3 |
| DS18B20 1-Wire | GPIO4 |
| YF-S201 flow signal | GPIO5 |
| Battery ADC | GPIO1 |
| I2C SDA/SCL (unused) | GPIO6/GPIO7 |

---

## Tank Level Calculation

The ultrasonic sensor is mounted at the top of the tank, pointing down at the water
surface. Distance decreases as water level rises.

```
  Sensor ─────────── mounted at top of tank
  │
  │  distance (cm)   ← measured by JSN-SR04T
  │
  ▼
  ~~~~~~~~~~~~       ← water surface
  │
  │  water level     = TANK_DEPTH_CM - distance + SENSOR_OFFSET_CM
  │
  ▼
  ───────────────    ← bottom of tank
```

Set in `config.h`:
- `TANK_DEPTH_CM` — total inside depth of your tank
- `SENSOR_OFFSET_CM` — distance from sensor face to tank top (usually 2-5 cm)
- `TANK_FULL_CM` — water level when "100% full" (may be less than depth)

---

## Flow Sensor Setup

The **YF-S201** outputs pulses proportional to flow. The datasheet constant is
**7.5 pulses per second per L/min** (450 pulses/L). The firmware counts pulses
via interrupt during the measurement window.

### Plumbing

```
  Reservoir → ─── YF-S201 ─── → Grow system
                (flow direction arrow on body)
```

- Install **inline** with the pipe using G1/2" threaded fittings
- Mount **horizontally** — flow accuracy drops if mounted vertically
- Arrow on sensor body indicates flow direction

---

## Firmware

```bash
cd esp32/water-reservoir
cp src/config.example.h src/config.h
pio run -e wifi-esp32 -t upload
```

---

## Battery Life

| Interval | WiFi |
|----------|------|
| 5 min | ~55 days (2× 18650 parallel) |
| 15 min | ~160 days |
| 30 min | ~300 days |

*JSN-SR04T draws ~30 mA during measurement but runs < 1 second per cycle.*

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Ultrasonic reads 0 or max | Check 5V rail is powering on. Verify TRIG/ECHO wiring. |
| Level jumps around | Tank surface may be turbulent — increase measurement averaging or add a stilling tube. |
| Flow reads 0 | Check YF-S201 is powered (5V or 3.3V). Verify signal pin interrupt. Ensure water is actually flowing. |
| Flow accuracy off | YF-S201 is ±10% accuracy. Calibrate FLOW_FACTOR in config.h with a known volume. |
| DS18B20 reads -127 | Probe disconnected or pull-up missing. Check 4.7KΩ resistor. |
| Water in enclosure | Verify cable gland seals. Apply thread sealant if pipe vibration loosens glands. |
