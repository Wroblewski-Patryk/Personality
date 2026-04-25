from __future__ import annotations

from typing import Literal


ReflectionScopeType = Literal["global", "goal", "task"]

REFLECTION_SCOPE_POLICY_OWNER = "reflection_scope_policy"
GLOBAL_SCOPE_TYPE: ReflectionScopeType = "global"
GLOBAL_SCOPE_KEY = "global"

GOAL_SCOPED_CONCLUSION_KINDS = frozenset(
    {
        "goal_execution_state",
        "goal_progress_score",
        "goal_progress_trend",
        "goal_progress_arc",
        "goal_milestone_transition",
        "goal_milestone_state",
        "goal_milestone_arc",
        "goal_milestone_pressure",
        "goal_milestone_dependency_state",
        "goal_milestone_due_state",
        "goal_milestone_due_window",
        "goal_milestone_risk",
        "goal_completion_criteria",
    }
)
TASK_SCOPED_CONCLUSION_KINDS = frozenset()
GOAL_SCOPED_RELATION_TYPES = frozenset({"goal_execution_trust", "goal_collaboration_flow"})
TASK_SCOPED_RELATION_TYPES = frozenset()


def normalize_scope(scope_type: str | None, scope_key: str | None) -> tuple[ReflectionScopeType, str]:
    normalized_scope_type = str(scope_type or GLOBAL_SCOPE_TYPE).strip().lower()
    normalized_scope_key = str(scope_key or "").strip()
    if normalized_scope_type not in {"global", "goal", "task"}:
        return GLOBAL_SCOPE_TYPE, GLOBAL_SCOPE_KEY
    if normalized_scope_type == GLOBAL_SCOPE_TYPE:
        return GLOBAL_SCOPE_TYPE, GLOBAL_SCOPE_KEY
    if not normalized_scope_key:
        return GLOBAL_SCOPE_TYPE, GLOBAL_SCOPE_KEY
    return normalized_scope_type, normalized_scope_key


def conclusion_scope_type(kind: str) -> ReflectionScopeType:
    normalized_kind = str(kind).strip().lower()
    if normalized_kind in GOAL_SCOPED_CONCLUSION_KINDS:
        return "goal"
    if normalized_kind in TASK_SCOPED_CONCLUSION_KINDS:
        return "task"
    return "global"


def relation_scope_type(relation_type: str) -> ReflectionScopeType:
    normalized_relation_type = str(relation_type).strip().lower()
    if normalized_relation_type in GOAL_SCOPED_RELATION_TYPES:
        return "goal"
    if normalized_relation_type in TASK_SCOPED_RELATION_TYPES:
        return "task"
    return "global"


def resolve_conclusion_scope(
    *,
    kind: str,
    goal_id: int | str | None = None,
    task_id: int | str | None = None,
) -> tuple[ReflectionScopeType, str]:
    expected_scope_type = conclusion_scope_type(kind)
    if expected_scope_type == "goal" and goal_id is not None:
        return "goal", str(goal_id)
    if expected_scope_type == "task" and task_id is not None:
        return "task", str(task_id)
    return GLOBAL_SCOPE_TYPE, GLOBAL_SCOPE_KEY


def resolve_relation_scope(
    *,
    relation_type: str,
    goal_id: int | str | None = None,
    task_id: int | str | None = None,
) -> tuple[ReflectionScopeType, str]:
    expected_scope_type = relation_scope_type(relation_type)
    if expected_scope_type == "goal" and goal_id is not None:
        return "goal", str(goal_id)
    if expected_scope_type == "task" and task_id is not None:
        return "task", str(task_id)
    return GLOBAL_SCOPE_TYPE, GLOBAL_SCOPE_KEY


def canonicalize_conclusion_scope(
    *,
    kind: str,
    scope_type: str | None,
    scope_key: str | None,
) -> tuple[ReflectionScopeType, str]:
    expected_scope_type = conclusion_scope_type(kind)
    normalized_scope_type, normalized_scope_key = normalize_scope(scope_type=scope_type, scope_key=scope_key)
    if expected_scope_type == "global":
        return GLOBAL_SCOPE_TYPE, GLOBAL_SCOPE_KEY
    if normalized_scope_type == expected_scope_type:
        return normalized_scope_type, normalized_scope_key
    return GLOBAL_SCOPE_TYPE, GLOBAL_SCOPE_KEY


