# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Tendril, **please report it responsibly**. Do not open a public issue.

### How to Report

Email: **security@trec-tor.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Affected components (API, Web, ESP32, infrastructure)
- Potential impact
- Suggested fix (if you have one)

### What to Expect

- **Acknowledgment** within 48 hours
- **Assessment** within 7 days
- **Fix timeline** communicated based on severity
- **Credit** in the changelog and release notes (unless you prefer anonymity)

### Severity Levels

| Level | Response Time | Examples |
|-------|--------------|---------|
| Critical | 24–48 hours | RCE, auth bypass, data exfiltration |
| High | 7 days | SQL injection, privilege escalation, credential exposure |
| Medium | 14 days | XSS, CSRF, information disclosure |
| Low | 30 days | Minor information leaks, missing headers |

## Security Measures

Tendril implements the following security controls:

### Authentication & Authorization
- JWT with short-lived access tokens (15 min) and rotating refresh tokens
- Password hashing with bcrypt
- Brute-force protection on login endpoints
- OAuth2 support (Google, GitHub)
- Enterprise RBAC with granular permission system (~30 permissions across 12 domains)
- **Platform roles**: Super Admin, Support, Read-Only Admin, User
- **Tenant roles**: Admin, Member, Viewer
- **Account roles**: Owner, Billing Admin
- Permission-based route guards (`require_permission()`) instead of direct role checks
- Grow-scoped access control for restricting tenant users to specific grow cycles
- Tenant-switching with per-tenant JWT claims

### Data Isolation
- PostgreSQL Row-Level Security (RLS) for tenant isolation
- All tenant data is scoped via session-level `app.current_tenant` variable
- No cross-tenant data access is possible at the database level
- Account → Tenant hierarchy separates billing from data access
- Tenant memberships are explicit (join table), not implicit via user fields

### API Security
- Rate limiting middleware
- Security headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- CORS with configurable allowed origins
- Input validation via Pydantic schemas

### Infrastructure
- Docker images use slim base images with minimal attack surface
- No root processes in containers
- Secrets managed via environment variables (not baked into images)
- Kubernetes secrets for production deployments

### Device Security
- ESP32 devices authenticate to MQTT with pre-shared keys
- MQTT topics are scoped by tenant and device ID
- EMQX supports ACL rules to restrict device topic access

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest `main` | Yes |
| Older commits | Best effort |

## Scope

The following are **in scope** for security reports:

- Tendril API (Python / FastAPI)
- Tendril Web (Next.js)
- ESP32 firmware
- Docker and Kubernetes configurations
- MQTT topic security
- Tenant isolation bypass

The following are **out of scope**:

- Third-party services (Stripe, Google, GitHub, EMQX) — report to those vendors
- Social engineering
- Denial of service via network flooding
- Issues requiring physical access to deployed hardware
