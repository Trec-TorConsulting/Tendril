# Tendril Sensor Hardware — ESP32 Firmware Collection

Production-grade, battery-powered sensor kits for every grow type Tendril supports.
Each kit ships firmware for **WiFi (MQTT)**, **Zigbee 3.0**, and **Matter** connectivity.

## Sensor Kits

| Kit | Use Case | Key Sensors | Battery Life (WiFi/Zigbee) |
|-----|----------|-------------|---------------------------|
| [soil-basic](soil-basic/) | Soil / Coco / Rockwool — basic | Soil moisture, ambient temp/humidity | ~3 mo / ~18 mo |
| [soil-pro](soil-pro/) | Soil / Coco — with runoff analysis | Soil moisture + temp, runoff pH & EC | ~2 mo / ~12 mo |
| [hydro-monitor](hydro-monitor/) | DWC / RDWC / NFT / Ebb & Flow / Drip | Water temp, pH, EC, reservoir level | ~6 wk / ~6 mo |
| [aero-monitor](aero-monitor/) | Aeroponics | All hydro sensors + mist pressure | ~5 wk / ~5 mo |
| [multi-zone-soil](multi-zone-soil/) | Outdoor beds / multi-pot | 4× soil moisture + temp, ambient | ~2 mo / ~12 mo |
| [environment-monitor](environment-monitor/) | Tent / room ambient | CO₂, temp, humidity, light, VOC | ~6 wk / ~8 mo |
| [water-reservoir](water-reservoir/) | Reservoir / irrigation | Water level, temp, flow rate | ~3 mo / ~18 mo |

## Grow Type → Kit Mapping

| Grow Type | Primary Kit | Optional Add-on |
|-----------|------------|-----------------|
| DWC / RDWC | hydro-monitor | environment-monitor |
| NFT | hydro-monitor | environment-monitor |
| Ebb & Flow | hydro-monitor | environment-monitor |
| Drip / Top Feed | hydro-monitor | water-reservoir |
| Aeroponics | aero-monitor | environment-monitor |
| Kratky | water-reservoir | environment-monitor |
| Coco Coir | soil-pro | environment-monitor |
| Rockwool | soil-basic | environment-monitor |
| Soil / Living Soil | soil-pro | environment-monitor |
| Outdoor Soil | multi-zone-soil | — |
| Outdoor Container | soil-basic (per pot) | — |
| Aquaponics | hydro-monitor | water-reservoir |
| Dutch Bucket | hydro-monitor | multi-zone-soil |
| Vertical / Tower | hydro-monitor | environment-monitor |
| Wicking Bed | soil-basic | water-reservoir |

## Connectivity Options

Every kit supports three protocol variants built from the same source tree:

### WiFi (MQTT over TLS)
- **MCU**: ESP32-WROOM-32E or ESP32-C6
- **Protocol**: MQTT → Tendril API directly
- **Range**: Standard WiFi (~30 m indoors)
- **Power**: Moderate (WiFi radio draws ~160 mA during TX)
- **Best for**: Grows near a WiFi router, simplest setup

### Zigbee 3.0
- **MCU**: ESP32-C6 (802.15.4 radio)
- **Protocol**: Zigbee → Zigbee2MQTT → MQTT → Tendril API
- **Range**: Mesh network (~10-30 m per hop, extends with routers)
- **Power**: Excellent (802.15.4 radio draws ~15 mA during TX)
- **Best for**: Battery longevity, mesh coverage, large facilities
- **Requires**: Zigbee coordinator (e.g., Sonoff ZBDongle-E, $20)

### Matter (over Thread)
- **MCU**: ESP32-C6 (802.15.4 radio)
- **Protocol**: Matter → Thread Border Router → Home network
- **Range**: Thread mesh (~10-30 m per hop)
- **Power**: Excellent (same radio as Zigbee)
- **Best for**: Apple Home / Google Home / Alexa / Home Assistant ecosystems
- **Requires**: Thread Border Router (Apple TV 4K, HomePod Mini, Google Nest Hub, etc.)

## Repository Structure

