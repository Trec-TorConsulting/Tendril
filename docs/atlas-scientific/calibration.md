# Atlas Scientific EZO Calibration Guide

Proper calibration is essential for accurate readings. Atlas EZO circuits store
calibration data on-board — it persists across power cycles.

---

## pH Calibration (3-Point)

### Equipment Needed
- pH 4.00 buffer solution
- pH 7.00 buffer solution
- pH 10.00 buffer solution
- Rinse bottle with distilled/DI water
- Small beakers or cups

### Procedure

1. **Rinse** the probe thoroughly with DI water, shake off excess
2. **Mid-point** — Place probe in pH 7.00 buffer
   - Wait 1-2 minutes for reading to stabilize
   - Send command: `Cal,mid,7.00`
   - Response: `*OK`
3. **Low-point** — Rinse, place probe in pH 4.00 buffer
   - Wait 1-2 minutes
   - Send command: `Cal,low,4.00`
   - Response: `*OK`
4. **High-point** — Rinse, place probe in pH 10.00 buffer
   - Wait 1-2 minutes
   - Send command: `Cal,high,10.00`
   - Response: `*OK`

### I2C Command (from ESP32)

```cpp
#include <Wire.h>

void calibratePH(uint8_t addr, const char* cmd) {
    Wire.beginTransmission(addr);
    Wire.print(cmd);  // e.g. "Cal,mid,7.00"
    Wire.endTransmission();
    delay(900);       // EZO needs ~900ms to process calibration
}
```

### Verification
- Send `Cal,?` to check calibration status
- Response: `?Cal,3` means 3-point calibration stored

---

## EC Calibration (2-Point)

### Equipment Needed
- Dry calibration (air)
- 1413 µS/cm calibration solution (or 12,880 µS/cm for high-range)
- Rinse bottle with DI water

### Procedure

1. **Dry calibration** — Probe in air, completely dry
   - Send command: `Cal,dry`
   - Response: `*OK`
2. **Single-point** — Rinse, place probe in 1413 µS/cm solution
   - Wait 1-2 minutes
   - Send command: `Cal,one,1413`
   - Response: `*OK`

### Optional Dual-Point (for wider range)

3. **Low-point** — 1413 µS/cm: `Cal,low,1413`
4. **High-point** — 12880 µS/cm: `Cal,high,12880`

### Setting the K Value

The K value must match your probe:

| Probe | K Value | Range |
|-------|---------|-------|
| K 0.1 | 0.1 | 0.5 – 50 µS/cm (ultra-pure water) |
| K 1.0 | 1.0 | 5 – 200,000 µS/cm (general hydro) |
| K 10 | 10 | 10 – 1,000,000 µS/cm (seawater, brine) |

Send: `K,1.0` to set K value (most hydroponic setups use K 1.0).

---

## RTD Temperature Calibration

### Equipment Needed
- Ice bath (0 °C) or boiling water (100 °C)
- Accurate reference thermometer

### Procedure

PT-1000 probes are factory-calibrated and typically don't need user calibration.
If readings are off:

1. Place probe in ice bath, wait 2 minutes
2. Send command: `Cal,0`
3. Or use boiling water: `Cal,100`

---

## Dissolved Oxygen Calibration

### Equipment Needed
- Open air (atmospheric calibration)
- Optional: 0 mg/L solution (sodium sulfite)

### Procedure

1. **Atmospheric calibration** — Probe in open air, wet the membrane
   - Send command: `Cal`
   - Response: `*OK` (calibrates to atmospheric O2)
2. **Zero-point** (optional) — Place in 0 DO solution
   - Send command: `Cal,0`

### Pressure/Salinity Compensation

For accurate DO readings, set compensation values:

- Pressure: `P,101.3` (kPa, default sea level)
- Salinity: `S,0.0` (ppt, default freshwater)
- Temperature: Applied automatically if RTD probe connected

---

## Calibration Schedule

| Probe | Frequency | Signs of Drift |
|-------|-----------|----------------|
| pH | Every 2-4 weeks | Reading off by >0.2 in buffer |
| EC | Every 1-3 months | Dry cal first, then solution |
| RTD | Rarely (factory cal) | Compare to reference thermometer |
| DO | Every 2-4 weeks | Atmospheric reading ≠ ~8-9 mg/L |

---

## Storing Probes

| Probe | Storage | Never Do |
|-------|---------|----------|
| pH | KCl storage solution in cap | Store dry — kills the probe |
| EC | Dry, cap on | Submerge long-term in DI water |
| RTD | Dry or submerged, no preference | — |
| DO | Cap with wet sponge | Let membrane dry out |

---

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| pH always reads 7.0 | Probe dead or not connected | Check BNC connector, try new probe |
| pH drifts rapidly | Probe needs replacement | Replace after 1-2 years |
| EC reads 0 in solution | K value wrong or dry cal missing | Run `Cal,dry` first |
| DO reads very high | Membrane damaged | Replace DO membrane cap |
| No I2C response | Still in UART mode | Short PGND→TX and power cycle |
| All readings NaN | Pull-up resistors missing | Add 4.7KΩ on SDA and SCL |
