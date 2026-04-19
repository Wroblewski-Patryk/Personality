from app.core.contracts import (
    EmbeddingRecord,
    SemanticRetrievalHit,
    SemanticRetrievalQuery,
    SemanticRetrievalResult,
)


def test_semantic_retrieval_contract_models_round_trip() -> None:
    query = SemanticRetrievalQuery(
        user_id="u-1",
        query_text="help me with deployment blocker",
        query_embedding=[0.12, 0.44, 0.91],
        limit=4,
        source_kinds=["episodic", "semantic", "affective"],
        scope_type="goal",
        scope_key="11",
    )
    hit = SemanticRetrievalHit(
        source_kind="episodic",
        source_id="mem-77",
        content="deploy blocker workaround",
        score=0.87,
        lexical_score=0.4,
        vector_score=0.47,
        affective_score=0.0,
        metadata={"memory_kind": "semantic"},
    )
    result = SemanticRetrievalResult(
        query=query,
        hits=[hit],
        diagnostics={"vector_hits": 1, "lexical_hits": 1},
    )
    record = EmbeddingRecord(
        id=1,
        user_id="u-1",
        source_kind="episodic",
        source_id="mem-77",
        content="deploy blocker workaround",
        embedding=[0.12, 0.44, 0.91],
        embedding_model="deterministic-v1",
        embedding_dimensions=3,
        metadata={"memory_kind": "semantic"},
    )

    dumped = result.model_dump(mode="python")
    assert dumped["query"]["scope_type"] == "goal"
    assert dumped["hits"][0]["source_kind"] == "episodic"
    assert dumped["diagnostics"]["vector_hits"] == 1
    assert record.embedding_dimensions == 3
