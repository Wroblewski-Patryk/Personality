from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.memory.models import (
    AionAttentionTurn,
    AionConclusion,
    AionGoal,
    AionGoalMilestone,
    AionGoalMilestoneHistory,
    AionGoalProgress,
    AionMemory,
    AionPlannedWorkItem,
    AionRelation,
    AionReflectionTask,
    AionSchedulerCadenceEvidence,
    AionSemanticEmbedding,
    AionSubconsciousProposal,
    AionTask,
)
from app.memory.repository import MemoryRepository


class FakeOpenAIEmbeddingClient:
    def __init__(self):
        self.calls: list[dict[str, object]] = []

    @property
    def ready(self) -> bool:
        return True

    async def create_embedding(self, *, text: str, model: str, dimensions: int) -> list[float]:
        self.calls.append(
            {
                "text": text,
                "model": model,
                "dimensions": dimensions,
            }
        )
        return [0.25] * dimensions


async def test_memory_repository_persists_structured_episode_payload(tmp_path) -> None:
    database_path = tmp_path / "memory-episodic-payload.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    written = await repository.write_episode(
        event_id="evt-1",
        trace_id="trace-1",
        source="api",
        user_id="u-1",
        event_timestamp=datetime.now(timezone.utc),
        summary="User said 'deploy the fix now'.",
        payload={
            "payload_version": 1,
            "event": "deploy the fix now",
            "memory_kind": "semantic",
            "memory_topics": ["deploy", "fix"],
            "response_language": "en",
            "plan_steps": ["reply"],
            "action": "success",
            "expression": "Let's deploy it.",
        },
        importance=0.81,
    )

    recent = await repository.get_recent_for_user(user_id="u-1", limit=5)

    assert written["payload"]["memory_kind"] == "semantic"
    assert written["payload"]["memory_topics"] == ["deploy", "fix"]
    assert recent[0]["payload"]["plan_steps"] == ["reply"]

    async with session_factory() as session:
        row = await session.get(AionMemory, int(written["id"]))

    assert row is not None
    assert row.payload is not None
    assert row.payload["response_language"] == "en"

    await engine.dispose()


async def test_memory_repository_exposes_memory_layer_vocabulary_and_conclusion_mapping(tmp_path) -> None:
    database_path = tmp_path / "memory-layer-vocabulary.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    assert repository.memory_layer_vocabulary() == (
        "episodic",
        "semantic",
        "affective",
        "operational",
    )
    assert repository.conclusion_memory_layer("affective_support_pattern") == "affective"
    assert repository.conclusion_memory_layer("goal_milestone_risk") == "operational"
    assert repository.conclusion_memory_layer("custom_semantic_fact") == "semantic"


async def test_memory_repository_persists_attention_turn_contract_store_and_cleans_up_answered_rows(tmp_path) -> None:
    database_path = tmp_path / "memory-attention-turn-store.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    stored = await repository.upsert_attention_turn(
        user_id="u-1",
        conversation_key="telegram:123",
        turn_id="turn-1",
        status="pending",
        messages=["first message"],
        event_ids=["evt-1"],
        update_keys=["update:1"],
        source_count=1,
        owner_mode="durable_inbox",
    )
    claimed = await repository.upsert_attention_turn(
        user_id="u-1",
        conversation_key="telegram:123",
        turn_id="turn-1",
        status="claimed",
        messages=["first message", "second message"],
        event_ids=["evt-1", "evt-2"],
        update_keys=["update:1", "update:2"],
        source_count=2,
        assembled_text="first message\nsecond message",
        owner_mode="durable_inbox",
    )

    loaded = await repository.get_attention_turn(user_id="u-1", conversation_key="telegram:123")
    stats = await repository.get_attention_turn_stats(
        answered_ttl_seconds=5.0,
        stale_turn_seconds=30.0,
    )

    assert stored["status"] == "pending"
    assert claimed["status"] == "claimed"
    assert loaded is not None
    assert loaded["assembled_text"] == "first message\nsecond message"
    assert loaded["source_count"] == 2
    assert stats["pending"] == 0
    assert stats["claimed"] == 1
    assert stats["answered"] == 0
    assert stats["active_turns"] == 1

    answered = await repository.upsert_attention_turn(
        user_id="u-1",
        conversation_key="telegram:123",
        turn_id="turn-1",
        status="answered",
        messages=["first message", "second message"],
        event_ids=["evt-1", "evt-2"],
        update_keys=["update:1", "update:2"],
        source_count=2,
        assembled_text="first message\nsecond message",
        owner_mode="durable_inbox",
    )

    async with session_factory() as session:
        row = await session.get(AionAttentionTurn, int(answered["id"]))
        assert row is not None
        row.updated_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        await session.commit()

    stale_stats = await repository.get_attention_turn_stats(
        answered_ttl_seconds=5.0,
        stale_turn_seconds=30.0,
    )
    cleanup = await repository.cleanup_attention_turns(
        answered_ttl_seconds=5.0,
        stale_turn_seconds=30.0,
    )
    after_cleanup = await repository.get_attention_turn(user_id="u-1", conversation_key="telegram:123")

    assert stale_stats["answered_cleanup_candidates"] == 1
    assert cleanup == {"deleted_answered": 1, "deleted_stale": 0}
    assert after_cleanup is None

    await engine.dispose()


async def test_memory_repository_persists_scheduler_cadence_evidence_contract_store(tmp_path) -> None:
    database_path = tmp_path / "memory-scheduler-cadence-evidence.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    stored = await repository.upsert_scheduler_cadence_evidence(
        cadence_kind="maintenance",
        execution_owner="external_scheduler",
        execution_mode="externalized",
        summary={
            "executed": True,
            "reason": "external_scheduler_owner",
            "entrypoint_owner": "external_scheduler",
            "idempotency_baseline": "single_tick_summary_per_invocation",
        },
    )
    loaded = await repository.get_scheduler_cadence_evidence(cadence_kind="maintenance")

    assert stored["cadence_kind"] == "maintenance"
    assert stored["execution_owner"] == "external_scheduler"
    assert stored["execution_mode"] == "externalized"
    assert loaded is not None
    assert loaded["summary"]["reason"] == "external_scheduler_owner"
    assert loaded["summary"]["idempotency_baseline"] == "single_tick_summary_per_invocation"

    async with session_factory() as session:
        row = await session.get(AionSchedulerCadenceEvidence, int(stored["id"]))

    assert row is not None
    assert row.cadence_kind == "maintenance"
    assert row.execution_owner == "external_scheduler"

    await engine.dispose()


async def test_memory_repository_upserts_and_queries_semantic_embeddings(tmp_path) -> None:
    database_path = tmp_path / "memory-semantic-embeddings.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    first = await repository.upsert_semantic_embedding(
        user_id="u-1",
        source_kind="episodic",
        source_id="mem-1",
        source_event_id="evt-1",
        scope_type="global",
        scope_key="global",
        content="deploy blocker workaround",
        embedding=[1.0, 0.0, 0.0],
        embedding_model="test-v1",
        embedding_dimensions=3,
        metadata={"memory_kind": "semantic"},
    )
    second = await repository.upsert_semantic_embedding(
        user_id="u-1",
        source_kind="semantic",
        source_id="conclusion-1",
        source_event_id="evt-2",
        scope_type="goal",
        scope_key="11",
        content="goal execution recovering",
        embedding=[0.0, 1.0, 0.0],
        embedding_model="test-v1",
        embedding_dimensions=3,
        metadata={"kind": "goal_execution_state"},
    )
    third = await repository.upsert_semantic_embedding(
        user_id="u-1",
        source_kind="affective",
        source_id="aff-1",
        source_event_id="evt-3",
        scope_type="global",
        scope_key="global",
        content="recurring distress pattern",
        embedding=[0.8, 0.2, 0.0],
        embedding_model="test-v1",
        embedding_dimensions=3,
        metadata={"kind": "affective_support_pattern"},
    )

    hits = await repository.query_semantic_similarity(
        user_id="u-1",
        query_embedding=[0.9, 0.1, 0.0],
        source_kinds=["episodic", "affective"],
        limit=3,
    )

    assert first["source_kind"] == "episodic"
    assert second["scope_type"] == "goal"
    assert second["scope_key"] == "11"
    assert third["source_kind"] == "affective"
    assert hits[0]["source_id"] in {"mem-1", "aff-1"}
    assert hits[0]["similarity"] >= hits[1]["similarity"]

    await engine.dispose()


