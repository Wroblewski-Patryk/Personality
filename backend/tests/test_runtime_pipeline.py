import json
from datetime import datetime, timedelta, timezone

import pytest

from app.affective.assessor import AffectiveAssessor
from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.core.action import ActionExecutor
from app.core.behavior_harness import (
    BehaviorScenarioCheck,
    BehaviorScenarioDefinition,
    behavior_results_as_jsonable,
    execute_behavior_scenarios,
)
from app.core.contracts import Event, EventMeta, MotivationOutput, NoopDomainIntent
from app.core.events import build_scheduler_event
from app.core.reflection_scope_policy import (
    conclusion_matches_scope_request,
    normalize_scope,
    relation_matches_scope_request,
)
from app.core.runtime import RuntimeOrchestrator
from app.expression.generator import ExpressionAgent
from app.motivation.engine import MotivationEngine
from app.workers.scheduler import SchedulerWorker
from tests.empathy_fixtures import EMPATHY_SUPPORT_SCENARIOS


class FakeMemoryRepository:
    def __init__(self, recent_memory: list[dict] | None = None, user_profile: dict | None = None):
        self.recent_memory = recent_memory or []
        self.recent_limits: list[int] = []
        self.user_profile = user_profile
        self.auth_user: dict | None = None
        self.profile_updates: list[dict] = []
        self.conclusion_updates: list[dict] = []
        self.relation_updates: list[dict] = []
        self.user_preferences: dict = {}
        self.scoped_user_preferences: dict[tuple[str, str], dict] = {}
        self.user_conclusions: list[dict] = []
        self.scoped_user_conclusions: list[dict] = []
        self.user_theta: dict | None = None
        self.active_goals: list[dict] = []
        self.active_tasks: list[dict] = []
        self.active_planned_work: list[dict] = []
        self.active_goal_milestones: list[dict] = []
        self.goal_milestone_history: list[dict] = []
        self.goal_progress_history: list[dict] = []
        self.reflection_tasks: list[dict] = []
        self.reflection_stats = {
            "total": 0,
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "retryable_failed": 0,
            "exhausted_failed": 0,
            "stuck_processing": 0,
        }
        self.pending_subconscious_proposals: list[dict] = []
        self.resolved_subconscious_proposals: list[dict] = []
        self.proactive_candidates: list[dict] = []
        self.planned_work_due_updates: list[dict] = []
        self.planned_work_recurrence_updates: list[dict] = []


    async def get_recent_for_user(self, user_id: str, limit: int = 5) -> list[dict]:
        self.recent_limits.append(limit)
        return [
            item
            for item in self.recent_memory
            if not item.get("user_id") or str(item.get("user_id")) == str(user_id)
        ][:limit]

    async def get_recent_chat_transcript_for_user(self, user_id: str, limit: int = 10) -> list[dict]:
        normalized_limit = max(1, int(limit))
        recent_items = await self.get_recent_for_user(user_id=user_id, limit=max(normalized_limit, 10))
        transcript_items: list[dict] = []
        for memory_item in recent_items:
            payload = memory_item.get("payload") if isinstance(memory_item.get("payload"), dict) else {}
            event_id = str(memory_item.get("event_id", "") or "").strip()
            timestamp = memory_item.get("event_timestamp") or memory_item.get("timestamp")
            channel = "telegram" if str(memory_item.get("source", "")).strip().lower() == "telegram" else "api"
            event_text = str(payload.get("event", "") or "").strip()
            expression_text = str(payload.get("expression", "") or "").strip()
            response_language = str(payload.get("response_language", "") or payload.get("language", "") or "").strip()
            if event_text:
                transcript_items.append(
                    {
                        "message_id": f"{event_id}:user",
                        "event_id": event_id,
                        "role": "user",
                        "text": event_text,
                        "channel": channel,
                        "timestamp": timestamp,
                    }
                )
            if expression_text:
                item = {
                    "message_id": f"{event_id}:assistant",
                    "event_id": event_id,
                    "role": "assistant",
                    "text": expression_text,
                    "channel": channel,
                    "timestamp": timestamp,
                }
                if response_language:
                    item["metadata"] = {"language": response_language}
                transcript_items.append(item)
        transcript_items.sort(key=lambda item: item["timestamp"])
        return transcript_items[-normalized_limit:]

    async def get_user_profile(self, user_id: str) -> dict | None:
        return self.user_profile

    async def get_auth_user_by_id(self, user_id: str) -> dict | None:
        return self.auth_user

    async def get_user_runtime_preferences(
        self,
        user_id: str,
        *,
        scope_type: str | None = None,
        scope_key: str | None = None,
        include_global: bool = True,
    ) -> dict:
        normalized_scope_type, normalized_scope_key = self._normalize_scope(scope_type=scope_type, scope_key=scope_key)
        if scope_type is None and scope_key is None:
            return self.user_preferences
        if normalized_scope_type == "global":
            return self.user_preferences
        scoped = {
            key: value
            for key, value in self.scoped_user_preferences.get((normalized_scope_type, normalized_scope_key), {}).items()
            if conclusion_matches_scope_request(
                kind=key.removesuffix("_confidence").removesuffix("_source").removesuffix("_updated_at").removesuffix("_scope_type").removesuffix("_scope_key"),
                row_scope_type=normalized_scope_type,
                row_scope_key=normalized_scope_key,
                requested_scope_type=scope_type,
                requested_scope_key=scope_key,
                include_global=include_global,
            )
        }
        if include_global:
            merged = dict(self.user_preferences)
            merged.update(scoped)
            return merged
        return dict(scoped)

    async def get_user_conclusions(
        self,
        user_id: str,
        limit: int = 3,
        *,
        scope_type: str | None = None,
        scope_key: str | None = None,
        include_global: bool = False,
    ) -> list[dict]:
        rows = [*self.user_conclusions, *self.scoped_user_conclusions]
        if scope_type is None and scope_key is None:
            return rows[:limit]
        filtered_rows = [
            row
            for row in rows
            if conclusion_matches_scope_request(
                kind=str(row.get("kind", "")),
                row_scope_type=str(row.get("scope_type", "global")),
                row_scope_key=str(row.get("scope_key", "global")),
                requested_scope_type=scope_type,
                requested_scope_key=scope_key,
                include_global=include_global,
            )
        ]
        return filtered_rows[:limit]

    async def get_user_theta(self, user_id: str) -> dict | None:
        return self.user_theta

    async def get_active_goals(self, user_id: str, limit: int = 5) -> list[dict]:
        return self.active_goals[:limit]

    async def get_active_tasks(self, user_id: str, *, goal_ids: list[int] | None = None, limit: int = 5) -> list[dict]:
        active = [task for task in self.active_tasks if task.get("status") in {"todo", "in_progress", "blocked"}]
        if goal_ids:
            goal_linked = [task for task in active if task.get("goal_id") in set(goal_ids)]
            rest = [task for task in active if task.get("goal_id") not in set(goal_ids)]
            return (goal_linked + rest)[:limit]
        return active[:limit]

    async def get_active_planned_work(
        self,
        user_id: str,
        *,
        goal_ids: list[int] | None = None,
        task_ids: list[int] | None = None,
        limit: int = 8,
    ) -> list[dict]:
        rows = [item for item in self.active_planned_work if item.get("status") in {"pending", "due", "snoozed"}]
        goal_id_set = {goal_id for goal_id in (goal_ids or []) if goal_id is not None}
        task_id_set = {task_id for task_id in (task_ids or []) if task_id is not None}
        if goal_id_set:
            rows = [item for item in rows if item.get("goal_id") in goal_id_set or item.get("goal_id") is None]
        if task_id_set:
            rows = [item for item in rows if item.get("task_id") in task_id_set or item.get("task_id") is None]
        return rows[:limit]

    async def get_active_goal_milestones(self, user_id: str, *, goal_ids: list[int] | None = None, limit: int = 6) -> list[dict]:
        rows = [item for item in self.active_goal_milestones if item.get("status") == "active"]
        if goal_ids:
            rows = [row for row in rows if row.get("goal_id") in set(goal_ids)]
        return rows[:limit]

    async def get_pending_subconscious_proposals(self, user_id: str, limit: int = 8) -> list[dict]:
        return self.pending_subconscious_proposals[:limit]

    async def upsert_subconscious_proposal(self, **kwargs) -> dict:
        proposal_type = str(kwargs.get("proposal_type", "nudge_user"))
        summary = str(kwargs.get("summary", ""))
        existing = next(
            (
                proposal
                for proposal in self.pending_subconscious_proposals
                if str(proposal.get("proposal_type", "")) == proposal_type
                and str(proposal.get("summary", "")) == summary
                and str(proposal.get("status", "pending")) in {"pending", "deferred"}
            ),
            None,
        )
        if existing is not None:
            existing.update(kwargs)
            return dict(existing)
        payload = {
            "proposal_id": len(self.pending_subconscious_proposals) + 1,
            "status": "pending",
            **kwargs,
        }
        self.pending_subconscious_proposals.append(payload)
        return payload

    async def resolve_subconscious_proposal(
        self,
        *,
        proposal_id: int,
        decision: str,
        reason: str,
    ) -> dict | None:
        payload = {
            "proposal_id": proposal_id,
            "decision": decision,
            "reason": reason,
        }
        self.resolved_subconscious_proposals.append(payload)
        for proposal in self.pending_subconscious_proposals:
            if int(proposal.get("proposal_id", -1)) == proposal_id:
                proposal["status"] = {
                    "accept": "accepted",
                    "merge": "merged",
                    "defer": "deferred",
                    "discard": "discarded",
                }.get(decision, "pending")
                proposal["decision_reason"] = reason
                return dict(proposal)
        return None

    async def get_recent_goal_progress(self, user_id: str, *, goal_ids: list[int] | None = None, limit: int = 6) -> list[dict]:
        rows = self.goal_progress_history[:]
        if goal_ids:
            rows = [row for row in rows if int(row.get("goal_id", -1)) in set(goal_ids)]
        return rows[:limit]

    async def get_recent_goal_milestone_history(self, user_id: str, *, goal_ids: list[int] | None = None, limit: int = 6) -> list[dict]:
        rows = self.goal_milestone_history[:]
        if goal_ids:
            rows = [row for row in rows if int(row.get("goal_id", -1)) in set(goal_ids)]
        return rows[:limit]

    def _normalize_scope(self, *, scope_type: str | None, scope_key: str | None) -> tuple[str, str]:
        return normalize_scope(scope_type=scope_type, scope_key=scope_key)

    async def write_episode(self, **kwargs) -> dict:
        return {
            "id": 1,
            "event_id": kwargs["event_id"],
            "timestamp": kwargs["event_timestamp"],
            "summary": kwargs["summary"],
            "payload": kwargs["payload"],
            "importance": kwargs["importance"],
        }

    async def upsert_user_profile_language(self, **kwargs) -> dict:
        self.profile_updates.append(kwargs)
        return kwargs

    async def upsert_conclusion(self, **kwargs) -> dict:
        self.conclusion_updates.append(kwargs)
        kind = str(kwargs.get("kind", "")).strip().lower()
        payload = {
            "kind": kwargs.get("kind"),
            "content": kwargs.get("content"),
            "confidence": kwargs.get("confidence"),
            "source": kwargs.get("source"),
            "supporting_event_id": kwargs.get("supporting_event_id"),
            "scope_type": kwargs.get("scope_type", "global"),
            "scope_key": kwargs.get("scope_key", "global"),
        }
        existing_index = next(
            (
                index
                for index, row in enumerate(self.user_conclusions)
                if str(row.get("kind", "")).strip().lower() == kind
                and str(row.get("scope_type", "global")) == str(payload["scope_type"])
                and str(row.get("scope_key", "global")) == str(payload["scope_key"])
            ),
            None,
        )
        if existing_index is None:
            self.user_conclusions.append(payload)
        else:
            self.user_conclusions[existing_index] = payload
        if kind == "proactive_opt_in":
            value = str(kwargs.get("content", "")).strip().lower() in {"1", "true", "yes", "on"}
            self.user_preferences["proactive_opt_in"] = value
            self.user_preferences["proactive_opt_in_confidence"] = kwargs.get("confidence")
            self.user_preferences["proactive_opt_in_source"] = kwargs.get("source")
        return kwargs

    async def upsert_relation(self, **kwargs) -> dict:
        payload = {"id": len(self.relation_updates) + 1, **kwargs}
        self.relation_updates.append(payload)
        return payload

    async def upsert_theta(self, **kwargs) -> dict:
        self.user_theta = kwargs
        return kwargs

    async def upsert_active_goal(self, **kwargs) -> dict:
        payload = {
            "id": len(self.active_goals) + 1,
            "status": "active",
            "goal_type": kwargs.get("goal_type", "tactical"),
            **kwargs,
        }
        self.active_goals.append(payload)
        return payload

    async def upsert_active_task(self, **kwargs) -> dict:
        payload = {
            "id": len(self.active_tasks) + 1,
            "status": kwargs.get("status", "todo"),
            **kwargs,
        }
        self.active_tasks.append(payload)
        return payload

    async def upsert_planned_work_item(self, **kwargs) -> dict:
        payload = {
            "id": len(self.active_planned_work) + 1,
            "status": "pending",
            **kwargs,
        }
        self.active_planned_work.append(payload)
        return payload

    async def reschedule_planned_work_item(self, *, work_id: int, **kwargs) -> dict | None:
        for item in self.active_planned_work:
            if int(item["id"]) == work_id:
                item["status"] = "pending"
                item.update(kwargs)
                return item
        return None

    async def cancel_planned_work_item(self, *, work_id: int) -> dict | None:
        for item in self.active_planned_work:
            if int(item["id"]) == work_id:
                item["status"] = "cancelled"
                return item
        return None

    async def complete_planned_work_item(self, *, work_id: int) -> dict | None:
        for item in self.active_planned_work:
            if int(item["id"]) == work_id:
                item["status"] = "completed"
                return item
        return None

    async def get_due_planned_work(self, *, now: datetime | None = None, limit: int = 8) -> list[dict]:
        due_at = now or datetime.now(timezone.utc)
        rows: list[dict] = []
        for item in self.active_planned_work:
            if item.get("status") not in {"pending", "snoozed"}:
                continue
            preferred_at = item.get("preferred_at")
            not_before = item.get("not_before")
            if preferred_at is not None and preferred_at <= due_at:
                rows.append(item)
                continue
            if preferred_at is None and not_before is not None and not_before <= due_at:
                rows.append(item)
        return rows[:limit]

    async def mark_planned_work_due(self, *, work_id: int, evaluated_at: datetime | None = None) -> dict | None:
        for item in self.active_planned_work:
            if int(item["id"]) == work_id:
                item["status"] = "due"
                item["last_evaluated_at"] = evaluated_at
                payload = {
                    "work_id": work_id,
                    "status": "due",
                    "evaluated_at": evaluated_at,
                }
                self.planned_work_due_updates.append(payload)
                return item
        return None

    async def advance_planned_work_recurrence(
        self,
        *,
        work_id: int,
        evaluated_at: datetime | None = None,
    ) -> dict | None:
        for item in self.active_planned_work:
            if int(item["id"]) != work_id:
                continue
            mode = str(item.get("recurrence_mode", "none")).strip().lower()
            if mode == "daily":
                delta_seconds = 86400
            elif mode == "weekly":
                delta_seconds = 7 * 86400
            else:
                delta_seconds = 0
            preferred_at = item.get("preferred_at") or evaluated_at or datetime.now(timezone.utc)
            next_preferred_at = preferred_at
            if delta_seconds > 0:
                next_preferred_at = preferred_at + timedelta(seconds=delta_seconds)
            item["status"] = "pending"
            item["preferred_at"] = next_preferred_at
            item["not_before"] = next_preferred_at
            item["last_evaluated_at"] = evaluated_at
            payload = {
                "work_id": work_id,
                "recurrence_mode": mode,
                "preferred_at": next_preferred_at,
                "evaluated_at": evaluated_at,
            }
            self.planned_work_recurrence_updates.append(payload)
            return item
        return None

    async def sync_goal_milestone(self, **kwargs) -> dict:
        payload = {
            "id": len(self.active_goal_milestones) + 1,
            "name": {
                "early_stage": "Establish goal foundation",
                "execution_phase": "Sustain active execution",
                "recovery_phase": "Stabilize goal recovery",
                "completion_window": "Drive goal to closure",
            }.get(kwargs["phase"], "Advance goal milestone"),
            "status": "active",
            **kwargs,
        }
        self.active_goal_milestones = [
            item
            for item in self.active_goal_milestones
            if not (item.get("goal_id") == kwargs["goal_id"] and item.get("status") == "active")
        ]
        self.active_goal_milestones.append(payload)
        return payload

    async def append_goal_milestone_history(self, **kwargs) -> dict:
        payload = {"id": len(self.goal_milestone_history) + 1, "created_at": datetime.now(timezone.utc), **kwargs}
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

    async def update_task_status(self, *, task_id: int, status: str) -> dict | None:
        for task in self.active_tasks:
            if int(task["id"]) == task_id:
                task["status"] = status
                return task
        return None

    async def enqueue_reflection_task(self, user_id: str, event_id: str) -> dict:
        for task in self.reflection_tasks:
            if task["event_id"] == event_id:
                if task["status"] != "completed":
                    task["user_id"] = user_id
                    task["status"] = "pending"
                    task["last_error"] = None
                return dict(task)
        task = {
            "id": len(self.reflection_tasks) + 1,
            "user_id": user_id,
            "event_id": event_id,
            "status": "pending",
            "attempts": 0,
            "last_error": None,
        }
        self.reflection_tasks.append(task)
        return dict(task)

    async def get_proactive_scheduler_candidates(
        self,
        *,
        proactive_interval_seconds: int,
        limit: int = 8,
    ) -> list[dict]:
        return self.proactive_candidates[:limit]

    async def get_reflection_task_stats(
        self,
        *,
        max_attempts: int,
        stuck_after_seconds: int,
        retry_backoff_seconds: tuple[int, ...],
        now=None,
    ) -> dict[str, int]:
        return dict(self.reflection_stats)


class PersistingFakeMemoryRepository(FakeMemoryRepository):
    async def write_episode(self, **kwargs) -> dict:
        record = await super().write_episode(**kwargs)
        self.recent_memory.insert(
            0,
            {
                "event_id": record["event_id"],
                "user_id": kwargs["user_id"],
                "source": kwargs["source"],
                "event_timestamp": kwargs["event_timestamp"],
                "timestamp": record["timestamp"],
                "summary": record["summary"],
                "payload": dict(record["payload"]),
                "importance": record["importance"],
            },
        )
        return record


class FailingWriteMemoryRepository(FakeMemoryRepository):
    async def write_episode(self, **kwargs) -> dict:
        raise RuntimeError("database unavailable")


class FakeClickUpTaskClient:
    def __init__(self, *, ready: bool = True, error: Exception | None = None):
        self.ready = ready
        self.error = error
        self.calls: list[dict[str, str]] = []

    async def list_tasks(self, *, limit: int = 10) -> list[dict]:
        self.calls.append({"operation": "list_tasks", "limit": str(limit)})
        if self.error is not None:
            raise self.error
        return [
            {"id": "clk_1", "name": "Release checklist"},
            {"id": "clk_2", "name": "Docs sync"},
        ]

    async def update_task(self, *, task_id: str, status: str) -> dict:
        self.calls.append({"operation": "update_task", "task_id": task_id, "status": status})
        if self.error is not None:
            raise self.error
        return {"id": task_id, "name": "Release checklist", "status": status}


class FakeGoogleCalendarClient:
    def __init__(self, *, ready: bool = True, error: Exception | None = None):
        self.ready = ready
        self.error = error
        self.calls: list[dict[str, str]] = []

    async def read_availability(self, *, time_hint: str, slot_minutes: int = 60, slot_limit: int = 3) -> dict:
        self.calls.append(
            {
                "time_hint": time_hint,
                "slot_minutes": str(slot_minutes),
                "slot_limit": str(slot_limit),
            }
        )
        if self.error is not None:
            raise self.error
        return {
            "window_start": "2026-04-28T08:00:00+00:00",
            "window_end": "2026-05-03T18:00:00+00:00",
            "time_zone": "UTC",
            "busy_window_count": 1,
            "free_slot_preview": [
                "2026-04-28T09:00:00+00:00 -> 2026-04-28T10:00:00+00:00",
                "2026-04-28T11:00:00+00:00 -> 2026-04-28T12:00:00+00:00",
            ],
        }


class FakeGoogleDriveClient:
    def __init__(self, *, ready: bool = True, error: Exception | None = None):
        self.ready = ready
        self.error = error
        self.calls: list[dict[str, str]] = []

    async def list_files(self, *, file_hint: str, limit: int = 5) -> list[dict]:
        self.calls.append({"file_hint": file_hint, "limit": str(limit)})
        if self.error is not None:
            raise self.error
        return [
            {
                "id": "drv_1",
                "name": "Release notes",
                "mime_type": "application/vnd.google-apps.document",
                "modified_time": "2026-04-22T07:00:00Z",
            },
            {
                "id": "drv_2",
                "name": "Deployment checklist",
                "mime_type": "text/markdown",
                "modified_time": "2026-04-21T12:00:00Z",
            },
        ]


class FakeDuckDuckGoSearchClient:
    def __init__(self, *, ready: bool = True, error: Exception | None = None):
        self.ready = ready
        self.error = error
        self.calls: list[dict[str, str]] = []

    async def search_web(self, *, query: str, limit: int = 5) -> list[dict]:
        self.calls.append({"query": query, "limit": str(limit)})
        if self.error is not None:
            raise self.error
        return [
            {
                "title": "Release notes",
                "url": "https://example.com/release-notes",
                "snippet": "Changelog summary",
                "rank": "1",
            }
        ]


