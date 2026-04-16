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
        runtime_preferences = await self.memory_repository.get_user_runtime_preferences(user_id=user_id)
        active_goals = await self.memory_repository.get_active_goals(user_id=user_id, limit=5)
        active_tasks = await self.memory_repository.get_active_tasks(user_id=user_id, limit=8)
        primary_goal = self._select_primary_goal(active_goals)
        recent_goal_progress = []
        recent_goal_milestone_history = []
        if primary_goal is not None and primary_goal.get("id") is not None:
            recent_goal_progress = await self.memory_repository.get_recent_goal_progress(
                user_id=user_id,
                goal_ids=[int(primary_goal["id"])],
                limit=4,
            )
            recent_goal_milestone_history = await self.memory_repository.get_recent_goal_milestone_history(
                user_id=user_id,
                goal_ids=[int(primary_goal["id"])],
                limit=5,
            )
        previous_goal_progress_score = self._coerce_progress_score(runtime_preferences.get("goal_progress_score"))
        if recent_goal_progress:
            previous_goal_progress_score = self._coerce_progress_score(recent_goal_progress[0].get("score"))
        conclusions = self._derive_conclusions(
            recent_memory,
            active_goals=active_goals,
            active_tasks=active_tasks,
            previous_goal_progress_score=previous_goal_progress_score,
            recent_goal_progress=recent_goal_progress,
            recent_goal_milestone_history=recent_goal_milestone_history,
        )
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
        synced_milestone: dict | None = None
        if primary_goal is not None and primary_goal.get("id") is not None:
            goal_milestone_state = next(
                (item for item in conclusions if str(item.get("kind")) == "goal_milestone_state"),
                None,
            )
            if goal_milestone_state is not None:
                synced_milestone = await self.memory_repository.sync_goal_milestone(
                    user_id=user_id,
                    goal_id=int(primary_goal["id"]),
                    phase=str(goal_milestone_state["content"]),
                    source_event_id=event_id,
                )
                self.logger.info(
                    "reflection_goal_milestone_synced user_id=%s event_id=%s goal_id=%s phase=%s",
                    user_id,
                    event_id,
                    primary_goal["id"],
                    goal_milestone_state["content"],
                )
        if synced_milestone is not None:
            goal_milestone_risk = next(
                (item for item in conclusions if str(item.get("kind")) == "goal_milestone_risk"),
                None,
            )
            goal_completion_criteria = next(
                (item for item in conclusions if str(item.get("kind")) == "goal_completion_criteria"),
                None,
            )
            await self.memory_repository.append_goal_milestone_history(
                user_id=user_id,
                goal_id=int(synced_milestone["goal_id"]),
                milestone_name=str(synced_milestone["name"]),
                phase=str(synced_milestone["phase"]),
                risk_level=str(goal_milestone_risk["content"]) if goal_milestone_risk is not None else None,
                completion_criteria=(
                    str(goal_completion_criteria["content"]) if goal_completion_criteria is not None else None
                ),
                source_event_id=event_id,
            )
            self.logger.info(
                "reflection_goal_milestone_history_appended user_id=%s event_id=%s goal_id=%s phase=%s risk=%s criteria=%s",
                user_id,
                event_id,
                synced_milestone["goal_id"],
                synced_milestone["phase"],
                goal_milestone_risk["content"] if goal_milestone_risk is not None else "",
                goal_completion_criteria["content"] if goal_completion_criteria is not None else "",
            )
        if primary_goal is not None and primary_goal.get("id") is not None:
            goal_progress_score = next(
                (item for item in conclusions if str(item.get("kind")) == "goal_progress_score"),
                None,
            )
            if goal_progress_score is not None:
                goal_execution_state = next(
                    (item for item in conclusions if str(item.get("kind")) == "goal_execution_state"),
                    None,
                )
                goal_progress_trend = next(
                    (item for item in conclusions if str(item.get("kind")) == "goal_progress_trend"),
                    None,
                )
                await self.memory_repository.append_goal_progress_snapshot(
                    user_id=user_id,
                    goal_id=int(primary_goal["id"]),
                    score=float(goal_progress_score["content"]),
                    execution_state=str(goal_execution_state["content"]) if goal_execution_state is not None else None,
                    progress_trend=str(goal_progress_trend["content"]) if goal_progress_trend is not None else None,
                    source_event_id=event_id,
                )
                self.logger.info(
                    "reflection_goal_progress_snapshot user_id=%s event_id=%s goal_id=%s score=%s state=%s trend=%s",
                    user_id,
                    event_id,
                    primary_goal["id"],
                    goal_progress_score["content"],
                    goal_execution_state["content"] if goal_execution_state is not None else "",
                    goal_progress_trend["content"] if goal_progress_trend is not None else "",
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

    def _derive_conclusions(
        self,
        recent_memory: Sequence[dict],
        *,
        active_goals: Sequence[dict] | None = None,
        active_tasks: Sequence[dict] | None = None,
        previous_goal_progress_score: float | None = None,
        recent_goal_progress: Sequence[dict] | None = None,
        recent_goal_milestone_history: Sequence[dict] | None = None,
    ) -> list[dict]:
        if not recent_memory:
            recent_memory = []

        explicit_updates: list[str] = []
        explicit_collaboration_updates: list[str] = []
        structured_count = 0
        concise_count = 0
        sample_size = 0
        role_counts: dict[str, int] = {}
        task_done_updates = 0
        task_in_progress_updates = 0

        for memory_item in recent_memory:
            fields = self._extract_fields(str(memory_item.get("summary", "")))
            preference_update = fields.get("preference_update", "")
            if preference_update.startswith("response_style:"):
                explicit_updates.append(preference_update.split(":", 1)[1].strip().lower())
            collaboration_update = fields.get("collaboration_update", "").strip().lower()
            if collaboration_update in {"guided", "hands_on"}:
                explicit_collaboration_updates.append(collaboration_update)
            task_status_update = fields.get("task_status_update", "").strip().lower()
            if task_status_update.endswith(":done"):
                task_done_updates += 1
            elif task_status_update.endswith(":in_progress"):
                task_in_progress_updates += 1

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

        if explicit_collaboration_updates:
            latest = explicit_collaboration_updates[0]
            conclusions.append(
                {
                    "kind": "collaboration_preference",
                    "content": latest,
                    "confidence": 0.94,
                    "source": "background_reflection",
                }
            )

        collaboration_preference = self._derive_collaboration_preference(recent_memory)
        if collaboration_preference is not None:
            conclusions.append(collaboration_preference)

        goal_execution_state = self._derive_goal_execution_state(
            recent_memory=recent_memory,
            active_goals=active_goals or [],
            active_tasks=active_tasks or [],
            task_done_updates=task_done_updates,
            task_in_progress_updates=task_in_progress_updates,
        )
        if goal_execution_state is not None:
            conclusions.append(goal_execution_state)
        goal_progress_score = self._derive_goal_progress_score(
            active_goals=active_goals or [],
            active_tasks=active_tasks or [],
            task_done_updates=task_done_updates,
        )
        if goal_progress_score is not None:
            conclusions.append(goal_progress_score)
        goal_progress_trend = self._derive_goal_progress_trend(
            current_goal_progress_score=goal_progress_score,
            previous_goal_progress_score=previous_goal_progress_score,
        )
        if goal_progress_trend is not None:
            conclusions.append(goal_progress_trend)
        goal_progress_arc = self._derive_goal_progress_arc(
            recent_goal_progress=recent_goal_progress or [],
            current_goal_progress_score=goal_progress_score,
            goal_execution_state=goal_execution_state,
            goal_progress_trend=goal_progress_trend,
        )
        if goal_progress_arc is not None:
            conclusions.append(goal_progress_arc)
        goal_milestone_state = self._derive_goal_milestone_state(
            has_active_goal=bool(active_goals),
            current_goal_progress_score=goal_progress_score,
            goal_execution_state=goal_execution_state,
            goal_progress_arc=goal_progress_arc,
        )
        if goal_milestone_state is not None:
            conclusions.append(goal_milestone_state)
        goal_milestone_transition = self._derive_goal_milestone_transition(
            current_goal_progress_score=goal_progress_score,
            previous_goal_progress_score=previous_goal_progress_score,
        )
        if goal_milestone_transition is not None:
            conclusions.append(goal_milestone_transition)
        goal_milestone_arc = self._derive_goal_milestone_arc(
            recent_goal_milestone_history=recent_goal_milestone_history or [],
            goal_milestone_state=goal_milestone_state,
            goal_milestone_transition=goal_milestone_transition,
        )
        if goal_milestone_arc is not None:
            conclusions.append(goal_milestone_arc)
        goal_milestone_pressure = self._derive_goal_milestone_pressure(
            recent_goal_milestone_history=recent_goal_milestone_history or [],
            goal_milestone_state=goal_milestone_state,
            goal_milestone_arc=goal_milestone_arc,
            goal_milestone_transition=goal_milestone_transition,
        )
        if goal_milestone_pressure is not None:
            conclusions.append(goal_milestone_pressure)
        goal_milestone_dependency_state = self._derive_goal_milestone_dependency_state(
            active_tasks=active_tasks or [],
            goal_milestone_state=goal_milestone_state,
            goal_execution_state=goal_execution_state,
        )
        if goal_milestone_dependency_state is not None:
            conclusions.append(goal_milestone_dependency_state)
        goal_milestone_risk = self._derive_goal_milestone_risk(
            active_tasks=active_tasks or [],
            goal_execution_state=goal_execution_state,
            goal_progress_arc=goal_progress_arc,
            goal_milestone_state=goal_milestone_state,
            goal_milestone_transition=goal_milestone_transition,
        )
        if goal_milestone_risk is not None:
            conclusions.append(goal_milestone_risk)
        goal_completion_criteria = self._derive_goal_completion_criteria(
            active_tasks=active_tasks or [],
            goal_execution_state=goal_execution_state,
            goal_milestone_state=goal_milestone_state,
            goal_milestone_risk=goal_milestone_risk,
        )
        if goal_completion_criteria is not None:
            conclusions.append(goal_completion_criteria)
        goal_milestone_due_state = self._derive_goal_milestone_due_state(
            goal_milestone_state=goal_milestone_state,
            goal_milestone_pressure=goal_milestone_pressure,
            goal_milestone_dependency_state=goal_milestone_dependency_state,
            goal_completion_criteria=goal_completion_criteria,
        )
        if goal_milestone_due_state is not None:
            conclusions.append(goal_milestone_due_state)
        goal_milestone_due_window = self._derive_goal_milestone_due_window(
            goal_milestone_due_state=goal_milestone_due_state,
            goal_milestone_pressure=goal_milestone_pressure,
            goal_milestone_arc=goal_milestone_arc,
            goal_milestone_transition=goal_milestone_transition,
        )
        if goal_milestone_due_window is not None:
            conclusions.append(goal_milestone_due_window)

        deduped: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for conclusion in conclusions:
            key = (str(conclusion["kind"]), str(conclusion["content"]))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(conclusion)
        return deduped

    def _derive_goal_execution_state(
        self,
        *,
        recent_memory: Sequence[dict],
        active_goals: Sequence[dict],
        active_tasks: Sequence[dict],
        task_done_updates: int,
        task_in_progress_updates: int,
    ) -> dict | None:
        if not active_goals:
            return None

        blocked_tasks = [
            task
            for task in active_tasks
            if str(task.get("status", "")).strip().lower() == "blocked"
        ]
        in_progress_tasks = [
            task
            for task in active_tasks
            if str(task.get("status", "")).strip().lower() == "in_progress"
        ]
        remaining_active_tasks = [
            task
            for task in active_tasks
            if str(task.get("status", "")).strip().lower() in {"todo", "in_progress"}
        ]

        if blocked_tasks:
            return {
                "kind": "goal_execution_state",
                "content": "blocked",
                "confidence": 0.82,
                "source": "background_reflection",
            }

        if task_done_updates >= 1 and remaining_active_tasks:
            return {
                "kind": "goal_execution_state",
                "content": "recovering",
                "confidence": 0.77,
                "source": "background_reflection",
            }

        if in_progress_tasks or task_in_progress_updates >= 1:
            return {
                "kind": "goal_execution_state",
                "content": "advancing",
                "confidence": 0.75,
                "source": "background_reflection",
            }

        if task_done_updates >= 1:
            return {
                "kind": "goal_execution_state",
                "content": "progressing",
                "confidence": 0.76,
                "source": "background_reflection",
            }

        if self._goal_stagnation_signal_count(recent_memory) >= 3:
            return {
                "kind": "goal_execution_state",
                "content": "stagnating",
                "confidence": 0.72,
                "source": "background_reflection",
            }

        return None

    def _derive_goal_progress_score(
        self,
        *,
        active_goals: Sequence[dict],
        active_tasks: Sequence[dict],
        task_done_updates: int,
    ) -> dict | None:
        if not active_goals:
            return None

        signal_count = len(active_tasks) + task_done_updates
        if signal_count <= 0:
            return None

        weighted_progress = float(task_done_updates)
        for task in active_tasks:
            status = str(task.get("status", "")).strip().lower()
            weighted_progress += {
                "blocked": 0.1,
                "todo": 0.3,
                "in_progress": 0.65,
            }.get(status, 0.0)

        score = min(0.99, max(0.0, round(weighted_progress / signal_count, 2)))
        confidence = 0.74 if signal_count >= 2 else 0.7
        return {
            "kind": "goal_progress_score",
            "content": f"{score:.2f}",
            "confidence": confidence,
            "source": "background_reflection",
        }

    def _derive_goal_progress_trend(
        self,
        *,
        current_goal_progress_score: dict | None,
        previous_goal_progress_score: float | None,
    ) -> dict | None:
        current_score = self._coerce_progress_score(
            current_goal_progress_score.get("content") if current_goal_progress_score else None
        )
        if current_score is None or previous_goal_progress_score is None:
            return None

        delta = round(current_score - previous_goal_progress_score, 2)
        if delta >= 0.12:
            return {
                "kind": "goal_progress_trend",
                "content": "improving",
                "confidence": 0.73,
                "source": "background_reflection",
            }
        if delta <= -0.12:
            return {
                "kind": "goal_progress_trend",
                "content": "slipping",
                "confidence": 0.75,
                "source": "background_reflection",
            }
        if abs(delta) <= 0.05 and current_score > 0.0:
            return {
                "kind": "goal_progress_trend",
                "content": "steady",
                "confidence": 0.7,
                "source": "background_reflection",
            }
        return None

    def _derive_goal_progress_arc(
        self,
        *,
        recent_goal_progress: Sequence[dict],
        current_goal_progress_score: dict | None,
        goal_execution_state: dict | None,
        goal_progress_trend: dict | None,
    ) -> dict | None:
        current_score = self._coerce_progress_score(
            current_goal_progress_score.get("content") if current_goal_progress_score else None
        )
        if current_score is None:
            return None

        ordered_history = list(reversed(recent_goal_progress))
        scores: list[float] = []
        states: list[str] = []
        for item in ordered_history:
            score = self._coerce_progress_score(item.get("score"))
            if score is None:
                continue
            scores.append(score)
            states.append(str(item.get("execution_state", "")).strip().lower())

        scores.append(current_score)
        states.append(str(goal_execution_state.get("content", "")).strip().lower() if goal_execution_state is not None else "")

        if len(scores) < 2:
            return None

        start = round(scores[0], 2)
        end = round(scores[-1], 2)
        delta = round(end - start, 2)
        span = round(max(scores) - min(scores), 2)
        trend = str(goal_progress_trend.get("content", "")).strip().lower() if goal_progress_trend is not None else ""
        has_recovery_state = any(state in {"blocked", "recovering"} for state in states)

        if has_recovery_state and trend == "improving" and end >= 0.5:
            return {
                "kind": "goal_progress_arc",
                "content": "recovery_gaining_traction",
                "confidence": 0.76,
                "source": "background_reflection",
            }
        if trend == "improving" and delta >= 0.35 and end >= 0.75:
            return {
                "kind": "goal_progress_arc",
                "content": "breakthrough_momentum",
                "confidence": 0.77,
                "source": "background_reflection",
            }
        if span >= 0.35 and abs(delta) < 0.15:
            return {
                "kind": "goal_progress_arc",
                "content": "unstable_progress",
                "confidence": 0.74,
                "source": "background_reflection",
            }
        if trend == "slipping" and delta <= -0.2 and end <= 0.35:
            return {
                "kind": "goal_progress_arc",
                "content": "falling_behind",
                "confidence": 0.78,
                "source": "background_reflection",
            }
        if trend == "steady" and start >= 0.45 and end >= 0.45:
            return {
                "kind": "goal_progress_arc",
                "content": "holding_pattern",
                "confidence": 0.71,
                "source": "background_reflection",
            }
        return None

    def _derive_goal_milestone_transition(
        self,
        *,
        current_goal_progress_score: dict | None,
        previous_goal_progress_score: float | None,
    ) -> dict | None:
        current_score = self._coerce_progress_score(
            current_goal_progress_score.get("content") if current_goal_progress_score else None
        )
        if current_score is None or previous_goal_progress_score is None:
            return None

        previous_score = round(previous_goal_progress_score, 2)
        current_score = round(current_score, 2)

        if previous_score >= 0.75 and current_score < 0.75:
            return {
                "kind": "goal_milestone_transition",
                "content": "slipped_from_completion_window",
                "confidence": 0.78,
                "source": "background_reflection",
            }
        if previous_score < 0.75 and current_score >= 0.75:
            return {
                "kind": "goal_milestone_transition",
                "content": "entered_completion_window",
                "confidence": 0.77,
                "source": "background_reflection",
            }
        if previous_score >= 0.35 and current_score < 0.35:
            return {
                "kind": "goal_milestone_transition",
                "content": "dropped_back_to_early_stage",
                "confidence": 0.76,
                "source": "background_reflection",
            }
        if previous_score < 0.35 and current_score >= 0.35:
            return {
                "kind": "goal_milestone_transition",
                "content": "entered_execution_phase",
                "confidence": 0.74,
                "source": "background_reflection",
            }
        return None

    def _derive_goal_milestone_state(
        self,
        *,
        has_active_goal: bool,
        current_goal_progress_score: dict | None,
        goal_execution_state: dict | None,
        goal_progress_arc: dict | None,
    ) -> dict | None:
        if not has_active_goal:
            return None
        current_score = self._coerce_progress_score(
            current_goal_progress_score.get("content") if current_goal_progress_score else None
        )
        if current_score is None:
            return {
                "kind": "goal_milestone_state",
                "content": "early_stage",
                "confidence": 0.7,
                "source": "background_reflection",
            }
        if current_score <= 0.0:
            return None

        execution_state = str(goal_execution_state.get("content", "")).strip().lower() if goal_execution_state is not None else ""
        progress_arc = str(goal_progress_arc.get("content", "")).strip().lower() if goal_progress_arc is not None else ""

        if current_score >= 0.75:
            return {
                "kind": "goal_milestone_state",
                "content": "completion_window",
                "confidence": 0.8,
                "source": "background_reflection",
            }
        if execution_state == "recovering" or progress_arc == "recovery_gaining_traction":
            return {
                "kind": "goal_milestone_state",
                "content": "recovery_phase",
                "confidence": 0.76,
                "source": "background_reflection",
            }
        if current_score >= 0.35:
            return {
                "kind": "goal_milestone_state",
                "content": "execution_phase",
                "confidence": 0.74,
                "source": "background_reflection",
            }
        return {
            "kind": "goal_milestone_state",
            "content": "early_stage",
            "confidence": 0.72,
            "source": "background_reflection",
        }

    def _derive_goal_milestone_arc(
        self,
        *,
        recent_goal_milestone_history: Sequence[dict],
        goal_milestone_state: dict | None,
        goal_milestone_transition: dict | None,
    ) -> dict | None:
        current_phase = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
        if not current_phase:
            return None

        transition = (
            str(goal_milestone_transition.get("content", "")).strip().lower()
            if goal_milestone_transition is not None
            else ""
        )
        ordered_history = list(reversed(recent_goal_milestone_history))
        states: list[tuple[str, str]] = []
        for item in ordered_history:
            phase = str(item.get("phase", "")).strip().lower()
            risk = str(item.get("risk_level", "")).strip().lower()
            if not phase and not risk:
                continue
            pair = (phase, risk)
            if not states or states[-1] != pair:
                states.append(pair)

        current_pair = (current_phase, "")
        if not states or states[-1][0] != current_phase:
            states.append(current_pair)
        else:
            states[-1] = (current_phase, states[-1][1])

        if len(states) < 2:
            return None

        previous_phase, _ = states[-2]
        phase_changes = sum(
            1
            for index in range(1, len(states))
            if states[index][0] and states[index - 1][0] and states[index][0] != states[index - 1][0]
        )
        distinct_phases = {phase for phase, _ in states if phase}
        had_completion_before = any(phase == "completion_window" for phase, _ in states[:-1])
        had_recovery_before = any(phase == "recovery_phase" for phase, _ in states[:-1])

        if current_phase == "completion_window" and transition == "entered_completion_window" and had_completion_before and had_recovery_before:
            return {
                "kind": "goal_milestone_arc",
                "content": "reentered_completion_window",
                "confidence": 0.79,
                "source": "background_reflection",
            }
        if current_phase == "recovery_phase" and had_completion_before:
            return {
                "kind": "goal_milestone_arc",
                "content": "recovery_backslide",
                "confidence": 0.78,
                "source": "background_reflection",
            }
        if len(distinct_phases) >= 3 and phase_changes >= 3:
            return {
                "kind": "goal_milestone_arc",
                "content": "milestone_whiplash",
                "confidence": 0.77,
                "source": "background_reflection",
            }
        if current_phase == "completion_window" and previous_phase == "completion_window":
            return {
                "kind": "goal_milestone_arc",
                "content": "steady_closure",
                "confidence": 0.75,
                "source": "background_reflection",
            }
        if current_phase == "completion_window" and previous_phase != "completion_window":
            return {
                "kind": "goal_milestone_arc",
                "content": "closure_momentum",
                "confidence": 0.76,
                "source": "background_reflection",
            }
        return None

    def _derive_goal_milestone_pressure(
        self,
        *,
        recent_goal_milestone_history: Sequence[dict],
        goal_milestone_state: dict | None,
        goal_milestone_arc: dict | None,
        goal_milestone_transition: dict | None,
    ) -> dict | None:
        current_phase = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
        latest_history_phase = ""
        if recent_goal_milestone_history:
            latest_history_phase = str(recent_goal_milestone_history[0].get("phase", "")).strip().lower()
        if (not current_phase or current_phase == "early_stage") and latest_history_phase:
            current_phase = latest_history_phase
        if not current_phase:
            return None

        milestone_arc = str(goal_milestone_arc.get("content", "")).strip().lower() if goal_milestone_arc is not None else ""
        transition = (
            str(goal_milestone_transition.get("content", "")).strip().lower()
            if goal_milestone_transition is not None
            else ""
        )

        ordered_history = list(reversed(recent_goal_milestone_history))
        consecutive_same_phase = 1
        latest_timestamp = datetime.now(timezone.utc)
        oldest_same_phase_timestamp = latest_timestamp
        found_current_phase = False

        for item in reversed(ordered_history):
            phase = str(item.get("phase", "")).strip().lower()
            if phase != current_phase:
                if found_current_phase:
                    break
                continue

            found_current_phase = True
            consecutive_same_phase += 1
            item_timestamp = item.get("created_at")
            if isinstance(item_timestamp, datetime):
                normalized_timestamp = (
                    item_timestamp if item_timestamp.tzinfo is not None else item_timestamp.replace(tzinfo=timezone.utc)
                )
                oldest_same_phase_timestamp = min(oldest_same_phase_timestamp, normalized_timestamp)

        same_phase_hours = max(0.0, (latest_timestamp - oldest_same_phase_timestamp).total_seconds() / 3600.0)

        if current_phase == "completion_window":
            if consecutive_same_phase >= 4 or same_phase_hours >= 12:
                return {
                    "kind": "goal_milestone_pressure",
                    "content": "lingering_completion",
                    "confidence": 0.8,
                    "source": "background_reflection",
                }
            if milestone_arc in {"closure_momentum", "reentered_completion_window"} or transition == "entered_completion_window":
                return {
                    "kind": "goal_milestone_pressure",
                    "content": "building_closure_pressure",
                    "confidence": 0.74,
                    "source": "background_reflection",
                }
            return None

        if current_phase == "recovery_phase" and (consecutive_same_phase >= 3 or same_phase_hours >= 8):
            return {
                "kind": "goal_milestone_pressure",
                "content": "dragging_recovery",
                "confidence": 0.78,
                "source": "background_reflection",
            }

        if current_phase == "execution_phase" and (consecutive_same_phase >= 4 or same_phase_hours >= 12):
            return {
                "kind": "goal_milestone_pressure",
                "content": "stale_execution",
                "confidence": 0.75,
                "source": "background_reflection",
            }

        if current_phase == "early_stage" and (consecutive_same_phase >= 4 or same_phase_hours >= 12):
            return {
                "kind": "goal_milestone_pressure",
                "content": "lingering_setup",
                "confidence": 0.74,
                "source": "background_reflection",
            }

        return None

    def _derive_goal_milestone_dependency_state(
        self,
        *,
        active_tasks: Sequence[dict],
        goal_milestone_state: dict | None,
        goal_execution_state: dict | None,
    ) -> dict | None:
        milestone_state = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
        execution_state = str(goal_execution_state.get("content", "")).strip().lower() if goal_execution_state is not None else ""
        blocked_tasks = [
            task
            for task in active_tasks
            if str(task.get("status", "")).strip().lower() == "blocked"
        ]
        remaining_tasks = [
            task
            for task in active_tasks
            if str(task.get("status", "")).strip().lower() in {"todo", "in_progress", "blocked"}
        ]

        if blocked_tasks or execution_state == "blocked":
            return {
                "kind": "goal_milestone_dependency_state",
                "content": "blocked_dependency",
                "confidence": 0.83,
                "source": "background_reflection",
            }
        if len(remaining_tasks) >= 2:
            return {
                "kind": "goal_milestone_dependency_state",
                "content": "multi_step_dependency",
                "confidence": 0.76,
                "source": "background_reflection",
            }
        if len(remaining_tasks) == 1:
            return {
                "kind": "goal_milestone_dependency_state",
                "content": "single_step_dependency",
                "confidence": 0.74,
                "source": "background_reflection",
            }
        if milestone_state == "completion_window":
            return {
                "kind": "goal_milestone_dependency_state",
                "content": "clear_to_close",
                "confidence": 0.79,
                "source": "background_reflection",
            }
        return None

    def _derive_goal_milestone_due_state(
        self,
        *,
        goal_milestone_state: dict | None,
        goal_milestone_pressure: dict | None,
        goal_milestone_dependency_state: dict | None,
        goal_completion_criteria: dict | None,
    ) -> dict | None:
        milestone_state = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
        pressure = str(goal_milestone_pressure.get("content", "")).strip().lower() if goal_milestone_pressure is not None else ""
        dependency_state = (
            str(goal_milestone_dependency_state.get("content", "")).strip().lower()
            if goal_milestone_dependency_state is not None
            else ""
        )
        completion_criteria = (
            str(goal_completion_criteria.get("content", "")).strip().lower()
            if goal_completion_criteria is not None
            else ""
        )

        if milestone_state == "completion_window":
            if dependency_state == "clear_to_close" or completion_criteria == "confirm_goal_completion":
                return {
                    "kind": "goal_milestone_due_state",
                    "content": "closure_due_now",
                    "confidence": 0.82,
                    "source": "background_reflection",
                }
            if dependency_state in {"blocked_dependency", "single_step_dependency", "multi_step_dependency"}:
                return {
                    "kind": "goal_milestone_due_state",
                    "content": "dependency_due_next",
                    "confidence": 0.79,
                    "source": "background_reflection",
                }
            return None

        if milestone_state == "recovery_phase" and pressure == "dragging_recovery":
            return {
                "kind": "goal_milestone_due_state",
                "content": "recovery_due_attention",
                "confidence": 0.77,
                "source": "background_reflection",
            }

        if milestone_state == "execution_phase" and pressure == "stale_execution":
            return {
                "kind": "goal_milestone_due_state",
                "content": "execution_due_attention",
                "confidence": 0.75,
                "source": "background_reflection",
            }

        if milestone_state == "early_stage" and pressure == "lingering_setup":
            return {
                "kind": "goal_milestone_due_state",
                "content": "setup_due_start",
                "confidence": 0.74,
                "source": "background_reflection",
            }

        return None

    def _derive_goal_milestone_due_window(
        self,
        *,
        goal_milestone_due_state: dict | None,
        goal_milestone_pressure: dict | None,
        goal_milestone_arc: dict | None,
        goal_milestone_transition: dict | None,
    ) -> dict | None:
        due_state = str(goal_milestone_due_state.get("content", "")).strip().lower() if goal_milestone_due_state is not None else ""
        pressure = str(goal_milestone_pressure.get("content", "")).strip().lower() if goal_milestone_pressure is not None else ""
        milestone_arc = str(goal_milestone_arc.get("content", "")).strip().lower() if goal_milestone_arc is not None else ""
        transition = (
            str(goal_milestone_transition.get("content", "")).strip().lower()
            if goal_milestone_transition is not None
            else ""
        )

        if not due_state:
            return None
        if milestone_arc == "reentered_completion_window":
            return {
                "kind": "goal_milestone_due_window",
                "content": "reopened_due_window",
                "confidence": 0.8,
                "source": "background_reflection",
            }
        if pressure in {"lingering_completion", "dragging_recovery", "stale_execution", "lingering_setup"}:
            return {
                "kind": "goal_milestone_due_window",
                "content": "overdue_due_window",
                "confidence": 0.82,
                "source": "background_reflection",
            }
        if transition == "entered_completion_window" or pressure == "building_closure_pressure":
            return {
                "kind": "goal_milestone_due_window",
                "content": "fresh_due_window",
                "confidence": 0.76,
                "source": "background_reflection",
            }
        return {
            "kind": "goal_milestone_due_window",
            "content": "active_due_window",
            "confidence": 0.73,
            "source": "background_reflection",
        }

    def _derive_goal_milestone_risk(
        self,
        *,
        active_tasks: Sequence[dict],
        goal_execution_state: dict | None,
        goal_progress_arc: dict | None,
        goal_milestone_state: dict | None,
        goal_milestone_transition: dict | None,
    ) -> dict | None:
        execution_state = str(goal_execution_state.get("content", "")).strip().lower() if goal_execution_state is not None else ""
        progress_arc = str(goal_progress_arc.get("content", "")).strip().lower() if goal_progress_arc is not None else ""
        milestone_state = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
        milestone_transition = (
            str(goal_milestone_transition.get("content", "")).strip().lower()
            if goal_milestone_transition is not None
            else ""
        )
        blocked_tasks = [
            task
            for task in active_tasks
            if str(task.get("status", "")).strip().lower() == "blocked"
        ]

        if blocked_tasks or execution_state == "blocked" or progress_arc == "falling_behind":
            return {
                "kind": "goal_milestone_risk",
                "content": "at_risk",
                "confidence": 0.81,
                "source": "background_reflection",
            }
        if milestone_transition == "slipped_from_completion_window" or progress_arc == "unstable_progress":
            return {
                "kind": "goal_milestone_risk",
                "content": "watch",
                "confidence": 0.75,
                "source": "background_reflection",
            }
        if milestone_state == "completion_window":
            return {
                "kind": "goal_milestone_risk",
                "content": "ready_to_close",
                "confidence": 0.79,
                "source": "background_reflection",
            }
        if milestone_state == "recovery_phase" or progress_arc == "recovery_gaining_traction":
            return {
                "kind": "goal_milestone_risk",
                "content": "stabilizing",
                "confidence": 0.74,
                "source": "background_reflection",
            }
        if milestone_state in {"execution_phase", "early_stage"} or execution_state in {"advancing", "progressing"}:
            return {
                "kind": "goal_milestone_risk",
                "content": "on_track",
                "confidence": 0.71,
                "source": "background_reflection",
            }
        return None

    def _derive_goal_completion_criteria(
        self,
        *,
        active_tasks: Sequence[dict],
        goal_execution_state: dict | None,
        goal_milestone_state: dict | None,
        goal_milestone_risk: dict | None,
    ) -> dict | None:
        milestone_state = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
        execution_state = str(goal_execution_state.get("content", "")).strip().lower() if goal_execution_state is not None else ""
        milestone_risk = str(goal_milestone_risk.get("content", "")).strip().lower() if goal_milestone_risk is not None else ""
        blocked_tasks = [
            task
            for task in active_tasks
            if str(task.get("status", "")).strip().lower() == "blocked"
        ]
        in_progress_tasks = [
            task
            for task in active_tasks
            if str(task.get("status", "")).strip().lower() == "in_progress"
        ]
        todo_tasks = [
            task
            for task in active_tasks
            if str(task.get("status", "")).strip().lower() == "todo"
        ]

        if milestone_state == "completion_window":
            if blocked_tasks:
                return {
                    "kind": "goal_completion_criteria",
                    "content": "resolve_remaining_blocker",
                    "confidence": 0.82,
                    "source": "background_reflection",
                }
            if in_progress_tasks or todo_tasks:
                return {
                    "kind": "goal_completion_criteria",
                    "content": "finish_remaining_active_work",
                    "confidence": 0.8,
                    "source": "background_reflection",
                }
            return {
                "kind": "goal_completion_criteria",
                "content": "confirm_goal_completion",
                "confidence": 0.79,
                "source": "background_reflection",
            }

        if blocked_tasks:
            return {
                "kind": "goal_completion_criteria",
                "content": "resolve_remaining_blocker",
                "confidence": 0.82,
                "source": "background_reflection",
            }

        if milestone_state == "recovery_phase" or execution_state == "recovering" or milestone_risk == "stabilizing":
            return {
                "kind": "goal_completion_criteria",
                "content": "stabilize_remaining_work",
                "confidence": 0.76,
                "source": "background_reflection",
            }

        if milestone_state == "early_stage":
            return {
                "kind": "goal_completion_criteria",
                "content": "define_first_execution_step",
                "confidence": 0.72,
                "source": "background_reflection",
            }

        if milestone_state == "execution_phase":
            return {
                "kind": "goal_completion_criteria",
                "content": "advance_next_task",
                "confidence": 0.74,
                "source": "background_reflection",
            }

        return None

    def _goal_stagnation_signal_count(self, recent_memory: Sequence[dict]) -> int:
        planning_heavy_steps = {
            "align_with_active_goal",
            "break_down_problem",
            "highlight_next_step",
            "offer_guidance",
            "favor_guided_walkthrough",
            "review_context",
        }
        execution_steps = {
            "identify_requested_change",
            "propose_execution_step",
            "advance_active_task",
            "unblock_active_task",
            "recover_goal_progress",
            "preserve_goal_momentum",
            "favor_concrete_next_step",
        }

        stagnation_signals = 0
        for memory_item in recent_memory:
            fields = self._extract_fields(str(memory_item.get("summary", "")))
            if fields.get("action", "").strip().lower() != "success":
                continue
            if fields.get("task_status_update", "").strip():
                continue
            if fields.get("task_update", "").strip():
                continue

            plan_steps = {
                step.strip().lower()
                for step in fields.get("plan_steps", "").split(",")
                if step.strip()
            }
            if "align_with_active_goal" not in plan_steps:
                continue
            if plan_steps.intersection(execution_steps):
                continue
            if not plan_steps.intersection(planning_heavy_steps):
                continue
            stagnation_signals += 1

        return stagnation_signals

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

    def _select_primary_goal(self, active_goals: Sequence[dict]) -> dict | None:
        if not active_goals:
            return None

        ranked = sorted(
            active_goals,
            key=lambda goal: (
                self._goal_priority_rank(str(goal.get("priority", ""))),
                str(goal.get("updated_at", "")),
                int(goal.get("id", 0) or 0),
            ),
            reverse=True,
        )
        return ranked[0]

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

    def _derive_collaboration_preference(self, recent_memory: Sequence[dict]) -> dict | None:
        if len(recent_memory) < 4:
            return None

        guided_count = 0
        hands_on_count = 0
        sample_size = 0

        for memory_item in recent_memory:
            fields = self._extract_fields(str(memory_item.get("summary", "")))
            role = fields.get("role", "").strip().lower()
            motivation = fields.get("motivation", "").strip().lower()
            plan_steps = {
                step.strip().lower()
                for step in fields.get("plan_steps", "").split(",")
                if step.strip()
            }

            if not role and not motivation and not plan_steps:
                continue
            sample_size += 1

            if (
                role == "executor"
                or motivation == "execute"
                or {"propose_execution_step", "identify_requested_change", "favor_concrete_next_step"}.intersection(plan_steps)
            ):
                hands_on_count += 1
                continue

            if (
                role in {"analyst", "mentor", "friend"}
                or motivation in {"analyze", "support"}
                or {"break_down_problem", "offer_guidance", "favor_guided_walkthrough", "highlight_next_step"}.intersection(plan_steps)
            ):
                guided_count += 1

        if sample_size < 4:
            return None

        if hands_on_count >= 3 and hands_on_count / sample_size >= 0.7:
            return {
                "kind": "collaboration_preference",
                "content": "hands_on",
                "confidence": 0.73,
                "source": "background_reflection",
            }

        if guided_count >= 3 and guided_count / sample_size >= 0.7:
            return {
                "kind": "collaboration_preference",
                "content": "guided",
                "confidence": 0.73,
                "source": "background_reflection",
            }

        return None

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

    def _coerce_progress_score(self, value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _goal_priority_rank(self, priority: str) -> int:
        return {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }.get(priority, 0)
