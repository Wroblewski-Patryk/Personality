from __future__ import annotations

import hashlib
import math

DEFAULT_EMBEDDING_PROVIDER = "deterministic"
DEFAULT_EMBEDDING_MODEL = "deterministic-v1"
EMBEDDING_SOURCE_KIND_ORDER = ("episodic", "semantic", "affective", "relation")
DEFAULT_EMBEDDING_SOURCE_KINDS = ("episodic", "semantic", "affective")
EMBEDDING_REFRESH_MODES = ("on_write", "manual")
DEFAULT_EMBEDDING_REFRESH_MODE = "on_write"
DEFAULT_EMBEDDING_REFRESH_INTERVAL_SECONDS = 21600
EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT_MODES = ("warn", "strict")
DEFAULT_EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT = "warn"
EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT_MODES = ("warn", "strict")
DEFAULT_EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT = "warn"
EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT_MODES = ("warn", "strict")
DEFAULT_EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT = "warn"


def resolve_embedding_posture(
    *,
    provider: str | None,
    model: str | None,
) -> dict[str, str]:
    requested_provider = str(provider or DEFAULT_EMBEDDING_PROVIDER).strip().lower() or DEFAULT_EMBEDDING_PROVIDER
    requested_model = str(model or DEFAULT_EMBEDDING_MODEL).strip() or DEFAULT_EMBEDDING_MODEL

    if requested_provider == DEFAULT_EMBEDDING_PROVIDER:
        return {
            "provider_requested": requested_provider,
            "provider_effective": DEFAULT_EMBEDDING_PROVIDER,
            "model_requested": requested_model,
            "model_effective": requested_model,
            "provider_hint": "deterministic_baseline",
        }

    return {
        "provider_requested": requested_provider,
        "provider_effective": DEFAULT_EMBEDDING_PROVIDER,
        "model_requested": requested_model,
        "model_effective": DEFAULT_EMBEDDING_MODEL,
        "provider_hint": "provider_not_implemented_fallback_deterministic",
    }


