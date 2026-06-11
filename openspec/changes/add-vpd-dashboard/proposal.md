# Change: Add VPD Dashboard

## Why
VPD (Vapor Pressure Deficit) is the single most important environmental metric for cannabis cultivation — it determines transpiration rate, nutrient uptake efficiency, and directly impacts terpene production. While Tendril stores VPD readings and has per-stage target ranges in grow configs, there's no dedicated VPD dashboard showing real-time readings, historical trends, or stage-aware zone visualization. Growers need at-a-glance VPD status with actionable guidance.

## What Changes
- New frontend VPD calculation utility (`src/lib/vpd.ts`) with configurable leaf temperature offset
- New dedicated `/dashboard/vpd` page with real-time VPD, 24h trend chart, stage-aware zone visualization
- Expose VPD (and missing columns: co2, lux, dew_point_f, par_ppfd, voc, air_pressure) in tent sensor API response schema
- Add VPD endpoint for historical data with zone annotations
- Add VPD gauge preset to the sensor-gauge component
- Add VPD summary card to main dashboard
- Add VPD to AI health check context

## Impact
- Affected specs: `environment-monitoring`
- Affected code:
  - `api/app/sensors/tent_routes.py` — expand response schema
  - `api/app/sensors/schemas.py` — add VPD and extended fields
  - `web/src/lib/vpd.ts` — new utility
  - `web/src/app/dashboard/vpd/page.tsx` — new page
  - `web/src/components/sensor-gauge.tsx` — add VPD preset
  - `web/src/components/app-sidebar.tsx` — add nav entry
- **NOT BREAKING**: Existing API response gains additional fields (additive)
- No schema/migration changes — VPD column already exists in tent_sensor_readings
