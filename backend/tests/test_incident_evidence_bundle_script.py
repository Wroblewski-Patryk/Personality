from __future__ import annotations

import importlib.util
import json
import sys
from argparse import Namespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "export_incident_evidence_bundle.py"
SPEC = importlib.util.spec_from_file_location("export_incident_evidence_bundle_script", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class _BundleHandler(BaseHTTPRequestHandler):
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
            self._write_json(
                {
                    "status": "ok",
                    "observability": {
                        "policy_owner": "incident_evidence_export_policy",
                        "bundle_helper_available": True,
                    },
                }
            )
            return
        self._write_json({"detail": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/internal/event/debug":
            self._write_json({"detail": "not found"}, status=404)
            return
        body_length = int(self.headers.get("Content-Length", "0"))
        payload = {}
        if body_length > 0:
            payload = json.loads(self.rfile.read(body_length).decode("utf-8"))
        trace_id = str(payload.get("meta", {}).get("trace_id", "trace-default"))
        self._write_json(
            {
                "event_id": "evt-bundle",
                "trace_id": trace_id,
                "source": "api",
                "incident_evidence": {
                    "kind": "runtime_incident_evidence",
                    "schema_version": "1.0.0",
                    "policy_owner": "incident_evidence_export_policy",
                    "trace_id": trace_id,
                    "event_id": "evt-bundle",
                    "source": "api",
                    "duration_ms": 15,
                    "stage_timings_ms": {
                        "memory_load": 1,
                        "perception": 2,
                        "total": 15,
                    },
                    "policy_surface_coverage": {
                        "present": [
                            "runtime_policy",
                            "memory_retrieval",
                            "scheduler.external_owner_policy",
                            "reflection.supervision",
                            "connectors.execution_baseline",
                        ],
                        "missing": [],
                        "complete": True,
                    },
                    "policy_posture": {
                        "runtime_policy": {"event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy"},
                        "memory_retrieval": {"retrieval_lifecycle_policy_owner": "retrieval_lifecycle_policy"},
                        "scheduler.external_owner_policy": {"policy_owner": "external_scheduler_cadence_policy"},
                        "reflection.supervision": {"policy_owner": "deferred_reflection_supervision_policy"},
                        "connectors.execution_baseline": {"execution_owner": "connector_execution_registry"},
                    },
                },
            }
        )


class _BundleServer:
    def __init__(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _BundleHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def start(self) -> "_BundleServer":
        self.thread.start()
        return self

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


def test_main_exports_canonical_bundle_and_attaches_behavior_report(monkeypatch, tmp_path: Path) -> None:
    server = _BundleServer().start()
    try:
        report_path = tmp_path / "behavior-report.json"
        report_path.write_text(json.dumps({"kind": "behavior_validation_artifact"}), encoding="utf-8")
        output_root = tmp_path / "bundles"

        monkeypatch.setattr(
            MODULE,
            "_parse_args",
            lambda: Namespace(
                base_url=server.base_url,
                text="capture bundle",
                user_id="incident-user",
                output_root=str(output_root),
                capture_mode="incident",
                debug_token="",
                behavior_validation_report_path=str(report_path),
                trace_id="trace-bundle",
            ),
        )

        exit_code = MODULE.main()

        assert exit_code == 0
        bundle_dirs = list(output_root.iterdir())
        assert len(bundle_dirs) == 1
        bundle_dir = bundle_dirs[0]
        manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
        incident_evidence = json.loads((bundle_dir / "incident_evidence.json").read_text(encoding="utf-8"))
        health_snapshot = json.loads((bundle_dir / "health_snapshot.json").read_text(encoding="utf-8"))
        attached_report = json.loads((bundle_dir / "behavior_validation_report.json").read_text(encoding="utf-8"))

        assert manifest["kind"] == "incident_evidence_bundle_manifest"
        assert manifest["trace_id"] == "trace-bundle"
        assert manifest["event_id"] == "evt-bundle"
        assert manifest["files"]["behavior_validation_report"] == "behavior_validation_report.json"
        assert incident_evidence["trace_id"] == "trace-bundle"
        assert health_snapshot["status"] == "ok"
        assert attached_report["kind"] == "behavior_validation_artifact"
    finally:
        server.stop()
