## 1. Database Schema
- [ ] 1.1 Create `platform_role` PostgreSQL enum type (`super_admin`, `support`, `readonly_admin`, `user`)
- [ ] 1.2 Create `tenant_role` PostgreSQL enum type (`admin`, `member`, `viewer`)
- [ ] 1.3 Create `account_role` PostgreSQL enum type (`owner`, `billing_admin`)
- [ ] 1.4 Create `accounts` table (id, name, billing_email, stripe_customer_id, stripe_subscription_id, created_at)
- [ ] 1.5 Create `account_members` table (id, account_id FK, user_id FK, role account_role, created_at, UNIQUE(account_id, user_id))
- [ ] 1.6 Add `account_id` FK column to `tenants` table
- [ ] 1.7 Create `tenant_memberships` table (id, tenant_id FK, user_id FK, role tenant_role, created_at, UNIQUE(tenant_id, user_id))
- [ ] 1.8 Create `membership_grow_access` table (id, membership_id FK, grow_cycle_id UUID, UNIQUE(membership_id, grow_cycle_id))
- [ ] 1.9 Add `platform_role` column to `users` table (default 'user')
- [ ] 1.10 Data migration: backfill platform_role from is_platform_admin/is_support flags
- [ ] 1.11 Data migration: create Account per existing Tenant, move Stripe fields
- [ ] 1.12 Data migration: create AccountMember for each existing owner
- [ ] 1.13 Data migration: create TenantMembership from existing users.tenant_id + users.role
- [ ] 1.14 Drop old columns: users.tenant_id, users.role, users.is_platform_admin, users.is_support
- [ ] 1.15 Drop old columns: tenants.stripe_customer_id, tenants.stripe_subscription_id
- [ ] 1.16 Update SQLAlchemy models (User, Tenant, new Account, AccountMember, TenantMembership, MemberGrowAccess)

## 2. Permission System
- [ ] 2.1 Create `app/auth/permissions.py` with permission constants (grouped by domain)
- [ ] 2.2 Create role → permission mapping (PLATFORM_PERMISSIONS, TENANT_PERMISSIONS)
- [ ] 2.3 Create `require_permission(*perms)` dependency factory
- [ ] 2.4 Create `require_platform_role(*roles)` dependency
- [ ] 2.5 Create `require_grow_access(grow_id_param)` dependency for grow-scoped operations
- [ ] 2.6 Update `CurrentUser` model (platform_role, tenant_id, tenant_role, grow_scope, account_id)

## 3. Auth Endpoints
- [ ] 3.1 Update `create_access_token()` with new JWT payload (pr, tid, tr, gs, aid)
- [ ] 3.2 Update `create_refresh_token()` (tenant-agnostic, just sub + type + exp)
- [ ] 3.3 Update login to resolve active tenant + membership
- [ ] 3.4 Update registration to create Account + Tenant + AccountMember + TenantMembership
- [ ] 3.5 Add `POST /auth/switch-tenant` endpoint
- [ ] 3.6 Update refresh endpoint to include new claims
- [ ] 3.7 Update `/auth/me` response with full role/permission info
- [ ] 3.8 Update `get_current_user()` to decode new JWT payload

## 4. Route Guards Migration
- [ ] 4.1 Replace all `require_role("owner", "member")` → `require_permission("resource:write")`
- [ ] 4.2 Replace all `require_role("owner")` → `require_permission("resource:delete")` or `require_permission("tenant:manage")`
- [ ] 4.3 Replace all `require_role("owner", "member", "viewer")` → `require_permission("resource:read")`
- [ ] 4.4 Replace `require_platform_admin` → `require_platform_role("super_admin")`
- [ ] 4.5 Replace `require_support_or_admin` → `require_platform_role("super_admin", "support", "readonly_admin")`
- [ ] 4.6 Add grow-scope checks on grow-specific routes
- [ ] 4.7 Add `require_permission("billing:manage")` on billing routes
- [ ] 4.8 Update admin routes for readonly_admin restrictions (read but not write)

## 5. Tenant & Account Management
- [ ] 5.1 Update tenant member routes to use TenantMembership model
- [ ] 5.2 Add grow-scope assignment endpoint (assign/remove grows from membership)
- [ ] 5.3 Add account management routes (create account, add/remove tenant from account)
- [ ] 5.4 Update admin user management for platform_role enum

## 6. Frontend Updates
- [ ] 6.1 Update `UserData` interface in `use-user.ts`
- [ ] 6.2 Update `app-sidebar.tsx` role checks
- [ ] 6.3 Update `platform/layout.tsx` authorization
- [ ] 6.4 Update team management page for new membership model
- [ ] 6.5 Add tenant-switcher component
- [ ] 6.6 Update `lib/api.ts` with new types and endpoints

## 7. Testing
- [ ] 7.1 Unit tests for permission system (role → permission mapping)
- [ ] 7.2 Integration tests for new auth endpoints (login, switch-tenant, refresh)
- [ ] 7.3 Integration tests for route guards (permission checks)
- [ ] 7.4 Migration test (up + down on test DB)
- [ ] 7.5 Run full test suite, fix any regressions
