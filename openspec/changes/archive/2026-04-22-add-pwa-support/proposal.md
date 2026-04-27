# Change: Add Progressive Web App Support

## Why
The Grow Assistant is used in grow tents/rooms where users take manual pH/EC readings on their phones. A PWA enables Add-to-Home-Screen, offline caching, push notifications for alerts, and background sync for queuing sensor readings when connectivity is spotty — all critical for a mobile-first field tool.

## What Changes
- Add `manifest.json` with app metadata, icons, theme colors
- Add Service Worker for offline shell caching (HTML, CSS, JS assets)
- Add push notification support for environmental alerts and health check results
- Add background sync for queuing manual sensor readings when offline
- Add install prompt UX in the frontend
- Update `<head>` with PWA meta tags and manifest link

## Impact
- Affected specs: `grow-assistant-core` (frontend meta), `environment-monitoring` (push alerts), `bucket-monitoring` (background sync for sensor entry)
- Affected code: `app/static/index.html`, new `app/static/manifest.json`, new `app/static/sw.js`, `app/main.py` (push subscription endpoint)
- No breaking changes
