from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


MotivationMode = Literal["respond", "ignore", "analyze", "execute", "clarify"]
MemoryLayerKind = Literal["episodic", "semantic", "affective", "operational"]
SemanticSourceKind = Literal["episodic", "semantic", "affective", "relation"]
ProactiveOutputType = Literal["suggestion", "reminder", "question", "warning", "encouragement", "insight"]
ProactiveMode = Literal["soft", "medium", "strong"]
SubconsciousProposalType = Literal[
    "ask_user",
    "research_topic",
    "suggest_goal",
    "nudge_user",
    "suggest_connector_expansion",
]
ProposalHandoffDecisionType = Literal["accept", "merge", "defer", "discard"]
SubconsciousProposalStatus = Literal["pending", "accepted", "merged", "deferred", "discarded"]
SubconsciousResearchPolicy = Literal["read_only"]
ConnectorKind = Literal["calendar", "task_system", "cloud_drive", "knowledge_search", "web_browser"]
ConnectorOperationMode = Literal["read_only", "suggestion_only", "mutate_with_confirmation"]


class EventMeta(BaseModel):
    user_id: str = "anonymous"
    trace_id: str


class Event(BaseModel):
    event_id: str
    source: str
    subsource: str
    timestamp: datetime
    payload: dict[str, Any] = Field(default_factory=dict)
    meta: EventMeta


class AffectiveAssessmentOutput(BaseModel):
    affect_label: str = "neutral"
    intensity: float = 0.0
    needs_support: bool = False
    confidence: float = 0.0
    source: str = "deterministic_placeholder"
    evidence: list[str] = Field(default_factory=list)


class PerceptionOutput(BaseModel):
    event_type: str
    topic: str
    topic_tags: list[str] = Field(default_factory=list)
    intent: str
    language: str
    language_source: str
    language_confidence: float
    ambiguity: float
    initial_salience: float
    affective: AffectiveAssessmentOutput = Field(default_factory=AffectiveAssessmentOutput)


class ContextOutput(BaseModel):
    summary: str
    related_goals: list[str] = Field(default_factory=list)
    related_tags: list[str] = Field(default_factory=list)
    risk_level: float


class IdentityOutput(BaseModel):
    mission: str
    values: list[str] = Field(default_factory=list)
    behavioral_style: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    preferred_language: str | None = None
    response_style: str | None = None
    collaboration_preference: str | None = None
    theta_orientation: str | None = None
    summary: str


class GoalRecordOutput(BaseModel):
    id: int | None = None
    name: str
    description: str
    priority: str
    status: str
    goal_type: str


class TaskRecordOutput(BaseModel):
    id: int | None = None
    goal_id: int | None = None
    name: str
    description: str
    priority: str
    status: str


class PlannedWorkRecordOutput(BaseModel):
    id: int | None = None
    user_id: str
    goal_id: int | None = None
    task_id: int | None = None
    kind: Literal["follow_up", "check_in", "reminder", "routine", "research_window"]
    summary: str
    status: Literal["pending", "due", "snoozed", "completed", "cancelled"] = "pending"
    not_before: datetime | None = None
    preferred_at: datetime | None = None
    expires_at: datetime | None = None
    recurrence_mode: Literal["none", "daily", "weekly", "custom"] = "none"
    recurrence_rule: str = ""
    delivery_channel: Literal["telegram", "api", "none"] = "none"
    requires_foreground_execution: bool = True
    quiet_hours_policy: str = "respect_user_context"
    provenance: Literal["explicit_user_request", "planning_inference", "reflection_inference"] = "explicit_user_request"
    source_event_id: str | None = None
    last_evaluated_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GoalProgressRecordOutput(BaseModel):
    id: int | None = None
    goal_id: int
    score: float
    execution_state: str | None = None
    progress_trend: str | None = None
    source_event_id: str | None = None
    created_at: datetime


class GoalMilestoneRecordOutput(BaseModel):
    id: int | None = None
    goal_id: int
    name: str
    phase: str
    status: str
    arc: str | None = None
    pressure_level: str | None = None
    dependency_state: str | None = None
    due_state: str | None = None
    due_window: str | None = None
    risk_level: str | None = None
    completion_criteria: str | None = None
    source_event_id: str | None = None


