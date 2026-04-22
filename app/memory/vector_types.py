from __future__ import annotations

from typing import Any

from sqlalchemy import JSON
from sqlalchemy.types import TypeDecorator

try:  # pragma: no cover - optional dependency path
    from pgvector.sqlalchemy import Vector
except Exception:  # pragma: no cover - optional dependency path
    Vector = None  # type: ignore[assignment]


def pgvector_python_binding_available() -> bool:
    return Vector is not None


class EmbeddingVectorType(TypeDecorator):
    """Stores vector data as pgvector on PostgreSQL and JSON elsewhere."""

    impl = JSON
    cache_ok = True

    def __init__(self, *, dimensions: int = 1536) -> None:
        self.dimensions = dimensions
        super().__init__()

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and Vector is not None:
            return dialect.type_descriptor(Vector(self.dimensions))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: Any, dialect):
        if value is None:
            return None
        if isinstance(value, list):
            return [float(item) for item in value]
        return value

    def process_result_value(self, value: Any, dialect):
        if value is None:
            return None
        if isinstance(value, list):
            return [float(item) for item in value]
        return value
