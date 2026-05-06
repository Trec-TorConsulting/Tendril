# Change: Add Multi-Provider Payment Adapter System

## Why
The current billing module is hardcoded to Stripe. Self-hosters and SaaS operators need to choose their preferred payment processor. We need a pluggable adapter pattern (like our integration connectors) that lets the platform owner connect Stripe, PayPal, Square, or Paddle — with Apple Pay/Google Pay as checkout methods within those providers.

## What Changes
- New `PaymentProvider` abstract base class with adapter pattern
- Provider adapters: Stripe, PayPal, Square, Paddle
- Apple Pay / Google Pay exposed as checkout methods within primary provider
- Provider configuration stored encrypted in DB (like integration configs)
- Admin UI to connect/disconnect payment providers
- Existing hardcoded Stripe billing refactored into the adapter
- Wallet-based payments (Apple/Google Pay) configured as sub-methods
- **BREAKING**: `STRIPE_*` env vars become optional; provider config moves to DB

## Impact
- Affected specs: billing (new capability)
- Affected code: `api/app/billing/`, `web/src/app/dashboard/settings/billing/`, admin routes
- Migration: Existing Stripe configs auto-imported into new provider table on first run

## Design Decisions

### Provider Adapter Pattern
```
BasePaymentProvider (ABC)
├── StripeProvider         (checkout, subscriptions, portal, webhooks)
├── PayPalProvider         (orders, subscriptions, webhooks)
├── SquareProvider         (subscriptions, invoices, webhooks)
└── PaddleProvider         (checkout overlay, subscriptions, webhooks)
```

Each adapter implements:
- `create_customer(email, metadata)` → external customer ID
- `create_checkout_session(customer_id, plan, success_url, cancel_url)` → redirect URL
- `create_portal_session(customer_id, return_url)` → management URL
- `create_subscription(customer_id, plan_id)` → subscription object
- `cancel_subscription(subscription_id)` → confirmation
- `update_subscription(subscription_id, new_plan_id)` → updated object
- `verify_webhook(payload, signature, secret)` → parsed event
- `sync_plans(plans: list[PlanConfig])` → synced IDs
- `get_payment_methods(customer_id)` → list of methods
- `list_supported_checkout_methods()` → ["card", "apple_pay", "google_pay", ...]

### Wallet Payments
Apple Pay and Google Pay are NOT standalone providers — they're checkout methods within Stripe/Paddle/Square. The adapter exposes `list_supported_checkout_methods()` and the checkout session enables the appropriate wallet types based on provider capabilities.

### Provider Config Storage
```sql
CREATE TABLE payment_providers (
    id UUID PRIMARY KEY,
    provider_type VARCHAR(50) NOT NULL,  -- stripe, paypal, square, paddle
    display_name VARCHAR(100),
    is_active BOOLEAN DEFAULT false,
    is_primary BOOLEAN DEFAULT false,   -- only one primary at a time
    config_encrypted BYTEA NOT NULL,    -- encrypted JSON (API keys, secrets)
    webhook_secret_encrypted BYTEA,
    supported_methods TEXT[],           -- ["card", "apple_pay", "google_pay"]
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Tenant → Provider Resolution
- Platform has one primary payment provider (set by admin)
- All checkouts route through the primary provider
- Multiple providers allowed for migration scenarios (old subs stay on old provider)

## Tier Breakdown (5 tiers)
| Tier | Price | Target |
|------|-------|--------|
| Free | $0 | Hobbyist, 1 grow space |
| Hobby | $9.99/mo | Home grower, ≤3 grows |
| Pro | $29.99/mo | Serious cultivator, unlimited grows |
| Commercial | $79.99/mo | Small business, team features |
| Enterprise | Custom | Large operations, dedicated support |
