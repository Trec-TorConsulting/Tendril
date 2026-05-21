# Change: Add CSRF Protection and httpOnly Cookie Auth

## Why
The current auth implementation stores JWT tokens in `localStorage`, which is vulnerable to XSS attacks. Additionally, no CSRF protection exists on state-changing endpoints. Both are OWASP Top 10 failures (A02 Cryptographic Failures, A08 Data Integrity Failures).

## What Changes
- Migrate JWT access/refresh tokens from `localStorage` to `httpOnly` secure cookies
- Implement CSRF token generation and validation on all state-changing endpoints (POST, PUT, PATCH, DELETE)
- Add `SameSite=Strict` cookie attribute for additional CSRF defense
- Update frontend `auth.ts` to use cookie-based auth instead of `Authorization` header

## Impact
- Affected specs: `grow-assistant-core`
- **Breaking change**: Frontend auth flow changes from header-based to cookie-based
- Backwards compatibility: Support both patterns during migration with feature flag

## Implementation Notes
- CSRF tokens generated per session and returned in response headers
- Frontend reads CSRF token from `X-CSRF-Token` response header and sends it back on mutations
- `httpOnly` cookies prevent JavaScript access to tokens, eliminating XSS token theft
- `Secure` flag ensures cookies only sent over HTTPS
- Double-submit cookie pattern for CSRF validation

## Effort
MEDIUM — Requires coordinated backend + frontend changes
