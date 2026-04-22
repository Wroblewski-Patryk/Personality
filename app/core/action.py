from app.core.action_delivery import action_delivery_envelope_matches_plan
from app.core.contracts import (
    ActionDelivery,
    ActionResult,
    CalendarSchedulingIntentDomainIntent,
    ConnectedDriveAccessDomainIntent,
    ConnectorCapabilityDiscoveryDomainIntent,
    ContextOutput,
    Event,
    ExternalTaskSyncDomainIntent,
    ExpressionOutput,
    MaintainTaskStatusDomainIntent,
    MemoryRecord,
    MotivationOutput,
    NoopDomainIntent,
    PerceptionOutput,
    PlanOutput,
    PromoteInferredGoalDomainIntent,
    PromoteInferredTaskDomainIntent,
    RoleOutput,
    MaintainRelationDomainIntent,
    UpdateProactiveStateDomainIntent,
    UpdateCollaborationPreferenceDomainIntent,
    UpdateResponseStyleDomainIntent,
    UpdateTaskStatusDomainIntent,
    UpsertGoalDomainIntent,
    UpsertTaskDomainIntent,
)
from app.core.connector_policy import (
    connector_guardrail_snapshot,
    connector_intent_policy_violation,
)
from app.integrations.delivery_router import DeliveryRouter
from app.integrations.task_system.clickup_client import ClickUpTaskClient
from app.integrations.telegram.client import TelegramClient
from app.memory.embeddings import (
    materialize_embedding,
    normalize_embedding_refresh_mode,
    normalize_embedding_source_kinds,
    resolve_embedding_posture,
)
from app.memory.episodic import build_episode_summary
from app.memory.openai_embedding_client import OpenAIEmbeddingClient
from app.memory.repository import MemoryRepository


