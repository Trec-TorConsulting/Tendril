# Change: Add 5-Tier Billing System with Flat, Usage, and PAYG Models

## Why
The current billing has only 3 hardcoded tiers (grower/pro/commercial) with flat pricing only. We need 5 tiers (Free/Hobby/Pro/Commercial/Enterprise) with three billing models: flat subscription, tier + usage overage, and pure pay-as-you-go. Free tier never expires — it's the entry point for basic home users.

## What Changes
- Expand from 3 to 5 tiers with clear breakpoints
- Three billing models selectable by user: Flat, Tier+Usage, Pay As You Go
- Free tier: permanent, never expires, generous enough for 1-grow beginners
- Usage tracking: AI analyses, storage, devices, automations
- Overage pricing for Tier+Usage model
- Per-unit pricing for PAYG model
- Annual billing option with 20% discount
- Enterprise: custom pricing, contact sales flow
- Feature gate definitions per tier (what's locked/unlocked)
- Upgrade/downgrade proration
- **BREAKING**: `tenant.plan` values change from grower/pro/commercial to free/hobby/pro/commercial/enterprise

## Impact
- Affected specs: billing capability
- Affected code: `api/app/billing/`, `api/app/auth/middleware.py` (TierGate), pricing page, settings
- Migration: `grower` → `hobby`, existing `pro` and `commercial` unchanged, no `enterprise` existing customers

## Tier Definitions

### Free (Seedling) — $0/forever
**Target**: First-time home grower, just starting out, single tent/plant
| Feature | Limit |
|---------|-------|
| Grow Spaces | 1 |
| Plants/Buckets | 4 |
| Devices (sensors) | 2 |
| AI Health Analyses | 10/month |
| Storage (photos) | 1 GB |
| Team Members | 1 (just you) |
| Automations | 2 |
| Data Retention | 90 days |
| Support | Knowledge Base only |
| Journal Entries | 50/month |
| Integrations | 1 |

### Hobby (Sprout) — $9.99/mo or $95.90/yr
**Target**: Home grower with multiple grows, wants more AI help
| Feature | Limit |
|---------|-------|
| Grow Spaces | 3 |
| Plants/Buckets | 15 |
| Devices | 5 |
| AI Health Analyses | 50/month |
| Storage | 5 GB |
| Team Members | 1 |
| Automations | 10 |
| Data Retention | 1 year |
| Support | KB + Email |
| Journal Entries | Unlimited |
| Integrations | 3 |
| Data Export | CSV |

### Pro (Canopy) — $29.99/mo or $287.90/yr
**Target**: Serious cultivator, multiple rooms, wants full automation
| Feature | Limit |
|---------|-------|
| Grow Spaces | Unlimited |
| Plants/Buckets | Unlimited |
| Devices | 20 |
| AI Health Analyses | 200/month |
| Storage | 25 GB |
| Team Members | 5 |
| Automations | 50 |
| Data Retention | 2 years |
| Support | KB + Email + Priority |
| Journal Entries | Unlimited |
| Integrations | Unlimited |
| Data Export | CSV + ZIP + API |
| Custom Grow Types | Yes |
| API Keys | 3 |
| Live Chat | Yes |

### Commercial (Grove) — $79.99/mo or $767.90/yr
**Target**: Small business, multiple facilities, team collaboration
| Feature | Limit |
|---------|-------|
| Grow Spaces | Unlimited |
| Plants/Buckets | Unlimited |
| Devices | 100 |
| AI Health Analyses | 1000/month |
| Storage | 100 GB |
| Team Members | 25 |
| Automations | Unlimited |
| Data Retention | 5 years |
| Support | All channels + Priority |
| Journal Entries | Unlimited |
| Integrations | Unlimited |
| Data Export | All formats + scheduled |
| Custom Grow Types | Yes + submit to registry |
| API Keys | 10 |
| Audit Trail | Yes |
| Advanced Analytics | Yes |
| White-label Reports | Yes |

### Enterprise (Forest) — Custom pricing
**Target**: Large operations, multi-site, compliance needs
| Feature | Limit |
|---------|-------|
| Everything | Unlimited |
| Dedicated Support Rep | Yes |
| Custom SLA | Yes |
| On-premise option | Yes |
| SSO/SAML | Yes |
| Compliance reporting | Yes |
| Uptime SLA | 99.9% |
| Custom integrations | Yes |

### Dedicated Hosting (Greenhouse) — Custom pricing (monthly retainer)
**Target**: High-value clients who need complete infrastructure isolation, hosted by Trec-Tor Consulting
| Feature | Included |
|---------|----------|
| Everything | Unlimited |
| Isolated Server Cluster | Dedicated hardware (not shared) |
| Custom Domain | client.tendril.app or client's own domain |
| SSL/TLS | Auto-provisioned for custom domain |
| Dedicated Database | Isolated PostgreSQL instance |
| Dedicated Storage | Isolated MinIO/S3 bucket per client |
| Dedicated MQTT Broker | Client-only message bus |
| Geographic Region Choice | US, EU, or client-specified |
| Full Backups | Daily automated, 30-day retention, client-downloadable |
| Disaster Recovery | Cross-region replica, 4h RTO |
| White-Label Option | Client branding, custom logo, colors, email from-address |
| Uptime SLA | 99.95% with financial credit |
| Admin Access | Client gets platform admin role on their instance |
| Custom Integrations | Trec-Tor builds bespoke connectors on request |
| Priority Deployments | Client gets new features first (or can opt for stable channel) |
| Dedicated Support | Slack/Teams channel, named account manager |
| Data Sovereignty | Data never leaves specified region |
| Compliance | SOC2, HIPAA-ready, custom audit reports on request |

**Provisioning**: Trec-Tor Consulting spins up an isolated k3s/k8s cluster per client with:
- Separate namespace or separate cluster (client choice)
- DNS: `<client>.tendril.app` or client CNAME
- Automated via Terraform/Ansible playbook
- Monthly retainer covers infra + support + SLA

## Billing Models

### Flat (Default)
Simple monthly/annual subscription. You get exactly what your tier includes. If you hit a limit, you're prompted to upgrade.

### Tier + Usage Overage
Base tier subscription + pay extra for what you exceed:
| Metric | Overage Price |
|--------|--------------|
| AI Analyses | $0.05/analysis over limit |
| Storage | $0.50/GB over limit |
| Devices | $1.00/device over limit |
| Team Members | $5.00/member over limit |

### Pay As You Go
No base subscription, pay only for consumption:
| Metric | Unit Price |
|--------|-----------|
| AI Analyses | $0.10/analysis |
| Storage | $1.00/GB/month |
| Devices | $2.00/device/month |
| Grow Spaces | $5.00/space/month |
| Automations | $0.50/automation/month |

PAYG includes all features (no feature locks), just usage-based.

## Upgrade/Downgrade Rules
- **Upgrade**: Immediate, prorated charge for remaining period
- **Downgrade**: Takes effect at end of current billing period
- **Over-limit on downgrade**: Grace period (7 days) to reduce usage, then oldest items archived (not deleted)
- **Free → Paid**: No trial, just upgrade whenever ready
- **Enterprise**: Contact sales → custom proposal → manual activation
