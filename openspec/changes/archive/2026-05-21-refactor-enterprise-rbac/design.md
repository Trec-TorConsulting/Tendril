## Context
The Tendril SaaS platform currently uses a simplistic RBAC model: each user is hard-linked to one tenant via FK, roles are unconstrained strings, and platform-level access is controlled by two boolean flags. This architecture cannot support:
- A single user owning/accessing multiple tenants (common in commercial operations)
- Restricting team members to specific grows within a tenant
- Differentiating between "can read everything platform-wide" vs "can modify user accounts" vs "full god-mode"
- Proper separation of billing ownership from operational access

## Goals / Non-Goals

### Goals
- Enterprise-grade multi-tenant RBAC with clear role hierarchy
- Platform roles: super_admin, support, readonly_admin
- Account-level ownership: multi-owner, multi-tenant
- Tenant-level roles: admin, member, viewer (enum-validated)
- Object-level scoping: restrict users to specific grows within a tenant
- Permission-based route guards (not role-string comparisons)
- JWT that supports tenant switching without full re-auth
- Zero-downtime data migration from existing schema
- PostgreSQL RLS integration for grow-level scoping

### Non-Goals
- ABAC (attribute-based access control) — too complex for current scale
- External identity provider integration (SAML/LDAP) — future work
- Fine-grained field-level permissions — unnecessary overhead
- Custom role definitions by tenants — predefined roles only for now
- Permission caching in Redis — JWT-based claims are sufficient

## Decisions

### 1. Platform Role as Enum Column (not separate table)
**Decision**: Store `platform_role` as a PostgreSQL enum directly on the `users` table.
**Why**: Only 4 platform roles exist, they're unlikely to grow dynamically, and this avoids an extra JOIN on every auth check. The enum provides DB-level validation.
**Alternatives**: Separate `platform_roles` table with FK — overkill for 4 static values.

### 2. Account Entity for Billing/Ownership
**Decision**: Introduce an `accounts` table that owns tenants and has its own member pivot.
**Why**: The user requirement explicitly states "A Single owner can have multi tenants" and ownership is distinct from operational access. Billing (Stripe) attaches to accounts, not individual tenants.
**Alternatives**: Flatten into tenant model — doesn't support multi-tenant ownership cleanly.

### 3. Pivot Table for Tenant Membership
**Decision**: `tenant_memberships(user_id, tenant_id, role)` replaces `users.tenant_id + users.role`.
**Why**: A user can be `admin` in one tenant and `viewer` in another. The pivot enables multi-tenant access with per-tenant roles.
**Alternatives**: Keep single FK and duplicate user records per tenant — violates unique email constraint and loses audit trail.

### 4. Grow-Level Scoping via Optional Access Table
**Decision**: `membership_grow_access(membership_id, grow_cycle_id)` — if no rows exist for a membership, that user has access to ALL grows in the tenant. Rows restrict to specific grows.
**Why**: User requirement states "Users can be limited to a grow or a set of grows within that tenant." The NULL-means-all pattern avoids populating rows for unrestricted users.
**Alternatives**: JSON array on membership row — harder to query, no FK integrity.

### 5. Permission Constants (not DB-stored permissions)
**Decision**: Define permissions as Python string constants grouped by domain. Map roles → permissions in code. Route guards check permissions.
**Why**: Permissions don't change at runtime. Code-defined permissions are testable, type-safe, and don't require DB queries beyond what's in the JWT.
**Alternatives**: DB permission tables (Django-style) — adds complexity without runtime flexibility benefit for our use case.

### 6. JWT Payload Structure
**Decision**: New payload:
```json
{
  "sub": "user-uuid",
  "pr": "super_admin|support|readonly_admin|user",
  "tid": "active-tenant-uuid",
  "tr": "admin|member|viewer",
  "gs": ["grow-uuid-1", "grow-uuid-2"] | null,
  "aid": "account-uuid",
  "type": "access",
  "exp": 1234567890
}
```
- `pr`: platform role (replaces `pa`/`sup` booleans)
- `tid`: active tenant (switchable without re-login)
- `tr`: tenant role for active tenant
- `gs`: grow scope (null = all grows)
- `aid`: account owning the active tenant

**Why**: Single tenant context per token (not array of all memberships) keeps tokens small and RLS simple. Tenant-switch endpoint re-issues token.
**Alternatives**: Embed all memberships in JWT — bloats token for users in many tenants.

### 7. Tenant Switching
**Decision**: `POST /auth/switch-tenant` accepts `tenant_id`, validates membership, issues new access token with that tenant's context.
**Why**: Users with multi-tenant access need to switch without re-entering credentials. Refresh token remains tenant-agnostic.

### 8. Migration Strategy
**Decision**: Single Alembic migration that:
1. Creates new tables (accounts, account_members, tenant_memberships, membership_grow_access)
2. Adds `platform_role` enum + column to users
3. Migrates existing data (each user → account + membership)
4. Drops old columns (tenant_id, role, is_platform_admin, is_support) in same migration

**Why**: Atomic migration prevents inconsistent state. Old columns are fully redundant after data migration.
**Risk**: Large migration. Mitigated by running in transaction (PostgreSQL DDL is transactional).

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Large migration on production DB | Potential downtime | PostgreSQL DDL is transactional; test on staging first |
| JWT token grows slightly | Marginal latency increase | Still under 1KB; no practical impact |
| Breaking API contract | Frontend/mobile clients break | Version the auth response; deploy API + frontend together |
| Grow-scope check on every request | Performance | Only queries `membership_grow_access` when `gs` is non-null in JWT (pre-computed at token issue) |
| Support role can see all data | Privacy concern | Audit logging for all support access; support cannot export/download bulk data |

## Migration Plan

### Phase 1: Schema + Models (non-breaking)
1. Create new tables alongside existing ones
2. Add `platform_role` column with default `'user'`
3. Backfill: `is_platform_admin=True` → `'super_admin'`, `is_support=True` → `'support'`
4. Backfill: For each user, create Account (named after their tenant) + AccountMember(role='owner') + TenantMembership(role mapped from users.role)

### Phase 2: Auth Middleware Swap
1. Deploy new middleware that reads from new tables but falls back to old columns
2. Validate in staging
3. Remove fallback once confirmed

### Phase 3: Drop Old Columns
1. Remove `users.tenant_id`, `users.role`, `users.is_platform_admin`, `users.is_support`
2. Remove `tenants.stripe_customer_id`, `tenants.stripe_subscription_id` (moved to accounts)

**Note**: For this implementation, we'll execute all phases in a single migration since we control the full deploy pipeline.

## Open Questions
- None — requirements are fully specified by the user.
