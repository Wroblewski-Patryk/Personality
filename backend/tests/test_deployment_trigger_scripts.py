from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import pytest


ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
TRIGGER_SCRIPT_PATH = BACKEND_ROOT / "scripts" / "trigger_coolify_deploy_webhook.py"
RELEASE_SMOKE_PS1_PATH = BACKEND_ROOT / "scripts" / "run_release_smoke.ps1"
PYTHON_EXE = ROOT / ".venv" / "Scripts" / "python.exe"
BACKEND_SCRIPT_ENTRYPOINTS = [
    "export_incident_evidence_bundle.py",
    "run_behavior_validation.py",
    "run_communication_boundary_backfill_once.py",
    "run_maintenance_tick_once.py",
    "run_proactive_tick_once.py",
    "run_reflection_queue_once.py",
    "run_user_data_cleanup.py",
    "trigger_coolify_deploy_webhook.py",
]
LOCAL_REPO_HEAD_SHA = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

TRIGGER_SPEC = importlib.util.spec_from_file_location("trigger_coolify_deploy_webhook_script", TRIGGER_SCRIPT_PATH)
assert TRIGGER_SPEC is not None and TRIGGER_SPEC.loader is not None
TRIGGER_MODULE = importlib.util.module_from_spec(TRIGGER_SPEC)
sys.modules[TRIGGER_SPEC.name] = TRIGGER_MODULE
TRIGGER_SPEC.loader.exec_module(TRIGGER_MODULE)

LEARNED_STATE_INSPECTION_SECTIONS = [
    "identity_state",
    "learned_knowledge",
    "role_skill_state",
    "planning_state",
]
LEARNED_STATE_GROWTH_SUMMARY_SECTIONS = [
    "preference_summary",
    "knowledge_summary",
    "reflection_growth_summary",
    "planning_continuity_summary",
]
LEARNED_STATE_ROLE_SKILL_METADATA_SECTIONS = [
    "role_skill_policy",
    "skill_registry",
    "selection_visibility_summary",
]
LEARNED_STATE_PLANNING_CONTINUITY_SECTIONS = [
    "active_goals",
    "active_tasks",
    "active_goal_milestones",
    "pending_proposals",
    "continuity_summary",
]
LEARNED_STATE_REFLECTION_GROWTH_SIGNAL_KINDS = [
    "semantic_conclusions",
    "affective_conclusions",
    "tool_grounded_conclusions",
    "adaptive_outputs",
    "relations",
]
PLANNED_ACTION_OBSERVER_POSTURE = {
    "policy_owner": "planned_action_observer_policy",
    "last_observer_state": "empty_noop",
    "last_observer_reason": "no_due_or_actionable_work",
    "empty_result_behavior": "no_foreground_event",
    "due_planned_work_count": 0,
    "actionable_proposal_count": 0,
    "foreground_events_emitted": 0,
    "noop_supported": True,
    "raw_payload_exposure": "counts_only",
}
TOOL_GROUNDED_LEARNING_CONTRACT = {
    "policy_owner": "tool_grounded_learning_policy",
    "capture_owner": "action_owned_external_read_summaries_only",
    "persistence_owner": "memory_conclusion_write_after_action",
    "allowed_read_operations": [
        "knowledge_search.search_web",
        "web_browser.read_page",
        "task_system.list_tasks",
        "calendar.read_availability",
        "cloud_drive.list_files",
    ],
    "raw_payload_storage_allowed": False,
    "execution_bypass_allowed": False,
    "self_modifying_skill_learning_allowed": False,
}
CAPABILITY_CATALOG_APPROVED_TOOL_FAMILIES = [
    "calendar",
    "cloud_drive",
    "knowledge_search",
    "task_system",
    "web_browser",
]
V1_REQUIRED_BEHAVIOR_SCENARIOS = [
    "T13.1",
    "T14.1",
    "T14.2",
    "T14.3",
    "T15.1",
    "T15.2",
    "T16.1",
    "T16.2",
    "T16.3",
    "T17.1",
    "T17.2",
    "T18.1",
    "T18.2",
    "T19.1",
    "T19.2",
]
V1_APPROVED_TOOL_SLICES = [
    "knowledge_search.search_web",
    "web_browser.read_page",
    "task_system.clickup_list_tasks",
    "task_system.clickup_update_task",
    "calendar.google_calendar_read_availability",
    "cloud_drive.google_drive_list_files",
]
ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS = [
    "task_system.clickup_create_task",
    "task_system.clickup_list_tasks",
    "task_system.clickup_update_task",
    "calendar.google_calendar_read_availability",
    "cloud_drive.google_drive_list_files",
]
ORGANIZER_TOOL_STACK_READ_ONLY_OPERATIONS = [
    "task_system.clickup_list_tasks",
    "calendar.google_calendar_read_availability",
    "cloud_drive.google_drive_list_files",
]
ORGANIZER_TOOL_STACK_CONFIRMATION_REQUIRED_OPERATIONS = [
    "task_system.clickup_create_task",
    "task_system.clickup_update_task",
]
ORGANIZER_TOOL_ACTIVATION_NEXT_ACTIONS = [
    "configure_google_calendar_access_token_calendar_id_and_timezone",
    "configure_google_drive_access_token_and_folder_id",
]
ORGANIZER_TOOL_ACTIVATION_MISSING_SETTINGS_BY_PROVIDER = {
    "clickup": [],
    "google_calendar": [
        "GOOGLE_CALENDAR_ACCESS_TOKEN",
        "GOOGLE_CALENDAR_CALENDAR_ID",
        "GOOGLE_CALENDAR_TIMEZONE",
    ],
    "google_drive": [
        "GOOGLE_DRIVE_ACCESS_TOKEN",
        "GOOGLE_DRIVE_FOLDER_ID",
    ],
}
ORGANIZER_DAILY_USE_READY_WORKFLOWS = [
    "clickup_task_review_and_mutation",
]
ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS = [
    "google_calendar_availability_inspection",
    "google_drive_file_space_inspection",
]


def _powershell_exe() -> str | None:
    return shutil.which("powershell") or shutil.which("pwsh")


@pytest.mark.parametrize("script_name", BACKEND_SCRIPT_ENTRYPOINTS)
def test_backend_operator_scripts_expose_help_from_backend_working_directory(script_name: str) -> None:
    script_path = BACKEND_ROOT / "scripts" / script_name
    completed = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        cwd=BACKEND_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    assert "usage:" in completed.stdout.lower()


def _organizer_tool_activation_snapshot() -> dict[str, object]:
    return {
        "policy_owner": "production_organizer_tool_activation",
        "provider_activation_total": 3,
        "provider_activation_ready": 1,
        "provider_activation_state": "provider_activation_incomplete",
        "user_opt_in_required": True,
        "mutation_confirmation_required": True,
        "provider_requirements": {
            "clickup": {
                "provider": "clickup",
                "required_settings": ["CLICKUP_API_TOKEN", "CLICKUP_LIST_ID"],
                "activation_scope": [
                    "task_system.clickup_create_task",
                    "task_system.clickup_list_tasks",
                    "task_system.clickup_update_task",
                ],
                "ready": True,
                "missing_settings": [],
                "user_opt_in_required": True,
                "confirmation_required_operations": [
                    "task_system.clickup_create_task",
                    "task_system.clickup_update_task",
                ],
                "next_action": "ready_for_clickup_operator_acceptance",
            },
            "google_calendar": {
                "provider": "google_calendar",
                "required_settings": [
                    "GOOGLE_CALENDAR_ACCESS_TOKEN",
                    "GOOGLE_CALENDAR_CALENDAR_ID",
                    "GOOGLE_CALENDAR_TIMEZONE",
                ],
                "activation_scope": ["calendar.google_calendar_read_availability"],
                "ready": False,
                "missing_settings": [
                    "GOOGLE_CALENDAR_ACCESS_TOKEN",
                    "GOOGLE_CALENDAR_CALENDAR_ID",
                    "GOOGLE_CALENDAR_TIMEZONE",
                ],
                "user_opt_in_required": True,
                "confirmation_required_operations": [],
                "next_action": "configure_google_calendar_access_token_calendar_id_and_timezone",
            },
            "google_drive": {
                "provider": "google_drive",
                "required_settings": [
                    "GOOGLE_DRIVE_ACCESS_TOKEN",
                    "GOOGLE_DRIVE_FOLDER_ID",
                ],
                "activation_scope": ["cloud_drive.google_drive_list_files"],
                "ready": False,
                "missing_settings": [
                    "GOOGLE_DRIVE_ACCESS_TOKEN",
                    "GOOGLE_DRIVE_FOLDER_ID",
                ],
                "user_opt_in_required": True,
                "confirmation_required_operations": [],
                "next_action": "configure_google_drive_access_token_and_folder_id",
            },
        },
        "next_actions": ORGANIZER_TOOL_ACTIVATION_NEXT_ACTIONS,
    }


def _organizer_daily_use_workflows() -> dict[str, object]:
    return {
        "clickup_task_review_and_mutation": {
            "provider": "clickup",
            "workflow_kind": "task_review_and_mutation",
            "approved_operations": [
                "task_system.clickup_list_tasks",
                "task_system.clickup_create_task",
                "task_system.clickup_update_task",
            ],
            "daily_use_ready": True,
            "daily_use_state": "ready_for_daily_use_with_opt_in_and_confirmed_mutations",
            "user_opt_in_required": True,
            "mutation_confirmation_required": True,
            "planning_boundary": "internal_tasks_and_goals_remain_primary",
            "next_action": "ready_for_clickup_daily_use",
        },
        "google_calendar_availability_inspection": {
            "provider": "google_calendar",
            "workflow_kind": "availability_inspection",
            "approved_operations": [
                "calendar.google_calendar_read_availability",
            ],
            "daily_use_ready": False,
            "daily_use_state": "blocked_missing_provider_credentials",
            "user_opt_in_required": True,
            "mutation_confirmation_required": False,
            "planning_boundary": "availability_evidence_only_no_calendar_management",
            "next_action": "configure_google_calendar_access_token_calendar_id_and_timezone",
        },
        "google_drive_file_space_inspection": {
            "provider": "google_drive",
            "workflow_kind": "file_space_inspection",
            "approved_operations": [
                "cloud_drive.google_drive_list_files",
            ],
            "daily_use_ready": False,
            "daily_use_state": "blocked_missing_provider_credentials",
            "user_opt_in_required": True,
            "mutation_confirmation_required": False,
            "planning_boundary": "metadata_only_file_evidence_no_document_body_ingestion",
            "next_action": "configure_google_drive_access_token_and_folder_id",
        },
    }


