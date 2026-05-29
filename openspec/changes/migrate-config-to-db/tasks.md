## Phase 1A: Database Schema + Seed Migration

- [ ] 1.1 Create Alembic migration: `grow_type_profiles` table (id, name, slug, description, sensor_kit, ai_context_prompt, is_system, created_at, updated_at)
- [ ] 1.2 Create Alembic migration: `grow_type_stages` table (id, profile_id FK, name, slug, order, duration_days_min, duration_days_max, description, tips)
- [ ] 1.3 Create Alembic migration: `grow_type_environment` table (id, stage_id FK, temp_min, temp_max, temp_ideal, humidity_min, humidity_max, humidity_ideal, vpd_min, vpd_max, light_hours, light_ppfd_min, light_ppfd_max, co2_min, co2_max, water_temp_min, water_temp_max)
- [ ] 1.4 Create Alembic migration: `grow_type_nutrients` table (id, stage_id FK, week, ec_min, ec_max, ec_target, ph_min, ph_max, ph_target, base_nutrients, supplements, notes)
- [ ] 1.5 Create Alembic migration: `grow_type_watering` table (id, stage_id FK, method, frequency_hours, volume_ml, runoff_target_pct, notes)
- [ ] 1.6 Create Alembic migration: `grow_type_equipment` table (id, profile_id FK, item_name, category, required, notes, purchase_url)
- [ ] 1.7 Create Alembic migration: `grow_type_troubleshooting` table (id, profile_id FK, stage_id FK nullable, symptom, cause, solution, severity, image_url)
- [ ] 1.8 Create Alembic migration: `task_templates` table (id, name, description, category, grow_type_slugs[], frequency_hours, stage_slug, priority, is_system, created_at)
- [ ] 1.9 Create Alembic migration: `task_template_steps` table (id, template_id FK, order, instruction, duration_minutes, optional)
- [ ] 1.10 Create Alembic migration: `tenant_config_overrides` table (id, tenant_id FK, config_type enum, config_key, override_json, created_at, updated_at)
- [ ] 1.11 Write seed script: parse `grows/grow_type_configs/*.py` → populate grow_type_profiles/stages/environment/nutrients/watering/equipment/troubleshooting
- [ ] 1.12 Write seed script: parse `scheduler/task_generator.py` TaskTemplate list → populate task_templates/steps
- [ ] 1.13 Verify treatment_db.py is fully seeded to existing `treatments` table (remove any in-memory reads)
- [ ] 1.14 Write migration tests: assert row counts match source data counts

## Phase 1B: Service Layer (DB reads + cache)

- [ ] 1.15 Create `app/config_service/__init__.py` — service module
- [ ] 1.16 Create `app/config_service/grow_types.py` — async functions: get_profile(slug), get_stage_config(profile, stage), get_full_config(slug), list_profiles()
- [ ] 1.17 Create `app/config_service/task_templates.py` — async functions: get_templates(grow_type, stage), get_template(id)
- [ ] 1.18 Create `app/config_service/treatments.py` — async functions: search_treatments(query), get_treatment(id) (replace in-memory fallback)
- [ ] 1.19 Create `app/config_service/overrides.py` — async functions: get_with_overrides(tenant_id, config_type, key), set_override(), delete_override()
- [ ] 1.20 Create `app/config_service/cache.py` — in-process TTL cache (5-min) with invalidation on write
- [ ] 1.21 Write unit tests for service layer (mock DB, test cache behavior, test override merging)

## Phase 1C: Swap Consumers to Service Layer

- [ ] 1.22 Update `grows/grow_type_routes.py` — use config_service.grow_types instead of importing grow_type_configs/
- [ ] 1.23 Update `grows/grow_types.py` — use config_service for profile lookups
- [ ] 1.24 Update `ai/routes.py` — use config_service.grow_types for AI context building
- [ ] 1.25 Update `ai/diagnose_routes.py` — use config_service.treatments instead of treatment_db.py
- [ ] 1.26 Update `scheduler/task_generator.py` — use config_service.task_templates instead of hardcoded list
- [ ] 1.27 Update `commercial/grow_type_routes.py` — use config_service for custom grow types
- [ ] 1.28 Update `automation/engine.py` — use config_service for alert thresholds
- [ ] 1.29 Run full test suite, fix any breakage from consumer swap

## Phase 1D: Admin CRUD API

- [ ] 1.30 Create `app/admin/config_routes.py` — CRUD endpoints for grow_type_profiles
- [ ] 1.31 Add CRUD endpoints for grow_type_stages (nested under profile)
- [ ] 1.32 Add CRUD endpoints for grow_type_environment (nested under stage)
- [ ] 1.33 Add CRUD endpoints for grow_type_nutrients (nested under stage)
- [ ] 1.34 Add CRUD endpoints for task_templates + steps
- [ ] 1.35 Add CRUD endpoints for tenant_config_overrides
- [ ] 1.36 Add export/import endpoints (JSON backup/restore)
- [ ] 1.37 Write API tests for all CRUD endpoints (auth, validation, 404s)

## Phase 1E: Frontend Admin Pages

- [ ] 1.38 Create admin layout + navigation (Settings → Config Management)
- [ ] 1.39 Build Grow Type Config editor page (profile list → stage editor → environment/nutrient forms)
- [ ] 1.40 Build Task Template editor page (list → detail → step editor)
- [ ] 1.41 Build Tenant Override editor (select tenant → view overrides → edit/delete)
- [ ] 1.42 Build config export/import UI (download JSON, upload JSON with preview)
- [ ] 1.43 Write frontend tests for admin pages

## Phase 1F: Cleanup

- [ ] 1.44 Remove `grows/grow_type_configs/` directory (18 files)
- [ ] 1.45 Remove `grows/grow_types.py` hardcoded GROW_TYPE_PROFILES dict
- [ ] 1.46 Remove `ai/treatment_db.py` (data now fully in DB)
- [ ] 1.47 Remove hardcoded TaskTemplate list from `scheduler/task_generator.py`
- [ ] 1.48 Update imports across codebase — ensure nothing references deleted files
- [ ] 1.49 Final integration test: full startup → seed → API responses match previous behavior

## Phase 2: MED/LOW Priority Migrations

- [ ] 2.1 Create `nutrient_guides` table + seed from `reference/nutrient_knowledge.py` + admin CRUD
- [ ] 2.2 Create `feed_charts` table + seed from `reference/feed_charts.py` + admin CRUD
- [ ] 2.3 Create `companion_plants` table + seed from `outdoor/companion_routes.py` + admin CRUD
- [ ] 2.4 Create `alert_rule_templates` table + seed from `automation/engine.py` CRITICAL_ALERTS/WEATHER_RULES + admin CRUD
- [ ] 2.5 Create `esphome_templates` table + seed from `reference/esphome_templates.py` + admin CRUD
- [ ] 2.6 Create `system_config` table for simple settings (retention periods, SLA hours, frost dates) + admin CRUD
- [ ] 2.7 Remove hardcoded source in `nutrient_sync.py` — make admin UI the source of truth for nutrient products
- [ ] 2.8 Remove hardcoded source in `strain_sync.py` — manage strains via admin UI
- [ ] 2.9 Remove hardcoded source in `kb_seed.py` — manage KB articles via admin UI
- [ ] 2.10 Frontend admin pages for Phase 2 tables (nutrient guides, feed charts, companion plants, alert rules, ESPHome templates, system config)
- [ ] 2.11 Final cleanup: remove all deprecated Python data files from Phase 2
