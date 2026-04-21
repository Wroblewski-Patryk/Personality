import asyncio
from time import perf_counter
from typing import Awaitable, Callable, TypeVar

from app.affective.assessor import AffectiveAssessor
from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.core.action import ActionExecutor
from app.core.attention_gate import evaluate_proactive_attention_gate
from app.core.background_adaptive_outputs import summarize_loaded_adaptive_state
from app.core.contracts import (
    ActionDelivery,
    Event,
    ExpressionOutput,
    RuntimeResult,
    RuntimeSystemDebugEventView,
    RuntimeSystemDebugMemoryBundle,
    RuntimeSystemDebugOutput,
    RuntimeSystemDebugPlanView,
)
from app.core.graph_adapters import GraphStageAdapters
from app.core.graph_state import GraphMemoryState, build_graph_state_seed, expression_to_action_delivery
from app.core.identity_policy import identity_policy_snapshot
from app.core.logging import RuntimeLogContext, RuntimeStageLogger, get_logger
from app.core.retrieval_policy import retrieval_depth_policy_snapshot, theta_influence_snapshot
from app.core.runtime_graph import ForegroundLangGraphRunner
from app.core.scheduler_contracts import (
    normalize_reflection_runtime_mode,
    reflection_enqueue_dispatch_decision,
)
from app.expression.generator import ExpressionAgent
from app.identity.service import IdentityService
from app.memory.embeddings import deterministic_embedding, resolve_embedding_posture
from app.memory.repository import MemoryRepository
from app.motivation.engine import MotivationEngine
from app.reflection.worker import ReflectionWorker

T = TypeVar("T")


