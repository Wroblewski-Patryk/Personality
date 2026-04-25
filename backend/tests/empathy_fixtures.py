from dataclasses import dataclass

from app.core.contracts import AffectiveAssessmentOutput


@dataclass(frozen=True)
class EmpathyScenario:
    key: str
    text: str
    affect_label: str
    intensity: float
    needs_support: bool
    confidence: float
    evidence: tuple[str, ...]
    expected_min_urgency: float
    expected_max_valence: float
    expected_min_arousal: float

    def affective(self) -> AffectiveAssessmentOutput:
        return AffectiveAssessmentOutput(
            affect_label=self.affect_label,
            intensity=self.intensity,
            needs_support=self.needs_support,
            confidence=self.confidence,
            source="ai_classifier",
            evidence=list(self.evidence),
        )

    def classifier_payload(self) -> dict:
        return {
            "affect_label": self.affect_label,
            "intensity": self.intensity,
            "needs_support": self.needs_support,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
        }


EMPATHY_SUPPORT_SCENARIOS = [
    EmpathyScenario(
        key="emotionally_heavy_distress",
        text="I am panicking and I feel completely overwhelmed right now.",
        affect_label="support_distress",
        intensity=0.9,
        needs_support=True,
        confidence=0.83,
        evidence=("panicking", "overwhelmed"),
        expected_min_urgency=0.2,
        expected_max_valence=-0.6,
        expected_min_arousal=0.55,
    ),
    EmpathyScenario(
        key="ambiguous_emotional_freeze",
        text="I don't even know what to do anymore.",
        affect_label="support_distress",
        intensity=0.66,
        needs_support=True,
        confidence=0.74,
        evidence=("dont know", "stuck"),
        expected_min_urgency=0.2,
        expected_max_valence=-0.5,
        expected_min_arousal=0.5,
    ),
    EmpathyScenario(
        key="mixed_intent_distress_and_urgent_execution",
        text="Deploy the hotfix now, I am overwhelmed and spiraling.",
        affect_label="support_distress",
        intensity=0.78,
        needs_support=True,
        confidence=0.79,
        evidence=("overwhelmed", "spiraling"),
        expected_min_urgency=0.75,
        expected_max_valence=-0.58,
        expected_min_arousal=0.85,
    ),
]
