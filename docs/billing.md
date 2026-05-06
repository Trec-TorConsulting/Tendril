# Billing & Pricing

Tendril uses a tiered subscription model with usage-based limits. This document covers plans, payment methods, and billing management.

## Plans

| Plan | Price | Grows | Devices | AI Analyses/mo | Storage | Key Features |
|------|-------|-------|---------|----------------|---------|--------------|
| **Seedling** (Free) | $0 | 1 | 2 | 10 | 1 GB | Basic grow tracking |
| **Hobby** | $9.99/mo | 5 | 10 | 50 | 10 GB | Automations, integrations |
| **Pro** | $29.99/mo | 25 | 50 | 500 | 100 GB | Cost/ROI tracking, priority support |
| **Commercial** | $79.99/mo | 100 | 200 | Unlimited | 500 GB | API access, audit logs, custom grow types, 5 team members |
| **Enterprise** | $249.99/mo | Unlimited | Unlimited | Unlimited | Unlimited | White-label, SSO/SAML, 25 team members, dedicated support |
| **Dedicated** | Custom | Unlimited | Unlimited | Unlimited | Unlimited | Own infrastructure, custom domain, on-premise |

## Payment Methods

Tendril supports multiple payment providers and methods:

### Stripe (Default)
- Credit/debit cards (Visa, Mastercard, Amex, Discover)
- Apple Pay
- Google Pay
- Link (Stripe's one-click checkout)

### PayPal
- PayPal balance
- Credit/debit cards via PayPal
- Venmo

### Square
- Credit/debit cards
- Apple Pay
- Google Pay
- Cash App Pay

### Paddle
- Credit/debit cards
- PayPal
- Apple Pay
- Google Pay
- Wire transfer

## Managing Your Subscription

### Upgrading
1. Go to **Dashboard → Billing**
2. Select your desired plan
3. Complete checkout via the payment provider
4. Your plan activates immediately

### Downgrading
1. Go to **Dashboard → Billing** → **Manage Subscription**
2. Change your plan in the billing portal
3. The downgrade takes effect at the end of your current billing period
4. Features beyond your new plan's limits become read-only

### Cancellation
- Cancel anytime from the billing portal
- Access continues until the end of the paid period
- Data is retained for 30 days after expiration
- Reverts to Free tier (Seedling) after cancellation

## Usage Limits & Overages

Each plan has monthly limits for metered features:

- **AI Analyses**: Gemini-powered health checks, feeding advice, pest identification
- **Storage**: Photos, camera recordings, sensor data retention
- **Journal Entries** (Free plan only): 50/month

When you hit a limit:
- You'll see a notification with your current usage
- The feature becomes temporarily unavailable
- Limits reset at the start of each calendar month
- Upgrade to increase your limits instantly

## Billing for Teams

- **Account**: Represents the billing entity (one subscription)
- **Tenant**: Represents a workspace (grows, devices, data)
- One Account can own multiple Tenants
- Team members are added at the Tenant level with roles: Admin, Member, Viewer
- Only Account Owners can manage billing

## Self-Hosted Billing

Self-hosted instances can configure their own payment provider:

1. Deploy Tendril with the API
2. Go to **Admin → Payment Providers**
3. Add your Stripe/PayPal/Square/Paddle credentials
4. Plans and pricing sync automatically to the provider

For self-hosted deployments without billing, all features are unlocked by default.

## Security

- All payment credentials are encrypted at rest (AES-256)
- Webhook signatures are verified for every event
- No card numbers are stored — handled by the payment provider
- PCI compliance is handled by Stripe/PayPal/Square/Paddle
- Billing admin access requires the `owner` role

## FAQ

**Can I switch payment methods?**
Yes. Use "Manage Subscription" to access the billing portal where you can update payment methods.

**Do you offer annual billing?**
Annual billing with a discount is planned. Currently all plans are billed monthly.

**What happens if payment fails?**
The payment provider retries 3 times over 7 days. If all retries fail, the subscription is cancelled and the account reverts to Free.

**Can I get a refund?**
Contact support within 7 days of a charge for a full refund. Partial-month refunds are prorated.

**Is there a trial period?**
New accounts start on the Free tier with full access to basic features. Upgrade when you're ready.
