# Change: Add Stage-Aware and Strain-Aware Alerting

## Why
The automation/alerting engine ([api/app/automation/engine.py](api/app/automation/engine.py)) evaluates thresholds that are static per grow-type but **not per growth stage**. The single variable that most changes what counts as "healthy" — the grow's phase — is ignored. For example, an `EC > 2.2` alert is equally appropriate in late flower and inappropriate in veg; VPD, humidity, and water-temp ideal ranges all shift by stage per the cannabis quality philosophy in `openspec/project.md`. The result is either false alarms or missed warnings, and alert copy that isn't actionable. We will make thresholds resolve dynamically from the grow's current stage (and strain where known), seeded from documented science defaults but overridable per grow.

## What Changes
- Introduce a **stage-aware threshold resolution layer** that, at evaluation time, resolves the effective ideal/caution/critical range for each sensor metric from the grow's current stage (veg / transition / flower / late-flower / ripening, etc.), seeded from the ranges documented in `openspec/project.md`.
- Add **per-grow threshold overrides**: science defaults seed the ranges; users MAY override any range for a specific grow. Overrides take precedence over defaults.
- Add optional **strain-aware adjustment**: when a bucket/grow has locked strain genetics with a known preference (e.g., indica-leaning shorter flower, sativa longer), thresholds and harvest-timing hints adjust accordingly.
- Make alert messages **contextual and actionable**: include stage, current value, effective range, and a quality-first recommendation (e.g., "EC 2.1 is high for late flower — reduce toward 1.0–1.4 to protect terpenes").
- Preserve existing suppression/cooldown behavior; a stage transition MAY reset cooldowns for affected rules so re-evaluation reflects the new stage.

## Impact
- Affected specs:
  - adaptive-alerting (NEW capability)
- Affected code (expected):
  - api/app/automation/engine.py (threshold resolution)
  - api/app/automation/critical_alerts_defaults.py (stage-keyed defaults)
  - api/app/automation/models.py (per-grow override storage)
  - api/app/automation/routes.py (override CRUD)
  - web/src/app/dashboard/automation/** (override UI)
- Data model impact:
  - NEW table for per-grow, per-metric, per-stage threshold overrides (new tables approved)
- Security impact:
  - override CRUD guarded by existing automation permissions; tenant-scoped via RLS
- Breaking changes:
  - none; when no stage/override data exists, evaluation falls back to current static behavior
