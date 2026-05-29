## Context
Plans are hardcoded. Self-hosters need to define their own pricing. SaaS operators need to experiment with tiers. The payment provider adapter (separate proposal) provides the plumbing; this proposal defines what gets pushed through it.

## Goals / Non-Goals
- **Goals**: Admin can CRUD plans in UI, plans sync to payment provider, usage metering, billing model flexibility (flat/usage/PAYG)
- **Non-Goals**: Multi-currency (future), coupon/discount management (use provider dashboard), tax calculation (delegated to provider)

## Decisions

### Decision: Plans in Tendril DB are source of truth
Both sides can edit (bidirectional), but Tendril DB is canonical. Provider-side changes are pulled and reconciled with last-write-wins.

**Rationale:** Platform operator may not have provider dashboard access (self-hoster using someone else's keys). Tendril admin must always work.

### Decision: Three billing models, user selects at signup
- **Flat**: Simple subscription, most users
- **Tier + Usage**: Base plan with overage (AI-heavy users)
- **Pay As You Go**: No base, per-unit (API consumers, developers)

Users see all 3 as options. Default is Flat. Can switch models at any time (prorated).

### Decision: Feature limits in plan table, not code
The `billing_plans` table holds all limits. TierGate middleware reads from DB at request time (with 60s cache). No code changes needed to adjust limits.

### Decision: Usage metering is internal-first
We track usage ourselves (AI calls, storage, devices) and optionally report to the payment provider for overage billing. This means free-tier limits work even without a payment provider connected.

## Risks / Trade-offs
- **Risk**: Sync conflicts between Tendril and provider → **Mitigation**: Audit log of all sync operations, admin notification on conflict
- **Risk**: Stale plan cache → **Mitigation**: 60s TTL, cache bust on plan update webhook
- **Risk**: Usage tracking overhead → **Mitigation**: Batch inserts, daily aggregation, lightweight counter per request

## Default Plan Configuration

| Plan | Monthly | Grows | Devices | AI/mo | Storage | Team | Support |
|------|---------|-------|---------|-------|---------|------|---------|
| Free | $0 | 1 | 2 | 10 | 1 GB | 1 | Community |
| Hobby | $9.99 | 3 | 5 | 50 | 5 GB | 1 | Email |
| Pro | $29.99 | ∞ | 20 | 200 | 25 GB | 5 | Priority |
| Commercial | $79.99 | ∞ | 100 | 1000 | 100 GB | 25 | Priority |
| Enterprise | Custom | ∞ | ∞ | ∞ | ∞ | ∞ | Dedicated |

Annual discount: 20% (2 months free).
