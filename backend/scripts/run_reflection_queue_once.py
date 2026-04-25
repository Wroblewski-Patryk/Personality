from __future__ import annotations

import argparse
import asyncio
import json

from app.core.background_worker_policy import (
    REFLECTION_EXTERNAL_DRIVER_POLICY_OWNER,
    reflection_external_driver_policy_snapshot,
)
from app.core.config import get_settings
from app.core.database import Database
from app.core.logging import setup_logging
from app.memory.openai_embedding_client import OpenAIEmbeddingClient
from app.memory.repository import MemoryRepository
from app.reflection.worker import ReflectionWorker


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Drain the durable reflection queue once for external-driver posture."
    )
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--allow-in-process",
        action="store_true",
        help="Allow manual draining even when REFLECTION_RUNTIME_MODE is not deferred.",
    )
    return parser.parse_args()


async def _run() -> int:
    args = _parse_args()
    settings = get_settings()
    settings.validate_required()
    setup_logging(settings.log_level)

    policy = reflection_external_driver_policy_snapshot(
        reflection_runtime_mode=settings.reflection_runtime_mode,
        worker_running=False,
        scheduler_execution_mode=settings.scheduler_execution_mode,
    )
    if (
        str(policy["selected_runtime_mode"]) != "deferred"
        and not bool(args.allow_in_process)
    ):
        print(
            json.dumps(
                {
                    "policy_owner": REFLECTION_EXTERNAL_DRIVER_POLICY_OWNER,
                    "selected_runtime_mode": policy["selected_runtime_mode"],
                    "status": "blocked_non_deferred_runtime_mode",
                    "hint": "use --allow-in-process for local manual drain only",
                }
            )
        )
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
    reflection_worker = ReflectionWorker(memory_repository=memory_repository)
    try:
        summary = await reflection_worker.run_pending_once(limit=max(1, int(args.limit)))
    finally:
        await database.dispose()

    print(
        json.dumps(
            {
                "policy_owner": REFLECTION_EXTERNAL_DRIVER_POLICY_OWNER,
                "selected_runtime_mode": policy["selected_runtime_mode"],
                "selected_scheduler_execution_mode": policy[
                    "selected_scheduler_execution_mode"
                ],
                "entrypoint_path": policy["entrypoint_path"],
                "limit": max(1, int(args.limit)),
                "summary": summary,
                "status": "ok",
            }
        )
    )
    return 0


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    raise SystemExit(main())
