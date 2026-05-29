## Context
Tendril currently has hardcoded Stripe billing. This design introduces a provider adapter pattern allowing the platform operator to select and configure their preferred payment processor. Self-hosters can connect their own Stripe/PayPal/Square/Paddle account.

## Goals / Non-Goals
- **Goals**: Multi-provider support, encrypted config storage, bidirectional plan sync foundation, wallet payments as sub-methods, admin setup UI
- **Non-Goals**: Supporting obscure/regional processors (can be added later), cryptocurrency payments, custom payment forms (we use hosted checkout pages)

## Decisions

### Decision: Adapter pattern over SDK abstraction
Each provider has vastly different APIs. Rather than trying to normalize at the SDK level, each adapter implements a common interface with provider-specific HTTP calls. This is the same pattern as `BaseConnector` for integrations.

**Alternatives considered:**
- Universal payment SDK (e.g., `saloon`): Too abstract, poor TypeScript/webhook support
- Direct SDK per provider in routes: Current approach, doesn't scale

### Decision: One primary provider per platform
A Tendril deployment has ONE active payment provider at a time. Multiple can be configured (for migration), but new checkouts always route to the primary.

**Rationale:** Simplifies plan management, avoids split-brain subscription states.

### Decision: Wallet payments are provider features, not standalone
Apple Pay and Google Pay are not their own payment processors — they're checkout methods within Stripe/Paddle/Square. We enable them via the provider's payment element configuration.

### Decision: Config in DB, not env vars
Provider credentials stored encrypted in DB (like integration configs) so self-hosters can configure via admin UI without restart. Existing env vars auto-imported on migration.

## Risks / Trade-offs
- **Risk**: Provider API changes → **Mitigation**: Pin API versions, adapter isolation means one provider break doesn't affect others
- **Risk**: Webhook routing complexity → **Mitigation**: Each provider gets a unique webhook URL path (`/billing/webhook/{provider_type}`)
- **Risk**: Testing matrix grows → **Mitigation**: Mock-heavy unit tests per provider, only Stripe gets live E2E in CI

## Migration Plan
1. Add `payment_providers` table
2. Auto-import STRIPE_* env vars into a Stripe provider row (marked primary)
3. Refactor billing routes to go through adapter
4. Old env vars continue working as fallback during transition
5. Admin can then add/switch providers via UI

## Open Questions
- Should we support multiple currencies per provider? (Start with platform-wide default currency)
- Paddle handles tax/compliance automatically — do we want to surface that as a selling point for self-hosters?
