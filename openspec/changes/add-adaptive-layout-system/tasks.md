## 1. Backend: Multi-Camera Model — DONE
- [x] 1.1 Create `tent_cameras` SQLAlchemy model (id, tent_id, label, camera_type, url, sort_order, is_primary, created_at)
- [x] 1.2 Create Alembic migration: new `tent_cameras` table, migrate existing `tents.camera_url` data, drop column
- [x] 1.3 Add `layout_mode` column to `users` table (VARCHAR(20), default 'standard')
- [x] 1.4 Create camera CRUD routes: list/create/update/delete cameras for a tent
- [x] 1.5 Update `GET /tents/{tent_id}/camera-snapshot` to accept optional `camera_id` param (default: primary)
- [x] 1.6 Update AI gather code (`app/ai/gather.py`) to query `tent_cameras` table (primary camera)
- [x] 1.7 Add `GET /v1/auth/me` response field: `layout_mode`
- [x] 1.8 Add `PATCH /v1/auth/profile` support for updating `layout_mode`
- [x] 1.9 Write tests for camera CRUD, migration, layout_mode

## 2. Backend: Quick-Log Endpoints — DONE
- [x] 2.1 Create `POST /v1/quick-log/feeding` — accepts array of bucket_ids + shared reading data (pH, EC, temp, volume, nutrients)
- [x] 2.2 Create `POST /v1/quick-log/reading` — manual sensor reading (temp, humidity, VPD) for a tent
- [x] 2.3 Create `POST /v1/quick-log/note` — quick journal entry with optional tags
- [x] 2.4 Create `POST /v1/quick-log/photo` — photo upload with auto-tag to grow/bucket
- [x] 2.5 Create `POST /v1/quick-log/batch` — offline queue replay (array of quick-log actions with client timestamps)
- [x] 2.6 Write tests for all quick-log endpoints

## 3. Frontend: Layout Engine Core — DONE
- [x] 3.1 Create `LayoutMode` type and `LAYOUT_CONFIGS` constant defining all 5 modes
- [x] 3.2 Create `LayoutProvider` context (reads user.layout_mode, provides mode config)
- [x] 3.3 Create `LayoutShell` component: switches between MobileShell and DesktopShell
- [x] 3.4 Create `MobileShell` — bottom tab bar + content area (replaces sidebar on mobile)
- [x] 3.5 Create `DesktopShell` — sidebar + content area (adapts density per mode)
- [x] 3.6 Create `BottomTabBar` component with per-mode tab configurations
- [x] 3.7 Update `use-user.ts` hook to include `layout_mode` field
- [x] 3.8 Update dashboard `layout.tsx` to wrap with `LayoutProvider` and use `LayoutShell`
- [x] 3.9 Create `useLayoutMode()` hook for components to read current mode + density settings

## 4. Frontend: Quick-Log System — DONE
- [x] 4.1 Create `QuickLogSheet` component (bottom sheet / modal, always accessible)
- [x] 4.2 Create `FeedingLogForm` — pH, EC, water temp, volume, nutrient selector
- [x] 4.3 Create `BulkBucketSelector` — multi-select buckets for DWC flush-and-fill
- [x] 4.4 Create `QuickPhotoCapture` — camera access → auto-tag to active grow/bucket
- [x] 4.5 Create `QuickNoteForm` — free text + quick-tag buttons (topped, transplanted, pest, etc.)
- [x] 4.6 Create `ManualReadingForm` — temp, humidity, VPD for manual environment logging
- [x] 4.7 Wire quick-log to bottom tab "Log" button (all modes)
- [x] 4.8 Add keyboard shortcut ⌘L for desktop quick-log
- [x] 4.9 Implement offline queue with localStorage + sync on reconnect
- [x] 4.10 Add "recent values" quick-fill suggestions in feeding form

## 5. Frontend: Home Screens (per mode) — DONE
- [x] 5.1 Unified home page adapts per mode (maxCards, density, etc.)
- [x] 5.2 Create shared `GrowCard` component with density variants (compact, standard, expanded)
- [x] 5.3 Create shared `SensorSummaryStrip` — inline sensor badges (pH, EC, temp, humidity)
- [x] 5.4 Wire home screen selection to LayoutProvider mode

## 6. Frontend: Camera Views — DONE
- [x] 6.1 Create `CameraGrid` component (2x2 or 3x3 layout for multiple cameras)
- [x] 6.2 Camera fullscreen mode with close overlay
- [x] 6.3 Camera refresh per-camera
- [x] 6.4 Create `CameraManagement` settings page (add/edit/delete/reorder cameras per tent)
- [x] 6.5 Update tent detail page to show camera grid instead of single image
- [x] 6.6 Add camera tab to bottom nav (Beginner/Home/Pro modes)
- [x] 6.7 Wire AI health check to support selecting specific camera from multi-camera tent

## 7. Frontend: Onboarding Wizard — DONE
- [x] 7.1 Create `OnboardingWizard` component (3 steps + completion)
- [x] 7.2 Create Step 1: "What are you growing?" (Indoor / Outdoor / Both) with illustrations
- [x] 7.3 Create Step 2: "How many grows?" (1 / 2-5 / 6-20 / 20+) with visual scale
- [x] 7.4 Create Step 3: "Experience level?" (First grow / Hobbyist / Experienced / Professional / Commercial)
- [x] 7.5 Create `WizardComplete` — shows selected mode, creates first grow, sets layout_mode via API
- [x] 7.6 Add "Change layout" option in settings page
- [x] 7.7 OnboardingGate shows wizard on first login (when user has 0 grows)

## 8. Integration & Polish — DONE
- [x] 8.1 Ensure all existing pages respect `LayoutProvider` density settings
- [x] 8.2 Add page transition animations per mode (Beginner: playful, Pro: instant)
- [x] 8.3 Vitest unit tests for layout config + onboarding mode logic (15 tests)
- [x] 8.4 Playwright E2E tests for onboarding flow, quick-log, camera management, responsive
- [x] 8.5 TypeScript compiles clean (no errors in new files)
