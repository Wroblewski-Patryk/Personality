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


def test_coolify_compose_includes_external_cadence_services() -> None:
    compose_path = Path("docker-compose.coolify.yml")
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    maintenance_service = compose["services"]["maintenance_cadence"]
    proactive_service = compose["services"]["proactive_cadence"]

    assert "python scripts/run_maintenance_tick_once.py" in maintenance_service["command"][2]
    assert "python scripts/run_proactive_tick_once.py" in proactive_service["command"][2]
