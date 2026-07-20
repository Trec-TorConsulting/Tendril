"""Enrich reference_strains with type, cannabinoid ranges, sensory data, and provenance.

Revision ID: 0054
Revises: 0053
Create Date: 2026-07-20

Adds a fuller, source-attributed profile to the global strain library so it can
serve as the authoritative reference for AI prompts. Cannabinoid content is
stored as a typical (midpoint) value plus a commonly observed min/max range,
because real-world THC/CBD varies by phenotype, cultivation, and testing lab.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0054"
down_revision = "0053"
branch_labels = None
depends_on = None


_NEW_COLUMNS = (
    ("strain_type", sa.String(50)),
    ("indica_pct", sa.Integer()),
    ("sativa_pct", sa.Integer()),
    ("thc_min", sa.Float()),
    ("thc_max", sa.Float()),
    ("cbd_min", sa.Float()),
    ("cbd_max", sa.Float()),
    ("terpenes", postgresql.JSON()),
    ("effects", postgresql.JSON()),
    ("flavors", postgresql.JSON()),
    ("flowering_min_weeks", sa.Float()),
    ("flowering_max_weeks", sa.Float()),
    ("yield_indoor", sa.String(100)),
    ("yield_outdoor", sa.String(100)),
    ("sources", postgresql.JSON()),
    ("last_verified", sa.Date()),
)


def upgrade() -> None:
    for name, col_type in _NEW_COLUMNS:
        op.add_column("reference_strains", sa.Column(name, col_type, nullable=True))


def downgrade() -> None:
    for name, _ in reversed(_NEW_COLUMNS):
        op.drop_column("reference_strains", name)
