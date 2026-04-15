from datetime import datetime, timezone

from app.core.contracts import ContextOutput, Event, EventMeta
from app.motivation.engine import MotivationEngine


def _event(text: str) -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _context(risk_level: float = 0.1) -> ContextOutput:
    return ContextOutput(summary="ctx", related_goals=[], related_tags=["general"], risk_level=risk_level)


def test_motivation_engine_requests_clarification_without_text() -> None:
    result = MotivationEngine().run(event=_event(""), context=_context())

    assert result.mode == "clarify"
    assert result.importance == 0.3


def test_motivation_engine_uses_support_mode_for_emotional_text() -> None:
    result = MotivationEngine().run(
        event=_event("I feel stressed and overwhelmed"),
        context=_context(),
    )

    assert result.mode == "support"
    assert result.valence < 0


def test_motivation_engine_uses_execute_mode_for_urgent_action_requests() -> None:
    result = MotivationEngine().run(
        event=_event("deploy the production fix now"),
        context=_context(risk_level=0.2),
    )

    assert result.mode == "execute"
    assert result.urgency >= 0.75
    assert result.importance >= 0.65


def test_motivation_engine_uses_analyze_mode_for_questions() -> None:
    result = MotivationEngine().run(
        event=_event("Can you explain why this rollout failed?"),
        context=_context(),
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.6


def test_motivation_engine_handles_polish_urgent_request() -> None:
    result = MotivationEngine().run(
        event=_event("wdroż to na produkcję teraz"),
        context=_context(),
    )

    assert result.mode == "execute"
    assert result.urgency >= 0.75