def embedding_strategy_snapshot(
    *,
    semantic_vector_enabled: bool,
    provider: str | None,
    model: str | None,
    dimensions: int,
    source_kinds: tuple[str, ...] | None = None,
    refresh_mode: str | None = None,
    refresh_interval_seconds: int | None = None,
    provider_ownership_enforcement: str | None = None,
    model_governance_enforcement: str | None = None,
    source_rollout_enforcement: str | None = None,
) -> dict[str, str | bool | int | list[str]]:
    posture = resolve_embedding_posture(provider=provider, model=model)
    if source_kinds is None:
        normalized_source_kinds = normalize_embedding_source_kinds(None)
    else:
        normalized_source_kinds = normalize_embedding_source_kinds(",".join(source_kinds))
    source_kind_set = set(normalized_source_kinds)
    vector_source_order = ("semantic", "affective", "relation")
    source_rollout_enabled_sources = [
        kind for kind in vector_source_order if kind in source_kind_set
    ]
    source_rollout_missing_sources = [
        kind for kind in vector_source_order if kind not in source_kind_set
    ]
    provider_ready = posture["provider_requested"] == posture["provider_effective"]
    semantic_ready = "semantic" in source_kind_set
    affective_ready = "affective" in source_kind_set
    relation_ready = "relation" in source_kind_set
    if not semantic_vector_enabled:
        source_coverage_state = "vectors_disabled"
        source_coverage_hint = "not_applicable_vectors_disabled"
    elif semantic_ready and affective_ready:
        source_coverage_state = "full_for_current_retrieval_path"
        source_coverage_hint = "semantic_and_affective_sources_enabled"
    elif semantic_ready or affective_ready:
        source_coverage_state = "partial_for_current_retrieval_path"
        source_coverage_hint = "enable_missing_semantic_or_affective_source"
    else:
        source_coverage_state = "missing_for_current_retrieval_path"
        source_coverage_hint = "enable_semantic_or_affective_source_for_vector_hits"

    if not semantic_vector_enabled:
        source_rollout_state = "vectors_disabled"
        source_rollout_hint = "enable_vectors_before_source_rollout"
        source_rollout_recommendation = "defer_source_rollout_until_vectors_enabled"
    elif semantic_ready and affective_ready and relation_ready:
        source_rollout_state = "all_vector_sources_enabled"
        source_rollout_hint = "semantic_affective_relation_sources_enabled"
        source_rollout_recommendation = "maintain_current_source_rollout"
    elif semantic_ready and affective_ready:
        source_rollout_state = "semantic_affective_baseline"
        source_rollout_hint = "high_signal_sources_active"
        source_rollout_recommendation = "add_relation_source_after_baseline_stabilizes"
    elif semantic_ready:
        source_rollout_state = "semantic_only_phase"
        source_rollout_hint = "affective_source_missing"
        source_rollout_recommendation = "enable_affective_source_next"
    elif affective_ready:
        source_rollout_state = "affective_only_phase"
        source_rollout_hint = "semantic_source_missing"
        source_rollout_recommendation = "enable_semantic_source_next"
    else:
        source_rollout_state = "foundational_sources_only"
        source_rollout_hint = "semantic_and_affective_sources_missing"
        source_rollout_recommendation = "enable_semantic_then_affective_sources"

    source_rollout_phase_total = len(vector_source_order)
    if not semantic_vector_enabled:
        source_rollout_completion_state = "vectors_disabled"
        source_rollout_next_source_kind = "none"
    elif semantic_ready and affective_ready and relation_ready:
        source_rollout_completion_state = "fully_enabled"
        source_rollout_next_source_kind = "none"
    elif semantic_ready and affective_ready:
        source_rollout_completion_state = "baseline_complete_relation_pending"
        source_rollout_next_source_kind = "relation"
    elif semantic_ready:
        source_rollout_completion_state = "baseline_in_progress_affective_pending"
        source_rollout_next_source_kind = "affective"
    elif affective_ready or relation_ready:
        source_rollout_completion_state = "baseline_blocked_semantic_missing"
        source_rollout_next_source_kind = "semantic"
    else:
        source_rollout_completion_state = "not_started"
        source_rollout_next_source_kind = "semantic"
    source_rollout_phase_index = len(source_rollout_enabled_sources)
    source_rollout_progress_percent = int(
        round((source_rollout_phase_index / source_rollout_phase_total) * 100)
    )

    if not semantic_vector_enabled:
        warning_state = "vectors_disabled"
        warning_hint = "enable_semantic_vectors_to_activate_embedding_strategy"
    elif provider_ready:
        warning_state = "no_warning"
        warning_hint = "embedding_strategy_ready"
    else:
        warning_state = "provider_fallback_active"
        warning_hint = "provider_not_implemented_using_deterministic_fallback"

    if not semantic_vector_enabled:
        provider_ownership_state = "vectors_disabled"
        provider_ownership_hint = "not_applicable_vectors_disabled"
    elif posture["provider_requested"] != posture["provider_effective"]:
        provider_ownership_state = "provider_fallback_active"
        provider_ownership_hint = "requested_provider_not_effective_owner"
    elif posture["provider_effective"] == DEFAULT_EMBEDDING_PROVIDER:
        provider_ownership_state = "deterministic_baseline_owner"
        provider_ownership_hint = "deterministic_provider_owns_embedding_execution"
    else:
        provider_ownership_state = "provider_owned_execution"
        provider_ownership_hint = "provider_controls_embedding_execution"

    if not semantic_vector_enabled:
        model_governance_state = "vectors_disabled"
        model_governance_hint = "not_applicable_vectors_disabled"
    elif posture["provider_effective"] != posture["provider_requested"]:
        model_governance_state = "provider_fallback_effective_model"
        model_governance_hint = "effective_model_controlled_by_fallback_provider"
    elif (
        posture["provider_effective"] == DEFAULT_EMBEDDING_PROVIDER
        and posture["model_requested"] != DEFAULT_EMBEDDING_MODEL
    ):
        model_governance_state = "deterministic_custom_model_name"
        model_governance_hint = "deterministic_provider_uses_fixed_embedding_behavior"
    else:
        model_governance_state = "model_contract_aligned"
        model_governance_hint = "embedding_model_contract_aligned_with_provider"

    normalized_refresh_mode = normalize_embedding_refresh_mode(refresh_mode)
    normalized_refresh_interval_seconds = normalize_embedding_refresh_interval_seconds(
        refresh_interval_seconds
    )
    normalized_provider_ownership_enforcement = normalize_embedding_provider_ownership_enforcement(
        provider_ownership_enforcement
    )
    normalized_model_governance_enforcement = normalize_embedding_model_governance_enforcement(
        model_governance_enforcement
    )
    normalized_source_rollout_enforcement = normalize_embedding_source_rollout_enforcement(
        source_rollout_enforcement
    )
    if not semantic_vector_enabled:
        source_rollout_enforcement_state = "not_applicable_vectors_disabled"
        source_rollout_enforcement_hint = "not_applicable_vectors_disabled"
    elif source_rollout_next_source_kind != "none":
        if normalized_source_rollout_enforcement == "strict":
            source_rollout_enforcement_state = "blocked"
            source_rollout_enforcement_hint = "enable_pending_source_kinds_before_startup"
        else:
            source_rollout_enforcement_state = "warning_only"
            source_rollout_enforcement_hint = "pending_source_rollout_allowed_in_warn_mode"
    else:
        source_rollout_enforcement_state = "not_applicable_rollout_complete"
        source_rollout_enforcement_hint = "source_rollout_is_complete"

    if not semantic_vector_enabled:
        refresh_state = "vectors_disabled"
        refresh_hint = "not_applicable_vectors_disabled"
        refresh_cadence_state = "vectors_disabled"
        refresh_cadence_hint = "not_applicable_vectors_disabled"
    elif normalized_refresh_mode == "manual":
        refresh_state = "manual_refresh_required"
        refresh_hint = "ensure_manual_refresh_process_is_defined"
        if normalized_refresh_interval_seconds <= 900:
            refresh_cadence_state = "manual_high_frequency"
            refresh_cadence_hint = "manual_refresh_runs_at_high_frequency"
        elif normalized_refresh_interval_seconds <= DEFAULT_EMBEDDING_REFRESH_INTERVAL_SECONDS:
            refresh_cadence_state = "manual_moderate_frequency"
            refresh_cadence_hint = "manual_refresh_runs_within_daily_window"
        else:
            refresh_cadence_state = "manual_low_frequency"
            refresh_cadence_hint = "manual_refresh_may_cause_stale_vectors"
    else:
        refresh_state = "on_write_refresh_active"
        refresh_hint = "refresh_on_write_enabled"
        refresh_cadence_state = "on_write_continuous"
        refresh_cadence_hint = "on_write_refresh_has_no_manual_gap"

    if provider_ownership_state == "provider_fallback_active":
        if normalized_provider_ownership_enforcement == "strict":
            provider_ownership_enforcement_state = "blocked"
            provider_ownership_enforcement_hint = "switch_to_effective_provider_owner_before_startup"
        else:
            provider_ownership_enforcement_state = "warning_only"
            provider_ownership_enforcement_hint = "fallback_allowed_in_warn_mode"
    elif provider_ownership_state == "vectors_disabled":
        provider_ownership_enforcement_state = "not_applicable_vectors_disabled"
        provider_ownership_enforcement_hint = "not_applicable_vectors_disabled"
    else:
        provider_ownership_enforcement_state = "not_applicable_no_fallback"
        provider_ownership_enforcement_hint = "no_provider_ownership_violation"

    if not semantic_vector_enabled:
        owner_strategy_state = "vectors_disabled"
        owner_strategy_hint = "enable_vectors_before_owner_strategy_rollout"
        owner_strategy_recommendation = "defer_owner_strategy_selection_until_vectors_enabled"
    elif provider_ownership_state == "provider_fallback_active":
        owner_strategy_state = "fallback_owner_active"
        owner_strategy_hint = "requested_provider_not_effective_owner"
        owner_strategy_recommendation = "keep_deterministic_owner_until_provider_execution_is_available"
    elif (
        posture["provider_effective"] == DEFAULT_EMBEDDING_PROVIDER
        and normalized_refresh_mode == "manual"
    ):
        owner_strategy_state = "deterministic_manual_owner"
        owner_strategy_hint = "manual_refresh_required_for_deterministic_owner"
        owner_strategy_recommendation = "document_and_operate_manual_refresh_process"
    elif posture["provider_effective"] == DEFAULT_EMBEDDING_PROVIDER:
        owner_strategy_state = "deterministic_on_write_owner"
        owner_strategy_hint = "deterministic_baseline_owner_active"
        owner_strategy_recommendation = "deterministic_on_write_baseline_is_active"
    else:
        owner_strategy_state = "provider_owned_execution"
        owner_strategy_hint = "effective_provider_owns_embedding_execution"
        owner_strategy_recommendation = "provider_owned_strategy_active"

    if model_governance_state == "deterministic_custom_model_name":
        if normalized_model_governance_enforcement == "strict":
            model_governance_enforcement_state = "blocked"
            model_governance_enforcement_hint = "use_deterministic_v1_or_switch_to_effective_provider_model"
        else:
            model_governance_enforcement_state = "warning_only"
            model_governance_enforcement_hint = "custom_model_name_allowed_in_warn_mode"
    elif model_governance_state == "vectors_disabled":
        model_governance_enforcement_state = "not_applicable_vectors_disabled"
        model_governance_enforcement_hint = "not_applicable_vectors_disabled"
    else:
        model_governance_enforcement_state = "not_applicable_aligned"
        model_governance_enforcement_hint = "no_model_governance_violation"

    strict_rollout_violations: list[str] = []
    if semantic_vector_enabled and provider_ownership_state == "provider_fallback_active":
        strict_rollout_violations.append("provider_ownership_fallback_active")
    if semantic_vector_enabled and model_governance_state == "deterministic_custom_model_name":
        strict_rollout_violations.append("model_governance_deterministic_custom_model_name")
    strict_rollout_violation_count = len(strict_rollout_violations)
    if not semantic_vector_enabled:
        strict_rollout_ready = False
        strict_rollout_state = "not_applicable_vectors_disabled"
        strict_rollout_hint = "enable_vectors_before_strict_enforcement_rollout"
        strict_rollout_recommendation = "defer_strict_enforcement_until_vectors_enabled"
    elif strict_rollout_violation_count == 0:
        strict_rollout_ready = True
        strict_rollout_state = "ready"
        strict_rollout_hint = "can_enable_strict_provider_and_model_enforcement"
        strict_rollout_recommendation = "enable_strict_provider_and_model_enforcement"
    elif strict_rollout_violation_count > 1:
        strict_rollout_ready = False
        strict_rollout_state = "not_ready_multi_violation"
        strict_rollout_hint = "resolve_provider_ownership_and_model_governance_before_strict"
        strict_rollout_recommendation = "keep_warn_until_provider_and_model_governance_are_aligned"
    elif "provider_ownership_fallback_active" in strict_rollout_violations:
        strict_rollout_ready = False
        strict_rollout_state = "not_ready_provider_ownership"
        strict_rollout_hint = "resolve_provider_ownership_before_strict"
        strict_rollout_recommendation = "keep_provider_ownership_warn_until_provider_owner_is_effective"
    else:
        strict_rollout_ready = False
        strict_rollout_state = "not_ready_model_governance"
        strict_rollout_hint = "resolve_model_governance_before_strict"
        strict_rollout_recommendation = "keep_model_governance_warn_until_model_contract_is_aligned"

    recommended_provider_ownership_enforcement = (
        "warn"
        if (
            not semantic_vector_enabled
            or "provider_ownership_fallback_active" in strict_rollout_violations
        )
        else "strict"
    )
    recommended_model_governance_enforcement = (
        "warn"
        if (
            not semantic_vector_enabled
            or "model_governance_deterministic_custom_model_name" in strict_rollout_violations
        )
        else "strict"
    )

    def _enforcement_alignment_state(current: str, recommended: str) -> str:
        if current == recommended:
            return "aligned"
        if current == "warn" and recommended == "strict":
            return "below_recommendation"
        return "above_recommendation"

    if not semantic_vector_enabled:
        provider_ownership_enforcement_alignment = "not_applicable_vectors_disabled"
        model_governance_enforcement_alignment = "not_applicable_vectors_disabled"
        enforcement_alignment_state = "not_applicable_vectors_disabled"
        enforcement_alignment_hint = "enable_vectors_before_enforcement_alignment"
    else:
        provider_ownership_enforcement_alignment = _enforcement_alignment_state(
            normalized_provider_ownership_enforcement,
            recommended_provider_ownership_enforcement,
        )
        model_governance_enforcement_alignment = _enforcement_alignment_state(
            normalized_model_governance_enforcement,
            recommended_model_governance_enforcement,
        )
        alignments = {
            provider_ownership_enforcement_alignment,
            model_governance_enforcement_alignment,
        }
        if alignments == {"aligned"}:
            enforcement_alignment_state = "aligned_with_recommendation"
            enforcement_alignment_hint = "enforcement_matches_rollout_recommendation"
        elif "below_recommendation" in alignments and "above_recommendation" in alignments:
            enforcement_alignment_state = "mixed_relative_to_recommendation"
            enforcement_alignment_hint = "normalize_enforcement_levels_to_recommendation"
        elif "below_recommendation" in alignments:
            enforcement_alignment_state = "below_recommendation"
            if (
                provider_ownership_enforcement_alignment == "below_recommendation"
                and model_governance_enforcement_alignment == "below_recommendation"
            ):
                enforcement_alignment_hint = "consider_enabling_strict_for_provider_and_model"
            elif provider_ownership_enforcement_alignment == "below_recommendation":
                enforcement_alignment_hint = "consider_enabling_provider_ownership_strict"
            else:
                enforcement_alignment_hint = "consider_enabling_model_governance_strict"
        else:
            enforcement_alignment_state = "above_recommendation"
            if (
                provider_ownership_enforcement_alignment == "above_recommendation"
                and model_governance_enforcement_alignment == "above_recommendation"
            ):
                enforcement_alignment_hint = (
                    "strict_enforcement_enabled_ahead_of_recommendation_for_provider_and_model"
                )
            elif provider_ownership_enforcement_alignment == "above_recommendation":
                enforcement_alignment_hint = "provider_ownership_strict_enabled_ahead_of_recommendation"
            else:
                enforcement_alignment_hint = "model_governance_strict_enabled_ahead_of_recommendation"

    if not semantic_vector_enabled:
        recommended_source_rollout_enforcement = "warn"
        source_rollout_enforcement_alignment = "not_applicable_vectors_disabled"
        source_rollout_enforcement_alignment_state = "not_applicable_vectors_disabled"
        source_rollout_enforcement_alignment_hint = (
            "enable_vectors_before_source_rollout_enforcement_alignment"
        )
    else:
        recommended_source_rollout_enforcement = (
            "strict" if source_rollout_next_source_kind == "none" else "warn"
        )
        source_rollout_enforcement_alignment = _enforcement_alignment_state(
            normalized_source_rollout_enforcement,
            recommended_source_rollout_enforcement,
        )
        if source_rollout_enforcement_alignment == "aligned":
            source_rollout_enforcement_alignment_state = "aligned_with_recommendation"
            source_rollout_enforcement_alignment_hint = (
                "source_rollout_enforcement_matches_recommendation"
            )
        elif source_rollout_enforcement_alignment == "below_recommendation":
            source_rollout_enforcement_alignment_state = "below_recommendation"
            source_rollout_enforcement_alignment_hint = (
                "consider_enabling_source_rollout_strict_when_rollout_is_complete"
            )
        else:
            source_rollout_enforcement_alignment_state = "above_recommendation"
            source_rollout_enforcement_alignment_hint = (
                "source_rollout_strict_enabled_ahead_of_recommendation"
            )

    if not semantic_vector_enabled:
        recommended_refresh_mode = "on_write"
        refresh_alignment_state = "not_applicable_vectors_disabled"
        refresh_alignment_hint = "enable_vectors_before_refresh_alignment"
    elif source_rollout_completion_state == "fully_enabled":
        recommended_refresh_mode = "manual"
        if normalized_refresh_mode == "manual":
            refresh_alignment_state = "aligned"
            refresh_alignment_hint = "refresh_mode_matches_mature_rollout_recommendation"
        else:
            refresh_alignment_state = "on_write_before_recommended_manual"
            refresh_alignment_hint = "consider_switching_to_manual_for_mature_rollout"
    else:
        recommended_refresh_mode = "on_write"
        if normalized_refresh_mode == "on_write":
            refresh_alignment_state = "aligned"
            refresh_alignment_hint = "refresh_mode_matches_active_rollout_recommendation"
        else:
            refresh_alignment_state = "manual_override"
            refresh_alignment_hint = "ensure_manual_mode_has_operational_coverage"

    return {
        "semantic_vector_enabled": semantic_vector_enabled,
        "semantic_retrieval_mode": "hybrid_vector_lexical" if semantic_vector_enabled else "lexical_only",
        "semantic_embedding_provider_ready": provider_ready,
        "semantic_embedding_posture": "ready" if provider_ready else "fallback_deterministic",
        "semantic_embedding_provider_requested": posture["provider_requested"],
        "semantic_embedding_provider_effective": posture["provider_effective"],
        "semantic_embedding_provider_hint": posture["provider_hint"],
        "semantic_embedding_provider_ownership_state": provider_ownership_state,
        "semantic_embedding_provider_ownership_hint": provider_ownership_hint,
        "semantic_embedding_provider_ownership_enforcement": normalized_provider_ownership_enforcement,
        "semantic_embedding_provider_ownership_enforcement_state": provider_ownership_enforcement_state,
        "semantic_embedding_provider_ownership_enforcement_hint": provider_ownership_enforcement_hint,
        "semantic_embedding_owner_strategy_state": owner_strategy_state,
        "semantic_embedding_owner_strategy_hint": owner_strategy_hint,
        "semantic_embedding_owner_strategy_recommendation": owner_strategy_recommendation,
        "semantic_embedding_model_requested": posture["model_requested"],
        "semantic_embedding_model_effective": posture["model_effective"],
        "semantic_embedding_model_governance_state": model_governance_state,
        "semantic_embedding_model_governance_hint": model_governance_hint,
        "semantic_embedding_model_governance_enforcement": normalized_model_governance_enforcement,
        "semantic_embedding_model_governance_enforcement_state": model_governance_enforcement_state,
        "semantic_embedding_model_governance_enforcement_hint": model_governance_enforcement_hint,
        "semantic_embedding_strict_rollout_violations": list(strict_rollout_violations),
        "semantic_embedding_strict_rollout_violation_count": strict_rollout_violation_count,
        "semantic_embedding_strict_rollout_ready": strict_rollout_ready,
        "semantic_embedding_strict_rollout_state": strict_rollout_state,
        "semantic_embedding_strict_rollout_hint": strict_rollout_hint,
        "semantic_embedding_strict_rollout_recommendation": strict_rollout_recommendation,
        "semantic_embedding_recommended_provider_ownership_enforcement": recommended_provider_ownership_enforcement,
        "semantic_embedding_recommended_model_governance_enforcement": recommended_model_governance_enforcement,
        "semantic_embedding_provider_ownership_enforcement_alignment": provider_ownership_enforcement_alignment,
        "semantic_embedding_model_governance_enforcement_alignment": model_governance_enforcement_alignment,
        "semantic_embedding_enforcement_alignment_state": enforcement_alignment_state,
        "semantic_embedding_enforcement_alignment_hint": enforcement_alignment_hint,
        "semantic_embedding_dimensions": max(1, int(dimensions)),
        "semantic_embedding_source_kinds": list(normalized_source_kinds),
        "semantic_embedding_source_coverage_state": source_coverage_state,
        "semantic_embedding_source_coverage_hint": source_coverage_hint,
        "semantic_embedding_source_rollout_state": source_rollout_state,
        "semantic_embedding_source_rollout_hint": source_rollout_hint,
        "semantic_embedding_source_rollout_recommendation": source_rollout_recommendation,
        "semantic_embedding_source_rollout_order": list(vector_source_order),
        "semantic_embedding_source_rollout_enabled_sources": list(source_rollout_enabled_sources),
        "semantic_embedding_source_rollout_missing_sources": list(source_rollout_missing_sources),
        "semantic_embedding_source_rollout_next_source_kind": source_rollout_next_source_kind,
        "semantic_embedding_source_rollout_completion_state": source_rollout_completion_state,
        "semantic_embedding_source_rollout_phase_index": source_rollout_phase_index,
        "semantic_embedding_source_rollout_phase_total": source_rollout_phase_total,
        "semantic_embedding_source_rollout_progress_percent": source_rollout_progress_percent,
        "semantic_embedding_source_rollout_enforcement": normalized_source_rollout_enforcement,
        "semantic_embedding_source_rollout_enforcement_state": source_rollout_enforcement_state,
        "semantic_embedding_source_rollout_enforcement_hint": source_rollout_enforcement_hint,
        "semantic_embedding_recommended_source_rollout_enforcement": recommended_source_rollout_enforcement,
        "semantic_embedding_source_rollout_enforcement_alignment": source_rollout_enforcement_alignment,
        "semantic_embedding_source_rollout_enforcement_alignment_state": source_rollout_enforcement_alignment_state,
        "semantic_embedding_source_rollout_enforcement_alignment_hint": source_rollout_enforcement_alignment_hint,
        "semantic_embedding_warning_state": warning_state,
        "semantic_embedding_warning_hint": warning_hint,
        "semantic_embedding_refresh_mode": normalized_refresh_mode,
        "semantic_embedding_refresh_interval_seconds": normalized_refresh_interval_seconds,
        "semantic_embedding_refresh_state": refresh_state,
        "semantic_embedding_refresh_hint": refresh_hint,
        "semantic_embedding_refresh_cadence_state": refresh_cadence_state,
        "semantic_embedding_refresh_cadence_hint": refresh_cadence_hint,
        "semantic_embedding_recommended_refresh_mode": recommended_refresh_mode,
        "semantic_embedding_refresh_alignment_state": refresh_alignment_state,
        "semantic_embedding_refresh_alignment_hint": refresh_alignment_hint,
    }


