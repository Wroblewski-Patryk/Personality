import asyncio
from datetime import datetime, timedelta, timezone

from app.reflection.worker import ReflectionWorker


class FakeMemoryRepository:
    def __init__(self, recent_memory: list[dict]):
        self.recent_memory = recent_memory
        self.conclusion_updates: list[dict] = []
        self.theta_updates: list[dict] = []
        self.runtime_preferences: dict = {}
        self.goal_progress_history: list[dict] = []
        self.goal_progress_snapshots: list[dict] = []
        self.created_tasks: list[dict] = []
        self.pending_tasks: list[dict] = []
        self.processing_marks: list[int] = []
        self.completed_marks: list[int] = []
        self.failed_marks: list[dict] = []
        self.active_goals: list[dict] = []
        self.active_tasks: list[dict] = []

    async def get_recent_for_user(self, user_id: str, limit: int = 8) -> list[dict]:
        return self.recent_memory[:limit]

    async def get_user_runtime_preferences(self, user_id: str) -> dict:
        return self.runtime_preferences

    async def get_recent_goal_progress(self, user_id: str, *, goal_ids: list[int] | None = None, limit: int = 6) -> list[dict]:
        rows = self.goal_progress_history[:]
        if goal_ids:
            rows = [row for row in rows if int(row.get("goal_id", -1)) in set(goal_ids)]
        return rows[:limit]

    async def append_goal_progress_snapshot(self, **kwargs) -> dict:
        payload = {"id": len(self.goal_progress_snapshots) + 1, **kwargs}
        self.goal_progress_snapshots.insert(0, payload)
        self.goal_progress_history.insert(0, payload)
        return payload

    async def upsert_conclusion(self, **kwargs) -> dict:
        self.conclusion_updates.append(kwargs)
        return kwargs

    async def upsert_theta(self, **kwargs) -> dict:
        self.theta_updates.append(kwargs)
        return kwargs

    async def get_active_goals(self, user_id: str, limit: int = 5) -> list[dict]:
        return self.active_goals[:limit]

    async def get_active_tasks(self, user_id: str, limit: int = 8) -> list[dict]:
        return self.active_tasks[:limit]

    async def enqueue_reflection_task(self, user_id: str, event_id: str) -> dict:
        task = {
            "id": len(self.created_tasks) + 1,
            "user_id": user_id,
            "event_id": event_id,
            "status": "pending",
            "attempts": 0,
            "last_error": None,
        }
        self.created_tasks.append(task)
        return task

    async def get_pending_reflection_tasks(self, limit: int = 100) -> list[dict]:
        return [
            task
            for task in self.pending_tasks
            if task["status"] in {"pending", "processing", "failed"}
        ][:limit]

    async def mark_reflection_task_processing(self, task_id: int) -> dict:
        self.processing_marks.append(task_id)
        self._update_task_status(task_id=task_id, status="processing", last_error=None)
        return {"id": task_id, "status": "processing"}

    async def mark_reflection_task_completed(self, task_id: int) -> dict:
        self.completed_marks.append(task_id)
        self._update_task_status(task_id=task_id, status="completed", last_error=None)
        return {"id": task_id, "status": "completed"}

    async def mark_reflection_task_failed(self, task_id: int, error: str) -> dict:
        self.failed_marks.append({"id": task_id, "error": error})
        self._update_task_status(task_id=task_id, status="failed", last_error=error)
        return {"id": task_id, "status": "failed", "last_error": error}

    def _update_task_status(self, task_id: int, status: str, last_error: str | None) -> None:
        for task in self.pending_tasks:
            if int(task["id"]) == task_id:
                task["status"] = status
                task["last_error"] = last_error
                return


async def test_reflection_worker_consolidates_explicit_preference_update_in_background() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {
                "summary": (
                    "event=Reply in bullet points from now on.; memory_kind=semantic; memory_topics=reply,bullet,points; "
                    "response_language=en; preference_update=response_style:structured; "
                    "action=success; expression=- first\\n- second"
                )
            }
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-1")

    assert result is True
    assert repository.conclusion_updates == [
        {
            "user_id": "u-1",
            "kind": "response_style",
            "content": "structured",
            "confidence": 0.98,
            "source": "background_reflection",
            "supporting_event_id": "evt-1",
        }
    ]
    assert repository.theta_updates == []


