# Tendril Soil Basic — Sensor Kit

Battery-powered soil moisture and ambient environment monitor for soil, coco coir,
rockwool, and wicking-bed grows. The simplest Tendril sensor — one probe, one board,
months of battery life.

---

## Supported Grow Types

| Grow Type | Medium | Notes |
|-----------|--------|-------|
| Soil | Soil / Super soil / Living soil | Primary use case |
| Coco Coir | Coco coir | Ideal for hand-watered coco |
| Rockwool | Rockwool slabs / cubes | Place probe at root zone |
| Outdoor Container | Soil / Coco-perlite | One kit per pot |
| Wicking Bed | Soil-perlite / Vermiculite | Monitor wicking zone |
| Living Soil / No-Till | Living soil / Super soil | Low-disturbance monitoring |

---

## What It Measures

| Metric | Sensor | Range | Accuracy | MQTT Topic |
|--------|--------|-------|----------|------------|
| Soil moisture | Capacitive v2.0 | 0-100 % | ±3 % | `sensor/readings` |
| Ambient temperature | BME680 | -40 to +85 °C | ±1 °C | `sensor/ambient` |
| Ambient humidity | BME680 | 0-100 % RH | ±3 % RH | `sensor/ambient` |
| Barometric pressure | BME680 | 300-1100 hPa | ±1 hPa | `sensor/ambient` |
| VOC / Air quality | BME680 | 0-500+ kΩ | Relative | `sensor/ambient` |
| Battery voltage | ADC voltage divider | 2.5-4.3 V | ±0.05 V | `status` |

---

## Bill of Materials

### Core Components (Required)

| # | Component | Specification | Qty | ~USD | Source |
|---|-----------|---------------|-----|------|--------|
| 1 | **ESP32-WROOM-32E DevKit** | WiFi variant; 4 MB flash, USB-C | 1 | $8 | Amazon / AliExpress |
| 1a | *or* **ESP32-C6-DevKitM-1** | Zigbee / Matter variant; WiFi + 802.15.4 | 1 | $10 | Espressif / Mouser |
| 2 | **Capacitive Soil Moisture Sensor v2.0** | Corrosion-resistant, analog out, 3.3 V | 1 | $3 | Amazon / AliExpress |
| 3 | **BME680 Breakout Board** | I2C, 3.3 V, Qwiic/STEMMA QT | 1 | $10 | Adafruit / Amazon |
| 4 | **18650 Li-Ion Cell** | 3.7 V, 3000-3500 mAh, **with protection PCB** | 1 | $5 | Amazon / 18650BatteryStore |
| 5 | **TP4056 USB-C Charger Module** | With DW01A battery protection IC | 1 | $2 | Amazon / AliExpress |
| 6 | **HT7333 LDO Voltage Regulator** | SOT-89, 3.3 V 250 mA, 4 µA quiescent | 1 | $0.50 | LCSC / AliExpress |
| 7 | **18650 Battery Holder** | Single cell, solder tabs or spring clips | 1 | $1 | Amazon |
| 8 | **Resistors** | 100 KΩ ¼W (×2) for voltage divider | 2 | $0.10 | Amazon kit |
| 9 | **Capacitors** | 10 µF + 100 nF ceramic for LDO decoupling | 2 | $0.20 | Amazon kit |
| 10 | **Hookup wire** | 22 AWG solid core, assorted colours | — | $5 | Amazon |
| 11 | **Prototype PCB** | 5×7 cm, double-sided | 1 | $1 | Amazon / AliExpress |

### Enclosure (Recommended)

| # | Component | Specification | Qty | ~USD | Source |
|---|-----------|---------------|-----|------|--------|
| 12 | **IP65 Junction Box** | 100×68×50 mm, ABS | 1 | $5 | Amazon |
| 13 | **PG7 Cable Glands** | For sensor cable pass-through | 2 | $1 | Amazon |
| 14 | **Silicone sealant** | Waterproof, clear | — | $5 | Hardware store |

### Optional Add-ons

| # | Component | Use | ~USD |
|---|-----------|-----|------|
| 15 | 6V 1W Mini Solar Panel | Outdoor perpetual power | $8 |
| 16 | Momentary push button | Factory reset / manual wake | $0.50 |
| 17 | LED (green) + 330Ω resistor | Status indicator | $0.20 |

**Total estimated cost**: **$35-42** (WiFi) / **$37-44** (Zigbee/Matter)

---

## Wiring

### Power Circuit

| From | To | Notes |
|------|----|-------|
| 18650 B+ | TP4056 BAT+ | Protected cell, 3.7V nominal |
| 18650 B− | TP4056 BAT− | |
| TP4056 OUT+ | HT7333 VIN | |
| TP4056 OUT− | HT7333 GND | |
| HT7333 VOUT | **3.3V rail** | Add 10 µF input cap, 100 nF + 10 µF output caps |

### Battery Monitor

| From | To | Notes |
|------|----|-------|
| VBAT (TP4056 OUT+) | 100KΩ resistor → **GPIO35** → 100KΩ resistor → GND | Divides VBAT by 2 (4.2V → ~2.1V) for safe ADC reading |

### ESP32 — Sensor Connections

| GPIO | Direction | Connects To | Signal | Voltage |
|------|-----------|-------------|--------|---------|
| GPIO21 | ↔ | BME680 SDA | I2C data | 3.3V |
| GPIO22 | ↔ | BME680 SCL | I2C clock | 3.3V |
| GPIO34 | ← | Soil Moisture AOUT | Analog 0–3.3V | 3.3V |
| GPIO35 | ← | Battery voltage divider midpoint | Analog | — |
| 3V3 | → | BME680 VIN, Soil VCC | Power | 3.3V |
| GND | — | BME680 GND, Soil GND | Common ground | — |

