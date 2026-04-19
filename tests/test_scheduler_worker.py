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
