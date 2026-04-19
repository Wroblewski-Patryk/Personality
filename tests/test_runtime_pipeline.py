import json
from datetime import datetime, timezone

from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.core.action import ActionExecutor
from app.core.contracts import Event, EventMeta
from app.core.runtime import RuntimeOrchestrator
from app.expression.generator import ExpressionAgent
from app.motivation.engine import MotivationEngine


class FakeMemoryRepository:
    def __init__(self, recent_memory: list[dict] | None = None, user_profile: dict | None = None):
        self.recent_memory = recent_memory or []
        self.user_profile = user_profile
        self.profile_updates: list[dict] = []
        self.conclusion_updates: list[dict] = []
        self.user_preferences: dict = {}
        self.user_conclusions: list[dict] = []
        self.user_theta: dict | None = None
        self.active_goals: list[dict] = []
        self.active_tasks: list[dict] = []
        self.active_goal_milestones: list[dict] = []
        self.goal_milestone_history: list[dict] = []
        self.goal_progress_history: list[dict] = []

    async def get_recent_for_user(self, user_id: str, limit: int = 5) -> list[dict]:
        return self.recent_memory[:limit]

    async def get_user_profile(self, user_id: str) -> dict | None:
        return self.user_profile

    async def get_user_runtime_preferences(self, user_id: str) -> dict:
        return self.user_preferences

    async def get_user_conclusions(self, user_id: str, limit: int = 3) -> list[dict]:
        return self.user_conclusions[:limit]

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


class FailingWriteMemoryRepository(FakeMemoryRepository):
    async def write_episode(self, **kwargs) -> dict:
        raise RuntimeError("database unavailable")


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


class FakeReflectionWorker:
    def __init__(self, enqueue_result: bool = True):
        self.enqueue_result = enqueue_result
        self.calls: list[dict[str, str]] = []

    async def enqueue(self, user_id: str, event_id: str) -> bool:
        self.calls.append({"user_id": user_id, "event_id": event_id})
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
    assert result.perception.affective.source == "deterministic_placeholder"
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
    assert result.reflection_triggered is True
    assert set(result.stage_timings_ms) == {
        "memory_load",
        "task_load",
        "goal_milestone_load",
        "goal_milestone_history_load",
        "goal_progress_load",
        "identity_load",
        "perception",
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
    assert reflection.calls == [{"user_id": "u-1", "event_id": "evt-1"}]
    assert memory.profile_updates == []
    assert openai.calls[0]["response_style"] == ""
    assert openai.calls[0]["response_tone"] == "supportive"
    assert openai.calls[0]["collaboration_preference"] == ""
    assert "constructive support" in openai.calls[0]["identity_summary"]


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

    assert result.motivation.mode == "respond"
    assert result.motivation.valence <= -0.45
    assert result.role.selected == "friend"
    assert "acknowledge_emotion" in result.plan.steps
    assert "reduce_pressure" in result.plan.steps
    assert result.expression.tone == "supportive"
    assert openai.calls[0]["motivation_mode"] == "respond"
    assert openai.calls[0]["response_tone"] == "supportive"
    assert result.reflection_triggered is True


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

    assert done_result.active_goals[0].name == "ship the MVP this week"
    assert done_result.active_tasks == []
    assert done_result.stage_timings_ms["state_refresh"] >= 0


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
