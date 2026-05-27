## 1. DWC Config Enhancement

### Reservoir & Root Zone (DWC's Core Differentiator)
- [x] 1.1 Add scale tier profiles (solo → warehouse) with reservoir management strategy per tier
- [x] 1.2 Add water source profiles (RO, tap/chlorine, tap/chloramine, well, softened) with CalMag adjustment tables
- [x] 1.3 Add monitoring thresholds (info/warning/alert/critical) for pH, EC, water temp, DO, water level
- [x] 1.4 Expand reservoir management: top-off decision tree (EC rising vs dropping), change schedule by stage, emergency drain protocol
- [x] 1.5 Add beneficial microbe program details: Hydroguard dosing schedule, alternatives (Great White, Mammoth P, Recharge), compatibility notes

### Stage Durations & Strain Types
- [ ] 1.6 Add `duration_days_auto` and `duration_days_photo` to each stage
- [ ] 1.7 Add autoflower-specific notes per stage (no light flip, limited training window, faster progression signals)
- [ ] 1.8 Add photoperiod-specific notes (veg length flexibility, light flip timing, re-veg recovery)

### Advanced Techniques
- [ ] 1.9 Add CO2 supplementation section: PPFD/CO2 correlation table, temp tolerance increases, VPD adjustments, seal requirements
- [ ] 1.10 Add foliar feeding schedule: what/when/dilution rates, stop in flower timing
- [ ] 1.11 Add silica supplementation: Armor Si timing (before nutrients, raises pH), stem strengthening benefits
- [ ] 1.12 Add crop steering concepts for DWC: light intensity manipulation, temperature differential (DIF), stress techniques

### Nutrient Alternatives
- [ ] 1.13 Create nutrient brand mapping table: GH Flora Trio → Jack's 321 stage-by-stage conversion
- [ ] 1.14 Create nutrient brand mapping: GH Flora Trio → Athena Pro stage-by-stage conversion
- [ ] 1.15 Create nutrient brand mapping: GH Flora Trio → Advanced Nutrients pH Perfect conversion
- [ ] 1.16 Create nutrient brand mapping: GH Flora Trio → FloraNova (simple 2-part) conversion
- [ ] 1.17 Create nutrient brand mapping: GH Flora Trio → MaxiGro/MaxiBloom (dry nutrient) conversion

### Harvest & Post-Harvest
- [ ] 1.18 Add harvest decision matrix: trichome ratios by desired effect, flush timing by nutrient line
- [ ] 1.19 Expand drying section: room specs (60°F/60%RH), whole-plant vs branch hang, stem snap test, duration tracking
- [ ] 1.20 Expand curing section: jar curing protocol, Boveda 62% vs Grove bags, burping schedule, long-term storage
- [ ] 1.21 Add environmental manipulation for final days: temperature drop, extended dark period, humidity reduction

### Photo Documentation
- [ ] 1.22 Add per-stage photo guidance: what to shoot, timing, angles, root zone documentation protocol

### Commercial & Compliance
- [ ] 1.23 Add batch tracking field hooks (lot number, mother plant ID, clone date, harvest batch)
- [ ] 1.24 Add seed-to-sale integration points (Metrc, BioTrack field mappings)
- [ ] 1.25 Add testing requirement fields (state-mandated testing stages, lab submission tracking)

## 2. API Enhancements
- [ ] 2.1 Add `?scale=` query parameter to `GET /v1/grow-types/{id}/config`
- [ ] 2.2 Add `?strain_type=` query parameter to `GET /v1/grow-types/{id}/config`
- [ ] 2.3 Add `GET /v1/grow-types/{id}/thresholds` endpoint for automation integration
- [ ] 2.4 Add `GET /v1/grow-types/{id}/equipment?scale=` endpoint with scale filtering
- [ ] 2.5 Update AI context builder to include scale and strain type when available

## 3. Profile Enhancement (grow_types.py)
- [x] 3.1 Add `scale_tiers` array to DWC profile in GROW_TYPE_PROFILES
- [x] 3.2 Add `strain_adjustments` (auto/photo differences) to DWC profile
- [x] 3.3 Add `water_source_profiles` to DWC profile

## 4. Testing
- [x] 4.1 Add config completeness test: all 12 stages present, all required fields populated
- [ ] 4.2 Add threshold validation test: info < warning < alert < critical for each sensor
- [ ] 4.3 Add API tests for `?scale=` and `?strain_type=` query params
- [ ] 4.4 Add API test for thresholds endpoint
- [ ] 4.5 Add nutrient conversion sanity tests (PPM ranges reasonable per stage)
