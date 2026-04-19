import asyncio
from time import perf_counter
from typing import Awaitable, Callable, TypeVar

from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.core.action import ActionExecutor
from app.core.contracts import ActionDelivery, Event, ExpressionOutput, RuntimeResult
from app.core.logging import RuntimeLogContext, RuntimeStageLogger, get_logger
from app.expression.generator import ExpressionAgent
from app.identity.service import IdentityService
from app.memory.repository import MemoryRepository
from app.motivation.engine import MotivationEngine
from app.reflection.worker import ReflectionWorker

T = TypeVar("T")


class RuntimeOrchestrator:
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
        self.logger = get_logger("aion.runtime")

    def _present_label(self, value: object | None) -> str:
        return "yes" if value else "no"

    def _build_action_delivery(self, *, event: Event, expression: ExpressionOutput) -> ActionDelivery:
        channel = expression.channel if expression.channel in {"api", "telegram"} else "api"
        raw_chat_id = event.payload.get("chat_id") if channel == "telegram" else None
        chat_id = raw_chat_id if isinstance(raw_chat_id, (int, str)) else None
        return ActionDelivery(
            message=expression.message,
            tone=expression.tone,
            channel=channel,
            language=expression.language,
            chat_id=chat_id,
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
            return await asyncio.gather(
                self.memory_repository.get_recent_for_user(user_id=event.meta.user_id, limit=5),
                self.memory_repository.get_user_profile(user_id=event.meta.user_id),
                self.memory_repository.get_user_runtime_preferences(user_id=event.meta.user_id),
                self.memory_repository.get_user_conclusions(user_id=event.meta.user_id, limit=3),
                self.memory_repository.get_user_theta(user_id=event.meta.user_id),
                self.memory_repository.get_active_goals(user_id=event.meta.user_id, limit=5),
            )

        memory, user_profile, user_preferences, user_conclusions, user_theta, active_goals = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="memory_load",
            input_summary=f"user_id={event.meta.user_id}",
            operation=load_memory_bundle,
            output_summary=lambda result: (
                "memory="
                f"{len(result[0])} profile={self._present_label(result[1])} preferences={len(result[2])} "
                f"conclusions={len(result[3])} theta={self._present_label(result[4])} goals={len(result[5])}"
            ),
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
                f"profile={self._present_label(user_profile)} preferences={len(user_preferences)} "
                f"theta={self._present_label(user_theta)}"
            ),
            operation=lambda: self.identity_service.build(
                user_profile=user_profile,
                user_preferences=user_preferences,
                user_theta=user_theta,
            ),
            output_summary=lambda result: (
                f"preferred_language={result.preferred_language or 'none'} "
                f"response_style={result.response_style or 'none'} "
                f"collaboration={result.collaboration_preference or 'none'}"
            ),
        )

        text = str(event.payload.get("text", "")).strip()
        perception = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="perception",
            input_summary=(
                f"text_len={len(text)} recent_memory={len(memory)} profile={self._present_label(user_profile)}"
            ),
            operation=lambda: self.perception_agent.run(event, recent_memory=memory, user_profile=user_profile),
            output_summary=lambda result: (
                f"topic={result.topic} intent={result.intent} language={result.language} "
                f"affect={result.affective.affect_label} ambiguity={result.ambiguity}"
            ),
        )
        affective = perception.affective

        context = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="context",
            input_summary=(
                f"memory={len(memory)} conclusions={len(user_conclusions)} goals={len(active_goals)} "
                f"tasks={len(active_tasks)} milestones={len(active_goal_milestones)}"
            ),
            operation=lambda: self.context_agent.run(
                event=event,
                perception=perception,
                recent_memory=memory,
                conclusions=user_conclusions,
                identity=identity,
                active_goals=active_goals,
                active_tasks=active_tasks,
                active_goal_milestones=active_goal_milestones,
                goal_milestone_history=goal_milestone_history,
                goal_progress_history=goal_progress_history,
            ),
            output_summary=lambda result: (
                f"related_goals={len(result.related_goals)} tags={len(result.related_tags)} "
                f"risk={result.risk_level}"
            ),
        )

        motivation = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="motivation",
            input_summary=(
                f"intent={perception.intent} risk={context.risk_level} preferences={len(user_preferences)}"
            ),
            operation=lambda: self.motivation_engine.run(
                event=event,
                context=context,
                perception=perception,
                user_preferences=user_preferences,
                theta=user_theta,
                active_goals=active_goals,
                active_tasks=active_tasks,
                goal_milestone_history=goal_milestone_history,
                goal_progress_history=goal_progress_history,
            ),
            output_summary=lambda result: (
                f"mode={result.mode} importance={result.importance} urgency={result.urgency} "
                f"valence={result.valence}"
            ),
        )

        role = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="role",
            input_summary=(
                f"topic={perception.topic} intent={perception.intent} preferences={len(user_preferences)}"
            ),
            operation=lambda: self.role_agent.run(
                event=event,
                perception=perception,
                context=context,
                user_preferences=user_preferences,
                theta=user_theta,
            ),
            output_summary=lambda result: f"selected={result.selected} confidence={result.confidence}",
        )

        plan = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="planning",
            input_summary=(
                f"mode={motivation.mode} role={role.selected} goals={len(active_goals)} "
                f"tasks={len(active_tasks)}"
            ),
            operation=lambda: self.planning_agent.run(
                event=event,
                context=context,
                motivation=motivation,
                role=role,
                user_preferences=user_preferences,
                theta=user_theta,
                active_goals=active_goals,
                active_tasks=active_tasks,
                active_goal_milestones=active_goal_milestones,
                goal_milestone_history=goal_milestone_history,
                goal_progress_history=goal_progress_history,
            ),
            output_summary=lambda result: (
                f"steps={len(result.steps)} needs_action={result.needs_action} "
                f"needs_response={result.needs_response}"
            ),
        )

        expression = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="expression",
            input_summary=(
                f"language={perception.language} mode={motivation.mode} role={role.selected} "
                f"needs_response={plan.needs_response}"
            ),
            operation=lambda: self.expression_agent.run(
                event=event,
                perception=perception,
                context=context,
                plan=plan,
                role=role,
                motivation=motivation,
                identity=identity,
                user_preferences=user_preferences,
                theta=user_theta,
            ),
            output_summary=lambda result: (
                f"tone={result.tone} language={result.language} channel={result.channel} "
                f"message_len={len(result.message)}"
            ),
        )
        action_delivery = self._build_action_delivery(event=event, expression=expression)

        action_result = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="action",
            input_summary=(
                f"needs_action={plan.needs_action} channel={action_delivery.channel} "
                f"has_chat_id={self._present_label(action_delivery.chat_id)}"
            ),
            operation=lambda: self.action_executor.execute(plan=plan, delivery=action_delivery),
            output_summary=lambda result: f"status={result.status} actions={len(result.actions)}",
        )

        memory_record = None
        reflection_triggered = False
        stage_timings_ms["memory_persist"] = 0
        stage_timings_ms["reflection_enqueue"] = 0
        stage_timings_ms["state_refresh"] = 0
        result_active_goals = active_goals
        result_active_tasks = active_tasks
        result_active_goal_milestones = active_goal_milestones
        result_goal_milestone_history = goal_milestone_history
        try:
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
            if self.reflection_worker is not None:
                reflection_triggered = await self._run_async_stage(
                    stage_logger=stage_logger,
                    stage_timings_ms=stage_timings_ms,
                    stage="reflection_enqueue",
                    input_summary=f"worker={self._present_label(self.reflection_worker)}",
                    operation=lambda: self.reflection_worker.enqueue(
                        user_id=event.meta.user_id,
                        event_id=event.event_id,
                    ),
                    output_summary=lambda result: f"triggered={result}",
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
            stage_timings_ms=stage_timings_ms,
            duration_ms=duration_ms,
        )