class FakeGenericHttpPageClient:
    def __init__(self, *, ready: bool = True, error: Exception | None = None):
        self.ready = ready
        self.error = error
        self.calls: list[dict[str, str]] = []

    async def read_page(self, *, url: str, excerpt_length: int = 500) -> dict:
        self.calls.append({"url": url, "excerpt_length": str(excerpt_length)})
        if self.error is not None:
            raise self.error
        return {
            "url": url,
            "title": "Release notes",
            "content_type": "text/html",
            "excerpt": "Important changes.",
            "truncated": "false",
        }


class FakeHybridMemoryRepository(FakeMemoryRepository):
    def __init__(self, recent_memory: list[dict] | None = None, user_profile: dict | None = None):
        super().__init__(recent_memory=recent_memory, user_profile=user_profile)
        self.hybrid_calls: list[dict] = []
        self.relations: list[dict] = []

    async def get_hybrid_memory_bundle(
        self,
        *,
        user_id: str,
        query_text: str,
        query_embedding: list[float] | None = None,
        scope_type: str | None = None,
        scope_key: str | None = None,
        include_global: bool = True,
        episodic_limit: int = 12,
        conclusion_limit: int = 8,
    ) -> dict:
        self.hybrid_calls.append(
            {
                "user_id": user_id,
                "query_text": query_text,
                "query_embedding_dimensions": len(query_embedding or []),
                "scope_type": scope_type or "",
                "scope_key": scope_key or "",
                "include_global": include_global,
                "episodic_limit": episodic_limit,
                "conclusion_limit": conclusion_limit,
            }
        )
        affective = [
            row
            for row in self.user_conclusions
            if str(row.get("kind", "")).startswith("affective_")
        ]
        semantic = [
            row
            for row in self.user_conclusions
            if row not in affective
        ]
        return {
            "episodic": self.recent_memory[:episodic_limit],
            "semantic": semantic[:conclusion_limit],
            "affective": affective[:conclusion_limit],
            "diagnostics": {
                "query_tokens": len(query_text.split()),
                "episodic_candidates": len(self.recent_memory),
                "semantic_candidates": len(semantic),
                "affective_candidates": len(affective),
                "episodic_lexical_hits": len(self.recent_memory),
                "vector_hits": 1,
                "semantic_selected": len(semantic[:conclusion_limit]),
                "affective_selected": len(affective[:conclusion_limit]),
            },
        }

    async def get_user_relations(
        self,
        *,
        user_id: str,
        min_confidence: float | None = None,
        scope_type: str | None = None,
        scope_key: str | None = None,
        include_global: bool = True,
        limit: int = 8,
    ) -> list[dict]:
        threshold = 0.0 if min_confidence is None else float(min_confidence)
        normalized_scope_type, normalized_scope_key = self._normalize_scope(scope_type=scope_type, scope_key=scope_key)
        has_scope = scope_type is not None or scope_key is not None
        rows: list[dict] = []
        for item in self.relations:
            confidence = float(item.get("confidence", 0.0) or 0.0)
            if confidence < threshold:
                continue
            if not has_scope:
                rows.append(item)
                continue
            if relation_matches_scope_request(
                relation_type=str(item.get("relation_type", "")),
                row_scope_type=str(item.get("scope_type") or "global"),
                row_scope_key=str(item.get("scope_key") or "global"),
                requested_scope_type=scope_type,
                requested_scope_key=scope_key,
                include_global=include_global,
            ):
                rows.append(item)
        return rows[:limit]


class FakeTelegramClient:
    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        *,
        parse_mode: str | None = None,
    ) -> dict:
        return {"ok": True}


class FailingTelegramClient:
    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        *,
        parse_mode: str | None = None,
    ) -> dict:
        raise TimeoutError("telegram transport timeout")


class FakeOpenAIClient:
    def __init__(self):
        self.calls: list[dict[str, str]] = []

    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        foreground_awareness_summary: str,
        role_name: str,
        response_language: str,
        response_style: str | None,
        plan_goal: str,
        motivation_mode: str,
        response_tone: str,
        collaboration_preference: str | None,
        identity_summary: str = "",
        current_turn_timestamp: str = "",
    ) -> str | None:
        self.calls.append(
            {
                "user_text": user_text,
                "context_summary": context_summary,
                "foreground_awareness_summary": foreground_awareness_summary,
                "role_name": role_name,
                "response_language": response_language,
                "response_style": response_style or "",
                "plan_goal": plan_goal,
                "motivation_mode": motivation_mode,
                "response_tone": response_tone,
                "collaboration_preference": collaboration_preference or "",
                "identity_summary": identity_summary,
                "current_turn_timestamp": current_turn_timestamp,
            }
        )
        return "Mocked OpenAI reply"

    async def classify_affective_state(
        self,
        *,
        user_text: str,
        response_language: str,
    ) -> dict | None:
        return None


class FakeAffectiveClassifierClient:
    def __init__(self, payload: dict | None):
        self.payload = payload
        self.calls: list[dict[str, str]] = []

    async def classify_affective_state(self, *, user_text: str, response_language: str) -> dict | None:
        self.calls.append({"user_text": user_text, "response_language": response_language})
        return self.payload


class FakeReflectionWorker:
    def __init__(self, enqueue_result: bool = True, running: bool = True):
        self.enqueue_result = enqueue_result
        self.running = running
        self.calls: list[dict[str, str]] = []

    def is_running(self) -> bool:
        return self.running

    async def enqueue(self, user_id: str, event_id: str, *, dispatch: bool = True) -> bool:
        self.calls.append(
            {
                "user_id": user_id,
                "event_id": event_id,
                "dispatch": "yes" if dispatch else "no",
            }
        )
        return self.enqueue_result


async def test_runtime_pipeline_api_source() -> None:
    memory = FakeMemoryRepository(
        recent_memory=[
            {
                "id": 7,
                "event_id": "evt-prev",
                "summary": (
                    "event=previous hello; memory_kind=continuity; memory_topics=previous,hello; response_language=en; context=old context; "
                    "plan_goal=reply; action=success; expression=Earlier reply"
                ),
                "importance": 0.6,
                "event_timestamp": datetime.now(timezone.utc),
            }
        ]
    )
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "hello"},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert result.identity.mission == "Help the user move forward with clear, constructive support."
    assert result.identity.behavioral_style == ["direct", "supportive", "analytical"]
    assert result.active_goals == []
    assert result.active_tasks == []
    assert result.active_goal_milestones == []
    assert result.goal_milestone_history == []
    assert "Identity stance: direct, supportive, analytical." in result.context.summary
    assert "previous hello" in result.context.summary
    assert "Earlier reply" in result.context.summary
    assert result.perception.language == "en"
    assert result.perception.language_source == "recent_memory"
    assert result.perception.affective.affect_label == "neutral"
    assert result.perception.affective.source == "fallback"
    assert result.affective.affect_label == result.perception.affective.affect_label
    assert "general" in result.perception.topic_tags
    assert result.role.selected == "advisor"
    assert result.motivation.mode == "respond"
    assert result.plan.steps == ["interpret_event", "review_context", "prepare_response"]
    assert result.expression.message == "Mocked OpenAI reply"
    assert result.expression.language == "en"
    assert result.memory_record is not None
    assert "User said 'hello'." in result.memory_record.summary
    assert result.memory_record.payload["memory_kind"] == "continuity"
    assert result.memory_record.payload["memory_topics"] == ["general", "hello"]
    assert result.memory_record.payload["response_language"] == "en"
    assert result.memory_record.payload["affect_label"] == "neutral"
    assert result.memory_record.payload["affect_needs_support"] is False
    assert result.reflection_triggered is True
    assert memory.recent_limits[0] == 12
    assert set(result.stage_timings_ms) == {
        "memory_load",
        "task_load",
        "planned_work_load",
        "goal_milestone_load",
        "goal_milestone_history_load",
        "goal_progress_load",
        "identity_load",
        "perception",
        "affective_assessment",
        "context",
        "motivation",
        "role",
        "planning",
        "expression",
        "action",
        "memory_persist",
        "reflection_enqueue",
        "state_refresh",
        "total",
    }
    assert result.stage_timings_ms["total"] == result.duration_ms
    assert reflection.calls == [{"user_id": "u-1", "event_id": "evt-1", "dispatch": "yes"}]
    assert memory.profile_updates == []
    assert openai.calls[0]["response_style"] == ""
    assert openai.calls[0]["response_tone"] == "supportive"
    assert openai.calls[0]["collaboration_preference"] == ""
    assert "constructive support" in openai.calls[0]["identity_summary"]


async def test_runtime_pipeline_persists_reflection_task_without_in_process_worker() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=None,
    )

    event = Event(
        event_id="evt-reflection-deferred",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "hello from deferred reflection mode"},
        meta=EventMeta(user_id="u-1", trace_id="t-reflection-deferred"),
    )

    result = await runtime.run(event)

    assert result.reflection_triggered is True
    assert memory.reflection_tasks == [
        {
            "id": 1,
            "user_id": "u-1",
            "event_id": "evt-reflection-deferred",
            "status": "pending",
            "attempts": 0,
            "last_error": None,
        }
    ]


async def test_runtime_pipeline_respects_deferred_enqueue_dispatch_boundary_when_worker_is_attached() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    reflection = FakeReflectionWorker(running=True)
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
        reflection_runtime_mode="deferred",
    )

    event = Event(
        event_id="evt-reflection-deferred-boundary",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "respect deferred boundary"},
        meta=EventMeta(user_id="u-1", trace_id="t-reflection-deferred-boundary"),
    )

    result = await runtime.run(event)

    assert result.reflection_triggered is True
    assert reflection.calls == [
        {
            "user_id": "u-1",
            "event_id": "evt-reflection-deferred-boundary",
            "dispatch": "no",
        }
    ]


async def test_runtime_pipeline_invokes_langgraph_foreground_graph() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    class _GraphProxy:
        def __init__(self, graph):
            self.graph = graph
            self.called = False

        async def ainvoke(self, state):
            self.called = True
            return await self.graph.ainvoke(state)

    proxy = _GraphProxy(runtime.foreground_graph_runner._graph)
    runtime.foreground_graph_runner._graph = proxy

    event = Event(
        event_id="evt-langgraph",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "show me the next migration step"},
        meta=EventMeta(user_id="u-1", trace_id="t-langgraph"),
    )

    result = await runtime.run(event)

    assert proxy.called is True
    assert "langgraph" in proxy.graph.__class__.__module__
    assert result.action_result.status == "success"


async def test_runtime_pipeline_uses_hybrid_memory_bundle_when_supported() -> None:
    memory = FakeHybridMemoryRepository(
        recent_memory=[
            {
                "id": 7,
                "event_id": "evt-prev",
                "summary": "event=deployment blocker; memory_kind=semantic; memory_topics=deploy,blocker; response_language=en; expression=Earlier deployment guidance",
                "importance": 0.7,
                "event_timestamp": datetime.now(timezone.utc),
                "payload": {
                    "event": "deployment blocker",
                    "memory_topics": ["deploy", "blocker"],
                    "memory_kind": "semantic",
                },
            }
        ]
    )
    memory.user_conclusions = [
        {
            "kind": "custom_semantic_fact",
            "content": "deployment blockers often need dependency sequencing",
            "confidence": 0.74,
            "source": "background_reflection",
        },
        {
            "kind": "affective_support_pattern",
            "content": "recurring_distress",
            "confidence": 0.78,
            "source": "background_reflection",
        },
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = Event(
        event_id="evt-hybrid",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "help me sequence this deploy blocker"},
        meta=EventMeta(user_id="u-1", trace_id="t-hybrid"),
    )

    result = await runtime.run(event)

    assert len(memory.hybrid_calls) == 1
    assert memory.hybrid_calls[0]["query_text"] == "help me sequence this deploy blocker"
    assert memory.hybrid_calls[0]["query_embedding_dimensions"] == 32
    assert memory.hybrid_calls[0]["episodic_limit"] == RuntimeOrchestrator.MEMORY_LOAD_LIMIT
    assert memory.hybrid_calls[0]["conclusion_limit"] == 8
    assert memory.hybrid_calls[0]["include_global"] is False
    assert result.action_result.status == "success"
    assert "deployment blocker" in result.context.summary


async def test_runtime_pipeline_uses_lexical_only_hybrid_query_when_semantic_vector_is_disabled() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
        semantic_vector_enabled=False,
    )

    event = Event(
        event_id="evt-hybrid-lexical-only",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "help me sequence this deploy blocker"},
        meta=EventMeta(user_id="u-1", trace_id="t-hybrid-lexical-only"),
    )

    await runtime.run(event)

    assert len(memory.hybrid_calls) == 1
    assert memory.hybrid_calls[0]["query_embedding_dimensions"] == 0
    assert memory.hybrid_calls[0]["episodic_limit"] == RuntimeOrchestrator.MEMORY_LOAD_LIMIT
    assert memory.hybrid_calls[0]["conclusion_limit"] == 8


async def test_runtime_pipeline_uses_configured_embedding_dimensions_even_when_provider_falls_back_to_deterministic() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    action = ActionExecutor(
        memory_repository=memory,
        telegram_client=FakeTelegramClient(),
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=24,
    )
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
        semantic_vector_enabled=True,
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=24,
    )

    event = Event(
        event_id="evt-hybrid-provider-fallback",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "help me sequence this deploy blocker"},
        meta=EventMeta(user_id="u-1", trace_id="t-hybrid-provider-fallback"),
    )

    await runtime.run(event)

    assert len(memory.hybrid_calls) == 1
    assert memory.hybrid_calls[0]["query_embedding_dimensions"] == 24


async def test_runtime_pipeline_keeps_transition_retrieval_lifecycle_active_for_local_hybrid_provider() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    action = ActionExecutor(
        memory_repository=memory,
        telegram_client=FakeTelegramClient(),
        embedding_provider="local_hybrid",
        embedding_model="local-hybrid-v1",
        embedding_dimensions=32,
    )
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
        semantic_vector_enabled=True,
        embedding_provider="local_hybrid",
        embedding_model="local-hybrid-v1",
        embedding_dimensions=32,
    )

    event = Event(
        event_id="evt-hybrid-local-lifecycle",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "help me sequence this deploy blocker"},
        meta=EventMeta(user_id="u-1", trace_id="t-hybrid-local-lifecycle"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert len(memory.hybrid_calls) == 1
    assert memory.hybrid_calls[0]["query_embedding_dimensions"] == 32
    assert memory.hybrid_calls[0]["episodic_limit"] == RuntimeOrchestrator.MEMORY_LOAD_LIMIT
    assert memory.hybrid_calls[0]["include_global"] is False


async def test_runtime_pipeline_surfaces_relation_signals_in_context_and_planning() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    memory.relations = [
        {
            "relation_type": "collaboration_dynamic",
            "relation_value": "guided",
            "confidence": 0.79,
        },
        {
            "relation_type": "delivery_reliability",
            "relation_value": "high_trust",
            "confidence": 0.74,
        },
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = Event(
        event_id="evt-rel-runtime",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this next step?"},
        meta=EventMeta(user_id="u-1", trace_id="t-rel-runtime"),
    )

    result = await runtime.run(event)

    assert "Relation cues: current collaboration flow is guided and step-oriented." in result.context.summary
    assert "guided step by step" in result.plan.goal.lower()
    assert any(
        step in result.plan.steps for step in ("favor_guided_walkthrough", "break_down_problem")
    )
    assert "favor_concrete_next_step" in result.plan.steps


async def test_runtime_pipeline_loads_memory_beyond_latest_five_and_surfaces_ranked_relevant_item() -> None:
    memory = FakeMemoryRepository(
        recent_memory=[
            {
                "id": 101,
                "event_id": "evt-irr-1",
                "summary": "event=weather update; memory_kind=semantic; memory_topics=weather,rain; response_language=en; action=success; expression=Weather summary",
                "importance": 0.8,
                "event_timestamp": datetime.now(timezone.utc),
            },
            {
                "id": 102,
                "event_id": "evt-irr-2",
                "summary": "event=coffee chat; memory_kind=continuity; memory_topics=coffee,chat; response_language=en; action=success; expression=Coffee summary",
                "importance": 0.8,
                "event_timestamp": datetime.now(timezone.utc),
            },
            {
                "id": 103,
                "event_id": "evt-irr-3",
                "summary": "event=book notes; memory_kind=semantic; memory_topics=book,notes; response_language=en; action=success; expression=Book summary",
                "importance": 0.8,
                "event_timestamp": datetime.now(timezone.utc),
            },
            {
                "id": 104,
                "event_id": "evt-irr-4",
                "summary": "event=travel plan; memory_kind=semantic; memory_topics=travel,plan; response_language=en; action=success; expression=Travel summary",
                "importance": 0.8,
                "event_timestamp": datetime.now(timezone.utc),
            },
            {
                "id": 105,
                "event_id": "evt-irr-5",
                "summary": "event=music playlist; memory_kind=continuity; memory_topics=music,playlist; response_language=en; action=success; expression=Music summary",
                "importance": 0.8,
                "event_timestamp": datetime.now(timezone.utc),
            },
            {
                "id": 106,
                "event_id": "evt-rel-6",
                "summary": "event=deployment blocker follow-up; memory_kind=semantic; memory_topics=deploy,blocker,release; response_language=en; action=success; expression=Let's remove the blocker first",
                "importance": 0.74,
                "event_timestamp": datetime.now(timezone.utc),
            },
        ]
    )
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )
    event = Event(
        event_id="evt-memory-depth",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me fix the deployment blocker?"},
        meta=EventMeta(user_id="u-1", trace_id="t-memory-depth"),
    )

    result = await runtime.run(event)

    assert memory.recent_limits[0] == 12
    assert "deployment blocker follow-up" in result.context.summary


async def test_runtime_pipeline_uses_ai_assisted_affective_assessor_when_available() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    classifier = FakeAffectiveClassifierClient(
        {
            "affect_label": "support_distress",
            "intensity": 0.81,
            "needs_support": True,
            "confidence": 0.77,
            "evidence": ["overwhelmed", "anxious"],
        }
    )
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
        affective_assessor=AffectiveAssessor(classifier_client=classifier),
    )

    event = Event(
        event_id="evt-affect-ai",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "I feel overwhelmed and anxious about this release"},
        meta=EventMeta(user_id="u-1", trace_id="t-affect-ai"),
    )

    result = await runtime.run(event)

    assert classifier.calls == [
        {
            "user_text": "I feel overwhelmed and anxious about this release",
            "response_language": "en",
        }
    ]
    assert result.affective.affect_label == "support_distress"
    assert result.affective.source == "ai_classifier"
    assert result.affective.needs_support is True
    assert result.perception.affective.source == "ai_classifier"


async def test_runtime_pipeline_builds_explicit_action_delivery_contract() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    captured_delivery = None
    original_execute = action.execute

    async def capture_execute(plan, delivery):
        nonlocal captured_delivery
        captured_delivery = delivery
        return await original_execute(plan, delivery)

    action.execute = capture_execute  # type: ignore[method-assign]

    event = Event(
        event_id="evt-delivery-contract",
        source="telegram",
        subsource="user_message",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "hello from telegram", "chat_id": 777},
        meta=EventMeta(user_id="u-1", trace_id="t-delivery-contract"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert result.action_result.actions == ["send_telegram_message"]
    assert captured_delivery is not None
    assert captured_delivery.channel == "telegram"
    assert captured_delivery.chat_id == 777
    assert captured_delivery.message == "Mocked OpenAI reply"
    assert captured_delivery.language == "en"
    assert captured_delivery.execution_envelope.connector_safe is False
    assert captured_delivery.execution_envelope.connector_intents == []
    assert captured_delivery.execution_envelope.connector_permission_gates == []


async def test_runtime_pipeline_builds_connector_safe_action_delivery_envelope_for_connector_intents() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    captured_delivery = None
    original_execute = action.execute

    async def capture_execute(plan, delivery):
        nonlocal captured_delivery
        captured_delivery = delivery
        return await original_execute(plan, delivery)

    action.execute = capture_execute  # type: ignore[method-assign]

    event = Event(
        event_id="evt-delivery-envelope",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Create calendar meeting tomorrow, create task in ClickUp, and upload notes to Google Drive."},
        meta=EventMeta(user_id="u-1", trace_id="t-delivery-envelope"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert captured_delivery is not None
    assert captured_delivery.execution_envelope.connector_safe is True
    assert len(captured_delivery.execution_envelope.connector_intents) == 3
    assert len(captured_delivery.execution_envelope.connector_permission_gates) == 3
    assert {intent.connector_kind for intent in captured_delivery.execution_envelope.connector_intents} == {
        "calendar",
        "task_system",
        "cloud_drive",
    }
    assert "Execution envelope:" in result.action_result.notes


async def test_runtime_pipeline_degrades_telegram_delivery_exception_to_fail_action_result() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FailingTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-telegram-fail-boundary",
        source="telegram",
        subsource="user_message",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "hello from telegram", "chat_id": 777},
        meta=EventMeta(user_id="u-1", trace_id="t-telegram-fail-boundary"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "fail"
    assert result.action_result.actions == ["send_telegram_message"]
    assert "TimeoutError" in result.action_result.notes
    assert result.memory_record is not None
    assert result.memory_record.payload["action"] == "fail"
    assert result.reflection_triggered is True


async def test_runtime_pipeline_contract_smoke_pins_stage_and_action_boundary_invariants() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-contract-smoke",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Please summarize the current runtime contract."},
        meta=EventMeta(user_id="u-1", trace_id="t-contract-smoke"),
    )

    result = await runtime.run(event)

    stage_order = list(result.stage_timings_ms.keys())
    assert stage_order.index("expression") < stage_order.index("action")
    assert stage_order.index("action") < stage_order.index("memory_persist")
    assert stage_order[-1] == "total"
    assert result.event.event_id == event.event_id
    assert result.event.meta.trace_id == event.meta.trace_id
    assert result.action_result.status == "success"
    assert result.action_result.actions == ["api_response"]
    assert result.expression.channel == "api"
    assert result.memory_record is not None
    assert result.memory_record.event_id == event.event_id
    assert result.reflection_triggered is True


async def test_runtime_pipeline_keeps_explicit_runtime_graph_boundary_segments() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-boundary-contract",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Show runtime boundary ownership."},
        meta=EventMeta(user_id="u-1", trace_id="t-boundary-contract"),
    )

    result = await runtime.run(event)
    stage_order = list(result.stage_timings_ms.keys())

    assert stage_order.index("memory_load") < stage_order.index("perception")
    assert stage_order.index("task_load") < stage_order.index("perception")
    assert stage_order.index("goal_milestone_load") < stage_order.index("perception")
    assert stage_order.index("identity_load") < stage_order.index("perception")
    assert stage_order.index("action") < stage_order.index("memory_persist")
    assert stage_order.index("memory_persist") < stage_order.index("reflection_enqueue")
    assert stage_order.index("reflection_enqueue") < stage_order.index("state_refresh")


