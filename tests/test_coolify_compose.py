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
