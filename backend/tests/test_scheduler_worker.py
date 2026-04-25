import logging
from datetime import datetime, timedelta, timezone

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
        self.cadence_evidence_writes: list[dict] = []
        self.due_planned_work: list[dict] = []
        self.subconscious_proposals: list[dict] = []
        self.planned_work_due_updates: list[dict] = []
        self.planned_work_snoozes: list[dict] = []
        self.planned_work_recurrence_updates: list[dict] = []
        self.planned_work_cancellations: list[int] = []

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

    async def upsert_scheduler_cadence_evidence(
        self,
        *,
        cadence_kind: str,
        execution_owner: str,
        execution_mode: str,
        summary: dict,
        last_run_at,
    ) -> dict:
        payload = {
            "cadence_kind": cadence_kind,
            "execution_owner": execution_owner,
            "execution_mode": execution_mode,
            "summary": dict(summary),
            "last_run_at": last_run_at,
        }
        self.cadence_evidence_writes.append(payload)
        return payload

    async def get_due_planned_work(self, *, now: datetime | None = None, limit: int = 8) -> list[dict]:
        due_at = now or datetime.now(timezone.utc)
        rows = []
        for item in self.due_planned_work:
            if item.get("status") not in {"pending", "snoozed"}:
                continue
            preferred_at = item.get("preferred_at")
            if preferred_at is not None and preferred_at <= due_at:
                rows.append(item)
        return rows[:limit]

    async def upsert_subconscious_proposal(self, **kwargs) -> dict:
        payload = {
            "proposal_id": len(self.subconscious_proposals) + 1,
            "status": "pending",
            **kwargs,
        }
        self.subconscious_proposals.append(payload)
        return payload

    async def mark_planned_work_due(self, *, work_id: int, evaluated_at: datetime | None = None) -> dict | None:
        for item in self.due_planned_work:
            if int(item["id"]) == work_id:
                item["status"] = "due"
                item["last_evaluated_at"] = evaluated_at
                payload = {
                    "work_id": work_id,
                    "evaluated_at": evaluated_at,
                    "status": "due",
                }
                self.planned_work_due_updates.append(payload)
                return dict(item)
        return None

    async def snooze_planned_work_item(
        self,
        *,
        work_id: int,
        until_at: datetime,
        evaluated_at: datetime | None = None,
    ) -> dict | None:
        for item in self.due_planned_work:
            if int(item["id"]) == work_id:
                item["status"] = "snoozed"
                item["preferred_at"] = until_at
                item["not_before"] = until_at
                item["last_evaluated_at"] = evaluated_at
                payload = {
                    "work_id": work_id,
                    "until_at": until_at,
                    "evaluated_at": evaluated_at,
                    "status": "snoozed",
                }
                self.planned_work_snoozes.append(payload)
                return dict(item)
        return None

    async def advance_planned_work_recurrence(self, *, work_id: int, evaluated_at: datetime | None = None) -> dict | None:
        for item in self.due_planned_work:
            if int(item["id"]) != work_id:
                continue
            mode = str(item.get("recurrence_mode", "none")).strip().lower()
            if mode == "daily":
                delta = timedelta(days=1)
            elif mode == "weekly":
                delta = timedelta(days=7)
            elif mode == "custom":
                rule = str(item.get("recurrence_rule", "")).strip().lower()
                interval = 1
                if rule.startswith("interval_days:"):
                    interval = max(1, int(rule.split(":", 1)[1]))
                delta = timedelta(days=interval)
            else:
                return None
            anchor = item.get("preferred_at") or item.get("not_before") or evaluated_at or datetime.now(timezone.utc)
            item["status"] = "pending"
            item["preferred_at"] = anchor + delta
            item["not_before"] = anchor + delta
            item["last_evaluated_at"] = evaluated_at
            payload = {
                "work_id": work_id,
                "evaluated_at": evaluated_at,
                "status": "pending",
                "preferred_at": item["preferred_at"],
            }
            self.planned_work_recurrence_updates.append(payload)
            return dict(item)
        return None

    async def cancel_planned_work_item(self, *, work_id: int) -> dict | None:
        for item in self.due_planned_work:
            if int(item["id"]) == work_id:
                item["status"] = "cancelled"
                self.planned_work_cancellations.append(work_id)
                return dict(item)
        return None


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
                "planned_work_due": event.payload.get("planned_work_due"),
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
        "due_planned_work": 0,
        "proposal_handoffs_created": 0,
        "foreground_events_emitted": 0,
        "foreground_delivery_successes": 0,
        "foreground_delivery_blocked": 0,
        "foreground_failures": 0,
        "delivery_delayed": 0,
        "delivery_skipped": 0,
        "recurrence_advanced": 0,
    }


