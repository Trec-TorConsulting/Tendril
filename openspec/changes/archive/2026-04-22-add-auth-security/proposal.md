# Change: Add Authentication & Security

## Why
The app currently has zero authentication — anyone on the network can access all data, control cameras, and interact with the AI. For an open-source distro running on home networks, we need local user accounts, session management, and security hardening to protect sensitive data (camera feeds, API keys, grow data).

## What Changes
- Add local user account system (registration, login, session management)
- Add JWT-based API authentication with httpOnly cookie sessions
- Add CSRF protection for state-changing endpoints
- Add rate limiting on auth endpoints
- Add password hashing (bcrypt)
- Add first-user setup flow (first registered user becomes admin)
- **BREAKING**: All API endpoints require authentication (except `/health`, `/api/status`, static assets)
- Add role-based access (admin vs viewer) for future multi-user scenarios

## Impact
- Affected specs: `grow-assistant-core` (all API endpoints gated), `bucket-monitoring` (API auth), `environment-monitoring` (API auth), `camera-health-checks` (API auth, sensitive camera access)
- Affected code: `app/main.py` (auth middleware), new `app/auth.py`, `app/store.py` (users table), `app/static/index.html` (login screen)
- **BREAKING**: Existing unauthenticated API access will stop working
