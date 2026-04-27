# Tasks: Upgrade Client Portal v2

**Change ID:** `upgrade-client-portal-v2`  
**Last Updated:** March 12, 2026  
**Status:** In Progress — Phase 1-6 core implementation complete

---

## Phase 1: Cleanup & Foundation

### 1.1 Delete Desk Access Script
- [x] Delete `frappe-setup/scripts/setup_customer_desk.py`
- [x] Verify no other scripts reference or import from it
- [x] Update README.md to remove reference

### 1.2 Server-Side Dashboard Stats
- [x] Update `portal.py` to query stats server-side (active projects, open issues, unpaid invoices, pending orders)
- [x] Add customer resolution from session user (`_resolve_customer()`)
- [x] Add recent activity query (`_get_recent_activity()` — last 10 events across Issue, Project, Sales Invoice, Sales Order, Quotation)
- [x] Update `portal.html` to render stats from server context (no JS fetch flicker)
- [x] Add contextual quick actions (`_get_contextual_actions()` — hide Request Quote if pending, show Pay Invoice if unpaid)
- [x] Add retainer status card with progress bar (`_get_retainer()`)
- [x] Add technology assessment card with SVG score ring (`_get_assessment()`)
- [x] Add notification bell with unread count (`_get_notifications()`)
- [x] Add profile completion banner (`profile_incomplete` check)
- [x] Add comprehensive inline CSS (mobile-first, responsive)

---

## Phase 2: Support & Project Visibility

### 2.1 Issue/Support Enhancements
- [x] Create Issue Types (Bug Report, Feature Request, General Inquiry, Account Issue, Billing Question, Technical Support, Access/Permissions, Data Request)
- [x] Create Issue Priorities (Low, Medium, High, Urgent)
- [x] Create auto-reply Notification on Issue creation (branded email)
- [x] Create status change Notification (email on status update)
- [ ] Add "Status Timeline" section to Issue web view (requires custom template)
- [ ] Add canned response dropdown for common issue categories
- [ ] Add SLA visibility fields (expected response time)

### 2.2 Project Visibility
- [x] Enable `has_web_view` on Task DocType
- [x] Create Project completion Notification (email when status = Completed)
- [x] Create Task milestone Notification (email when milestone task completed)
- [ ] Add Task child-list display within Project portal detail page (requires custom template)
- [ ] Add visual milestone progress bar
- [ ] Add hours summary card per project

---

## Phase 3: Assessment & Onboarding

### 3.1 Technology Assessment Portal View
- [x] Add `setup_assessment_portal()` function to `setup_customer_portal.py`
- [x] Add Customer read permission for Technology Assessment DocType
- [x] Enable `has_web_view` on Technology Assessment via Property Setter
- [x] Set `is_published_field` on Technology Assessment
- [x] Create Server Script to mark completed assessments as published
- [x] Add assessment score card to portal dashboard (SVG score ring with gradient)
- [x] Add CSS radar chart with 8 positions for categories
- [x] Display maturity level badge (Critical/Basic/Developing/Mature/Optimized)
- [x] Add "Download PDF Report" button linking to print format
- [x] Add Technology Assessment to Portal Settings menu
- [x] Add assessment icon to sidebar (`🔬`)

### 3.2 Client Onboarding Flow
- [x] Add `setup_onboarding_flow()` function to `setup_customer_portal.py`
- [x] Create welcome email Notification for new portal users with Customer role
- [x] Add profile completion check in `portal.py` (banner if missing first/last name)
- [x] Brand the edit-profile Web Form with gradient intro
- [ ] Add first-login tour overlay JS (future enhancement)
- [ ] Store `portal_tour_completed` flag in user defaults (future enhancement)

---

## Phase 4: Engagement & Content

### 4.1 Notification Bell System
- [x] Add notification bell icon injection via portal.html JS
- [x] Query unread Notification Log count server-side in `portal.py`
- [x] Add dropdown panel showing recent notifications (last 10)
- [x] Add notification count badge with pulse animation CSS
- [x] Add mark-all-read functionality via frappe.call
- [x] Add notification bell CSS (badge, dropdown, hover states, mobile responsive)
- [ ] Configure socketio for real-time push (future — currently uses on-demand fetch)

