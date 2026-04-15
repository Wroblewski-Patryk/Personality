from app.core.contracts import Event, PerceptionOutput


class PerceptionAgent:
    def run(self, event: Event) -> PerceptionOutput:
        text = str(event.payload.get("text", "")).strip()
        lowered = text.lower()
        planning_keywords = {"plan", "zaplanuj", "rollout", "wdrozenie", "wdrożenie", "krok", "steps"}

        event_type = "question" if text.endswith("?") else "statement"
        topic = "planning" if any(keyword in lowered for keyword in planning_keywords) else "general"
        intent = "request_help" if event_type == "question" else "share_information"
        ambiguity = 0.6 if not text else 0.1
        initial_salience = 0.8 if event_type == "question" else 0.5

        return PerceptionOutput(
            event_type=event_type,
            topic=topic,
            intent=intent,
            ambiguity=ambiguity,
            initial_salience=initial_salience,
        )