async def test_scheduler_worker_maintenance_tick_hands_due_planned_work_to_proposal_boundary() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    repository.due_planned_work = [
        {
            "id": 9,
            "user_id": "u-1",
            "kind": "reminder",
            "summary": "send the release summary",
            "status": "pending",
            "delivery_channel": "telegram",
            "preferred_at": datetime.now(timezone.utc) - timedelta(minutes=5),
            "source_event_id": "evt-reminder-1",
        }
    ]
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="deferred",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )

    summary = await scheduler.run_maintenance_tick_once(reason="planned_work_due_check")

    assert summary["executed"] is True
    assert summary["due_planned_work"] == 1
    assert summary["proposal_handoffs_created"] == 1
    assert summary["foreground_events_emitted"] == 0
    assert summary["delivery_delayed"] == 0
    assert summary["delivery_skipped"] == 0
    assert summary["recurrence_advanced"] == 0
    assert repository.subconscious_proposals[0]["proposal_type"] == "nudge_user"
    assert repository.subconscious_proposals[0]["payload"]["handoff_kind"] == "planned_work_due"
    assert repository.subconscious_proposals[0]["payload"]["work_id"] == 9
    assert repository.planned_work_due_updates[0]["work_id"] == 9


async def test_scheduler_worker_maintenance_tick_dispatches_due_planned_work_via_runtime_foreground() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    repository.due_planned_work = [
        {
            "id": 11,
            "user_id": "123456",
            "kind": "follow_up",
            "summary": "check the release outcome",
            "status": "pending",
            "delivery_channel": "telegram",
            "requires_foreground_execution": True,
            "preferred_at": datetime.now(timezone.utc) - timedelta(minutes=3),
            "source_event_id": "evt-follow-up-11",
        }
    ]
    runtime = FakeRuntime(status="success", actions=["send_telegram_message"])
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="deferred",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )
    scheduler.set_runtime(runtime)

    summary = await scheduler.run_maintenance_tick_once(reason="planned_work_foreground_delivery")

    assert summary["due_planned_work"] == 1
    assert summary["proposal_handoffs_created"] == 1
    assert summary["foreground_events_emitted"] == 1
    assert summary["foreground_delivery_successes"] == 1
    assert summary["foreground_delivery_blocked"] == 0
    assert summary["foreground_failures"] == 0
    assert summary["delivery_delayed"] == 0
    assert summary["delivery_skipped"] == 0
    assert summary["recurrence_advanced"] == 0
    assert runtime.calls == [
        {
            "user_id": "123456",
            "subsource": "maintenance_tick",
            "chat_id": 123456,
            "trigger": None,
            "planned_work_due": {
                "work_id": 11,
                "summary": "check the release outcome",
                "work_kind": "follow_up",
                "delivery_channel": "telegram",
                "source_event_id": "evt-follow-up-11",
            },
        }
    ]


async def test_scheduler_worker_delays_due_planned_work_during_quiet_hours() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    repository.due_planned_work = [
        {
            "id": 12,
            "user_id": "123456",
            "kind": "reminder",
            "summary": "send the status update",
            "status": "pending",
            "delivery_channel": "telegram",
            "quiet_hours_policy": "respect_user_context",
            "preferred_at": datetime(2026, 4, 25, 22, 30, tzinfo=timezone.utc),
        }
    ]
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="deferred",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )

    summary = await scheduler._handoff_due_planned_work(now=datetime(2026, 4, 25, 22, 45, tzinfo=timezone.utc))

    assert summary["due_planned_work"] == 0
    assert summary["proposal_handoffs_created"] == 0
    assert summary["delivery_delayed"] == 1
    assert summary["delivery_skipped"] == 0
    assert summary["recurrence_advanced"] == 0
    assert repository.planned_work_snoozes[0]["work_id"] == 12
    assert repository.planned_work_snoozes[0]["until_at"] == datetime(2026, 4, 26, 7, 0, tzinfo=timezone.utc)


