## 1. PWA Manifest & Icons
- [x] 1.1 Create `app/static/manifest.json` with name, short_name, icons, start_url, display: standalone, theme_color, background_color
- [x] 1.2 Generate PWA icon set (192x192, 512x512 PNG) with grow-assistant branding
- [x] 1.3 Add `<link rel="manifest">`, `<meta name="theme-color">`, `<meta name="apple-mobile-web-app-capable">` to index.html `<head>`
- [x] 1.4 Add apple-touch-icon link for iOS support

## 2. Service Worker — Offline Shell
- [x] 2.1 Create `app/static/sw.js` with cache-first strategy for static assets (index.html, manifest, icons)
- [x] 2.2 Register service worker in index.html with scope `/`
- [x] 2.3 Implement versioned cache (cache name includes version hash) with old cache cleanup on activate
- [x] 2.4 Network-first strategy for API calls (don't cache API responses in SW)
- [x] 2.5 Add offline fallback page/state when network and cache both miss

## 3. Install Prompt
- [x] 3.1 Listen for `beforeinstallprompt` event and show custom install banner
- [x] 3.2 Add "Install App" button in settings modal
- [x] 3.3 Track installation state and hide prompt once installed

## 4. Push Notifications
- [x] 4.1 Add `POST /api/push/subscribe` endpoint to store push subscription (endpoint, keys)
- [x] 4.2 Add `DELETE /api/push/subscribe` endpoint to unsubscribe
- [x] 4.3 Create `push_subscriptions` table in database
- [x] 4.4 Integrate `pywebpush` library for sending notifications from backend
- [x] 4.5 Generate VAPID keys and store in environment config
- [x] 4.6 Send push notification on new environmental alerts (pH/EC out of range, water level low)
- [x] 4.7 Send push notification on daily health check completion
- [x] 4.8 Add notification permission request flow in frontend UI
- [x] 4.9 Handle notification click to open relevant tent/bucket view

## 5. Background Sync
- [x] 5.1 Register `sync` event in service worker for `sensor-reading-sync` tag
- [x] 5.2 Queue failed `POST /api/buckets/{id}/sensors` requests in IndexedDB when offline
- [x] 5.3 Replay queued readings when connectivity resumes (via sync event)
- [x] 5.4 Show pending sync count badge in UI

## 6. Testing & Validation
- [ ] 6.1 Test PWA install flow on iOS Safari and Android Chrome
- [ ] 6.2 Test offline mode — app shell loads, API calls show graceful error
- [ ] 6.3 Test push notifications on mobile and desktop
- [ ] 6.4 Test background sync — queue reading offline, verify it posts when online
- [ ] 6.5 Validate with Lighthouse PWA audit (target 100 score)