async def test_runtime_pipeline_emits_structured_stage_logs(caplog) -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )
    caplog.set_level("INFO", logger="aion.runtime")

    event = Event(
        event_id="evt-log-success",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "hello"},
        meta=EventMeta(user_id="u-1", trace_id="t-log-success"),
    )

    await runtime.run(event)

    stage_logs = [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.name == "aion.runtime" and record.getMessage().startswith("{")
    ]

    assert {
        (entry["stage"], entry["status"])
        for entry in stage_logs
        if entry.get("kind") == "runtime_stage"
    } >= {
        ("memory_load", "start"),
        ("memory_load", "success"),
        ("perception", "start"),
        ("perception", "success"),
        ("affective_assessment", "success"),
        ("expression", "success"),
        ("memory_persist", "success"),
        ("state_refresh", "success"),
    }
    perception_success = next(
        entry
        for entry in stage_logs
        if entry.get("kind") == "runtime_stage"
        and entry["stage"] == "perception"
        and entry["status"] == "success"
    )
    assert perception_success["event_id"] == "evt-log-success"
    assert perception_success["trace_id"] == "t-log-success"
    assert "topic=general" in perception_success["summary"]
    assert perception_success["duration_ms"] >= 0
    affective_success = next(
        entry
        for entry in stage_logs
        if entry.get("kind") == "runtime_stage"
        and entry["stage"] == "affective_assessment"
        and entry["status"] == "success"
    )
    assert "source=fallback" in affective_success["summary"]


async def test_runtime_pipeline_emits_affective_fallback_reason_in_stage_logs(caplog) -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    classifier = FakeAffectiveClassifierClient(
        {"_aion_affective_fallback_reason": "openai_affective_parse_failed"}
    )
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
        affective_assessor=AffectiveAssessor(classifier_client=classifier),
    )
    caplog.set_level("INFO", logger="aion.runtime")

    event = Event(
        event_id="evt-affective-fallback-reason",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "I feel overwhelmed and anxious"},
        meta=EventMeta(user_id="u-1", trace_id="t-affective-fallback-reason"),
    )

    result = await runtime.run(event)

    assert result.affective.source == "fallback"
    assert "fallback_reason:openai_affective_parse_failed" in result.affective.evidence

    stage_logs = [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.name == "aion.runtime" and record.getMessage().startswith("{")
    ]
    affective_success = next(
        entry
        for entry in stage_logs
        if entry.get("kind") == "runtime_stage"
        and entry["stage"] == "affective_assessment"
        and entry["status"] == "success"
    )
    assert "source=fallback" in affective_success["summary"]
    assert "fallback_reason=openai_affective_parse_failed" in affective_success["summary"]


async def test_runtime_pipeline_emits_stage_failure_log_for_memory_persist(caplog) -> None:
    memory = FailingWriteMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )
    caplog.set_level("INFO", logger="aion.runtime")

    event = Event(
        event_id="evt-log-failure",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "hello"},
        meta=EventMeta(user_id="u-1", trace_id="t-log-failure"),
    )

    result = await runtime.run(event)

    stage_logs = [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.name == "aion.runtime" and record.getMessage().startswith("{")
    ]
    memory_persist_failure = next(
        entry
        for entry in stage_logs
        if entry.get("kind") == "runtime_stage"
        and entry["stage"] == "memory_persist"
        and entry["status"] == "failure"
    )

    assert result.memory_record is None
    assert result.reflection_triggered is False
    assert memory_persist_failure["event_id"] == "evt-log-failure"
    assert memory_persist_failure["trace_id"] == "t-log-failure"
    assert memory_persist_failure["error_type"] == "RuntimeError"
    assert "database unavailable" in memory_persist_failure["error"]
    assert memory_persist_failure["duration_ms"] >= 0


async def test_runtime_pipeline_routes_emotional_turn_through_documented_contract() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-emotional",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "I feel stressed and overwhelmed right now"},
        meta=EventMeta(user_id="u-1", trace_id="t-emotional"),
    )

    result = await runtime.run(event)

    assert result.affective.affect_label == "support_distress"
    assert result.affective.needs_support is True
    assert result.motivation.mode == "respond"
    assert result.motivation.valence <= -0.45
    assert result.role.selected == "friend"
    assert "acknowledge_emotion" in result.plan.steps
    assert "reduce_pressure" in result.plan.steps
    assert result.expression.tone == "supportive"
    assert openai.calls[0]["motivation_mode"] == "respond"
    assert openai.calls[0]["response_tone"] == "supportive"
    assert result.reflection_triggered is True


@pytest.mark.parametrize("scenario", EMPATHY_SUPPORT_SCENARIOS, ids=lambda scenario: scenario.key)
async def test_runtime_pipeline_pins_empathy_quality_for_heavy_ambiguous_and_mixed_turns(scenario) -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    classifier = FakeAffectiveClassifierClient(scenario.classifier_payload())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
        affective_assessor=AffectiveAssessor(classifier_client=classifier),
    )

    event = Event(
        event_id=f"evt-empathy-{scenario.key}",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": scenario.text},
        meta=EventMeta(user_id="u-1", trace_id=f"t-empathy-{scenario.key}"),
    )

    result = await runtime.run(event)

    assert result.affective.affect_label == scenario.affect_label
    assert result.affective.needs_support is True
    assert result.motivation.mode == "respond"
    assert result.motivation.urgency >= scenario.expected_min_urgency
    assert result.role.selected == "friend"
    assert "acknowledge_emotion" in result.plan.steps
    assert "reduce_pressure" in result.plan.steps
    assert result.expression.tone == "supportive"
    assert openai.calls[0]["response_tone"] == "supportive"
    assert result.reflection_triggered is True


async def test_runtime_pipeline_accepts_goal_scoped_conclusions_in_runtime_context() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.user_conclusions = [
        {
            "kind": "goal_execution_state",
            "content": "blocked",
            "confidence": 0.82,
            "source": "background_reflection",
            "scope_type": "goal",
            "scope_key": "11",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-scoped-conclusion",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for this goal?"},
        meta=EventMeta(user_id="u-1", trace_id="t-scoped-conclusion"),
    )

    result = await runtime.run(event)

    assert "current goal progress is blocked by an active task" in result.context.summary
    assert result.motivation.mode == "analyze"
    assert result.action_result.status == "success"
    assert result.reflection_triggered is True


async def test_runtime_pipeline_uses_primary_goal_scoped_state_without_cross_goal_leakage() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        },
        {
            "id": 22,
            "user_id": "u-1",
            "name": "prepare post-launch documentation",
            "description": "User-declared goal: prepare post-launch documentation",
            "priority": "medium",
            "status": "active",
            "goal_type": "operational",
        },
    ]
    memory.scoped_user_preferences[("goal", "11")] = {
        "goal_execution_state": "blocked",
        "goal_execution_state_confidence": 0.82,
        "goal_execution_state_source": "background_reflection",
    }
    memory.scoped_user_preferences[("goal", "22")] = {
        "goal_execution_state": "advancing",
        "goal_execution_state_confidence": 0.75,
        "goal_execution_state_source": "background_reflection",
    }
    memory.scoped_user_conclusions = [
        {
            "kind": "goal_execution_state",
            "content": "blocked",
            "confidence": 0.82,
            "source": "background_reflection",
            "scope_type": "goal",
            "scope_key": "11",
        },
        {
            "kind": "goal_execution_state",
            "content": "advancing",
            "confidence": 0.75,
            "source": "background_reflection",
            "scope_type": "goal",
            "scope_key": "22",
        },
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-scoped-primary-goal",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-scoped-primary-goal"),
    )

    result = await runtime.run(event)

    assert "Stable user preferences: current goal progress is blocked by an active task." in result.context.summary
    assert "Stable user preferences: current goal work is actively advancing." not in result.context.summary
    assert result.motivation.mode == "analyze"
    assert "recover_goal_progress" in result.plan.steps
    assert "continue_goal_execution" not in result.plan.steps
    assert result.action_result.status == "success"


async def test_runtime_pipeline_ignores_goal_scoped_overrides_for_global_reflection_outputs() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.user_preferences = {
        "affective_support_pattern": "confidence_recovery",
        "affective_support_pattern_confidence": 0.74,
        "affective_support_pattern_source": "background_reflection",
    }
    memory.scoped_user_preferences[("goal", "11")] = {
        "affective_support_pattern": "recurring_distress",
        "affective_support_pattern_confidence": 0.76,
        "affective_support_pattern_source": "background_reflection",
    }
    memory.user_conclusions = [
        {
            "kind": "affective_support_pattern",
            "content": "confidence_recovery",
            "confidence": 0.74,
            "source": "background_reflection",
            "scope_type": "global",
            "scope_key": "global",
        }
    ]
    memory.scoped_user_conclusions = [
        {
            "kind": "affective_support_pattern",
            "content": "recurring_distress",
            "confidence": 0.76,
            "source": "background_reflection",
            "scope_type": "goal",
            "scope_key": "11",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = Event(
        event_id="evt-global-reflection-scope",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "How should we handle this release work?"},
        meta=EventMeta(user_id="u-1", trace_id="t-global-reflection-scope"),
    )

    result = await runtime.run(event)

    assert "Stable user preferences: recent turns show confidence recovery after earlier stress." in result.context.summary
    assert "Stable user preferences: recent turns show recurring stress signals and benefit from supportive pacing." not in result.context.summary
    assert result.action_result.status == "success"


async def test_runtime_pipeline_uses_goal_scoped_relations_without_cross_goal_leakage() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "proactive_opt_in": True,
        "proactive_recent_outbound_limit": 3,
        "proactive_unanswered_limit": 2,
    }
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        },
        {
            "id": 22,
            "user_id": "u-1",
            "name": "prepare post-launch documentation",
            "description": "User-declared goal: prepare post-launch documentation",
            "priority": "medium",
            "status": "active",
            "goal_type": "operational",
        },
    ]
    memory.relations = [
        {
            "relation_type": "support_intensity_preference",
            "relation_value": "high_support",
            "confidence": 0.78,
            "scope_type": "goal",
            "scope_key": "22",
        },
        {
            "relation_type": "delivery_reliability",
            "relation_value": "medium_trust",
            "confidence": 0.74,
            "scope_type": "goal",
            "scope_key": "22",
        },
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = build_scheduler_event(
        subsource="proactive_tick",
        payload={
            "text": "check goal stagnation",
            "chat_id": 123456,
            "proactive_trigger": "goal_stagnation",
            "importance": 0.84,
            "urgency": 0.7,
            "user_context": {
                "quiet_hours": False,
                "focus_mode": False,
                "recent_user_activity": "active",
                "recent_outbound_count": 1,
                "unanswered_proactive_count": 1,
            },
        },
    )

    result = await runtime.run(event)

    assert result.plan.proactive_decision is not None
    assert result.plan.proactive_decision.should_interrupt is True
    assert result.event.payload["attention_gate"]["allowed"] is True
    assert result.event.payload["attention_gate"]["reason"] == "attention_gate_pass"
    assert result.event.payload["attention_gate"]["unanswered_proactive_limit"] == 2
    assert result.event.payload["attention_gate"]["relation_support_intensity"] is None
    assert result.event.payload["attention_gate"]["relation_delivery_reliability"] is None
    assert "respect_attention_gate" not in result.plan.steps
    assert result.plan.proactive_delivery_guard is not None
    assert result.plan.proactive_delivery_guard.allowed is True
    assert result.action_result.status == "success"


async def test_runtime_pipeline_loads_active_goals_and_tasks_into_context_and_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.active_tasks = [
        {
            "id": 21,
            "user_id": "u-1",
            "goal_id": 11,
            "name": "fix deployment blocker",
            "description": "User-declared task: fix deployment blocker",
            "priority": "high",
            "status": "blocked",
        }
    ]
    memory.active_goal_milestones = [
        {
            "id": 31,
            "goal_id": 11,
            "name": "Stabilize goal recovery",
            "phase": "recovery_phase",
            "status": "active",
        }
    ]
    memory.goal_milestone_history = [
        {
            "id": 41,
            "goal_id": 11,
            "milestone_name": "Stabilize goal recovery",
            "phase": "recovery_phase",
            "risk_level": "stabilizing",
            "completion_criteria": "stabilize_remaining_work",
            "source_event_id": "evt-history-old",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "id": 42,
            "goal_id": 11,
            "milestone_name": "Drive goal to closure",
            "phase": "completion_window",
            "risk_level": "ready_to_close",
            "completion_criteria": "finish_remaining_active_work",
            "source_event_id": "evt-history-new",
            "created_at": datetime.now(timezone.utc),
        },
    ]
    memory.user_preferences = {
        "goal_milestone_risk": "stabilizing",
        "goal_completion_criteria": "stabilize_remaining_work",
    }
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-goal-task",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me plan how to fix the deployment blocker for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-goal-task"),
    )

    result = await runtime.run(event)

    assert result.active_goals[0].name == "ship the MVP this week"
    assert result.active_tasks[0].name == "fix deployment blocker"
    assert result.active_goal_milestones[0].name == "Stabilize goal recovery"
    assert result.active_goal_milestones[0].risk_level == "stabilizing"
    assert result.active_goal_milestones[0].completion_criteria == "stabilize_remaining_work"
    assert result.goal_milestone_history[0].milestone_name == "Stabilize goal recovery"
    assert "Active goals: ship the MVP this week." in result.context.summary
    assert "Active tasks: fix deployment blocker (blocked)." in result.context.summary
    assert "Active milestones: Stabilize goal recovery (recovery_phase, stabilizing, stabilize remaining work)." in result.context.summary
    assert "Recent milestone history moved from completion window to recovery phase." in result.context.summary
    assert result.context.related_goals == ["ship the MVP this week"]
    assert "align_with_active_goal" in result.plan.steps
    assert "align_with_active_milestone" in result.plan.steps
    assert "unblock_active_task" in result.plan.steps
    assert result.motivation.importance >= 0.78


async def test_runtime_pipeline_returns_refreshed_goal_and_task_state_after_explicit_updates() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    goal_event = Event(
        event_id="evt-goal",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "My goal is to ship the MVP this week."},
        meta=EventMeta(user_id="u-1", trace_id="t-goal"),
    )
    goal_result = await runtime.run(goal_event)

    assert any(intent.intent_type == "upsert_goal" for intent in goal_result.plan.domain_intents)
    assert goal_result.active_goals[0].name == "ship the MVP this week"

    task_event = Event(
        event_id="evt-task",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "I need to fix the deployment blocker."},
        meta=EventMeta(user_id="u-1", trace_id="t-task"),
    )
    task_result = await runtime.run(task_event)

    assert any(intent.intent_type == "upsert_task" for intent in task_result.plan.domain_intents)
    assert task_result.active_tasks[0].name == "fix the deployment blocker"
    assert task_result.active_tasks[0].status == "blocked"

    done_event = Event(
        event_id="evt-task-done",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "I fixed the deployment blocker."},
        meta=EventMeta(user_id="u-1", trace_id="t-task-done"),
    )
    done_result = await runtime.run(done_event)

    assert any(intent.intent_type == "update_task_status" for intent in done_result.plan.domain_intents)
    assert done_result.active_goals[0].name == "ship the MVP this week"
    assert done_result.active_tasks == []
    assert done_result.stage_timings_ms["state_refresh"] >= 0


async def test_runtime_pipeline_detects_inline_goal_and_task_commands() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-inline-goal-task",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Prosze, dodaj cel: ship the MVP this week i dodaj zadanie: fix deployment blocker."},
        meta=EventMeta(user_id="u-1", trace_id="t-inline-goal-task"),
    )
    result = await runtime.run(event)

    assert any(intent.intent_type == "upsert_goal" for intent in result.plan.domain_intents)
    assert any(intent.intent_type == "upsert_task" for intent in result.plan.domain_intents)
    assert any(goal.name == "ship the MVP this week" for goal in result.active_goals)
    assert any(task.name == "fix deployment blocker" for task in result.active_tasks)


async def test_runtime_pipeline_persists_inferred_goal_and_task_promotions_from_repeated_blocker_evidence() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-inferred-goal-task",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Again I am still blocked by deployment migration failures for the MVP release."},
        meta=EventMeta(user_id="u-1", trace_id="t-inferred-goal-task"),
    )

    result = await runtime.run(event)

    assert any(intent.intent_type == "promote_inferred_goal" for intent in result.plan.domain_intents)
    assert any(intent.intent_type == "promote_inferred_task" for intent in result.plan.domain_intents)
    assert result.active_goals
    assert result.active_tasks
    assert result.active_goals[0].description.startswith("Inferred goal from repeated execution evidence:")
    assert result.active_tasks[0].description.startswith("Inferred task from repeated execution evidence:")
    assert result.active_tasks[0].status == "blocked"
    assert "reason=gate_open" in result.plan.inferred_promotion_diagnostics
    assert "result=promote_inferred_task" in result.plan.inferred_promotion_diagnostics
    assert "result=promote_inferred_goal" in result.plan.inferred_promotion_diagnostics


async def test_runtime_pipeline_blocks_inferred_promotion_under_low_trust_with_borderline_importance() -> None:
    class FixedMotivationEngine:
        def run(self, **kwargs) -> MotivationOutput:  # noqa: ANN003
            return MotivationOutput(
                importance=0.69,
                urgency=0.71,
                valence=-0.08,
                arousal=0.58,
                mode="execute",
            )

    memory = FakeHybridMemoryRepository(recent_memory=[])
    memory.relations = [
        {
            "relation_type": "delivery_reliability",
            "relation_value": "low_trust",
            "confidence": 0.79,
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=FixedMotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-inferred-trust-gate",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Again I am still blocked by deployment migration failures for the MVP release."},
        meta=EventMeta(user_id="u-1", trace_id="t-inferred-trust-gate"),
    )

    result = await runtime.run(event)

    assert result.plan.domain_intents[0].intent_type == "noop"
    assert not any(intent.intent_type == "promote_inferred_goal" for intent in result.plan.domain_intents)
    assert not any(intent.intent_type == "promote_inferred_task" for intent in result.plan.domain_intents)
    assert "reason=trust_gate_low_confidence" in result.plan.inferred_promotion_diagnostics
    assert "reason=trust_gate_low_confidence" in result.system_debug.plan.inferred_promotion_diagnostics
    assert result.active_goals == []
    assert result.active_tasks == []


async def test_runtime_pipeline_surfaces_high_trust_inferred_promotion_diagnostics() -> None:
    class FixedMotivationEngine:
        def run(self, **kwargs) -> MotivationOutput:  # noqa: ANN003
            return MotivationOutput(
                importance=0.59,
                urgency=0.71,
                valence=-0.08,
                arousal=0.58,
                mode="execute",
            )

    memory = FakeHybridMemoryRepository(recent_memory=[])
    memory.relations = [
        {
            "relation_type": "delivery_reliability",
            "relation_value": "high_trust",
            "confidence": 0.79,
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=FixedMotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-inferred-trust-open",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Again I am still blocked by deployment migration failures for the MVP release."},
        meta=EventMeta(user_id="u-1", trace_id="t-inferred-trust-open"),
    )

    result = await runtime.run(event)

    assert any(intent.intent_type == "promote_inferred_goal" for intent in result.plan.domain_intents)
    assert any(intent.intent_type == "promote_inferred_task" for intent in result.plan.domain_intents)
    assert "reason=gate_open" in result.plan.inferred_promotion_diagnostics
    assert "result=promote_inferred_goal" in result.plan.inferred_promotion_diagnostics
    assert "result=promote_inferred_task" in result.plan.inferred_promotion_diagnostics
    assert "reason=gate_open" in result.system_debug.plan.inferred_promotion_diagnostics


async def test_runtime_pipeline_does_not_duplicate_inferred_goal_task_when_matching_active_state_exists() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.active_goals = [
        {
            "id": 7,
            "user_id": "u-1",
            "name": "stabilize deployment migration failures mvp release",
            "description": "Inferred goal from repeated execution evidence: stabilize deployment migration failures mvp release",
            "priority": "high",
            "status": "active",
            "goal_type": "tactical",
        }
    ]
    memory.active_tasks = [
        {
            "id": 11,
            "goal_id": 7,
            "name": "deployment migration failures mvp release",
            "description": "Inferred task from repeated execution evidence: deployment migration failures mvp release",
            "priority": "high",
            "status": "blocked",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-inferred-no-duplicate",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Again I am still blocked by deployment migration failures for the MVP release."},
        meta=EventMeta(user_id="u-1", trace_id="t-inferred-no-duplicate"),
    )

    result = await runtime.run(event)

    assert len(result.active_goals) == 1
    assert len(result.active_tasks) == 1
    assert result.active_goals[0].name == "stabilize deployment migration failures mvp release"
    assert result.active_tasks[0].name == "deployment migration failures mvp release"
    assert result.plan.domain_intents[0].intent_type == "noop"
    assert not any(intent.intent_type == "promote_inferred_goal" for intent in result.plan.domain_intents)
    assert not any(intent.intent_type == "promote_inferred_task" for intent in result.plan.domain_intents)
    assert not any(intent.intent_type == "maintain_task_status" for intent in result.plan.domain_intents)


