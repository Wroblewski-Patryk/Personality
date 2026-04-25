"""Add scheduler cadence evidence table."""

from alembic import op
import sqlalchemy as sa


revision = "20260423_0007"
down_revision = "20260422_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "aion_scheduler_cadence_evidence",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cadence_kind", sa.String(length=24), nullable=False),
        sa.Column("execution_owner", sa.String(length=32), nullable=False),
        sa.Column("execution_mode", sa.String(length=24), nullable=False),
        sa.Column("summary_json", sa.JSON(), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "cadence_kind",
            name="uq_aion_scheduler_cadence_evidence_kind",
        ),
    )
    op.create_index(
        "ix_aion_scheduler_cadence_evidence_cadence_kind",
        "aion_scheduler_cadence_evidence",
        ["cadence_kind"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_aion_scheduler_cadence_evidence_cadence_kind",
        table_name="aion_scheduler_cadence_evidence",
    )
    op.drop_table("aion_scheduler_cadence_evidence")
