# Change: Add Offline PWA Support

## Why
Climate FieldView's FieldView Drive works offline and syncs when connected. Grow rooms are often in basements, warehouses, or rural areas with poor connectivity. Tendril's PWA currently requires connectivity for all operations. Offline support was identified as #4 gap in competitive analysis and is critical for real-world usage.

## What Changes

### New: Service Worker Caching Strategy
- Cache static assets (JS, CSS, images) for instant load
- Cache API responses for grow data, configs, and recent sensor readings
- Stale-while-revalidate for grow type configs (rarely change)
- Network-first for sensor data and live readings

### New: Offline Data Entry
- Queue sensor readings, expense entries, task completions, and notes while offline
- Background sync when connectivity returns (using Background Sync API)
- Visual indicator showing offline mode and pending sync count

### New: Offline Grow Type Configs
- Pre-cache all grow type configs on first visit
- Growers can browse stage guidance, troubleshooting, and quick reference without connectivity

## Impact
- Affected code: Frontend service worker, IndexedDB for offline queue, sync logic
- New spec: `offline-pwa`
