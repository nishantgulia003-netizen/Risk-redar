"""Add responder verification and area dispatch workflow fields."""

from alembic import op
import sqlalchemy as sa


revision = "0004_add_responder_workflow_fields"
down_revision = "0003_add_safety_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("areas", sa.Column("dispatch_status", sa.String(20), nullable=False, server_default="none"))
    op.create_check_constraint(
        "ck_area_dispatch_status",
        "areas",
        "dispatch_status IN ('none', 'dispatched', 'in_progress', 'resolved')",
    )
    op.add_column("safety_reports", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("safety_reports", sa.Column("verified_by", sa.String(255), nullable=True))
    op.add_column("safety_reports", sa.Column("verification_decision", sa.String(20), nullable=True))
    op.create_check_constraint(
        "ck_safety_report_verification_decision",
        "safety_reports",
        "verification_decision IS NULL OR verification_decision IN ('confirm', 'dismiss')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_safety_report_verification_decision", "safety_reports", type_="check")
    op.drop_column("safety_reports", "verification_decision")
    op.drop_column("safety_reports", "verified_by")
    op.drop_column("safety_reports", "is_verified")
    op.drop_constraint("ck_area_dispatch_status", "areas", type_="check")
    op.drop_column("areas", "dispatch_status")
