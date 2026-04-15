from app.core.contracts import ContextOutput, Event, PerceptionOutput


class ContextAgent:
    STOPWORDS = {
        "a",
        "an",
        "and",
        "are",
        "do",
        "for",
        "how",
        "i",
        "in",
        "is",
        "it",
        "me",
        "my",
        "na",
        "o",
        "or",
        "please",
        "the",
        "this",
        "to",
        "we",
        "what",
        "with",
        "you",
        "czy",
        "co",
        "dla",
        "i",
        "jak",
        "mi",
        "mnie",
        "na",
        "po",
        "prosze",
        "sie",
        "to",
        "w",
        "z",
    }

    def _normalize_text(self, value: str) -> str:
        return " ".join(str(value).split())

    def _canonical_text(self, value: str) -> str:
        normalized = self._normalize_text(value).lower()
        return "".join(char if char.isalnum() or char.isspace() else " " for char in normalized).strip()

    def _text_tokens(self, value: str) -> set[str]:
        canonical = self._canonical_text(value)
        return {
            token
            for token in canonical.split()
            if len(token) >= 3 and token not in self.STOPWORDS
        }

    def _extract_fields(self, raw_summary: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for part in self._normalize_text(raw_summary).split(";"):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            fields[key.strip()] = value.strip()
        return fields

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

        fields = self._extract_fields(raw_summary)
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

    def _memory_language(self, memory_item: dict) -> str | None:
        fields = self._extract_fields(str(memory_item.get("summary", "")))
        return fields.get("response_language") or fields.get("language")

    def _memory_fingerprint(self, memory_item: dict) -> str:
        fields = self._extract_fields(str(memory_item.get("summary", "")))
        event_text = fields.get("event")
        if event_text:
            return f"event:{self._canonical_text(event_text)}"

        expression = fields.get("expression")
        if expression:
            return f"expression:{self._canonical_text(expression)}"

        return f"summary:{self._canonical_text(str(memory_item.get('summary', '')))}"

    def _memory_relevance_components(
        self,
        memory_item: dict,
        current_text: str,
        preferred_language: str,
    ) -> tuple[float, int, float]:
        fields = self._extract_fields(str(memory_item.get("summary", "")))
        memory_language = self._memory_language(memory_item)
        event_text = fields.get("event", "")
        current_tokens = self._text_tokens(current_text)
        memory_tokens = self._text_tokens(event_text)
        overlap = len(current_tokens.intersection(memory_tokens))
        language_bonus = 1.0 if memory_language == preferred_language else 0.4 if memory_language is None else 0.0
        importance = float(memory_item.get("importance", 0.0))

        return (language_bonus, overlap, importance)

    def _should_require_topical_match(self, current_text: str) -> bool:
        return len(self._text_tokens(current_text)) >= 2

    def _select_memory_items(
        self,
        recent_memory: list[dict],
        preferred_language: str,
        current_text: str,
        limit: int = 2,
    ) -> list[dict]:
        if not recent_memory:
            return []

        matching = [item for item in recent_memory if self._memory_language(item) == preferred_language]
        unknown = [item for item in recent_memory if self._memory_language(item) is None]
        fallback = matching or unknown or recent_memory

        scored = [
            (
                index,
                item,
                self._memory_relevance_components(
                    memory_item=item,
                    current_text=current_text,
                    preferred_language=preferred_language,
                ),
            )
            for index, item in enumerate(fallback)
        ]
        topical = [entry for entry in scored if entry[2][1] > 0]
        if topical:
            candidate_pool = topical
        elif self._should_require_topical_match(current_text):
            return []
        else:
            candidate_pool = scored

        ranked = sorted(
            candidate_pool,
            key=lambda pair: (
                pair[2],
                -pair[0],
            ),
            reverse=True,
        )

        selected: list[dict] = []
        seen_fingerprints: set[str] = set()
        for _, item, _ in ranked:
            fingerprint = self._memory_fingerprint(item)
            if fingerprint in seen_fingerprints:
                continue
            seen_fingerprints.add(fingerprint)
            selected.append(item)
            if len(selected) >= limit:
                break

        return selected

    def run(self, event: Event, perception: PerceptionOutput, recent_memory: list[dict]) -> ContextOutput:
        text = str(event.payload.get("text", "")).strip()
        memory_hint = ""
        if recent_memory:
            selected_memory = self._select_memory_items(
                recent_memory,
                preferred_language=perception.language,
                current_text=text,
            )
            memory_summaries = [
                self._summarize_memory_item(memory_item)
                for memory_item in selected_memory
            ]
            memory_summaries = [summary for summary in memory_summaries if summary]
            if memory_summaries:
                memory_hint = " Relevant recent memory: " + " | ".join(memory_summaries) + "."

        summary = f"User said: '{text}' with detected intent '{perception.intent}'." + memory_hint
        risk_level = 0.1 if text else 0.4

        return ContextOutput(
            summary=summary,
            related_goals=[],
            related_tags=[perception.topic, f"language:{perception.language}"],
            risk_level=risk_level,
        )
