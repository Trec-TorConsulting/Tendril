## 1. Drip Config Build (api/app/grows/grow_type_configs/drip.py)

### Emitter & Runoff Management (Drip's Core Differentiator)
- [x] 1.1 Define emitter management: types, clog detection, cleaning protocol, flow verification
- [x] 1.2 Define runoff monitoring: input vs runoff EC/pH interpretation, target runoff %, flush triggers
- [x] 1.3 Define DTW vs recirculating decision guide with equipment requirements for each
- [x] 1.4 Define media-specific irrigation profiles: coco, rockwool, perlite, mixed — shot count/volume/timing per stage
- [x] 1.5 Define crop steering section: generative vs vegetative, dryback targets, EC manipulation, shot timing strategies
- [x] 1.6 Define irrigation scheduling: first/last shot timing, P1-P2-P3 shot strategy, stage-based ramp

### Stages (12 stages — media-specific irrigation + runoff targets)
- [x] 1.7 Build germination + seedling (hand watering or low-volume drip, propagation)
- [x] 1.8 Build veg stages (increasing shot count, vegetative steering, runoff monitoring begins)
- [x] 1.9 Build transition + flower stages (generative steering, peak irrigation, runoff EC management)
- [x] 1.10 Build flush, harvest, drying, curing stages
- [x] 1.11 Add environment variants per stage

### Equipment, Troubleshooting, Quick Reference
- [x] 1.12 Build equipment: emitters, manifold, pump, timer/controller, runoff trays, substrate sensors
- [x] 1.13 Build troubleshooting: Emitter Clogs, Runoff Issues, Media Problems, Salt Buildup, Uneven Growth
- [x] 1.14 Build quick reference: irrigation schedule matrix (media × stage), runoff interpretation chart, crop steering cheat sheet

### Scale, Strain, Water Source
- [x] 1.15 Add scale tiers (hand watering → commercial precision controller)
- [x] 1.16 Add auto/photo variants, water source profiles

## 2. Registration & Testing
- [x] 2.1 Register DRIP_CONFIG in __init__.py
- [ ] 2.2 Config completeness test
