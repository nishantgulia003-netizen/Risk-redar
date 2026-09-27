"""Add decaying, trust-weighted safety reports."""
from alembic import op
import sqlalchemy as sa

revision = "0003_add_safety_reports"
down_revision = "0002_upgrade_legacy_scaffold"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "safety_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reporter_id", sa.String(255), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("target_type IN ('road_segment', 'shelter', 'area')", name="ck_safety_report_target_type"),
        sa.CheckConstraint("source_type IN ('police', 'rescue_team', 'news', 'user')", name="ck_safety_report_source_type"),
        sa.CheckConstraint("status IN ('unsafe', 'safe', 'blocked', 'clear')", name="ck_safety_report_status"),
    )
    op.create_index("ix_safety_reports_target_created", "safety_reports", ["target_type", "target_id", "created_at"])


def downgrade() -> None:
    op.drop_table("safety_reports")
