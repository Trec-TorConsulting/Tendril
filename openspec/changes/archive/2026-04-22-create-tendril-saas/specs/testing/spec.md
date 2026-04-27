## ADDED Requirements

### Requirement: Unit Test Coverage
The system SHALL have unit tests covering auth, tenant isolation (RLS), RBAC, input validation, and service logic using pytest.

#### Scenario: Tenant RLS isolation test
- **WHEN** a test creates data for tenant A and queries as tenant B
- **THEN** tenant B receives zero rows and cannot access tenant A's data

### Requirement: Integration Test Coverage
The system SHALL have integration tests using pytest + testcontainers (PostgreSQL) covering all API endpoints, MQTT auth webhooks, and device pairing.

#### Scenario: API endpoint tenant isolation
- **WHEN** an integration test calls any CRUD endpoint with a valid JWT
- **THEN** only data belonging to the JWT's tenant is returned or modified

### Requirement: Security Test Suite
The system SHALL have dedicated security tests covering cross-tenant access, SQL injection payloads, token tampering, RBAC bypass, and SSRF probes.

#### Scenario: Cross-tenant resource access
- **WHEN** a test attempts to access another tenant's resource by guessing IDs
- **THEN** the API returns 404 (not 403) to prevent information leakage

#### Scenario: SQL injection payload
- **WHEN** a test submits SQL injection payloads in all string input fields
- **THEN** the API treats them as literal data and returns normal responses or validation errors

### Requirement: Frontend Test Coverage
The system SHALL have frontend component tests using Vitest + React Testing Library covering auth flows, dashboard, and PWA manifest.

#### Scenario: Auth page tests
- **WHEN** frontend tests render the login page
- **THEN** the test verifies form validation, error display, and successful redirect on login

### Requirement: E2E Test Suite
The system SHALL have end-to-end tests using Playwright covering full user flows from signup through sensor data viewing.

#### Scenario: Complete user flow
- **WHEN** an E2E test runs the full flow: signup → verify email → pair device → create tent → create grow → add bucket → view sensor data → AI chat
- **THEN** all steps complete successfully with correct data displayed

### Requirement: CI Pipeline
The system SHALL have a GitHub Actions CI pipeline that runs lint, type-check, all tests, and dependency scanning on every PR, with E2E tests and deployment on merge to main.

#### Scenario: PR validation
- **WHEN** a pull request is opened or updated
- **THEN** the CI pipeline runs lint, type-check, unit/integration/security tests, frontend tests, dependency scan, and Docker build verification in parallel

#### Scenario: Merge deployment
- **WHEN** a PR is merged to main
- **THEN** the CI pipeline runs all checks plus E2E tests, builds and pushes Docker images, and deploys to the K3S cluster
