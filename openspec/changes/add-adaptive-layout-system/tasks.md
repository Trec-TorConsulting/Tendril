## 1. Backend: Multi-Camera Model
- [ ] 1.1 Create `tent_cameras` SQLAlchemy model (id, tent_id, label, camera_type, url, sort_order, is_primary, created_at)
- [ ] 1.2 Create Alembic migration: new `tent_cameras` table, migrate existing `tents.camera_url` data, drop column
- [ ] 1.3 Add `layout_mode` column to `users` table (VARCHAR(20), default 'standard')
- [ ] 1.4 Create camera CRUD routes: list/create/update/delete cameras for a tent
- [ ] 1.5 Update `GET /tents/{tent_id}/camera-snapshot` to accept optional `camera_id` param (default: primary)
- [ ] 1.6 Update AI gather code (`app/ai/gather.py`) to query `tent_cameras` table (primary camera)
- [ ] 1.7 Add `GET /v1/auth/me` response field: `layout_mode`
- [ ] 1.8 Add `PATCH /v1/auth/profile` support for updating `layout_mode`
- [ ] 1.9 Write tests for camera CRUD, migration, layout_mode

## 2. Backend: Quick-Log Endpoints
- [ ] 2.1 Create `POST /v1/quick-log/feeding` — accepts array of bucket_ids + shared reading data (pH, EC, temp, volume, nutrients)
- [ ] 2.2 Create `POST /v1/quick-log/reading` — manual sensor reading (temp, humidity, VPD) for a tent
- [ ] 2.3 Create `POST /v1/quick-log/note` — quick journal entry with optional tags
- [ ] 2.4 Create `POST /v1/quick-log/photo` — photo upload with auto-tag to grow/bucket
- [ ] 2.5 Create `POST /v1/quick-log/batch` — offline queue replay (array of quick-log actions with client timestamps)
- [ ] 2.6 Write tests for all quick-log endpoints

## 3. Frontend: Layout Engine Core
- [ ] 3.1 Create `LayoutMode` type and `LAYOUT_CONFIGS` constant defining all 5 modes
- [ ] 3.2 Create `LayoutProvider` context (reads user.layout_mode, provides mode config)
- [ ] 3.3 Create `LayoutShell` component: switches between MobileShell and DesktopShell
- [ ] 3.4 Create `MobileShell` — bottom tab bar + content area (replaces sidebar on mobile)
- [ ] 3.5 Create `DesktopShell` — sidebar + content area (adapts density per mode)
- [ ] 3.6 Create `BottomTabBar` component with per-mode tab configurations
- [ ] 3.7 Update `use-user.ts` hook to include `layout_mode` field
- [ ] 3.8 Update dashboard `layout.tsx` to wrap with `LayoutProvider` and use `LayoutShell`
- [ ] 3.9 Create `useLayoutMode()` hook for components to read current mode + density settings

## 4. Frontend: Quick-Log System
- [ ] 4.1 Create `QuickLogSheet` component (bottom sheet / modal, always accessible)
- [ ] 4.2 Create `FeedingLogForm` — pH, EC, water temp, volume, nutrient selector
- [ ] 4.3 Create `BulkBucketSelector` — multi-select buckets for DWC flush-and-fill
- [ ] 4.4 Create `QuickPhotoCapture` — camera access → auto-tag to active grow/bucket
- [ ] 4.5 Create `QuickNoteForm` — free text + quick-tag buttons (topped, transplanted, pest, etc.)
- [ ] 4.6 Create `ManualReadingForm` — temp, humidity, VPD for manual environment logging
- [ ] 4.7 Wire quick-log to bottom tab "Log" button (all modes)
- [ ] 4.8 Add keyboard shortcut ⌘L for desktop quick-log
- [ ] 4.9 Implement offline queue with localStorage + sync on reconnect
- [ ] 4.10 Add "recent values" quick-fill suggestions in feeding form

## 5. Frontend: Home Screens (per mode)
- [ ] 5.1 Create `BeginnerHome` — full-screen single-grow card, guided next-steps, achievements
- [ ] 5.2 Create `HomeHome` — hero grow card + sensor summary + harvest countdown
- [ ] 5.3 Create `StandardHome` — multi-grow grid + stats strip + recent activity
- [ ] 5.4 Create `ProHome` — dense multi-grow table + live sensor panels + alerts sidebar
- [ ] 5.5 Create `CommercialHome` — fleet overview + team activity feed + alert banner
- [ ] 5.6 Create shared `GrowCard` component with density variants (compact, standard, expanded)
- [ ] 5.7 Create shared `SensorSummaryStrip` — inline sensor badges (pH, EC, temp, humidity)
- [ ] 5.8 Wire home screen selection to LayoutProvider mode

## 6. Frontend: Camera Views
- [ ] 6.1 Create `CameraGrid` component (2x2 or 3x3 layout for multiple cameras)
- [ ] 6.2 Create `CameraCarousel` component (swipe between cameras on mobile)
- [ ] 6.3 Create `CameraFullScreen` component (single camera with refresh timer)
- [ ] 6.4 Create `CameraManagement` settings page (add/edit/delete/reorder cameras per tent)
- [ ] 6.5 Update tent detail page to show camera grid instead of single image
- [ ] 6.6 Add camera tab to bottom nav (Beginner/Home/Pro modes)
- [ ] 6.7 Wire AI health check to support selecting specific camera from multi-camera tent

## 7. Frontend: Onboarding Wizard
- [ ] 7.1 Create `OnboardingWizard` component (3 steps + completion)
- [ ] 7.2 Create Step 1: "What are you growing?" (Indoor / Outdoor / Both) with illustrations
- [ ] 7.3 Create Step 2: "How many grows?" (1 / 2-5 / 6-20 / 20+) with visual scale
- [ ] 7.4 Create Step 3: "Experience level?" (First grow / Hobbyist / Experienced / Professional / Commercial)
- [ ] 7.5 Create `WizardComplete` — shows selected mode, creates first grow, sets layout_mode via API
- [ ] 7.6 Add "Change layout" option in settings page
- [ ] 7.7 Add mode-upgrade prompt (triggers when user outgrows current mode)
- [ ] 7.8 Wire onboarding to show on first login (when user has 0 grows)

## 8. Integration & Polish
- [ ] 8.1 Ensure all existing pages respect `LayoutProvider` density settings
- [ ] 8.2 Add page transition animations per mode (Beginner: playful, Pro: instant)
- [ ] 8.3 Test all 5 modes on mobile viewport (375px, 390px, 428px)
- [ ] 8.4 Test all 5 modes on tablet viewport (768px, 1024px)
- [ ] 8.5 Test all 5 modes on desktop viewport (1280px, 1920px)
- [ ] 8.6 Accessibility audit: ensure tab navigation and screen reader support per mode
- [ ] 8.7 Performance audit: ensure mode switching doesn't cause layout shift or re-render cascade
- [ ] 8.8 Update PWA manifest icons and splash screens
- [ ] 8.9 Write Vitest unit tests for LayoutEngine, QuickLog, Onboarding
- [ ] 8.10 Write Playwright e2e tests for onboarding flow and mode switching
