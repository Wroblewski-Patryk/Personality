from app.memory.embeddings import embedding_strategy_snapshot, normalize_embedding_source_kinds


def test_embedding_strategy_snapshot_marks_no_warning_when_deterministic_provider_is_ready() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=True,
        provider="deterministic",
        model="deterministic-v1",
        dimensions=32,
    )

    assert snapshot["semantic_embedding_provider_ready"] is True
    assert snapshot["semantic_embedding_posture"] == "ready"
    assert snapshot["semantic_embedding_source_coverage_state"] == "full_for_current_retrieval_path"
    assert snapshot["semantic_embedding_source_coverage_hint"] == "semantic_and_affective_sources_enabled"
    assert snapshot["semantic_embedding_source_rollout_state"] == "semantic_affective_baseline"
    assert snapshot["semantic_embedding_source_rollout_hint"] == "high_signal_sources_active"
    assert (
        snapshot["semantic_embedding_source_rollout_recommendation"]
        == "add_relation_source_after_baseline_stabilizes"
    )
    assert snapshot["semantic_embedding_warning_state"] == "no_warning"
    assert snapshot["semantic_embedding_warning_hint"] == "embedding_strategy_ready"
    assert snapshot["semantic_embedding_provider_ownership_state"] == "deterministic_baseline_owner"
    assert (
        snapshot["semantic_embedding_provider_ownership_hint"]
        == "deterministic_provider_owns_embedding_execution"
    )
    assert snapshot["semantic_embedding_provider_ownership_enforcement"] == "warn"
    assert snapshot["semantic_embedding_provider_ownership_enforcement_state"] == "not_applicable_no_fallback"
    assert (
        snapshot["semantic_embedding_provider_ownership_enforcement_hint"]
        == "no_provider_ownership_violation"
    )
    assert snapshot["semantic_embedding_owner_strategy_state"] == "deterministic_on_write_owner"
    assert snapshot["semantic_embedding_owner_strategy_hint"] == "deterministic_baseline_owner_active"
    assert (
        snapshot["semantic_embedding_owner_strategy_recommendation"]
        == "deterministic_on_write_baseline_is_active"
    )
    assert snapshot["semantic_embedding_model_governance_state"] == "model_contract_aligned"
    assert (
        snapshot["semantic_embedding_model_governance_hint"]
        == "embedding_model_contract_aligned_with_provider"
    )
    assert snapshot["semantic_embedding_model_governance_enforcement"] == "warn"
    assert snapshot["semantic_embedding_model_governance_enforcement_state"] == "not_applicable_aligned"
    assert (
        snapshot["semantic_embedding_model_governance_enforcement_hint"]
        == "no_model_governance_violation"
    )
    assert snapshot["semantic_embedding_refresh_mode"] == "on_write"
    assert snapshot["semantic_embedding_refresh_interval_seconds"] == 21600
    assert snapshot["semantic_embedding_refresh_state"] == "on_write_refresh_active"
    assert snapshot["semantic_embedding_refresh_hint"] == "refresh_on_write_enabled"


def test_embedding_strategy_snapshot_marks_vectors_disabled_warning_state() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=False,
        provider="deterministic",
        model="deterministic-v1",
        dimensions=16,
    )

    assert snapshot["semantic_retrieval_mode"] == "lexical_only"
    assert snapshot["semantic_embedding_source_coverage_state"] == "vectors_disabled"
    assert snapshot["semantic_embedding_source_coverage_hint"] == "not_applicable_vectors_disabled"
    assert snapshot["semantic_embedding_source_rollout_state"] == "vectors_disabled"
    assert snapshot["semantic_embedding_source_rollout_hint"] == "enable_vectors_before_source_rollout"
    assert (
        snapshot["semantic_embedding_source_rollout_recommendation"]
        == "defer_source_rollout_until_vectors_enabled"
    )
    assert snapshot["semantic_embedding_warning_state"] == "vectors_disabled"
    assert (
        snapshot["semantic_embedding_warning_hint"]
        == "enable_semantic_vectors_to_activate_embedding_strategy"
    )
    assert snapshot["semantic_embedding_provider_ownership_state"] == "vectors_disabled"
    assert snapshot["semantic_embedding_provider_ownership_hint"] == "not_applicable_vectors_disabled"
    assert snapshot["semantic_embedding_provider_ownership_enforcement"] == "warn"
    assert (
        snapshot["semantic_embedding_provider_ownership_enforcement_state"]
        == "not_applicable_vectors_disabled"
    )
    assert (
        snapshot["semantic_embedding_provider_ownership_enforcement_hint"]
        == "not_applicable_vectors_disabled"
    )
    assert snapshot["semantic_embedding_owner_strategy_state"] == "vectors_disabled"
    assert snapshot["semantic_embedding_owner_strategy_hint"] == "enable_vectors_before_owner_strategy_rollout"
    assert (
        snapshot["semantic_embedding_owner_strategy_recommendation"]
        == "defer_owner_strategy_selection_until_vectors_enabled"
    )
    assert snapshot["semantic_embedding_model_governance_state"] == "vectors_disabled"
    assert snapshot["semantic_embedding_model_governance_hint"] == "not_applicable_vectors_disabled"
    assert snapshot["semantic_embedding_model_governance_enforcement"] == "warn"
    assert (
        snapshot["semantic_embedding_model_governance_enforcement_state"]
        == "not_applicable_vectors_disabled"
    )
    assert (
        snapshot["semantic_embedding_model_governance_enforcement_hint"]
        == "not_applicable_vectors_disabled"
    )
    assert snapshot["semantic_embedding_refresh_state"] == "vectors_disabled"
    assert snapshot["semantic_embedding_refresh_hint"] == "not_applicable_vectors_disabled"


