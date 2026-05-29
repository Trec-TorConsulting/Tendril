## Context
DWC is Tendril's most mature grow type config (1262 lines) but targets hobby-scale single-bucket setups. This design establishes the comprehensive config architecture that all 12 grow types will follow.

### Current Architecture
- `grow_types.py` — 12 profile definitions (terminology, sensors, pH/EC ranges, health checks, AI context)
- `grow_type_configs/{type}.py` — Full stage-by-stage configs (only DWC + Kratky exist)
- `grow_type_configs/__init__.py` — Registry: `GROW_TYPE_CONFIGS` dict + `get_grow_type_config()`
- API: `GET /v1/grow-types/{id}/config` returns full config or 404
- AI: `context.py` uses profiles for terminology + `ai_prompt_context` string

### Constraints
- Config files are pure Python dicts (no ORM) — served directly as JSON
- Must remain backwards-compatible (existing clients use current shape)
- Configs must work offline (PWA caches them)
- Commercial features gated by tenant plan

## Goals / Non-Goals
- **Goals**: DWC config accurate from 1 plant to 100+ bucket commercial operation; autoflower + photoperiod support; water source handling; advanced technique guidance; automation-ready thresholds; commercial compliance hooks
- **Non-Goals**: UI changes (separate phase); changing the config file format to a database (configs stay as Python dicts); implementing actual Metrc/seed-to-sale integration (just the field hooks)

## Decisions

### 1. Scale tiers as nested config sections (not separate files)
Each config file contains a `scale_tiers` section. The API accepts `?scale=` query param and returns the base config + scale-specific overrides merged.
- **Why**: Keeps one source of truth per grow type. Scale differences are incremental (commercial adds batch tracking, labor scheduling) not fundamental rewrites.
- **Alternative**: Separate files per scale (e.g., `dwc_commercial.py`) — rejected because 90% of content would be duplicated.

### 2. Strain type (auto vs photo) as stage duration overrides
Each stage gets `duration_days_auto` and `duration_days_photo` fields alongside the existing `duration_days`. The API accepts `?strain_type=auto|photo` to return the appropriate durations.
- **Why**: Autoflowers have shorter, fixed veg periods and don't respond to light schedule changes. But the stages themselves (germination, veg, flower, etc.) are the same.
- **Alternative**: Separate stage lists for auto vs photo — rejected because stages are identical, only durations and a few notes differ.

### 3. Monitoring thresholds as a separate config section
New `thresholds` section in each config with `info`, `warning`, `alert`, `critical` tiers per sensor. Exposed via `GET /v1/grow-types/{id}/thresholds`.
- **Why**: Automation rules need numeric thresholds, not just "target ranges." Separating thresholds from stage-by-stage data lets the automation engine consume them independently.
- **Alternative**: Embed thresholds in each stage's environment/reservoir section — rejected because automation rules need type-level thresholds, not stage-specific ones (stage-specific targets already exist).

### 4. Nutrient brand alternatives as a mapping table
New `nutrient_alternatives` section maps the current GH Flora Trio formulas to equivalent dosing for popular alternatives (Jack's 321, Athena, Advanced Nutrients, etc.).
- **Why**: Many growers don't use GH Flora Trio. Providing conversion tables makes the config useful regardless of nutrient line.
- **Alternative**: Only support one nutrient brand — rejected because it limits the app's utility.

## Risks / Trade-offs
- **Config file size**: DWC config will grow from ~1200 to ~2500+ lines. Acceptable — it's reference data, not business logic.
- **Maintenance burden**: 12 types × comprehensive configs = large data surface. Mitigated by establishing clear structure and tests that validate completeness.
- **Domain accuracy**: Growing advice must be correct. Mitigated by sourcing from established references (GWE, manufacturer charts) and noting sources in comments.

## Migration Plan
- No migration needed — all additions are backwards-compatible
- Existing `DWC_CONFIG` export dict gains new keys; no existing keys change
- API adds optional query params; existing calls without params return same response

## Open Questions
- Should nutrient brand alternatives be a separate API endpoint or embedded in the config? (Decision: embedded, with option to extract later)
- Should commercial compliance fields require commercial plan to view? (Decision: visible to all, but compliance tracking features require commercial plan)