class GoalMilestoneHistoryRecordOutput(BaseModel):
    id: int | None = None
    goal_id: int
    milestone_name: str
    phase: str
    risk_level: str | None = None
    completion_criteria: str | None = None
    source_event_id: str | None = None
    created_at: datetime


class MotivationOutput(BaseModel):
    importance: float
    urgency: float
    valence: float
    arousal: float
    mode: MotivationMode


class ProactiveDecisionOutput(BaseModel):
    trigger: str
    output_type: ProactiveOutputType
    mode: ProactiveMode
    importance: float
    urgency: float
    relevance: float
    interruption_cost: float
    decision_score: float
    should_interrupt: bool
    reason: str


class ProactiveDeliveryGuardOutput(BaseModel):
    allowed: bool
    reason: str
    recent_outbound_count: int = 0
    recent_outbound_limit: int = 0
    unanswered_proactive_count: int = 0
    unanswered_proactive_limit: int = 0


class SubconsciousProposalRecord(BaseModel):
    proposal_id: int | None = None
    proposal_type: SubconsciousProposalType
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    status: SubconsciousProposalStatus = "pending"
    source_event_id: str | None = None
    research_policy: SubconsciousResearchPolicy = "read_only"
    allowed_tools: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProposalHandoffDecisionOutput(BaseModel):
    proposal_id: int
    decision: ProposalHandoffDecisionType
    reason: str = ""
    decided_by: Literal["conscious"] = "conscious"
    decided_at: datetime | None = None


class ConnectorPermissionGateOutput(BaseModel):
    connector_kind: ConnectorKind
    provider_hint: str | None = None
    operation: str
    mode: ConnectorOperationMode
    requires_opt_in: bool = True
    requires_confirmation: bool = False
    allowed: bool = False
    reason: str = "explicit_user_authorization_required"


class SkillCapabilityOutput(BaseModel):
    policy_owner: Literal["role_skill_boundary_policy"] = "role_skill_boundary_policy"
    skill_id: str
    label: str
    capability_family: Literal[
        "support",
        "analysis",
        "execution",
        "memory",
        "connector_boundary",
    ]
    reason: str
    side_effect_posture: Literal["metadata_only"] = "metadata_only"


class RoleSelectionEvidenceOutput(BaseModel):
    signal: str
    source: str
    value: str
    applied: bool = False
    note: str = ""


class RoleOutput(BaseModel):
    selected: str
    confidence: float
    selection_policy_owner: Literal["role_selection_policy"] = "role_selection_policy"
    skill_policy_owner: Literal["role_skill_boundary_policy"] = "role_skill_boundary_policy"
    selection_reason: str = ""
    selection_evidence: list[RoleSelectionEvidenceOutput] = Field(default_factory=list)
    selected_skills: list[SkillCapabilityOutput] = Field(default_factory=list)


class NoopDomainIntent(BaseModel):
    intent_type: Literal["noop"] = "noop"
    reason: str = "no_domain_change_detected"


class UpsertGoalDomainIntent(BaseModel):
    intent_type: Literal["upsert_goal"] = "upsert_goal"
    name: str
    description: str
    priority: str = "medium"
    goal_type: str = "tactical"


class UpsertTaskDomainIntent(BaseModel):
    intent_type: Literal["upsert_task"] = "upsert_task"
    name: str
    description: str
    priority: str = "medium"
    status: str = "todo"


class UpdateTaskStatusDomainIntent(BaseModel):
    intent_type: Literal["update_task_status"] = "update_task_status"
    status: str
    task_hint: str


class UpsertPlannedWorkItemDomainIntent(BaseModel):
    intent_type: Literal["upsert_planned_work_item"] = "upsert_planned_work_item"
    work_kind: Literal["follow_up", "check_in", "reminder", "routine", "research_window"]
    summary: str
    goal_id: int | None = None
    task_id: int | None = None
    not_before: datetime | None = None
    preferred_at: datetime | None = None
    expires_at: datetime | None = None
    recurrence_mode: Literal["none", "daily", "weekly", "custom"] = "none"
    recurrence_rule: str = ""
    channel_hint: Literal["telegram", "api", "none"] = "none"
    requires_foreground_execution: bool = True
    quiet_hours_policy: str = "respect_user_context"
    provenance: Literal["explicit_user_request", "planning_inference", "reflection_inference"] = "explicit_user_request"


