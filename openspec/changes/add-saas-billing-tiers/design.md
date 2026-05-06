## Context
Tendril's billing has 3 tiers with flat pricing only. The market expects flexible billing (usage-based is standard for dev tools and SaaS). We also need a permanently free tier that doesn't feel crippled — it should be genuinely useful for a single-tent home grower.

## Goals / Non-Goals
- **Goals**: 5 tiers (Free→Enterprise), 3 billing models (flat/usage/PAYG), usage tracking, overage billing, upgrade/downgrade with proration, enterprise contact-sales flow
- **Non-Goals**: Multi-currency (future), invoicing/NET-30 (enterprise only, manual), reseller/affiliate billing

## Decisions

### Decision: Free tier is permanently free, genuinely useful
A home grower with 1 tent and a few plants should never need to pay. The Free tier supports 1 grow space, 4 plants, 2 sensors, 10 AI analyses/month. This is a real product, not a demo.

**Rationale:** Generous free tiers drive adoption. Users upgrade when they grow (literally).

### Decision: Breakpoints based on real growing patterns
| Pattern | Tier |
|---------|------|
| First tent, learning | Free |
| 2-3 tents, getting serious | Hobby |
| Dedicated grow room, full automation | Pro |
| Multiple rooms, employees, compliance | Commercial |
| Warehouse/greenhouse operation | Enterprise |
| Full isolation, custom domain, managed by Trec-Tor | Dedicated Hosting |

### Decision: Three billing models, user chooses
Not everyone wants the same billing structure:
- **Flat**: Predictable cost, most users (especially hobbyists)
- **Tier + Usage**: Base subscription with overage for AI/storage-heavy users
- **PAYG**: Developers, API consumers, intermittent/seasonal growers

Users can switch models at any time (takes effect next billing period).

### Decision: Soft limits + upgrade prompt, not hard blocks
When users hit a limit:
1. 80%: Yellow banner "Approaching limit"
2. 100%: Modal with upgrade CTA, but existing data is NOT locked
3. Over-limit actions blocked (can't add 5th grow on Free), existing data accessible

**Rationale:** Never punish users for being successful. Make upgrade the obvious easy path.

### Decision: Downgrade grace period
When downgrading, user gets 7 days to bring usage under new limits. After that, excess resources are archived (read-only), not deleted. User can upgrade again to restore access.

## Risks / Trade-offs
- **Risk**: PAYG users with no usage still consume infra → **Mitigation**: Monthly minimum of $1 for PAYG (or just accept the cost for potential future conversion)
- **Risk**: Complex pricing confuses users → **Mitigation**: Default to Flat (simplest), only show PAYG/Usage on "More Options" expansion
- **Risk**: Overage billing disputes → **Mitigation**: Clear usage dashboard, alerts before overage, transparent per-unit pricing

## Migration Plan
1. Rename `grower` → `hobby` in DB (preserving subscriptions)
2. Existing `pro` and `commercial` unchanged
3. Add `free` as default for unsubscribed tenants (already the case)
4. Add `enterprise` as manual-assignment tier
5. Add `dedicated` as manual-assignment tier (provisioned by Trec-Tor ops)
6. Existing env-based PRICE_IDS continue working until provider adapter migration completes

## Dedicated Hosting Architecture
Each dedicated client gets:
```
cluster: k3s (3-node minimum) or namespace in managed k8s
├── tendril-api (2+ replicas)
├── tendril-web (2+ replicas)
├── tendril-mqtt-worker (1+ replicas)
├── tendril-scheduler (1 replica, leader-elected)
├── postgresql (dedicated instance, daily WAL backups)
├── minio (dedicated bucket, cross-region replication)
├── emqx (dedicated broker)
├── ingress (custom domain + auto-TLS via cert-manager)
└── monitoring (Prometheus + Grafana, client-visible dashboard)
```
Provisioning automated via Terraform module. Monthly retainer invoiced separately (not through Stripe — manual contract + invoice or custom Stripe subscription).
