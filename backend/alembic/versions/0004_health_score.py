"""add health score to daily_logs

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("daily_logs", sa.Column("health_score", sa.Float(), nullable=True))
    op.add_column("daily_logs", sa.Column("health_status", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("daily_logs", "health_status")
    op.drop_column("daily_logs", "health_score")