def test_embedding_strategy_snapshot_marks_provider_fallback_warning_state() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=True,
        provider="openai",
        model="text-embedding-3-small",
        dimensions=1536,
    )

    assert snapshot["semantic_embedding_provider_ready"] is False
    assert snapshot["semantic_embedding_posture"] == "fallback_deterministic"
    assert snapshot["semantic_embedding_provider_effective"] == "deterministic"
    assert snapshot["semantic_embedding_model_effective"] == "deterministic-v1"
    assert snapshot["semantic_embedding_warning_state"] == "provider_fallback_active"
    assert (
        snapshot["semantic_embedding_warning_hint"]
        == "provider_not_implemented_using_deterministic_fallback"
    )
    assert snapshot["semantic_embedding_provider_ownership_state"] == "provider_fallback_active"
    assert (
        snapshot["semantic_embedding_provider_ownership_hint"]
        == "requested_provider_not_effective_owner"
    )
    assert snapshot["semantic_embedding_provider_ownership_enforcement"] == "warn"
    assert snapshot["semantic_embedding_provider_ownership_enforcement_state"] == "warning_only"
    assert (
        snapshot["semantic_embedding_provider_ownership_enforcement_hint"]
        == "fallback_allowed_in_warn_mode"
    )
    assert snapshot["semantic_embedding_owner_strategy_state"] == "fallback_owner_active"
    assert snapshot["semantic_embedding_owner_strategy_hint"] == "requested_provider_not_effective_owner"
    assert (
        snapshot["semantic_embedding_owner_strategy_recommendation"]
        == "keep_deterministic_owner_until_provider_execution_is_available"
    )
    assert snapshot["semantic_embedding_model_governance_state"] == "provider_fallback_effective_model"
    assert (
        snapshot["semantic_embedding_model_governance_hint"]
        == "effective_model_controlled_by_fallback_provider"
    )
    assert snapshot["semantic_embedding_model_governance_enforcement"] == "warn"
    assert snapshot["semantic_embedding_model_governance_enforcement_state"] == "not_applicable_aligned"
    assert (
        snapshot["semantic_embedding_model_governance_enforcement_hint"]
        == "no_model_governance_violation"
    )


def test_embedding_strategy_snapshot_marks_missing_source_coverage_when_semantic_and_affective_are_disabled() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=True,
        provider="deterministic",
        model="deterministic-v1",
        dimensions=32,
        source_kinds=("episodic", "relation"),
    )

    assert snapshot["semantic_embedding_source_kinds"] == ["episodic", "relation"]
    assert snapshot["semantic_embedding_source_coverage_state"] == "missing_for_current_retrieval_path"
    assert (
        snapshot["semantic_embedding_source_coverage_hint"]
        == "enable_semantic_or_affective_source_for_vector_hits"
    )
    assert snapshot["semantic_embedding_source_rollout_state"] == "foundational_sources_only"
    assert snapshot["semantic_embedding_source_rollout_hint"] == "semantic_and_affective_sources_missing"
    assert (
        snapshot["semantic_embedding_source_rollout_recommendation"]
        == "enable_semantic_then_affective_sources"
    )


def test_embedding_strategy_snapshot_marks_semantic_only_source_rollout_phase() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=True,
        provider="deterministic",
        model="deterministic-v1",
        dimensions=32,
        source_kinds=("episodic", "semantic"),
    )

    assert snapshot["semantic_embedding_source_rollout_state"] == "semantic_only_phase"
    assert snapshot["semantic_embedding_source_rollout_hint"] == "affective_source_missing"
    assert snapshot["semantic_embedding_source_rollout_recommendation"] == "enable_affective_source_next"


