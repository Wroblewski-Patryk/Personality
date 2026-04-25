"""Add planned work table."""

from alembic import op
import sqlalchemy as sa


revision = "20260424_0008"
down_revision = "20260423_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "aion_planned_work_item",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("kind", sa.String(length=24), nullable=False),
        sa.Column("summary", sa.String(length=220), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("not_before", sa.DateTime(timezone=True), nullable=True),
        sa.Column("preferred_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recurrence_mode", sa.String(length=16), nullable=False),
        sa.Column("recurrence_rule", sa.String(length=120), nullable=False),
        sa.Column("delivery_channel", sa.String(length=16), nullable=False),
        sa.Column("requires_foreground_execution", sa.Integer(), nullable=False),
        sa.Column("quiet_hours_policy", sa.String(length=32), nullable=False),
        sa.Column("provenance", sa.String(length=32), nullable=False),
        sa.Column("source_event_id", sa.String(length=64), nullable=True),
        sa.Column("last_evaluated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_aion_planned_work_item_user_id", "aion_planned_work_item", ["user_id"], unique=False)
    op.create_index("ix_aion_planned_work_item_goal_id", "aion_planned_work_item", ["goal_id"], unique=False)
    op.create_index("ix_aion_planned_work_item_task_id", "aion_planned_work_item", ["task_id"], unique=False)
    op.create_index("ix_aion_planned_work_item_kind", "aion_planned_work_item", ["kind"], unique=False)
    op.create_index("ix_aion_planned_work_item_status", "aion_planned_work_item", ["status"], unique=False)
    op.create_index(
        "ix_aion_planned_work_item_not_before",
        "aion_planned_work_item",
        ["not_before"],
        unique=False,
    )
    op.create_index(
        "ix_aion_planned_work_item_preferred_at",
        "aion_planned_work_item",
        ["preferred_at"],
        unique=False,
    )
    op.create_index(
        "ix_aion_planned_work_item_expires_at",
        "aion_planned_work_item",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        "ix_aion_planned_work_item_source_event_id",
        "aion_planned_work_item",
        ["source_event_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_aion_planned_work_item_source_event_id", table_name="aion_planned_work_item")
    op.drop_index("ix_aion_planned_work_item_expires_at", table_name="aion_planned_work_item")
    op.drop_index("ix_aion_planned_work_item_preferred_at", table_name="aion_planned_work_item")
    op.drop_index("ix_aion_planned_work_item_not_before", table_name="aion_planned_work_item")
    op.drop_index("ix_aion_planned_work_item_status", table_name="aion_planned_work_item")
    op.drop_index("ix_aion_planned_work_item_kind", table_name="aion_planned_work_item")
    op.drop_index("ix_aion_planned_work_item_task_id", table_name="aion_planned_work_item")
    op.drop_index("ix_aion_planned_work_item_goal_id", table_name="aion_planned_work_item")
    op.drop_index("ix_aion_planned_work_item_user_id", table_name="aion_planned_work_item")
    op.drop_table("aion_planned_work_item")
