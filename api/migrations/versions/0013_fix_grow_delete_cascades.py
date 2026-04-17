"""Fix FK cascades so grow cycles can be deleted.

tasks.grow_cycle_id → ON DELETE CASCADE
automation_rules.grow_cycle_id → ON DELETE SET NULL
alert_history.grow_cycle_id → ON DELETE SET NULL

Revision ID: 0013
Create Date: 2026-04-17
"""
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # tasks.grow_cycle_id → CASCADE (delete tasks when grow is deleted)
    op.drop_constraint("tasks_grow_cycle_id_fkey", "tasks", type_="foreignkey")
    op.create_foreign_key(
        "tasks_grow_cycle_id_fkey", "tasks", "grow_cycles",
        ["grow_cycle_id"], ["id"], ondelete="CASCADE",
    )

    # automation_rules.grow_cycle_id → SET NULL
    op.drop_constraint("automation_rules_grow_cycle_id_fkey", "automation_rules", type_="foreignkey")
    op.create_foreign_key(
        "automation_rules_grow_cycle_id_fkey", "automation_rules", "grow_cycles",
        ["grow_cycle_id"], ["id"], ondelete="SET NULL",
    )

    # alert_history.grow_cycle_id → SET NULL
    op.drop_constraint("alert_history_grow_cycle_id_fkey", "alert_history", type_="foreignkey")
    op.create_foreign_key(
        "alert_history_grow_cycle_id_fkey", "alert_history", "grow_cycles",
        ["grow_cycle_id"], ["id"], ondelete="SET NULL",
    )


def downgrade() -> None:
    # Revert to no ondelete
    op.drop_constraint("tasks_grow_cycle_id_fkey", "tasks", type_="foreignkey")
    op.create_foreign_key(
        "tasks_grow_cycle_id_fkey", "tasks", "grow_cycles",
        ["grow_cycle_id"], ["id"],
    )

    op.drop_constraint("automation_rules_grow_cycle_id_fkey", "automation_rules", type_="foreignkey")
    op.create_foreign_key(
        "automation_rules_grow_cycle_id_fkey", "automation_rules", "grow_cycles",
        ["grow_cycle_id"], ["id"],
    )

    op.drop_constraint("alert_history_grow_cycle_id_fkey", "alert_history", type_="foreignkey")
    op.create_foreign_key(
        "alert_history_grow_cycle_id_fkey", "alert_history", "grow_cycles",
        ["grow_cycle_id"], ["id"],
    )
