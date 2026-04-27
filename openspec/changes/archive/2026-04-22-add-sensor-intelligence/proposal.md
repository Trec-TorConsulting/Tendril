# Change: Add Sensor Intelligence (Tier 1 Features)

## Why
The app collects rich sensor data but doesn't do anything smart with it yet. Users must manually watch numbers and mentally track trends. Adding automated trend analysis, VPD calculations, nutrient recommendations, reservoir countdowns, and harvest yield tracking turns raw data into actionable intelligence — the core value proposition over a simple dashboard.

## What Changes
- Add sensor trend drift detection (pH/EC drift alerts over 24h windows)
- Add per-bucket VPD calculation from ambient temp/humidity + water temp
- Add nutrient calculator (target EC/PPM → how much to add per gallon)
- Add reservoir flush countdown with configurable reminders per growth stage
- Add harvest yield tracking (dry weight, grams-per-plant, grams-per-watt)

## Impact
- Affected specs: `environment-monitoring` (VPD, trend alerts), `bucket-monitoring` (nutrient calc, yield tracking, reservoir countdown)
- Affected code: `app/main.py` (new endpoints), `app/store.py` (yield table, alert logic), `app/static/index.html` (VPD gauge, nutrient calc UI, yield entry)
- No breaking changes
