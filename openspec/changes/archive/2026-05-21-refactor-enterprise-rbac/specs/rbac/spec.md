## ADDED Requirements

### Requirement: Platform Role Hierarchy
The system SHALL enforce a platform-level role hierarchy stored as a PostgreSQL enum on the users table with exactly four values: `super_admin`, `support`, `readonly_admin`, `user`.

#### Scenario: Super admin full access
- **WHEN** a user with platform_role `super_admin` accesses any endpoint
- **THEN** access SHALL be granted regardless of tenant membership or object scope

#### Scenario: Support read and fix access
- **WHEN** a user with platform_role `support` accesses a read endpoint or user-account modification endpoint
- **THEN** access SHALL be granted
- **WHEN** a user with platform_role `support` attempts to modify platform configuration or promote users to super_admin
- **THEN** the system SHALL return 403 Forbidden

#### Scenario: Readonly admin observation only
- **WHEN** a user with platform_role `readonly_admin` accesses any read endpoint across all tenants
- **THEN** access SHALL be granted
- **WHEN** a user with platform_role `readonly_admin` attempts any write/delete/update operation
- **THEN** the system SHALL return 403 Forbidden

#### Scenario: Regular user platform access denied
- **WHEN** a user with platform_role `user` attempts to access platform admin endpoints
- **THEN** the system SHALL return 403 Forbidden

---

### Requirement: Account Ownership Model
The system SHALL provide an `accounts` entity that groups one or more tenants under a single billing umbrella. Account membership SHALL be stored in an `account_members` pivot table with roles `owner` or `billing_admin`.

#### Scenario: Multi-owner account
- **WHEN** an account has multiple users with account_members.role = 'owner'
- **THEN** all owners SHALL have full administrative access to all tenants within that account

#### Scenario: Single owner multi-tenant
- **WHEN** a user is an account owner and the account contains multiple tenants
- **THEN** the user SHALL be able to switch between tenants and have admin-level access in each

#### Scenario: Account creation on registration
- **WHEN** a new user registers
- **THEN** the system SHALL create an Account, assign the user as owner, create a Tenant within that account, and create a TenantMembership with role `admin`

---

### Requirement: Tenant Membership with Role
The system SHALL store tenant-level access in a `tenant_memberships` pivot table with a role enum of `admin`, `member`, or `viewer`. A user MAY have memberships in multiple tenants with different roles.

#### Scenario: Admin full tenant access
- **WHEN** a user has tenant_memberships.role = 'admin' for a tenant
- **THEN** the user SHALL have full CRUD access to all resources within that tenant including user management and settings

#### Scenario: Member operational access
- **WHEN** a user has tenant_memberships.role = 'member' for a tenant
- **THEN** the user SHALL be able to create and update grows, devices, sensors, integrations, journals, and feedings
- **THEN** the user SHALL NOT be able to access billing, manage other users, or delete resources

#### Scenario: Viewer read-only access
- **WHEN** a user has tenant_memberships.role = 'viewer' for a tenant
- **THEN** the user SHALL only be able to read metrics, status, and health data
- **THEN** the user SHALL NOT be able to create, update, or delete any resources

#### Scenario: Multi-tenant membership
- **WHEN** a user has memberships in tenants A and B
- **THEN** the user SHALL be able to switch active tenant context without re-authentication

---

### Requirement: Object-Level Grow Scoping
The system SHALL support restricting tenant members and viewers to a specific subset of grows via a `membership_grow_access` table. If no rows exist for a membership, the user SHALL have access to all grows in that tenant.

#### Scenario: Unrestricted member
- **WHEN** a membership has no rows in membership_grow_access
- **THEN** the user SHALL have access to all grows in the tenant

#### Scenario: Grow-scoped member
- **WHEN** a membership has specific grow_cycle_ids in membership_grow_access
- **THEN** the user SHALL only access data related to those specific grows
- **WHEN** the user attempts to access a grow not in their scope
- **THEN** the system SHALL return 403 Forbidden

#### Scenario: Scope encoded in JWT
- **WHEN** a user with grow-level scoping authenticates or switches tenant
- **THEN** the JWT access token SHALL include the grow scope as a `gs` claim (array of grow UUIDs or null for unrestricted)

---

### Requirement: Permission-Based Route Guards
The system SHALL enforce access control via granular permission constants mapped from roles, replacing direct role-string comparisons. Route handlers SHALL use `require_permission()` dependency injection.

#### Scenario: Permission check on write endpoint
- **WHEN** a request arrives at a write endpoint (create/update)
- **THEN** the system SHALL verify the user's effective permissions include the required write permission for that resource domain

#### Scenario: Permission check on delete endpoint
- **WHEN** a request arrives at a delete endpoint
- **THEN** the system SHALL verify the user has the delete permission (granted only to admin role and above)

#### Scenario: Permission check on read endpoint
- **WHEN** a request arrives at a read endpoint
- **THEN** the system SHALL verify the user has at minimum read permission (granted to all tenant roles including viewer)

#### Scenario: Platform role bypass
- **WHEN** a super_admin accesses any tenant endpoint
- **THEN** permission checks SHALL be bypassed entirely

#### Scenario: Support platform endpoints
- **WHEN** a support user accesses an admin endpoint
- **THEN** write operations SHALL be restricted to user account management only (password resets, unlocks)

---

### Requirement: Tenant Switching
The system SHALL provide a `POST /auth/switch-tenant` endpoint that accepts a target tenant_id and re-issues an access token scoped to that tenant's membership context.

#### Scenario: Valid tenant switch
- **WHEN** a user with active membership in tenant B calls switch-tenant with tenant B's ID
- **THEN** the system SHALL return a new access token with `tid` = tenant B, `tr` = user's role in tenant B, and `gs` = user's grow scope in tenant B

#### Scenario: Unauthorized tenant switch
- **WHEN** a user without membership in tenant C calls switch-tenant with tenant C's ID
- **THEN** the system SHALL return 403 Forbidden

#### Scenario: Platform admin tenant switch
- **WHEN** a super_admin calls switch-tenant with any tenant ID
- **THEN** the system SHALL return a new access token with admin-level access regardless of membership

---

### Requirement: Billing Access Control
The system SHALL restrict billing endpoints to users with account-level owner role or explicit `billing:manage` permission. Tenant-level member and viewer roles SHALL NOT have billing access.

#### Scenario: Account owner billing access
- **WHEN** an account owner accesses billing endpoints
- **THEN** access SHALL be granted

#### Scenario: Tenant member billing denied
- **WHEN** a tenant member (non-owner) attempts to access billing endpoints
- **THEN** the system SHALL return 403 Forbidden

---

### Requirement: Data Migration Integrity
The system SHALL migrate all existing user-tenant relationships to the new schema in a single atomic database transaction preserving all existing access levels.

#### Scenario: Existing owner migration
- **WHEN** migration runs on a user with role='owner' in tenant T
- **THEN** the system SHALL create: Account (named after T), AccountMember(user, account, 'owner'), TenantMembership(user, T, 'admin'), and set tenants.account_id

#### Scenario: Existing member migration
- **WHEN** migration runs on a user with role='member' in tenant T
- **THEN** the system SHALL create TenantMembership(user, T, 'member')

#### Scenario: Existing platform admin migration
- **WHEN** migration runs on a user with is_platform_admin=True
- **THEN** the system SHALL set users.platform_role = 'super_admin'

#### Scenario: Existing support migration
- **WHEN** migration runs on a user with is_support=True
- **THEN** the system SHALL set users.platform_role = 'support'
