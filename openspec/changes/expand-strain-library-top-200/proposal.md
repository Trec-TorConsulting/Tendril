# Change: Expand the Strain Library to the Top ~200 Strains

## Why
The global strain reference library — the AI's authoritative source of truth for
strain facts — currently holds only **21** curated strains. Growers cultivate far more
than 21 varieties, so most real grows reference a strain the library does not know,
forcing the AI to fall back on unsourced model knowledge. Expanding the library to the
**~200 most-popular strains**, each with verified, source-attributed data, makes
strain-specific guidance accurate and trustworthy for the large majority of grows.

The enrichment infrastructure already exists — migration `0054`, the `SEED_STRAINS`
dataset + idempotent `sync_seed_strains()`, AI resolution in
`api/app/ai/gather.py:_resolve_strain_profile`, prompt rendering in
`api/app/ai/context.py:_fmt_strain_profile`, and the reference API/UI. This change is
primarily a **curated-data expansion** on that foundation, plus the confidence
signalling, quality gates, and discoverability needed for a ~10x larger dataset.

## What Changes
- Expand `SEED_STRAINS` from 21 toward a **target of ~200** entries, expressed as a
  **range, not a hard number**: a firm floor of **150** verified strains, a target of
  **~200**, and **no upper cap** — add as many strains as can be responsibly, verifiably
  sourced. Every entry carries the full, verified profile: `strain_type` + indica/sativa
  split, THC/CBD typical value **and** min/max range, dominant terpenes, effects, flavors,
  flowering weeks, indoor/outdoor yield, `description`, and per-strain `sources` +
  `last_verified`.
- Define and apply an explicit **"top 200" selection methodology** (popularity-ranked,
  alias-deduped, with deliberate coverage of indica / sativa / hybrid, high-CBD,
  autoflower, and landrace strains). The ranked list is produced and **reviewed before**
  bulk data entry.
- Deliver the data in **vetted batches (~25–30 strains each)**; every batch MUST pass the
  automated data-quality gate before the next begins.
- Add explicit **confidence signalling** — a nullable `data_confidence`
  (`high` | `medium` | `low`) column — so entries with thin or conflicting public data
  are marked honestly rather than presented with false certainty.
- **Truthfulness rule (hard constraint):** never fabricate lab-precise figures. Use
  typical ranges aggregated from reputable sources, cite them per strain, and flag
  uncertainty with `data_confidence`. Unknown genetics/breeders are recorded as
  `"Unknown"`, not guessed.
- Enforce **data-quality invariants** with automated tests over every entry (required
  fields present, range/ratio/flowering consistency, sane bounds, unique canonical names,
  non-empty terpenes/effects/flavors/sources, confidence set).
- Add **browse-at-scale** discoverability: the reference API and UI SHALL let users
  list/browse the library without a search query (paginated), since search-only UX does
  not scale to ~200 entries.

## Impact
- Affected specs:
  - `strain-library` (**NEW** capability — formalizes the curated global strain library
    and its role as the AI's strain source of truth)
- Affected code (expected):
  - `api/app/reference/strain_sync.py` — the ~200-entry `SEED_STRAINS` dataset (bulk of the work)
  - `api/app/grows/models.py` + new migration `0055_strain_data_confidence.py` — add `data_confidence`
  - `api/app/reference/routes.py` — expose `data_confidence`; add an unfiltered paginated list endpoint
  - `api/app/reference/service.py` — browse/list query helper
  - `api/app/ai/gather.py`, `api/app/ai/context.py` — surface `data_confidence` in the AI profile
  - `web/src/lib/api-types.ts` (regenerate via `npm run gen:types`), `web/src/lib/api.ts`,
    `web/src/components/reference-search.tsx`, `web/src/app/dashboard/reference/page.tsx` — browse + confidence badge
  - `api/tests/unit/test_ai_gather_strain.py` (+ `test_reference.py`) — full-dataset quality gate
- **Non-goals:** changing the enrichment schema beyond `data_confidence`; auto-vs-photoperiod
  flowering-type AI logic; any change to the tenant-scoped custom `Strain` table.
