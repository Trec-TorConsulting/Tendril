# Design: Mother Plant Keeping and Cloning Spaces

## Context
Tendril models cultivation as `Tenant → Tent (grow space) → GrowCycle (a grow) → Bucket (a plant
site)`. Grow behavior is driven by `GrowCycle.grow_type`, which resolves to a DB-backed
`grow_type_profiles` row seeded from `api/app/grows/grow_types.py` (`GROW_TYPE_PROFILES`) and
`api/app/grows/grow_type_configs/*` (`GROW_TYPE_CONFIGS`). Buckets already carry a `role`
(`site` | `header`), a `planting_method` (`direct_seed` | `transplant` | `clone`), and a free-form
`settings` JSON. There is **no** cross-grow move/transplant API today — only a `transplant`
journal event type.

A separate, not-yet-implemented change (`add-seed-to-sale`) introduces regulated plant tags and
adds a `plant_tag_id` column to `Bucket` (it MODIFIES the `bucket-monitoring` "Bucket CRUD"
requirement). This change must avoid colliding with that work.

Constraints:
- Must remain self-hostable (no new external services).
- Enterprise-grade: full CRUD, tests, migrations with rollback, OWASP compliance, RLS/tenant
  isolation on every new table and endpoint.
- Cannabis-first quality philosophy applies to all AI/alert output.

## Goals / Non-Goals
**Goals**
- Model mother-plant keeping as a perpetual-veg mode on any medium.
- Add a dedicated `cloning` grow type with real clone-kit presets and per-site rooting tracking.
- Support promoting a rooted clone into a production grow in a different tent, preserving lineage.
- Provide lightweight lineage (mother → clone → plant) for all growers, forward-compatible with
  seed-to-sale plant tags.

**Non-Goals**
- Regulated METRC/seed-to-sale plant tagging (owned by `add-seed-to-sale`).
- Tissue culture / micropropagation workflows.
- Automated dome/mister hardware control loops (only monitoring + reminders here).
- Genetic phenotype hunting / pheno-selection scoring (future).

## Decisions

### Decision 1: Purpose is a field on both Tent and GrowCycle
Add `purpose ∈ {production, mother, clone}` (default `production`) to **both** `Tent` (space
designation / default) and `GrowCycle` (authoritative, drives behavior). A tent tagged `mother` is
a hint that pre-selects the purpose when creating a grow; the grow's `purpose` is what the engine,
alerts, and AI read.
- **Why not a dedicated `mother_plant` grow type?** Mothers live in many media (soil, coco, DWC).
  Purpose is an orthogonal overlay on the existing medium grow types, so a field composes cleanly
  where a new grow type would force one fixed medium.
- **Why not tent-only?** A single tent can, over time, host grows of different purposes; behavior
  must bind to the grow, not the physical space.

### Decision 2: Cloning IS a new grow type; mothers are NOT
Cloning is a genuinely distinct *method* (bare-root aeroponic mist or media plugs under a dome)
with its own sensors (dome RH, misting cycle, root development), stages, and health checks — so it
is added as a first-class `cloning` grow type via the existing profile/config seed path. Mother
keeping reuses the plant's chosen medium grow type and only overlays a *playbook* selected by
`purpose = mother`.

### Decision 3: Overload `Bucket` for mothers and clone sites (Option A)
A **mother** is a `Bucket` with `role = mother` in a `purpose = mother` grow. A **clone site** is a
`Bucket` with `role = clone_site` in a `purpose = clone` (`grow_type = cloning`) grow. This reuses
all existing bucket infrastructure (sensors, journal, photos, field canvas, detail modal) and
matches the user's mental model: *"take the site in the clone and move it to a grow."*
- Extend `Bucket.role` allowed values: `site | header | mother | clone_site`.
- Add nullable lineage FKs: `Bucket.mother_bucket_id → buckets.id`,
  `Bucket.source_clone_record_id → clone_records.id`.
- Add `Bucket.clone_status ∈ {empty, occupied, rooting, rooted, failed, transplanted}` (nullable;
  meaningful only for `clone_site`).