class ActionExecutor:
    GENERIC_TOPIC_TAGS = {"general"}
    PERSISTABLE_LANGUAGE_SOURCES = {"explicit_request", "diacritic_signal", "keyword_signal"}

    def __init__(
        self,
        memory_repository: MemoryRepository,
        telegram_client: TelegramClient,
        *,
        semantic_vector_enabled: bool = True,
        embedding_provider: str = "deterministic",
        embedding_model: str = "deterministic-v1",
        embedding_dimensions: int = 32,
        embedding_source_kinds: tuple[str, ...] | None = None,
        embedding_refresh_mode: str = "on_write",
        openai_api_key: str | None = None,
        openai_embedding_client: OpenAIEmbeddingClient | None = None,
        clickup_task_client: ClickUpTaskClient | None = None,
    ):
        self.memory_repository = memory_repository
        self.delivery_router = DeliveryRouter(telegram_client=telegram_client)
        self.semantic_vector_enabled = semantic_vector_enabled
        self.embedding_dimensions = max(1, int(embedding_dimensions))
        self.embedding_refresh_mode = normalize_embedding_refresh_mode(embedding_refresh_mode)
        if embedding_source_kinds is None:
            self.embedding_source_kinds = set(normalize_embedding_source_kinds(None))
        else:
            self.embedding_source_kinds = {str(item).strip().lower() for item in embedding_source_kinds if str(item).strip()}
        self.embedding_posture = resolve_embedding_posture(
            provider=embedding_provider,
            model=embedding_model,
            openai_api_key=openai_api_key,
        )
        self.openai_embedding_client = openai_embedding_client
        if self.openai_embedding_client is None and str(openai_api_key or "").strip():
            self.openai_embedding_client = OpenAIEmbeddingClient(api_key=openai_api_key)
        self.clickup_task_client = clickup_task_client

    async def execute(self, plan: PlanOutput, delivery: ActionDelivery) -> ActionResult:
        proactive_delivery_guard = plan.proactive_delivery_guard
        if proactive_delivery_guard is not None and not proactive_delivery_guard.allowed:
            return ActionResult(
                status="noop",
                actions=[],
                notes=f"Proactive delivery deferred: {proactive_delivery_guard.reason}.",
            )
        connector_policy_violations = self._connector_policy_violations(plan)
        if connector_policy_violations:
            return ActionResult(
                status="fail",
                actions=[],
                notes=(
                    "Connector policy guardrail blocked inconsistent intent posture: "
                    + "; ".join(connector_policy_violations)
                ),
            )
        if not action_delivery_envelope_matches_plan(
            envelope=delivery.execution_envelope,
            plan=plan,
        ):
            return ActionResult(
                status="fail",
                actions=[],
                notes="Action delivery envelope drift detected between planning and action.",
            )
        connector_execution_result = await self._execute_provider_backed_connector_intents(plan)
        if connector_execution_result is not None and connector_execution_result.status == "fail":
            return connector_execution_result
        if not plan.needs_response:
            if connector_execution_result is not None:
                return connector_execution_result
            return ActionResult(status="noop", actions=[], notes="No response required.")
        delivery_result = await self.delivery_router.deliver(delivery)
        if connector_execution_result is None:
            return delivery_result
        return self._merge_connector_execution_with_delivery(
            connector_execution_result=connector_execution_result,
            delivery_result=delivery_result,
        )

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
        intent_updates = await self._apply_domain_intents(event=event, plan=plan)
        preference_update = str(intent_updates["preference_update"])
        collaboration_update = str(intent_updates["collaboration_update"])
        goal_update = str(intent_updates["goal_update"])
        task_update = str(intent_updates["task_update"])
        task_status_update = str(intent_updates["task_status_update"])
        calendar_connector_update = str(intent_updates["calendar_connector_update"])
        task_connector_update = str(intent_updates["task_connector_update"])
        drive_connector_update = str(intent_updates["drive_connector_update"])
        connector_expansion_update = str(intent_updates["connector_expansion_update"])
        relation_update = str(intent_updates["relation_update"])
        proactive_state_update = str(intent_updates["proactive_state_update"])
        calendar_connector_guardrail = str(intent_updates["calendar_connector_guardrail"])
        task_connector_guardrail = str(intent_updates["task_connector_guardrail"])
        drive_connector_guardrail = str(intent_updates["drive_connector_guardrail"])
        connector_expansion_guardrail = str(intent_updates["connector_expansion_guardrail"])
        executed_intents = list(intent_updates["executed_intents"])

        payload = {
            "payload_version": 1,
            "event": str(event.payload.get("text", "")),
            "memory_kind": memory_kind,
            "memory_topics": memory_topics,
            "domain_intents": executed_intents,
            "response_language": expression.language,
            "affect_label": perception.affective.affect_label,
            "affect_intensity": perception.affective.intensity,
            "affect_needs_support": perception.affective.needs_support,
            "affect_source": perception.affective.source,
            "affect_evidence": perception.affective.evidence[:3],
            "preference_update": preference_update,
            "collaboration_update": collaboration_update,
            "goal_update": goal_update,
            "task_update": task_update,
            "task_status_update": task_status_update,
            "calendar_connector_update": calendar_connector_update,
            "task_connector_update": task_connector_update,
            "drive_connector_update": drive_connector_update,
            "connector_expansion_update": connector_expansion_update,
            "relation_update": relation_update,
            "proactive_state_update": proactive_state_update,
            "calendar_connector_guardrail": calendar_connector_guardrail,
            "task_connector_guardrail": task_connector_guardrail,
            "drive_connector_guardrail": drive_connector_guardrail,
            "connector_expansion_guardrail": connector_expansion_guardrail,
            "context": context.summary,
            "motivation": motivation.mode,
            "role": role.selected,
            "plan_goal": plan.goal,
            "plan_steps": plan.steps,
            "action": action_result.status,
            "expression": expression.message,
        }
        summary = build_episode_summary(payload, max_length=1000)

        stored = await self.memory_repository.write_episode(
            event_id=event.event_id,
            trace_id=event.meta.trace_id,
            source=event.source,
            user_id=event.meta.user_id,
            event_timestamp=event.timestamp,
            summary=summary,
            payload=payload,
            importance=motivation.importance,
        )
        if (
            self.semantic_vector_enabled
            and "episodic" in self.embedding_source_kinds
            and hasattr(self.memory_repository, "upsert_semantic_embedding")
        ):
            if self.embedding_refresh_mode == "manual":
                episode_embedding = None
                embedding_status = "pending_manual_refresh"
            else:
                episode_embedding, embedding_status = await materialize_embedding(
                    content=f"{payload['event']} {payload['context']} {payload['expression']}",
                    posture=self.embedding_posture,
                    dimensions=self.embedding_dimensions,
                    refresh_mode=self.embedding_refresh_mode,
                    openai_embedding_client=self.openai_embedding_client,
                )
            await self.memory_repository.upsert_semantic_embedding(
                user_id=event.meta.user_id,
                source_kind="episodic",
                source_id=str(stored["id"]),
                source_event_id=event.event_id,
                scope_type="global",
                scope_key="global",
                content=str(payload["event"]),
                embedding=episode_embedding,
                embedding_model=self.embedding_posture["model_effective"],
                embedding_dimensions=self.embedding_dimensions,
                metadata={
                    "memory_kind": memory_kind,
                    "memory_topics": memory_topics,
                    "response_language": expression.language,
                    "affect_label": perception.affective.affect_label,
                    "affect_needs_support": perception.affective.needs_support,
                    "embedding_provider_requested": self.embedding_posture["provider_requested"],
                    "embedding_provider_effective": self.embedding_posture["provider_effective"],
                    "embedding_provider_hint": self.embedding_posture["provider_hint"],
                    "embedding_model_requested": self.embedding_posture["model_requested"],
                    "embedding_model_effective": self.embedding_posture["model_effective"],
                    "embedding_refresh_mode": self.embedding_refresh_mode,
                    "embedding_status": embedding_status,
                },
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
            payload=stored.get("payload", {}),
            importance=stored["importance"],
        )

    async def _execute_provider_backed_connector_intents(self, plan: PlanOutput) -> ActionResult | None:
        if self.clickup_task_client is None or not getattr(self.clickup_task_client, "ready", False):
            return None

        executed_actions: list[str] = []
        notes: list[str] = []

        for intent in plan.domain_intents:
            if not isinstance(intent, ExternalTaskSyncDomainIntent):
                continue
            if intent.provider_hint != "clickup" or intent.operation != "create_task":
                continue

            task_name = self._connector_task_name(intent.task_hint)
            try:
                result = await self.clickup_task_client.create_task(
                    name=task_name,
                    description=f"Created by AION connector execution from intent: {intent.task_hint}",
                )
            except Exception as exc:
                return ActionResult(
                    status="fail",
                    actions=["clickup_create_task"],
                    notes=f"ClickUp task execution failed: {type(exc).__name__}: {exc}",
                )

            executed_actions.append("clickup_create_task")
            task_id = str(result.get("id", "unknown"))
            notes.append(f"ClickUp task created ({task_id}) for '{task_name}'.")

        if not executed_actions:
            return None

        return ActionResult(
            status="success",
            actions=executed_actions,
            notes=" ".join(notes),
        )

    def _merge_connector_execution_with_delivery(
        self,
        *,
        connector_execution_result: ActionResult,
        delivery_result: ActionResult,
    ) -> ActionResult:
        status = delivery_result.status
        if connector_execution_result.status == "success" and delivery_result.status == "fail":
            status = "partial"
        notes = f"{connector_execution_result.notes} {delivery_result.notes}".strip()
        return ActionResult(
            status=status,
            actions=[*connector_execution_result.actions, *delivery_result.actions],
            notes=notes,
        )

    def _connector_task_name(self, task_hint: str) -> str:
        normalized = " ".join(str(task_hint or "").split())
        if not normalized:
            return "AION follow-up"
        return normalized[:120]

    async def _apply_domain_intents(self, *, event: Event, plan: PlanOutput) -> dict[str, object]:
        preference_update = ""
        collaboration_update = ""
        goal_update = ""
        task_update = ""
        task_status_update = ""
        calendar_connector_update = ""
        task_connector_update = ""
        drive_connector_update = ""
        connector_expansion_update = ""
        relation_update = ""
        proactive_state_update = ""
        calendar_connector_guardrail = ""
        task_connector_guardrail = ""
        drive_connector_guardrail = ""
        connector_expansion_guardrail = ""
        executed_intents: list[str] = []
        active_goals_cache: list[dict] | None = None
        active_tasks_cache: list[dict] | None = None

        for intent in plan.domain_intents:
            executed_intents.append(intent.intent_type)

            if isinstance(intent, NoopDomainIntent):
                continue

            if isinstance(intent, UpdateResponseStyleDomainIntent):
                preference_update = f"response_style:{intent.style}"
                continue

            if isinstance(intent, UpdateCollaborationPreferenceDomainIntent):
                collaboration_update = intent.preference
                continue

            if isinstance(intent, UpsertGoalDomainIntent):
                stored_goal = await self.memory_repository.upsert_active_goal(
                    user_id=event.meta.user_id,
                    name=intent.name,
                    description=intent.description,
                    priority=intent.priority,
                    goal_type=intent.goal_type,
                )
                goal_update = str(stored_goal["name"])
                if active_goals_cache is None:
                    active_goals_cache = [stored_goal]
                else:
                    active_goals_cache.append(stored_goal)
                continue

            if isinstance(intent, PromoteInferredGoalDomainIntent):
                stored_goal = await self.memory_repository.upsert_active_goal(
                    user_id=event.meta.user_id,
                    name=intent.name,
                    description=intent.description,
                    priority=intent.priority,
                    goal_type=intent.goal_type,
                )
                goal_update = str(stored_goal["name"])
                if active_goals_cache is None:
                    active_goals_cache = [stored_goal]
                else:
                    active_goals_cache.append(stored_goal)
                continue

            if isinstance(intent, UpsertTaskDomainIntent):
                if active_goals_cache is None:
                    active_goals_cache = await self.memory_repository.get_active_goals(
                        user_id=event.meta.user_id,
                        limit=5,
                    )
                linked_goal_id = self._match_goal_for_task(intent.name, active_goals_cache)
                stored_task = await self.memory_repository.upsert_active_task(
                    user_id=event.meta.user_id,
                    name=intent.name,
                    description=intent.description,
                    priority=intent.priority,
                    goal_id=linked_goal_id,
                    status=intent.status,
                )
                task_update = str(stored_task["name"])
                if active_tasks_cache is None:
                    active_tasks_cache = [stored_task]
                else:
                    active_tasks_cache.append(stored_task)
                continue

            if isinstance(intent, PromoteInferredTaskDomainIntent):
                if active_goals_cache is None:
                    active_goals_cache = await self.memory_repository.get_active_goals(
                        user_id=event.meta.user_id,
                        limit=5,
                    )
                linked_goal_id = self._match_goal_for_task(intent.name, active_goals_cache)
                stored_task = await self.memory_repository.upsert_active_task(
                    user_id=event.meta.user_id,
                    name=intent.name,
                    description=intent.description,
                    priority=intent.priority,
                    goal_id=linked_goal_id,
                    status=intent.status,
                )
                task_update = str(stored_task["name"])
                if active_tasks_cache is None:
                    active_tasks_cache = [stored_task]
                else:
                    active_tasks_cache.append(stored_task)
                continue

            if isinstance(intent, UpdateTaskStatusDomainIntent):
                if active_tasks_cache is None:
                    active_tasks_cache = await self.memory_repository.get_active_tasks(
                        user_id=event.meta.user_id,
                        limit=8,
                    )
                matched_task = self._match_task_for_status(intent.task_hint, active_tasks_cache)
                if matched_task is None:
                    continue
                updated_task = await self.memory_repository.update_task_status(
                    task_id=int(matched_task["id"]),
                    status=intent.status,
                )
                if updated_task is not None:
                    task_status_update = f"{updated_task['name']}:{updated_task['status']}"
                continue

            if isinstance(intent, MaintainTaskStatusDomainIntent):
                if active_tasks_cache is None:
                    active_tasks_cache = await self.memory_repository.get_active_tasks(
                        user_id=event.meta.user_id,
                        limit=8,
                    )
                matched_task = self._match_task_for_status(intent.task_hint, active_tasks_cache)
                if matched_task is None:
                    continue
                updated_task = await self.memory_repository.update_task_status(
                    task_id=int(matched_task["id"]),
                    status=intent.status,
                )
                if updated_task is not None:
                    task_status_update = f"{updated_task['name']}:{updated_task['status']}"
                continue

            if isinstance(intent, CalendarSchedulingIntentDomainIntent):
                calendar_connector_update = (
                    f"{intent.operation}:{intent.mode}:{intent.provider_hint or 'generic'}"
                )
                calendar_connector_guardrail = connector_guardrail_snapshot(intent)
                continue

            if isinstance(intent, ExternalTaskSyncDomainIntent):
                task_connector_update = (
                    f"{intent.operation}:{intent.mode}:{intent.provider_hint}"
                )
                task_connector_guardrail = connector_guardrail_snapshot(intent)
                continue

            if isinstance(intent, ConnectedDriveAccessDomainIntent):
                drive_connector_update = (
                    f"{intent.operation}:{intent.mode}:{intent.provider_hint}"
                )
                drive_connector_guardrail = connector_guardrail_snapshot(intent)
                continue

            if isinstance(intent, ConnectorCapabilityDiscoveryDomainIntent):
                connector_expansion_update = (
                    f"{intent.connector_kind}:{intent.provider_hint}:{intent.requested_capability}"
                )
                connector_expansion_guardrail = connector_guardrail_snapshot(intent)
                continue

            if isinstance(intent, MaintainRelationDomainIntent):
                if hasattr(self.memory_repository, "upsert_relation"):
                    stored_relation = await self.memory_repository.upsert_relation(
                        user_id=event.meta.user_id,
                        relation_type=intent.relation_type,
                        relation_value=intent.relation_value,
                        confidence=float(intent.confidence),
                        source=intent.source,
                        supporting_event_id=event.event_id,
                        scope_type=intent.scope_type,
                        scope_key=intent.scope_key,
                        evidence_count=int(intent.evidence_count),
                        decay_rate=float(intent.decay_rate),
                    )
                    relation_update = (
                        f"{stored_relation['relation_type']}:"
                        f"{stored_relation['relation_value']}:"
                        f"{stored_relation['scope_type']}:"
                        f"{stored_relation['scope_key']}"
                    )
                continue

            if isinstance(intent, UpdateProactiveStateDomainIntent):
                proactive_state_update = f"{intent.state}:{intent.trigger}:{intent.reason}"
                if hasattr(self.memory_repository, "upsert_conclusion"):
                    await self.memory_repository.upsert_conclusion(
                        user_id=event.meta.user_id,
                        kind="proactive_outreach_state",
                        content=intent.state,
                        confidence=0.9,
                        source=intent.source,
                        supporting_event_id=event.event_id,
                    )
                    await self.memory_repository.upsert_conclusion(
                        user_id=event.meta.user_id,
                        kind="proactive_outreach_trigger",
                        content=intent.trigger,
                        confidence=0.9,
                        source=intent.source,
                        supporting_event_id=event.event_id,
                    )
                continue

        return {
            "preference_update": preference_update,
            "collaboration_update": collaboration_update,
            "goal_update": goal_update,
            "task_update": task_update,
            "task_status_update": task_status_update,
            "calendar_connector_update": calendar_connector_update,
            "task_connector_update": task_connector_update,
            "drive_connector_update": drive_connector_update,
            "connector_expansion_update": connector_expansion_update,
            "relation_update": relation_update,
            "proactive_state_update": proactive_state_update,
            "calendar_connector_guardrail": calendar_connector_guardrail,
            "task_connector_guardrail": task_connector_guardrail,
            "drive_connector_guardrail": drive_connector_guardrail,
            "connector_expansion_guardrail": connector_expansion_guardrail,
            "executed_intents": executed_intents,
        }

    def _connector_policy_violations(self, plan: PlanOutput) -> list[str]:
        violations: list[str] = []
        for intent in plan.domain_intents:
            if isinstance(
                intent,
                (
                    CalendarSchedulingIntentDomainIntent,
                    ExternalTaskSyncDomainIntent,
                    ConnectedDriveAccessDomainIntent,
                    ConnectorCapabilityDiscoveryDomainIntent,
                ),
            ):
                violation = connector_intent_policy_violation(intent)
                if violation is not None:
                    violations.append(violation)
        return violations

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

    def _match_task_for_status(self, task_hint: str, active_tasks: list[dict]) -> dict | None:
        hint_tokens = self._text_tokens(task_hint)
        best_task: dict | None = None
        best_score = 0
        for task in active_tasks:
            task_id = task.get("id")
            if task_id is None:
                continue
            task_tokens = self._text_tokens(str(task.get("name", "")) + " " + str(task.get("description", "")))
            overlap = len(hint_tokens.intersection(task_tokens))
            if overlap > best_score:
                best_score = overlap
                best_task = task
        return best_task if best_score > 0 else None

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
