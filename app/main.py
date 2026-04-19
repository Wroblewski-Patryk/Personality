from contextlib import asynccontextmanager

from app.affective.assessor import AffectiveAssessor
from fastapi import FastAPI

from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.api.routes import router
from app.core.action import ActionExecutor
from app.core.attention import AttentionTurnCoordinator
from app.core.config import get_settings
from app.core.database import Database
from app.core.debug_compat import DebugQueryCompatTelemetry
from app.core.logging import get_logger, setup_logging
from app.core.runtime_policy import (
    app_environment,
    production_debug_token_required,
    production_policy_mismatches,
    runtime_policy_snapshot,
    strict_startup_blocked,
)
from app.core.runtime import RuntimeOrchestrator
from app.expression.generator import ExpressionAgent
from app.integrations.openai.client import OpenAIClient
from app.integrations.telegram.client import TelegramClient
from app.memory.repository import MemoryRepository
from app.motivation.engine import MotivationEngine
from app.reflection.worker import ReflectionWorker
from app.workers.scheduler import SchedulerWorker


def _log_runtime_policy_warnings(*, settings, logger) -> None:
    policy = runtime_policy_snapshot(settings)
    violations = production_policy_mismatches(settings)
    if "event_debug_enabled=true" in violations:
        logger.warning(
            "runtime_policy_warning env=%s event_debug_enabled=%s source=%s recommendation=disable_debug_payload_in_production",
            settings.app_env,
            policy["event_debug_enabled"],
            policy["event_debug_source"],
        )
        if policy["event_debug_query_compat_enabled"]:
            logger.warning(
                "runtime_policy_warning env=%s event_debug_query_compat_enabled=%s recommendation=disable_event_debug_query_compat_in_production",
                settings.app_env,
                policy["event_debug_query_compat_enabled"],
            )
        if not policy["event_debug_token_required"] and production_debug_token_required(settings):
            logger.warning(
                "runtime_policy_warning env=%s event_debug_token_required=%s recommendation=configure_event_debug_token_when_debug_enabled",
                settings.app_env,
                policy["event_debug_token_required"],
            )
        if (
            not policy["event_debug_token_required"]
            and not production_debug_token_required(settings)
            and app_environment(settings) == "production"
        ):
            logger.warning(
                "runtime_policy_warning env=%s production_debug_token_required=%s recommendation=enable_production_debug_token_requirement_or_configure_event_debug_token",
                settings.app_env,
                policy["production_debug_token_required"],
            )
    if "startup_schema_mode=create_tables" in violations:
        logger.warning(
            "runtime_policy_warning env=%s startup_schema_mode=%s recommendation=use_migration_first_startup_in_production",
            settings.app_env,
            policy["startup_schema_mode"],
        )
    if strict_startup_blocked(settings):
        violation_summary = ",".join(violations)
        logger.error(
            "runtime_policy_block env=%s enforcement=%s violations=%s",
            settings.app_env,
            policy["production_policy_enforcement"],
            violation_summary,
        )
        raise RuntimeError(
            "Production runtime policy strict-mode violation: "
            f"{violation_summary}. Resolve policy mismatch or set PRODUCTION_POLICY_ENFORCEMENT=warn."
        )
    if (
        app_environment(settings) == "production"
        and policy["production_policy_enforcement"] == "warn"
        and policy["recommended_production_policy_enforcement"] == "strict"
    ):
        logger.info(
            "runtime_policy_hint env=%s enforcement=%s recommended_enforcement=%s hint=%s",
            settings.app_env,
            policy["production_policy_enforcement"],
            policy["recommended_production_policy_enforcement"],
            policy["strict_rollout_hint"],
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.validate_required()

    setup_logging(settings.log_level)
    logger = get_logger("aion.app")
    _log_runtime_policy_warnings(settings=settings, logger=logger)

    database = Database(settings.database_url)  # type: ignore[arg-type]
    memory_repository = MemoryRepository(database.session_factory)
    if settings.startup_schema_mode == "create_tables":
        await memory_repository.create_tables(database.engine)
        logger.warning(
            "schema_bootstrap mode=%s action=create_tables note=compatibility_path",
            settings.startup_schema_mode,
        )
    else:
        logger.info(
            "schema_bootstrap mode=%s action=skip_create_tables note=expect_migrations",
            settings.startup_schema_mode,
        )

    telegram_client = TelegramClient(settings.telegram_bot_token)
    openai_client = OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )
    action_executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
    )
    reflection_worker = ReflectionWorker(memory_repository=memory_repository)
    scheduler_worker = SchedulerWorker(
        memory_repository=memory_repository,
        reflection_worker=reflection_worker,
        enabled=settings.scheduler_enabled,
        reflection_runtime_mode=settings.reflection_runtime_mode,
        reflection_interval_seconds=settings.reflection_interval,
        maintenance_interval_seconds=settings.maintenance_interval,
    )
    runtime_reflection_worker = reflection_worker
    if settings.reflection_runtime_mode == "in_process":
        await reflection_worker.start()
    else:
        runtime_reflection_worker = None
        logger.info(
            "reflection_runtime mode=%s action=defer_background_worker note=enqueue_only_for_out_of_process_execution",
            settings.reflection_runtime_mode,
        )
    if settings.scheduler_enabled:
        await scheduler_worker.start()
        logger.info(
            "scheduler_runtime enabled=%s reflection_interval=%s maintenance_interval=%s",
            settings.scheduler_enabled,
            settings.reflection_interval,
            settings.maintenance_interval,
        )
    else:
        logger.info("scheduler_runtime enabled=%s", settings.scheduler_enabled)

    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai_client),
        action_executor=action_executor,
        memory_repository=memory_repository,
        reflection_worker=runtime_reflection_worker,
        affective_assessor=AffectiveAssessor(classifier_client=openai_client),
    )
    attention_turn_coordinator = AttentionTurnCoordinator(
        burst_window_ms=settings.attention_burst_window_ms,
        answered_ttl_seconds=settings.attention_answered_ttl_seconds,
        stale_turn_seconds=settings.attention_stale_turn_seconds,
    )

    app.state.settings = settings
    app.state.database = database
    app.state.memory_repository = memory_repository
    app.state.telegram_client = telegram_client
    app.state.reflection_worker = reflection_worker
    app.state.scheduler_worker = scheduler_worker
    app.state.reflection_runtime_mode = settings.reflection_runtime_mode
    app.state.attention_turn_coordinator = attention_turn_coordinator
    app.state.debug_query_compat_telemetry = DebugQueryCompatTelemetry(
        recent_window_size=settings.event_debug_query_compat_recent_window
    )
    app.state.runtime = runtime

    logger.info(
        "AION started env=%s port=%s openai_enabled=%s telegram_enabled=%s reflection_runtime_mode=%s scheduler_enabled=%s",
        settings.app_env,
        settings.app_port,
        bool(settings.openai_api_key),
        bool(settings.telegram_bot_token),
        settings.reflection_runtime_mode,
        settings.scheduler_enabled,
    )
    try:
        yield
    finally:
        await scheduler_worker.stop()
        await reflection_worker.stop()
        await telegram_client.close()
        await database.dispose()
        logger.info("AION stopped")


app = FastAPI(title="AION MVP", version="0.1.0", lifespan=lifespan)
app.include_router(router)
