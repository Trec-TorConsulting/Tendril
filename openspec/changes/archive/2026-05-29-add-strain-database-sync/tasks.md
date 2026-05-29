## 1. Data Model
- [x] 1.1 `ReferenceStrain` model (name, breeder, genetics, thc_pct, cbd_pct, description, external_id, synced_at)
- [x] 1.2 `Strain` model — tenant-scoped (name, breeder, genetics, flowering_days, thc_pct, cbd_pct, terpene_profile JSON)
- [x] 1.3 Bucket model has `strain_name` + `strain_id` FK to Strain

## 2. Strain Lookup Service
- [x] 2.1 `reference/strain_sync.py` — seed data with 16+ popular strains (Blue Dream, GSC, OG Kush, etc.)
- [x] 2.2 `GET /v1/reference/strains` — search/autocomplete endpoint
- [x] 2.3 `GET /v1/reference/strains/{id}` — strain detail fetch
- [x] 2.4 Reference strain data cached locally (no external API dependency)

## 3. AI Integration
- [x] 3.1 Strain profile (flowering time, sensitivity) included in AI context
- [x] 3.2 AI adjusts advice based on strain characteristics

## 4. Frontend
- [x] 4.1 `ReferenceStrainSearch` component (reference-search.tsx) — autocomplete in grow/bucket creation
- [x] 4.2 Reference page with strain leaderboard tab
- [x] 4.3 Strain selection in bucket creation (buckets-tab.tsx)
