from app.affective.assessor import AffectiveAssessor
from app.core.contracts import AffectiveAssessmentOutput


class FakeClassifierClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls: list[dict[str, str]] = []

    async def classify_affective_state(self, *, user_text: str, response_language: str):
        self.calls.append({"user_text": user_text, "response_language": response_language})
        return self.payload


async def test_affective_assessor_falls_back_without_classifier_client() -> None:
    assessor = AffectiveAssessor()
    fallback = AffectiveAssessmentOutput(
        affect_label="support_distress",
        intensity=0.62,
        needs_support=True,
        confidence=0.61,
        source="deterministic_placeholder",
        evidence=["stressed"],
    )

    result = await assessor.assess(
        user_text="I feel stressed",
        response_language="en",
        fallback=fallback,
    )

    assert result.affect_label == "support_distress"
    assert result.needs_support is True
    assert result.source == "fallback"


async def test_affective_assessor_uses_ai_classifier_when_payload_is_valid() -> None:
    classifier = FakeClassifierClient(
        {
            "affect_label": "support_distress",
            "intensity": 0.83,
            "needs_support": True,
            "confidence": 0.79,
            "evidence": ["overwhelmed", "anxious"],
        }
    )
    assessor = AffectiveAssessor(classifier_client=classifier)
    fallback = AffectiveAssessmentOutput()

    result = await assessor.assess(
        user_text="I feel overwhelmed and anxious",
        response_language="en",
        fallback=fallback,
    )

    assert classifier.calls == [
        {
            "user_text": "I feel overwhelmed and anxious",
            "response_language": "en",
        }
    ]
    assert result.affect_label == "support_distress"
    assert result.intensity == 0.83
    assert result.needs_support is True
    assert result.confidence == 0.79
    assert result.source == "ai_classifier"
    assert result.evidence == ["overwhelmed", "anxious"]


async def test_affective_assessor_uses_fallback_when_ai_payload_is_invalid() -> None:
    classifier = FakeClassifierClient({"affect_label": "unsupported"})
    assessor = AffectiveAssessor(classifier_client=classifier)
    fallback = AffectiveAssessmentOutput(
        affect_label="neutral",
        intensity=0.18,
        needs_support=False,
        confidence=0.45,
        source="deterministic_placeholder",
        evidence=[],
    )

    result = await assessor.assess(
        user_text="hello",
        response_language="en",
        fallback=fallback,
    )

    assert result.affect_label == "neutral"
    assert result.source == "fallback"


async def test_affective_assessor_preserves_structured_fallback_reason_from_classifier_payload() -> None:
    classifier = FakeClassifierClient({"_aion_affective_fallback_reason": "openai_affective_parse_failed"})
    assessor = AffectiveAssessor(classifier_client=classifier)
    fallback = AffectiveAssessmentOutput(
        affect_label="neutral",
        intensity=0.18,
        needs_support=False,
        confidence=0.45,
        source="deterministic_placeholder",
        evidence=["baseline"],
    )

    result = await assessor.assess(
        user_text="hello",
        response_language="en",
        fallback=fallback,
    )

    assert result.source == "fallback"
    assert result.evidence[0] == "fallback_reason:openai_affective_parse_failed"
    assert "baseline" in result.evidence


async def test_affective_assessor_adds_reason_marker_for_invalid_affective_label_payload() -> None:
    classifier = FakeClassifierClient({"affect_label": "unsupported"})
    assessor = AffectiveAssessor(classifier_client=classifier)
    fallback = AffectiveAssessmentOutput(
        affect_label="neutral",
        intensity=0.18,
        needs_support=False,
        confidence=0.45,
        source="deterministic_placeholder",
        evidence=[],
    )

    result = await assessor.assess(
        user_text="hello",
        response_language="en",
        fallback=fallback,
    )

    assert result.source == "fallback"
    assert result.evidence[0] == "fallback_reason:unsupported_affect_label"


async def test_affective_assessor_respects_disabled_policy_even_with_classifier_client() -> None:
    classifier = FakeClassifierClient(
        {
            "affect_label": "support_distress",
            "intensity": 0.83,
            "needs_support": True,
            "confidence": 0.79,
            "evidence": ["overwhelmed"],
        }
    )
    assessor = AffectiveAssessor(
        classifier_client=classifier,
        enabled=False,
        policy_source="explicit",
    )
    fallback = AffectiveAssessmentOutput(
        affect_label="neutral",
        intensity=0.18,
        needs_support=False,
        confidence=0.45,
        source="deterministic_placeholder",
        evidence=[],
    )

    result = await assessor.assess(
        user_text="hello",
        response_language="en",
        fallback=fallback,
    )

    assert classifier.calls == []
    assert result.source == "fallback"
    assert result.evidence[0] == "fallback_reason:policy_disabled"
    assert assessor.snapshot()["affective_assessment_posture"] == "fallback_only_policy_disabled"