async def test_runtime_pipeline_does_not_write_domain_state_without_planning_intents() -> None:
    class NoDomainWritePlanningAgent(PlanningAgent):
        def run(self, *args, **kwargs):  # type: ignore[override]
            base = super().run(*args, **kwargs)
            return base.model_copy(update={"domain_intents": [NoopDomainIntent(reason="contract_test")]})

    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=NoDomainWritePlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-no-domain-intent",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "My goal is to ship the MVP this week."},
        meta=EventMeta(user_id="u-1", trace_id="t-no-domain-intent"),
    )

    result = await runtime.run(event)

    assert result.plan.domain_intents[0].intent_type == "noop"
    assert result.active_goals == []
    assert result.memory_record is not None
    assert result.memory_record.payload["goal_update"] == ""


async def test_runtime_pipeline_uses_goal_milestone_transition_across_context_motivation_and_planning() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {"goal_milestone_transition": "entered_completion_window"}
    memory.user_conclusions = [
        {
            "id": 1,
            "kind": "goal_milestone_transition",
            "content": "entered_completion_window",
            "confidence": 0.77,
            "source": "background_reflection",
            "supporting_event_id": "evt-goal-milestone",
            "updated_at": datetime.now(timezone.utc),
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-goal-milestone-runtime",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-goal-milestone-runtime"),
    )

    result = await runtime.run(event)

    assert "goal has entered the completion window" in result.context.summary
    assert result.motivation.importance >= 0.79
    assert "close_goal_completion_window" in result.plan.steps


async def test_runtime_pipeline_uses_goal_milestone_state_after_transition_turn_has_passed() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {"goal_milestone_state": "completion_window"}
    memory.user_conclusions = [
        {
            "id": 1,
            "kind": "goal_milestone_state",
            "content": "completion_window",
            "confidence": 0.8,
            "source": "background_reflection",
            "supporting_event_id": "evt-goal-milestone-state",
            "updated_at": datetime.now(timezone.utc),
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-goal-milestone-state-runtime",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-goal-milestone-state-runtime"),
    )

    result = await runtime.run(event)

    assert "current goal is currently in the completion window" in result.context.summary
    assert result.motivation.importance >= 0.8
    assert "drive_goal_to_closure" in result.plan.steps


async def test_runtime_pipeline_uses_milestone_risk_and_completion_criteria_across_runtime() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_milestone_risk": "ready_to_close",
        "goal_completion_criteria": "finish_remaining_active_work",
    }
    memory.user_conclusions = [
        {
            "kind": "goal_milestone_risk",
            "content": "ready_to_close",
            "confidence": 0.79,
            "source": "background_reflection",
        },
        {
            "kind": "goal_completion_criteria",
            "content": "finish_remaining_active_work",
            "confidence": 0.8,
            "source": "background_reflection",
        },
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.active_goal_milestones = [
        {
            "id": 31,
            "goal_id": 11,
            "name": "Drive goal to closure",
            "phase": "completion_window",
            "status": "active",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-goal-milestone-ops-runtime",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-goal-milestone-ops-runtime"),
    )

    result = await runtime.run(event)

    assert result.active_goal_milestones[0].risk_level == "ready_to_close"
    assert result.active_goal_milestones[0].completion_criteria == "finish_remaining_active_work"
    assert "active milestone looks ready to close" in result.context.summary
    assert result.motivation.importance >= 0.83
    assert "validate_milestone_closure" in result.plan.steps
    assert "finish_remaining_active_work" in result.plan.steps


async def test_runtime_pipeline_uses_goal_milestone_history_across_context_motivation_and_planning() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.goal_milestone_history = [
        {
            "id": 31,
            "goal_id": 11,
            "milestone_name": "Drive goal to closure",
            "phase": "completion_window",
            "risk_level": "ready_to_close",
            "completion_criteria": "finish_remaining_active_work",
            "source_event_id": "evt-history-new",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "id": 30,
            "goal_id": 11,
            "milestone_name": "Stabilize goal recovery",
            "phase": "recovery_phase",
            "risk_level": "stabilizing",
            "completion_criteria": "stabilize_remaining_work",
            "source_event_id": "evt-history-old",
            "created_at": datetime.now(timezone.utc),
        },
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-goal-milestone-history-runtime",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-goal-milestone-history-runtime"),
    )

    result = await runtime.run(event)

    assert len(result.goal_milestone_history) == 2
    assert "Recent milestone history moved from recovery phase to completion window." in result.context.summary
    assert result.motivation.importance >= 0.8
    assert "protect_milestone_closure_arc" in result.plan.steps


async def test_runtime_pipeline_uses_user_profile_language_for_ambiguous_turn_without_recent_memory() -> None:
    memory = FakeMemoryRepository(
        recent_memory=[],
        user_profile={"preferred_language": "pl", "language_confidence": 0.92, "language_source": "explicit_request"},
    )
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-2",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "ok"},
        meta=EventMeta(user_id="u-1", trace_id="t-2"),
    )

    result = await runtime.run(event)

    assert result.perception.language == "pl"
    assert result.perception.language_source == "user_profile"
    assert result.expression.language == "pl"
    assert result.context.related_tags == ["general", "language:pl"]
    assert result.reflection_triggered is True
    assert memory.profile_updates == []
    assert openai.calls[0]["response_style"] == ""
    assert openai.calls[0]["response_tone"] == "supportive"
    assert openai.calls[0]["collaboration_preference"] == ""
    assert result.system_debug is not None
    assert result.system_debug.adaptive_state["language_continuity"]["selected_language"] == "pl"
    assert result.system_debug.adaptive_state["language_continuity"]["selected_source"] == "user_profile"
    assert result.system_debug.adaptive_state["language_continuity"]["continuity_resolution"] == "profile_only"
    assert result.system_debug.adaptive_state["language_continuity"]["profile_candidate"] == {
        "code": "pl",
        "confidence": 0.92,
        "source": "user_profile",
    }
    assert result.system_debug.adaptive_state["language_continuity"]["memory_candidate"] is None


async def test_runtime_pipeline_exposes_explicit_request_language_diagnostics_for_current_event() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    result = await runtime.run(
        Event(
            event_id="evt-language-explicit-debug",
            source="api",
            subsource="event_endpoint",
            timestamp=datetime.now(timezone.utc),
            payload={"text": "Reply in Polish, please."},
            meta=EventMeta(user_id="u-language-explicit-debug", trace_id="t-language-explicit-debug"),
        )
    )

    assert result.perception.language == "pl"
    assert result.perception.language_source == "explicit_request"
    assert result.system_debug is not None
    assert result.system_debug.adaptive_state["language_continuity"]["selected_source"] == "explicit_request"
    assert result.system_debug.adaptive_state["language_continuity"]["current_turn_posture"] == "explicit_request"
    assert result.system_debug.adaptive_state["language_continuity"]["continuity_resolution"] == (
        "not_needed_current_turn_signal"
    )
    assert result.system_debug.adaptive_state["language_continuity"]["fallback_posture"] == "not_used"


async def test_runtime_pipeline_ignores_unsupported_profile_language_in_continuity_diagnostics() -> None:
    memory = FakeMemoryRepository(
        recent_memory=[],
        user_profile={"preferred_language": "es", "language_confidence": 0.95, "language_source": "explicit_request"},
    )
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    result = await runtime.run(
        Event(
            event_id="evt-language-unsupported-profile",
            source="api",
            subsource="event_endpoint",
            timestamp=datetime.now(timezone.utc),
            payload={"text": "ok"},
            meta=EventMeta(user_id="u-language-unsupported-profile", trace_id="t-language-unsupported-profile"),
        )
    )

    assert result.perception.language == "en"
    assert result.perception.language_source == "default"
    assert result.expression.language == "en"
    assert result.system_debug is not None
    assert result.system_debug.adaptive_state["language_continuity"]["selected_source"] == "default"
    assert result.system_debug.adaptive_state["language_continuity"]["profile_candidate"] is None
    assert result.system_debug.adaptive_state["language_continuity"]["fallback_posture"] == "selected_default"


async def test_runtime_pipeline_preserves_language_continuity_across_session_restart_without_recent_memory() -> None:
    class SessionProfileMemoryRepository(PersistingFakeMemoryRepository):
        def __init__(self) -> None:
            super().__init__(recent_memory=[])
            self._user_profiles: dict[str, dict] = {}

        async def get_user_profile(self, user_id: str) -> dict | None:
            return self._user_profiles.get(user_id)

        async def upsert_user_profile_language(self, **kwargs) -> dict:
            stored = {
                "user_id": str(kwargs.get("user_id", "")),
                "preferred_language": str(kwargs.get("language_code", "")).strip().lower(),
                "language_confidence": float(kwargs.get("confidence", 0.0) or 0.0),
                "language_source": str(kwargs.get("source", "")).strip().lower(),
            }
            self.profile_updates.append(dict(kwargs))
            self._user_profiles[stored["user_id"]] = stored
            return stored

    memory = SessionProfileMemoryRepository()
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    runtime_session_one = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    first = await runtime_session_one.run(
        Event(
            event_id="evt-language-session-1",
            source="api",
            subsource="event_endpoint",
            timestamp=datetime.now(timezone.utc),
            payload={"text": "Reply in Polish, please."},
            meta=EventMeta(user_id="u-session-language", trace_id="t-language-session-1"),
        )
    )
    assert first.perception.language == "pl"
    assert first.perception.language_source == "explicit_request"
    assert memory.profile_updates

    memory.recent_memory = []

    runtime_session_two = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )
    second = await runtime_session_two.run(
        Event(
            event_id="evt-language-session-2",
            source="api",
            subsource="event_endpoint",
            timestamp=datetime.now(timezone.utc),
            payload={"text": "ok"},
            meta=EventMeta(user_id="u-session-language", trace_id="t-language-session-2"),
        )
    )

    assert second.perception.language == "pl"
    assert second.perception.language_source == "user_profile"
    assert second.expression.language == "pl"
    assert second.system_debug is not None
    assert second.system_debug.adaptive_state["language_continuity"]["selected_source"] == "user_profile"
    assert second.system_debug.adaptive_state["language_continuity"]["current_turn_posture"] == "no_current_turn_signal"
    assert second.system_debug.adaptive_state["language_continuity"]["fallback_posture"] == "not_used"


async def test_runtime_pipeline_applies_structured_response_preference_from_conclusion_memory() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {"response_style": "structured", "response_style_source": "explicit_request"}
    memory.user_conclusions = [
        {"kind": "response_style", "content": "structured", "confidence": 0.95, "source": "explicit_request"}
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-3",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "How should we deploy this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-3"),
    )

    result = await runtime.run(event)

    assert result.expression.message == "Mocked OpenAI reply"
    assert openai.calls[0]["response_style"] == "structured"
    assert "Stable user preferences: prefers structured responses." in result.context.summary
    assert "format_response_as_bullets" in result.plan.steps
    assert result.reflection_triggered is True
    assert openai.calls[0]["response_tone"] == "analytical"
    assert openai.calls[0]["collaboration_preference"] == ""


async def test_runtime_pipeline_applies_concise_response_preference_to_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {"response_style": "concise", "response_style_source": "explicit_request"}
    memory.user_conclusions = [
        {"kind": "response_style", "content": "concise", "confidence": 0.95, "source": "explicit_request"}
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-4",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you review the current deployment issue?"},
        meta=EventMeta(user_id="u-1", trace_id="t-4"),
    )

    result = await runtime.run(event)

    assert result.expression.message == "Mocked OpenAI reply"
    assert openai.calls[0]["response_style"] == "concise"
    assert "keep_response_concise" in result.plan.steps
    assert result.reflection_triggered is True
    assert openai.calls[0]["response_tone"] == "analytical"
    assert openai.calls[0]["collaboration_preference"] == ""


async def test_runtime_pipeline_uses_preferred_role_from_semantic_memory_for_ambiguous_question() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "preferred_role": "analyst",
        "preferred_role_confidence": 0.76,
    }
    memory.user_conclusions = [
        {"kind": "preferred_role", "content": "analyst", "confidence": 0.76, "source": "background_reflection"}
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-5",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-5"),
    )

    result = await runtime.run(event)

    assert result.role.selected == "analyst"
    assert result.role.selection_policy_owner == "role_selection_policy"
    assert result.role.selection_reason == "preferred_role_help_tie_break"
    assert any(item.source == "user_preference" and item.applied for item in result.role.selection_evidence)
    assert any(skill.skill_id == "structured_reasoning" for skill in result.role.selected_skills)
    assert any(skill.skill_id == "structured_reasoning" for skill in result.plan.selected_skills)
    assert result.reflection_triggered is True


async def test_runtime_pipeline_uses_theta_bias_when_no_preferred_role_exists() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_theta = {
        "support_bias": 0.12,
        "analysis_bias": 0.67,
        "execution_bias": 0.21,
    }
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-6",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-6"),
    )

    result = await runtime.run(event)

    assert result.role.selected == "analyst"
    assert result.reflection_triggered is True
    assert result.system_debug is not None
    assert result.system_debug.adaptive_state["theta_influence"]["dominant_channel"] == "analysis"
    assert result.system_debug.adaptive_state["theta_influence"]["role_posture"] == "applied"


async def test_runtime_pipeline_uses_active_goal_context_in_role_selection_diagnostics() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "Finish the rollout safely",
            "priority": "high",
            "status": "active",
            "goal_type": "tactical",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    ]
    memory.active_tasks = [
        {
            "id": 31,
            "user_id": "u-1",
            "goal_id": 11,
            "name": "fix deployment blocker",
            "description": "Resolve the blocker before release",
            "priority": "high",
            "status": "blocked",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-role-risk-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me plan how to ship the MVP this week?"},
        meta=EventMeta(user_id="u-1", trace_id="t-role-risk-1"),
    )

    result = await runtime.run(event)

    assert result.role.selected == "analyst"
    assert result.role.selection_reason == "planning_topic_active_goal_context"
    assert any(item.signal == "active_goal_context" and item.applied for item in result.role.selection_evidence)
    assert result.role.confidence == 0.85
    assert result.system_debug is not None
    assert result.system_debug.role.selection_reason == "planning_topic_active_goal_context"


async def test_runtime_pipeline_uses_theta_bias_for_motivation_and_planning_on_brief_turn() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_theta = {
        "support_bias": 0.14,
        "analysis_bias": 0.71,
        "execution_bias": 0.15,
    }
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-7",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "help me"},
        meta=EventMeta(user_id="u-1", trace_id="t-7"),
    )

    result = await runtime.run(event)

    assert result.motivation.mode == "analyze"
    assert result.role.selected == "analyst"
    assert "break_down_problem" in result.plan.steps or "favor_structured_reasoning" in result.plan.steps
    assert result.reflection_triggered is True
    assert result.expression.tone == "analytical"
    assert openai.calls[0]["response_tone"] == "analytical"
    assert result.system_debug is not None
    assert result.system_debug.adaptive_state["theta_influence"]["motivation_posture"] == "applied"
    assert result.system_debug.adaptive_state["theta_influence"]["planning_posture"] == "eligible_not_selected"
    assert result.system_debug.adaptive_state["theta_influence"]["expression_posture"] == "applied"


async def test_runtime_pipeline_uses_collaboration_preference_in_context_and_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "collaboration_preference": "hands_on",
        "collaboration_preference_confidence": 0.73,
    }
    memory.user_conclusions = [
        {
            "kind": "collaboration_preference",
            "content": "hands_on",
            "confidence": 0.73,
            "source": "background_reflection",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-8",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-8"),
    )

    result = await runtime.run(event)

    assert "Stable user preferences: prefers concrete execution help." in result.context.summary
    assert result.plan.goal == "Move the requested task toward execution with the smallest concrete next step."
    assert "propose_execution_step" in result.plan.steps
    assert result.reflection_triggered is True
    assert result.expression.tone == "action-oriented"
    assert openai.calls[0]["collaboration_preference"] == "hands_on"
    assert openai.calls[0]["response_tone"] == "action-oriented"


async def test_runtime_pipeline_uses_guided_collaboration_preference_for_role_and_motivation() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "collaboration_preference": "guided",
        "collaboration_preference_confidence": 0.73,
    }
    memory.user_conclusions = [
        {
            "kind": "collaboration_preference",
            "content": "guided",
            "confidence": 0.73,
            "source": "background_reflection",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-9",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-9"),
    )

    result = await runtime.run(event)

    assert result.motivation.mode == "analyze"
    assert result.role.selected == "mentor"
    assert result.plan.goal == "Explain the situation clearly with a guided step by step path."
    assert "break_down_problem" in result.plan.steps
    assert result.expression.tone == "guiding"
    assert openai.calls[0]["collaboration_preference"] == "guided"
    assert openai.calls[0]["response_tone"] == "guiding"


async def test_runtime_pipeline_identity_uses_conclusion_owner_not_relation_fallback_for_collaboration() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    memory.relations = [
        {
            "relation_type": "collaboration_dynamic",
            "relation_value": "guided",
            "confidence": 0.81,
            "source": "background_reflection",
            "scope_type": "global",
            "scope_key": "global",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-identity-owner-boundary",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-identity-owner-boundary"),
    )

    result = await runtime.run(event)

    assert result.identity.collaboration_preference is None
    assert "Collaboration preference:" not in result.identity.summary
    assert openai.calls[0]["collaboration_preference"] == "guided"
    assert result.system_debug is not None
    assert result.system_debug.adaptive_state["identity_policy"] == {
        "policy_owner": "identity_policy",
        "language_strategy": "heuristic_plus_profile_continuity",
        "profile_owner_fields": ["preferred_language"],
        "conclusion_owner_fields": ["response_style", "collaboration_preference", "preferred_role"],
        "relation_fallback_identity_write": "disallowed",
        "supported_language_codes": ["en", "pl"],
        "multilingual_posture": "mvp_supported_languages_only",
    }


async def test_runtime_pipeline_uses_reflected_goal_execution_state_across_context_motivation_and_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_execution_state": "blocked",
        "goal_execution_state_confidence": 0.82,
    }
    memory.user_conclusions = [
        {
            "kind": "goal_execution_state",
            "content": "blocked",
            "confidence": 0.82,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-10",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me move the MVP forward?"},
        meta=EventMeta(user_id="u-1", trace_id="t-10"),
    )

    result = await runtime.run(event)

    assert "Stable user preferences: current goal progress is blocked by an active task." in result.context.summary
    assert result.motivation.mode == "analyze"
    assert result.motivation.importance >= 0.75
    assert "align_with_active_goal" in result.plan.steps
    assert "recover_goal_progress" in result.plan.steps
    assert result.reflection_triggered is True


async def test_runtime_pipeline_uses_stagnating_goal_execution_state_to_restart_goal_progress() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_execution_state": "stagnating",
        "goal_execution_state_confidence": 0.72,
    }
    memory.user_conclusions = [
        {
            "kind": "goal_execution_state",
            "content": "stagnating",
            "confidence": 0.72,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-11",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-11"),
    )

    result = await runtime.run(event)

    assert "Stable user preferences: current goal seems to be stagnating without recent execution." in result.context.summary
    assert result.motivation.mode == "analyze"
    assert result.motivation.importance >= 0.73
    assert "align_with_active_goal" in result.plan.steps
    assert "restart_goal_progress" in result.plan.steps
    assert result.reflection_triggered is True


async def test_runtime_pipeline_uses_recovering_goal_execution_state_to_stabilize_recovery() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_execution_state": "recovering",
        "goal_execution_state_confidence": 0.77,
    }
    memory.user_conclusions = [
        {
            "kind": "goal_execution_state",
            "content": "recovering",
            "confidence": 0.77,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-12",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-12"),
    )

    result = await runtime.run(event)

    assert "Stable user preferences: current goal is recovering after a recent unblock or completion." in result.context.summary
    assert result.motivation.mode == "analyze"
    assert result.motivation.importance >= 0.74
    assert "align_with_active_goal" in result.plan.steps
    assert "stabilize_goal_recovery" in result.plan.steps
    assert result.reflection_triggered is True


async def test_runtime_pipeline_uses_advancing_goal_execution_state_to_continue_execution() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_execution_state": "advancing",
        "goal_execution_state_confidence": 0.75,
    }
    memory.user_conclusions = [
        {
            "kind": "goal_execution_state",
            "content": "advancing",
            "confidence": 0.75,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-13",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-13"),
    )

    result = await runtime.run(event)

    assert "Stable user preferences: current goal work is actively advancing." in result.context.summary
    assert result.motivation.mode == "analyze"
    assert result.motivation.importance >= 0.73
    assert "align_with_active_goal" in result.plan.steps
    assert "continue_goal_execution" in result.plan.steps
    assert result.reflection_triggered is True


async def test_runtime_pipeline_uses_goal_progress_score_to_push_goal_to_completion() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_progress_score": 0.84,
        "goal_progress_score_confidence": 0.74,
    }
    memory.user_conclusions = [
        {
            "kind": "goal_progress_score",
            "content": "0.84",
            "confidence": 0.74,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-14",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-14"),
    )

    result = await runtime.run(event)

    assert "Stable user preferences: goal completion is entering the final stretch." in result.context.summary
    assert result.motivation.mode == "analyze"
    assert result.motivation.importance >= 0.73
    assert "align_with_active_goal" in result.plan.steps
    assert "push_goal_to_completion" in result.plan.steps
    assert result.reflection_triggered is True


