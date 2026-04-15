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
        language="en",
        language_confidence=0.8,
        ambiguity=0.1,
        initial_salience=0.5,
    )


def test_context_summary_stays_simple_without_recent_memory() -> None:
    result = ContextAgent().run(event=_event(), perception=_perception(), recent_memory=[])

    assert result.summary == "User said: 'hello' with detected intent 'share_information'."
    assert result.related_tags == ["general", "language:en"]


def test_context_summary_includes_recent_memory_signal() -> None:
    recent_memory = [
        {
            "id": 1,
            "event_id": "evt-prev",
            "summary": (
                "event=asked about deployment; response_language=en; context=old context; "
                "plan_goal=reply; action=success; expression=We deployed it successfully"
            ),
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
                "response_language=en; "
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


def test_context_prefers_same_language_memory_over_mismatched_recent_entries() -> None:
    perception = PerceptionOutput(
        event_type="statement",
        topic="general",
        intent="share_information",
        language="pl",
        language_confidence=0.9,
        ambiguity=0.1,
        initial_salience=0.5,
    )
    recent_memory = [
        {
            "id": 10,
            "event_id": "evt-en",
            "summary": (
                "event=deploy the fix; response_language=en; context=old context; "
                "plan_goal=reply; action=success; expression=Let's deploy it carefully"
            ),
            "importance": 0.95,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 11,
            "event_id": "evt-pl",
            "summary": (
                "event=wdroz poprawke; response_language=pl; context=stary kontekst; "
                "plan_goal=reply; action=success; expression=Jasne, lecimy z tym"
            ),
            "importance": 0.6,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=_event(), perception=perception, recent_memory=recent_memory)

    assert "wdroz poprawke" in result.summary
    assert "Jasne, lecimy z tym" in result.summary
    assert "deploy the fix" not in result.summary


def test_context_falls_back_to_unknown_language_memory_when_no_match_exists() -> None:
    recent_memory = [
        {
            "id": 12,
            "event_id": "evt-unknown",
            "summary": (
                "event=asked about rollout; context=old context; "
                "plan_goal=reply; action=success; expression=We can keep going"
            ),
            "importance": 0.8,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=_event(), perception=_perception(), recent_memory=recent_memory)

    assert "asked about rollout" in result.summary
    assert "We can keep going" in result.summary


def test_context_deduplicates_same_memory_summary() -> None:
    repeated_summary = (
        "event=deploy the fix now; response_language=en; context=old context; "
        "plan_goal=reply; action=success; expression=Please provide the deployment details"
    )
    recent_memory = [
        {
            "id": 13,
            "event_id": "evt-en-1",
            "summary": repeated_summary,
            "importance": 0.9,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 14,
            "event_id": "evt-en-2",
            "summary": repeated_summary,
            "importance": 0.8,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 15,
            "event_id": "evt-en-3",
            "summary": (
                "event=deploy checklist; response_language=en; context=other context; "
                "plan_goal=reply; action=success; expression=Let's verify the rollout checklist"
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=_event(), perception=_perception(), recent_memory=recent_memory)

    assert result.summary.count("deploy the fix now") == 1
    assert "deploy checklist" in result.summary


def test_context_deduplicates_near_duplicate_event_memory() -> None:
    recent_memory = [
        {
            "id": 16,
            "event_id": "evt-en-4",
            "summary": (
                "event=deploy the fix now; response_language=en; context=old context; "
                "plan_goal=reply; action=success; expression=Please provide the necessary deployment details to proceed."
            ),
            "importance": 0.9,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 17,
            "event_id": "evt-en-5",
            "summary": (
                "event=deploy the fix now!; response_language=en; context=updated context; "
                "plan_goal=reply; action=success; expression=To proceed with deploying the fix, please provide the necessary deployment details."
            ),
            "importance": 0.85,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 18,
            "event_id": "evt-en-6",
            "summary": (
                "event=deploy checklist; response_language=en; context=other context; "
                "plan_goal=reply; action=success; expression=Let's verify the rollout checklist"
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=_event(), perception=_perception(), recent_memory=recent_memory)

    assert result.summary.count("deploy the fix now") == 1
    assert "deploy checklist" in result.summary


def test_context_prefers_more_topically_relevant_memory_over_higher_importance() -> None:
    event = Event(
        event_id="evt-2",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "deploy the fix to production now"},
        meta=EventMeta(user_id="u-1", trace_id="t-2"),
    )
    recent_memory = [
        {
            "id": 19,
            "event_id": "evt-en-7",
            "summary": (
                "event=write blog post draft; response_language=en; context=old context; "
                "plan_goal=reply; action=success; expression=Let's outline the article first"
            ),
            "importance": 0.95,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 20,
            "event_id": "evt-en-8",
            "summary": (
                "event=deploy the fix to production; response_language=en; context=deploy context; "
                "plan_goal=reply; action=success; expression=Let's verify the production deploy steps"
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "deploy the fix to production" in result.summary
    assert "Let's verify the production deploy steps" in result.summary
    assert "write blog post draft" not in result.summary


def test_context_uses_importance_when_relevance_is_tied() -> None:
    event = Event(
        event_id="evt-3",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "status update please"},
        meta=EventMeta(user_id="u-1", trace_id="t-3"),
    )
    recent_memory = [
        {
            "id": 21,
            "event_id": "evt-en-9",
            "summary": (
                "event=deployment status update; response_language=en; context=old context; "
                "plan_goal=reply; action=success; expression=Production looks stable"
            ),
            "importance": 0.55,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 22,
            "event_id": "evt-en-10",
            "summary": (
                "event=deployment status update; response_language=en; context=newer context; "
                "plan_goal=reply; action=success; expression=Production is healthy and all services are up"
            ),
            "importance": 0.9,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "Production is healthy and all services are up" in result.summary


def test_context_skips_irrelevant_memory_for_specific_request() -> None:
    event = Event(
        event_id="evt-4",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "status update please"},
        meta=EventMeta(user_id="u-1", trace_id="t-4"),
    )
    recent_memory = [
        {
            "id": 23,
            "event_id": "evt-en-11",
            "summary": (
                "event=deploy the fix now; response_language=en; context=deploy context; "
                "plan_goal=reply; action=success; expression=Please provide the necessary deployment details to proceed."
            ),
            "importance": 0.95,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert result.summary == "User said: 'status update please' with detected intent 'share_information'."


def test_context_keeps_memory_for_ambiguous_short_follow_up() -> None:
    event = Event(
        event_id="evt-5",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "ok"},
        meta=EventMeta(user_id="u-1", trace_id="t-5"),
    )
    recent_memory = [
        {
            "id": 24,
            "event_id": "evt-en-12",
            "summary": (
                "event=deploy the fix now; response_language=en; context=deploy context; "
                "plan_goal=reply; action=success; expression=Please provide the necessary deployment details to proceed."
            ),
            "importance": 0.95,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "Relevant recent memory:" in result.summary
