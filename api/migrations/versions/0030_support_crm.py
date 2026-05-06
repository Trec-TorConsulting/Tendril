"""Support CRM — tickets, KB, chat, forum tables.

Revision ID: 0030
Revises: 0029
Create Date: 2025-01-20
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID

revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Support channels config — use DO $$ for idempotent enum creation with asyncpg
    op.execute(
        "DO $$ BEGIN CREATE TYPE channel_type_enum AS ENUM ('tickets', 'knowledge_base', 'live_chat', 'email', 'forum'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "support_channels",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "channel_type",
            ENUM(
                "tickets", "knowledge_base", "live_chat", "email", "forum", name="channel_type_enum", create_type=False
            ),
        ),
        sa.Column("is_enabled", sa.Boolean(), default=False),
        sa.Column("min_plan", sa.String(50), default="free"),
        sa.Column("config_json", JSONB, default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("channel_type"),
    )

    # Tickets
    op.execute(
        "DO $$ BEGIN CREATE TYPE ticket_status_enum AS ENUM ('open', 'in_progress', 'waiting_on_user', 'waiting_on_staff', 'resolved', 'closed'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.execute(
        "DO $$ BEGIN CREATE TYPE ticket_priority_enum AS ENUM ('low', 'medium', 'high', 'urgent'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.execute(
        "DO $$ BEGIN CREATE TYPE ticket_category_enum AS ENUM ('general', 'billing', 'technical', 'feature_request', 'bug_report', 'account'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "support_tickets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_by_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assigned_to_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column(
            "status",
            ENUM(
                "open",
                "in_progress",
                "waiting_on_user",
                "waiting_on_staff",
                "resolved",
                "closed",
                name="ticket_status_enum",
                create_type=False,
            ),
            default="open",
        ),
        sa.Column(
            "priority",
            ENUM("low", "medium", "high", "urgent", name="ticket_priority_enum", create_type=False),
            default="medium",
        ),
        sa.Column(
            "category",
            ENUM(
                "general",
                "billing",
                "technical",
                "feature_request",
                "bug_report",
                "account",
                name="ticket_category_enum",
                create_type=False,
            ),
            default="general",
        ),
        sa.Column("due_at", sa.DateTime(timezone=True)),
        sa.Column("first_response_at", sa.DateTime(timezone=True)),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("satisfaction_rating", sa.Integer()),
        sa.Column("satisfaction_comment", sa.Text()),
        sa.Column("tags", JSONB, default=[]),
        sa.Column("metadata_json", JSONB, default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ticket_tenant_status", "support_tickets", ["tenant_id", "status"])
    op.create_index("ix_ticket_assigned", "support_tickets", ["assigned_to_id"])

    # Ticket messages
    op.create_table(
        "support_messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "ticket_id",
            UUID(as_uuid=True),
            sa.ForeignKey("support_tickets.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("author_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_internal", sa.Boolean(), default=False),
        sa.Column("attachments", JSONB, default=[]),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Knowledge Base categories
    op.create_table(
        "kb_categories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("icon", sa.String(50)),
        sa.Column("sort_order", sa.Integer(), default=0),
        sa.Column("is_published", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Knowledge Base articles
    op.create_table(
        "kb_articles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "category_id",
            UUID(as_uuid=True),
            sa.ForeignKey("kb_categories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("body_markdown", sa.Text(), nullable=False),
        sa.Column("tags", JSONB, default=[]),
        sa.Column("sort_order", sa.Integer(), default=0),
        sa.Column("is_published", sa.Boolean(), default=True),
        sa.Column("views", sa.Integer(), default=0),
        sa.Column("helpful_yes", sa.Integer(), default=0),
        sa.Column("helpful_no", sa.Integer(), default=0),
        sa.Column("author_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_kb_article_search", "kb_articles", ["title", "slug"])

    # Chat sessions
    op.execute(
        "DO $$ BEGIN CREATE TYPE chat_session_status_enum AS ENUM ('queued', 'active', 'ended', 'converted_to_ticket'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "chat_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("staff_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column(
            "status",
            ENUM(
                "queued", "active", "ended", "converted_to_ticket", name="chat_session_status_enum", create_type=False
            ),
            default="queued",
        ),
        sa.Column("converted_ticket_id", UUID(as_uuid=True), sa.ForeignKey("support_tickets.id")),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("metadata_json", JSONB, default={}),
    )

    # Chat messages
    op.create_table(
        "chat_messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("sender_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("attachments", JSONB, default=[]),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Forum categories
    op.create_table(
        "forum_categories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("icon", sa.String(50)),
        sa.Column("sort_order", sa.Integer(), default=0),
        sa.Column("thread_count", sa.Integer(), default=0),
        sa.Column("post_count", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Forum threads
    op.execute(
        "DO $$ BEGIN CREATE TYPE forum_thread_status_enum AS ENUM ('open', 'solved', 'locked', 'pinned'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "forum_threads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "category_id",
            UUID(as_uuid=True),
            sa.ForeignKey("forum_categories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("author_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "status",
            ENUM("open", "solved", "locked", "pinned", name="forum_thread_status_enum", create_type=False),
            default="open",
        ),
        sa.Column("is_pinned", sa.Boolean(), default=False),
        sa.Column("view_count", sa.Integer(), default=0),
        sa.Column("reply_count", sa.Integer(), default=0),
        sa.Column("upvotes", sa.Integer(), default=0),
        sa.Column("solution_post_id", UUID(as_uuid=True)),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_forum_thread_category", "forum_threads", ["category_id", "status"])

    # Forum posts
    op.create_table(
        "forum_posts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "thread_id",
            UUID(as_uuid=True),
            sa.ForeignKey("forum_threads.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("author_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_solution", sa.Boolean(), default=False),
        sa.Column("upvotes", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Canned responses
    op.create_table(
        "support_canned_responses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50)),
        sa.Column("shortcut", sa.String(50)),
        sa.Column("created_by_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Seed default channels (tickets + KB enabled by default)
    op.execute("""
        INSERT INTO support_channels (id, channel_type, is_enabled, min_plan)
        VALUES
            (gen_random_uuid(), 'tickets', true, 'free'),
            (gen_random_uuid(), 'knowledge_base', true, 'free'),
            (gen_random_uuid(), 'live_chat', false, 'pro'),
            (gen_random_uuid(), 'email', false, 'hobby'),
            (gen_random_uuid(), 'forum', false, 'free')
    """)

    # Seed KB categories
    op.execute("""
        INSERT INTO kb_categories (id, name, slug, description, icon, sort_order)
        VALUES
            (gen_random_uuid(), 'Getting Started', 'getting-started', 'New to Tendril? Start here.', 'rocket', 0),
            (gen_random_uuid(), 'Grows & Environments', 'grows', 'Managing grows, environments, and schedules.', 'leaf', 1),
            (gen_random_uuid(), 'Devices & Sensors', 'devices', 'Setting up and configuring hardware.', 'cpu', 2),
            (gen_random_uuid(), 'Billing & Plans', 'billing', 'Subscriptions, payments, and plan features.', 'credit-card', 3),
            (gen_random_uuid(), 'Troubleshooting', 'troubleshooting', 'Common issues and solutions.', 'wrench', 4)
    """)

    # Seed forum categories
    op.execute("""
        INSERT INTO forum_categories (id, name, slug, description, icon, sort_order)
        VALUES
            (gen_random_uuid(), 'General Discussion', 'general', 'Anything Tendril-related.', 'message-circle', 0),
            (gen_random_uuid(), 'Growing Tips', 'growing-tips', 'Share and learn growing techniques.', 'sprout', 1),
            (gen_random_uuid(), 'Hardware & DIY', 'hardware-diy', 'ESP32, sensors, and custom builds.', 'cpu', 2),
            (gen_random_uuid(), 'Feature Requests', 'feature-requests', 'Ideas for improving Tendril.', 'lightbulb', 3),
            (gen_random_uuid(), 'Bug Reports', 'bugs', 'Found something broken? Report it here.', 'bug', 4)
    """)


def downgrade() -> None:
    op.drop_table("support_canned_responses")
    op.drop_table("forum_posts")
    op.drop_table("forum_threads")
    op.drop_table("forum_categories")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("kb_articles")
    op.drop_table("kb_categories")
    op.drop_table("support_messages")
    op.drop_table("support_tickets")
    op.drop_table("support_channels")
    op.execute("DROP TYPE IF EXISTS forum_thread_status_enum")
    op.execute("DROP TYPE IF EXISTS chat_session_status_enum")
    op.execute("DROP TYPE IF EXISTS ticket_category_enum")
    op.execute("DROP TYPE IF EXISTS ticket_priority_enum")
    op.execute("DROP TYPE IF EXISTS ticket_status_enum")
    op.execute("DROP TYPE IF EXISTS channel_type_enum")
