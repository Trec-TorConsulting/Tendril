## Context
Tendril is a multi-tenant grow management SaaS with a Next.js 16 / React 19 / Tailwind v4 / shadcn-ui v4 PWA frontend. The UI overhaul (Phases 1-3) is complete. This change adds 11 high-impact UX features across 4 phases to elevate the experience.

### Constraints
- ARM64 only (K3S cluster on RPi5 + Jetson)
- All features client-side — no backend API changes
- Must work in PWA mode (standalone display)
- Bundle size matters — lazy-load heavy components

## Goals / Non-Goals
- **Goals**: Make the app feel alive, intelligent, and delightful. Leverage existing API endpoints. Ship incrementally (phase by phase).
- **Non-Goals**: No backend changes. No new API endpoints. No changes to auth or multi-tenancy. Not building native mobile apps.

## Decisions

### Command Palette
- **Use shadcn Command (cmdk)** — Already installed. No new dependency. Wire global ⌘K handler at layout level. Search sources load lazily (API calls on open, not on mount).
- **Alternatives**: kbar (heavier), custom (unnecessary)

### Celebration Animations
- **canvas-confetti** (~6KB gzipped) — Lightweight, canvas-based, no React dependency. Import dynamically only when triggered.
- **Alternatives**: react-confetti (heavier, React-specific), Lottie (overkill)

### Sensor Gauges
- **Custom SVG arcs + framer-motion** — Lightweight, matches existing animation stack. No new chart library needed.
- **Alternatives**: D3 gauges (too heavy for this), recharts radial (limited customization)

### AI Chat Panel
- **Native WebSocket + streaming** — Use browser WebSocket API directly with the existing `getAiChatWsUrl()` endpoint. Stream tokens and render progressively.
- **Alternatives**: Socket.IO (server doesn't use it), SSE (endpoint is WebSocket)

### Camera Feeds
- **go2rtc WebRTC** — Direct browser WebRTC connection to go2rtc. Falls back to MSE (MediaSource Extensions) if WebRTC fails, then snapshot JPEG.
- **Alternatives**: HLS (higher latency), direct RTSP (no browser support)

### Push Notifications
- **Web Push API + Service Worker** — Standard PWA approach. next-pwa already generates a Service Worker. Extend it with push event handler.
- **Alternatives**: Firebase Cloud Messaging (cloud dependency, against project philosophy)

### Grow Stage Indicator
- **Inline SVG with CSS transitions** — Hand-crafted 5-stage plant SVG. CSS clip-path and transform transitions between stages. No animation library needed beyond what exists.
- **Alternatives**: Lottie (requires After Effects export), Rive (new dependency)

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Bundle size growth | Slower initial load | Dynamic imports for confetti, chat panel, timelapse, camera feed |
| WebRTC camera compatibility | May not work on all browsers | MSE fallback → JPEG snapshot fallback chain |
| Push notification permission fatigue | Users decline, never asked again | Only prompt after meaningful user action (e.g., creating first automation rule) |
| Timelapse performance with many photos | Memory pressure on mobile | Virtualize frames, preload only ±5 frames from current position |
| AI chat WebSocket reliability | Connection drops | Auto-reconnect with exponential backoff, offline indicator |

## Open Questions
- Camera-to-tent mapping: How are cameras associated with tents? (May need a config or API field)
- Push notification backend: Does the Tendril API support push subscription registration, or does that need to be added? (Marked as no backend changes needed — may need to defer 4.9 if not)
