## 1. NFT Config Build (api/app/grows/grow_type_configs/nft.py)

### Channel & Flow Engineering (NFT's Core Differentiator)
- [ ] 1.1 Define channel engineering section: slope tables, width by plant size, material guide, length limits, spacing
- [ ] 1.2 Define flow rate management: thin film targets, pump sizing per channel count, flow uniformity verification
- [ ] 1.3 Define root mat management guide: blockage signs, training techniques, trimming protocol, cleaning schedule
- [ ] 1.4 Define pump failure protocol: 2-5 minute death window, backup requirements, battery backup, alarm integration
- [ ] 1.5 Define salt accumulation management: EC gradient monitoring, flush schedules, bi-directional flow
- [ ] 1.6 Define propagation-to-channel transfer: rockwool cube readiness, placement technique, post-transfer monitoring

### Stages (12 stages — NFT-specific flow and channel parameters)
- [ ] 1.7 Build germination + seedling stages (in rockwool cubes, NOT in channels yet)
- [ ] 1.8 Build early veg stage (channel placement, initial flow rate, root establishment monitoring)
- [ ] 1.9 Build late veg through transition (increasing flow rate, root mat monitoring begins)
- [ ] 1.10 Build flower stages (peak flow requirements, root trimming if needed, salt flush schedule)
- [ ] 1.11 Build flush, harvest, drying, curing stages
- [ ] 1.12 Add environment variants (indoor/outdoor/greenhouse) per stage

### Equipment, Troubleshooting, Quick Reference
- [ ] 1.13 Build equipment list: channels, end caps, pump + backup, flow restrictors, slope tools, rockwool cubes
- [ ] 1.14 Build troubleshooting: Flow Issues, Root Blockage, Salt Buildup, Pump Failure, Channel Leaks
- [ ] 1.15 Build quick reference: flow rate by stage, slope specs, channel sizing table, pump failure response
- [ ] 1.16 Add commercial NFT section: multi-tier, A-frame, conveyor systems

### Scale, Strain, Water Source
- [ ] 1.17 Add scale tiers (single channel → commercial multi-tier)
- [ ] 1.18 Add auto/photo strain variants
- [ ] 1.19 Add water source profiles

## 2. Registration & Testing
- [ ] 2.1 Register NFT_CONFIG in __init__.py
- [ ] 2.2 Config completeness test
