## ADDED Requirements

### Requirement: Tenant Isolation
The system SHALL isolate all data by tenant using PostgreSQL Row-Level Security policies on every data table.

#### Scenario: Cross-tenant data access
- **WHEN** a user queries data
- **THEN** only rows belonging to their tenant are returned, enforced at the database level

#### Scenario: Tenant context from JWT
- **WHEN** an authenticated request is received
- **THEN** the middleware extracts tenant_id from the JWT and sets the PostgreSQL session variable `app.current_tenant`

### Requirement: Tenant Management
The system SHALL provide CRUD operations for tenant settings (name, slug, plan).

#### Scenario: Update tenant name
- **WHEN** a tenant owner updates the tenant name
- **THEN** the tenant name is updated and the change is reflected in all subsequent responses

### Requirement: Team Management
The system SHALL allow tenant owners to invite, remove, and manage team members.

#### Scenario: Invite team member
- **WHEN** a tenant owner invites a user by email with a role
- **THEN** the system sends an invitation email and creates a pending membership

#### Scenario: Remove team member
- **WHEN** a tenant owner removes a member
- **THEN** the member loses access to the tenant's data immediately
