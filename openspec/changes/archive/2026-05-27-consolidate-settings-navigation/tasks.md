## 1. Design & Planning
- [x] 1.1 Define final sidebar navigation hierarchy (groups, labels, icons)
- [x] 1.2 Define URL routing strategy (keep old routes as redirects or restructure)
- [x] 1.3 Decide if settings sub-pages stay as separate routes or become tabs within a single page

## 2. Sidebar Navigation Restructure
- [x] 2.1 Update `app-sidebar.tsx` with new navigation groups
- [x] 2.2 New group: "Account" — Profile & Preferences, Security, Billing, Team, API Keys, Support, Audit Trail
- [x] 2.3 New group: "Automation" — Rules, Schedules, Notifications, Devices, Integrations
- [x] 2.4 Connections merged into Automation per user decision
- [x] 2.5 Keep "Library" — Strains, Reference
- [x] 2.6 "Account" group is now the unified settings section
- [x] 2.7 API Keys under Account, Audit Trail owner-only

## 3. Settings Hub Page
- [x] 3.1 Create a unified settings index page with category cards linking to sub-pages
- [x] 3.2 Add search/filter to quickly find settings by keyword
- [x] 3.3 Hub page at /dashboard/settings-hub with breadcrumbs

## 4. Cameras → Devices Merge
- [x] 4.1 Added Sensors and Cameras tabs to Devices page
- [x] 4.2 Old /dashboard/cameras redirects to /dashboard/devices?tab=cameras
- [x] 4.3 Updated layout-config camera references

## 5. Mobile Navigation
- [x] 5.1 Update mobile bottom nav to reflect new grouping
- [x] 5.2 Settings accessible via "All Settings" in More menu (2 taps)

## 6. Testing
- [x] 6.1 TypeScript type-check passes
- [x] 6.2 No IDE errors in modified files
- [x] 6.3 Manual QA: walk through each settings area on mobile and desktop
- [x] 6.2 Verify all old routes redirect properly
- [x] 6.3 Manual QA: walk through each settings area on mobile and desktop
