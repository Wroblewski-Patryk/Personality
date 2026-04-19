import asyncio
from datetime import datetime, timedelta, timezone

from app.reflection.worker import ReflectionWorker


class FakeMemoryRepository:
    def __init__(self, recent_memory: list[dict]):
        self.recent_memory = recent_memory
        self.conclusion_updates: list[dict] = []
        self.raw_conclusion_updates: list[dict] = []
        self.relation_updates: list[dict] = []
        self.theta_updates: list[dict] = []
        self.runtime_preferences: dict = {}
        self.goal_progress_history: list[dict] = []
        self.goal_milestone_history: list[dict] = []
        self.goal_progress_snapshots: list[dict] = []
        self.created_tasks: list[dict] = []
        self.pending_tasks: list[dict] = []
        self.processing_marks: list[int] = []
        self.completed_marks: list[int] = []
        self.failed_marks: list[dict] = []
        self.active_goals: list[dict] = []
        self.active_tasks: list[dict] = []
        self.goal_milestones: list[dict] = []
        self.subconscious_proposals: list[dict] = []

    async def get_recent_for_user(self, user_id: str, limit: int = 8) -> list[dict]:
        return self.recent_memory[:limit]

    async def get_user_runtime_preferences(self, user_id: str) -> dict:
        return self.runtime_preferences

    async def get_recent_goal_progress(self, user_id: str, *, goal_ids: list[int] | None = None, limit: int = 6) -> list[dict]:
        rows = self.goal_progress_history[:]
        if goal_ids:
            rows = [row for row in rows if int(row.get("goal_id", -1)) in set(goal_ids)]
        return rows[:limit]

    async def get_recent_goal_milestone_history(
        self,
        user_id: str,
        *,
        goal_ids: list[int] | None = None,
        limit: int = 6,
    ) -> list[dict]:
        rows = self.goal_milestone_history[:]
        if goal_ids:
            rows = [row for row in rows if int(row.get("goal_id", -1)) in set(goal_ids)]
        return rows[:limit]

    async def append_goal_progress_snapshot(self, **kwargs) -> dict:
        payload = {"id": len(self.goal_progress_snapshots) + 1, **kwargs}
        self.goal_progress_snapshots.insert(0, payload)
        self.goal_progress_history.insert(0, payload)
        return payload

    async def upsert_conclusion(self, **kwargs) -> dict:
        self.raw_conclusion_updates.append(dict(kwargs))
        stripped = {
            key: value
            for key, value in kwargs.items()
            if key not in {"scope_type", "scope_key"}
        }
        self.conclusion_updates.append(stripped)
        return kwargs

    async def upsert_theta(self, **kwargs) -> dict:
        self.theta_updates.append(kwargs)
        return kwargs

    async def upsert_relation(self, **kwargs) -> dict:
        self.relation_updates.append(dict(kwargs))
        return kwargs

    async def upsert_subconscious_proposal(self, **kwargs) -> dict:
        payload = {
            "proposal_id": len(self.subconscious_proposals) + 1,
            "status": "pending",
            **kwargs,
        }
        self.subconscious_proposals.append(payload)
        return payload

    async def get_active_goals(self, user_id: str, limit: int = 5) -> list[dict]:
        return self.active_goals[:limit]

    async def get_active_tasks(self, user_id: str, limit: int = 8) -> list[dict]:
        return self.active_tasks[:limit]

    async def sync_goal_milestone(self, **kwargs) -> dict:
        payload = {
            "id": len(self.goal_milestones) + 1,
            "name": {
                "early_stage": "Establish goal foundation",
                "execution_phase": "Sustain active execution",
                "recovery_phase": "Stabilize goal recovery",
                "completion_window": "Drive goal to closure",
            }.get(kwargs["phase"], "Advance goal milestone"),
            "status": "active",
            **kwargs,
        }
        self.goal_milestones = [item for item in self.goal_milestones if not (item.get("goal_id") == kwargs["goal_id"] and item.get("status") == "active")]
        self.goal_milestones.insert(0, payload)
        return payload

    async def append_goal_milestone_history(self, **kwargs) -> dict:
        payload = {"id": len(self.goal_milestone_history) + 1, **kwargs}
        if self.goal_milestone_history:
            latest = self.goal_milestone_history[0]
            if (
                latest.get("goal_id") == kwargs.get("goal_id")
                and latest.get("milestone_name") == kwargs.get("milestone_name")
                and latest.get("phase") == kwargs.get("phase")
                and (latest.get("risk_level") or "") == (kwargs.get("risk_level") or "")
                and (latest.get("completion_criteria") or "") == (kwargs.get("completion_criteria") or "")
            ):
                return latest
        self.goal_milestone_history.insert(0, payload)
        return payload

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


