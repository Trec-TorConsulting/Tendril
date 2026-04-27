## ADDED Requirements

### Requirement: Harvest Workflow
The system SHALL track the post-harvest process including drying, curing, and trimming stages with environmental monitoring (Pro and Commercial tiers).

#### Scenario: Start harvest
- **WHEN** a user marks a grow as harvested
- **THEN** the system transitions the grow to "harvesting" status and presents the harvest workflow (wet weight → dry → cure → trim → final weight)

#### Scenario: Drying phase tracking
- **WHEN** a user is in the drying phase
- **THEN** the system tracks drying environment (temp, humidity), duration, and weight loss over time

#### Scenario: Curing phase tracking
- **WHEN** a user moves to the curing phase
- **THEN** the system tracks curing jars, burp schedule reminders, humidity readings, and duration

#### Scenario: Final yield recording
- **WHEN** a user completes the harvest workflow
- **THEN** the system records final dry weight, quality rating, terpene notes, and calculates wet-to-dry ratio for strain performance analytics

### Requirement: Harvest Analytics
The system SHALL provide harvest outcome analytics across grows, strains, and methods.

#### Scenario: Strain harvest comparison
- **WHEN** a user views harvest analytics
- **THEN** the system shows average dry weight, wet-to-dry ratio, drying duration, and quality ratings grouped by strain
