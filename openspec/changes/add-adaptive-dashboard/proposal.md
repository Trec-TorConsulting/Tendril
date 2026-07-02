# Change: Add Adaptive Dashboard Surfacing

## Why
The dashboard home ([web/src/app/dashboard/page.tsx](web/src/app/dashboard/page.tsx)) shows dynamic data but a **static layout** — the same cards in the same order regardless of the grow's stage, urgency, or what the user just did. The `useLayoutMode` hook ([web/src/lib/layout-config.ts](web/src/lib/layout-config.ts)) only encodes a persona (beginner/home/standard/pro/commercial); it is not situational. Users must hunt for what matters right now. We will add a situational layer that reorders and shows/hides cards by stage + urgency, and a single "Next Best Action" block that consolidates the most important thing to do.

## What Changes
- Add a **situational surfacing layer** on top of the existing persona layout: compute a priority-ordered set of dashboard sections from the grow's current stage, active alerts, unacknowledged coaching, pending high-priority tasks, and sensor state.
- Add a **"Next Best Action"** block that deterministically selects the single most important item (critical alert > urgent task > important coaching > stage-relevant tip) and renders it at the top with a one-tap action.
- **Stage-relevant surfacing**: e.g., ripening floats trichome/harvest guidance up; a live critical alert pins to the top; veg de-prioritizes harvest countdown.
- Keep persona layout intact — situational ordering operates within the persona's density/tabs; it does not replace the user's chosen mode.
- Persist nothing new server-side by default (compute client-side from existing endpoints), unless a small ranking config is useful.

## Impact
- Affected specs:
  - adaptive-dashboard (NEW capability)
- Affected code (expected):
  - web/src/app/dashboard/page.tsx (situational ordering)
  - web/src/hooks/ (new `use-dashboard-priority.ts`)
  - web/src/components/ (new `next-best-action.tsx`)
  - web/src/lib/layout-config.ts (unchanged persona; consumed alongside)
- Data model impact:
  - none required (client-side computation from existing data)
- Security impact:
  - none new; uses existing authenticated data
- Breaking changes:
  - none; additive and reversible (falls back to current fixed order if priority is empty)
