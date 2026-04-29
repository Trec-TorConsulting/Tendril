## Context
Tendril's web frontend needs an adaptive layout system that serves users from first-time hobby growers to commercial farm teams. The current UI is a fixed widget-based dashboard requiring too many navigation steps for the #1 daily action (logging pH/EC/feeding for DWC systems). The system must be PWA-first with mobile as the primary platform.

## Goals
- Users select their layout mode during onboarding (< 30 seconds)
- Each mode provides appropriate information density and navigation depth
- Quick-log is always ≤ 2 taps away regardless of mode
- Multi-camera support per grow space with grid/carousel viewing
- All modes share a common component library — modes are layout configurations, not separate apps
- Layout mode is changeable at any time from settings

## Non-Goals
- Complete frontend rewrite — we build on existing shadcn/ui components and patterns
- Custom CSS per mode — modes use the same design tokens, just different compositions
- Native mobile app — PWA is the target, not React Native
- Drag-and-drop layout customization (Pro/Commercial can reorder widgets, but not freeform grid)

## Decisions

### Decision: Layout modes are configurations, not separate codepaths
Each mode is a JSON configuration that controls: which components render, their order, information density props, and navigation structure. A single `LayoutEngine` component reads the config and renders accordingly.

**Alternatives considered:**
- Separate page trees per mode → Rejected: massive code duplication, drift between modes
- CSS-only density switching → Rejected: can't change which components appear or navigation structure
- User builds their own dashboard → Rejected: too complex for beginners, analysis paralysis

### Decision: Bottom tab bar for all mobile modes
All 5 modes use the same bottom tab bar on mobile, but with different tab configurations:

| Mode | Tabs |
|------|------|
| Beginner | Home, Log, Camera, Guide |
| Home | Home, Log, Camera, Alerts, More |
| Standard | Home, Grows, Log, AI, More |
| Pro | Home, Grows, Log, Cameras, More |
| Commercial | Home, Grows, Log, Team, More |

The "Log" tab is always present and in position 2 or 3 — quick-log is sacred.

### Decision: Grow-centric home screen
The home screen for all modes centers on the active grow(s):
- Beginner: Full-screen single-grow card with guided next-steps
- Home: Hero grow card + sensor summary + countdown
- Standard: Multi-grow grid + stats strip
- Pro: Multi-grow table + live sensor panels
- Commercial: Fleet overview + team activity + alerts

### Decision: Multi-camera as a first-class entity
Replace `tents.camera_url` (single string) with a `tent_cameras` table supporting:
- Multiple cameras per tent with labels ("Canopy", "Root Zone", "Wide Angle")
- Camera type (http_snapshot, rtsp, frigate)
- Sort order for display priority
- Thumbnail generation for grid views

### Decision: Quick-Log as a dedicated subsystem
Quick-log is not a page — it's a modal/sheet accessible from:
- Bottom tab "Log" tap
- FAB (if in Standard/Pro mode)
- Swipe-up gesture on home screen
- ⌘L keyboard shortcut on desktop

Quick-log supports:
- Single bucket feed logging (pH, EC, water temp, volume, nutrients)
- **Bulk bucket logging** — select multiple buckets for identical readings (DWC flush-and-fill)
- Auto-detection of active grow context
- Recent values as quick-fill suggestions
- Offline queueing (logs sync when connection returns)

### Decision: Onboarding wizard determines layout mode
3-screen wizard (< 30 seconds):
1. "What are you growing?" → Indoor / Outdoor / Both
2. "How many grows do you run?" → 1 / 2-5 / 6-20 / 20+
3. "Experience level?" → First grow / Hobbyist / Experienced / Professional / Commercial

Mapping:
- First grow → Beginner
- Hobbyist + 1-2 grows → Home
- Hobbyist + 3+ grows OR Experienced + 1-5 → Standard
- Experienced + 6+ OR Professional → Pro
- Commercial → Commercial

User can always override in settings.

## Data Model Changes

### New Table: `tent_cameras`
```sql
CREATE TABLE tent_cameras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tent_id UUID NOT NULL REFERENCES tents(id) ON DELETE CASCADE,
    label VARCHAR(100) NOT NULL DEFAULT 'Camera',
    camera_type VARCHAR(20) NOT NULL DEFAULT 'http_snapshot',
    url VARCHAR(1024) NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_camera_type CHECK (camera_type IN ('http_snapshot', 'rtsp', 'frigate'))
);
CREATE INDEX idx_tent_cameras_tent_id ON tent_cameras(tent_id);
```

### Migration: Move `tents.camera_url` → `tent_cameras`
- For each tent with a non-null `camera_url`, insert into `tent_cameras` with `is_primary=TRUE`
- Drop `tents.camera_url` column
- Update AI gather code to query from `tent_cameras` (primary camera)

### New Column: `users.layout_mode`
```sql
ALTER TABLE users ADD COLUMN layout_mode VARCHAR(20) NOT NULL DEFAULT 'standard';
```
Valid values: `beginner`, `home`, `standard`, `pro`, `commercial`

## Component Architecture

```
LayoutEngine (reads user.layout_mode)
├── LayoutShell
│   ├── MobileShell (bottom tab bar + content area)
│   └── DesktopShell (sidebar + content area)
├── HomeScreen (mode-specific composition)
│   ├── BeginnerHome (guided single-grow)
│   ├── HomeHome (hero card + summary)
│   ├── StandardHome (multi-grow grid)
│   ├── ProHome (dense panels)
│   └── CommercialHome (fleet + team)
├── QuickLog (universal sheet/modal)
│   ├── FeedingLog (pH, EC, temp, volume, nutrients)
│   ├── BulkBucketSelector (multi-select for DWC)
│   ├── QuickPhoto (camera → auto-tag)
│   ├── QuickNote (free text + tags)
│   └── ManualReading (temp, humidity, VPD)
├── CameraView
│   ├── CameraGrid (2x2, 3x3 layouts)
│   ├── CameraCarousel (swipe between cameras)
│   └── CameraFull (single camera full-screen + timeline)
└── Onboarding
    ├── WizardStep1 (what growing)
    ├── WizardStep2 (how many)
    ├── WizardStep3 (experience)
    └── WizardComplete (create first grow + set mode)
```

## Risks / Trade-offs
- **Risk**: 5 modes = 5x testing surface → **Mitigation**: Shared component library, modes only compose differently
- **Risk**: Beginners outgrow Beginner mode → **Mitigation**: Prompt to upgrade when they add 2nd grow or 5+ buckets
- **Risk**: Camera table migration breaks existing snapshots → **Mitigation**: Migration auto-migrates camera_url data; API falls back gracefully
- **Risk**: Quick-log offline queue causes data conflicts → **Mitigation**: Timestamps are client-generated; server merges by timestamp

## Open Questions
- Should timelapse generation happen server-side (scheduler) or client-side (browser)?
- Should Beginner mode hide "advanced" features entirely or show them as locked/teaser?
- Camera streaming (live RTSP in browser via HLS/WebRTC) — defer to `add-camera-rtsp-support` change?
