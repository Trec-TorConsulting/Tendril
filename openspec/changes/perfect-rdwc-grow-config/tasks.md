## 1. RDWC Config Build (api/app/grows/grow_type_configs/rdwc.py)

### Plumbing & System Architecture (RDWC's Core Differentiator)
- [ ] 1.1 Define plumbing architecture section: pipe sizing table by site count (2-50+), flow patterns (waterfall vs current-culture), fitting guide
- [ ] 1.2 Define system sizing calculator: total water volume, pump GPH, airline requirements, chiller BTU sizing
- [ ] 1.3 Define central reservoir management: control bucket sizing rules, sensor placement, dosing integration points
- [ ] 1.4 Define flow distribution targets: GPH per site by pipe diameter, manifold vs daisy-chain guidance
- [ ] 1.5 Define failure mode responses: pump failure, line clog, leak, power outage — severity + response time + protocol
- [ ] 1.6 Define cross-contamination protocol: quarantine, isolation valves, system flush, sterilization

### Stages (12 stages — RDWC-specific reservoir and task differences)
- [ ] 1.7 Build germination stage (seedlings propagated separately before connecting to system)
- [ ] 1.8 Build seedling stage (connect to system when roots reach water, system prime procedure)
- [ ] 1.9 Build early veg through late veg stages (central dosing approach, flow monitoring)
- [ ] 1.10 Build transition through mid flower stages (flow rate adjustments for heavy root mass)
- [ ] 1.11 Build late flower, flush, harvest stages (sequential harvest strategy for connected systems)
- [ ] 1.12 Build drying and curing stages (same as DWC)
- [ ] 1.13 Add environment variants (indoor/outdoor/greenhouse) for each stage

### Equipment, Troubleshooting, Quick Reference
- [ ] 1.14 Build RDWC equipment list: circulation pump, plumbing fittings, control bucket, flow meters, inline filter, UV sterilizer (optional)
- [ ] 1.15 Build troubleshooting guide: Plumbing Issues, Flow Distribution, Central Reservoir, Root Zone, Water Quality
- [ ] 1.16 Build quick reference: system sizing table, pH/EC by stage, flow targets, maintenance schedule
- [ ] 1.17 Build plumbing maintenance schedule: biofilm cleaning, salt removal, leak inspection, winterization

### Scale, Strain, Water Source
- [ ] 1.18 Add scale tier profiles (2-site hobby → 50+ site commercial)
- [ ] 1.19 Add auto/photo strain duration variants
- [ ] 1.20 Add water source profiles (same as DWC but with system volume considerations)

## 2. Registration & API
- [ ] 2.1 Register RDWC_CONFIG in grow_type_configs/__init__.py
- [ ] 2.2 Verify /v1/grow-types/rdwc/config returns full config

## 3. Testing
- [ ] 3.1 Config completeness test: all 12 stages, required fields, equipment, troubleshooting present
- [ ] 3.2 Plumbing sizing table validation: values scale logically with site count
