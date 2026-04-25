from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _normalized_tool_entry(
    entry: Mapping[str, Any] | None,
    *,
    provider_hint: str,
    execution_mode: str,
    ready: bool,
    state: str,
    hint: str,
) -> dict[str, Any]:
    payload = dict(entry or {})
    return {
        "provider": str(payload.get("provider", provider_hint) or provider_hint),
        "execution_mode": str(payload.get("execution_mode", execution_mode) or execution_mode),
        "ready": bool(payload.get("ready", ready)),
        "state": str(payload.get("state", state) or state),
        "hint": str(payload.get("hint", hint) or hint),
    }


def _website_reading_workflow_snapshot(
    *,
    knowledge_search: Mapping[str, Any],
    web_browser: Mapping[str, Any],
) -> dict[str, Any]:
    search_ready = bool(knowledge_search.get("ready", False))
    browser_ready = bool(web_browser.get("ready", False))

    blockers: list[str] = []
    next_actions: list[str] = []

    if not browser_ready:
        blockers.append("page_read_provider_not_ready")
        browser_hint = str(web_browser.get("hint", "") or "").strip()
        if browser_hint:
            next_actions.append(browser_hint)

    if not search_ready:
        blockers.append("search_provider_not_ready")
        search_hint = str(knowledge_search.get("hint", "") or "").strip()
        if search_hint:
            next_actions.append(search_hint)

    if browser_ready and search_ready:
        readiness_state = "ready_for_direct_and_search_first_review"
    elif browser_ready:
        readiness_state = "ready_for_direct_url_review_only"
    elif search_ready:
        readiness_state = "search_available_but_page_review_blocked"
    else:
        readiness_state = "website_reading_blocked"

    allowed_entry_modes = ["direct_url_review"] if browser_ready else []
    if browser_ready and search_ready:
        allowed_entry_modes.append("search_then_page_review")

    return {
        "policy_owner": "website_reading_workflow_policy",
        "workflow_state": readiness_state,
        "direct_url_review_available": browser_ready,
        "search_then_page_review_available": browser_ready and search_ready,
        "allowed_entry_modes": allowed_entry_modes,
        "selected_provider_path": {
            "search_provider_hint": str(knowledge_search.get("provider", "duckduckgo_html") or "duckduckgo_html"),
            "page_read_provider_hint": str(web_browser.get("provider", "generic_http") or "generic_http"),
        },
        "bounded_input_contract": [
            "explicit_url",
            "explicit_site_or_domain_hint",
            "explicit_answer_focus",
        ],
        "bounded_output_contract": [
            "final_page_url",
            "page_title_when_available",
            "bounded_summary",
            "source_note",
            "explicit_uncertainty_or_blocker_note",
        ],
        "bounded_read_semantics": [
            "single_page_read_only",
            "search_optional_before_page_read",
            "no_multi_page_crawl",
            "no_login_or_form_submission",
            "no_paywall_or_hidden_auth_bypass",
            "no_raw_full_page_dump",
        ],
        "memory_capture_boundary": "tool_grounded_summary_only_via_action_then_memory",
        "blockers": blockers,
        "next_actions": next_actions,
    }


def web_knowledge_tooling_snapshot(
    *,
    knowledge_search: Mapping[str, Any] | None = None,
    web_browser: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    normalized_search = _normalized_tool_entry(
        knowledge_search,
        provider_hint="duckduckgo_html",
        execution_mode="provider_backed_without_credentials",
        ready=True,
        state="provider_backed_ready",
        hint="duckduckgo_html_search_live",
    )
    normalized_browser = _normalized_tool_entry(
        web_browser,
        provider_hint="generic_http",
        execution_mode="provider_backed_without_credentials",
        ready=True,
        state="provider_backed_ready",
        hint="generic_http_read_page_live",
    )
    return {
        "policy_owner": "web_knowledge_tooling_policy",
        "tool_boundary": "action_owned_external_capability",
        "skill_execution_boundary": "metadata_only_capability_hints",
        "provider_execution_posture": "first_bounded_provider_slices_selected",
        "fallback_posture": "respond_without_external_tool_execution",
        "knowledge_search": {
            "capability_kind": "knowledge_search",
            "selected_provider_hint": normalized_search["provider"],
            "authorized_operations": ["search_web", "suggest_search"],
            **normalized_search,
        },
        "web_browser": {
            "capability_kind": "web_browser",
            "selected_provider_hint": normalized_browser["provider"],
            "authorized_operations": ["read_page", "suggest_page_review"],
            **normalized_browser,
        },
        "website_reading_workflow": _website_reading_workflow_snapshot(
            knowledge_search=normalized_search,
            web_browser=normalized_browser,
        ),
    }
