# Change: Competitive Analysis 2026 — Feature Gap Identification

## Why
Evaluated 12 ag-tech platforms (GrowLink, GrowDirector, Cropin, Plantix, AGRIVI, FarmKeep, farmOS, LandPKS, AGMRI, Climate FieldView, John Deere Operations Center, WiseYield) to identify features Tendril is missing. This is a meta-change that documents the analysis and spawns individual change proposals for each gap.

## What Changes
This change itself is documentation-only. It produces:
1. `competitive-analysis.md` — Full spreadsheet-style comparison matrix
2. Individual OpenSpec change proposals for each P0/P1 feature gap identified

### P0 Feature Gaps (spawned as separate changes)
- `add-photo-plant-health-ai` — Camera-based plant deficiency/pest/disease detection (inspired by Plantix)
- `add-cost-roi-tracking` — Per-grow cost tracking and ROI calculation (inspired by AGRIVI, FarmKeep)
- `add-data-export` — CSV/PDF report export for all data (inspired by all competitors — table stakes)
- `add-offline-pwa-support` — Service worker caching for offline grow room usage (inspired by Climate FieldView)

### P1 Feature Gaps (future proposals)
- Equipment control via ESP32 relay (inspired by GrowLink, GrowDirector)
- VPD real-time dashboard (GrowLink, GrowDirector)
- Season-over-season comparison (AGRIVI, Climate FV)
- Treatment/spray log (Plantix, AGRIVI)
- Pest/disease visual library (Plantix, AGRIVI)
- Notification channels — SMS, push, email (GrowLink, AGRIVI)

## Impact
- Affected specs: Multiple new capabilities
- Affected code: API, frontend, ESP32, AI modules
