import asyncio
from datetime import datetime, timedelta, timezone
from collections.abc import Sequence

from app.core.logging import get_logger
from app.memory.episodic import extract_episode_fields
from app.memory.repository import MemoryRepository
from app.reflection.adaptive_signals import (
    derive_collaboration_preference,
    derive_preferred_role,
    derive_theta,
    has_outcome_evidence,
)
from app.reflection.affective_signals import derive_affective_conclusions
from app.reflection.goal_conclusions import (
    derive_goal_completion_criteria,
    derive_goal_execution_state,
    derive_goal_milestone_arc,
    derive_goal_milestone_dependency_state,
    derive_goal_milestone_due_state,
    derive_goal_milestone_due_window,
    derive_goal_milestone_pressure,
    derive_goal_milestone_risk,
    derive_goal_milestone_state,
    derive_goal_milestone_transition,
    derive_goal_progress_arc,
    derive_goal_progress_score,
    derive_goal_progress_trend,
)
from app.reflection.relation_signals import derive_relation_updates
from app.reflection.proposals import derive_subconscious_proposals
from app.utils.goal_task_selection import priority_rank as shared_priority_rank


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

    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def stop(self) -> None:
        if not self._task:
            return
        await self.queue.put(None)
        await self._task
        self._task = None

    async def enqueue(self, user_id: str, event_id: str, *, dispatch: bool = True) -> bool:
        task = await self.memory_repository.enqueue_reflection_task(user_id=user_id, event_id=event_id)
        if str(task.get("status")) == "completed":
            return True
        if not dispatch:
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
        primary_goal = self._select_primary_goal(
            active_goals,
            recent_memory=recent_memory,
            active_tasks=active_tasks,
        )
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
        relation_updates = derive_relation_updates(
            recent_memory,
            extract_memory_fields=self._extract_memory_fields,
        )
        theta = derive_theta(recent_memory, extract_memory_fields=self._extract_memory_fields)
        subconscious_proposals: list[dict] = []
        if hasattr(self.memory_repository, "upsert_subconscious_proposal"):
            subconscious_proposals = derive_subconscious_proposals(
                recent_memory,
                active_goals=active_goals,
                active_tasks=active_tasks,
                extract_memory_fields=self._extract_memory_fields,
            )
        if not conclusions and not relation_updates and theta is None and not subconscious_proposals:
            self.logger.info("reflection_noop user_id=%s event_id=%s", user_id, event_id)
            return False

        for conclusion in conclusions:
            scope_type, scope_key = self._conclusion_scope(kind=str(conclusion["kind"]), primary_goal=primary_goal)
            await self.memory_repository.upsert_conclusion(
                user_id=user_id,
                kind=conclusion["kind"],
                content=conclusion["content"],
                confidence=conclusion["confidence"],
                source=conclusion["source"],
                supporting_event_id=event_id,
                scope_type=scope_type,
                scope_key=scope_key,
            )
            self.logger.info(
                "reflection_conclusion_updated user_id=%s event_id=%s kind=%s content=%s confidence=%.2f source=%s scope_type=%s scope_key=%s",
                user_id,
                event_id,
                conclusion["kind"],
                conclusion["content"],
                conclusion["confidence"],
                conclusion["source"],
                scope_type,
                scope_key,
            )
        for relation in relation_updates:
            relation_scope_type, relation_scope_key = self._relation_scope(
                relation_type=str(relation["relation_type"]),
                primary_goal=primary_goal,
            )
            await self.memory_repository.upsert_relation(
                user_id=user_id,
                relation_type=str(relation["relation_type"]),
                relation_value=str(relation["relation_value"]),
                confidence=float(relation["confidence"]),
                source=str(relation["source"]),
                supporting_event_id=event_id,
                scope_type=relation_scope_type,
                scope_key=relation_scope_key,
                evidence_count=int(relation.get("evidence_count", 1)),
                decay_rate=float(relation.get("decay_rate", 0.02)),
            )
            self.logger.info(
                "reflection_relation_updated user_id=%s event_id=%s relation_type=%s relation_value=%s confidence=%.2f scope_type=%s scope_key=%s",
                user_id,
                event_id,
                relation["relation_type"],
                relation["relation_value"],
                relation["confidence"],
                relation_scope_type,
                relation_scope_key,
            )
        if hasattr(self.memory_repository, "upsert_subconscious_proposal"):
            for proposal in subconscious_proposals:
                stored_proposal = await self.memory_repository.upsert_subconscious_proposal(
                    user_id=user_id,
                    proposal_type=str(proposal.get("proposal_type", "nudge_user")),
                    summary=str(proposal.get("summary", "")),
                    payload=proposal.get("payload") if isinstance(proposal.get("payload"), dict) else {},
                    confidence=float(proposal.get("confidence", 0.0) or 0.0),
                    source_event_id=event_id,
                    research_policy=str(proposal.get("research_policy", "read_only")),
                    allowed_tools=[
                        str(item)
                        for item in proposal.get("allowed_tools", [])
                        if isinstance(item, str)
                    ],
                )
                self.logger.info(
                    "reflection_subconscious_proposal_upserted user_id=%s event_id=%s proposal_id=%s type=%s confidence=%.2f status=%s",
                    user_id,
                    event_id,
                    stored_proposal["proposal_id"],
                    stored_proposal["proposal_type"],
                    stored_proposal["confidence"],
                    stored_proposal["status"],
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
            try:
                await self._process_task(item)
            finally:
                self.queue.task_done()
                await self._schedule_pending_tasks(limit=1)

    async def run_pending_once(self, *, limit: int = 10) -> dict[str, int]:
        pending_tasks = await self.memory_repository.get_pending_reflection_tasks(limit=max(1, limit))
        summary = {
            "scanned": len(pending_tasks),
            "processed": 0,
            "completed": 0,
            "failed": 0,
            "skipped_not_ready": 0,
        }
        for task in pending_tasks:
            if not self._is_task_ready(task):
                summary["skipped_not_ready"] += 1
                continue
            summary["processed"] += 1
            completed = await self._process_task(task)
            if completed:
                summary["completed"] += 1
            else:
                summary["failed"] += 1
        return summary

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

    async def _process_task(self, item: dict) -> bool:
        task_id = int(item["id"])
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
        return completed

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
        outcome_evidence_count = 0

        for memory_item in recent_memory:
            fields = self._extract_memory_fields(memory_item)
            if has_outcome_evidence(fields):
                outcome_evidence_count += 1
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

        preferred_role = derive_preferred_role(
            role_counts=role_counts,
            total=len(recent_memory),
            outcome_evidence_count=outcome_evidence_count,
        )
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

        collaboration_preference = derive_collaboration_preference(
            recent_memory,
            extract_memory_fields=self._extract_memory_fields,
        )
        if collaboration_preference is not None:
            conclusions.append(collaboration_preference)

        affective_conclusions = derive_affective_conclusions(
            recent_memory,
            extract_memory_fields=self._extract_memory_fields,
        )
        if affective_conclusions:
            conclusions.extend(affective_conclusions)

        goal_execution_state = derive_goal_execution_state(
            recent_memory=recent_memory,
            active_goals=active_goals or [],
            active_tasks=active_tasks or [],
            task_done_updates=task_done_updates,
            task_in_progress_updates=task_in_progress_updates,
            extract_memory_fields=self._extract_memory_fields,
        )
        if goal_execution_state is not None:
            conclusions.append(goal_execution_state)
        goal_progress_score = derive_goal_progress_score(
            active_goals=active_goals or [],
            active_tasks=active_tasks or [],
            task_done_updates=task_done_updates,
        )
        if goal_progress_score is not None:
            conclusions.append(goal_progress_score)
        goal_progress_trend = derive_goal_progress_trend(
            current_goal_progress_score=goal_progress_score,
            previous_goal_progress_score=previous_goal_progress_score,
            coerce_progress_score=self._coerce_progress_score,
        )
        if goal_progress_trend is not None:
            conclusions.append(goal_progress_trend)
        goal_progress_arc = derive_goal_progress_arc(
            recent_goal_progress=recent_goal_progress or [],
            current_goal_progress_score=goal_progress_score,
            goal_execution_state=goal_execution_state,
            goal_progress_trend=goal_progress_trend,
            coerce_progress_score=self._coerce_progress_score,
        )
        if goal_progress_arc is not None:
            conclusions.append(goal_progress_arc)
        goal_milestone_state = derive_goal_milestone_state(
            has_active_goal=bool(active_goals),
            current_goal_progress_score=goal_progress_score,
            goal_execution_state=goal_execution_state,
            goal_progress_arc=goal_progress_arc,
            coerce_progress_score=self._coerce_progress_score,
        )
        if goal_milestone_state is not None:
            conclusions.append(goal_milestone_state)
        goal_milestone_transition = derive_goal_milestone_transition(
            current_goal_progress_score=goal_progress_score,
            previous_goal_progress_score=previous_goal_progress_score,
            coerce_progress_score=self._coerce_progress_score,
        )
        if goal_milestone_transition is not None:
            conclusions.append(goal_milestone_transition)
        goal_milestone_arc = derive_goal_milestone_arc(
            recent_goal_milestone_history=recent_goal_milestone_history or [],
            goal_milestone_state=goal_milestone_state,
            goal_milestone_transition=goal_milestone_transition,
        )
        if goal_milestone_arc is not None:
            conclusions.append(goal_milestone_arc)
        goal_milestone_pressure = derive_goal_milestone_pressure(
            recent_goal_milestone_history=recent_goal_milestone_history or [],
            goal_milestone_state=goal_milestone_state,
            goal_milestone_arc=goal_milestone_arc,
            goal_milestone_transition=goal_milestone_transition,
        )
        if goal_milestone_pressure is not None:
            conclusions.append(goal_milestone_pressure)
        goal_milestone_dependency_state = derive_goal_milestone_dependency_state(
            active_tasks=active_tasks or [],
            goal_milestone_state=goal_milestone_state,
            goal_execution_state=goal_execution_state,
        )
        if goal_milestone_dependency_state is not None:
            conclusions.append(goal_milestone_dependency_state)
        goal_milestone_risk = derive_goal_milestone_risk(
            active_tasks=active_tasks or [],
            goal_execution_state=goal_execution_state,
            goal_progress_arc=goal_progress_arc,
            goal_milestone_state=goal_milestone_state,
            goal_milestone_transition=goal_milestone_transition,
        )
        if goal_milestone_risk is not None:
            conclusions.append(goal_milestone_risk)
        goal_completion_criteria = derive_goal_completion_criteria(
            active_tasks=active_tasks or [],
            goal_execution_state=goal_execution_state,
            goal_milestone_state=goal_milestone_state,
            goal_milestone_risk=goal_milestone_risk,
        )
        if goal_completion_criteria is not None:
            conclusions.append(goal_completion_criteria)
        goal_milestone_due_state = derive_goal_milestone_due_state(
            goal_milestone_state=goal_milestone_state,
            goal_milestone_pressure=goal_milestone_pressure,
            goal_milestone_dependency_state=goal_milestone_dependency_state,
            goal_completion_criteria=goal_completion_criteria,
        )
        if goal_milestone_due_state is not None:
            conclusions.append(goal_milestone_due_state)
        goal_milestone_due_window = derive_goal_milestone_due_window(
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

    def _select_primary_goal(
        self,
        active_goals: Sequence[dict],
        *,
        recent_memory: Sequence[dict],
        active_tasks: Sequence[dict],
    ) -> dict | None:
        if not active_goals:
            return None

        hints: list[str] = []
        for memory_item in list(recent_memory)[:3]:
            fields = self._extract_memory_fields(memory_item)
            hints.extend(
                [
                    fields.get("event", ""),
                    fields.get("goal_update", ""),
                    fields.get("task_update", ""),
                    fields.get("task_status_update", "").split(":", 1)[0],
                ]
            )
        hint_tokens = self._text_tokens(" ".join(hints))

        if hint_tokens:
            task_by_goal: dict[int, list[str]] = {}
            for task in active_tasks:
                goal_id = task.get("goal_id")
                if goal_id is None:
                    continue
                task_by_goal.setdefault(int(goal_id), []).append(
                    f"{task.get('name', '')} {task.get('description', '')}"
                )

            ranked_by_hint = sorted(
                active_goals,
                key=lambda goal: (
                    len(
                        hint_tokens.intersection(
                            self._text_tokens(
                                " ".join(
                                    [
                                        str(goal.get("name", "")),
                                        str(goal.get("description", "")),
                                        " ".join(task_by_goal.get(int(goal.get("id", 0) or 0), [])),
                                    ]
                                )
                            )
                        )
                    ),
                    self._goal_priority_rank(str(goal.get("priority", ""))),
                    str(goal.get("updated_at", "")),
                    int(goal.get("id", 0) or 0),
                ),
                reverse=True,
            )
            if ranked_by_hint:
                top = ranked_by_hint[0]
                top_tokens = self._text_tokens(
                    f"{top.get('name', '')} {top.get('description', '')}"
                )
                if hint_tokens.intersection(top_tokens):
                    return top

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

    def _extract_fields(self, raw_summary: str) -> dict[str, str]:
        return extract_episode_fields({"summary": raw_summary})

    def _extract_memory_fields(self, memory_item: dict) -> dict[str, str]:
        return extract_episode_fields(memory_item)

    def _looks_structured(self, expression: str) -> bool:
        return expression.startswith("- ") or "\n1." in expression or "### " in expression

    def _coerce_progress_score(self, value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _text_tokens(self, value: str) -> set[str]:
        canonical = "".join(char if char.isalnum() or char.isspace() else " " for char in value.strip().lower())
        return {token for token in canonical.split() if len(token) >= 3}

    def _goal_priority_rank(self, priority: str) -> int:
        return shared_priority_rank(priority)

    def _conclusion_scope(self, *, kind: str, primary_goal: dict | None) -> tuple[str, str]:
        if kind.startswith("goal_") and primary_goal is not None and primary_goal.get("id") is not None:
            return "goal", str(primary_goal["id"])
        return "global", "global"

    def _relation_scope(self, *, relation_type: str, primary_goal: dict | None) -> tuple[str, str]:
        goal_scoped_types = {
            "goal_execution_trust",
            "goal_collaboration_flow",
        }
        if relation_type in goal_scoped_types and primary_goal is not None and primary_goal.get("id") is not None:
            return "goal", str(primary_goal["id"])
        return "global", "global"
