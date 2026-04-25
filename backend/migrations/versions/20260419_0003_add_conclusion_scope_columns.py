"""Add scoped conclusion columns for global, goal, and task context."""

from alembic import op
import sqlalchemy as sa


revision = "20260419_0003"
down_revision = "20260417_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("aion_conclusion", schema=None) as batch_op:
        batch_op.add_column(sa.Column("scope_type", sa.String(length=16), nullable=False, server_default="global"))
        batch_op.add_column(sa.Column("scope_key", sa.String(length=64), nullable=False, server_default="global"))
        batch_op.drop_constraint("uq_aion_conclusion_user_kind", type_="unique")
        batch_op.create_unique_constraint(
            "uq_aion_conclusion_user_kind_scope",
            ["user_id", "kind", "scope_type", "scope_key"],
        )
        batch_op.create_index("ix_aion_conclusion_scope_type", ["scope_type"], unique=False)
        batch_op.create_index("ix_aion_conclusion_scope_key", ["scope_key"], unique=False)
        batch_op.alter_column("scope_type", server_default=None)
        batch_op.alter_column("scope_key", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("aion_conclusion", schema=None) as batch_op:
        batch_op.drop_index("ix_aion_conclusion_scope_key")
        batch_op.drop_index("ix_aion_conclusion_scope_type")
        batch_op.drop_constraint("uq_aion_conclusion_user_kind_scope", type_="unique")
        batch_op.create_unique_constraint("uq_aion_conclusion_user_kind", ["user_id", "kind"])
        batch_op.drop_column("scope_key")
        batch_op.drop_column("scope_type")
