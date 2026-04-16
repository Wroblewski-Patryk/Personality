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
        self.logger = get_logger("aion.runtime")

    async def run(self, event: Event) -> RuntimeResult:
        started = perf_counter()
        self.logger.info("start event_id=%s trace_id=%s", event.event_id, event.meta.trace_id)

        memory, user_profile, user_preferences, user_conclusions, user_theta = await asyncio.gather(
            self.memory_repository.get_recent_for_user(user_id=event.meta.user_id, limit=5),
            self.memory_repository.get_user_profile(user_id=event.meta.user_id),
            self.memory_repository.get_user_runtime_preferences(user_id=event.meta.user_id),
            self.memory_repository.get_user_conclusions(user_id=event.meta.user_id, limit=3),
            self.memory_repository.get_user_theta(user_id=event.meta.user_id),
        )
        perception = self.perception_agent.run(event, recent_memory=memory, user_profile=user_profile)
        context = self.context_agent.run(
            event=event,
            perception=perception,
            recent_memory=memory,
            conclusions=user_conclusions,
        )
        motivation = self.motivation_engine.run(
            event=event,
            context=context,
            perception=perception,
            user_preferences=user_preferences,
            theta=user_theta,
        )
        role = self.role_agent.run(
            event=event,
            perception=perception,
            context=context,
            user_preferences=user_preferences,
            theta=user_theta,
        )
        plan = self.planning_agent.run(
            event=event,
            context=context,
            motivation=motivation,
            role=role,
            user_preferences=user_preferences,
            theta=user_theta,
        )
        expression = await self.expression_agent.run(
            event=event,
            perception=perception,
            context=context,
            plan=plan,
            role=role,
            motivation=motivation,
            user_preferences=user_preferences,
            theta=user_theta,
        )
        action_result = await self.action_executor.execute(plan=plan, event=event, expression=expression)

        memory_record = None
        reflection_triggered = False
        try:
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
            if self.reflection_worker is not None:
                reflection_triggered = await self.reflection_worker.enqueue(
                    user_id=event.meta.user_id,
                    event_id=event.event_id,
                )
        except Exception as exc:  # pragma: no cover - defensive path
            self.logger.exception("memory_persist_failed event_id=%s error=%s", event.event_id, exc)

        duration_ms = int((perf_counter() - started) * 1000)
        self.logger.info(
            "end event_id=%s trace_id=%s status=%s duration_ms=%s",
            event.event_id,
            event.meta.trace_id,
            action_result.status,
            duration_ms,
        )

        return RuntimeResult(
            event=event,
            perception=perception,
            context=context,
            motivation=motivation,
            role=role,
            plan=plan,
            action_result=action_result,
            expression=expression,
            memory_record=memory_record,
            reflection_triggered=reflection_triggered,
            duration_ms=duration_ms,
        )
