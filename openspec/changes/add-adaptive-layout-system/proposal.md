# Change: Add Adaptive Layout System

## Why
The current Tendril UI is one-size-fits-all. A home grower with 1 tent and 3 DWC buckets has identical UI to a commercial operation with 20 grows. The result: too many screens to navigate for simple logging (the #1 daily action), an interface that feels "hard to use" for manual loggers, and no path to grow with the user. Users need a UI that matches their scale, experience, and workflow — not a fixed dashboard they must learn to navigate.

## What Changes
- **Adaptive Layout Engine** with 5 selectable modes: Beginner, Home, Standard, Pro, Commercial
- **Grow-centric navigation** — the Grow is the primary object, everything radiates from it
- **Bottom tab bar** (Instagram-style) replaces sidebar on mobile PWA
- **Quick-Log system** — pH/EC/feeding logging in 2-3 taps with DWC bulk bucket support
- **Multi-camera per grow space** — new `tent_cameras` table replacing single `camera_url` column
- **Onboarding wizard** — 30-second flow that determines layout mode and creates first grow
- Each layout mode has its own **information density**, **navigation depth**, and **visual style**

## Impact
- Affected specs: `adaptive-layouts` (NEW), `multi-camera` (NEW), `quick-log` (NEW)
- Affected code: `web/src/` (major frontend rewrite), `api/app/grows/` (camera model), new migration
- **BREAKING**: `tents.camera_url` column replaced by `tent_cameras` table (migration handles data)
- Builds on top of `redesign-tendril-ui` (shell/nav already implemented)

## Design Philosophy

### Core Principle: The Grow IS the App
- Opening the app = seeing your grow(s)
- Every action (log, photo, check, note) is contextual to the active grow
- Navigation depth scales with layout mode (Beginner: 1 level, Commercial: 4 levels)

### Layout Mode Vibes

| Mode | Target | Vibe | Density | Nav Depth |
|------|--------|------|---------|-----------|
| Beginner | First grow ever | Duolingo — guided, gamified, tutorials | Minimal | 1 level |
| Home | 1-2 tents, hobbyist | Apple Health — calm, beautiful cards | Low | 2 levels |
| Standard | Multi-tent, intermediate | Notion + Linear — functional, data-forward | Medium | 3 levels |
| Pro | Serious grower, many grows | Grafana lite — dense, real-time, panels | High | 3 levels |
| Commercial | Enterprise/farm teams | Stripe Dashboard — teams, audit, fleet | Very High | 4 levels |

### PWA-First, Web Near Parity
- Mobile PWA is the PRIMARY experience (bottom tab nav, touch gestures, quick-log)
- Desktop web gets the same features with sidebar nav restored and wider layouts
- Both share identical components, just different layout shells

## Status
- [ ] Pending approval
