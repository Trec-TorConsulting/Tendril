# Tendril Soil Pro — Sensor Kit

Battery-powered soil monitoring with **soil temperature** and **runoff pH/EC analysis**.
For growers who want deeper insight into root-zone conditions and nutrient uptake.

---

## Supported Grow Types

| Grow Type | Medium | Why Soil Pro |
|-----------|--------|-------------|
| Soil | Soil / Super soil | Runoff pH/EC reveals nutrient lockout |
| Coco Coir | Coco coir | EC drift monitoring is critical in coco |
| Living Soil / No-Till | Living soil | Soil temp tracks microbial activity |
| Outdoor Container | Soil / Coco-perlite | Runoff testing without meters |

---

## What It Measures

| Metric | Sensor | Range | Accuracy | MQTT Topic |
|--------|--------|-------|----------|------------|
| Soil moisture | Capacitive v2.0 | 0-100 % | ±3 % | `sensor/readings` |
| Soil temperature | DS18B20 waterproof | -55 to +125 °C | ±0.5 °C | `sensor/readings` |
| Runoff pH | DFRobot Gravity pH v2 | 0-14 pH | ±0.1 pH | `sensor/runoff` |
| Runoff EC | DFRobot Gravity EC v2 | 0-20 mS/cm | ±5 % | `sensor/runoff` |
| Ambient temp / humidity | BME680 | Full range | ±1 °C / ±3 % | `sensor/ambient` |
| Air quality (VOC) | BME680 | Relative | Qualitative | `sensor/ambient` |
| Battery voltage | ADC divider | 2.5-4.3 V | ±0.05 V | `status` |

---

## Bill of Materials

| # | Component | Specification | Qty | ~USD | Source |
|---|-----------|---------------|-----|------|--------|
| 1 | **ESP32-WROOM-32E DevKit** | WiFi; or ESP32-C6 for Zigbee/Matter | 1 | $8-10 | Amazon / AliExpress |
| 2 | **BME680 Breakout** | I2C, 3.3V | 1 | $10 | Adafruit |
| 3 | **Capacitive Soil Moisture v2.0** | 3.3V, corrosion-resistant | 1 | $3 | Amazon |
| 4 | **DS18B20 Waterproof Probe** | 1-Wire, 1 m cable, stainless steel | 1 | $4 | Amazon |
| 5 | **4.7 KΩ Resistor** | Pull-up for 1-Wire bus | 1 | $0.05 | Any |
| 6 | **DFRobot Gravity Analog pH Sensor v2** | SEN0161-V2, BNC connector | 1 | $30 | DFRobot / Amazon |
| 7 | **DFRobot Gravity Analog EC Sensor v2** | DFR0300-H, K=10 (high range) | 1 | $35 | DFRobot / Amazon |
| 8 | **18650 Li-Ion Cell** | 3000+ mAh, protected | 2 | $10 | Amazon |
| 9 | **Dual 18650 Battery Holder** | Series (7.4V) or parallel (3.7V) | 1 | $2 | Amazon |
| 10 | **TP4056 USB-C Charger** | With DW01A protection | 1 | $2 | Amazon |
| 11 | **HT7333 LDO** | 3.3V 250 mA | 1 | $0.50 | AliExpress |
| 12 | **MT3608 Boost Converter** | 5V output (for pH/EC probes) | 1 | $2 | Amazon |
| 13 | **Resistors** | 100KΩ ×2 (battery divider) | 2 | $0.10 | Any |
| 14 | **Capacitors** | 10µF ×2, 100nF ×3 | 5 | $0.50 | Any |
| 15 | **IP65 Enclosure** | 150×100×70 mm | 1 | $8 | Amazon |
| 16 | **PG7 Cable Glands** | For sensor cables | 5 | $2 | Amazon |
| 17 | **Prototype PCB** | 7×9 cm | 1 | $1.50 | Amazon |
| 18 | **Hookup Wire** | 22 AWG solid | — | $3 | Any |
| | **Total** | | | **~$120** | |

### Optional

| Component | Use | ~USD |
|-----------|-----|------|
| pH calibration solutions (4.0, 7.0) | Probe calibration | $10 |
| EC calibration solution (1413 µS/cm) | Probe calibration | $8 |
| Runoff collection tray | Hold probes in runoff | $5 |
| 6V 2W Solar Panel | Outdoor perpetual power | $12 |

