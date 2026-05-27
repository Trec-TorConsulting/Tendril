## 1. Database & Models — DONE
- [x] 1.1 Create `billing_plans` table migration
- [x] 1.2 Create `billing_plan_prices` table migration (provider price ID mapping)
- [x] 1.3 Create `billing_usage_records` table migration
- [x] 1.4 Create SQLAlchemy models: `BillingPlan`, `BillingPlanPrice`, `BillingUsageRecord` (+ BillingOverageRate, BillingPaygRate)
- [x] 1.5 Seed migration: insert default plans (Free, Hobby, Pro, Commercial, Enterprise, Dedicated) with feature limits
- [x] 1.6 Migration to populate `billing_plan_prices` from existing Stripe config

## 2. Plan CRUD API — DONE
- [x] 2.1 Create `api/app/billing/plans.py` — plan CRUD endpoints (admin-only)
- [x] 2.2 Endpoints: list plans, create plan, update plan, archive plan
- [x] 2.3 Endpoint: sync plan to provider
- [x] 2.4 Public endpoint: list active public plans (for pricing page, no auth required)

## 3. Bidirectional Sync Engine — DONE
- [x] 3.1 Plan sync: push plan to provider (creates Product + Price in Stripe)
- [x] 3.2 Webhook handler: provider plan/price change events trigger sync
- [x] 3.3 Implement pull_plans_from_provider(provider) — fetches and reconciles with DB
- [x] 3.4 Implement conflict detection + resolution (last-write-wins with audit entry)
- [x] 3.5 Add scheduler task: periodic plan reconciliation (every 6 hours)

## 4. Usage Metering — DONE
- [x] 4.1 Create `api/app/billing/metering.py` — usage tracking service
- [x] 4.2 Implement: record_usage(tenant_id, metric, quantity)
- [x] 4.3 Implement: get_usage_summary(tenant_id, period) → current usage vs limits
- [x] 4.4 Implement: check_limit(tenant_id, metric) → bool (under limit)
- [x] 4.5 Implement: report_usage_to_provider(subscription_id, metric, quantity) via adapter
- [x] 4.6 Integrate with TierGate: DB-driven limits with 60s TTL cache

## 5. TierGate — DONE
- [x] 5.1 `TierGate` reads limits from `billing_plans` table (via `tier_gate.py`)
- [x] 5.2 No hardcoded plan limits in code (all from DB)
- [x] 5.3 Usage-based gating: `require_usage_limit()`, `require_feature()`, `require_plan()`
- [x] 5.4 Returns usage info in error response (current, limit, metric)

## 6. Admin UI — DONE
- [x] 6.1 Plan management page (`/platform/billing`) — CRUD with sync
- [x] 6.2 Plan editor: name, slug, description, pricing, billing model
- [x] 6.3 Plan editor: feature limits (grows, devices, AI, storage, team, automations)
- [x] 6.4 Plan editor: feature flags (JSON)
- [x] 6.5 Provider sync status display
- [x] 6.6 Manual sync button per plan

## 7. Public Pricing Page — DONE
- [x] 7.1 Pricing page fetches from `/billing/plans/public` API (dynamic, no hardcoded PLANS)
- [x] 7.2 `getPublicPlans()` API client function added (no auth)
- [x] 7.3 Monthly/Annual toggle with annual discount display
- [x] 7.4 Feature list auto-generated from plan limits (formatLimit, planFeatures helpers)
- [x] 7.5 PWA: pricing page works offline (standard Next.js caching)

## 8. Tests — DONE
- [x] 8.1 Unit tests: provider registry, adapter instantiation, contract verification
- [x] 8.2 Unit tests: sync module importable, metering importable
- [x] 8.3 Integration tests: TierGate with DB-driven limits (in test_billing.py)
- [x] 8.4 Integration tests: webhook rejection with invalid signature
- [x] 8.5 E2E tests: billing status, checkout auth, portal auth
