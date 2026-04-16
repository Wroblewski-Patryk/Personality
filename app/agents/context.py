from app.core.contracts import ContextOutput, Event, IdentityOutput, PerceptionOutput


class ContextAgent:
    GENERIC_TAGS = {"general"}
    SUPPORTED_CONCLUSION_KINDS = {"response_style", "collaboration_preference"}
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

    def _current_topic_tokens(self, event: Event, perception: PerceptionOutput) -> set[str]:
        tokens = set(perception.topic_tags)
        tokens.update(self._text_tokens(str(event.payload.get("text", ""))))
        return {self._canonical_text(token) for token in tokens if self._canonical_text(token)}

    def _related_tags(self, perception: PerceptionOutput) -> list[str]:
        raw_tags = [perception.topic, *perception.topic_tags, f"language:{perception.language}"]
        related_tags: list[str] = []
        seen: set[str] = set()
        for tag in raw_tags:
            cleaned = self._normalize_text(tag).lower()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            related_tags.append(tag)
        return related_tags

    def _summarize_conclusions(self, conclusions: list[dict] | None) -> str:
        if not conclusions:
            return ""

        summarized: list[str] = []
        seen: set[str] = set()
        for conclusion in conclusions:
            kind = str(conclusion.get("kind", "")).strip().lower()
            if kind not in self.SUPPORTED_CONCLUSION_KINDS:
                continue
            confidence = float(conclusion.get("confidence", 0.0))
            if confidence < 0.7:
                continue

            content = str(conclusion.get("content", "")).strip().lower()
            if not content:
                continue

            summary = self._summarize_conclusion(kind=kind, content=content)
            if not summary or summary in seen:
                continue

            seen.add(summary)
            summarized.append(summary)
            if len(summarized) >= 2:
                break

        if not summarized:
            return ""

        return " Stable user preferences: " + " | ".join(summarized) + "."

    def _summarize_conclusion(self, kind: str, content: str) -> str:
        if kind != "response_style":
            if kind == "collaboration_preference":
                if content == "hands_on":
                    return "prefers concrete execution help"
                if content == "guided":
                    return "prefers guided step by step help"
            return ""
        if content == "concise":
            return "prefers concise responses"
        if content == "structured":
            return "prefers structured responses"
        return ""

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

    def _memory_kind(self, memory_item: dict) -> str | None:
        fields = self._extract_fields(str(memory_item.get("summary", "")))
        return fields.get("memory_kind")

    def _memory_topics(self, memory_item: dict) -> set[str]:
        fields = self._extract_fields(str(memory_item.get("summary", "")))
        topics = fields.get("memory_topics", "")
        if not topics:
            return set()
        return {
            self._canonical_text(topic)
            for topic in topics.split(",")
            if self._canonical_text(topic)
        }

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
        current_tokens: set[str],
        preferred_language: str,
        current_mode: str,
    ) -> tuple[float, float, int, float]:
        fields = self._extract_fields(str(memory_item.get("summary", "")))
        memory_language = self._memory_language(memory_item)
        memory_kind = self._memory_kind(memory_item)
        event_text = fields.get("event", "")
        memory_tokens = self._memory_topics(memory_item) or self._text_tokens(event_text)
        overlap = len(current_tokens.intersection(memory_tokens))
        language_bonus = 1.0 if memory_language == preferred_language else 0.4 if memory_language is None else 0.0
        mode_bonus = 1.0 if memory_kind == current_mode else 0.45 if memory_kind is None else 0.0
        importance = float(memory_item.get("importance", 0.0))

        return (language_bonus, mode_bonus, overlap, importance)

    def _specific_topic_tags(self, perception: PerceptionOutput) -> set[str]:
        return {tag for tag in perception.topic_tags if tag not in self.GENERIC_TAGS}

    def _should_require_topical_match(self, current_text: str, perception: PerceptionOutput) -> bool:
        return len(self._text_tokens(current_text)) >= 2 or len(self._specific_topic_tags(perception)) >= 2

    def _current_memory_mode(self, current_text: str, perception: PerceptionOutput) -> str:
        return "semantic" if self._should_require_topical_match(current_text, perception) else "continuity"

    def _select_memory_items(
        self,
        recent_memory: list[dict],
        preferred_language: str,
        current_tokens: set[str],
        current_text: str,
        perception: PerceptionOutput,
        limit: int = 2,
    ) -> list[dict]:
        if not recent_memory:
            return []

        current_mode = self._current_memory_mode(current_text, perception)
        matching = [item for item in recent_memory if self._memory_language(item) == preferred_language]
        unknown_language = [item for item in recent_memory if self._memory_language(item) is None]
        fallback = matching or unknown_language or recent_memory

        mode_matching = [item for item in fallback if self._memory_kind(item) == current_mode]
        unknown_mode = [item for item in fallback if self._memory_kind(item) is None]
        fallback = mode_matching or unknown_mode or fallback

        scored = [
            (
                index,
                item,
                self._memory_relevance_components(
                    memory_item=item,
                    current_tokens=current_tokens,
                    preferred_language=preferred_language,
                    current_mode=current_mode,
                ),
            )
            for index, item in enumerate(fallback)
        ]
        topical = [entry for entry in scored if entry[2][2] > 0]
        if topical:
            candidate_pool = topical
        elif self._should_require_topical_match(current_text, perception):
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

    def run(
        self,
        event: Event,
        perception: PerceptionOutput,
        recent_memory: list[dict],
        conclusions: list[dict] | None = None,
        identity: IdentityOutput | None = None,
    ) -> ContextOutput:
        text = str(event.payload.get("text", "")).strip()
        identity_hint = ""
        if identity is not None:
            identity_hint = f" Identity stance: {', '.join(identity.behavioral_style)}."
        conclusion_hint = self._summarize_conclusions(conclusions)
        memory_hint = ""
        if recent_memory:
            current_tokens = self._current_topic_tokens(event=event, perception=perception)
            selected_memory = self._select_memory_items(
                recent_memory,
                preferred_language=perception.language,
                current_tokens=current_tokens,
                current_text=text,
                perception=perception,
            )
            memory_summaries = [
                self._summarize_memory_item(memory_item)
                for memory_item in selected_memory
            ]
            memory_summaries = [summary for summary in memory_summaries if summary]
            if memory_summaries:
                memory_hint = " Relevant recent memory: " + " | ".join(memory_summaries) + "."

        summary = (
            f"User said: '{text}' with detected intent '{perception.intent}'."
            + identity_hint
            + conclusion_hint
            + memory_hint
        )
        risk_level = 0.1 if text else 0.4

        return ContextOutput(
            summary=summary,
            related_goals=[],
            related_tags=self._related_tags(perception),
            risk_level=risk_level,
        )
