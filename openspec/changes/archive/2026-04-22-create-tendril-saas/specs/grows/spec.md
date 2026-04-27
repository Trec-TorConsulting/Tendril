## ADDED Requirements

### Requirement: Tenant-Scoped Grow CRUD
The system SHALL provide full CRUD operations for grow cycles, scoped to the authenticated tenant.

#### Scenario: Create grow
- **WHEN** a user creates a grow with name, tent_id, start_date, and grow_type
- **THEN** the grow is created with the user's tenant_id, status "active", and the selected grow_type
- **AND** default sensor thresholds, pH/EC ranges, and feeding parameters are pre-filled from the grow type profile

#### Scenario: Grow type selection
- **WHEN** a user creates a grow
- **THEN** they select a grow type from: DWC, RDWC, NFT, Ebb & Flow, Drip/Top Feed, Aeroponics, Kratky, Coco Coir, Rockwool, Soil, Outdoor Soil, Outdoor Container
- **AND** the selected type determines which sensors, fields, questions, automations, and guidance appear throughout the app

#### Scenario: List grows
- **WHEN** a user lists grows with optional tent_id and status filters
- **THEN** only grows belonging to the user's tenant are returned

#### Scenario: Archive grow
- **WHEN** a user archives a grow
- **THEN** the grow status is set to "archived" and end_date is recorded

### Requirement: Tent Management
The system SHALL provide CRUD operations for tents, scoped to the authenticated tenant.

#### Scenario: Create tent
- **WHEN** a user creates a tent with name and configuration
- **THEN** the tent is created with the user's tenant_id

#### Scenario: Create outdoor tent
- **WHEN** a user creates a tent with `environment_type = "outdoor"`
- **THEN** the system prompts for location (browser geolocation or manual city/zip/coordinates) and stores latitude/longitude for weather data fetching

#### Scenario: Environment type options
- **WHEN** a user creates or edits a tent
- **THEN** they can select an environment type: "indoor" (default), "outdoor", or "greenhouse"
- **AND** outdoor and greenhouse tents require a location for weather integration

### Requirement: Grow Comparison
The system SHALL allow comparing metrics between two or more grow cycles within the same tenant.

#### Scenario: Compare grows
- **WHEN** a user selects two grows for comparison
- **THEN** the system returns side-by-side metrics (duration, yields, sensor averages)
