import asyncio
from collections.abc import Sequence

from app.core.logging import get_logger
from app.memory.repository import MemoryRepository


class ReflectionWorker:
    def __init__(self, memory_repository: MemoryRepository, queue_size: int = 100):
        self.memory_repository = memory_repository
        self.queue: asyncio.Queue[dict | None] = asyncio.Queue(maxsize=queue_size)
        self._task: asyncio.Task | None = None
        self.logger = get_logger("aion.reflection")

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._run_loop(), name="aion-reflection-worker")

    async def stop(self) -> None:
        if not self._task:
            return
        await self.queue.put(None)
        await self._task
        self._task = None

    def enqueue(self, user_id: str, event_id: str) -> bool:
        payload = {"user_id": user_id, "event_id": event_id}
        try:
            self.queue.put_nowait(payload)
        except asyncio.QueueFull:
            self.logger.warning("reflection_queue_full user_id=%s event_id=%s", user_id, event_id)
            return False
        return True

    async def reflect_user(self, user_id: str, event_id: str) -> bool:
        recent_memory = await self.memory_repository.get_recent_for_user(user_id=user_id, limit=8)
        conclusions = self._derive_conclusions(recent_memory)
        if not conclusions:
            self.logger.info("reflection_noop user_id=%s event_id=%s", user_id, event_id)
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
        return True

    async def _run_loop(self) -> None:
        while True:
            item = await self.queue.get()
            if item is None:
                self.queue.task_done()
                break

            try:
                await self.reflect_user(user_id=str(item["user_id"]), event_id=str(item["event_id"]))
            except Exception as exc:  # pragma: no cover - defensive worker path
                self.logger.exception("reflection_failed user_id=%s event_id=%s error=%s", item["user_id"], item["event_id"], exc)
            finally:
                self.queue.task_done()

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
