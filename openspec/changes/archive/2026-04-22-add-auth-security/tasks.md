## 1. Database Schema
- [ ] 1.1 Create `users` table (id, username, password_hash, display_name, role, created_at)
- [ ] 1.2 Create `sessions` table (id, user_id, token_hash, expires_at, created_at)
- [ ] 1.3 Add migration logic to create tables on startup (same pattern as existing tables)

## 2. Auth Module
- [ ] 2.1 Create `app/auth.py` with password hashing (bcrypt), JWT creation/verification
- [ ] 2.2 Implement `POST /api/auth/register` — create user account (first user auto-admin)
- [ ] 2.3 Implement `POST /api/auth/login` — validate credentials, return JWT in httpOnly cookie
- [ ] 2.4 Implement `POST /api/auth/logout` — clear session cookie
- [ ] 2.5 Implement `GET /api/auth/me` — return current user info from JWT
- [ ] 2.6 Add auth dependency (`get_current_user`) for FastAPI route injection
- [ ] 2.7 Add rate limiting on `/api/auth/login` (max 5 attempts per minute per IP)

## 3. API Protection
- [ ] 3.1 Add auth middleware — require valid JWT for all `/api/*` endpoints except auth routes, `/health`, `/api/status`
- [ ] 3.2 Add CSRF token generation and validation for state-changing requests (POST, PUT, DELETE)
- [ ] 3.3 Add CSRF token endpoint `GET /api/auth/csrf`
- [ ] 3.4 Update WebSocket `/ws/chat` to validate JWT from cookie on connection upgrade
- [ ] 3.5 Protect camera snapshot endpoints (prevent unauthenticated camera access)

## 4. Frontend Auth UI
- [ ] 4.1 Add login screen (shown when no valid session)
- [ ] 4.2 Add registration screen (shown only when no users exist — first-run)
- [ ] 4.3 Add logout button to settings/nav
- [ ] 4.4 Add CSRF token to all fetch() calls (POST/PUT/DELETE)
- [ ] 4.5 Handle 401 responses — redirect to login screen
- [ ] 4.6 Store CSRF token in memory (not localStorage)

## 5. Role-Based Access
- [ ] 5.1 Define roles: `admin` (full access), `viewer` (read-only, no settings changes)
- [ ] 5.2 Admin can create/invite additional users
- [ ] 5.3 Viewer cannot modify tent config, delete data, or change settings
- [ ] 5.4 Add user management section in settings (admin only)

## 6. Security Hardening
- [ ] 6.1 Set secure cookie flags (httpOnly, SameSite=Strict, Secure when HTTPS)
- [ ] 6.2 Add Content-Security-Policy header
- [ ] 6.3 Add X-Content-Type-Options, X-Frame-Options, X-XSS-Protection headers
- [ ] 6.4 Sanitize all user inputs (XSS prevention in bucket names, notes, etc.)
- [ ] 6.5 Validate API key / secret environment variables are not exposed in API responses
- [ ] 6.6 Add request size limits to prevent abuse

## 7. Testing
- [ ] 7.1 Test registration flow (first user = admin)
- [ ] 7.2 Test login/logout cycle
- [ ] 7.3 Test API returns 401 without auth
- [ ] 7.4 Test CSRF rejection on missing/invalid token
- [ ] 7.5 Test rate limiting on login endpoint
- [ ] 7.6 Test role enforcement (viewer cannot delete)
- [ ] 7.7 Test WebSocket auth
