from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


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


class GoalProgressRecordOutput(BaseModel):
    id: int | None = None
    goal_id: int
    score: float
    execution_state: str | None = None
    progress_trend: str | None = None
    source_event_id: str | None = None
    created_at: datetime


class MotivationOutput(BaseModel):
    importance: float
    urgency: float
    valence: float
    arousal: float
    mode: str


class RoleOutput(BaseModel):
    selected: str
    confidence: float


class PlanOutput(BaseModel):
    goal: str
    steps: list[str] = Field(default_factory=list)
    needs_action: bool
    needs_response: bool


class ActionResult(BaseModel):
    status: str
    actions: list[str] = Field(default_factory=list)
    notes: str


class ExpressionOutput(BaseModel):
    message: str
    tone: str
    channel: str
    language: str


class MemoryRecord(BaseModel):
    id: int | None = None
    event_id: str
    timestamp: datetime
    summary: str
    importance: float


class RuntimeResult(BaseModel):
    event: Event
    identity: IdentityOutput
    active_goals: list[GoalRecordOutput] = Field(default_factory=list)
    active_tasks: list[TaskRecordOutput] = Field(default_factory=list)
    goal_progress_history: list[GoalProgressRecordOutput] = Field(default_factory=list)
    perception: PerceptionOutput
    context: ContextOutput
    motivation: MotivationOutput
    role: RoleOutput
    plan: PlanOutput
    action_result: ActionResult
    expression: ExpressionOutput
    memory_record: MemoryRecord | None = None
    reflection_triggered: bool = False
    stage_timings_ms: dict[str, int] = Field(default_factory=dict)
    duration_ms: int