async def test_runtime_pipeline_uses_goal_progress_trend_to_correct_drift() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_progress_score": 0.28,
        "goal_progress_score_confidence": 0.74,
        "goal_progress_trend": "slipping",
        "goal_progress_trend_confidence": 0.75,
    }
    memory.user_conclusions = [
        {
            "kind": "goal_progress_trend",
            "content": "slipping",
            "confidence": 0.75,
            "source": "background_reflection",
        },
        {
            "kind": "goal_progress_score",
            "content": "0.28",
            "confidence": 0.74,
            "source": "background_reflection",
        },
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-15",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-15"),
    )

    result = await runtime.run(event)

    assert "goal progress trend is slipping" in result.context.summary
    assert result.motivation.mode == "analyze"
    assert result.motivation.importance >= 0.79
    assert "align_with_active_goal" in result.plan.steps
    assert "increase_goal_progress" in result.plan.steps
    assert "correct_goal_drift" in result.plan.steps
    assert result.reflection_triggered is True


async def test_runtime_pipeline_uses_goal_progress_history_for_context_and_planning() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.goal_progress_history = [
        {
            "id": 3,
            "goal_id": 11,
            "score": 0.72,
            "execution_state": "advancing",
            "progress_trend": "improving",
            "source_event_id": "evt-older",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "id": 2,
            "goal_id": 11,
            "score": 0.49,
            "execution_state": "recovering",
            "progress_trend": "improving",
            "source_event_id": "evt-old",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "id": 1,
            "goal_id": 11,
            "score": 0.26,
            "execution_state": "blocked",
            "progress_trend": "slipping",
            "source_event_id": "evt-oldest",
            "created_at": datetime.now(timezone.utc),
        },
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-16",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-16"),
    )

    result = await runtime.run(event)

    assert len(result.goal_progress_history) == 3
    assert "Recent goal history shows lift from 0.26 to 0.72." in result.context.summary
    assert result.motivation.importance >= 0.75
    assert "align_with_active_goal" in result.plan.steps
    assert "protect_goal_trajectory" in result.plan.steps


async def test_runtime_pipeline_uses_goal_progress_arc_across_context_motivation_and_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_progress_arc": "recovery_gaining_traction",
        "goal_progress_arc_confidence": 0.76,
    }
    memory.user_conclusions = [
        {
            "kind": "goal_progress_arc",
            "content": "recovery_gaining_traction",
            "confidence": 0.76,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-17",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-17"),
    )

    result = await runtime.run(event)

    assert "goal recovery is gaining traction" in result.context.summary
    assert result.motivation.mode == "analyze"
    assert result.motivation.importance >= 0.76
    assert "align_with_active_goal" in result.plan.steps
    assert "consolidate_goal_recovery" in result.plan.steps


