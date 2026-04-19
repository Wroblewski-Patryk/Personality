from __future__ import annotations

from collections.abc import Callable, Sequence

from app.core.subconscious_policy import normalize_read_only_tools

MemoryFieldsExtractor = Callable[[dict], dict[str, str]]


def derive_subconscious_proposals(
    recent_memory: Sequence[dict],
    *,
    active_goals: Sequence[dict],
    active_tasks: Sequence[dict],
    extract_memory_fields: MemoryFieldsExtractor,
) -> list[dict]:
    if not recent_memory:
        return []

    proposals: list[dict] = []
    latest_fields = extract_memory_fields(recent_memory[0])
    latest_event = str(latest_fields.get("event", "")).strip()

    blocked_task = _first_blocked_task(active_tasks)
    if blocked_task is not None:
        proposals.append(
            {
                "proposal_type": "nudge_user",
                "summary": f"Nudge the user about blocked task '{blocked_task}'.",
                "payload": {"task_name": blocked_task},
                "confidence": 0.72,
            }
        )

    if latest_event and ("?" in latest_event or "clarif" in latest_event.lower()):
        proposals.append(
            {
                "proposal_type": "ask_user",
                "summary": "Ask the user to clarify the current blocker scope.",
                "payload": {"question_focus": latest_event[:120]},
                "confidence": 0.74,
            }
        )

    if latest_event and _looks_like_research_request(latest_event):
        proposals.append(
            {
                "proposal_type": "research_topic",
                "summary": "Research context needed for the current task using read-only tools.",
                "payload": {"topic": latest_event[:160]},
                "confidence": 0.69,
                "research_policy": "read_only",
                "allowed_tools": normalize_read_only_tools(
                    [
                        "memory_retrieval",
                        "knowledge_search",
                        "calendar_availability_read",
                        "task_provider_read",
                    ]
                ),
            }
        )

    if not active_goals and latest_event:
        proposals.append(
            {
                "proposal_type": "suggest_goal",
                "summary": "Suggest creating a stable internal goal aligned to repeated execution work.",
                "payload": {"goal_hint": latest_event[:160]},
                "confidence": 0.64,
            }
        )

    proposals.extend(
        _derive_connector_expansion_proposals(
            recent_memory=recent_memory,
            extract_memory_fields=extract_memory_fields,
        )
    )

    deduped: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for proposal in proposals:
        key = (str(proposal.get("proposal_type", "")), str(proposal.get("summary", "")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(proposal)
    return deduped[:4]


def _first_blocked_task(active_tasks: Sequence[dict]) -> str | None:
    for task in active_tasks:
        status = str(task.get("status", "")).strip().lower()
        if status != "blocked":
            continue
        name = str(task.get("name", "")).strip()
        if name:
            return name
    return None


def _looks_like_research_request(text: str) -> bool:
    lowered = text.lower()
    keywords = (
        "research",
        "investigate",
        "look up",
        "check",
        "sprawd",
        "zbadaj",
    )
    return any(keyword in lowered for keyword in keywords)


def _derive_connector_expansion_proposals(
    *,
    recent_memory: Sequence[dict],
    extract_memory_fields: MemoryFieldsExtractor,
) -> list[dict]:
    if not recent_memory:
        return []

    connector_update_field = {
        "calendar": "calendar_connector_update",
        "task_system": "task_connector_update",
        "cloud_drive": "drive_connector_update",
    }
    unmet_counts: dict[tuple[str, str, str], int] = {}
    sample_events: dict[tuple[str, str, str], str] = {}

    for memory_item in list(recent_memory)[:6]:
        fields = extract_memory_fields(memory_item)
        event_text = str(fields.get("event", "")).strip()
        if not event_text:
            continue
        inferred_gap = _infer_connector_gap(event_text)
        if inferred_gap is None:
            continue
        connector_kind, provider_hint, requested_capability = inferred_gap
        connector_update = str(fields.get(connector_update_field[connector_kind], "")).strip().lower()
        if connector_update:
            continue
        connector_expansion_update = str(fields.get("connector_expansion_update", "")).strip().lower()
        if connector_kind in connector_expansion_update:
            continue
        key = (connector_kind, provider_hint, requested_capability)
        unmet_counts[key] = unmet_counts.get(key, 0) + 1
        sample_events.setdefault(key, event_text[:120])

    proposals: list[dict] = []
    ranked = sorted(unmet_counts.items(), key=lambda item: item[1], reverse=True)
    for (connector_kind, provider_hint, requested_capability), count in ranked:
        if count < 2:
            continue
        provider_label = provider_hint.replace("_", " ")
        connector_label = connector_kind.replace("_", " ")
        confidence = min(0.86, 0.62 + (0.07 * count))
        proposals.append(
            {
                "proposal_type": "suggest_connector_expansion",
                "summary": (
                    "Suggest connector expansion for "
                    f"{provider_label} {connector_label} capability '{requested_capability}'."
                ),
                "payload": {
                    "connector_kind": connector_kind,
                    "provider_hint": provider_hint,
                    "requested_capability": requested_capability,
                    "evidence": f"repeated_unmet_need:{count}",
                    "sample_request": sample_events.get(
                        (connector_kind, provider_hint, requested_capability),
                        "",
                    ),
                },
                "confidence": round(confidence, 2),
            }
        )
    return proposals[:2]


def _infer_connector_gap(event_text: str) -> tuple[str, str, str] | None:
    lowered = event_text.strip().lower()
    if not lowered:
        return None

    if any(keyword in lowered for keyword in ("google drive", "gdrive", "onedrive", "dropbox", "box drive", "box ")):
        return "cloud_drive", _drive_provider_hint(lowered), _drive_requested_capability(lowered)
    if any(keyword in lowered for keyword in ("clickup", "trello", "asana", "jira")):
        return "task_system", _task_provider_hint(lowered), _task_requested_capability(lowered)
    if any(
        keyword in lowered
        for keyword in ("google calendar", "calendar", "kalendarz", "meeting", "spotkanie", "schedule", "availability")
    ):
        return "calendar", _calendar_provider_hint(lowered), _calendar_requested_capability(lowered)
    return None


def _calendar_provider_hint(lowered: str) -> str:
    if "google calendar" in lowered:
        return "google_calendar"
    if "outlook" in lowered:
        return "outlook_calendar"
    return "generic"


def _calendar_requested_capability(lowered: str) -> str:
    if any(keyword in lowered for keyword in ("availability", "free", "woln", "kiedy")):
        return "availability_read"
    if any(keyword in lowered for keyword in ("create", "book", "reserve", "utw", "zaplanuj", "cancel", "update", "reschedule")):
        return "event_mutation"
    return "scheduling_support"


def _task_provider_hint(lowered: str) -> str:
    for provider in ("clickup", "trello", "asana", "jira"):
        if provider in lowered:
            return provider
    return "generic"


def _task_requested_capability(lowered: str) -> str:
    if any(keyword in lowered for keyword in ("sync", "integrat", "connect", "link", "mirror")):
        return "task_sync"
    if any(keyword in lowered for keyword in ("create", "add", "update", "close", "complete", "utw", "dodaj", "zamkn")):
        return "task_mutation"
    return "task_visibility"


def _drive_provider_hint(lowered: str) -> str:
    if "google drive" in lowered or "gdrive" in lowered:
        return "google_drive"
    if "onedrive" in lowered:
        return "onedrive"
    if "dropbox" in lowered:
        return "dropbox"
    if "box drive" in lowered or "box " in lowered:
        return "box"
    return "generic"


def _drive_requested_capability(lowered: str) -> str:
    if any(keyword in lowered for keyword in ("upload", "wgraj", "send", "przeslij")):
        return "file_upload"
    if any(keyword in lowered for keyword in ("search", "find", "lookup", "szuk")):
        return "document_search"
    if any(keyword in lowered for keyword in ("read", "open", "preview", "otworz")):
        return "document_read"
    return "cloud_file_access"