def _capability_catalog_snapshot() -> dict[str, object]:
    return {
        "policy_owner": "backend_capability_catalog_policy",
        "catalog_posture": "aggregated_backend_truth_surface",
        "aggregation_boundary": "composed_from_existing_health_and_internal_inspection_surfaces",
        "execution_authority": "unchanged_action_boundary",
        "authorization_authority": "unchanged_connector_permission_gates",
        "capability_record_truth_model": {
            "description_boundary": "durable_role_and_skill_metadata_plus_tool_authorization_records",
            "selection_boundary": "runtime_turn_selection_and_selected_skill_metadata",
            "authorization_boundary": "connector_permission_gates_plus_provider_readiness",
        },
        "future_ui_posture": "consume_catalog_without_reconstructing_backend_truth_client_side",
        "source_surfaces": {
            "api_readiness": "/health.api_readiness",
            "learned_state": "/health.learned_state",
            "role_skill": "/health.role_skill",
            "connectors": "/health.connectors",
            "internal_inspection": "/internal/state/inspect",
            "current_turn_role": "system_debug.role",
            "current_turn_selected_skills": "system_debug.adaptive_state.selected_skills",
            "current_turn_plan": "system_debug.plan",
        },
        "role_posture": {
            "role_selection_owner": "role_selection_policy",
            "current_role_name": "",
            "work_partner_role_available": True,
            "work_partner_role_state": "available",
            "work_partner_scope": "work_organization_and_decision_support",
            "work_partner_mutation_boundary": "respect_existing_confirmation_and_opt_in_policies",
            "described_role_presets": [
                {
                    "role_name": "friend",
                    "label": "Friend",
                    "prompt_posture": "supportive_relational",
                    "record_kind": "durable_role_preset",
                    "selection_authority": "runtime_turn_selection",
                    "selection_state": "available",
                },
                {
                    "role_name": "advisor",
                    "label": "Advisor",
                    "prompt_posture": "risk_aware_guidance",
                    "record_kind": "durable_role_preset",
                    "selection_authority": "runtime_turn_selection",
                    "selection_state": "available",
                },
                {
                    "role_name": "analyst",
                    "label": "Analyst",
                    "prompt_posture": "structured_analysis",
                    "record_kind": "durable_role_preset",
                    "selection_authority": "runtime_turn_selection",
                    "selection_state": "available",
                },
                {
                    "role_name": "executor",
                    "label": "Executor",
                    "prompt_posture": "bounded_execution",
                    "record_kind": "durable_role_preset",
                    "selection_authority": "runtime_turn_selection",
                    "selection_state": "available",
                },
                {
                    "role_name": "mentor",
                    "label": "Mentor",
                    "prompt_posture": "guided_help",
                    "record_kind": "durable_role_preset",
                    "selection_authority": "runtime_turn_selection",
                    "selection_state": "available",
                },
                {
                    "role_name": "work_partner",
                    "label": "Work partner",
                    "prompt_posture": "organization_and_decision_support",
                    "record_kind": "durable_role_preset",
                    "selection_authority": "runtime_turn_selection",
                    "selection_state": "available",
                },
            ],
            "described_role_names": [
                "friend",
                "advisor",
                "analyst",
                "executor",
                "mentor",
                "work_partner",
            ],
            "selectable_role_names": [
                "friend",
                "advisor",
                "analyst",
                "executor",
                "mentor",
                "work_partner",
            ],
            "preferred_role_eligible_names": [
                "analyst",
                "executor",
                "friend",
                "mentor",
                "work_partner",
            ],
        },
        "skill_catalog_posture": {
            "skill_selection_owner": "skill_registry",
            "skill_execution_boundary": "metadata_only_capability_hints",
            "action_skill_execution_allowed": False,
            "selection_visibility_summary": {},
            "catalog_count": 5,
            "catalog": [
                {
                    "skill_id": "emotional_support",
                    "label": "Emotional support",
                    "capability_family": "support",
                    "side_effect_posture": "metadata_only",
                },
                {
                    "skill_id": "structured_reasoning",
                    "label": "Structured reasoning",
                    "capability_family": "analysis",
                    "side_effect_posture": "metadata_only",
                },
                {
                    "skill_id": "execution_planning",
                    "label": "Execution planning",
                    "capability_family": "execution",
                    "side_effect_posture": "metadata_only",
                },
                {
                    "skill_id": "memory_recall",
                    "label": "Memory recall",
                    "capability_family": "memory",
                    "side_effect_posture": "metadata_only",
                },
                {
                    "skill_id": "connector_boundary_review",
                    "label": "Connector boundary review",
                    "capability_family": "connector_boundary",
                    "side_effect_posture": "metadata_only",
                },
            ],
            "described_skill_ids": [
                "emotional_support",
                "structured_reasoning",
                "execution_planning",
                "memory_recall",
                "connector_boundary_review",
            ],
            "runtime_selection_surface": "system_debug.adaptive_state.selected_skills",
            "learning_posture": "registry_metadata_only",
            "learning_hint": "selected_skill_metadata_is_inspectable_but_not_self_modifying_code",
        },
        "tool_and_connector_posture": {
            "authorization_record_owner": "connector_execution_policy",
            "authorization_subject": "global_runtime_policy_posture",
            "authorization_record_state": "global_policy_and_provider_posture",
            "approved_tool_families": CAPABILITY_CATALOG_APPROVED_TOOL_FAMILIES,
            "selectable_tool_families": CAPABILITY_CATALOG_APPROVED_TOOL_FAMILIES,
            "approved_operations": ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS,
            "authorized_without_opt_in_operations": [
                "knowledge_search.search_web",
                "knowledge_search.suggest_search",
                "web_browser.read_page",
                "web_browser.suggest_page_review",
            ],
            "authorized_with_opt_in_operations": [
                "calendar.read_availability",
                "calendar.suggest_slots",
                "cloud_drive.list_files",
                "cloud_drive.read_document",
                "cloud_drive.search_documents",
                "cloud_drive.suggest_file_plan",
                "task_system.link_internal_task",
                "task_system.list_tasks",
                "task_system.suggest_sync",
            ],
            "authorized_with_confirmation_operations": [
                "calendar.cancel_event",
                "calendar.create_event",
                "calendar.update_event",
                "cloud_drive.delete_file",
                "cloud_drive.update_document",
                "cloud_drive.upload_file",
                "task_system.create_task",
                "task_system.update_task",
            ],
            "ready_operations": [
                "task_system.clickup_create_task",
                "task_system.clickup_list_tasks",
                "task_system.clickup_update_task",
            ],
            "credential_gap_operations": [
                "calendar.google_calendar_read_availability",
                "cloud_drive.google_drive_list_files",
            ],
            "organizer_stack_state": "provider_credentials_missing",
            "organizer_stack_hint": "configure_clickup_google_calendar_and_google_drive_credentials_for_full_stack_readiness",
            "organizer_activation_state": "provider_activation_incomplete",
            "organizer_activation_next_actions": ORGANIZER_TOOL_ACTIVATION_NEXT_ACTIONS,
            "confirmation_required_operations": ORGANIZER_TOOL_STACK_CONFIRMATION_REQUIRED_OPERATIONS,
            "user_opt_in_required_operations": ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS,
            "web_knowledge_tools": {
                "policy_owner": "web_knowledge_tooling_policy",
                "tool_boundary": "action_owned_external_capability",
                "skill_execution_boundary": "metadata_only_capability_hints",
                "provider_execution_posture": "first_bounded_provider_slices_selected",
                "fallback_posture": "respond_without_external_tool_execution",
                "knowledge_search": {
                    "capability_kind": "knowledge_search",
                    "selected_provider_hint": "duckduckgo_html",
                    "authorized_operations": ["search_web", "suggest_search"],
                    "execution_mode": "provider_backed_without_credentials",
                    "state": "provider_backed_ready",
                    "hint": "duckduckgo_html_search_live",
                },
                "web_browser": {
                    "capability_kind": "web_browser",
                    "selected_provider_hint": "generic_http",
                    "authorized_operations": ["read_page", "suggest_page_review"],
                    "execution_mode": "provider_backed_without_credentials",
                    "state": "provider_backed_ready",
                    "hint": "generic_http_read_page_live",
                },
                "website_reading_workflow": {
                    "policy_owner": "website_reading_workflow_policy",
                    "workflow_state": "ready_for_direct_and_search_first_review",
                    "direct_url_review_available": True,
                    "search_then_page_review_available": True,
                    "allowed_entry_modes": [
                        "direct_url_review",
                        "search_then_page_review",
                    ],
                    "selected_provider_path": {
                        "search_provider_hint": "duckduckgo_html",
                        "page_read_provider_hint": "generic_http",
                    },
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
                    "blockers": [],
                    "next_actions": [],
                },
            },
            "execution_baseline_owner": "connector_execution_registry",
            "execution_baseline_boundary": "clickup_task_create_list_update_plus_google_calendar_google_drive_duckduckgo_and_generic_http_first_live_paths",
        },
        "learned_state_linkage": {
            "learned_state_policy_owner": "learned_state_inspection_policy",
            "tool_grounded_learning_policy_owner": "tool_grounded_learning_policy",
            "skill_learning_posture": "selected_skill_metadata_only",
            "internal_inspection_path": "/internal/state/inspect",
        },
    }


