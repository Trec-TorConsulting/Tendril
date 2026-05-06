## 1. Database & Models
- [ ] 1.1 Create `billing_plans` table migration
- [ ] 1.2 Create `billing_plan_prices` table migration (provider price ID mapping)
- [ ] 1.3 Create `billing_usage_records` table migration
- [ ] 1.4 Create SQLAlchemy models: `BillingPlan`, `BillingPlanPrice`, `BillingUsageRecord`
- [ ] 1.5 Seed migration: insert 5 default plans (Free, Hobby, Pro, Commercial, Enterprise) with sensible feature limits
- [ ] 1.6 Migration to populate `billing_plan_prices` from existing STRIPE_PRICE_* env vars

## 2. Plan CRUD API
- [ ] 2.1 Create `api/app/billing/plans.py` — plan CRUD endpoints (admin-only)
- [ ] 2.2 Endpoints: list plans, get plan, create plan, update plan, archive plan
- [ ] 2.3 Endpoints: list plan prices (per provider), trigger sync to provider
- [ ] 2.4 Endpoint: duplicate plan (for creating variants)
- [ ] 2.5 Public endpoint: list active public plans (for pricing page, no auth required)

## 3. Bidirectional Sync Engine
- [ ] 3.1 Create `api/app/billing/sync.py` — sync orchestrator
- [ ] 3.2 Implement push_plan_to_provider(plan, provider) — creates/updates product + price in external platform
- [ ] 3.3 Implement pull_plans_from_provider(provider) — fetches products/prices and reconciles
- [ ] 3.4 Implement conflict detection + resolution (last-write-wins with audit entry)
- [ ] 3.5 Add scheduler task: periodic plan reconciliation (every 6 hours)
- [ ] 3.6 Webhook handler: provider plan/price change events trigger pull

## 4. Usage Metering
- [ ] 4.1 Create `api/app/billing/metering.py` — usage tracking service
- [ ] 4.2 Implement: record_usage(tenant_id, metric, quantity)
- [ ] 4.3 Implement: get_usage_summary(tenant_id, period) → current usage vs limits
- [ ] 4.4 Implement: check_limit(tenant_id, metric) → bool (under limit)
- [ ] 4.5 Implement: report_usage_to_provider(tenant_id, period) — push metered usage for billing
- [ ] 4.6 Add scheduler task: daily usage aggregation + provider reporting
- [ ] 4.7 Integrate with TierGate middleware: use billing_plans table instead of hardcoded limits

## 5. Refactor TierGate
- [ ] 5.1 Update `TierGate` middleware to read limits from `billing_plans` table
- [ ] 5.2 Remove hardcoded plan limits from code
- [ ] 5.3 Add usage-based gating (check current period usage against plan limit)
- [ ] 5.4 Return usage info in rate-limit headers (X-Usage-Remaining, X-Usage-Limit)

## 6. Admin UI
- [ ] 6.1 Build plan management page (`/admin/billing/plans`) — CRUD table with inline editing
- [ ] 6.2 Plan editor: name, slug, description, pricing, billing model selector
- [ ] 6.3 Plan editor: feature limits (grows, devices, AI, storage, team, automations)
- [ ] 6.4 Plan editor: feature flags (JSON editor for custom gates)
- [ ] 6.5 Provider sync status display: per-plan, per-provider (synced/pending/error)
- [ ] 6.6 Manual sync button: push single plan or pull all from provider
- [ ] 6.7 Usage dashboard: per-tenant usage overview, overage alerts

## 7. Public Pricing Page
- [ ] 7.1 Update pricing page to fetch plans from API (not hardcoded)
- [ ] 7.2 Show billing model options (flat / usage / PAYG) as tabs
- [ ] 7.3 Monthly/Annual toggle with annual discount display
- [ ] 7.4 Feature comparison table auto-generated from plan feature limits
- [ ] 7.5 PWA: pricing page works offline (cached plan data)

## 8. Tests
- [ ] 8.1 Unit tests: plan CRUD, sync engine (mocked providers)
- [ ] 8.2 Unit tests: usage metering, limit checking
- [ ] 8.3 Integration tests: TierGate with DB-driven limits
- [ ] 8.4 Integration tests: bidirectional sync with mocked Stripe
- [ ] 8.5 Frontend tests: plan admin UI, pricing page, usage display