```
esp32/
├── README.md                       ← You are here
├── LICENSE
├── shared/                         ← Shared libraries (all kits)
│   └── lib/
│       ├── TendrilPower/           Battery management & deep sleep
│       └── TendrilMQTT/           MQTT client with TLS-PSK
├── soil-basic/                     ← Kit firmware projects
├── soil-pro/
├── hydro-monitor/
├── aero-monitor/
├── multi-zone-soil/
├── environment-monitor/
└── water-reservoir/
```

Each kit folder contains:
```
kit-name/
├── README.md            Full docs: BOM, wiring, build, setup
├── platformio.ini       PlatformIO build config (wifi/zigbee/matter envs)
└── src/
    ├── config.example.h Hardware pin & credential config
    ├── sensors.h        Sensor interface
    ├── sensors.cpp      Sensor drivers (shared across protocols)
    ├── main_wifi.cpp    WiFi + MQTT entry point
    ├── main_zigbee.cpp  Zigbee 3.0 entry point (ESP-IDF)
    └── main_matter.cpp  Matter entry point (ESP-IDF)
```

## Quick Start

### Prerequisites
- PlatformIO (VS Code extension or CLI)
- USB-C cable for flashing
- Parts from the kit's BOM

### Flash Any Kit (WiFi Example)
```bash
cd esp32/soil-basic
cp src/config.example.h src/config.h
# Edit src/config.h with your WiFi, MQTT, and tenant credentials
pio run -e wifi-esp32 -t upload
```

### Flash Zigbee Variant
```bash
cd esp32/soil-basic
cp src/config.example.h src/config.h
pio run -e zigbee-esp32c6 -t upload
```

### Monitor Serial Output
```bash
pio device monitor -b 115200
```

## Battery & Power Design

All kits share a common power architecture:

- **Cell**: 18650 Li-Ion (3.7V nominal, 3000-3500 mAh)
- **Charger**: TP4056 USB-C module with DW01A protection
- **Regulator**: HT7333 LDO (3.3V, 250 mA, low quiescent current)
- **Monitoring**: Voltage divider (100K/100K) → ADC for battery percentage
- **Deep sleep**: ESP32 ULP or RTC timer between readings
- **Solar** (optional for outdoor kits): 6V/1W panel → TP4056 input

### Power Budget (WiFi, 5-minute intervals)

| Phase | Current | Duration | Energy per cycle |
|-------|---------|----------|-----------------|
| Wake + sensor read | 40 mA | 500 ms | 20 mA·s |
| WiFi connect + MQTT publish | 160 mA | 2,000 ms | 320 mA·s |
| Deep sleep | 10 µA | 297,500 ms | 2.975 mA·s |
| **Average** | **~1.14 mA** | — | — |
| **18650 (3000 mAh) life** | — | — | **~110 days** |

### Power Budget (Zigbee, 5-minute intervals)

| Phase | Current | Duration | Energy per cycle |
|-------|---------|----------|-----------------|
| Wake + sensor read | 35 mA | 500 ms | 17.5 mA·s |
| Zigbee TX | 15 mA | 200 ms | 3 mA·s |
| Deep sleep | 5 µA | 299,300 ms | 1.497 mA·s |
| **Average** | **~0.073 mA** | — | — |
| **18650 (3000 mAh) life** | — | — | **~4.7 years** |

## Provisioning & Pairing

1. **Flash firmware** with PlatformIO
2. **Configure** `config.h` with credentials (WiFi) or use BLE provisioning (Zigbee/Matter)
3. **Register device** in Tendril: Dashboard → Devices → Add Device → scan QR code
4. **Assign to tent/bucket** in Tendril to start receiving data

WiFi devices register with a pre-shared key (PSK) and authenticate via MQTT.
Zigbee/Matter devices are discovered through their respective ecosystems and bridged to Tendril.

## OTA Updates

WiFi kits support over-the-air firmware updates triggered from the Tendril dashboard.
Zigbee/Matter OTA follows their respective protocol's update mechanisms.

## Safety

- All kits operate at 3.3V DC — no high voltage
- Waterproof sensors (DS18B20, JSN-SR04T) are IP67/IP68 rated
- pH/EC probes should not be left in solution 24/7 without Atlas Scientific industrial probes
- Keep electronics out of direct water spray — use IP65+ enclosures for humid environments
- 18650 cells must have built-in protection circuits (PCB/BMS)

## License

CERN Open Hardware Licence v2 — Permissive. See [LICENSE](LICENSE).
