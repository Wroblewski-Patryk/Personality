from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.contracts import (
    ActionDelivery,
    ActionResult,
    AffectiveAssessmentOutput,
    ContextOutput,
    Event,
    ExpressionOutput,
    IdentityOutput,
    MemoryRecord,
    MotivationOutput,
    PerceptionOutput,
    PlanOutput,
    RoleOutput,
    RuntimeResult,
)

GRAPH_STATE_SCHEMA_VERSION = "aion_runtime_graph_v1"
GRAPH_FOREGROUND_STAGE_ORDER = (
    "perception",
    "context",
    "motivation",
    "role",
    "planning",
    "expression",
    "action",
)


class GraphMemoryState(BaseModel):
    episodic: list[dict[str, Any]] = Field(default_factory=list)
    semantic: list[dict[str, Any]] = Field(default_factory=list)
    affective: list[dict[str, Any]] = Field(default_factory=list)
    operational: dict[str, Any] = Field(default_factory=dict)


AttentionInboxSource = Literal["user_event", "scheduler_tick", "subconscious_proposal"]
AttentionInboxStatus = Literal["pending", "claimed", "answered", "deferred"]
ProposalType = Literal["ask_user", "research_topic", "suggest_goal", "nudge_user"]
ProposalDecision = Literal["accept", "merge", "defer", "discard"]
TurnAssemblyStatus = Literal["pending", "claimed", "answered"]
ConnectorKind = Literal["calendar", "task_system", "cloud_drive"]
ConnectorOperationMode = Literal["read_only", "suggestion_only", "mutate_with_confirmation"]


class SubconsciousProposalState(BaseModel):
    proposal_id: str
    proposal_type: ProposalType
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    status: Literal["pending", "accepted", "merged", "deferred", "discarded"] = "pending"
    source_loop: Literal["subconscious"] = "subconscious"
    research_policy: Literal["read_only"] = "read_only"
    allowed_tools: list[str] = Field(default_factory=list)
    created_at: datetime | None = None


class AttentionInboxItemState(BaseModel):
    item_id: str
    source: AttentionInboxSource
    conversation_key: str = "global"
    event: Event | None = None
    proposal: SubconsciousProposalState | None = None
    status: AttentionInboxStatus = "pending"
    priority: float = 0.5
    created_at: datetime | None = None


class TurnAssemblyState(BaseModel):
    turn_id: str
    conversation_key: str
    item_ids: list[str] = Field(default_factory=list)
    assembled_text: str = ""
    status: TurnAssemblyStatus = "pending"
    owner: Literal["conscious", "none"] = "none"
    source_item_count: int = 0
    claimed_at: datetime | None = None
    answered_at: datetime | None = None


class ProposalHandoffState(BaseModel):
    proposal_id: str
    decision: ProposalDecision
    reason: str = ""
    decided_by: Literal["conscious"] = "conscious"
    decided_at: datetime | None = None


class ExternalConnectorCapabilityState(BaseModel):
    connector_kind: ConnectorKind
    provider_hint: str | None = None
    capability: str
    mode: ConnectorOperationMode
    requires_opt_in: bool = True
    requires_confirmation: bool = False


class ExternalConnectorPermissionGateState(BaseModel):
    connector_kind: ConnectorKind
    provider_hint: str | None = None
    operation: str
    mode: ConnectorOperationMode
    allowed: bool = False
    reason: str = "explicit_user_authorization_required"


class GraphRuntimeState(BaseModel):
    schema_version: str = GRAPH_STATE_SCHEMA_VERSION
    source_runtime: Literal["python_orchestrator", "langgraph"] = "python_orchestrator"
    event: Event
    memory: GraphMemoryState = Field(default_factory=GraphMemoryState)
    conclusions: list[dict[str, Any]] = Field(default_factory=list)
    relations: list[dict[str, Any]] = Field(default_factory=list)
    user_preferences: dict[str, Any] = Field(default_factory=dict)
    theta: dict[str, Any] | None = None
    identity: IdentityOutput | None = None
    active_goals: list[dict[str, Any]] = Field(default_factory=list)
    active_tasks: list[dict[str, Any]] = Field(default_factory=list)
    active_goal_milestones: list[dict[str, Any]] = Field(default_factory=list)
    goal_milestone_history: list[dict[str, Any]] = Field(default_factory=list)
    goal_progress_history: list[dict[str, Any]] = Field(default_factory=list)
    attention_inbox: list[AttentionInboxItemState] = Field(default_factory=list)
    pending_turn: TurnAssemblyState | None = None
    subconscious_proposals: list[SubconsciousProposalState] = Field(default_factory=list)
    proposal_handoffs: list[ProposalHandoffState] = Field(default_factory=list)
    connector_capabilities: list[ExternalConnectorCapabilityState] = Field(default_factory=list)
    connector_permission_gates: list[ExternalConnectorPermissionGateState] = Field(default_factory=list)
    perception: PerceptionOutput | None = None
    affective: AffectiveAssessmentOutput | None = None
    context: ContextOutput | None = None
    motivation: MotivationOutput | None = None
    role: RoleOutput | None = None
    plan: PlanOutput | None = None
    expression: ExpressionOutput | None = None
    action_delivery: ActionDelivery | None = None
    action_result: ActionResult | None = None
    memory_record: MemoryRecord | None = None
    reflection_triggered: bool | None = None
    stage_timings_ms: dict[str, int] = Field(default_factory=dict)
    duration_ms: int | None = None