async def test_reflection_worker_reads_structured_episode_payload_before_legacy_summary() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {
                "summary": "Readable summary only.",
                "payload": {
                    "payload_version": 1,
                    "event": "Reply in bullet points from now on.",
                    "memory_kind": "semantic",
                    "memory_topics": ["reply", "bullet", "points"],
                    "response_language": "en",
                    "preference_update": "response_style:structured",
                    "action": "success",
                    "expression": "- first\\n- second",
                },
            }
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-structured-payload")

    assert result is True
    assert repository.conclusion_updates == [
        {
            "user_id": "u-1",
            "kind": "response_style",
            "content": "structured",
            "confidence": 0.98,
            "source": "background_reflection",
            "supporting_event_id": "evt-structured-payload",
        }
    ]


async def test_reflection_worker_derives_read_only_subconscious_proposals_from_recent_memory() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {
                "summary": (
                    "event=Can you research deployment rollback options?; "
                    "task_status_update=deploy blocker:blocked; action=success; expression=Noted."
                )
            }
        ]
    )
    repository.active_tasks = [
        {
            "id": 9,
            "goal_id": 2,
            "name": "fix deploy blocker",
            "priority": "high",
            "status": "blocked",
        }
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-subconscious-proposals")

    assert result is True
    assert len(repository.subconscious_proposals) >= 3
    proposal_types = {item["proposal_type"] for item in repository.subconscious_proposals}
    assert "nudge_user" in proposal_types
    assert "ask_user" in proposal_types
    assert "research_topic" in proposal_types
    research_proposal = next(item for item in repository.subconscious_proposals if item["proposal_type"] == "research_topic")
    assert research_proposal["research_policy"] == "read_only"
    assert research_proposal["allowed_tools"] == [
        "memory_retrieval",
        "knowledge_search",
        "calendar_availability_read",
        "task_provider_read",
    ]


async def test_reflection_worker_derives_connector_expansion_proposal_from_repeated_unmet_connector_needs() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {
                "summary": (
                    "event=Can you sync my backlog with ClickUp?; "
                    "action=noop; expression=I can suggest steps but I cannot sync yet."
                )
            },
            {
                "summary": (
                    "event=Please connect this with ClickUp and create task there.; "
                    "action=success; expression=Noted."
                )
            },
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-connector-expansion")

    assert result is True
    connector_proposal = next(
        item for item in repository.subconscious_proposals if item["proposal_type"] == "suggest_connector_expansion"
    )
    assert connector_proposal["payload"]["connector_kind"] == "task_system"
    assert connector_proposal["payload"]["provider_hint"] == "clickup"
    assert connector_proposal["payload"]["requested_capability"] == "task_sync"
    assert connector_proposal["research_policy"] == "read_only"


async def test_reflection_worker_infers_preferred_role_from_repeated_role_usage() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "role=executor; task_status_update=deploy blocker:done; action=success; expression=Done one."},
            {"summary": "role=executor; task_status_update=release smoke:done; action=success; expression=Done two."},
            {"summary": "role=executor; task_status_update=docs update:done; action=success; expression=Done three."},
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
            {"summary": "role=analyst; task_status_update=analyze issue:done; action=success; expression=One."},
            {"summary": "role=analyst; task_status_update=verify issue:done; action=success; expression=Two."},
            {"summary": "role=executor; task_status_update=apply fix:done; action=success; expression=Three."},
            {"summary": "role=friend; task_status_update=support checkin:done; action=success; expression=Four."},
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
            {"summary": "event=Please walk me through this step by step.; task_status_update=doc outline:done; action=success; expression=One."},
            {"summary": "event=Can you explain this step by step?; task_status_update=test outline:done; action=success; expression=Two."},
            {"summary": "event=Guide me through this release checklist.; goal_update=ship the MVP this week; action=success; expression=Three."},
            {"summary": "event=Walk me through it step by step please.; task_update=final review checklist; action=success; expression=Four."},
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
            {"summary": "event=Just do it for me and ship it.; task_status_update=deploy prep:done; action=success; expression=One."},
            {"summary": "event=Take care of it and handle it for me.; task_status_update=smoke prep:done; action=success; expression=Two."},
            {"summary": "event=Please do it for me.; goal_update=ship the MVP this week; action=success; expression=Three."},
            {"summary": "event=Handle it and just ship it.; task_update=release handoff; action=success; expression=Four."},
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


