from __future__ import annotations

import hashlib
import math

DEFAULT_EMBEDDING_PROVIDER = "deterministic"
DEFAULT_EMBEDDING_MODEL = "deterministic-v1"
EMBEDDING_SOURCE_KIND_ORDER = ("episodic", "semantic", "affective", "relation")
DEFAULT_EMBEDDING_SOURCE_KINDS = ("episodic", "semantic", "affective")


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
) -> dict[str, str | bool | int]:
    posture = resolve_embedding_posture(provider=provider, model=model)
    provider_ready = posture["provider_requested"] == posture["provider_effective"]
    if not semantic_vector_enabled:
        warning_state = "vectors_disabled"
        warning_hint = "enable_semantic_vectors_to_activate_embedding_strategy"
    elif provider_ready:
        warning_state = "no_warning"
        warning_hint = "embedding_strategy_ready"
    else:
        warning_state = "provider_fallback_active"
        warning_hint = "provider_not_implemented_using_deterministic_fallback"

    return {
        "semantic_vector_enabled": semantic_vector_enabled,
        "semantic_retrieval_mode": "hybrid_vector_lexical" if semantic_vector_enabled else "lexical_only",
        "semantic_embedding_provider_ready": provider_ready,
        "semantic_embedding_posture": "ready" if provider_ready else "fallback_deterministic",
        "semantic_embedding_provider_requested": posture["provider_requested"],
        "semantic_embedding_provider_effective": posture["provider_effective"],
        "semantic_embedding_provider_hint": posture["provider_hint"],
        "semantic_embedding_model_requested": posture["model_requested"],
        "semantic_embedding_model_effective": posture["model_effective"],
        "semantic_embedding_dimensions": max(1, int(dimensions)),
        "semantic_embedding_warning_state": warning_state,
        "semantic_embedding_warning_hint": warning_hint,
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
