from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.memory.vector_types import EmbeddingVectorType


class Base(DeclarativeBase):
    pass


class AionMemory(Base):
    __tablename__ = "aion_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    importance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionSemanticEmbedding(Base):
    __tablename__ = "aion_semantic_embedding"
    __table_args__ = (
        UniqueConstraint("user_id", "source_kind", "source_id", name="uq_aion_semantic_embedding_source"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_kind: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(96), nullable=False, index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    scope_type: Mapped[str] = mapped_column(String(16), nullable=False, default="global", index=True)
    scope_key: Mapped[str] = mapped_column(String(64), nullable=False, default="global", index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(
        EmbeddingVectorType(dimensions=1536),
        nullable=True,
    )
    embedding_model: Mapped[str] = mapped_column(String(64), nullable=False, default="deterministic-v1")
    embedding_dimensions: Mapped[int] = mapped_column(Integer, nullable=False, default=32)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionProfile(Base):
    __tablename__ = "aion_profile"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    preferred_language: Mapped[str] = mapped_column(String(8), nullable=False)
    language_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    language_source: Mapped[str] = mapped_column(String(32), nullable=False, default="default")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionConclusion(Base):
    __tablename__ = "aion_conclusion"
    __table_args__ = (
        UniqueConstraint("user_id", "kind", "scope_type", "scope_key", name="uq_aion_conclusion_user_kind_scope"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    scope_type: Mapped[str] = mapped_column(String(16), nullable=False, default="global", index=True)
    scope_key: Mapped[str] = mapped_column(String(64), nullable=False, default="global", index=True)
    content: Mapped[str] = mapped_column(String(128), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="system")
    supporting_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionAuthUser(Base):
    __tablename__ = "aion_auth_user"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionAuthSession(Base):
    __tablename__ = "aion_auth_session"
    __table_args__ = (
        UniqueConstraint("session_token_hash", name="uq_aion_auth_session_token_hash"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_token_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(256), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionRelation(Base):
    __tablename__ = "aion_relation"
    __table_args__ = (
        UniqueConstraint("user_id", "relation_type", "scope_type", "scope_key", name="uq_aion_relation_user_type_scope"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    relation_value: Mapped[str] = mapped_column(String(128), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="background_reflection")
    scope_type: Mapped[str] = mapped_column(String(16), nullable=False, default="global", index=True)
    scope_key: Mapped[str] = mapped_column(String(64), nullable=False, default="global", index=True)
    supporting_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    decay_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.02)
    last_observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionTheta(Base):
    __tablename__ = "aion_theta"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    support_bias: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    analysis_bias: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    execution_bias: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionGoal(Base):
    __tablename__ = "aion_goal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="medium", index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active", index=True)
    goal_type: Mapped[str] = mapped_column(String(24), nullable=False, default="tactical")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AionTask(Base):
    __tablename__ = "aion_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    goal_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="medium", index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="todo", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AionPlannedWorkItem(Base):
    __tablename__ = "aion_planned_work_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    goal_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    task_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(String(220), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending", index=True)
    not_before: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    preferred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    recurrence_mode: Mapped[str] = mapped_column(String(16), nullable=False, default="none")
    recurrence_rule: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    delivery_channel: Mapped[str] = mapped_column(String(16), nullable=False, default="none")
    requires_foreground_execution: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    quiet_hours_policy: Mapped[str] = mapped_column(String(32), nullable=False, default="respect_user_context")
    provenance: Mapped[str] = mapped_column(String(32), nullable=False, default="explicit_user_request")
    source_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    last_evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionGoalProgress(Base):
    __tablename__ = "aion_goal_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    goal_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    execution_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    progress_trend: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionGoalMilestone(Base):
    __tablename__ = "aion_goal_milestone"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    goal_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    phase: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active", index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AionGoalMilestoneHistory(Base):
    __tablename__ = "aion_goal_milestone_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    goal_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    milestone_name: Mapped[str] = mapped_column(String(160), nullable=False)
    phase: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    risk_level: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    completion_criteria: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionAttentionTurn(Base):
    __tablename__ = "aion_attention_turn"
    __table_args__ = (
        UniqueConstraint("user_id", "conversation_key", name="uq_aion_attention_turn_user_conversation"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    conversation_key: Mapped[str] = mapped_column(String(96), nullable=False, index=True)
    turn_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending", index=True)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    assembled_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_mode: Mapped[str] = mapped_column(String(24), nullable=False, default="durable_inbox")
    messages_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    event_ids_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    update_keys_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionReflectionTask(Base):
    __tablename__ = "aion_reflection_task"
    __table_args__ = (UniqueConstraint("event_id", name="uq_aion_reflection_task_event_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionSchedulerCadenceEvidence(Base):
    __tablename__ = "aion_scheduler_cadence_evidence"
    __table_args__ = (
        UniqueConstraint("cadence_kind", name="uq_aion_scheduler_cadence_evidence_kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cadence_kind: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    execution_owner: Mapped[str] = mapped_column(String(32), nullable=False)
    execution_mode: Mapped[str] = mapped_column(String(24), nullable=False)
    summary_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class AionSubconsciousProposal(Base):
    __tablename__ = "aion_subconscious_proposal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    proposal_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending", index=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_policy: Mapped[str] = mapped_column(String(16), nullable=False, default="read_only")
    allowed_tools_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
