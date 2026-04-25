from app.core.contracts import AffectiveAssessmentOutput, Event, PerceptionOutput
from app.utils.language import detect_language, normalize_for_matching


class PerceptionAgent:
    def run(
        self,
        event: Event,
        recent_memory: list[dict] | None = None,
        user_profile: dict | None = None,
    ) -> PerceptionOutput:
        text = str(event.payload.get("text", "")).strip()
        lowered = normalize_for_matching(text)
        planning_keywords = {"plan", "zaplanuj", "rollout", "wdrozenie", "krok", "steps"}
        language = detect_language(text=text, recent_memory=recent_memory, user_profile=user_profile)
        affective = self._assess_affective_placeholder(lowered=lowered)

        event_type = "question" if text.endswith("?") else "statement"
        topic = "planning" if any(keyword in lowered for keyword in planning_keywords) else "general"
        topic_tags = self._topic_tags(lowered=lowered, topic=topic)
        intent = "request_help" if event_type == "question" else "share_information"
        ambiguity = 0.6 if not text else 0.1
        initial_salience = 0.8 if event_type == "question" else 0.5

        return PerceptionOutput(
            event_type=event_type,
            topic=topic,
            topic_tags=topic_tags,
            intent=intent,
            language=language.code,
            language_source=language.source,
            language_confidence=language.confidence,
            ambiguity=ambiguity,
            initial_salience=initial_salience,
            affective=affective,
        )

    def _topic_tags(self, lowered: str, topic: str) -> list[str]:
        tags: list[str] = []
        keyword_map = {
            "deploy": {"deploy", "wdroz", "wdrozenie", "release"},
            "production": {"production", "prod", "produkcja"},
            "planning": {"plan", "zaplanuj", "rollout", "steps", "krok"},
            "status": {"status", "update", "health"},
            "bug": {"bug", "fix", "issue", "problem", "napraw"},
            "telegram": {"telegram", "webhook", "bot"},
            "memory": {"memory", "context", "pamiec", "kontekst"},
        }

        for tag, keywords in keyword_map.items():
            if any(keyword in lowered for keyword in keywords):
                tags.append(tag)

        if topic not in tags:
            tags.insert(0, topic)

        return tags[:5]

    def _assess_affective_placeholder(self, lowered: str) -> AffectiveAssessmentOutput:
        if not lowered:
            return AffectiveAssessmentOutput(
                affect_label="neutral",
                intensity=0.0,
                needs_support=False,
                confidence=0.35,
                source="deterministic_placeholder",
                evidence=[],
            )

        distress_keywords = {
            "sad",
            "stressed",
            "overwhelmed",
            "anxious",
            "tired",
            "lonely",
            "upset",
            "scared",
            "smutny",
            "smutna",
            "zestresowany",
            "zestresowana",
            "przytloczony",
            "przytloczona",
            "zmeczony",
            "samotny",
            "samotna",
            "zdenerwowany",
            "zdenerwowana",
            "niespokojny",
            "niespokojna",
        }
        urgent_keywords = {
            "urgent",
            "asap",
            "immediately",
            "now",
            "blocked",
            "broken",
            "failing",
            "deadline",
            "pilne",
            "natychmiast",
            "teraz",
            "blokuje",
            "awaria",
            "termin",
        }
        positive_keywords = {
            "thanks",
            "thank you",
            "happy",
            "great",
            "awesome",
            "dzieki",
            "dziękuję",
            "super",
        }

        distress_matches = [keyword for keyword in distress_keywords if keyword in lowered]
        if distress_matches:
            return AffectiveAssessmentOutput(
                affect_label="support_distress",
                intensity=0.74 if len(distress_matches) > 1 else 0.62,
                needs_support=True,
                confidence=0.69 if len(distress_matches) > 1 else 0.61,
                source="deterministic_placeholder",
                evidence=distress_matches[:3],
            )

        urgent_matches = [keyword for keyword in urgent_keywords if keyword in lowered]
        if urgent_matches:
            return AffectiveAssessmentOutput(
                affect_label="urgent_pressure",
                intensity=0.66,
                needs_support=False,
                confidence=0.58,
                source="deterministic_placeholder",
                evidence=urgent_matches[:3],
            )

        positive_matches = [keyword for keyword in positive_keywords if keyword in lowered]
        if positive_matches:
            return AffectiveAssessmentOutput(
                affect_label="positive_engagement",
                intensity=0.45,
                needs_support=False,
                confidence=0.56,
                source="deterministic_placeholder",
                evidence=positive_matches[:3],
            )

        return AffectiveAssessmentOutput(
            affect_label="neutral",
            intensity=0.18,
            needs_support=False,
            confidence=0.45,
            source="deterministic_placeholder",
            evidence=[],
        )