async def test_memory_repository_upsert_conclusion_materializes_affective_embedding_on_write(tmp_path) -> None:
    database_path = tmp_path / "memory-conclusion-embedding-shell.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="affective_support_pattern",
        content="recurring_distress",
        confidence=0.81,
        source="background_reflection",
        supporting_event_id="evt-aff",
    )

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].source_kind == "affective"
    assert rows[0].source_id.startswith("conclusion:")
    assert isinstance(rows[0].embedding, list)
    assert len(rows[0].embedding) == 32
    assert rows[0].embedding_model == "deterministic-v1"
    assert rows[0].embedding_dimensions == 32
    assert rows[0].metadata_json["embedding_status"] == "materialized_on_write"
    assert rows[0].metadata_json["embedding_refresh_mode"] == "on_write"
    assert rows[0].metadata_json["embedding_provider_requested"] == "deterministic"
    assert rows[0].metadata_json["embedding_provider_effective"] == "deterministic"
    assert rows[0].metadata_json["embedding_provider_hint"] == "deterministic_baseline"

    await engine.dispose()


async def test_memory_repository_upsert_conclusion_materializes_semantic_embedding_on_write(tmp_path) -> None:
    database_path = tmp_path / "memory-conclusion-embedding-on-write.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="custom_semantic_fact",
        content="deployment blockers require explicit rollback paths",
        confidence=0.77,
        source="background_reflection",
        supporting_event_id="evt-semantic-on-write",
    )

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].source_kind == "semantic"
    assert isinstance(rows[0].embedding, list)
    assert len(rows[0].embedding) == 32
    assert rows[0].embedding_model == "deterministic-v1"
    assert rows[0].embedding_dimensions == 32
    assert rows[0].metadata_json["embedding_status"] == "materialized_on_write"
    assert rows[0].metadata_json["embedding_refresh_mode"] == "on_write"
    assert rows[0].metadata_json["embedding_provider_requested"] == "deterministic"
    assert rows[0].metadata_json["embedding_provider_effective"] == "deterministic"
    assert rows[0].metadata_json["embedding_provider_hint"] == "deterministic_baseline"

    await engine.dispose()


async def test_memory_repository_upsert_conclusion_uses_effective_embedding_posture_when_provider_is_not_implemented(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory-conclusion-embedding-fallback.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(
        session_factory=session_factory,
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=24,
    )
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="custom_semantic_fact",
        content="deployment blockers require explicit rollback paths",
        confidence=0.77,
        source="background_reflection",
        supporting_event_id="evt-sem-shell",
    )

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].source_kind == "semantic"
    assert isinstance(rows[0].embedding, list)
    assert len(rows[0].embedding) == 24
    assert rows[0].embedding_model == "deterministic-v1"
    assert rows[0].embedding_dimensions == 24
    assert rows[0].metadata_json["embedding_provider_requested"] == "openai"
    assert rows[0].metadata_json["embedding_provider_effective"] == "deterministic"
    assert (
        rows[0].metadata_json["embedding_provider_hint"]
        == "openai_api_key_missing_fallback_deterministic"
    )
    assert rows[0].metadata_json["embedding_model_requested"] == "text-embedding-3-small"
    assert rows[0].metadata_json["embedding_model_effective"] == "deterministic-v1"
    assert rows[0].metadata_json["embedding_status"] == "materialized_on_write"
    assert rows[0].metadata_json["embedding_refresh_mode"] == "on_write"

    await engine.dispose()


async def test_memory_repository_upsert_conclusion_keeps_semantic_embedding_pending_in_manual_refresh_mode(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory-conclusion-embedding-manual-refresh.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(
        session_factory=session_factory,
        embedding_refresh_mode="manual",
    )
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="custom_semantic_fact",
        content="deployment blockers require explicit rollback paths",
        confidence=0.77,
        source="background_reflection",
        supporting_event_id="evt-semantic-manual",
    )

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].source_kind == "semantic"
    assert rows[0].embedding is None
    assert rows[0].embedding_model == "deterministic-v1"
    assert rows[0].embedding_dimensions == 32
    assert rows[0].metadata_json["embedding_status"] == "pending_manual_refresh"
    assert rows[0].metadata_json["embedding_refresh_mode"] == "manual"

    await engine.dispose()


async def test_memory_repository_materializes_local_hybrid_embedding_provider_when_selected(tmp_path) -> None:
    database_path = tmp_path / "memory-conclusion-embedding-local-hybrid.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(
        session_factory=session_factory,
        embedding_provider="local_hybrid",
        embedding_model="local-hybrid-v1",
        embedding_dimensions=16,
    )
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="custom_semantic_fact",
        content="release evidence must verify topology and ingress posture",
        confidence=0.82,
        source="background_reflection",
        supporting_event_id="evt-local-hybrid",
    )

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].embedding_model == "local-hybrid-v1"
    assert rows[0].embedding_dimensions == 16
    assert rows[0].metadata_json["embedding_provider_requested"] == "local_hybrid"
    assert rows[0].metadata_json["embedding_provider_effective"] == "local_hybrid"
    assert rows[0].metadata_json["embedding_provider_hint"] == "local_provider_execution"
    assert rows[0].metadata_json["embedding_status"] == "materialized_by_local_hybrid_provider"

    await engine.dispose()


async def test_memory_repository_materializes_openai_embedding_provider_when_selected_and_configured(tmp_path) -> None:
    database_path = tmp_path / "memory-conclusion-embedding-openai.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    embedding_client = FakeOpenAIEmbeddingClient()
    repository = MemoryRepository(
        session_factory=session_factory,
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=12,
        openai_api_key="test-openai-key",
        openai_embedding_client=embedding_client,
    )
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="custom_semantic_fact",
        content="provider owned retrieval should use real embeddings when configured",
        confidence=0.84,
        source="background_reflection",
        supporting_event_id="evt-openai-provider",
    )

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].embedding_model == "text-embedding-3-small"
    assert rows[0].embedding_dimensions == 12
    assert rows[0].metadata_json["embedding_provider_requested"] == "openai"
    assert rows[0].metadata_json["embedding_provider_effective"] == "openai"
    assert rows[0].metadata_json["embedding_provider_hint"] == "openai_api_embeddings"
    assert rows[0].metadata_json["embedding_status"] == "materialized_by_openai_provider"
    assert embedding_client.calls == [
        {
            "text": "provider owned retrieval should use real embeddings when configured",
            "model": "text-embedding-3-small",
            "dimensions": 12,
        }
    ]

    await engine.dispose()


