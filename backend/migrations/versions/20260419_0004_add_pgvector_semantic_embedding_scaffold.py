"""Add pgvector-ready semantic embedding storage scaffold."""

from alembic import op
import sqlalchemy as sa


revision = "20260419_0004"
down_revision = "20260419_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dialect_name = op.get_context().dialect.name
    if dialect_name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        op.execute(
            """
            CREATE TABLE aion_semantic_embedding (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                source_kind VARCHAR(24) NOT NULL,
                source_id VARCHAR(96) NOT NULL,
                source_event_id VARCHAR(64) NULL,
                scope_type VARCHAR(16) NOT NULL DEFAULT 'global',
                scope_key VARCHAR(64) NOT NULL DEFAULT 'global',
                content TEXT NOT NULL,
                embedding VECTOR(1536) NULL,
                embedding_model VARCHAR(64) NOT NULL DEFAULT 'deterministic-v1',
                embedding_dimensions INTEGER NOT NULL DEFAULT 32,
                metadata_json JSON NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                CONSTRAINT uq_aion_semantic_embedding_source UNIQUE (user_id, source_kind, source_id)
            )
            """
        )
        op.execute("CREATE INDEX ix_aion_semantic_embedding_user_id ON aion_semantic_embedding (user_id)")
        op.execute("CREATE INDEX ix_aion_semantic_embedding_source_kind ON aion_semantic_embedding (source_kind)")
        op.execute("CREATE INDEX ix_aion_semantic_embedding_source_id ON aion_semantic_embedding (source_id)")
        op.execute("CREATE INDEX ix_aion_semantic_embedding_source_event_id ON aion_semantic_embedding (source_event_id)")
        op.execute("CREATE INDEX ix_aion_semantic_embedding_scope_type ON aion_semantic_embedding (scope_type)")
        op.execute("CREATE INDEX ix_aion_semantic_embedding_scope_key ON aion_semantic_embedding (scope_key)")
        return

    op.create_table(
        "aion_semantic_embedding",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("source_kind", sa.String(length=24), nullable=False),
        sa.Column("source_id", sa.String(length=96), nullable=False),
        sa.Column("source_event_id", sa.String(length=64), nullable=True),
        sa.Column("scope_type", sa.String(length=16), nullable=False, server_default="global"),
        sa.Column("scope_key", sa.String(length=64), nullable=False, server_default="global"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("embedding_model", sa.String(length=64), nullable=False, server_default="deterministic-v1"),
        sa.Column("embedding_dimensions", sa.Integer(), nullable=False, server_default="32"),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "source_kind", "source_id", name="uq_aion_semantic_embedding_source"),
    )
    op.create_index("ix_aion_semantic_embedding_user_id", "aion_semantic_embedding", ["user_id"], unique=False)
    op.create_index(
        "ix_aion_semantic_embedding_source_kind",
        "aion_semantic_embedding",
        ["source_kind"],
        unique=False,
    )
    op.create_index("ix_aion_semantic_embedding_source_id", "aion_semantic_embedding", ["source_id"], unique=False)
    op.create_index(
        "ix_aion_semantic_embedding_source_event_id",
        "aion_semantic_embedding",
        ["source_event_id"],
        unique=False,
    )
    op.create_index(
        "ix_aion_semantic_embedding_scope_type",
        "aion_semantic_embedding",
        ["scope_type"],
        unique=False,
    )
    op.create_index(
        "ix_aion_semantic_embedding_scope_key",
        "aion_semantic_embedding",
        ["scope_key"],
        unique=False,
    )
    with op.batch_alter_table("aion_semantic_embedding", schema=None) as batch_op:
        batch_op.alter_column("scope_type", server_default=None)
        batch_op.alter_column("scope_key", server_default=None)
        batch_op.alter_column("embedding_model", server_default=None)
        batch_op.alter_column("embedding_dimensions", server_default=None)


def downgrade() -> None:
    dialect_name = op.get_context().dialect.name
    if dialect_name == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_aion_semantic_embedding_scope_key")
        op.execute("DROP INDEX IF EXISTS ix_aion_semantic_embedding_scope_type")
        op.execute("DROP INDEX IF EXISTS ix_aion_semantic_embedding_source_event_id")
        op.execute("DROP INDEX IF EXISTS ix_aion_semantic_embedding_source_id")
        op.execute("DROP INDEX IF EXISTS ix_aion_semantic_embedding_source_kind")
        op.execute("DROP INDEX IF EXISTS ix_aion_semantic_embedding_user_id")
        op.execute("DROP TABLE IF EXISTS aion_semantic_embedding")
        return

    op.drop_index("ix_aion_semantic_embedding_scope_key", table_name="aion_semantic_embedding")
    op.drop_index("ix_aion_semantic_embedding_scope_type", table_name="aion_semantic_embedding")
    op.drop_index("ix_aion_semantic_embedding_source_event_id", table_name="aion_semantic_embedding")
    op.drop_index("ix_aion_semantic_embedding_source_id", table_name="aion_semantic_embedding")
    op.drop_index("ix_aion_semantic_embedding_source_kind", table_name="aion_semantic_embedding")
    op.drop_index("ix_aion_semantic_embedding_user_id", table_name="aion_semantic_embedding")
    op.drop_table("aion_semantic_embedding")
