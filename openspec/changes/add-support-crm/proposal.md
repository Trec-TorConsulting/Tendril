# Change: Add Built-in Support CRM with Optional External Sync

## Why
Users need a way to reach the platform operator for help. Currently there's no support system. We need a modular CRM that starts with a built-in ticket system and knowledge base, with the ability to enable/disable channels (live chat, email, community forum) and optionally sync to external platforms (Zendesk, Freshdesk, Intercom).

## What Changes
- New `support` module: tickets, knowledge base articles, chat messages
- In-app ticket submission and tracking (user-facing)
- Live chat widget (optional, toggleable)
- Knowledge base / FAQ system (admin-authored, public)
- Community forum (optional, toggleable)
- Email inbound/outbound support (optional, toggleable)
- Admin support dashboard: ticket queue, assignments, SLA tracking
- External CRM sync adapters (Zendesk, Freshdesk, Intercom) — optional
- All channels toggleable per-deployment via admin settings
- PWA: full support experience works offline (cached KB, queued tickets)

## Impact
- Affected specs: new `support-crm` capability
- Affected code: new `api/app/support/` module, new web pages under `/support` and `/admin/support`
- No breaking changes — purely additive

## Design Decisions

### Module Architecture
```
api/app/support/
├── __init__.py
├── models.py          # Ticket, Message, KBArticle, KBCategory, ChatSession
├── routes.py          # User-facing: submit ticket, view tickets, search KB
├── admin_routes.py    # Admin: manage tickets, KB CRUD, channel config
├── chat.py            # WebSocket live chat handler
├── email_handler.py   # Inbound email parsing + outbound notifications
├── forum/
│   ├── models.py      # ForumCategory, ForumThread, ForumPost
│   └── routes.py      # Forum CRUD + moderation
└── sync/
    ├── base.py        # BaseCRMSync adapter
    ├── zendesk.py     # Zendesk ticket sync
    ├── freshdesk.py   # Freshdesk sync
    └── intercom.py    # Intercom conversation sync
```

### Data Model
```sql
-- Tickets
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    subject VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'open',      -- open, in_progress, waiting, resolved, closed
    priority VARCHAR(20) DEFAULT 'normal',  -- low, normal, high, urgent
    category VARCHAR(50),                   -- billing, technical, account, feature_request
    assigned_to UUID REFERENCES users(id),
    external_id VARCHAR(255),               -- Zendesk/Freshdesk ticket ID
    tags TEXT[],
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    resolved_at TIMESTAMP,
    sla_due_at TIMESTAMP
);

CREATE TABLE support_messages (
    id UUID PRIMARY KEY,
    ticket_id UUID REFERENCES support_tickets(id),
    user_id UUID REFERENCES users(id),
    is_staff BOOLEAN DEFAULT false,
    content TEXT NOT NULL,
    attachments JSONB,                      -- [{filename, url, size}]
    created_at TIMESTAMP
);

-- Knowledge Base
CREATE TABLE kb_categories (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT true
);

CREATE TABLE kb_articles (
    id UUID PRIMARY KEY,
    category_id UUID REFERENCES kb_categories(id),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,                   -- Markdown
    excerpt TEXT,
    tags TEXT[],
    is_published BOOLEAN DEFAULT false,
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Live Chat
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'active',    -- active, waiting, closed
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(id),
    user_id UUID REFERENCES users(id),
    is_staff BOOLEAN DEFAULT false,
    content TEXT NOT NULL,
    created_at TIMESTAMP
);

-- Forum
CREATE TABLE forum_categories (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE forum_threads (
    id UUID PRIMARY KEY,
    category_id UUID REFERENCES forum_categories(id),
    user_id UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    is_pinned BOOLEAN DEFAULT false,
    is_locked BOOLEAN DEFAULT false,
    view_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    last_reply_at TIMESTAMP,
    created_at TIMESTAMP
);

CREATE TABLE forum_posts (
    id UUID PRIMARY KEY,
    thread_id UUID REFERENCES forum_threads(id),
    user_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    is_solution BOOLEAN DEFAULT false,
    upvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Channel Configuration
CREATE TABLE support_channels (
    id UUID PRIMARY KEY,
    channel_type VARCHAR(30) NOT NULL,      -- tickets, live_chat, email, kb, forum
    is_enabled BOOLEAN DEFAULT false,
    config_json JSONB,                      -- channel-specific config
    updated_at TIMESTAMP
);
```

### Channel Toggle System
Each support channel is independently toggleable:
| Channel | Default | Tier Requirement |
|---------|---------|-----------------|
| Knowledge Base | ON | Free+ |
| Ticket System | ON | Free+ |
| Email Support | OFF | Hobby+ |
| Live Chat | OFF | Pro+ |
| Community Forum | OFF | Free+ |

Admin enables/disables channels. UI dynamically shows only active channels.

### SLA System
| Priority | First Response | Resolution |
|----------|---------------|------------|
| Low | 48h | 7 days |
| Normal | 24h | 3 days |
| High | 4h | 24h |
| Urgent | 1h | 4h |

SLA tracking with overdue alerts to support staff.