async def test_runtime_pipeline_uses_goal_milestone_arc_across_context_motivation_and_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_milestone_arc": "reentered_completion_window",
        "goal_milestone_arc_confidence": 0.79,
        "goal_milestone_risk": "ready_to_close",
        "goal_completion_criteria": "confirm_goal_completion",
    }
    memory.user_conclusions = [
        {
            "kind": "goal_milestone_arc",
            "content": "reentered_completion_window",
            "confidence": 0.79,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.active_goal_milestones = [
        {
            "id": 41,
            "goal_id": 11,
            "name": "Drive goal to closure",
            "phase": "completion_window",
            "status": "active",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-milestone-arc",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-milestone-arc"),
    )

    result = await runtime.run(event)

    assert result.active_goal_milestones[0].arc == "reentered_completion_window"
    assert "Stable user preferences: active milestone has re-entered the completion window after recovery." in result.context.summary
    assert "Active milestones: Drive goal to closure (completion_window, re-entered completion window, ready_to_close, confirm goal completion)." in result.context.summary
    assert result.motivation.importance >= 0.8
    assert "align_with_active_goal" in result.plan.steps
    assert "stabilize_reentered_completion_window" in result.plan.steps


async def test_runtime_pipeline_uses_goal_milestone_pressure_across_context_motivation_and_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_milestone_pressure": "lingering_completion",
        "goal_milestone_pressure_confidence": 0.8,
        "goal_milestone_risk": "ready_to_close",
        "goal_completion_criteria": "confirm_goal_completion",
    }
    memory.user_conclusions = [
        {
            "kind": "goal_milestone_pressure",
            "content": "lingering_completion",
            "confidence": 0.8,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.active_goal_milestones = [
        {
            "id": 41,
            "goal_id": 11,
            "name": "Drive goal to closure",
            "phase": "completion_window",
            "status": "active",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-milestone-pressure",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-milestone-pressure"),
    )

    result = await runtime.run(event)

    assert result.active_goal_milestones[0].pressure_level == "lingering_completion"
    assert "Stable user preferences: active milestone has lingered in the completion window for too long." in result.context.summary
    assert "Active milestones: Drive goal to closure (completion_window, lingering completion, ready_to_close, confirm goal completion)." in result.context.summary
    assert result.motivation.importance >= 0.82
    assert "align_with_active_goal" in result.plan.steps
    assert "force_goal_closure_decision" in result.plan.steps


async def test_runtime_pipeline_uses_goal_milestone_dependency_state_across_context_motivation_and_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_milestone_dependency_state": "multi_step_dependency",
        "goal_milestone_dependency_state_confidence": 0.76,
        "goal_milestone_risk": "ready_to_close",
        "goal_completion_criteria": "finish_remaining_active_work",
    }
    memory.user_conclusions = [
        {
            "kind": "goal_milestone_dependency_state",
            "content": "multi_step_dependency",
            "confidence": 0.76,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.active_goal_milestones = [
        {
            "id": 41,
            "goal_id": 11,
            "name": "Drive goal to closure",
            "phase": "completion_window",
            "status": "active",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-milestone-dependency",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-milestone-dependency"),
    )

    result = await runtime.run(event)

    assert result.active_goal_milestones[0].dependency_state == "multi_step_dependency"
    assert "Stable user preferences: active milestone still depends on multiple remaining work items." in result.context.summary
    assert "Active milestones: Drive goal to closure (completion_window, multi-step dependency chain, ready_to_close, finish remaining active work)." in result.context.summary
    assert result.motivation.importance >= 0.79
    assert "align_with_active_goal" in result.plan.steps
    assert "sequence_remaining_dependencies" in result.plan.steps


async def test_runtime_pipeline_uses_goal_milestone_due_state_across_context_motivation_and_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_milestone_due_state": "dependency_due_next",
        "goal_milestone_due_state_confidence": 0.79,
        "goal_milestone_risk": "ready_to_close",
        "goal_completion_criteria": "finish_remaining_active_work",
    }
    memory.user_conclusions = [
        {
            "kind": "goal_milestone_due_state",
            "content": "dependency_due_next",
            "confidence": 0.79,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.active_goal_milestones = [
        {
            "id": 41,
            "goal_id": 11,
            "name": "Drive goal to closure",
            "phase": "completion_window",
            "status": "active",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-milestone-due",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-milestone-due"),
    )

    result = await runtime.run(event)

    assert result.active_goal_milestones[0].due_state == "dependency_due_next"
    assert "Stable user preferences: active milestone is due to resolve its next dependency." in result.context.summary
    assert "Active milestones: Drive goal to closure (completion_window, next dependency is due now, ready_to_close, finish remaining active work)." in result.context.summary
    assert result.motivation.importance >= 0.8
    assert "align_with_active_goal" in result.plan.steps
    assert "finish_due_dependency" in result.plan.steps


async def test_runtime_pipeline_uses_goal_milestone_due_window_across_context_motivation_and_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "goal_milestone_due_window": "overdue_due_window",
        "goal_milestone_due_window_confidence": 0.82,
        "goal_milestone_risk": "ready_to_close",
        "goal_completion_criteria": "confirm_goal_completion",
    }
    memory.user_conclusions = [
        {
            "kind": "goal_milestone_due_window",
            "content": "overdue_due_window",
            "confidence": 0.82,
            "source": "background_reflection",
        }
    ]
    memory.active_goals = [
        {
            "id": 11,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory.active_goal_milestones = [
        {
            "id": 41,
            "goal_id": 11,
            "name": "Drive goal to closure",
            "phase": "completion_window",
            "status": "active",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-milestone-due-window",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What should I do next for the MVP?"},
        meta=EventMeta(user_id="u-1", trace_id="t-milestone-due-window"),
    )

    result = await runtime.run(event)

    assert result.active_goal_milestones[0].due_window == "overdue_due_window"
    assert "Stable user preferences: active milestone due window has become overdue." in result.context.summary
    assert "Active milestones: Drive goal to closure (completion_window, overdue due window, ready_to_close, confirm goal completion)." in result.context.summary
    assert result.motivation.importance >= 0.81
    assert "align_with_active_goal" in result.plan.steps
    assert "recover_overdue_window" in result.plan.steps


async def test_runtime_pipeline_runs_proactive_warning_tick_with_response_enabled() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {"proactive_opt_in": True}
    memory.active_tasks = [
        {
            "id": 11,
            "goal_id": 7,
            "name": "fix deployment blocker",
            "description": "Deploy is blocked by failing migration",
            "priority": "high",
            "status": "blocked",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = build_scheduler_event(
        subsource="proactive_tick",
        payload={
            "text": "check blocker urgency",
            "chat_id": 123456,
            "proactive_trigger": "task_blocked",
            "importance": 0.88,
            "urgency": 0.9,
            "user_context": {
                "quiet_hours": False,
                "focus_mode": False,
                "recent_user_activity": "active",
                "recent_outbound_count": 0,
                "unanswered_proactive_count": 0,
            },
        },
    )

    result = await runtime.run(event)

    assert result.event.source == "scheduler"
    assert result.event.subsource == "proactive_tick"
    assert result.plan.proactive_decision is not None
    assert result.plan.proactive_decision.output_type == "warning"
    assert result.plan.proactive_decision.should_interrupt is True
    assert result.plan.proactive_delivery_guard is not None
    assert result.plan.proactive_delivery_guard.allowed is True
    assert result.plan.domain_intents[0].intent_type == "update_proactive_state"
    assert result.plan.domain_intents[0].state == "delivery_ready"
    assert result.motivation.mode == "execute"
    assert "compose_proactive_warning" in result.plan.steps
    assert "send_telegram_message" in result.plan.steps
    assert result.plan.needs_response is True
    assert result.plan.needs_action is True
    assert result.action_result.status == "success"
    assert result.action_result.actions == ["send_telegram_message"]
    assert result.reflection_triggered is True
    assert memory.conclusion_updates == [
        {
            "user_id": "scheduler",
            "kind": "proactive_outreach_state",
            "content": "delivery_ready",
            "confidence": 0.9,
            "source": "proactive_planning",
            "supporting_event_id": event.event_id,
        },
        {
            "user_id": "scheduler",
            "kind": "proactive_outreach_trigger",
            "content": "task_blocked",
            "confidence": 0.9,
            "source": "proactive_planning",
            "supporting_event_id": event.event_id,
        },
    ]


async def test_runtime_pipeline_defers_proactive_tick_when_interruption_cost_is_high() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.active_goals = [
        {
            "id": 9,
            "user_id": "scheduler",
            "name": "ship weekly milestone",
            "description": "User-declared goal: ship weekly milestone",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = build_scheduler_event(
        subsource="proactive_tick",
        payload={
            "text": "quiet-hours check",
            "proactive_trigger": "goal_stagnation",
            "importance": 0.84,
            "urgency": 0.72,
            "user_context": {
                "quiet_hours": True,
                "focus_mode": True,
                "recent_user_activity": "away",
                "recent_outbound_count": 3,
                "unanswered_proactive_count": 2,
            },
        },
    )

    result = await runtime.run(event)

    assert result.plan.proactive_decision is not None
    assert result.plan.proactive_decision.should_interrupt is False
    assert result.plan.proactive_delivery_guard is None
    assert result.motivation.mode == "ignore"
    assert (
        "defer_proactive_outreach" in result.plan.steps
        or "respect_attention_gate" in result.plan.steps
    )
    assert result.plan.needs_response is False
    assert result.action_result.status == "noop"
    assert result.reflection_triggered is True
    assert result.plan.domain_intents[0].intent_type == "update_proactive_state"
    assert result.plan.domain_intents[0].state == "attention_gate_blocked"
    assert memory.conclusion_updates[0]["content"] == "attention_gate_blocked"


async def test_runtime_pipeline_defers_proactive_tick_when_user_did_not_opt_in() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.active_tasks = [
        {
            "id": 11,
            "goal_id": 7,
            "name": "fix deployment blocker",
            "description": "Deploy is blocked by failing migration",
            "priority": "high",
            "status": "blocked",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = build_scheduler_event(
        subsource="proactive_tick",
        payload={
            "text": "check blocker urgency",
            "chat_id": 123456,
            "proactive_trigger": "task_blocked",
            "importance": 0.88,
            "urgency": 0.9,
            "user_context": {
                "quiet_hours": False,
                "focus_mode": False,
                "recent_user_activity": "active",
                "recent_outbound_count": 0,
                "unanswered_proactive_count": 0,
            },
        },
    )

    result = await runtime.run(event)

    assert result.plan.proactive_decision is not None
    assert result.plan.proactive_decision.should_interrupt is True
    assert result.plan.proactive_delivery_guard is not None
    assert result.plan.proactive_delivery_guard.allowed is False
    assert result.plan.proactive_delivery_guard.reason == "opt_in_required"
    assert "respect_proactive_delivery_guardrails" in result.plan.steps
    assert result.plan.needs_response is False
    assert result.action_result.status == "noop"
    assert result.plan.domain_intents[0].intent_type == "update_proactive_state"
    assert result.plan.domain_intents[0].state == "delivery_guard_blocked"
    assert memory.conclusion_updates[0]["content"] == "delivery_guard_blocked"


async def test_runtime_pipeline_applies_adaptive_attention_limits_without_bypassing_guardrails() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    memory.user_preferences = {"proactive_opt_in": True}
    memory.user_theta = {
        "support_bias": 0.71,
        "analysis_bias": 0.14,
        "execution_bias": 0.15,
    }
    memory.relations = [
        {
            "relation_type": "support_intensity_preference",
            "relation_value": "high_support",
            "confidence": 0.78,
        }
    ]
    memory.active_tasks = [
        {
            "id": 11,
            "goal_id": 7,
            "name": "check in with blocked deploy task",
            "description": "Deploy remains blocked",
            "priority": "high",
            "status": "blocked",
        }
    ]
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = build_scheduler_event(
        subsource="proactive_tick",
        payload={
            "text": "supportive check-in",
            "chat_id": 123456,
            "proactive_trigger": "task_blocked",
            "importance": 0.86,
            "urgency": 0.82,
            "user_context": {
                "quiet_hours": False,
                "focus_mode": False,
                "recent_user_activity": "active",
                "recent_outbound_count": 2,
                "unanswered_proactive_count": 1,
            },
        },
    )

    result = await runtime.run(event)

    assert result.plan.proactive_decision is not None
    assert result.plan.proactive_decision.should_interrupt is True
    assert result.event.payload["attention_gate"]["allowed"] is False
    assert result.event.payload["attention_gate"]["reason"] == "attention_unanswered_backlog"
    assert result.event.payload["attention_gate"]["unanswered_proactive_limit"] == 1
    assert result.event.payload["attention_gate"]["theta_channel"] == "support"
    assert "respect_attention_gate" in result.plan.steps
    assert result.plan.needs_response is False
    assert result.action_result.status == "noop"
    assert result.plan.domain_intents[0].state == "attention_gate_blocked"


async def test_runtime_pipeline_tightens_attention_gate_for_low_delivery_trust() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    memory.user_preferences = {"proactive_opt_in": True}
    memory.relations = [
        {
            "relation_type": "delivery_reliability",
            "relation_value": "low_trust",
            "confidence": 0.81,
        }
    ]
    memory.active_tasks = [
        {
            "id": 11,
            "goal_id": 7,
            "name": "check in with blocked deploy task",
            "description": "Deploy remains blocked",
            "priority": "high",
            "status": "blocked",
        }
    ]
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = build_scheduler_event(
        subsource="proactive_tick",
        payload={
            "text": "follow up on blocked deploy",
            "chat_id": 123456,
            "proactive_trigger": "task_blocked",
            "importance": 0.9,
            "urgency": 0.85,
            "user_context": {
                "quiet_hours": False,
                "focus_mode": False,
                "recent_user_activity": "active",
                "recent_outbound_count": 1,
                "unanswered_proactive_count": 0,
            },
        },
    )

    result = await runtime.run(event)

    assert result.plan.proactive_decision is not None
    assert result.plan.proactive_decision.should_interrupt is True
    assert result.event.payload["attention_gate"]["allowed"] is False
    assert result.event.payload["attention_gate"]["reason"] == "attention_outbound_cooldown"
    assert result.event.payload["attention_gate"]["recent_outbound_limit"] == 1
    assert result.event.payload["attention_gate"]["relation_delivery_reliability"] == "low_trust"
    assert "respect_attention_gate" in result.plan.steps
    assert result.action_result.status == "noop"
    assert result.plan.domain_intents[0].state == "attention_gate_blocked"


async def test_runtime_pipeline_ignores_low_confidence_delivery_trust_for_attention_gate() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    memory.user_preferences = {"proactive_opt_in": True}
    memory.relations = [
        {
            "relation_type": "delivery_reliability",
            "relation_value": "low_trust",
            "confidence": 0.67,
        }
    ]
    memory.active_tasks = [
        {
            "id": 11,
            "goal_id": 7,
            "name": "check in with blocked deploy task",
            "description": "Deploy remains blocked",
            "priority": "high",
            "status": "blocked",
        }
    ]
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = build_scheduler_event(
        subsource="proactive_tick",
        payload={
            "text": "follow up on blocked deploy",
            "chat_id": 123456,
            "proactive_trigger": "task_blocked",
            "importance": 0.9,
            "urgency": 0.85,
            "user_context": {
                "quiet_hours": False,
                "focus_mode": False,
                "recent_user_activity": "active",
                "recent_outbound_count": 1,
                "unanswered_proactive_count": 0,
            },
        },
    )

    result = await runtime.run(event)

    assert result.plan.proactive_decision is not None
    assert result.plan.proactive_decision.should_interrupt is True
    assert result.event.payload["attention_gate"]["allowed"] is True
    assert result.event.payload["attention_gate"]["recent_outbound_limit"] == 3
    assert result.event.payload["attention_gate"]["relation_delivery_reliability"] is None
    assert result.plan.proactive_delivery_guard is not None
    assert result.plan.proactive_delivery_guard.recent_outbound_limit == 2
    assert "respect_attention_gate" not in result.plan.steps
    assert result.action_result.status == "success"


async def test_runtime_pipeline_keeps_proactive_tick_separate_from_proposal_handoff_and_connector_permission_gates() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {"proactive_opt_in": True}
    memory.active_tasks = [
        {
            "id": 11,
            "goal_id": 7,
            "name": "fix deployment blocker",
            "description": "Deploy is blocked by failing migration",
            "priority": "high",
            "status": "blocked",
        }
    ]
    memory.pending_subconscious_proposals = [
        {
            "proposal_id": 801,
            "proposal_type": "ask_user",
            "summary": "Ask user to confirm blocker details.",
            "payload": {"question_focus": "blocker details"},
            "confidence": 0.74,
            "status": "pending",
            "research_policy": "read_only",
            "allowed_tools": ["memory_retrieval"],
            "source_event_id": "evt-prop-801",
        },
        {
            "proposal_id": 802,
            "proposal_type": "suggest_connector_expansion",
            "summary": "Suggest clickup task sync connector expansion.",
            "payload": {
                "connector_kind": "task_system",
                "provider_hint": "clickup",
                "requested_capability": "task_sync",
            },
            "confidence": 0.79,
            "status": "pending",
            "research_policy": "read_only",
            "allowed_tools": [],
            "source_event_id": "evt-prop-802",
        },
    ]
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = build_scheduler_event(
        subsource="proactive_tick",
        payload={
            "text": "please connect clickup and calendar for this blocker",
            "chat_id": 123456,
            "proactive_trigger": "task_blocked",
            "importance": 0.88,
            "urgency": 0.9,
            "user_context": {
                "quiet_hours": False,
                "focus_mode": False,
                "recent_user_activity": "active",
                "recent_outbound_count": 0,
                "unanswered_proactive_count": 0,
            },
        },
    )

    result = await runtime.run(event)

    assert result.plan.proactive_decision is not None
    assert result.plan.needs_response is True
    assert result.plan.needs_action is True
    assert result.plan.domain_intents[0].intent_type == "update_proactive_state"
    assert result.plan.domain_intents[0].state == "delivery_ready"
    assert result.plan.proposal_handoffs == []
    assert result.plan.accepted_proposals == []
    assert result.plan.connector_permission_gates == []
    assert len(memory.resolved_subconscious_proposals) == 0
    assert all(item["status"] == "pending" for item in memory.pending_subconscious_proposals)
    assert result.memory_record is not None
    assert result.memory_record.payload["connector_expansion_update"] == ""
    assert result.memory_record.payload["calendar_connector_update"] == ""
    assert result.memory_record.payload["task_connector_update"] == ""
    assert result.memory_record.payload["drive_connector_update"] == ""
    assert result.memory_record.payload["relation_update"] == ""
    assert result.memory_record.payload["proactive_state_update"] == "delivery_ready:task_blocked:delivery_ready"
    assert result.memory_record.payload["connector_expansion_guardrail"] == ""
    assert result.memory_record.payload["calendar_connector_guardrail"] == ""
    assert result.memory_record.payload["task_connector_guardrail"] == ""
    assert result.memory_record.payload["drive_connector_guardrail"] == ""
    assert "proposal_handoff" not in result.stage_timings_ms


async def test_runtime_pipeline_promotes_and_resolves_pending_subconscious_proposals() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.pending_subconscious_proposals = [
        {
            "proposal_id": 41,
            "proposal_type": "ask_user",
            "summary": "Ask the user to clarify blocker scope.",
            "payload": {"question_focus": "blocker scope"},
            "confidence": 0.75,
            "status": "pending",
            "research_policy": "read_only",
            "allowed_tools": ["memory_retrieval"],
            "source_event_id": "evt-prop-41",
        },
        {
            "proposal_id": 42,
            "proposal_type": "nudge_user",
            "summary": "Nudge user toward one unblock step.",
            "payload": {"task_name": "deploy blocker"},
            "confidence": 0.7,
            "status": "pending",
            "research_policy": "read_only",
            "allowed_tools": [],
            "source_event_id": "evt-prop-42",
        },
    ]
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = Event(
        event_id="evt-proposal-promotion",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this deploy blocker?"},
        meta=EventMeta(user_id="u-1", trace_id="t-proposal-promotion"),
    )

    result = await runtime.run(event)

    assert len(result.plan.proposal_handoffs) == 2
    assert result.plan.proposal_handoffs[0].decision == "accept"
    assert len(result.plan.accepted_proposals) == 1
    assert result.plan.accepted_proposals[0].proposal_id == 41
    assert "ask_subconscious_clarifier" in result.plan.steps
    assert len(memory.resolved_subconscious_proposals) == 2
    assert "proposal_handoff" in result.stage_timings_ms


async def test_runtime_pipeline_reenters_deferred_subconscious_proposal_for_conscious_handoff() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.pending_subconscious_proposals = [
        {
            "proposal_id": 55,
            "proposal_type": "ask_user",
            "summary": "Deferred clarifier can re-enter conscious turn.",
            "payload": {"question_focus": "blocker scope refresh"},
            "confidence": 0.72,
            "status": "deferred",
            "research_policy": "read_only",
            "allowed_tools": ["memory_retrieval"],
            "source_event_id": "evt-prop-55",
        }
    ]
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = Event(
        event_id="evt-proposal-reentry",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me validate this blocker again?"},
        meta=EventMeta(user_id="u-1", trace_id="t-proposal-reentry"),
    )

    result = await runtime.run(event)

    assert len(result.plan.proposal_handoffs) == 1
    assert result.plan.proposal_handoffs[0].proposal_id == 55
    assert result.plan.proposal_handoffs[0].decision == "accept"
    assert len(result.plan.accepted_proposals) == 1
    assert result.plan.accepted_proposals[0].proposal_id == 55
    assert "ask_subconscious_clarifier" in result.plan.steps
    assert len(memory.resolved_subconscious_proposals) == 1
    assert memory.resolved_subconscious_proposals[0]["proposal_id"] == 55
    assert memory.resolved_subconscious_proposals[0]["decision"] == "accept"


async def test_runtime_pipeline_delivers_due_planned_work_through_foreground_path() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.pending_subconscious_proposals = [
        {
            "proposal_id": 91,
            "proposal_type": "nudge_user",
            "summary": "planned_work_due:9:send the release summary",
            "payload": {
                "handoff_kind": "planned_work_due",
                "work_id": 9,
                "work_kind": "reminder",
                "summary": "send the release summary",
                "delivery_channel": "telegram",
                "source_event_id": "evt-reminder-1",
            },
            "confidence": 0.82,
            "status": "pending",
            "research_policy": "read_only",
            "allowed_tools": [],
            "source_event_id": "evt-reminder-1",
        }
    ]
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = build_scheduler_event(
        subsource="maintenance_tick",
        user_id="123456",
        payload={
            "text": "planned work due: send the release summary",
            "chat_id": 123456,
            "planned_work_due": {
                "work_id": 9,
                "summary": "send the release summary",
                "work_kind": "reminder",
                "delivery_channel": "telegram",
                "source_event_id": "evt-reminder-1",
            },
        },
    )

    result = await runtime.run(event)

    assert result.plan.goal == "Deliver the due planned-work follow-up with one clear immediate next step."
    assert result.plan.steps == [
        "interpret_event",
        "review_context",
        "integrate_subconscious_nudge",
        "prepare_response",
        "send_telegram_message",
    ]
    assert result.plan.needs_response is True
    assert result.plan.needs_action is True
    assert len(result.plan.proposal_handoffs) == 1
    assert result.plan.proposal_handoffs[0].proposal_id == 91
    assert result.plan.proposal_handoffs[0].decision == "accept"
    assert result.plan.proposal_handoffs[0].reason == "scheduled_due_planned_work_handoff"
    assert len(result.plan.accepted_proposals) == 1
    assert result.plan.accepted_proposals[0].proposal_id == 91
    assert result.expression.channel == "telegram"
    assert result.action_result.status == "success"
    assert result.action_result.actions == ["send_telegram_message"]
    assert len(memory.resolved_subconscious_proposals) == 1
    assert memory.resolved_subconscious_proposals[0]["proposal_id"] == 91
    assert memory.resolved_subconscious_proposals[0]["decision"] == "accept"
    assert "proposal_handoff" in result.stage_timings_ms


async def test_runtime_pipeline_emits_connector_expansion_discovery_outputs_from_pending_proposal() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.pending_subconscious_proposals = [
        {
            "proposal_id": 77,
            "proposal_type": "suggest_connector_expansion",
            "summary": "Suggest connector expansion for clickup task_system capability 'task_sync'.",
            "payload": {
                "connector_kind": "task_system",
                "provider_hint": "clickup",
                "requested_capability": "task_sync",
            },
            "confidence": 0.79,
            "status": "pending",
            "research_policy": "read_only",
            "allowed_tools": [],
            "source_event_id": "evt-prop-77",
        }
    ]
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = Event(
        event_id="evt-connector-expansion",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "What could we improve in integrations?"},
        meta=EventMeta(user_id="u-1", trace_id="t-connector-expansion"),
    )

    result = await runtime.run(event)

    assert len(result.plan.proposal_handoffs) == 1
    assert result.plan.proposal_handoffs[0].decision == "accept"
    assert result.plan.proposal_handoffs[0].reason == "connector_capability_gap_detected"
    assert "propose_connector_capability_expansion" in result.plan.steps
    assert any(intent.intent_type == "connector_capability_discovery_intent" for intent in result.plan.domain_intents)
    assert any(
        gate.reason == "proposal_only_no_external_access"
        and gate.operation == "discover_task_sync"
        and gate.allowed is True
        for gate in result.plan.connector_permission_gates
    )
    assert result.memory_record is not None
    assert result.memory_record.payload["connector_expansion_update"] == "task_system:clickup:task_sync"
    assert (
        result.memory_record.payload["connector_expansion_guardrail"]
        == "proposal_only_no_external_access:allowed_without_external_access"
    )
    assert len(memory.resolved_subconscious_proposals) == 1


async def test_runtime_pipeline_emits_connector_permission_gates_and_connector_payload_updates() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = Event(
        event_id="evt-connector-intents",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Create calendar meeting tomorrow, create task in ClickUp, and upload notes to Google Drive."},
        meta=EventMeta(user_id="u-1", trace_id="t-connector-intents"),
    )

    result = await runtime.run(event)

    assert len(result.plan.connector_permission_gates) == 3
    assert {gate.connector_kind for gate in result.plan.connector_permission_gates} == {"calendar", "task_system", "cloud_drive"}
    assert all(gate.allowed is False for gate in result.plan.connector_permission_gates)
    assert result.memory_record is not None
    assert result.memory_record.payload["calendar_connector_update"] == "create_event:mutate_with_confirmation:generic"
    assert result.memory_record.payload["task_connector_update"] == "create_task:mutate_with_confirmation:clickup"
    assert result.memory_record.payload["drive_connector_update"] == "upload_file:mutate_with_confirmation:google_drive"
    assert (
        result.memory_record.payload["calendar_connector_guardrail"]
        == "external_mutation_requires_confirmation:blocked_until_confirmation"
    )
    assert (
        result.memory_record.payload["task_connector_guardrail"]
        == "external_mutation_requires_confirmation:blocked_until_confirmation"
    )
    assert (
        result.memory_record.payload["drive_connector_guardrail"]
        == "external_mutation_requires_confirmation:blocked_until_confirmation"
    )


async def test_runtime_pipeline_emits_web_knowledge_permission_gates_under_shared_policy() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )

    event = Event(
        event_id="evt-web-knowledge-intents",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Search the web for release notes and read page https://example.com/changelog in the browser."},
        meta=EventMeta(user_id="u-1", trace_id="t-web-knowledge-intents"),
    )

    result = await runtime.run(event)

    assert len(result.plan.connector_permission_gates) == 2
    assert {gate.connector_kind for gate in result.plan.connector_permission_gates} == {
        "knowledge_search",
        "web_browser",
    }
    assert all(gate.allowed is True for gate in result.plan.connector_permission_gates)
    assert all(gate.requires_opt_in is False for gate in result.plan.connector_permission_gates)


async def test_runtime_pipeline_executes_provider_backed_clickup_task_read_path() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=memory,
            telegram_client=FakeTelegramClient(),
            clickup_task_client=FakeClickUpTaskClient(),
        ),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )
    event = Event(
        event_id="evt-clickup-read",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "List tasks in ClickUp for the current sprint."},
        meta=EventMeta(user_id="u-1", trace_id="t-clickup-read"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert "clickup_list_tasks" in result.action_result.actions
    assert "ClickUp task read returned: Release checklist, Docs sync." in result.action_result.notes


async def test_runtime_pipeline_executes_provider_backed_clickup_task_update_path() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=memory,
            telegram_client=FakeTelegramClient(),
            clickup_task_client=FakeClickUpTaskClient(),
        ),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )
    event = Event(
        event_id="evt-clickup-update",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Mark the Release checklist task as done in ClickUp."},
        meta=EventMeta(user_id="u-1", trace_id="t-clickup-update"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert "clickup_update_task" in result.action_result.actions
    assert "ClickUp task updated (clk_1)" in result.action_result.notes


async def test_runtime_pipeline_executes_provider_backed_google_calendar_read_path() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=memory,
            telegram_client=FakeTelegramClient(),
            google_calendar_client=FakeGoogleCalendarClient(),
        ),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )
    event = Event(
        event_id="evt-calendar-read",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "When can we use the calendar next week for a team sync?"},
        meta=EventMeta(user_id="u-1", trace_id="t-calendar-read"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert "google_calendar_read_availability" in result.action_result.actions
    assert "Google Calendar availability read" in result.action_result.notes


async def test_runtime_pipeline_executes_provider_backed_google_drive_metadata_read_path() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=memory,
            telegram_client=FakeTelegramClient(),
            google_drive_client=FakeGoogleDriveClient(),
        ),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )
    event = Event(
        event_id="evt-drive-read",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "List files in drive for the release notes folder."},
        meta=EventMeta(user_id="u-1", trace_id="t-drive-read"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert "google_drive_list_files" in result.action_result.actions
    assert "Google Drive metadata read returned:" in result.action_result.notes


async def test_runtime_pipeline_executes_provider_backed_web_search_path() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=memory,
            telegram_client=FakeTelegramClient(),
            knowledge_search_client=FakeDuckDuckGoSearchClient(),
        ),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )
    event = Event(
        event_id="evt-web-search",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Please search the web for the latest release notes."},
        meta=EventMeta(user_id="u-1", trace_id="t-web-search"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert "duckduckgo_search_web" in result.action_result.actions
    assert "Web search returned: Release notes (https://example.com/release-notes)." in result.action_result.notes


async def test_runtime_pipeline_executes_provider_backed_browser_page_read_path() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=memory,
            telegram_client=FakeTelegramClient(),
            web_browser_client=FakeGenericHttpPageClient(),
        ),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )
    event = Event(
        event_id="evt-browser-read",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Read page https://example.com/release-notes in the browser."},
        meta=EventMeta(user_id="u-1", trace_id="t-browser-read"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert "generic_http_read_page" in result.action_result.actions
    assert "Browser page read returned: Release notes [text/html] https://example.com/release-notes." in result.action_result.notes


async def test_runtime_pipeline_surfaces_work_partner_orchestration_baseline() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=memory,
            telegram_client=FakeTelegramClient(),
            clickup_task_client=FakeClickUpTaskClient(),
            knowledge_search_client=FakeDuckDuckGoSearchClient(),
        ),
        memory_repository=memory,
        reflection_worker=FakeReflectionWorker(),
    )
    event = Event(
        event_id="evt-work-partner",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={
            "text": "Be my work partner and search the web for release notes, then mark the Release checklist task as done in ClickUp."
        },
        meta=EventMeta(user_id="u-1", trace_id="t-work-partner"),
    )

    result = await runtime.run(event)

    selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
    intent_types = [intent.intent_type for intent in result.plan.domain_intents]
    assert result.role.selected == "work_partner"
    assert result.role.selection_reason == "work_partner_explicit_orchestration"
    assert selected_skill_ids == [
        "structured_reasoning",
        "execution_planning",
        "connector_boundary_review",
    ]
    assert "knowledge_search_intent" in intent_types
    assert "external_task_sync_intent" in intent_types
    assert "duckduckgo_search_web" in result.action_result.actions
    assert "clickup_update_task" in result.action_result.actions
    assert result.system_debug is not None
    assert result.system_debug.adaptive_state["role_skill_policy"]["current_role_name"] == "work_partner"
    assert result.system_debug.adaptive_state["role_skill_policy"]["work_partner_role_state"] == "selected"


def _build_behavior_runtime(
    memory_repository: FakeMemoryRepository,
    *,
    clickup_task_client: FakeClickUpTaskClient | None = None,
    google_calendar_client: FakeGoogleCalendarClient | None = None,
    google_drive_client: FakeGoogleDriveClient | None = None,
    knowledge_search_client: FakeDuckDuckGoSearchClient | None = None,
    web_browser_client: FakeGenericHttpPageClient | None = None,
) -> RuntimeOrchestrator:
    return RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=memory_repository,
            telegram_client=FakeTelegramClient(),
            clickup_task_client=clickup_task_client,
            google_calendar_client=google_calendar_client,
            google_drive_client=google_drive_client,
            knowledge_search_client=knowledge_search_client,
            web_browser_client=web_browser_client,
        ),
        memory_repository=memory_repository,
        reflection_worker=FakeReflectionWorker(),
    )


def _behavior_event(*, event_id: str, trace_id: str, text: str, user_id: str = "u-behavior") -> Event:
    return Event(
        event_id=event_id,
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id=user_id, trace_id=trace_id),
    )


async def test_runtime_pipeline_exposes_system_debug_surface_for_behavior_validation() -> None:
    memory = FakeHybridMemoryRepository(
        recent_memory=[
            {
                "event_id": "evt-prev-1",
                "summary": "event=review deployment risks; response_language=en; memory_topics=deployment,risks",
                "payload": {"text": "review deployment risks"},
                "importance": 0.8,
            }
        ]
    )
    memory.user_conclusions = [{"kind": "response_style", "content": "structured", "confidence": 0.82}]
    memory.relations = [{"relation_type": "collaboration_dynamic", "relation_value": "guided", "confidence": 0.79}]
    memory.embedding_source_kinds = {"episodic", "semantic", "affective"}
    runtime = _build_behavior_runtime(memory)

    result = await runtime.run(
        _behavior_event(
            event_id="evt-system-debug-1",
            trace_id="t-system-debug-1",
            text="Can you help with deployment risks?",
        )
    )

    assert result.system_debug is not None
    assert result.system_debug.mode == "system_debug"
    assert result.system_debug.event.event_id == "evt-system-debug-1"
    assert result.system_debug.event.trace_id == "t-system-debug-1"
    assert result.system_debug.memory_bundle.episodic
    assert "episodic_lexical_hits" in result.system_debug.memory_bundle.diagnostics
    assert result.system_debug.plan.domain_intents
    assert result.system_debug.action_result.status in {"success", "noop"}
    assert result.system_debug.adaptive_state["identity_policy"]["policy_owner"] == "identity_policy"
    assert result.system_debug.adaptive_state["identity_policy"]["profile_owner_fields"] == ["preferred_language"]
    assert result.system_debug.adaptive_state["retrieval_depth_policy"]["episodic_limit"] == RuntimeOrchestrator.MEMORY_LOAD_LIMIT
    assert result.system_debug.adaptive_state["relation_source_policy"] == {
        "policy_owner": "relation_source_retrieval_policy",
        "steady_state_posture": "optional_follow_on_family",
        "relation_source_enabled": False,
        "baseline_ready": True,
        "state": "optional_family_not_enabled",
        "hint": "steady_state_baseline_does_not_require_relation",
        "recommendation": "relation_can_remain_disabled_without_rollout_gap",
    }
    assert result.system_debug.adaptive_state["background_adaptive_outputs"]["theta_loaded"] is False
    assert result.system_debug.adaptive_state["role_skill_policy"]["policy_owner"] == "role_skill_boundary_policy"
    assert result.system_debug.adaptive_state["role_skill_policy"]["skill_execution_boundary"] == (
        "metadata_only_capability_hints"
    )
    assert result.system_debug.adaptive_state["role_skill_policy"]["action_skill_execution_allowed"] is False
    assert result.system_debug.adaptive_state["web_knowledge_tools"]["policy_owner"] == (
        "web_knowledge_tooling_policy"
    )
    assert result.system_debug.adaptive_state["web_knowledge_tools"]["knowledge_search"]["state"] == (
        "provider_not_ready"
    )
    website_reading = result.system_debug.adaptive_state["web_knowledge_tools"]["website_reading_workflow"]
    assert website_reading["policy_owner"] == "website_reading_workflow_policy"
    assert website_reading["workflow_state"] == "website_reading_blocked"
    assert website_reading["direct_url_review_available"] is False
    assert website_reading["search_then_page_review_available"] is False
    assert website_reading["allowed_entry_modes"] == []
    assert website_reading["blockers"] == [
        "page_read_provider_not_ready",
        "search_provider_not_ready",
    ]
    assert result.system_debug.adaptive_state["affective_input_policy"] == {
        "policy_owner": "perception_affective_input",
        "input_kind": "heuristic_turn_signal",
        "input_source_baseline": "deterministic_placeholder",
        "final_assessment_owner": "affective_assessment_rollout_policy",
        "fallback_resolution_posture": "reuse_input_when_assessment_unavailable",
    }
    assert result.system_debug.adaptive_state["affective_assessment_policy"]["affective_assessment_owner"] == (
        "affective_assessment_rollout_policy"
    )
    assert result.system_debug.adaptive_state["affective_resolution"]["input_source"] == (
        "deterministic_placeholder"
    )
    assert result.system_debug.adaptive_state["affective_resolution"]["final_source"] in {
        "fallback",
        "ai_classifier",
    }
    assert (
        result.system_debug.adaptive_state["affective_resolution"]["resolution_owner_chain"]
        == "perception_affective_input_to_affective_assessment"
    )


async def test_runtime_pipeline_exposes_relation_source_policy_when_optional_family_is_enabled() -> None:
    memory = FakeHybridMemoryRepository(recent_memory=[])
    memory.embedding_source_kinds = {"episodic", "semantic", "affective", "relation"}
    runtime = _build_behavior_runtime(memory)

    result = await runtime.run(
        _behavior_event(
            event_id="evt-relation-policy-1",
            trace_id="t-relation-policy-1",
            text="Can you keep the answer structured?",
        )
    )

    assert result.system_debug is not None
    assert result.system_debug.adaptive_state["relation_source_policy"] == {
        "policy_owner": "relation_source_retrieval_policy",
        "steady_state_posture": "optional_follow_on_family",
        "relation_source_enabled": True,
        "baseline_ready": True,
        "state": "optional_family_enabled",
        "hint": "relation_enabled_without_redefining_steady_state_baseline",
        "recommendation": "keep_relation_as_optional_follow_on_family",
    }


async def test_runtime_pipeline_exposes_disabled_affective_policy_in_system_debug() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
        affective_assessor=AffectiveAssessor(
            classifier_client=FakeAffectiveClassifierClient(
                {
                    "affect_label": "support_distress",
                    "intensity": 0.92,
                    "needs_support": True,
                    "confidence": 0.88,
                    "evidence": ["overwhelmed"],
                }
            ),
            enabled=False,
            policy_source="explicit",
        ),
    )

    event = Event(
        event_id="evt-affective-policy-off",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "I feel overwhelmed"},
        meta=EventMeta(user_id="u-1", trace_id="t-affective-policy-off"),
    )

    result = await runtime.run(event)

    assert result.system_debug is not None
    assert result.affective.source == "fallback"
    assert result.affective.evidence[0] == "fallback_reason:policy_disabled"
    assert result.system_debug.adaptive_state["affective_assessment_policy"] == {
        "affective_assessment_enabled": False,
        "affective_assessment_source": "explicit",
        "affective_classifier_available": True,
        "affective_assessment_posture": "fallback_only_policy_disabled",
        "affective_assessment_hint": "policy_disabled_use_deterministic_affective_baseline",
        "affective_assessment_owner": "affective_assessment_rollout_policy",
    }
    assert result.system_debug.adaptive_state["affective_resolution"] == {
        "input_source": "deterministic_placeholder",
        "input_label": "support_distress",
        "input_needs_support": True,
        "final_source": "fallback",
        "final_label": "support_distress",
        "final_needs_support": True,
        "input_reused_as_final": True,
        "fallback_reason": "policy_disabled",
        "resolution_owner_chain": "perception_affective_input_to_affective_assessment",
    }


async def test_behavior_harness_outputs_structured_contract_results() -> None:
    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(
                test_id="T0.1",
                run=lambda: BehaviorScenarioCheck(
                    passed=True,
                    reason="baseline_pass",
                    trace_id="trace-baseline-pass",
                    notes="structured output smoke",
                ),
            ),
            BehaviorScenarioDefinition(
                test_id="T0.2",
                run=lambda: BehaviorScenarioCheck(
                    passed=False,
                    skip=True,
                    reason="feature_not_implemented",
                    trace_id="trace-baseline-skip",
                    notes="intentional skip contract",
                ),
            ),
        ]
    )

    jsonable = behavior_results_as_jsonable(results)
    assert len(jsonable) == 2
    assert set(jsonable[0].keys()) == {"test_id", "status", "reason", "trace_id", "notes"}
    assert jsonable[0]["status"] == "pass"
    assert jsonable[1]["status"] == "skip"
    assert jsonable[1]["reason"] == "feature_not_implemented"


