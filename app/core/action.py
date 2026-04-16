from app.core.contracts import (
    ActionResult,
    ContextOutput,
    Event,
    ExpressionOutput,
    MemoryRecord,
    MotivationOutput,
    PerceptionOutput,
    PlanOutput,
    RoleOutput,
)
from app.integrations.telegram.client import TelegramClient
from app.memory.repository import MemoryRepository
from app.utils.goal_task_signals import detect_goal_signal, detect_task_signal
from app.utils.preferences import detect_collaboration_preference, detect_response_style_preference


class ActionExecutor:
    GENERIC_TOPIC_TAGS = {"general"}
    PERSISTABLE_LANGUAGE_SOURCES = {"explicit_request", "diacritic_signal", "keyword_signal"}

    def __init__(self, memory_repository: MemoryRepository, telegram_client: TelegramClient):
        self.memory_repository = memory_repository
        self.telegram_client = telegram_client

    async def execute(self, plan: PlanOutput, event: Event, expression: ExpressionOutput) -> ActionResult:
        if not plan.needs_response:
            return ActionResult(status="noop", actions=[], notes="No response required.")

        if event.source == "telegram":
            chat_id = event.payload.get("chat_id")
            if chat_id is None:
                return ActionResult(
                    status="fail",
                    actions=[],
                    notes="Telegram response requested but chat_id is missing.",
                )

            telegram_result = await self.telegram_client.send_message(chat_id=chat_id, text=expression.message)
            if telegram_result.get("ok"):
                return ActionResult(
                    status="success",
                    actions=["send_telegram_message"],
                    notes="Telegram message sent.",
                )
            return ActionResult(
                status="fail",
                actions=["send_telegram_message"],
                notes=f"Telegram API error: {telegram_result}",
            )

        return ActionResult(status="success", actions=["api_response"], notes="Response returned via API.")

    async def persist_episode(
        self,
        event: Event,
        perception: PerceptionOutput,
        context: ContextOutput,
        motivation: MotivationOutput,
        role: RoleOutput,
        plan: PlanOutput,
        action_result: ActionResult,
        expression: ExpressionOutput,
    ) -> MemoryRecord:
        memory_kind = self._memory_kind(event, perception)
        memory_topics = self._memory_topics(event, perception)
        style_preference = detect_response_style_preference(str(event.payload.get("text", "")))
        collaboration_preference = detect_collaboration_preference(str(event.payload.get("text", "")))
        goal_signal = detect_goal_signal(str(event.payload.get("text", "")))
        task_signal = detect_task_signal(str(event.payload.get("text", "")))
        preference_update = (
            f"response_style:{style_preference.style}"
            if style_preference is not None
            else ""
        )
        collaboration_update = (
            collaboration_preference.preference
            if collaboration_preference is not None
            else ""
        )
        goal_update = ""
        task_update = ""

        if goal_signal is not None:
            stored_goal = await self.memory_repository.upsert_active_goal(
                user_id=event.meta.user_id,
                name=goal_signal.name,
                description=goal_signal.description,
                priority=goal_signal.priority,
                goal_type=goal_signal.goal_type,
            )
            goal_update = str(stored_goal["name"])

        if task_signal is not None:
            active_goals = await self.memory_repository.get_active_goals(user_id=event.meta.user_id, limit=5)
            linked_goal_id = self._match_goal_for_task(task_signal.name, active_goals)
            stored_task = await self.memory_repository.upsert_active_task(
                user_id=event.meta.user_id,
                name=task_signal.name,
                description=task_signal.description,
                priority=task_signal.priority,
                goal_id=linked_goal_id,
                status=task_signal.status,
            )
            task_update = str(stored_task["name"])

        summary = (
            f"event={event.payload.get('text', '')}; "
            f"memory_kind={memory_kind}; "
            f"memory_topics={','.join(memory_topics)}; "
            f"response_language={expression.language}; "
            f"preference_update={preference_update}; "
            f"collaboration_update={collaboration_update}; "
            f"goal_update={goal_update}; "
            f"task_update={task_update}; "
            f"context={context.summary}; "
            f"motivation={motivation.mode}; "
            f"role={role.selected}; "
            f"plan_goal={plan.goal}; "
            f"plan_steps={','.join(plan.steps)}; "
            f"action={action_result.status}; "
            f"expression={expression.message}"
        )
        summary = summary[:1000]

        stored = await self.memory_repository.write_episode(
            event_id=event.event_id,
            trace_id=event.meta.trace_id,
            source=event.source,
            user_id=event.meta.user_id,
            event_timestamp=event.timestamp,
            summary=summary,
            importance=motivation.importance,
        )

        if perception.language_source in self.PERSISTABLE_LANGUAGE_SOURCES:
            await self.memory_repository.upsert_user_profile_language(
                user_id=event.meta.user_id,
                language_code=expression.language,
                confidence=perception.language_confidence,
                source=perception.language_source,
            )

        return MemoryRecord(
            id=stored["id"],
            event_id=stored["event_id"],
            timestamp=stored["timestamp"],
            summary=stored["summary"],
            importance=stored["importance"],
        )

    def _match_goal_for_task(self, task_name: str, active_goals: list[dict]) -> int | None:
        task_tokens = self._text_tokens(task_name)
        best_goal_id: int | None = None
        best_score = 0
        for goal in active_goals:
            goal_id = goal.get("id")
            if goal_id is None:
                continue
            goal_tokens = self._text_tokens(str(goal.get("name", "")) + " " + str(goal.get("description", "")))
            overlap = len(task_tokens.intersection(goal_tokens))
            if overlap > best_score:
                best_score = overlap
                best_goal_id = int(goal_id)
        return best_goal_id

    def _memory_kind(self, event: Event, perception: PerceptionOutput) -> str:
        specific_topics = [
            topic
            for topic in self._memory_topics(event, perception)
            if topic not in self.GENERIC_TOPIC_TAGS
        ]
        return "semantic" if len(specific_topics) >= 2 else "continuity"

    def _memory_topics(self, event: Event, perception: PerceptionOutput) -> list[str]:
        text = str(event.payload.get("text", "")).strip().lower()
        canonical = "".join(char if char.isalnum() or char.isspace() else " " for char in text)
        stopwords = {
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
            "now",
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
            "jak",
            "mi",
            "mnie",
            "na",
            "po",
            "prosze",
            "sie",
            "teraz",
            "to",
            "w",
            "z",
        }
        topics: list[str] = []
        seen: set[str] = set()
        for tag in perception.topic_tags:
            cleaned = tag.strip().lower()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            topics.append(cleaned)
            if len(topics) >= 4:
                return topics

        for token in canonical.split():
            if len(token) < 3 or token in stopwords or token in seen:
                continue
            seen.add(token)
            topics.append(token)
            if len(topics) >= 4:
                break
        return topics

    def _text_tokens(self, value: str) -> set[str]:
        canonical = "".join(char if char.isalnum() or char.isspace() else " " for char in value.strip().lower())
        return {token for token in canonical.split() if len(token) >= 3}
