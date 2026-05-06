## 1. Database & Models
- [ ] 1.1 Create `payment_providers` table migration (id, provider_type, display_name, is_active, is_primary, config_encrypted, webhook_secret_encrypted, supported_methods, created_at, updated_at)
- [ ] 1.2 Create `PaymentProvider` SQLAlchemy model in `api/app/billing/models.py`
- [ ] 1.3 Add encryption/decryption helpers for provider config (reuse pattern from integrations)
- [ ] 1.4 Migration to import existing STRIPE_* env vars into payment_providers table as initial Stripe row

## 2. Provider Adapter Base & Registry
- [ ] 2.1 Create `api/app/billing/providers/base.py` — `BasePaymentProvider` ABC with all required methods
- [ ] 2.2 Create `api/app/billing/providers/__init__.py` — provider registry with `@register_provider` decorator
- [ ] 2.3 Implement `get_active_provider()` helper that resolves the primary provider for the platform

## 3. Stripe Adapter
- [ ] 3.1 Create `api/app/billing/providers/stripe_provider.py` — full implementation
- [ ] 3.2 Implement: create_customer, create_checkout_session, create_portal_session
- [ ] 3.3 Implement: create_subscription, cancel_subscription, update_subscription
- [ ] 3.4 Implement: verify_webhook, sync_plans, get_payment_methods
- [ ] 3.5 Implement: list_supported_checkout_methods (card, apple_pay, google_pay, link)
- [ ] 3.6 Enable Apple Pay / Google Pay via Stripe Payment Element configuration

## 4. PayPal Adapter
- [ ] 4.1 Create `api/app/billing/providers/paypal_provider.py`
- [ ] 4.2 Implement OAuth2 token flow (client_id + secret → access token)
- [ ] 4.3 Implement: create_customer (via PayPal vault), create_checkout_session (Orders API)
- [ ] 4.4 Implement: create_subscription (Subscriptions API), cancel/update subscription
- [ ] 4.5 Implement: verify_webhook (PayPal signature verification)
- [ ] 4.6 Implement: sync_plans (Products + Plans API)
- [ ] 4.7 Implement: list_supported_checkout_methods (paypal, card, venmo)

## 5. Square Adapter
- [ ] 5.1 Create `api/app/billing/providers/square_provider.py`
- [ ] 5.2 Implement OAuth2 flow (Square application credentials)
- [ ] 5.3 Implement: create_customer (Customers API), create_checkout_session (Checkout API)
- [ ] 5.4 Implement: create_subscription (Subscriptions API), cancel/update
- [ ] 5.5 Implement: verify_webhook (Square signature verification)
- [ ] 5.6 Implement: sync_plans (Catalog API — subscription plans)
- [ ] 5.7 Implement: list_supported_checkout_methods (card, apple_pay, google_pay, cash_app)

## 6. Paddle Adapter
- [ ] 6.1 Create `api/app/billing/providers/paddle_provider.py`
- [ ] 6.2 Implement API key auth (Paddle Classic or Billing API)
- [ ] 6.3 Implement: create_customer, create_checkout_session (Paddle.js overlay URL)
- [ ] 6.4 Implement: create_subscription, cancel/update subscription
- [ ] 6.5 Implement: verify_webhook (Paddle signature + ts verification)
- [ ] 6.6 Implement: sync_plans (Products + Prices API)
- [ ] 6.7 Implement: list_supported_checkout_methods (card, paypal, apple_pay, google_pay, wire)

## 7. Refactor Existing Billing Routes
- [ ] 7.1 Refactor `api/app/billing/routes.py` to use `get_active_provider()` instead of direct Stripe calls
- [ ] 7.2 Make webhook endpoint provider-aware (route by provider_type path param or header)
- [ ] 7.3 Update checkout flow to pass supported_methods for wallet pay enablement
- [ ] 7.4 Update portal/management flow through adapter

## 8. Admin API & UI
- [ ] 8.1 Create admin endpoints: list providers, add provider, update provider, set primary, test connection
- [ ] 8.2 Build admin provider configuration page (`/admin/billing/providers`)
- [ ] 8.3 Provider setup wizard: enter credentials → test connection → activate
- [ ] 8.4 Show connected status, supported methods, last webhook received

## 9. Frontend Updates
- [ ] 9.1 Update billing settings to show provider-agnostic checkout flow
- [ ] 9.2 Show Apple Pay / Google Pay buttons when provider supports them
- [ ] 9.3 PWA: ensure payment sheet APIs work in standalone mode
- [ ] 9.4 Update billing status page to work with any provider

## 10. Tests
- [ ] 10.1 Unit tests: each provider adapter (mocked HTTP)
- [ ] 10.2 Integration tests: provider registry, active provider resolution
- [ ] 10.3 Integration tests: webhook verification per provider
- [ ] 10.4 Frontend tests: provider-agnostic billing UI
- [ ] 10.5 E2E: full checkout flow with Stripe test mode
