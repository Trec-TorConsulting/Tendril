# Tendril Aero Monitor — Sensor Kit

Everything from the **Hydro Monitor** plus a **mist/nozzle pressure transducer**
for aeroponics systems. Tracks reservoir health and verifies mist chamber pressure
in real time.

---

## Supported Grow Types

| Grow Type | Notes |
|-----------|-------|
| Aeroponics | High-pressure aero (80+ PSI) and low-pressure aero |

---

## What It Measures

| Metric | Sensor | Range | Accuracy | MQTT Topic |
|--------|--------|-------|----------|------------|
| Water temperature | DS18B20 waterproof | -10 to +85 °C | ±0.5 °C | `sensor/hydro` |
| pH | DFRobot Gravity pH v2 | 0-14 | ±0.1 | `sensor/hydro` |
| EC | DFRobot Gravity EC v2 | 0-20 mS/cm | ±5 % | `sensor/hydro` |
| Water level | JSN-SR04T ultrasonic | 25-450 cm | ±1 cm | `sensor/hydro` |
| **Mist pressure** | **Pressure transducer 0-150 PSI** | **0-150 PSI** | **±1.5 %** | **`sensor/pressure`** |
| Battery | ADC divider | 2.5-4.3 V | ±0.05 V | `status` |

---

## Bill of Materials

*Includes everything from the Hydro Monitor BOM, plus:*

| # | Component | Specification | Qty | ~USD | Source |
|---|-----------|---------------|-----|------|--------|
| A1 | **Pressure Transducer** | 0-150 PSI, 0.5-4.5V output, 1/4" NPT | 1 | $15 | Amazon |
| A2 | **1/4" NPT Tee Fitting** | Brass, for inline plumbing | 1 | $5 | Hardware store |
| A3 | **Teflon Tape** | For thread sealing | 1 | $2 | Hardware store |

**Total (Aero Monitor)**: ~$140 (Hydro BOM + aero add-ons)

---

## Wiring

Inherits the full **Hydro Monitor** wiring (see `hydro-monitor/README.md`), plus the
pressure transducer below.

### Additional Connection — Pressure Transducer

| GPIO | Direction | Connects To | Signal | Power Rail |
|------|-----------|-------------|--------|------------|
| GPIO36 | ← | Voltage divider midpoint | Analog (scaled) | — |
| — | — | Transducer VCC | — | **5V** (MOSFET-switched) |
| — | — | Transducer GND | — | GND |

### Voltage Divider (required)

The transducer outputs 0.5 V at 0 PSI and 4.5 V at 150 PSI. Since the ESP32 ADC
max is 3.3 V, a voltage divider scales the output to a safe range:

| From | Through | To |
|------|---------|----|
| Transducer signal out | **47KΩ** resistor | Midpoint (GPIO36) |
| Midpoint (GPIO36) | **100KΩ** resistor | GND |

This scales 4.5 V → ~3.06 V at the ADC pin.

---

## Pressure Transducer Installation

1. Install the 1/4" NPT tee fitting inline on the high-pressure output (after the pump, before the mist nozzles).
2. Thread the transducer into the tee with Teflon tape.
3. Route the wire to your enclosure through a cable gland.
4. **Do not exceed the transducer's rated pressure** (150 PSI for most units).

---

## Firmware

```bash
cd esp32/aero-monitor
cp src/config.example.h src/config.h
pio run -e wifi-esp32 -t upload
```

Uses the same build environments as Hydro Monitor (wifi-esp32, wifi-esp32c6, zigbee-esp32c6, matter-esp32c6).

---

## Configuration

All Hydro Monitor settings, plus:

```c
#define PRESSURE_ADC_PIN    36      // Transducer analog output
#define PRESSURE_MAX_PSI    150.0f  // Full-scale PSI of your transducer
#define PRESSURE_V_MIN      0.5f    // Output voltage at 0 PSI
#define PRESSURE_V_MAX      4.5f    // Output voltage at max PSI
#define PRESSURE_R1         47000   // Voltage divider top (Ω)
#define PRESSURE_R2         100000  // Voltage divider bottom (Ω)
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Pressure reads 0 constantly | Check 5V power to transducer. Verify GPIO pin. |
| Pressure reads max constantly | Transducer may be damaged or air-locked. Check plumbing. |
| Pressure fluctuates wildly | Add a 100nF cap between signal and GND at the ADC pin. |