class _StubAionHandler(BaseHTTPRequestHandler):
    health_payload: dict[str, object] = {}
    event_payload: dict[str, object] = {}
    web_build_revision: str = LOCAL_REPO_HEAD_SHA
    web_routes_missing_revision: set[str] = set()
    health_payload_sequence: list[dict[str, object]] = []
    health_status_code: int = 200
    health_status_code_sequence: list[int] = []
    health_request_count: int = 0
    sync_web_build_revision_from_health: bool = False

    def _write_json(self, payload: dict[str, object], *, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_html(self, html: str, *, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/chat", "/settings", "/tools", "/personality"}:
            revision = type(self).web_build_revision
            if self.path in type(self).web_routes_missing_revision:
                revision = ""
            self._write_html(
                (
                    "<!doctype html><html><head>"
                    f'<meta name="aion-web-build-revision" content="{revision}" />'
                    "</head><body><div id=\"root\"></div></body></html>"
                )
            )
            return
        if self.path == "/health":
            handler_type = type(self)
            payload = handler_type.health_payload
            status_code = handler_type.health_status_code
            if handler_type.health_payload_sequence:
                index = min(
                    handler_type.health_request_count,
                    len(handler_type.health_payload_sequence) - 1,
                )
                payload = handler_type.health_payload_sequence[index]
            if handler_type.health_status_code_sequence:
                status_index = min(
                    handler_type.health_request_count,
                    len(handler_type.health_status_code_sequence) - 1,
                )
                status_code = handler_type.health_status_code_sequence[status_index]
            handler_type.health_request_count += 1

            deployment = payload.get("deployment") if isinstance(payload, dict) else None
            if handler_type.sync_web_build_revision_from_health and isinstance(deployment, dict):
                runtime_build_revision = deployment.get("runtime_build_revision")
                if isinstance(runtime_build_revision, str) and runtime_build_revision:
                    handler_type.web_build_revision = runtime_build_revision

            self._write_json(payload, status=status_code)
            return
        self._write_json({"detail": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/event":
            self._write_json({"detail": "not found"}, status=404)
            return

        body_length = int(self.headers.get("Content-Length", "0"))
        if body_length > 0:
            self.rfile.read(body_length)

        payload = dict(type(self).event_payload)
        query = parse_qs(parsed.query)
        if query.get("debug") == ["true"]:
            payload.setdefault("debug", {"mode": "debug"})
        self._write_json(payload)


class _StubAionServer:
    def __init__(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _StubAionHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def start(self) -> "_StubAionServer":
        self.thread.start()
        return self

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


@pytest.fixture
def stub_aion_server() -> _StubAionServer:
    _StubAionHandler.web_build_revision = LOCAL_REPO_HEAD_SHA
    _StubAionHandler.web_routes_missing_revision = set()
    _StubAionHandler.health_payload_sequence = []
    _StubAionHandler.health_status_code = 200
    _StubAionHandler.health_status_code_sequence = []
    _StubAionHandler.health_request_count = 0
    _StubAionHandler.sync_web_build_revision_from_health = False
    _StubAionHandler.health_payload = {
        "status": "ok",
        "runtime_policy": {
            "startup_schema_compatibility_posture": "migration_only",
            "startup_schema_compatibility_sunset_ready": True,
            "startup_schema_compatibility_sunset_reason": "migration_only_baseline_active",
            "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
            "event_debug_admin_ingress_target_path": "/internal/event/debug",
            "event_debug_admin_posture_state": "debug_disabled_admin_route_primary_by_default",
            "event_debug_internal_ingress_path": "/internal/event/debug",
            "event_debug_shared_ingress_path": "/event/debug",
            "event_debug_shared_ingress_mode": "break_glass_only",
            "event_debug_shared_ingress_break_glass_required": True,
            "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
            "event_debug_shared_ingress_retirement_blockers": [],
            "event_debug_shared_ingress_retirement_ready": True,
            "event_debug_enabled": False,
            "event_debug_shared_ingress_sunset_ready": True,
            "event_debug_shared_ingress_sunset_reason": "shared_debug_route_disabled_with_debug_payload_off",
            "compatibility_sunset_ready": True,
            "compatibility_sunset_blockers": [],
            "strict_startup_blocked": False,
            "event_debug_query_compat_enabled": False,
            "production_policy_mismatches": [],
        },
        "release_readiness": {
            "ready": True,
            "violations": [],
        },
        "v1_readiness": {
            "policy_owner": "v1_release_readiness_policy",
            "product_stage": "v1_no_ui_life_assistant",
            "conversation_gate_state": "conversation_surface_ready",
            "learned_state_gate_state": "inspection_surface_ready",
            "website_reading_workflow_state": "ready_for_direct_and_search_first_review",
            "tool_grounded_learning_state": "tool_grounded_learning_surface_ready",
            "time_aware_planned_work_policy_owner": "internal_time_aware_planned_work_policy",
            "time_aware_planned_work_delivery_path": "attention_to_planning_to_expression_to_action",
            "time_aware_planned_work_recurrence_owner": "scheduler_reevaluation_with_foreground_handoff",
            "time_aware_planned_work_gate_state": "foreground_due_delivery_and_recurring_reevaluation_ready",
            "deploy_parity_state": "deploy_parity_surface_ready",
            "organizer_daily_use_state": "daily_use_workflows_blocked_by_provider_activation",
            "organizer_daily_use_classification": "extension_readiness_non_blocking_for_core_v1",
            "organizer_daily_use_total_workflow_count": 3,
            "organizer_daily_use_ready_workflow_count": 1,
            "organizer_daily_use_ready_workflows": ORGANIZER_DAILY_USE_READY_WORKFLOWS,
            "organizer_daily_use_blocked_workflows": ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS,
            "final_acceptance_state": "core_v1_bundle_ready",
            "final_acceptance_gate_states": {
                "conversation_reliability": "conversation_surface_ready",
                "learned_state_inspection": "inspection_surface_ready",
                "website_reading": "ready_for_direct_and_search_first_review",
                "tool_grounded_learning": "tool_grounded_learning_surface_ready",
                "time_aware_planned_work": "foreground_due_delivery_and_recurring_reevaluation_ready",
                "deploy_parity": "deploy_parity_surface_ready",
            },
            "final_acceptance_surfaces": {
                "conversation_reliability": "/health.conversation_channels.telegram",
                "learned_state_inspection": "/health.learned_state",
                "website_reading": "/health.connectors.web_knowledge_tools.website_reading_workflow",
                "tool_grounded_learning": "/health.learned_state.tool_grounded_learning",
                "time_aware_planned_work": "/health.v1_readiness",
                "deploy_parity": "/health.deployment",
            },
            "extension_gate_states": {
                "organizer_daily_use": "daily_use_workflows_blocked_by_provider_activation",
            },
            "extension_gate_surfaces": {
                "organizer_daily_use": "/health.connectors.organizer_tool_stack",
            },
            "required_behavior_scenarios": V1_REQUIRED_BEHAVIOR_SCENARIOS,
            "approved_tool_slices": V1_APPROVED_TOOL_SLICES,
        },
        "runtime_topology": {
            "policy_owner": "runtime_topology_finalization",
            "release_window": "after_group_50_evidence_green",
            "attention_switch": {
                "policy_owner": "runtime_topology_finalization",
                "selected_mode": "durable_inbox",
                "production_default_change_ready": True,
            },
        },
        "attention": {
            "attention_policy_owner": "durable_attention_inbox_policy",
            "coordination_mode": "durable_inbox",
            "contract_store_mode": "repository_backed",
            "deployment_readiness": {
                "selected_coordination_mode": "durable_inbox",
                "contract_store_state": "repository_backed_contract_store_active",
                "store_available": True,
            },
        },
        "proactive": {
            "policy_owner": "proactive_runtime_policy",
            "enabled": True,
            "production_baseline_ready": True,
            "production_baseline_state": "external_scheduler_target_owner",
            "planned_action_observer": dict(PLANNED_ACTION_OBSERVER_POSTURE),
        },
        "deployment": {
            "deployment_automation_policy_owner": "coolify_repo_deploy_automation",
            "hosting_baseline": "coolify_medium_term_standard",
            "runtime_build_revision": LOCAL_REPO_HEAD_SHA,
            "runtime_build_revision_state": "runtime_build_revision_declared",
            "runtime_build_revision_hint": "runtime_build_revision_can_be_compared_with_local_repo_head_or_deploy_evidence",
            "runtime_trigger_mode": "source_automation",
            "runtime_trigger_class": "primary_automation",
            "runtime_provenance_state": "primary_runtime_provenance_declared",
            "repo_to_production_parity_surface": "release_smoke_compares_runtime_build_revision_with_local_repo_head_and_optional_deploy_evidence",
            "canonical_coolify_app": {
                "project_id": "icmgqml9uw3slzch9m9ok23z",
                "environment_id": "qxooi9coxat272krzjx221fv",
                "application_id": "jr1oehwlzl8tcn3h8gh2vvih",
            },
            "deployment_automation_baseline": {
                "primary_trigger_mode": "source_automation",
                "fallback_trigger_modes": [
                    "webhook_manual_fallback",
                    "ui_manual_fallback",
                ],
                "provenance_evidence_state": "fallback_artifact_supported_primary_history_required",
                "provenance_evidence_hint": "verify_coolify_history_and_attach_fallback_artifact_when_primary_automation_is_not_used",
            },
            "deployment_trigger_slo": {
                "delivery_success_rate_percent": 99.0,
                "manual_redeploy_exception_rate_percent": 5.0,
                "evidence_owner": "coolify_webhook_plus_release_smoke",
            },
        },
        "memory_retrieval": {
            "semantic_embedding_provider_requested": "openai",
            "semantic_embedding_provider_effective": "openai",
            "semantic_embedding_model_requested": "text-embedding-3-small",
            "semantic_embedding_model_effective": "text-embedding-3-small",
            "semantic_embedding_execution_class": "provider_owned_openai_api",
            "semantic_embedding_production_baseline_state": "aligned_openai_provider_owned",
            "retrieval_lifecycle_policy_owner": "retrieval_lifecycle_policy",
            "retrieval_lifecycle_relation_source_policy_owner": "relation_source_retrieval_policy",
            "retrieval_lifecycle_relation_source_posture": "optional_after_foreground_baseline",
            "retrieval_lifecycle_relation_source_state": "optional_family_not_enabled",
            "retrieval_lifecycle_relation_source_enabled": False,
            "retrieval_lifecycle_provider_drift_state": "aligned_target_provider",
            "retrieval_lifecycle_alignment_state": "aligned_with_defined_lifecycle_baseline",
            "retrieval_lifecycle_pending_gaps": [],
        },
        "observability": {
            "policy_owner": "incident_evidence_export_policy",
            "export_artifact_available": True,
            "incident_export_ready": True,
        },
        "learned_state": {
            "policy_owner": "learned_state_inspection_policy",
            "internal_inspection_path": "/internal/state/inspect",
            "inspection_sections": LEARNED_STATE_INSPECTION_SECTIONS,
            "growth_summary_sections": LEARNED_STATE_GROWTH_SUMMARY_SECTIONS,
            "role_skill_metadata_sections": LEARNED_STATE_ROLE_SKILL_METADATA_SECTIONS,
            "planning_continuity_sections": LEARNED_STATE_PLANNING_CONTINUITY_SECTIONS,
            "reflection_growth_signal_kinds": LEARNED_STATE_REFLECTION_GROWTH_SIGNAL_KINDS,
            "tool_grounded_learning": TOOL_GROUNDED_LEARNING_CONTRACT,
        },
        "capability_catalog": _capability_catalog_snapshot(),
        "connectors": {
            "organizer_tool_stack": {
                "policy_owner": "production_organizer_tool_stack",
                "stack_name": "clickup_calendar_drive_first_stack",
                "approved_connector_kinds": ["task_system", "calendar", "cloud_drive"],
                "approved_operations": ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS,
                "read_only_operations": ORGANIZER_TOOL_STACK_READ_ONLY_OPERATIONS,
                "confirmation_required_operations": ORGANIZER_TOOL_STACK_CONFIRMATION_REQUIRED_OPERATIONS,
                "user_opt_in_required_operations": ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS,
                "ready_operations": [
                    "task_system.clickup_create_task",
                    "task_system.clickup_list_tasks",
                    "task_system.clickup_update_task",
                ],
                "credential_gap_operations": [
                    "calendar.google_calendar_read_availability",
                    "cloud_drive.google_drive_list_files",
                ],
                "readiness_state": "provider_credentials_missing",
                "daily_use_workflows": _organizer_daily_use_workflows(),
                "daily_use_ready_workflow_count": 1,
                "daily_use_total_workflow_count": 3,
                "daily_use_ready_workflows": ORGANIZER_DAILY_USE_READY_WORKFLOWS,
                "daily_use_blocked_workflows": ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS,
                "daily_use_state": "daily_use_workflows_blocked_by_provider_activation",
                "daily_use_hint": "finish_provider_activation_before_treating_organizer_stack_as_daily_use_ready",
                "activation_snapshot": _organizer_tool_activation_snapshot(),
            },
            "web_knowledge_tools": {
                "policy_owner": "web_knowledge_tooling_policy",
                "tool_boundary": "action_owned_external_capability",
                "skill_execution_boundary": "metadata_only_capability_hints",
                "provider_execution_posture": "first_bounded_provider_slices_selected",
                "fallback_posture": "respond_without_external_tool_execution",
                "knowledge_search": {
                    "capability_kind": "knowledge_search",
                    "selected_provider_hint": "duckduckgo_html",
                    "authorized_operations": ["search_web", "suggest_search"],
                    "execution_mode": "provider_backed_without_credentials",
                    "state": "provider_backed_ready",
                    "hint": "duckduckgo_html_search_live",
                },
                "web_browser": {
                    "capability_kind": "web_browser",
                    "selected_provider_hint": "generic_http",
                    "authorized_operations": ["read_page", "suggest_page_review"],
                    "execution_mode": "provider_backed_without_credentials",
                    "state": "provider_backed_ready",
                    "hint": "generic_http_read_page_live",
                },
                "website_reading_workflow": {
                    "policy_owner": "website_reading_workflow_policy",
                    "workflow_state": "ready_for_direct_and_search_first_review",
                    "direct_url_review_available": True,
                    "search_then_page_review_available": True,
                    "allowed_entry_modes": [
                        "direct_url_review",
                        "search_then_page_review",
                    ],
                    "selected_provider_path": {
                        "search_provider_hint": "duckduckgo_html",
                        "page_read_provider_hint": "generic_http",
                    },
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
                    "blockers": [],
                    "next_actions": [],
                },
            },
        },
        "conversation_channels": {
            "telegram": {
                "policy_owner": "telegram_conversation_reliability_telemetry",
                "round_trip_ready": True,
                "round_trip_state": "provider_backed_ready",
                "bot_token_configured": True,
                "delivery_adaptation_policy_owner": "telegram_delivery_channel_adaptation",
                "delivery_segmentation_state": "bounded_transport_segmentation",
                "delivery_formatting_state": "supported_markdown_to_html_with_plain_text_fallback",
                "delivery_attempts": 2,
                "delivery_failures": 0,
            },
        },
        "scheduler": {
            "healthy": True,
            "external_owner_policy": {
                "policy_owner": "external_scheduler_cadence_policy",
                "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                "maintenance_entrypoint_path": "scripts/run_maintenance_tick_once.py",
                "proactive_entrypoint_path": "scripts/run_proactive_tick_once.py",
                "maintenance_run_evidence": {
                    "evidence_state": "missing_external_run_evidence",
                },
                "proactive_run_evidence": {
                    "evidence_state": "missing_external_run_evidence",
                },
                "duplicate_protection_posture": {
                    "state": "single_owner_boundary_clear",
                },
                "cutover_proof_ready": False,
                "production_baseline_ready": False,
                "production_baseline_state": "external_scheduler_target_without_cutover_proof",
            },
        },
        "reflection": {
            "healthy": True,
            "deployment_readiness": {
                "ready": True,
                "blocking_signals": [],
            },
            "external_driver_policy": {
                "policy_owner": "deferred_reflection_external_worker",
                "entrypoint_path": "scripts/run_reflection_queue_once.py",
                "production_baseline_ready": False,
            },
            "supervision": {
                "policy_owner": "deferred_reflection_supervision_policy",
                "queue_health_state": "active_backlog_under_supervision",
                "production_supervision_ready": True,
                "production_supervision_state": "deferred_supervision_active_backlog",
                "blocking_signals": [],
                "recovery_actions": [],
            },
        },
    }
    _StubAionHandler.event_payload = {
        "event_id": "evt-test",
        "trace_id": "trace-test",
        "reply": {
            "message": "Smoke response",
            "language": "en",
            "tone": "supportive",
            "channel": "api",
        },
        "runtime": {
            "role": "advisor",
            "motivation_mode": "respond",
            "action_status": "success",
            "reflection_triggered": False,
        },
        "incident_evidence": {
            "kind": "runtime_incident_evidence",
            "schema_version": "1.0.0",
            "policy_owner": "incident_evidence_export_policy",
            "trace_id": "trace-test",
            "event_id": "evt-test",
            "source": "api",
            "duration_ms": 12,
            "stage_timings_ms": {
                "memory_load": 1,
                "perception": 2,
                "action": 3,
                "total": 12,
            },
            "policy_surface_coverage": {
            "present": [
                "runtime_policy",
                "memory_retrieval",
                "learned_state",
                "v1_readiness",
                "deployment",
                "attention",
                "runtime_topology.attention_switch",
                "proactive",
                "scheduler.external_owner_policy",
                "reflection.supervision",
                "connectors.execution_baseline",
                "connectors.organizer_tool_stack",
                "connectors.web_knowledge_tools",
                "conversation_channels.telegram",
            ],
                "missing": [],
                "complete": True,
            },
            "policy_posture": {
                "runtime_policy": {
                    "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                    "event_debug_admin_ingress_target_path": "/internal/event/debug",
                    "event_debug_shared_ingress_mode": "break_glass_only",
                    "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
                    "event_debug_query_compat_enabled": False,
                    "event_debug_shared_ingress_retirement_ready": True,
                    "event_debug_shared_ingress_sunset_ready": True,
                    "event_debug_shared_ingress_sunset_reason": "shared_debug_route_break_glass_only",
                },
                "memory_retrieval": {
                    "semantic_embedding_provider_requested": "openai",
                    "semantic_embedding_provider_effective": "openai",
                    "semantic_embedding_model_requested": "text-embedding-3-small",
                    "semantic_embedding_model_effective": "text-embedding-3-small",
                    "semantic_embedding_execution_class": "provider_owned_openai_api",
                    "semantic_embedding_production_baseline_state": "aligned_openai_provider_owned",
                    "retrieval_lifecycle_policy_owner": "retrieval_lifecycle_policy",
                    "retrieval_lifecycle_relation_source_policy_owner": "relation_source_retrieval_policy",
                    "retrieval_lifecycle_relation_source_posture": "optional_after_foreground_baseline",
                    "retrieval_lifecycle_relation_source_state": "optional_family_not_enabled",
                    "retrieval_lifecycle_relation_source_enabled": False,
                    "retrieval_lifecycle_provider_drift_state": "aligned_target_provider",
                    "retrieval_lifecycle_alignment_state": "aligned_with_defined_lifecycle_baseline",
                    "retrieval_lifecycle_pending_gaps": [],
                },
                "learned_state": {
                    "policy_owner": "learned_state_inspection_policy",
                    "internal_inspection_path": "/internal/state/inspect",
                    "inspection_sections": LEARNED_STATE_INSPECTION_SECTIONS,
                    "growth_summary_sections": LEARNED_STATE_GROWTH_SUMMARY_SECTIONS,
                    "role_skill_metadata_sections": LEARNED_STATE_ROLE_SKILL_METADATA_SECTIONS,
                    "planning_continuity_sections": LEARNED_STATE_PLANNING_CONTINUITY_SECTIONS,
                    "reflection_growth_signal_kinds": LEARNED_STATE_REFLECTION_GROWTH_SIGNAL_KINDS,
                    "tool_grounded_learning": TOOL_GROUNDED_LEARNING_CONTRACT,
                },
                "v1_readiness": {
                    "policy_owner": "v1_release_readiness_policy",
                    "product_stage": "v1_no_ui_life_assistant",
                    "conversation_gate_state": "conversation_surface_ready",
                    "learned_state_gate_state": "inspection_surface_ready",
                    "website_reading_workflow_state": "ready_for_direct_and_search_first_review",
                    "tool_grounded_learning_state": "tool_grounded_learning_surface_ready",
                    "time_aware_planned_work_policy_owner": "internal_time_aware_planned_work_policy",
                    "time_aware_planned_work_delivery_path": "attention_to_planning_to_expression_to_action",
                    "time_aware_planned_work_recurrence_owner": "scheduler_reevaluation_with_foreground_handoff",
                    "time_aware_planned_work_gate_state": "foreground_due_delivery_and_recurring_reevaluation_ready",
                    "deploy_parity_state": "deploy_parity_surface_ready",
                    "organizer_daily_use_state": "daily_use_workflows_blocked_by_provider_activation",
                    "organizer_daily_use_classification": "extension_readiness_non_blocking_for_core_v1",
                    "organizer_daily_use_ready_workflow_count": 1,
                    "organizer_daily_use_total_workflow_count": 3,
                    "organizer_daily_use_ready_workflows": ORGANIZER_DAILY_USE_READY_WORKFLOWS,
                    "organizer_daily_use_blocked_workflows": ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS,
                    "final_acceptance_state": "core_v1_bundle_ready",
                    "final_acceptance_gate_states": {
                        "conversation_reliability": "conversation_surface_ready",
                        "learned_state_inspection": "inspection_surface_ready",
                        "website_reading": "ready_for_direct_and_search_first_review",
                        "tool_grounded_learning": "tool_grounded_learning_surface_ready",
                        "time_aware_planned_work": "foreground_due_delivery_and_recurring_reevaluation_ready",
                        "deploy_parity": "deploy_parity_surface_ready",
                    },
                    "final_acceptance_surfaces": {
                        "conversation_reliability": "/health.conversation_channels.telegram",
                        "learned_state_inspection": "/health.learned_state",
                        "website_reading": "/health.connectors.web_knowledge_tools.website_reading_workflow",
                        "tool_grounded_learning": "/health.learned_state.tool_grounded_learning",
                        "time_aware_planned_work": "/health.v1_readiness",
                        "deploy_parity": "/health.deployment",
                    },
                    "extension_gate_states": {
                        "organizer_daily_use": "daily_use_workflows_blocked_by_provider_activation",
                    },
                    "extension_gate_surfaces": {
                        "organizer_daily_use": "/health.connectors.organizer_tool_stack",
                    },
                    "required_behavior_scenarios": V1_REQUIRED_BEHAVIOR_SCENARIOS,
                    "approved_tool_slices": V1_APPROVED_TOOL_SLICES,
                },
            "deployment": {
                "deployment_automation_policy_owner": "coolify_repo_deploy_automation",
                "runtime_build_revision": LOCAL_REPO_HEAD_SHA,
                "runtime_build_revision_state": "runtime_build_revision_declared",
                "runtime_build_revision_hint": "runtime_build_revision_can_be_compared_with_local_repo_head_or_deploy_evidence",
                "runtime_trigger_mode": "source_automation",
                "runtime_trigger_class": "primary_automation",
                "runtime_provenance_state": "primary_runtime_provenance_declared",
                "repo_to_production_parity_surface": "release_smoke_compares_runtime_build_revision_with_local_repo_head_and_optional_deploy_evidence",
                "canonical_coolify_app": {
                    "project_id": "icmgqml9uw3slzch9m9ok23z",
                    "environment_id": "qxooi9coxat272krzjx221fv",
                    "application_id": "jr1oehwlzl8tcn3h8gh2vvih",
                },
                "deployment_automation_baseline": {
                    "primary_trigger_mode": "source_automation",
                    "fallback_trigger_modes": [
                        "webhook_manual_fallback",
                        "ui_manual_fallback",
                    ],
                },
            },
            "attention": {
                "attention_policy_owner": "durable_attention_inbox_policy",
                "coordination_mode": "durable_inbox",
                "deployment_readiness": {
                    "selected_coordination_mode": "durable_inbox",
                    "contract_store_state": "repository_backed_contract_store_active",
                    "store_available": True,
                },
            },
            "runtime_topology.attention_switch": {
                "policy_owner": "runtime_topology_finalization",
                "selected_mode": "durable_inbox",
                "production_default_change_ready": True,
            },
            "proactive": {
                "policy_owner": "proactive_runtime_policy",
                "enabled": True,
                "production_baseline_ready": True,
                "production_baseline_state": "external_scheduler_target_owner",
                "planned_action_observer": dict(PLANNED_ACTION_OBSERVER_POSTURE),
            },
            "scheduler.external_owner_policy": {
                "policy_owner": "external_scheduler_cadence_policy",
                    "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                    "maintenance_run_evidence": {
                        "evidence_state": "missing_external_run_evidence",
                    },
                    "proactive_run_evidence": {
                        "evidence_state": "missing_external_run_evidence",
                    },
                    "duplicate_protection_posture": {
                        "state": "single_owner_boundary_clear",
                    },
                    "cutover_proof_ready": False,
                    "cutover_proof_state": "external_scheduler_target_only",
                },
                "reflection.supervision": {
                    "policy_owner": "deferred_reflection_supervision_policy",
                },
                "connectors.execution_baseline": {
                    "execution_owner": "connector_execution_registry",
                },
                "connectors.organizer_tool_stack": {
                    "policy_owner": "production_organizer_tool_stack",
                    "stack_name": "clickup_calendar_drive_first_stack",
                    "approved_connector_kinds": ["task_system", "calendar", "cloud_drive"],
                    "approved_operations": ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS,
                    "read_only_operations": ORGANIZER_TOOL_STACK_READ_ONLY_OPERATIONS,
                    "confirmation_required_operations": ORGANIZER_TOOL_STACK_CONFIRMATION_REQUIRED_OPERATIONS,
                    "user_opt_in_required_operations": ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS,
                    "ready_operations": [
                        "task_system.clickup_create_task",
                        "task_system.clickup_list_tasks",
                        "task_system.clickup_update_task",
                    ],
                    "credential_gap_operations": [
                        "calendar.google_calendar_read_availability",
                        "cloud_drive.google_drive_list_files",
                    ],
                    "readiness_state": "provider_credentials_missing",
                    "daily_use_workflows": _organizer_daily_use_workflows(),
                    "daily_use_ready_workflow_count": 1,
                    "daily_use_total_workflow_count": 3,
                    "daily_use_ready_workflows": ORGANIZER_DAILY_USE_READY_WORKFLOWS,
                    "daily_use_blocked_workflows": ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS,
                    "daily_use_state": "daily_use_workflows_blocked_by_provider_activation",
                    "daily_use_hint": "finish_provider_activation_before_treating_organizer_stack_as_daily_use_ready",
                    "activation_snapshot": _organizer_tool_activation_snapshot(),
                },
                "connectors.web_knowledge_tools": {
                    "policy_owner": "web_knowledge_tooling_policy",
                    "tool_boundary": "action_owned_external_capability",
                    "skill_execution_boundary": "metadata_only_capability_hints",
                    "provider_execution_posture": "first_bounded_provider_slices_selected",
                    "fallback_posture": "respond_without_external_tool_execution",
                    "knowledge_search": {
                        "capability_kind": "knowledge_search",
                        "selected_provider_hint": "duckduckgo_html",
                        "authorized_operations": ["search_web", "suggest_search"],
                        "execution_mode": "provider_backed_without_credentials",
                        "state": "provider_backed_ready",
                        "hint": "duckduckgo_html_search_live",
                    },
                    "web_browser": {
                        "capability_kind": "web_browser",
                        "selected_provider_hint": "generic_http",
                        "authorized_operations": ["read_page", "suggest_page_review"],
                        "execution_mode": "provider_backed_without_credentials",
                        "state": "provider_backed_ready",
                        "hint": "generic_http_read_page_live",
                    },
                    "website_reading_workflow": {
                        "policy_owner": "website_reading_workflow_policy",
                        "workflow_state": "ready_for_direct_and_search_first_review",
                        "direct_url_review_available": True,
                        "search_then_page_review_available": True,
                        "allowed_entry_modes": [
                            "direct_url_review",
                            "search_then_page_review",
                        ],
                        "selected_provider_path": {
                            "search_provider_hint": "duckduckgo_html",
                            "page_read_provider_hint": "generic_http",
                        },
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
                        "blockers": [],
                        "next_actions": [],
                    },
                },
                "conversation_channels.telegram": {
                    "policy_owner": "telegram_conversation_reliability_telemetry",
                    "round_trip_ready": True,
                    "round_trip_state": "provider_backed_ready",
                    "bot_token_configured": True,
                    "delivery_adaptation_policy_owner": "telegram_delivery_channel_adaptation",
                    "delivery_segmentation_state": "bounded_transport_segmentation",
                    "delivery_formatting_state": "supported_markdown_to_html_with_plain_text_fallback",
                },
            },
        },
    }
    server = _StubAionServer().start()
    try:
        yield server
    finally:
        server.stop()


def _run_release_smoke(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    powershell_exe = _powershell_exe()
    if powershell_exe is None:
        pytest.skip("PowerShell executable is unavailable in this environment.")

    return subprocess.run(
        [powershell_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(RELEASE_SMOKE_PS1_PATH), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )


def test_behavior_validation_powershell_wrapper_resolves_python_from_repo_root(tmp_path: Path) -> None:
    powershell_exe = _powershell_exe()
    if powershell_exe is None:
        pytest.skip("PowerShell executable is unavailable in this environment.")

    input_artifact = tmp_path / "behavior-input.json"
    output_artifact = tmp_path / "behavior-output.json"
    input_artifact.write_text(
        json.dumps(
            {
                "kind": "behavior_validation_artifact",
                "summary": {
                    "total": 1,
                    "passed": 1,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 0,
                    "exit_code": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            powershell_exe,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(BACKEND_ROOT / "scripts" / "run_behavior_validation.ps1"),
            "-GateMode",
            "ci",
            "-ArtifactInputPath",
            str(input_artifact),
            "-ArtifactPath",
            str(output_artifact),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_artifact.read_text(encoding="utf-8"))
    assert payload["gate"]["status"] == "pass"
    assert payload["summary"]["total"] == 1


def _write_evidence(
    path: Path,
    *,
    minutes_ago: int = 0,
    ok: bool = True,
    status_code: int = 200,
    after_sha: str | None = None,
) -> None:
    generated_at = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    payload = {
        "kind": "coolify_deploy_webhook_evidence",
        "policy_owner": "coolify_repo_deploy_automation",
        "generated_at": generated_at.isoformat(),
        "trigger_mode": "webhook_manual_fallback",
        "trigger_class": "manual_fallback",
        "canonical_coolify_app": {
            "project_id": "icmgqml9uw3slzch9m9ok23z",
            "environment_id": "qxooi9coxat272krzjx221fv",
            "application_id": "jr1oehwlzl8tcn3h8gh2vvih",
        },
        "triggered_at": generated_at.isoformat(),
        "finished_at": generated_at.isoformat(),
        "response": {
            "ok": ok,
            "status_code": status_code,
            "body": "queued",
            "error": "",
        },
        "after_sha": after_sha or LOCAL_REPO_HEAD_SHA,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_incident_bundle(
    bundle_dir: Path,
    *,
    include_behavior_report: bool = False,
    policy_surface_complete: bool = True,
) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "kind": "incident_evidence_bundle_manifest",
        "schema_version": "1.0.0",
        "policy_owner": "incident_evidence_export_policy",
        "capture_mode": "incident",
        "trace_id": "trace-test",
        "event_id": "evt-test",
        "files": {
            "manifest": "manifest.json",
            "incident_evidence": "incident_evidence.json",
            "health_snapshot": "health_snapshot.json",
        },
    }
    if include_behavior_report:
        manifest["files"]["behavior_validation_report"] = "behavior_validation_report.json"
    incident_evidence = {
        "kind": "runtime_incident_evidence",
        "schema_version": "1.0.0",
        "policy_owner": "incident_evidence_export_policy",
        "trace_id": "trace-test",
        "event_id": "evt-test",
        "source": "api",
        "duration_ms": 12,
        "stage_timings_ms": {
            "memory_load": 1,
            "perception": 2,
            "action": 3,
            "total": 12,
        },
        "policy_surface_coverage": {
            "present": [
                "runtime_policy",
                "memory_retrieval",
                "learned_state",
                "v1_readiness",
                "deployment",
                "attention",
                "runtime_topology.attention_switch",
                "proactive",
                "scheduler.external_owner_policy",
                "reflection.supervision",
                "connectors.execution_baseline",
                "connectors.organizer_tool_stack",
                "conversation_channels.telegram",
            ],
            "missing": [],
            "complete": policy_surface_complete,
        },
            "policy_posture": {
                "runtime_policy": {
                    "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                    "event_debug_admin_ingress_target_path": "/internal/event/debug",
                    "event_debug_shared_ingress_mode": "break_glass_only",
                    "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
                    "event_debug_query_compat_enabled": False,
                    "event_debug_shared_ingress_retirement_ready": True,
                    "event_debug_shared_ingress_sunset_ready": True,
                    "event_debug_shared_ingress_sunset_reason": "shared_debug_route_break_glass_only",
                },
            "memory_retrieval": {
                "semantic_embedding_provider_requested": "openai",
                "semantic_embedding_provider_effective": "openai",
                "semantic_embedding_model_requested": "text-embedding-3-small",
                "semantic_embedding_model_effective": "text-embedding-3-small",
                "semantic_embedding_execution_class": "provider_owned_openai_api",
                "semantic_embedding_production_baseline_state": "aligned_openai_provider_owned",
                "retrieval_lifecycle_policy_owner": "retrieval_lifecycle_policy",
                "retrieval_lifecycle_relation_source_policy_owner": "relation_source_retrieval_policy",
                "retrieval_lifecycle_relation_source_posture": "optional_after_foreground_baseline",
                "retrieval_lifecycle_relation_source_state": "optional_family_not_enabled",
                "retrieval_lifecycle_relation_source_enabled": False,
                "retrieval_lifecycle_provider_drift_state": "aligned_target_provider",
                "retrieval_lifecycle_alignment_state": "aligned_with_defined_lifecycle_baseline",
                "retrieval_lifecycle_pending_gaps": [],
            },
            "learned_state": {
                "policy_owner": "learned_state_inspection_policy",
                "internal_inspection_path": "/internal/state/inspect",
                "inspection_sections": LEARNED_STATE_INSPECTION_SECTIONS,
                "growth_summary_sections": LEARNED_STATE_GROWTH_SUMMARY_SECTIONS,
                "role_skill_metadata_sections": LEARNED_STATE_ROLE_SKILL_METADATA_SECTIONS,
                "planning_continuity_sections": LEARNED_STATE_PLANNING_CONTINUITY_SECTIONS,
                "reflection_growth_signal_kinds": LEARNED_STATE_REFLECTION_GROWTH_SIGNAL_KINDS,
                "tool_grounded_learning": TOOL_GROUNDED_LEARNING_CONTRACT,
            },
            "v1_readiness": {
                "policy_owner": "v1_release_readiness_policy",
                "product_stage": "v1_no_ui_life_assistant",
                "conversation_gate_state": "conversation_surface_ready",
                "learned_state_gate_state": "inspection_surface_ready",
                "website_reading_workflow_state": "ready_for_direct_and_search_first_review",
                "tool_grounded_learning_state": "tool_grounded_learning_surface_ready",
                "time_aware_planned_work_policy_owner": "internal_time_aware_planned_work_policy",
                "time_aware_planned_work_delivery_path": "attention_to_planning_to_expression_to_action",
                "time_aware_planned_work_recurrence_owner": "scheduler_reevaluation_with_foreground_handoff",
                "time_aware_planned_work_gate_state": "foreground_due_delivery_and_recurring_reevaluation_ready",
                "deploy_parity_state": "deploy_parity_surface_ready",
                "organizer_daily_use_state": "daily_use_workflows_blocked_by_provider_activation",
                "organizer_daily_use_classification": "extension_readiness_non_blocking_for_core_v1",
                "organizer_daily_use_ready_workflow_count": 1,
                "organizer_daily_use_total_workflow_count": 3,
                "organizer_daily_use_ready_workflows": ORGANIZER_DAILY_USE_READY_WORKFLOWS,
                "organizer_daily_use_blocked_workflows": ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS,
                "final_acceptance_state": "core_v1_bundle_ready",
                "final_acceptance_gate_states": {
                    "conversation_reliability": "conversation_surface_ready",
                    "learned_state_inspection": "inspection_surface_ready",
                    "website_reading": "ready_for_direct_and_search_first_review",
                    "tool_grounded_learning": "tool_grounded_learning_surface_ready",
                    "time_aware_planned_work": "foreground_due_delivery_and_recurring_reevaluation_ready",
                    "deploy_parity": "deploy_parity_surface_ready",
                },
                "final_acceptance_surfaces": {
                    "conversation_reliability": "/health.conversation_channels.telegram",
                    "learned_state_inspection": "/health.learned_state",
                    "website_reading": "/health.connectors.web_knowledge_tools.website_reading_workflow",
                    "tool_grounded_learning": "/health.learned_state.tool_grounded_learning",
                    "time_aware_planned_work": "/health.v1_readiness",
                    "deploy_parity": "/health.deployment",
                },
                "extension_gate_states": {
                    "organizer_daily_use": "daily_use_workflows_blocked_by_provider_activation",
                },
                "extension_gate_surfaces": {
                    "organizer_daily_use": "/health.connectors.organizer_tool_stack",
                },
                "required_behavior_scenarios": V1_REQUIRED_BEHAVIOR_SCENARIOS,
                "approved_tool_slices": V1_APPROVED_TOOL_SLICES,
            },
            "deployment": {
                "deployment_automation_policy_owner": "coolify_repo_deploy_automation",
                "runtime_build_revision": LOCAL_REPO_HEAD_SHA,
                "runtime_build_revision_state": "runtime_build_revision_declared",
                "runtime_build_revision_hint": "runtime_build_revision_can_be_compared_with_local_repo_head_or_deploy_evidence",
                "runtime_trigger_mode": "source_automation",
                "runtime_trigger_class": "primary_automation",
                "runtime_provenance_state": "primary_runtime_provenance_declared",
                "repo_to_production_parity_surface": "release_smoke_compares_runtime_build_revision_with_local_repo_head_and_optional_deploy_evidence",
                "canonical_coolify_app": {
                    "project_id": "icmgqml9uw3slzch9m9ok23z",
                    "environment_id": "qxooi9coxat272krzjx221fv",
                    "application_id": "jr1oehwlzl8tcn3h8gh2vvih",
                },
                "deployment_automation_baseline": {
                    "primary_trigger_mode": "source_automation",
                    "fallback_trigger_modes": [
                        "webhook_manual_fallback",
                        "ui_manual_fallback",
                    ],
                },
            },
            "attention": {
                "attention_policy_owner": "durable_attention_inbox_policy",
                "coordination_mode": "durable_inbox",
                "deployment_readiness": {
                    "selected_coordination_mode": "durable_inbox",
                        "contract_store_state": "repository_backed_contract_store_active",
                        "store_available": True,
                    },
                },
                "runtime_topology.attention_switch": {
                    "policy_owner": "runtime_topology_finalization",
                    "selected_mode": "durable_inbox",
                    "production_default_change_ready": True,
                },
                "proactive": {
                    "policy_owner": "proactive_runtime_policy",
                    "enabled": True,
                    "production_baseline_ready": True,
                    "production_baseline_state": "external_scheduler_target_owner",
                    "planned_action_observer": dict(PLANNED_ACTION_OBSERVER_POSTURE),
                },
                "scheduler.external_owner_policy": {
                    "policy_owner": "external_scheduler_cadence_policy",
                "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                "maintenance_run_evidence": {
                    "evidence_state": "missing_external_run_evidence",
                },
                "proactive_run_evidence": {
                    "evidence_state": "missing_external_run_evidence",
                },
                "duplicate_protection_posture": {
                    "state": "single_owner_boundary_clear",
                },
                "cutover_proof_ready": False,
                "cutover_proof_state": "external_scheduler_target_only",
            },
            "reflection.supervision": {
                "policy_owner": "deferred_reflection_supervision_policy",
            },
            "connectors.execution_baseline": {
                "execution_owner": "connector_execution_registry",
            },
            "connectors.organizer_tool_stack": {
                "policy_owner": "production_organizer_tool_stack",
                "stack_name": "clickup_calendar_drive_first_stack",
                "approved_connector_kinds": ["task_system", "calendar", "cloud_drive"],
                "approved_operations": ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS,
                "read_only_operations": ORGANIZER_TOOL_STACK_READ_ONLY_OPERATIONS,
                "confirmation_required_operations": ORGANIZER_TOOL_STACK_CONFIRMATION_REQUIRED_OPERATIONS,
                "user_opt_in_required_operations": ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS,
                "ready_operations": [
                    "task_system.clickup_create_task",
                    "task_system.clickup_list_tasks",
                    "task_system.clickup_update_task",
                ],
                "credential_gap_operations": [
                    "calendar.google_calendar_read_availability",
                    "cloud_drive.google_drive_list_files",
                ],
                "readiness_state": "provider_credentials_missing",
                "daily_use_workflows": _organizer_daily_use_workflows(),
                "daily_use_ready_workflow_count": 1,
                "daily_use_total_workflow_count": 3,
                "daily_use_ready_workflows": ORGANIZER_DAILY_USE_READY_WORKFLOWS,
                "daily_use_blocked_workflows": ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS,
                "daily_use_state": "daily_use_workflows_blocked_by_provider_activation",
                "daily_use_hint": "finish_provider_activation_before_treating_organizer_stack_as_daily_use_ready",
                "activation_snapshot": _organizer_tool_activation_snapshot(),
            },
            "connectors.web_knowledge_tools": {
                "policy_owner": "web_knowledge_tooling_policy",
                "tool_boundary": "action_owned_external_capability",
                "skill_execution_boundary": "metadata_only_capability_hints",
                "provider_execution_posture": "first_bounded_provider_slices_selected",
                "fallback_posture": "respond_without_external_tool_execution",
                "knowledge_search": {
                    "capability_kind": "knowledge_search",
                    "selected_provider_hint": "duckduckgo_html",
                    "authorized_operations": ["search_web", "suggest_search"],
                    "execution_mode": "provider_backed_without_credentials",
                    "state": "provider_backed_ready",
                    "hint": "duckduckgo_html_search_live",
                },
                "web_browser": {
                    "capability_kind": "web_browser",
                    "selected_provider_hint": "generic_http",
                    "authorized_operations": ["read_page", "suggest_page_review"],
                    "execution_mode": "provider_backed_without_credentials",
                    "state": "provider_backed_ready",
                    "hint": "generic_http_read_page_live",
                },
                "website_reading_workflow": {
                    "policy_owner": "website_reading_workflow_policy",
                    "workflow_state": "ready_for_direct_and_search_first_review",
                    "direct_url_review_available": True,
                    "search_then_page_review_available": True,
                    "allowed_entry_modes": [
                        "direct_url_review",
                        "search_then_page_review",
                    ],
                    "selected_provider_path": {
                        "search_provider_hint": "duckduckgo_html",
                        "page_read_provider_hint": "generic_http",
                    },
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
                    "blockers": [],
                    "next_actions": [],
                },
            },
            "conversation_channels.telegram": {
                "policy_owner": "telegram_conversation_reliability_telemetry",
                "round_trip_ready": True,
                "round_trip_state": "provider_backed_ready",
                "bot_token_configured": True,
                "delivery_adaptation_policy_owner": "telegram_delivery_channel_adaptation",
                "delivery_segmentation_state": "bounded_transport_segmentation",
                "delivery_formatting_state": "supported_markdown_to_html_with_plain_text_fallback",
            },
        },
    }
    health_snapshot = {
        "status": "ok",
        "observability": {
            "policy_owner": "incident_evidence_export_policy",
            "bundle_helper_available": True,
        },
        "learned_state": {
            "policy_owner": "learned_state_inspection_policy",
            "internal_inspection_path": "/internal/state/inspect",
            "inspection_sections": LEARNED_STATE_INSPECTION_SECTIONS,
            "growth_summary_sections": LEARNED_STATE_GROWTH_SUMMARY_SECTIONS,
            "role_skill_metadata_sections": LEARNED_STATE_ROLE_SKILL_METADATA_SECTIONS,
            "planning_continuity_sections": LEARNED_STATE_PLANNING_CONTINUITY_SECTIONS,
            "reflection_growth_signal_kinds": LEARNED_STATE_REFLECTION_GROWTH_SIGNAL_KINDS,
            "tool_grounded_learning": TOOL_GROUNDED_LEARNING_CONTRACT,
        },
        "capability_catalog": _capability_catalog_snapshot(),
            "v1_readiness": {
                "policy_owner": "v1_release_readiness_policy",
                "product_stage": "v1_no_ui_life_assistant",
                "conversation_gate_state": "conversation_surface_ready",
                "learned_state_gate_state": "inspection_surface_ready",
                "website_reading_workflow_state": "ready_for_direct_and_search_first_review",
                "tool_grounded_learning_state": "tool_grounded_learning_surface_ready",
                "time_aware_planned_work_policy_owner": "internal_time_aware_planned_work_policy",
                "time_aware_planned_work_delivery_path": "attention_to_planning_to_expression_to_action",
                "time_aware_planned_work_recurrence_owner": "scheduler_reevaluation_with_foreground_handoff",
                "time_aware_planned_work_gate_state": "foreground_due_delivery_and_recurring_reevaluation_ready",
                "deploy_parity_state": "deploy_parity_surface_ready",
                "organizer_daily_use_state": "daily_use_workflows_blocked_by_provider_activation",
                "organizer_daily_use_classification": "extension_readiness_non_blocking_for_core_v1",
                "organizer_daily_use_ready_workflow_count": 1,
                "organizer_daily_use_total_workflow_count": 3,
                "organizer_daily_use_ready_workflows": ORGANIZER_DAILY_USE_READY_WORKFLOWS,
                "organizer_daily_use_blocked_workflows": ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS,
                "final_acceptance_state": "core_v1_bundle_ready",
                "final_acceptance_gate_states": {
                    "conversation_reliability": "conversation_surface_ready",
                    "learned_state_inspection": "inspection_surface_ready",
                    "website_reading": "ready_for_direct_and_search_first_review",
                    "tool_grounded_learning": "tool_grounded_learning_surface_ready",
                    "time_aware_planned_work": "foreground_due_delivery_and_recurring_reevaluation_ready",
                    "deploy_parity": "deploy_parity_surface_ready",
                },
                "final_acceptance_surfaces": {
                    "conversation_reliability": "/health.conversation_channels.telegram",
                    "learned_state_inspection": "/health.learned_state",
                    "website_reading": "/health.connectors.web_knowledge_tools.website_reading_workflow",
                    "tool_grounded_learning": "/health.learned_state.tool_grounded_learning",
                    "time_aware_planned_work": "/health.v1_readiness",
                    "deploy_parity": "/health.deployment",
                },
                "extension_gate_states": {
                    "organizer_daily_use": "daily_use_workflows_blocked_by_provider_activation",
                },
                "extension_gate_surfaces": {
                    "organizer_daily_use": "/health.connectors.organizer_tool_stack",
                },
                "required_behavior_scenarios": V1_REQUIRED_BEHAVIOR_SCENARIOS,
                "approved_tool_slices": V1_APPROVED_TOOL_SLICES,
            },
        "connectors": {
            "organizer_tool_stack": {
                "policy_owner": "production_organizer_tool_stack",
                "stack_name": "clickup_calendar_drive_first_stack",
                "approved_connector_kinds": ["task_system", "calendar", "cloud_drive"],
                "approved_operations": ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS,
                "read_only_operations": ORGANIZER_TOOL_STACK_READ_ONLY_OPERATIONS,
                "confirmation_required_operations": ORGANIZER_TOOL_STACK_CONFIRMATION_REQUIRED_OPERATIONS,
                "user_opt_in_required_operations": ORGANIZER_TOOL_STACK_APPROVED_OPERATIONS,
                "ready_operations": [
                    "task_system.clickup_create_task",
                    "task_system.clickup_list_tasks",
                    "task_system.clickup_update_task",
                ],
                "credential_gap_operations": [
                    "calendar.google_calendar_read_availability",
                    "cloud_drive.google_drive_list_files",
                ],
                "readiness_state": "provider_credentials_missing",
                "daily_use_workflows": _organizer_daily_use_workflows(),
                "daily_use_ready_workflow_count": 1,
                "daily_use_total_workflow_count": 3,
                "daily_use_ready_workflows": ORGANIZER_DAILY_USE_READY_WORKFLOWS,
                "daily_use_blocked_workflows": ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS,
                "daily_use_state": "daily_use_workflows_blocked_by_provider_activation",
                "daily_use_hint": "finish_provider_activation_before_treating_organizer_stack_as_daily_use_ready",
                "activation_snapshot": _organizer_tool_activation_snapshot(),
            },
            "web_knowledge_tools": {
                "policy_owner": "web_knowledge_tooling_policy",
                "tool_boundary": "action_owned_external_capability",
                "skill_execution_boundary": "metadata_only_capability_hints",
                "provider_execution_posture": "first_bounded_provider_slices_selected",
                "fallback_posture": "respond_without_external_tool_execution",
                "knowledge_search": {
                    "capability_kind": "knowledge_search",
                    "selected_provider_hint": "duckduckgo_html",
                    "authorized_operations": ["search_web", "suggest_search"],
                    "execution_mode": "provider_backed_without_credentials",
                    "state": "provider_backed_ready",
                    "hint": "duckduckgo_html_search_live",
                },
                "web_browser": {
                    "capability_kind": "web_browser",
                    "selected_provider_hint": "generic_http",
                    "authorized_operations": ["read_page", "suggest_page_review"],
                    "execution_mode": "provider_backed_without_credentials",
                    "state": "provider_backed_ready",
                    "hint": "generic_http_read_page_live",
                },
                "website_reading_workflow": {
                    "policy_owner": "website_reading_workflow_policy",
                    "workflow_state": "ready_for_direct_and_search_first_review",
                    "direct_url_review_available": True,
                    "search_then_page_review_available": True,
                    "allowed_entry_modes": [
                        "direct_url_review",
                        "search_then_page_review",
                    ],
                    "selected_provider_path": {
                        "search_provider_hint": "duckduckgo_html",
                        "page_read_provider_hint": "generic_http",
                    },
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
                    "blockers": [],
                    "next_actions": [],
                },
            },
        },
    }
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (bundle_dir / "incident_evidence.json").write_text(json.dumps(incident_evidence), encoding="utf-8")
    (bundle_dir / "health_snapshot.json").write_text(json.dumps(health_snapshot), encoding="utf-8")
    if include_behavior_report:
        (bundle_dir / "behavior_validation_report.json").write_text(
            json.dumps({"kind": "behavior_validation_artifact"}),
            encoding="utf-8",
        )


def test_trigger_main_writes_success_evidence_file(monkeypatch, tmp_path: Path) -> None:
    evidence_path = tmp_path / "deploy-evidence.json"

    monkeypatch.setattr(
        TRIGGER_MODULE,
        "_parse_args",
        lambda: SimpleNamespace(
            webhook_url="https://coolify.example/webhook",
            webhook_secret="secret",
            repository="owner/repo",
            branch="main",
            before_sha="a" * 40,
            after_sha="b" * 40,
            pusher_name="codex",
            evidence_path=str(evidence_path),
        ),
    )
    monkeypatch.setattr(
        TRIGGER_MODULE,
        "_post_webhook",
        lambda **_: (True, 202, "queued", ""),
    )

    exit_code = TRIGGER_MODULE.main()

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert evidence["kind"] == "coolify_deploy_webhook_evidence"
    assert evidence["webhook_url"] == "https://coolify.example/webhook"
    assert evidence["repository"] == "owner/repo"
    assert evidence["branch"] == "main"
    assert evidence["before_sha"] == "a" * 40
    assert evidence["after_sha"] == "b" * 40
    assert evidence["policy_owner"] == "coolify_repo_deploy_automation"
    assert evidence["trigger_mode"] == "webhook_manual_fallback"
    assert evidence["trigger_class"] == "manual_fallback"
    assert evidence["canonical_coolify_app"] == {
        "project_id": "icmgqml9uw3slzch9m9ok23z",
        "environment_id": "qxooi9coxat272krzjx221fv",
        "application_id": "jr1oehwlzl8tcn3h8gh2vvih",
    }
    assert evidence["response"] == {
        "ok": True,
        "status_code": 202,
        "body": "queued",
        "error": "",
    }
    assert evidence["generated_at"] == evidence["finished_at"]


def test_trigger_main_writes_failure_evidence_file_and_returns_non_zero(monkeypatch, tmp_path: Path) -> None:
    evidence_path = tmp_path / "deploy-evidence.json"

    monkeypatch.setattr(
        TRIGGER_MODULE,
        "_parse_args",
        lambda: SimpleNamespace(
            webhook_url="https://coolify.example/webhook",
            webhook_secret="secret",
            repository="owner/repo",
            branch="main",
            before_sha="a" * 40,
            after_sha="b" * 40,
            pusher_name="codex",
            evidence_path=str(evidence_path),
        ),
    )
    monkeypatch.setattr(
        TRIGGER_MODULE,
        "_post_webhook",
        lambda **_: (False, 500, "failed", "http_error:500"),
    )

    exit_code = TRIGGER_MODULE.main()

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert evidence["kind"] == "coolify_deploy_webhook_evidence"
    assert evidence["policy_owner"] == "coolify_repo_deploy_automation"
    assert evidence["trigger_mode"] == "webhook_manual_fallback"
    assert evidence["trigger_class"] == "manual_fallback"
    assert evidence["canonical_coolify_app"] == {
        "project_id": "icmgqml9uw3slzch9m9ok23z",
        "environment_id": "qxooi9coxat272krzjx221fv",
        "application_id": "jr1oehwlzl8tcn3h8gh2vvih",
    }
    assert evidence["response"] == {
        "ok": False,
        "status_code": 500,
        "body": "failed",
        "error": "http_error:500",
    }


def test_release_smoke_allows_optional_deployment_evidence_to_be_omitted(
    stub_aion_server: _StubAionServer,
) -> None:
    result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["health_status"] == "ok"
    assert summary["startup_schema_compatibility_posture"] == "migration_only"
    assert summary["startup_schema_compatibility_sunset_ready"] is True
    assert summary["startup_schema_compatibility_sunset_reason"] == "migration_only_baseline_active"
    assert summary["debug_admin_policy_owner"] == "dedicated_admin_debug_ingress_policy"
    assert summary["debug_admin_ingress_target_path"] == "/internal/event/debug"
    assert summary["debug_admin_posture_state"] == "debug_disabled_admin_route_primary_by_default"
    assert summary["debug_shared_ingress_sunset_ready"] is True
    assert summary["debug_shared_ingress_sunset_reason"] == "shared_debug_route_disabled_with_debug_payload_off"
    assert summary["debug_shared_ingress_retirement_ready"] is True
    assert summary["debug_shared_ingress_retirement_blockers"] == []
    assert summary["compatibility_sunset_ready"] is True
    assert summary["compatibility_sunset_blockers"] == []
    assert summary["runtime_topology_owner"] == "runtime_topology_finalization"
    assert summary["topology_release_window"] == "after_group_50_evidence_green"
    assert summary["attention_coordination_mode"] == "durable_inbox"
    assert summary["attention_contract_store_mode"] == "repository_backed"
    assert summary["attention_contract_store_state"] == "repository_backed_contract_store_active"
    assert summary["attention_store_available"] is True
    assert summary["runtime_topology_attention_selected_mode"] == "durable_inbox"
    assert summary["runtime_topology_attention_ready"] is True
    assert summary["proactive_policy_owner"] == "proactive_runtime_policy"
    assert summary["proactive_enabled"] is True
    assert summary["proactive_production_baseline_ready"] is True
    assert summary["proactive_production_baseline_state"] == "external_scheduler_target_owner"
    assert summary["proactive_observer_policy_owner"] == "planned_action_observer_policy"
    assert summary["proactive_observer_state"] == "empty_noop"
    assert summary["proactive_observer_empty_result_behavior"] == "no_foreground_event"
    assert summary["proactive_observer_due_planned_work_count"] == 0
    assert summary["deployment_hosting_baseline"] == "coolify_medium_term_standard"
    assert summary["deployment_automation_policy_owner"] == "coolify_repo_deploy_automation"
    assert summary["deployment_primary_trigger_mode"] == "source_automation"
    assert summary["deployment_runtime_trigger_mode"] == "source_automation"
    assert summary["deployment_runtime_trigger_class"] == "primary_automation"
    assert summary["deployment_runtime_build_revision"] == LOCAL_REPO_HEAD_SHA
    assert summary["deployment_runtime_build_revision_state"] == "runtime_build_revision_declared"
    assert summary["deployment_runtime_provenance_state"] == "primary_runtime_provenance_declared"
    assert summary["web_shell_build_revision"] == LOCAL_REPO_HEAD_SHA
    assert summary["deployment_local_repo_head_sha"] == LOCAL_REPO_HEAD_SHA
    assert summary["deployment_fallback_trigger_modes"] == [
        "webhook_manual_fallback",
        "ui_manual_fallback",
    ]
    assert summary["deployment_canonical_application_id"] == "jr1oehwlzl8tcn3h8gh2vvih"
    assert summary["deployment_manual_fallback_exception_rate_percent"] == 5.0
    assert summary["scheduler_external_policy_owner"] == "external_scheduler_cadence_policy"
    assert summary["scheduler_external_maintenance_entrypoint"] == "scripts/run_maintenance_tick_once.py"
    assert summary["scheduler_external_proactive_entrypoint"] == "scripts/run_proactive_tick_once.py"
    assert summary["scheduler_external_baseline_ready"] is False
    assert summary["scheduler_external_baseline_state"] == "external_scheduler_target_without_cutover_proof"
    assert summary["retrieval_lifecycle_policy_owner"] == "retrieval_lifecycle_policy"
    assert summary["retrieval_lifecycle_relation_source_policy_owner"] == "relation_source_retrieval_policy"
    assert summary["retrieval_lifecycle_relation_source_posture"] == "optional_after_foreground_baseline"
    assert summary["retrieval_lifecycle_relation_source_state"] == "optional_family_not_enabled"
    assert summary["retrieval_lifecycle_relation_source_enabled"] is False
    assert summary["retrieval_semantic_embedding_provider_requested"] == "openai"
    assert summary["retrieval_semantic_embedding_provider_effective"] == "openai"
    assert summary["retrieval_semantic_embedding_model_requested"] == "text-embedding-3-small"
    assert summary["retrieval_semantic_embedding_model_effective"] == "text-embedding-3-small"
    assert summary["retrieval_semantic_embedding_execution_class"] == "provider_owned_openai_api"
    assert summary["retrieval_semantic_embedding_production_baseline_state"] == "aligned_openai_provider_owned"
    assert summary["retrieval_lifecycle_provider_drift_state"] == "aligned_target_provider"
    assert summary["retrieval_lifecycle_alignment_state"] == "aligned_with_defined_lifecycle_baseline"
    assert summary["retrieval_lifecycle_pending_gaps"] == []
    assert summary["reflection_external_driver_policy_owner"] == "deferred_reflection_external_worker"
    assert summary["reflection_external_driver_entrypoint_path"] == "scripts/run_reflection_queue_once.py"
    assert summary["reflection_external_driver_baseline_ready"] is False
    assert summary["reflection_supervision_policy_owner"] == "deferred_reflection_supervision_policy"
    assert summary["reflection_supervision_queue_health_state"] == "active_backlog_under_supervision"
    assert summary["reflection_supervision_ready"] is True
    assert summary["reflection_supervision_state"] == "deferred_supervision_active_backlog"
    assert summary["reflection_supervision_blocking_signals"] == []
    assert summary["reflection_supervision_recovery_actions"] == []
    assert summary["telegram_conversation_policy_owner"] == "telegram_conversation_reliability_telemetry"
    assert summary["telegram_conversation_round_trip_state"] == "provider_backed_ready"
    assert summary["telegram_conversation_bot_token_configured"] is True
    assert summary["telegram_conversation_delivery_adaptation_policy_owner"] == "telegram_delivery_channel_adaptation"
    assert summary["telegram_conversation_delivery_segmentation_state"] == "bounded_transport_segmentation"
    assert summary["telegram_conversation_delivery_formatting_state"] == (
        "supported_markdown_to_html_with_plain_text_fallback"
    )
    assert summary["capability_catalog_policy_owner"] == "backend_capability_catalog_policy"
    assert summary["capability_catalog_approved_tool_families"] == CAPABILITY_CATALOG_APPROVED_TOOL_FAMILIES
    assert summary["capability_catalog_skill_execution_boundary"] == "metadata_only_capability_hints"
    assert summary["capability_catalog_catalog_count"] == 5
    assert summary["capability_catalog_organizer_stack_state"] == "provider_credentials_missing"
    assert summary["capability_catalog_organizer_activation_state"] == "provider_activation_incomplete"
    assert summary["capability_catalog_execution_baseline_owner"] == "connector_execution_registry"
    assert summary["capability_catalog_tool_grounded_learning_policy_owner"] == "tool_grounded_learning_policy"
    assert summary["deployment_evidence_checked"] is False
    assert summary["deployment_evidence_path"] == ""
    assert summary["deployment_evidence_status_code"] is None


def test_release_smoke_fails_when_proactive_observer_posture_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload["proactive"])
    broken = dict(original)
    broken.pop("planned_action_observer", None)
    _StubAionHandler.health_payload["proactive"] = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload["proactive"] = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "proactive planned_action_observer posture is missing" in combined_output


def test_release_smoke_fails_when_relation_source_policy_evidence_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload["memory_retrieval"])
    broken = dict(original)
    broken.pop("retrieval_lifecycle_relation_source_policy_owner", None)
    _StubAionHandler.health_payload["memory_retrieval"] = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload["memory_retrieval"] = original

    assert result.returncode != 0
    assert "retrieval_lifecycle_relation_source_policy_owner" in result.stderr


def test_release_smoke_fails_when_retrieval_provider_alignment_drifts(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload["memory_retrieval"])
    broken = dict(original)
    broken["semantic_embedding_provider_effective"] = "deterministic"
    broken["semantic_embedding_execution_class"] = "deterministic_baseline"
    broken["semantic_embedding_production_baseline_state"] = "deterministic_compatibility_baseline"
    broken["retrieval_lifecycle_provider_drift_state"] = "compatibility_fallback_active"
    broken["retrieval_lifecycle_alignment_state"] = "lifecycle_gaps_present"
    broken["retrieval_lifecycle_pending_gaps"] = ["provider_baseline_not_aligned"]
    _StubAionHandler.health_payload["memory_retrieval"] = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload["memory_retrieval"] = original

    assert result.returncode != 0
    assert "semantic_embedding_provider_effective" in result.stderr


def test_release_smoke_fails_when_telegram_conversation_health_surface_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload)
    broken = dict(original)
    broken.pop("conversation_channels", None)
    _StubAionHandler.health_payload = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "conversation_channels" in combined_output


def test_release_smoke_fails_when_telegram_delivery_adaptation_posture_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload)
    broken = dict(original)
    broken_conversation_channels = dict(original["conversation_channels"])
    broken_telegram = dict(broken_conversation_channels["telegram"])
    broken_telegram.pop("delivery_adaptation_policy_owner", None)
    broken_conversation_channels["telegram"] = broken_telegram
    broken["conversation_channels"] = broken_conversation_channels
    _StubAionHandler.health_payload = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "delivery_adaptation_policy_owner" in combined_output


def test_release_smoke_fails_when_attention_health_surface_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload)
    broken = dict(original)
    broken.pop("attention", None)
    _StubAionHandler.health_payload = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "response is missing attention" in combined_output


def test_release_smoke_fails_when_proactive_health_surface_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload)
    broken = dict(original)
    broken.pop("proactive", None)
    _StubAionHandler.health_payload = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "response is missing proactive" in combined_output


def test_release_smoke_fails_when_organizer_tool_stack_health_surface_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload)
    broken = dict(original)
    broken["connectors"] = {}
    _StubAionHandler.health_payload = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "organizer_tool_stack posture is missing" in combined_output


def test_release_smoke_verifies_fresh_successful_deployment_evidence(
    stub_aion_server: _StubAionServer,
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "deploy-evidence.json"
    _write_evidence(evidence_path)

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-DeploymentEvidencePath",
        str(evidence_path),
        "-DeploymentEvidenceMaxAgeMinutes",
        "60",
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["deployment_evidence_checked"] is True
    assert summary["deployment_evidence_path"] == str(evidence_path)
    assert summary["deployment_evidence_status_code"] == 200
    assert isinstance(summary["deployment_evidence_age_minutes"], float)
    assert summary["deployment_evidence_age_minutes"] >= 0.0
    assert summary["deployment_evidence_policy_owner"] == "coolify_repo_deploy_automation"
    assert summary["deployment_evidence_trigger_mode"] == "webhook_manual_fallback"
    assert summary["deployment_evidence_trigger_class"] == "manual_fallback"
    assert summary["deployment_evidence_canonical_application_id"] == "jr1oehwlzl8tcn3h8gh2vvih"
    assert summary["deployment_evidence_after_sha"] == LOCAL_REPO_HEAD_SHA


def test_release_smoke_validates_exported_incident_evidence_when_debug_mode_is_requested(
    stub_aion_server: _StubAionServer,
) -> None:
    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-IncludeDebug",
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["debug_included"] is True
    assert summary["incident_evidence_policy_owner"] == "incident_evidence_export_policy"
    assert summary["incident_evidence_schema_version"] == "1.0.0"
    assert summary["incident_evidence_stage_count"] == 4
    assert summary["incident_evidence_duration_ms"] == 12
    assert summary["incident_evidence_policy_surface_complete"] is True
    assert summary["incident_evidence_debug_posture_state"] == "dedicated_admin_only"
    assert summary["incident_evidence_debug_exception_state"] == "shared_debug_break_glass_only"
    assert summary["incident_evidence_telegram_conversation_policy_owner"] == (
        "telegram_conversation_reliability_telemetry"
    )
    assert summary["incident_evidence_telegram_conversation_round_trip_state"] == "provider_backed_ready"
    assert summary["incident_evidence_telegram_conversation_delivery_adaptation_policy_owner"] == (
        "telegram_delivery_channel_adaptation"
    )
    assert summary["incident_evidence_telegram_conversation_delivery_segmentation_state"] == (
        "bounded_transport_segmentation"
    )
    assert summary["incident_evidence_telegram_conversation_delivery_formatting_state"] == (
        "supported_markdown_to_html_with_plain_text_fallback"
    )
    assert summary["incident_evidence_attention_policy_owner"] == "durable_attention_inbox_policy"
    assert summary["incident_evidence_attention_coordination_mode"] == "durable_inbox"
    assert summary["incident_evidence_attention_contract_store_state"] == (
        "repository_backed_contract_store_active"
    )
    assert summary["incident_evidence_attention_runtime_topology_policy_owner"] == "runtime_topology_finalization"
    assert summary["incident_evidence_attention_runtime_topology_selected_mode"] == "durable_inbox"
    assert summary["incident_evidence_attention_runtime_topology_ready"] is True
    assert summary["incident_evidence_proactive_policy_owner"] == "proactive_runtime_policy"
    assert summary["incident_evidence_proactive_enabled"] is True
    assert summary["incident_evidence_proactive_production_baseline_ready"] is True
    assert summary["incident_evidence_proactive_production_baseline_state"] == (
        "external_scheduler_target_owner"
    )
    assert summary["incident_evidence_proactive_observer_policy_owner"] == "planned_action_observer_policy"
    assert summary["incident_evidence_proactive_observer_state"] == "empty_noop"
    assert summary["incident_evidence_deployment_automation_policy_owner"] == (
        "coolify_repo_deploy_automation"
    )
    assert summary["incident_evidence_deployment_primary_trigger_mode"] == "source_automation"
    assert summary["deployment_runtime_trigger_mode"] == "source_automation"
    assert summary["deployment_runtime_trigger_class"] == "primary_automation"
    assert summary["deployment_runtime_build_revision"] == LOCAL_REPO_HEAD_SHA
    assert summary["deployment_runtime_build_revision_state"] == "runtime_build_revision_declared"
    assert summary["deployment_runtime_provenance_state"] == "primary_runtime_provenance_declared"
    assert summary["incident_evidence_learned_state_policy_owner"] == "learned_state_inspection_policy"
    assert summary["incident_evidence_learned_state_internal_inspection_path"] == "/internal/state/inspect"
    assert summary["incident_evidence_learned_state_inspection_sections"] == LEARNED_STATE_INSPECTION_SECTIONS
    assert summary["incident_evidence_learned_state_growth_summary_sections"] == (
        LEARNED_STATE_GROWTH_SUMMARY_SECTIONS
    )
    assert summary["organizer_tool_stack_policy_owner"] == "production_organizer_tool_stack"
    assert summary["organizer_tool_stack_readiness_state"] == "provider_credentials_missing"
    assert summary["organizer_tool_stack_ready_operations"] == [
        "task_system.clickup_create_task",
        "task_system.clickup_list_tasks",
        "task_system.clickup_update_task",
    ]
    assert summary["organizer_tool_stack_credential_gap_operations"] == [
        "calendar.google_calendar_read_availability",
        "cloud_drive.google_drive_list_files",
    ]
    assert summary["organizer_tool_stack_daily_use_state"] == "daily_use_workflows_blocked_by_provider_activation"
    assert summary["organizer_tool_stack_daily_use_ready_workflow_count"] == 1
    assert summary["organizer_tool_stack_daily_use_ready_workflows"] == ORGANIZER_DAILY_USE_READY_WORKFLOWS
    assert summary["organizer_tool_stack_daily_use_blocked_workflows"] == ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS
    assert summary["organizer_tool_activation_state"] == "provider_activation_incomplete"
    assert summary["organizer_tool_activation_next_actions"] == ORGANIZER_TOOL_ACTIVATION_NEXT_ACTIONS
    assert (
        summary["organizer_tool_activation_missing_settings_by_provider"]
        == ORGANIZER_TOOL_ACTIVATION_MISSING_SETTINGS_BY_PROVIDER
    )
    assert summary["v1_organizer_daily_use_state"] == "daily_use_workflows_blocked_by_provider_activation"
    assert summary["v1_organizer_daily_use_ready_workflow_count"] == 1
    assert summary["v1_organizer_daily_use_ready_workflows"] == ORGANIZER_DAILY_USE_READY_WORKFLOWS
    assert summary["v1_organizer_daily_use_blocked_workflows"] == ORGANIZER_DAILY_USE_BLOCKED_WORKFLOWS
    assert summary["incident_evidence_organizer_tool_stack_policy_owner"] == "production_organizer_tool_stack"
    assert summary["incident_evidence_organizer_tool_stack_readiness_state"] == "provider_credentials_missing"
    assert summary["incident_evidence_organizer_tool_stack_daily_use_state"] == (
        "daily_use_workflows_blocked_by_provider_activation"
    )
    assert summary["incident_evidence_organizer_tool_stack_daily_use_ready_workflow_count"] == 1
    assert summary["incident_evidence_organizer_tool_activation_state"] == "provider_activation_incomplete"
    assert summary["incident_evidence_organizer_tool_activation_next_actions"] == (
        ORGANIZER_TOOL_ACTIVATION_NEXT_ACTIONS
    )
    assert (
        summary["incident_evidence_organizer_tool_activation_missing_settings_by_provider"]
        == ORGANIZER_TOOL_ACTIVATION_MISSING_SETTINGS_BY_PROVIDER
    )
    assert summary["incident_evidence_v1_organizer_daily_use_state"] == (
        "daily_use_workflows_blocked_by_provider_activation"
    )
    assert summary["incident_evidence_retrieval_policy_owner"] == "retrieval_lifecycle_policy"
    assert summary["incident_evidence_retrieval_provider_requested"] == "openai"
    assert summary["incident_evidence_retrieval_provider_effective"] == "openai"
    assert summary["incident_evidence_retrieval_execution_class"] == "provider_owned_openai_api"
    assert summary["incident_evidence_retrieval_baseline_state"] == "aligned_openai_provider_owned"
    assert summary["incident_evidence_retrieval_provider_drift_state"] == "aligned_target_provider"
    assert summary["incident_evidence_retrieval_alignment_state"] == "aligned_with_defined_lifecycle_baseline"
    assert summary["scheduler_external_cutover_proof_owner"] == "external_scheduler_cutover_proof_policy"
    assert summary["scheduler_external_cutover_proof_ready"] is False
    assert summary["scheduler_external_maintenance_evidence_state"] == "missing_external_run_evidence"
    assert summary["scheduler_external_proactive_evidence_state"] == "missing_external_run_evidence"
    assert summary["scheduler_external_duplicate_protection_state"] == "single_owner_boundary_clear"


def test_release_smoke_verifies_incident_evidence_bundle_when_bundle_path_is_provided(
    stub_aion_server: _StubAionServer,
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "incident-bundle"
    _write_incident_bundle(bundle_dir, include_behavior_report=True)

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-IncidentEvidenceBundlePath",
        str(bundle_dir),
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["incident_bundle_checked"] is True
    assert summary["incident_bundle_path"] == str(bundle_dir)
    assert summary["incident_bundle_manifest_schema_version"] == "1.0.0"
    assert summary["incident_bundle_capture_mode"] == "incident"
    assert summary["incident_bundle_trace_id"] == "trace-test"
    assert summary["incident_bundle_event_id"] == "evt-test"
    assert summary["incident_bundle_behavior_report_attached"] is True
    assert summary["incident_bundle_policy_surface_complete"] is True
    assert summary["incident_bundle_health_status"] == "ok"
    assert summary["incident_bundle_debug_posture_state"] == "dedicated_admin_only"
    assert summary["incident_bundle_debug_exception_state"] == "shared_debug_break_glass_only"
    assert summary["incident_bundle_telegram_round_trip_state"] == "provider_backed_ready"
    assert summary["incident_bundle_telegram_delivery_adaptation_policy_owner"] == (
        "telegram_delivery_channel_adaptation"
    )
    assert summary["incident_bundle_telegram_delivery_segmentation_state"] == (
        "bounded_transport_segmentation"
    )
    assert summary["incident_bundle_telegram_delivery_formatting_state"] == (
        "supported_markdown_to_html_with_plain_text_fallback"
    )
    assert summary["incident_bundle_attention_coordination_mode"] == "durable_inbox"
    assert summary["incident_bundle_attention_contract_store_state"] == "repository_backed_contract_store_active"
    assert summary["incident_bundle_attention_runtime_topology_selected_mode"] == "durable_inbox"
    assert summary["incident_bundle_proactive_policy_owner"] == "proactive_runtime_policy"
    assert summary["incident_bundle_proactive_enabled"] is True
    assert summary["incident_bundle_proactive_production_baseline_state"] == (
        "external_scheduler_target_owner"
    )
    assert summary["incident_bundle_proactive_observer_policy_owner"] == "planned_action_observer_policy"
    assert summary["incident_bundle_proactive_observer_state"] == "empty_noop"
    assert summary["incident_bundle_deployment_automation_policy_owner"] == (
        "coolify_repo_deploy_automation"
    )
    assert summary["incident_bundle_deployment_primary_trigger_mode"] == "source_automation"
    assert summary["incident_bundle_deployment_runtime_trigger_mode"] == "source_automation"
    assert summary["incident_bundle_deployment_runtime_trigger_class"] == "primary_automation"
    assert summary["incident_bundle_deployment_runtime_build_revision"] == LOCAL_REPO_HEAD_SHA
    assert summary["incident_bundle_deployment_runtime_build_revision_state"] == (
        "runtime_build_revision_declared"
    )
    assert summary["incident_bundle_deployment_runtime_provenance_state"] == (
        "primary_runtime_provenance_declared"
    )
    assert summary["incident_bundle_organizer_tool_stack_policy_owner"] == "production_organizer_tool_stack"
    assert summary["incident_bundle_organizer_tool_stack_readiness_state"] == "provider_credentials_missing"
    assert summary["incident_bundle_organizer_tool_stack_ready_operations"] == [
        "task_system.clickup_create_task",
        "task_system.clickup_list_tasks",
        "task_system.clickup_update_task",
    ]
    assert summary["incident_bundle_organizer_tool_stack_credential_gap_operations"] == [
        "calendar.google_calendar_read_availability",
        "cloud_drive.google_drive_list_files",
    ]
    assert summary["incident_bundle_organizer_tool_stack_daily_use_state"] == (
        "daily_use_workflows_blocked_by_provider_activation"
    )
    assert summary["incident_bundle_organizer_tool_stack_daily_use_ready_workflow_count"] == 1
    assert summary["incident_bundle_organizer_tool_activation_state"] == "provider_activation_incomplete"
    assert summary["incident_bundle_organizer_tool_activation_next_actions"] == (
        ORGANIZER_TOOL_ACTIVATION_NEXT_ACTIONS
    )
    assert (
        summary["incident_bundle_organizer_tool_activation_missing_settings_by_provider"]
        == ORGANIZER_TOOL_ACTIVATION_MISSING_SETTINGS_BY_PROVIDER
    )
    assert summary["incident_bundle_learned_state_policy_owner"] == "learned_state_inspection_policy"
    assert summary["incident_bundle_learned_state_internal_inspection_path"] == "/internal/state/inspect"
    assert summary["incident_bundle_learned_state_inspection_sections"] == LEARNED_STATE_INSPECTION_SECTIONS
    assert summary["incident_bundle_learned_state_growth_summary_sections"] == (
        LEARNED_STATE_GROWTH_SUMMARY_SECTIONS
    )
    assert summary["incident_bundle_capability_catalog_policy_owner"] == "backend_capability_catalog_policy"
    assert summary["incident_bundle_capability_catalog_approved_tool_families"] == (
        CAPABILITY_CATALOG_APPROVED_TOOL_FAMILIES
    )
    assert summary["incident_bundle_capability_catalog_skill_execution_boundary"] == (
        "metadata_only_capability_hints"
    )
    assert summary["incident_bundle_capability_catalog_catalog_count"] == 5
    assert summary["incident_bundle_capability_catalog_organizer_stack_state"] == (
        "provider_credentials_missing"
    )
    assert summary["incident_bundle_capability_catalog_organizer_activation_state"] == (
        "provider_activation_incomplete"
    )
    assert summary["incident_bundle_capability_catalog_execution_baseline_owner"] == (
        "connector_execution_registry"
    )
    assert summary["incident_bundle_capability_catalog_tool_grounded_learning_policy_owner"] == (
        "tool_grounded_learning_policy"
    )
    assert summary["incident_bundle_retrieval_policy_owner"] == "retrieval_lifecycle_policy"
    assert summary["incident_bundle_retrieval_provider_requested"] == "openai"
    assert summary["incident_bundle_retrieval_provider_effective"] == "openai"
    assert summary["incident_bundle_retrieval_execution_class"] == "provider_owned_openai_api"
    assert summary["incident_bundle_retrieval_baseline_state"] == "aligned_openai_provider_owned"
    assert summary["incident_bundle_retrieval_provider_drift_state"] == "aligned_target_provider"
    assert summary["incident_bundle_retrieval_alignment_state"] == "aligned_with_defined_lifecycle_baseline"


def test_release_smoke_fails_when_incident_evidence_bundle_is_partial(
    stub_aion_server: _StubAionServer,
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "incident-bundle"
    _write_incident_bundle(bundle_dir)
    (bundle_dir / "health_snapshot.json").unlink()

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-IncidentEvidenceBundlePath",
        str(bundle_dir),
        cwd=ROOT,
    )

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Incident evidence bundle verification failed" in combined_output
    assert "required file missing" in combined_output


def test_release_smoke_fails_when_incident_evidence_bundle_organizer_tool_stack_is_partial(
    stub_aion_server: _StubAionServer,
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "incident-bundle"
    _write_incident_bundle(bundle_dir)
    health_snapshot_path = bundle_dir / "health_snapshot.json"
    health_snapshot = json.loads(health_snapshot_path.read_text(encoding="utf-8"))
    health_snapshot["connectors"]["organizer_tool_stack"].pop("approved_operations", None)
    health_snapshot_path.write_text(json.dumps(health_snapshot), encoding="utf-8")

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-IncidentEvidenceBundlePath",
        str(bundle_dir),
        cwd=ROOT,
    )

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Incident evidence bundle verification failed" in combined_output
    assert "organizer_tool_stack is missing approved_operations" in combined_output


def test_release_smoke_fails_when_incident_evidence_bundle_capability_catalog_is_partial(
    stub_aion_server: _StubAionServer,
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "incident-bundle"
    _write_incident_bundle(bundle_dir)
    health_snapshot_path = bundle_dir / "health_snapshot.json"
    health_snapshot = json.loads(health_snapshot_path.read_text(encoding="utf-8"))
    health_snapshot["capability_catalog"].pop("tool_and_connector_posture", None)
    health_snapshot_path.write_text(json.dumps(health_snapshot), encoding="utf-8")

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-IncidentEvidenceBundlePath",
        str(bundle_dir),
        cwd=ROOT,
    )

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Incident evidence bundle verification failed" in combined_output
    assert "capability_catalog tool_and_connector_posture is missing" in combined_output


def test_release_smoke_fails_when_incident_evidence_debug_posture_is_not_dedicated_admin_only(
    stub_aion_server: _StubAionServer,
) -> None:
    incident_evidence = _StubAionHandler.event_payload["incident_evidence"]
    assert isinstance(incident_evidence, dict)
    policy_posture = dict(incident_evidence["policy_posture"])
    runtime_policy = dict(policy_posture["runtime_policy"])
    runtime_policy["event_debug_shared_ingress_mode"] = "compatibility"
    runtime_policy["event_debug_shared_ingress_posture"] = "shared_route_compatibility"
    runtime_policy["event_debug_query_compat_enabled"] = True
    runtime_policy["event_debug_shared_ingress_retirement_ready"] = False
    runtime_policy["event_debug_shared_ingress_sunset_ready"] = False
    runtime_policy["event_debug_shared_ingress_sunset_reason"] = "shared_debug_route_still_in_compatibility_mode"
    policy_posture["runtime_policy"] = runtime_policy
    _StubAionHandler.event_payload["incident_evidence"] = {
        **incident_evidence,
        "policy_posture": policy_posture,
    }

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-IncludeDebug",
        cwd=ROOT,
    )

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Smoke request failed" in combined_output
    assert "shared debug ingress is not retired to break-glass-only mode" in combined_output


def test_release_smoke_fails_when_incident_evidence_retrieval_alignment_drifts(
    stub_aion_server: _StubAionServer,
) -> None:
    incident_evidence = _StubAionHandler.event_payload["incident_evidence"]
    assert isinstance(incident_evidence, dict)
    policy_posture = dict(incident_evidence["policy_posture"])
    retrieval_policy = dict(policy_posture["memory_retrieval"])
    retrieval_policy["semantic_embedding_provider_effective"] = "deterministic"
    retrieval_policy["semantic_embedding_execution_class"] = "deterministic_baseline"
    retrieval_policy["semantic_embedding_production_baseline_state"] = "deterministic_compatibility_baseline"
    retrieval_policy["retrieval_lifecycle_provider_drift_state"] = "compatibility_fallback_active"
    retrieval_policy["retrieval_lifecycle_alignment_state"] = "lifecycle_gaps_present"
    retrieval_policy["retrieval_lifecycle_pending_gaps"] = ["provider_baseline_not_aligned"]
    policy_posture["memory_retrieval"] = retrieval_policy
    _StubAionHandler.event_payload["incident_evidence"] = {
        **incident_evidence,
        "policy_posture": policy_posture,
    }

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-IncludeDebug",
        cwd=ROOT,
    )

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Smoke request failed" in combined_output
    assert "semantic_embedding_provider_effective" in combined_output


def test_release_smoke_fails_when_learned_state_health_contract_is_partial(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload["learned_state"])
    broken = dict(original)
    broken.pop("inspection_sections", None)
    _StubAionHandler.health_payload["learned_state"] = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload["learned_state"] = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "learned_state is missing inspection_sections" in combined_output


def test_release_smoke_fails_when_incident_evidence_learned_state_contract_is_partial(
    stub_aion_server: _StubAionServer,
) -> None:
    incident_evidence = _StubAionHandler.event_payload["incident_evidence"]
    assert isinstance(incident_evidence, dict)
    policy_posture = dict(incident_evidence["policy_posture"])
    learned_state_policy = dict(policy_posture["learned_state"])
    learned_state_policy.pop("growth_summary_sections", None)
    policy_posture["learned_state"] = learned_state_policy
    _StubAionHandler.event_payload["incident_evidence"] = {
        **incident_evidence,
        "policy_posture": policy_posture,
    }

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-IncludeDebug",
        cwd=ROOT,
    )

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Smoke request failed" in combined_output
    assert "learned_state is missing growth_summary_sections" in combined_output


