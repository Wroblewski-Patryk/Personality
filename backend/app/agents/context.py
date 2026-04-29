from app.core.contracts import ContextOutput, Event, IdentityOutput, PerceptionOutput
from app.core.web_knowledge_policy import web_knowledge_tooling_snapshot
from app.utils.goal_task_selection import (
    priority_rank as shared_priority_rank,
    select_active_goals as shared_select_active_goals,
    select_active_tasks as shared_select_active_tasks,
    task_status_rank as shared_task_status_rank,
    text_tokens as shared_text_tokens,
)
from app.memory.episodic import extract_episode_fields


class ContextAgent:
    GENERIC_TAGS = {"general"}
    SUPPORTED_CONCLUSION_KINDS = {
        "response_style",
        "collaboration_preference",
        "affective_support_pattern",
        "affective_support_sensitivity",
        "goal_execution_state",
        "goal_progress_score",
        "goal_progress_trend",
        "goal_progress_arc",
        "goal_milestone_state",
        "goal_milestone_arc",
        "goal_milestone_pressure",
        "goal_milestone_dependency_state",
        "goal_milestone_due_state",
        "goal_milestone_due_window",
        "goal_milestone_transition",
        "goal_milestone_risk",
        "goal_completion_criteria",
    }
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
        return shared_text_tokens(value, stopwords=self.STOPWORDS, normalize=False)

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

    def _priority_rank(self, priority: str) -> int:
        return shared_priority_rank(priority)

    def _task_status_rank(self, status: str) -> int:
        return shared_task_status_rank(status)

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

    def _summarize_relations(self, relations: list[dict] | None) -> str:
        if not relations:
            return ""

        relation_parts: list[str] = []
        seen: set[str] = set()
        for relation in relations:
            confidence = float(relation.get("confidence", 0.0) or 0.0)
            if confidence < 0.65:
                continue
            relation_type = str(relation.get("relation_type", "")).strip().lower()
            relation_value = str(relation.get("relation_value", "")).strip().lower()
            summary = self._summarize_relation(relation_type=relation_type, relation_value=relation_value)
            if not summary or summary in seen:
                continue
            seen.add(summary)
            relation_parts.append(summary)
            if len(relation_parts) >= 4:
                break

        if not relation_parts:
            return ""
        return " Relation cues: " + ". ".join(relation_parts) + "."

    def _summarize_relation(self, *, relation_type: str, relation_value: str) -> str:
        if relation_type == "collaboration_dynamic":
            if relation_value == "guided":
                return "current collaboration flow is guided and step-oriented"
            if relation_value == "hands_on":
                return "current collaboration flow prefers direct execution support"
        if relation_type == "support_intensity_preference":
            if relation_value == "high_support":
                return "relationship context benefits from explicit supportive framing"
            if relation_value == "balanced_support":
                return "relationship context benefits from balanced support and execution"
        if relation_type == "delivery_reliability":
            if relation_value == "high_trust":
                return "interaction trust is high when concrete delivery is proposed"
            if relation_value == "medium_trust":
                return "interaction trust improves with explicit next-step delivery"
        if relation_type == "contact_cadence_preference":
            if relation_value == "on_demand":
                return "user prefers assistant-initiated contact only on demand"
            if relation_value == "low_frequency":
                return "user prefers less frequent proactive contact"
            if relation_value == "scheduled_only":
                return "user prefers only scheduled reminders"
            if relation_value == "open_to_checkins":
                return "user is open to proactive check-ins"
        if relation_type == "interruption_tolerance":
            if relation_value == "low":
                return "user has low tolerance for interruptions"
            if relation_value == "high":
                return "user accepts more frequent interruptions"
        if relation_type == "interaction_ritual_preference":
            if relation_value == "avoid_repeated_greeting":
                return "avoid greeting the user at the start of every message"
            if relation_value == "warm_opening_ok":
                return "warm openings are acceptable"
        if relation_type == "goal_execution_trust":
            return "goal-focused trust is currently " + relation_value.replace("_", " ")
        return ""

    def _summarize_conclusion(self, kind: str, content: str) -> str:
        if kind != "response_style":
            if kind == "collaboration_preference":
                if content == "hands_on":
                    return "prefers concrete execution help"
                if content == "guided":
                    return "prefers guided step by step help"
            if kind == "affective_support_pattern":
                return self._summarize_affective_support_pattern(content)
            if kind == "affective_support_sensitivity":
                return self._summarize_affective_support_sensitivity(content)
            if kind == "goal_execution_state":
                if content == "blocked":
                    return "current goal progress is blocked by an active task"
                if content == "recovering":
                    return "current goal is recovering after a recent unblock or completion"
                if content == "advancing":
                    return "current goal work is actively advancing"
                if content == "progressing":
                    return "current goal work shows recent progress"
                if content == "stagnating":
                    return "current goal seems to be stagnating without recent execution"
            if kind == "goal_progress_score":
                return self._summarize_goal_progress_score(content)
            if kind == "goal_progress_trend":
                return self._summarize_goal_progress_trend(content)
            if kind == "goal_progress_arc":
                return self._summarize_goal_progress_arc(content)
            if kind == "goal_milestone_state":
                return self._summarize_goal_milestone_state(content)
            if kind == "goal_milestone_arc":
                return self._summarize_goal_milestone_arc(content)
            if kind == "goal_milestone_pressure":
                return self._summarize_goal_milestone_pressure(content)
            if kind == "goal_milestone_dependency_state":
                return self._summarize_goal_milestone_dependency_state(content)
            if kind == "goal_milestone_due_state":
                return self._summarize_goal_milestone_due_state(content)
            if kind == "goal_milestone_due_window":
                return self._summarize_goal_milestone_due_window(content)
            if kind == "goal_milestone_transition":
                return self._summarize_goal_milestone_transition(content)
            if kind == "goal_milestone_risk":
                return self._summarize_goal_milestone_risk(content)
            if kind == "goal_completion_criteria":
                return self._summarize_goal_completion_criteria(content)
            return ""
        if content == "concise":
            return "prefers concise responses"
        if content == "structured":
            return "prefers structured responses"
        return ""

    def _summarize_affective_support_pattern(self, content: str) -> str:
        if content == "recurring_distress":
            return "recent turns show recurring stress signals and benefit from supportive pacing"
        if content == "confidence_recovery":
            return "recent turns show confidence recovery after earlier stress"
        return ""

    def _summarize_affective_support_sensitivity(self, content: str) -> str:
        if content == "high":
            return "responds best to explicit emotional validation on challenging turns"
        if content == "moderate":
            return "responds well to brief supportive check-ins during problem solving"
        return ""

    def _summarize_goal_progress_score(self, content: str) -> str:
        try:
            score = float(content)
        except ValueError:
            return ""

        if score < 0.35:
            return "goal completion is still at an early stage"
        if score >= 0.75:
            return "goal completion is entering the final stretch"
        return "goal completion is around the midpoint"

    def _summarize_goal_progress_trend(self, content: str) -> str:
        if content == "improving":
            return "goal progress trend is improving"
        if content == "slipping":
            return "goal progress trend is slipping"
        if content == "steady":
            return "goal progress trend is staying steady"
        return ""

    def _summarize_goal_progress_arc(self, content: str) -> str:
        if content == "recovery_gaining_traction":
            return "goal recovery is gaining traction"
        if content == "breakthrough_momentum":
            return "goal progress has entered a breakthrough phase"
        if content == "unstable_progress":
            return "goal progress has become unstable"
        if content == "falling_behind":
            return "goal is falling behind its recent baseline"
        if content == "holding_pattern":
            return "goal progress is holding in a steady pattern"
        return ""

    def _summarize_goal_milestone_transition(self, content: str) -> str:
        if content == "entered_execution_phase":
            return "goal has crossed from early setup into active execution"
        if content == "entered_completion_window":
            return "goal has entered the completion window"
        if content == "slipped_from_completion_window":
            return "goal has slipped back out of the completion window"
        if content == "dropped_back_to_early_stage":
            return "goal has dropped back into an early execution stage"
        return ""

    def _summarize_goal_milestone_state(self, content: str) -> str:
        if content == "early_stage":
            return "current goal is still in an early stage"
        if content == "execution_phase":
            return "current goal is in an active execution phase"
        if content == "recovery_phase":
            return "current goal is in a recovery phase"
        if content == "completion_window":
            return "current goal is currently in the completion window"
        return ""

    def _summarize_goal_milestone_arc(self, content: str) -> str:
        if content == "closure_momentum":
            return "active milestone is building closure momentum"
        if content == "reentered_completion_window":
            return "active milestone has re-entered the completion window after recovery"
        if content == "recovery_backslide":
            return "active milestone has slipped back into recovery pressure"
        if content == "milestone_whiplash":
            return "active milestone is oscillating across phases"
        if content == "steady_closure":
            return "active milestone is holding steady near closure"
        return ""

    def _summarize_goal_milestone_pressure(self, content: str) -> str:
        if content == "building_closure_pressure":
            return "active milestone is approaching a closure push"
        if content == "lingering_completion":
            return "active milestone has lingered in the completion window for too long"
        if content == "dragging_recovery":
            return "active milestone recovery is dragging without enough closure"
        if content == "stale_execution":
            return "active milestone has stayed in execution too long without phase change"
        if content == "lingering_setup":
            return "active milestone has remained in setup longer than expected"
        return ""

    def _summarize_goal_milestone_dependency_state(self, content: str) -> str:
        if content == "blocked_dependency":
            return "active milestone is blocked by a remaining dependency"
        if content == "multi_step_dependency":
            return "active milestone still depends on multiple remaining work items"
        if content == "single_step_dependency":
            return "active milestone now depends on a single remaining work item"
        if content == "clear_to_close":
            return "active milestone has a clear dependency path to closure"
        return ""

    def _summarize_goal_milestone_due_state(self, content: str) -> str:
        if content == "closure_due_now":
            return "active milestone is due for a closure call"
        if content == "dependency_due_next":
            return "active milestone is due to resolve its next dependency"
        if content == "recovery_due_attention":
            return "active milestone recovery is due immediate attention"
        if content == "execution_due_attention":
            return "active milestone execution is due a concrete push"
        if content == "setup_due_start":
            return "active milestone setup is due its first execution move"
        return ""

    def _summarize_goal_milestone_due_window(self, content: str) -> str:
        if content == "fresh_due_window":
            return "active milestone has just entered a fresh due window"
        if content == "active_due_window":
            return "active milestone remains in an active due window"
        if content == "overdue_due_window":
            return "active milestone due window has become overdue"
        if content == "reopened_due_window":
            return "active milestone due window has reopened after recovery"
        return ""

    def _summarize_goal_milestone_risk(self, content: str) -> str:
        if content == "at_risk":
            return "active milestone is currently at risk"
        if content == "watch":
            return "active milestone needs closer monitoring"
        if content == "ready_to_close":
            return "active milestone looks ready to close"
        if content == "stabilizing":
            return "active milestone is stabilizing after recent movement"
        if content == "on_track":
            return "active milestone is staying on track"
        return ""

    def _summarize_goal_completion_criteria(self, content: str) -> str:
        if content == "resolve_remaining_blocker":
            return "goal completion depends on resolving the remaining blocker"
        if content == "finish_remaining_active_work":
            return "goal completion depends on finishing the remaining active work"
        if content == "confirm_goal_completion":
            return "goal completion now depends on confirming closure"
        if content == "stabilize_remaining_work":
            return "goal progress now depends on stabilizing the remaining work"
        if content == "unblock_next_task":
            return "goal progress now depends on unblocking the next task"
        if content == "define_first_execution_step":
            return "goal progress now depends on defining the first execution step"
        if content == "advance_next_task":
            return "goal progress now depends on advancing the next active task"
        return ""

    def _extract_fields(self, raw_summary: str) -> dict[str, str]:
        return extract_episode_fields({"summary": raw_summary})

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
        fields = extract_episode_fields(memory_item)
        raw_summary = self._normalize_text(memory_item.get("summary", ""))
        if not raw_summary and not fields:
            return ""

        event_text = fields.get("event")
        expression = fields.get("expression")
        if event_text and expression:
            clipped_event = self._clip_text(event_text, 48)
            clipped_expression = self._clip_text(expression, 96)
            summary = f"user said '{clipped_event}' and received '{clipped_expression}'"
        elif event_text:
            summary = f"user said '{self._clip_text(event_text, 72)}'"
        else:
            summary = self._clip_text(raw_summary or str(memory_item.get("payload", "")), 140)

        return summary

    def _memory_language(self, memory_item: dict) -> str | None:
        fields = extract_episode_fields(memory_item)
        return fields.get("response_language") or fields.get("language")

    def _memory_kind(self, memory_item: dict) -> str | None:
        fields = extract_episode_fields(memory_item)
        return fields.get("memory_kind")

    def _memory_affect_label(self, memory_item: dict) -> str | None:
        fields = extract_episode_fields(memory_item)
        value = str(fields.get("affect_label", "")).strip().lower()
        return value or None

    def _memory_affect_needs_support(self, memory_item: dict) -> bool:
        fields = extract_episode_fields(memory_item)
        value = str(fields.get("affect_needs_support", "")).strip().lower()
        return value in {"1", "true", "yes"}

    def _memory_topics(self, memory_item: dict) -> set[str]:
        fields = extract_episode_fields(memory_item)
        topics = fields.get("memory_topics", "")
        if not topics:
            return set()
        return {
            self._canonical_text(topic)
            for topic in topics.split(",")
            if self._canonical_text(topic)
        }

    def _memory_fingerprint(self, memory_item: dict) -> str:
        fields = extract_episode_fields(memory_item)
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
        perception: PerceptionOutput,
    ) -> tuple[float, float, int, float, float]:
        fields = extract_episode_fields(memory_item)
        memory_language = self._memory_language(memory_item)
        memory_kind = self._memory_kind(memory_item)
        event_text = fields.get("event", "")
        memory_tokens = self._memory_topics(memory_item) or self._text_tokens(event_text)
        overlap = len(current_tokens.intersection(memory_tokens))
        language_bonus = 1.0 if memory_language == preferred_language else 0.4 if memory_language is None else 0.0
        mode_bonus = 1.0 if memory_kind == current_mode else 0.45 if memory_kind is None else 0.0
        affective_bonus = 0.0
        memory_affect_label = self._memory_affect_label(memory_item)
        current_affect_label = str(perception.affective.affect_label).strip().lower()
        if perception.affective.needs_support and self._memory_affect_needs_support(memory_item):
            affective_bonus += 0.9
        if (
            current_affect_label
            and current_affect_label != "neutral"
            and memory_affect_label == current_affect_label
        ):
            affective_bonus += 0.7
        importance = float(memory_item.get("importance", 0.0))

        return (language_bonus, mode_bonus, overlap, affective_bonus, importance)

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
                    perception=perception,
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

    def _select_active_goals(self, active_goals: list[dict], current_tokens: set[str], limit: int = 2) -> list[dict]:
        return shared_select_active_goals(
            active_goals=active_goals,
            current_tokens=current_tokens,
            tokenize=self._text_tokens,
            limit=limit,
        )

    def _select_active_tasks(
        self,
        active_tasks: list[dict],
        current_tokens: set[str],
        selected_goals: list[dict],
        limit: int = 2,
    ) -> list[dict]:
        return shared_select_active_tasks(
            active_tasks=active_tasks,
            current_tokens=current_tokens,
            selected_goals=selected_goals,
            tokenize=self._text_tokens,
            limit=limit,
        )

    def _select_goal_progress_history(
        self,
        goal_progress_history: list[dict],
        selected_goals: list[dict],
        limit: int = 3,
    ) -> list[dict]:
        if not goal_progress_history:
            return []

        goal_ids = {int(goal["id"]) for goal in selected_goals if goal.get("id") is not None}
        if goal_ids:
            filtered = [
                item
                for item in goal_progress_history
                if int(item.get("goal_id", -1)) in goal_ids
            ]
            if filtered:
                return filtered[:limit]
        return goal_progress_history[:limit]

    def _select_goal_milestone_history(
        self,
        goal_milestone_history: list[dict],
        selected_goals: list[dict],
        limit: int = 3,
    ) -> list[dict]:
        if not goal_milestone_history:
            return []

        goal_ids = {int(goal["id"]) for goal in selected_goals if goal.get("id") is not None}
        if goal_ids:
            filtered = [
                item
                for item in goal_milestone_history
                if int(item.get("goal_id", -1)) in goal_ids
            ]
            if filtered:
                return filtered[:limit]
        return goal_milestone_history[:limit]

    def _select_goal_milestones(
        self,
        active_goal_milestones: list[dict],
        selected_goals: list[dict],
        limit: int = 2,
    ) -> list[dict]:
        if not active_goal_milestones:
            return []

        goal_ids = {int(goal["id"]) for goal in selected_goals if goal.get("id") is not None}
        if goal_ids:
            filtered = [
                item
                for item in active_goal_milestones
                if int(item.get("goal_id", -1)) in goal_ids
            ]
            if filtered:
                return filtered[:limit]
        return active_goal_milestones[:limit]

    def _goal_history_hint(self, goal_progress_history: list[dict]) -> str:
        if len(goal_progress_history) < 2:
            return ""

        ordered = list(reversed(goal_progress_history))
        scores: list[float] = []
        for item in ordered:
            try:
                scores.append(float(item.get("score", 0.0)))
            except (TypeError, ValueError):
                continue

        if len(scores) < 2:
            return ""

        start = round(scores[0], 2)
        end = round(scores[-1], 2)
        span = round(max(scores) - min(scores), 2)
        delta = round(end - start, 2)

        if span >= 0.3 and abs(delta) < 0.12:
            return f" Recent goal history has been volatile between {min(scores):.2f} and {max(scores):.2f}."
        if delta >= 0.2:
            return f" Recent goal history shows lift from {start:.2f} to {end:.2f}."
        if delta <= -0.2:
            return f" Recent goal history shows regression from {start:.2f} to {end:.2f}."
        return f" Recent goal history is holding near {end:.2f}."

    def _goal_milestone_history_hint(self, goal_milestone_history: list[dict]) -> str:
        if len(goal_milestone_history) < 2:
            return ""

        ordered = list(reversed(goal_milestone_history))
        start = ordered[0]
        end = ordered[-1]
        start_phase = str(start.get("phase", "")).strip().lower()
        end_phase = str(end.get("phase", "")).strip().lower()
        start_risk = str(start.get("risk_level", "")).strip().lower()
        end_risk = str(end.get("risk_level", "")).strip().lower()

        if start_phase != end_phase:
            return (
                " Recent milestone history moved from "
                f"{self._humanize_phase(start_phase)} to {self._humanize_phase(end_phase)}."
            )
        if start_risk and end_risk and start_risk != end_risk:
            return (
                " Recent milestone history shifted from "
                f"{self._humanize_risk(start_risk)} to {self._humanize_risk(end_risk)}."
            )
        if end_phase or end_risk:
            details = [self._humanize_phase(end_phase)] if end_phase else []
            if end_risk:
                details.append(self._humanize_risk(end_risk))
            return " Recent milestone history is holding in " + " with ".join(details) + "."
        return ""

    def run(
        self,
        event: Event,
        perception: PerceptionOutput,
        recent_memory: list[dict],
        conclusions: list[dict] | None = None,
        relations: list[dict] | None = None,
        identity: IdentityOutput | None = None,
        active_goals: list[dict] | None = None,
        active_tasks: list[dict] | None = None,
        active_goal_milestones: list[dict] | None = None,
        goal_milestone_history: list[dict] | None = None,
        goal_progress_history: list[dict] | None = None,
    ) -> ContextOutput:
        text = str(event.payload.get("text", "")).strip()
        identity_hint = ""
        known_user_name = None
        if identity is not None:
            identity_hint = f" Identity stance: {', '.join(identity.behavioral_style)}."
            known_user_name = str(identity.display_name or "").strip() or None
            if known_user_name:
                identity_hint += f" Known user name: {known_user_name}."
        tooling_snapshot = web_knowledge_tooling_snapshot()
        available_tool_hints: list[str] = []
        if bool(tooling_snapshot["knowledge_search"].get("ready", False)):
            available_tool_hints.append("search_web")
        if bool(tooling_snapshot["web_browser"].get("ready", False)):
            available_tool_hints.append("read_page")
        memory_continuity_available = bool(recent_memory or conclusions or relations or known_user_name)
        foreground_parts = [
            f"Current turn timestamp: {event.timestamp.isoformat()}.",
        ]
        if known_user_name:
            foreground_parts.append(f"Known user name: {known_user_name}.")
        foreground_parts.append(
            "Memory continuity is "
            + ("available from loaded runtime state." if memory_continuity_available else "not strongly grounded in this turn.")
        )
        if available_tool_hints:
            foreground_parts.append("Bounded tools available now: " + ", ".join(available_tool_hints) + ".")
        foreground_awareness_summary = " ".join(foreground_parts)
        current_tokens = self._current_topic_tokens(event=event, perception=perception)
        selected_goals = self._select_active_goals(active_goals or [], current_tokens=current_tokens)
        selected_tasks = self._select_active_tasks(
            active_tasks or [],
            current_tokens=current_tokens,
            selected_goals=selected_goals,
        )
        goal_hint = ""
        if selected_goals:
            goal_names = [str(goal.get("name", "")).strip() for goal in selected_goals if goal.get("name")]
            if goal_names:
                goal_hint = " Active goals: " + " | ".join(goal_names) + "."
        task_hint = ""
        if selected_tasks:
            task_parts = [
                f"{str(task.get('name', '')).strip()} ({str(task.get('status', '')).strip()})"
                for task in selected_tasks
                if task.get("name")
            ]
            if task_parts:
                task_hint = " Active tasks: " + " | ".join(task_parts) + "."
        milestone_hint = ""
        selected_milestones = self._select_goal_milestones(
            active_goal_milestones or [],
            selected_goals=selected_goals,
        )
        if selected_milestones:
            milestone_parts = [
                self._format_milestone_hint(item)
                for item in selected_milestones
                if item.get("name")
            ]
            if milestone_parts:
                milestone_hint = " Active milestones: " + " | ".join(milestone_parts) + "."
        goal_history_hint = self._goal_history_hint(
            self._select_goal_progress_history(goal_progress_history or [], selected_goals=selected_goals)
        )
        milestone_history_hint = self._goal_milestone_history_hint(
            self._select_goal_milestone_history(goal_milestone_history or [], selected_goals=selected_goals)
        )
        conclusion_hint = self._summarize_conclusions(conclusions)
        relation_hint = self._summarize_relations(relations)
        memory_hint = ""
        if recent_memory:
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
            + goal_hint
            + task_hint
            + milestone_hint
            + milestone_history_hint
            + goal_history_hint
            + conclusion_hint
            + relation_hint
            + memory_hint
            + " Foreground awareness: "
            + foreground_awareness_summary
        )
        risk_level = 0.1 if text else 0.4

        return ContextOutput(
            summary=summary,
            related_goals=[str(goal.get("name", "")).strip() for goal in selected_goals if goal.get("name")],
            related_tags=self._related_tags(perception),
            risk_level=risk_level,
            foreground_awareness_summary=foreground_awareness_summary,
            known_user_name=known_user_name,
            memory_continuity_available=memory_continuity_available,
            available_tool_hints=available_tool_hints,
        )

    def _format_milestone_hint(self, milestone: dict) -> str:
        name = str(milestone.get("name", "")).strip()
        phase = str(milestone.get("phase", "")).strip()
        raw_arc = milestone.get("arc")
        raw_pressure_level = milestone.get("pressure_level")
        raw_dependency_state = milestone.get("dependency_state")
        raw_due_state = milestone.get("due_state")
        raw_due_window = milestone.get("due_window")
        raw_risk_level = milestone.get("risk_level")
        raw_completion_criteria = milestone.get("completion_criteria")
        arc = str(raw_arc).strip().lower() if raw_arc else ""
        pressure_level = str(raw_pressure_level).strip().lower() if raw_pressure_level else ""
        dependency_state = str(raw_dependency_state).strip().lower() if raw_dependency_state else ""
        due_state = str(raw_due_state).strip().lower() if raw_due_state else ""
        due_window = str(raw_due_window).strip().lower() if raw_due_window else ""
        risk_level = str(raw_risk_level).strip().lower() if raw_risk_level else ""
        completion_criteria = str(raw_completion_criteria).strip().lower() if raw_completion_criteria else ""

        details = [phase] if phase else []
        if arc:
            details.append(self._humanize_arc(arc))
        if pressure_level:
            details.append(self._humanize_pressure(pressure_level))
        if dependency_state:
            details.append(self._humanize_dependency_state(dependency_state))
        if due_state:
            details.append(self._humanize_due_state(due_state))
        if due_window:
            details.append(self._humanize_due_window(due_window))
        if risk_level:
            details.append(risk_level)
        if completion_criteria:
            details.append(self._humanize_completion_criteria(completion_criteria))

        if not details:
            return name
        return f"{name} ({', '.join(details)})"

    def _humanize_completion_criteria(self, value: str) -> str:
        return {
            "resolve_remaining_blocker": "resolve remaining blocker",
            "finish_remaining_active_work": "finish remaining active work",
            "confirm_goal_completion": "confirm goal completion",
            "stabilize_remaining_work": "stabilize remaining work",
            "unblock_next_task": "unblock next task",
            "define_first_execution_step": "define first execution step",
            "advance_next_task": "advance next task",
        }.get(value, value.replace("_", " "))

    def _humanize_phase(self, value: str) -> str:
        return {
            "early_stage": "early stage",
            "execution_phase": "execution phase",
            "recovery_phase": "recovery phase",
            "completion_window": "completion window",
        }.get(value, value.replace("_", " "))

    def _humanize_arc(self, value: str) -> str:
        return {
            "closure_momentum": "closure momentum",
            "reentered_completion_window": "re-entered completion window",
            "recovery_backslide": "recovery backslide",
            "milestone_whiplash": "milestone whiplash",
            "steady_closure": "steady closure",
        }.get(value, value.replace("_", " "))

    def _humanize_pressure(self, value: str) -> str:
        return {
            "building_closure_pressure": "building closure pressure",
            "lingering_completion": "lingering completion",
            "dragging_recovery": "dragging recovery",
            "stale_execution": "stale execution",
            "lingering_setup": "lingering setup",
        }.get(value, value.replace("_", " "))

    def _humanize_dependency_state(self, value: str) -> str:
        return {
            "blocked_dependency": "blocked dependency",
            "multi_step_dependency": "multi-step dependency chain",
            "single_step_dependency": "single remaining dependency",
            "clear_to_close": "dependency path is clear",
        }.get(value, value.replace("_", " "))

    def _humanize_due_state(self, value: str) -> str:
        return {
            "closure_due_now": "closure is due now",
            "dependency_due_next": "next dependency is due now",
            "recovery_due_attention": "recovery needs attention now",
            "execution_due_attention": "execution needs a push now",
            "setup_due_start": "setup needs a start now",
        }.get(value, value.replace("_", " "))

    def _humanize_due_window(self, value: str) -> str:
        return {
            "fresh_due_window": "fresh due window",
            "active_due_window": "active due window",
            "overdue_due_window": "overdue due window",
            "reopened_due_window": "reopened due window",
        }.get(value, value.replace("_", " "))

    def _humanize_risk(self, value: str) -> str:
        return {
            "at_risk": "at risk",
            "watch": "watch status",
            "ready_to_close": "closure readiness",
            "stabilizing": "stabilizing risk",
            "on_track": "on-track status",
        }.get(value, value.replace("_", " "))
