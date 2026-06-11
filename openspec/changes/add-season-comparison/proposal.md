# Change: Add Season-over-Season Comparison

## Why
Growers need to compare multiple grows side-by-side to identify what worked, what didn't, and track improvement over time. Normalized time-series (day-in-grow as X axis) enables fair comparison between grows of different durations and calendar dates. This is especially valuable when experimenting with different nutrients, environmental controls, or strain variations.

## What Changes
- New `GET /v1/analytics/compare` endpoint returning normalized time-series for 2-4 selected grows
- Comparison data: per-metric daily averages aligned by day-in-grow (not calendar date)
- Summary statistics: avg pH, avg EC, avg VPD, total yield, grow duration, quality rating
- New `/dashboard/analytics/compare` page with grow multi-select, overlay charts, and stats table
- Auto-detection of comparable grows (same strain + grow type)
- "Compare with previous" shortcut from grow detail

## Impact
- Affected specs: `environment-monitoring`
- Affected code: new routes file, new frontend page, analytics page tab addition
- **NOT BREAKING**: All new endpoints, no existing changes
- No migration needed — reads from existing sensor reading + yield tables