async def test_memory_repository_upsert_conclusion_keeps_affective_embedding_pending_in_manual_refresh_mode(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory-affective-embedding-manual-refresh.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(
        session_factory=session_factory,
        embedding_refresh_mode="manual",
    )
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="affective_support_pattern",
        content="recurring_distress",
        confidence=0.81,
        source="background_reflection",
        supporting_event_id="evt-affective-manual",
    )

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].source_kind == "affective"
    assert rows[0].embedding is None
    assert rows[0].embedding_model == "deterministic-v1"
    assert rows[0].embedding_dimensions == 32
    assert rows[0].metadata_json["embedding_status"] == "pending_manual_refresh"
    assert rows[0].metadata_json["embedding_refresh_mode"] == "manual"

    await engine.dispose()


async def test_memory_repository_upsert_conclusion_skips_embedding_shell_when_source_kind_is_disabled(tmp_path) -> None:
    database_path = tmp_path / "memory-conclusion-embedding-source-kind-disabled.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(
        session_factory=session_factory,
        embedding_source_kinds=("episodic",),
    )
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="custom_semantic_fact",
        content="deployment blockers require dependency sequencing",
        confidence=0.72,
        source="background_reflection",
        supporting_event_id="evt-semantic-no-shell",
    )
    await repository.upsert_conclusion(
        user_id="u-1",
        kind="affective_support_pattern",
        content="recurring_distress",
        confidence=0.81,
        source="background_reflection",
        supporting_event_id="evt-affective-no-shell",
    )

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert rows == []

    await engine.dispose()


async def test_memory_repository_builds_hybrid_memory_bundle_with_vector_and_lexical_diagnostics(tmp_path) -> None:
    database_path = tmp_path / "memory-hybrid-bundle.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.write_episode(
        event_id="evt-1",
        trace_id="trace-1",
        source="api",
        user_id="u-1",
        event_timestamp=datetime.now(timezone.utc),
        summary="User said 'fix deploy blocker'.",
        payload={
            "event": "fix deploy blocker",
            "memory_topics": ["deploy", "blocker"],
            "memory_kind": "semantic",
            "response_language": "en",
        },
        importance=0.9,
    )
    await repository.upsert_conclusion(
        user_id="u-1",
        kind="custom_semantic_fact",
        content="deployment blockers usually require dependency sequencing",
        confidence=0.75,
        source="background_reflection",
        supporting_event_id="evt-1",
    )
    await repository.upsert_semantic_embedding(
        user_id="u-1",
        source_kind="semantic",
        source_id="conclusion:vector-1",
        source_event_id="evt-1",
        scope_type="global",
        scope_key="global",
        content="deployment blockers usually require dependency sequencing",
        embedding=[1.0, 0.0, 0.0],
        embedding_model="test-v1",
        embedding_dimensions=3,
        metadata={"kind": "custom_semantic_fact"},
    )

    bundle = await repository.get_hybrid_memory_bundle(
        user_id="u-1",
        query_text="deploy blocker sequencing",
        query_embedding=[0.95, 0.05, 0.0],
        episodic_limit=4,
        conclusion_limit=4,
    )

    assert len(bundle["episodic"]) == 1
    assert any("deploy" in str(item.get("summary", "")).lower() for item in bundle["episodic"])
    assert len(bundle["semantic"]) >= 1
    assert bundle["diagnostics"]["episodic_candidates"] >= 1
    assert bundle["diagnostics"]["semantic_candidates"] >= 1
    assert bundle["diagnostics"]["vector_hits"] >= 1

    await engine.dispose()


async def test_memory_repository_keeps_relation_embeddings_out_of_default_foreground_retrieval_baseline(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory-hybrid-relation-optional.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="custom_semantic_fact",
        content="structured replies should stay explicit",
        confidence=0.82,
        source="background_reflection",
        supporting_event_id="evt-sem-1",
    )
    await repository.upsert_semantic_embedding(
        user_id="u-1",
        source_kind="relation",
        source_id="relation:manual-1",
        source_event_id="evt-rel-1",
        scope_type="global",
        scope_key="global",
        content="collaboration_dynamic guided",
        embedding=[0.95, 0.05, 0.0],
        embedding_model="test-v1",
        embedding_dimensions=3,
        metadata={"relation_type": "collaboration_dynamic"},
    )

    bundle = await repository.get_hybrid_memory_bundle(
        user_id="u-1",
        query_text="explicit structured reply please",
        query_embedding=[0.95, 0.05, 0.0],
        episodic_limit=4,
        conclusion_limit=4,
    )

    assert len(bundle["semantic"]) >= 1
    assert bundle["diagnostics"]["vector_hits"] == 1
    assert bundle["diagnostics"]["semantic_candidates"] >= 1

    await engine.dispose()


async def test_memory_repository_upserts_and_reads_scoped_relations(tmp_path) -> None:
    database_path = tmp_path / "memory-relations.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_relation(
        user_id="u-1",
        relation_type="communication_style_alignment",
        relation_value="guided",
        confidence=0.78,
        source="background_reflection",
        supporting_event_id="evt-rel-1",
    )
    await repository.upsert_relation(
        user_id="u-1",
        relation_type="goal_execution_trust",
        relation_value="high_trust",
        confidence=0.74,
        source="background_reflection",
        supporting_event_id="evt-rel-2",
        scope_type="goal",
        scope_key="11",
    )

    goal_relations = await repository.get_user_relations(
        user_id="u-1",
        scope_type="goal",
        scope_key="11",
        include_global=True,
    )
    strict_goal_relations = await repository.get_user_relations(
        user_id="u-1",
        scope_type="goal",
        scope_key="11",
        include_global=False,
    )

    assert any(item["relation_type"] == "communication_style_alignment" for item in goal_relations)
    assert any(item["relation_type"] == "goal_execution_trust" for item in goal_relations)
    assert len(strict_goal_relations) == 1
    assert strict_goal_relations[0]["scope_type"] == "goal"
    assert strict_goal_relations[0]["scope_key"] == "11"

    async with session_factory() as session:
        embedding_rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert embedding_rows == []

    await engine.dispose()


async def test_memory_repository_upsert_relation_materializes_embedding_when_relation_source_is_enabled(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory-relations-embedding.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(
        session_factory=session_factory,
        embedding_source_kinds=("episodic", "semantic", "affective", "relation"),
    )
    await repository.create_tables(engine)

    await repository.upsert_relation(
        user_id="u-1",
        relation_type="collaboration_dynamic",
        relation_value="guided",
        confidence=0.78,
        source="background_reflection",
        supporting_event_id="evt-rel-embed",
    )

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].source_kind == "relation"
    assert rows[0].source_id.startswith("relation:")
    assert isinstance(rows[0].embedding, list)
    assert len(rows[0].embedding) == 32
    assert rows[0].metadata_json["embedding_status"] == "materialized_on_write"
    assert rows[0].metadata_json["embedding_refresh_mode"] == "on_write"
    assert rows[0].metadata_json["relation_type"] == "collaboration_dynamic"
    assert rows[0].metadata_json["relation_value"] == "guided"

    await engine.dispose()


async def test_memory_repository_upsert_relation_keeps_embedding_pending_in_manual_refresh_mode(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory-relations-embedding-manual.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(
        session_factory=session_factory,
        embedding_source_kinds=("episodic", "semantic", "affective", "relation"),
        embedding_refresh_mode="manual",
    )
    await repository.create_tables(engine)

    await repository.upsert_relation(
        user_id="u-1",
        relation_type="collaboration_dynamic",
        relation_value="guided",
        confidence=0.78,
        source="background_reflection",
        supporting_event_id="evt-rel-manual",
    )

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionSemanticEmbedding).order_by(AionSemanticEmbedding.id.asc())
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].source_kind == "relation"
    assert rows[0].embedding is None
    assert rows[0].metadata_json["embedding_status"] == "pending_manual_refresh"
    assert rows[0].metadata_json["embedding_refresh_mode"] == "manual"

    await engine.dispose()