async def test_runtime_pipeline_captures_reminder_preference_and_daily_planning_tasks() -> None:
    memory = PersistingFakeMemoryRepository(recent_memory=[])
    runtime = _build_behavior_runtime(memory)

    reminder_result = await runtime.run(
        _behavior_event(
            event_id="evt-v1-reminder-1",
            trace_id="t-v1-reminder-1",
            text="Remind me to send the release summary tomorrow.",
        )
    )
    planning_result = await runtime.run(
        _behavior_event(
            event_id="evt-v1-plan-1",
            trace_id="t-v1-plan-1",
            text="Help me plan tomorrow.",
        )
    )

    active_task_names = {str(task.get("name", "")) for task in memory.active_tasks}
    active_planned_work_summaries = {str(item.get("summary", "")) for item in memory.active_planned_work}

    assert reminder_result.memory_record is not None
    assert planning_result.memory_record is not None
    assert reminder_result.memory_record.payload["proactive_preference_update"] == "proactive_opt_in:true"
    assert reminder_result.memory_record.payload["planned_work_update"] == "reminder:send the release summary tomorrow:pending"
    assert memory.user_preferences["proactive_opt_in"] is True
    assert "send the release summary tomorrow" in active_task_names
    assert "send the release summary tomorrow" in active_planned_work_summaries
    assert "plan tomorrow" in active_task_names


async def test_runtime_behavior_memory_scenarios_cover_write_retrieve_influence_and_delayed_recall() -> None:
    async def memory_behavior_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(memory)

        first = await runtime.run(
            _behavior_event(
                event_id="evt-memory-write-1",
                trace_id="t-memory-write-1",
                text="Remember that deployment blocker is caused by migration mismatch.",
            )
        )
        second = await runtime.run(
            _behavior_event(
                event_id="evt-memory-retrieve-1",
                trace_id="t-memory-retrieve-1",
                text="What is the blocker we already identified?",
            )
        )
        if memory.recent_memory:
            memory.recent_memory[0]["timestamp"] = datetime(2024, 1, 15, tzinfo=timezone.utc)
        delayed = await runtime.run(
            _behavior_event(
                event_id="evt-memory-delayed-1",
                trace_id="t-memory-delayed-1",
                text="After a break, remind me what was blocking deploy.",
            )
        )
        control_runtime = _build_behavior_runtime(FakeMemoryRepository(recent_memory=[]))
        control = await control_runtime.run(
            _behavior_event(
                event_id="evt-memory-control-1",
                trace_id="t-memory-control-1",
                text="What is the blocker we already identified?",
            )
        )

        checks = {
            "write": first.memory_record is not None and len(memory.recent_memory) >= 1,
            "retrieve": "Relevant recent memory:" in second.context.summary,
            "influence": "Relevant recent memory:" in second.system_debug.context.summary
            and "Relevant recent memory:" not in control.context.summary,
            "delayed_recall": "Relevant recent memory:" in delayed.context.summary,
        }
        missing = [name for name, passed in checks.items() if not passed]
        return BehaviorScenarioCheck(
            passed=not missing,
            reason="memory_write_retrieve_influence_delayed_recall"
            if not missing
            else "memory_behavior_missing:" + ",".join(missing),
            trace_id=delayed.event.meta.trace_id,
            notes=(
                f"write={checks['write']};"
                f"retrieve={checks['retrieve']};"
                f"influence={checks['influence']};"
                f"delayed_recall={checks['delayed_recall']}"
            ),
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(
                test_id="T2.1",
                run=memory_behavior_scenario,
            )
        ]
    )
    assert len(results) == 1
    assert results[0].status == "pass"


async def test_runtime_behavior_continuity_scenario_covers_multi_session_personality_stability() -> None:
    async def continuity_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime_session_one = _build_behavior_runtime(memory)

        first = await runtime_session_one.run(
            _behavior_event(
                event_id="evt-continuity-1",
                trace_id="t-continuity-1",
                text="Status update for today.",
            )
        )
        runtime_session_two = _build_behavior_runtime(memory)
        second = await runtime_session_two.run(
            _behavior_event(
                event_id="evt-continuity-2",
                trace_id="t-continuity-2",
                text="Status update for today.",
            )
        )

        checks = {
            "identity_continuity": first.identity.mission == second.identity.mission
            and first.identity.behavioral_style == second.identity.behavioral_style,
            "tone_stability": first.expression.tone == second.expression.tone,
            "language_stability": first.expression.language == second.expression.language,
            "context_reuse": "Relevant recent memory:" in second.context.summary,
        }
        missing = [name for name, passed in checks.items() if not passed]
        return BehaviorScenarioCheck(
            passed=not missing,
            reason="multi_session_continuity_and_personality_stability"
            if not missing
            else "continuity_behavior_missing:" + ",".join(missing),
            trace_id=second.event.meta.trace_id,
            notes=(
                f"identity_continuity={checks['identity_continuity']};"
                f"tone_stability={checks['tone_stability']};"
                f"language_stability={checks['language_stability']};"
                f"context_reuse={checks['context_reuse']}"
            ),
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(
                test_id="T10.1",
                run=continuity_scenario,
            )
        ]
    )
    assert len(results) == 1
    assert results[0].status == "pass"


async def test_runtime_pipeline_projects_shared_transcript_for_api_and_telegram_turns_under_same_user() -> None:
    memory = PersistingFakeMemoryRepository(recent_memory=[])
    runtime = _build_behavior_runtime(memory)

    api_result = await runtime.run(
        _behavior_event(
            event_id="evt-shared-api-1",
            trace_id="t-shared-api-1",
            user_id="linked-user-1",
            text="hello from the app",
        )
    )
    telegram_result = await runtime.run(
        Event(
            event_id="evt-shared-telegram-1",
            source="telegram",
            subsource="user_message",
            timestamp=datetime.now(timezone.utc),
            payload={"text": "hello from telegram", "chat_id": 123456},
            meta=EventMeta(user_id="linked-user-1", trace_id="t-shared-telegram-1"),
        )
    )

    transcript = await memory.get_recent_chat_transcript_for_user("linked-user-1", limit=10)

    assert api_result.memory_record is not None
    assert telegram_result.memory_record is not None
    assert [item["message_id"] for item in transcript] == [
        "evt-shared-api-1:user",
        "evt-shared-api-1:assistant",
        "evt-shared-telegram-1:user",
        "evt-shared-telegram-1:assistant",
    ]
    assert [item["channel"] for item in transcript] == ["api", "api", "telegram", "telegram"]
    assert transcript[0]["text"] == "hello from the app"
    assert transcript[2]["text"] == "hello from telegram"
    assert transcript[1]["metadata"] == {"language": "en"}
    assert transcript[3]["metadata"] == {"language": "en"}


async def test_runtime_behavior_failure_scenarios_cover_contradiction_missing_data_and_noise() -> None:
    async def contradiction_scenario() -> BehaviorScenarioCheck:
        runtime = _build_behavior_runtime(FakeMemoryRepository(recent_memory=[]))
        result = await runtime.run(
            _behavior_event(
                event_id="evt-failure-contradiction",
                trace_id="t-failure-contradiction",
                text="Do not answer me, but answer now with one action plan.",
            )
        )
        passed = (
            result.action_result.status in {"success", "noop"}
            and result.system_debug is not None
            and "User said:" in result.context.summary
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="contradiction_input_stays_explainable" if passed else "contradiction_handling_regression",
            trace_id=result.event.meta.trace_id,
            notes=f"action_status={result.action_result.status};context_has_user_said={'User said:' in result.context.summary}",
        )

    async def missing_data_scenario() -> BehaviorScenarioCheck:
        runtime = _build_behavior_runtime(FakeMemoryRepository(recent_memory=[]))
        result = await runtime.run(
            _behavior_event(
                event_id="evt-failure-missing-data",
                trace_id="t-failure-missing-data",
                text="   ",
            )
        )
        passed = bool(result.expression.message.strip()) and result.system_debug is not None
        return BehaviorScenarioCheck(
            passed=passed,
            reason="missing_data_fallback_response" if passed else "missing_data_response_regression",
            trace_id=result.event.meta.trace_id,
            notes=f"message_present={bool(result.expression.message.strip())};motivation_mode={result.motivation.mode}",
        )

    async def noisy_input_scenario() -> BehaviorScenarioCheck:
        runtime = _build_behavior_runtime(FakeMemoryRepository(recent_memory=[]))
        result = await runtime.run(
            _behavior_event(
                event_id="evt-failure-noisy-input",
                trace_id="t-failure-noisy-input",
                text="!!! ??? ### random<>text<>12345 // ???",
            )
        )
        passed = (
            result.action_result.status in {"success", "noop"}
            and len(result.stage_timings_ms) > 0
            and result.system_debug is not None
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="noisy_input_stays_controlled" if passed else "noisy_input_stability_regression",
            trace_id=result.event.meta.trace_id,
            notes=f"action_status={result.action_result.status};stage_count={len(result.stage_timings_ms)}",
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(test_id="T11.1", run=contradiction_scenario),
            BehaviorScenarioDefinition(test_id="T11.2", run=missing_data_scenario),
            BehaviorScenarioDefinition(test_id="T11.3", run=noisy_input_scenario),
        ]
    )
    assert len(results) == 3
    assert {result.status for result in results} == {"pass"}


@pytest.mark.asyncio()
async def test_runtime_persists_tool_grounded_learning_from_bounded_external_reads() -> None:
    memory = PersistingFakeMemoryRepository(recent_memory=[])
    runtime = _build_behavior_runtime(
        memory_repository=memory,
        clickup_task_client=FakeClickUpTaskClient(),
        google_calendar_client=FakeGoogleCalendarClient(),
        google_drive_client=FakeGoogleDriveClient(),
        knowledge_search_client=FakeDuckDuckGoSearchClient(),
        web_browser_client=FakeGenericHttpPageClient(),
    )

    await runtime.run(
        _behavior_event(
            event_id="evt-tool-learning-1",
            trace_id="t-tool-learning-1",
            text="Search the web for deployment risks and read page https://example.com/release-notes.",
        )
    )
    await runtime.run(
        _behavior_event(
            event_id="evt-tool-learning-2",
            trace_id="t-tool-learning-2",
            text="Be my work partner and list tasks in ClickUp.",
        )
    )
    await runtime.run(
        _behavior_event(
            event_id="evt-tool-learning-3",
            trace_id="t-tool-learning-3",
            text="Be my work partner and check my calendar availability tomorrow.",
        )
    )
    await runtime.run(
        _behavior_event(
            event_id="evt-tool-learning-4",
            trace_id="t-tool-learning-4",
            text="Be my work partner and list files in Google Drive.",
        )
    )

    conclusion_kinds = {str(row.get("kind", "")) for row in memory.user_conclusions}
    assert {
        "tool_grounded_search_knowledge",
        "tool_grounded_page_knowledge",
        "tool_grounded_task_snapshot",
        "tool_grounded_calendar_snapshot",
        "tool_grounded_drive_snapshot",
    }.issubset(conclusion_kinds)


async def test_runtime_behavior_proactive_scenarios_cover_delivery_and_anti_spam_posture() -> None:
    async def proactive_delivery_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        memory.user_preferences = {
            "proactive_opt_in": True,
            "proactive_recent_outbound_limit": 2,
            "proactive_unanswered_limit": 1,
        }
        runtime = _build_behavior_runtime(memory)
        event = build_scheduler_event(
            subsource="proactive_tick",
            user_id="123456",
            payload={
                "text": "follow up on blocked task deploy",
                "chat_id": 123456,
                "proactive_trigger": "task_blocked",
                "user_context": {
                    "quiet_hours": False,
                    "focus_mode": False,
                    "recent_user_activity": "active",
                    "recent_outbound_count": 0,
                    "unanswered_proactive_count": 0,
                },
            },
        )

        result = await runtime.run(event)
        passed = (
            result.action_result.status == "success"
            and "send_telegram_message" in result.action_result.actions
            and result.memory_record is not None
            and result.memory_record.payload["proactive_state_update"].startswith("delivery_ready:")
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="proactive_delivery_ready_path" if passed else "proactive_delivery_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"action_status={result.action_result.status};"
                f"actions={','.join(result.action_result.actions)};"
                f"state={result.memory_record.payload.get('proactive_state_update', '') if result.memory_record else ''}"
            ),
        )

    async def proactive_anti_spam_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        memory.user_preferences = {"proactive_opt_in": True}
        runtime = _build_behavior_runtime(memory)
        first = await runtime.run(
            build_scheduler_event(
                subsource="proactive_tick",
                user_id="123456",
                payload={
                    "text": "follow up on blocked task deploy",
                    "chat_id": 123456,
                    "proactive_trigger": "task_blocked",
                    "user_context": {
                        "quiet_hours": False,
                        "focus_mode": False,
                        "recent_user_activity": "active",
                        "recent_outbound_count": 0,
                        "unanswered_proactive_count": 0,
                    },
                },
            )
        )
        second = await runtime.run(
            build_scheduler_event(
                subsource="proactive_tick",
                user_id="123456",
                payload={
                    "text": "follow up on blocked task deploy again",
                    "chat_id": 123456,
                    "proactive_trigger": "task_blocked",
                    "user_context": {
                        "quiet_hours": False,
                        "focus_mode": False,
                        "recent_user_activity": "active",
                        "recent_outbound_count": 4,
                        "unanswered_proactive_count": 1,
                    },
                },
            )
        )
        passed = (
            first.action_result.status == "success"
            and second.action_result.status == "noop"
            and second.memory_record is not None
            and second.memory_record.payload["proactive_state_update"].startswith("attention_gate_blocked:")
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="proactive_anti_spam_guardrails" if passed else "proactive_anti_spam_regression",
            trace_id=second.event.meta.trace_id,
            notes=(
                f"first={first.action_result.status};"
                f"second={second.action_result.status};"
                f"second_state={second.memory_record.payload.get('proactive_state_update', '') if second.memory_record else ''}"
            ),
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(test_id="T12.1", run=proactive_delivery_scenario),
            BehaviorScenarioDefinition(test_id="T12.2", run=proactive_anti_spam_scenario),
        ]
    )
    assert len(results) == 2
    assert {result.status for result in results} == {"pass"}


async def test_runtime_behavior_life_assistant_workflow_scenario_covers_capture_planning_and_follow_up() -> None:
    async def life_assistant_workflow_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(memory)

        reminder_result = await runtime.run(
            _behavior_event(
                event_id="evt-life-assistant-reminder-1",
                trace_id="t-life-assistant-reminder-1",
                user_id="123456",
                text="Remind me to send the release summary tomorrow.",
            )
        )
        planning_result = await runtime.run(
            _behavior_event(
                event_id="evt-life-assistant-plan-1",
                trace_id="t-life-assistant-plan-1",
                user_id="123456",
                text="Help me plan tomorrow.",
            )
        )
        proactive_result = await runtime.run(
            build_scheduler_event(
                subsource="proactive_tick",
                user_id="123456",
                payload={
                    "text": "time check-in for tomorrow plan",
                    "chat_id": 123456,
                    "proactive_trigger": "time_checkin",
                    "user_context": {
                        "quiet_hours": False,
                        "focus_mode": False,
                        "recent_user_activity": "active",
                        "recent_outbound_count": 0,
                        "unanswered_proactive_count": 0,
                    },
                },
            )
        )

        active_task_names = {str(task.get("name", "")) for task in memory.active_tasks}
        checks = {
            "preference_persisted": memory.user_preferences.get("proactive_opt_in") is True,
            "reminder_task_captured": "send the release summary tomorrow" in active_task_names,
            "daily_planning_task_captured": "plan tomorrow" in active_task_names,
            "reminder_payload_visible": (
                reminder_result.memory_record is not None
                and reminder_result.memory_record.payload.get("proactive_preference_update") == "proactive_opt_in:true"
            ),
            "proactive_follow_up_ready": (
                proactive_result.action_result.status == "success"
                and "send_telegram_message" in proactive_result.action_result.actions
                and proactive_result.memory_record is not None
                and proactive_result.memory_record.payload["proactive_state_update"].startswith("delivery_ready:")
            ),
        }
        missing = [name for name, passed in checks.items() if not passed]
        return BehaviorScenarioCheck(
            passed=not missing,
            reason="life_assistant_capture_plan_follow_up"
            if not missing
            else "life_assistant_workflow_missing:" + ",".join(missing),
            trace_id=proactive_result.event.meta.trace_id,
            notes=(
                f"preference={checks['preference_persisted']};"
                f"reminder_task={checks['reminder_task_captured']};"
                f"planning_task={checks['daily_planning_task_captured']};"
                f"payload={checks['reminder_payload_visible']};"
                f"follow_up={checks['proactive_follow_up_ready']};"
                f"plan_status={planning_result.action_result.status}"
            ),
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(
                test_id="T13.1",
                run=life_assistant_workflow_scenario,
            )
        ]
    )
    assert len(results) == 1
    assert results[0].status == "pass"


async def test_runtime_behavior_role_skill_connector_and_deferred_reflection_scenarios() -> None:
    async def role_skill_boundary_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(memory)
        result = await runtime.run(
            _behavior_event(
                event_id="evt-role-skill-1",
                trace_id="t-role-skill-1",
                text="Can you help me plan the rollout and remember the key risks?",
            )
        )
        selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
        policy = result.system_debug.adaptive_state["role_skill_policy"] if result.system_debug else {}
        passed = (
            result.role.skill_policy_owner == "role_skill_boundary_policy"
            and "structured_reasoning" in selected_skill_ids
            and "memory_recall" in selected_skill_ids
            and result.action_result.status in {"success", "noop"}
            and policy.get("action_skill_execution_allowed") is False
            and policy.get("skill_execution_boundary") == "metadata_only_capability_hints"
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="role_skill_metadata_only_boundary" if passed else "role_skill_boundary_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"skills={','.join(selected_skill_ids)};"
                f"action_status={result.action_result.status};"
                f"policy={policy.get('skill_execution_boundary', '')}"
            ),
        )

    async def connector_posture_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(memory)
        result = await runtime.run(
            _behavior_event(
                event_id="evt-connector-behavior-1",
                trace_id="t-connector-behavior-1",
                text="Create calendar meeting tomorrow, create task in ClickUp, and upload notes to Google Drive.",
            )
        )
        payload = result.memory_record.payload if result.memory_record else {}
        passed = (
            result.memory_record is not None
            and payload.get("task_connector_update") == "create_task:mutate_with_confirmation:clickup"
            and payload.get("calendar_connector_guardrail") == "external_mutation_requires_confirmation:blocked_until_confirmation"
            and payload.get("drive_connector_guardrail") == "external_mutation_requires_confirmation:blocked_until_confirmation"
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="connector_boundary_posture_visible" if passed else "connector_boundary_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"task={payload.get('task_connector_update', '')};"
                f"calendar={payload.get('calendar_connector_guardrail', '')};"
                f"drive={payload.get('drive_connector_guardrail', '')}"
            ),
        )

    async def deferred_reflection_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        reflection = FakeReflectionWorker(running=False)
        runtime = RuntimeOrchestrator(
            perception_agent=PerceptionAgent(),
            context_agent=ContextAgent(),
            motivation_engine=MotivationEngine(),
            role_agent=RoleAgent(),
            planning_agent=PlanningAgent(),
            expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
            action_executor=ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient()),
            memory_repository=memory,
            reflection_worker=reflection,
            reflection_runtime_mode="deferred",
        )
        result = await runtime.run(
            _behavior_event(
                event_id="evt-deferred-reflection-1",
                trace_id="t-deferred-reflection-1",
                text="Remember that the blocker is still migration drift.",
            )
        )
        dispatch_posture = reflection.calls[0]["dispatch"] if reflection.calls else "missing"
        passed = (
            result.reflection_triggered is True
            and len(reflection.calls) == 1
            and dispatch_posture == "no"
            and result.memory_record is not None
        )
        return BehaviorScenarioCheck(
            passed=passed,
                reason="deferred_reflection_enqueue_boundary" if passed else "deferred_reflection_boundary_regression",
                trace_id=result.event.meta.trace_id,
                notes=(
                    f"triggered={result.reflection_triggered};"
                    f"enqueue_calls={len(reflection.calls)};"
                    f"dispatch={dispatch_posture}"
                ),
            )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(test_id="T6.1", run=role_skill_boundary_scenario),
            BehaviorScenarioDefinition(test_id="T7.1", run=connector_posture_scenario),
            BehaviorScenarioDefinition(test_id="T9.1", run=deferred_reflection_scenario),
        ]
    )
    assert len(results) == 3
    assert {result.status for result in results} == {"pass"}


