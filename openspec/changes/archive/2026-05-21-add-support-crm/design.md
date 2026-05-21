## Context
Tendril has no support infrastructure. Users can't ask for help, report bugs, or find answers. We need a modular, toggleable support system that works for a solo self-hoster (just KB + tickets) and scales to a full SaaS operation (all channels + CRM sync).

## Goals / Non-Goals
- **Goals**: Built-in ticket system, knowledge base, live chat, email support, community forum — all independently toggleable. Optional external CRM sync. PWA-ready.
- **Non-Goals**: Phone support, video calls, AI chatbot for support (use existing Tendril AI chat for grow help, not support tickets), white-label support portal

## Decisions

### Decision: All channels toggleable independently
Each channel (tickets, KB, chat, email, forum) has an on/off switch in admin. UI dynamically renders only enabled channels. This means a self-hoster running for friends only needs KB; a SaaS operator can enable everything.

**Rationale:** Different deployment scales need different support levels. Don't force complexity on small operators.

### Decision: Built-in first, external sync optional
The CRM is fully self-contained (PostgreSQL-backed). External sync (Zendesk, Freshdesk, Intercom) is an optional add-on for operators who already use those platforms.

**Alternatives considered:**
- External-only (just integrate with Zendesk): Requires external dependency, cost, not self-host friendly
- Headless CRM lib: No good open-source options for our stack

### Decision: Forum as support channel, not social
The forum is focused on Q&A and troubleshooting, not general social interaction. Solution marking, upvotes, and search make it a living knowledge base.

### Decision: WebSocket for live chat, not polling
Live chat uses WebSocket (same infrastructure as our AI chat). Staff gets real-time incoming messages. Offline users get notification + ticket conversion.

### Decision: SLA tracking built-in
Even for small deployments, SLA tracking helps the operator understand their response quality. Overdue tickets get flagged in the admin dashboard.

## Risks / Trade-offs
- **Risk**: Feature bloat for self-hosters → **Mitigation**: Everything off by default except KB + tickets
- **Risk**: Email parsing complexity → **Mitigation**: Use webhook-based email providers (SendGrid inbound parse, Mailgun routes) not raw IMAP
- **Risk**: Forum spam → **Mitigation**: Rate limiting, email verification required, admin moderation queue
- **Risk**: Chat scaling → **Mitigation**: One staff member per session, queue when all busy, auto-convert to ticket after timeout

## Open Questions
- Should we add a satisfaction survey after ticket resolution? (Probably yes — simple 1-5 stars)
- Should forum posts be visible to unauthenticated users? (SEO benefit, but privacy consideration)