async def test_memory_repository_refreshes_relation_with_repeated_quality_evidence(tmp_path) -> None:
    database_path = tmp_path / "memory-relations-refresh.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    first = await repository.upsert_relation(
        user_id="u-1",
        relation_type="delivery_reliability",
        relation_value="high_trust",
        confidence=0.72,
        source="background_reflection",
        supporting_event_id="evt-rel-refresh-1",
        evidence_count=1,
        decay_rate=0.04,
    )
    refreshed = await repository.upsert_relation(
        user_id="u-1",
        relation_type="delivery_reliability",
        relation_value="high_trust",
        confidence=0.86,
        source="background_reflection",
        supporting_event_id="evt-rel-refresh-2",
        evidence_count=3,
        decay_rate=0.02,
    )

    assert refreshed["confidence"] > first["confidence"]
    assert refreshed["evidence_count"] == 4
    assert refreshed["supporting_event_id"] == "evt-rel-refresh-2"
    assert refreshed["decay_rate"] < first["decay_rate"]

    await engine.dispose()


async def test_memory_repository_resets_relation_lifecycle_when_relation_value_changes(tmp_path) -> None:
    database_path = tmp_path / "memory-relations-value-shift.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_relation(
        user_id="u-1",
        relation_type="delivery_reliability",
        relation_value="high_trust",
        confidence=0.88,
        source="background_reflection",
        supporting_event_id="evt-rel-shift-1",
        evidence_count=4,
        decay_rate=0.02,
    )

    async with session_factory() as session:
        row = (
            await session.execute(
                select(AionRelation).where(
                    AionRelation.user_id == "u-1",
                    AionRelation.relation_type == "delivery_reliability",
                )
            )
        ).scalar_one()
        row.last_observed_at = datetime.now(timezone.utc) - timedelta(days=5)
        await session.commit()

    shifted = await repository.upsert_relation(
        user_id="u-1",
        relation_type="delivery_reliability",
        relation_value="low_trust",
        confidence=0.63,
        source="background_reflection",
        supporting_event_id="evt-rel-shift-2",
        evidence_count=2,
        decay_rate=0.07,
    )

    assert shifted["relation_value"] == "low_trust"
    assert shifted["confidence"] == 0.63
    assert shifted["evidence_count"] == 2
    assert shifted["decay_rate"] == 0.07
    assert shifted["supporting_event_id"] == "evt-rel-shift-2"

    visible = await repository.get_user_relations(user_id="u-1", min_confidence=0.0)
    assert len(visible) == 1
    assert visible[0]["relation_value"] == "low_trust"
    assert visible[0]["confidence_raw"] == 0.63
    assert visible[0]["evidence_count"] == 2
    assert visible[0]["decay_rate"] == 0.07
    assert visible[0]["revalidation_state"] == "refreshed"

    await engine.dispose()


async def test_memory_repository_revalidates_relation_confidence_and_expires_stale_rows(tmp_path) -> None:
    database_path = tmp_path / "memory-relations-revalidation.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_relation(
        user_id="u-1",
        relation_type="delivery_reliability",
        relation_value="high_trust",
        confidence=0.9,
        source="background_reflection",
        supporting_event_id="evt-rel-revalidate-1",
        evidence_count=1,
        decay_rate=0.08,
    )

    async with session_factory() as session:
        row = (
            await session.execute(
                select(AionRelation).where(
                    AionRelation.user_id == "u-1",
                    AionRelation.relation_type == "delivery_reliability",
                )
            )
        ).scalar_one()
        row.last_observed_at = datetime.now(timezone.utc) - timedelta(days=2)
        await session.commit()

    weakened = await repository.get_user_relations(
        user_id="u-1",
        min_confidence=0.0,
    )
    assert len(weakened) == 1
    assert weakened[0]["confidence"] < 0.9
    assert weakened[0]["confidence_raw"] == 0.9
    assert weakened[0]["revalidation_state"] == "weakened"

    async with session_factory() as session:
        row = (
            await session.execute(
                select(AionRelation).where(
                    AionRelation.user_id == "u-1",
                    AionRelation.relation_type == "delivery_reliability",
                )
            )
        ).scalar_one()
        row.last_observed_at = datetime.now(timezone.utc) - timedelta(days=40)
        await session.commit()

    expired = await repository.get_user_relations(
        user_id="u-1",
        min_confidence=0.0,
    )
    assert expired == []

    await engine.dispose()


async def test_memory_repository_persists_and_resolves_subconscious_proposals(tmp_path) -> None:
    database_path = tmp_path / "memory-subconscious-proposals.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    first = await repository.upsert_subconscious_proposal(
        user_id="u-1",
        proposal_type="research_topic",
        summary="Research deployment rollback constraints.",
        payload={"topic": "deployment rollback constraints"},
        confidence=0.72,
        source_event_id="evt-proposal-1",
        research_policy="read_only",
        allowed_tools=["memory_retrieval", "knowledge_search"],
    )
    second = await repository.upsert_subconscious_proposal(
        user_id="u-1",
        proposal_type="research_topic",
        summary="Research deployment rollback constraints.",
        payload={"topic": "deployment rollback constraints", "detail": "recent incidents"},
        confidence=0.78,
        source_event_id="evt-proposal-2",
        research_policy="read_only",
        allowed_tools=["knowledge_search"],
    )

    pending = await repository.get_pending_subconscious_proposals(user_id="u-1", limit=5)
    resolved = await repository.resolve_subconscious_proposal(
        proposal_id=int(second["proposal_id"]),
        decision="accept",
        reason="confirmed by conscious planning",
    )
    pending_after = await repository.get_pending_subconscious_proposals(user_id="u-1", limit=5)

    assert int(first["proposal_id"]) == int(second["proposal_id"])
    assert len(pending) == 1
    assert pending[0]["summary"] == "Research deployment rollback constraints."
    assert pending[0]["confidence"] == 0.78
    assert pending[0]["research_policy"] == "read_only"
    assert pending[0]["allowed_tools"] == ["knowledge_search"]
    assert resolved is not None
    assert resolved["status"] == "accepted"
    assert resolved["decision_reason"] == "confirmed by conscious planning"
    assert pending_after == []

    async with session_factory() as session:
        rows = (await session.execute(select(AionSubconsciousProposal))).scalars().all()

    assert len(rows) == 1
    assert rows[0].status == "accepted"
    assert rows[0].decision_reason == "confirmed by conscious planning"

    await engine.dispose()


