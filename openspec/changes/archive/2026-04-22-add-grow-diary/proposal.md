# Change: Add Grow Diary Features (Tier 2)

## Why
Community grow platforms (GrowDiaries, Grow with Jane) are wildly popular because growers love documenting and sharing their grows. Adding a structured grow diary with week-by-week timeline, strain library, photo integration, feeding schedule templates, and AI-assisted growth stage transitions transforms the app from a monitoring tool into a comprehensive grow companion.

## What Changes
- Add grow diary timline — week-by-week view combining photos, journal entries, and sensor snapshots
- Add strain library — store strain metadata (breeder, genetics, flowering time, expected yield) and auto-populate
- Add growth stage auto-advance — AI suggests stage transitions based on sensor patterns + days elapsed
- Add feeding schedule templates — pre-built nutrient schedules per growth stage for common nutrient lines
- Add photo comparison — side-by-side snapshots from different dates for same tent/bucket

## Impact
- Affected specs: `bucket-monitoring` (diary, strain library, stage advance, feeding schedules), `camera-health-checks` (photo comparison)
- Affected code: `app/main.py` (new endpoints), `app/store.py` (strains, feeding schedules tables), `app/static/index.html` (diary view, strain picker, photo compare)
- No breaking changes
