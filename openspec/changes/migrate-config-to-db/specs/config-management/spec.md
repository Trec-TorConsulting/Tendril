## ADDED Requirements

### Requirement: Database-Driven Configuration System
The system SHALL store all domain reference data (grow type configs, task templates, treatments, nutrient guides, feed charts, alert rules) in PostgreSQL tables rather than hardcoded Python files.

#### Scenario: Grow type config retrieved from database
- **WHEN** any service requests grow type configuration (e.g. "cannabis-indoor" vegetative stage environment targets)
- **THEN** the system reads from normalized database tables (grow_type_profiles → grow_type_stages → grow_type_environment)
- **AND** results are cached in-process with 5-minute TTL

#### Scenario: Config cache invalidation on admin write
- **WHEN** an admin updates a grow type config via the admin API
- **THEN** the in-process cache for that config is immediately invalidated
- **AND** subsequent reads fetch fresh data from the database

### Requirement: Tenant Configuration Overrides
The system SHALL support per-tenant overrides of global configuration defaults using JSON merge semantics.

#### Scenario: Tenant override applied to environment targets
- **WHEN** a tenant has an override for config_type='environment' with config_key='grow_type:cannabis-indoor:stage:veg:environment'
- **THEN** the system merges the tenant's override_json on top of the global default
- **AND** only overridden fields change; non-overridden fields retain global values

#### Scenario: Override deleted reverts to global
- **WHEN** a tenant's override is deleted via the admin API
- **THEN** subsequent queries for that tenant return the unmodified global default

### Requirement: Admin CRUD API for Configuration
The system SHALL provide RESTful admin API endpoints for creating, reading, updating, and deleting all configuration data.

#### Scenario: Admin creates a new grow type profile
- **WHEN** an authenticated admin user POSTs to `/v1/admin/config/grow-types`
- **THEN** a new grow_type_profile is created in the database
- **AND** the response includes the created profile with its ID

#### Scenario: Non-admin rejected from config endpoints
- **WHEN** a non-admin user attempts to access any `/v1/admin/config/*` endpoint
- **THEN** the system returns 403 Forbidden

#### Scenario: Config export as JSON
- **WHEN** an admin GETs `/v1/admin/config/{type}/export`
- **THEN** the system returns a complete JSON export of all records for that config type
- **AND** the export is suitable for backup/restore via the import endpoint

#### Scenario: Config import from JSON
- **WHEN** an admin POSTs a JSON payload to `/v1/admin/config/{type}/import`
- **THEN** the system upserts all records from the JSON into the database
- **AND** existing records with matching keys are updated, new records are inserted

### Requirement: Admin Frontend for Configuration Management
The system SHALL provide user-friendly admin pages in the web frontend for managing all database-driven configuration.

#### Scenario: Admin navigates to grow type config editor
- **WHEN** an admin opens Settings → Config Management → Grow Types
- **THEN** a list of all grow type profiles is displayed
- **AND** each profile can be expanded to edit stages, environment targets, nutrients, and equipment

#### Scenario: Admin edits task template
- **WHEN** an admin modifies a task template's frequency or steps
- **THEN** changes are saved via the admin API
- **AND** the scheduler uses the updated template on its next cycle

### Requirement: Seed Migration from Existing Code
The system SHALL provide an Alembic migration that seeds all new tables from the existing hardcoded Python data with zero data loss.

#### Scenario: Migration seeds grow type data
- **WHEN** `alembic upgrade head` runs the seed migration
- **THEN** all 18 grow type profiles with their stages, environment targets, nutrients, watering, equipment, and troubleshooting entries are inserted
- **AND** row counts match the source data (verified by migration test)

#### Scenario: Migration is idempotent
- **WHEN** the seed migration runs multiple times (e.g. via `INSERT ... ON CONFLICT DO NOTHING`)
- **THEN** no duplicate rows are created
- **AND** existing data is not overwritten