async def test_reflection_worker_derives_relation_updates_from_recent_memory() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "collaboration_update=guided; affect_needs_support=true; action=success; expression=One."},
            {"summary": "collaboration_update=guided; affect_needs_support=true; action=success; expression=Two."},
            {"summary": "action=success; expression=Three."},
            {"summary": "action=success; expression=Four."},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-relations")

    assert result is True
    assert {
        "user_id": "u-1",
        "relation_type": "delivery_reliability",
        "relation_value": "high_trust",
        "confidence": 0.74,
        "source": "background_reflection",
        "supporting_event_id": "evt-relations",
        "scope_type": "global",
        "scope_key": "global",
        "evidence_count": 4,
        "decay_rate": 0.02,
    } in repository.relation_updates
    assert {
        "user_id": "u-1",
        "relation_type": "collaboration_dynamic",
        "relation_value": "guided",
        "confidence": 0.78,
        "source": "background_reflection",
        "supporting_event_id": "evt-relations",
        "scope_type": "global",
        "scope_key": "global",
        "evidence_count": 2,
        "decay_rate": 0.04,
    } in repository.relation_updates
    assert {
        "user_id": "u-1",
        "relation_type": "support_intensity_preference",
        "relation_value": "high_support",
        "confidence": 0.76,
        "source": "background_reflection",
        "supporting_event_id": "evt-relations",
        "scope_type": "global",
        "scope_key": "global",
        "evidence_count": 2,
        "decay_rate": 0.03,
    } in repository.relation_updates


async def test_reflection_worker_avoids_adaptive_inference_without_outcome_evidence() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "role=executor; action=success; expression=This is a longer response that should not be treated as concise output for adaptive updates."},
            {"summary": "role=executor; action=success; expression=This is another longer response that keeps adaptive inference from style-only feedback loops."},
            {"summary": "role=analyst; action=success; expression=This is a detailed explanatory response without explicit domain update markers."},
            {"summary": "role=executor; action=success; expression=This is still a long response without any explicit goal or task update evidence."},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-no-adaptive-evidence")

    assert result is True
    assert repository.theta_updates == []
    assert not any(
        update.get("kind") in {"preferred_role", "collaboration_preference"}
        for update in repository.conclusion_updates
    )


async def test_reflection_worker_derives_recurring_distress_affective_pattern() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {
                "payload": {
                    "payload_version": 1,
                    "event": "I am overwhelmed by this release",
                    "affect_label": "support_distress",
                    "affect_needs_support": True,
                    "action": "success",
                    "expression": "Let's break this down together.",
                }
            },
            {
                "payload": {
                    "payload_version": 1,
                    "event": "I still feel stressed",
                    "affect_label": "support_distress",
                    "affect_needs_support": True,
                    "action": "success",
                    "expression": "You're not alone in this.",
                }
            },
            {
                "payload": {
                    "payload_version": 1,
                    "event": "This keeps getting heavy",
                    "affect_label": "support_distress",
                    "affect_needs_support": True,
                    "action": "success",
                    "expression": "Let's choose one manageable next step.",
                }
            },
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-affective-recurring")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "affective_support_pattern",
        "content": "recurring_distress",
        "confidence": 0.76,
        "source": "background_reflection",
        "supporting_event_id": "evt-affective-recurring",
    } in repository.conclusion_updates
    assert {
        "user_id": "u-1",
        "kind": "affective_support_sensitivity",
        "content": "high",
        "confidence": 0.78,
        "source": "background_reflection",
        "supporting_event_id": "evt-affective-recurring",
    } in repository.conclusion_updates


