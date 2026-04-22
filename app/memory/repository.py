from datetime import datetime, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.contracts import MemoryLayerKind
from app.core.reflection_scope_policy import (
    GLOBAL_SCOPE_KEY,
    GLOBAL_SCOPE_TYPE,
    canonicalize_conclusion_scope,
    canonicalize_relation_scope,
    conclusion_matches_scope_request,
    relation_matches_scope_request,
)
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
    AionConclusion,
    AionGoal,
    AionGoalMilestone,
    AionGoalMilestoneHistory,
    AionGoalProgress,
    AionMemory,
    AionProfile,
    AionRelation,
    AionReflectionTask,
    AionSemanticEmbedding,
    AionSubconsciousProposal,
    AionTask,
    AionTheta,
    Base,
)


class MemoryRepository:
    ACTIVE_GOAL_STATUSES = ("active",)
    ACTIVE_TASK_STATUSES = ("todo", "in_progress", "blocked")
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
    GLOBAL_SCOPE_TYPE = GLOBAL_SCOPE_TYPE
    GLOBAL_SCOPE_KEY = GLOBAL_SCOPE_KEY

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
                source_kinds=["semantic", "affective", "relation"],
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

    async def get_recent_for_user(self, user_id: str, limit: int = 5) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionMemory)
                .where(AionMemory.user_id == user_id)
                .order_by(AionMemory.id.desc())
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

    async def get_user_profile(self, user_id: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionProfile, user_id)

        if row is None:
            return None

        return {
            "user_id": row.user_id,
            "preferred_language": row.preferred_language,
            "language_confidence": row.language_confidence,
            "language_source": row.language_source,
            "updated_at": row.updated_at,
        }

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
            "language_confidence": row.language_confidence,
            "language_source": row.language_source,
            "updated_at": row.updated_at,
        }

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

    def _serialize_memory(self, row: AionMemory) -> dict:
        return {
            "id": row.id,
            "event_id": row.event_id,
            "timestamp": row.event_timestamp,
            "summary": row.summary,
            "payload": row.payload or {},
            "importance": row.importance,
        }

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

    def _coerce_datetime(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
