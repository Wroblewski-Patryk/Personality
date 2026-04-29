import re
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.communication.boundary import proactive_boundary_block_reason
from app.core.contracts import MemoryLayerKind
from app.core.reflection_scope_policy import (
    GLOBAL_SCOPE_KEY,
    GLOBAL_SCOPE_TYPE,
    canonicalize_conclusion_scope,
    canonicalize_relation_scope,
    conclusion_matches_scope_request,
    relation_matches_scope_request,
)
from app.core.retrieval_policy import foreground_retrieval_source_kinds
from app.memory.embeddings import (
    cosine_similarity,
    materialize_embedding,
    normalize_embedding_refresh_mode,
    normalize_embedding_source_kinds,
    resolve_embedding_posture,
)
from app.memory.openai_embedding_client import OpenAIEmbeddingClient
from app.memory.models import (
    AionAttentionTurn,
    AionAuthSession,
    AionAuthUser,
    AionConclusion,
    AionGoal,
    AionGoalMilestone,
    AionGoalMilestoneHistory,
    AionPlannedWorkItem,
    AionGoalProgress,
    AionMemory,
    AionProfile,
    AionRelation,
    AionReflectionTask,
    AionSchedulerCadenceEvidence,
    AionSemanticEmbedding,
    AionSubconsciousProposal,
    AionTask,
    AionTheta,
    Base,
)
from app.utils.utc_offset import DEFAULT_UTC_OFFSET, normalize_utc_offset


