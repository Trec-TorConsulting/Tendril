## 1. Foundation — Shell, Router, State
- [ ] 1.1 Create `app/static/css/app.css` — extract all styles from index.html, organize by component, implement CSS custom properties for light/dark mode
- [ ] 1.2 Create `app/static/js/state.js` — global App namespace, state object, api() helper, toast(), router, theme toggle (prefers-color-scheme + localStorage)
- [ ] 1.3 Implement hash-based router in state.js — maps `#view` to render functions, handles `#view/param` patterns
- [ ] 1.4 Create new `app/static/index.html` shell — minimal HTML with nav structure, view containers, script tags
- [ ] 1.5 Add bottom nav bar (mobile) with 5 items: Dashboard, Grows, Buckets, Analytics, Chat
- [ ] 1.6 Add responsive sidebar nav for wider screens (>768px) with same 5 items
- [ ] 1.7 Add header bar with tent selector dropdown, settings icon, and active tent label
- [ ] 1.8 Add view container `<div id="viewRoot">` for router-rendered content
- [ ] 1.9 Update `sw.js` APP_SHELL to include new JS/CSS files, bump CACHE_VERSION

## 2. Dashboard View
- [ ] 2.1 Create `app/static/js/dashboard.js` — render function for `#dashboard` route
- [ ] 2.2 Camera snapshot hero — full-width camera image at top of dashboard with refresh button and tent label
- [ ] 2.3 Grow Score card — large score display with colored ring (green/yellow/red), factor breakdown on tap
- [ ] 2.4 Environment snapshot card — current temp, humidity, VPD from Vivosun with last-updated time
- [ ] 2.5 Active alerts card — list of current unacked alerts with severity badges
- [ ] 2.6 Recent activity feed — last 10 events (journal entries, sensor alerts, health checks, doses)
- [ ] 2.7 Quick actions row — buttons for Health Check, New Grow, Export CSV
- [ ] 2.8 Active grow summary card — current grow name, duration, stage, bucket count

## 3. Grow Manager View
- [ ] 3.1 Create `app/static/js/grows.js` — render function for `#grows` route
- [ ] 3.2 Active grows section — cards showing name, tent, start date, duration, bucket count, score
- [ ] 3.3 New grow form — inline name input + start button (replaces prompt dialog)
- [ ] 3.4 Active grow detail view (`#grows/:id`) — shows live bucket data, environment timeline, journal
- [ ] 3.5 Modify `GET /api/grows/{id}` in main.py — return live bucket data for active grows
- [ ] 3.6 Modify `store.get_grow_cycle_data()` — query live sensors, journal, photos for active grows using start_date + tent_id
- [ ] 3.7 Archive button on grow detail — confirms, archives, redirects to grow list
- [ ] 3.8 Archived grows section — collapsed list with name, dates, final score, bucket count
- [ ] 3.9 Archived grow detail view — displays snapshot data (existing behavior)
- [ ] 3.10 Grow compare — select 2-3 grows, side-by-side metric comparison cards
- [ ] 3.11 Grow notes editing — inline textarea for adding/editing grow notes

## 4. Bucket Views
- [ ] 4.1 Create `app/static/js/buckets.js` — render function for `#buckets` route
- [ ] 4.2 Bucket grid — responsive card grid showing all buckets for active tent
- [ ] 4.3 Bucket card — shows label, position, strain, stage, last pH/EC, status indicator (green/yellow/red)
- [ ] 4.4 Add bucket form — slide-up form (replaces modal) with all fields
- [ ] 4.5 Bucket detail route (`#buckets/:id`) with tabbed layout:
- [ ] 4.6 — Overview tab: strain, stage, plant date, status, stage suggestion, milestone timeline
- [ ] 4.7 — Sensors tab: pH/EC/temp Chart.js charts (24h/7d/30d toggle), latest readings, drift analysis
- [ ] 4.8 — Diary tab: journal timeline, add entry form, auto-entries highlighted differently
- [ ] 4.9 — Photos tab: photo gallery grid, upload button, photo compare side-by-side
- [ ] 4.10 — Feeding tab: current week's feeding schedule, full schedule view, nutrient calculator
- [ ] 4.11 — Pump tab: dose controls, dose history, cooldown timer
- [ ] 4.12 Bucket status badges — visual indicators based on sensor health (in-range = green, drifting = yellow, out-of-range = red)

