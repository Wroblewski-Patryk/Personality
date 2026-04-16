from app.core.contracts import ContextOutput, Event, MotivationOutput, PerceptionOutput
from app.utils.language import normalize_for_matching


class MotivationEngine:
    def run(
        self,
        event: Event,
        context: ContextOutput,
        perception: PerceptionOutput,
        user_preferences: dict | None = None,
        theta: dict | None = None,
    ) -> MotivationOutput:
        text = str(event.payload.get("text", "")).strip()
        lowered = normalize_for_matching(text)

        if not text:
            return MotivationOutput(
                importance=0.3,
                urgency=0.1,
                valence=0.0,
                arousal=0.1,
                mode="clarify",
            )

        emotional_keywords = {
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
        }
        urgent_keywords = {
            "urgent",
            "asap",
            "immediately",
            "now",
            "blocked",
            "broken",
            "production",
            "failing",
            "deadline",
            "pilne",
            "natychmiast",
            "teraz",
            "blokuje",
            "awaria",
            "produkcja",
            "termin",
        }
        analysis_keywords = {
            "analyze",
            "analysis",
            "review",
            "compare",
            "debug",
            "explain",
            "plan",
            "analiza",
            "przeanalizuj",
            "porownaj",
            "wyjasnij",
            "sprawdz",
            "zaplanuj",
        }
        execution_keywords = {
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
        positive_keywords = {"thanks", "thank you", "happy", "great", "awesome", "dzieki", "super"}

        has_question = text.endswith("?")
        has_urgent_signal = any(keyword in lowered for keyword in urgent_keywords) or "!" in text
        has_emotional_signal = any(keyword in lowered for keyword in emotional_keywords)
        has_analysis_signal = has_question or any(keyword in lowered for keyword in analysis_keywords)
        has_execution_signal = any(lowered.startswith(keyword) for keyword in execution_keywords)
        has_positive_signal = any(keyword in lowered for keyword in positive_keywords)
        is_brief_turn = len(lowered.split()) <= 4
        collaboration_preference = str((user_preferences or {}).get("collaboration_preference", "")).strip().lower()

        importance = 0.45
        importance += 0.15 if has_question else 0.0
        importance += 0.2 if has_urgent_signal else 0.0
        importance += min(context.risk_level, 0.2)

        urgency = 0.2
        urgency += 0.45 if has_urgent_signal else 0.0
        urgency += 0.1 if has_execution_signal else 0.0

        if has_emotional_signal:
            valence = -0.45
        elif has_positive_signal:
            valence = 0.35
        elif has_urgent_signal:
            valence = -0.1
        else:
            valence = 0.05

        arousal = 0.3
        arousal += 0.35 if has_urgent_signal else 0.0
        arousal += 0.2 if has_emotional_signal else 0.0
        arousal += 0.1 if has_question else 0.0

        theta_mode = None
        if not has_emotional_signal and not has_execution_signal and not has_analysis_signal:
            theta_mode = self._theta_mode(theta)
        collaboration_mode = None
        if not has_emotional_signal and not has_execution_signal and not has_analysis_signal:
            collaboration_mode = self._collaboration_mode(collaboration_preference)

        if has_emotional_signal:
            mode = "support"
        elif has_execution_signal:
            mode = "execute"
        elif has_analysis_signal:
            mode = "analyze"
        elif collaboration_mode and (
            perception.intent == "request_help"
            or (perception.topic == "general" and is_brief_turn and not has_positive_signal)
        ):
            mode = collaboration_mode
            importance += 0.05
            if collaboration_mode == "execute":
                urgency += 0.08
                arousal += 0.05
        elif theta_mode and (
            perception.intent == "request_help"
            or (perception.topic == "general" and is_brief_turn and not has_positive_signal)
        ):
            mode = theta_mode
            importance += 0.05
            if theta_mode == "execute":
                urgency += 0.08
                arousal += 0.05
            elif theta_mode == "support":
                valence = min(valence, -0.05)
        else:
            mode = "respond"

        return MotivationOutput(
            importance=self._clamp(importance),
            urgency=self._clamp(urgency),
            valence=max(-1.0, min(1.0, valence)),
            arousal=self._clamp(arousal),
            mode=mode,
        )

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, round(value, 2)))

    def _theta_mode(self, theta: dict | None) -> str | None:
        if not theta:
            return None

        candidates = {
            "support": float(theta.get("support_bias", 0.0) or 0.0),
            "analyze": float(theta.get("analysis_bias", 0.0) or 0.0),
            "execute": float(theta.get("execution_bias", 0.0) or 0.0),
        }
        mode, bias = max(candidates.items(), key=lambda item: item[1])
        if bias < 0.58:
            return None
        return mode

    def _collaboration_mode(self, collaboration_preference: str) -> str | None:
        if collaboration_preference == "hands_on":
            return "execute"
        if collaboration_preference == "guided":
            return "analyze"
        return None