async def test_reflection_worker_derives_confidence_recovery_affective_pattern() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {
                "payload": {
                    "payload_version": 1,
                    "event": "I feel better about this now",
                    "affect_label": "positive_engagement",
                    "affect_needs_support": False,
                    "action": "success",
                    "expression": "Great momentum.",
                }
            },
            {
                "payload": {
                    "payload_version": 1,
                    "event": "This is starting to click",
                    "affect_label": "positive_engagement",
                    "affect_needs_support": False,
                    "action": "success",
                    "expression": "Let's keep that confidence.",
                }
            },
            {
                "payload": {
                    "payload_version": 1,
                    "event": "I can handle the next step",
                    "affect_label": "positive_engagement",
                    "affect_needs_support": False,
                    "action": "success",
                    "expression": "Good progress.",
                }
            },
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-affective-recovery")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "affective_support_pattern",
        "content": "confidence_recovery",
        "confidence": 0.74,
        "source": "background_reflection",
        "supporting_event_id": "evt-affective-recovery",
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


async def test_reflection_worker_writes_goal_operational_conclusions_with_goal_scope() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "goal_update=ship the MVP this week; action=success; expression=One."},
            {"summary": "task_update=fix deployment blocker; action=success; expression=Two."},
        ]
    )
    repository.active_goals = [
        {"id": 11, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 2, "goal_id": 11, "name": "fix deployment blocker", "priority": "high", "status": "blocked"}
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-scope")

    assert result is True
    assert any(
        update.get("kind") == "goal_execution_state"
        and update.get("scope_type") == "goal"
        and update.get("scope_key") == "11"
        for update in repository.raw_conclusion_updates
    )


async def test_reflection_worker_infers_goal_milestone_transition_into_completion_window() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "task_status_update=stabilize release pipeline:done; action=success; expression=One."},
            {"summary": "task_status_update=verify release candidate:done; action=success; expression=Two."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 2, "goal_id": 1, "name": "prepare final rollout", "priority": "high", "status": "in_progress"}
    ]
    repository.goal_progress_history = [
        {"id": 11, "goal_id": 1, "score": 0.62, "execution_state": "advancing", "progress_trend": "improving"}
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-milestone")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_transition",
        "content": "entered_completion_window",
        "confidence": 0.77,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-milestone",
    } in repository.conclusion_updates
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_state",
        "content": "completion_window",
        "confidence": 0.8,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-milestone",
    } in repository.conclusion_updates
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_risk",
        "content": "ready_to_close",
        "confidence": 0.79,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-milestone",
    } in repository.conclusion_updates
    assert {
        "user_id": "u-1",
        "kind": "goal_completion_criteria",
        "content": "finish_remaining_active_work",
        "confidence": 0.8,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-milestone",
    } in repository.conclusion_updates


async def test_reflection_worker_infers_goal_milestone_transition_out_of_completion_window() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "goal_update=ship the MVP this week; action=success; expression=One."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 2, "goal_id": 1, "name": "fix release blocker", "priority": "high", "status": "blocked"}
    ]
    repository.goal_progress_history = [
        {"id": 12, "goal_id": 1, "score": 0.86, "execution_state": "advancing", "progress_trend": "steady"}
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-slip")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_transition",
        "content": "slipped_from_completion_window",
        "confidence": 0.78,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-slip",
    } in repository.conclusion_updates
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_risk",
        "content": "at_risk",
        "confidence": 0.81,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-slip",
    } in repository.conclusion_updates
    assert {
        "user_id": "u-1",
        "kind": "goal_completion_criteria",
        "content": "resolve_remaining_blocker",
        "confidence": 0.82,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-slip",
    } in repository.conclusion_updates


async def test_reflection_worker_infers_goal_milestone_recovery_phase() -> None:
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

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-recovery-phase")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_state",
        "content": "recovery_phase",
        "confidence": 0.76,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-recovery-phase",
    } in repository.conclusion_updates
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_risk",
        "content": "stabilizing",
        "confidence": 0.74,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-recovery-phase",
    } in repository.conclusion_updates
    assert {
        "user_id": "u-1",
        "kind": "goal_completion_criteria",
        "content": "stabilize_remaining_work",
        "confidence": 0.76,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-recovery-phase",
    } in repository.conclusion_updates
    assert repository.goal_milestones[0]["goal_id"] == 1
    assert repository.goal_milestones[0]["phase"] == "recovery_phase"
    assert repository.goal_milestone_history[0]["goal_id"] == 1
    assert repository.goal_milestone_history[0]["phase"] == "recovery_phase"
    assert repository.goal_milestone_history[0]["risk_level"] == "stabilizing"
    assert repository.goal_milestone_history[0]["completion_criteria"] == "stabilize_remaining_work"


