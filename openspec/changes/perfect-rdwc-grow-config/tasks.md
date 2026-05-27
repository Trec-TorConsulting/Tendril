## 1. RDWC Config Build (api/app/grows/grow_type_configs/rdwc.py)

### Plumbing & System Architecture (RDWC's Core Differentiator)
- [x] 1.1 Define plumbing architecture section: pipe sizing table by site count (2-50+), flow patterns (waterfall vs current-culture), fitting guide
- [x] 1.2 Define system sizing calculator: total water volume, pump GPH, airline requirements, chiller BTU sizing
- [x] 1.3 Define central reservoir management: control bucket sizing rules, sensor placement, dosing integration points
- [x] 1.4 Define flow distribution targets: GPH per site by pipe diameter, manifold vs daisy-chain guidance
- [x] 1.5 Define failure mode responses: pump failure, line clog, leak, power outage — severity + response time + protocol
- [x] 1.6 Define cross-contamination protocol: quarantine, isolation valves, system flush, sterilization

### Stages (12 stages — RDWC-specific reservoir and task differences)
- [x] 1.7 Build germination stage (seedlings propagated separately before connecting to system)
- [x] 1.8 Build seedling stage (connect to system when roots reach water, system prime procedure)
- [x] 1.9 Build early veg through late veg stages (central dosing approach, flow monitoring)
- [x] 1.10 Build transition through mid flower stages (flow rate adjustments for heavy root mass)
- [x] 1.11 Build late flower, flush, harvest stages (sequential harvest strategy for connected systems)
- [x] 1.12 Build drying and curing stages (same as DWC)
- [x] 1.13 Add environment variants (indoor/outdoor/greenhouse) for each stage

### Equipment, Troubleshooting, Quick Reference
- [x] 1.14 Build RDWC equipment list: circulation pump, plumbing fittings, control bucket, flow meters, inline filter, UV sterilizer (optional)
- [x] 1.15 Build troubleshooting guide: Plumbing Issues, Flow Distribution, Central Reservoir, Root Zone, Water Quality
- [x] 1.16 Build quick reference: system sizing table, pH/EC by stage, flow targets, maintenance schedule
- [x] 1.17 Build plumbing maintenance schedule: biofilm cleaning, salt removal, leak inspection, winterization

### Scale, Strain, Water Source
- [x] 1.18 Add scale tier profiles (2-site hobby → 50+ site commercial)
- [x] 1.19 Add auto/photo strain duration variants
- [x] 1.20 Add water source profiles (same as DWC but with system volume considerations)

## 2. Registration & API
- [x] 2.1 Register RDWC_CONFIG in grow_type_configs/__init__.py
- [x] 2.2 Verify /v1/grow-types/rdwc/config returns full config

## 3. Testing
- [x] 3.1 Config completeness test: all 12 stages, required fields, equipment, troubleshooting present
- [x] 3.2 Plumbing sizing table validation: values scale logically with site count
