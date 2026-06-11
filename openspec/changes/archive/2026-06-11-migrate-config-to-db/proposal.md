# Change: Migrate Config-as-Code to Database

## Why
~44,800 lines of domain data (grow type configs, treatments, task templates, feed charts, nutrient knowledge, etc.) are hardcoded in Python files. This prevents admin management, tenant customization, and hot-reloading. Integrations coming next will need the same pattern — better to establish it now.

## What Changes
- **Phase 1 (HIGH):** Migrate grow type configs, treatment DB, and task templates to fully normalized DB tables with admin CRUD + tenant override inheritance
- **Phase 2 (MED/LOW):** Migrate nutrient knowledge, feed charts, companion planting, KB articles, alert rules, ESPHome templates, retention/SLA defaults
- Add Alembic migrations to create all new tables
- Add seed commands to populate from existing hardcoded data
- Add admin API endpoints for CRUD management
- Add tenant override system (global defaults + per-tenant overrides that merge)
- Add frontend admin pages for user-friendly management
- Remove hardcoded Python data files after migration

## Impact
- Affected specs: `grow-assistant-core`, `environment-monitoring`
- Affected code: `grows/grow_types.py`, `grows/grow_type_configs/` (18 files), `ai/treatment_db.py`, `scheduler/task_generator.py`, `reference/nutrient_knowledge.py`, `reference/feed_charts.py`, `reference/nutrient_sync.py`, `reference/strain_sync.py`, `outdoor/companion_routes.py`, `support/kb_seed.py`, `reference/esphome_templates.py`, `automation/engine.py`
- New tables: ~15 new database tables
- **BREAKING**: Code that directly imports from hardcoded data files will need to use DB queries instead