### 4.2 Knowledge Base / Help Center
- [x] Add `setup_knowledge_base()` function to `setup_customer_portal.py`
- [x] Create 6 Help Article Categories (Getting Started, Billing & Payments, Project Management, Support & Issues, Security & Privacy, Services Overview)
- [x] Create 8 Help Articles covering portal usage and service FAQs
- [x] Create Knowledge Base Web Page at `/knowledge-base` with category cards
- [x] Add Knowledge Base to portal sidebar navigation (`📖`)
- [x] Add Knowledge Base link in dashboard nav grid and quick actions
- [ ] Add search functionality to knowledge base (future — uses Frappe's built-in search)

---

## Phase 5: Polish & Security

### 5.1 Mobile Responsiveness
- [x] Dashboard stat cards: 4-col → 2-col (tablet) → 1-col (phone)
- [x] Navigation grid: 2-col → 1-col on mobile
- [x] Quick actions: full-width stacking on mobile
- [x] Touch target enforcement: min 44px for all interactive elements
- [x] Retainer and assessment cards stack vertically on mobile
- [x] Notification dropdown responsive positioning
- [x] Profile banner full-width CTA on mobile
- [ ] Full manual test pass on 375px, 390px, 768px devices

### 5.2 Security Hardening
- [x] Add `setup_security_hardening()` function to `setup_customer_portal.py`
- [x] Enable password policy (minimum score 3)
- [x] Set login rate limiting (5 attempts, 5 minute lockout)
- [x] Set session expiry (6 hours desktop, 30 days mobile)
- [x] Force HTTPS
- [x] Disable login by mobile number and username (email only)
- [x] reCAPTCHA auto-enabled if keys configured
- [x] Stripe payment API validates customer ownership before creating payment request
- [ ] Document 2FA (TOTP) configuration steps for portal users
- [ ] Add Content-Security-Policy headers (requires Traefik middleware)

### 5.3 Analytics & Feedback
- [x] Add `setup_analytics_feedback()` function to `setup_customer_portal.py`
- [x] GA4 portal_dashboard_view event tracking in portal.html JS
- [x] GA4 configuration check (prints status, requires manual ID setup)
- [x] Create "Client Feedback" Web Form (Communication-backed, stars + text)
- [x] Add feedback icon to sidebar (`⭐`)
- [ ] Create NPS Survey Web Form (0-10 scale + reason)
- [ ] Add Server Script to trigger NPS survey quarterly
- [ ] Add satisfaction prompt after Issue closure

---

## Phase 6: Revenue & Retention

### 6.1 Stripe Pay Now on Invoices
- [x] Add `setup_stripe_payments()` function to `setup_customer_portal.py`
- [x] Create Payment Gateway record for Stripe
- [x] Create Payment Gateway Account linking Stripe to company bank
- [x] Create Server Script API (`portal_create_payment_request`) with customer ownership validation
- [x] Inject "Pay Now" button via head_html JS (TREC-TOR-STRIPE-PAY markers)
- [x] Button only appears on invoice detail pages with outstanding amount > 0
- [ ] Configure Stripe Settings (API keys) — requires manual setup
- [ ] Test end-to-end Stripe payment flow

### 6.2 Retainer Dashboard
- [x] Add `setup_retainer_portal()` function to `setup_customer_portal.py`
- [x] Add retainer status card to `portal.html` (tier badge, hours used/allocated, progress bar, auto-renew indicator)
- [x] Query Retainer Contract server-side in `portal.py` (`_get_retainer()`)
- [x] Add Customer read permission for Retainer Contract DocType
- [x] Enable `has_web_view` on Retainer Contract via Property Setter
- [x] Set `is_published_field` on Retainer Contract
- [x] Create Server Script to mark active retainers as published
- [x] Add Retainer Contract to Portal Settings menu
- [x] Add retainer CSS (progress bar with gradient, warn/over states, tier badges)
- [x] Add retainer icon to sidebar (`📋`)
