# Tasks: Add Mother Plant Keeping and Cloning Spaces

## 1. Data model & migrations
- [ ] 1.1 Add `purpose: Mapped[str]` (`String(20)`, default `"production"`, server_default) to `Tent` in `api/app/grows/models.py`
- [ ] 1.2 Add `purpose: Mapped[str]` (`String(20)`, default `"production"`, server_default) to `GrowCycle`
- [ ] 1.3 Add `mother_bucket_id`, `source_clone_record_id` (nullable UUID FKs) and `clone_status` (nullable `String(20)`) to `Bucket`; extend the documented `role` values to `site | header | mother | clone_site`
- [ ] 1.4 Add `CloneRecord` model (`clone_records` table) with fields from design.md (tenant_id, mother_bucket_id, strain_id, cloning_grow_id, clone_site_bucket_id, method, status, cut_at, rooted_at, root_dev_pct, transplanted_at, dest_bucket_id, notes, created_at) and relationships
- [ ] 1.5 Write one additive Alembic migration in `api/migrations/` adding the two `purpose` columns, three `buckets` columns, the `clone_records` table, FKs, and indexes (`clone_records` on tenant_id/mother_bucket_id/cloning_grow_id/strain_id; `buckets` on mother_bucket_id)
- [ ] 1.6 Enable Row-Level Security + tenant policy on `clone_records` matching existing tenant-scoped tables
- [ ] 1.7 Implement `downgrade()` that drops the table and added columns cleanly; verify upgrade→downgrade→upgrade round-trip locally

## 2. Cloning grow type
- [ ] 2.1 Add a `cloning` entry to `GROW_TYPE_PROFILES` in `api/app/grows/grow_types.py` (category `propagation`, propagation terminology, relevant/primary sensors: ambient_humidity, water_temp/soil_temp, mist_pressure, plus root development; ph/ec ranges for clone solution; automations; `ai_prompt_context`)
- [ ] 2.2 Create `api/app/grows/grow_type_configs/cloning.py` exporting `CLONING_CONFIG` with propagation stages (cutting/sticking → callus → rooting → hardening → ready-to-transplant), per-stage environment targets (high RH, low PPFD), tasks, health checks, common problems, and transition signals
- [ ] 2.3 Register `cloning` in `GROW_TYPE_CONFIGS` in `api/app/grows/grow_type_configs/__init__.py`
- [ ] 2.4 Verify `config_management/seed.py` upserts the new profile; run the seed and confirm `GET /v1/grow-types` and `/v1/grow-types/cloning/config` return it
- [ ] 2.5 Ensure enhancements (`apply_enhancements`) either apply cleanly to `cloning` or are appropriately skipped for the propagation category

## 3. Clone kit catalog
- [ ] 3.1 Create `api/app/grows/clone_kits.py` with the `CLONE_KIT_PRESETS` constant (top-10 kits + `custom`), each with id, name, brand, method, site_count, sensor_kit, default_media, notes
- [ ] 3.2 Add `GET /v1/clone-kits` read-only endpoint returning the catalog

## 4. Mother keeping playbook
- [ ] 4.1 Create `api/app/grows/mother_keeping.py` exposing `MOTHER_KEEPING_PLAYBOOK` (perpetual veg environment targets, maintenance nutrition schedule referencing existing veg/clone reference products, recurring tasks: light topping, IPM scouting, re-pot/root-prune, sanitation)
- [ ] 4.2 Enforce in the stage-transition logic that `purpose = mother` grows cannot advance to `flowering`
- [ ] 4.3 Ensure feeding-advice and alert-threshold logic select veg ranges perpetually when `grow.purpose = mother`
- [ ] 4.4 Exclude `purpose ∈ {mother, clone}` grows from harvest/yield rollups and lifecycle "completion" logic

## 5. Purpose plumbing (tents & grows)
- [ ] 5.1 Add `purpose` to `TentCreate`/`TentUpdate`/`TentResponse` in `api/app/grows/tent_routes.py` with validation (`production|mother|clone`)
- [ ] 5.2 Add `purpose` to the grow create/update/response models in `api/app/grows/grow_routes.py`, defaulting from the tent's purpose when omitted
- [ ] 5.3 Add purpose filtering to the grows and tents list endpoints

