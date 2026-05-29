"""plant health treatments and diagnosis linking

Revision ID: 0038
Revises: 0037
Create Date: 2026-05-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0038"
down_revision = "0037"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Plant health treatment entries (deficiencies, pests, diseases, environmental)
    op.create_table(
        "plant_health_treatments",
        sa.Column("id", sa.String(100), primary_key=True),  # e.g., "nitrogen_deficiency"
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("aka", JSONB, nullable=False, server_default="[]"),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("symptoms", JSONB, nullable=False, server_default="[]"),
        sa.Column("identification_tips", JSONB, nullable=False, server_default="[]"),
        sa.Column("causes", JSONB, nullable=False, server_default="[]"),
        sa.Column("severity_criteria", JSONB, nullable=False, server_default="{}"),
        sa.Column("treatments", JSONB, nullable=False, server_default="{}"),
        sa.Column("prevention", JSONB, nullable=False, server_default="[]"),
        sa.Column("recovery_time", sa.String(100), nullable=False, server_default=""),
        sa.Column("commonly_confused_with", JSONB, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Add diagnosis linkage to health_evals
    op.add_column(
        "health_evals",
        sa.Column("diagnosis_treatment_ids", JSONB, server_default="[]"),
    )
    op.add_column(
        "health_evals",
        sa.Column("confidence_scores", JSONB, server_default="{}"),
    )
    op.add_column(
        "health_evals",
        sa.Column("severity", sa.String(20)),
    )
    op.add_column(
        "health_evals",
        sa.Column("model_used", sa.String(100)),
    )


def downgrade() -> None:
    op.drop_column("health_evals", "model_used")
    op.drop_column("health_evals", "severity")
    op.drop_column("health_evals", "confidence_scores")
    op.drop_column("health_evals", "diagnosis_treatment_ids")
    op.drop_table("plant_health_treatments")