async def test_reflection_worker_infers_preferred_role_from_repeated_role_usage() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "role=executor; action=success; expression=Done one."},
            {"summary": "role=executor; action=success; expression=Done two."},
            {"summary": "role=executor; action=success; expression=Done three."},
            {"summary": "role=mentor; action=success; expression=Different path."},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-role")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "preferred_role",
        "content": "executor",
        "confidence": 0.76,
        "source": "background_reflection",
        "supporting_event_id": "evt-role",
    } in repository.conclusion_updates
    assert repository.theta_updates == [
        {
            "user_id": "u-1",
            "support_bias": 0.0,
            "analysis_bias": 0.0,
            "execution_bias": 1.0,
        }
    ]


async def test_reflection_worker_infers_concise_style_from_repeated_short_successful_outputs() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "action=success; expression=Short answer one."},
            {"summary": "action=success; expression=Short answer two."},
            {"summary": "action=success; expression=Short answer three."},
            {"summary": "action=success; expression=Another short answer."},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-2")

    assert result is True
    assert repository.conclusion_updates[0]["content"] == "concise"
    assert repository.conclusion_updates[0]["source"] == "background_reflection"


async def test_reflection_worker_skips_when_recent_memory_has_no_consistent_signal() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "action=success; expression=This is a longer explanatory response that should not count as concise."},
            {"summary": "action=success; expression=- one\\n- two"},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-3")

    assert result is False
    assert repository.conclusion_updates == []
    assert repository.theta_updates == []


async def test_reflection_worker_updates_theta_from_mixed_recent_roles() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "role=analyst; action=success; expression=One."},
            {"summary": "role=analyst; action=success; expression=Two."},
            {"summary": "role=executor; action=success; expression=Three."},
            {"summary": "role=friend; action=success; expression=Four."},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-theta")

    assert result is True
    assert repository.theta_updates == [
        {
            "user_id": "u-1",
            "support_bias": 0.25,
            "analysis_bias": 0.5,
            "execution_bias": 0.25,
        }
    ]


async def test_reflection_worker_infers_guided_collaboration_preference() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "motivation=analyze; role=analyst; plan_steps=interpret_event,review_context,break_down_problem,highlight_next_step,prepare_response; action=success; expression=One."},
            {"summary": "motivation=analyze; role=analyst; plan_steps=interpret_event,review_context,break_down_problem,highlight_next_step,prepare_response; action=success; expression=Two."},
            {"summary": "motivation=respond; role=mentor; plan_steps=interpret_event,review_context,offer_guidance,prepare_response; action=success; expression=Three."},
            {"summary": "motivation=support; role=friend; plan_steps=interpret_event,review_context,reduce_pressure,prepare_response; action=success; expression=Four."},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-guided")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "collaboration_preference",
        "content": "guided",
        "confidence": 0.73,
        "source": "background_reflection",
        "supporting_event_id": "evt-guided",
    } in repository.conclusion_updates


async def test_reflection_worker_infers_hands_on_collaboration_preference() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "motivation=execute; role=executor; plan_steps=interpret_event,review_context,identify_requested_change,propose_execution_step,prepare_response; action=success; expression=One."},
            {"summary": "motivation=execute; role=executor; plan_steps=interpret_event,review_context,identify_requested_change,propose_execution_step,prepare_response; action=success; expression=Two."},
            {"summary": "motivation=execute; role=executor; plan_steps=interpret_event,review_context,identify_requested_change,propose_execution_step,prepare_response; action=success; expression=Three."},
            {"summary": "motivation=respond; role=advisor; plan_steps=interpret_event,review_context,favor_concrete_next_step,prepare_response; action=success; expression=Four."},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-hands-on")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "collaboration_preference",
        "content": "hands_on",
        "confidence": 0.73,
        "source": "background_reflection",
        "supporting_event_id": "evt-hands-on",
    } in repository.conclusion_updates


async def test_reflection_worker_prefers_explicit_guided_collaboration_update() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "collaboration_update=guided; action=success; expression=One."},
            {"summary": "motivation=execute; role=executor; plan_steps=identify_requested_change,propose_execution_step; action=success; expression=Two."},
            {"summary": "motivation=execute; role=executor; plan_steps=identify_requested_change,propose_execution_step; action=success; expression=Three."},
            {"summary": "motivation=execute; role=executor; plan_steps=identify_requested_change,propose_execution_step; action=success; expression=Four."},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-explicit-guided")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "collaboration_preference",
        "content": "guided",
        "confidence": 0.94,
        "source": "background_reflection",
        "supporting_event_id": "evt-explicit-guided",
    } in repository.conclusion_updates


async def test_reflection_worker_infers_blocked_goal_execution_state() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "goal_update=ship the MVP this week; action=success; expression=One."},
            {"summary": "task_update=fix deployment blocker; action=success; expression=Two."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 2, "goal_id": 1, "name": "fix deployment blocker", "priority": "high", "status": "blocked"}
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-blocked")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_execution_state",
        "content": "blocked",
        "confidence": 0.82,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-blocked",
    } in repository.conclusion_updates


