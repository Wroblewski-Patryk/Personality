from __future__ import annotations

from pathlib import Path

import yaml


def test_coolify_compose_defaults_reflection_runtime_mode_to_deferred() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    app_environment = compose["services"]["app"]["environment"]

    assert (
        app_environment["REFLECTION_RUNTIME_MODE"]
        == "${REFLECTION_RUNTIME_MODE:-deferred}"
    )


def test_coolify_compose_defaults_scheduler_execution_mode_to_externalized() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    app_environment = compose["services"]["app"]["environment"]

    assert (
        app_environment["SCHEDULER_EXECUTION_MODE"]
        == "${SCHEDULER_EXECUTION_MODE:-externalized}"
    )


def test_coolify_compose_defaults_attention_coordination_mode_to_durable_inbox() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    app_environment = compose["services"]["app"]["environment"]

    assert (
        app_environment["ATTENTION_COORDINATION_MODE"]
        == "${ATTENTION_COORDINATION_MODE:-durable_inbox}"
    )


def test_coolify_compose_defaults_proactive_enabled_to_true() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    app_environment = compose["services"]["app"]["environment"]

    assert app_environment["PROACTIVE_ENABLED"] == "${PROACTIVE_ENABLED:-true}"


def test_coolify_compose_defaults_embedding_provider_to_openai() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    app_environment = compose["services"]["app"]["environment"]

    assert app_environment["EMBEDDING_PROVIDER"] == "${EMBEDDING_PROVIDER:-openai}"


def test_coolify_compose_defaults_embedding_model_to_openai_small() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    app_environment = compose["services"]["app"]["environment"]

    assert app_environment["EMBEDDING_MODEL"] == "${EMBEDDING_MODEL:-text-embedding-3-small}"


def test_coolify_compose_maps_app_build_revision_to_coolify_source_commit() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    app_environment = compose["services"]["app"]["environment"]

    assert app_environment["APP_BUILD_REVISION"] == "${SOURCE_COMMIT:-unknown}"


def test_coolify_compose_defaults_deployment_trigger_mode_to_source_automation() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    app_environment = compose["services"]["app"]["environment"]

    assert app_environment["DEPLOYMENT_TRIGGER_MODE"] == "${DEPLOYMENT_TRIGGER_MODE:-source_automation}"


def test_coolify_compose_builds_runtime_services_with_app_build_revision_arg() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    for service_name in ("app", "maintenance_cadence", "proactive_cadence"):
        build_args = compose["services"][service_name]["build"]["args"]
        assert build_args["APP_BUILD_REVISION"] == "${SOURCE_COMMIT:-unknown}"


def test_coolify_compose_includes_external_cadence_services() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    maintenance_service = compose["services"]["maintenance_cadence"]
    proactive_service = compose["services"]["proactive_cadence"]
    app_environment = compose["services"]["app"]["environment"]

    assert (
        app_environment["CADENCE_FAILURE_RETRY_SECONDS"]
        == "${CADENCE_FAILURE_RETRY_SECONDS:-30}"
    )
    assert "if python scripts/run_maintenance_tick_once.py;" in maintenance_service["command"][2]
    assert "sleep ${CADENCE_FAILURE_RETRY_SECONDS:-30}" in maintenance_service["command"][2]
    assert "if python scripts/run_proactive_tick_once.py;" in proactive_service["command"][2]
    assert "sleep ${CADENCE_FAILURE_RETRY_SECONDS:-30}" in proactive_service["command"][2]
