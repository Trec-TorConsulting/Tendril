## 1. Service Worker
- [ ] 1.1 Configure Next.js service worker with Workbox
- [ ] 1.2 Cache static assets (JS, CSS, images, fonts)
- [ ] 1.3 Implement stale-while-revalidate for grow type configs
- [ ] 1.4 Implement network-first for dynamic data (grows, sensor readings)
- [ ] 1.5 Pre-cache all grow type configs on first visit

## 2. Offline Data Queue
- [ ] 2.1 Set up IndexedDB store for offline queue (Dexie.js or idb)
- [ ] 2.2 Queue POST/PATCH requests when offline
- [ ] 2.3 Background Sync API registration for automatic sync
- [ ] 2.4 Manual sync trigger button as fallback
- [ ] 2.5 Conflict resolution strategy (server wins for sensor data, client wins for notes)

## 3. UI Indicators
- [ ] 3.1 Offline mode banner/indicator
- [ ] 3.2 Pending sync count badge
- [ ] 3.3 Sync progress feedback
- [ ] 3.4 Stale data warning on cached views

## 4. Testing
- [ ] 4.1 Service worker caching tests
- [ ] 4.2 Offline queue and sync tests
- [ ] 4.3 Conflict resolution tests
