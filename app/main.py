from contextlib import asynccontextmanager

from app.affective.assessor import AffectiveAssessor
from fastapi import FastAPI

from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.api.routes import router
from app.core.action import ActionExecutor
from app.core.affective_policy import affective_assessment_policy_snapshot
from app.core.attention import AttentionTurnCoordinator
from app.core.background_worker_policy import (
    reflection_external_driver_policy_snapshot,
)
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
from app.integrations.task_system.clickup_client import ClickUpTaskClient
from app.integrations.telegram.client import TelegramClient
from app.memory.embeddings import embedding_strategy_snapshot, normalize_embedding_source_kinds
from app.memory.openai_embedding_client import OpenAIEmbeddingClient
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
    if (
        app_environment(settings) == "production"
        and policy["event_debug_enabled"]
        and not policy["event_debug_shared_ingress_sunset_ready"]
    ):
        logger.warning(
            "runtime_policy_warning env=%s event_debug_shared_ingress_mode=%s recommendation=retire_shared_debug_ingress_from_normal_production_use",
            settings.app_env,
            policy["event_debug_shared_ingress_mode"],
        )
    if app_environment(settings) == "production":
        logger.info(
            "runtime_policy_compatibility_sunset_hint env=%s startup_schema_compatibility_sunset_ready=%s startup_schema_compatibility_sunset_reason=%s event_debug_shared_ingress_sunset_ready=%s event_debug_shared_ingress_sunset_reason=%s compatibility_sunset_ready=%s compatibility_sunset_blockers=%s",
            settings.app_env,
            policy["startup_schema_compatibility_sunset_ready"],
            policy["startup_schema_compatibility_sunset_reason"],
            policy["event_debug_shared_ingress_sunset_ready"],
            policy["event_debug_shared_ingress_sunset_reason"],
            policy["compatibility_sunset_ready"],
            ",".join(str(item) for item in policy["compatibility_sunset_blockers"]),
        )


