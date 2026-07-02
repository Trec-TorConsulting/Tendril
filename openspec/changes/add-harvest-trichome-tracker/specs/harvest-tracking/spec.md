# Capability: Harvest Tracking

## Purpose
Evidence-based harvest timing for cannabis grows. Users log trichome observations over time; the system produces a live optimal-harvest window that refines as data accrues, plus a quality-first ripening checklist. Prioritizes cannabinoid maturity and terpene preservation over yield — never nudging toward an early harvest for quantity.

## ADDED Requirements

### Requirement: Trichome Observation Logging
The system SHALL allow users to log trichome observations (clear/cloudy/amber percentages, optional note and photo) over time for a grow.

#### Scenario: Log an observation
- **WHEN** a user submits a trichome observation with clear/cloudy/amber percentages
- **THEN** the system stores it with a timestamp for the grow

#### Scenario: Percentages validated
- **WHEN** the submitted percentages do not sum to approximately 100
- **THEN** the system rejects the observation with a validation error

### Requirement: Live Harvest Window Estimate
The system SHALL compute an optimal harvest window (earliest, optimal, latest) with a confidence level, refined as trichome observations accrue.

#### Scenario: Estimate with sparse data
- **WHEN** few or no trichome observations exist
- **THEN** the system returns a wider window with lower confidence based on flower start and strain flower-weeks (or a grow-type default)

#### Scenario: Estimate refined by trichome trend
- **WHEN** observations show cloudy trichomes rising with emerging amber
- **THEN** the system narrows and shifts the window toward the quality-first target profile

#### Scenario: Never a single hard date
- **WHEN** the harvest window is presented
- **THEN** the system presents a range and confidence, not a single guaranteed date

### Requirement: Quality-First Ripening Checklist
The system SHALL provide a stage-gated ripening checklist prioritizing cannabinoid maturity and terpene preservation.

#### Scenario: Checklist in ripening
- **WHEN** a grow is in flowering or ripening
- **THEN** the system surfaces ripening checklist items (e.g., flush timing, terpene-preserving environment, mold vigilance)

#### Scenario: Quality over yield
- **WHEN** harvest guidance is generated
- **THEN** it never recommends harvesting early to increase yield at the expense of quality
