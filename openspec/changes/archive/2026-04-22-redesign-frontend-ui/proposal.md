# Change: Redesign Frontend UI

## Why
The grow-assistant frontend has grown from a simple camera+chat SPA into a feature-rich cultivation platform (strain library, feeding schedules, grow diary, analytics, crop steering, PWA, pump controls, yield tracking, photo comparison, grow scoring) — but the UI was never restructured to accommodate this growth. Key features are buried 3+ clicks deep, the bucket detail overlay is an overloaded "everything drawer," active grows show empty data, and the entire frontend is a single 4,800-line HTML file. The app needs a proper information architecture to match its capabilities.

## What Changes
- **BREAKING**: Complete frontend restructure — all views rebuilt with new navigation and layout
- Replace tent-tabs + 7-sub-tabs pattern with a routed multi-view SPA (hash-based routing)
- New global navigation: Dashboard, Grows, Buckets, Strains, Analytics, Settings
- Dedicated Dashboard with grow score card, active alerts, environment snapshot, recent activity
- Dedicated Grow Manager view — active grows show live bucket data (not just archive snapshots)
- Strain Library promoted to top-level view
- Feeding Schedule Planner as top-level view
- Analytics view with crop steering, sensor trends, score history, CSV export
- Bucket detail split into tabbed sections (Overview, Sensors, Diary, Photos, Feeding, Pump)
- Modular JS file structure (separate files per view, shared utilities)
- Responsive mobile-first layout optimized for PWA standalone mode
- No framework dependencies — stays vanilla JS/CSS (keeps Docker image small, no build step)

## Impact
- Affected specs: grow-assistant-core, bucket-monitoring, environment-monitoring, camera-health-checks
- Affected code: `app/static/index.html` (full rewrite), `app/main.py` (active grow data endpoint), `app/store.py` (active grow query)
- No backend API breaking changes — all existing endpoints remain, minor additions only
- All existing tests continue to pass — backend unchanged except grow data enrichment
