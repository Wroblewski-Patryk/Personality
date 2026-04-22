import logging

from app.workers.scheduler import SchedulerWorker


class FakeReflectionWorker:
    def __init__(self, *, running: bool = False):
        self.running = running
        self.run_pending_limits: list[int] = []

    def is_running(self) -> bool:
        return self.running

    async def run_pending_once(self, *, limit: int = 10) -> dict[str, int]:
        self.run_pending_limits.append(limit)
        return {
            "scanned": 3,
            "processed": 2,
            "completed": 2,
            "failed": 0,
            "skipped_not_ready": 1,
        }

    def snapshot(self) -> dict:
        return {
            "running": self.running,
            "queue_size": 0,
            "queue_capacity": 100,
            "queued_task_count": 0,
            "queued_task_ids": [],
            "max_attempts": 3,
            "retry_backoff_seconds": [5, 30, 120],
            "stuck_processing_seconds": 180,
        }


class FakeMemoryRepository:
    def __init__(self, stats: dict[str, int] | None = None):
        self.stats = stats or {
            "total": 4,
            "pending": 1,
            "processing": 1,
            "completed": 1,
            "failed": 1,
            "retryable_failed": 1,
            "exhausted_failed": 0,
            "stuck_processing": 0,
        }
        self.stats_calls: list[dict] = []
        self.proactive_candidates: list[dict] = []

    async def get_reflection_task_stats(
        self,
        *,
        max_attempts: int,
        stuck_after_seconds: int,
        retry_backoff_seconds: tuple[int, ...],
        now=None,
    ) -> dict[str, int]:
        self.stats_calls.append(
            {
                "max_attempts": max_attempts,
                "stuck_after_seconds": stuck_after_seconds,
                "retry_backoff_seconds": retry_backoff_seconds,
            }
        )
        return self.stats

    async def get_proactive_scheduler_candidates(
        self,
        *,
        proactive_interval_seconds: int,
        limit: int = 8,
    ) -> list[dict]:
        return self.proactive_candidates[:limit]


class FakeRuntime:
    def __init__(self, *, status: str = "success", actions: list[str] | None = None):
        self.calls: list[dict] = []
        self.status = status
        self.actions = list(actions or ["send_telegram_message"])

    async def run(self, event):
        self.calls.append(
            {
                "user_id": event.meta.user_id,
                "subsource": event.subsource,
                "chat_id": event.payload.get("chat_id"),
                "trigger": event.payload.get("proactive", {}).get("trigger"),
            }
        )

        class Result:
            def __init__(self, status: str, actions: list[str]):
                self.action_result = type("ActionResult", (), {"status": status, "actions": actions})()

        return Result(self.status, self.actions)


async def test_scheduler_worker_reflection_tick_runs_in_deferred_mode() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="deferred",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )

    summary = await scheduler.run_reflection_tick_once(reason="test_reflection")

    assert reflection_worker.run_pending_limits == [10]
    assert summary["executed"] is True
    assert summary["reason"] == "deferred_runtime"
    assert summary["processed"] == 2


async def test_scheduler_worker_reflection_tick_skips_when_in_process_worker_is_running() -> None:
    reflection_worker = FakeReflectionWorker(running=True)
    repository = FakeMemoryRepository()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="in_process",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )

    summary = await scheduler.run_reflection_tick_once(reason="test_reflection")

    assert reflection_worker.run_pending_limits == []
    assert summary["executed"] is False
    assert summary["reason"] == "in_process_worker_running"


async def test_scheduler_worker_reflection_tick_dispatches_when_in_process_worker_is_stopped() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="in_process",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )

    summary = await scheduler.run_reflection_tick_once(reason="test_reflection")

    assert reflection_worker.run_pending_limits == [10]
    assert summary["executed"] is True
    assert summary["reason"] == "in_process_worker_not_running"


async def test_scheduler_worker_maintenance_tick_uses_reflection_worker_guardrail_settings() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository(
        stats={
            "total": 5,
            "pending": 2,
            "processing": 0,
            "completed": 2,
            "failed": 1,
            "retryable_failed": 1,
            "exhausted_failed": 0,
            "stuck_processing": 0,
        }
    )
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="deferred",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )

    summary = await scheduler.run_maintenance_tick_once(reason="test_maintenance")

    assert repository.stats_calls == [
        {
            "max_attempts": 3,
            "stuck_after_seconds": 180,
            "retry_backoff_seconds": (5, 30, 120),
        }
    ]
    assert summary == {
        "executed": True,
        "reason": "in_process_owner_mode",
        "trigger": "test_maintenance",
        "pending": 2,
        "processing": 0,
        "retryable_failed": 1,
        "exhausted_failed": 0,
        "stuck_processing": 0,
    }


async def test_scheduler_worker_start_is_noop_when_scheduler_disabled() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=False,
        reflection_runtime_mode="deferred",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )

    await scheduler.start()
    snapshot = scheduler.snapshot()
    await scheduler.stop()

    assert snapshot["enabled"] is False
    assert snapshot["running"] is False


