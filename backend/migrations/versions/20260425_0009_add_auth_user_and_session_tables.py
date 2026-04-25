"""Add auth user and session tables."""

from alembic import op
import sqlalchemy as sa


revision = "20260425_0009"
down_revision = "20260424_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "aion_auth_user",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Integer(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_aion_auth_user_email", "aion_auth_user", ["email"], unique=True)

    op.create_table(
        "aion_auth_session",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("session_token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_agent", sa.String(length=256), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_token_hash", name="uq_aion_auth_session_token_hash"),
    )
    op.create_index("ix_aion_auth_session_user_id", "aion_auth_session", ["user_id"], unique=False)
    op.create_index(
        "ix_aion_auth_session_session_token_hash",
        "aion_auth_session",
        ["session_token_hash"],
        unique=False,
    )
    op.create_index("ix_aion_auth_session_expires_at", "aion_auth_session", ["expires_at"], unique=False)
    op.create_index("ix_aion_auth_session_revoked_at", "aion_auth_session", ["revoked_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_aion_auth_session_revoked_at", table_name="aion_auth_session")
    op.drop_index("ix_aion_auth_session_expires_at", table_name="aion_auth_session")
    op.drop_index("ix_aion_auth_session_session_token_hash", table_name="aion_auth_session")
    op.drop_index("ix_aion_auth_session_user_id", table_name="aion_auth_session")
    op.drop_table("aion_auth_session")

    op.drop_index("ix_aion_auth_user_email", table_name="aion_auth_user")
    op.drop_table("aion_auth_user")