## 6. Clone workflow API (`api/app/grows/clone_routes.py`)
- [ ] 6.1 Cloning-grow creation path (or extension) that, given a clone-kit selection, auto-creates `site_count` `clone_site` buckets with `clone_status = empty`
- [ ] 6.2 Clone record CRUD (create, get, list by grow/mother/strain, update status, delete) with Pydantic models and tenant scoping
- [ ] 6.3 `POST /v1/grows/{mother_grow_id}/buckets/{mother_bucket_id}/take-clones` — validate mother vigor, create N clone records, occupy available sites (`rooting`), reject/clamp when sites insufficient, journal the mother
- [ ] 6.4 `POST /v1/grows/{dest_grow_id}/promote-clone` — atomic promotion (create dest bucket `planting_method=clone` + lineage, set record `transplanted`, free clone site, journal both sides); guard unrooted/failed/transplanted and invalid destination
- [ ] 6.5 `PATCH` endpoints to mark a clone `rooted`/`failed` and set `root_dev_pct`
- [ ] 6.6 Register the new router in the grows package/app router
- [ ] 6.7 Apply `require_permission()`/role guards (editor for mutations, viewer for reads) and grow-scoped access checks

## 7. Lineage & analytics API
- [ ] 7.1 `GET /v1/plants/{bucket_id}/lineage` returning ancestors (source clone record, mother, mother origin) and descendants (clones, promoted plants); include compliance plant tag only if the column/data exists
- [ ] 7.2 `GET /v1/mothers/{bucket_id}/analytics` and `GET /v1/propagation/analytics?strain_id=` returning success rate and average days-to-root from `clone_records`
- [ ] 7.3 Guard lineage code so it degrades gracefully when seed-to-sale plant tags are absent

## 8. AI & coaching integration
- [ ] 8.1 Inject mother/clone purpose and playbook context into AI health-check and chat prompt assembly in `api/app/ai/`
- [ ] 8.2 Add clone/mother troubleshooting knowledge (damping-off, failure to root, mother stress) to the AI knowledge/treatment layer
- [ ] 8.3 Ensure coach tips and alerts for mother/clone grows follow the cannabis-first quality philosophy (no flower flip, low-stress, high-RH rooting)

## 9. Web UI (`web/src/`)
- [ ] 9.1 Regenerate `web/src/lib/api-types.ts` from the updated OpenAPI schema; add/extend hand-written interfaces in `web/src/lib/api.ts` (`purpose`, bucket lineage/clone fields, `CloneRecord`, clone-kit types) and API client functions
- [ ] 9.2 Add a purpose selector (Production / Mother / Clone) to the tent form (`web/src/app/dashboard/tents/page.tsx`) and grow-create dialog (`web/src/app/dashboard/grows/page.tsx`), with purpose badges + filters on both lists
- [ ] 9.3 Add a cloning-grow creation wizard with a clone-kit picker (auto-site-count preview + custom count)
- [ ] 9.4 Add a clone-site board view (grid of sites with status) reusing bucket rendering; support mark-rooted/mark-failed and per-site notes/photos
- [ ] 9.5 Add the "take clones" flow on a mother's detail view and the "promote clone" flow from a rooted site into a destination grow (grow/tent picker)
- [ ] 9.6 Add mother registry view (list of mothers with vigor + clone-take history) and a lineage view (mother → clones → plants)
- [ ] 9.7 Add propagation analytics UI (per-mother and per-strain success rate, days-to-root)
- [ ] 9.8 Add cloning terminology map to `web/src/lib/terminology.ts` (Cutting / Site / Dome)

## 10. Tests
- [ ] 10.1 API unit tests: purpose defaulting/validation on tents & grows; mother flower-flip rejection; perpetual-grow exclusion from yield rollups
- [ ] 10.2 API unit tests: cloning grow type profile/config seeding and endpoints; clone-kit catalog
- [ ] 10.3 API unit tests: take-clones (happy path, insufficient sites, vigor caution), clone record lifecycle (rooting→rooted→failed→transplanted)
- [ ] 10.4 API unit tests: promote-clone atomicity, guards (unrooted/failed/cross-tenant/self), lineage + site freeing
- [ ] 10.5 API unit tests: lineage endpoint with and without compliance tags; propagation analytics math (success rate, days-to-root)
- [ ] 10.6 API tests: RBAC/role guards and grow-scoped access on all new endpoints; RLS isolation for `clone_records`
- [ ] 10.7 Migration test: additive upgrade preserves existing rows; downgrade round-trip
- [ ] 10.8 Web tests (Vitest): purpose selector/badges, kit picker site generation, take/promote flows; update any affected snapshots
- [ ] 10.9 Web e2e (Playwright): create mother space → take clones → mark rooted → promote into a 4x4 grow → verify lineage

## 11. Docs & validation
- [ ] 11.1 Update relevant docs (e.g., `docs/` grow/space guide) to describe mother keeping and cloning spaces
- [ ] 11.2 Ensure OpenAPI docs cover all new endpoints
- [ ] 11.3 Run `ruff`, `black`, `eslint`, `prettier`, type checks, and the full API/web test suites — all green
- [ ] 11.4 Run `openspec validate add-mothers-and-cloning --strict --no-interactive` and resolve any issues
