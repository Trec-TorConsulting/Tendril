# Change: Enterprise RBAC Overhaul

## Why
The current RBAC system uses single-tenant FK binding, boolean platform flags, and string-based roles with no enum validation. Users cannot belong to multiple tenants, there is no grow-level access scoping, the "viewer" role is effectively dead (only 4 of 78 routes allow it), and there is no distinction between platform admin sub-roles (support vs readonly admin). This blocks enterprise multi-tenant deployments and violates the "Security First, API First" principle.

## What Changes
- **BREAKING**: Replace `User.tenant_id` FK + `User.role` with a `tenant_memberships` pivot table
- **BREAKING**: Replace `User.is_platform_admin` + `User.is_support` booleans with a `platform_role` enum column
- **BREAKING**: JWT payload restructured (new claims: `pr`, `memberships`)
- Add `accounts` table as billing/ownership umbrella over tenants
- Add `account_members` pivot table (multi-owner, multi-tenant support)
- Add `tenant_memberships` table with per-membership role enum
- Add `membership_grow_access` table for object-level grow scoping
- Add `permissions` module with granular permission constants and checker
- Replace all `require_role()` calls with `require_permission()` guards
- Add tenant-switch endpoint (re-issues JWT for different active tenant)
- Update all frontend role checks to use new permission model
- Data migration: existing users → account + membership records

## Impact
- Affected specs: `rbac` (new capability spec)
- Affected code:
  - `api/app/tenants/models.py` — new Account, AccountMember, TenantMembership, MemberGrowAccess models; User model changes
  - `api/app/auth/middleware.py` — complete rewrite of CurrentUser, require_role → require_permission
  - `api/app/auth/jwt.py` — new token payload structure
  - `api/app/auth/routes.py` — registration, login, refresh, tenant-switch
  - `api/app/admin/routes.py` — platform role management
  - `api/app/tenants/routes.py` — membership management
  - All 13 route files with `require_role` (78 endpoints total)
  - `api/app/database.py` — optional grow-scoped RLS
  - `web/src/hooks/use-user.ts` — new UserData interface
  - `web/src/lib/auth.ts` — tenant switching
  - `web/src/components/app-sidebar.tsx` — new permission checks
  - `web/src/app/platform/layout.tsx` — platform_role enum
  - Migration 0024