async def test_reflection_worker_infers_progressing_goal_execution_state_from_done_update() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "task_status_update=fix deployment blocker:done; action=success; expression=One."},
            {"summary": "goal_update=ship the MVP this week; action=success; expression=Two."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = []
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-progress")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_execution_state",
        "content": "progressing",
        "confidence": 0.76,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-progress",
    } in repository.conclusion_updates


async def test_reflection_worker_infers_recovering_goal_execution_state_after_recent_done_with_remaining_work() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "task_status_update=fix deployment blocker:done; action=success; expression=One."},
            {"summary": "goal_update=ship the MVP this week; action=success; expression=Two."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 3, "goal_id": 1, "name": "finalize rollout checklist", "priority": "medium", "status": "todo"}
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-recovering")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_execution_state",
        "content": "recovering",
        "confidence": 0.77,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-recovering",
    } in repository.conclusion_updates


async def test_reflection_worker_infers_advancing_goal_execution_state_from_in_progress_task() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "task_status_update=finalize rollout checklist:in_progress; action=success; expression=One."},
            {"summary": "goal_update=ship the MVP this week; action=success; expression=Two."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 4, "goal_id": 1, "name": "finalize rollout checklist", "priority": "medium", "status": "in_progress"}
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-advancing")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_execution_state",
        "content": "advancing",
        "confidence": 0.75,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-advancing",
    } in repository.conclusion_updates


async def test_reflection_worker_derives_goal_progress_score_from_task_mix() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "task_status_update=fix deployment blocker:done; action=success; expression=One."},
            {"summary": "goal_update=ship the MVP this week; action=success; expression=Two."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 3, "goal_id": 1, "name": "finalize rollout checklist", "priority": "medium", "status": "in_progress"},
        {"id": 4, "goal_id": 1, "name": "prepare release notes", "priority": "medium", "status": "todo"},
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-progress-score")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_progress_score",
        "content": "0.65",
        "confidence": 0.74,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-progress-score",
    } in repository.conclusion_updates
    assert repository.goal_progress_snapshots == [
        {
            "id": 1,
            "user_id": "u-1",
            "goal_id": 1,
            "score": 0.65,
            "execution_state": "recovering",
            "progress_trend": None,
            "source_event_id": "evt-goal-progress-score",
        }
    ]


async def test_reflection_worker_derives_improving_goal_progress_trend_against_previous_score() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "task_status_update=fix deployment blocker:done; action=success; expression=One."},
            {"summary": "goal_update=ship the MVP this week; action=success; expression=Two."},
        ]
    )
    repository.runtime_preferences = {"goal_progress_score": 0.31}
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 3, "goal_id": 1, "name": "finalize rollout checklist", "priority": "medium", "status": "in_progress"},
        {"id": 4, "goal_id": 1, "name": "prepare release notes", "priority": "medium", "status": "todo"},
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-progress-improving")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_progress_trend",
        "content": "improving",
        "confidence": 0.73,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-progress-improving",
    } in repository.conclusion_updates


async def test_reflection_worker_derives_slipping_goal_progress_trend_against_previous_score() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "goal_update=ship the MVP this week; action=success; expression=One."},
            {"summary": "task_update=fix deployment blocker; action=success; expression=Two."},
        ]
    )
    repository.runtime_preferences = {"goal_progress_score": 0.82}
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 2, "goal_id": 1, "name": "fix deployment blocker", "priority": "high", "status": "blocked"},
        {"id": 3, "goal_id": 1, "name": "finalize rollout checklist", "priority": "medium", "status": "todo"},
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-progress-slipping")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_progress_trend",
        "content": "slipping",
        "confidence": 0.75,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-progress-slipping",
    } in repository.conclusion_updates


async def test_reflection_worker_derives_steady_goal_progress_trend_for_small_change() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "task_status_update=finalize rollout checklist:in_progress; action=success; expression=One."},
            {"summary": "goal_update=ship the MVP this week; action=success; expression=Two."},
        ]
    )
    repository.runtime_preferences = {"goal_progress_score": 0.67}
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 4, "goal_id": 1, "name": "finalize rollout checklist", "priority": "medium", "status": "in_progress"}
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-progress-steady")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_progress_trend",
        "content": "steady",
        "confidence": 0.7,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-progress-steady",
    } in repository.conclusion_updates