## 5. Analytics View
- [ ] 5.1 Create `app/static/js/analytics.js` — render function for `#analytics` route
- [ ] 5.2 Grow score history chart — 30-day Chart.js line chart with score breakdown tooltip
- [ ] 5.3 Crop steering panel — dry-back %, EC ramp, generative/vegetative signal for each bucket
- [ ] 5.4 Environment trends — temp/humidity/VPD Chart.js charts over time (24h/7d/30d)
- [ ] 5.5 Bucket comparison — side-by-side pH/EC/temp for all active buckets
- [ ] 5.6 Export controls — CSV export buttons (per bucket, per grow, live snapshot)
- [ ] 5.7 DLI calculator display — daily light integral if light schedule configured

## 6. Strain Library View
- [ ] 6.1 Create `app/static/js/strains.js` — render function for `#strains` route
- [ ] 6.2 Strain list with search/filter — sortable by name, breeder, THC, flowering weeks
- [ ] 6.3 Seed defaults button — seeds popular strains with count feedback
- [ ] 6.4 Add custom strain form — inline form (replaces current modal approach)
- [ ] 6.5 Strain detail card — expandable card showing genetics, notes, linked buckets
- [ ] 6.6 Delete strain with confirmation

## 7. Feeding Schedule View
- [ ] 7.1 Create `app/static/js/feeding.js` — render function for `#feeding` route
- [ ] 7.2 Schedule list — cards showing name, nutrient line, stage count
- [ ] 7.3 Seed preset schedules button
- [ ] 7.4 Schedule detail view — week-by-week table with amounts, EC targets, notes
- [ ] 7.5 Schedule assignment — link schedules to buckets from this view

## 8. Chat Panel
- [ ] 8.1 Create `app/static/js/chat.js` — slide-out panel from right side
- [ ] 8.2 Chat toggle button in bottom nav (💬) — opens/closes panel
- [ ] 8.3 Conversation list per tent with new/switch/delete
- [ ] 8.4 Message stream with markdown rendering and WebSocket streaming
- [ ] 8.5 Quick action buttons: 🏥 Health Check, 📸 Snapshot, 🔄 Summarize
- [ ] 8.6 Image attachment for vision analysis

## 9. Health & Alerts
- [ ] 9.1 Create `app/static/js/health.js` — health check and alert display functions
- [ ] 9.2 Health check results display — rendered inline on Dashboard (latest) and in grow detail
- [ ] 9.3 Alert list with dismiss/acknowledge — accessible from Dashboard alerts card
- [ ] 9.4 Alert badge on nav — shows count of unacked alerts

## 10. Settings
- [ ] 10.1 Create `app/static/js/settings.js` — settings modal/view
- [ ] 10.2 Tent configuration form — all existing fields (thresholds, light, VPD, pH, auto-health, notes)
- [ ] 10.3 PWA controls section — install app button, notification toggle, notification status
- [ ] 10.4 Theme toggle — light/dark/auto selector, persisted in localStorage
- [ ] 10.5 Tent selector — switch active tent (persisted in localStorage)
- [ ] 10.6 Data management — memory viewer, event cleanup

## 11. Migration & Cleanup
- [ ] 11.1 Back up current `index.html` as `index.html.v1`
- [ ] 11.2 Verify all API endpoints are exercised by new UI (audit checklist)
- [ ] 11.3 Verify service worker caches all new static files
- [ ] 11.4 Test PWA install flow with new file structure
- [ ] 11.5 Test offline mode with new cached assets
- [ ] 11.6 Run all existing backend tests — ensure 139/139 pass
- [ ] 11.7 Manual smoke test: create bucket, log sensor, start grow, view diary, check score, export CSV
- [ ] 11.8 Remove `index.html.bak` and `mockup.html` if no longer needed
