import asyncio
from datetime import datetime, timedelta, timezone
from collections.abc import Sequence

from app.core.logging import get_logger
from app.memory.repository import MemoryRepository


class ReflectionWorker:
    RETRY_BACKOFF_SECONDS = (5, 30, 120)
    STUCK_PROCESSING_SECONDS = 180

    def __init__(
        self,
        memory_repository: MemoryRepository,
        queue_size: int = 100,
        max_attempts: int = 3,
    ):
        self.memory_repository = memory_repository
        self.queue: asyncio.Queue[dict | None] = asyncio.Queue(maxsize=queue_size)
        self._task: asyncio.Task | None = None
        self._queued_task_ids: set[int] = set()
        self.max_attempts = max_attempts
        self.logger = get_logger("aion.reflection")

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        await self._schedule_pending_tasks(limit=self.queue.maxsize or 100)
        self._task = asyncio.create_task(self._run_loop(), name="aion-reflection-worker")

    async def stop(self) -> None:
        if not self._task:
            return
        await self.queue.put(None)
        await self._task
        self._task = None

    async def enqueue(self, user_id: str, event_id: str) -> bool:
        task = await self.memory_repository.enqueue_reflection_task(user_id=user_id, event_id=event_id)
        if str(task.get("status")) == "completed":
            return True
        queued = self._schedule_task(task)
        if not queued:
            self.logger.warning(
                "reflection_queue_full task_id=%s user_id=%s event_id=%s",
                task["id"],
                user_id,
                event_id,
            )
        return True

    async def reflect_user(self, user_id: str, event_id: str) -> bool:
        recent_memory = await self.memory_repository.get_recent_for_user(user_id=user_id, limit=8)
        conclusions = self._derive_conclusions(recent_memory)
        theta = self._derive_theta(recent_memory)
        if not conclusions:
            self.logger.info("reflection_noop user_id=%s event_id=%s", user_id, event_id)
            if theta is None:
                return False

        for conclusion in conclusions:
            await self.memory_repository.upsert_conclusion(
                user_id=user_id,
                kind=conclusion["kind"],
                content=conclusion["content"],
                confidence=conclusion["confidence"],
                source=conclusion["source"],
                supporting_event_id=event_id,
            )
            self.logger.info(
                "reflection_conclusion_updated user_id=%s event_id=%s kind=%s content=%s confidence=%.2f source=%s",
                user_id,
                event_id,
                conclusion["kind"],
                conclusion["content"],
                conclusion["confidence"],
                conclusion["source"],
            )
        if theta is not None:
            await self.memory_repository.upsert_theta(
                user_id=user_id,
                support_bias=theta["support_bias"],
                analysis_bias=theta["analysis_bias"],
                execution_bias=theta["execution_bias"],
            )
            self.logger.info(
                "reflection_theta_updated user_id=%s event_id=%s support=%.2f analysis=%.2f execution=%.2f",
                user_id,
                event_id,
                theta["support_bias"],
                theta["analysis_bias"],
                theta["execution_bias"],
            )
        return True

    async def _run_loop(self) -> None:
        while True:
            item = await self.queue.get()
            if item is None:
                self.queue.task_done()
                break

            task_id = int(item["id"])
            self._queued_task_ids.discard(task_id)
            completed = False
            try:
                await self.memory_repository.mark_reflection_task_processing(task_id=task_id)
                await self.reflect_user(user_id=str(item["user_id"]), event_id=str(item["event_id"]))
                completed = True
            except Exception as exc:  # pragma: no cover - defensive worker path
                await self.memory_repository.mark_reflection_task_failed(task_id=task_id, error=str(exc))
                self.logger.exception("reflection_failed user_id=%s event_id=%s error=%s", item["user_id"], item["event_id"], exc)
            finally:
                if completed:
                    await self.memory_repository.mark_reflection_task_completed(task_id=task_id)
                self.queue.task_done()
                await self._schedule_pending_tasks(limit=1)

    async def _schedule_pending_tasks(self, limit: int = 10) -> int:
        capacity = self._queue_capacity()
        if capacity <= 0:
            return 0

        pending_tasks = await self.memory_repository.get_pending_reflection_tasks(limit=max(limit, capacity))
        scheduled = 0
        for task in pending_tasks:
            if self._is_task_ready(task) and self._schedule_task(task):
                scheduled += 1
            if self._queue_capacity() <= 0:
                break
        return scheduled

    def _schedule_task(self, task: dict) -> bool:
        task_id = int(task["id"])
        if task_id in self._queued_task_ids:
            return False

        try:
            self.queue.put_nowait(task)
        except asyncio.QueueFull:
            return False

        self._queued_task_ids.add(task_id)
        return True

    def _queue_capacity(self) -> int:
        if self.queue.maxsize <= 0:
            return 100
        return max(0, self.queue.maxsize - self.queue.qsize())

    def snapshot(self) -> dict[str, int | bool | list[int]]:
        running = self._task is not None and not self._task.done()
        return {
            "running": running,
            "queue_size": self.queue.qsize(),
            "queue_capacity": self._queue_capacity(),
            "queued_task_count": len(self._queued_task_ids),
            "queued_task_ids": sorted(self._queued_task_ids),
            "max_attempts": self.max_attempts,
            "retry_backoff_seconds": list(self.RETRY_BACKOFF_SECONDS),
            "stuck_processing_seconds": self.STUCK_PROCESSING_SECONDS,
        }

    def _is_task_ready(self, task: dict) -> bool:
        status = str(task.get("status", "pending"))
        attempts = int(task.get("attempts", 0) or 0)

        if status in {"pending", "processing"}:
            return attempts < self.max_attempts

        if status != "failed" or attempts >= self.max_attempts:
            return False

        updated_at = task.get("updated_at")
        if not isinstance(updated_at, datetime):
            return True

        retry_after = updated_at + timedelta(seconds=self._retry_backoff_seconds(attempts))
        return retry_after <= datetime.now(timezone.utc)

    def _retry_backoff_seconds(self, attempts: int) -> int:
        if attempts <= 0:
            return 0
        index = min(attempts - 1, len(self.RETRY_BACKOFF_SECONDS) - 1)
        return self.RETRY_BACKOFF_SECONDS[index]

    def _derive_conclusions(self, recent_memory: Sequence[dict]) -> list[dict]:
        if not recent_memory:
            return []

        explicit_updates: list[str] = []
        structured_count = 0
        concise_count = 0
        sample_size = 0
        role_counts: dict[str, int] = {}

        for memory_item in recent_memory:
            fields = self._extract_fields(str(memory_item.get("summary", "")))
            preference_update = fields.get("preference_update", "")
            if preference_update.startswith("response_style:"):
                explicit_updates.append(preference_update.split(":", 1)[1].strip().lower())

            role = fields.get("role", "").strip().lower()
            if role in {"friend", "analyst", "executor", "mentor"}:
                role_counts[role] = role_counts.get(role, 0) + 1

            expression = fields.get("expression", "")
            action_status = fields.get("action", "")
            if not expression or action_status != "success":
                continue

            sample_size += 1
            normalized_expression = " ".join(expression.split())
            if self._looks_structured(normalized_expression):
                structured_count += 1
            if len(normalized_expression) <= 140:
                concise_count += 1

        conclusions: list[dict] = []
        if explicit_updates:
            latest = explicit_updates[0]
            if latest in {"concise", "structured"}:
                conclusions.append(
                    {
                        "kind": "response_style",
                        "content": latest,
                        "confidence": 0.98,
                        "source": "background_reflection",
                    }
                )

        if sample_size >= 3:
            if structured_count >= 3 and structured_count / sample_size >= 0.75:
                conclusions.append(
                    {
                        "kind": "response_style",
                        "content": "structured",
                        "confidence": 0.78,
                        "source": "background_reflection",
                    }
                )

            elif concise_count >= 3 and concise_count / sample_size >= 0.75:
                conclusions.append(
                    {
                        "kind": "response_style",
                        "content": "concise",
                        "confidence": 0.74,
                        "source": "background_reflection",
                    }
                )

        preferred_role = self._derive_preferred_role(role_counts=role_counts, total=len(recent_memory))
        if preferred_role is not None:
            conclusions.append(preferred_role)

        deduped: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for conclusion in conclusions:
            key = (str(conclusion["kind"]), str(conclusion["content"]))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(conclusion)
        return deduped

    def _derive_preferred_role(self, role_counts: dict[str, int], total: int) -> dict | None:
        if total < 4 or not role_counts:
            return None

        preferred_role, count = max(role_counts.items(), key=lambda item: item[1])
        if count < 3:
            return None
        if count / total < 0.6:
            return None

        return {
            "kind": "preferred_role",
            "content": preferred_role,
            "confidence": 0.76,
            "source": "background_reflection",
        }

    def _derive_theta(self, recent_memory: Sequence[dict]) -> dict | None:
        if len(recent_memory) < 3:
            return None

        role_map = {
            "friend": "support_bias",
            "analyst": "analysis_bias",
            "executor": "execution_bias",
        }
        totals = {
            "support_bias": 0,
            "analysis_bias": 0,
            "execution_bias": 0,
        }
        counted = 0

        for memory_item in recent_memory:
            fields = self._extract_fields(str(memory_item.get("summary", "")))
            role = fields.get("role", "").strip().lower()
            key = role_map.get(role)
            if key is None:
                continue
            totals[key] += 1
            counted += 1

        if counted < 3:
            return None

        return {
            "support_bias": round(totals["support_bias"] / counted, 2),
            "analysis_bias": round(totals["analysis_bias"] / counted, 2),
            "execution_bias": round(totals["execution_bias"] / counted, 2),
        }

    def _extract_fields(self, raw_summary: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for part in " ".join(raw_summary.split()).split(";"):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            fields[key.strip()] = value.strip()
        return fields

    def _looks_structured(self, expression: str) -> bool:
        return expression.startswith("- ") or "\n1." in expression or "### " in expression
