## 1. Coco Config Build (api/app/grows/grow_type_configs/coco.py)

### CalMag & Fertigation (Coco's Core Differentiators)
- [x] 1.1 Define CalMag science section: cation exchange chemistry, buffering protocol, ongoing dosing, LED/RO adjustments
- [x] 1.2 Define coco preparation: rinsing, buffering soak, brick rehydration, perlite mixing ratios, pre-buffered brands
- [x] 1.3 Define fertigation frequency schedule: stage-specific targets, never-plain-water rule, frequency ramping
- [x] 1.4 Define dryback monitoring: pot weight methods, target % by stage, never-dry-completely warnings, recovery protocol
- [x] 1.5 Define runoff management: input vs runoff EC interpretation, target runoff %, flush triggers
- [x] 1.6 Define pot sizing and transplant schedule: solo cup → 1gal → final pot, fabric pot recommendation, timing
- [x] 1.7 Define reuse/recycling: cleaning protocol, enzyme treatment, re-buffering, composting

### Stages (12 stages — fertigation frequency + CalMag dosing per stage)
- [x] 1.8 Build germination + seedling (start in small pots, low frequency, gentle nutrients + CalMag)
- [x] 1.9 Build veg stages (transplant schedule, increasing frequency, dryback vegetative targets)
- [x] 1.10 Build flower stages (peak frequency 3-6x/day, generative dryback steering, runoff monitoring)
- [x] 1.11 Build flush, harvest, drying, curing stages (coco flush is the ONE time you use plain water)
- [x] 1.12 Add environment variants per stage

### Equipment, Troubleshooting, Quick Reference
- [x] 1.13 Build equipment: pots (fabric preferred), saucers/trays, watering can or pump, pH/EC meters, CalMag, coco/perlite
- [x] 1.14 Build troubleshooting: CalMag Deficiency, Salt Buildup, Overwatering Seedlings, Drying Out, pH Issues
- [x] 1.15 Build quick reference: fertigation frequency by stage, CalMag dosing chart, dryback targets, runoff interpretation

### Scale, Strain, Water Source
- [x] 1.16 Add scale tiers (hand watering → automated drip in coco)
- [x] 1.17 Add auto/photo variants (autos in smaller final pots)
- [x] 1.18 Add water source profiles (RO needs extra CalMag)

## 2. Registration & Testing
- [x] 2.1 Register COCO_CONFIG in __init__.py
- [x] 2.2 Config completeness test