async def test_reflection_worker_infers_early_stage_completion_criteria() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "goal_update=ship the MVP this week; action=success; expression=One."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = []
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-early-stage")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_state",
        "content": "early_stage",
        "confidence": 0.7,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-early-stage",
    } in repository.conclusion_updates
    assert {
        "user_id": "u-1",
        "kind": "goal_completion_criteria",
        "content": "define_first_execution_step",
        "confidence": 0.72,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-early-stage",
    } in repository.conclusion_updates


async def test_reflection_worker_appends_distinct_goal_milestone_history_snapshots() -> None:
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

    first = await worker.reflect_user(user_id="u-1", event_id="evt-goal-history-1")
    assert first is True

    repository.recent_memory = [
        {"summary": "task_status_update=finalize rollout checklist:in_progress; action=success; expression=Three."},
        {"summary": "goal_update=ship the MVP this week; action=success; expression=Four."},
    ]
    repository.active_tasks = [
        {"id": 3, "goal_id": 1, "name": "finalize rollout checklist", "priority": "medium", "status": "in_progress"}
    ]
    second = await worker.reflect_user(user_id="u-1", event_id="evt-goal-history-2")

    assert second is True
    assert len(repository.goal_milestone_history) == 2
    assert repository.goal_milestone_history[0]["phase"] == "execution_phase"
    assert repository.goal_milestone_history[1]["phase"] == "recovery_phase"


async def test_reflection_worker_derives_reentered_completion_window_milestone_arc() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "task_status_update=finalize rollout checklist:done; action=success; expression=One."},
            {"summary": "goal_update=ship the MVP this week; action=success; expression=Two."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = []
    repository.goal_progress_history = [
        {"id": 11, "goal_id": 1, "score": 0.62, "execution_state": "recovering", "progress_trend": "improving"}
    ]
    repository.goal_milestone_history = [
        {
            "id": 2,
            "goal_id": 1,
            "milestone_name": "Stabilize goal recovery",
            "phase": "recovery_phase",
            "risk_level": "stabilizing",
            "completion_criteria": "stabilize_remaining_work",
        },
        {
            "id": 1,
            "goal_id": 1,
            "milestone_name": "Drive goal to closure",
            "phase": "completion_window",
            "risk_level": "ready_to_close",
            "completion_criteria": "finish_remaining_active_work",
        },
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-milestone-arc")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_arc",
        "content": "reentered_completion_window",
        "confidence": 0.79,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-milestone-arc",
    } in repository.conclusion_updates


async def test_reflection_worker_derives_lingering_completion_milestone_pressure() -> None:
    now = datetime.now(timezone.utc)
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "goal_update=ship the MVP this week; action=success; expression=One."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = []
    repository.runtime_preferences = {"goal_progress_score": 0.82}
    repository.goal_progress_history = [
        {"id": 11, "goal_id": 1, "score": 0.82, "execution_state": "advancing", "progress_trend": "steady"}
    ]
    repository.goal_milestone_history = [
        {
            "id": 3,
            "goal_id": 1,
            "milestone_name": "Drive goal to closure",
            "phase": "completion_window",
            "risk_level": "ready_to_close",
            "completion_criteria": "confirm_goal_completion",
            "created_at": now - timedelta(hours=20),
        },
        {
            "id": 2,
            "goal_id": 1,
            "milestone_name": "Drive goal to closure",
            "phase": "completion_window",
            "risk_level": "ready_to_close",
            "completion_criteria": "confirm_goal_completion",
            "created_at": now - timedelta(hours=10),
        },
        {
            "id": 1,
            "goal_id": 1,
            "milestone_name": "Drive goal to closure",
            "phase": "completion_window",
            "risk_level": "ready_to_close",
            "completion_criteria": "confirm_goal_completion",
            "created_at": now - timedelta(hours=2),
        },
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-milestone-pressure")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_pressure",
        "content": "lingering_completion",
        "confidence": 0.8,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-milestone-pressure",
    } in repository.conclusion_updates


async def test_reflection_worker_prunes_time_only_lingering_completion_pressure_signal() -> None:
    now = datetime.now(timezone.utc)
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "goal_update=ship the MVP this week; action=success; expression=One."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = []
    repository.runtime_preferences = {"goal_progress_score": 0.82}
    repository.goal_progress_history = [
        {"id": 11, "goal_id": 1, "score": 0.82, "execution_state": "advancing", "progress_trend": "steady"}
    ]
    repository.goal_milestone_history = [
        {
            "id": 1,
            "goal_id": 1,
            "milestone_name": "Drive goal to closure",
            "phase": "completion_window",
            "risk_level": "ready_to_close",
            "completion_criteria": "confirm_goal_completion",
            "created_at": now - timedelta(hours=36),
        }
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-pruned-milestone-pressure")

    assert result is True
    assert not any(update.get("kind") == "goal_milestone_pressure" for update in repository.conclusion_updates)


async def test_reflection_worker_derives_multi_step_milestone_dependency_state() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "goal_update=ship the MVP this week; action=success; expression=One."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 2, "goal_id": 1, "name": "finish rollout checklist", "priority": "medium", "status": "in_progress"},
        {"id": 3, "goal_id": 1, "name": "verify final smoke test", "priority": "medium", "status": "todo"},
    ]
    repository.runtime_preferences = {"goal_progress_score": 0.82}
    repository.goal_progress_history = [
        {"id": 11, "goal_id": 1, "score": 0.82, "execution_state": "advancing", "progress_trend": "steady"}
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-milestone-dependency")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_dependency_state",
        "content": "multi_step_dependency",
        "confidence": 0.76,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-milestone-dependency",
    } in repository.conclusion_updates


