from datetime import datetime, timezone

from app.agents.perception import PerceptionAgent
from app.core.contracts import Event, EventMeta
from app.utils.language import detect_language


def _event(text: str) -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def test_detect_language_prefers_explicit_request() -> None:
    result = detect_language("Reply in Polish, please.")

    assert result.code == "pl"
    assert result.source == "explicit_request"


def test_detect_language_uses_recent_memory_for_short_follow_up() -> None:
    result = detect_language(
        "ok",
        recent_memory=[
            {"summary": "event=hej; response_language=pl; expression=Jasne, robimy to."},
        ],
    )

    assert result.code == "pl"
    assert result.source == "recent_memory"


def test_detect_language_uses_user_profile_when_recent_memory_is_missing() -> None:
    result = detect_language(
        "ok",
        user_profile={"preferred_language": "pl", "language_confidence": 0.9},
    )

    assert result.code == "pl"
    assert result.source == "user_profile"


def test_detect_language_prefers_recent_memory_over_user_profile() -> None:
    result = detect_language(
        "ok",
        recent_memory=[
            {"summary": "event=hello; response_language=en; expression=Sure, let's keep going."},
        ],
        user_profile={"preferred_language": "pl", "language_confidence": 0.9},
    )

    assert result.code == "en"
    assert result.source == "recent_memory"


def test_detect_language_uses_payload_language_from_recent_memory() -> None:
    result = detect_language(
        "ok",
        recent_memory=[
            {"payload": {"response_language": "pl"}},
        ],
    )

    assert result.code == "pl"
    assert result.source == "recent_memory"


def test_detect_language_ignores_unsupported_memory_language_and_falls_back_to_profile() -> None:
    result = detect_language(
        "ok",
        recent_memory=[
            {"summary": "event=hola; response_language=es; expression=Vale."},
        ],
        user_profile={"preferred_language": "pl", "language_confidence": 0.9},
    )

    assert result.code == "pl"
    assert result.source == "user_profile"


def test_detect_language_can_prefer_explicit_profile_preference_on_ambiguous_follow_up() -> None:
    result = detect_language(
        "ok",
        recent_memory=[
            {"summary": "event=hello; response_language=en; expression=Sure, let's keep going."},
        ],
        user_profile={
            "preferred_language": "pl",
            "language_confidence": 0.93,
            "language_source": "explicit_request",
        },
    )

    assert result.code == "pl"
    assert result.source == "user_profile"


def test_perception_agent_propagates_detected_language() -> None:
    perception = PerceptionAgent().run(_event("How should we deploy this?"), recent_memory=[])

    assert perception.language == "en"
    assert perception.language_source == "keyword_signal"
    assert perception.language_confidence >= 0.5
    assert "deploy" in perception.topic_tags


def test_perception_agent_uses_memory_language_for_ambiguous_text() -> None:
    perception = PerceptionAgent().run(
        _event("dalej"),
        recent_memory=[
            {"summary": "event=czesc; response_language=pl; expression=Jasne, lecimy dalej."},
        ],
    )

    assert perception.language == "pl"
    assert perception.language_source == "recent_memory"
    assert perception.language_confidence >= 0.7


def test_perception_agent_uses_profile_language_for_ambiguous_text_without_recent_memory() -> None:
    perception = PerceptionAgent().run(
        _event("ok"),
        recent_memory=[],
        user_profile={"preferred_language": "pl", "language_confidence": 0.9},
    )

    assert perception.language == "pl"
    assert perception.language_source == "user_profile"
    assert perception.language_confidence >= 0.6


def test_perception_agent_emits_topic_tags_for_planning_and_production() -> None:
    perception = PerceptionAgent().run(_event("Can you plan the production rollout?"), recent_memory=[])

    assert perception.topic == "planning"
    assert "planning" in perception.topic_tags
    assert "production" in perception.topic_tags
