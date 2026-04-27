## 1. Phase 1 — Power User UX

### Command Palette
- [x] 1.1 Install `cmdk` if not present (shadcn Command already exists, verify)
- [x] 1.2 Create `src/components/command-palette.tsx` — global command palette dialog
- [x] 1.3 Wire ⌘K / Ctrl+K keyboard shortcut in root layout
- [x] 1.4 Implement search sources: pages (static routes), grows, tents, strains, devices
- [x] 1.5 Implement quick actions: Create Grow, Create Tent, Run Health Check, Toggle Theme
- [x] 1.6 Add recent items tracking (localStorage)
- [x] 1.7 Add fuzzy search filtering with match highlighting
- [x] 1.8 Add command palette trigger button in page header (search icon)

### Celebration Animations
- [x] 1.9 Install `canvas-confetti` package
- [x] 1.10 Create `src/lib/confetti.ts` — reusable confetti trigger functions (burst, fireworks, rain)
- [x] 1.11 Add confetti on grow status → "completed" transition (grows page)
- [x] 1.12 Add confetti on harvest yield creation (harvest tab)
- [x] 1.13 Add confetti on task completion streak (3+ tasks in a row)
- [x] 1.14 Add confetti on onboarding checklist completion (dashboard)

### Sparkline Mini-Charts
- [x] 1.15 Create `src/components/sparkline.tsx` — tiny inline recharts line chart (no axes, just the line + gradient fill)
- [x] 1.16 Add sparklines to dashboard stat cards (pH, EC, temp, humidity)
- [x] 1.17 Fetch 7-day trend data from sensor readings API
- [x] 1.18 Add color-coded sparkline (green = stable, yellow = drifting, red = out of range)

## 2. Phase 2 — Data Visualization

### Heat Map Calendar
- [ ] 2.1 Create `src/components/heat-map-calendar.tsx` — GitHub-style year grid component
- [ ] 2.2 Implement activity score aggregation (journal entries, photos, tasks, feedings)
- [ ] 2.3 Add to analytics page with tooltip showing day breakdown
- [ ] 2.4 Support dark/light theme color scales
- [ ] 2.5 Add year selector and legend

### Real-time Sensor Gauges
- [ ] 2.6 Create `src/components/sensor-gauge.tsx` — animated radial gauge with SVG arcs
- [ ] 2.7 Implement color-coded zones: danger (red), warning (amber), optimal (green)
- [ ] 2.8 Define zone thresholds per sensor type (pH: 5.5-6.5 optimal, EC: 1.0-2.5, temp: 68-82°F, humidity: 40-60%)
- [ ] 2.9 Add smooth animated transitions between values (framer-motion)
- [ ] 2.10 Add gauges to grow detail sensors tab
- [ ] 2.11 Add gauges to tent detail page

### Grow Timeline
- [ ] 2.12 Create `src/components/grow-timeline.tsx` — vertical timeline with milestone markers
- [ ] 2.13 Define milestone types: planted, transplant, veg start, flip to flower, first pistils, harvest, cure complete
- [ ] 2.14 Link journal entries, photos, and feeding events to timeline nodes
- [ ] 2.15 Add photo thumbnails inline on timeline
- [ ] 2.16 Add expandable detail cards at each milestone
- [ ] 2.17 Add to grow detail page as a new tab or section

## 3. Phase 3 — AI & Media

### AI Chat Panel
- [ ] 3.1 Create `src/components/ai-chat-panel.tsx` — sliding drawer component
- [ ] 3.2 Implement WebSocket connection to `getAiChatWsUrl()` with auto-reconnect
- [ ] 3.3 Add streaming message rendering with typing indicator
- [ ] 3.4 Add markdown rendering in chat messages (code blocks, lists, bold)
- [ ] 3.5 Pass current grow/tent context with each message
- [ ] 3.6 Add message history with scroll-to-bottom behavior
- [ ] 3.7 Add floating action button (FAB) to trigger chat from any dashboard page
- [ ] 3.8 Add suggested prompts (e.g., "How's my grow doing?", "What should I feed today?")

### Photo Timelapse Player
- [ ] 3.9 Create `src/components/timelapse-player.tsx` — photo sequence player
- [ ] 3.10 Implement scrubber/slider for manual frame navigation
- [ ] 3.11 Add play/pause with configurable speed (0.5x, 1x, 2x, 4x)
- [ ] 3.12 Add fullscreen mode
- [ ] 3.13 Fetch grow photo sequence and sort chronologically
- [ ] 3.14 Add smooth crossfade transitions between frames
- [ ] 3.15 Integrate into grow detail photos tab

### Animated Grow Stage Indicator
- [ ] 3.16 Create `src/components/grow-stage-indicator.tsx` — SVG plant illustration
- [ ] 3.17 Design 5 plant stages: seed, seedling, vegetative (small), vegetative (large/bushy), flowering, harvest-ready
- [ ] 3.18 Animate transitions between stages with morph/grow effects
- [ ] 3.19 Map grow phase/day count to visual stage
- [ ] 3.20 Add to grow detail hero card
- [ ] 3.21 Add small versions to dashboard active-grows widget cards

## 4. Phase 4 — Platform Integration

### Live Camera Feeds
- [ ] 4.1 Create `src/components/camera-feed.tsx` — WebRTC/MSE video player component
- [ ] 4.2 Integrate with go2rtc streaming endpoint for Frigate cameras
- [ ] 4.3 Add snapshot fallback when stream unavailable
- [ ] 4.4 Add to tent detail page (map camera to tent)
- [ ] 4.5 Add fullscreen and picture-in-picture support
- [ ] 4.6 Handle connection errors gracefully with retry

### Push Notifications
- [ ] 4.7 Create `src/lib/push-notifications.ts` — Push subscription management
- [ ] 4.8 Implement notification permission request flow (non-intrusive, after user action)
- [ ] 4.9 Register push subscription with Tendril API
- [ ] 4.10 Add notification categories: sensor alerts, task reminders, harvest countdown, AI results
- [ ] 4.11 Add notification preferences UI on notifications settings page
- [ ] 4.12 Update Service Worker to handle push events and show native notifications
- [ ] 4.13 Add click-to-navigate: tapping notification opens relevant page

## 5. Deploy & Verify
- [ ] 5.1 Build and push Docker image
- [ ] 5.2 Deploy to cluster and verify all features
- [ ] 5.3 Test on mobile (PWA)