def canonicalize_relation_scope(
    *,
    relation_type: str,
    scope_type: str | None,
    scope_key: str | None,
) -> tuple[ReflectionScopeType, str]:
    expected_scope_type = relation_scope_type(relation_type)
    normalized_scope_type, normalized_scope_key = normalize_scope(scope_type=scope_type, scope_key=scope_key)
    if expected_scope_type == "global":
        return GLOBAL_SCOPE_TYPE, GLOBAL_SCOPE_KEY
    if normalized_scope_type == expected_scope_type:
        return normalized_scope_type, normalized_scope_key
    return GLOBAL_SCOPE_TYPE, GLOBAL_SCOPE_KEY


def conclusion_matches_scope_request(
    *,
    kind: str,
    row_scope_type: str | None,
    row_scope_key: str | None,
    requested_scope_type: str | None,
    requested_scope_key: str | None,
    include_global: bool,
) -> bool:
    expected_scope_type = conclusion_scope_type(kind)
    normalized_row_scope_type, normalized_row_scope_key = normalize_scope(
        scope_type=row_scope_type,
        scope_key=row_scope_key,
    )
    if expected_scope_type == "global":
        return normalized_row_scope_type == GLOBAL_SCOPE_TYPE

    if requested_scope_type is None and requested_scope_key is None:
        return True

    normalized_requested_scope_type, normalized_requested_scope_key = normalize_scope(
        scope_type=requested_scope_type,
        scope_key=requested_scope_key,
    )
    if normalized_requested_scope_type == GLOBAL_SCOPE_TYPE:
        return normalized_row_scope_type == GLOBAL_SCOPE_TYPE
    if normalized_row_scope_type == normalized_requested_scope_type and normalized_row_scope_key == normalized_requested_scope_key:
        return True
    if include_global and normalized_row_scope_type == GLOBAL_SCOPE_TYPE:
        return True
    return False


def relation_matches_scope_request(
    *,
    relation_type: str,
    row_scope_type: str | None,
    row_scope_key: str | None,
    requested_scope_type: str | None,
    requested_scope_key: str | None,
    include_global: bool,
) -> bool:
    expected_scope_type = relation_scope_type(relation_type)
    normalized_row_scope_type, normalized_row_scope_key = normalize_scope(
        scope_type=row_scope_type,
        scope_key=row_scope_key,
    )
    if expected_scope_type == "global":
        return normalized_row_scope_type == GLOBAL_SCOPE_TYPE

    if requested_scope_type is None and requested_scope_key is None:
        return True

    normalized_requested_scope_type, normalized_requested_scope_key = normalize_scope(
        scope_type=requested_scope_type,
        scope_key=requested_scope_key,
    )
    if normalized_requested_scope_type == GLOBAL_SCOPE_TYPE:
        return normalized_row_scope_type == GLOBAL_SCOPE_TYPE
    if normalized_row_scope_type == normalized_requested_scope_type and normalized_row_scope_key == normalized_requested_scope_key:
        return True
    if include_global and normalized_row_scope_type == GLOBAL_SCOPE_TYPE:
        return True
    return False


def reflection_scope_policy_snapshot() -> dict[str, object]:
    return {
        "reflection_scope_policy_owner": REFLECTION_SCOPE_POLICY_OWNER,
        "global_scope_type": GLOBAL_SCOPE_TYPE,
        "global_scope_key": GLOBAL_SCOPE_KEY,
        "goal_scoped_conclusion_kinds": sorted(GOAL_SCOPED_CONCLUSION_KINDS),
        "task_scoped_conclusion_kinds": sorted(TASK_SCOPED_CONCLUSION_KINDS),
        "goal_scoped_relation_types": sorted(GOAL_SCOPED_RELATION_TYPES),
        "task_scoped_relation_types": sorted(TASK_SCOPED_RELATION_TYPES),
    }
