from datetime import datetime, timezone

from app.agents.perception import PerceptionAgent
from app.core.contracts import AffectiveAssessmentOutput, Event, EventMeta, PerceptionOutput


def _event(text: str) -> Event:
    return Event(
        event_id="evt-affect-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-affect-1"),
    )


def test_affective_assessment_output_defaults() -> None:
    assessment = AffectiveAssessmentOutput()

    assert assessment.affect_label == "neutral"
    assert assessment.intensity == 0.0
    assert assessment.needs_support is False
    assert assessment.confidence == 0.0
    assert assessment.source == "deterministic_placeholder"
    assert assessment.evidence == []


def test_perception_output_embeds_affective_contract_by_default() -> None:
    perception = PerceptionOutput(
        event_type="statement",
        topic="general",
        topic_tags=["general"],
        intent="share_information",
        language="en",
        language_source="default",
        language_confidence=0.35,
        ambiguity=0.1,
        initial_salience=0.5,
    )

    assert perception.affective.affect_label == "neutral"
    assert perception.affective.source == "deterministic_placeholder"
    assert perception.affective.evidence == []


def test_perception_agent_emits_support_distress_affective_placeholder() -> None:
    perception = PerceptionAgent().run(
        _event("I feel overwhelmed and anxious about this release."),
        recent_memory=[],
    )

    assert perception.affective.affect_label == "support_distress"
    assert perception.affective.needs_support is True
    assert perception.affective.source == "deterministic_placeholder"
    assert perception.affective.confidence >= 0.61
    assert "overwhelmed" in perception.affective.evidence or "anxious" in perception.affective.evidence
