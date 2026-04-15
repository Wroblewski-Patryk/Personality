from app.core.contracts import ContextOutput, Event, MotivationOutput


class MotivationEngine:
    def run(self, event: Event, context: ContextOutput) -> MotivationOutput:
        text = str(event.payload.get("text", "")).strip()
        lowered = text.lower()

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
            "przytłoczony",
            "przytloczona",
            "przytłoczona",
            "zmeczony",
            "zmęczony",
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
            "porównaj",
            "wyjasnij",
            "wyjaśnij",
            "sprawdz",
            "sprawdź",
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
            "stwórz",
            "napisz",
            "napraw",
            "wdroz",
            "wdroż",
            "dodaj",
            "skonfiguruj",
            "ustaw",
            "zrob",
            "zrób",
        }
        positive_keywords = {"thanks", "thank you", "happy", "great", "awesome", "dzieki", "dzięki", "super"}

        has_question = text.endswith("?")
        has_urgent_signal = any(keyword in lowered for keyword in urgent_keywords) or "!" in text
        has_emotional_signal = any(keyword in lowered for keyword in emotional_keywords)
        has_analysis_signal = has_question or any(keyword in lowered for keyword in analysis_keywords)
        has_execution_signal = any(lowered.startswith(keyword) for keyword in execution_keywords)
        has_positive_signal = any(keyword in lowered for keyword in positive_keywords)

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

        if has_emotional_signal:
            mode = "support"
        elif has_execution_signal:
            mode = "execute"
        elif has_analysis_signal:
            mode = "analyze"
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