- **Alternative considered — dedicated `mother_plants` / `clones` tables**: rejected because it
  duplicates sensor/journal/photo/canvas infrastructure and complicates the promotion flow, for
  little gain.

### Decision 4: A `clone_records` ledger for batches and analytics
Clone sites are reused across many rounds, so per-site columns cannot hold history. Introduce an
append-only `clone_records` table — one row per cutting taken — to hold the analytics/lineage
ledger:

```
clone_records
  id                   uuid pk
  tenant_id            uuid fk tenants(id) on delete cascade    -- RLS
  mother_bucket_id     uuid fk buckets(id) on delete set null    -- source mother
  strain_id            uuid fk strains(id) on delete set null
  cloning_grow_id      uuid fk grow_cycles(id) on delete cascade -- the cloner grow
  clone_site_bucket_id uuid fk buckets(id) on delete set null    -- current site occupancy
  method               varchar(30)      -- aeroponic | bubbler | rockwool | rapid_rooter | soil
  status               varchar(20)      -- rooting | rooted | failed | transplanted
  cut_at               timestamptz
  rooted_at            timestamptz null
  root_dev_pct         float null       -- 0-100 subjective/observed
  transplanted_at      timestamptz null
  dest_bucket_id       uuid fk buckets(id) on delete set null    -- the promoted plant
  notes                text null
  created_at           timestamptz default now()
```

Success rate = `count(status IN (rooted, transplanted)) / count(*)` per mother or per strain;
days-to-root = `avg(rooted_at - cut_at)`. `Bucket.source_clone_record_id` back-links a promoted
plant to its originating cutting for lineage.

### Decision 5: Clone kits are a seeded code constant, not a table
Define `CLONE_KIT_PRESETS` in `api/app/grows/clone_kits.py` (mirroring how `GROW_TYPE_PROFILES` is
a code constant) and surface read-only via `GET /v1/clone-kits`. Each preset: `id`, `name`,
`brand`, `method`, `site_count`, `sensor_kit`, `default_media`, `notes`. Selecting a preset in the
cloning-grow wizard auto-creates `site_count` `clone_site` buckets. No new table; tenants may still
override the generated site count. Seed set (top 10):

| id | name | brand | method | sites |
|----|------|-------|--------|-------|
| clone_king_25 | Clone King 25 | TurboKlone/CK | aeroponic | 25 |
| clone_king_36 | Clone King 36 | Clone King | aeroponic | 36 |
| clone_king_64 | Clone King 64 | Clone King | aeroponic | 64 |
| ez_clone_32 | EZ-Clone Classic 32 | EZ-Clone | aeroponic | 32 |
| ez_clone_64 | EZ-Clone Classic 64 | EZ-Clone | aeroponic | 64 |
| ez_clone_128 | EZ-Clone Pro 128 | EZ-Clone | aeroponic | 128 |
| turboklone_t24 | TurboKlone T24 | TurboKlone | aeroponic | 24 |
| turboklone_t48 | TurboKlone T48 | TurboKlone | aeroponic | 48 |
| bubble_cloner_20 | Bubble Cloner (DWC) 20 | Generic | bubbler | 20 |
| rockwool_tray_72 | Rockwool / Rapid Rooter Tray 72 | Generic | rockwool | 72 |

A `custom` option lets the user set an arbitrary site count and method.

### Decision 6: Promotion is an explicit, atomic API action
`POST /v1/grows/{dest_grow_id}/promote-clone` (body: `clone_record_id`, optional `position`,
`label`, `strain_id`, `volume_gallons`). In one transaction it:
1. Validates the clone record is `rooted` (guard: reject `rooting`/`failed`/`transplanted` unless
   `force=true`) and that the destination grow belongs to the same tenant and is not the cloner.
2. Creates a new `Bucket` in `dest_grow_id` with `planting_method = clone`,
   `mother_bucket_id = record.mother_bucket_id`, `source_clone_record_id = record.id`, strain
   inherited from the record (overridable).
3. Sets `clone_records.status = transplanted`, `transplanted_at = now()`,
   `dest_bucket_id = new bucket`.