async def test_reflection_worker_infers_stagnating_goal_execution_state_from_repeated_planning_without_progress() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {
                "summary": (
                    "motivation=analyze; role=analyst; "
                    "plan_steps=interpret_event,review_context,break_down_problem,highlight_next_step,align_with_active_goal,prepare_response; "
                    "action=success; expression=One."
                )
            },
            {
                "summary": (
                    "motivation=analyze; role=analyst; "
                    "plan_steps=interpret_event,review_context,break_down_problem,highlight_next_step,align_with_active_goal,prepare_response; "
                    "action=success; expression=Two."
                )
            },
            {
                "summary": (
                    "motivation=respond; role=mentor; "
                    "plan_steps=interpret_event,review_context,offer_guidance,align_with_active_goal,prepare_response; "
                    "action=success; expression=Three."
                )
            },
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 2, "goal_id": 1, "name": "finalize deploy checklist", "priority": "medium", "status": "todo"}
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-stagnating")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_execution_state",
        "content": "stagnating",
        "confidence": 0.72,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-stagnating",
    } in repository.conclusion_updates


async def test_reflection_worker_enqueue_persists_durable_task() -> None:
    repository = FakeMemoryRepository(recent_memory=[])
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.enqueue(user_id="u-1", event_id="evt-queued")

    assert result is True
    assert repository.created_tasks == [
        {
            "id": 1,
            "user_id": "u-1",
            "event_id": "evt-queued",
            "status": "pending",
            "attempts": 0,
            "last_error": None,
        }
    ]


async def test_reflection_worker_recovers_pending_tasks_on_start() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "role=analyst; action=success; expression=One."},
            {"summary": "role=analyst; action=success; expression=Two."},
            {"summary": "role=executor; action=success; expression=Three."},
        ]
    )
    repository.pending_tasks = [
        {
            "id": 7,
            "user_id": "u-1",
            "event_id": "evt-pending",
            "status": "pending",
            "attempts": 0,
            "last_error": None,
        }
    ]
    worker = ReflectionWorker(memory_repository=repository, queue_size=5)

    await worker.start()
    await asyncio.sleep(0.05)
    await worker.stop()

    assert repository.processing_marks == [7]
    assert repository.completed_marks == [7]
    assert repository.failed_marks == []
    assert repository.theta_updates == [
        {
            "user_id": "u-1",
            "support_bias": 0.0,
            "analysis_bias": 0.67,
            "execution_bias": 0.33,
        }
    ]


async def test_reflection_worker_retries_failed_task_after_backoff_window() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "role=analyst; action=success; expression=One."},
            {"summary": "role=analyst; action=success; expression=Two."},
            {"summary": "role=executor; action=success; expression=Three."},
        ]
    )
    repository.pending_tasks = [
        {
            "id": 9,
            "user_id": "u-1",
            "event_id": "evt-failed-old",
            "status": "failed",
            "attempts": 1,
            "last_error": "temporary issue",
            "updated_at": datetime.now(timezone.utc) - timedelta(seconds=8),
        }
    ]
    worker = ReflectionWorker(memory_repository=repository, queue_size=5)

    await worker.start()
    await asyncio.sleep(0.05)
    await worker.stop()

    assert repository.processing_marks == [9]
    assert repository.completed_marks == [9]
    assert repository.failed_marks == []


async def test_reflection_worker_skips_failed_task_before_backoff_window() -> None:
    repository = FakeMemoryRepository(recent_memory=[])
    repository.pending_tasks = [
        {
            "id": 10,
            "user_id": "u-1",
            "event_id": "evt-failed-fresh",
            "status": "failed",
            "attempts": 1,
            "last_error": "temporary issue",
            "updated_at": datetime.now(timezone.utc),
        }
    ]
    worker = ReflectionWorker(memory_repository=repository, queue_size=5)

    scheduled = await worker._schedule_pending_tasks(limit=5)

    assert scheduled == 0
    assert repository.processing_marks == []
    assert repository.completed_marks == []


async def test_reflection_worker_stops_retrying_after_max_attempts() -> None:
    repository = FakeMemoryRepository(recent_memory=[])
    repository.pending_tasks = [
        {
            "id": 11,
            "user_id": "u-1",
            "event_id": "evt-failed-max",
            "status": "failed",
            "attempts": 3,
            "last_error": "permanent issue",
            "updated_at": datetime.now(timezone.utc) - timedelta(minutes=10),
        }
    ]
    worker = ReflectionWorker(memory_repository=repository, queue_size=5, max_attempts=3)

    scheduled = await worker._schedule_pending_tasks(limit=5)

    assert scheduled == 0
    assert repository.processing_marks == []