def test_release_smoke_fails_when_v1_readiness_time_aware_planned_work_contract_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload["v1_readiness"])
    broken = dict(original)
    broken.pop("time_aware_planned_work_gate_state", None)
    _StubAionHandler.health_payload["v1_readiness"] = broken

    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload["v1_readiness"] = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "time_aware_planned_work_gate_state" in combined_output


def test_release_smoke_fails_when_incident_evidence_v1_time_aware_planned_work_contract_drifts(
    stub_aion_server: _StubAionServer,
) -> None:
    incident_evidence = _StubAionHandler.event_payload["incident_evidence"]
    assert isinstance(incident_evidence, dict)
    original_payload = incident_evidence
    policy_posture = dict(incident_evidence["policy_posture"])
    v1_readiness = dict(policy_posture["v1_readiness"])
    v1_readiness["time_aware_planned_work_gate_state"] = "planned_work_surface_invalid"
    policy_posture["v1_readiness"] = v1_readiness
    _StubAionHandler.event_payload["incident_evidence"] = {
        **incident_evidence,
        "policy_posture": policy_posture,
    }

    try:
        result = _run_release_smoke(
            "-BaseUrl",
            stub_aion_server.base_url,
            "-IncludeDebug",
            cwd=ROOT,
        )
    finally:
        _StubAionHandler.event_payload["incident_evidence"] = original_payload

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Smoke request failed" in combined_output
    assert "time_aware_planned_work_gate_state" in combined_output


