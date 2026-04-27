## 1. Backend — httpOnly Cookie Auth
- [ ] 1.1 Update `api/app/auth/routes.py` login/register to set `httpOnly`, `Secure`, `SameSite=Strict` cookies
- [ ] 1.2 Update `api/app/auth/middleware.py` `get_current_user` to read token from cookie (fallback to header)
- [ ] 1.3 Add logout endpoint that clears auth cookies
- [ ] 1.4 Update refresh token flow to use cookie-based rotation

## 2. Backend — CSRF Protection
- [ ] 2.1 Create `api/app/middleware/csrf.py` with double-submit cookie pattern
- [ ] 2.2 Generate CSRF token on auth and include in response header `X-CSRF-Token`
- [ ] 2.3 Validate CSRF token on all POST/PUT/PATCH/DELETE endpoints
- [ ] 2.4 Exempt webhook endpoints (Stripe, MQTT) that use their own auth

## 3. Frontend — Cookie Auth Migration
- [ ] 3.1 Update `web/src/lib/auth.ts` to remove `localStorage` token storage
- [ ] 3.2 Update API client to include `credentials: 'include'` on all requests
- [ ] 3.3 Read CSRF token from response headers and include in mutation requests
- [ ] 3.4 Update login/logout flows for cookie-based auth

## 4. Validation
- [ ] 4.1 Unit tests for CSRF middleware (valid token, missing token, invalid token)
- [ ] 4.2 Unit tests for cookie-based auth (httpOnly, Secure, SameSite flags)
- [ ] 4.3 E2E test: login → mutation → verify CSRF token required
- [ ] 4.4 Verify XSS cannot access tokens via `document.cookie`
