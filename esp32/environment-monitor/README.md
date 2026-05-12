# Tendril Environment Monitor — Sensor Kit

Battery-powered **tent / room ambient** monitor. Tracks the full grow environment:
**CO₂**, **temperature**, **humidity**, **VPD**, **light intensity**, **barometric
pressure**, and **VOC / air quality**.

---

## Supported Grow Types

All indoor grow types benefit from environment monitoring:
DWC, RDWC, NFT, Ebb & Flow, Drip, Aeroponics, Kratky, Coco, Rockwool, Soil,
Living Soil, Dutch Bucket, Vertical Tower.

---

## What It Measures

| Metric | Sensor | Range | Accuracy | MQTT Topic |
|--------|--------|-------|----------|------------|
| CO₂ | SCD41 (photoacoustic) | 400-5000 ppm | ±40 ppm + 5% | `sensor/environment` |
| Temperature | BME680 | -40 to +85 °C | ±1 °C | `sensor/environment` |
| Humidity | BME680 | 0-100 % RH | ±3 % | `sensor/environment` |
| VPD | Calculated | 0-5 kPa | — | `sensor/environment` |
| Light (lux) | BH1750 | 1-65535 lux | ±1 lux | `sensor/environment` |
| Barometric pressure | BME680 | 300-1100 hPa | ±1 hPa | `sensor/environment` |
| Air quality (VOC) | BME680 gas | Relative kΩ | Qualitative | `sensor/environment` |
| Dew point | Calculated | — | — | `sensor/environment` |
| Battery | ADC divider | 2.5-4.3 V | ±0.05 V | `status` |

---

## Bill of Materials

| # | Component | Specification | Qty | ~USD | Source |
|---|-----------|---------------|-----|------|--------|
| 1 | ESP32-WROOM-32E DevKit (or C6) | USB-C | 1 | $8-10 | Amazon |
| 2 | **SCD41 CO₂ Sensor** | Photoacoustic NDIR, I2C | 1 | $50 | Adafruit / SparkFun |
| 3 | **BME680 Breakout** | I2C, temp/humidity/pressure/VOC | 1 | $10 | Adafruit |
| 4 | **BH1750 Light Sensor** | I2C, 16-bit lux | 1 | $3 | Amazon |
| 5 | 18650 Li-Ion Cell (protected) | 3000+ mAh | 1 | $5 | Amazon |
| 6 | 18650 Battery Holder | Single cell | 1 | $1 | Amazon |
| 7 | TP4056 USB-C Charger | With protection IC | 1 | $2 | Amazon |
| 8 | HT7333 LDO | 3.3V 250 mA | 1 | $0.50 | AliExpress |
| 9 | Resistors / caps | 100KΩ ×2, 10µF, 100nF ×2 | — | $0.50 | Any |
| 10 | IP54 Ventilated Enclosure | Allows airflow for gas sensors | 1 | $6 | Amazon |
| 11 | PCB + hookup wire | 5×7 cm proto board | — | $4 | Amazon |
| | **Total** | | | **~$92** | |

---

## Wiring

### Power Circuit

| From | To | Notes |
|------|----|-------|
| 18650 Li-Ion | TP4056 BAT+/BAT− | 3.7V / 3000 mAh |
| TP4056 OUT+ | HT7333 VIN | |
| HT7333 VOUT | **3.3V rail** | All sensors + MCU |
| VBAT | 100KΩ → **GPIO35** → 100KΩ → GND | Battery voltage divider |

### ESP32 — Sensor Connections (all I2C)

All three sensors share the same I2C bus. No analog or digital GPIO needed beyond SDA/SCL.

| GPIO | Direction | Connects To | I2C Address | Notes |
|------|-----------|-------------|-------------|-------|
| GPIO21 | ↔ | BME680 SDA · SCD41 SDA · BH1750 SDA | — | Shared I2C data |
| GPIO22 | ↔ | BME680 SCL · SCD41 SCL · BH1750 SCL | — | Shared I2C clock |
| GPIO35 | ← | Battery voltage divider midpoint | — | Analog |
| 3V3 | → | BME680 VIN · SCD41 VIN · BH1750 VCC | — | Power |
| GND | — | All sensor GND | — | Common ground |

### I2C Address Map

| Sensor | Address | Function |
|--------|---------|----------|
| BME680 | `0x77` (or `0x76`) | Temp, humidity, pressure, VOC |
| SCD41 | `0x62` | CO₂, temp, humidity |
| BH1750 | `0x23` (ADDR LOW) / `0x5C` (ADDR HIGH) | Lux |

---

## VPD Calculation

VPD (Vapor Pressure Deficit) is calculated from temperature and humidity:

$$VPD = SVP \times \left(1 - \frac{RH}{100}\right)$$

Where $SVP = 0.6108 \times e^{\frac{17.27 \times T}{T + 237.3}}$ (kPa, T in °C)

The firmware computes VPD automatically — no additional sensor needed.

---

## Enclosure Notes

The environment monitor **must have airflow** for accurate CO₂ and VOC readings:
- Use a ventilated/louvered enclosure (not sealed IP65)
- Or drill 4-6 small holes (3 mm) in a standard enclosure
- Keep the BH1750 light sensor facing outward (or use a light pipe)
- Mount at plant canopy height for representative readings

---

## Firmware

```bash
cd esp32/environment-monitor
cp src/config.example.h src/config.h
pio run -e wifi-esp32 -t upload
```

---

## SCD41 CO₂ Sensor Notes

- **First reading takes ~5 seconds** after power-on (photoacoustic measurement cycle)
- Automatically self-calibrates over 7 days (ASC — Automatic Self-Calibration)
- For immediate accuracy: expose to fresh outdoor air (400 ppm) and run `forced_recalibration` via serial command
- Altitude compensation is built into the firmware — set `ALTITUDE_M` in config.h

---

## Battery Life

| Interval | WiFi | Zigbee |
|----------|------|--------|
| 5 min | ~45 days | ~8 months |
| 15 min | ~130 days | ~2+ years |

*SCD41 draws ~18 mA during its 5-second measurement cycle, which limits battery life compared to passive sensors.*

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CO₂ reads 0 or 400 constantly | Check SCD41 wiring. Wait 5+ seconds for first reading. |
| CO₂ reads abnormally high (5000+) | Sensor saturated — ventilate and recalibrate outdoors. |
| Light reads 0 | BH1750 powered? Check ADDR pin and I2C address (0x23 vs 0x5C). |
| VPD looks wrong | VPD requires accurate temp AND humidity — verify BME680 readings first. |
| BME680 VOC unreliable | VOC needs 30+ minutes of burn-in after first power-on. Normal. |
