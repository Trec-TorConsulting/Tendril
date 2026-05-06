# Change: Add Plan Management Admin with Bidirectional Sync

## Why
Plans/products/subscriptions are currently hardcoded as env vars mapped to Stripe Price IDs. The platform operator needs a proper admin UI to create, price, and manage subscription plans — with bidirectional sync to the connected payment provider. Plans created in Tendril push to Stripe; plans modified in Stripe sync back to Tendril.

## What Changes
- New `billing_plans` table storing the canonical plan definitions
- New `billing_plan_prices` table for per-provider price ID mapping
- Admin CRUD UI for plans at `/admin/billing/plans`
- Bidirectional sync engine: Tendril → Provider and Provider → Tendril
- Plan feature gates defined per plan (grows, devices, AI calls, storage, team members)
- Support for one-time products (marketplace items, add-ons) in addition to subscriptions
- Usage metering records for overage-based billing
- **BREAKING**: `PRICE_IDS` dict removed; plans resolved from DB

## Impact
- Affected specs: billing (new capability)
- Affected code: `api/app/billing/`, `api/app/auth/middleware.py` (TierGate), admin routes, pricing page
- Migration: Existing 3 plans (grower/pro/commercial) seeded into billing_plans table

## Design Decisions

### Plan Schema
```sql
CREATE TABLE billing_plans (
    id UUID PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,       -- "free", "hobby", "pro", "commercial", "enterprise"
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT true,         -- shown on pricing page
    sort_order INTEGER DEFAULT 0,
    billing_model VARCHAR(20) NOT NULL,     -- "flat", "tiered_usage", "pay_as_you_go"
    base_price_cents INTEGER,               -- monthly base price in cents (0 for free)
    annual_price_cents INTEGER,             -- annual price (optional discount)
    currency VARCHAR(3) DEFAULT 'usd',
    -- Feature limits (NULL = unlimited)
    max_grows INTEGER,
    max_devices INTEGER,
    max_team_members INTEGER,
    max_ai_analyses_month INTEGER,
    max_storage_gb INTEGER,
    max_automations INTEGER,
    included_support_tier VARCHAR(20),      -- "community", "email", "priority", "dedicated"
    features_json JSONB,                    -- flexible feature flags
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE billing_plan_prices (
    id UUID PRIMARY KEY,
    plan_id UUID REFERENCES billing_plans(id),
    provider_type VARCHAR(50) NOT NULL,     -- "stripe", "paypal", "square", "paddle"
    external_product_id VARCHAR(255),       -- provider's product ID
    external_price_id VARCHAR(255),         -- provider's price/plan ID
    external_annual_price_id VARCHAR(255),  -- annual variant
    sync_status VARCHAR(20) DEFAULT 'pending',  -- pending, synced, error
    last_synced_at TIMESTAMP,
    sync_error TEXT
);

CREATE TABLE billing_usage_records (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    plan_id UUID REFERENCES billing_plans(id),
    metric VARCHAR(50) NOT NULL,            -- "ai_analyses", "storage_gb", "devices"
    quantity INTEGER NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    reported_to_provider BOOLEAN DEFAULT false,
    created_at TIMESTAMP
);
```

### Bidirectional Sync
1. **Tendril → Provider**: When admin creates/updates a plan, push product + price to provider
2. **Provider → Tendril**: Webhook + periodic poll reconciles changes made in provider dashboard
3. **Conflict resolution**: Last-write-wins with audit log; admin gets notification of external changes

### Billing Models
| Model | How it works |
|-------|-------------|
| Flat | Fixed monthly/annual price per tier |
| Tiered + Usage | Base tier price + overage charges for exceeding limits |
| Pay As You Go | No base; charged per unit consumed (AI calls, storage, devices) |

Users select their preferred model during signup. Default is Flat.