class ReschedulePlannedWorkItemDomainIntent(BaseModel):
    intent_type: Literal["reschedule_planned_work_item"] = "reschedule_planned_work_item"
    work_id: int
    not_before: datetime | None = None
    preferred_at: datetime | None = None
    expires_at: datetime | None = None
    reason: str = ""


class CancelPlannedWorkItemDomainIntent(BaseModel):
    intent_type: Literal["cancel_planned_work_item"] = "cancel_planned_work_item"
    work_id: int
    reason: str = ""


class CompletePlannedWorkItemDomainIntent(BaseModel):
    intent_type: Literal["complete_planned_work_item"] = "complete_planned_work_item"
    work_id: int
    reason: str = ""


class PromoteInferredGoalDomainIntent(BaseModel):
    intent_type: Literal["promote_inferred_goal"] = "promote_inferred_goal"
    name: str
    description: str
    priority: str = "medium"
    goal_type: str = "tactical"
    evidence: Literal["repeated_execution_blocker"] = "repeated_execution_blocker"


class PromoteInferredTaskDomainIntent(BaseModel):
    intent_type: Literal["promote_inferred_task"] = "promote_inferred_task"
    name: str
    description: str
    priority: str = "medium"
    status: str = "todo"
    evidence: Literal["repeated_execution_blocker"] = "repeated_execution_blocker"


class MaintainTaskStatusDomainIntent(BaseModel):
    intent_type: Literal["maintain_task_status"] = "maintain_task_status"
    status: str
    task_hint: str
    reason: str = "inferred_repeated_blocker_evidence"


class UpdateResponseStyleDomainIntent(BaseModel):
    intent_type: Literal["update_response_style"] = "update_response_style"
    style: Literal["concise", "structured"]
    source: str = "explicit_request"


class UpdateCollaborationPreferenceDomainIntent(BaseModel):
    intent_type: Literal["update_collaboration_preference"] = "update_collaboration_preference"
    preference: Literal["guided", "hands_on"]
    source: str = "explicit_request"


class UpdateProactivePreferenceDomainIntent(BaseModel):
    intent_type: Literal["update_proactive_preference"] = "update_proactive_preference"
    opt_in: bool
    source: str = "explicit_request"


class CalendarSchedulingIntentDomainIntent(BaseModel):
    intent_type: Literal["calendar_scheduling_intent"] = "calendar_scheduling_intent"
    operation: Literal["read_availability", "suggest_slots", "create_event", "update_event", "cancel_event"]
    provider_hint: str | None = None
    mode: ConnectorOperationMode = "suggestion_only"
    title_hint: str = ""
    time_hint: str = ""


class ExternalTaskSyncDomainIntent(BaseModel):
    intent_type: Literal["external_task_sync_intent"] = "external_task_sync_intent"
    operation: Literal["list_tasks", "suggest_sync", "create_task", "update_task", "link_internal_task"]
    provider_hint: str = "generic"
    mode: ConnectorOperationMode = "suggestion_only"
    task_hint: str = ""
    status_hint: str = ""


class ConnectedDriveAccessDomainIntent(BaseModel):
    intent_type: Literal["connected_drive_access_intent"] = "connected_drive_access_intent"
    operation: Literal[
        "list_files",
        "search_documents",
        "read_document",
        "suggest_file_plan",
        "upload_file",
        "update_document",
        "delete_file",
    ]
    provider_hint: str = "generic"
    mode: ConnectorOperationMode = "suggestion_only"
    file_hint: str = ""


class ConnectorCapabilityDiscoveryDomainIntent(BaseModel):
    intent_type: Literal["connector_capability_discovery_intent"] = "connector_capability_discovery_intent"
    connector_kind: ConnectorKind
    provider_hint: str = "generic"
    requested_capability: str = "connector_access"
    evidence: str = "repeated_unmet_need"
    mode: Literal["suggestion_only"] = "suggestion_only"


class KnowledgeSearchDomainIntent(BaseModel):
    intent_type: Literal["knowledge_search_intent"] = "knowledge_search_intent"
    operation: Literal["search_web", "suggest_search"] = "search_web"
    provider_hint: str = "generic"
    mode: ConnectorOperationMode = "suggestion_only"
    query_hint: str = ""


