## ADDED Requirements

### Requirement: User Authentication
The system SHALL require authentication for all API endpoints except `/health`, `/api/status`, `/api/auth/*`, and static assets. Authentication SHALL use JWT tokens stored in httpOnly cookies.

#### Scenario: Unauthenticated API request
- **WHEN** a request is made to a protected endpoint without a valid JWT cookie
- **THEN** the system returns HTTP 401 Unauthorized

#### Scenario: Successful login
- **WHEN** a user submits valid credentials to `POST /api/auth/login`
- **THEN** a JWT is set as an httpOnly cookie and the user's profile is returned

#### Scenario: First-user registration
- **WHEN** no users exist in the database and `POST /api/auth/register` is called
- **THEN** the user is created with the `admin` role and a session is established

---

### Requirement: CSRF Protection
The system SHALL enforce CSRF token validation on all state-changing requests (POST, PUT, DELETE) to prevent cross-site request forgery.

#### Scenario: Missing CSRF token
- **WHEN** a POST/PUT/DELETE request is made without a valid CSRF token
- **THEN** the system returns HTTP 403 Forbidden

---

### Requirement: Rate Limiting
The system SHALL rate-limit authentication endpoints to prevent brute-force attacks (maximum 5 login attempts per minute per IP).

#### Scenario: Rate limit exceeded
- **WHEN** more than 5 login attempts are made from the same IP within 60 seconds
- **THEN** the system returns HTTP 429 Too Many Requests

---

### Requirement: Security Headers
The system SHALL set security headers on all responses: Content-Security-Policy, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection.

#### Scenario: Security headers present
- **WHEN** any HTTP response is returned
- **THEN** security headers are present to prevent XSS, clickjacking, and MIME sniffing

---

### Requirement: Role-Based Access Control
The system SHALL support `admin` and `viewer` roles. Admin users have full access. Viewer users have read-only access and cannot modify settings, delete data, or manage users.

#### Scenario: Viewer attempts write operation
- **WHEN** a user with the `viewer` role attempts a POST, PUT, or DELETE on a protected resource
- **THEN** the system returns HTTP 403 Forbidden

#### Scenario: Admin manages users
- **WHEN** an admin user accesses user management endpoints
- **THEN** they can create, list, and delete user accounts

## MODIFIED Requirements

### Requirement: WebSocket Streaming
The system SHALL stream LLM responses via WebSocket with keepalive pings to prevent connection drops. WebSocket connections SHALL validate the JWT cookie on upgrade.

#### Scenario: Streaming response
- **WHEN** a user sends a message via the WebSocket endpoint `/ws/chat`
- **THEN** tokens are streamed incrementally as the LLM generates them

#### Scenario: Connection keepalive
- **WHEN** a WebSocket connection is idle during LLM processing
- **THEN** the server sends periodic keepalive pings to prevent timeout

#### Scenario: Unauthenticated WebSocket
- **WHEN** a WebSocket upgrade request is made without a valid JWT cookie
- **THEN** the connection is rejected with HTTP 401
