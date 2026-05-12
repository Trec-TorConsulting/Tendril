# Tendril Multi-Zone Soil — Sensor Kit

Battery-powered **4-channel** soil monitoring for outdoor beds, greenhouses,
and multi-pot setups. One device monitors four separate root zones simultaneously.

---

## Supported Grow Types

| Grow Type | Notes |
|-----------|-------|
| Outdoor Soil | 4 probes across a raised bed |
| Outdoor Container | 1 probe per pot, up to 4 pots |
| Living Soil / No-Till | Low-disturbance multi-point monitoring |
| Dutch Bucket (Bato) | 1 probe per bucket, up to 4 |

---

## What It Measures

| Metric | Sensor | Per Zone | MQTT Topic |
|--------|--------|----------|------------|
| Soil moisture (×4) | Capacitive v2.0 | Independent | `sensor/readings` |
| Soil temperature (×4) | DS18B20 waterproof | Independent | `sensor/readings` |
| Ambient temp / humidity | BME680 | Shared | `sensor/ambient` |
| Battery | ADC divider | — | `status` |

---

## Bill of Materials

| # | Component | Qty | ~USD | Source |
|---|-----------|-----|------|--------|
| 1 | ESP32-WROOM-32E DevKit (or C6) | 1 | $8-10 | Amazon |
| 2 | Capacitive Soil Moisture Sensor v2.0 | 4 | $12 | Amazon (4-pack) |
| 3 | DS18B20 Waterproof Probe (1 m) | 4 | $16 | Amazon (4-pack) |
| 4 | 4.7 KΩ Resistor | 1 | $0.05 | Any (shared 1-Wire bus) |
| 5 | BME680 Breakout | 1 | $10 | Adafruit |
| 6 | 18650 Li-Ion Cell (protected) | 1 | $5 | Amazon |
| 7 | 18650 Battery Holder | 1 | $1 | Amazon |
| 8 | TP4056 USB-C Charger | 1 | $2 | Amazon |
| 9 | HT7333 LDO | 1 | $0.50 | AliExpress |
| 10 | Resistors 100KΩ ×2, caps | — | $1 | Any |
| 11 | IP65 Enclosure (150×100×70) | 1 | $8 | Amazon |
| 12 | PG7 Cable Glands | 6 | $3 | Amazon |
| 13 | PCB + hookup wire | — | $4 | Amazon |
| | **Total** | | **~$72** | |

### Optional

| Component | Use | ~USD |
|-----------|-----|------|
| 6V 2W Solar Panel | Perpetual outdoor power | $12 |
| 5 m sensor extension cables | Spread probes across large bed | $8 |

---

## Wiring

### Power Circuit

| From | To | Notes |
|------|----|-------|
| 18650 Li-Ion | TP4056 BAT+/BAT− | 3.7V / 3000 mAh |
| TP4056 OUT+ | HT7333 VIN | |
| HT7333 VOUT | **3.3V rail** | All sensors + MCU |
| VBAT | 100KΩ → **GPIO36** → 100KΩ → GND | Battery voltage divider |

### ESP32 — Sensor Connections

| GPIO | Direction | Connects To | Signal | Notes |
|------|-----------|-------------|--------|-------|
| GPIO34 | ← | Soil Sensor 1 AOUT | Analog | Zone 1 |
| GPIO35 | ← | Soil Sensor 2 AOUT | Analog | Zone 2 |
| GPIO32 | ← | Soil Sensor 3 AOUT | Analog | Zone 3 |
| GPIO33 | ← | Soil Sensor 4 AOUT | Analog | Zone 4 |
| GPIO4 | ↔ | DS18B20 shared 1-Wire bus | 1-Wire | 4.7KΩ pull-up to 3V3. All 4 probes share this pin. |
| GPIO21 | ↔ | BME680 SDA | I2C data | |
| GPIO22 | ↔ | BME680 SCL | I2C clock | |
| GPIO36 | ← | Battery voltage divider midpoint | Analog | |
| 3V3 | → | All sensor VCC / VIN / VDD | Power | |
| GND | — | All sensor GND | Common ground | |

### ESP32-C6 Pin Mapping

| Function | GPIO |
|----------|------|
| Soil 1-4 ADC | GPIO0, GPIO1, GPIO2, GPIO3 |
| 1-Wire bus | GPIO4 |
| I2C SDA/SCL | GPIO6/GPIO7 |
| Battery ADC | GPIO5 |

---

## DS18B20 Zone Assignment

All four DS18B20 probes share a single 1-Wire bus. Each probe has a unique 64-bit ROM address. The firmware auto-discovers all probes on first boot and assigns them to zones 1-4 in order of discovery.

To manually assign ROM addresses (for consistent zone mapping after probe replacement), update `config.h`:

```c
// Optional: hard-code DS18B20 ROM addresses for stable zone assignment.
// Read addresses from serial output on first boot.
// #define DS18B20_ZONE1_ROM { 0x28, 0xFF, 0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC }
```

---

## Firmware

```bash
cd esp32/multi-zone-soil
cp src/config.example.h src/config.h
pio run -e wifi-esp32 -t upload
```

---

## Solar Panel Setup (Outdoor)

1. Connect 6V solar panel positive to TP4056 VIN+ (USB side).
2. Connect solar negative to TP4056 GND.
3. The TP4056 handles charge regulation — no extra circuitry needed.
4. With a 6V/2W panel and 18650, the system runs indefinitely in most climates.

---

## Battery Life (No Solar)

| Interval | WiFi | Zigbee |
|----------|------|--------|
| 5 min | ~65 days | ~12 months |
| 15 min | ~180 days | ~3+ years |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Only 1-3 DS18B20 detected | Check wiring on missing probe. All share same bus — a short on one can block all. |
| Zone assignment changes after reboot | Set ROM addresses in config.h for stable mapping. |
| Soil channels read same value | Check each AOUT goes to a different GPIO pin. |
| Outdoor enclosure condensation | Add silica gel packs. Ensure glands are sealed. |
