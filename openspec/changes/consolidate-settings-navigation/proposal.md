# Change: Consolidate Settings & Navigation

## Why
Settings are scattered across 12+ locations with inconsistent grouping. Users must navigate to 5+ different pages to find related configuration. Billing appears in two places. Notifications live under "Automation" instead of a logical settings group. The sidebar hierarchy doesn't match mental models.

## What Changes
- Restructure sidebar navigation into clear logical groups
- Consolidate account-related pages (profile, security, billing, team) under one "Account" section
- Group system configuration (notifications, automation, schedules) under one "Automation & Alerts" section
- Move integrations and devices into a "Connections" group
- Remove duplicate billing access points
- Add a unified settings search/index page

## Impact
- Affected specs: None existing (new UX spec)
- Affected code: `web/src/components/app-sidebar.tsx`, `web/src/app/dashboard/settings/`, all settings-adjacent pages (routing may change)
- **NOT breaking API** — backend unchanged, only frontend navigation restructure
