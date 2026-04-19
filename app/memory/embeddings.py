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
) -> dict[str, str | bool | int]:
    posture = resolve_embedding_posture(provider=provider, model=model)
    if source_kinds is None:
        normalized_source_kinds = normalize_embedding_source_kinds(None)
    else:
        normalized_source_kinds = normalize_embedding_source_kinds(",".join(source_kinds))
    source_kind_set = set(normalized_source_kinds)
    provider_ready = posture["provider_requested"] == posture["provider_effective"]
    semantic_ready = "semantic" in source_kind_set
    affective_ready = "affective" in source_kind_set
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
    if not semantic_vector_enabled:
        refresh_state = "vectors_disabled"
        refresh_hint = "not_applicable_vectors_disabled"
    elif normalized_refresh_mode == "manual":
        refresh_state = "manual_refresh_required"
        refresh_hint = "ensure_manual_refresh_process_is_defined"
    else:
        refresh_state = "on_write_refresh_active"
        refresh_hint = "refresh_on_write_enabled"

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
        "semantic_embedding_model_requested": posture["model_requested"],
        "semantic_embedding_model_effective": posture["model_effective"],
        "semantic_embedding_model_governance_state": model_governance_state,
        "semantic_embedding_model_governance_hint": model_governance_hint,
        "semantic_embedding_dimensions": max(1, int(dimensions)),
        "semantic_embedding_source_kinds": list(normalized_source_kinds),
        "semantic_embedding_source_coverage_state": source_coverage_state,
        "semantic_embedding_source_coverage_hint": source_coverage_hint,
        "semantic_embedding_warning_state": warning_state,
        "semantic_embedding_warning_hint": warning_hint,
        "semantic_embedding_refresh_mode": normalized_refresh_mode,
        "semantic_embedding_refresh_interval_seconds": normalized_refresh_interval_seconds,
        "semantic_embedding_refresh_state": refresh_state,
        "semantic_embedding_refresh_hint": refresh_hint,
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
