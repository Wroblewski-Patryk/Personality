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

    async def _record_cadence_evidence(
        self,
        *,
        cadence_kind: str,
        execution_owner: str,
        summary: dict[str, Any],
        now: datetime,
    ) -> None:
        recorder = getattr(self.memory_repository, "upsert_scheduler_cadence_evidence", None)
        if not callable(recorder):
            return
        await recorder(
            cadence_kind=cadence_kind,
            execution_owner=execution_owner,
            execution_mode=self.execution_mode,
            summary=summary,
            last_run_at=now,
        )

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
            await self._record_cadence_evidence(
                cadence_kind="maintenance",
                execution_owner="external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler",
                summary=summary,
                now=now,
            )
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
        due_summary = await self._handoff_due_planned_work(now=now)
        summary["due_planned_work"] = int(due_summary["due_planned_work"])
        summary["proposal_handoffs_created"] = int(due_summary["proposal_handoffs_created"])
        summary["delivery_delayed"] = int(due_summary["delivery_delayed"])
        summary["delivery_skipped"] = int(due_summary["delivery_skipped"])
        summary["recurrence_advanced"] = int(due_summary["recurrence_advanced"])
        foreground_summary = await self._dispatch_due_planned_work_foreground(
            items=list(due_summary["items"]),
            reason=reason,
            now=now,
        )
        summary["foreground_events_emitted"] = int(foreground_summary["events_emitted"])
        summary["foreground_delivery_successes"] = int(foreground_summary["delivery_successes"])
        summary["foreground_delivery_blocked"] = int(foreground_summary["delivery_blocked"])
        summary["foreground_failures"] = int(foreground_summary["failures"])
        summary["recurrence_advanced"] += int(foreground_summary["recurrence_advanced"])
        self._last_maintenance_tick_at = now
        self._last_maintenance_summary = summary
        await self._record_cadence_evidence(
            cadence_kind="maintenance",
            execution_owner="in_process_scheduler",
            summary=summary,
            now=now,
        )
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

    async def run_external_maintenance_tick_once(
        self,
        *,
        reason: str = "external_scheduler_tick",
    ) -> dict[str, Any]:
        now = self._utcnow()
        if self.execution_mode != "externalized":
            summary = {
                "executed": False,
                "reason": "external_owner_not_selected",
                "trigger": reason,
                "pending": 0,
                "processing": 0,
                "retryable_failed": 0,
                "exhausted_failed": 0,
                "stuck_processing": 0,
            }
            self._last_maintenance_tick_at = now
            self._last_maintenance_summary = summary
            await self._record_cadence_evidence(
                cadence_kind="maintenance",
                execution_owner="in_process_scheduler",
                summary=summary,
                now=now,
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
            "reason": "external_scheduler_owner",
            "trigger": reason,
            "entrypoint_owner": "external_scheduler",
            "idempotency_baseline": "single_tick_summary_per_invocation",
            "pending": int(reflection_stats["pending"]),
            "processing": int(reflection_stats["processing"]),
            "retryable_failed": int(reflection_stats["retryable_failed"]),
            "exhausted_failed": int(reflection_stats["exhausted_failed"]),
            "stuck_processing": int(reflection_stats["stuck_processing"]),
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
        due_summary = await self._handoff_due_planned_work(now=now)
        summary["due_planned_work"] = int(due_summary["due_planned_work"])
        summary["proposal_handoffs_created"] = int(due_summary["proposal_handoffs_created"])
        summary["delivery_delayed"] = int(due_summary["delivery_delayed"])
        summary["delivery_skipped"] = int(due_summary["delivery_skipped"])
        summary["recurrence_advanced"] = int(due_summary["recurrence_advanced"])
        foreground_summary = await self._dispatch_due_planned_work_foreground(
            items=list(due_summary["items"]),
            reason=reason,
            now=now,
        )
        summary["foreground_events_emitted"] = int(foreground_summary["events_emitted"])
        summary["foreground_delivery_successes"] = int(foreground_summary["delivery_successes"])
        summary["foreground_delivery_blocked"] = int(foreground_summary["delivery_blocked"])
        summary["foreground_failures"] = int(foreground_summary["failures"])
        summary["recurrence_advanced"] += int(foreground_summary["recurrence_advanced"])
        self._last_maintenance_tick_at = now
        self._last_maintenance_summary = summary
        await self._record_cadence_evidence(
            cadence_kind="maintenance",
            execution_owner="external_scheduler",
            summary=summary,
            now=now,
        )
        return summary

    async def _handoff_due_planned_work(self, *, now: datetime) -> dict[str, Any]:
        if not hasattr(self.memory_repository, "get_due_planned_work"):
            return {
                "due_planned_work": 0,
                "proposal_handoffs_created": 0,
                "delivery_delayed": 0,
                "delivery_skipped": 0,
                "recurrence_advanced": 0,
                "items": [],
            }

        due_items = await self.memory_repository.get_due_planned_work(now=now, limit=8)
        proposal_handoffs_created = 0
        delivery_delayed = 0
        delivery_skipped = 0
        recurrence_advanced = 0
        handoff_items: list[dict] = []
        for item in due_items:
            if self._planned_work_expired(item=item, now=now):
                if await self._advance_or_cancel_due_item(item=item, now=now):
                    recurrence_advanced += 1
                else:
                    delivery_skipped += 1
                continue
            quiet_hours_decision = await self._apply_quiet_hours_policy(item=item, now=now)
            if quiet_hours_decision == "delayed":
                delivery_delayed += 1
                continue
            if quiet_hours_decision == "skipped":
                if str(item.get("recurrence_mode", "none")).strip().lower() != "none":
                    recurrence_advanced += 1
                else:
                    delivery_skipped += 1
                continue
            if hasattr(self.memory_repository, "upsert_subconscious_proposal"):
                await self.memory_repository.upsert_subconscious_proposal(
                    user_id=str(item.get("user_id", "")),
                    proposal_type="nudge_user",
                    summary=f"planned_work_due:{int(item['id'])}:{str(item.get('summary', ''))}",
                    payload={
                        "handoff_kind": "planned_work_due",
                        "work_id": int(item["id"]),
                        "work_kind": str(item.get("kind", "follow_up")),
                        "summary": str(item.get("summary", "")),
                        "delivery_channel": str(item.get("delivery_channel", "none")),
                        "preferred_at": item.get("preferred_at"),
                        "source_event_id": item.get("source_event_id"),
                    },
                    confidence=0.82,
                    source_event_id=str(item.get("source_event_id", "") or "") or None,
                )
                proposal_handoffs_created += 1
            if hasattr(self.memory_repository, "mark_planned_work_due"):
                await self.memory_repository.mark_planned_work_due(
                    work_id=int(item["id"]),
                    evaluated_at=now,
                )
            handoff_items.append(item)

        return {
            "due_planned_work": len(handoff_items),
            "proposal_handoffs_created": proposal_handoffs_created,
            "delivery_delayed": delivery_delayed,
            "delivery_skipped": delivery_skipped,
            "recurrence_advanced": recurrence_advanced,
            "items": handoff_items,
        }

    async def _dispatch_due_planned_work_foreground(self, *, items: list[dict], reason: str, now: datetime) -> dict[str, int]:
        if self.runtime is None or not hasattr(self.runtime, "run"):
            return {
                "events_emitted": 0,
                "delivery_successes": 0,
                "delivery_blocked": 0,
                "failures": 0,
                "recurrence_advanced": 0,
            }

        events_emitted = 0
        delivery_successes = 0
        delivery_blocked = 0
        failures = 0
        recurrence_advanced = 0

        for item in items:
            if not bool(item.get("requires_foreground_execution", True)):
                continue
            delivery_channel = str(item.get("delivery_channel", "none")).strip().lower()
            chat_id = self._foreground_delivery_chat_id(item) if delivery_channel == "telegram" else None
            event = build_scheduler_event(
                subsource=SCHEDULER_MAINTENANCE_TICK,
                user_id=str(item.get("user_id", "")),
                payload={
                    "text": f"planned work due: {str(item.get('summary', ''))}",
                    "chat_id": chat_id,
                    "planned_work_due": {
                        "work_id": int(item["id"]),
                        "summary": str(item.get("summary", "")),
                        "work_kind": str(item.get("kind", "follow_up")),
                        "delivery_channel": delivery_channel,
                        "source_event_id": item.get("source_event_id"),
                    },
                },
            )
            try:
                result = await self.runtime.run(event)
            except Exception:
                failures += 1
                continue
            events_emitted += 1
            if result.action_result.status == "success":
                delivery_successes += 1
                if await self._advance_recurring_item_if_needed(item=item, now=now):
                    recurrence_advanced += 1
            elif result.action_result.status in {"noop", "partial"}:
                delivery_blocked += 1
            else:
                failures += 1

        return {
            "events_emitted": events_emitted,
            "delivery_successes": delivery_successes,
            "delivery_blocked": delivery_blocked,
            "failures": failures,
            "recurrence_advanced": recurrence_advanced,
        }

    async def _apply_quiet_hours_policy(self, *, item: dict, now: datetime) -> str:
        policy = str(item.get("quiet_hours_policy", "respect_user_context")).strip().lower()
        if policy == "deliver_anytime" or not self._is_quiet_hours(now=now):
            return "deliver"
        if policy == "skip_if_quiet_hours":
            await self._advance_or_cancel_due_item(item=item, now=now)
            return "skipped"
        if hasattr(self.memory_repository, "snooze_planned_work_item"):
            await self.memory_repository.snooze_planned_work_item(
                work_id=int(item["id"]),
                until_at=self._next_quiet_hours_release(now=now),
                evaluated_at=now,
            )
            return "delayed"
        return "deliver"

    async def _advance_recurring_item_if_needed(self, *, item: dict, now: datetime) -> bool:
        if str(item.get("recurrence_mode", "none")).strip().lower() == "none":
            return False
        if not hasattr(self.memory_repository, "advance_planned_work_recurrence"):
            return False
        updated = await self.memory_repository.advance_planned_work_recurrence(
            work_id=int(item["id"]),
            evaluated_at=now,
        )
        return updated is not None

    async def _advance_or_cancel_due_item(self, *, item: dict, now: datetime) -> bool:
        if await self._advance_recurring_item_if_needed(item=item, now=now):
            return True
        if hasattr(self.memory_repository, "cancel_planned_work_item"):
            await self.memory_repository.cancel_planned_work_item(work_id=int(item["id"]))
        return False

    def _planned_work_expired(self, *, item: dict, now: datetime) -> bool:
        expires_at = item.get("expires_at")
        if not isinstance(expires_at, datetime):
            return False
        return expires_at <= now

    def _is_quiet_hours(self, *, now: datetime) -> bool:
        hour = now.astimezone(timezone.utc).hour
        return hour >= 22 or hour < 7

    def _next_quiet_hours_release(self, *, now: datetime) -> datetime:
        current = now.astimezone(timezone.utc)
        release = current.replace(hour=7, minute=0, second=0, microsecond=0)
        if current.hour >= 7:
            release += timedelta(days=1)
        return release

    def _foreground_delivery_chat_id(self, item: dict) -> int | str | None:
        raw_chat_id = item.get("chat_id")
        if isinstance(raw_chat_id, (int, str)):
            return raw_chat_id
        user_id = str(item.get("user_id", "")).strip()
        if user_id.lstrip("-").isdigit():
            try:
                return int(user_id)
            except ValueError:
                return user_id
        return None

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
            await self._record_cadence_evidence(
                cadence_kind="proactive",
                execution_owner="external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler",
                summary=summary,
                now=now,
            )
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
            await self._record_cadence_evidence(
                cadence_kind="proactive",
                execution_owner="in_process_scheduler",
                summary=summary,
                now=now,
            )
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
        await self._record_cadence_evidence(
            cadence_kind="proactive",
            execution_owner="in_process_scheduler",
            summary=summary,
            now=now,
        )
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

    async def run_external_proactive_tick_once(
        self,
        *,
        reason: str = "external_scheduler_tick",
    ) -> dict[str, Any]:
        now = self._utcnow()
        if self.execution_mode != "externalized":
            summary = {
                "executed": False,
                "reason": "external_owner_not_selected",
                "trigger": reason,
                "candidates_considered": 0,
                "events_emitted": 0,
                "messages_delivered": 0,
                "delivery_blocked": 0,
                "failures": 0,
            }
            self._last_proactive_tick_at = now
            self._last_proactive_summary = summary
            await self._record_cadence_evidence(
                cadence_kind="proactive",
                execution_owner="in_process_scheduler",
                summary=summary,
                now=now,
            )
            return summary

        if not self.proactive_enabled:
            summary = {
                "executed": False,
                "reason": "proactive_disabled",
                "trigger": reason,
                "candidates_considered": 0,
                "events_emitted": 0,
                "messages_delivered": 0,
                "delivery_blocked": 0,
                "failures": 0,
            }
            self._last_proactive_tick_at = now
            self._last_proactive_summary = summary
            await self._record_cadence_evidence(
                cadence_kind="proactive",
                execution_owner="external_scheduler",
                summary=summary,
                now=now,
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
            await self._record_cadence_evidence(
                cadence_kind="proactive",
                execution_owner="external_scheduler",
                summary=summary,
                now=now,
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
            "reason": "external_scheduler_owner",
            "trigger": reason,
            "entrypoint_owner": "external_scheduler",
            "idempotency_baseline": "single_tick_candidate_evaluation_per_invocation",
            "candidates_considered": len(candidates),
            "events_emitted": events_emitted,
            "messages_delivered": messages_delivered,
            "delivery_blocked": delivery_blocked,
            "failures": failures,
        }
        self._last_proactive_tick_at = now
        self._last_proactive_summary = summary
        await self._record_cadence_evidence(
            cadence_kind="proactive",
            execution_owner="external_scheduler",
            summary=summary,
            now=now,
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
