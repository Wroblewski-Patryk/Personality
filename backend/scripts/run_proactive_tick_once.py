from __future__ import annotations

import argparse
import asyncio
import json

from app.affective.assessor import AffectiveAssessor
from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.core.action import ActionExecutor
from app.core.config import get_settings
from app.core.database import Database
from app.core.external_scheduler_policy import (
    PROACTIVE_EXTERNAL_ENTRYPOINT,
    external_scheduler_policy_snapshot,
)
from app.core.logging import setup_logging
from app.core.runtime import RuntimeOrchestrator
from app.expression.generator import ExpressionAgent
from app.integrations.openai.client import OpenAIClient
from app.integrations.task_system.clickup_client import ClickUpTaskClient
from app.integrations.telegram.client import TelegramClient
from app.memory.openai_embedding_client import OpenAIEmbeddingClient
from app.memory.repository import MemoryRepository
from app.motivation.engine import MotivationEngine
from app.reflection.worker import ReflectionWorker
from app.workers.scheduler import SchedulerWorker


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one proactive cadence tick under external scheduler ownership.")
    parser.add_argument("--allow-in-process", action="store_true")
    return parser.parse_args()


async def _run() -> int:
    args = _parse_args()
    settings = get_settings()
    settings.validate_required()
    setup_logging(settings.log_level)

    policy = external_scheduler_policy_snapshot(
        scheduler_execution_mode=settings.scheduler_execution_mode
    )
    if (
        str(policy["selected_execution_mode"]) != "externalized"
        and not bool(args.allow_in_process)
    ):
        print(json.dumps({"policy_owner": policy["policy_owner"], "status": "blocked_non_externalized_mode", "entrypoint_path": PROACTIVE_EXTERNAL_ENTRYPOINT}))
        return 2

    database = Database(settings.database_url)  # type: ignore[arg-type]
    openai_embedding_client = OpenAIEmbeddingClient(api_key=settings.openai_api_key)
    memory_repository = MemoryRepository(
        database.session_factory,
        embedding_provider=str(getattr(settings, "embedding_provider", "deterministic")),
        embedding_model=str(getattr(settings, "embedding_model", "deterministic-v1")),
        embedding_dimensions=int(getattr(settings, "embedding_dimensions", 32)),
        embedding_source_kinds=tuple(getattr(settings, "get_embedding_source_kinds", lambda: ("episodic", "semantic", "affective"))()),
        embedding_refresh_mode=str(getattr(settings, "embedding_refresh_mode", "on_write")),
        openai_api_key=settings.openai_api_key,
        openai_embedding_client=openai_embedding_client,
    )
    telegram_client = TelegramClient(settings.telegram_bot_token)
    openai_client = OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )
    action_executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        semantic_vector_enabled=bool(getattr(settings, "semantic_vector_enabled", True)),
        embedding_provider=str(getattr(settings, "embedding_provider", "deterministic")),
        embedding_model=str(getattr(settings, "embedding_model", "deterministic-v1")),
        embedding_dimensions=int(getattr(settings, "embedding_dimensions", 32)),
        embedding_source_kinds=tuple(getattr(settings, "get_embedding_source_kinds", lambda: ("episodic", "semantic", "affective"))()),
        embedding_refresh_mode=str(getattr(settings, "embedding_refresh_mode", "on_write")),
        openai_api_key=settings.openai_api_key,
        openai_embedding_client=openai_embedding_client,
        clickup_task_client=ClickUpTaskClient(
            api_token=getattr(settings, "clickup_api_token", None),
            list_id=getattr(settings, "clickup_list_id", None),
        ),
    )
    reflection_worker = ReflectionWorker(memory_repository=memory_repository)
    scheduler = SchedulerWorker(
        memory_repository=memory_repository,
        reflection_worker=reflection_worker,
        enabled=settings.scheduler_enabled,
        reflection_runtime_mode=settings.reflection_runtime_mode,
        reflection_interval_seconds=settings.reflection_interval,
        maintenance_interval_seconds=settings.maintenance_interval,
        execution_mode="externalized",
        proactive_enabled=settings.proactive_enabled,
        proactive_interval_seconds=settings.proactive_interval,
    )
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai_client),
        action_executor=action_executor,
        memory_repository=memory_repository,
        reflection_worker=None,
        affective_assessor=AffectiveAssessor(
            classifier_client=openai_client,
            enabled=settings.is_affective_assessment_enabled(),
            policy_source=("explicit" if settings.affective_assessment_enabled is not None else "environment_default"),
        ),
        semantic_vector_enabled=bool(getattr(settings, "semantic_vector_enabled", True)),
        embedding_provider=str(getattr(settings, "embedding_provider", "deterministic")),
        embedding_model=str(getattr(settings, "embedding_model", "deterministic-v1")),
        embedding_dimensions=int(getattr(settings, "embedding_dimensions", 32)),
        reflection_runtime_mode=settings.reflection_runtime_mode,
    )
    scheduler.set_runtime(runtime)
    try:
        summary = await scheduler.run_external_proactive_tick_once()
    finally:
        await telegram_client.close()
        await database.dispose()

    print(json.dumps({"policy_owner": policy["policy_owner"], "entrypoint_path": PROACTIVE_EXTERNAL_ENTRYPOINT, "summary": summary, "status": "ok"}))
    return 0


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    raise SystemExit(main())
