# Tendril Hydro Monitor — Sensor Kit

Battery-powered reservoir monitoring for all active hydroponic systems.
Tracks **water temperature**, **pH**, **EC/PPM**, and **water level** — the four
pillars of hydro health.

---

## Supported Grow Types

| Grow Type | Medium | Notes |
|-----------|--------|-------|
| DWC (Deep Water Culture) | Hydroton / Clay pebbles | Mount level sensor above reservoir |
| RDWC (Recirculating DWC) | Hydroton / Clay pebbles | Monitor control bucket |
| NFT (Nutrient Film Technique) | Rockwool starter cubes | Tank-level monitoring |
| Ebb & Flow (Flood and Drain) | Hydroton / Rockwool | Level tracks flood cycles |
| Drip / Top Feed | Coco / Rockwool / Perlite | Reservoir monitoring |
| Aquaponics | Expanded clay / Gravel | Fish-safe probes required |
| Dutch Bucket (Bato) | Perlite / Hydroton | Central reservoir monitoring |
| Vertical / Tower Garden | Rockwool / Felt | Base tank monitoring |

---

## What It Measures

| Metric | Sensor | Range | Accuracy | MQTT Topic |
|--------|--------|-------|----------|------------|
| Water temperature | DS18B20 waterproof | -10 to +85 °C | ±0.5 °C | `sensor/hydro` |
| pH | DFRobot Gravity pH v2 | 0-14 | ±0.1 | `sensor/hydro` |
| EC | DFRobot Gravity EC v2 | 0-20 mS/cm | ±5 % | `sensor/hydro` |
| PPM (TDS) | Calculated from EC | 0-10000 | — | `sensor/hydro` |
| Water level | JSN-SR04T ultrasonic | 25-450 cm | ±1 cm | `sensor/hydro` |
| Battery | ADC divider | 2.5-4.3 V | ±0.05 V | `status` |

---

## Bill of Materials

| # | Component | Specification | Qty | ~USD | Source |
|---|-----------|---------------|-----|------|--------|
| 1 | **ESP32-WROOM-32E DevKit** | WiFi; or ESP32-C6 for Zigbee/Matter | 1 | $8-10 | Amazon |
| 2 | **DS18B20 Waterproof Probe** | Stainless steel, 1 m cable | 1 | $4 | Amazon |
| 3 | **4.7 KΩ Resistor** | 1-Wire pull-up | 1 | $0.05 | Any |
| 4 | **DFRobot Gravity pH Sensor v2** | SEN0161-V2, BNC | 1 | $30 | DFRobot |
| 5 | **DFRobot Gravity EC Sensor v2** | DFR0300, K=1 (0-20 mS/cm) | 1 | $35 | DFRobot |
| 6 | **JSN-SR04T Ultrasonic Sensor** | IP67 waterproof, 25-450 cm | 1 | $8 | Amazon |
| 7 | **18650 Li-Ion Cell** | 3000+ mAh, protected | 2 | $10 | Amazon |
| 8 | **Dual 18650 Holder** | Parallel wiring (3.7V, 6000+ mAh) | 1 | $2 | Amazon |
| 9 | **TP4056 USB-C Charger** | With protection IC | 1 | $2 | Amazon |
| 10 | **HT7333 LDO** | 3.3V | 1 | $0.50 | AliExpress |
| 11 | **MT3608 Boost Converter** | 5V for pH/EC/ultrasonic boards | 1 | $2 | Amazon |
| 12 | **MOSFET Module** | N-channel, for switching 5V rail | 1 | $1 | Amazon |
| 13 | **Resistors/Caps** | 100KΩ ×2, 10µF ×2, 100nF ×3 | — | $1 | Any |
| 14 | **IP65 Enclosure** | 150×100×70 mm | 1 | $8 | Amazon |
| 15 | **PG7/PG9 Cable Glands** | For probe cables | 5 | $3 | Amazon |
| 16 | **PCB + Wire** | 7×9 cm proto board + 22 AWG | — | $4 | Amazon |
| | **Total** | | | **~$120** | |

### Optional Premium Upgrades

| Component | Replaces | ~USD | Why |
|-----------|----------|------|-----|
| Atlas Scientific pH EZO Kit | DFRobot pH | $100 | Lab-grade, I2C, long-term immersion rated |
| Atlas Scientific EC EZO Kit | DFRobot EC | $120 | Lab-grade, I2C, temp-compensated |
| Atlas Scientific DO EZO Kit | — (add-on) | $200 | Dissolved oxygen for aquaponics |

---

## Wiring

### Power Circuit

