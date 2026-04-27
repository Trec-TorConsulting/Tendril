## ADDED Requirements

### Requirement: User Registration
The system SHALL allow users to register with email and password, creating a new tenant and user account.

#### Scenario: Email/password registration
- **WHEN** a user submits a valid email and password
- **THEN** the system creates a tenant, creates a user with role "owner", sends a verification email, and returns a JWT access token

#### Scenario: Duplicate email
- **WHEN** a user registers with an email that already exists
- **THEN** the system returns a 409 Conflict error

### Requirement: User Login
The system SHALL authenticate users via email/password and return JWT tokens.

#### Scenario: Valid credentials
- **WHEN** a user submits valid email and password
- **THEN** the system returns an access token (short-lived) and refresh token (long-lived)

#### Scenario: Invalid credentials
- **WHEN** a user submits invalid credentials
- **THEN** the system returns a 401 Unauthorized error without revealing which field was wrong

### Requirement: Token Refresh
The system SHALL allow refreshing expired access tokens using a valid refresh token.

#### Scenario: Valid refresh
- **WHEN** a valid refresh token is submitted
- **THEN** the system returns a new access token and rotates the refresh token

### Requirement: Email Verification
The system SHALL require email verification before granting full account access.

#### Scenario: Verify email
- **WHEN** a user clicks the verification link
- **THEN** the user's email_verified flag is set to true

### Requirement: Social Login
The system SHALL support OAuth2 social login with Google, GitHub, Apple, and Discord.

#### Scenario: First social login
- **WHEN** a user authenticates via a social provider for the first time
- **THEN** the system creates a tenant, user, and links the social provider ID

#### Scenario: Existing social login
- **WHEN** a user authenticates via a previously linked social provider
- **THEN** the system returns JWT tokens for the existing account

### Requirement: Auth Provider Adapters
The system SHALL support pluggable identity provider adapters for Auth0, Firebase, and Supabase.

#### Scenario: Auth0 adapter
- **WHEN** Auth0 is configured as the identity provider
- **THEN** the system validates Auth0 JWT tokens and maps claims to tenant/user context

### Requirement: RBAC
The system SHALL enforce role-based access control with owner, member, and viewer roles.

#### Scenario: Viewer access
- **WHEN** a user with viewer role attempts a write operation
- **THEN** the system returns a 403 Forbidden error

#### Scenario: Owner management
- **WHEN** a tenant owner invites a user
- **THEN** the invited user receives an email with a join link and assigned role

### Requirement: Password Reset
The system SHALL allow users to reset their password via email.

#### Scenario: Password reset flow
- **WHEN** a user requests a password reset
- **THEN** the system sends a time-limited reset link to their email

### Requirement: Tier-Based Feature Gating
The system SHALL enforce pricing tier limits on resource counts, feature access, and usage quotas based on the tenant's plan.

#### Scenario: Resource limit exceeded
- **WHEN** a Grower tier tenant attempts to create a 3rd tent (limit: 2)
- **THEN** the system returns 403 with an error message indicating the limit and a link to upgrade

#### Scenario: Feature not available on tier
- **WHEN** a Seedling (free) tier user attempts to access AI chat
- **THEN** the system returns 403 with an upgrade prompt

#### Scenario: Usage quota exceeded
- **WHEN** a Grower tier tenant triggers a 3rd AI health check in one day (limit: 2/day)
- **THEN** the system returns 429 with the quota reset time

#### Scenario: Plan upgrade
- **WHEN** a tenant owner upgrades from Grower to Pro
- **THEN** the new limits take effect immediately and previously gated features become accessible
