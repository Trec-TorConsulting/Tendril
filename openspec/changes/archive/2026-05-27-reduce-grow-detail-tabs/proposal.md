# Change: Reduce Grow Detail Tab Count

## Why
The grow detail page has up to 19 tabs in a horizontal scrollbar. Users must scroll horizontally to find the tab they need. Related concerns are split into separate tabs (Sensors and Journal both show time-series data; Feeding and Harvest are both about nutrition/output). The cognitive load is too high for what should be a focused workspace.

## What Changes
- Consolidate related tabs into grouped views (reduce from 19 to ~8-9 max)
- Group: Sensors + Journal → "Activity" (unified timeline of readings and events)
- Group: Feeding + Harvest/Yields → "Nutrition & Yield"
- Group: Photos + Health → "Health & Photos"
- Keep: Overview, Buckets, Tasks, Settings as standalone
- Outdoor-only tabs grouped into a single "Field" tab with sub-sections
- Add tab badges showing counts/alerts (e.g., "Tasks (3)" or a dot for new health issues)

## Impact
- Affected specs: None existing (UX-only change)
- Affected code: `web/src/app/dashboard/grows/[id]/page.tsx` (tab definitions), individual tab components
- No API changes — only frontend tab organization