### ESP32-C6 Pin Mapping (Zigbee / Matter variant)

| Function | ESP32-C6 GPIO | Notes |
|----------|---------------|-------|
| I2C SDA | GPIO6 | BME680 data |
| I2C SCL | GPIO7 | BME680 clock |
| Soil moisture ADC | GPIO0 (ADC1_CH0) | Analog input |
| Battery ADC | GPIO1 (ADC1_CH1) | Voltage divider |
| Status LED | GPIO8 | On-board LED (C6-DevKitM) |
| Reset button | GPIO9 | BOOT button (factory reset) |

---

## Assembly Guide

### Step 1 — Prepare the Power Circuit
1. Solder the 18650 holder to the TP4056 module (B+ → red, B− → black)
2. Connect TP4056 OUT+ → HT7333 VIN, TP4056 OUT− → HT7333 GND
3. Solder 10 µF cap across HT7333 input, 100 nF + 10 µF across output
4. HT7333 VOUT is your 3.3V rail, GND is common ground

### Step 2 — Wire the Battery Monitor
1. Solder 100 KΩ resistor from VBAT (TP4056 OUT+) to GPIO35
2. Solder 100 KΩ resistor from GPIO35 to GND
3. This divides VBAT by 2 so a 4.2V battery reads ~2.1V on the ADC

### Step 3 — Connect Sensors
1. Wire BME680: VIN → 3V3, GND → GND, SDA → GPIO21, SCL → GPIO22
2. Wire soil sensor: VCC → 3V3, GND → GND, AOUT → GPIO34

### Step 4 — Enclosure
1. Drill holes in the IP65 box for USB-C access and cable glands
2. Feed the soil sensor cable through one PG7 gland
3. Mount the PCB with standoffs or hot glue
4. Seal cable glands with silicone

### Step 5 — Calibrate Soil Sensor
1. Record the ADC reading with the probe in dry air → `SOIL_DRY_VALUE`
2. Submerge the probe to the line in a glass of water → `SOIL_WET_VALUE`
3. Enter these values in `config.h`

---

## Firmware

### Flash (WiFi — ESP32)
```bash
cd esp32/soil-basic
cp src/config.example.h src/config.h
# Edit config.h with your values
pio run -e wifi-esp32 -t upload
pio device monitor -b 115200
```

### Flash (WiFi — ESP32-C6)
```bash
pio run -e wifi-esp32c6 -t upload
```

### Flash (Zigbee — ESP32-C6)
```bash
pio run -e zigbee-esp32c6 -t upload
```

### Flash (Matter — ESP32-C6)
```bash
pio run -e matter-esp32c6 -t upload
```

---

## Configuration

Copy `src/config.example.h` to `src/config.h` and edit:

```c
// WiFi (only for wifi-* builds)
#define WIFI_SSID     "YourNetwork"
#define WIFI_PASS     "YourPassword"

// MQTT
#define MQTT_HOST     "api.tendrilgrow.com"
#define MQTT_PORT     8883
#define MQTT_DEVICE_ID "td-XXXXXXXXXXXX"   // From Tendril dashboard
#define MQTT_PSK       "your-psk-here"     // From device registration

// Tenant
#define TENANT_ID     "your-tenant-uuid"

// Soil calibration
#define SOIL_DRY_VALUE 2800   // ADC reading in dry air
#define SOIL_WET_VALUE 1200   // ADC reading in water
```

---

## Battery Life Estimates

| Protocol | Interval | Daily Cycles | Avg Current | 18650 (3000 mAh) |
|----------|----------|-------------|-------------|-------------------|
| WiFi | 5 min | 288 | ~1.1 mA | ~110 days |
| WiFi | 15 min | 96 | ~0.4 mA | ~310 days |
| Zigbee | 5 min | 288 | ~0.07 mA | ~4.7 years |
| Zigbee | 15 min | 96 | ~0.03 mA | ~10+ years |
| Matter | 5 min | 288 | ~0.08 mA | ~4.3 years |

Add a 6V solar panel for indefinite outdoor operation.

---

## Pairing with Tendril

1. Go to **Dashboard → Devices → Add Device**
2. Select **Tendril Soil Basic** as the device type
3. Copy the generated **Device ID** and **PSK** into your `config.h`
4. Flash the firmware and power on
5. The device appears as "Online" within 60 seconds
6. Assign the device to a **tent** and **bucket/pot**
7. Soil moisture and ambient data begin flowing to your grow dashboard

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No serial output | Wrong board selected | Check `platformio.ini` board matches your hardware |
| WiFi won't connect | Wrong credentials or out of range | Double-check SSID/password, move closer to router |
| MQTT connect fails | Wrong host/port/PSK | Verify credentials in Tendril dashboard |
| Soil reads 0% always | Sensor not calibrated | Re-calibrate dry/wet values |
| Soil reads 100% always | Sensor wired to wrong pin or broken | Check AOUT → GPIO34, try a new sensor |
| BME680 not found | I2C wiring issue | Check SDA/SCL connections, try address 0x76 |
| Battery drains fast | Not entering deep sleep | Check serial log for sleep messages |
| Device shows offline | WiFi or MQTT dropping | Check signal strength, reduce interval |