async def test_reflection_worker_derives_dependency_due_next_milestone_due_state() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "task_status_update=stabilize release notes:done; action=success; expression=One."},
            {"summary": "task_status_update=prepare handoff summary:done; action=success; expression=Two."},
            {"summary": "task_status_update=review rollout readiness:done; action=success; expression=Three."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = [
        {"id": 2, "goal_id": 1, "name": "finish rollout checklist", "priority": "medium", "status": "in_progress"},
        {"id": 3, "goal_id": 1, "name": "verify final smoke test", "priority": "medium", "status": "todo"},
    ]
    repository.runtime_preferences = {"goal_progress_score": 0.82}
    repository.goal_progress_history = [
        {"id": 11, "goal_id": 1, "score": 0.82, "execution_state": "advancing", "progress_trend": "steady"}
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-milestone-due")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_due_state",
        "content": "dependency_due_next",
        "confidence": 0.79,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-milestone-due",
    } in repository.conclusion_updates


async def test_reflection_worker_derives_overdue_due_window_from_lingering_completion() -> None:
    now = datetime.now(timezone.utc)
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "task_status_update=stabilize release notes:done; action=success; expression=One."},
            {"summary": "task_status_update=prepare handoff summary:done; action=success; expression=Two."},
            {"summary": "task_status_update=review rollout readiness:done; action=success; expression=Three."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"}
    ]
    repository.active_tasks = []
    repository.runtime_preferences = {"goal_progress_score": 0.82}
    repository.goal_progress_history = [
        {"id": 11, "goal_id": 1, "score": 0.82, "execution_state": "advancing", "progress_trend": "steady"}
    ]
    repository.goal_milestone_history = [
        {
            "id": 3,
            "goal_id": 1,
            "milestone_name": "Drive goal to closure",
            "phase": "completion_window",
            "risk_level": "ready_to_close",
            "completion_criteria": "confirm_goal_completion",
            "created_at": now - timedelta(hours=20),
        },
        {
            "id": 2,
            "goal_id": 1,
            "milestone_name": "Drive goal to closure",
            "phase": "completion_window",
            "risk_level": "ready_to_close",
            "completion_criteria": "confirm_goal_completion",
            "created_at": now - timedelta(hours=10),
        },
        {
            "id": 1,
            "goal_id": 1,
            "milestone_name": "Drive goal to closure",
            "phase": "completion_window",
            "risk_level": "ready_to_close",
            "completion_criteria": "confirm_goal_completion",
            "created_at": now - timedelta(hours=2),
        },
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-milestone-due-window")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_milestone_due_window",
        "content": "overdue_due_window",
        "confidence": 0.82,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-milestone-due-window",
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


async def test_reflection_worker_scopes_goal_conclusions_to_goal_matched_by_recent_turn_hints() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "event=I fixed invoice import for tax filing.; task_status_update=prepare tax documents:done; action=success; expression=One."},
            {"summary": "event=Need to close tax filing soon.; task_update=prepare tax documents; action=success; expression=Two."},
        ]
    )
    repository.active_goals = [
        {"id": 1, "name": "ship the MVP this week", "priority": "high", "status": "active", "goal_type": "operational"},
        {"id": 2, "name": "close tax filing", "priority": "medium", "status": "active", "goal_type": "operational"},
    ]
    repository.active_tasks = [
        {"id": 5, "goal_id": 2, "name": "prepare tax documents", "priority": "high", "status": "todo"},
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-scope-match")

    assert result is True
    goal_execution_updates = [
        update
        for update in repository.raw_conclusion_updates
        if update.get("kind") == "goal_execution_state"
    ]
    assert any(update.get("scope_type") == "goal" and update.get("scope_key") == "2" for update in goal_execution_updates)
    assert not any(update.get("scope_type") == "goal" and update.get("scope_key") == "1" for update in goal_execution_updates)


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
    repository.goal_progress_history = [
        {"id": 1, "goal_id": 1, "score": 0.31, "execution_state": "blocked"}
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
    assert {
        "user_id": "u-1",
        "kind": "goal_progress_arc",
        "content": "recovery_gaining_traction",
        "confidence": 0.76,
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


async def test_reflection_worker_derives_unstable_goal_progress_arc_from_whiplash_history() -> None:
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
        {"id": 3, "goal_id": 1, "name": "finalize rollout checklist", "priority": "medium", "status": "in_progress"},
    ]
    repository.goal_progress_history = [
        {"id": 3, "goal_id": 1, "score": 0.64, "execution_state": "advancing"},
        {"id": 2, "goal_id": 1, "score": 0.19, "execution_state": "blocked"},
        {"id": 1, "goal_id": 1, "score": 0.58, "execution_state": "recovering"},
    ]
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-goal-progress-unstable")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "goal_progress_arc",
        "content": "unstable_progress",
        "confidence": 0.74,
        "source": "background_reflection",
        "supporting_event_id": "evt-goal-progress-unstable",
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


async def test_reflection_worker_enqueue_can_skip_in_process_dispatch() -> None:
    repository = FakeMemoryRepository(recent_memory=[])
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.enqueue(user_id="u-1", event_id="evt-queued-deferred", dispatch=False)

    assert result is True
    assert repository.created_tasks == [
        {
            "id": 1,
            "user_id": "u-1",
            "event_id": "evt-queued-deferred",
            "status": "pending",
            "attempts": 0,
            "last_error": None,
        }
    ]
    assert worker.queue.qsize() == 0


async def test_reflection_worker_run_pending_once_processes_ready_tasks_without_start_loop() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "role=analyst; task_status_update=analysis pass:done; action=success; expression=One."},
            {"summary": "role=analyst; task_status_update=analysis followup:done; action=success; expression=Two."},
            {"summary": "role=executor; task_status_update=execution handoff:done; action=success; expression=Three."},
        ]
    )
    repository.pending_tasks = [
        {
            "id": 13,
            "user_id": "u-1",
            "event_id": "evt-drain-once",
            "status": "pending",
            "attempts": 0,
            "last_error": None,
        }
    ]
    worker = ReflectionWorker(memory_repository=repository, queue_size=5)

    summary = await worker.run_pending_once(limit=5)

    assert summary == {
        "scanned": 1,
        "processed": 1,
        "completed": 1,
        "failed": 0,
        "skipped_not_ready": 0,
    }
    assert repository.processing_marks == [13]
    assert repository.completed_marks == [13]
    assert repository.failed_marks == []


async def test_reflection_worker_recovers_pending_tasks_on_start() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "role=analyst; task_status_update=analysis pass:done; action=success; expression=One."},
            {"summary": "role=analyst; task_status_update=analysis followup:done; action=success; expression=Two."},
            {"summary": "role=executor; task_status_update=execution handoff:done; action=success; expression=Three."},
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
            {"summary": "role=analyst; task_status_update=analysis pass:done; action=success; expression=One."},
            {"summary": "role=analyst; task_status_update=analysis followup:done; action=success; expression=Two."},
            {"summary": "role=executor; task_status_update=execution handoff:done; action=success; expression=Three."},
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
