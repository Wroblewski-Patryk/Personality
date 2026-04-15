from app.core.contracts import ContextOutput, Event, PerceptionOutput, RoleOutput
from app.utils.language import normalize_for_matching


class RoleAgent:
    PREFERRED_ROLES = {"friend", "analyst", "executor", "mentor"}

    def run(
        self,
        event: Event,
        perception: PerceptionOutput,
        context: ContextOutput,
        user_preferences: dict | None = None,
    ) -> RoleOutput:
        text = str(event.payload.get("text", "")).strip()
        lowered = normalize_for_matching(text)
        preferred_role = str((user_preferences or {}).get("preferred_role", "")).strip().lower()
        preferred_role_confidence = float((user_preferences or {}).get("preferred_role_confidence", 0.0) or 0.0)

        emotional_keywords = {
            "sad",
            "stressed",
            "overwhelmed",
            "tired",
            "lonely",
            "happy",
            "anxious",
            "smutny",
            "smutna",
            "zestresowany",
            "zestresowana",
            "przytloczony",
            "przytloczona",
            "zmeczony",
            "samotny",
            "samotna",
            "szczesliwy",
            "niespokojny",
        }
        analysis_keywords = {
            "analyze",
            "analysis",
            "review",
            "compare",
            "debug",
            "explain",
            "analiza",
            "przeanalizuj",
            "porownaj",
            "wyjasnij",
            "sprawdz",
            "zaplanuj",
        }
        executor_keywords = {
            "build",
            "create",
            "write",
            "fix",
            "implement",
            "add",
            "setup",
            "deploy",
            "zbuduj",
            "stworz",
            "napisz",
            "napraw",
            "wdroz",
            "dodaj",
            "skonfiguruj",
            "ustaw",
            "zrob",
        }

        if any(keyword in lowered for keyword in emotional_keywords):
            return RoleOutput(selected="friend", confidence=0.74)

        if perception.topic == "planning" or any(keyword in lowered for keyword in analysis_keywords):
            return RoleOutput(selected="analyst", confidence=0.82)

        if any(lowered.startswith(keyword) for keyword in executor_keywords):
            return RoleOutput(selected="executor", confidence=0.78)

        if preferred_role in self.PREFERRED_ROLES and preferred_role_confidence >= 0.72:
            if perception.event_type == "question" or perception.intent == "request_help":
                return RoleOutput(selected=preferred_role, confidence=0.73)
            if perception.topic == "general":
                return RoleOutput(selected=preferred_role, confidence=0.68)

        if perception.event_type == "question" or perception.intent == "request_help":
            return RoleOutput(selected="mentor", confidence=0.71)

        if context.risk_level >= 0.5:
            return RoleOutput(selected="advisor", confidence=0.7)

        return RoleOutput(selected="advisor", confidence=0.6)
