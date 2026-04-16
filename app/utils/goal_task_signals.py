from dataclasses import dataclass

from app.utils.language import normalize_for_matching


@dataclass(frozen=True)
class GoalSignal:
    name: str
    description: str
    priority: str
    goal_type: str


@dataclass(frozen=True)
class TaskSignal:
    name: str
    description: str
    priority: str
    status: str


def detect_goal_signal(text: str) -> GoalSignal | None:
    normalized = normalize_for_matching(text)
    if not normalized:
        return None

    patterns = (
        "my goal is to ",
        "the goal is to ",
        "goal: ",
        "i want to achieve ",
        "moim celem jest ",
        "celem jest ",
        "cel: ",
        "chce osiagnac ",
    )
    for pattern in patterns:
        if normalized.startswith(pattern):
            raw = text[len(pattern):].strip() if text.lower().startswith(pattern) else text.strip()
            cleaned = _clean_signal_text(raw, fallback=text)
            if not cleaned:
                return None
            return GoalSignal(
                name=cleaned[:160],
                description=f"User-declared goal: {cleaned[:220]}",
                priority=_goal_priority(normalized),
                goal_type=_goal_type(normalized),
            )
    return None


def detect_task_signal(text: str) -> TaskSignal | None:
    normalized = normalize_for_matching(text)
    if not normalized:
        return None

    patterns = (
        "i need to ",
        "next task is ",
        "task: ",
        "we need to ",
        "musze ",
        "mam zrobic ",
        "zadanie: ",
    )
    for pattern in patterns:
        if normalized.startswith(pattern):
            raw = text[len(pattern):].strip() if text.lower().startswith(pattern) else text.strip()
            cleaned = _clean_signal_text(raw, fallback=text)
            if not cleaned:
                return None
            return TaskSignal(
                name=cleaned[:160],
                description=f"User-declared task: {cleaned[:220]}",
                priority=_task_priority(normalized),
                status="blocked" if _looks_blocked(normalized) else "todo",
            )
    return None


def _goal_priority(normalized: str) -> str:
    if any(keyword in normalized for keyword in ("critical", "urgent", "production", "pilne", "produkcja")):
        return "critical"
    if any(keyword in normalized for keyword in ("this week", "mvp", "launch", "wydac", "w tym tygodniu")):
        return "high"
    return "medium"


def _goal_type(normalized: str) -> str:
    if any(keyword in normalized for keyword in ("this week", "today", "tomorrow", "w tym tygodniu", "dzis", "jutro")):
        return "operational"
    if any(keyword in normalized for keyword in ("mvp", "system", "architecture", "projekt", "project")):
        return "tactical"
    return "strategic"


def _task_priority(normalized: str) -> str:
    if any(
        keyword in normalized
        for keyword in ("urgent", "now", "production", "pilne", "teraz", "produkcja", "blocker", "blocked", "blokuje")
    ):
        return "high"
    return "medium"


def _looks_blocked(normalized: str) -> bool:
    return any(
        keyword in normalized
        for keyword in ("blocked", "blocker", "failing", "broken", "zablokowane", "blokuje", "awaria")
    )


def _clean_signal_text(value: str, fallback: str) -> str:
    text = " ".join(value.split()).strip(" .,:;!-")
    if not text:
        text = " ".join(fallback.split()).strip(" .,:;!-")
    return text