def normalize_embedding_source_kinds(value: str | None) -> tuple[str, ...]:
    raw = str(value or "").strip().lower()
    if not raw:
        return DEFAULT_EMBEDDING_SOURCE_KINDS

    requested = [item.strip().lower() for item in raw.split(",") if item.strip()]
    if not requested:
        return DEFAULT_EMBEDDING_SOURCE_KINDS

    allowed = set(EMBEDDING_SOURCE_KIND_ORDER)
    unknown = sorted({item for item in requested if item not in allowed})
    if unknown:
        joined = ", ".join(unknown)
        raise ValueError(f"EMBEDDING_SOURCE_KINDS contains unknown kinds: {joined}")

    requested_set = set(requested)
    ordered = tuple(item for item in EMBEDDING_SOURCE_KIND_ORDER if item in requested_set)
    return ordered or DEFAULT_EMBEDDING_SOURCE_KINDS


def normalize_embedding_refresh_mode(value: str | None) -> str:
    normalized = str(value or DEFAULT_EMBEDDING_REFRESH_MODE).strip().lower()
    if normalized not in EMBEDDING_REFRESH_MODES:
        return DEFAULT_EMBEDDING_REFRESH_MODE
    return normalized


def normalize_embedding_refresh_interval_seconds(value: int | None) -> int:
    try:
        interval = int(
            DEFAULT_EMBEDDING_REFRESH_INTERVAL_SECONDS if value is None else value
        )
    except (TypeError, ValueError):
        interval = DEFAULT_EMBEDDING_REFRESH_INTERVAL_SECONDS
    return max(60, interval)