async def test_scheduler_worker_externalized_execution_mode_disables_in_process_start() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="in_process",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
        execution_mode="externalized",
        proactive_enabled=True,
    )

    await scheduler.start()
    snapshot = scheduler.snapshot()
    await scheduler.stop()

    assert snapshot["execution_mode"] == "externalized"
    assert snapshot["configured_enabled"] is True
    assert snapshot["enabled"] is False
    assert snapshot["running"] is False
    assert snapshot["proactive_enabled"] is True
    assert snapshot["maintenance_cadence_owner"] == "external_scheduler"
    assert snapshot["proactive_cadence_owner"] == "external_scheduler"
    assert snapshot["cadence_execution"]["ready"] is True
    assert snapshot["cadence_execution"]["selected_execution_mode"] == "externalized"


async def test_scheduler_worker_maintenance_tick_skips_when_execution_mode_is_externalized() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="in_process",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
        execution_mode="externalized",
        proactive_enabled=True,
    )

    summary = await scheduler.run_maintenance_tick_once(reason="test_maintenance")

    assert summary == {
        "executed": False,
        "reason": "externalized_owner_mode",
        "trigger": "test_maintenance",
        "pending": 0,
        "processing": 0,
        "retryable_failed": 0,
        "exhausted_failed": 0,
        "stuck_processing": 0,
    }
    assert repository.stats_calls == []


async def test_scheduler_worker_snapshot_exposes_owner_aware_execution_posture() -> None:
    reflection_worker = FakeReflectionWorker(running=True)
    repository = FakeMemoryRepository()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="in_process",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
        execution_mode="in_process",
        proactive_enabled=False,
    )

    snapshot = scheduler.snapshot()

    assert snapshot["execution_mode"] == "in_process"
    assert snapshot["configured_enabled"] is True
    assert snapshot["maintenance_cadence_owner"] == "in_process_scheduler"
    assert snapshot["proactive_cadence_owner"] == "in_process_scheduler"
    assert snapshot["cadence_execution"]["ready"] is False
    assert "in_process_scheduler_not_running" in snapshot["cadence_execution"]["blocking_signals"]
    assert snapshot["cadence_execution"]["maintenance_tick_dispatch"] is True
    assert snapshot["cadence_execution"]["maintenance_tick_reason"] == "in_process_owner_mode"
    assert snapshot["cadence_execution"]["proactive_tick_dispatch"] is False
    assert snapshot["cadence_execution"]["proactive_tick_reason"] == "proactive_disabled"


async def test_scheduler_worker_proactive_tick_emits_bounded_scheduler_events() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    repository.proactive_candidates = [
        {
            "user_id": "123456",
            "chat_id": 123456,
            "trigger": "task_blocked",
            "text": "follow up on blocked task deploy",
            "recent_outbound_count": 0,
            "unanswered_proactive_count": 0,
            "recent_user_activity": "active",
        }
    ]
    runtime = FakeRuntime()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="deferred",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
        proactive_enabled=True,
        proactive_interval_seconds=1800,
    )
    scheduler.set_runtime(runtime)

    summary = await scheduler.run_proactive_tick_once(reason="test_proactive")

    assert summary == {
        "executed": True,
        "reason": "in_process_owner_mode",
        "trigger": "test_proactive",
        "candidates_considered": 1,
        "events_emitted": 1,
        "messages_delivered": 1,
        "delivery_blocked": 0,
        "failures": 0,
    }
    assert runtime.calls == [
        {
            "user_id": "123456",
            "subsource": "proactive_tick",
            "chat_id": 123456,
            "trigger": "task_blocked",
        }
    ]


async def test_scheduler_worker_snapshot_exposes_live_proactive_policy() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="deferred",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
        proactive_enabled=True,
        proactive_interval_seconds=1800,
    )

    await scheduler.start()
    snapshot = scheduler.snapshot()
    await scheduler.stop()

    assert snapshot["proactive_interval_seconds"] == 1800
    assert snapshot["proactive_policy"]["policy_owner"] == "proactive_runtime_policy"
    assert snapshot["proactive_policy"]["selected_cadence_owner"] == "in_process_scheduler"
    assert snapshot["proactive_policy"]["production_baseline_ready"] is True
    assert snapshot["proactive_policy"]["production_baseline_state"] == "in_process_scheduler_live"


async def test_scheduler_worker_reflection_tick_logs_worker_mode_handoff_posture(caplog) -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="deferred",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )
    caplog.set_level(logging.INFO, logger="aion.scheduler")

    await scheduler.run_reflection_tick_once(reason="test_reflection")

    message = next(
        record.getMessage()
        for record in caplog.records
        if record.name == "aion.scheduler" and "scheduler_reflection_tick" in record.getMessage()
    )
    assert "runtime_mode=deferred" in message
    assert "queue_drain_owner=external_driver" in message
    assert "external_driver_expected=True" in message
    assert "retry_owner=durable_queue" in message


async def test_scheduler_worker_reflection_tick_logs_in_process_handoff_posture_when_worker_stopped(caplog) -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="in_process",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )
    caplog.set_level(logging.INFO, logger="aion.scheduler")

    await scheduler.run_reflection_tick_once(reason="test_reflection")

    message = next(
        record.getMessage()
        for record in caplog.records
        if record.name == "aion.scheduler" and "scheduler_reflection_tick" in record.getMessage()
    )
    assert "runtime_mode=in_process" in message
    assert "queue_drain_owner=in_process_worker" in message
    assert "external_driver_expected=False" in message
    assert "retry_owner=durable_queue" in message
