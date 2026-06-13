"""farms ponds stockings daily_logs

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "farms",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location", sa.String(500), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("total_area_acres", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_farms_organization_id", "farms", ["organization_id"])

    op.create_table(
        "ponds",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("farm_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("area_acres", sa.Float(), nullable=True),
        sa.Column("depth_feet", sa.Float(), nullable=True),
        sa.Column("pond_type", sa.String(50), nullable=True),
        sa.Column("water_source", sa.String(100), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "harvested", "fallow", "preparation", name="pondstatus"),
            nullable=False,
            server_default="preparation",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ponds_farm_id", "ponds", ["farm_id"])

    op.create_table(
        "stockings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("pond_id", sa.String(), nullable=False),
        sa.Column("stocking_date", sa.Date(), nullable=False),
        sa.Column("pl_count", sa.Integer(), nullable=True),
        sa.Column("stocking_density", sa.Float(), nullable=True),
        sa.Column("pl_source", sa.String(255), nullable=True),
        sa.Column("pl_age_days", sa.Integer(), nullable=True),
        sa.Column("seed_cost", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pond_id"], ["ponds.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stockings_pond_id", "stockings", ["pond_id"])

    op.create_table(
        "daily_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("pond_id", sa.String(), nullable=False),
        sa.Column("log_date", sa.Date(), nullable=False),
        sa.Column("doc", sa.Integer(), nullable=True),
        sa.Column("dissolved_oxygen", sa.Float(), nullable=True),
        sa.Column("ph", sa.Float(), nullable=True),
        sa.Column("salinity", sa.Float(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("alkalinity", sa.Float(), nullable=True),
        sa.Column("ammonia", sa.Float(), nullable=True),
        sa.Column("nitrite", sa.Float(), nullable=True),
        sa.Column("secchi_depth", sa.Float(), nullable=True),
        sa.Column("feed_quantity_kg", sa.Float(), nullable=True),
        sa.Column("feed_brand", sa.String(100), nullable=True),
        sa.Column("feed_type", sa.String(100), nullable=True),
        sa.Column("abw_grams", sa.Float(), nullable=True),
        sa.Column("mortality_count", sa.Integer(), nullable=True),
        sa.Column("sampling_count", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pond_id"], ["ponds.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_daily_logs_pond_id", "daily_logs", ["pond_id"])
    op.create_index("ix_daily_logs_log_date", "daily_logs", ["log_date"])


def downgrade() -> None:
    op.drop_table("daily_logs")
    op.drop_index("ix_stockings_pond_id", table_name="stockings")
    op.drop_table("stockings")
    op.drop_index("ix_ponds_farm_id", table_name="ponds")
    op.drop_table("ponds")
    op.execute("DROP TYPE IF EXISTS pondstatus")
    op.drop_index("ix_farms_organization_id", table_name="farms")
    op.drop_table("farms")
