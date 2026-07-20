# strain-library

## ADDED Requirements

### Requirement: Curated Top-Strain Reference Library
The system SHALL maintain a curated global reference library of the most-popular cannabis
strains, sized as a range rather than a fixed count: no fewer than 150 verified strains,
targeting approximately 200, with no upper cap — as many strains as can be responsibly and
verifiably sourced SHALL be included. Strains SHALL be selected by aggregated popularity and
de-duplicated by canonical name (aliases merged). The library SHALL deliberately include
representation across indica-, sativa-, and hybrid-dominant strains, high-CBD/therapeutic
strains, at least one CBG cultivar, popular autoflowering strains, and landrace strains.

#### Scenario: Library meets the floor and targets ~200
- **WHEN** the reference library seed data is loaded
- **THEN** it contains at least 150 distinct verified strains (target ≈200, no upper bound)
- **AND** it includes at least one high-CBD, one autoflower, and one landrace strain

#### Scenario: Aliases are de-duplicated
- **WHEN** a strain is known by multiple names (e.g. "Original Glue" and "Gorilla Glue #4")
- **THEN** it appears exactly once under a single canonical name

### Requirement: Complete Per-Strain Profile
Every strain in the library SHALL carry a complete profile: canonical name, breeder,
genetics/lineage, `strain_type`, indica/sativa percentage split, typical THC and CBD
values with min/max ranges, dominant terpenes, effects, flavors, flowering-time range in
weeks, indoor and outdoor yield estimates, a description, source attribution, and a
confidence signal.

#### Scenario: No strain ships with missing fields
- **WHEN** the data-quality suite runs over the seed dataset
- **THEN** every strain has all required fields populated (none null/empty)
- **AND** `indica_pct + sativa_pct` equals 100 for each strain

### Requirement: Truthful Cannabinoid Ranges
The system SHALL store cannabinoid content as a typical value plus a commonly-observed
min/max range, and SHALL NOT present a single value as an exact measurement. The system
SHALL NOT fabricate lab-precise figures or invent genetics/breeder attribution; unknown
provenance SHALL be recorded explicitly (e.g. "Unknown").

#### Scenario: Ranges are internally consistent
- **WHEN** a strain's cannabinoid data is validated
- **THEN** `thc_min <= thc_pct <= thc_max` and `cbd_min <= cbd_pct <= cbd_max`
- **AND** all percentages fall within sane bounds (THC ≤ 35%, CBD ≤ 25%)

#### Scenario: Unknown provenance is explicit
- **WHEN** a strain's breeder or genetics cannot be reliably sourced
- **THEN** the field records "Unknown" rather than a guessed value

### Requirement: Source Provenance and Verification Date
Every strain SHALL record the sources its values were cross-referenced against and the
date the entry was last verified, so the data is auditable.

#### Scenario: Provenance present on every entry
- **WHEN** the data-quality suite runs
- **THEN** each strain has a non-empty `sources` list and a `last_verified` date

### Requirement: Data Confidence Signalling
Each strain SHALL carry a `data_confidence` signal of `high`, `medium`, or `low`
reflecting how well its values are corroborated, so thin or conflicting data is disclosed
rather than presented with false certainty. Low-confidence entries SHALL still be ranged
and sourced — never fabricated.

#### Scenario: Confidence is set and valid
- **WHEN** the data-quality suite runs
- **THEN** every strain's `data_confidence` is one of `high`, `medium`, or `low`

#### Scenario: Low confidence is surfaced
- **WHEN** a strain with `data_confidence = "low"` is shown in the reference UI or included
  in an AI prompt
- **THEN** the low-confidence status is indicated to the user/model

### Requirement: Strain Library as AI Source of Truth
When an AI prompt needs information about a strain being grown, the system SHALL resolve
that strain's profile from the strain library (tenant/global custom strains first, then
the global reference library) and present it as the authoritative source, preferring it
over the model's general knowledge. When a strain is unknown to the library, the system
SHALL omit a fabricated profile.

#### Scenario: Known strain grounds the prompt
- **WHEN** a bucket references a strain present in the library (by link or by name)
- **THEN** the assembled AI context includes that strain's library profile marked as
  authoritative

#### Scenario: Unknown strain is not fabricated
- **WHEN** a bucket references a strain not present in the library
- **THEN** no strain profile is injected into the prompt

### Requirement: Automated Data-Quality Enforcement
The system SHALL enforce the library's structural invariants with automated tests that run
over every entry, so a malformed or incomplete strain fails CI rather than shipping.

#### Scenario: Invariants block bad data
- **WHEN** an entry violates an invariant (missing field, inconsistent range, ratio not
  summing to 100, duplicate name, empty terpenes/effects/flavors/sources, or invalid
  confidence)
- **THEN** the data-quality test suite fails

#### Scenario: Count floor enforced
- **WHEN** the data-quality suite runs
- **THEN** it asserts the library contains at least the agreed floor (≥150 strains), not an exact count

### Requirement: Browse and Search at Scale
The reference API and UI SHALL let users both search the library by name/breeder/genetics
and browse the full library without entering a query, using pagination so the ~200-entry
list remains usable.

#### Scenario: Browse without a query
- **WHEN** a user opens the reference library without typing a search term
- **THEN** the system returns a paginated list of strains

#### Scenario: Search by name still works
- **WHEN** a user types at least two characters
- **THEN** the system returns strains whose name, breeder, or genetics match
