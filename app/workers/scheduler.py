from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.logging import get_logger
from app.core.events import build_scheduler_event
from app.core.proactive_policy import proactive_runtime_policy_snapshot
from app.core.scheduler_contracts import (
    SCHEDULER_MAINTENANCE_TICK,
    SCHEDULER_PROACTIVE_TICK,
    SCHEDULER_REFLECTION_TICK,
    clamp_scheduler_interval_seconds,
    normalize_reflection_runtime_mode,
    normalize_scheduler_execution_mode,
    reflection_topology_handoff_posture,
    reflection_scheduler_dispatch_decision,
    scheduler_cadence_dispatch_decision,
    scheduler_cadence_execution_snapshot,
)
from app.memory.repository import MemoryRepository
from app.reflection.worker import ReflectionWorker


class SchedulerWorker:
    """In-process scheduler for reflection and maintenance cadences."""

    MIN_SLEEP_SECONDS = 0.2
    MAX_SLEEP_SECONDS = 2.0

    def __init__(
        self,
        *,
        memory_repository: MemoryRepository,
        reflection_worker: ReflectionWorker,
        enabled: bool,
        reflection_runtime_mode: str,
        reflection_interval_seconds: int,
        maintenance_interval_seconds: int,
        execution_mode: str = "in_process",
        proactive_enabled: bool = False,
        proactive_interval_seconds: int = 1800,
        reflection_batch_limit: int = 10,
    ) -> None:
        self.memory_repository = memory_repository
        self.reflection_worker = reflection_worker
        self.configured_enabled = bool(enabled)
        self.execution_mode = normalize_scheduler_execution_mode(execution_mode)
        self.enabled = self.configured_enabled and self.execution_mode == "in_process"
        self.reflection_runtime_mode = normalize_reflection_runtime_mode(reflection_runtime_mode)
        self.reflection_interval_seconds = clamp_scheduler_interval_seconds(
            subsource=SCHEDULER_REFLECTION_TICK,
            interval_seconds=int(reflection_interval_seconds),
        )
        self.maintenance_interval_seconds = clamp_scheduler_interval_seconds(
            subsource=SCHEDULER_MAINTENANCE_TICK,
            interval_seconds=int(maintenance_interval_seconds),
        )
        self.proactive_enabled = bool(proactive_enabled)
        self.proactive_interval_seconds = clamp_scheduler_interval_seconds(
            subsource=SCHEDULER_PROACTIVE_TICK,
            interval_seconds=int(proactive_interval_seconds),
        )
        self.reflection_batch_limit = max(1, int(reflection_batch_limit))
        self.runtime = None

        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()
        self._next_reflection_due_at: datetime | None = None
        self._next_maintenance_due_at: datetime | None = None
        self._next_proactive_due_at: datetime | None = None
        self._last_reflection_tick_at: datetime | None = None
        self._last_maintenance_tick_at: datetime | None = None
        self._last_proactive_tick_at: datetime | None = None
        self._last_reflection_summary: dict[str, Any] | None = None
        self._last_maintenance_summary: dict[str, Any] | None = None
        self._last_proactive_summary: dict[str, Any] | None = None
        self.logger = get_logger("aion.scheduler")

    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    def set_runtime(self, runtime: Any) -> None:
        self.runtime = runtime

    async def start(self) -> None:
        if not self.enabled or self.is_running():
            return

        now = self._utcnow()
        self._next_reflection_due_at = now
        self._next_maintenance_due_at = now
        self._next_proactive_due_at = now
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._run_loop(), name="aion-scheduler-worker")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._stop_event.set()
        await self._task
        self._task = None

    async def run_reflection_tick_once(self, *, reason: str = "cadence") -> dict[str, Any]:
        now = self._utcnow()
        reflection_topology = reflection_topology_handoff_posture(
            runtime_mode=self.reflection_runtime_mode,
            worker_running=self.reflection_worker.is_running(),
        )
        should_dispatch = bool(reflection_topology["scheduler_tick_dispatch"])
        dispatch_reason = str(reflection_topology["scheduler_tick_reason"])
        if should_dispatch:
            drain_summary = await self.reflection_worker.run_pending_once(limit=self.reflection_batch_limit)
            summary = {
                "executed": True,
                "reason": dispatch_reason,
                "trigger": reason,
                **drain_summary,
            }
        else:
            summary = {
                "executed": False,
                "reason": dispatch_reason,
                "trigger": reason,
                "scanned": 0,
                "processed": 0,
                "completed": 0,
                "failed": 0,
                "skipped_not_ready": 0,
            }
        self._last_reflection_tick_at = now
        self._last_reflection_summary = summary
        self.logger.info(
            "scheduler_reflection_tick executed=%s reason=%s trigger=%s runtime_mode=%s queue_drain_owner=%s external_driver_expected=%s retry_owner=%s processed=%s completed=%s failed=%s",
            summary["executed"],
            summary["reason"],
            summary["trigger"],
            reflection_topology["runtime_mode"],
            reflection_topology["queue_drain_owner"],
            reflection_topology["external_driver_expected"],
            reflection_topology["retry_owner"],
            summary["processed"],
            summary["completed"],
            summary["failed"],
        )
        return summary

    async def run_maintenance_tick_once(self, *, reason: str = "cadence") -> dict[str, Any]:
        now = self._utcnow()
        should_dispatch, dispatch_reason = scheduler_cadence_dispatch_decision(
            execution_mode=self.execution_mode,
            cadence_kind=SCHEDULER_MAINTENANCE_TICK,
            proactive_enabled=self.proactive_enabled,
        )
        if not should_dispatch:
            summary = {
                "executed": False,
                "reason": dispatch_reason,
                "trigger": reason,
                "pending": 0,
                "processing": 0,
                "retryable_failed": 0,
                "exhausted_failed": 0,
                "stuck_processing": 0,
            }
            self._last_maintenance_tick_at = now
            self._last_maintenance_summary = summary
            self.logger.info(
                "scheduler_maintenance_tick executed=%s reason=%s trigger=%s execution_mode=%s maintenance_owner=%s proactive_owner=%s",
                summary["executed"],
                summary["reason"],
                summary["trigger"],
                self.execution_mode,
                "external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler",
                "external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler",
            )
            return summary

        reflection_snapshot = self.reflection_worker.snapshot()
        reflection_stats = await self.memory_repository.get_reflection_task_stats(
            max_attempts=int(reflection_snapshot["max_attempts"]),
            stuck_after_seconds=int(reflection_snapshot["stuck_processing_seconds"]),
            retry_backoff_seconds=tuple(int(value) for value in reflection_snapshot["retry_backoff_seconds"]),  # type: ignore[arg-type]
        )
        summary = {
            "executed": True,
            "reason": dispatch_reason,
            "trigger": reason,
            "pending": int(reflection_stats["pending"]),
            "processing": int(reflection_stats["processing"]),
            "retryable_failed": int(reflection_stats["retryable_failed"]),
            "exhausted_failed": int(reflection_stats["exhausted_failed"]),
            "stuck_processing": int(reflection_stats["stuck_processing"]),
        }
        self._last_maintenance_tick_at = now
        self._last_maintenance_summary = summary
        log_level = self.logger.warning if summary["stuck_processing"] > 0 or summary["exhausted_failed"] > 0 else self.logger.info
        log_level(
            "scheduler_maintenance_tick executed=%s reason=%s trigger=%s pending=%s processing=%s retryable_failed=%s exhausted_failed=%s stuck_processing=%s maintenance_owner=%s proactive_owner=%s",
            summary["executed"],
            summary["reason"],
            summary["trigger"],
            summary["pending"],
            summary["processing"],
            summary["retryable_failed"],
            summary["exhausted_failed"],
            summary["stuck_processing"],
            "external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler",
            "external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler",
        )
        return summary

    async def run_proactive_tick_once(self, *, reason: str = "cadence") -> dict[str, Any]:
        now = self._utcnow()
        should_dispatch, dispatch_reason = scheduler_cadence_dispatch_decision(
            execution_mode=self.execution_mode,
            cadence_kind=SCHEDULER_PROACTIVE_TICK,
            proactive_enabled=self.proactive_enabled,
        )
        if not should_dispatch:
            summary = {
                "executed": False,
                "reason": dispatch_reason,
                "trigger": reason,
                "candidates_considered": 0,
                "events_emitted": 0,
                "messages_delivered": 0,
                "delivery_blocked": 0,
                "failures": 0,
            }
            self._last_proactive_tick_at = now
            self._last_proactive_summary = summary
            self.logger.info(
                "scheduler_proactive_tick executed=%s reason=%s trigger=%s execution_mode=%s proactive_owner=%s candidates_considered=%s events_emitted=%s delivered=%s blocked=%s failures=%s",
                summary["executed"],
                summary["reason"],
                summary["trigger"],
                self.execution_mode,
                "external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler",
                summary["candidates_considered"],
                summary["events_emitted"],
                summary["messages_delivered"],
                summary["delivery_blocked"],
                summary["failures"],
            )
            return summary

        if self.runtime is None or not hasattr(self.runtime, "run"):
            summary = {
                "executed": False,
                "reason": "runtime_unavailable",
                "trigger": reason,
                "candidates_considered": 0,
                "events_emitted": 0,
                "messages_delivered": 0,
                "delivery_blocked": 0,
                "failures": 0,
            }
            self._last_proactive_tick_at = now
            self._last_proactive_summary = summary
            self.logger.warning(
                "scheduler_proactive_tick executed=%s reason=%s trigger=%s execution_mode=%s proactive_owner=%s candidates_considered=%s events_emitted=%s delivered=%s blocked=%s failures=%s",
                summary["executed"],
                summary["reason"],
                summary["trigger"],
                self.execution_mode,
                "external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler",
                summary["candidates_considered"],
                summary["events_emitted"],
                summary["messages_delivered"],
                summary["delivery_blocked"],
                summary["failures"],
            )
            return summary

        candidates = []
        if hasattr(self.memory_repository, "get_proactive_scheduler_candidates"):
            candidates = await self.memory_repository.get_proactive_scheduler_candidates(
                proactive_interval_seconds=self.proactive_interval_seconds,
                limit=5,
            )

        messages_delivered = 0
        delivery_blocked = 0
        failures = 0
        events_emitted = 0
        for candidate in candidates:
            proactive_event = build_scheduler_event(
                subsource=SCHEDULER_PROACTIVE_TICK,
                user_id=str(candidate["user_id"]),
                payload={
                    "text": str(candidate["text"]),
                    "chat_id": candidate["chat_id"],
                    "proactive_trigger": str(candidate["trigger"]),
                    "user_context": {
                        "quiet_hours": False,
                        "focus_mode": False,
                        "recent_user_activity": str(candidate["recent_user_activity"]),
                        "recent_outbound_count": int(candidate["recent_outbound_count"]),
                        "unanswered_proactive_count": int(candidate["unanswered_proactive_count"]),
                    },
                },
            )
            try:
                result = await self.runtime.run(proactive_event)
            except Exception:
                failures += 1
                continue
            events_emitted += 1
            if result.action_result.status == "success" and "send_telegram_message" in result.action_result.actions:
                messages_delivered += 1
            elif result.action_result.status in {"noop", "partial"}:
                delivery_blocked += 1
            elif result.action_result.status == "fail":
                failures += 1

        summary = {
            "executed": True,
            "reason": dispatch_reason,
            "trigger": reason,
            "candidates_considered": len(candidates),
            "events_emitted": events_emitted,
            "messages_delivered": messages_delivered,
            "delivery_blocked": delivery_blocked,
            "failures": failures,
        }
        self._last_proactive_tick_at = now
        self._last_proactive_summary = summary
        log_method = self.logger.warning if failures > 0 else self.logger.info
        log_method(
            "scheduler_proactive_tick executed=%s reason=%s trigger=%s execution_mode=%s proactive_owner=%s candidates_considered=%s events_emitted=%s delivered=%s blocked=%s failures=%s",
            summary["executed"],
            summary["reason"],
            summary["trigger"],
            self.execution_mode,
            "external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler",
            summary["candidates_considered"],
            summary["events_emitted"],
            summary["messages_delivered"],
            summary["delivery_blocked"],
            summary["failures"],
        )
        return summary

    def snapshot(self) -> dict[str, Any]:
        running = self.is_running()
        cadence_execution = scheduler_cadence_execution_snapshot(
            execution_mode=self.execution_mode,
            scheduler_enabled=self.enabled,
            scheduler_running=running,
            proactive_enabled=self.proactive_enabled,
        )
        proactive_policy = proactive_runtime_policy_snapshot(
            proactive_enabled=self.proactive_enabled,
            proactive_interval_seconds=self.proactive_interval_seconds,
            scheduler_execution_mode=self.execution_mode,
            scheduler_ready=bool(cadence_execution["ready"]),
            scheduler_running=running,
        )
        return {
            "execution_mode": self.execution_mode,
            "configured_enabled": self.configured_enabled,
            "enabled": self.enabled,
            "running": running,
            "proactive_enabled": self.proactive_enabled,
            "maintenance_cadence_owner": cadence_execution["maintenance_cadence_owner"],
            "proactive_cadence_owner": cadence_execution["proactive_cadence_owner"],
            "cadence_execution": cadence_execution,
            "reflection_runtime_mode": self.reflection_runtime_mode,
            "reflection_interval_seconds": self.reflection_interval_seconds,
            "maintenance_interval_seconds": self.maintenance_interval_seconds,
            "proactive_interval_seconds": self.proactive_interval_seconds,
            "reflection_batch_limit": self.reflection_batch_limit,
            "next_reflection_due_at": self._format_timestamp(self._next_reflection_due_at),
            "next_maintenance_due_at": self._format_timestamp(self._next_maintenance_due_at),
            "next_proactive_due_at": self._format_timestamp(self._next_proactive_due_at),
            "last_reflection_tick_at": self._format_timestamp(self._last_reflection_tick_at),
            "last_maintenance_tick_at": self._format_timestamp(self._last_maintenance_tick_at),
            "last_proactive_tick_at": self._format_timestamp(self._last_proactive_tick_at),
            "last_reflection_summary": dict(self._last_reflection_summary or {}),
            "last_maintenance_summary": dict(self._last_maintenance_summary or {}),
            "last_proactive_summary": dict(self._last_proactive_summary or {}),
            "proactive_policy": proactive_policy,
        }

    async def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            now = self._utcnow()
            if self._next_reflection_due_at is None:
                self._next_reflection_due_at = now
            if self._next_maintenance_due_at is None:
                self._next_maintenance_due_at = now
            if self._next_proactive_due_at is None:
                self._next_proactive_due_at = now

            if now >= self._next_reflection_due_at:
                await self.run_reflection_tick_once(reason="scheduled_reflection_tick")
                self._next_reflection_due_at = now + timedelta(seconds=self.reflection_interval_seconds)

            if now >= self._next_maintenance_due_at:
                await self.run_maintenance_tick_once(reason="scheduled_maintenance_tick")
                self._next_maintenance_due_at = now + timedelta(seconds=self.maintenance_interval_seconds)

            if now >= self._next_proactive_due_at:
                await self.run_proactive_tick_once(reason="scheduled_proactive_tick")
                self._next_proactive_due_at = now + timedelta(seconds=self.proactive_interval_seconds)

            sleep_seconds = self._sleep_duration_seconds(now)
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=sleep_seconds)
            except TimeoutError:
                continue

    def _should_dispatch_reflection(self) -> tuple[bool, str]:
        return reflection_scheduler_dispatch_decision(
            runtime_mode=self.reflection_runtime_mode,
            worker_running=self.reflection_worker.is_running(),
        )

    def _sleep_duration_seconds(self, now: datetime) -> float:
        due_times = [
            value
            for value in [self._next_reflection_due_at, self._next_maintenance_due_at, self._next_proactive_due_at]
            if value is not None
        ]
        if not due_times:
            return self.MAX_SLEEP_SECONDS
        next_due = min(due_times)
        seconds = max(0.0, (next_due - now).total_seconds())
        return min(self.MAX_SLEEP_SECONDS, max(self.MIN_SLEEP_SECONDS, seconds))

    def _format_timestamp(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.astimezone(timezone.utc).isoformat()

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)