async def test_memory_repository_reenters_deferred_subconscious_proposals_in_pending_query(tmp_path) -> None:
    database_path = tmp_path / "memory-subconscious-proposals-deferred.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    created = await repository.upsert_subconscious_proposal(
        user_id="u-1",
        proposal_type="ask_user",
        summary="Ask whether rollout blocker still reproduces.",
        payload={"question_focus": "rollout blocker status"},
        confidence=0.68,
        source_event_id="evt-proposal-deferred-1",
        research_policy="read_only",
        allowed_tools=["memory_retrieval"],
    )
    deferred = await repository.resolve_subconscious_proposal(
        proposal_id=int(created["proposal_id"]),
        decision="defer",
        reason="wait_for_next_conscious_turn",
    )
    retriable = await repository.get_pending_subconscious_proposals(user_id="u-1", limit=5)
    replayed = await repository.upsert_subconscious_proposal(
        user_id="u-1",
        proposal_type="ask_user",
        summary="Ask whether rollout blocker still reproduces.",
        payload={"question_focus": "rollout blocker status", "scope": "next check-in"},
        confidence=0.74,
        source_event_id="evt-proposal-deferred-2",
        research_policy="read_only",
        allowed_tools=["memory_retrieval", "knowledge_search"],
    )
    accepted = await repository.resolve_subconscious_proposal(
        proposal_id=int(replayed["proposal_id"]),
        decision="accept",
        reason="confirmed by conscious follow-up",
    )
    retriable_after_accept = await repository.get_pending_subconscious_proposals(user_id="u-1", limit=5)

    assert deferred is not None
    assert deferred["status"] == "deferred"
    assert deferred["decision_reason"] == "wait_for_next_conscious_turn"
    assert len(retriable) == 1
    assert retriable[0]["proposal_id"] == created["proposal_id"]
    assert retriable[0]["status"] == "deferred"
    assert replayed["proposal_id"] == created["proposal_id"]
    assert replayed["status"] == "deferred"
    assert replayed["confidence"] == 0.74
    assert replayed["allowed_tools"] == ["memory_retrieval", "knowledge_search"]
    assert accepted is not None
    assert accepted["status"] == "accepted"
    assert retriable_after_accept == []

    async with session_factory() as session:
        rows = (await session.execute(select(AionSubconsciousProposal))).scalars().all()

    assert len(rows) == 1
    assert rows[0].status == "accepted"

    await engine.dispose()


async def test_memory_repository_can_read_conclusions_by_memory_layer(tmp_path) -> None:
    database_path = tmp_path / "memory-layer-read.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="response_style",
        content="structured",
        confidence=0.92,
        source="background_reflection",
        supporting_event_id="evt-style",
    )
    await repository.upsert_conclusion(
        user_id="u-1",
        kind="affective_support_pattern",
        content="recurring_distress",
        confidence=0.79,
        source="background_reflection",
        supporting_event_id="evt-affective",
    )
    await repository.upsert_conclusion(
        user_id="u-1",
        kind="custom_semantic_fact",
        content="user works on deployment docs",
        confidence=0.71,
        source="background_reflection",
        supporting_event_id="evt-semantic",
    )

    affective = await repository.get_conclusions_for_layer(
        user_id="u-1",
        layer="affective",
        limit=5,
    )
    operational = await repository.get_conclusions_for_layer(
        user_id="u-1",
        layer="operational",
        limit=5,
    )
    semantic = await repository.get_conclusions_for_layer(
        user_id="u-1",
        layer="semantic",
        limit=5,
    )
    operational_view = await repository.get_operational_memory_view(user_id="u-1")

    assert [item["kind"] for item in affective] == ["affective_support_pattern"]
    assert [item["kind"] for item in operational] == ["response_style"]
    assert [item["kind"] for item in semantic] == ["custom_semantic_fact"]
    assert operational_view["response_style"] == "structured"

    await engine.dispose()


async def test_memory_repository_reports_reflection_task_stats(tmp_path) -> None:
    database_path = tmp_path / "memory-repository.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    pending = await repository.enqueue_reflection_task(user_id="u-1", event_id="evt-pending")
    processing = await repository.enqueue_reflection_task(user_id="u-1", event_id="evt-processing")
    retryable_failed = await repository.enqueue_reflection_task(user_id="u-1", event_id="evt-retryable")
    exhausted_failed = await repository.enqueue_reflection_task(user_id="u-1", event_id="evt-exhausted")
    completed = await repository.enqueue_reflection_task(user_id="u-1", event_id="evt-completed")

    await repository.mark_reflection_task_processing(task_id=int(processing["id"]))
    await repository.mark_reflection_task_processing(task_id=int(retryable_failed["id"]))
    await repository.mark_reflection_task_failed(task_id=int(retryable_failed["id"]), error="temporary issue")
    await repository.mark_reflection_task_processing(task_id=int(exhausted_failed["id"]))
    await repository.mark_reflection_task_failed(task_id=int(exhausted_failed["id"]), error="still failing")
    await repository.mark_reflection_task_processing(task_id=int(exhausted_failed["id"]))
    await repository.mark_reflection_task_failed(task_id=int(exhausted_failed["id"]), error="final failure")
    await repository.mark_reflection_task_processing(task_id=int(exhausted_failed["id"]))
    await repository.mark_reflection_task_failed(task_id=int(exhausted_failed["id"]), error="final final failure")
    await repository.mark_reflection_task_processing(task_id=int(completed["id"]))
    await repository.mark_reflection_task_completed(task_id=int(completed["id"]))

    now = datetime.now(timezone.utc)
    async with session_factory() as session:
        processing_row = await session.get(AionReflectionTask, int(processing["id"]))
        retryable_failed_row = await session.get(AionReflectionTask, int(retryable_failed["id"]))
        exhausted_failed_row = await session.get(AionReflectionTask, int(exhausted_failed["id"]))
        pending_row = await session.get(AionReflectionTask, int(pending["id"]))
        assert processing_row is not None
        assert retryable_failed_row is not None
        assert exhausted_failed_row is not None
        assert pending_row is not None
        processing_row.updated_at = now - timedelta(seconds=240)
        retryable_failed_row.updated_at = now - timedelta(seconds=40)
        exhausted_failed_row.updated_at = now - timedelta(minutes=5)
        pending_row.updated_at = now - timedelta(seconds=10)
        await session.commit()

    stats = await repository.get_reflection_task_stats(
        max_attempts=3,
        stuck_after_seconds=180,
        retry_backoff_seconds=(5, 30, 120),
        now=now,
    )

    assert stats == {
        "total": 5,
        "pending": 1,
        "processing": 1,
        "completed": 1,
        "failed": 2,
        "retryable_failed": 1,
        "exhausted_failed": 1,
        "stuck_processing": 1,
    }

    async with session_factory() as session:
        result = await session.execute(select(AionReflectionTask).order_by(AionReflectionTask.id.asc()))
        rows = result.scalars().all()

    assert [row.status for row in rows] == ["pending", "processing", "failed", "failed", "completed"]

    await engine.dispose()


async def test_memory_repository_upserts_and_loads_active_goals_and_tasks(tmp_path) -> None:
    database_path = tmp_path / "memory-goals.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    goal = await repository.upsert_active_goal(
        user_id="u-1",
        name="ship the MVP this week",
        description="User-declared goal: ship the MVP this week",
        priority="high",
        goal_type="operational",
    )
    task = await repository.upsert_active_task(
        user_id="u-1",
        goal_id=int(goal["id"]),
        name="fix deployment blocker",
        description="User-declared task: fix deployment blocker",
        priority="high",
        status="blocked",
    )

    goals = await repository.get_active_goals(user_id="u-1", limit=5)
    tasks = await repository.get_active_tasks(user_id="u-1", goal_ids=[int(goal["id"])], limit=5)

    assert goals[0]["name"] == "ship the MVP this week"
    assert goals[0]["priority"] == "high"
    assert tasks[0]["name"] == "fix deployment blocker"
    assert tasks[0]["goal_id"] == goal["id"]
    assert tasks[0]["status"] == "blocked"

    async with session_factory() as session:
        goal_rows = (await session.execute(select(AionGoal))).scalars().all()
        task_rows = (await session.execute(select(AionTask))).scalars().all()

    assert len(goal_rows) == 1
    assert len(task_rows) == 1

    await engine.dispose()


