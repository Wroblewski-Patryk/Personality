from app.core.contracts import ContextOutput, Event, PerceptionOutput


class ContextAgent:
    def _normalize_text(self, value: str) -> str:
        return " ".join(str(value).split())

    def _clip_text(self, value: str, max_length: int) -> str:
        text = self._normalize_text(value)
        if len(text) <= max_length:
            return text

        sentence_endings = [index for index, char in enumerate(text[:max_length]) if char in ".!?"]
        if sentence_endings:
            candidate = text[: sentence_endings[-1] + 1].strip()
            if len(candidate) >= max_length // 2:
                return candidate

        truncated = text[: max_length - 3].rstrip()
        if " " in truncated:
            truncated = truncated.rsplit(" ", 1)[0]

        return truncated.rstrip(" ,;:-") + "..."

    def _summarize_memory_item(self, memory_item: dict) -> str:
        raw_summary = self._normalize_text(memory_item.get("summary", ""))
        if not raw_summary:
            return ""

        fields: dict[str, str] = {}
        for part in raw_summary.split(";"):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            fields[key.strip()] = value.strip()

        event_text = fields.get("event")
        expression = fields.get("expression")
        if event_text and expression:
            clipped_event = self._clip_text(event_text, 48)
            clipped_expression = self._clip_text(expression, 96)
            summary = f"user said '{clipped_event}' and received '{clipped_expression}'"
        elif event_text:
            summary = f"user said '{self._clip_text(event_text, 72)}'"
        else:
            summary = self._clip_text(raw_summary, 140)

        return summary

    def run(self, event: Event, perception: PerceptionOutput, recent_memory: list[dict]) -> ContextOutput:
        text = str(event.payload.get("text", "")).strip()
        memory_hint = ""
        if recent_memory:
            memory_summaries = [
                self._summarize_memory_item(memory_item)
                for memory_item in recent_memory[:2]
            ]
            memory_summaries = [summary for summary in memory_summaries if summary]
            if memory_summaries:
                memory_hint = " Relevant recent memory: " + " | ".join(memory_summaries) + "."

        summary = f"User said: '{text}' with detected intent '{perception.intent}'." + memory_hint
        risk_level = 0.1 if text else 0.4

        return ContextOutput(
            summary=summary,
            related_goals=[],
            related_tags=[perception.topic],
            risk_level=risk_level,
        )
