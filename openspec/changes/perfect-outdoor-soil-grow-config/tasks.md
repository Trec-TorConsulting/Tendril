## 1. Outdoor Soil Config Build (api/app/grows/grow_type_configs/outdoor_soil.py)

### Weather, Photoperiod & GDD (Outdoor Soil's Core Differentiators)
- [ ] 1.1 Define weather integration: frost protection protocols, heat stress management, rain management, wind protection, storm preparation
- [ ] 1.2 Define natural photoperiod management: flower trigger by latitude, light dep technique, autoflower outdoor advantages, supplemental lighting
- [ ] 1.3 Define GDD tracking: formula, base temperature, stage transition thresholds, maturity prediction, daily accumulation
- [ ] 1.4 Define hardiness zone integration: auto-detect from lat/lng, frost dates, season length, zone-adjusted timelines
- [ ] 1.5 Define companion planting guide: beneficial/harmful pairings, spacing, trap cropping, per-stage planting schedule
- [ ] 1.6 Define in-ground soil building: soil testing protocol, amendment recommendations, cover crop rotations, compost, mulch, no-till, biochar
- [ ] 1.7 Define pest & wildlife management: deer, rabbits, caterpillars, spider mites, powdery mildew, budrot, full IPM protocol
- [ ] 1.8 Define seasonal planning: indoor start → hardening off → transplant → veg → flower → harvest, calendar by zone
- [ ] 1.9 Define moon phase / biodynamic planting (optional): lunar calendar, waxing/waning guidance
- [ ] 1.10 Define irrigation planning: drip vs soaker vs hand, rain-skip, mulch, morning watering, water source profiles

### Stages (12 stages — GDD-based transitions, weather-integrated)
- [ ] 1.11 Build germination + seedling (indoor start, under lights, before last frost)
- [ ] 1.12 Build hardening off stage (unique to outdoor: 7-10 day gradual exposure transition)
- [ ] 1.13 Build transplant + early veg (after last frost, in-ground or raised bed placement)
- [ ] 1.14 Build mid/late veg (peak growth, companion planting active, pest scouting begins)
- [ ] 1.15 Build pre-flower + flower stages (natural photoperiod trigger, generative nutrition, pest vigilance, weather monitoring)
- [ ] 1.16 Build late flower (harvest window calculator: trichome stage × weather forecast × first frost date)
- [ ] 1.17 Build harvest, drying, curing stages (outdoor harvest logistics, field drying considerations)
- [ ] 1.18 Build post-harvest / off-season (cover crop planting, soil testing, composting, bed preparation)
- [ ] 1.19 Add in-ground vs raised bed variants per stage
- [ ] 1.20 Add zone-adjusted timeline variants

### Equipment, Troubleshooting, Quick Reference
- [ ] 1.21 Build equipment: row covers, shade cloth, trellis, fencing, drip irrigation, soil test kit, compost bins, rain gauge
- [ ] 1.22 Build troubleshooting: Frost Damage, Heat Stress, Pest Invasion, PM/Budrot, Overwatering from Rain, Nutrient Deficiency in Ground Soil
- [ ] 1.23 Build quick reference: planting calendar by zone, companion plant chart, GDD targets, pest ID quick guide, frost protection checklist

### Scale, Strain, Water Source
- [ ] 1.24 Add scale tiers (backyard 1-4 plants → market garden → small farm)
- [ ] 1.25 Add autoflower vs photoperiod outdoor variants
- [ ] 1.26 Add water source profiles (well, municipal, rainwater collection)

## 2. Registration & Testing
- [ ] 2.1 Register OUTDOOR_SOIL_CONFIG in __init__.py
- [ ] 2.2 Config completeness test

## Note
This config integrates with the outdoor modules defined in `add-outdoor-soil-experience` (plot grid, soil tests, pest scouting, weather, yields, companion plants — 129 tasks). This config provides the grow type configuration; that change provides the API/frontend infrastructure.