class RuntimeOrchestrator:
    MEMORY_LOAD_LIMIT = 12

    def __init__(
        self,
        perception_agent: PerceptionAgent,
        context_agent: ContextAgent,
        motivation_engine: MotivationEngine,
        role_agent: RoleAgent,
        planning_agent: PlanningAgent,
        expression_agent: ExpressionAgent,
        action_executor: ActionExecutor,
        memory_repository: MemoryRepository,
        reflection_worker: ReflectionWorker | None = None,
        identity_service: IdentityService | None = None,
        affective_assessor: AffectiveAssessor | None = None,
        semantic_vector_enabled: bool = True,
        embedding_provider: str = "deterministic",
        embedding_model: str = "deterministic-v1",
        embedding_dimensions: int = 32,
        reflection_runtime_mode: str = "in_process",
    ):
        self.perception_agent = perception_agent
        self.context_agent = context_agent
        self.motivation_engine = motivation_engine
        self.role_agent = role_agent
        self.planning_agent = planning_agent
        self.expression_agent = expression_agent
        self.action_executor = action_executor
        self.memory_repository = memory_repository
        self.reflection_worker = reflection_worker
        self.identity_service = identity_service or IdentityService()
        self.affective_assessor = affective_assessor or AffectiveAssessor()
        self.semantic_vector_enabled = semantic_vector_enabled
        self.embedding_dimensions = max(1, int(embedding_dimensions))
        self.reflection_runtime_mode = normalize_reflection_runtime_mode(reflection_runtime_mode)
        self.embedding_posture = resolve_embedding_posture(
            provider=embedding_provider,
            model=embedding_model,
        )
        self.graph_stage_adapters = GraphStageAdapters(
            perception_agent=self.perception_agent,
            context_agent=self.context_agent,
            motivation_engine=self.motivation_engine,
            role_agent=self.role_agent,
            planning_agent=self.planning_agent,
            expression_agent=self.expression_agent,
            action_executor=self.action_executor,
            affective_assessor=self.affective_assessor,
        )
        self.foreground_graph_runner = ForegroundLangGraphRunner(adapters=self.graph_stage_adapters)
        self.logger = get_logger("aion.runtime")

    def _present_label(self, value: object | None) -> str:
        return "yes" if value else "no"

    def _build_action_delivery(self, *, event: Event, expression: ExpressionOutput) -> ActionDelivery:
        plan = None
        return expression_to_action_delivery(event=event, expression=expression, plan=plan)

    def _build_system_debug_output(
        self,
        *,
        event: Event,
        perception,
        memory: list[dict],
        user_conclusions: list[dict],
        affective_conclusions: list[dict],
        relations: list[dict],
        hybrid_diagnostics: dict[str, int],
        retrieval_depth_policy: dict,
        adaptive_state: dict,
        context,
        motivation,
        role,
        plan,
        expression,
        action_result,
    ) -> RuntimeSystemDebugOutput:
        semantic_conclusions = [item for item in user_conclusions if item not in affective_conclusions]
        return RuntimeSystemDebugOutput(
            event=RuntimeSystemDebugEventView(
                event_id=event.event_id,
                trace_id=event.meta.trace_id,
                source=event.source,
                subsource=event.subsource,
                timestamp=event.timestamp,
                user_id=event.meta.user_id,
                payload=dict(event.payload),
            ),
            perception=perception,
            memory_bundle=RuntimeSystemDebugMemoryBundle(
                episodic=[dict(item) for item in memory],
                semantic=[dict(item) for item in semantic_conclusions],
                affective=[dict(item) for item in affective_conclusions],
                relations=[dict(item) for item in relations],
                diagnostics=dict(hybrid_diagnostics),
            ),
            context=context,
            motivation=motivation,
            role=role,
            plan=RuntimeSystemDebugPlanView(
                goal=plan.goal,
                steps=list(plan.steps),
                needs_action=plan.needs_action,
                needs_response=plan.needs_response,
                domain_intents=[intent.model_dump(mode="json") for intent in plan.domain_intents],
                inferred_promotion_diagnostics=list(plan.inferred_promotion_diagnostics),
            ),
            expression=expression,
            action_result=action_result,
            adaptive_state={
                **dict(adaptive_state),
                "retrieval_depth_policy": dict(retrieval_depth_policy),
                "affective_assessment_policy": dict(self.affective_assessor.snapshot()),
            },
        )

    def _run_stage(
        self,
        *,
        stage_logger: RuntimeStageLogger,
        stage_timings_ms: dict[str, int],
        stage: str,
        input_summary: str,
        operation: Callable[[], T],
        output_summary: Callable[[T], str],
    ) -> T:
        stage_logger.start(stage, summary=input_summary)
        started = perf_counter()
        try:
            result = operation()
        except Exception as exc:
            duration_ms = int((perf_counter() - started) * 1000)
            stage_timings_ms[stage] = duration_ms
            stage_logger.failure(stage, duration_ms=duration_ms, error=exc, summary=input_summary)
            raise

        duration_ms = int((perf_counter() - started) * 1000)
        stage_timings_ms[stage] = duration_ms
        stage_logger.success(stage, duration_ms=duration_ms, summary=output_summary(result))
        return result

    async def _run_async_stage(
        self,
        *,
        stage_logger: RuntimeStageLogger,
        stage_timings_ms: dict[str, int],
        stage: str,
        input_summary: str,
        operation: Callable[[], Awaitable[T]],
        output_summary: Callable[[T], str],
    ) -> T:
        stage_logger.start(stage, summary=input_summary)
        started = perf_counter()
        try:
            result = await operation()
        except Exception as exc:
            duration_ms = int((perf_counter() - started) * 1000)
            stage_timings_ms[stage] = duration_ms
            stage_logger.failure(stage, duration_ms=duration_ms, error=exc, summary=input_summary)
            raise

        duration_ms = int((perf_counter() - started) * 1000)
        stage_timings_ms[stage] = duration_ms
        stage_logger.success(stage, duration_ms=duration_ms, summary=output_summary(result))
        return result

    def _goal_priority_rank(self, priority: str) -> int:
        return {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }.get(priority, 0)

    def _primary_goal_id(self, active_goals: list[dict]) -> int | None:
        if not active_goals:
            return None
        ranked = sorted(
            active_goals,
            key=lambda goal: (
                self._goal_priority_rank(str(goal.get("priority", ""))),
                int(goal.get("id", 0) or 0),
            ),
            reverse=True,
        )
        top = ranked[0]
        if top.get("id") is None:
            return None
        return int(top["id"])

    def _enrich_goal_milestones(
        self,
        *,
        active_goal_milestones: list[dict],
        user_preferences: dict,
        active_goals: list[dict],
    ) -> list[dict]:
        if not active_goal_milestones:
            return []

        primary_goal_id = self._primary_goal_id(active_goals)
        arc = str(user_preferences.get("goal_milestone_arc", "")).strip().lower() or None
        pressure_level = str(user_preferences.get("goal_milestone_pressure", "")).strip().lower() or None
        dependency_state = str(user_preferences.get("goal_milestone_dependency_state", "")).strip().lower() or None
        due_state = str(user_preferences.get("goal_milestone_due_state", "")).strip().lower() or None
        due_window = str(user_preferences.get("goal_milestone_due_window", "")).strip().lower() or None
        risk_level = str(user_preferences.get("goal_milestone_risk", "")).strip().lower() or None
        completion_criteria = str(user_preferences.get("goal_completion_criteria", "")).strip().lower() or None

        enriched: list[dict] = []
        for milestone in active_goal_milestones:
            item = dict(milestone)
            if primary_goal_id is not None and int(item.get("goal_id", -1)) == primary_goal_id:
                item["arc"] = arc
                item["pressure_level"] = pressure_level
                item["dependency_state"] = dependency_state
                item["due_state"] = due_state
                item["due_window"] = due_window
                item["risk_level"] = risk_level
                item["completion_criteria"] = completion_criteria
            else:
                item.setdefault("arc", None)
                item.setdefault("pressure_level", None)
                item.setdefault("dependency_state", None)
                item.setdefault("due_state", None)
                item.setdefault("due_window", None)
                item.setdefault("risk_level", None)
                item.setdefault("completion_criteria", None)
            enriched.append(item)
        return enriched

    def _relation_preferences(self, relations: list[dict]) -> dict:
        preferences: dict[str, object] = {}
        for relation in relations:
            relation_type = str(relation.get("relation_type", "")).strip().lower()
            relation_value = relation.get("relation_value")
            confidence = float(relation.get("confidence", 0.0) or 0.0)
            if not relation_type:
                continue
            if relation_type == "collaboration_dynamic":
                preferences.setdefault("collaboration_preference", relation_value)
                preferences.setdefault("collaboration_preference_confidence", confidence)
                continue
            if relation_type == "support_intensity_preference":
                preferences.setdefault("relation_support_intensity", relation_value)
                preferences.setdefault("relation_support_intensity_confidence", confidence)
                continue
            if relation_type == "delivery_reliability":
                preferences.setdefault("relation_delivery_reliability", relation_value)
                preferences.setdefault("relation_delivery_reliability_confidence", confidence)
                continue
            preferences.setdefault(f"relation_{relation_type}", relation_value)
            preferences.setdefault(f"relation_{relation_type}_confidence", confidence)
        return preferences

    def _identity_conclusion_preferences(self, user_preferences: dict) -> dict:
        identity_preferences: dict[str, str] = {}
        response_style = str(user_preferences.get("response_style", "")).strip().lower()
        collaboration_preference = str(user_preferences.get("collaboration_preference", "")).strip().lower()
        if response_style:
            identity_preferences["response_style"] = response_style
        if collaboration_preference:
            identity_preferences["collaboration_preference"] = collaboration_preference
        return identity_preferences

    def _build_foreground_graph_state_seed(
        self,
        *,
        event: Event,
        memory: list[dict],
        user_profile: dict | None,
        user_preferences: dict,
        user_theta: dict | None,
        user_conclusions: list[dict],
        affective_conclusions: list[dict],
        relations: list[dict],
        identity,
        active_goals: list[dict],
        active_tasks: list[dict],
        active_goal_milestones: list[dict],
        goal_milestone_history: list[dict],
        goal_progress_history: list[dict],
        pending_subconscious_proposals: list[dict],
        hybrid_diagnostics: dict[str, int],
        stage_timings_ms: dict[str, int],
    ):
        retrieval_depth_policy = retrieval_depth_policy_snapshot(
            episodic_limit=self.MEMORY_LOAD_LIMIT,
            conclusion_limit=8,
            semantic_vector_enabled=self.semantic_vector_enabled,
            hybrid_diagnostics=hybrid_diagnostics,
        )
        background_adaptive_outputs = summarize_loaded_adaptive_state(
            user_conclusions=user_conclusions,
            relations=relations,
            theta=user_theta if isinstance(user_theta, dict) else None,
        )
        return build_graph_state_seed(event).model_copy(
            update={
                "memory": GraphMemoryState(
                    episodic=list(memory),
                    semantic=list(user_conclusions),
                    affective=list(affective_conclusions),
                    operational={
                        "user_profile": user_profile,
                        "user_preferences": user_preferences,
                        "user_theta": user_theta,
                        "hybrid_retrieval_diagnostics": hybrid_diagnostics,
                        "retrieval_depth_policy": retrieval_depth_policy,
                    },
                ),
                "conclusions": list(user_conclusions),
                "relations": list(relations),
                "background_adaptive_outputs": background_adaptive_outputs,
                "user_preferences": dict(user_preferences),
                "theta": user_theta,
                "identity": identity,
                "active_goals": list(active_goals),
                "active_tasks": list(active_tasks),
                "active_goal_milestones": list(active_goal_milestones),
                "goal_milestone_history": list(goal_milestone_history),
                "goal_progress_history": list(goal_progress_history),
                "subconscious_proposals": list(pending_subconscious_proposals),
                "stage_timings_ms": stage_timings_ms,
            }
        )

    async def _run_foreground_stage_graph(
        self,
        *,
        graph_state_seed,
        stage_logger: RuntimeStageLogger,
        stage_timings_ms: dict[str, int],
        text: str,
        user_profile: dict | None,
    ):
        graph_state = await self.foreground_graph_runner.run(
            graph_state=graph_state_seed,
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            text=text,
            user_profile=user_profile,
        )
        missing = [
            name
            for name in ("perception", "context", "motivation", "role", "plan", "expression", "action_result")
            if getattr(graph_state, name) is None
        ]
        if missing:  # pragma: no cover - defensive path
            raise ValueError(f"langgraph foreground run did not produce required output: {', '.join(missing)}")
        return graph_state

    async def _run_post_graph_followups(
        self,
        *,
        event: Event,
        stage_logger: RuntimeStageLogger,
        stage_timings_ms: dict[str, int],
        perception,
        context,
        motivation,
        role,
        plan,
        expression,
        action_result,
        user_preferences: dict,
        active_goals: list[dict],
        active_tasks: list[dict],
        active_goal_milestones: list[dict],
        goal_milestone_history: list[dict],
    ):
        memory_record = None
        reflection_triggered = False
        result_active_goals = active_goals
        result_active_tasks = active_tasks
        result_active_goal_milestones = active_goal_milestones
        result_goal_milestone_history = goal_milestone_history

        stage_timings_ms["memory_persist"] = 0
        stage_timings_ms["reflection_enqueue"] = 0
        stage_timings_ms["state_refresh"] = 0

        try:
            if plan.proposal_handoffs and hasattr(self.memory_repository, "resolve_subconscious_proposal"):

                async def resolve_subconscious_proposals() -> int:
                    resolved = 0
                    for handoff in plan.proposal_handoffs:
                        await self.memory_repository.resolve_subconscious_proposal(
                            proposal_id=int(handoff.proposal_id),
                            decision=handoff.decision,
                            reason=handoff.reason,
                        )
                        resolved += 1
                    return resolved

                await self._run_async_stage(
                    stage_logger=stage_logger,
                    stage_timings_ms=stage_timings_ms,
                    stage="proposal_handoff",
                    input_summary=f"handoffs={len(plan.proposal_handoffs)}",
                    operation=resolve_subconscious_proposals,
                    output_summary=lambda result: f"resolved={result}",
                )

            memory_record = await self._run_async_stage(
                stage_logger=stage_logger,
                stage_timings_ms=stage_timings_ms,
                stage="memory_persist",
                input_summary=(
                    f"mode={motivation.mode} role={role.selected} action_status={action_result.status}"
                ),
                operation=lambda: self.action_executor.persist_episode(
                    event=event,
                    perception=perception,
                    context=context,
                    motivation=motivation,
                    role=role,
                    plan=plan,
                    action_result=action_result,
                    expression=expression,
                ),
                output_summary=lambda result: f"memory_id={result.id or 'none'} importance={result.importance}",
            )

            reflection_enqueue_dispatch = False
            reflection_enqueue_reason = "boundary_not_evaluated"

            async def enqueue_reflection_task() -> bool:
                nonlocal reflection_enqueue_dispatch
                nonlocal reflection_enqueue_reason
                worker_running = bool(self.reflection_worker is not None and self.reflection_worker.is_running())
                reflection_enqueue_dispatch, reflection_enqueue_reason = reflection_enqueue_dispatch_decision(
                    runtime_mode=self.reflection_runtime_mode,
                    worker_running=worker_running,
                )
                if self.reflection_worker is not None:
                    return await self.reflection_worker.enqueue(
                        user_id=event.meta.user_id,
                        event_id=event.event_id,
                        dispatch=reflection_enqueue_dispatch,
                    )
                await self.memory_repository.enqueue_reflection_task(
                    user_id=event.meta.user_id,
                    event_id=event.event_id,
                )
                return True

            reflection_triggered = await self._run_async_stage(
                stage_logger=stage_logger,
                stage_timings_ms=stage_timings_ms,
                stage="reflection_enqueue",
                input_summary=(
                    f"mode={self.reflection_runtime_mode} "
                    f"worker={self._present_label(self.reflection_worker)}"
                ),
                operation=enqueue_reflection_task,
                output_summary=lambda result: (
                    f"triggered={result} "
                    f"dispatch={self._present_label(reflection_enqueue_dispatch)} "
                    f"reason={reflection_enqueue_reason}"
                ),
            )

            async def refresh_runtime_state():
                refreshed_goals = await self.memory_repository.get_active_goals(user_id=event.meta.user_id, limit=5)
                refreshed_goal_ids = [int(goal["id"]) for goal in refreshed_goals if goal.get("id") is not None]
                refreshed_tasks = await self.memory_repository.get_active_tasks(
                    user_id=event.meta.user_id,
                    goal_ids=refreshed_goal_ids,
                    limit=5,
                )
                refreshed_milestones = await self.memory_repository.get_active_goal_milestones(
                    user_id=event.meta.user_id,
                    goal_ids=refreshed_goal_ids,
                    limit=5,
                )
                refreshed_milestone_history = await self.memory_repository.get_recent_goal_milestone_history(
                    user_id=event.meta.user_id,
                    goal_ids=refreshed_goal_ids,
                    limit=6,
                )
                return (
                    refreshed_goals,
                    refreshed_tasks,
                    refreshed_milestones,
                    refreshed_milestone_history,
                )

            refreshed_goals, refreshed_tasks, refreshed_milestones, refreshed_milestone_history = await self._run_async_stage(
                stage_logger=stage_logger,
                stage_timings_ms=stage_timings_ms,
                stage="state_refresh",
                input_summary=f"user_id={event.meta.user_id}",
                operation=refresh_runtime_state,
                output_summary=lambda result: (
                    f"goals={len(result[0])} tasks={len(result[1])} milestones={len(result[2])} "
                    f"history={len(result[3])}"
                ),
            )
            result_active_goals = refreshed_goals
            result_active_tasks = refreshed_tasks
            result_active_goal_milestones = self._enrich_goal_milestones(
                active_goal_milestones=refreshed_milestones,
                user_preferences=user_preferences,
                active_goals=refreshed_goals,
            )
            result_goal_milestone_history = refreshed_milestone_history
        except Exception as exc:  # pragma: no cover - defensive path
            self.logger.warning(
                "memory follow-up degraded event_id=%s trace_id=%s error_type=%s",
                event.event_id,
                event.meta.trace_id,
                type(exc).__name__,
            )

        return (
            memory_record,
            reflection_triggered,
            result_active_goals,
            result_active_tasks,
            result_active_goal_milestones,
            result_goal_milestone_history,
        )

    async def run(self, event: Event) -> RuntimeResult:
        started = perf_counter()
        stage_timings_ms: dict[str, int] = {}
        log_context = RuntimeLogContext(
            event_id=event.event_id,
            trace_id=event.meta.trace_id,
            source=event.source,
        )
        stage_logger = RuntimeStageLogger(self.logger, log_context)
        self.logger.info("start event_id=%s trace_id=%s source=%s", event.event_id, event.meta.trace_id, event.source)

        async def load_memory_bundle():
            user_profile, user_theta, active_goals = await asyncio.gather(
                self.memory_repository.get_user_profile(user_id=event.meta.user_id),
                self.memory_repository.get_user_theta(user_id=event.meta.user_id),
                self.memory_repository.get_active_goals(user_id=event.meta.user_id, limit=5),
            )
            primary_goal_id = self._primary_goal_id(active_goals)
            preference_kwargs: dict[str, str | bool] = {}
            conclusion_kwargs: dict[str, str | bool | int] = {"limit": 3}
            if primary_goal_id is not None:
                scope_key = str(primary_goal_id)
                preference_kwargs = {
                    "scope_type": "goal",
                    "scope_key": scope_key,
                    "include_global": True,
                }
                conclusion_kwargs = {
                    "limit": 3,
                    "scope_type": "goal",
                    "scope_key": scope_key,
                    "include_global": True,
                }
            conclusion_preferences, fallback_conclusions = await asyncio.gather(
                self.memory_repository.get_user_runtime_preferences(
                    user_id=event.meta.user_id,
                    **preference_kwargs,
                ),
                self.memory_repository.get_user_conclusions(
                    user_id=event.meta.user_id,
                    **conclusion_kwargs,
                ),
            )
            relations: list[dict] = []
            if hasattr(self.memory_repository, "get_user_relations"):
                relations = await self.memory_repository.get_user_relations(
                    user_id=event.meta.user_id,
                    scope_type=conclusion_kwargs.get("scope_type"),
                    scope_key=conclusion_kwargs.get("scope_key"),
                    include_global=bool(conclusion_kwargs.get("include_global", False)),
                    limit=6,
                )
            runtime_user_preferences = dict(conclusion_preferences)
            for key, value in self._relation_preferences(relations).items():
                runtime_user_preferences.setdefault(key, value)
            identity_preferences = self._identity_conclusion_preferences(conclusion_preferences)
            memory: list[dict]
            user_conclusions: list[dict]
            affective_conclusions: list[dict] = []
            hybrid_diagnostics: dict[str, int] = {}
            pending_subconscious_proposals: list[dict] = []
            query_text = str(event.payload.get("text", "")).strip()
            if hasattr(self.memory_repository, "get_hybrid_memory_bundle"):
                query_embedding = (
                    deterministic_embedding(query_text, dimensions=self.embedding_dimensions)
                    if self.semantic_vector_enabled and query_text
                    else []
                )
                hybrid_bundle = await self.memory_repository.get_hybrid_memory_bundle(
                    user_id=event.meta.user_id,
                    query_text=query_text,
                    query_embedding=query_embedding,
                    scope_type=conclusion_kwargs.get("scope_type"),
                    scope_key=conclusion_kwargs.get("scope_key"),
                    include_global=bool(conclusion_kwargs.get("include_global", False)),
                    episodic_limit=self.MEMORY_LOAD_LIMIT,
                    conclusion_limit=8,
                )
                memory = list(hybrid_bundle.get("episodic", []))
                semantic_conclusions = list(hybrid_bundle.get("semantic", []))
                affective_conclusions = list(hybrid_bundle.get("affective", []))
                user_conclusions = [*semantic_conclusions, *affective_conclusions]
                diagnostics = hybrid_bundle.get("diagnostics", {})
                if isinstance(diagnostics, dict):
                    hybrid_diagnostics = {str(key): int(value) for key, value in diagnostics.items() if isinstance(value, int)}
            else:
                memory = await self.memory_repository.get_recent_for_user(
                    user_id=event.meta.user_id,
                    limit=self.MEMORY_LOAD_LIMIT,
                )
                user_conclusions = fallback_conclusions
            if hasattr(self.memory_repository, "get_pending_subconscious_proposals"):
                pending_subconscious_proposals = await self.memory_repository.get_pending_subconscious_proposals(
                    user_id=event.meta.user_id,
                    limit=8,
                )
            return (
                memory,
                user_profile,
                runtime_user_preferences,
                identity_preferences,
                user_conclusions,
                affective_conclusions,
                relations,
                user_theta,
                active_goals,
                hybrid_diagnostics,
                pending_subconscious_proposals,
            )

        memory, user_profile, user_preferences, identity_preferences, user_conclusions, affective_conclusions, relations, user_theta, active_goals, hybrid_diagnostics, pending_subconscious_proposals = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="memory_load",
            input_summary=f"user_id={event.meta.user_id}",
            operation=load_memory_bundle,
            output_summary=lambda result: (
                "memory="
                f"{len(result[0])} profile={self._present_label(result[1])} runtime_preferences={len(result[2])} "
                f"identity_preferences={len(result[3])} conclusions={len(result[4])} affective={len(result[5])} "
                f"relations={len(result[6])} theta={self._present_label(result[7])} goals={len(result[8])} "
                f"hybrid_vector_hits={result[9].get('vector_hits', 0)} "
                f"hybrid_lexical_hits={result[9].get('episodic_lexical_hits', 0)} "
                f"pending_proposals={len(result[10])}"
            ),
        )
        attention_gate = evaluate_proactive_attention_gate(
            event,
            relations=relations,
            theta=user_theta if isinstance(user_theta, dict) else None,
        )
        if attention_gate is not None:
            event = event.model_copy(
                update={
                    "payload": {
                        **event.payload,
                        "attention_gate": attention_gate,
                    }
                }
            )

        goal_ids = [int(goal["id"]) for goal in active_goals if goal.get("id") is not None]
        active_tasks = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="task_load",
            input_summary=f"goal_ids={len(goal_ids)}",
            operation=lambda: self.memory_repository.get_active_tasks(
                user_id=event.meta.user_id,
                goal_ids=goal_ids,
                limit=5,
            ),
            output_summary=lambda result: f"tasks={len(result)}",
        )

        raw_goal_milestones = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="goal_milestone_load",
            input_summary=f"goal_ids={len(goal_ids)}",
            operation=lambda: self.memory_repository.get_active_goal_milestones(
                user_id=event.meta.user_id,
                goal_ids=goal_ids,
                limit=5,
            ),
            output_summary=lambda result: f"milestones={len(result)}",
        )
        active_goal_milestones = self._enrich_goal_milestones(
            active_goal_milestones=raw_goal_milestones,
            user_preferences=user_preferences,
            active_goals=active_goals,
        )

        goal_milestone_history = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="goal_milestone_history_load",
            input_summary=f"goal_ids={len(goal_ids)}",
            operation=lambda: self.memory_repository.get_recent_goal_milestone_history(
                user_id=event.meta.user_id,
                goal_ids=goal_ids,
                limit=6,
            ),
            output_summary=lambda result: f"history={len(result)}",
        )

        goal_progress_history = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="goal_progress_load",
            input_summary=f"goal_ids={len(goal_ids)}",
            operation=lambda: self.memory_repository.get_recent_goal_progress(
                user_id=event.meta.user_id,
                goal_ids=goal_ids,
                limit=6,
            ),
            output_summary=lambda result: f"history={len(result)}",
        )

        identity = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="identity_load",
            input_summary=(
                f"profile_owner={self._present_label(user_profile)} "
                f"conclusion_owner={len(identity_preferences)} "
                f"theta={self._present_label(user_theta)}"
            ),
            operation=lambda: self.identity_service.build(
                user_profile=user_profile,
                user_preferences=identity_preferences,
                user_theta=user_theta,
            ),
            output_summary=lambda result: (
                f"preferred_language={result.preferred_language or 'none'} "
                f"response_style={result.response_style or 'none'} "
                f"collaboration={result.collaboration_preference or 'none'}"
            ),
        )

        text = str(event.payload.get("text", "")).strip()
        graph_state_seed = self._build_foreground_graph_state_seed(
            event=event,
            memory=memory,
            user_profile=user_profile,
            user_preferences=user_preferences,
            user_theta=user_theta,
            user_conclusions=user_conclusions,
            affective_conclusions=affective_conclusions,
            relations=relations,
            identity=identity,
            active_goals=active_goals,
            active_tasks=active_tasks,
            active_goal_milestones=active_goal_milestones,
            goal_milestone_history=goal_milestone_history,
            goal_progress_history=goal_progress_history,
            pending_subconscious_proposals=pending_subconscious_proposals,
            hybrid_diagnostics=hybrid_diagnostics,
            stage_timings_ms=stage_timings_ms,
        )
        graph_state = await self._run_foreground_stage_graph(
            graph_state_seed=graph_state_seed,
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            text=text,
            user_profile=user_profile,
        )

        perception = graph_state.perception
        assert perception is not None
        affective = graph_state.affective or perception.affective
        context = graph_state.context
        assert context is not None
        motivation = graph_state.motivation
        assert motivation is not None
        role = graph_state.role
        assert role is not None
        plan = graph_state.plan
        assert plan is not None
        expression = graph_state.expression
        assert expression is not None
        action_result = graph_state.action_result
        assert action_result is not None
        retrieval_depth_policy = retrieval_depth_policy_snapshot(
            episodic_limit=self.MEMORY_LOAD_LIMIT,
            conclusion_limit=8,
            semantic_vector_enabled=self.semantic_vector_enabled,
            hybrid_diagnostics=hybrid_diagnostics,
        )
        adaptive_state = {
            "identity_policy": identity_policy_snapshot(),
            "background_adaptive_outputs": summarize_loaded_adaptive_state(
                user_conclusions=user_conclusions,
                relations=relations,
                theta=user_theta if isinstance(user_theta, dict) else None,
            ),
            "theta_influence": theta_influence_snapshot(
                theta=user_theta if isinstance(user_theta, dict) else None,
                role_selected=role.selected,
                motivation_mode=motivation.mode,
                plan_steps=list(plan.steps),
                expression_tone=expression.tone,
            ),
            "selected_skills": [skill.model_dump(mode="json") for skill in role.selected_skills],
            "planned_skills": [skill.model_dump(mode="json") for skill in plan.selected_skills],
        }
        system_debug = self._build_system_debug_output(
            event=event,
            perception=perception,
            memory=memory,
            user_conclusions=user_conclusions,
            affective_conclusions=affective_conclusions,
            relations=relations,
            hybrid_diagnostics=hybrid_diagnostics,
            retrieval_depth_policy=retrieval_depth_policy,
            adaptive_state=adaptive_state,
            context=context,
            motivation=motivation,
            role=role,
            plan=plan,
            expression=expression,
            action_result=action_result,
        )

        (
            memory_record,
            reflection_triggered,
            result_active_goals,
            result_active_tasks,
            result_active_goal_milestones,
            result_goal_milestone_history,
        ) = await self._run_post_graph_followups(
            event=event,
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            perception=perception,
            context=context,
            motivation=motivation,
            role=role,
            plan=plan,
            expression=expression,
            action_result=action_result,
            user_preferences=user_preferences,
            active_goals=active_goals,
            active_tasks=active_tasks,
            active_goal_milestones=active_goal_milestones,
            goal_milestone_history=goal_milestone_history,
        )

        duration_ms = int((perf_counter() - started) * 1000)
        stage_timings_ms["total"] = duration_ms
        self.logger.info(
            "end event_id=%s trace_id=%s status=%s duration_ms=%s stage_timings_ms=%s",
            event.event_id,
            event.meta.trace_id,
            action_result.status,
            duration_ms,
            stage_timings_ms,
        )

        return RuntimeResult(
            event=event,
            identity=identity,
            active_goals=result_active_goals,
            active_tasks=result_active_tasks,
            active_goal_milestones=result_active_goal_milestones,
            goal_milestone_history=result_goal_milestone_history,
            goal_progress_history=goal_progress_history,
            perception=perception,
            affective=affective,
            context=context,
            motivation=motivation,
            role=role,
            plan=plan,
            action_result=action_result,
            expression=expression,
            memory_record=memory_record,
            reflection_triggered=reflection_triggered,
            system_debug=system_debug,
            stage_timings_ms=stage_timings_ms,
            duration_ms=duration_ms,
        )
