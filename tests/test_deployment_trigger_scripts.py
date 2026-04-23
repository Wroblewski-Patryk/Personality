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


ROOT = Path(__file__).resolve().parents[1]
TRIGGER_SCRIPT_PATH = ROOT / "scripts" / "trigger_coolify_deploy_webhook.py"
RELEASE_SMOKE_PS1_PATH = ROOT / "scripts" / "run_release_smoke.ps1"
PYTHON_EXE = ROOT / ".venv" / "Scripts" / "python.exe"

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
    "adaptive_outputs",
    "relations",
]


def _powershell_exe() -> str | None:
    return shutil.which("powershell") or shutil.which("pwsh")


class _StubAionHandler(BaseHTTPRequestHandler):
    health_payload: dict[str, object] = {}
    event_payload: dict[str, object] = {}

    def _write_json(self, payload: dict[str, object], *, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._write_json(type(self).health_payload)
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
            "required_behavior_scenarios": [
                "T13.1",
                "T14.1",
                "T14.2",
                "T14.3",
                "T15.1",
                "T15.2",
            ],
            "approved_tool_slices": [
                "knowledge_search.search_web",
                "web_browser.read_page",
                "task_system.clickup_update_task",
            ],
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
        },
        "deployment": {
            "hosting_baseline": "coolify_medium_term_standard",
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
        },
        "conversation_channels": {
            "telegram": {
                "policy_owner": "telegram_conversation_reliability_telemetry",
                "round_trip_state": "provider_backed_ready",
                "bot_token_configured": True,
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
                "attention",
                "runtime_topology.attention_switch",
                "proactive",
                "scheduler.external_owner_policy",
                "reflection.supervision",
                "connectors.execution_baseline",
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
                },
            "v1_readiness": {
                "policy_owner": "v1_release_readiness_policy",
                "product_stage": "v1_no_ui_life_assistant",
                "conversation_gate_state": "conversation_surface_ready",
                    "learned_state_gate_state": "inspection_surface_ready",
                    "required_behavior_scenarios": [
                        "T13.1",
                        "T14.1",
                        "T14.2",
                        "T14.3",
                        "T15.1",
                        "T15.2",
                    ],
                    "approved_tool_slices": [
                        "knowledge_search.search_web",
                        "web_browser.read_page",
                    "task_system.clickup_update_task",
                ],
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
                "conversation_channels.telegram": {
                    "policy_owner": "telegram_conversation_reliability_telemetry",
                    "round_trip_state": "provider_backed_ready",
                    "bot_token_configured": True,
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


def _write_evidence(path: Path, *, minutes_ago: int = 0, ok: bool = True, status_code: int = 200) -> None:
    generated_at = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    payload = {
        "kind": "coolify_deploy_webhook_evidence",
        "generated_at": generated_at.isoformat(),
        "triggered_at": generated_at.isoformat(),
        "finished_at": generated_at.isoformat(),
        "response": {
            "ok": ok,
            "status_code": status_code,
            "body": "queued",
            "error": "",
        },
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
                "attention",
                "runtime_topology.attention_switch",
                "proactive",
                "scheduler.external_owner_policy",
                "reflection.supervision",
                "connectors.execution_baseline",
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
            },
                "v1_readiness": {
                    "policy_owner": "v1_release_readiness_policy",
                    "product_stage": "v1_no_ui_life_assistant",
                    "conversation_gate_state": "conversation_surface_ready",
                "learned_state_gate_state": "inspection_surface_ready",
                "required_behavior_scenarios": [
                    "T13.1",
                    "T14.1",
                    "T14.2",
                    "T14.3",
                    "T15.1",
                    "T15.2",
                ],
                "approved_tool_slices": [
                    "knowledge_search.search_web",
                    "web_browser.read_page",
                        "task_system.clickup_update_task",
                    ],
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
            "conversation_channels.telegram": {
                "policy_owner": "telegram_conversation_reliability_telemetry",
                "round_trip_state": "provider_backed_ready",
                "bot_token_configured": True,
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
        },
        "v1_readiness": {
            "policy_owner": "v1_release_readiness_policy",
            "product_stage": "v1_no_ui_life_assistant",
            "conversation_gate_state": "conversation_surface_ready",
            "learned_state_gate_state": "inspection_surface_ready",
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
    assert summary["deployment_hosting_baseline"] == "coolify_medium_term_standard"
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
    assert summary["deployment_evidence_checked"] is False
    assert summary["deployment_evidence_path"] == ""
    assert summary["deployment_evidence_status_code"] is None


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
    assert summary["incident_evidence_learned_state_policy_owner"] == "learned_state_inspection_policy"
    assert summary["incident_evidence_learned_state_internal_inspection_path"] == "/internal/state/inspect"
    assert summary["incident_evidence_learned_state_inspection_sections"] == LEARNED_STATE_INSPECTION_SECTIONS
    assert summary["incident_evidence_learned_state_growth_summary_sections"] == (
        LEARNED_STATE_GROWTH_SUMMARY_SECTIONS
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
    assert summary["incident_bundle_attention_coordination_mode"] == "durable_inbox"
    assert summary["incident_bundle_attention_contract_store_state"] == "repository_backed_contract_store_active"
    assert summary["incident_bundle_attention_runtime_topology_selected_mode"] == "durable_inbox"
    assert summary["incident_bundle_proactive_policy_owner"] == "proactive_runtime_policy"
    assert summary["incident_bundle_proactive_enabled"] is True
    assert summary["incident_bundle_proactive_production_baseline_state"] == (
        "external_scheduler_target_owner"
    )
    assert summary["incident_bundle_learned_state_policy_owner"] == "learned_state_inspection_policy"
    assert summary["incident_bundle_learned_state_internal_inspection_path"] == "/internal/state/inspect"
    assert summary["incident_bundle_learned_state_inspection_sections"] == LEARNED_STATE_INSPECTION_SECTIONS
    assert summary["incident_bundle_learned_state_growth_summary_sections"] == (
        LEARNED_STATE_GROWTH_SUMMARY_SECTIONS
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
