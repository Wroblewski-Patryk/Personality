import asyncio
from time import perf_counter

from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.core.action import ActionExecutor
from app.core.contracts import Event, RuntimeResult
from app.core.logging import get_logger
from app.expression.generator import ExpressionAgent
from app.identity.service import IdentityService
from app.memory.repository import MemoryRepository
from app.motivation.engine import MotivationEngine
from app.reflection.worker import ReflectionWorker


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

    async def run(self, event: Event) -> RuntimeResult:
        started = perf_counter()
        stage_timings_ms: dict[str, int] = {}
        self.logger.info("start event_id=%s trace_id=%s", event.event_id, event.meta.trace_id)

        stage_started = perf_counter()
        memory, user_profile, user_preferences, user_conclusions, user_theta, active_goals = await asyncio.gather(
            self.memory_repository.get_recent_for_user(user_id=event.meta.user_id, limit=5),
            self.memory_repository.get_user_profile(user_id=event.meta.user_id),
            self.memory_repository.get_user_runtime_preferences(user_id=event.meta.user_id),
            self.memory_repository.get_user_conclusions(user_id=event.meta.user_id, limit=3),
            self.memory_repository.get_user_theta(user_id=event.meta.user_id),
            self.memory_repository.get_active_goals(user_id=event.meta.user_id, limit=5),
        )
        stage_timings_ms["memory_load"] = int((perf_counter() - stage_started) * 1000)

        stage_started = perf_counter()
        active_tasks = await self.memory_repository.get_active_tasks(
            user_id=event.meta.user_id,
            goal_ids=[int(goal["id"]) for goal in active_goals if goal.get("id") is not None],
            limit=5,
        )
        stage_timings_ms["task_load"] = int((perf_counter() - stage_started) * 1000)

        stage_started = perf_counter()
        goal_progress_history = await self.memory_repository.get_recent_goal_progress(
            user_id=event.meta.user_id,
            goal_ids=[int(goal["id"]) for goal in active_goals if goal.get("id") is not None],
            limit=6,
        )
        stage_timings_ms["goal_progress_load"] = int((perf_counter() - stage_started) * 1000)

        stage_started = perf_counter()
        identity = self.identity_service.build(
            user_profile=user_profile,
            user_preferences=user_preferences,
            user_theta=user_theta,
        )
        stage_timings_ms["identity_load"] = int((perf_counter() - stage_started) * 1000)

        stage_started = perf_counter()
        perception = self.perception_agent.run(event, recent_memory=memory, user_profile=user_profile)
        stage_timings_ms["perception"] = int((perf_counter() - stage_started) * 1000)

        stage_started = perf_counter()
        context = self.context_agent.run(
            event=event,
            perception=perception,
            recent_memory=memory,
            conclusions=user_conclusions,
            identity=identity,
            active_goals=active_goals,
            active_tasks=active_tasks,
            goal_progress_history=goal_progress_history,
        )
        stage_timings_ms["context"] = int((perf_counter() - stage_started) * 1000)

        stage_started = perf_counter()
        motivation = self.motivation_engine.run(
            event=event,
            context=context,
            perception=perception,
            user_preferences=user_preferences,
            theta=user_theta,
            active_goals=active_goals,
            active_tasks=active_tasks,
            goal_progress_history=goal_progress_history,
        )
        stage_timings_ms["motivation"] = int((perf_counter() - stage_started) * 1000)

        stage_started = perf_counter()
        role = self.role_agent.run(
            event=event,
            perception=perception,
            context=context,
            user_preferences=user_preferences,
            theta=user_theta,
        )
        stage_timings_ms["role"] = int((perf_counter() - stage_started) * 1000)

        stage_started = perf_counter()
        plan = self.planning_agent.run(
            event=event,
            context=context,
            motivation=motivation,
            role=role,
            user_preferences=user_preferences,
            theta=user_theta,
            active_goals=active_goals,
            active_tasks=active_tasks,
            goal_progress_history=goal_progress_history,
        )
        stage_timings_ms["planning"] = int((perf_counter() - stage_started) * 1000)

        stage_started = perf_counter()
        expression = await self.expression_agent.run(
            event=event,
            perception=perception,
            context=context,
            plan=plan,
            role=role,
            motivation=motivation,
            identity=identity,
            user_preferences=user_preferences,
            theta=user_theta,
        )
        stage_timings_ms["expression"] = int((perf_counter() - stage_started) * 1000)

        stage_started = perf_counter()
        action_result = await self.action_executor.execute(plan=plan, event=event, expression=expression)
        stage_timings_ms["action"] = int((perf_counter() - stage_started) * 1000)

        memory_record = None
        reflection_triggered = False
        stage_timings_ms["memory_persist"] = 0
        stage_timings_ms["reflection_enqueue"] = 0
        stage_timings_ms["state_refresh"] = 0
        result_active_goals = active_goals
        result_active_tasks = active_tasks
        try:
            stage_started = perf_counter()
            memory_record = await self.action_executor.persist_episode(
                event=event,
                perception=perception,
                context=context,
                motivation=motivation,
                role=role,
                plan=plan,
                action_result=action_result,
                expression=expression,
            )
            stage_timings_ms["memory_persist"] = int((perf_counter() - stage_started) * 1000)
            if self.reflection_worker is not None:
                stage_started = perf_counter()
                reflection_triggered = await self.reflection_worker.enqueue(
                    user_id=event.meta.user_id,
                    event_id=event.event_id,
                )
                stage_timings_ms["reflection_enqueue"] = int((perf_counter() - stage_started) * 1000)

            stage_started = perf_counter()
            refreshed_goals = await self.memory_repository.get_active_goals(user_id=event.meta.user_id, limit=5)
            refreshed_tasks = await self.memory_repository.get_active_tasks(
                user_id=event.meta.user_id,
                goal_ids=[int(goal["id"]) for goal in refreshed_goals if goal.get("id") is not None],
                limit=5,
            )
            result_active_goals = refreshed_goals
            result_active_tasks = refreshed_tasks
            stage_timings_ms["state_refresh"] = int((perf_counter() - stage_started) * 1000)
        except Exception as exc:  # pragma: no cover - defensive path
            if stage_timings_ms["memory_persist"] == 0:
                stage_timings_ms["memory_persist"] = int((perf_counter() - stage_started) * 1000)
            self.logger.exception("memory_persist_failed event_id=%s error=%s", event.event_id, exc)

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
            goal_progress_history=goal_progress_history,
            perception=perception,
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
