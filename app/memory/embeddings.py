from __future__ import annotations

import hashlib
import math


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