async def test_scheduler_worker_advances_recurring_due_planned_work_after_successful_delivery() -> None:
    reflection_worker = FakeReflectionWorker(running=False)
    repository = FakeMemoryRepository()
    repository.due_planned_work = [
        {
            "id": 13,
            "user_id": "123456",
            "kind": "routine",
            "summary": "daily planning review",
            "status": "pending",
            "delivery_channel": "telegram",
            "recurrence_mode": "daily",
            "recurrence_rule": "",
            "requires_foreground_execution": True,
            "preferred_at": datetime.now(timezone.utc) - timedelta(minutes=5),
            "source_event_id": "evt-routine-13",
        }
    ]
    runtime = FakeRuntime(status="success", actions=["send_telegram_message"])
    scheduler = SchedulerWorker(
        memory_repository=repository,  # type: ignore[arg-type]
        reflection_worker=reflection_worker,  # type: ignore[arg-type]
        enabled=True,
        reflection_runtime_mode="deferred",
        reflection_interval_seconds=900,
        maintenance_interval_seconds=3600,
    )
    scheduler.set_runtime(runtime)

    summary = await scheduler.run_maintenance_tick_once(reason="recurring_due_delivery")

    assert summary["due_planned_work"] == 1
    assert summary["foreground_delivery_successes"] == 1
    assert summary["recurrence_advanced"] == 1
    assert repository.planned_work_recurrence_updates[0]["work_id"] == 13
    assert repository.due_planned_work[0]["status"] == "pending"


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


async def test_scheduler_worker_external_maintenance_tick_runs_when_execution_mode_is_externalized() -> None:
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
        execution_mode="externalized",
        proactive_enabled=True,
    )

    summary = await scheduler.run_external_maintenance_tick_once(reason="external_maintenance")

    assert summary == {
        "executed": True,
        "reason": "external_scheduler_owner",
        "trigger": "external_maintenance",
        "entrypoint_owner": "external_scheduler",
        "idempotency_baseline": "single_tick_summary_per_invocation",
        "pending": 2,
        "processing": 0,
        "retryable_failed": 1,
        "exhausted_failed": 0,
        "stuck_processing": 0,
        "due_planned_work": 0,
        "proposal_handoffs_created": 0,
        "foreground_events_emitted": 0,
        "foreground_delivery_successes": 0,
        "foreground_delivery_blocked": 0,
        "foreground_failures": 0,
        "delivery_delayed": 0,
        "delivery_skipped": 0,
        "recurrence_advanced": 0,
    }
    assert repository.stats_calls == [
        {
            "max_attempts": 3,
            "stuck_after_seconds": 180,
            "retry_backoff_seconds": (5, 30, 120),
        }
    ]
    assert repository.cadence_evidence_writes[-1]["cadence_kind"] == "maintenance"
    assert repository.cadence_evidence_writes[-1]["execution_owner"] == "external_scheduler"
    assert repository.cadence_evidence_writes[-1]["execution_mode"] == "externalized"
    assert repository.cadence_evidence_writes[-1]["summary"]["reason"] == "external_scheduler_owner"


async def test_scheduler_worker_external_proactive_tick_runs_when_execution_mode_is_externalized() -> None:
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
        execution_mode="externalized",
        proactive_enabled=True,
        proactive_interval_seconds=1800,
    )
    scheduler.set_runtime(runtime)

    summary = await scheduler.run_external_proactive_tick_once(reason="external_proactive")

    assert summary == {
        "executed": True,
        "reason": "external_scheduler_owner",
        "trigger": "external_proactive",
        "entrypoint_owner": "external_scheduler",
        "idempotency_baseline": "single_tick_candidate_evaluation_per_invocation",
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
            "planned_work_due": None,
        }
    ]
    assert repository.cadence_evidence_writes[-1]["cadence_kind"] == "proactive"
    assert repository.cadence_evidence_writes[-1]["execution_owner"] == "external_scheduler"
    assert repository.cadence_evidence_writes[-1]["execution_mode"] == "externalized"
    assert repository.cadence_evidence_writes[-1]["summary"]["reason"] == "external_scheduler_owner"


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
            "planned_work_due": None,
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