class WebBrowserAccessDomainIntent(BaseModel):
    intent_type: Literal["web_browser_access_intent"] = "web_browser_access_intent"
    operation: Literal["read_page", "suggest_page_review"] = "read_page"
    provider_hint: str = "generic"
    mode: ConnectorOperationMode = "suggestion_only"
    page_hint: str = ""


class MaintainRelationDomainIntent(BaseModel):
    intent_type: Literal["maintain_relation"] = "maintain_relation"
    relation_type: str
    relation_value: str
    confidence: float = 0.7
    source: str = "planning_intent"
    scope_type: Literal["global", "goal", "task"] = "global"
    scope_key: str = "global"
    evidence_count: int = 1
    decay_rate: float = 0.02


class UpdateProactiveStateDomainIntent(BaseModel):
    intent_type: Literal["update_proactive_state"] = "update_proactive_state"
    state: Literal[
        "attention_gate_blocked",
        "interruption_deferred",
        "delivery_guard_blocked",
        "delivery_ready",
    ]
    trigger: str
    reason: str
    output_type: ProactiveOutputType
    mode: ProactiveMode
    source: str = "proactive_planning"


DomainActionIntent = Annotated[
    NoopDomainIntent
    | UpsertGoalDomainIntent
    | UpsertTaskDomainIntent
    | UpdateTaskStatusDomainIntent
    | UpsertPlannedWorkItemDomainIntent
    | ReschedulePlannedWorkItemDomainIntent
    | CancelPlannedWorkItemDomainIntent
    | CompletePlannedWorkItemDomainIntent
    | PromoteInferredGoalDomainIntent
    | PromoteInferredTaskDomainIntent
    | MaintainTaskStatusDomainIntent
    | UpdateResponseStyleDomainIntent
    | UpdateCollaborationPreferenceDomainIntent
    | UpdateProactivePreferenceDomainIntent
    | CalendarSchedulingIntentDomainIntent
    | ExternalTaskSyncDomainIntent
    | ConnectedDriveAccessDomainIntent
    | ConnectorCapabilityDiscoveryDomainIntent
    | KnowledgeSearchDomainIntent
    | WebBrowserAccessDomainIntent
    | MaintainRelationDomainIntent
    | UpdateProactiveStateDomainIntent,
    Field(discriminator="intent_type"),
]


class PlanOutput(BaseModel):
    goal: str
    steps: list[str] = Field(default_factory=list)
    needs_action: bool
    needs_response: bool
    domain_intents: list[DomainActionIntent] = Field(default_factory=list)
    inferred_promotion_diagnostics: list[str] = Field(default_factory=list)
    proactive_decision: ProactiveDecisionOutput | None = None
    proactive_delivery_guard: ProactiveDeliveryGuardOutput | None = None
    proposal_handoffs: list[ProposalHandoffDecisionOutput] = Field(default_factory=list)
    accepted_proposals: list[SubconsciousProposalRecord] = Field(default_factory=list)
    connector_permission_gates: list[ConnectorPermissionGateOutput] = Field(default_factory=list)
    selected_skills: list[SkillCapabilityOutput] = Field(default_factory=list)


class ToolGroundedLearningCandidate(BaseModel):
    policy_owner: Literal["tool_grounded_learning_policy"] = "tool_grounded_learning_policy"
    source_family: Literal["knowledge_search", "web_browser", "task_system", "calendar", "cloud_drive"]
    source_operation: str
    conclusion_kind: str
    content: str
    confidence: float = 0.74
    source_reference: str = ""


class ActionResult(BaseModel):
    status: str
    actions: list[str] = Field(default_factory=list)
    notes: str
    tool_learning_candidates: list[ToolGroundedLearningCandidate] = Field(default_factory=list)


class ExpressionOutput(BaseModel):
    message: str
    tone: str
    channel: str
    language: str


class ActionDeliveryConnectorIntent(BaseModel):
    connector_kind: ConnectorKind
    provider_hint: str | None = None
    operation: str
    mode: ConnectorOperationMode
    allowed: bool = False
    requires_confirmation: bool = False
    reason: str = "explicit_user_authorization_required"


