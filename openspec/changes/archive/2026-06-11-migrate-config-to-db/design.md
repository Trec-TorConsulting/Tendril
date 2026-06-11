## Context
Tendril has accumulated ~44,800 lines of domain-specific configuration data hardcoded in Python files. This data includes grow type environment targets, nutrient schedules, treatment databases, task templates, and more. All of it should be database-driven for:
1. Admin manageability without code deployments
2. Tenant-specific overrides (custom thresholds, schedules)
3. Hot-reloading without pod restarts
4. Proper CRUD lifecycle with audit trails

## Goals
- Every piece of domain reference data lives in PostgreSQL with admin CRUD
- Tenant override system: global defaults + per-tenant overrides with JSON merge semantics
- Alembic migrations seed initial data from current hardcoded sources
- Admin API endpoints with proper auth (admin role required)
- Frontend admin pages for user-friendly management
- Zero data loss during migration (seed from existing code → DB)
- AI context builder reads from DB instead of importing Python dicts

## Non-Goals
- Migrating AI tool schemas (CHAT_TOOLS) — these are functional code, not data
- Real-time collaborative editing of configs
- Version history/rollback for individual config changes (audit trail suffices)
- Multi-language/i18n for reference content

## Decisions

### Schema Strategy: Fully Normalized
The grow type config system (35K lines) will be fully normalized into relational tables rather than JSONB blobs. This enables:
- SQL-level querying of stage targets (e.g. "all grow types where seedling humidity > 70%")
- Efficient partial updates
- Foreign keys for referential integrity
- Clean tenant override at any granularity level

### Table Design (Phase 1 — HIGH priority)

#### Grow Type Configuration System
```
grow_type_profiles          — Core profile (name, description, sensor_kit, ai_context)
grow_type_stages            — Stages per profile (name, order, duration_days, description)
grow_type_environment       — Environment targets per stage (temp_min/max, humidity, vpd, light_hours, co2)
grow_type_nutrients         — Nutrient schedule per stage (week, ec_target, ph_target, nutrients_json)
grow_type_watering          — Watering guidance per stage (frequency, volume, method, notes)
grow_type_equipment         — Equipment list per profile (item, required, notes)
grow_type_troubleshooting   — Common issues per profile (symptom, cause, solution, stage)
```

#### Treatment Database
```
treatments                  — Already exists (seeded from treatment_db.py)
                              Ensure: all fields populated, remove in-memory fallback reads
```

#### Task Templates
```
task_templates              — Template definition (name, description, category, grow_types[], frequency, stage, priority)
task_template_steps         — Steps within a template (order, instruction, duration_minutes)
```

### Tenant Override System
```
tenant_config_overrides     — (tenant_id, config_type, config_key, override_json)
```
- `config_type`: enum of 'environment', 'nutrients', 'alerts', 'retention', 'tasks'
- `config_key`: identifies what's overridden (e.g. "grow_type:cannabis-indoor:stage:veg:environment")
- `override_json`: partial JSON merged over the global default at query time
- Query pattern: `SELECT global + COALESCE(tenant_override)` with JSON merge

### Table Design (Phase 2 — MED/LOW priority)

```
nutrient_guides             — DIY recipes, pH management, emergency subs (category, title, content_json)
feed_charts                 — Brand feeding schedules (brand, product_line, week, nutrients_json)
companion_plants            — Planting compatibility (plant_a, plant_b, relationship, notes)
alert_rule_templates        — Default alert rules (sensor_type, grow_type, thresholds_json, severity)
esphome_templates           — Device templates (kit_name, board, sensors_json, yaml_template)
system_config               — Simple key-value admin config (key, value, description, overridable)
```

Existing tables already migrated (just remove hardcoded source):
- `nutrient_products` (from nutrient_sync.py)
- `reference_strains` (from strain_sync.py)
- `kb_categories` / `kb_articles` (from kb_seed.py)

### Admin API Pattern
```
GET    /v1/admin/config/{type}              — List all configs of type
GET    /v1/admin/config/{type}/{id}         — Get specific config
POST   /v1/admin/config/{type}              — Create new config
PUT    /v1/admin/config/{type}/{id}         — Update config
DELETE /v1/admin/config/{type}/{id}         — Delete config
GET    /v1/admin/config/{type}/export       — Export as JSON (backup)
POST   /v1/admin/config/{type}/import       — Import from JSON (restore)

# Tenant overrides
GET    /v1/tenants/{id}/overrides           — List tenant overrides
PUT    /v1/tenants/{id}/overrides/{type}    — Set tenant override
DELETE /v1/tenants/{id}/overrides/{type}    — Remove override (revert to global)
```

### Migration Strategy
1. Create tables via Alembic migration
2. Seed migration reads existing Python data and INSERTs into new tables
3. Update all consumers to read from DB (with in-memory cache, 5-min TTL)
4. Once verified, remove old Python data files
5. Add admin CRUD endpoints
6. Add frontend admin pages

### Caching
- Global configs cached in-process with 5-minute TTL (invalidated on admin write)
- Tenant overrides cached per-request (already scoped by RLS)
- No Redis caching needed — these are small, rarely-changing datasets

## Risks / Trade-offs
- **Fully normalized = more tables**: 15+ new tables adds DB complexity → mitigate with clear naming and good admin UI
- **Migration data integrity**: Must not lose any of the 44K lines of carefully authored content → seed migration tests with row-count assertions
- **Performance**: DB reads vs in-memory dicts → mitigate with 5-min TTL cache
- **AI context building**: Currently imports dicts directly — needs refactor to async DB reads → already async-capable

## Migration Plan
1. Phase 1A: Create tables + Alembic migrations + seed data (no behavior change yet)
2. Phase 1B: Add service layer that reads from DB with cache
3. Phase 1C: Swap all consumers from hardcoded imports → service layer
4. Phase 1D: Add admin CRUD API endpoints + tests
5. Phase 1E: Add frontend admin pages
6. Phase 1F: Remove deprecated Python data files
7. Phase 2: Repeat for MED/LOW priority items

## Resolved Questions
- **JSONB vs normalized?** → Fully normalized (user chose this)
- **Admin UI?** → Full stack: API first, tests, then frontend
- **Tenant overrides?** → Yes, with inheritance (global defaults + tenant merge)
- **AI tool schemas?** → Keep as code (functional, not data)
- **Phasing?** → HIGH first (grow configs, treatments, task templates), then MED/LOW
