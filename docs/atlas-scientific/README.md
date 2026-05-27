# Atlas Scientific EZO Sensor Integration

Build a lab-grade hydroponic sensor rig using Atlas Scientific EZO circuits
with an ESP32 that reports directly to Tendril via MQTT.

---

## Why Atlas Scientific?

| Feature | DFRobot (analog) | Atlas Scientific (I2C) |
|---------|-------------------|------------------------|
| Accuracy | ±0.1 pH / ±5% EC | ±0.002 pH / ±2% EC |
| Longevity | 6-12 months | 2-5 years |
| Calibration | Manual voltage tweak | Digital, stored on circuit |
| Multi-probe | Interference risk | I2C daisy-chain, no crosstalk |
| Price | ~$30-35/probe | ~$100-200/probe |
| Best for | Hobby / budget builds | Serious growers, commercial |

Atlas probes are the standard in hydroponics research and commercial facilities.
They're rated for continuous immersion and maintain calibration far longer than
analog alternatives.

---

## Supported Circuits

| Circuit | Measures | I2C Address | Probe |
|---------|----------|-------------|-------|
| EZO pH | 0.001 – 14.000 pH | 0x63 (default) | Consumer or Lab Grade pH |
| EZO EC | 0.07 – 500,000 µS/cm | 0x64 (default) | K 1.0 Conductivity |
| EZO RTD | -200 – +850 °C | 0x66 (default) | PT-1000 Temperature |
| EZO DO | 0 – 100 mg/L | 0x61 (default) | Dissolved Oxygen |
| EZO ORP | -1019 – +1019 mV | 0x62 (default) | ORP Probe |

---

## Bill of Materials

### Core Kit (pH + EC + Temperature)

| # | Component | Qty | ~USD | Notes |
|---|-----------|-----|------|-------|
| 1 | ESP32-WROOM-32E DevKit | 1 | $8 | WiFi + I2C |
| 2 | Atlas EZO pH Circuit | 1 | $40 | Set to I2C mode |
| 3 | Atlas Consumer/Lab Grade pH Probe | 1 | $50-85 | BNC connector |
| 4 | Atlas EZO EC Circuit | 1 | $40 | Set to I2C mode |
| 5 | Atlas K 1.0 Conductivity Probe | 1 | $70-100 | BNC connector |
| 6 | Atlas EZO RTD Circuit | 1 | $40 | Temperature compensation |
| 7 | Atlas PT-1000 Temperature Probe | 1 | $24-35 | Waterproof, stainless |
| 8 | Atlas Electrically Isolated Carrier Boards | 3 | $26 ea | Prevents ground loops |
| 9 | Breadboard or custom PCB | 1 | $5 | For I2C bus wiring |
| 10 | 4.7 KΩ pull-up resistors | 2 | $0.10 | SDA + SCL pull-ups |
| 11 | IP65 Enclosure | 1 | $8 | 200×120×75 mm |
| 12 | Cable Glands (PG7/PG9) | 5 | $3 | Probe pass-through |
| | **Subtotal** | | **~$380** | |

### Optional Add-ons

| Component | ~USD | Why |
|-----------|------|-----|
| Atlas EZO DO Circuit + Probe | $150-260 | Dissolved oxygen (aquaponics, RDWC) |
| Atlas EZO ORP Circuit + Probe | $70-100 | Oxidation-reduction potential |
| 18650 battery kit (2S holder + TP4056) | $15 | Portable / backup power |
| ADS1115 ADC breakout | $5 | Add analog sensors alongside I2C |

---

## Wiring — ESP32 + Atlas EZO I2C Daisy Chain

All Atlas EZO circuits share a single I2C bus. Use electrically isolated
carrier boards to prevent ground loops between probes in the same solution.

```
ESP32                  EZO pH          EZO EC          EZO RTD
─────                  ──────          ──────          ───────
GPIO21 (SDA) ──────── SDA ─────────── SDA ─────────── SDA
GPIO22 (SCL) ──────── SCL ─────────── SCL ─────────── SCL
3.3V ─────────┬────── VCC ─────────── VCC ─────────── VCC
              │
              ├── 4.7KΩ → SDA (pull-up)
              └── 4.7KΩ → SCL (pull-up)

GND ──────────┬────── GND ─────────── GND ─────────── GND
              │
              └── (All isolated carrier board GND)
```

### Important: Set EZO Circuits to I2C Mode

Atlas EZO circuits ship in **UART mode** by default. You must switch them to
I2C mode before wiring:

1. Connect EZO circuit to USB UART adapter (or Arduino Serial)
2. Send: `I2C,99` (where 99 is desired address, or use defaults above)
3. Power cycle the circuit — it's now in I2C mode
4. Verify with I2C scanner sketch

Or short the `PGND` pin to `TX` on the EZO circuit and power cycle
(sets default I2C address).

---

## MQTT Topic Structure

The firmware publishes to Tendril's standard topic format:

```
t/{tenant_id}/d/{device_id}/sensor/hydro
```

Payload (JSON):
```json
{
  "ph": 6.21,
  "ec": 1.42,
  "ppm": 710,
  "water_temp_f": 68.5,
  "do_mg_l": 7.8
}
```

---

## Next Steps

- [Calibration Guide](calibration.md) — Calibrate pH, EC, DO probes
- [ESPHome YAML Template](../atlas-scientific-esphome.md) — For ESPHome users
- [Arduino/PlatformIO Sketch](../../esp32/hydro-monitor/src/atlas_sensors.h) — Direct firmware integration