def test_release_smoke_fails_when_v1_readiness_treats_extension_posture_as_core_bundle_blocker(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload["v1_readiness"])
    broken = dict(original)
    broken["final_acceptance_state"] = "core_v1_bundle_incomplete"
    broken["final_acceptance_gate_states"] = {
        **dict(original["final_acceptance_gate_states"]),
        "organizer_daily_use": "daily_use_workflows_blocked_by_provider_activation",
    }
    _StubAionHandler.health_payload["v1_readiness"] = broken

    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload["v1_readiness"] = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "final_acceptance_gate_states" in combined_output or "final_acceptance_state" in combined_output


def test_release_smoke_fails_when_incident_evidence_v1_readiness_treats_extension_posture_as_core_bundle_blocker(
    stub_aion_server: _StubAionServer,
) -> None:
    incident_evidence = _StubAionHandler.event_payload["incident_evidence"]
    assert isinstance(incident_evidence, dict)
    original_payload = incident_evidence
    policy_posture = dict(incident_evidence["policy_posture"])
    v1_readiness = dict(policy_posture["v1_readiness"])
    v1_readiness["final_acceptance_state"] = "core_v1_bundle_incomplete"
    v1_readiness["final_acceptance_gate_states"] = {
        **dict(v1_readiness["final_acceptance_gate_states"]),
        "organizer_daily_use": "daily_use_workflows_blocked_by_provider_activation",
    }
    policy_posture["v1_readiness"] = v1_readiness
    _StubAionHandler.event_payload["incident_evidence"] = {
        **incident_evidence,
        "policy_posture": policy_posture,
    }

    try:
        result = _run_release_smoke(
            "-BaseUrl",
            stub_aion_server.base_url,
            "-IncludeDebug",
            cwd=ROOT,
        )
    finally:
        _StubAionHandler.event_payload["incident_evidence"] = original_payload

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Smoke request failed" in combined_output
    assert "final_acceptance_gate_states" in combined_output or "final_acceptance_state" in combined_output


