"""Tenant-editable system alert rules.

Adds ``grow_type`` and ``is_system_default`` columns to ``automation_rules``
and a ``system_alert_rules_seeded_version`` counter to ``tenants``, then
backfills the safety-net defaults from
``app.automation.critical_alerts_defaults.CRITICAL_ALERTS`` into every
existing tenant.

This moves what used to be a hardcoded dict inside
``app/automation/engine.py`` into per-tenant database rows so tenants can
disable, retune, or extend safety alarms via the standard rule CRUD
endpoints in ``app/automation/routes.py``.

Revision ID: 0047
Revises: 0046
Create Date: 2026-06-16
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "0047"
down_revision = "0046"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---- automation_rules: new columns ------------------------------------
    op.add_column(
        "automation_rules",
        sa.Column("grow_type", sa.String(50), nullable=True),
    )
    op.add_column(
        "automation_rules",
        sa.Column(
            "is_system_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_index(
        "ix_automation_rules_grow_type",
        "automation_rules",
        ["grow_type"],
    )
    op.create_index(
        "ix_automation_rules_tenant_grow_type",
        "automation_rules",
        ["tenant_id", "grow_type"],
    )

    # ---- tenants: version counter -----------------------------------------
    op.add_column(
        "tenants",
        sa.Column(
            "system_alert_rules_seeded_version",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    # ---- backfill: seed defaults for every existing tenant ----------------
    # The defaults dict is imported here (not at module top-level) so the
    # migration can still be loaded by Alembic in environments where the
    # app package isn't on the path (e.g. ``alembic history`` introspection).
    from app.automation.critical_alerts_defaults import CRITICAL_ALERTS, DEFAULTS_VERSION

    bind = op.get_bind()

    automation_rules = sa.table(
        "automation_rules",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("tenant_id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("sensor", sa.String),
        sa.column("condition", sa.String),
        sa.column("threshold", sa.Float),
        sa.column("action", sa.String),
        sa.column("cooldown_minutes", sa.Integer),
        sa.column("severity", sa.String),
        sa.column("enabled", sa.Boolean),
        sa.column("grow_type", sa.String),
        sa.column("is_system_default", sa.Boolean),
    )

    tenants = sa.table(
        "tenants",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("system_alert_rules_seeded_version", sa.Integer),
    )

    tenant_ids = [row[0] for row in bind.execute(sa.select(tenants.c.id)).all()]

    seeded_total = 0
    for tenant_id in tenant_ids:
        # Natural key of a system default is (grow_type, sensor, condition,
        # severity) — threshold is what tenants edit. Tiered alerts (e.g.
        # DWC water_temp_f gt 72 warning + gt 78 critical) are
        # disambiguated by severity.
        existing_signatures = {
            (gt, sensor, condition, severity)
            for gt, sensor, condition, severity in bind.execute(
                sa.select(
                    automation_rules.c.grow_type,
                    automation_rules.c.sensor,
                    automation_rules.c.condition,
                    automation_rules.c.severity,
                ).where(automation_rules.c.tenant_id == tenant_id)
            ).all()
        }

        rows_to_insert: list[dict] = []
        for grow_type, defaults in CRITICAL_ALERTS.items():
            for default in defaults:
                signature = (
                    grow_type,
                    default["sensor"],
                    default["condition"],
                    default["severity"],
                )
                if signature in existing_signatures:
                    continue
                rows_to_insert.append(
                    {
                        # ``automation_rules.id`` is a Python-side
                        # ``default=uuid.uuid4`` on the ORM model; this raw
                        # ``sa.table()`` insert bypasses that default, so
                        # generate the UUID explicitly. The column has no
                        # server-side default.
                        "id": uuid.uuid4(),
                        "tenant_id": tenant_id,
                        "name": default["message"],
                        "sensor": default["sensor"],
                        "condition": default["condition"],
                        "threshold": default["threshold"],
                        "action": "alert",
                        "cooldown_minutes": 0,
                        "severity": default["severity"],
                        "enabled": True,
                        "grow_type": grow_type,
                        "is_system_default": True,
                    }
                )

        if rows_to_insert:
            bind.execute(automation_rules.insert(), rows_to_insert)
            seeded_total += len(rows_to_insert)

        bind.execute(
            tenants.update().where(tenants.c.id == tenant_id).values(system_alert_rules_seeded_version=DEFAULTS_VERSION)
        )

    # Drop the server_default for is_system_default — application defaults
    # are now driven by the SQLAlchemy column default, and we don't want a
    # stale literal on the table.
    op.alter_column("automation_rules", "is_system_default", server_default=None)


def downgrade() -> None:
    # Best-effort revert. The seeded rows are removed by grow_type filter
    # (system defaults always carry a grow_type); user-authored rules that
    # happen to have a grow_type set are preserved by also requiring
    # is_system_default = true.
    bind = op.get_bind()
    automation_rules = sa.table(
        "automation_rules",
        sa.column("grow_type", sa.String),
        sa.column("is_system_default", sa.Boolean),
    )
    bind.execute(
        automation_rules.delete().where(
            sa.and_(
                automation_rules.c.is_system_default.is_(True),
                automation_rules.c.grow_type.is_not(None),
            )
        )
    )

    op.drop_column("tenants", "system_alert_rules_seeded_version")
    op.drop_index("ix_automation_rules_tenant_grow_type", table_name="automation_rules")
    op.drop_index("ix_automation_rules_grow_type", table_name="automation_rules")
    op.drop_column("automation_rules", "is_system_default")
    op.drop_column("automation_rules", "grow_type")