def test_embedding_strategy_snapshot_marks_affective_only_source_rollout_phase() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=True,
        provider="deterministic",
        model="deterministic-v1",
        dimensions=32,
        source_kinds=("episodic", "affective"),
    )

    assert snapshot["semantic_embedding_source_rollout_state"] == "affective_only_phase"
    assert snapshot["semantic_embedding_source_rollout_hint"] == "semantic_source_missing"
    assert snapshot["semantic_embedding_source_rollout_recommendation"] == "enable_semantic_source_next"


def test_embedding_strategy_snapshot_marks_manual_refresh_posture_when_manual_mode_is_requested() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=True,
        provider="deterministic",
        model="deterministic-v1",
        dimensions=32,
        refresh_mode="manual",
        refresh_interval_seconds=7200,
    )

    assert snapshot["semantic_embedding_refresh_mode"] == "manual"
    assert snapshot["semantic_embedding_refresh_interval_seconds"] == 7200
    assert snapshot["semantic_embedding_refresh_state"] == "manual_refresh_required"
    assert snapshot["semantic_embedding_refresh_hint"] == "ensure_manual_refresh_process_is_defined"


def test_embedding_strategy_snapshot_marks_deterministic_custom_model_governance_posture() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=True,
        provider="deterministic",
        model="deterministic-v2",
        dimensions=32,
    )

    assert snapshot["semantic_embedding_model_requested"] == "deterministic-v2"
    assert snapshot["semantic_embedding_model_effective"] == "deterministic-v2"
    assert snapshot["semantic_embedding_model_governance_state"] == "deterministic_custom_model_name"
    assert (
        snapshot["semantic_embedding_model_governance_hint"]
        == "deterministic_provider_uses_fixed_embedding_behavior"
    )
    assert snapshot["semantic_embedding_model_governance_enforcement"] == "warn"
    assert snapshot["semantic_embedding_model_governance_enforcement_state"] == "warning_only"
    assert (
        snapshot["semantic_embedding_model_governance_enforcement_hint"]
        == "custom_model_name_allowed_in_warn_mode"
    )
    assert snapshot["semantic_embedding_owner_strategy_state"] == "deterministic_on_write_owner"


def test_embedding_strategy_snapshot_marks_provider_ownership_enforcement_blocked_in_strict_mode() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=True,
        provider="openai",
        model="text-embedding-3-small",
        dimensions=1536,
        provider_ownership_enforcement="strict",
    )

    assert snapshot["semantic_embedding_provider_ownership_enforcement"] == "strict"
    assert snapshot["semantic_embedding_provider_ownership_enforcement_state"] == "blocked"
    assert (
        snapshot["semantic_embedding_provider_ownership_enforcement_hint"]
        == "switch_to_effective_provider_owner_before_startup"
    )
    assert snapshot["semantic_embedding_owner_strategy_state"] == "fallback_owner_active"


def test_embedding_strategy_snapshot_marks_model_governance_enforcement_blocked_in_strict_mode() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=True,
        provider="deterministic",
        model="deterministic-v2",
        dimensions=32,
        model_governance_enforcement="strict",
    )

    assert snapshot["semantic_embedding_model_governance_enforcement"] == "strict"
    assert snapshot["semantic_embedding_model_governance_enforcement_state"] == "blocked"
    assert (
        snapshot["semantic_embedding_model_governance_enforcement_hint"]
        == "use_deterministic_v1_or_switch_to_effective_provider_model"
    )


def test_embedding_strategy_snapshot_marks_deterministic_manual_owner_strategy_when_manual_refresh_is_enabled() -> None:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=True,
        provider="deterministic",
        model="deterministic-v1",
        dimensions=32,
        refresh_mode="manual",
        refresh_interval_seconds=7200,
    )

    assert snapshot["semantic_embedding_owner_strategy_state"] == "deterministic_manual_owner"
    assert snapshot["semantic_embedding_owner_strategy_hint"] == "manual_refresh_required_for_deterministic_owner"
    assert (
        snapshot["semantic_embedding_owner_strategy_recommendation"]
        == "document_and_operate_manual_refresh_process"
    )


def test_normalize_embedding_source_kinds_returns_defaults_when_missing() -> None:
    assert normalize_embedding_source_kinds(None) == ("episodic", "semantic", "affective")
    assert normalize_embedding_source_kinds("") == ("episodic", "semantic", "affective")


def test_normalize_embedding_source_kinds_normalizes_order_and_uniqueness() -> None:
    assert normalize_embedding_source_kinds("relation,episodic,episodic") == ("episodic", "relation")