class ActionDeliveryExecutionEnvelope(BaseModel):
    connector_safe: bool = False
    connector_intents: list[ActionDeliveryConnectorIntent] = Field(default_factory=list)
    connector_permission_gates: list[ConnectorPermissionGateOutput] = Field(default_factory=list)


class ActionDelivery(BaseModel):
    message: str
    tone: str
    channel: Literal["api", "telegram"]
    language: str
    chat_id: int | str | None = None
    execution_envelope: ActionDeliveryExecutionEnvelope = Field(default_factory=ActionDeliveryExecutionEnvelope)


class MemoryRecord(BaseModel):
    id: int | None = None
    event_id: str
    timestamp: datetime
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    importance: float


class EmbeddingRecord(BaseModel):
    id: int | None = None
    user_id: str
    source_kind: SemanticSourceKind
    source_id: str
    content: str
    embedding: list[float] = Field(default_factory=list)
    embedding_model: str
    embedding_dimensions: int
    scope_type: str = "global"
    scope_key: str = "global"
    source_event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SemanticRetrievalQuery(BaseModel):
    user_id: str
    query_text: str
    query_embedding: list[float] = Field(default_factory=list)
    limit: int = 5
    source_kinds: list[SemanticSourceKind] = Field(default_factory=lambda: ["episodic", "semantic", "affective"])
    scope_type: str = "global"
    scope_key: str = "global"


class SemanticRetrievalHit(BaseModel):
    source_kind: SemanticSourceKind
    source_id: str
    content: str
    score: float
    lexical_score: float = 0.0
    vector_score: float = 0.0
    affective_score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class SemanticRetrievalResult(BaseModel):
    query: SemanticRetrievalQuery
    hits: list[SemanticRetrievalHit] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class RuntimeSystemDebugEventView(BaseModel):
    event_id: str
    trace_id: str
    source: str
    subsource: str
    timestamp: datetime
    user_id: str
    payload: dict[str, Any] = Field(default_factory=dict)


class RuntimeSystemDebugMemoryBundle(BaseModel):
    episodic: list[dict[str, Any]] = Field(default_factory=list)
    semantic: list[dict[str, Any]] = Field(default_factory=list)
    affective: list[dict[str, Any]] = Field(default_factory=list)
    relations: list[dict[str, Any]] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class RuntimeSystemDebugPlanView(BaseModel):
    goal: str
    steps: list[str] = Field(default_factory=list)
    needs_action: bool
    needs_response: bool
    domain_intents: list[dict[str, Any]] = Field(default_factory=list)
    inferred_promotion_diagnostics: list[str] = Field(default_factory=list)


class RuntimeSystemDebugOutput(BaseModel):
    mode: Literal["system_debug"] = "system_debug"
    event: RuntimeSystemDebugEventView
    perception: PerceptionOutput
    memory_bundle: RuntimeSystemDebugMemoryBundle
    context: ContextOutput
    motivation: MotivationOutput
    role: RoleOutput
    plan: RuntimeSystemDebugPlanView
    expression: ExpressionOutput
    action_result: ActionResult
    adaptive_state: dict[str, Any] = Field(default_factory=dict)


class RuntimeResult(BaseModel):
    event: Event
    identity: IdentityOutput
    active_goals: list[GoalRecordOutput] = Field(default_factory=list)
    active_tasks: list[TaskRecordOutput] = Field(default_factory=list)
    active_planned_work: list[PlannedWorkRecordOutput] = Field(default_factory=list)
    active_goal_milestones: list[GoalMilestoneRecordOutput] = Field(default_factory=list)
    goal_milestone_history: list[GoalMilestoneHistoryRecordOutput] = Field(default_factory=list)
    goal_progress_history: list[GoalProgressRecordOutput] = Field(default_factory=list)
    perception: PerceptionOutput
    affective: AffectiveAssessmentOutput = Field(default_factory=AffectiveAssessmentOutput)
    context: ContextOutput
    motivation: MotivationOutput
    role: RoleOutput
    plan: PlanOutput
    action_result: ActionResult
    expression: ExpressionOutput
    memory_record: MemoryRecord | None = None
    reflection_triggered: bool = False
    system_debug: RuntimeSystemDebugOutput | None = None
    stage_timings_ms: dict[str, int] = Field(default_factory=dict)
    duration_ms: int
