# Change: Add Mother Plant Keeping and Cloning Spaces

## Why
Serious growers run a **perpetual cycle**: they keep genetics alive on dedicated **mother
plants** and take **clones (cuttings)** from them to start every new grow. Today Tendril can
only model a linear "grow" (seed/clone → harvest) inside a tent. There is no way to:

- Designate a tent/grow as a **Mother Keeping** space (perpetual veg, maintenance nutrition,
  18/6 light that is never flipped to flower).
- Run a **Cloning / Propagation** space backed by a real clone kit (e.g., Clone King 36,
  EZ-Clone 32, TurboKlone T24) and track each rooting cutting site-by-site.
- **Move a rooted clone site** out of the cloner into a production grow in another tent
  (e.g., a 4x4) while preserving the plant's lineage.

This is the single most-requested cultivation workflow after seed-to-harvest, and it is core to
how every returning grower actually operates. Adding it makes Tendril the system of record for
the *entire* genetic lifecycle, not just one crop cycle — driving retention and making the
platform credible for both hobbyists and commercial operators.

## What Changes
- **Space & grow purpose** — add a `purpose` field to grow spaces (tents) and grows
  (`production` | `mother` | `clone`, default `production`). Purpose drives behavior, UI badges,
  filtering, and AI context. Additive and backward-compatible.
- **Mother Keeping mode** — a perpetual-veg grow mode layered on *any* medium (soil, coco, DWC,
  etc.). Mothers are never advanced to flower, use a maintenance nutrition playbook and a fixed
  vegetative photoperiod, and expose a per-mother **clone-take history** and vigor scoring.
- **New `cloning` grow type** — a first-class grow type with propagation stages
  (stick cutting → callus → rooting → hardening → ready-to-transplant), clone-specific sensors
  (dome humidity, media/water temp, misting cycle, root development), tasks, health checks, and
  terminology (Cutting / Site / Dome).
- **Clone kit presets** — a seeded catalog of the top-10 clone kits (Clone King 25/36/64,
  EZ-Clone 32/64/128, TurboKlone T24/T48, a deep-water bubble cloner, and a rockwool/rapid-rooter
  propagation tray). Selecting a kit when creating a cloning grow **auto-generates its N clone
  sites** and sets the correct sensor/method context.
- **Clone site & batch tracking** — each clone site tracks its source mother, strain, cut date,
  rooting status, root development, and outcome. A new append-only `clone_records` ledger records
  every cutting for success-rate analytics even as sites are reused.
- **Take clones from a mother** — an action that records taking N cuttings from a mother into a
  cloning grow, populating clone sites and linking lineage (mother → clone).
- **Promote a rooted clone into a grow** — move a rooted clone site into a destination grow in any
  tent/medium: it creates a new plant site there (`planting_method = clone`), records lineage
  (mother → clone → plant), frees the clone site, and journals both sides.
- **Plant lineage graph** — lightweight, built-in lineage for all growers (parent mother +
  source clone references on each plant), with ancestor/descendant lookup. Integrates with the
  pending seed-to-sale `plant_tag_id` when compliance is enabled.
- **Propagation analytics** — per-mother and per-strain clone success rate and average
  days-to-root, surfaced in the UI.
- **AI coaching & alerting** — mother/clone purpose is injected into AI context; recommendations,
  alerts, and coach tips follow the cannabis-first quality philosophy (preserve genetics, keep
  mothers low-stress, never flower a mother, high-RH/low-light cloning) and include clone
  troubleshooting.

No breaking changes: all new columns are nullable/defaulted, existing tents and grows default to
`purpose = production`, and the `Bucket.role` enum is extended (not repurposed).

## Impact
- **Affected specs**: new `plant-propagation` capability; `bucket-monitoring` (ADDED requirements
  for mother/clone-site roles and clone promotion).
- **Affected code**:
  - `api/app/grows/models.py` — `purpose` on `Tent` and `GrowCycle`; lineage + clone fields on
    `Bucket`; new `CloneRecord` model.
  - `api/app/grows/grow_types.py` + `api/app/grows/grow_type_configs/cloning.py` (+ `__init__.py`
    registration) — new `cloning` grow type profile & config; picked up automatically by
    `config_management/seed.py`.
  - `api/app/grows/` — new `clone_routes.py` (take-clones, promote-clone, clone-site CRUD,
    clone-kit catalog, lineage, analytics); `tent_routes.py` & `grow_routes.py` gain `purpose`.
  - `api/app/grows/mother_keeping.py` — mother maintenance playbook (nutrition/light/tasks).
  - `api/app/ai/` — mother/clone context injection and clone troubleshooting.
  - `api/migrations/` — one additive Alembic migration (new columns + `clone_records` table).
  - `web/src/` — purpose selector in tent/grow forms; cloning grow wizard with kit picker; clone
    site board; take-clones and promote-clone flows; mother registry & lineage views;
    `web/src/lib/terminology.ts` cloning terms; regenerated `api-types.ts`.
- **New reference data**: `CLONE_KIT_PRESETS` constant (no new table) surfaced via
  `GET /v1/clone-kits`.
- **Billing/plans**: available on all plans (core cultivation).
- **Relationship to `add-seed-to-sale`**: complementary. This change adds lightweight lineage for
  everyone; seed-to-sale layers regulated plant tags on top. Both add orthogonal fields to
  `Bucket`, so they must be reconciled at archive time (see design.md).
