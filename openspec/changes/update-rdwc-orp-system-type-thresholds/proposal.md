# Change: Update RDWC ORP System-Type Thresholds

## Why
RDWC grows using live beneficial biology (for example HydroGuard) were being evaluated with sterile ORP assumptions in some dashboard and configuration paths. This caused misleading warning states and confusing UX.

## What Changes
- Update ORP thresholds for RDWC by system type:
  - live_beneficial: 200-300 mV (target 260)
  - sterilized: 300-450 mV (target 375)
- Ensure UI status logic and gauge zones use per-grow system_type.
- Ensure grow settings updates merge partial settings safely and validate system_type values.
- Add explicit per-grow settings control for system_type in RDWC settings.
- Add human-friendly labels for settings options.
- Update documentation and tests for the above behavior.

## Impact
- Affected specs: grow-orp-system-type
- Affected code:
  - api/app/grows/grow_type_configs/rdwc.py
  - api/app/grows/orp_utils.py
  - api/app/grows/grow_routes.py
  - web/src/components/sensor-gauge.tsx
  - web/src/components/dashboard/adaptive-dashboard.tsx
  - web/src/app/dashboard/page.tsx
  - web/src/app/dashboard/analytics/page.tsx
  - web/src/app/dashboard/grows/[id]/page.tsx
  - docs/orp-system-type.md
  - api/tests/unit/test_grows.py
