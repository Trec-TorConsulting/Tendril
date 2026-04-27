# Change: Add Tendril Cool Features — Elevate the UX

## Why
The Tendril web UI overhaul (Phases 1-3) established a polished, mobile-first foundation. The next step is to layer on high-impact features that make the app feel alive, intelligent, and delightful — transforming it from a capable dashboard into a best-in-class grow management experience.

## What Changes

### Phase 1: Power User UX
- **Command Palette (⌘K)** — Global search and quick-action launcher using shadcn Command component. Search grows, tents, strains, devices; jump to any page; trigger actions (create grow, start health check).
- **Celebration Animations** — Canvas-confetti bursts on grow completion, harvest milestones, task completion streaks, and onboarding checklist completion.
- **Sparkline Mini-Charts** — Inline recharts sparklines on dashboard stat cards showing 7-day pH, EC, temperature, and humidity micro-trends.

### Phase 2: Data Visualization
- **Heat Map Calendar** — GitHub-style contribution grid on the analytics page showing daily grow activity (journal entries, photos, sensor readings, tasks completed).
- **Real-time Sensor Gauges** — Animated radial gauge/dial components for pH, EC, temperature, and humidity with color-coded zones (danger / warning / optimal). Used on grow detail and tent detail pages.
- **Grow Timeline** — Vertical visual timeline on grow detail page showing lifecycle milestones (planted → transplant → veg → flower → harvest) with linked journal entries, photos, and feeding events at each point.

### Phase 3: AI & Media
- **AI Chat Panel** — Sliding drawer with streaming WebSocket chat to the Tendril AI assistant. Markdown rendering, typing indicator, message history, context-aware (knows current grow/tent). Uses existing `getAiChatWsUrl()` endpoint.
- **Photo Timelapse Player** — Smooth scrubber/player UI on grow detail photos tab. Drag through grow photos chronologically like a video. Play/pause, speed control, fullscreen. Uses existing `timelapseUrl()` endpoint.
- **Animated Grow Stage Indicator** — SVG/CSS plant illustration that visually evolves based on grow stage (seed → seedling → vegetative → flowering → harvest). Displayed on grow detail hero and dashboard active-grows widget.

### Phase 4: Platform Integration
- **Live Camera Feeds** — Embed Frigate camera streams (via go2rtc WebRTC/MSE) directly into tent detail pages. Live view of grow spaces with snapshot fallback.
- **Push Notifications** — Real PWA push notifications via Service Worker + Web Push API. Sensor threshold alerts, task reminders, harvest countdowns, AI health check results. Requires notification permission flow.

## Impact
- Affected specs: tendril-web-experience (new capability spec)
- Affected code: `tendril/web/` — new components, hooks, dashboard widgets, grow detail tabs
- New dependencies: `canvas-confetti`, `@nicepkg/gpt-runner` or similar for chat streaming (evaluate), web-push utilities
- No backend changes required — all features use existing API endpoints
- No breaking changes
