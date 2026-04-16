from sqlalchemy import UniqueConstraint

from app.memory.models import Base


def test_schema_baseline_includes_expected_tables() -> None:
    assert set(Base.metadata.tables) == {
        "aion_memory",
        "aion_profile",
        "aion_conclusion",
        "aion_theta",
        "aion_goal",
        "aion_task",
        "aion_goal_progress",
        "aion_goal_milestone",
        "aion_goal_milestone_history",
        "aion_reflection_task",
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

    assert "uq_aion_conclusion_user_kind" in conclusion_constraints
    assert "uq_aion_reflection_task_event_id" in reflection_constraints
