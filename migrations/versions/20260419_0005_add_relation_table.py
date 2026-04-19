"""Add relation table with scope and confidence fields."""

from alembic import op
import sqlalchemy as sa


revision = "20260419_0005"
down_revision = "20260419_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "aion_relation",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("relation_type", sa.String(length=32), nullable=False),
        sa.Column("relation_value", sa.String(length=128), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("scope_type", sa.String(length=16), nullable=False, server_default="global"),
        sa.Column("scope_key", sa.String(length=64), nullable=False, server_default="global"),
        sa.Column("supporting_event_id", sa.String(length=64), nullable=True),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("decay_rate", sa.Float(), nullable=False, server_default="0.02"),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "relation_type",
            "scope_type",
            "scope_key",
            name="uq_aion_relation_user_type_scope",
        ),
    )
    op.create_index("ix_aion_relation_user_id", "aion_relation", ["user_id"], unique=False)
    op.create_index("ix_aion_relation_relation_type", "aion_relation", ["relation_type"], unique=False)
    op.create_index("ix_aion_relation_scope_type", "aion_relation", ["scope_type"], unique=False)
    op.create_index("ix_aion_relation_scope_key", "aion_relation", ["scope_key"], unique=False)
    with op.batch_alter_table("aion_relation", schema=None) as batch_op:
        batch_op.alter_column("scope_type", server_default=None)
        batch_op.alter_column("scope_key", server_default=None)
        batch_op.alter_column("evidence_count", server_default=None)
        batch_op.alter_column("decay_rate", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_aion_relation_scope_key", table_name="aion_relation")
    op.drop_index("ix_aion_relation_scope_type", table_name="aion_relation")
    op.drop_index("ix_aion_relation_relation_type", table_name="aion_relation")
    op.drop_index("ix_aion_relation_user_id", table_name="aion_relation")
    op.drop_table("aion_relation")