def normalize_embedding_provider_ownership_enforcement(value: str | None) -> str:
    normalized = str(value or DEFAULT_EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT).strip().lower()
    if normalized not in EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT_MODES:
        return DEFAULT_EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT
    return normalized


def normalize_embedding_model_governance_enforcement(value: str | None) -> str:
    normalized = str(value or DEFAULT_EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT).strip().lower()
    if normalized not in EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT_MODES:
        return DEFAULT_EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT
    return normalized


def normalize_embedding_source_rollout_enforcement(value: str | None) -> str:
    normalized = str(value or DEFAULT_EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT).strip().lower()
    if normalized not in EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT_MODES:
        return DEFAULT_EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT
    return normalized


def deterministic_embedding(text: str, *, dimensions: int = 32) -> list[float]:
    """Returns a deterministic normalized embedding vector for fallback retrieval paths."""
    normalized = " ".join(str(text or "").strip().lower().split())
    if not normalized:
        return [0.0] * dimensions

    vector = [0.0] * dimensions
    for token in normalized.split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for index, byte in enumerate(digest):
            target = index % dimensions
            signed = (int(byte) - 127.5) / 127.5
            vector[target] += signed

    norm = math.sqrt(sum(component * component for component in vector))
    if norm <= 0.0:
        return [0.0] * dimensions
    return [component / norm for component in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0

    dimensions = min(len(left), len(right))
    if dimensions == 0:
        return 0.0

    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0
    for index in range(dimensions):
        left_value = float(left[index])
        right_value = float(right[index])
        dot += left_value * right_value
        left_norm += left_value * left_value
        right_norm += right_value * right_value

    if left_norm <= 0.0 or right_norm <= 0.0:
        return 0.0
    return dot / math.sqrt(left_norm * right_norm)
