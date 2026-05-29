## 1. Aeroponics Config Build (api/app/grows/grow_type_configs/aeroponics.py)

### Mist & Pressure System (Aeroponics' Core Differentiator)
- [x] 1.1 Define HPA vs LPA comparison: equipment, performance, maintenance, difficulty
- [x] 1.2 Define mist cycle engineering: on/off timing per stage, day/night adjustments, cycle optimization by root observation
- [x] 1.3 Define nozzle management: types, clog prevention (inline filter specs), cleaning protocol, backup strategy, spray verification
- [x] 1.4 Define root chamber design: light exclusion, temp control, humidity dynamics, material specs, drain design
- [x] 1.5 Define pressure system: accumulator sizing, pressure switch settings, solenoid selection, gauge monitoring
- [x] 1.6 Define failure modes: nozzle clog, pump failure, solenoid stuck, power failure — severity + response time + emergency protocols
- [x] 1.7 Define nutrient approach: low EC targets, synthetic only, particle filtration, frequent changes, no organics

### Stages (12 stages — mist cycle timing is the key parameter)
- [x] 1.8 Build germination + seedling (clones/seedlings must have root mass before chamber placement)
- [x] 1.9 Build veg stages (mist cycle ramp, root observation checkpoints, nozzle inspection)
- [x] 1.10 Build flower stages (adjusted mist cycles, peak EC — still lower than other hydro)
- [x] 1.11 Build flush, harvest, drying, curing stages
- [x] 1.12 Add environment variants (indoor primarily — outdoor aero is extremely rare)

### Equipment, Troubleshooting, Quick Reference
- [x] 1.13 Build HPA equipment list: accumulator, solenoids, high-pressure pump, mist nozzles, inline filters, pressure gauge
- [x] 1.14 Build LPA equipment list: pump, mist sprayers, timer with seconds precision, inline filter
- [x] 1.15 Build troubleshooting: Nozzle Issues, Pressure Problems, Root Chamber, Pump Failure, Algae
- [x] 1.16 Build quick reference: mist cycle by stage, pressure targets, EC by stage, nozzle maintenance schedule
- [x] 1.17 Add clone/propagation integration section (aeroponics is gold standard for cloning)

### Scale, Strain, Water Source
- [x] 1.18 Add scale tiers (hobby chamber → commercial multi-zone)
- [x] 1.19 Add auto/photo variants, water source profiles (RO preferred for nozzle longevity)

## 2. Registration & Testing
- [x] 2.1 Register AERO_CONFIG in __init__.py
- [x] 2.2 Config completeness test