def _log_embedding_strategy_warnings(*, settings, logger) -> None:
    source_kinds_getter = getattr(settings, "get_embedding_source_kinds", None)
    if callable(source_kinds_getter):
        source_kinds = tuple(source_kinds_getter())
    else:
        source_kinds = normalize_embedding_source_kinds(
            str(getattr(settings, "embedding_source_kinds", "episodic,semantic,affective"))
        )
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=bool(getattr(settings, "semantic_vector_enabled", True)),
        provider=str(getattr(settings, "embedding_provider", "deterministic")),
        model=str(getattr(settings, "embedding_model", "deterministic-v1")),
        dimensions=max(1, int(getattr(settings, "embedding_dimensions", 32))),
        source_kinds=source_kinds,
        refresh_mode=str(getattr(settings, "embedding_refresh_mode", "on_write")),
        refresh_interval_seconds=int(getattr(settings, "embedding_refresh_interval_seconds", 21600)),
        provider_ownership_enforcement=str(
            getattr(settings, "embedding_provider_ownership_enforcement", "warn")
        ),
        model_governance_enforcement=str(
            getattr(settings, "embedding_model_governance_enforcement", "warn")
        ),
        source_rollout_enforcement=str(
            getattr(settings, "embedding_source_rollout_enforcement", "warn")
        ),
        openai_api_key=str(getattr(settings, "openai_api_key", "") or ""),
    )
    if str(snapshot["semantic_embedding_warning_state"]) == "provider_fallback_active":
        logger.warning(
            "embedding_strategy_warning semantic_vector_enabled=%s requested_provider=%s effective_provider=%s requested_model=%s effective_model=%s ownership_state=%s ownership_hint=%s ownership_enforcement=%s ownership_enforcement_state=%s ownership_enforcement_hint=%s owner_strategy_state=%s owner_strategy_hint=%s owner_strategy_recommendation=%s hint=%s recommendation=keep_deterministic_or_implement_provider_execution",
            bool(snapshot["semantic_vector_enabled"]),
            str(snapshot["semantic_embedding_provider_requested"]),
            str(snapshot["semantic_embedding_provider_effective"]),
            str(snapshot["semantic_embedding_model_requested"]),
            str(snapshot["semantic_embedding_model_effective"]),
            str(snapshot["semantic_embedding_provider_ownership_state"]),
            str(snapshot["semantic_embedding_provider_ownership_hint"]),
            str(snapshot["semantic_embedding_provider_ownership_enforcement"]),
            str(snapshot["semantic_embedding_provider_ownership_enforcement_state"]),
            str(snapshot["semantic_embedding_provider_ownership_enforcement_hint"]),
            str(snapshot["semantic_embedding_owner_strategy_state"]),
            str(snapshot["semantic_embedding_owner_strategy_hint"]),
            str(snapshot["semantic_embedding_owner_strategy_recommendation"]),
            str(snapshot["semantic_embedding_provider_hint"]),
        )
    if str(snapshot["semantic_embedding_provider_ownership_enforcement_state"]) == "blocked":
        logger.error(
            "embedding_strategy_block semantic_vector_enabled=%s requested_provider=%s effective_provider=%s ownership_enforcement=%s ownership_enforcement_state=%s ownership_enforcement_hint=%s",
            bool(snapshot["semantic_vector_enabled"]),
            str(snapshot["semantic_embedding_provider_requested"]),
            str(snapshot["semantic_embedding_provider_effective"]),
            str(snapshot["semantic_embedding_provider_ownership_enforcement"]),
            str(snapshot["semantic_embedding_provider_ownership_enforcement_state"]),
            str(snapshot["semantic_embedding_provider_ownership_enforcement_hint"]),
        )
        raise RuntimeError(
            "Embedding provider ownership strict-mode violation: "
            f"requested_provider={snapshot['semantic_embedding_provider_requested']} "
            f"effective_provider={snapshot['semantic_embedding_provider_effective']}. "
            "Resolve provider ownership mismatch or set EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT=warn."
        )
    if str(snapshot["semantic_embedding_model_governance_state"]) == "deterministic_custom_model_name":
        logger.warning(
            "embedding_model_governance_warning semantic_vector_enabled=%s provider=%s requested_model=%s effective_model=%s governance_state=%s governance_enforcement=%s governance_enforcement_state=%s governance_enforcement_hint=%s hint=%s recommendation=use_deterministic_v1_or_implement_provider_backed_model_execution",
            bool(snapshot["semantic_vector_enabled"]),
            str(snapshot["semantic_embedding_provider_effective"]),
            str(snapshot["semantic_embedding_model_requested"]),
            str(snapshot["semantic_embedding_model_effective"]),
            str(snapshot["semantic_embedding_model_governance_state"]),
            str(snapshot["semantic_embedding_model_governance_enforcement"]),
            str(snapshot["semantic_embedding_model_governance_enforcement_state"]),
            str(snapshot["semantic_embedding_model_governance_enforcement_hint"]),
            str(snapshot["semantic_embedding_model_governance_hint"]),
        )
    if str(snapshot["semantic_embedding_model_governance_enforcement_state"]) == "blocked":
        logger.error(
            "embedding_model_governance_block semantic_vector_enabled=%s requested_model=%s effective_model=%s governance_enforcement=%s governance_enforcement_state=%s governance_enforcement_hint=%s",
            bool(snapshot["semantic_vector_enabled"]),
            str(snapshot["semantic_embedding_model_requested"]),
            str(snapshot["semantic_embedding_model_effective"]),
            str(snapshot["semantic_embedding_model_governance_enforcement"]),
            str(snapshot["semantic_embedding_model_governance_enforcement_state"]),
            str(snapshot["semantic_embedding_model_governance_enforcement_hint"]),
        )
        raise RuntimeError(
            "Embedding model governance strict-mode violation: "
            f"requested_model={snapshot['semantic_embedding_model_requested']} "
            f"effective_model={snapshot['semantic_embedding_model_effective']}. "
            "Resolve model governance mismatch or set EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT=warn."
        )
    if str(snapshot["semantic_embedding_source_coverage_state"]) in {
        "partial_for_current_retrieval_path",
        "missing_for_current_retrieval_path",
    }:
        logger.warning(
            "embedding_source_coverage_warning semantic_vector_enabled=%s source_kinds=%s coverage_state=%s hint=%s rollout_state=%s rollout_hint=%s rollout_recommendation=%s rollout_next_source_kind=%s rollout_completion_state=%s rollout_progress_percent=%s recommendation=enable_semantic_and_affective_sources_for_vector_hits",
            bool(snapshot["semantic_vector_enabled"]),
            ",".join(str(item) for item in snapshot["semantic_embedding_source_kinds"]),
            str(snapshot["semantic_embedding_source_coverage_state"]),
            str(snapshot["semantic_embedding_source_coverage_hint"]),
            str(snapshot["semantic_embedding_source_rollout_state"]),
            str(snapshot["semantic_embedding_source_rollout_hint"]),
            str(snapshot["semantic_embedding_source_rollout_recommendation"]),
            str(snapshot["semantic_embedding_source_rollout_next_source_kind"]),
            str(snapshot["semantic_embedding_source_rollout_completion_state"]),
            int(snapshot["semantic_embedding_source_rollout_progress_percent"]),
        )
    if (
        bool(snapshot["semantic_vector_enabled"])
        and str(snapshot["semantic_embedding_source_rollout_next_source_kind"]) != "none"
    ):
        logger.info(
            "embedding_source_rollout_hint semantic_vector_enabled=%s rollout_state=%s rollout_completion_state=%s rollout_next_source_kind=%s rollout_enabled_sources=%s rollout_missing_sources=%s rollout_phase_index=%s rollout_phase_total=%s rollout_progress_percent=%s rollout_recommendation=%s",
            bool(snapshot["semantic_vector_enabled"]),
            str(snapshot["semantic_embedding_source_rollout_state"]),
            str(snapshot["semantic_embedding_source_rollout_completion_state"]),
            str(snapshot["semantic_embedding_source_rollout_next_source_kind"]),
            ",".join(str(item) for item in snapshot["semantic_embedding_source_rollout_enabled_sources"]),
            ",".join(str(item) for item in snapshot["semantic_embedding_source_rollout_missing_sources"]),
            int(snapshot["semantic_embedding_source_rollout_phase_index"]),
            int(snapshot["semantic_embedding_source_rollout_phase_total"]),
            int(snapshot["semantic_embedding_source_rollout_progress_percent"]),
            str(snapshot["semantic_embedding_source_rollout_recommendation"]),
        )
    source_rollout_enforcement_alignment_state = str(
        snapshot["semantic_embedding_source_rollout_enforcement_alignment_state"]
    )
    if source_rollout_enforcement_alignment_state in {
        "below_recommendation",
        "above_recommendation",
        "aligned_with_recommendation",
    }:
        logger.info(
            "embedding_source_rollout_enforcement_hint semantic_vector_enabled=%s source_rollout_enforcement=%s recommended_source_rollout_enforcement=%s source_rollout_enforcement_alignment=%s source_rollout_enforcement_alignment_state=%s source_rollout_enforcement_alignment_hint=%s rollout_completion_state=%s rollout_next_source_kind=%s",
            bool(snapshot["semantic_vector_enabled"]),
            str(snapshot["semantic_embedding_source_rollout_enforcement"]),
            str(snapshot["semantic_embedding_recommended_source_rollout_enforcement"]),
            str(snapshot["semantic_embedding_source_rollout_enforcement_alignment"]),
            source_rollout_enforcement_alignment_state,
            str(snapshot["semantic_embedding_source_rollout_enforcement_alignment_hint"]),
            str(snapshot["semantic_embedding_source_rollout_completion_state"]),
            str(snapshot["semantic_embedding_source_rollout_next_source_kind"]),
        )
    if str(snapshot["semantic_embedding_source_rollout_enforcement_state"]) == "warning_only":
        logger.warning(
            "embedding_source_rollout_warning semantic_vector_enabled=%s source_rollout_enforcement=%s source_rollout_enforcement_state=%s source_rollout_enforcement_hint=%s recommended_source_rollout_enforcement=%s source_rollout_enforcement_alignment=%s source_rollout_enforcement_alignment_state=%s source_rollout_enforcement_alignment_hint=%s rollout_state=%s rollout_completion_state=%s rollout_next_source_kind=%s recommendation=complete_source_rollout_or_keep_warn_mode",
            bool(snapshot["semantic_vector_enabled"]),
            str(snapshot["semantic_embedding_source_rollout_enforcement"]),
            str(snapshot["semantic_embedding_source_rollout_enforcement_state"]),
            str(snapshot["semantic_embedding_source_rollout_enforcement_hint"]),
            str(snapshot["semantic_embedding_recommended_source_rollout_enforcement"]),
            str(snapshot["semantic_embedding_source_rollout_enforcement_alignment"]),
            source_rollout_enforcement_alignment_state,
            str(snapshot["semantic_embedding_source_rollout_enforcement_alignment_hint"]),
            str(snapshot["semantic_embedding_source_rollout_state"]),
            str(snapshot["semantic_embedding_source_rollout_completion_state"]),
            str(snapshot["semantic_embedding_source_rollout_next_source_kind"]),
        )
    if str(snapshot["semantic_embedding_source_rollout_enforcement_state"]) == "blocked":
        logger.error(
            "embedding_source_rollout_block semantic_vector_enabled=%s source_rollout_enforcement=%s source_rollout_enforcement_state=%s source_rollout_enforcement_hint=%s recommended_source_rollout_enforcement=%s source_rollout_enforcement_alignment=%s source_rollout_enforcement_alignment_state=%s source_rollout_enforcement_alignment_hint=%s rollout_state=%s rollout_completion_state=%s rollout_next_source_kind=%s",
            bool(snapshot["semantic_vector_enabled"]),
            str(snapshot["semantic_embedding_source_rollout_enforcement"]),
            str(snapshot["semantic_embedding_source_rollout_enforcement_state"]),
            str(snapshot["semantic_embedding_source_rollout_enforcement_hint"]),
            str(snapshot["semantic_embedding_recommended_source_rollout_enforcement"]),
            str(snapshot["semantic_embedding_source_rollout_enforcement_alignment"]),
            source_rollout_enforcement_alignment_state,
            str(snapshot["semantic_embedding_source_rollout_enforcement_alignment_hint"]),
            str(snapshot["semantic_embedding_source_rollout_state"]),
            str(snapshot["semantic_embedding_source_rollout_completion_state"]),
            str(snapshot["semantic_embedding_source_rollout_next_source_kind"]),
        )
        raise RuntimeError(
            "Embedding source rollout strict-mode violation: "
            f"rollout_completion_state={snapshot['semantic_embedding_source_rollout_completion_state']} "
            f"next_source_kind={snapshot['semantic_embedding_source_rollout_next_source_kind']}. "
            "Complete source rollout or set EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT=warn."
        )
    if str(snapshot["semantic_embedding_refresh_state"]) == "manual_refresh_required":
        logger.warning(
            "embedding_refresh_warning semantic_vector_enabled=%s refresh_mode=%s refresh_interval_seconds=%s refresh_state=%s hint=%s refresh_cadence_state=%s refresh_cadence_hint=%s recommendation=ensure_manual_refresh_process_is_defined",
            bool(snapshot["semantic_vector_enabled"]),
            str(snapshot["semantic_embedding_refresh_mode"]),
            int(snapshot["semantic_embedding_refresh_interval_seconds"]),
            str(snapshot["semantic_embedding_refresh_state"]),
            str(snapshot["semantic_embedding_refresh_hint"]),
            str(snapshot["semantic_embedding_refresh_cadence_state"]),
            str(snapshot["semantic_embedding_refresh_cadence_hint"]),
        )
    refresh_alignment_state = str(snapshot["semantic_embedding_refresh_alignment_state"])
    if refresh_alignment_state in {
        "manual_override",
        "on_write_before_recommended_manual",
    }:
        logger.info(
            "embedding_refresh_hint semantic_vector_enabled=%s refresh_mode=%s recommended_refresh_mode=%s refresh_alignment_state=%s refresh_alignment_hint=%s refresh_cadence_state=%s refresh_cadence_hint=%s refresh_interval_seconds=%s",
            bool(snapshot["semantic_vector_enabled"]),
            str(snapshot["semantic_embedding_refresh_mode"]),
            str(snapshot["semantic_embedding_recommended_refresh_mode"]),
            refresh_alignment_state,
            str(snapshot["semantic_embedding_refresh_alignment_hint"]),
            str(snapshot["semantic_embedding_refresh_cadence_state"]),
            str(snapshot["semantic_embedding_refresh_cadence_hint"]),
            int(snapshot["semantic_embedding_refresh_interval_seconds"]),
        )
    alignment_state = str(snapshot["semantic_embedding_enforcement_alignment_state"])
    if alignment_state in {
        "below_recommendation",
        "mixed_relative_to_recommendation",
        "above_recommendation",
        "aligned_with_recommendation",
    }:
        logger.info(
            "embedding_strategy_hint semantic_vector_enabled=%s enforcement_alignment_state=%s enforcement_alignment_hint=%s strict_rollout_ready=%s strict_rollout_state=%s strict_rollout_hint=%s strict_rollout_recommendation=%s strict_rollout_violation_count=%s strict_rollout_violations=%s recommended_provider_ownership_enforcement=%s recommended_model_governance_enforcement=%s",
            bool(snapshot["semantic_vector_enabled"]),
            alignment_state,
            str(snapshot["semantic_embedding_enforcement_alignment_hint"]),
            bool(snapshot["semantic_embedding_strict_rollout_ready"]),
            str(snapshot["semantic_embedding_strict_rollout_state"]),
            str(snapshot["semantic_embedding_strict_rollout_hint"]),
            str(snapshot["semantic_embedding_strict_rollout_recommendation"]),
            int(snapshot["semantic_embedding_strict_rollout_violation_count"]),
            ",".join(str(item) for item in snapshot["semantic_embedding_strict_rollout_violations"]),
            str(snapshot["semantic_embedding_recommended_provider_ownership_enforcement"]),
            str(snapshot["semantic_embedding_recommended_model_governance_enforcement"]),
        )


