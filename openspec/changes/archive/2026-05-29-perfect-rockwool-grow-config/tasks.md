## 1. Rockwool Config Build (api/app/grows/grow_type_configs/rockwool.py)

### Crop Steering & Shot Irrigation (Rockwool's Core Differentiator)
- [x] 1.1 Define slab conditioning protocol: pH soak procedure, verification, common mistakes
- [x] 1.2 Define crop steering deep dive: vegetative vs generative, dryback targets, EC manipulation, transition timelines
- [x] 1.3 Define shot-based irrigation: volume, count, first/last shot timing, P1/P2/P3 phases, stage-based ramp
- [x] 1.4 Define slab weight tracking: field capacity calibration, dry weight baseline, target ranges, measurement methods
- [x] 1.5 Define cube-to-slab propagation: 1" → 4" → slab, transition signals, technique, post-transplant care
- [x] 1.6 Define slab management: drainage slits, wrapping, tilting, multi-plant configs, replacement schedule
- [x] 1.7 Define environmental health: handling safety (gloves/mask), disposal, recycling programs

### Stages (12 stages — shot parameters + dryback targets per stage)
- [x] 1.8 Build germination + seedling (in rockwool cubes, not slabs yet)
- [x] 1.9 Build veg stages (cube-to-slab transplant, vegetative steering, increasing shot count)
- [x] 1.10 Build transition + flower stages (shift to generative steering, peak shot count, dryback management)
- [x] 1.11 Build flush, harvest, drying, curing stages
- [x] 1.12 Add environment variants per stage

### Equipment, Troubleshooting, Quick Reference
- [x] 1.13 Build equipment: cubes, slabs, drip stakes, irrigation controller, substrate sensors, scale, pH conditioning supplies
- [x] 1.14 Build troubleshooting: pH Conditioning, Algae on Slabs, Overwatering, Root Zone Issues, Shot Timing Problems
- [x] 1.15 Build quick reference: shot schedule by stage, dryback targets, steering cheat sheet, conditioning protocol

### Scale, Strain, Water Source
- [x] 1.16 Add scale tiers (hobby with manual irrigation → commercial with Aroya/GroSens integration)
- [x] 1.17 Add auto/photo variants, water source profiles

## 2. Registration & Testing
- [x] 2.1 Register ROCKWOOL_CONFIG in __init__.py
- [x] 2.2 Config completeness test
