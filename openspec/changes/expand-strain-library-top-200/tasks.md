# Implementation Tasks — Expand the Strain Library to the Top ~200 Strains

> Truthfulness is a hard gate on every task: use typical ranges, cite real `sources` per
> strain, set `data_confidence` honestly, and **never fabricate** figures or genetics.
> The existing 21 strains already in `SEED_STRAINS` do **not** get re-entered — extend the list.

## 1. Selection & methodology (GATE — review before data entry)
- [ ] 1.1 Compile a popularity-ranked candidate list from major public databases
      (Leafly, Weedmaps, AllBud, seed-bank best-sellers). The count is a **range, not a hard
      number**: floor 150, target ~200, no upper cap — capture as many as can be verified,
      including the existing 21.
- [ ] 1.2 Canonicalize names and de-duplicate aliases (e.g. `Original Glue`→`Gorilla Glue #4`,
      `GSC`→`Girl Scout Cookies`); remove any already present in `SEED_STRAINS`.
- [ ] 1.3 Apply category quotas for breadth: mainstream hybrids, OG/Kush, haze/diesel sativas,
      cookies/gelato/runtz lineage, dessert/fruity, **high-CBD/therapeutic** (ACDC,
      Charlotte's Web, Harlequin, Cannatonic…), ≥1 **CBG** cultivar, popular **autoflowers**,
      and **landraces** (Durban Poison, Hindu Kush, Afghani, Acapulco Gold).
- [ ] 1.4 Record the final ranked+categorized list in this change folder (e.g. `research/top-200.md`)
      and get it reviewed/approved before Section 3.

## 2. Schema — data confidence
- [ ] 2.1 Add nullable `data_confidence: Mapped[str | None]` (`high`|`medium`|`low`) to
      `ReferenceStrain` in `api/app/grows/models.py`.
- [ ] 2.2 Create migration `api/migrations/versions/0055_strain_data_confidence.py`
      (`down_revision = "0054"`); additive nullable column; backfill existing rows to `'high'`;
      reversible `drop_column` downgrade.
- [ ] 2.3 Set `data_confidence` on every `SEED_STRAINS` entry (existing 21 → `high`); update
      `sync_seed_strains()` if it needs to write the field (it uses `**strain_data`, so a dict
      key suffices).

## 3. Data entry — vetted batches (each batch: research → fill → validate → review)
Deliver in batches of ~25–30. After **each** batch, run Section 7 gates and stop for review
before starting the next. Batch themes are guides; the authoritative members come from Task 1.4.
- [ ] 3.1 Batch A (~25): remaining top mainstream (e.g. Durban Poison, Pineapple Express,
      Trainwreck, Cheese, Amnesia Haze, Super Silver Haze, GG-adjacent, Chemdawg…).
- [ ] 3.2 Batch B (~25): OG/Kush family (Bubba Kush, Master Kush, Hindu Kush, Skywalker OG,
      Fire OG, SFV OG, Death Star…).
- [ ] 3.3 Batch C (~25): cookies/gelato/runtz & modern hype (Sunset Sherbet, Biscotti,
      Cereal Milk, Apple Fritter, Jealousy, Gary Payton…).
- [ ] 3.4 Batch D (~25): haze/diesel/sativa (Green Crack-adjacent, Maui Wowie, Ghost Train
      Haze, Strawberry Cough, Tangie, Lemon Haze…).
- [ ] 3.5 Batch E (~25): dessert/fruity (Sherbet, Zkittlez-adjacent, Grape Ape, Blueberry,
      Strawberry Banana, Papaya, Forbidden Fruit…).
- [ ] 3.6 Batch F (~25): high-CBD/therapeutic + CBG (ACDC, Charlotte's Web, Harlequin,
      Cannatonic, Ringo's Gift, CBD Critical Mass, Sour Tsunami, White CBG…) — expect wider
      `cbd_min/max`; some `medium`/`low` confidence.
- [ ] 3.7 Batch G (~25): autoflowers + landraces (Northern Lights Auto, Gorilla Glue Auto,
      Blackberry Auto…; Afghani, Acapulco Gold, Panama Red, Malawi, Thai, Colombian Gold…).
- [ ] 3.8 Each entry MUST include: `name`, `breeder`, `genetics`, `strain_type`, `indica_pct`,
      `sativa_pct`, `thc_pct/min/max`, `cbd_pct/min/max`, `terpenes`, `effects`, `flavors`,
      `flowering_min/max_weeks`, `yield_indoor`, `yield_outdoor`, `description`, `sources`,
      `data_confidence`. Use hyphens (not en dashes) in strings to satisfy ruff `RUF001/RUF002`.

## 4. API & service
- [ ] 4.1 Add `data_confidence` to `ReferenceStrainResponse` in `api/app/reference/routes.py`.
- [ ] 4.2 Add a paginated browse/list endpoint (e.g. `GET /v1/reference/strains/all` or a
      no-query mode) using `PaginationParams`/`PaginatedResponse`; add the query helper in
      `api/app/reference/service.py`.
- [ ] 4.3 Keep the existing `ilike` autocomplete search working unchanged.

## 5. AI surface
- [ ] 5.1 Map `data_confidence` into the profile in `api/app/ai/gather.py:_reference_to_profile`.
- [ ] 5.2 In `api/app/ai/context.py:_fmt_strain_profile`, render a short confidence note when
      `data_confidence == "low"` so the model hedges appropriately.

## 6. Web
- [ ] 6.1 `cd web && npm run gen:types`; commit the `web/src/lib/api-types.ts` diff.
- [ ] 6.2 Add browse-all UI to `web/src/app/dashboard/reference/page.tsx` (list without typing a query).
- [ ] 6.3 Show a `data_confidence` badge on strain cards (e.g. amber for `low`).
- [ ] 6.4 `npx tsc --noEmit` and `npm run lint` clean.

## 7. Quality gates & tests
- [ ] 7.1 Extend `api/tests/unit/test_ai_gather_strain.py` invariants to run over **every**
      `SEED_STRAINS` entry: required keys present; `indica_pct + sativa_pct == 100`;
      `thc_min <= thc_pct <= thc_max`; `cbd_min <= cbd_pct <= cbd_max`; sane bounds
      (0 ≤ THC ≤ 35, 0 ≤ CBD ≤ 25, 5 ≤ flowering weeks ≤ 16, `min <= max`); non-empty
      `terpenes`/`effects`/`flavors`/`sources`; `data_confidence in {high,medium,low}`.
- [ ] 7.2 Add a uniqueness test: no duplicate canonical `name`s (alias collisions).
- [ ] 7.3 Add a count-floor test asserting a **minimum** (range floor), not an exact count:
      `len(SEED_STRAINS) >= 150` (target ~200+, no upper bound — more verified strains is better).
- [ ] 7.4 Add a `sync_seed_strains` persistence test asserting a new sample strain round-trips
      with `data_confidence` + `last_verified`.
- [ ] 7.5 Run `ruff check --config api/pyproject.toml api/` and the full `pytest` suite green.
      **Run only ONE full `pytest tests` at a time** — concurrent runs deadlock on the shared
      `tendril_test` DB (`_setup_db` drop/create + `_clean_tables` TRUNCATE CASCADE).

## 8. Docs
- [ ] 8.1 Note the expanded library + `data_confidence` semantics in `docs/` (e.g. the AI
      operations / reference docs) if strain data is documented there.
- [ ] 8.2 On completion, set every task above to `- [x]` and archive per `openspec/AGENTS.md`.
