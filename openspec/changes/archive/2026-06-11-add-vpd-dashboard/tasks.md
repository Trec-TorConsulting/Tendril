## 1. VPD Calculation Engine
- [x] 1.1 Create `src/lib/vpd.ts` — VPD calculation from temp + humidity (leaf temp offset configurable)
- [x] 1.2 Define VPD zone ranges by stage (seedling: 0.4-0.8, veg: 0.8-1.2, flower: 1.0-1.5 kPa)
- [x] 1.3 Add VPD to tent readings processing (auto-calculate from ambient_temp + humidity)

## 2. VPD Dashboard Page
- [x] 2.1 Create `/dashboard/vpd` page with VPD chart (current + 24h trend)
- [x] 2.2 Add VPD zone visualization (color bands: too low, transpiration sweet spot, stress)
- [x] 2.3 Show current VPD with stage-aware target indicator
- [x] 2.4 Add leaf temperature offset control (input: 0-5°F below ambient)
- [x] 2.5 Add VPD recommendations based on current stage

## 3. Integration
- [x] 3.1 Add VPD card to main dashboard environment section
- [x] 3.2 Add VPD to grow detail environment metrics (API now returns vpd in response)
- [x] 3.3 Add VPD threshold to automation rules (already supported via sensor selector)
- [x] 3.4 Add VPD to AI health check context (already passed via tent sensor data)
