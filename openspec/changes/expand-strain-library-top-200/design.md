# Design — Expand the Strain Library to the Top ~200 Strains

## Context
The curated global strain library (`reference_strains` table, seeded from
`SEED_STRAINS` in `api/app/reference/strain_sync.py`) is the AI's authoritative source
for strain facts. As of this change it holds **21** fully-enriched strains. The schema
and plumbing were completed in a prior change:

- Migration `0054_enrich_reference_strains.py` added `strain_type`, `indica_pct`,
  `sativa_pct`, `thc_min/max`, `cbd_min/max`, `terpenes`, `effects`, `flavors`,
  `flowering_min/max_weeks`, `yield_indoor/outdoor`, `sources`, `last_verified`.
- `sync_seed_strains()` idempotently upserts `SEED_STRAINS` by name at startup.
- `api/app/ai/gather.py:_resolve_strain_profile` resolves a bucket's strain (by
  `strain_id`, then by name against the tenant/global `Strain` library, then against
  `ReferenceStrain`) and `context.py:_fmt_strain_profile` renders it into prompts under
  `STRAIN_LIBRARY_DIRECTIVE` + `STRAIN_DATA_CAVEAT`.

This change adds **~180 more strains** of the same quality, the honesty controls needed
at that scale, and browse discoverability.

**Hard constraint — truthfulness.** Cannabis potency is inherently variable; there is no
single "correct" THC number. Data MUST be represented as typical ranges, attributed to
real sources, and flagged when uncertain. Fabricating lab-precise figures or inventing
genetics is prohibited.

**Environment reality.** Many cannabis databases are blocked or rate-limited on some
networks (observed: iboss filtering of SeedFinder, plus 404s from Leafly/Wikileaf/
Weedmaps/Hytiva); AllBud loaded reliably. The implementer must expect partial source
access and must **not** fabricate to fill gaps — use cross-referenced consensus and mark
`data_confidence` accordingly.

## Goals / Non-Goals
- **Goals**
  - Grow `SEED_STRAINS` toward ~200 top strains (floor 150, no upper cap) with complete,
    verified, source-attributed profiles.
  - Represent uncertainty honestly (`data_confidence`) and never fabricate.
  - Keep the dataset machine-verifiable (invariant tests) and reviewable (batches).
  - Make a 200-entry library discoverable (browse/paginate, not search-only).
- **Non-Goals**
  - No enrichment-schema changes beyond adding `data_confidence`.
  - No auto-vs-photoperiod AI logic (the `strain_type` free-text detection stays as-is).
  - No changes to the tenant custom `Strain` table or its CRUD.
  - No external live-scraping service; data is curated into `SEED_STRAINS` at author time.

## Decisions

- **D1 — Selection methodology.** The "top ~200" is compiled by aggregating popularity
  signals from major public databases (Leafly most-popular, Weedmaps, AllBud top lists,
  seed-bank best-sellers) and de-duplicating by canonical name (merging aliases, e.g.
  `Gorilla Glue #4` = `Original Glue`, `GSC` = `Girl Scout Cookies`). The ranked list is
  produced in Task 1 and **reviewed before** data entry. Category quotas guarantee
  breadth: mainstream hybrids, OG/Kush, haze/diesel sativas, cookies/gelato/runtz
  lineage, dessert/fruity, **high-CBD/therapeutic** (e.g. ACDC, Charlotte's Web,
  Harlequin, Cannatonic), at least one **CBG** cultivar, popular **autoflowers**, and
  **landraces** (Durban Poison, Hindu Kush, Afghani, Acapulco Gold). The **count is a
  range, not a fixed number** — floor **150**, target **~200**, no upper cap; prioritize
  maximal verifiable coverage over hitting an exact figure.

- **D2 — Ranges, not false precision.** Reaffirms the established model: store `thc_pct`
  / `cbd_pct` as the typical (≈midpoint) value plus `thc_min/max` and `cbd_min/max` as the
  commonly-observed range. UI/AI present the range; the midpoint is for sort/display only.

- **D3 — Add `data_confidence` (`high` | `medium` | `low`).** A small, nullable column is
  the honest way to signal thin/conflicting data at 200-strain scale. `high` = corroborated
  across multiple reputable sources; `medium` = single reputable source or minor conflict;
  `low` = sparse/contested (still ranged + sourced, never fabricated). *Alternative
  considered:* encoding confidence by convention inside `sources`/`description` — rejected
  as unqueryable and untestable. This is the only schema change in scope; it can be
  de-scoped to a convention if the reviewer prefers, at the cost of testability.

- **D4 — Batched delivery with a gate.** Data lands in batches of ~25–30. Each batch must
  pass `ruff` + the invariant tests before the next starts; batches are small enough for
  human spot-review. This bounds blast radius and keeps accuracy high.

- **D5 — Provenance semantics.** `sources` is the list of databases/breeder pages the
  values were cross-referenced against (the basis of the consensus), and `last_verified`
  is the date checked. The shared `STRAIN_DATA_CAVEAT` still communicates general variability.

- **D6 — Autoflower / high-CBD via existing fields.** Autoflowers are represented in
  `strain_type` text (e.g. `"Autoflower — indica-dominant"`) and high-CBD strains via their
  `cbd_min/max` range; no new flags. Deeper auto/photo scheduling logic is a Non-Goal.

- **D7 — Browse/pagination.** Add an endpoint that lists strains without requiring a query
  (reusing `PaginationParams`/`PaginatedResponse`), and a UI "browse all" affordance. The
  existing `ilike` search stays for name/breeder/genetics lookup.

- **D8 — Sourcing hierarchy.** Prefer, in order: breeder/seed-bank official pages →
  lab/COA data where publicly published → major aggregators (Leafly, Wikileaf, AllBud,
  SeedFinder). Cross-reference ≥2 sources for `high` confidence. Where sources are blocked
  or absent, use consensus and drop to `medium`/`low` — **never fabricate**.

## Risks / Trade-offs
- **Accuracy variance across 200 strains** → ranges + `data_confidence` + per-strain
  `sources` + per-batch review; invariant tests catch structural errors.
- **Blocked/again-unavailable sources** → consensus + confidence downgrade; hard no-fabrication rule.
- **Alias/duplicate collisions** (sync upserts by name) → Task 1 canonicalization + a
  uniqueness invariant test on names.
- **Seed table growth** → negligible (~200 rows); `ix_reference_strains_name` already
  exists; `ilike` and paginated list are fine at this size.

## Migration Plan
- Additive migration `0055_strain_data_confidence.py`: add nullable
  `data_confidence VARCHAR` to `reference_strains`; backfill the existing 21 rows to
  `'high'`. Fully reversible (`drop_column` on downgrade). Test DB builds from
  `Base.metadata.create_all`, so the model field is enough for tests.
- OpenAPI contract changes (new field + browse endpoint) → run `npm run gen:types` and
  commit `web/src/lib/api-types.ts` in the same PR (the `Verify API Types` CI gate).

## Open Questions
- **Resolved (2026-07-20):** the count is a **range, not a hard number** — floor **150**,
  target **~200**, no upper cap; capture as many strains as can be responsibly, verifiably
  sourced. The quality-gate floor is **150**.
- Should `data_confidence` also be injected into AI prompts (so the model hedges on
  `low`-confidence strains), or surfaced UI-only? (Recommend: include a short confidence
  note in the profile when `low`.)
- Licensing/attribution posture for aggregated third-party strain data.