async def test_memory_repository_updates_task_status_and_removes_done_from_active_list(tmp_path) -> None:
    database_path = tmp_path / "memory-task-status.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    task = await repository.upsert_active_task(
        user_id="u-1",
        name="fix deployment blocker",
        description="User-declared task: fix deployment blocker",
        priority="high",
        status="blocked",
    )

    updated = await repository.update_task_status(task_id=int(task["id"]), status="done")
    active_tasks = await repository.get_active_tasks(user_id="u-1", limit=5)

    assert updated is not None
    assert updated["status"] == "done"
    assert active_tasks == []

    async with session_factory() as session:
        task_row = await session.get(AionTask, int(task["id"]))

    assert task_row is not None
    assert task_row.status == "done"

    await engine.dispose()


async def test_memory_repository_syncs_and_loads_active_goal_milestones(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestones.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    goal = await repository.upsert_active_goal(
        user_id="u-1",
        name="ship the MVP this week",
        description="User-declared goal: ship the MVP this week",
        priority="high",
        goal_type="operational",
    )

    first = await repository.sync_goal_milestone(
        user_id="u-1",
        goal_id=int(goal["id"]),
        phase="execution_phase",
        source_event_id="evt-execution-phase",
    )
    second = await repository.sync_goal_milestone(
        user_id="u-1",
        goal_id=int(goal["id"]),
        phase="completion_window",
        source_event_id="evt-completion-window",
    )

    milestones = await repository.get_active_goal_milestones(user_id="u-1", goal_ids=[int(goal["id"])], limit=5)

    assert first["phase"] == "execution_phase"
    assert second["phase"] == "completion_window"
    assert milestones[0]["phase"] == "completion_window"
    assert milestones[0]["name"] == "Drive goal to closure"

    async with session_factory() as session:
        rows = (await session.execute(select(AionGoalMilestone).order_by(AionGoalMilestone.id.asc()))).scalars().all()

    assert [row.status for row in rows] == ["completed", "active"]
    await engine.dispose()


async def test_memory_repository_appends_and_reads_goal_milestone_history(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-history.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    first = await repository.append_goal_milestone_history(
        user_id="u-1",
        goal_id=11,
        milestone_name="Stabilize goal recovery",
        phase="recovery_phase",
        risk_level="stabilizing",
        completion_criteria="stabilize_remaining_work",
        source_event_id="evt-1",
    )
    second = await repository.append_goal_milestone_history(
        user_id="u-1",
        goal_id=11,
        milestone_name="Stabilize goal recovery",
        phase="recovery_phase",
        risk_level="stabilizing",
        completion_criteria="stabilize_remaining_work",
        source_event_id="evt-2",
    )
    third = await repository.append_goal_milestone_history(
        user_id="u-1",
        goal_id=11,
        milestone_name="Drive goal to closure",
        phase="completion_window",
        risk_level="ready_to_close",
        completion_criteria="finish_remaining_active_work",
        source_event_id="evt-3",
    )

    history = await repository.get_recent_goal_milestone_history(user_id="u-1", goal_ids=[11], limit=5)

    assert first["id"] == second["id"]
    assert third["phase"] == "completion_window"
    assert history[0]["phase"] == "completion_window"
    assert history[1]["phase"] == "recovery_phase"

    async with session_factory() as session:
        rows = (
            await session.execute(select(AionGoalMilestoneHistory).order_by(AionGoalMilestoneHistory.id.asc()))
        ).scalars().all()

    assert len(rows) == 2

    await engine.dispose()


async def test_memory_repository_exposes_goal_execution_state_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-execution-state.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_execution_state",
                content="blocked",
                confidence=0.82,
                source="background_reflection",
                supporting_event_id="evt-goal-blocked",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_execution_state"] == "blocked"
    assert preferences["goal_execution_state_confidence"] == 0.82
    assert preferences["goal_execution_state_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_affective_reflection_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-affective-preferences.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="affective_support_pattern",
        content="recurring_distress",
        confidence=0.76,
        source="background_reflection",
        supporting_event_id="evt-aff-pattern",
    )
    await repository.upsert_conclusion(
        user_id="u-1",
        kind="affective_support_sensitivity",
        content="high",
        confidence=0.78,
        source="background_reflection",
        supporting_event_id="evt-aff-sensitivity",
    )

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["affective_support_pattern"] == "recurring_distress"
    assert preferences["affective_support_pattern_confidence"] == 0.76
    assert preferences["affective_support_sensitivity"] == "high"
    assert preferences["affective_support_sensitivity_confidence"] == 0.78

    await engine.dispose()


async def test_memory_repository_allows_dynamic_goal_execution_state_transition(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-execution-transition.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_execution_state",
        content="blocked",
        confidence=0.82,
        source="background_reflection",
        supporting_event_id="evt-blocked",
    )
    updated = await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_execution_state",
        content="progressing",
        confidence=0.76,
        source="background_reflection",
        supporting_event_id="evt-progressing",
    )

    assert updated["content"] == "progressing"
    assert updated["confidence"] == 0.76
    assert updated["supporting_event_id"] == "evt-progressing"

    await engine.dispose()


async def test_memory_repository_supports_scoped_goal_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-scoped-preferences.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_execution_state",
        content="stagnating",
        confidence=0.7,
        source="background_reflection",
        supporting_event_id="evt-global",
    )
    await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_execution_state",
        content="recovering",
        confidence=0.77,
        source="background_reflection",
        supporting_event_id="evt-goal-11",
        scope_type="goal",
        scope_key="11",
    )
    await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_execution_state",
        content="blocked",
        confidence=0.82,
        source="background_reflection",
        supporting_event_id="evt-goal-22",
        scope_type="goal",
        scope_key="22",
    )

    global_preferences = await repository.get_user_runtime_preferences(
        user_id="u-1",
        scope_type="global",
        scope_key="global",
    )
    goal_11_preferences = await repository.get_user_runtime_preferences(
        user_id="u-1",
        scope_type="goal",
        scope_key="11",
        include_global=True,
    )
    goal_22_preferences = await repository.get_user_runtime_preferences(
        user_id="u-1",
        scope_type="goal",
        scope_key="22",
        include_global=True,
    )

    assert global_preferences["goal_execution_state"] == "stagnating"
    assert global_preferences["goal_execution_state_scope_type"] == "global"
    assert goal_11_preferences["goal_execution_state"] == "recovering"
    assert goal_11_preferences["goal_execution_state_scope_type"] == "goal"
    assert goal_11_preferences["goal_execution_state_scope_key"] == "11"
    assert goal_22_preferences["goal_execution_state"] == "blocked"
    assert goal_22_preferences["goal_execution_state_scope_key"] == "22"

    await engine.dispose()


async def test_memory_repository_get_user_conclusions_can_filter_by_scope(tmp_path) -> None:
    database_path = tmp_path / "memory-conclusions-scope-filter.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="response_style",
        content="structured",
        confidence=0.9,
        source="background_reflection",
        supporting_event_id="evt-global-style",
    )
    await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_progress_arc",
        content="recovery_gaining_traction",
        confidence=0.76,
        source="background_reflection",
        supporting_event_id="evt-goal-11-arc",
        scope_type="goal",
        scope_key="11",
    )
    await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_progress_arc",
        content="falling_behind",
        confidence=0.78,
        source="background_reflection",
        supporting_event_id="evt-goal-22-arc",
        scope_type="goal",
        scope_key="22",
    )

    goal_only = await repository.get_user_conclusions(
        user_id="u-1",
        limit=5,
        scope_type="goal",
        scope_key="11",
    )
    goal_with_global = await repository.get_user_conclusions(
        user_id="u-1",
        limit=5,
        scope_type="goal",
        scope_key="11",
        include_global=True,
    )

    assert len(goal_only) == 1
    assert goal_only[0]["scope_type"] == "goal"
    assert goal_only[0]["scope_key"] == "11"
    assert goal_only[0]["content"] == "recovery_gaining_traction"
    assert any(item["scope_type"] == "global" and item["kind"] == "response_style" for item in goal_with_global)
    assert any(item["scope_type"] == "goal" and item["scope_key"] == "11" for item in goal_with_global)

    await engine.dispose()


