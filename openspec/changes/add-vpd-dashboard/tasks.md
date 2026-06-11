## 1. VPD Calculation Engine
- [ ] 1.1 Create `src/lib/vpd.ts` — VPD calculation from temp + humidity (leaf temp offset configurable)
- [ ] 1.2 Define VPD zone ranges by stage (seedling: 0.4-0.8, veg: 0.8-1.2, flower: 1.0-1.5 kPa)
- [ ] 1.3 Add VPD to tent readings processing (auto-calculate from ambient_temp + humidity)

## 2. VPD Dashboard Page
- [ ] 2.1 Create `/dashboard/vpd` page with VPD chart (current + 24h trend)
- [ ] 2.2 Add VPD zone visualization (color bands: too low, transpiration sweet spot, stress)
- [ ] 2.3 Show current VPD with stage-aware target indicator
- [ ] 2.4 Add leaf temperature offset control (slider: 0-5°F below ambient)
- [ ] 2.5 Add VPD recommendations based on current stage

## 3. Integration
- [ ] 3.1 Add VPD card to main dashboard environment section
- [ ] 3.2 Add VPD to grow detail environment metrics
- [ ] 3.3 Add VPD threshold to automation rules (alert when outside zone)
- [ ] 3.4 Add VPD to AI health check context for recommendations
