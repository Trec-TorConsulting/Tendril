## 1. Database & Tier Configuration
- [ ] 1.1 Update `billing_plans` seed migration with 5 tiers + all feature limits
- [ ] 1.2 Add billing_model column to tenant/subscription (flat, tiered_usage, pay_as_you_go)
- [ ] 1.3 Create `billing_overage_rates` table (metric, plan_id, unit_price_cents)
- [ ] 1.4 Create `billing_payg_rates` table (metric, unit_price_cents)
- [ ] 1.5 Seed overage rates and PAYG rates per the defined pricing
- [ ] 1.6 Migration: rename existing plan slugs (grower → hobby), preserve subscription continuity

## 2. TierGate Enhancement
- [ ] 2.1 Update TierGate middleware to support all 5 tiers from DB
- [ ] 2.2 Implement feature-flag gating (features_json check per endpoint)
- [ ] 2.3 Implement usage-limit gating with billing_model awareness
- [ ] 2.4 For PAYG: no feature locks, only track usage
- [ ] 2.5 Add `X-Plan`, `X-Usage-{metric}`, `X-Limit-{metric}` response headers
- [ ] 2.6 Grace period logic for downgrades (7-day window before archival)

## 3. Usage Tracking
- [ ] 3.1 Instrument AI analysis endpoint: increment usage counter
- [ ] 3.2 Instrument storage uploads: track cumulative storage per tenant
- [ ] 3.3 Instrument device registration: track active device count
- [ ] 3.4 Instrument automation creation: track active automations
- [ ] 3.5 Instrument team member invites: track active members
- [ ] 3.6 Create usage summary endpoint: GET /billing/usage → current period metrics vs limits

## 4. Overage & PAYG Billing
- [ ] 4.1 Scheduler task: end-of-period usage aggregation
- [ ] 4.2 For Tier+Usage: calculate overage, create invoice line items via payment provider
- [ ] 4.3 For PAYG: calculate total usage, create invoice via payment provider
- [ ] 4.4 Usage threshold alerts: notify at 80% and 100% of limit
- [ ] 4.5 Soft limit vs hard limit: warn at soft, block at hard (configurable per metric)

## 5. Upgrade/Downgrade Flow
- [ ] 5.1 Implement upgrade endpoint: immediate plan change + prorated charge
- [ ] 5.2 Implement downgrade endpoint: schedule change at period end
- [ ] 5.3 Implement billing model switch: flat ↔ tiered_usage ↔ payg
- [ ] 5.4 Downgrade limit check: warn user of features/data they'll lose access to
- [ ] 5.5 Grace period handler: after 7 days over-limit, archive excess (grows → read-only)
- [ ] 5.6 Enterprise inquiry endpoint: collect requirements, email to sales
- [ ] 5.7 Dedicated hosting inquiry endpoint: collect client info, infra requirements, preferred region

## 6. Dedicated Hosting Provisioning
- [ ] 6.1 Create Terraform module for dedicated client cluster (k3s 3-node)
- [ ] 6.2 Ansible playbook: deploy Tendril stack to dedicated cluster
- [ ] 6.3 Custom domain setup: cert-manager ClusterIssuer + Ingress template with client domain
- [ ] 6.4 Isolated PostgreSQL provisioning (dedicated instance, not shared)
- [ ] 6.5 Isolated MinIO bucket + cross-region replication config
- [ ] 6.6 Isolated EMQX broker deployment
- [ ] 6.7 Client monitoring stack (Prometheus + Grafana with client-visible dashboard)
- [ ] 6.8 Automated backup pipeline (daily DB dump + WAL archiving, 30-day retention)
- [ ] 6.9 Admin API: provision dedicated tenant (mark as `dedicated` plan, set custom domain, assign cluster)
- [ ] 6.10 White-label config: per-tenant branding (logo URL, primary color, app name, email from-address)
- [ ] 6.11 DNS automation: create CNAME record via Cloudflare API (or manual instructions for client-owned DNS)
- [ ] 6.12 Client admin portal: system status, backup downloads, usage metrics, support channel

## 7. Frontend — Pricing Page
- [ ] 7.1 Redesign pricing page with 6 tiers in responsive card layout (Dedicated as premium callout)
- [ ] 7.2 Billing model tabs: Flat (default) / Usage-Based / Pay As You Go
- [ ] 7.3 Monthly/Annual toggle with savings badge
- [ ] 7.4 Feature comparison table (auto-generated from plan data)
- [ ] 7.5 "Current Plan" badge for logged-in users
- [ ] 7.6 Enterprise CTA: "Contact Sales" → inquiry form
- [ ] 7.7 Dedicated Hosting CTA: "Get a Quote" → dedicated inquiry form (infra needs, region, domain)
- [ ] 7.8 PWA: pricing cached offline, upgrade action queued if offline

## 8. Frontend — Billing Dashboard
- [ ] 8.1 Current plan card with tier name, billing model, next invoice date
- [ ] 8.2 Usage meters: visual progress bars for each metered resource
- [ ] 8.3 Usage history chart (30-day trend)
- [ ] 8.4 Upgrade/downgrade buttons with plan comparison modal
- [ ] 8.5 Billing model switcher with cost estimate
- [ ] 8.6 Invoice history table
- [ ] 8.7 Payment method display + update link (via provider portal)

## 9. Frontend — Limit Reached UX
- [ ] 9.1 Soft-limit warning banner (80% usage): "You're approaching your limit"
- [ ] 9.2 Hard-limit modal: "Upgrade to continue" with plan comparison
- [ ] 9.3 Feature-locked indicators (lock icon + "Available on Pro+")
- [ ] 9.4 Inline upgrade prompts at the point of friction (not just settings page)
- [ ] 9.5 PWA: limit warnings work offline (cached plan info)

## 10. Tests
- [ ] 10.1 Unit tests: TierGate with all 6 tiers and 3 billing models
- [ ] 10.2 Unit tests: usage tracking, overage calculation, PAYG calculation
- [ ] 10.3 Unit tests: upgrade/downgrade proration, grace period logic
- [ ] 10.4 Integration tests: end-to-end billing flow with mocked provider
- [ ] 10.5 Integration tests: dedicated provisioning scripts (dry-run mode)
- [ ] 10.6 Frontend tests: pricing page, billing dashboard, limit UX
- [ ] 10.7 E2E: free user → upgrade to Pro → use features → check usage
