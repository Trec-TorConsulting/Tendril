## 1. Database & Models — DONE
- [x] 1.1 Create `payment_providers` table migration
- [x] 1.2 Create `PaymentProvider` SQLAlchemy model in `api/app/billing/models.py`
- [x] 1.3 Add encryption/decryption helpers for provider config (Fernet with JWT secret as key)
- [x] 1.4 Migration to import existing STRIPE_* env vars into payment_providers table as initial Stripe row

## 2. Provider Adapter Base & Registry — DONE
- [x] 2.1 Create `api/app/billing/providers/base.py` — `BasePaymentProvider` ABC with all required methods
- [x] 2.2 Create `api/app/billing/providers/__init__.py` — provider registry
- [x] 2.3 Implement `get_active_provider()` helper in `api/app/billing/service.py`

## 3. Stripe Adapter — DONE
- [x] 3.1 Create `api/app/billing/providers/stripe_provider.py` — full implementation
- [x] 3.2 Implement: create_customer, create_checkout_session, create_portal_session
- [x] 3.3 Implement: create_subscription, cancel_subscription, update_subscription
- [x] 3.4 Implement: verify_webhook, sync_plan, get_payment_methods
- [x] 3.5 Implement: supported checkout methods (card, apple_pay, google_pay, link)
- [x] 3.6 Enable Apple Pay / Google Pay via Stripe Payment Element + automatic tax

## 4. PayPal Adapter — DONE
- [x] 4.1 Implement `api/app/billing/providers/paypal_provider.py` (OAuth2, subscriptions, webhooks)
- [x] 4.2 Implement OAuth2 token flow (client_id + secret → access token)
- [x] 4.3 Implement: create_customer (SHA256 email hash), create_checkout_session (Subscriptions API)
- [x] 4.4 Implement: create_subscription (Subscriptions API), cancel/update subscription
- [x] 4.5 Implement: verify_webhook (PayPal notification verification API)
- [x] 4.6 Implement: sync_plan (Products + Plans API)
- [x] 4.7 Implement: list_supported_checkout_methods (paypal, card, venmo)

## 5. Square Adapter — DONE
- [x] 5.1 Implement `api/app/billing/providers/square_provider.py`
- [x] 5.2 Implement OAuth2 flow (Square application credentials)
- [x] 5.3 Implement: create_customer (Customers API), create_checkout_session (Checkout API)
- [x] 5.4 Implement: create_subscription (Subscriptions API), cancel/update
- [x] 5.5 Implement: verify_webhook (Square signature verification)
- [x] 5.6 Implement: sync_plan (Catalog API — subscription plans)
- [x] 5.7 Implement: list_supported_checkout_methods (card, apple_pay, google_pay, cash_app)

## 6. Paddle Adapter — DONE
- [x] 6.1 Implement `api/app/billing/providers/paddle_provider.py`
- [x] 6.2 Implement API key auth (Paddle Billing API v2)
- [x] 6.3 Implement: create_customer, create_checkout_session (Paddle.js overlay URL)
- [x] 6.4 Implement: create_subscription, cancel/update subscription
- [x] 6.5 Implement: verify_webhook (Paddle signature + ts verification)
- [x] 6.6 Implement: sync_plan (Products + Prices API)
- [x] 6.7 Implement: list_supported_checkout_methods (card, paypal, apple_pay, google_pay, wire)

## 7. Refactor Existing Billing Routes — DONE
- [x] 7.1 `api/app/billing/routes.py` uses provider adapter pattern via `service.py`
- [x] 7.2 Webhook endpoint is provider-aware (`/webhook/{provider_type}`)
- [x] 7.3 Checkout flow passes supported methods for wallet pay
- [x] 7.4 Portal/management flow uses adapter

## 8. Admin API & UI — DONE
- [x] 8.1 Admin endpoints in `api/app/billing/provider_admin.py` (list, create, update, delete, test)
- [x] 8.2 Admin provider configuration page (`/platform/billing`)
- [x] 8.3 Provider setup: enter credentials → test connection → activate
- [x] 8.4 Connected status display in admin UI

## 9. Frontend Updates — DONE
- [x] 9.1 Billing settings show provider-agnostic checkout flow
- [x] 9.2 Apple Pay / Google Pay supported via Stripe Payment Element
- [x] 9.3 PWA billing flow functional
- [x] 9.4 Billing status page works with any provider

## 10. Tests — DONE
- [x] 10.1 Unit tests: PayPal adapter (mocked HTTP)
- [x] 10.2 Unit tests: Square adapter (mocked HTTP)
- [x] 10.3 Unit tests: Paddle adapter (mocked HTTP)
- [x] 10.4 Integration tests: provider registry, active provider resolution
- [x] 10.5 Integration tests: webhook verification per provider
- [x] 10.6 E2E: full checkout flow with Stripe test mode
