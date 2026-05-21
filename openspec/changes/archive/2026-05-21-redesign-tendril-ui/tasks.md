# Tasks: redesign-tendril-ui — Phase 1

## 1. Foundation
- [x] 1.1 Install framer-motion
- [x] 1.2 Wire up next-themes (light/dark/system) — remove hardcoded `dark` class from root layout
- [x] 1.3 Add theme toggle button to sidebar footer and mobile nav

## 2. Navigation Overhaul
- [x] 2.1 Redesign mobile-bottom-nav: 4 tabs (Home, Grows, AI, More) + center FAB button
- [x] 2.2 Build FABMenu component — expands to show quick actions (Log Reading, Health Check, Quick Photo, Log Ambient)
- [x] 2.3 Build "More" sheet — grid of remaining nav items (Tasks, Devices, Automation, Schedules, Strains, Tents, Notifications, Analytics, Settings)
- [x] 2.4 Clean up sidebar — collapsible groups with chevron indicator

## 3. Clickable Cards
- [x] 3.1 Grows list — wrap cards in Link, entire surface navigable
- [N/A] 3.2 Devices list — no device detail page exists; skipped
- [x] 3.3 Dashboard — harvest countdown cards clickable (link to grow detail)

## 4. Destructive Action Dialogs
- [x] 4.1 Create reusable ConfirmDialog component (title, description, confirmLabel, variant)
- [x] 4.2 Replace all window.confirm() calls with ConfirmDialog

## 5. Subtle Animations
- [x] 5.1 Add framer-motion page transition wrapper (template.tsx with fade+slide)
- [x] 5.2 Add tap spring feedback to interactive cards (whileTap scale 0.98)

## 6. Validation & Deploy
- [ ] 6.1 Test on mobile viewport (responsive check)
- [x] 6.2 Commit, push, build, deploy

## Status: PHASE 1 COMPLETE (15/16 tasks — 1 N/A, 1 manual QA remaining)

---

# Tasks: redesign-tendril-ui — Phase 2

## 7. Dashboard Hero Card
- [x] 7.1 Hero card on dashboard — primary active grow with camera snapshot, stage, day count, harvest countdown
- [x] 7.2 Harvest countdown cards wrapped in Link to grow detail

## 8. Navigation Polish
- [x] 8.1 Grow detail tabs — horizontally scrollable pill tabs on mobile (overflow-x-auto + scrollbar-none)

## 9. Loading Skeletons
- [x] 9.1 Create reusable PageSkeleton component (card grid / row variants)
- [x] 9.2 Add loading state + PageSkeleton to strains page
- [x] 9.3 Add loading state + PageSkeleton to tasks page
- [x] 9.4 Add loading state + PageSkeleton to automation page
- [x] 9.5 Add loading state + PageSkeleton to schedules page
- [x] 9.6 Add loading state + PageSkeleton to notifications page
- [x] 9.7 Add loading state + PageSkeleton to grow-types page
- [x] 9.8 Add loading state + PageSkeleton to audit page
- [x] 9.9 Add loading state + PageSkeleton to api-keys page

## 10. Empty State Polish
- [x] 10.1 Strains library tab — Card with Library icon + message + action button
- [x] 10.2 Strains leaderboard — Card with Trophy icon + message
- [x] 10.3 Audit page — Card with Eye icon + message
- [x] 10.4 API Keys page — Card with Key icon + message + action button
- [x] 10.5 Notifications preferences — Bell icon + contextual message

## 11. Form Validation
- [x] 11.1 Install react-hook-form + zod + @hookform/resolvers
- [x] 11.2 Create Grow dialog — react-hook-form + zod schema (name, tent_id, grow_type all required), field-level error messages
- [x] 11.3 Create Task dialog — show validation error when title is empty

## 12. Deploy
- [x] 12.1 Commit, push, build, deploy

## Status: PHASE 2 COMPLETE

---

# Tasks: redesign-tendril-ui — Phase 3

## 13. Gesture Support
- [x] 13.1 Create reusable SwipeableCard component (swipe right = complete, swipe left = delete)
- [x] 13.2 Add swipe-to-complete on task cards (tasks page)
- [x] 13.3 Add swipe-to-complete on grow detail tasks tab
- [x] 13.4 Create PullToRefresh component (drag-down spinner + async refresh)
- [x] 13.5 Add pull-to-refresh on dashboard
- [x] 13.6 Add pull-to-refresh on grows list
- [x] 13.7 Add pull-to-refresh on tasks list

## 14. Onboarding Flow
- [x] 14.1 Create OnboardingChecklist component (3-step: tent → grow → device)
- [x] 14.2 Integrate into dashboard — shows when any setup step is incomplete
- [x] 14.3 Steps auto-check based on actual data (tents, grows, devices)

## 15. Customizable Dashboard Widgets
- [x] 15.1 Create useWidgetLayout hook (localStorage persistence, toggle/reorder/reset)
- [x] 15.2 Create CustomizeWidgetsDialog (toggle switches + up/down reorder + reset)
- [x] 15.3 Refactor dashboard sections into widget render map (stats, hero, countdown, active-grows)
- [x] 15.4 Add "Customize" button to dashboard header

## 16. Deploy
- [ ] 16.1 Commit, push, build, deploy

## Status: PHASE 3 IN PROGRESS (14/15 tasks complete)