class MemoryRepository:
    ACTIVE_GOAL_STATUSES = ("active",)
    ACTIVE_TASK_STATUSES = ("todo", "in_progress", "blocked")
    ACTIVE_PLANNED_WORK_STATUSES = ("pending", "due", "snoozed")
    ACTIVE_MILESTONE_STATUSES = ("active",)
    MEMORY_LAYER_EPISODIC: MemoryLayerKind = "episodic"
    MEMORY_LAYER_SEMANTIC: MemoryLayerKind = "semantic"
    MEMORY_LAYER_AFFECTIVE: MemoryLayerKind = "affective"
    MEMORY_LAYER_OPERATIONAL: MemoryLayerKind = "operational"
    SEMANTIC_SOURCE_KINDS = frozenset({"episodic", "semantic", "affective", "relation"})
    AFFECTIVE_CONCLUSION_KINDS = frozenset({"affective_support_pattern", "affective_support_sensitivity"})
    RELATION_CONFIDENCE_THRESHOLD = 0.65
    RELATION_EXPIRATION_CONFIDENCE = 0.12
    RELATION_DECAY_EVIDENCE_WEIGHT = 0.35
    RELATION_DECAY_EVIDENCE_CAP = 4.0
    RELATION_REFRESH_EVIDENCE_CAP = 64
    OPERATIONAL_CONCLUSION_KINDS = frozenset(
        {
            "response_style",
            "preferred_role",
            "collaboration_preference",
            "proactive_opt_in",
            "telegram_enabled",
            "clickup_enabled",
            "google_calendar_enabled",
            "google_drive_enabled",
            "goal_execution_state",
            "goal_progress_score",
            "goal_progress_trend",
            "goal_progress_arc",
            "goal_milestone_transition",
            "goal_milestone_state",
            "goal_milestone_arc",
            "goal_milestone_pressure",
            "goal_milestone_dependency_state",
            "goal_milestone_due_state",
            "goal_milestone_due_window",
            "goal_milestone_risk",
            "goal_completion_criteria",
            "proactive_outreach_state",
            "proactive_outreach_trigger",
        }
    )
    USER_MANAGED_OPERATIONAL_CONCLUSION_KINDS = frozenset(
        {
            "proactive_opt_in",
            "telegram_enabled",
            "clickup_enabled",
            "google_calendar_enabled",
            "google_drive_enabled",
        }
    )
    RUNTIME_RESET_USER_SCOPED_MODELS = (
        ("memory", AionMemory),
        ("semantic_embeddings", AionSemanticEmbedding),
        ("relations", AionRelation),
        ("theta", AionTheta),
        ("goals", AionGoal),
        ("tasks", AionTask),
        ("planned_work_items", AionPlannedWorkItem),
        ("goal_progress_entries", AionGoalProgress),
        ("goal_milestones", AionGoalMilestone),
        ("goal_milestone_history_entries", AionGoalMilestoneHistory),
        ("attention_turns", AionAttentionTurn),
        ("reflection_tasks", AionReflectionTask),
        ("subconscious_proposals", AionSubconsciousProposal),
    )
    GLOBAL_SCOPE_TYPE = GLOBAL_SCOPE_TYPE
    GLOBAL_SCOPE_KEY = GLOBAL_SCOPE_KEY
    PROACTIVE_OPT_IN_TRUTHY = frozenset({"1", "true", "yes", "on"})
    PLANNED_WORK_KINDS = frozenset({"follow_up", "check_in", "reminder", "routine", "research_window"})
    PLANNED_WORK_STATUSES = frozenset({"pending", "due", "snoozed", "completed", "cancelled"})
    PLANNED_WORK_RECURRENCE_MODES = frozenset({"none", "daily", "weekly", "custom"})
    PLANNED_WORK_CHANNELS = frozenset({"telegram", "api", "none"})
    PLANNED_WORK_PROVENANCE = frozenset({"explicit_user_request", "planning_inference", "reflection_inference"})

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        *,
        embedding_provider: str = "deterministic",
        embedding_model: str = "deterministic-v1",
        embedding_dimensions: int = 32,
        embedding_source_kinds: tuple[str, ...] | None = None,
        embedding_refresh_mode: str = "on_write",
        openai_api_key: str | None = None,
        openai_embedding_client: OpenAIEmbeddingClient | None = None,
    ):
        self.session_factory = session_factory
        self.embedding_dimensions = max(1, int(embedding_dimensions))
        self.embedding_refresh_mode = normalize_embedding_refresh_mode(embedding_refresh_mode)
        self.openai_embedding_client = openai_embedding_client
        if self.openai_embedding_client is None and str(openai_api_key or "").strip():
            self.openai_embedding_client = OpenAIEmbeddingClient(api_key=openai_api_key)
        if embedding_source_kinds is None:
            self.embedding_source_kinds = set(normalize_embedding_source_kinds(None))
        else:
            self.embedding_source_kinds = {str(item).strip().lower() for item in embedding_source_kinds if str(item).strip()}
        self.embedding_posture = resolve_embedding_posture(
            provider=embedding_provider,
            model=embedding_model,
            openai_api_key=openai_api_key,
        )

    async def create_tables(self, engine: AsyncEngine) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def memory_layer_vocabulary(self) -> tuple[MemoryLayerKind, ...]:
        return (
            self.MEMORY_LAYER_EPISODIC,
            self.MEMORY_LAYER_SEMANTIC,
            self.MEMORY_LAYER_AFFECTIVE,
            self.MEMORY_LAYER_OPERATIONAL,
        )

    def conclusion_memory_layer(self, kind: str) -> MemoryLayerKind:
        normalized_kind = str(kind).strip().lower()
        if normalized_kind in self.AFFECTIVE_CONCLUSION_KINDS:
            return self.MEMORY_LAYER_AFFECTIVE
        if normalized_kind in self.OPERATIONAL_CONCLUSION_KINDS:
            return self.MEMORY_LAYER_OPERATIONAL
        return self.MEMORY_LAYER_SEMANTIC

    @staticmethod
    def _merge_unique_values(
        primary_values: list[str] | None,
        secondary_values: list[str] | None,
    ) -> list[str]:
        merged: list[str] = []
        seen: set[str] = set()
        for values in (primary_values or [], secondary_values or []):
            for value in values:
                normalized = str(value or "").strip()
                if not normalized or normalized in seen:
                    continue
                seen.add(normalized)
                merged.append(normalized)
        return merged

    async def _reassign_user_rows(
        self,
        session: AsyncSession,
        *,
        model: type,
        source_user_id: str,
        target_user_id: str,
    ) -> None:
        statement = select(model).where(model.user_id == source_user_id)
        result = await session.execute(statement)
        for row in result.scalars().all():
            row.user_id = target_user_id

    async def _merge_profile_identity_state(
        self,
        session: AsyncSession,
        *,
        source_user_id: str,
        target_user_id: str,
    ) -> None:
        source_row = await session.get(AionProfile, source_user_id)
        if source_row is None:
            return
        target_row = await session.get(AionProfile, target_user_id)
        if target_row is None:
            target_row = AionProfile(
                user_id=target_user_id,
                preferred_language="en",
                ui_language="system",
                utc_offset=DEFAULT_UTC_OFFSET,
                language_confidence=0.0,
                language_source="default",
            )
            session.add(target_row)
            await session.flush()

        if (
            float(source_row.language_confidence or 0.0) > float(target_row.language_confidence or 0.0)
            or str(target_row.language_source or "default").strip() == "default"
        ):
            target_row.preferred_language = source_row.preferred_language
            target_row.language_confidence = source_row.language_confidence
            target_row.language_source = source_row.language_source
        if str(target_row.ui_language or "system").strip() == "system" and str(source_row.ui_language or "").strip():
            target_row.ui_language = source_row.ui_language
        if normalize_utc_offset(target_row.utc_offset) == DEFAULT_UTC_OFFSET:
            target_row.utc_offset = normalize_utc_offset(source_row.utc_offset)
        await session.delete(source_row)

    async def _merge_theta_state(
        self,
        session: AsyncSession,
        *,
        source_user_id: str,
        target_user_id: str,
    ) -> None:
        source_row = await session.get(AionTheta, source_user_id)
        if source_row is None:
            return
        target_row = await session.get(AionTheta, target_user_id)
        if target_row is None:
            source_row.user_id = target_user_id
            return
        for field_name in ("support_bias", "analysis_bias", "execution_bias"):
            source_value = float(getattr(source_row, field_name, 0.0) or 0.0)
            target_value = float(getattr(target_row, field_name, 0.0) or 0.0)
            if abs(source_value) > abs(target_value):
                setattr(target_row, field_name, source_value)
        await session.delete(source_row)

    async def _merge_conclusion_rows(
        self,
        session: AsyncSession,
        *,
        source_user_id: str,
        target_user_id: str,
    ) -> None:
        statement = select(AionConclusion).where(AionConclusion.user_id == source_user_id)
        result = await session.execute(statement)
        for source_row in result.scalars().all():
            target_statement = (
                select(AionConclusion)
                .where(
                    AionConclusion.user_id == target_user_id,
                    AionConclusion.kind == source_row.kind,
                    AionConclusion.scope_type == source_row.scope_type,
                    AionConclusion.scope_key == source_row.scope_key,
                )
                .limit(1)
            )
            target_result = await session.execute(target_statement)
            target_row = target_result.scalar_one_or_none()
            if target_row is None:
                source_row.user_id = target_user_id
                continue
            current_content = target_row.content
            current_confidence = float(target_row.confidence or 0.0)
            if self._should_update_conclusion(
                kind=source_row.kind,
                current_content=current_content,
                current_confidence=current_confidence,
                next_content=source_row.content,
                next_confidence=source_row.confidence,
                source=source_row.source,
            ):
                target_row.content = source_row.content
                target_row.confidence = self._next_conclusion_confidence(
                    current_content=current_content,
                    current_confidence=current_confidence,
                    next_content=source_row.content,
                    next_confidence=source_row.confidence,
                )
                target_row.source = source_row.source
                target_row.supporting_event_id = source_row.supporting_event_id
            await session.delete(source_row)

    async def _merge_relation_rows(
        self,
        session: AsyncSession,
        *,
        source_user_id: str,
        target_user_id: str,
    ) -> None:
        statement = select(AionRelation).where(AionRelation.user_id == source_user_id)
        result = await session.execute(statement)
        for source_row in result.scalars().all():
            target_statement = (
                select(AionRelation)
                .where(
                    AionRelation.user_id == target_user_id,
                    AionRelation.relation_type == source_row.relation_type,
                    AionRelation.scope_type == source_row.scope_type,
                    AionRelation.scope_key == source_row.scope_key,
                )
                .limit(1)
            )
            target_result = await session.execute(target_statement)
            target_row = target_result.scalar_one_or_none()
            if target_row is None:
                source_row.user_id = target_user_id
                continue
            if float(source_row.confidence or 0.0) >= float(target_row.confidence or 0.0):
                target_row.relation_value = source_row.relation_value
                target_row.source = source_row.source
                target_row.supporting_event_id = source_row.supporting_event_id
            target_row.confidence = max(float(target_row.confidence or 0.0), float(source_row.confidence or 0.0))
            target_row.evidence_count = int(target_row.evidence_count or 0) + int(source_row.evidence_count or 0)
            target_row.decay_rate = min(float(target_row.decay_rate or 0.02), float(source_row.decay_rate or 0.02))
            target_row.last_observed_at = max(target_row.last_observed_at, source_row.last_observed_at)
            await session.delete(source_row)

    async def _merge_embedding_rows(
        self,
        session: AsyncSession,
        *,
        source_user_id: str,
        target_user_id: str,
    ) -> None:
        statement = select(AionSemanticEmbedding).where(AionSemanticEmbedding.user_id == source_user_id)
        result = await session.execute(statement)
        for source_row in result.scalars().all():
            target_statement = (
                select(AionSemanticEmbedding)
                .where(
                    AionSemanticEmbedding.user_id == target_user_id,
                    AionSemanticEmbedding.source_kind == source_row.source_kind,
                    AionSemanticEmbedding.source_id == source_row.source_id,
                )
                .limit(1)
            )
            target_result = await session.execute(target_statement)
            target_row = target_result.scalar_one_or_none()
            if target_row is None:
                source_row.user_id = target_user_id
                continue
            if source_row.updated_at >= target_row.updated_at:
                target_row.source_event_id = source_row.source_event_id
                target_row.scope_type = source_row.scope_type
                target_row.scope_key = source_row.scope_key
                target_row.content = source_row.content
                target_row.embedding = source_row.embedding
                target_row.embedding_model = source_row.embedding_model
                target_row.embedding_dimensions = source_row.embedding_dimensions
                target_row.metadata_json = source_row.metadata_json
            await session.delete(source_row)

    async def _merge_attention_turn_rows(
        self,
        session: AsyncSession,
        *,
        source_user_id: str,
        target_user_id: str,
    ) -> None:
        statement = select(AionAttentionTurn).where(AionAttentionTurn.user_id == source_user_id)
        result = await session.execute(statement)
        for source_row in result.scalars().all():
            target_statement = (
                select(AionAttentionTurn)
                .where(
                    AionAttentionTurn.user_id == target_user_id,
                    AionAttentionTurn.conversation_key == source_row.conversation_key,
                )
                .limit(1)
            )
            target_result = await session.execute(target_statement)
            target_row = target_result.scalar_one_or_none()
            if target_row is None:
                source_row.user_id = target_user_id
                continue
            target_row.messages_json = self._merge_unique_values(target_row.messages_json, source_row.messages_json)
            target_row.event_ids_json = self._merge_unique_values(target_row.event_ids_json, source_row.event_ids_json)
            target_row.update_keys_json = self._merge_unique_values(target_row.update_keys_json, source_row.update_keys_json)
            target_row.source_count = max(
                int(target_row.source_count or 0),
                int(source_row.source_count or 0),
                len(target_row.messages_json or []),
            )
            if source_row.updated_at >= target_row.updated_at:
                target_row.turn_id = source_row.turn_id
                target_row.status = source_row.status
                target_row.owner_mode = source_row.owner_mode
                if source_row.assembled_text:
                    target_row.assembled_text = source_row.assembled_text
            elif not target_row.assembled_text and source_row.assembled_text:
                target_row.assembled_text = source_row.assembled_text
            await session.delete(source_row)

    async def _merge_legacy_telegram_user_state(
        self,
        session: AsyncSession,
        *,
        source_user_id: str,
        target_user_id: str,
    ) -> None:
        normalized_source_user_id = str(source_user_id or "").strip()
        normalized_target_user_id = str(target_user_id or "").strip()
        if (
            not normalized_source_user_id
            or not normalized_target_user_id
            or normalized_source_user_id == normalized_target_user_id
            or not normalized_source_user_id.isdigit()
        ):
            return
        if await session.get(AionAuthUser, normalized_source_user_id) is not None:
            return

        await self._merge_profile_identity_state(
            session,
            source_user_id=normalized_source_user_id,
            target_user_id=normalized_target_user_id,
        )
        await self._merge_theta_state(
            session,
            source_user_id=normalized_source_user_id,
            target_user_id=normalized_target_user_id,
        )
        await self._merge_conclusion_rows(
            session,
            source_user_id=normalized_source_user_id,
            target_user_id=normalized_target_user_id,
        )
        await self._merge_relation_rows(
            session,
            source_user_id=normalized_source_user_id,
            target_user_id=normalized_target_user_id,
        )
        await self._merge_embedding_rows(
            session,
            source_user_id=normalized_source_user_id,
            target_user_id=normalized_target_user_id,
        )
        await self._merge_attention_turn_rows(
            session,
            source_user_id=normalized_source_user_id,
            target_user_id=normalized_target_user_id,
        )
        for model in (
            AionMemory,
            AionGoal,
            AionTask,
            AionPlannedWorkItem,
            AionGoalProgress,
            AionGoalMilestone,
            AionGoalMilestoneHistory,
            AionReflectionTask,
            AionSubconsciousProposal,
        ):
            await self._reassign_user_rows(
                session,
                model=model,
                source_user_id=normalized_source_user_id,
                target_user_id=normalized_target_user_id,
            )

    async def get_recent_episodic_memory(self, user_id: str, limit: int = 5) -> list[dict]:
        return await self.get_recent_for_user(user_id=user_id, limit=limit)

    async def get_conclusions_for_layer(
        self,
        *,
        user_id: str,
        layer: MemoryLayerKind,
        limit: int = 5,
        scope_type: str | None = None,
        scope_key: str | None = None,
        include_global: bool = False,
    ) -> list[dict]:
        if layer not in {
            self.MEMORY_LAYER_SEMANTIC,
            self.MEMORY_LAYER_AFFECTIVE,
            self.MEMORY_LAYER_OPERATIONAL,
        }:
            return []

        rows = await self.get_user_conclusions(
            user_id=user_id,
            limit=max(limit * 3, limit),
            scope_type=scope_type,
            scope_key=scope_key,
            include_global=include_global,
        )
        filtered = [item for item in rows if self.conclusion_memory_layer(str(item.get("kind", ""))) == layer]
        return filtered[:limit]

    async def get_operational_memory_view(
        self,
        *,
        user_id: str,
        scope_type: str | None = None,
        scope_key: str | None = None,
        include_global: bool = True,
    ) -> dict:
        return await self.get_user_runtime_preferences(
            user_id=user_id,
            scope_type=scope_type,
            scope_key=scope_key,
            include_global=include_global,
        )

    async def upsert_relation(
        self,
        *,
        user_id: str,
        relation_type: str,
        relation_value: str,
        confidence: float,
        source: str,
        supporting_event_id: str | None = None,
        scope_type: str | None = None,
        scope_key: str | None = None,
        evidence_count: int = 1,
        decay_rate: float = 0.02,
    ) -> dict:
        normalized_scope_type, normalized_scope_key = canonicalize_relation_scope(
            relation_type=relation_type,
            scope_type=scope_type,
            scope_key=scope_key,
        )
        normalized_relation_type = str(relation_type).strip().lower()[:32]
        normalized_relation_value = str(relation_value).strip().lower()[:128]
        normalized_confidence = max(0.0, min(1.0, float(confidence)))
        normalized_source = str(source or "background_reflection").strip().lower()[:32] or "background_reflection"
        normalized_evidence_count = max(1, int(evidence_count))
        normalized_decay_rate = max(0.0, min(1.0, float(decay_rate)))
        now = datetime.now(timezone.utc)
        async with self.session_factory() as session:
            statement = (
                select(AionRelation)
                .where(
                    AionRelation.user_id == user_id,
                    AionRelation.relation_type == normalized_relation_type,
                    AionRelation.scope_type == normalized_scope_type,
                    AionRelation.scope_key == normalized_scope_key,
                )
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()

            if row is None:
                row = AionRelation(
                    user_id=user_id,
                    relation_type=normalized_relation_type,
                    relation_value=normalized_relation_value,
                    confidence=normalized_confidence,
                    source=normalized_source,
                    supporting_event_id=supporting_event_id,
                    scope_type=normalized_scope_type,
                    scope_key=normalized_scope_key,
                    evidence_count=normalized_evidence_count,
                    decay_rate=normalized_decay_rate,
                    last_observed_at=now,
                )
                session.add(row)
            else:
                current_effective_confidence = self._revalidated_relation_confidence(row=row, now=now)
                current_evidence_count = max(1, int(row.evidence_count or 1))
                combined_evidence_count = min(
                    self.RELATION_REFRESH_EVIDENCE_CAP,
                    current_evidence_count + normalized_evidence_count,
                )
                previous_relation_value = str(row.relation_value).strip().lower()
                row.relation_value = normalized_relation_value
                row.confidence = normalized_confidence
                if previous_relation_value == normalized_relation_value:
                    weighted_confidence = (
                        (current_effective_confidence * current_evidence_count)
                        + (normalized_confidence * normalized_evidence_count)
                    ) / float(max(1, current_evidence_count + normalized_evidence_count))
                    if normalized_confidence >= current_effective_confidence:
                        weighted_confidence = min(
                            1.0,
                            weighted_confidence + min(0.04, 0.005 * normalized_evidence_count),
                        )
                    row.confidence = max(0.0, min(1.0, weighted_confidence))
                    row.evidence_count = combined_evidence_count
                    row.decay_rate = self._blended_decay_rate(
                        current_decay_rate=float(row.decay_rate or normalized_decay_rate),
                        incoming_decay_rate=normalized_decay_rate,
                        incoming_evidence_count=normalized_evidence_count,
                    )
                else:
                    row.evidence_count = normalized_evidence_count
                    row.decay_rate = normalized_decay_rate
                row.source = normalized_source
                row.supporting_event_id = supporting_event_id
                row.last_observed_at = now

            await session.commit()
            await session.refresh(row)

        if "relation" in self.embedding_source_kinds:
            relation_content = f"{row.relation_type} {row.relation_value}".strip()
            relation_embedding, relation_embedding_status = await self._materialize_embedding(
                content=relation_content
            )
            await self.upsert_semantic_embedding(
                user_id=row.user_id,
                source_kind="relation",
                source_id=f"relation:{row.id}",
                source_event_id=row.supporting_event_id,
                scope_type=row.scope_type,
                scope_key=row.scope_key,
                content=relation_content,
                embedding=relation_embedding,
                embedding_model=self.embedding_posture["model_effective"],
                embedding_dimensions=self.embedding_dimensions,
                metadata={
                    "relation_type": row.relation_type,
                    "relation_value": row.relation_value,
                    "confidence": row.confidence,
                    "source": row.source,
                    "evidence_count": row.evidence_count,
                    "decay_rate": row.decay_rate,
                    "embedding_status": relation_embedding_status,
                    "embedding_refresh_mode": self.embedding_refresh_mode,
                    "embedding_provider_requested": self.embedding_posture["provider_requested"],
                    "embedding_provider_effective": self.embedding_posture["provider_effective"],
                    "embedding_provider_hint": self.embedding_posture["provider_hint"],
                    "embedding_model_requested": self.embedding_posture["model_requested"],
                    "embedding_model_effective": self.embedding_posture["model_effective"],
                },
            )

        return self._serialize_relation(row)

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
        where_clauses = [AionRelation.user_id == user_id]
        threshold = self.RELATION_CONFIDENCE_THRESHOLD if min_confidence is None else float(min_confidence)
        threshold = max(0.0, min(1.0, threshold))

        if scope_type is not None or scope_key is not None:
            normalized_scope_type, normalized_scope_key = self._normalize_conclusion_scope(
                scope_type=scope_type,
                scope_key=scope_key,
            )
            scoped_clause = and_(
                AionRelation.scope_type == normalized_scope_type,
                AionRelation.scope_key == normalized_scope_key,
            )
            if include_global and (
                normalized_scope_type != self.GLOBAL_SCOPE_TYPE
                or normalized_scope_key != self.GLOBAL_SCOPE_KEY
            ):
                where_clauses.append(
                    or_(
                        scoped_clause,
                        and_(
                            AionRelation.scope_type == self.GLOBAL_SCOPE_TYPE,
                            AionRelation.scope_key == self.GLOBAL_SCOPE_KEY,
                        ),
                    )
                )
            else:
                where_clauses.append(scoped_clause)

        async with self.session_factory() as session:
            statement = (
                select(AionRelation)
                .where(*where_clauses)
                .order_by(AionRelation.confidence.desc(), AionRelation.updated_at.desc(), AionRelation.id.desc())
                .limit(max(limit * 3, limit))
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        now = datetime.now(timezone.utc)
        revalidated_rows: list[dict] = []
        for row in rows:
            revalidated = self._serialize_relation_with_revalidation(row=row, now=now)
            if revalidated is None:
                continue
            if not relation_matches_scope_request(
                relation_type=str(revalidated.get("relation_type", "")),
                row_scope_type=str(revalidated.get("scope_type") or self.GLOBAL_SCOPE_TYPE),
                row_scope_key=str(revalidated.get("scope_key") or self.GLOBAL_SCOPE_KEY),
                requested_scope_type=scope_type,
                requested_scope_key=scope_key,
                include_global=include_global,
            ):
                continue
            if float(revalidated.get("confidence", 0.0) or 0.0) < threshold:
                continue
            revalidated_rows.append(revalidated)

        sorted_rows = sorted(
            revalidated_rows,
            key=lambda item: (
                float(item.get("confidence", 0.0) or 0.0),
                str(item.get("updated_at", "")),
                int(item.get("id", 0) or 0),
            ),
            reverse=True,
        )
        return sorted_rows[:limit]

    async def upsert_semantic_embedding(
        self,
        *,
        user_id: str,
        source_kind: str,
        source_id: str,
        content: str,
        embedding: list[float] | None,
        embedding_model: str,
        embedding_dimensions: int,
        source_event_id: str | None = None,
        scope_type: str | None = None,
        scope_key: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        normalized_source_kind = str(source_kind).strip().lower()
        if normalized_source_kind not in self.SEMANTIC_SOURCE_KINDS:
            normalized_source_kind = "semantic"
        normalized_scope_type, normalized_scope_key = self._normalize_conclusion_scope(
            scope_type=scope_type,
            scope_key=scope_key,
        )
        async with self.session_factory() as session:
            statement = (
                select(AionSemanticEmbedding)
                .where(
                    AionSemanticEmbedding.user_id == user_id,
                    AionSemanticEmbedding.source_kind == normalized_source_kind,
                    AionSemanticEmbedding.source_id == source_id,
                )
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()

            if row is None:
                row = AionSemanticEmbedding(
                    user_id=user_id,
                    source_kind=normalized_source_kind,
                    source_id=source_id[:96],
                    source_event_id=source_event_id,
                    scope_type=normalized_scope_type,
                    scope_key=normalized_scope_key,
                    content=content[:5000],
                    embedding=embedding,
                    embedding_model=embedding_model[:64],
                    embedding_dimensions=max(1, int(embedding_dimensions)),
                    metadata_json=metadata,
                )
                session.add(row)
            else:
                row.source_event_id = source_event_id
                row.scope_type = normalized_scope_type
                row.scope_key = normalized_scope_key
                row.content = content[:5000]
                row.embedding = embedding
                row.embedding_model = embedding_model[:64]
                row.embedding_dimensions = max(1, int(embedding_dimensions))
                row.metadata_json = metadata

            await session.commit()
            await session.refresh(row)

        return self._serialize_semantic_embedding(row)

    async def get_semantic_embeddings(
        self,
        *,
        user_id: str,
        source_kinds: list[str] | None = None,
        scope_type: str | None = None,
        scope_key: str | None = None,
        include_global: bool = True,
        limit: int = 32,
    ) -> list[dict]:
        where_clauses = [AionSemanticEmbedding.user_id == user_id]
        normalized_source_kinds = [
            str(kind).strip().lower()
            for kind in (source_kinds or [])
            if str(kind).strip().lower() in self.SEMANTIC_SOURCE_KINDS
        ]
        if normalized_source_kinds:
            where_clauses.append(AionSemanticEmbedding.source_kind.in_(normalized_source_kinds))

        if scope_type is not None or scope_key is not None:
            normalized_scope_type, normalized_scope_key = self._normalize_conclusion_scope(
                scope_type=scope_type,
                scope_key=scope_key,
            )
            scoped_clause = and_(
                AionSemanticEmbedding.scope_type == normalized_scope_type,
                AionSemanticEmbedding.scope_key == normalized_scope_key,
            )
            if include_global and (
                normalized_scope_type != self.GLOBAL_SCOPE_TYPE
                or normalized_scope_key != self.GLOBAL_SCOPE_KEY
            ):
                where_clauses.append(
                    or_(
                        scoped_clause,
                        and_(
                            AionSemanticEmbedding.scope_type == self.GLOBAL_SCOPE_TYPE,
                            AionSemanticEmbedding.scope_key == self.GLOBAL_SCOPE_KEY,
                        ),
                    )
                )
            else:
                where_clauses.append(scoped_clause)

        async with self.session_factory() as session:
            statement = (
                select(AionSemanticEmbedding)
                .where(*where_clauses)
                .order_by(AionSemanticEmbedding.updated_at.desc(), AionSemanticEmbedding.id.desc())
                .limit(limit)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        return [self._serialize_semantic_embedding(row) for row in rows]

    async def query_semantic_similarity(
        self,
        *,
        user_id: str,
        query_embedding: list[float],
        source_kinds: list[str] | None = None,
        scope_type: str | None = None,
        scope_key: str | None = None,
        include_global: bool = True,
        limit: int = 8,
    ) -> list[dict]:
        if not query_embedding:
            return []

        candidates = await self.get_semantic_embeddings(
            user_id=user_id,
            source_kinds=source_kinds,
            scope_type=scope_type,
            scope_key=scope_key,
            include_global=include_global,
            limit=max(limit * 4, limit),
        )
        scored: list[tuple[dict, float]] = []
        for item in candidates:
            embedding = item.get("embedding")
            if not isinstance(embedding, list) or not embedding:
                continue
            score = cosine_similarity(
                [float(value) for value in query_embedding],
                [float(value) for value in embedding],
            )
            scored.append((item, score))

        ranked = sorted(
            scored,
            key=lambda pair: (pair[1], str(pair[0].get("updated_at", ""))),
            reverse=True,
        )
        return [
            {
                **item,
                "similarity": round(float(score), 6),
            }
            for item, score in ranked[:limit]
        ]

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
        episodic_candidates = await self.get_recent_for_user(
            user_id=user_id,
            limit=max(episodic_limit * 2, episodic_limit),
        )
        conclusion_candidates = await self.get_user_conclusions(
            user_id=user_id,
            limit=max(conclusion_limit * 3, conclusion_limit),
            scope_type=scope_type,
            scope_key=scope_key,
            include_global=include_global,
        )
        affective_conclusions = [
            item
            for item in conclusion_candidates
            if self.conclusion_memory_layer(str(item.get("kind", ""))) == self.MEMORY_LAYER_AFFECTIVE
        ]
        semantic_conclusions = [
            item
            for item in conclusion_candidates
            if self.conclusion_memory_layer(str(item.get("kind", ""))) == self.MEMORY_LAYER_SEMANTIC
        ]

        query_tokens = self._hybrid_tokens(query_text)
        episodic_scored = sorted(
            (
                (
                    item,
                    self._hybrid_episodic_score(item=item, query_tokens=query_tokens),
                )
                for item in episodic_candidates
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )
        episodic = [item for item, _ in episodic_scored[:episodic_limit]]
        lexical_hit_count = len([score for _, score in episodic_scored if score > 0.0])

        vector_hits: list[dict] = []
        if query_embedding:
            vector_hits = await self.query_semantic_similarity(
                user_id=user_id,
                query_embedding=query_embedding,
                source_kinds=foreground_retrieval_source_kinds(
                    enabled_source_kinds=self.embedding_source_kinds
                ),
                scope_type=scope_type,
                scope_key=scope_key,
                include_global=include_global,
                limit=conclusion_limit,
            )

        vector_by_kind_content = {
            (
                str(hit.get("source_kind", "")),
                str(hit.get("content", "")).strip().lower(),
            ): float(hit.get("similarity", 0.0) or 0.0)
            for hit in vector_hits
        }
        semantic_scored = sorted(
            (
                (
                    item,
                    self._hybrid_semantic_score(
                        item=item,
                        query_tokens=query_tokens,
                        vector_similarity=vector_by_kind_content.get(
                            ("semantic", str(item.get("content", "")).strip().lower()),
                            0.0,
                        ),
                    ),
                )
                for item in semantic_conclusions
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )
        affective_scored = sorted(
            (
                (
                    item,
                    self._hybrid_semantic_score(
                        item=item,
                        query_tokens=query_tokens,
                        vector_similarity=vector_by_kind_content.get(
                            ("affective", str(item.get("content", "")).strip().lower()),
                            0.0,
                        ),
                    ),
                )
                for item in affective_conclusions
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )

        semantic = [item for item, _ in semantic_scored[:conclusion_limit]]
        affective = [item for item, _ in affective_scored[:conclusion_limit]]
        return {
            "episodic": episodic,
            "semantic": semantic,
            "affective": affective,
            "diagnostics": {
                "query_tokens": len(query_tokens),
                "episodic_candidates": len(episodic_candidates),
                "semantic_candidates": len(semantic_conclusions),
                "affective_candidates": len(affective_conclusions),
                "episodic_lexical_hits": lexical_hit_count,
                "vector_hits": len(vector_hits),
                "semantic_selected": len(semantic),
                "affective_selected": len(affective),
            },
        }

    async def write_episode(
        self,
        event_id: str,
        trace_id: str,
        source: str,
        user_id: str,
        event_timestamp: datetime,
        summary: str,
        payload: dict | None,
        importance: float,
    ) -> dict:
        async with self.session_factory() as session:
            row = AionMemory(
                event_id=event_id,
                trace_id=trace_id,
                source=source,
                user_id=user_id,
                event_timestamp=event_timestamp,
                summary=summary,
                payload=payload,
                importance=importance,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)

        return self._serialize_memory(row)

    async def get_recent_for_user(self, user_id: str, limit: int = 5, offset: int = 0) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionMemory)
                .where(AionMemory.user_id == user_id)
                .order_by(AionMemory.id.desc())
                .offset(max(0, int(offset)))
                .limit(limit)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        return [
            {
                **self._serialize_memory(row),
                "event_timestamp": row.event_timestamp,
            }
            for row in rows
        ]

    async def get_recent_chat_transcript_for_user(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        normalized_limit = max(1, int(limit))
        batch_size = max(normalized_limit, 10)
        offset = 0
        transcript_items: list[dict[str, Any]] = []

        while len(transcript_items) < normalized_limit:
            batch = await self.get_recent_for_user(user_id=user_id, limit=batch_size, offset=offset)
            if not batch:
                break
            for memory_item in batch:
                transcript_items.extend(self._project_memory_to_transcript_items(memory_item))
            offset += len(batch)
            if len(batch) < batch_size:
                break

        transcript_items.sort(
            key=lambda item: (self._coerce_datetime(item.get("timestamp")) or datetime.min.replace(tzinfo=timezone.utc))
        )
        if len(transcript_items) > normalized_limit:
            transcript_items = transcript_items[-normalized_limit:]
        return transcript_items

    async def get_proactive_scheduler_candidates(
        self,
        *,
        proactive_interval_seconds: int,
        limit: int = 8,
    ) -> list[dict]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(AionConclusion)
                .where(AionConclusion.kind == "proactive_opt_in")
                .order_by(AionConclusion.updated_at.desc(), AionConclusion.id.desc())
            )
            rows = result.scalars().all()

        opted_in_user_ids: list[str] = []
        seen_user_ids: set[str] = set()
        for row in rows:
            value = str(row.content or "").strip().lower()
            if value not in self.PROACTIVE_OPT_IN_TRUTHY:
                continue
            if row.user_id in seen_user_ids:
                continue
            seen_user_ids.add(row.user_id)
            opted_in_user_ids.append(str(row.user_id))

        candidates: list[dict] = []
        for user_id in opted_in_user_ids:
            if len(candidates) >= limit:
                break
            candidate = await self._build_proactive_scheduler_candidate(
                user_id=user_id,
                proactive_interval_seconds=proactive_interval_seconds,
            )
            if candidate is not None:
                candidates.append(candidate)
        return candidates

    async def get_user_profile(self, user_id: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionProfile, user_id)

        return self._serialize_profile(row)

    async def get_user_profile_by_telegram_link_code(self, link_code: str) -> dict | None:
        normalized_code = str(link_code or "").strip().upper()
        if not normalized_code:
            return None
        async with self.session_factory() as session:
            statement = (
                select(AionProfile)
                .where(AionProfile.telegram_link_code == normalized_code)
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()
        return self._serialize_profile(row)

    async def get_user_profile_by_telegram_chat_id(self, chat_id: str) -> dict | None:
        normalized_chat_id = str(chat_id or "").strip()
        if not normalized_chat_id:
            return None
        async with self.session_factory() as session:
            statement = (
                select(AionProfile)
                .where(AionProfile.telegram_chat_id == normalized_chat_id)
                .order_by(AionProfile.updated_at.desc())
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()
        return self._serialize_profile(row)

    async def get_user_profile_by_telegram_user_id(self, telegram_user_id: str) -> dict | None:
        normalized_telegram_user_id = str(telegram_user_id or "").strip()
        if not normalized_telegram_user_id:
            return None
        async with self.session_factory() as session:
            statement = (
                select(AionProfile)
                .where(AionProfile.telegram_user_id == normalized_telegram_user_id)
                .order_by(AionProfile.updated_at.desc())
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()
        return self._serialize_profile(row)

    async def get_auth_user_by_id(self, user_id: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionAuthUser, user_id)
        return self._serialize_auth_user(row)

    async def get_auth_user_by_email(self, email: str) -> dict | None:
        normalized_email = str(email or "").strip().lower()
        if not normalized_email:
            return None
        async with self.session_factory() as session:
            result = await session.execute(
                select(AionAuthUser)
                .where(AionAuthUser.email == normalized_email)
                .limit(1)
            )
            row = result.scalar_one_or_none()
        return self._serialize_auth_user(row)

    async def create_auth_user(
        self,
        *,
        user_id: str,
        email: str,
        password_hash: str,
        display_name: str | None = None,
    ) -> dict:
        normalized_email = str(email or "").strip().lower()
        normalized_display_name = str(display_name or "").strip() or None
        async with self.session_factory() as session:
            row = AionAuthUser(
                id=user_id,
                email=normalized_email,
                password_hash=password_hash,
                display_name=normalized_display_name,
                is_active=1,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)
        return self._serialize_auth_user(row) or {}

    async def update_auth_user(
        self,
        *,
        user_id: str,
        display_name: str | None = None,
        last_login_at: datetime | None = None,
        is_active: bool | None = None,
    ) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionAuthUser, user_id)
            if row is None:
                return None
            if display_name is not None:
                row.display_name = str(display_name).strip() or None
            if last_login_at is not None:
                row.last_login_at = self._coerce_datetime(last_login_at)
            if is_active is not None:
                row.is_active = 1 if is_active else 0
            await session.commit()
            await session.refresh(row)
        return self._serialize_auth_user(row)

    async def create_auth_session(
        self,
        *,
        session_id: str,
        user_id: str,
        session_token_hash: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> dict:
        normalized_expires_at = self._coerce_datetime(expires_at) or datetime.now(timezone.utc)
        async with self.session_factory() as session:
            row = AionAuthSession(
                id=session_id,
                user_id=user_id,
                session_token_hash=session_token_hash,
                expires_at=normalized_expires_at,
                user_agent=(str(user_agent or "").strip() or None),
                ip_address=(str(ip_address or "").strip() or None),
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)
        return self._serialize_auth_session(row) or {}

    async def get_auth_session_by_token_hash(self, session_token_hash: str) -> dict | None:
        normalized_hash = str(session_token_hash or "").strip()
        if not normalized_hash:
            return None
        async with self.session_factory() as session:
            result = await session.execute(
                select(AionAuthSession)
                .where(AionAuthSession.session_token_hash == normalized_hash)
                .limit(1)
            )
            row = result.scalar_one_or_none()
        return self._serialize_auth_session(row)

    async def revoke_auth_session(self, *, session_id: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionAuthSession, session_id)
            if row is None:
                return None
            row.revoked_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(row)
        return self._serialize_auth_session(row)

    async def touch_auth_session(self, *, session_id: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionAuthSession, session_id)
            if row is None:
                return None
            row.last_seen_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(row)
        return self._serialize_auth_session(row)

    async def reset_user_runtime_data(self, *, user_id: str) -> dict[str, object]:
        normalized_user_id = str(user_id or "").strip()
        if not normalized_user_id:
            raise ValueError("user_id is required for runtime reset.")

        async with self.session_factory() as session:
            deleted_counts = await self._delete_runtime_state_for_user(
                session,
                user_id=normalized_user_id,
            )
            deleted_counts["conclusions"] = await self._delete_non_preserved_conclusions_for_user(
                session,
                user_id=normalized_user_id,
            )
            revoked_session_count = await self._revoke_auth_sessions_for_user(
                session,
                user_id=normalized_user_id,
            )
            await session.commit()

        return self._runtime_reset_summary(
            scope="single_user_runtime_reset",
            target_user_id=normalized_user_id,
            deleted_counts=deleted_counts,
            revoked_session_count=revoked_session_count,
        )

    async def cleanup_runtime_data_preserving_auth(self) -> dict[str, object]:
        async with self.session_factory() as session:
            deleted_counts = await self._delete_runtime_state_for_all_users(session)
            deleted_counts["conclusions"] = await self._delete_all_non_preserved_conclusions(session)
            revoked_session_count = await self._revoke_all_auth_sessions(session)
            await session.commit()

        return self._runtime_reset_summary(
            scope="runtime_only_preserve_auth",
            target_user_id=None,
            deleted_counts=deleted_counts,
            revoked_session_count=revoked_session_count,
        )

    async def get_user_theta(self, user_id: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionTheta, user_id)

        if row is None:
            return None

        return {
            "user_id": row.user_id,
            "support_bias": row.support_bias,
            "analysis_bias": row.analysis_bias,
            "execution_bias": row.execution_bias,
            "updated_at": row.updated_at,
        }

    async def get_active_goals(self, user_id: str, limit: int = 5) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionGoal)
                .where(
                    AionGoal.user_id == user_id,
                    AionGoal.status.in_(self.ACTIVE_GOAL_STATUSES),
                )
                .order_by(AionGoal.updated_at.desc(), AionGoal.id.desc())
                .limit(limit)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        rows = sorted(
            rows,
            key=lambda row: (
                self._goal_priority_rank(row.priority),
                self._coerce_datetime(row.updated_at) or datetime.min.replace(tzinfo=timezone.utc),
                row.id,
            ),
            reverse=True,
        )
        return [self._serialize_goal(row) for row in rows[:limit]]

    async def get_active_tasks(
        self,
        user_id: str,
        *,
        goal_ids: list[int] | None = None,
        limit: int = 5,
    ) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionTask)
                .where(
                    AionTask.user_id == user_id,
                    AionTask.status.in_(self.ACTIVE_TASK_STATUSES),
                )
                .order_by(AionTask.updated_at.desc(), AionTask.id.desc())
                .limit(max(limit * 2, limit))
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        goal_id_set = {goal_id for goal_id in (goal_ids or []) if goal_id is not None}
        if goal_id_set:
            goal_linked = [row for row in rows if row.goal_id in goal_id_set]
            unlinked = [row for row in rows if row.goal_id not in goal_id_set]
            rows = goal_linked + unlinked

        rows = sorted(
            rows,
            key=lambda row: (
                self._task_status_rank(row.status),
                self._task_priority_rank(row.priority),
                self._coerce_datetime(row.updated_at) or datetime.min.replace(tzinfo=timezone.utc),
                row.id,
            ),
            reverse=True,
        )
        return [self._serialize_task(row) for row in rows[:limit]]

    async def get_active_planned_work(
        self,
        user_id: str,
        *,
        goal_ids: list[int] | None = None,
        task_ids: list[int] | None = None,
        limit: int = 8,
    ) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionPlannedWorkItem)
                .where(
                    AionPlannedWorkItem.user_id == user_id,
                    AionPlannedWorkItem.status.in_(self.ACTIVE_PLANNED_WORK_STATUSES),
                )
                .order_by(
                    AionPlannedWorkItem.preferred_at.asc(),
                    AionPlannedWorkItem.not_before.asc(),
                    AionPlannedWorkItem.updated_at.desc(),
                    AionPlannedWorkItem.id.desc(),
                )
                .limit(max(limit * 2, limit))
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        goal_id_set = {goal_id for goal_id in (goal_ids or []) if goal_id is not None}
        task_id_set = {task_id for task_id in (task_ids or []) if task_id is not None}
        if goal_id_set:
            linked_goal_rows = [row for row in rows if row.goal_id in goal_id_set]
            rows = linked_goal_rows + [row for row in rows if row.goal_id not in goal_id_set]
        if task_id_set:
            linked_task_rows = [row for row in rows if row.task_id in task_id_set]
            rows = linked_task_rows + [row for row in rows if row.task_id not in task_id_set]

        def _planned_work_sort_key(row: AionPlannedWorkItem) -> tuple[datetime, datetime, datetime, int]:
            max_dt = datetime.max.replace(tzinfo=timezone.utc)
            preferred_at = self._coerce_datetime(row.preferred_at) or max_dt
            not_before = self._coerce_datetime(row.not_before) or max_dt
            updated_at = self._coerce_datetime(row.updated_at) or datetime.min.replace(tzinfo=timezone.utc)
            return preferred_at, not_before, updated_at, int(row.id or 0)

        rows = sorted(rows, key=_planned_work_sort_key)
        return [self._serialize_planned_work(row) for row in rows[:limit]]

    async def get_due_planned_work(
        self,
        *,
        now: datetime | None = None,
        limit: int = 8,
    ) -> list[dict]:
        due_at = self._coerce_datetime(now) or datetime.now(timezone.utc)
        async with self.session_factory() as session:
            statement = (
                select(AionPlannedWorkItem)
                .where(
                    AionPlannedWorkItem.status.in_(("pending", "snoozed")),
                    (
                        (AionPlannedWorkItem.preferred_at.is_not(None) & (AionPlannedWorkItem.preferred_at <= due_at))
                        | (
                            AionPlannedWorkItem.preferred_at.is_(None)
                            & AionPlannedWorkItem.not_before.is_not(None)
                            & (AionPlannedWorkItem.not_before <= due_at)
                        )
                    ),
                )
                .order_by(
                    AionPlannedWorkItem.preferred_at.asc(),
                    AionPlannedWorkItem.not_before.asc(),
                    AionPlannedWorkItem.updated_at.asc(),
                    AionPlannedWorkItem.id.asc(),
                )
                .limit(limit)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        return [self._serialize_planned_work(row) for row in rows]

    async def get_recent_goal_progress(
        self,
        user_id: str,
        *,
        goal_ids: list[int] | None = None,
        limit: int = 6,
    ) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionGoalProgress)
                .where(AionGoalProgress.user_id == user_id)
                .order_by(AionGoalProgress.created_at.desc(), AionGoalProgress.id.desc())
                .limit(limit * 3)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        goal_id_set = {goal_id for goal_id in (goal_ids or []) if goal_id is not None}
        if goal_id_set:
            rows = [row for row in rows if int(row.goal_id) in goal_id_set]

        return [self._serialize_goal_progress(row) for row in rows[:limit]]

    async def get_active_goal_milestones(
        self,
        user_id: str,
        *,
        goal_ids: list[int] | None = None,
        limit: int = 6,
    ) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionGoalMilestone)
                .where(
                    AionGoalMilestone.user_id == user_id,
                    AionGoalMilestone.status.in_(self.ACTIVE_MILESTONE_STATUSES),
                )
                .order_by(AionGoalMilestone.updated_at.desc(), AionGoalMilestone.id.desc())
                .limit(limit * 3)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        goal_id_set = {goal_id for goal_id in (goal_ids or []) if goal_id is not None}
        if goal_id_set:
            rows = [row for row in rows if int(row.goal_id) in goal_id_set]

        rows = sorted(
            rows,
            key=lambda row: (
                self._goal_milestone_phase_rank(row.phase),
                self._coerce_datetime(row.updated_at) or datetime.min.replace(tzinfo=timezone.utc),
                row.id,
            ),
            reverse=True,
        )
        return [self._serialize_goal_milestone(row) for row in rows[:limit]]

    async def get_recent_goal_milestone_history(
        self,
        user_id: str,
        *,
        goal_ids: list[int] | None = None,
        limit: int = 6,
    ) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionGoalMilestoneHistory)
                .where(AionGoalMilestoneHistory.user_id == user_id)
                .order_by(AionGoalMilestoneHistory.created_at.desc(), AionGoalMilestoneHistory.id.desc())
                .limit(limit * 3)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        goal_id_set = {goal_id for goal_id in (goal_ids or []) if goal_id is not None}
        if goal_id_set:
            rows = [row for row in rows if int(row.goal_id) in goal_id_set]

        return [self._serialize_goal_milestone_history(row) for row in rows[:limit]]

    async def upsert_active_goal(
        self,
        *,
        user_id: str,
        name: str,
        description: str,
        priority: str = "medium",
        goal_type: str = "tactical",
    ) -> dict:
        normalized_name = self._normalize_match_text(name)
        async with self.session_factory() as session:
            statement = (
                select(AionGoal)
                .where(
                    AionGoal.user_id == user_id,
                    AionGoal.status.in_(("active", "paused")),
                )
                .order_by(AionGoal.updated_at.desc(), AionGoal.id.desc())
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

            row = next(
                (
                    item
                    for item in rows
                    if self._normalize_match_text(item.name) == normalized_name
                ),
                None,
            )

            if row is None:
                row = AionGoal(
                    user_id=user_id,
                    name=name[:160],
                    description=description[:500],
                    priority=priority,
                    status="active",
                    goal_type=goal_type,
                )
                session.add(row)
            else:
                row.name = name[:160]
                row.description = description[:500]
                row.priority = priority
                row.status = "active"
                row.goal_type = goal_type

            await session.commit()
            await session.refresh(row)

        return self._serialize_goal(row)

    async def upsert_active_task(
        self,
        *,
        user_id: str,
        name: str,
        description: str,
        priority: str = "medium",
        goal_id: int | None = None,
        status: str = "todo",
    ) -> dict:
        normalized_name = self._normalize_match_text(name)
        async with self.session_factory() as session:
            statement = (
                select(AionTask)
                .where(
                    AionTask.user_id == user_id,
                    AionTask.status.in_(self.ACTIVE_TASK_STATUSES),
                )
                .order_by(AionTask.updated_at.desc(), AionTask.id.desc())
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

            row = next(
                (
                    item
                    for item in rows
                    if self._normalize_match_text(item.name) == normalized_name
                    and (goal_id is None or item.goal_id == goal_id or item.goal_id is None)
                ),
                None,
            )

            if row is None:
                row = AionTask(
                    user_id=user_id,
                    goal_id=goal_id,
                    name=name[:160],
                    description=description[:500],
                    priority=priority,
                    status=status,
                )
                session.add(row)
            else:
                row.goal_id = goal_id if goal_id is not None else row.goal_id
                row.name = name[:160]
                row.description = description[:500]
                row.priority = priority
                row.status = status

            await session.commit()
            await session.refresh(row)

        return self._serialize_task(row)

    async def upsert_planned_work_item(
        self,
        *,
        user_id: str,
        kind: str,
        summary: str,
        goal_id: int | None = None,
        task_id: int | None = None,
        not_before: datetime | None = None,
        preferred_at: datetime | None = None,
        expires_at: datetime | None = None,
        recurrence_mode: str = "none",
        recurrence_rule: str = "",
        delivery_channel: str = "none",
        requires_foreground_execution: bool = True,
        quiet_hours_policy: str = "respect_user_context",
        provenance: str = "explicit_user_request",
        source_event_id: str | None = None,
    ) -> dict:
        normalized_kind = str(kind).strip().lower()
        if normalized_kind not in self.PLANNED_WORK_KINDS:
            normalized_kind = "follow_up"
        normalized_summary = " ".join(str(summary or "").split())[:220]
        normalized_recurrence_mode = str(recurrence_mode or "none").strip().lower()
        if normalized_recurrence_mode not in self.PLANNED_WORK_RECURRENCE_MODES:
            normalized_recurrence_mode = "none"
        normalized_channel = str(delivery_channel or "none").strip().lower()
        if normalized_channel not in self.PLANNED_WORK_CHANNELS:
            normalized_channel = "none"
        normalized_provenance = str(provenance or "explicit_user_request").strip().lower()
        if normalized_provenance not in self.PLANNED_WORK_PROVENANCE:
            normalized_provenance = "explicit_user_request"
        normalized_quiet_hours_policy = " ".join(str(quiet_hours_policy or "respect_user_context").split())[:32]
        normalized_recurrence_rule = " ".join(str(recurrence_rule or "").split())[:120]
        normalized_source_event_id = str(source_event_id).strip()[:64] if source_event_id else None
        match_summary = self._normalize_match_text(normalized_summary)

        async with self.session_factory() as session:
            statement = (
                select(AionPlannedWorkItem)
                .where(
                    AionPlannedWorkItem.user_id == user_id,
                    AionPlannedWorkItem.status.in_(self.ACTIVE_PLANNED_WORK_STATUSES),
                )
                .order_by(AionPlannedWorkItem.updated_at.desc(), AionPlannedWorkItem.id.desc())
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

            row = next(
                (
                    item
                    for item in rows
                    if self._normalize_match_text(item.summary) == match_summary
                    and item.kind == normalized_kind
                    and (goal_id is None or item.goal_id == goal_id or item.goal_id is None)
                    and (task_id is None or item.task_id == task_id or item.task_id is None)
                ),
                None,
            )

            if row is None:
                row = AionPlannedWorkItem(
                    user_id=user_id,
                    goal_id=goal_id,
                    task_id=task_id,
                    kind=normalized_kind,
                    summary=normalized_summary,
                    status="pending",
                    not_before=self._coerce_datetime(not_before),
                    preferred_at=self._coerce_datetime(preferred_at),
                    expires_at=self._coerce_datetime(expires_at),
                    recurrence_mode=normalized_recurrence_mode,
                    recurrence_rule=normalized_recurrence_rule,
                    delivery_channel=normalized_channel,
                    requires_foreground_execution=1 if requires_foreground_execution else 0,
                    quiet_hours_policy=normalized_quiet_hours_policy,
                    provenance=normalized_provenance,
                    source_event_id=normalized_source_event_id,
                )
                session.add(row)
            else:
                row.goal_id = goal_id if goal_id is not None else row.goal_id
                row.task_id = task_id if task_id is not None else row.task_id
                row.kind = normalized_kind
                row.summary = normalized_summary
                row.status = "pending"
                row.not_before = self._coerce_datetime(not_before)
                row.preferred_at = self._coerce_datetime(preferred_at)
                row.expires_at = self._coerce_datetime(expires_at)
                row.recurrence_mode = normalized_recurrence_mode
                row.recurrence_rule = normalized_recurrence_rule
                row.delivery_channel = normalized_channel
                row.requires_foreground_execution = 1 if requires_foreground_execution else 0
                row.quiet_hours_policy = normalized_quiet_hours_policy
                row.provenance = normalized_provenance
                row.source_event_id = normalized_source_event_id

            await session.commit()
            await session.refresh(row)

        return self._serialize_planned_work(row)

    async def reschedule_planned_work_item(
        self,
        *,
        work_id: int,
        not_before: datetime | None = None,
        preferred_at: datetime | None = None,
        expires_at: datetime | None = None,
    ) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionPlannedWorkItem, work_id)
            if row is None:
                return None
            row.status = "pending"
            row.not_before = self._coerce_datetime(not_before)
            row.preferred_at = self._coerce_datetime(preferred_at)
            row.expires_at = self._coerce_datetime(expires_at)
            await session.commit()
            await session.refresh(row)

        return self._serialize_planned_work(row)

    async def snooze_planned_work_item(
        self,
        *,
        work_id: int,
        until_at: datetime,
        evaluated_at: datetime | None = None,
    ) -> dict | None:
        snooze_until = self._coerce_datetime(until_at)
        if snooze_until is None:
            return None
        async with self.session_factory() as session:
            row = await session.get(AionPlannedWorkItem, work_id)
            if row is None:
                return None
            if row.status in {"completed", "cancelled"}:
                return self._serialize_planned_work(row)
            row.status = "snoozed"
            row.not_before = snooze_until
            row.preferred_at = snooze_until
            row.last_evaluated_at = self._coerce_datetime(evaluated_at) or datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(row)

        return self._serialize_planned_work(row)

    async def advance_planned_work_recurrence(
        self,
        *,
        work_id: int,
        evaluated_at: datetime | None = None,
    ) -> dict | None:
        effective_now = self._coerce_datetime(evaluated_at) or datetime.now(timezone.utc)
        async with self.session_factory() as session:
            row = await session.get(AionPlannedWorkItem, work_id)
            if row is None:
                return None
            if row.status == "cancelled":
                return self._serialize_planned_work(row)
            next_preferred_at = self._next_recurrence_at(row=row, evaluated_at=effective_now)
            if next_preferred_at is None:
                return self._serialize_planned_work(row)
            current_anchor = self._coerce_datetime(row.preferred_at) or self._coerce_datetime(row.not_before) or effective_now
            expiry_offset = None
            if row.expires_at is not None:
                expires_at = self._coerce_datetime(row.expires_at)
                if expires_at is not None:
                    expiry_offset = expires_at - current_anchor
            row.status = "pending"
            row.not_before = next_preferred_at
            row.preferred_at = next_preferred_at
            row.expires_at = next_preferred_at + expiry_offset if expiry_offset is not None else None
            row.last_evaluated_at = effective_now
            await session.commit()
            await session.refresh(row)

        return self._serialize_planned_work(row)

    async def cancel_planned_work_item(self, *, work_id: int) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionPlannedWorkItem, work_id)
            if row is None:
                return None
            row.status = "cancelled"
            await session.commit()
            await session.refresh(row)

        return self._serialize_planned_work(row)

    async def complete_planned_work_item(self, *, work_id: int) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionPlannedWorkItem, work_id)
            if row is None:
                return None
            row.status = "completed"
            await session.commit()
            await session.refresh(row)

        return self._serialize_planned_work(row)

    async def mark_planned_work_due(
        self,
        *,
        work_id: int,
        evaluated_at: datetime | None = None,
    ) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionPlannedWorkItem, work_id)
            if row is None:
                return None
            if row.status in {"completed", "cancelled"}:
                return self._serialize_planned_work(row)
            row.status = "due"
            row.last_evaluated_at = self._coerce_datetime(evaluated_at) or datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(row)

        return self._serialize_planned_work(row)

    async def update_task_status(self, *, task_id: int, status: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionTask, task_id)
            if row is None:
                return None
            row.status = status
            await session.commit()
            await session.refresh(row)

        return self._serialize_task(row)

    async def append_goal_progress_snapshot(
        self,
        *,
        user_id: str,
        goal_id: int,
        score: float,
        execution_state: str | None,
        progress_trend: str | None,
        source_event_id: str | None = None,
    ) -> dict:
        normalized_score = round(max(0.0, min(1.0, score)), 2)
        async with self.session_factory() as session:
            latest_statement = (
                select(AionGoalProgress)
                .where(
                    AionGoalProgress.user_id == user_id,
                    AionGoalProgress.goal_id == goal_id,
                )
                .order_by(AionGoalProgress.created_at.desc(), AionGoalProgress.id.desc())
                .limit(1)
            )
            latest_result = await session.execute(latest_statement)
            latest_row = latest_result.scalar_one_or_none()

            if (
                latest_row is not None
                and abs(float(latest_row.score) - normalized_score) < 0.01
                and (latest_row.execution_state or "") == (execution_state or "")
                and (latest_row.progress_trend or "") == (progress_trend or "")
            ):
                return self._serialize_goal_progress(latest_row)

            row = AionGoalProgress(
                user_id=user_id,
                goal_id=goal_id,
                score=normalized_score,
                execution_state=execution_state,
                progress_trend=progress_trend,
                source_event_id=source_event_id,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)

        return self._serialize_goal_progress(row)

    async def sync_goal_milestone(
        self,
        *,
        user_id: str,
        goal_id: int,
        phase: str,
        source_event_id: str | None = None,
    ) -> dict:
        milestone_name = self._goal_milestone_name(phase)
        async with self.session_factory() as session:
            statement = (
                select(AionGoalMilestone)
                .where(
                    AionGoalMilestone.user_id == user_id,
                    AionGoalMilestone.goal_id == goal_id,
                )
                .order_by(AionGoalMilestone.updated_at.desc(), AionGoalMilestone.id.desc())
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

            active_rows = [row for row in rows if row.status == "active"]
            same_phase_row = next((row for row in rows if row.phase == phase), None)

            if same_phase_row is None:
                row = AionGoalMilestone(
                    user_id=user_id,
                    goal_id=goal_id,
                    name=milestone_name,
                    phase=phase,
                    status="active",
                    source_event_id=source_event_id,
                )
                session.add(row)
            else:
                row = same_phase_row
                row.name = milestone_name
                row.status = "active"
                row.source_event_id = source_event_id

            for active_row in active_rows:
                if active_row is row:
                    continue
                active_row.status = "completed"

            await session.commit()
            await session.refresh(row)

        return self._serialize_goal_milestone(row)

    async def append_goal_milestone_history(
        self,
        *,
        user_id: str,
        goal_id: int,
        milestone_name: str,
        phase: str,
        risk_level: str | None,
        completion_criteria: str | None,
        source_event_id: str | None = None,
    ) -> dict:
        async with self.session_factory() as session:
            latest_statement = (
                select(AionGoalMilestoneHistory)
                .where(
                    AionGoalMilestoneHistory.user_id == user_id,
                    AionGoalMilestoneHistory.goal_id == goal_id,
                )
                .order_by(AionGoalMilestoneHistory.created_at.desc(), AionGoalMilestoneHistory.id.desc())
                .limit(1)
            )
            latest_result = await session.execute(latest_statement)
            latest_row = latest_result.scalar_one_or_none()

            if (
                latest_row is not None
                and latest_row.milestone_name == milestone_name
                and latest_row.phase == phase
                and (latest_row.risk_level or "") == (risk_level or "")
                and (latest_row.completion_criteria or "") == (completion_criteria or "")
            ):
                return self._serialize_goal_milestone_history(latest_row)

            row = AionGoalMilestoneHistory(
                user_id=user_id,
                goal_id=goal_id,
                milestone_name=milestone_name[:160],
                phase=phase,
                risk_level=risk_level,
                completion_criteria=completion_criteria,
                source_event_id=source_event_id,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)

        return self._serialize_goal_milestone_history(row)

    async def get_attention_turn(self, *, user_id: str, conversation_key: str) -> dict | None:
        normalized_conversation_key = str(conversation_key).strip()[:96]
        if not normalized_conversation_key:
            return None
        async with self.session_factory() as session:
            statement = (
                select(AionAttentionTurn)
                .where(
                    AionAttentionTurn.user_id == user_id,
                    AionAttentionTurn.conversation_key == normalized_conversation_key,
                )
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._serialize_attention_turn(row)

    async def upsert_attention_turn(
        self,
        *,
        user_id: str,
        conversation_key: str,
        turn_id: str,
        status: str,
        source_count: int,
        messages: list[str] | None = None,
        event_ids: list[str] | None = None,
        update_keys: list[str] | None = None,
        assembled_text: str | None = None,
        owner_mode: str = "durable_inbox",
    ) -> dict:
        normalized_conversation_key = str(conversation_key).strip()[:96]
        normalized_turn_id = str(turn_id).strip()[:64]
        normalized_status = str(status).strip().lower()[:24] or "pending"
        normalized_owner_mode = str(owner_mode).strip().lower()[:24] or "durable_inbox"
        normalized_messages = [str(item).strip() for item in (messages or []) if str(item).strip()]
        normalized_event_ids = [str(item).strip()[:64] for item in (event_ids or []) if str(item).strip()]
        normalized_update_keys = [str(item).strip()[:96] for item in (update_keys or []) if str(item).strip()]
        normalized_source_count = max(1, int(source_count))
        normalized_assembled_text = str(assembled_text).strip() if assembled_text else None

        async with self.session_factory() as session:
            statement = (
                select(AionAttentionTurn)
                .where(
                    AionAttentionTurn.user_id == user_id,
                    AionAttentionTurn.conversation_key == normalized_conversation_key,
                )
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()

            if row is None:
                row = AionAttentionTurn(
                    user_id=user_id,
                    conversation_key=normalized_conversation_key,
                    turn_id=normalized_turn_id,
                    status=normalized_status,
                    source_count=normalized_source_count,
                    assembled_text=normalized_assembled_text,
                    owner_mode=normalized_owner_mode,
                    messages_json=normalized_messages,
                    event_ids_json=normalized_event_ids,
                    update_keys_json=normalized_update_keys,
                )
                session.add(row)
            else:
                row.turn_id = normalized_turn_id
                row.status = normalized_status
                row.source_count = normalized_source_count
                row.assembled_text = normalized_assembled_text
                row.owner_mode = normalized_owner_mode
                row.messages_json = normalized_messages
                row.event_ids_json = normalized_event_ids
                row.update_keys_json = normalized_update_keys

            await session.commit()
            await session.refresh(row)

        return self._serialize_attention_turn(row)

    async def get_attention_turn_stats(
        self,
        *,
        answered_ttl_seconds: float,
        stale_turn_seconds: float,
        now: datetime | None = None,
    ) -> dict:
        async with self.session_factory() as session:
            result = await session.execute(select(AionAttentionTurn))
            rows = result.scalars().all()

        current_time = self._coerce_datetime(now or datetime.now(timezone.utc))
        stats = {
            "pending": 0,
            "claimed": 0,
            "answered": 0,
            "active_turns": 0,
            "stale_cleanup_candidates": 0,
            "answered_cleanup_candidates": 0,
        }
        for row in rows:
            updated_at = self._coerce_datetime(row.updated_at)
            age_seconds = max(0.0, (current_time - updated_at).total_seconds())
            if row.status == "answered" and age_seconds > float(answered_ttl_seconds):
                stats["answered_cleanup_candidates"] += 1
                continue
            if age_seconds > float(stale_turn_seconds):
                stats["stale_cleanup_candidates"] += 1
                continue
            if row.status == "pending":
                stats["pending"] += 1
            elif row.status == "claimed":
                stats["claimed"] += 1
            else:
                stats["answered"] += 1
            stats["active_turns"] += 1
        return stats

    async def cleanup_attention_turns(
        self,
        *,
        answered_ttl_seconds: float,
        stale_turn_seconds: float,
        now: datetime | None = None,
    ) -> dict:
        current_time = self._coerce_datetime(now or datetime.now(timezone.utc))
        deleted_answered = 0
        deleted_stale = 0
        async with self.session_factory() as session:
            result = await session.execute(select(AionAttentionTurn))
            rows = result.scalars().all()
            for row in rows:
                updated_at = self._coerce_datetime(row.updated_at)
                age_seconds = max(0.0, (current_time - updated_at).total_seconds())
                if row.status == "answered" and age_seconds > float(answered_ttl_seconds):
                    await session.delete(row)
                    deleted_answered += 1
                    continue
                if age_seconds > float(stale_turn_seconds):
                    await session.delete(row)
                    deleted_stale += 1
            await session.commit()
        return {
            "deleted_answered": deleted_answered,
            "deleted_stale": deleted_stale,
        }

    async def get_user_runtime_preferences(
        self,
        user_id: str,
        *,
        scope_type: str | None = None,
        scope_key: str | None = None,
        include_global: bool = True,
    ) -> dict:
        normalized_scope_type, normalized_scope_key = self._normalize_conclusion_scope(
            scope_type=scope_type,
            scope_key=scope_key,
        )
        use_scope_filter = scope_type is not None or scope_key is not None

        where_clauses = [AionConclusion.user_id == user_id]
        if use_scope_filter:
            scoped_clause = and_(
                AionConclusion.scope_type == normalized_scope_type,
                AionConclusion.scope_key == normalized_scope_key,
            )
            if include_global and (
                normalized_scope_type != self.GLOBAL_SCOPE_TYPE
                or normalized_scope_key != self.GLOBAL_SCOPE_KEY
            ):
                where_clauses.append(
                    or_(
                        scoped_clause,
                        and_(
                            AionConclusion.scope_type == self.GLOBAL_SCOPE_TYPE,
                            AionConclusion.scope_key == self.GLOBAL_SCOPE_KEY,
                        ),
                    )
                )
            else:
                where_clauses.append(scoped_clause)

        async with self.session_factory() as session:
            statement = (
                select(AionConclusion)
                .where(*where_clauses)
                .order_by(AionConclusion.updated_at.desc(), AionConclusion.id.desc())
                .limit(36)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        if not rows:
            return {}

        rows = [
            row
            for row in rows
            if conclusion_matches_scope_request(
                kind=row.kind,
                row_scope_type=row.scope_type,
                row_scope_key=row.scope_key,
                requested_scope_type=scope_type,
                requested_scope_key=scope_key,
                include_global=include_global,
            )
        ]
        if not rows:
            return {}

        preferences: dict[str, object] = {}

        def set_preference(key: str, value: object, row: AionConclusion) -> None:
            if key in preferences:
                return
            preferences[key] = value
            preferences[f"{key}_confidence"] = row.confidence
            preferences[f"{key}_source"] = row.source
            preferences[f"{key}_updated_at"] = row.updated_at
            preferences[f"{key}_scope_type"] = row.scope_type
            preferences[f"{key}_scope_key"] = row.scope_key

        for row in rows:
            if row.kind == "response_style":
                set_preference("response_style", row.content, row)
            elif row.kind == "preferred_role":
                set_preference("preferred_role", row.content, row)
            elif row.kind == "collaboration_preference":
                set_preference("collaboration_preference", row.content, row)
            elif row.kind == "proactive_opt_in":
                set_preference(
                    "proactive_opt_in",
                    str(row.content or "").strip().lower() in self.PROACTIVE_OPT_IN_TRUTHY,
                    row,
                )
            elif row.kind == "telegram_enabled":
                set_preference(
                    "telegram_enabled",
                    str(row.content or "").strip().lower() in self.PROACTIVE_OPT_IN_TRUTHY,
                    row,
                )
            elif row.kind == "clickup_enabled":
                set_preference(
                    "clickup_enabled",
                    str(row.content or "").strip().lower() in self.PROACTIVE_OPT_IN_TRUTHY,
                    row,
                )
            elif row.kind == "google_calendar_enabled":
                set_preference(
                    "google_calendar_enabled",
                    str(row.content or "").strip().lower() in self.PROACTIVE_OPT_IN_TRUTHY,
                    row,
                )
            elif row.kind == "google_drive_enabled":
                set_preference(
                    "google_drive_enabled",
                    str(row.content or "").strip().lower() in self.PROACTIVE_OPT_IN_TRUTHY,
                    row,
                )
            elif row.kind == "affective_support_pattern":
                set_preference("affective_support_pattern", row.content, row)
            elif row.kind == "affective_support_sensitivity":
                set_preference("affective_support_sensitivity", row.content, row)
            elif row.kind == "goal_execution_state":
                set_preference("goal_execution_state", row.content, row)
            elif row.kind == "goal_progress_score":
                if "goal_progress_score" in preferences:
                    continue
                try:
                    score = float(row.content)
                except ValueError:
                    continue
                set_preference("goal_progress_score", score, row)
            elif row.kind == "goal_progress_trend":
                set_preference("goal_progress_trend", row.content, row)
            elif row.kind == "goal_progress_arc":
                set_preference("goal_progress_arc", row.content, row)
            elif row.kind == "goal_milestone_transition":
                set_preference("goal_milestone_transition", row.content, row)
            elif row.kind == "goal_milestone_state":
                set_preference("goal_milestone_state", row.content, row)
            elif row.kind == "goal_milestone_arc":
                set_preference("goal_milestone_arc", row.content, row)
            elif row.kind == "goal_milestone_pressure":
                set_preference("goal_milestone_pressure", row.content, row)
            elif row.kind == "goal_milestone_dependency_state":
                set_preference("goal_milestone_dependency_state", row.content, row)
            elif row.kind == "goal_milestone_due_state":
                set_preference("goal_milestone_due_state", row.content, row)
            elif row.kind == "goal_milestone_due_window":
                set_preference("goal_milestone_due_window", row.content, row)
            elif row.kind == "goal_milestone_risk":
                set_preference("goal_milestone_risk", row.content, row)
            elif row.kind == "goal_completion_criteria":
                set_preference("goal_completion_criteria", row.content, row)
            elif row.kind == "proactive_outreach_state":
                set_preference("proactive_outreach_state", row.content, row)
            elif row.kind == "proactive_outreach_trigger":
                set_preference("proactive_outreach_trigger", row.content, row)

        return preferences

    async def _delete_runtime_state_for_user(
        self,
        session: AsyncSession,
        *,
        user_id: str,
    ) -> dict[str, int]:
        deleted_counts: dict[str, int] = {}
        for label, model in self.RUNTIME_RESET_USER_SCOPED_MODELS:
            result = await session.execute(delete(model).where(model.user_id == user_id))
            deleted_counts[label] = int(result.rowcount or 0)
        return deleted_counts

    async def _delete_runtime_state_for_all_users(self, session: AsyncSession) -> dict[str, int]:
        deleted_counts: dict[str, int] = {}
        for label, model in self.RUNTIME_RESET_USER_SCOPED_MODELS:
            result = await session.execute(delete(model))
            deleted_counts[label] = int(result.rowcount or 0)
        return deleted_counts

    async def _delete_non_preserved_conclusions_for_user(
        self,
        session: AsyncSession,
        *,
        user_id: str,
    ) -> int:
        result = await session.execute(
            delete(AionConclusion).where(
                AionConclusion.user_id == user_id,
                ~AionConclusion.kind.in_(self.USER_MANAGED_OPERATIONAL_CONCLUSION_KINDS),
            )
        )
        return int(result.rowcount or 0)

    async def _delete_all_non_preserved_conclusions(self, session: AsyncSession) -> int:
        result = await session.execute(
            delete(AionConclusion).where(
                ~AionConclusion.kind.in_(self.USER_MANAGED_OPERATIONAL_CONCLUSION_KINDS)
            )
        )
        return int(result.rowcount or 0)

    async def _revoke_auth_sessions_for_user(
        self,
        session: AsyncSession,
        *,
        user_id: str,
    ) -> int:
        result = await session.execute(
            update(AionAuthSession)
            .where(
                AionAuthSession.user_id == user_id,
                AionAuthSession.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        return int(result.rowcount or 0)

    async def _revoke_all_auth_sessions(self, session: AsyncSession) -> int:
        result = await session.execute(
            update(AionAuthSession)
            .where(AionAuthSession.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        return int(result.rowcount or 0)

    def _runtime_reset_summary(
        self,
        *,
        scope: str,
        target_user_id: str | None,
        deleted_counts: dict[str, int],
        revoked_session_count: int,
    ) -> dict[str, object]:
        return {
            "status": "ok",
            "scope": scope,
            "target_user_id": target_user_id,
            "deleted_counts": dict(deleted_counts),
            "total_deleted_records": sum(int(count) for count in deleted_counts.values()),
            "revoked_session_count": int(revoked_session_count),
            "cleared_categories": [
                label
                for label, count in deleted_counts.items()
                if int(count) > 0
            ],
            "preserved_categories": [
                "auth_users",
                "profiles",
                "linked_integrations",
                "linked_channels",
                "user_managed_operational_preferences",
            ],
            "preserved_conclusion_kinds": sorted(self.USER_MANAGED_OPERATIONAL_CONCLUSION_KINDS),
        }

    async def get_user_conclusions(
        self,
        user_id: str,
        limit: int = 3,
        *,
        scope_type: str | None = None,
        scope_key: str | None = None,
        include_global: bool = False,
    ) -> list[dict]:
        normalized_scope_type, normalized_scope_key = self._normalize_conclusion_scope(
            scope_type=scope_type,
            scope_key=scope_key,
        )
        use_scope_filter = scope_type is not None or scope_key is not None

        where_clauses = [AionConclusion.user_id == user_id]
        if use_scope_filter:
            scoped_clause = and_(
                AionConclusion.scope_type == normalized_scope_type,
                AionConclusion.scope_key == normalized_scope_key,
            )
            if include_global and (
                normalized_scope_type != self.GLOBAL_SCOPE_TYPE
                or normalized_scope_key != self.GLOBAL_SCOPE_KEY
            ):
                where_clauses.append(
                    or_(
                        scoped_clause,
                        and_(
                            AionConclusion.scope_type == self.GLOBAL_SCOPE_TYPE,
                            AionConclusion.scope_key == self.GLOBAL_SCOPE_KEY,
                        ),
                    )
                )
            else:
                where_clauses.append(scoped_clause)

        async with self.session_factory() as session:
            statement = (
                select(AionConclusion)
                .where(*where_clauses)
                .order_by(AionConclusion.updated_at.desc(), AionConclusion.id.desc())
                .limit(max(limit * 4, limit))
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        filtered_rows = [
            row
            for row in rows
            if conclusion_matches_scope_request(
                kind=row.kind,
                row_scope_type=row.scope_type,
                row_scope_key=row.scope_key,
                requested_scope_type=scope_type,
                requested_scope_key=scope_key,
                include_global=include_global,
            )
        ]

        return [
            {
                "id": row.id,
                "kind": row.kind,
                "content": row.content,
                "confidence": row.confidence,
                "source": row.source,
                "supporting_event_id": row.supporting_event_id,
                "scope_type": row.scope_type,
                "scope_key": row.scope_key,
                "updated_at": row.updated_at,
            }
            for row in filtered_rows[:limit]
        ]

    async def upsert_user_profile_language(
        self,
        user_id: str,
        language_code: str,
        confidence: float,
        source: str,
    ) -> dict:
        async with self.session_factory() as session:
            row = await session.get(AionProfile, user_id)
            if row is None:
                row = AionProfile(
                    user_id=user_id,
                    preferred_language=language_code,
                    ui_language="system",
                    utc_offset=DEFAULT_UTC_OFFSET,
                    language_confidence=confidence,
                    language_source=source,
                )
                session.add(row)
            elif self._should_update_language_profile(
                current_language=row.preferred_language,
                current_confidence=row.language_confidence,
                next_language=language_code,
                next_confidence=confidence,
                source=source,
            ):
                updated_confidence = self._next_language_confidence(
                    current_language=row.preferred_language,
                    current_confidence=row.language_confidence,
                    next_language=language_code,
                    next_confidence=confidence,
                )
                row.preferred_language = language_code
                row.language_confidence = updated_confidence
                row.language_source = source
            await session.commit()
            await session.refresh(row)

        return {
            "user_id": row.user_id,
            "preferred_language": row.preferred_language,
            "ui_language": row.ui_language,
            "utc_offset": normalize_utc_offset(row.utc_offset),
            "language_confidence": row.language_confidence,
            "language_source": row.language_source,
            "updated_at": row.updated_at,
        }

    async def set_user_profile_language(
        self,
        *,
        user_id: str,
        language_code: str,
        source: str = "app_settings",
    ) -> dict:
        normalized_language = str(language_code or "").strip().lower()[:8] or "en"
        async with self.session_factory() as session:
            row = await session.get(AionProfile, user_id)
            if row is None:
                row = AionProfile(
                    user_id=user_id,
                    preferred_language=normalized_language,
                    ui_language="system",
                    utc_offset=DEFAULT_UTC_OFFSET,
                    language_confidence=1.0,
                    language_source=source,
                )
                session.add(row)
            else:
                row.preferred_language = normalized_language
                row.language_confidence = 1.0
                row.language_source = source
            await session.commit()
            await session.refresh(row)
        return {
            "user_id": row.user_id,
            "preferred_language": row.preferred_language,
            "ui_language": row.ui_language,
            "utc_offset": normalize_utc_offset(row.utc_offset),
            "language_confidence": row.language_confidence,
            "language_source": row.language_source,
            "telegram_chat_id": row.telegram_chat_id,
            "telegram_user_id": row.telegram_user_id,
            "telegram_link_code": row.telegram_link_code,
            "telegram_link_code_issued_at": row.telegram_link_code_issued_at,
            "telegram_linked_at": row.telegram_linked_at,
            "updated_at": row.updated_at,
        }

    async def set_user_profile_ui_language(
        self,
        *,
        user_id: str,
        ui_language: str,
    ) -> dict:
        normalized_ui_language = str(ui_language or "").strip().lower() or "system"
        if normalized_ui_language not in {"system", "en", "pl", "de"}:
            normalized_ui_language = "system"
        async with self.session_factory() as session:
            row = await session.get(AionProfile, user_id)
            if row is None:
                row = AionProfile(
                    user_id=user_id,
                    preferred_language="en",
                    ui_language=normalized_ui_language,
                    utc_offset=DEFAULT_UTC_OFFSET,
                    language_confidence=0.0,
                    language_source="default",
                )
                session.add(row)
            else:
                row.ui_language = normalized_ui_language
            await session.commit()
            await session.refresh(row)
        return self._serialize_profile(row) or {}

    async def set_user_profile_utc_offset(
        self,
        *,
        user_id: str,
        utc_offset: str,
    ) -> dict:
        normalized_utc_offset = normalize_utc_offset(utc_offset)
        async with self.session_factory() as session:
            row = await session.get(AionProfile, user_id)
            if row is None:
                row = AionProfile(
                    user_id=user_id,
                    preferred_language="en",
                    ui_language="system",
                    utc_offset=normalized_utc_offset,
                    language_confidence=0.0,
                    language_source="default",
                )
                session.add(row)
            else:
                row.utc_offset = normalized_utc_offset
            await session.commit()
            await session.refresh(row)
        return self._serialize_profile(row) or {}

    async def create_or_rotate_telegram_link_code(
        self,
        *,
        user_id: str,
        link_code: str,
        issued_at: datetime,
    ) -> dict:
        normalized_code = str(link_code or "").strip().upper()[:32]
        async with self.session_factory() as session:
            row = await session.get(AionProfile, user_id)
            if row is None:
                row = AionProfile(
                    user_id=user_id,
                    preferred_language="en",
                    ui_language="system",
                    utc_offset=DEFAULT_UTC_OFFSET,
                    language_confidence=0.0,
                    language_source="default",
                )
                session.add(row)
            row.telegram_link_code = normalized_code or None
            row.telegram_link_code_issued_at = self._coerce_datetime(issued_at)
            await session.commit()
            await session.refresh(row)
        return {
            "user_id": row.user_id,
            "preferred_language": row.preferred_language,
            "ui_language": row.ui_language,
            "utc_offset": normalize_utc_offset(row.utc_offset),
            "language_confidence": row.language_confidence,
            "language_source": row.language_source,
            "telegram_chat_id": row.telegram_chat_id,
            "telegram_user_id": row.telegram_user_id,
            "telegram_link_code": row.telegram_link_code,
            "telegram_link_code_issued_at": row.telegram_link_code_issued_at,
            "telegram_linked_at": row.telegram_linked_at,
            "updated_at": row.updated_at,
        }

    async def set_user_telegram_link(
        self,
        *,
        user_id: str,
        chat_id: str,
        telegram_user_id: str | None,
        linked_at: datetime,
    ) -> dict:
        normalized_chat_id = str(chat_id or "").strip()
        normalized_telegram_user_id = str(telegram_user_id or "").strip() or None
        async with self.session_factory() as session:
            if normalized_telegram_user_id:
                await self._merge_legacy_telegram_user_state(
                    session,
                    source_user_id=normalized_telegram_user_id,
                    target_user_id=user_id,
                )
            conflict_conditions = []
            if normalized_chat_id:
                conflict_conditions.append(AionProfile.telegram_chat_id == normalized_chat_id)
            if normalized_telegram_user_id:
                conflict_conditions.append(AionProfile.telegram_user_id == normalized_telegram_user_id)
            if conflict_conditions:
                statement = select(AionProfile).where(
                    AionProfile.user_id != user_id,
                    or_(*conflict_conditions),
                )
                result = await session.execute(statement)
                for conflicting_row in result.scalars().all():
                    conflicting_row.telegram_chat_id = None
                    conflicting_row.telegram_user_id = None
                    conflicting_row.telegram_linked_at = None
                    conflicting_row.telegram_link_code = None
                    conflicting_row.telegram_link_code_issued_at = None
            row = await session.get(AionProfile, user_id)
            if row is None:
                row = AionProfile(
                    user_id=user_id,
                    preferred_language="en",
                    ui_language="system",
                    utc_offset=DEFAULT_UTC_OFFSET,
                    language_confidence=0.0,
                    language_source="default",
                )
                session.add(row)
            row.telegram_chat_id = normalized_chat_id or None
            row.telegram_user_id = normalized_telegram_user_id
            row.telegram_linked_at = self._coerce_datetime(linked_at)
            row.telegram_link_code = None
            row.telegram_link_code_issued_at = None
            await session.commit()
            await session.refresh(row)
        return self._serialize_profile(row) or {}

    async def upsert_conclusion(
        self,
        user_id: str,
        kind: str,
        content: str,
        confidence: float,
        source: str,
        supporting_event_id: str | None = None,
        scope_type: str | None = None,
        scope_key: str | None = None,
    ) -> dict:
        normalized_scope_type, normalized_scope_key = canonicalize_conclusion_scope(
            kind=kind,
            scope_type=scope_type,
            scope_key=scope_key,
        )
        async with self.session_factory() as session:
            statement = (
                select(AionConclusion)
                .where(
                    AionConclusion.user_id == user_id,
                    AionConclusion.kind == kind,
                    AionConclusion.scope_type == normalized_scope_type,
                    AionConclusion.scope_key == normalized_scope_key,
                )
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()

            if row is None:
                row = AionConclusion(
                    user_id=user_id,
                    kind=kind,
                    content=content,
                    confidence=confidence,
                    source=source,
                    supporting_event_id=supporting_event_id,
                    scope_type=normalized_scope_type,
                    scope_key=normalized_scope_key,
                )
                session.add(row)
            elif self._should_update_conclusion(
                kind=kind,
                current_content=row.content,
                current_confidence=row.confidence,
                next_content=content,
                next_confidence=confidence,
                source=source,
            ):
                updated_confidence = self._next_conclusion_confidence(
                    current_content=row.content,
                    current_confidence=row.confidence,
                    next_content=content,
                    next_confidence=confidence,
                )
                row.content = content
                row.confidence = updated_confidence
                row.source = source
                row.supporting_event_id = supporting_event_id

            await session.commit()
            await session.refresh(row)

        conclusion_layer = self.conclusion_memory_layer(kind)
        if conclusion_layer in {self.MEMORY_LAYER_SEMANTIC, self.MEMORY_LAYER_AFFECTIVE}:
            source_kind = "semantic" if conclusion_layer == self.MEMORY_LAYER_SEMANTIC else "affective"
            if source_kind not in self.embedding_source_kinds:
                return {
                    "user_id": row.user_id,
                    "kind": row.kind,
                    "content": row.content,
                    "confidence": row.confidence,
                    "source": row.source,
                    "supporting_event_id": row.supporting_event_id,
                    "scope_type": row.scope_type,
                    "scope_key": row.scope_key,
                    "updated_at": row.updated_at,
                }
            if source_kind in {"semantic", "affective"}:
                embedding, embedding_status = await self._materialize_embedding(content=row.content)
            else:
                embedding = None
                embedding_status = "pending_vector_materialization"
            await self.upsert_semantic_embedding(
                user_id=user_id,
                source_kind=source_kind,
                source_id=f"conclusion:{row.id}",
                source_event_id=row.supporting_event_id,
                scope_type=normalized_scope_type,
                scope_key=normalized_scope_key,
                content=row.content,
                embedding=embedding,
                embedding_model=self.embedding_posture["model_effective"],
                embedding_dimensions=self.embedding_dimensions,
                metadata={
                    "kind": row.kind,
                    "confidence": row.confidence,
                    "source": row.source,
                    "embedding_status": embedding_status,
                    "embedding_refresh_mode": self.embedding_refresh_mode,
                    "embedding_provider_requested": self.embedding_posture["provider_requested"],
                    "embedding_provider_effective": self.embedding_posture["provider_effective"],
                    "embedding_provider_hint": self.embedding_posture["provider_hint"],
                    "embedding_model_requested": self.embedding_posture["model_requested"],
                    "embedding_model_effective": self.embedding_posture["model_effective"],
                },
            )

        return {
            "user_id": row.user_id,
            "kind": row.kind,
            "content": row.content,
            "confidence": row.confidence,
            "source": row.source,
            "supporting_event_id": row.supporting_event_id,
            "scope_type": row.scope_type,
            "scope_key": row.scope_key,
            "updated_at": row.updated_at,
        }

    async def upsert_theta(
        self,
        user_id: str,
        support_bias: float,
        analysis_bias: float,
        execution_bias: float,
    ) -> dict:
        async with self.session_factory() as session:
            row = await session.get(AionTheta, user_id)
            if row is None:
                row = AionTheta(
                    user_id=user_id,
                    support_bias=support_bias,
                    analysis_bias=analysis_bias,
                    execution_bias=execution_bias,
                )
                session.add(row)
            else:
                row.support_bias = support_bias
                row.analysis_bias = analysis_bias
                row.execution_bias = execution_bias

            await session.commit()
            await session.refresh(row)

        return {
            "user_id": row.user_id,
            "support_bias": row.support_bias,
            "analysis_bias": row.analysis_bias,
            "execution_bias": row.execution_bias,
            "updated_at": row.updated_at,
        }

    async def upsert_scheduler_cadence_evidence(
        self,
        *,
        cadence_kind: str,
        execution_owner: str,
        execution_mode: str,
        summary: dict | None,
        last_run_at: datetime | None = None,
    ) -> dict:
        normalized_cadence_kind = str(cadence_kind).strip().lower()[:24]
        if normalized_cadence_kind not in {"maintenance", "proactive"}:
            raise ValueError("cadence_kind must be one of: maintenance, proactive")
        normalized_execution_owner = str(execution_owner).strip().lower()[:32] or "unknown_owner"
        normalized_execution_mode = str(execution_mode).strip().lower()[:24] or "unknown_mode"
        normalized_summary = dict(summary or {})
        normalized_last_run_at = self._coerce_datetime(last_run_at) or datetime.now(timezone.utc)

        async with self.session_factory() as session:
            statement = (
                select(AionSchedulerCadenceEvidence)
                .where(AionSchedulerCadenceEvidence.cadence_kind == normalized_cadence_kind)
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()

            if row is None:
                row = AionSchedulerCadenceEvidence(
                    cadence_kind=normalized_cadence_kind,
                    execution_owner=normalized_execution_owner,
                    execution_mode=normalized_execution_mode,
                    summary_json=normalized_summary,
                    last_run_at=normalized_last_run_at,
                )
                session.add(row)
            else:
                row.execution_owner = normalized_execution_owner
                row.execution_mode = normalized_execution_mode
                row.summary_json = normalized_summary
                row.last_run_at = normalized_last_run_at

            await session.commit()
            await session.refresh(row)

        return self._serialize_scheduler_cadence_evidence(row)

    async def get_scheduler_cadence_evidence(
        self,
        *,
        cadence_kind: str,
    ) -> dict | None:
        normalized_cadence_kind = str(cadence_kind).strip().lower()[:24]
        if normalized_cadence_kind not in {"maintenance", "proactive"}:
            return None

        async with self.session_factory() as session:
            statement = (
                select(AionSchedulerCadenceEvidence)
                .where(AionSchedulerCadenceEvidence.cadence_kind == normalized_cadence_kind)
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()

        if row is None:
            return None
        return self._serialize_scheduler_cadence_evidence(row)

    async def enqueue_reflection_task(self, user_id: str, event_id: str) -> dict:
        async with self.session_factory() as session:
            statement = (
                select(AionReflectionTask)
                .where(AionReflectionTask.event_id == event_id)
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()

            if row is None:
                row = AionReflectionTask(
                    user_id=user_id,
                    event_id=event_id,
                    status="pending",
                    attempts=0,
                    last_error=None,
                )
                session.add(row)
            elif row.status != "completed":
                row.user_id = user_id
                row.status = "pending"
                row.last_error = None

            await session.commit()
            await session.refresh(row)

        return self._serialize_reflection_task(row)

    async def get_pending_reflection_tasks(self, limit: int = 100) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionReflectionTask)
                .where(AionReflectionTask.status.in_(("pending", "processing", "failed")))
                .order_by(AionReflectionTask.id.asc())
                .limit(limit)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        return [self._serialize_reflection_task(row) for row in rows]

    async def mark_reflection_task_processing(self, task_id: int) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionReflectionTask, task_id)
            if row is None:
                return None
            row.status = "processing"
            row.attempts += 1
            row.last_error = None
            await session.commit()
            await session.refresh(row)

        return self._serialize_reflection_task(row)

    async def mark_reflection_task_completed(self, task_id: int) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionReflectionTask, task_id)
            if row is None:
                return None
            row.status = "completed"
            row.last_error = None
            await session.commit()
            await session.refresh(row)

        return self._serialize_reflection_task(row)

    async def mark_reflection_task_failed(self, task_id: int, error: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionReflectionTask, task_id)
            if row is None:
                return None
            row.status = "failed"
            row.last_error = error[:500]
            await session.commit()
            await session.refresh(row)

        return self._serialize_reflection_task(row)

    async def upsert_subconscious_proposal(
        self,
        *,
        user_id: str,
        proposal_type: str,
        summary: str,
        payload: dict | None = None,
        confidence: float = 0.0,
        source_event_id: str | None = None,
        research_policy: str = "read_only",
        allowed_tools: list[str] | None = None,
    ) -> dict:
        normalized_type = str(proposal_type).strip().lower()[:32]
        normalized_summary = str(summary).strip()
        normalized_tools = [str(item).strip().lower() for item in (allowed_tools or []) if str(item).strip()]
        async with self.session_factory() as session:
            statement = (
                select(AionSubconsciousProposal)
                .where(
                    AionSubconsciousProposal.user_id == user_id,
                    AionSubconsciousProposal.proposal_type == normalized_type,
                    AionSubconsciousProposal.summary == normalized_summary,
                    AionSubconsciousProposal.status.in_(("pending", "deferred")),
                )
                .order_by(AionSubconsciousProposal.id.desc())
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()
            if row is None:
                row = AionSubconsciousProposal(
                    user_id=user_id,
                    proposal_type=normalized_type,
                    summary=normalized_summary[:1000],
                    payload=dict(payload or {}),
                    confidence=max(0.0, min(1.0, float(confidence))),
                    source_event_id=source_event_id,
                    status="pending",
                    research_policy=str(research_policy or "read_only").strip().lower()[:16] or "read_only",
                    allowed_tools_json=normalized_tools,
                )
                session.add(row)
            else:
                row.payload = dict(payload or row.payload or {})
                row.confidence = max(row.confidence, max(0.0, min(1.0, float(confidence))))
                row.source_event_id = source_event_id or row.source_event_id
                row.research_policy = str(research_policy or row.research_policy or "read_only").strip().lower()[:16]
                row.allowed_tools_json = normalized_tools or list(row.allowed_tools_json or [])
            await session.commit()
            await session.refresh(row)
        return self._serialize_subconscious_proposal(row)

    async def get_pending_subconscious_proposals(self, *, user_id: str, limit: int = 8) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionSubconsciousProposal)
                .where(
                    AionSubconsciousProposal.user_id == user_id,
                    AionSubconsciousProposal.status.in_(("pending", "deferred")),
                )
                .order_by(
                    (AionSubconsciousProposal.status == "pending").desc(),
                    AionSubconsciousProposal.confidence.desc(),
                    AionSubconsciousProposal.created_at.asc(),
                    AionSubconsciousProposal.id.asc(),
                )
                .limit(limit)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()
        return [self._serialize_subconscious_proposal(row) for row in rows]

    async def resolve_subconscious_proposal(
        self,
        *,
        proposal_id: int,
        decision: str,
        reason: str = "",
    ) -> dict | None:
        status_map = {
            "accept": "accepted",
            "merge": "merged",
            "defer": "deferred",
            "discard": "discarded",
        }
        next_status = status_map.get(str(decision).strip().lower())
        if next_status is None:
            return None
        async with self.session_factory() as session:
            row = await session.get(AionSubconsciousProposal, proposal_id)
            if row is None:
                return None
            row.status = next_status
            row.decision_reason = str(reason or "").strip()[:1000]
            row.decided_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(row)
        return self._serialize_subconscious_proposal(row)

    async def get_reflection_task_stats(
        self,
        *,
        max_attempts: int,
        stuck_after_seconds: int,
        retry_backoff_seconds: tuple[int, ...],
        now: datetime | None = None,
    ) -> dict[str, int]:
        async with self.session_factory() as session:
            statement = select(AionReflectionTask)
            result = await session.execute(statement)
            rows = result.scalars().all()

        current_time = self._coerce_datetime(now or datetime.now(timezone.utc))
        stats = {
            "total": 0,
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "retryable_failed": 0,
            "exhausted_failed": 0,
            "stuck_processing": 0,
        }
        for row in rows:
            stats["total"] += 1
            status = row.status
            if status in stats:
                stats[status] += 1

            attempts = int(row.attempts or 0)
            updated_at = self._coerce_datetime(row.updated_at)
            age_seconds = max(0.0, (current_time - updated_at).total_seconds()) if updated_at else 0.0

            if status == "processing" and age_seconds >= stuck_after_seconds:
                stats["stuck_processing"] += 1

            if status != "failed":
                continue

            if attempts >= max_attempts:
                stats["exhausted_failed"] += 1
                continue

            backoff = self._retry_backoff_seconds_for_attempts(attempts, retry_backoff_seconds)
            if age_seconds >= backoff:
                stats["retryable_failed"] += 1

        return stats

    def _should_update_language_profile(
        self,
        current_language: str,
        current_confidence: float,
        next_language: str,
        next_confidence: float,
        source: str,
    ) -> bool:
        if current_language == next_language:
            return True
        if source == "explicit_request":
            return True
        if next_confidence >= 0.9:
            return True
        return current_confidence <= 0.55 and next_confidence >= 0.72

    def _next_language_confidence(
        self,
        current_language: str,
        current_confidence: float,
        next_language: str,
        next_confidence: float,
    ) -> float:
        if current_language == next_language:
            return min(0.99, max(current_confidence, next_confidence))
        return next_confidence

    def _normalize_conclusion_scope(
        self,
        *,
        scope_type: str | None,
        scope_key: str | None,
    ) -> tuple[str, str]:
        normalized_scope_type = str(scope_type or self.GLOBAL_SCOPE_TYPE).strip().lower()
        normalized_scope_key = str(scope_key or "").strip()
        if normalized_scope_type not in {"global", "goal", "task"}:
            return self.GLOBAL_SCOPE_TYPE, self.GLOBAL_SCOPE_KEY
        if normalized_scope_type == self.GLOBAL_SCOPE_TYPE:
            return self.GLOBAL_SCOPE_TYPE, self.GLOBAL_SCOPE_KEY
        if not normalized_scope_key:
            return self.GLOBAL_SCOPE_TYPE, self.GLOBAL_SCOPE_KEY
        return normalized_scope_type, normalized_scope_key

    def _should_update_conclusion(
        self,
        kind: str,
        current_content: str,
        current_confidence: float,
        next_content: str,
        next_confidence: float,
        source: str,
    ) -> bool:
        if current_content == next_content:
            return True
        if source == "explicit_request":
            return True
        if kind in {
            "goal_execution_state",
            "goal_progress_score",
            "goal_progress_trend",
            "goal_progress_arc",
            "goal_milestone_state",
            "goal_milestone_arc",
            "goal_milestone_pressure",
            "goal_milestone_dependency_state",
            "goal_milestone_due_state",
            "goal_milestone_due_window",
            "goal_milestone_transition",
            "goal_milestone_risk",
            "goal_completion_criteria",
            "affective_support_pattern",
            "affective_support_sensitivity",
        }:
            return True
        return next_confidence >= current_confidence

    def _next_conclusion_confidence(
        self,
        current_content: str,
        current_confidence: float,
        next_content: str,
        next_confidence: float,
    ) -> float:
        if current_content == next_content:
            return min(0.99, max(current_confidence, next_confidence))
        return next_confidence

    async def _materialize_embedding(self, *, content: str) -> tuple[list[float] | None, str]:
        return await materialize_embedding(
            content=content,
            posture=self.embedding_posture,
            dimensions=self.embedding_dimensions,
            refresh_mode=self.embedding_refresh_mode,
            openai_embedding_client=self.openai_embedding_client,
        )

    def _serialize_reflection_task(self, row: AionReflectionTask) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "event_id": row.event_id,
            "status": row.status,
            "attempts": row.attempts,
            "last_error": row.last_error,
            "updated_at": row.updated_at,
            "created_at": row.created_at,
        }

    def _serialize_scheduler_cadence_evidence(self, row: AionSchedulerCadenceEvidence) -> dict:
        return {
            "id": row.id,
            "cadence_kind": row.cadence_kind,
            "execution_owner": row.execution_owner,
            "execution_mode": row.execution_mode,
            "summary": dict(row.summary_json or {}),
            "last_run_at": row.last_run_at,
            "updated_at": row.updated_at,
            "created_at": row.created_at,
        }

    def _serialize_memory(self, row: AionMemory) -> dict:
        return {
            "id": row.id,
            "event_id": row.event_id,
            "source": row.source,
            "timestamp": row.event_timestamp,
            "summary": row.summary,
            "payload": row.payload or {},
            "importance": row.importance,
        }

    def _project_memory_to_transcript_items(self, memory_item: dict[str, Any]) -> list[dict[str, Any]]:
        payload = memory_item.get("payload")
        if not isinstance(payload, dict):
            payload = {}

        event_id = str(memory_item.get("event_id", "") or "").strip()
        timestamp = self._coerce_datetime(memory_item.get("event_timestamp") or memory_item.get("timestamp"))
        channel = self._normalize_transcript_channel(memory_item.get("source"))
        source = str(memory_item.get("source", "") or "").strip().lower()
        event_text = str(payload.get("event", "") or "").strip()
        expression_text = str(payload.get("expression", "") or "").strip()
        response_language = str(payload.get("response_language", "") or payload.get("language", "") or "").strip()
        items: list[dict[str, Any]] = []

        if event_text and self._event_projects_to_transcript(payload=payload, source=source):
            items.append(
                {
                    "message_id": f"{event_id}:user",
                    "event_id": event_id,
                    "role": "user",
                    "text": event_text,
                    "channel": channel,
                    "timestamp": timestamp,
                }
            )

        if expression_text and self._assistant_projects_to_transcript(payload=payload, source=source):
            metadata: dict[str, Any] | None = None
            if response_language:
                metadata = {"language": response_language}
            items.append(
                {
                    "message_id": f"{event_id}:assistant",
                    "event_id": event_id,
                    "role": "assistant",
                    "text": expression_text,
                    "channel": channel,
                    "timestamp": timestamp,
                    "metadata": metadata,
                }
            )

        return items

    @staticmethod
    def _normalize_transcript_channel(source: Any) -> str:
        normalized = str(source or "").strip().lower()
        if normalized == "telegram":
            return "telegram"
        return "api"

    @staticmethod
    def _event_projects_to_transcript(*, payload: dict[str, Any], source: str) -> bool:
        visibility = str(payload.get("event_visibility", "") or "").strip().lower()
        if visibility in {"transcript", "internal"}:
            return visibility == "transcript"
        return source != "scheduler"

    @staticmethod
    def _assistant_projects_to_transcript(*, payload: dict[str, Any], source: str) -> bool:
        visibility = str(payload.get("assistant_visibility", "") or "").strip().lower()
        if visibility in {"transcript", "internal"}:
            return visibility == "transcript"
        if source != "scheduler":
            return True
        actions = payload.get("action_actions")
        if isinstance(actions, list) and "send_telegram_message" in actions:
            return True
        action_status = str(payload.get("action", "") or "").strip().lower()
        chat_id = payload.get("chat_id")
        proactive_state = str(payload.get("proactive_state_update", "") or "").strip().lower()
        return (
            action_status == "success"
            and isinstance(chat_id, (int, str))
            and str(chat_id).strip() != ""
            and (
                proactive_state.startswith("delivery_ready:")
                or proactive_state == ""
            )
        )

    @staticmethod
    def _is_conversation_turn_memory(memory_item: dict[str, Any]) -> bool:
        source = str(memory_item.get("source", "") or "").strip().lower()
        if source not in {"api", "telegram", "scheduler"}:
            return False
        payload = memory_item.get("payload") if isinstance(memory_item.get("payload"), dict) else {}
        memory_kind = str(payload.get("memory_kind", "") or "").strip().lower()
        if memory_kind and memory_kind != "episodic":
            return False
        return True

    @staticmethod
    def _is_user_authored_turn(memory_item: dict[str, Any]) -> bool:
        if not MemoryRepository._is_conversation_turn_memory(memory_item):
            return False
        source = str(memory_item.get("source", "") or "").strip().lower()
        if source == "scheduler":
            return False
        payload = memory_item.get("payload") if isinstance(memory_item.get("payload"), dict) else {}
        return MemoryRepository._event_projects_to_transcript(payload=payload, source=source)

    @staticmethod
    def _is_delivered_scheduler_outreach(memory_item: dict[str, Any]) -> bool:
        if not MemoryRepository._is_conversation_turn_memory(memory_item):
            return False
        source = str(memory_item.get("source", "") or "").strip().lower()
        if source != "scheduler":
            return False
        payload = memory_item.get("payload") if isinstance(memory_item.get("payload"), dict) else {}
        return MemoryRepository._assistant_projects_to_transcript(payload=payload, source=source)

    def _serialize_goal(self, row: AionGoal) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "name": row.name,
            "description": row.description,
            "priority": row.priority,
            "status": row.status,
            "goal_type": row.goal_type,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    def _serialize_task(self, row: AionTask) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "goal_id": row.goal_id,
            "name": row.name,
            "description": row.description,
            "priority": row.priority,
            "status": row.status,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    def _serialize_planned_work(self, row: AionPlannedWorkItem) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "goal_id": row.goal_id,
            "task_id": row.task_id,
            "kind": row.kind,
            "summary": row.summary,
            "status": row.status,
            "not_before": self._coerce_datetime(row.not_before),
            "preferred_at": self._coerce_datetime(row.preferred_at),
            "expires_at": self._coerce_datetime(row.expires_at),
            "recurrence_mode": row.recurrence_mode,
            "recurrence_rule": row.recurrence_rule,
            "delivery_channel": row.delivery_channel,
            "requires_foreground_execution": bool(row.requires_foreground_execution),
            "quiet_hours_policy": row.quiet_hours_policy,
            "provenance": row.provenance,
            "source_event_id": row.source_event_id,
            "last_evaluated_at": self._coerce_datetime(row.last_evaluated_at),
            "created_at": self._coerce_datetime(row.created_at),
            "updated_at": self._coerce_datetime(row.updated_at),
        }

    def _serialize_goal_progress(self, row: AionGoalProgress) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "goal_id": row.goal_id,
            "score": row.score,
            "execution_state": row.execution_state,
            "progress_trend": row.progress_trend,
            "source_event_id": row.source_event_id,
            "created_at": row.created_at,
        }

    def _serialize_goal_milestone(self, row: AionGoalMilestone) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "goal_id": row.goal_id,
            "name": row.name,
            "phase": row.phase,
            "status": row.status,
            "source_event_id": row.source_event_id,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    def _serialize_goal_milestone_history(self, row: AionGoalMilestoneHistory) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "goal_id": row.goal_id,
            "milestone_name": row.milestone_name,
            "phase": row.phase,
            "risk_level": row.risk_level,
            "completion_criteria": row.completion_criteria,
            "source_event_id": row.source_event_id,
            "created_at": row.created_at,
        }

    def _serialize_attention_turn(self, row: AionAttentionTurn) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "conversation_key": row.conversation_key,
            "turn_id": row.turn_id,
            "status": row.status,
            "source_count": row.source_count,
            "assembled_text": row.assembled_text,
            "owner_mode": row.owner_mode,
            "messages": list(row.messages_json or []),
            "event_ids": list(row.event_ids_json or []),
            "update_keys": list(row.update_keys_json or []),
            "updated_at": row.updated_at,
            "created_at": row.created_at,
        }

    def _serialize_semantic_embedding(self, row: AionSemanticEmbedding) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "source_kind": row.source_kind,
            "source_id": row.source_id,
            "source_event_id": row.source_event_id,
            "scope_type": row.scope_type,
            "scope_key": row.scope_key,
            "content": row.content,
            "embedding": list(row.embedding or []),
            "embedding_model": row.embedding_model,
            "embedding_dimensions": row.embedding_dimensions,
            "metadata": row.metadata_json or {},
            "updated_at": row.updated_at,
            "created_at": row.created_at,
        }

    def _serialize_relation(self, row: AionRelation) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "relation_type": row.relation_type,
            "relation_value": row.relation_value,
            "confidence": row.confidence,
            "source": row.source,
            "scope_type": row.scope_type,
            "scope_key": row.scope_key,
            "supporting_event_id": row.supporting_event_id,
            "evidence_count": row.evidence_count,
            "decay_rate": row.decay_rate,
            "last_observed_at": row.last_observed_at,
            "updated_at": row.updated_at,
            "created_at": row.created_at,
        }

    def _serialize_relation_with_revalidation(self, *, row: AionRelation, now: datetime) -> dict | None:
        revalidated_confidence = self._revalidated_relation_confidence(row=row, now=now)
        if revalidated_confidence <= self.RELATION_EXPIRATION_CONFIDENCE:
            return None

        serialized = self._serialize_relation(row)
        raw_confidence = float(serialized.get("confidence", 0.0) or 0.0)
        serialized["confidence_raw"] = raw_confidence
        serialized["confidence"] = revalidated_confidence
        serialized["revalidation_state"] = "refreshed" if revalidated_confidence >= raw_confidence else "weakened"
        return serialized

    def _revalidated_relation_confidence(self, *, row: AionRelation, now: datetime) -> float:
        raw_confidence = max(0.0, min(1.0, float(row.confidence or 0.0)))
        decay_rate = max(0.0, min(1.0, float(row.decay_rate or 0.0)))
        if decay_rate <= 0.0:
            return raw_confidence

        observed_at = self._coerce_datetime(row.last_observed_at) or self._coerce_datetime(row.updated_at)
        if observed_at is None:
            return raw_confidence

        age_seconds = max(0.0, (now - observed_at).total_seconds())
        age_days = age_seconds / 86400.0
        if age_days <= 0.0:
            return raw_confidence

        evidence_count = max(1, int(row.evidence_count or 1))
        decay_scale = self._relation_decay_scale(evidence_count=evidence_count)
        decayed_confidence = raw_confidence - (age_days * decay_rate * decay_scale)
        return max(0.0, min(1.0, round(decayed_confidence, 4)))

    def _relation_decay_scale(self, *, evidence_count: int) -> float:
        return 1.0 / min(
            self.RELATION_DECAY_EVIDENCE_CAP,
            1.0 + (max(0, evidence_count - 1) * self.RELATION_DECAY_EVIDENCE_WEIGHT),
        )

    def _blended_decay_rate(
        self,
        *,
        current_decay_rate: float,
        incoming_decay_rate: float,
        incoming_evidence_count: int,
    ) -> float:
        current = max(0.0, min(1.0, float(current_decay_rate)))
        incoming = max(0.0, min(1.0, float(incoming_decay_rate)))
        incoming_weight = min(0.75, 0.2 + (0.05 * max(1, int(incoming_evidence_count))))
        return max(0.0, min(1.0, round((current * (1.0 - incoming_weight)) + (incoming * incoming_weight), 4)))

    def _serialize_subconscious_proposal(self, row: AionSubconsciousProposal) -> dict:
        return {
            "proposal_id": row.id,
            "user_id": row.user_id,
            "proposal_type": row.proposal_type,
            "summary": row.summary,
            "payload": row.payload or {},
            "confidence": row.confidence,
            "source_event_id": row.source_event_id,
            "status": row.status,
            "decision_reason": row.decision_reason,
            "research_policy": row.research_policy,
            "allowed_tools": list(row.allowed_tools_json or []),
            "decided_at": row.decided_at,
            "updated_at": row.updated_at,
            "created_at": row.created_at,
        }

    async def _build_proactive_scheduler_candidate(
        self,
        *,
        user_id: str,
        proactive_interval_seconds: int,
    ) -> dict | None:
        active_goals, active_tasks, recent_memory = await self._load_proactive_candidate_state(user_id=user_id)
        if not active_goals and not active_tasks and not recent_memory:
            return None

        chat_id = self._proactive_delivery_target(user_id=user_id, recent_memory=recent_memory)
        if chat_id is None:
            return None

        blocked_tasks = [
            task for task in active_tasks if str(task.get("status", "")).strip().lower() == "blocked"
        ]
        if blocked_tasks:
            trigger = "task_blocked"
            text = f"follow up on blocked task {blocked_tasks[0].get('name', '')}".strip()
        elif active_goals:
            trigger = "goal_stagnation"
            text = f"check progress for goal {active_goals[0].get('name', '')}".strip()
        else:
            trigger = "time_checkin"
            text = "time check-in follow up"

        recent_outbound_count = self._recent_proactive_outbound_count(
            recent_memory=recent_memory,
            proactive_interval_seconds=proactive_interval_seconds,
        )
        unanswered_proactive_count = self._unanswered_proactive_count(recent_memory=recent_memory)
        relations = await self.get_user_relations(user_id=user_id, limit=8)
        boundary_block_reason = proactive_boundary_block_reason(
            relations=relations,
            trigger=trigger,
            recent_outbound_count=recent_outbound_count,
            unanswered_proactive_count=unanswered_proactive_count,
        )
        if boundary_block_reason is not None:
            return None

        return {
            "user_id": user_id,
            "chat_id": chat_id,
            "trigger": trigger,
            "text": text[:160],
            "recent_outbound_count": recent_outbound_count,
            "unanswered_proactive_count": unanswered_proactive_count,
            "recent_user_activity": self._recent_user_activity(
                recent_memory=recent_memory,
                proactive_interval_seconds=proactive_interval_seconds,
            ),
            "active_goal_count": len(active_goals),
            "active_task_count": len(active_tasks),
            "blocked_task_count": len(blocked_tasks),
        }

    async def _load_proactive_candidate_state(self, *, user_id: str) -> tuple[list[dict], list[dict], list[dict]]:
        active_goals = await self.get_active_goals(user_id=user_id, limit=5)
        goal_ids = [int(goal["id"]) for goal in active_goals if goal.get("id") is not None]
        active_tasks = await self.get_active_tasks(user_id=user_id, goal_ids=goal_ids, limit=6)
        recent_memory = await self.get_recent_for_user(user_id=user_id, limit=12)
        return active_goals, active_tasks, recent_memory

    def _proactive_delivery_target(self, *, user_id: str, recent_memory: list[dict]) -> int | str | None:
        for item in recent_memory:
            payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
            chat_id = payload.get("chat_id")
            if isinstance(chat_id, int):
                return chat_id
            if isinstance(chat_id, str) and chat_id.strip():
                return chat_id.strip()
        if str(user_id).strip().isdigit():
            return str(user_id).strip()
        return None

    def _recent_proactive_outbound_count(
        self,
        *,
        recent_memory: list[dict],
        proactive_interval_seconds: int,
    ) -> int:
        now = datetime.now(timezone.utc)
        count = 0
        for item in recent_memory:
            if not self._is_delivered_scheduler_outreach(item):
                continue
            payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
            timestamp = self._coerce_datetime(item.get("timestamp") or item.get("event_timestamp"))
            if timestamp is None:
                continue
            age_seconds = max(0.0, (now - timestamp).total_seconds())
            if age_seconds <= max(1800, int(proactive_interval_seconds)):
                count += 1
        return count

    def _unanswered_proactive_count(self, *, recent_memory: list[dict]) -> int:
        count = 0
        for item in recent_memory:
            if not self._is_conversation_turn_memory(item):
                continue
            if self._is_delivered_scheduler_outreach(item):
                count += 1
                continue
            if self._is_user_authored_turn(item):
                break
        return count

    def _recent_user_activity(
        self,
        *,
        recent_memory: list[dict],
        proactive_interval_seconds: int,
    ) -> str:
        now = datetime.now(timezone.utc)
        for item in recent_memory:
            if not self._is_user_authored_turn(item):
                continue
            timestamp = self._coerce_datetime(item.get("timestamp") or item.get("event_timestamp"))
            if timestamp is None:
                return "unknown"
            age_seconds = max(0.0, (now - timestamp).total_seconds())
            if age_seconds <= max(1800, int(proactive_interval_seconds)):
                return "active"
            if age_seconds <= max(3600, int(proactive_interval_seconds) * 2):
                return "idle"
            return "away"
        return "unknown"

    def _goal_priority_rank(self, priority: str) -> int:
        return {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }.get(priority, 0)

    def _task_priority_rank(self, priority: str) -> int:
        return {
            "low": 1,
            "medium": 2,
            "high": 3,
        }.get(priority, 0)

    def _task_status_rank(self, status: str) -> int:
        return {
            "todo": 1,
            "in_progress": 2,
            "blocked": 3,
        }.get(status, 0)

    def _goal_milestone_phase_rank(self, phase: str) -> int:
        return {
            "early_stage": 1,
            "execution_phase": 2,
            "recovery_phase": 3,
            "completion_window": 4,
        }.get(phase, 0)

    def _hybrid_tokens(self, value: str) -> set[str]:
        canonical = "".join(char if char.isalnum() or char.isspace() else " " for char in str(value).strip().lower())
        return {token for token in canonical.split() if len(token) >= 3}

    def _hybrid_overlap_score(self, text: str, query_tokens: set[str]) -> float:
        if not query_tokens:
            return 0.0
        tokens = self._hybrid_tokens(text)
        if not tokens:
            return 0.0
        overlap = len(tokens.intersection(query_tokens))
        return float(overlap) / float(max(1, len(query_tokens)))

    def _hybrid_episodic_score(self, *, item: dict, query_tokens: set[str]) -> float:
        summary = str(item.get("summary", ""))
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
        content = f"{summary} {payload.get('event', '')} {' '.join(payload.get('memory_topics', []) if isinstance(payload.get('memory_topics'), list) else [])}"
        lexical = self._hybrid_overlap_score(content, query_tokens)
        importance = float(item.get("importance", 0.0) or 0.0)
        return lexical * 1.25 + importance * 0.35

    def _hybrid_semantic_score(self, *, item: dict, query_tokens: set[str], vector_similarity: float) -> float:
        content = str(item.get("content", ""))
        lexical = self._hybrid_overlap_score(content, query_tokens)
        confidence = float(item.get("confidence", 0.0) or 0.0)
        return lexical * 0.8 + float(vector_similarity) * 1.6 + confidence * 0.2

    def _normalize_match_text(self, value: str) -> str:
        lowered = " ".join(value.strip().lower().split())
        return "".join(char if char.isalnum() or char.isspace() else " " for char in lowered).strip()

    def _retry_backoff_seconds_for_attempts(self, attempts: int, retry_backoff_seconds: tuple[int, ...]) -> int:
        if attempts <= 0:
            return 0
        index = min(attempts - 1, len(retry_backoff_seconds) - 1)
        return retry_backoff_seconds[index]

    def _goal_milestone_name(self, phase: str) -> str:
        return {
            "early_stage": "Establish goal foundation",
            "execution_phase": "Sustain active execution",
            "recovery_phase": "Stabilize goal recovery",
            "completion_window": "Drive goal to closure",
        }.get(phase, "Advance goal milestone")

    def _next_recurrence_at(
        self,
        *,
        row: AionPlannedWorkItem,
        evaluated_at: datetime,
    ) -> datetime | None:
        recurrence_mode = str(row.recurrence_mode or "none").strip().lower()
        base_at = self._coerce_datetime(row.preferred_at) or self._coerce_datetime(row.not_before) or evaluated_at
        if recurrence_mode == "daily":
            return base_at + timedelta(days=1)
        if recurrence_mode == "weekly":
            return base_at + timedelta(days=7)
        if recurrence_mode == "custom":
            recurrence_rule = str(row.recurrence_rule or "").strip().lower()
            match = re.search(r"interval_days:(\d+)", recurrence_rule)
            if match is None:
                return None
            interval_days = max(1, int(match.group(1)))
            return base_at + timedelta(days=interval_days)
        return None

    def _coerce_datetime(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _serialize_auth_user(self, row: AionAuthUser | None) -> dict | None:
        if row is None:
            return None
        return {
            "id": row.id,
            "email": row.email,
            "password_hash": row.password_hash,
            "display_name": row.display_name,
            "is_active": bool(row.is_active),
            "last_login_at": row.last_login_at,
            "updated_at": row.updated_at,
            "created_at": row.created_at,
        }

    def _serialize_profile(self, row: AionProfile | None) -> dict | None:
        if row is None:
            return None
        return {
            "user_id": row.user_id,
            "preferred_language": row.preferred_language,
            "ui_language": row.ui_language,
            "utc_offset": normalize_utc_offset(row.utc_offset),
            "language_confidence": row.language_confidence,
            "language_source": row.language_source,
            "telegram_chat_id": row.telegram_chat_id,
            "telegram_user_id": row.telegram_user_id,
            "telegram_link_code": row.telegram_link_code,
            "telegram_link_code_issued_at": row.telegram_link_code_issued_at,
            "telegram_linked_at": row.telegram_linked_at,
            "updated_at": row.updated_at,
        }

    def _serialize_auth_session(self, row: AionAuthSession | None) -> dict | None:
        if row is None:
            return None
        return {
            "id": row.id,
            "user_id": row.user_id,
            "session_token_hash": row.session_token_hash,
            "expires_at": row.expires_at,
            "revoked_at": row.revoked_at,
            "last_seen_at": row.last_seen_at,
            "user_agent": row.user_agent,
            "ip_address": row.ip_address,
            "created_at": row.created_at,
        }