def _log_affective_assessment_policy(*, settings, logger) -> None:
    snapshot = affective_assessment_policy_snapshot(settings)
    if str(snapshot["affective_assessment_posture"]) == "fallback_only_classifier_unavailable":
        logger.warning(
            "affective_assessment_policy_warning env=%s enabled=%s source=%s classifier_available=%s posture=%s hint=%s",
            settings.app_env,
            bool(snapshot["affective_assessment_enabled"]),
            str(snapshot["affective_assessment_source"]),
            bool(snapshot["affective_classifier_available"]),
            str(snapshot["affective_assessment_posture"]),
            str(snapshot["affective_assessment_hint"]),
        )
    else:
        logger.info(
            "affective_assessment_policy env=%s enabled=%s source=%s classifier_available=%s posture=%s hint=%s",
            settings.app_env,
            bool(snapshot["affective_assessment_enabled"]),
            str(snapshot["affective_assessment_source"]),
            bool(snapshot["affective_classifier_available"]),
            str(snapshot["affective_assessment_posture"]),
            str(snapshot["affective_assessment_hint"]),
        )


def _log_reflection_external_driver_policy(
    *,
    settings,
    logger,
    worker_running: bool,
) -> None:
    snapshot = reflection_external_driver_policy_snapshot(
        reflection_runtime_mode=str(getattr(settings, "reflection_runtime_mode", "in_process")),
        worker_running=worker_running,
        scheduler_execution_mode=str(
            getattr(settings, "scheduler_execution_mode", "in_process")
        ),
    )
    logger.info(
        "reflection_external_driver_policy policy_owner=%s selected_runtime_mode=%s selected_scheduler_execution_mode=%s production_baseline_ready=%s production_baseline_state=%s entrypoint_path=%s hint=%s",
        str(snapshot["policy_owner"]),
        str(snapshot["selected_runtime_mode"]),
        str(snapshot["selected_scheduler_execution_mode"]),
        bool(snapshot["production_baseline_ready"]),
        str(snapshot["production_baseline_state"]),
        str(snapshot["entrypoint_path"]),
        str(snapshot["production_baseline_hint"]),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.validate_required()

    setup_logging(settings.log_level)
    logger = get_logger("aion.app")
    _log_runtime_policy_warnings(settings=settings, logger=logger)
    _log_embedding_strategy_warnings(settings=settings, logger=logger)
    _log_affective_assessment_policy(settings=settings, logger=logger)

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
    scheduler_worker = SchedulerWorker(
        memory_repository=memory_repository,
        reflection_worker=reflection_worker,
        enabled=settings.scheduler_enabled,
        reflection_runtime_mode=settings.reflection_runtime_mode,
        reflection_interval_seconds=settings.reflection_interval,
        maintenance_interval_seconds=settings.maintenance_interval,
        execution_mode=settings.scheduler_execution_mode,
        proactive_enabled=settings.proactive_enabled,
        proactive_interval_seconds=settings.proactive_interval,
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
    _log_reflection_external_driver_policy(
        settings=settings,
        logger=logger,
        worker_running=reflection_worker.is_running(),
    )
    if scheduler_worker.enabled:
        await scheduler_worker.start()
        logger.info(
            "scheduler_runtime enabled=%s configured_enabled=%s execution_mode=%s reflection_interval=%s maintenance_interval=%s proactive_enabled=%s",
            scheduler_worker.enabled,
            settings.scheduler_enabled,
            settings.scheduler_execution_mode,
            settings.reflection_interval,
            settings.maintenance_interval,
            settings.proactive_enabled,
        )
    else:
        logger.info(
            "scheduler_runtime enabled=%s configured_enabled=%s execution_mode=%s proactive_enabled=%s",
            scheduler_worker.enabled,
            settings.scheduler_enabled,
            settings.scheduler_execution_mode,
            settings.proactive_enabled,
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
        reflection_worker=runtime_reflection_worker,
        affective_assessor=AffectiveAssessor(
            classifier_client=openai_client,
            enabled=settings.is_affective_assessment_enabled(),
            policy_source=(
                "explicit"
                if settings.affective_assessment_enabled is not None
                else "environment_default"
            ),
        ),
        semantic_vector_enabled=bool(getattr(settings, "semantic_vector_enabled", True)),
        embedding_provider=str(getattr(settings, "embedding_provider", "deterministic")),
        embedding_model=str(getattr(settings, "embedding_model", "deterministic-v1")),
        embedding_dimensions=int(getattr(settings, "embedding_dimensions", 32)),
        reflection_runtime_mode=settings.reflection_runtime_mode,
    )
    scheduler_worker.set_runtime(runtime)
    attention_turn_coordinator = AttentionTurnCoordinator(
        burst_window_ms=settings.attention_burst_window_ms,
        answered_ttl_seconds=settings.attention_answered_ttl_seconds,
        stale_turn_seconds=settings.attention_stale_turn_seconds,
        coordination_mode=settings.attention_coordination_mode,
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
        "AION started env=%s port=%s openai_enabled=%s telegram_enabled=%s reflection_runtime_mode=%s scheduler_enabled=%s scheduler_execution_mode=%s proactive_enabled=%s attention_coordination_mode=%s semantic_vector_enabled=%s embedding_provider=%s embedding_model=%s embedding_dimensions=%s embedding_refresh_mode=%s embedding_refresh_interval_seconds=%s embedding_provider_ownership_enforcement=%s embedding_model_governance_enforcement=%s embedding_source_rollout_enforcement=%s",
        settings.app_env,
        settings.app_port,
        bool(settings.openai_api_key),
        bool(settings.telegram_bot_token),
        settings.reflection_runtime_mode,
        settings.scheduler_enabled,
        settings.scheduler_execution_mode,
        settings.proactive_enabled,
        settings.attention_coordination_mode,
        bool(getattr(settings, "semantic_vector_enabled", True)),
        str(getattr(settings, "embedding_provider", "deterministic")),
        str(getattr(settings, "embedding_model", "deterministic-v1")),
        int(getattr(settings, "embedding_dimensions", 32)),
        str(getattr(settings, "embedding_refresh_mode", "on_write")),
        int(getattr(settings, "embedding_refresh_interval_seconds", 21600)),
        str(getattr(settings, "embedding_provider_ownership_enforcement", "warn")),
        str(getattr(settings, "embedding_model_governance_enforcement", "warn")),
        str(getattr(settings, "embedding_source_rollout_enforcement", "warn")),
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
