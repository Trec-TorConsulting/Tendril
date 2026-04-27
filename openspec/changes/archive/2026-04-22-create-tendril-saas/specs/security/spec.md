## ADDED Requirements

### Requirement: OWASP A01 Broken Access Control
The system SHALL enforce access control at both the application and database layers, preventing unauthorized cross-tenant or cross-role data access.

#### Scenario: Cross-tenant API request
- **WHEN** a user crafts a request with another tenant's resource ID
- **THEN** PostgreSQL RLS returns zero rows and the API returns 404

### Requirement: OWASP A02 Cryptographic Failures
The system SHALL use strong cryptography for passwords, tokens, and transport.

#### Scenario: Password storage
- **WHEN** a user registers or changes their password
- **THEN** the password is hashed with bcrypt (cost factor >= 12) and the plaintext is never stored or logged

#### Scenario: TLS enforcement
- **WHEN** any client connects to the API, frontend, or MQTT broker
- **THEN** the connection uses TLS 1.2+ and plaintext connections are rejected

### Requirement: OWASP A03 Injection
The system SHALL prevent SQL injection, command injection, and XSS through parameterized queries and input validation.

#### Scenario: SQL injection attempt
- **WHEN** a user submits a payload containing SQL injection characters
- **THEN** the parameterized query treats it as literal data and the system returns a normal response or validation error

### Requirement: OWASP A04 Insecure Design
The system SHALL implement security controls by design including account lockout, brute-force protection, and rate limiting.

#### Scenario: Brute-force login
- **WHEN** 10 failed login attempts occur for the same email within 15 minutes
- **THEN** the account is temporarily locked and the user is notified via email

### Requirement: OWASP A05 Security Misconfiguration
The system SHALL enforce strict CORS, security headers, and minimal attack surface.

#### Scenario: CORS enforcement
- **WHEN** a request arrives from an unauthorized origin
- **THEN** the API rejects the request with no CORS headers

#### Scenario: Security headers
- **WHEN** any HTTP response is sent
- **THEN** it includes Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options headers

### Requirement: OWASP A06 Vulnerable Components
The system SHALL track and update dependencies to prevent known vulnerabilities.

#### Scenario: Dependency scan
- **WHEN** a CI pipeline runs
- **THEN** Dependabot or Snyk scans all Python and Node.js dependencies and fails the build on critical/high vulnerabilities

### Requirement: OWASP A07 Identification and Authentication Failures
The system SHALL enforce strong authentication practices including token expiry, rotation, and verification requirements.

#### Scenario: Expired access token
- **WHEN** a request is made with an expired JWT access token
- **THEN** the API returns 401 and the client must use the refresh token to obtain a new access token

### Requirement: OWASP A08 Software and Data Integrity Failures
The system SHALL validate all inputs and use signed tokens to prevent tampering.

#### Scenario: Tampered JWT
- **WHEN** a modified JWT is submitted
- **THEN** signature verification fails and the request is rejected with 401

### Requirement: OWASP A09 Security Logging and Monitoring
The system SHALL log security-relevant events in structured format for monitoring and incident response.

#### Scenario: Failed login logging
- **WHEN** a login attempt fails
- **THEN** the event is logged with timestamp, email (hashed), source IP, and failure reason (no passwords logged)

### Requirement: OWASP A10 Server-Side Request Forgery
The system SHALL prevent SSRF by validating and restricting server-side URL fetching.

#### Scenario: Camera URL validation
- **WHEN** a user configures a camera snapshot URL
- **THEN** the system validates the URL against allowed schemes (http/https/rtsp) and rejects internal/private IP ranges