def expression_to_action_delivery(*, event: Event, expression: ExpressionOutput) -> ActionDelivery:
    channel = expression.channel if expression.channel in {"api", "telegram"} else "api"
    raw_chat_id = event.payload.get("chat_id") if channel == "telegram" else None
    chat_id = raw_chat_id if isinstance(raw_chat_id, (int, str)) else None
    return ActionDelivery(
        message=expression.message,
        tone=expression.tone,
        channel=channel,
        language=expression.language,
        chat_id=chat_id,
    )


def build_graph_state_seed(
    event: Event,
    *,
    source_runtime: Literal["python_orchestrator", "langgraph"] = "python_orchestrator",
) -> GraphRuntimeState:
    return GraphRuntimeState(
        event=event,
        source_runtime=source_runtime,
    )


def runtime_result_to_graph_state(
    result: RuntimeResult,
    *,
    source_runtime: Literal["python_orchestrator", "langgraph"] = "python_orchestrator",
) -> GraphRuntimeState:
    episodic_rows: list[dict[str, Any]] = []
    if result.memory_record is not None:
        episodic_rows.append(result.memory_record.model_dump(mode="python"))

    action_delivery = expression_to_action_delivery(event=result.event, expression=result.expression)
    return GraphRuntimeState(
        event=result.event,
        source_runtime=source_runtime,
        memory=GraphMemoryState(
            episodic=episodic_rows,
            operational={
                "active_goals": [goal.model_dump(mode="python") for goal in result.active_goals],
                "active_tasks": [task.model_dump(mode="python") for task in result.active_tasks],
                "active_goal_milestones": [
                    milestone.model_dump(mode="python")
                    for milestone in result.active_goal_milestones
                ],
                "goal_milestone_history": [
                    history.model_dump(mode="python")
                    for history in result.goal_milestone_history
                ],
                "goal_progress_history": [
                    history.model_dump(mode="python")
                    for history in result.goal_progress_history
                ],
            },
        ),
        relations=[],
        identity=result.identity,
        active_goals=[goal.model_dump(mode="python") for goal in result.active_goals],
        active_tasks=[task.model_dump(mode="python") for task in result.active_tasks],
        active_goal_milestones=[
            milestone.model_dump(mode="python") for milestone in result.active_goal_milestones
        ],
        goal_milestone_history=[
            history.model_dump(mode="python") for history in result.goal_milestone_history
        ],
        goal_progress_history=[
            history.model_dump(mode="python") for history in result.goal_progress_history
        ],
        perception=result.perception,
        affective=result.affective,
        context=result.context,
        motivation=result.motivation,
        role=result.role,
        plan=result.plan,
        expression=result.expression,
        action_delivery=action_delivery,
        action_result=result.action_result,
        memory_record=result.memory_record,
        reflection_triggered=result.reflection_triggered,
        stage_timings_ms=dict(result.stage_timings_ms),
        duration_ms=result.duration_ms,
    )


def graph_state_missing_runtime_fields(state: GraphRuntimeState) -> list[str]:
    required_fields = (
        "identity",
        "perception",
        "context",
        "motivation",
        "role",
        "plan",
        "expression",
        "action_delivery",
        "action_result",
        "duration_ms",
    )
    return [field for field in required_fields if getattr(state, field) is None]


def graph_state_to_runtime_result(state: GraphRuntimeState) -> RuntimeResult:
    missing = graph_state_missing_runtime_fields(state)
    if missing:
        missing_fields = ", ".join(missing)
        raise ValueError(f"graph state is not complete for runtime result conversion: {missing_fields}")

    perception = state.perception
    assert perception is not None
    return RuntimeResult(
        event=state.event,
        identity=state.identity,
        active_goals=state.active_goals,
        active_tasks=state.active_tasks,
        active_goal_milestones=state.active_goal_milestones,
        goal_milestone_history=state.goal_milestone_history,
        goal_progress_history=state.goal_progress_history,
        perception=perception,
        affective=state.affective or perception.affective,
        context=state.context,
        motivation=state.motivation,
        role=state.role,
        plan=state.plan,
        action_result=state.action_result,
        expression=state.expression,
        memory_record=state.memory_record,
        reflection_triggered=bool(state.reflection_triggered),
        stage_timings_ms=dict(state.stage_timings_ms),
        duration_ms=int(state.duration_ms or 0),
    )