def test_release_smoke_fails_when_v1_readiness_deploy_gate_drifts_from_deployment_surface(
    stub_aion_server: _StubAionServer,
) -> None:
    original_health = dict(_StubAionHandler.health_payload)
    broken_health = dict(original_health)
    deployment = dict(broken_health["deployment"])
    deployment["runtime_trigger_mode"] = "ui_manual_fallback"
    deployment["runtime_trigger_class"] = "manual_fallback"
    deployment["runtime_provenance_state"] = "fallback_runtime_provenance_declared"
    broken_health["deployment"] = deployment
    _StubAionHandler.health_payload = broken_health

    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload = original_health

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "deploy_parity_state drifted from deployment" in combined_output


def test_release_smoke_fails_when_learned_state_tool_grounded_contract_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload["learned_state"])
    broken = dict(original)
    broken.pop("tool_grounded_learning", None)
    _StubAionHandler.health_payload["learned_state"] = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload["learned_state"] = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "learned_state is missing tool_grounded_learning" in combined_output


def test_release_smoke_fails_when_capability_catalog_health_contract_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload)
    broken = dict(original)
    broken.pop("capability_catalog", None)
    _StubAionHandler.health_payload = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "capability_catalog posture is missing" in combined_output


def test_release_smoke_fails_when_incident_evidence_organizer_tool_stack_contract_is_partial(
    stub_aion_server: _StubAionServer,
) -> None:
    incident_evidence = _StubAionHandler.event_payload["incident_evidence"]
    assert isinstance(incident_evidence, dict)
    policy_posture = dict(incident_evidence["policy_posture"])
    organizer_tool_stack = dict(policy_posture["connectors.organizer_tool_stack"])
    organizer_tool_stack.pop("approved_operations", None)
    policy_posture["connectors.organizer_tool_stack"] = organizer_tool_stack
    _StubAionHandler.event_payload["incident_evidence"] = {
        **incident_evidence,
        "policy_posture": policy_posture,
    }

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-IncludeDebug",
        cwd=ROOT,
    )

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Smoke request failed" in combined_output
    assert "organizer_tool_stack is missing approved_operations" in combined_output


