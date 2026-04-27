# Change: Add Advanced Analytics (Tier 3 Features)

## Why
Advanced features that differentiate the Grow Assistant from basic monitoring dashboards. Crop steering, multi-grow history, data export, pump automation, light/DLI tracking, and environmental scoring provide the kind of insights that commercial platforms like Trym and LUNA charge hundreds per month for — delivered as a free, self-hosted solution.

## What Changes
- Add crop steering dashboard — track generative vs vegetative signals (dry-backs, EC ramp) with recommended actions
- Add multi-grow history — archive completed grows, compare strain performance across cycles
- Add export/reports — PDF or CSV export of a full grow cycle (journal + sensors + photos)
- Add pump automation dashboard — UI for ESP32 dose commands (pH up/down, nutrient via MQTT)
- Add light schedule tracking — DLI calculator based on tent config light hours + wattage
- Add environmental scoring — daily "grow score" combining VPD, pH/EC stability, water temp consistency

## Impact
- Affected specs: `bucket-monitoring` (crop steering, multi-grow, export, pump UI), `environment-monitoring` (DLI, scoring), `camera-health-checks` (export includes photos)
- Affected code: `app/main.py` (new endpoints), `app/store.py` (grow archives, scores), `app/static/index.html` (crop steering view, export UI, pump controls, score widget)
- No breaking changes