4. Frees the clone site: `clone_status = empty`, clears the site's `mother_bucket_id`/current
   occupancy so the physical site can be reused.
5. Writes journal entries: a `transplant` event on the new bucket (referencing lineage) and an
   optional `clone_transplanted` event on the mother.
The inverse action, `POST /v1/grows/{mother_grow_id}/buckets/{mother_bucket_id}/take-clones`
(body: `count`, `cloning_grow_id`, `cut_at`, `method`, `notes`), creates `count` `clone_records`,
assigns them to available clone sites (or first-available), sets `clone_status = rooting`, and
journals the mother.

### Decision 7: Mother keeping playbook
`api/app/grows/mother_keeping.py` exposes `MOTHER_KEEPING_PLAYBOOK`: perpetual vegetative targets
(18/6 photoperiod — never flip; veg VPD 0.8–1.2 kPa; temp/RH veg ranges), a **maintenance**
nutrition schedule (reduced-strength balanced veg formula, e.g. EC 0.8–1.2, plus light
root/vitamin support such as the existing Clonex/RapidStart reference products), and recurring
tasks (light topping to keep bushy + generate clone sites, IPM/pest scouting, periodic
re-pot/root-prune, sanitation before taking cuttings). When `grow.purpose = mother`, alerting uses
veg ranges perpetually and the stage machine refuses to advance to `flowering`.

## Risks / Trade-offs
- **Bucket overloading** → clearer than parallel tables but risks `role`-specific branching.
  Mitigation: centralize role/purpose guards in a small service module; exhaustive unit tests per
  role.
- **Collision with `add-seed-to-sale` on `Bucket`** → both add columns and one MODIFIES "Bucket
  CRUD". Mitigation: this change only **ADDS** requirements to `bucket-monitoring` (never modifies
  "Bucket CRUD"); columns are disjoint (`mother_bucket_id`, `source_clone_record_id`,
  `clone_status` vs. `plant_tag_id`); whichever lands first, the other's migration is still
  additive. Lineage endpoints read `plant_tag_id` only if the column exists.
- **Perpetual grows never "complete"** → analytics/lifecycle code that assumes an end date must
  treat `purpose ∈ {mother, clone}` as long-lived. Mitigation: exclude perpetual grows from
  harvest/yield rollups; add explicit filters.
- **Auto-generating 128 sites** (EZ-Clone Pro) → bulk insert + UI virtualization. Mitigation: batch
  insert in one statement; paginate/virtualize the clone board.

## Migration Plan
1. One additive Alembic migration:
   - `ALTER TABLE tents ADD COLUMN purpose varchar(20) NOT NULL DEFAULT 'production'`.
   - `ALTER TABLE grow_cycles ADD COLUMN purpose varchar(20) NOT NULL DEFAULT 'production'`.
   - `ALTER TABLE buckets ADD COLUMN mother_bucket_id uuid NULL REFERENCES buckets(id) ON DELETE SET NULL`,
     `ADD COLUMN source_clone_record_id uuid NULL`, `ADD COLUMN clone_status varchar(20) NULL`.
   - `CREATE TABLE clone_records (...)` with tenant RLS policy mirroring existing tables; add FK
     `buckets.source_clone_record_id → clone_records(id) ON DELETE SET NULL` after table creation.
   - Indexes: `clone_records(tenant_id)`, `(mother_bucket_id)`, `(cloning_grow_id)`,
     `(strain_id)`; `buckets(mother_bucket_id)`.
   - Enable RLS + tenant policy on `clone_records`.
2. Extend `config_management/seed.py` path is automatic once `cloning` is added to
   `GROW_TYPE_PROFILES`/`GROW_TYPE_CONFIGS`; run the seed to upsert the new profile.
3. Rollback: `downgrade()` drops `clone_records`, the three `buckets` columns, and the two
   `purpose` columns; the `cloning` profile row is left in place (harmless) or deleted by slug.
   No data loss for existing grows (all defaults preserve prior behavior).

## Open Questions
- None blocking. Clone-kit list confirmed with the requester (top-10 above). If regulated markets
  later require a mother/clone to carry a plant tag at cut time, that is handled by `add-seed-to-sale`.