def test_release_smoke_fails_when_organizer_tool_activation_snapshot_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload)
    broken = dict(original)
    connectors = dict(broken["connectors"])
    organizer_tool_stack = dict(connectors["organizer_tool_stack"])
    organizer_tool_stack.pop("activation_snapshot", None)
    connectors["organizer_tool_stack"] = organizer_tool_stack
    broken["connectors"] = connectors
    _StubAionHandler.health_payload = broken
    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "organizer_tool_stack is missing activation_snapshot" in combined_output


def test_release_smoke_fails_when_deployment_evidence_is_stale(
    stub_aion_server: _StubAionServer,
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "deploy-evidence.json"
    _write_evidence(evidence_path, minutes_ago=90)

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-DeploymentEvidencePath",
        str(evidence_path),
        "-DeploymentEvidenceMaxAgeMinutes",
        "60",
        cwd=ROOT,
    )

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Deployment evidence verification failed" in combined_output
    assert "exceeds 60 min" in combined_output


def test_release_smoke_fails_when_deployment_evidence_response_is_unsuccessful(
    stub_aion_server: _StubAionServer,
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "deploy-evidence.json"
    _write_evidence(evidence_path, ok=False, status_code=500)

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-DeploymentEvidencePath",
        str(evidence_path),
        cwd=ROOT,
    )

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Deployment evidence verification failed" in combined_output
    assert "webhook response is not successful" in combined_output


