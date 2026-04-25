"""Add durable attention and subconscious proposal tables."""

from alembic import op
import sqlalchemy as sa


revision = "20260422_0006"
down_revision = "20260419_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "aion_attention_turn",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("conversation_key", sa.String(length=96), nullable=False),
        sa.Column("turn_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("assembled_text", sa.Text(), nullable=True),
        sa.Column("owner_mode", sa.String(length=24), nullable=False),
        sa.Column("messages_json", sa.JSON(), nullable=True),
        sa.Column("event_ids_json", sa.JSON(), nullable=True),
        sa.Column("update_keys_json", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "conversation_key",
            name="uq_aion_attention_turn_user_conversation",
        ),
    )
    op.create_index("ix_aion_attention_turn_user_id", "aion_attention_turn", ["user_id"], unique=False)
    op.create_index(
        "ix_aion_attention_turn_conversation_key",
        "aion_attention_turn",
        ["conversation_key"],
        unique=False,
    )
    op.create_index("ix_aion_attention_turn_turn_id", "aion_attention_turn", ["turn_id"], unique=False)
    op.create_index("ix_aion_attention_turn_status", "aion_attention_turn", ["status"], unique=False)

    op.create_table(
        "aion_subconscious_proposal",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("proposal_type", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_event_id", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("research_policy", sa.String(length=16), nullable=False),
        sa.Column("allowed_tools_json", sa.JSON(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_aion_subconscious_proposal_user_id",
        "aion_subconscious_proposal",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_aion_subconscious_proposal_proposal_type",
        "aion_subconscious_proposal",
        ["proposal_type"],
        unique=False,
    )
    op.create_index(
        "ix_aion_subconscious_proposal_source_event_id",
        "aion_subconscious_proposal",
        ["source_event_id"],
        unique=False,
    )
    op.create_index(
        "ix_aion_subconscious_proposal_status",
        "aion_subconscious_proposal",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_aion_subconscious_proposal_status", table_name="aion_subconscious_proposal")
    op.drop_index("ix_aion_subconscious_proposal_source_event_id", table_name="aion_subconscious_proposal")
    op.drop_index("ix_aion_subconscious_proposal_proposal_type", table_name="aion_subconscious_proposal")
    op.drop_index("ix_aion_subconscious_proposal_user_id", table_name="aion_subconscious_proposal")
    op.drop_table("aion_subconscious_proposal")

    op.drop_index("ix_aion_attention_turn_status", table_name="aion_attention_turn")
    op.drop_index("ix_aion_attention_turn_turn_id", table_name="aion_attention_turn")
    op.drop_index("ix_aion_attention_turn_conversation_key", table_name="aion_attention_turn")
    op.drop_index("ix_aion_attention_turn_user_id", table_name="aion_attention_turn")
    op.drop_table("aion_attention_turn")
