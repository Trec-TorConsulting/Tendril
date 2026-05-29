# Change: Add Strain Database Sync

## Why
Strain genetics data (flowering time, expected yield, THC/CBD ratios, terpene profiles, growth difficulty) helps the AI give strain-specific advice. Instead of users manually entering this data, auto-populate from existing public strain databases when a user selects their strain.

## What Changes
- Lookup service that queries external strain databases
- Auto-populates genetics fields when user selects a strain name
- Enriches AI context with strain-specific growth characteristics
- Provides strain search/autocomplete in grow creation flow

## Impact
- Affected specs: `integrations-framework`
- No breaking changes
- Existing strain field on grows is enhanced, not replaced

## Data Sources (Candidates)
- **Seedfinder.eu** — Largest strain database, searchable, scrape-friendly (check ToS)
- **Open Cannabis Project** — Open data initiative
- **Leafly/Weedmaps** — Commercial APIs (may require partnership)
- **Manual seed bank scraping** — Last resort fallback
- **User-contributed data** — Community-sourced strain data over time

## Fields to Populate
- Flowering time (days), Veg time recommendation (days)
- Indoor/Outdoor/Both, Indica/Sativa/Hybrid percentage
- Expected yield (g/m² indoor, g/plant outdoor)
- THC %, CBD %, terpene profile
- Growth difficulty (easy/medium/hard)
- Nutrient sensitivity, training responsiveness