async def test_memory_repository_canonicalizes_global_reflection_conclusions_to_global_scope(tmp_path) -> None:
    database_path = tmp_path / "memory-conclusions-reflection-scope-policy.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    stored = await repository.upsert_conclusion(
        user_id="u-1",
        kind="affective_support_pattern",
        content="recurring_distress",
        confidence=0.76,
        source="background_reflection",
        supporting_event_id="evt-affective-goal-11",
        scope_type="goal",
        scope_key="11",
    )

    goal_only = await repository.get_user_conclusions(
        user_id="u-1",
        limit=5,
        scope_type="goal",
        scope_key="11",
    )
    goal_with_global = await repository.get_user_conclusions(
        user_id="u-1",
        limit=5,
        scope_type="goal",
        scope_key="11",
        include_global=True,
    )
    preferences = await repository.get_user_runtime_preferences(
        user_id="u-1",
        scope_type="goal",
        scope_key="11",
        include_global=True,
    )

    assert stored["scope_type"] == "global"
    assert stored["scope_key"] == "global"
    assert goal_only == []
    assert len(goal_with_global) == 1
    assert goal_with_global[0]["scope_type"] == "global"
    assert preferences["affective_support_pattern"] == "recurring_distress"
    assert preferences["affective_support_pattern_scope_type"] == "global"
    assert preferences["affective_support_pattern_scope_key"] == "global"

    await engine.dispose()


async def test_memory_repository_exposes_goal_progress_score_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-progress-score.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_progress_score",
                content="0.84",
                confidence=0.74,
                source="background_reflection",
                supporting_event_id="evt-goal-progress-score",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_progress_score"] == 0.84
    assert preferences["goal_progress_score_confidence"] == 0.74
    assert preferences["goal_progress_score_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_proactive_opt_in_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-proactive-opt-in.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="proactive_opt_in",
                content="true",
                confidence=0.95,
                source="explicit_request",
                supporting_event_id="evt-proactive-opt-in",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["proactive_opt_in"] is True
    assert preferences["proactive_opt_in_confidence"] == 0.95
    assert preferences["proactive_opt_in_source"] == "explicit_request"

    await engine.dispose()


async def test_memory_repository_exposes_goal_progress_trend_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-progress-trend.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_progress_trend",
                content="improving",
                confidence=0.73,
                source="background_reflection",
                supporting_event_id="evt-goal-progress-trend",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_progress_trend"] == "improving"
    assert preferences["goal_progress_trend_confidence"] == 0.73
    assert preferences["goal_progress_trend_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_goal_milestone_transition_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-transition.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_milestone_transition",
                content="entered_completion_window",
                confidence=0.77,
                source="background_reflection",
                supporting_event_id="evt-goal-milestone-transition",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_milestone_transition"] == "entered_completion_window"
    assert preferences["goal_milestone_transition_confidence"] == 0.77
    assert preferences["goal_milestone_transition_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_allows_dynamic_goal_milestone_transition_updates(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-dynamic.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_milestone_transition",
        content="entered_completion_window",
        confidence=0.77,
        source="background_reflection",
        supporting_event_id="evt-entered-completion",
    )
    updated = await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_milestone_transition",
        content="slipped_from_completion_window",
        confidence=0.78,
        source="background_reflection",
        supporting_event_id="evt-slipped-completion",
    )

    assert updated["content"] == "slipped_from_completion_window"
    assert updated["confidence"] == 0.78
    assert updated["supporting_event_id"] == "evt-slipped-completion"

    await engine.dispose()


async def test_memory_repository_exposes_goal_milestone_state_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-state.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_milestone_state",
                content="completion_window",
                confidence=0.8,
                source="background_reflection",
                supporting_event_id="evt-goal-milestone-state",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_milestone_state"] == "completion_window"
    assert preferences["goal_milestone_state_confidence"] == 0.8
    assert preferences["goal_milestone_state_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_goal_milestone_risk_and_completion_criteria_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-ops.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_milestone_risk",
                content="ready_to_close",
                confidence=0.79,
                source="background_reflection",
                supporting_event_id="evt-goal-milestone-risk",
            )
        )
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_completion_criteria",
                content="finish_remaining_active_work",
                confidence=0.8,
                source="background_reflection",
                supporting_event_id="evt-goal-completion-criteria",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_milestone_risk"] == "ready_to_close"
    assert preferences["goal_milestone_risk_confidence"] == 0.79
    assert preferences["goal_completion_criteria"] == "finish_remaining_active_work"
    assert preferences["goal_completion_criteria_confidence"] == 0.8

    await engine.dispose()