async def test_runtime_behavior_role_governed_tool_usage_scenarios() -> None:
    async def analyst_web_search_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            knowledge_search_client=FakeDuckDuckGoSearchClient(),
        )
        result = await runtime.run(
            _behavior_event(
                event_id="evt-tool-search-1",
                trace_id="t-tool-search-1",
                text="Analyze the latest release notes and search the web for deployment risks.",
            )
        )
        intent_types = [intent.intent_type for intent in result.plan.domain_intents]
        selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
        policy = result.system_debug.adaptive_state["role_skill_policy"] if result.system_debug else {}
        passed = (
            result.role.selected == "analyst"
            and "knowledge_search_intent" in intent_types
            and "duckduckgo_search_web" in result.action_result.actions
            and "structured_reasoning" in selected_skill_ids
            and policy.get("action_skill_execution_allowed") is False
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="analyst_web_search_via_action_boundary" if passed else "analyst_web_search_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"role={result.role.selected};"
                f"intents={','.join(intent_types)};"
                f"actions={','.join(result.action_result.actions)};"
                f"skills={','.join(selected_skill_ids)}"
            ),
        )

    async def analyst_browser_review_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            web_browser_client=FakeGenericHttpPageClient(),
        )
        result = await runtime.run(
            _behavior_event(
                event_id="evt-tool-browser-1",
                trace_id="t-tool-browser-1",
                text="Read page https://example.com/release-notes and explain the important changes.",
            )
        )
        intent_types = [intent.intent_type for intent in result.plan.domain_intents]
        selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
        policy = result.system_debug.adaptive_state["role_skill_policy"] if result.system_debug else {}
        passed = (
            result.role.selected == "analyst"
            and "web_browser_access_intent" in intent_types
            and "generic_http_read_page" in result.action_result.actions
            and "structured_reasoning" in selected_skill_ids
            and policy.get("action_skill_execution_allowed") is False
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="analyst_browser_review_via_action_boundary" if passed else "analyst_browser_review_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"role={result.role.selected};"
                f"intents={','.join(intent_types)};"
                f"actions={','.join(result.action_result.actions)};"
                f"skills={','.join(selected_skill_ids)}"
            ),
        )

    async def executor_clickup_update_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        memory.user_preferences["preferred_role"] = "executor"
        memory.user_preferences["preferred_role_confidence"] = 0.94
        runtime = _build_behavior_runtime(
            memory,
            clickup_task_client=FakeClickUpTaskClient(),
        )
        result = await runtime.run(
            _behavior_event(
                event_id="evt-tool-clickup-1",
                trace_id="t-tool-clickup-1",
                text="Can you mark the Release checklist task as done in ClickUp?",
            )
        )
        intent_types = [intent.intent_type for intent in result.plan.domain_intents]
        selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
        payload = result.memory_record.payload if result.memory_record else {}
        passed = (
            result.role.selected == "executor"
            and "external_task_sync_intent" in intent_types
            and "clickup_update_task" in result.action_result.actions
            and "execution_planning" in selected_skill_ids
            and "connector_boundary_review" in selected_skill_ids
            and payload.get("task_connector_update") == "update_task:mutate_with_confirmation:clickup"
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="executor_clickup_update_via_action_boundary" if passed else "executor_clickup_update_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"role={result.role.selected};"
                f"intents={','.join(intent_types)};"
                f"actions={','.join(result.action_result.actions)};"
                f"skills={','.join(selected_skill_ids)};"
                f"task_connector={payload.get('task_connector_update', '')}"
            ),
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(test_id="T14.1", run=analyst_web_search_scenario),
            BehaviorScenarioDefinition(test_id="T14.2", run=analyst_browser_review_scenario),
            BehaviorScenarioDefinition(test_id="T14.3", run=executor_clickup_update_scenario),
        ]
    )
    assert len(results) == 3
    assert {result.status for result in results} == {"pass"}


async def test_runtime_behavior_work_partner_scenarios() -> None:
    async def work_partner_organization_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            clickup_task_client=FakeClickUpTaskClient(),
            knowledge_search_client=FakeDuckDuckGoSearchClient(),
        )
        result = await runtime.run(
            _behavior_event(
                event_id="evt-work-partner-behavior-1",
                trace_id="t-work-partner-behavior-1",
                text="Be my work partner and search the web for release notes, then mark the Release checklist task as done in ClickUp.",
            )
        )
        selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
        policy = result.system_debug.adaptive_state["role_skill_policy"] if result.system_debug else {}
        passed = (
            result.role.selected == "work_partner"
            and "duckduckgo_search_web" in result.action_result.actions
            and "clickup_update_task" in result.action_result.actions
            and selected_skill_ids == [
                "structured_reasoning",
                "execution_planning",
                "connector_boundary_review",
            ]
            and policy.get("current_role_name") == "work_partner"
            and policy.get("work_partner_role_state") == "selected"
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="work_partner_organization_boundary" if passed else "work_partner_organization_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"role={result.role.selected};"
                f"actions={','.join(result.action_result.actions)};"
                f"skills={','.join(selected_skill_ids)};"
                f"policy_state={policy.get('work_partner_role_state', '')}"
            ),
        )

    async def work_partner_decision_support_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            web_browser_client=FakeGenericHttpPageClient(),
        )
        result = await runtime.run(
            _behavior_event(
                event_id="evt-work-partner-behavior-2",
                trace_id="t-work-partner-behavior-2",
                text="Be my work partner and read page https://example.com/release-notes so we can decide whether today's release is safe.",
            )
        )
        selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
        intent_types = [intent.intent_type for intent in result.plan.domain_intents]
        passed = (
            result.role.selected == "work_partner"
            and "web_browser_access_intent" in intent_types
            and "generic_http_read_page" in result.action_result.actions
            and "structured_reasoning" in selected_skill_ids
            and "connector_boundary_review" in selected_skill_ids
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="work_partner_decision_support_boundary" if passed else "work_partner_decision_support_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"role={result.role.selected};"
                f"intents={','.join(intent_types)};"
                f"actions={','.join(result.action_result.actions)};"
                f"skills={','.join(selected_skill_ids)}"
            ),
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(test_id="T15.1", run=work_partner_organization_scenario),
            BehaviorScenarioDefinition(test_id="T15.2", run=work_partner_decision_support_scenario),
        ]
    )
    assert len(results) == 2
    assert {result.status for result in results} == {"pass"}


async def test_runtime_behavior_work_partner_organizer_tool_stack_scenarios() -> None:
    async def work_partner_clickup_list_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            clickup_task_client=FakeClickUpTaskClient(),
        )
        result = await runtime.run(
            _behavior_event(
                event_id="evt-work-partner-organizer-1",
                trace_id="t-work-partner-organizer-1",
                text="Be my work partner and list tasks in ClickUp for today's release work.",
            )
        )
        selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
        passed = (
            result.role.selected == "work_partner"
            and "clickup_list_tasks" in result.action_result.actions
            and "structured_reasoning" in selected_skill_ids
            and "connector_boundary_review" in selected_skill_ids
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="work_partner_clickup_list_boundary" if passed else "work_partner_clickup_list_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"role={result.role.selected};"
                f"actions={','.join(result.action_result.actions)};"
                f"skills={','.join(selected_skill_ids)}"
            ),
        )

    async def work_partner_calendar_availability_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            google_calendar_client=FakeGoogleCalendarClient(),
        )
        result = await runtime.run(
            _behavior_event(
                event_id="evt-work-partner-organizer-2",
                trace_id="t-work-partner-organizer-2",
                text="Be my work partner and check calendar availability next week for a release sync.",
            )
        )
        selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
        passed = (
            result.role.selected == "work_partner"
            and "google_calendar_read_availability" in result.action_result.actions
            and "structured_reasoning" in selected_skill_ids
            and "connector_boundary_review" in selected_skill_ids
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="work_partner_calendar_availability_boundary"
            if passed
            else "work_partner_calendar_availability_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"role={result.role.selected};"
                f"actions={','.join(result.action_result.actions)};"
                f"skills={','.join(selected_skill_ids)}"
            ),
        )

    async def work_partner_drive_metadata_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            google_drive_client=FakeGoogleDriveClient(),
        )
        result = await runtime.run(
            _behavior_event(
                event_id="evt-work-partner-organizer-3",
                trace_id="t-work-partner-organizer-3",
                text="Be my work partner and list files in Google Drive for release notes.",
            )
        )
        selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
        passed = (
            result.role.selected == "work_partner"
            and "google_drive_list_files" in result.action_result.actions
            and "structured_reasoning" in selected_skill_ids
            and "connector_boundary_review" in selected_skill_ids
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="work_partner_drive_metadata_boundary" if passed else "work_partner_drive_metadata_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"role={result.role.selected};"
                f"actions={','.join(result.action_result.actions)};"
                f"skills={','.join(selected_skill_ids)}"
            ),
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(test_id="T16.1", run=work_partner_clickup_list_scenario),
            BehaviorScenarioDefinition(test_id="T16.2", run=work_partner_calendar_availability_scenario),
            BehaviorScenarioDefinition(test_id="T16.3", run=work_partner_drive_metadata_scenario),
        ]
    )
    assert len(results) == 3
    assert {result.status for result in results} == {"pass"}


async def test_runtime_behavior_tool_grounded_learning_scenarios() -> None:
    async def search_learning_recall_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            knowledge_search_client=FakeDuckDuckGoSearchClient(),
        )

        research_result = await runtime.run(
            _behavior_event(
                event_id="evt-tool-grounded-1",
                trace_id="t-tool-grounded-1",
                user_id="tool-user",
                text="Search the web for release notes.",
            )
        )
        recall_result = await runtime.run(
            _behavior_event(
                event_id="evt-tool-grounded-2",
                trace_id="t-tool-grounded-2",
                user_id="tool-user",
                text="What did you learn from the release notes you checked earlier?",
            )
        )

        persisted_update = (
            dict(research_result.memory_record.payload).get("tool_grounded_learning_update", {})
            if research_result.memory_record is not None
            else {}
        )
        recalled_kinds = {
            str(item.get("kind", ""))
            for item in (recall_result.system_debug.memory_bundle.semantic if recall_result.system_debug else [])
        }
        passed = (
            "duckduckgo_search_web" in research_result.action_result.actions
            and "generic_http_read_page" not in research_result.action_result.actions
            and persisted_update == "tool_grounded_search_knowledge"
            and "tool_grounded_search_knowledge" in recalled_kinds
            and "duckduckgo_search_web" not in recall_result.action_result.actions
            and "generic_http_read_page" not in recall_result.action_result.actions
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="tool_grounded_search_recall"
            if passed
            else "tool_grounded_search_recall_regression",
            trace_id=recall_result.event.meta.trace_id,
            notes=(
                f"persisted={persisted_update};"
                f"research_actions={','.join(research_result.action_result.actions)};"
                f"recall_actions={','.join(recall_result.action_result.actions)};"
                f"recalled={','.join(sorted(recalled_kinds))}"
            ),
        )

    async def organizer_snapshot_learning_recall_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            clickup_task_client=FakeClickUpTaskClient(),
        )

        list_result = await runtime.run(
            _behavior_event(
                event_id="evt-tool-grounded-3",
                trace_id="t-tool-grounded-3",
                user_id="tool-user",
                text="List my ClickUp tasks for the release work.",
            )
        )
        recall_result = await runtime.run(
            _behavior_event(
                event_id="evt-tool-grounded-4",
                trace_id="t-tool-grounded-4",
                user_id="tool-user",
                text="Based on that task list, what should I focus on first?",
            )
        )

        persisted_update = (
            dict(list_result.memory_record.payload).get("tool_grounded_learning_update", {})
            if list_result.memory_record is not None
            else {}
        )
        recalled_kinds = {
            str(item.get("kind", ""))
            for item in (recall_result.system_debug.memory_bundle.semantic if recall_result.system_debug else [])
        }
        passed = (
            "clickup_list_tasks" in list_result.action_result.actions
            and persisted_update == "tool_grounded_task_snapshot"
            and "tool_grounded_task_snapshot" in recalled_kinds
            and "clickup_list_tasks" not in recall_result.action_result.actions
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="tool_grounded_task_snapshot_recall"
            if passed
            else "tool_grounded_task_snapshot_recall_regression",
            trace_id=recall_result.event.meta.trace_id,
            notes=(
                f"persisted={persisted_update};"
                f"list_actions={','.join(list_result.action_result.actions)};"
                f"recall_actions={','.join(recall_result.action_result.actions)};"
                f"recalled={','.join(sorted(recalled_kinds))}"
            ),
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(test_id="T17.1", run=search_learning_recall_scenario),
            BehaviorScenarioDefinition(test_id="T17.2", run=organizer_snapshot_learning_recall_scenario),
        ]
    )
    assert len(results) == 2
    assert {result.status for result in results} == {"pass"}


async def test_runtime_behavior_final_v1_daily_use_scenarios() -> None:
    async def website_read_then_recall_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            web_browser_client=FakeGenericHttpPageClient(),
        )

        read_result = await runtime.run(
            _behavior_event(
                event_id="evt-final-v1-daily-use-1",
                trace_id="t-final-v1-daily-use-1",
                user_id="daily-user",
                text="Read page https://example.com/release-notes and explain the important changes.",
            )
        )
        recall_result = await runtime.run(
            _behavior_event(
                event_id="evt-final-v1-daily-use-2",
                trace_id="t-final-v1-daily-use-2",
                user_id="daily-user",
                text="What did you learn from that page earlier and what should I remember?",
            )
        )

        recalled_kinds = {
            str(item.get("kind", ""))
            for item in (recall_result.system_debug.memory_bundle.semantic if recall_result.system_debug else [])
        }
        passed = (
            bool(read_result.expression.message.strip())
            and bool(recall_result.expression.message.strip())
            and "generic_http_read_page" in read_result.action_result.actions
            and "tool_grounded_page_knowledge" in recalled_kinds
            and "generic_http_read_page" not in recall_result.action_result.actions
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="final_v1_website_read_and_recall"
            if passed
            else "final_v1_website_read_and_recall_regression",
            trace_id=recall_result.event.meta.trace_id,
            notes=(
                f"read_actions={','.join(read_result.action_result.actions)};"
                f"recall_actions={','.join(recall_result.action_result.actions)};"
                f"recalled={','.join(sorted(recalled_kinds))};"
                f"message_present={bool(recall_result.expression.message.strip())}"
            ),
        )

    async def organizer_review_then_focus_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(
            memory,
            clickup_task_client=FakeClickUpTaskClient(),
        )

        review_result = await runtime.run(
            _behavior_event(
                event_id="evt-final-v1-daily-use-3",
                trace_id="t-final-v1-daily-use-3",
                user_id="daily-user",
                text="Be my work partner and list tasks in ClickUp for today's release work.",
            )
        )
        followup_result = await runtime.run(
            _behavior_event(
                event_id="evt-final-v1-daily-use-4",
                trace_id="t-final-v1-daily-use-4",
                user_id="daily-user",
                text="Based on that task list, what should I focus on first today?",
            )
        )

        recalled_kinds = {
            str(item.get("kind", ""))
            for item in (followup_result.system_debug.memory_bundle.semantic if followup_result.system_debug else [])
        }
        passed = (
            review_result.role.selected == "work_partner"
            and bool(review_result.expression.message.strip())
            and bool(followup_result.expression.message.strip())
            and "clickup_list_tasks" in review_result.action_result.actions
            and "tool_grounded_task_snapshot" in recalled_kinds
            and "clickup_list_tasks" not in followup_result.action_result.actions
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="final_v1_organizer_review_and_focus"
            if passed
            else "final_v1_organizer_review_and_focus_regression",
            trace_id=followup_result.event.meta.trace_id,
            notes=(
                f"review_actions={','.join(review_result.action_result.actions)};"
                f"followup_actions={','.join(followup_result.action_result.actions)};"
                f"recalled={','.join(sorted(recalled_kinds))};"
                f"message_present={bool(followup_result.expression.message.strip())}"
            ),
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(test_id="T18.1", run=website_read_then_recall_scenario),
            BehaviorScenarioDefinition(test_id="T18.2", run=organizer_review_then_focus_scenario),
        ]
    )
    assert len(results) == 2
    assert {result.status for result in results} == {"pass"}


async def test_runtime_behavior_time_aware_planned_work_scenarios() -> None:
    class _BehaviorReflectionWorker:
        running = False

        async def run_pending_once(self, limit: int = 1) -> list[dict]:
            return []

        def snapshot(self) -> dict[str, object]:
            return {
                "running": False,
                "max_attempts": 3,
                "stuck_processing_seconds": 180,
                "retry_backoff_seconds": (5, 30, 120),
            }

    async def due_delivery_foreground_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(memory)
        memory.pending_subconscious_proposals = [
            {
                "proposal_id": 91,
                "proposal_type": "nudge_user",
                "summary": "planned_work_due:9:send the release summary",
                "payload": {
                    "handoff_kind": "planned_work_due",
                    "work_id": 9,
                    "work_kind": "reminder",
                    "summary": "send the release summary",
                    "delivery_channel": "telegram",
                    "source_event_id": "evt-reminder-1",
                },
                "status": "pending",
            }
        ]
        memory.active_planned_work = [
            {
                "id": 9,
                "user_id": "daily-user",
                "kind": "reminder",
                "summary": "send the release summary",
                "status": "due",
                "delivery_channel": "telegram",
                "source_event_id": "evt-reminder-1",
            }
        ]

        result = await runtime.run(
            Event(
                event_id="evt-time-aware-behavior-1",
                source="scheduler",
                subsource="maintenance_tick",
                timestamp=datetime.now(timezone.utc),
                payload={
                    "text": "planned work due: send the release summary",
                    "chat_id": 123456,
                    "planned_work_due": {
                        "work_id": 9,
                        "summary": "send the release summary",
                        "work_kind": "reminder",
                        "delivery_channel": "telegram",
                        "source_event_id": "evt-reminder-1",
                    },
                },
                meta=EventMeta(user_id="daily-user", trace_id="t-time-aware-behavior-1"),
            )
        )

        passed = (
            result.expression.channel == "telegram"
            and result.action_result.status == "success"
            and result.action_result.actions == ["send_telegram_message"]
            and len(memory.resolved_subconscious_proposals) == 1
            and memory.resolved_subconscious_proposals[0]["decision"] == "accept"
            and memory.resolved_subconscious_proposals[0]["reason"] == "scheduled_due_planned_work_handoff"
            and result.plan.proposal_handoffs[0].decision == "accept"
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="time_aware_planned_work_foreground_due_delivery"
            if passed
            else "time_aware_planned_work_foreground_due_delivery_regression",
            trace_id=result.event.meta.trace_id,
            notes=(
                f"channel={result.expression.channel};"
                f"actions={','.join(result.action_result.actions)};"
                f"handoff_decision={result.plan.proposal_handoffs[0].decision};"
                f"resolved={len(memory.resolved_subconscious_proposals)}"
            ),
        )

    async def recurring_reevaluation_scenario() -> BehaviorScenarioCheck:
        memory = PersistingFakeMemoryRepository(recent_memory=[])
        runtime = _build_behavior_runtime(memory)
        reminder_result = await runtime.run(
            _behavior_event(
                event_id="evt-time-aware-behavior-2",
                trace_id="t-time-aware-behavior-2",
                user_id="daily-user",
                text="Remind me every day to review deployment health.",
            )
        )
        recurring_item = memory.active_planned_work[0]
        recurring_item["preferred_at"] = datetime.now(timezone.utc) - timedelta(minutes=5)
        recurring_item["not_before"] = recurring_item["preferred_at"]
        recurring_item["delivery_channel"] = "telegram"
        recurring_item["source_event_id"] = "evt-time-aware-behavior-2"

        scheduler = SchedulerWorker(
            memory_repository=memory,  # type: ignore[arg-type]
            reflection_worker=_BehaviorReflectionWorker(),  # type: ignore[arg-type]
            enabled=True,
            reflection_runtime_mode="deferred",
            reflection_interval_seconds=900,
            maintenance_interval_seconds=3600,
        )
        scheduler.set_runtime(runtime)
        summary = await scheduler.run_maintenance_tick_once(reason="behavior_recurring_due_delivery")

        recurrence_update = memory.planned_work_recurrence_updates[0] if memory.planned_work_recurrence_updates else {}
        passed = (
            reminder_result.memory_record is not None
            and recurring_item["recurrence_mode"] == "daily"
            and recurring_item["status"] == "pending"
            and summary["foreground_delivery_successes"] == 1
            and summary["recurrence_advanced"] == 1
            and recurrence_update.get("work_id") == recurring_item["id"]
            and isinstance(recurrence_update.get("preferred_at"), datetime)
            and recurrence_update["preferred_at"] > datetime.now(timezone.utc)
        )
        return BehaviorScenarioCheck(
            passed=passed,
            reason="time_aware_planned_work_recurring_reevaluation"
            if passed
            else "time_aware_planned_work_recurring_reevaluation_regression",
            trace_id="t-time-aware-behavior-2-maintenance",
            notes=(
                f"recurrence_mode={recurring_item.get('recurrence_mode', '')};"
                f"status={recurring_item.get('status', '')};"
                f"foreground_successes={summary['foreground_delivery_successes']};"
                f"recurrence_advanced={summary['recurrence_advanced']}"
            ),
        )

    results = await execute_behavior_scenarios(
        [
            BehaviorScenarioDefinition(test_id="T19.1", run=due_delivery_foreground_scenario),
            BehaviorScenarioDefinition(test_id="T19.2", run=recurring_reevaluation_scenario),
        ]
    )
    assert len(results) == 2
    assert {result.status for result in results} == {"pass"}


@pytest.mark.asyncio()
async def test_runtime_behavior_capability_record_truthfulness_boundary() -> None:
    memory = PersistingFakeMemoryRepository(recent_memory=[])
    runtime = _build_behavior_runtime(
        memory,
        web_browser_client=FakeGenericHttpPageClient(),
    )

    result = await runtime.run(
        Event(
            event_id="evt-capability-record-truthfulness",
            source="api",
            subsource="http",
            timestamp=datetime.now(timezone.utc),
            payload={
                "text": "Be my work partner and read page https://luckysparrow.ch so we can decide what is on that page.",
            },
            meta=EventMeta(user_id="u-1", trace_id="trace-capability-record-truthfulness"),
        )
    )

    selected_skill_ids = [skill.skill_id for skill in result.role.selected_skills]
    actions = list(result.action_result.actions)
    intent_types = [intent.intent_type for intent in result.plan.domain_intents]

    assert result.role.selected == "work_partner"
    assert "structured_reasoning" in selected_skill_ids
    assert "execution_planning" in selected_skill_ids
    assert "connector_boundary_review" in selected_skill_ids
    assert "web_browser_access_intent" in intent_types
    assert "generic_http_read_page" in actions
    assert "clickup_create_task" not in actions
    assert "clickup_update_task" not in actions
    assert "google_calendar_read_availability" not in actions
