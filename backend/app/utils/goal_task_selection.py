from collections.abc import Callable

from app.utils.language import normalize_for_matching

TokenizeFn = Callable[[str], set[str]]


def text_tokens(
    value: str,
    *,
    stopwords: set[str] | None = None,
    normalize: bool = False,
    min_length: int = 3,
) -> set[str]:
    source = normalize_for_matching(value) if normalize else str(value).strip().lower()
    canonical = "".join(char if char.isalnum() or char.isspace() else " " for char in source)
    blocked = stopwords or set()
    return {
        token
        for token in canonical.split()
        if len(token) >= min_length and token not in blocked
    }


def priority_rank(priority: str) -> int:
    return {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }.get(priority, 0)


def task_status_rank(status: str) -> int:
    return {
        "todo": 1,
        "in_progress": 2,
        "blocked": 3,
    }.get(status, 0)


def select_active_goals(
    *,
    active_goals: list[dict],
    current_tokens: set[str],
    tokenize: TokenizeFn,
    limit: int = 2,
) -> list[dict]:
    if not active_goals:
        return []

    ranked = sorted(
        active_goals,
        key=lambda goal: (
            len(current_tokens.intersection(tokenize(_goal_text(goal)))),
            priority_rank(str(goal.get("priority", ""))),
        ),
        reverse=True,
    )
    selected = [goal for goal in ranked if goal.get("name")]
    if current_tokens:
        topical = [goal for goal in selected if current_tokens.intersection(tokenize(_goal_text(goal)))]
        if topical:
            selected = topical
    return selected[:limit]


def select_active_tasks(
    *,
    active_tasks: list[dict],
    current_tokens: set[str],
    selected_goals: list[dict],
    tokenize: TokenizeFn,
    limit: int = 2,
) -> list[dict]:
    if not active_tasks:
        return []

    goal_ids = {goal.get("id") for goal in selected_goals if goal.get("id") is not None}
    ranked = sorted(
        active_tasks,
        key=lambda task: (
            1 if task.get("goal_id") in goal_ids and goal_ids else 0,
            len(current_tokens.intersection(tokenize(_task_text(task)))),
            task_status_rank(str(task.get("status", ""))),
            priority_rank(str(task.get("priority", ""))),
        ),
        reverse=True,
    )
    selected = [task for task in ranked if task.get("name")]
    if current_tokens:
        topical = [
            task
            for task in selected
            if current_tokens.intersection(tokenize(_task_text(task)))
            or (task.get("goal_id") in goal_ids and goal_ids)
        ]
        if topical:
            selected = topical
    return selected[:limit]


def select_relevant_goal(
    *,
    event_text: str,
    active_goals: list[dict],
    tokenize: TokenizeFn,
) -> dict | None:
    tokens = tokenize(event_text)
    ranked = sorted(
        active_goals,
        key=lambda goal: (
            len(tokens.intersection(tokenize(_goal_text(goal)))),
            priority_rank(str(goal.get("priority", ""))),
        ),
        reverse=True,
    )
    if not ranked:
        return None
    top = ranked[0]
    overlap = len(tokens.intersection(tokenize(_goal_text(top))))
    if overlap <= 0 and tokens:
        return None
    return top


def select_relevant_task(
    *,
    event_text: str,
    active_tasks: list[dict],
    tokenize: TokenizeFn,
    relevant_goal_id: int | None,
) -> dict | None:
    tokens = tokenize(event_text)
    ranked = sorted(
        active_tasks,
        key=lambda task: (
            1 if relevant_goal_id is not None and task.get("goal_id") == relevant_goal_id else 0,
            len(tokens.intersection(tokenize(_task_text(task)))),
            task_status_rank(str(task.get("status", ""))),
            priority_rank(str(task.get("priority", ""))),
        ),
        reverse=True,
    )
    if not ranked:
        return None
    top = ranked[0]
    overlap = len(tokens.intersection(tokenize(_task_text(top))))
    if overlap <= 0 and relevant_goal_id is None and tokens:
        return None
    return top


def related_goal_priority(
    *,
    text: str,
    goals: list[dict],
    tokenize: TokenizeFn,
) -> str | None:
    tokens = tokenize(text)
    best_priority: str | None = None
    best_rank = 0
    for goal in goals:
        goal_tokens = tokenize(_goal_text(goal))
        if tokens and not tokens.intersection(goal_tokens):
            continue
        rank = priority_rank(str(goal.get("priority", "")))
        if rank > best_rank:
            best_rank = rank
            best_priority = str(goal.get("priority", "")).strip().lower() or None
    return best_priority


def has_related_blocked_task(
    *,
    text: str,
    tasks: list[dict],
    tokenize: TokenizeFn,
) -> bool:
    tokens = tokenize(text)
    for task in tasks:
        if str(task.get("status", "")).strip().lower() != "blocked":
            continue
        task_tokens = tokenize(_task_text(task))
        if not tokens or tokens.intersection(task_tokens):
            return True
    return False


def _goal_text(goal: dict) -> str:
    return str(goal.get("name", "")) + " " + str(goal.get("description", ""))


def _task_text(task: dict) -> str:
    return str(task.get("name", "")) + " " + str(task.get("description", ""))
