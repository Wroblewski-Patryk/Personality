"""Add structured payload storage for episodic memory rows."""

from alembic import op
import sqlalchemy as sa


revision = "20260417_0002"
down_revision = "20260416_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("aion_memory", sa.Column("payload", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("aion_memory", "payload")
