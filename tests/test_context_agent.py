from datetime import datetime, timezone

from app.agents.context import ContextAgent
from app.core.contracts import Event, EventMeta, PerceptionOutput


def _event() -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "hello"},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _perception() -> PerceptionOutput:
    return PerceptionOutput(
        event_type="statement",
        topic="general",
        intent="share_information",
        ambiguity=0.1,
        initial_salience=0.5,
    )


def test_context_summary_stays_simple_without_recent_memory() -> None:
    result = ContextAgent().run(event=_event(), perception=_perception(), recent_memory=[])

    assert result.summary == "User said: 'hello' with detected intent 'share_information'."


def test_context_summary_includes_recent_memory_signal() -> None:
    recent_memory = [
        {
            "id": 1,
            "event_id": "evt-prev",
            "summary": "event=asked about deployment; context=old context; plan_goal=reply; action=success; expression=We deployed it successfully",
            "importance": 0.8,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=_event(), perception=_perception(), recent_memory=recent_memory)

    assert "Relevant recent memory:" in result.summary
    assert "asked about deployment" in result.summary
    assert "We deployed it successfully" in result.summary


def test_clip_text_prefers_completed_sentence_when_it_fits() -> None:
    result = ContextAgent()._clip_text(
        "First complete sentence. Second sentence that should not fit cleanly.",
        30,
    )

    assert result == "First complete sentence."


def test_clip_text_falls_back_to_word_boundary_with_ellipsis() -> None:
    result = ContextAgent()._clip_text(
        "one two three four five six seven",
        18,
    )

    assert result == "one two three..."


def test_context_summary_clips_long_memory_cleanly() -> None:
    recent_memory = [
        {
            "id": 2,
            "event_id": "evt-prev-2",
            "summary": (
                "event=asked for a very detailed production verification walkthrough with extra deployment notes; "
                "context=old context; plan_goal=reply; action=success; "
                "expression=This response is intentionally long so the context summary has to cut it cleanly "
                "without stopping in the middle of a word or sentence fragment during runtime"
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=_event(), perception=_perception(), recent_memory=recent_memory)

    assert "asked for a very detailed production..." in result.summary
    assert "cut it cleanly without..." in result.summary
