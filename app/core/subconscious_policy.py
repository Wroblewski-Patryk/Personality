from __future__ import annotations

from typing import Iterable

from app.core.contracts import SubconsciousResearchPolicy

DEFAULT_SUBCONSCIOUS_RESEARCH_POLICY: SubconsciousResearchPolicy = "read_only"
DEFAULT_READ_ONLY_TOOLS = (
    "memory_retrieval",
    "knowledge_search",
    "calendar_availability_read",
    "task_provider_read",
    "drive_metadata_read",
)


def normalize_subconscious_research_policy(
    value: object,
) -> SubconsciousResearchPolicy:
    candidate = str(value or "").strip().lower()
    if candidate == "read_only":
        return "read_only"
    return DEFAULT_SUBCONSCIOUS_RESEARCH_POLICY


def normalize_read_only_tools(tools: Iterable[object] | None) -> list[str]:
    if tools is None:
        return list(DEFAULT_READ_ONLY_TOOLS)

    allowed = {item for item in DEFAULT_READ_ONLY_TOOLS}
    normalized: list[str] = []
    for value in tools:
        candidate = str(value or "").strip().lower()
        if not candidate or candidate not in allowed:
            continue
        if candidate not in normalized:
            normalized.append(candidate)
    if normalized:
        return normalized
    return list(DEFAULT_READ_ONLY_TOOLS)