async def test_memory_repository_exposes_goal_milestone_arc_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-arc.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_milestone_arc",
                content="reentered_completion_window",
                confidence=0.79,
                source="background_reflection",
                supporting_event_id="evt-goal-milestone-arc",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_milestone_arc"] == "reentered_completion_window"
    assert preferences["goal_milestone_arc_confidence"] == 0.79
    assert preferences["goal_milestone_arc_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_goal_milestone_pressure_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-pressure.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_milestone_pressure",
                content="lingering_completion",
                confidence=0.8,
                source="background_reflection",
                supporting_event_id="evt-goal-milestone-pressure",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_milestone_pressure"] == "lingering_completion"
    assert preferences["goal_milestone_pressure_confidence"] == 0.8
    assert preferences["goal_milestone_pressure_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_goal_milestone_dependency_state_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-dependency.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_milestone_dependency_state",
                content="multi_step_dependency",
                confidence=0.76,
                source="background_reflection",
                supporting_event_id="evt-goal-milestone-dependency",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_milestone_dependency_state"] == "multi_step_dependency"
    assert preferences["goal_milestone_dependency_state_confidence"] == 0.76
    assert preferences["goal_milestone_dependency_state_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_goal_milestone_due_state_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-due.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_milestone_due_state",
                content="dependency_due_next",
                confidence=0.79,
                source="background_reflection",
                supporting_event_id="evt-goal-milestone-due",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_milestone_due_state"] == "dependency_due_next"
    assert preferences["goal_milestone_due_state_confidence"] == 0.79
    assert preferences["goal_milestone_due_state_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_goal_milestone_due_window_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-due-window.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_milestone_due_window",
                content="overdue_due_window",
                confidence=0.82,
                source="background_reflection",
                supporting_event_id="evt-goal-milestone-due-window",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_milestone_due_window"] == "overdue_due_window"
    assert preferences["goal_milestone_due_window_confidence"] == 0.82
    assert preferences["goal_milestone_due_window_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_goal_progress_arc_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-progress-arc.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_progress_arc",
                content="recovery_gaining_traction",
                confidence=0.76,
                source="background_reflection",
                supporting_event_id="evt-goal-progress-arc",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_progress_arc"] == "recovery_gaining_traction"
    assert preferences["goal_progress_arc_confidence"] == 0.76
    assert preferences["goal_progress_arc_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_runtime_preferences_can_hold_more_than_six_kinds(tmp_path) -> None:
    database_path = tmp_path / "memory-runtime-preferences-limit.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    rows = [
        ("response_style", "structured", 0.95),
        ("preferred_role", "analyst", 0.76),
        ("collaboration_preference", "guided", 0.73),
        ("goal_execution_state", "recovering", 0.77),
        ("goal_progress_score", "0.61", 0.74),
        ("goal_progress_trend", "improving", 0.73),
        ("goal_progress_arc", "recovery_gaining_traction", 0.76),
        ("goal_milestone_arc", "closure_momentum", 0.76),
        ("goal_milestone_pressure", "building_closure_pressure", 0.74),
        ("goal_milestone_dependency_state", "multi_step_dependency", 0.76),
        ("goal_milestone_due_state", "dependency_due_next", 0.79),
        ("goal_milestone_due_window", "active_due_window", 0.73),
        ("goal_milestone_risk", "ready_to_close", 0.79),
        ("goal_completion_criteria", "finish_remaining_active_work", 0.80),
    ]
    async with session_factory() as session:
        for index, (kind, content, confidence) in enumerate(rows, start=1):
            session.add(
                AionConclusion(
                    user_id="u-1",
                    kind=kind,
                    content=content,
                    confidence=confidence,
                    source="background_reflection",
                    supporting_event_id=f"evt-{index}",
                )
            )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["response_style"] == "structured"
    assert preferences["preferred_role"] == "analyst"
    assert preferences["collaboration_preference"] == "guided"
    assert preferences["goal_execution_state"] == "recovering"
    assert preferences["goal_progress_score"] == 0.61
    assert preferences["goal_progress_trend"] == "improving"
    assert preferences["goal_progress_arc"] == "recovery_gaining_traction"
    assert preferences["goal_milestone_arc"] == "closure_momentum"
    assert preferences["goal_milestone_pressure"] == "building_closure_pressure"
    assert preferences["goal_milestone_dependency_state"] == "multi_step_dependency"
    assert preferences["goal_milestone_due_state"] == "dependency_due_next"
    assert preferences["goal_milestone_due_window"] == "active_due_window"
    assert preferences["goal_milestone_risk"] == "ready_to_close"
    assert preferences["goal_completion_criteria"] == "finish_remaining_active_work"

    await engine.dispose()


async def test_memory_repository_appends_and_reads_goal_progress_history(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-progress-history.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    first = await repository.append_goal_progress_snapshot(
        user_id="u-1",
        goal_id=11,
        score=0.28,
        execution_state="blocked",
        progress_trend="slipping",
        source_event_id="evt-1",
    )
    second = await repository.append_goal_progress_snapshot(
        user_id="u-1",
        goal_id=11,
        score=0.28,
        execution_state="blocked",
        progress_trend="slipping",
        source_event_id="evt-2",
    )
    third = await repository.append_goal_progress_snapshot(
        user_id="u-1",
        goal_id=11,
        score=0.61,
        execution_state="recovering",
        progress_trend="improving",
        source_event_id="evt-3",
    )

    history = await repository.get_recent_goal_progress(user_id="u-1", goal_ids=[11], limit=5)

    assert first["id"] == second["id"]
    assert third["score"] == 0.61
    assert [item["score"] for item in history] == [0.61, 0.28]
    assert history[0]["progress_trend"] == "improving"

    async with session_factory() as session:
        rows = (await session.execute(select(AionGoalProgress).order_by(AionGoalProgress.id.asc()))).scalars().all()

    assert len(rows) == 2

    await engine.dispose()


async def test_memory_repository_upserts_and_updates_planned_work_items(tmp_path) -> None:
    database_path = tmp_path / "memory-planned-work.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    preferred_at = datetime(2026, 4, 25, 9, 0, tzinfo=timezone.utc)
    first = await repository.upsert_planned_work_item(
        user_id="u-1",
        kind="reminder",
        summary="send the release summary tomorrow",
        preferred_at=preferred_at,
        delivery_channel="telegram",
        provenance="explicit_user_request",
        source_event_id="evt-plan-1",
    )
    duplicate = await repository.upsert_planned_work_item(
        user_id="u-1",
        kind="reminder",
        summary="send the release summary tomorrow",
        preferred_at=preferred_at,
        delivery_channel="telegram",
        provenance="explicit_user_request",
        source_event_id="evt-plan-2",
    )
    rescheduled_at = datetime(2026, 4, 26, 8, 30, tzinfo=timezone.utc)
    rescheduled = await repository.reschedule_planned_work_item(
        work_id=int(first["id"]),
        preferred_at=rescheduled_at,
    )
    active = await repository.get_active_planned_work(user_id="u-1", limit=5)
    completed = await repository.complete_planned_work_item(work_id=int(first["id"]))

    assert first["id"] == duplicate["id"]
    assert first["kind"] == "reminder"
    assert first["delivery_channel"] == "telegram"
    assert rescheduled is not None
    assert rescheduled["preferred_at"] == rescheduled_at
    assert len(active) == 1
    assert active[0]["summary"] == "send the release summary tomorrow"
    assert completed is not None
    assert completed["status"] == "completed"
    assert await repository.get_active_planned_work(user_id="u-1", limit=5) == []

    async with session_factory() as session:
        rows = (
            await session.execute(
                select(AionPlannedWorkItem).order_by(AionPlannedWorkItem.id.asc())
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].source_event_id == "evt-plan-2"

    await engine.dispose()


async def test_memory_repository_returns_due_planned_work_and_marks_it_due(tmp_path) -> None:
    database_path = tmp_path / "memory-planned-work-due.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    due_at = datetime(2026, 4, 25, 9, 0, tzinfo=timezone.utc)
    await repository.upsert_planned_work_item(
        user_id="u-1",
        kind="reminder",
        summary="send the release summary",
        preferred_at=due_at,
    )
    await repository.upsert_planned_work_item(
        user_id="u-2",
        kind="check_in",
        summary="weekly check-in",
        preferred_at=datetime(2026, 4, 28, 9, 0, tzinfo=timezone.utc),
    )

    due_items = await repository.get_due_planned_work(
        now=datetime(2026, 4, 26, 9, 0, tzinfo=timezone.utc),
        limit=5,
    )
    updated = await repository.mark_planned_work_due(
        work_id=int(due_items[0]["id"]),
        evaluated_at=datetime(2026, 4, 26, 9, 0, tzinfo=timezone.utc),
    )

    assert len(due_items) == 1
    assert due_items[0]["summary"] == "send the release summary"
    assert updated is not None
    assert updated["status"] == "due"
    assert updated["last_evaluated_at"] == datetime(2026, 4, 26, 9, 0, tzinfo=timezone.utc)

    await engine.dispose()


async def test_memory_repository_snoozes_and_advances_recurring_planned_work(tmp_path) -> None:
    database_path = tmp_path / "memory-planned-work-recurring.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    preferred_at = datetime(2026, 4, 25, 8, 0, tzinfo=timezone.utc)
    created = await repository.upsert_planned_work_item(
        user_id="u-1",
        kind="routine",
        summary="daily review inbox",
        preferred_at=preferred_at,
        recurrence_mode="daily",
        quiet_hours_policy="respect_user_context",
    )
    snoozed = await repository.snooze_planned_work_item(
        work_id=int(created["id"]),
        until_at=datetime(2026, 4, 25, 10, 0, tzinfo=timezone.utc),
        evaluated_at=datetime(2026, 4, 25, 7, 30, tzinfo=timezone.utc),
    )
    advanced = await repository.advance_planned_work_recurrence(
        work_id=int(created["id"]),
        evaluated_at=datetime(2026, 4, 25, 10, 5, tzinfo=timezone.utc),
    )

    assert snoozed is not None
    assert snoozed["status"] == "snoozed"
    assert snoozed["preferred_at"] == datetime(2026, 4, 25, 10, 0, tzinfo=timezone.utc)
    assert advanced is not None
    assert advanced["status"] == "pending"
    assert advanced["preferred_at"] == datetime(2026, 4, 26, 10, 0, tzinfo=timezone.utc)
    assert advanced["recurrence_mode"] == "daily"

    await engine.dispose()
