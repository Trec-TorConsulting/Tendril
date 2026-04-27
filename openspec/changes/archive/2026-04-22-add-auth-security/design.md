## Context
The Grow Assistant currently has zero authentication. All endpoints are publicly accessible to anyone on the network. This is acceptable for a single-user home lab, but a distributable product needs auth to protect camera feeds, API keys, and grow data.

## Goals / Non-Goals
- **Goals**: Local user accounts, JWT sessions, CSRF protection, rate limiting, security headers, role-based access
- **Non-Goals**: OAuth/SSO integration (too complex for home users), multi-tenancy (separate data per user), API key management

## Decisions

### Authentication Method
- **Decision**: JWT in httpOnly cookies with CSRF tokens
- **Rationale**: Cookies are automatically sent with every request (including WebSocket upgrade), httpOnly prevents XSS token theft, CSRF tokens prevent cross-site attacks. No localStorage token management needed.
- **Alternatives**: Bearer token in localStorage (XSS vulnerable), session IDs in server memory (doesn't scale, lost on restart)

### Password Storage
- **Decision**: bcrypt with work factor 12
- **Rationale**: Industry standard, resistant to brute force, well-supported in Python
- **Alternative**: Argon2 — better but less commonly available in all Python environments

### First-User Bootstrap
- **Decision**: First registered user automatically becomes admin. Registration is open only when no users exist.
- **Rationale**: No need for a separate admin setup tool. After first user, new users must be invited by admin.
- **Alternative**: Require admin credentials in env vars — rejected (poor UX for home users)

### JWT Expiration
- **Decision**: 7-day token expiration with rotation on active use
- **Rationale**: Home users shouldn't need to re-login frequently. Token refreshed on each API call if within the last 24 hours of expiry.

## Risks / Trade-offs
- **Breaking Change**: All existing API consumers (if any) will need to authenticate. Mitigated by the setup wizard handling initial user creation.
- **Token theft via XSS**: Mitigated by httpOnly cookies + CSP headers. Notes/labels are sanitized before rendering.
- **Rate limiting in single-process**: Using in-memory store. Resets on restart, but sufficient for home use.

## Migration Plan
1. Add users/sessions tables (non-destructive, additive schema change)
2. Deploy auth module with `AUTH_ENABLED=false` env var initially
3. Enable auth via env var or setup wizard
4. Existing data remains — auth is additive

## Open Questions
- Should we support "remember me" (30-day) vs short sessions?
- Should API tokens (for ESP32 or Home Assistant integration) be a separate auth mechanism?
