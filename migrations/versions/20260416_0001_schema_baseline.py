"""Initial schema baseline for the current AION runtime state."""

from alembic import op
import sqlalchemy as sa


revision = "20260416_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "aion_memory",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("importance", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_aion_memory_event_id", "aion_memory", ["event_id"], unique=False)
    op.create_index("ix_aion_memory_trace_id", "aion_memory", ["trace_id"], unique=False)
    op.create_index("ix_aion_memory_user_id", "aion_memory", ["user_id"], unique=False)

    op.create_table(
        "aion_profile",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("preferred_language", sa.String(length=8), nullable=False),
        sa.Column("language_confidence", sa.Float(), nullable=False),
        sa.Column("language_source", sa.String(length=32), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "aion_conclusion",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("content", sa.String(length=128), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("supporting_event_id", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "kind", name="uq_aion_conclusion_user_kind"),
    )
    op.create_index("ix_aion_conclusion_kind", "aion_conclusion", ["kind"], unique=False)
    op.create_index("ix_aion_conclusion_user_id", "aion_conclusion", ["user_id"], unique=False)

    op.create_table(
        "aion_theta",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("support_bias", sa.Float(), nullable=False),
        sa.Column("analysis_bias", sa.Float(), nullable=False),
        sa.Column("execution_bias", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "aion_goal",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("goal_type", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_aion_goal_priority", "aion_goal", ["priority"], unique=False)
    op.create_index("ix_aion_goal_status", "aion_goal", ["status"], unique=False)
    op.create_index("ix_aion_goal_user_id", "aion_goal", ["user_id"], unique=False)

    op.create_table(
        "aion_task",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_aion_task_goal_id", "aion_task", ["goal_id"], unique=False)
    op.create_index("ix_aion_task_priority", "aion_task", ["priority"], unique=False)
    op.create_index("ix_aion_task_status", "aion_task", ["status"], unique=False)
    op.create_index("ix_aion_task_user_id", "aion_task", ["user_id"], unique=False)

    op.create_table(
        "aion_goal_progress",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("execution_state", sa.String(length=32), nullable=True),
        sa.Column("progress_trend", sa.String(length=32), nullable=True),
        sa.Column("source_event_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_aion_goal_progress_goal_id", "aion_goal_progress", ["goal_id"], unique=False)
    op.create_index("ix_aion_goal_progress_user_id", "aion_goal_progress", ["user_id"], unique=False)

    op.create_table(
        "aion_goal_milestone",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("phase", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("source_event_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_aion_goal_milestone_goal_id", "aion_goal_milestone", ["goal_id"], unique=False)
    op.create_index("ix_aion_goal_milestone_phase", "aion_goal_milestone", ["phase"], unique=False)
    op.create_index("ix_aion_goal_milestone_status", "aion_goal_milestone", ["status"], unique=False)
    op.create_index("ix_aion_goal_milestone_user_id", "aion_goal_milestone", ["user_id"], unique=False)

    op.create_table(
        "aion_goal_milestone_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=False),
        sa.Column("milestone_name", sa.String(length=160), nullable=False),
        sa.Column("phase", sa.String(length=32), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=True),
        sa.Column("completion_criteria", sa.String(length=64), nullable=True),
        sa.Column("source_event_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_aion_goal_milestone_history_goal_id",
        "aion_goal_milestone_history",
        ["goal_id"],
        unique=False,
    )
    op.create_index(
        "ix_aion_goal_milestone_history_phase",
        "aion_goal_milestone_history",
        ["phase"],
        unique=False,
    )
    op.create_index(
        "ix_aion_goal_milestone_history_risk_level",
        "aion_goal_milestone_history",
        ["risk_level"],
        unique=False,
    )
    op.create_index(
        "ix_aion_goal_milestone_history_user_id",
        "aion_goal_milestone_history",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "aion_reflection_task",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", name="uq_aion_reflection_task_event_id"),
    )
    op.create_index("ix_aion_reflection_task_event_id", "aion_reflection_task", ["event_id"], unique=False)
    op.create_index("ix_aion_reflection_task_status", "aion_reflection_task", ["status"], unique=False)
    op.create_index("ix_aion_reflection_task_user_id", "aion_reflection_task", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_aion_reflection_task_user_id", table_name="aion_reflection_task")
    op.drop_index("ix_aion_reflection_task_status", table_name="aion_reflection_task")
    op.drop_index("ix_aion_reflection_task_event_id", table_name="aion_reflection_task")
    op.drop_table("aion_reflection_task")

    op.drop_index("ix_aion_goal_milestone_history_user_id", table_name="aion_goal_milestone_history")
    op.drop_index("ix_aion_goal_milestone_history_risk_level", table_name="aion_goal_milestone_history")
    op.drop_index("ix_aion_goal_milestone_history_phase", table_name="aion_goal_milestone_history")
    op.drop_index("ix_aion_goal_milestone_history_goal_id", table_name="aion_goal_milestone_history")
    op.drop_table("aion_goal_milestone_history")

    op.drop_index("ix_aion_goal_milestone_user_id", table_name="aion_goal_milestone")
    op.drop_index("ix_aion_goal_milestone_status", table_name="aion_goal_milestone")
    op.drop_index("ix_aion_goal_milestone_phase", table_name="aion_goal_milestone")
    op.drop_index("ix_aion_goal_milestone_goal_id", table_name="aion_goal_milestone")
    op.drop_table("aion_goal_milestone")

    op.drop_index("ix_aion_goal_progress_user_id", table_name="aion_goal_progress")
    op.drop_index("ix_aion_goal_progress_goal_id", table_name="aion_goal_progress")
    op.drop_table("aion_goal_progress")

    op.drop_index("ix_aion_task_user_id", table_name="aion_task")
    op.drop_index("ix_aion_task_status", table_name="aion_task")
    op.drop_index("ix_aion_task_priority", table_name="aion_task")
    op.drop_index("ix_aion_task_goal_id", table_name="aion_task")
    op.drop_table("aion_task")

    op.drop_index("ix_aion_goal_user_id", table_name="aion_goal")
    op.drop_index("ix_aion_goal_status", table_name="aion_goal")
    op.drop_index("ix_aion_goal_priority", table_name="aion_goal")
    op.drop_table("aion_goal")

    op.drop_table("aion_theta")

    op.drop_index("ix_aion_conclusion_user_id", table_name="aion_conclusion")
    op.drop_index("ix_aion_conclusion_kind", table_name="aion_conclusion")
    op.drop_table("aion_conclusion")

    op.drop_table("aion_profile")

    op.drop_index("ix_aion_memory_user_id", table_name="aion_memory")
    op.drop_index("ix_aion_memory_trace_id", table_name="aion_memory")
    op.drop_index("ix_aion_memory_event_id", table_name="aion_memory")
    op.drop_table("aion_memory")