| From | To | Notes |
|------|----|-------|
| 2× 18650 (parallel) | TP4056 BAT+/BAT− | 3.7V / 6000 mAh combined |
| TP4056 OUT+ | HT7333 VIN | |
| TP4056 OUT+ | MT3608 VIN | |
| HT7333 VOUT | **3.3V rail** | DS18B20, MCU |
| MT3608 VOUT | **5V rail** | JSN-SR04T, pH board, EC board |
| GPIO27 | MOSFET gate → MT3608 EN | Firmware controls 5V on/off during sleep |
| VBAT | 100KΩ → **GPIO35** → 100KΩ → GND | Battery voltage divider |

### ESP32 — Sensor Connections

| GPIO | Direction | Connects To | Signal | Power Rail |
|------|-----------|-------------|--------|------------|
| GPIO4 | ↔ | DS18B20 DATA | 1-Wire + 4.7KΩ pull-up to 3V3 | 3.3V |
| GPIO32 | ← | DFRobot pH Signal Board AOUT | Analog | **5V** |
| GPIO33 | ← | DFRobot EC Signal Board AOUT | Analog | **5V** |
| GPIO25 | → | JSN-SR04T TRIG | Digital trigger | **5V** |
| GPIO26 | ← | JSN-SR04T ECHO | Digital pulse | **5V** |
| GPIO27 | → | N-Ch MOSFET gate (10KΩ) | Digital | — |
| GPIO35 | ← | Battery voltage divider midpoint | Analog | — |
| GPIO21 | ↔ | I2C SDA *(optional — Atlas EZO)* | I2C data | — |
| GPIO22 | ↔ | I2C SCL *(optional)* | I2C clock | — |
| 3V3 | → | DS18B20 VDD | Power | 3.3V |
| GND | — | All sensor GND, MOSFET source | Common ground | — |

### ESP32-C6 Pin Mapping

| Function | GPIO | Notes |
|----------|------|-------|
| DS18B20 DATA | 3 | + 4.7KΩ pull-up |
| pH ADC | 2 | ADC1 |
| EC ADC | 4 | ADC1 |
| Ultrasonic TRIG | 10 | |
| Ultrasonic ECHO | 11 | |
| 5V MOSFET gate | 5 | |
| Battery ADC | 1 | Via 100K divider |

---

## Assembly

1. **Power circuit**: 2× 18650 in parallel → TP4056 → HT7333 (3.3V) and MT3608 (5V).
2. **MOSFET switch**: Wire MOSFET gate to GPIO27 (ESP32) / GPIO5 (C6). Source to GND, drain to MT3608 enable. This lets firmware power off the 5V rail during sleep.
3. **DS18B20**: Submerge in reservoir. Route cable through gland.
4. **pH/EC probes**: Mount BNC connectors on enclosure. Signal boards inside.
5. **Ultrasonic sensor**: Mount facing down over the reservoir opening. Waterproof transducer hangs outside the enclosure.
6. **Seal all cable glands** with silicone.

---

## Firmware

```bash
cd esp32/hydro-monitor
cp src/config.example.h src/config.h
# Edit config.h
pio run -e wifi-esp32 -t upload
pio device monitor -b 115200
```

---

## Water Level Setup

The JSN-SR04T measures distance from the sensor to the water surface. You need to configure:

```c
#define TANK_DEPTH_CM      40    // Distance from sensor to tank bottom (empty)
#define TANK_FULL_CM       5     // Distance from sensor to water when full
```

The firmware calculates: `level_pct = 100 × (TANK_DEPTH_CM - distance) / (TANK_DEPTH_CM - TANK_FULL_CM)`

---

## Probe Maintenance

| Probe | Care | Frequency |
|-------|------|-----------|
| pH | Calibrate with 4.0 + 7.0 buffers | Monthly |
| pH | Store in KCl storage solution | Always when not in use |
| EC | Rinse with distilled water | After each use |
| EC | Calibrate with 1413 µS/cm solution | Monthly |
| DS18B20 | Rinse, check for corrosion | Monthly |
| Ultrasonic | Wipe transducer face | Monthly |

---

## Battery Life

| Interval | WiFi (2× 18650) | Zigbee |
|----------|-----------------|--------|
| 5 min | ~45 days | ~6 months |
| 15 min | ~130 days | ~18 months |

*Higher drain than soil kits due to 5V boost converter and probe warmup time.*

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| pH reads flat 7.0 | Probe disconnected. Check BNC connector. |
| EC reads 0 | Probe not submerged or K value wrong. |
| Water level erratic | Ultrasonic needs clear line-of-sight to water. No foam or obstructions. |
| DS18B20 reads -127 | Check 4.7KΩ pull-up and wiring. |
| Battery drains in <2 weeks | MOSFET not turning off 5V rail — check gate wiring. |