def test_release_smoke_fails_when_runtime_build_revision_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload["deployment"])
    broken = dict(original)
    broken["runtime_build_revision"] = "unknown"
    broken["runtime_build_revision_state"] = "runtime_build_revision_missing"
    _StubAionHandler.health_payload["deployment"] = broken

    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload["deployment"] = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "deployment runtime_build_revision is still missing" in combined_output


def test_release_smoke_fails_when_runtime_build_revision_does_not_match_local_repo_head(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload["deployment"])
    broken = dict(original)
    broken["runtime_build_revision"] = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    _StubAionHandler.health_payload["deployment"] = broken

    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.health_payload["deployment"] = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "does not match local repo HEAD" in combined_output


def test_release_smoke_can_wait_for_deploy_parity_until_runtime_revision_matches_local_head(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload)
    stale = dict(original)
    stale_deployment = dict(stale["deployment"])
    stale_deployment["runtime_build_revision"] = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    stale["deployment"] = stale_deployment
    _StubAionHandler.health_payload_sequence = [stale, original]
    _StubAionHandler.health_request_count = 0
    _StubAionHandler.sync_web_build_revision_from_health = True
    _StubAionHandler.web_build_revision = stale_deployment["runtime_build_revision"]

    try:
        result = _run_release_smoke(
            "-BaseUrl",
            stub_aion_server.base_url,
            "-WaitForDeployParity",
            "-DeployParityMaxWaitSeconds",
            "5",
            "-DeployParityPollSeconds",
            "1",
            cwd=ROOT,
        )
    finally:
        _StubAionHandler.health_payload_sequence = []
        _StubAionHandler.health_request_count = 0
        _StubAionHandler.sync_web_build_revision_from_health = False
        _StubAionHandler.health_payload = original
        _StubAionHandler.web_build_revision = LOCAL_REPO_HEAD_SHA

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["deployment_runtime_build_revision"] == LOCAL_REPO_HEAD_SHA


def test_release_smoke_wait_for_deploy_parity_times_out_when_runtime_revision_stays_stale(
    stub_aion_server: _StubAionServer,
) -> None:
    original = dict(_StubAionHandler.health_payload)
    stale = dict(original)
    stale_deployment = dict(stale["deployment"])
    stale_deployment["runtime_build_revision"] = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    stale["deployment"] = stale_deployment
    _StubAionHandler.health_payload_sequence = [stale]
    _StubAionHandler.health_request_count = 0
    _StubAionHandler.sync_web_build_revision_from_health = True
    _StubAionHandler.web_build_revision = stale_deployment["runtime_build_revision"]

    try:
        result = _run_release_smoke(
            "-BaseUrl",
            stub_aion_server.base_url,
            "-WaitForDeployParity",
            "-DeployParityMaxWaitSeconds",
            "2",
            "-DeployParityPollSeconds",
            "1",
            cwd=ROOT,
        )
    finally:
        _StubAionHandler.health_payload_sequence = []
        _StubAionHandler.health_request_count = 0
        _StubAionHandler.sync_web_build_revision_from_health = False
        _StubAionHandler.health_payload = original
        _StubAionHandler.web_build_revision = LOCAL_REPO_HEAD_SHA

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "did not match local repo HEAD" in combined_output


def test_release_smoke_retries_transient_health_503_before_succeeding(
    stub_aion_server: _StubAionServer,
) -> None:
    _StubAionHandler.health_status_code_sequence = [503, 200]
    _StubAionHandler.health_request_count = 0

    try:
        result = _run_release_smoke(
            "-BaseUrl",
            stub_aion_server.base_url,
            "-HealthRetryMaxAttempts",
            "2",
            "-HealthRetryDelaySeconds",
            "1",
            cwd=ROOT,
        )
    finally:
        _StubAionHandler.health_status_code_sequence = []
        _StubAionHandler.health_status_code = 200
        _StubAionHandler.health_request_count = 0

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["health_status"] == "ok"


def test_release_smoke_fails_when_transient_health_503_exceeds_retry_budget(
    stub_aion_server: _StubAionServer,
) -> None:
    _StubAionHandler.health_status_code_sequence = [503, 503, 503]
    _StubAionHandler.health_request_count = 0

    try:
        result = _run_release_smoke(
            "-BaseUrl",
            stub_aion_server.base_url,
            "-HealthRetryMaxAttempts",
            "2",
            "-HealthRetryDelaySeconds",
            "1",
            cwd=ROOT,
        )
    finally:
        _StubAionHandler.health_status_code_sequence = []
        _StubAionHandler.health_status_code = 200
        _StubAionHandler.health_request_count = 0

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "Health check failed after 2 attempts" in combined_output


def test_release_smoke_fails_when_web_shell_build_revision_meta_tag_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    original_routes = set(_StubAionHandler.web_routes_missing_revision)
    _StubAionHandler.web_routes_missing_revision = {"/tools"}

    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.web_routes_missing_revision = original_routes

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "web shell build revision is empty on '/tools'" in combined_output


def test_release_smoke_fails_when_web_shell_build_revision_drifts_from_runtime_build_revision(
    stub_aion_server: _StubAionServer,
) -> None:
    original = _StubAionHandler.web_build_revision
    _StubAionHandler.web_build_revision = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"

    try:
        result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)
    finally:
        _StubAionHandler.web_build_revision = original

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "web shell build revision" in combined_output
    assert "deployment runtime_build_revision" in combined_output


def test_release_smoke_fails_when_deployment_evidence_after_sha_does_not_match_runtime_build_revision(
    stub_aion_server: _StubAionServer,
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "deploy-evidence.json"
    _write_evidence(
        evidence_path,
        after_sha="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
    )

    result = _run_release_smoke(
        "-BaseUrl",
        stub_aion_server.base_url,
        "-DeploymentEvidencePath",
        str(evidence_path),
        cwd=ROOT,
    )

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "does not match deployment evidence after_sha" in combined_output


def test_release_smoke_fails_when_compatibility_sunset_evidence_is_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    runtime_policy = dict(_StubAionHandler.health_payload["runtime_policy"])
    runtime_policy.pop("compatibility_sunset_ready", None)
    _StubAionHandler.health_payload["runtime_policy"] = runtime_policy

    result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "runtime_policy is missing compatibility_sunset_ready" in combined_output


def test_release_smoke_fails_when_external_cadence_cutover_fields_are_missing(
    stub_aion_server: _StubAionServer,
) -> None:
    scheduler = dict(_StubAionHandler.health_payload["scheduler"])
    external_owner_policy = dict(scheduler["external_owner_policy"])
    external_owner_policy.pop("cutover_proof_owner", None)
    scheduler["external_owner_policy"] = external_owner_policy
    _StubAionHandler.health_payload["scheduler"] = scheduler

    result = _run_release_smoke("-BaseUrl", stub_aion_server.base_url, cwd=ROOT)

    assert result.returncode != 0
    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert "scheduler.external_owner_policy is missing cutover_proof_owner" in combined_output
