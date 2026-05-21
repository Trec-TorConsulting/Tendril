## 1. Database & Models
- [ ] 1.1 Create migration: `support_tickets`, `support_messages` tables
- [ ] 1.2 Create migration: `kb_categories`, `kb_articles` tables
- [ ] 1.3 Create migration: `chat_sessions`, `chat_messages` tables
- [ ] 1.4 Create migration: `forum_categories`, `forum_threads`, `forum_posts` tables
- [ ] 1.5 Create migration: `support_channels` table (channel config + toggle)
- [ ] 1.6 Create SQLAlchemy models in `api/app/support/models.py`
- [ ] 1.7 Seed default channels (tickets=on, kb=on, others=off)
- [ ] 1.8 Seed initial KB categories (Getting Started, Grows, Devices, Billing, Troubleshooting)

## 2. Ticket System (User-facing)
- [ ] 2.1 Create `api/app/support/routes.py` — user ticket endpoints
- [ ] 2.2 Endpoints: create ticket, list my tickets, get ticket, add message, close ticket
- [ ] 2.3 File attachment support (upload to MinIO, link in message)
- [ ] 2.4 Ticket auto-categorization (basic keyword matching)
- [ ] 2.5 Email notification on ticket reply (to user)

## 3. Ticket System (Admin)
- [ ] 3.1 Create `api/app/support/admin_routes.py` — admin support dashboard API
- [ ] 3.2 Endpoints: list all tickets (filterable), assign ticket, change priority/status, bulk actions
- [ ] 3.3 Internal notes (staff-only messages not visible to user)
- [ ] 3.4 SLA tracking: compute due_at on creation, flag overdue
- [ ] 3.5 Canned responses / templates for common issues
- [ ] 3.6 Ticket metrics: avg response time, resolution time, satisfaction

## 4. Knowledge Base
- [ ] 4.1 Admin endpoints: CRUD categories, CRUD articles (Markdown + images)
- [ ] 4.2 Public endpoints: list categories, list articles, get article, search articles
- [ ] 4.3 Full-text search with PostgreSQL tsvector
- [ ] 4.4 Article helpfulness voting (thumbs up/down)
- [ ] 4.5 Related articles suggestion (tag-based)
- [ ] 4.6 Article versioning (edit history)

## 5. Live Chat
- [ ] 5.1 Create `api/app/support/chat.py` — WebSocket chat handler
- [ ] 5.2 User initiates chat → assigned to available staff or queued
- [ ] 5.3 Staff chat dashboard: active sessions, queue, transfer
- [ ] 5.4 Chat → ticket conversion (if issue needs follow-up)
- [ ] 5.5 Typing indicators, read receipts
- [ ] 5.6 Chat transcript saved to DB, downloadable

## 6. Email Support
- [ ] 6.1 Create `api/app/support/email_handler.py`
- [ ] 6.2 Inbound: parse incoming email (webhook from email provider) → create/update ticket
- [ ] 6.3 Outbound: send reply notifications via configured SMTP/SES
- [ ] 6.4 Email threading (In-Reply-To headers map to ticket)
- [ ] 6.5 Admin config: support email address, SMTP settings

## 7. Community Forum
- [ ] 7.1 Create `api/app/support/forum/routes.py` — forum CRUD
- [ ] 7.2 Endpoints: list categories, list threads, create thread, reply, mark solution
- [ ] 7.3 Moderation: pin, lock, delete, move thread
- [ ] 7.4 Upvoting + solution marking
- [ ] 7.5 User reputation/badges (based on helpful answers)
- [ ] 7.6 Forum search (full-text)

## 8. External CRM Sync (Optional)
- [ ] 8.1 Create `api/app/support/sync/base.py` — BaseCRMSync adapter
- [ ] 8.2 Implement Zendesk adapter (create/update tickets, sync comments)
- [ ] 8.3 Implement Freshdesk adapter
- [ ] 8.4 Implement Intercom adapter (conversations API)
- [ ] 8.5 Bidirectional sync: Tendril → External on create/update, webhook pull for external updates
- [ ] 8.6 Admin config UI for CRM connection

## 9. Channel Configuration Admin
- [ ] 9.1 Admin endpoints: list channels, enable/disable channel, update channel config
- [ ] 9.2 Admin UI: channel toggle page with per-channel settings
- [ ] 9.3 Per-channel tier requirements enforcement

## 10. Frontend — User Support Pages
- [ ] 10.1 Build `/support` page — hub showing active channels (KB, tickets, chat, forum)
- [ ] 10.2 Build ticket submission form + ticket list + ticket detail (threaded messages)
- [ ] 10.3 Build knowledge base browser (categories → articles, search)
- [ ] 10.4 Build chat widget (floating button → chat panel, available when chat enabled)
- [ ] 10.5 Build forum pages (category list → thread list → thread detail with replies)
- [ ] 10.6 PWA: KB articles cached for offline reading, ticket submission queued offline

## 11. Frontend — Admin Support Dashboard
- [ ] 11.1 Build `/admin/support` — ticket queue with filters, bulk actions
- [ ] 11.2 Build ticket detail admin view (assignment, priority, internal notes, canned responses)
- [ ] 11.3 Build KB admin (article editor with Markdown preview, category management)
- [ ] 11.4 Build chat admin (active sessions panel, queue management)
- [ ] 11.5 Build forum moderation panel
- [ ] 11.6 Build support metrics dashboard (response times, satisfaction, volume charts)
- [ ] 11.7 Build channel configuration page

## 12. Tests
- [ ] 12.1 Unit tests: ticket CRUD, SLA calculation, auto-categorization
- [ ] 12.2 Unit tests: KB search, article voting
- [ ] 12.3 Unit tests: chat session management, message delivery
- [ ] 12.4 Unit tests: forum CRUD, moderation, reputation
- [ ] 12.5 Integration tests: CRM sync adapters (mocked)
- [ ] 12.6 Integration tests: email inbound/outbound
- [ ] 12.7 Frontend tests: support pages, chat widget, forum, KB
- [ ] 12.8 E2E: user submits ticket → admin responds → user sees reply