---

## Wiring

### Power Circuit

| From | To | Notes |
|------|----|-------|
| 2× 18650 (parallel) | TP4056 BAT+/BAT− | 3.7V / 6000 mAh combined |
| TP4056 OUT+ | HT7333 VIN | |
| TP4056 OUT+ | MT3608 VIN | |
| HT7333 VOUT | **3.3V rail** | Sensors, MCU |
| MT3608 VOUT | **5V rail** | pH / EC signal boards only |
| GPIO25 | MOSFET gate → MT3608 EN | Firmware controls 5V on/off during sleep |
| VBAT | 100KΩ → **GPIO35** → 100KΩ → GND | Battery voltage divider |

### ESP32 — Sensor Connections

| GPIO | Direction | Connects To | Signal | Power Rail |
|------|-----------|-------------|--------|------------|
| GPIO21 | ↔ | BME680 SDA | I2C data | — |
| GPIO22 | ↔ | BME680 SCL | I2C clock | — |
| GPIO34 | ← | Capacitive Soil Sensor AOUT | Analog 0–3.3V | 3.3V |
| GPIO4 | ↔ | DS18B20 DATA | 1-Wire + 4.7KΩ pull-up to 3V3 | 3.3V |
| GPIO32 | ← | DFRobot pH Signal Board AOUT | Analog | **5V** |
| GPIO33 | ← | DFRobot EC Signal Board AOUT | Analog | **5V** |
| GPIO35 | ← | Battery voltage divider midpoint | Analog | — |
| GPIO25 | → | N-Ch MOSFET gate (10KΩ) | Digital | — |
| 3V3 | → | BME680 VIN, Soil VCC, DS18B20 VDD | Power | 3.3V |
| GND | — | All sensor GND, MOSFET source | Common ground | — |

> **Note:** pH / EC probes sit in a runoff collection tray. Only dip probes during
> measurement; store dry between readings.

---

## Probe Care

- **pH probe**: Store in pH 4.0 storage solution when not in use. Calibrate monthly with 4.0 and 7.0 buffers.
- **EC probe**: Rinse with distilled water after each use. Calibrate monthly with 1413 µS/cm solution.
- **DS18B20**: Fully waterproof (IP68). Can be buried in soil or submerged indefinitely.
- **Soil moisture sensor**: Do not submerge above the marked line.

---

## Firmware

### Build Environments

| Environment | Board | Protocol |
|-------------|-------|----------|
| `wifi-esp32` | ESP32-WROOM-32E | WiFi + MQTT |
| `wifi-esp32c6` | ESP32-C6 | WiFi + MQTT |
| `zigbee-esp32c6` | ESP32-C6 | Zigbee 3.0 |
| `matter-esp32c6` | ESP32-C6 | Matter |

### Flash
```bash
cd esp32/soil-pro
cp src/config.example.h src/config.h
# Edit config.h
pio run -e wifi-esp32 -t upload
pio device monitor -b 115200
```

---

## pH/EC Calibration

The firmware includes a serial calibration mode:

1. Flash and open serial monitor (`pio device monitor`)
2. Send `cal` to enter calibration mode
3. For pH: dip probe in pH 7.0 buffer, send `ph7`. Then pH 4.0 buffer, send `ph4`.
4. For EC: dip probe in 1413 µS/cm solution, send `ec1413`.
5. Send `save` to store calibration to NVS flash.
6. Send `exit` to resume normal operation.

Calibration values persist across reboots and deep sleep cycles.

---

## Battery Life

| Interval | WiFi (2× 18650) | Zigbee |
|----------|-----------------|--------|
| 5 min | ~60 days | ~12 months |
| 15 min | ~170 days | ~3+ years |
| 30 min | ~300 days | ~5+ years |

*pH/EC probes draw more current than passive sensors — the boost converter adds ~2 mA quiescent.*

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| pH reads 7.0 constantly | Probe not connected or BNC loose. Check signal board wiring. |
| EC reads 0 | Probe not in solution. Check K constant matches your range. |
| DS18B20 reads -127°C | 1-Wire bus error — check 4.7KΩ pull-up resistor. |
| Wild pH/EC swings | Calibrate probes. Ensure 5V supply is stable (check MT3608 output). |
| Soil reads differently than expected | Re-calibrate for your specific medium. |
