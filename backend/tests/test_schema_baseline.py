from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import UniqueConstraint, create_engine, inspect

from app.memory.models import Base


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _upgrade_schema_with_alembic(tmp_path, monkeypatch):
    database_path = (tmp_path / "migration_parity.sqlite3").resolve()
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path.as_posix()}")

    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    command.upgrade(config, "head")

    return create_engine(f"sqlite:///{database_path.as_posix()}")


def test_schema_baseline_includes_expected_tables() -> None:
    assert set(Base.metadata.tables) == {
        "aion_memory",
        "aion_semantic_embedding",
        "aion_profile",
        "aion_auth_user",
        "aion_auth_session",
        "aion_conclusion",
        "aion_relation",
        "aion_theta",
        "aion_goal",
        "aion_task",
        "aion_planned_work_item",
        "aion_goal_progress",
        "aion_goal_milestone",
        "aion_goal_milestone_history",
        "aion_reflection_task",
        "aion_subconscious_proposal",
        "aion_attention_turn",
        "aion_scheduler_cadence_evidence",
    }


def test_schema_baseline_preserves_named_unique_constraints() -> None:
    conclusion_constraints = {
        constraint.name
        for constraint in Base.metadata.tables["aion_conclusion"].constraints
        if isinstance(constraint, UniqueConstraint)
    }
    reflection_constraints = {
        constraint.name
        for constraint in Base.metadata.tables["aion_reflection_task"].constraints
        if isinstance(constraint, UniqueConstraint)
    }
    embedding_constraints = {
        constraint.name
        for constraint in Base.metadata.tables["aion_semantic_embedding"].constraints
        if isinstance(constraint, UniqueConstraint)
    }
    relation_constraints = {
        constraint.name
        for constraint in Base.metadata.tables["aion_relation"].constraints
        if isinstance(constraint, UniqueConstraint)
    }
    attention_constraints = {
        constraint.name
        for constraint in Base.metadata.tables["aion_attention_turn"].constraints
        if isinstance(constraint, UniqueConstraint)
    }
    auth_session_constraints = {
        constraint.name
        for constraint in Base.metadata.tables["aion_auth_session"].constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert "uq_aion_conclusion_user_kind_scope" in conclusion_constraints
    assert "uq_aion_reflection_task_event_id" in reflection_constraints
    assert "uq_aion_semantic_embedding_source" in embedding_constraints
    assert "uq_aion_relation_user_type_scope" in relation_constraints
    assert "uq_aion_attention_turn_user_conversation" in attention_constraints
    assert "uq_aion_auth_session_token_hash" in auth_session_constraints


def test_schema_baseline_tracks_structured_memory_payload_column() -> None:
    memory_columns = Base.metadata.tables["aion_memory"].columns

    assert "payload" in memory_columns


def test_alembic_head_reaches_current_schema_baseline(tmp_path, monkeypatch) -> None:
    engine = _upgrade_schema_with_alembic(tmp_path, monkeypatch)
    inspector = inspect(engine)

    assert set(inspector.get_table_names()) == set(Base.metadata.tables) | {"alembic_version"}


def test_alembic_head_includes_attention_and_proposal_contracts(tmp_path, monkeypatch) -> None:
    engine = _upgrade_schema_with_alembic(tmp_path, monkeypatch)
    inspector = inspect(engine)

    attention_columns = {column["name"] for column in inspector.get_columns("aion_attention_turn")}
    proposal_columns = {column["name"] for column in inspector.get_columns("aion_subconscious_proposal")}
    attention_constraint_names = {
        constraint["name"] for constraint in inspector.get_unique_constraints("aion_attention_turn")
    }

    assert {
        "user_id",
        "conversation_key",
        "turn_id",
        "status",
        "source_count",
        "owner_mode",
        "messages_json",
        "event_ids_json",
        "update_keys_json",
    }.issubset(attention_columns)
    assert {
        "user_id",
        "proposal_type",
        "payload",
        "source_event_id",
        "status",
        "decision_reason",
        "research_policy",
        "allowed_tools_json",
        "decided_at",
    }.issubset(proposal_columns)
    assert "uq_aion_attention_turn_user_conversation" in attention_constraint_names
