## ADDED Requirements

### Requirement: RDWC ORP thresholds SHALL be system-type-aware
The system SHALL evaluate RDWC ORP ranges using the grow's configured system_type.

#### Scenario: Live beneficial RDWC threshold
- **WHEN** a grow has settings.system_type = live_beneficial
- **THEN** ORP status SHALL use min 200, max 300, target 260

#### Scenario: Sterilized RDWC threshold
- **WHEN** a grow has settings.system_type = sterilized
- **THEN** ORP status SHALL use min 300, max 450, target 375

### Requirement: Grow settings update SHALL preserve unrelated keys
The grow update API SHALL merge incoming settings keys into existing settings.

#### Scenario: Update only system_type
- **WHEN** a grow has settings with multiple keys
- **AND** the client PATCH payload provides only settings.system_type
- **THEN** existing unrelated settings keys SHALL remain unchanged

### Requirement: system_type values SHALL be validated
The grow update API SHALL reject unsupported settings.system_type values.

#### Scenario: Invalid system_type
- **WHEN** the client sends settings.system_type with a value not in {live_beneficial, sterilized}
- **THEN** the API SHALL return HTTP 400 with a validation error

### Requirement: RDWC system_type SHALL be configured per grow in settings UI
The grow settings UI SHALL provide system_type selection for RDWC grows as a settings field.

#### Scenario: Configure per-grow ORP mode
- **WHEN** a user edits RDWC grow settings
- **THEN** the UI SHALL allow selecting live_beneficial or sterilized
- **AND** the saved value SHALL be stored in grow settings.system_type

### Requirement: Settings option labels SHALL be human-friendly
The settings UI SHALL display human-friendly labels for select options while preserving canonical stored values.

#### Scenario: ORP system type labels
- **WHEN** displaying system_type options
- **THEN** live_beneficial SHALL render as "Live Beneficial (HydroGuard, microbes)"
- **AND** sterilized SHALL render as "Sterilized (H2O2 / oxidizer)"
