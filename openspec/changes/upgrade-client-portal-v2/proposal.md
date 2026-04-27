# Proposal: Upgrade Client Portal v2

**Change ID:** `upgrade-client-portal-v2`  
**Created:** March 12, 2026  
**Author:** Copilot  
**Status:** Approved  

## Summary

Enterprise-grade overhaul of the Trec-Tor Consulting client portal at client.trector.com. Transforms the existing portal from a functional MVP into a seamless, modern, mobile-first self-service experience with real-time data, Stripe payments, retainer visibility, technology assessment results, a knowledge base, notification system, and robust security hardening.

## Motivation

- **Revenue impact:** Stripe Pay Now on invoices removes friction from payments
- **Client retention:** Retainer dashboard and project visibility keep clients engaged
- **Sales enablement:** Technology Assessment portal view drives upsell conversations
- **Support reduction:** Knowledge Base and Issue enhancements reduce manual support burden
- **Professionalism:** Server-side rendered dashboard eliminates loading flicker
- **Security:** Enterprise hardening protects client data
- **Mobile:** Clients increasingly access portal on phone/tablet

## Scope

### In Scope
1. Delete `setup_customer_desk.py` (conflicting desk-access approach)
2. Server-side dashboard stats in `portal.py` (eliminate JS loading flicker)
3. Stripe Pay Now button on invoice detail pages
4. Retainer status card on portal dashboard + dedicated `/retainer` page
5. Issue/Support system: status timeline, file attachments UX, notification rules, canned responses
6. Project visibility: task list, milestone progress bar, hours summary, deliverables
7. Technology Assessment portal view: radar chart, maturity score, recommended actions
8. Client onboarding: auto-link on signup, welcome tour, profile completion redirect
9. Notification bell: real-time portal notification widget via socketio
10. Knowledge Base: Help articles organized by service category at `/knowledge-base`
11. Mobile responsiveness: comprehensive media queries, touch targets, stacking layouts
12. Security hardening: rate limiting, CAPTCHA on signup, 2FA option
13. Analytics & feedback: portal-specific GA4 events, satisfaction survey, NPS web form

### Out of Scope
- Custom Frappe app development (all changes via scripts, templates, CSS, server scripts)
- Backend API redesign
- Billing/subscription automation (manual invoicing continues)

## Impact

- **Portal template files patched:** `portal.html`, `portal.py`, `me.html`, `web_sidebar.html`
- **New setup script:** `setup_customer_portal.py` updated with new functions
- **New portal template:** `portal.html` updated with retainer card, notification bell, assessment section
- **New web forms:** Knowledge Base, NPS Survey, Feedback
- **New server scripts:** Rate limiting, auto-link on signup, notification triggers
- **CSS additions:** Mobile polish, notification bell, retainer card, assessment radar chart
- **File deleted:** `setup_customer_desk.py`
