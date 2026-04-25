"""Add Telegram linking fields to aion_profile."""

from alembic import op
import sqlalchemy as sa


revision = "20260425_0010"
down_revision = "20260425_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("aion_profile", sa.Column("telegram_chat_id", sa.String(length=64), nullable=True))
    op.add_column("aion_profile", sa.Column("telegram_user_id", sa.String(length=64), nullable=True))
    op.add_column("aion_profile", sa.Column("telegram_link_code", sa.String(length=32), nullable=True))
    op.add_column(
        "aion_profile",
        sa.Column("telegram_link_code_issued_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("aion_profile", sa.Column("telegram_linked_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_aion_profile_telegram_link_code", "aion_profile", ["telegram_link_code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_aion_profile_telegram_link_code", table_name="aion_profile")
    op.drop_column("aion_profile", "telegram_linked_at")
    op.drop_column("aion_profile", "telegram_link_code_issued_at")
    op.drop_column("aion_profile", "telegram_link_code")
    op.drop_column("aion_profile", "telegram_user_id")
    op.drop_column("aion_profile", "telegram_chat_id")
