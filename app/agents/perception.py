from app.core.contracts import Event, PerceptionOutput
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
