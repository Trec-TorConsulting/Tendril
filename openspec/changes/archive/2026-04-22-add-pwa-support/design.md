## Context
The Grow Assistant frontend is a single `index.html` file served by FastAPI's `StaticFiles`. It currently has no PWA capabilities — no manifest, no service worker, no offline support. Users access it via browser on mobile while taking plant readings in the grow tent.

## Goals / Non-Goals
- **Goals**: Installable PWA, offline app shell, push notifications for alerts, background sync for sensor readings
- **Non-Goals**: Full offline-first app (API data is server-side, not synced to client), native app wrapper, app store distribution

## Decisions

### Service Worker Strategy
- **Decision**: Cache-first for static assets, network-first for API calls
- **Rationale**: The app shell (HTML/CSS/JS) changes infrequently and should load instantly. API data is always fresh from the server.
- **Alternative**: stale-while-revalidate — rejected because sensor data must be current

### Push Notification Provider
- **Decision**: Web Push (VAPID) via `pywebpush` — no third-party service required
- **Rationale**: Self-hosted, no cloud dependency, works on all modern browsers. Aligns with the privacy-first design.
- **Alternative**: Firebase Cloud Messaging — rejected (cloud dependency, requires Google account)

### Background Sync Storage
- **Decision**: IndexedDB for queuing failed sensor readings
- **Rationale**: Robust client-side storage, persists across restarts, natively supported by service worker API
- **Alternative**: localStorage — rejected (synchronous, size limits, not accessible from SW)

## Risks / Trade-offs
- **iOS Push Limitations**: iOS Safari supports web push as of iOS 16.4+ but requires the app to be added to home screen first. Users on older iOS won't get push notifications.
- **Service Worker Updates**: Users may run stale cached versions. Mitigated by versioned cache names and `skipWaiting()` + `clients.claim()`.
- **Background Sync Browser Support**: Not supported in all browsers (Safari lacks it). Fallback: retry on next app open.

## Open Questions
- Should push notification preferences be per-tent or global?
- Should we include a "What's New" banner when the SW updates the cached app?
