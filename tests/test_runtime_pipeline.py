import json
from datetime import datetime, timezone

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
from app.core.contracts import Event, EventMeta, NoopDomainIntent
from app.core.events import build_scheduler_event
from app.core.runtime import RuntimeOrchestrator
from app.expression.generator import ExpressionAgent
from app.motivation.engine import MotivationEngine
from tests.empathy_fixtures import EMPATHY_SUPPORT_SCENARIOS


class FakeMemoryRepository:
    def __init__(self, recent_memory: list[dict] | None = None, user_profile: dict | None = None):
        self.recent_memory = recent_memory or []
        self.recent_limits: list[int] = []
        self.user_profile = user_profile
        self.profile_updates: list[dict] = []
        self.conclusion_updates: list[dict] = []
        self.user_preferences: dict = {}
        self.scoped_user_preferences: dict[tuple[str, str], dict] = {}
        self.user_conclusions: list[dict] = []
        self.scoped_user_conclusions: list[dict] = []
        self.user_theta: dict | None = None
        self.active_goals: list[dict] = []
        self.active_tasks: list[dict] = []
        self.active_goal_milestones: list[dict] = []
        self.goal_milestone_history: list[dict] = []
        self.goal_progress_history: list[dict] = []
        self.reflection_tasks: list[dict] = []
        self.pending_subconscious_proposals: list[dict] = []
        self.resolved_subconscious_proposals: list[dict] = []

    async def get_recent_for_user(self, user_id: str, limit: int = 5) -> list[dict]:
        self.recent_limits.append(limit)
        return self.recent_memory[:limit]

    async def get_user_profile(self, user_id: str) -> dict | None:
        return self.user_profile

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
        scoped = self.scoped_user_preferences.get((normalized_scope_type, normalized_scope_key), {})
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
        normalized_scope_type, normalized_scope_key = self._normalize_scope(scope_type=scope_type, scope_key=scope_key)
        if normalized_scope_type == "global":
            scoped_rows = [row for row in rows if str(row.get("scope_type", "global")) == "global"]
            return scoped_rows[:limit]
        scoped_rows = [
            row
            for row in rows
            if str(row.get("scope_type", "global")) == normalized_scope_type
            and str(row.get("scope_key", "global")) == normalized_scope_key
        ]
        if include_global:
            global_rows = [row for row in rows if str(row.get("scope_type", "global")) == "global"]
            return [*scoped_rows, *global_rows][:limit]
        return scoped_rows[:limit]

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

    async def get_active_goal_milestones(self, user_id: str, *, goal_ids: list[int] | None = None, limit: int = 6) -> list[dict]:
        rows = [item for item in self.active_goal_milestones if item.get("status") == "active"]
        if goal_ids:
            rows = [row for row in rows if row.get("goal_id") in set(goal_ids)]
        return rows[:limit]

    async def get_pending_subconscious_proposals(self, user_id: str, limit: int = 8) -> list[dict]:
        return self.pending_subconscious_proposals[:limit]

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
        normalized_scope_type = str(scope_type or "global").strip().lower()
        normalized_scope_key = str(scope_key or "").strip()
        if normalized_scope_type not in {"global", "goal", "task"}:
            return "global", "global"
        if normalized_scope_type == "global" or not normalized_scope_key:
            return "global", "global"
        return normalized_scope_type, normalized_scope_key

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
        return kwargs

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


class PersistingFakeMemoryRepository(FakeMemoryRepository):
    async def write_episode(self, **kwargs) -> dict:
        record = await super().write_episode(**kwargs)
        self.recent_memory.insert(
            0,
            {
                "event_id": record["event_id"],
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
            item_scope_type, item_scope_key = self._normalize_scope(
                scope_type=str(item.get("scope_type") or "global"),
                scope_key=str(item.get("scope_key") or "global"),
            )
            if item_scope_type == normalized_scope_type and item_scope_key == normalized_scope_key:
                rows.append(item)
                continue
            if include_global and item_scope_type == "global":
                rows.append(item)
        return rows[:limit]


class FakeTelegramClient:
    async def send_message(self, chat_id: int | str, text: str) -> dict:
        return {"ok": True}


class FakeOpenAIClient:
    def __init__(self):
        self.calls: list[dict[str, str]] = []

    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        role_name: str,
        response_language: str,
        response_style: str | None,
        plan_goal: str,
        motivation_mode: str,
        response_tone: str,
        collaboration_preference: str | None,
        identity_summary: str = "",
    ) -> str | None:
        self.calls.append(
            {
                "user_text": user_text,
                "context_summary": context_summary,
                "role_name": role_name,
                "response_language": response_language,
                "response_style": response_style or "",
                "plan_goal": plan_goal,
                "motivation_mode": motivation_mode,
                "response_tone": response_tone,
                "collaboration_preference": collaboration_preference or "",
                "identity_summary": identity_summary,
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
    memory = FakeMemoryRepository(recent_memory=[])
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
    assert result.motivation.mode == "execute"
    assert "compose_proactive_warning" in result.plan.steps
    assert "send_telegram_message" in result.plan.steps
    assert result.plan.needs_response is True
    assert result.plan.needs_action is True
    assert result.action_result.status == "success"
    assert result.action_result.actions == ["send_telegram_message"]
    assert result.reflection_triggered is True


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
    assert result.plan.domain_intents[0].intent_type == "noop"
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


def _build_behavior_runtime(memory_repository: FakeMemoryRepository) -> RuntimeOrchestrator:
    return RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient()),
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
