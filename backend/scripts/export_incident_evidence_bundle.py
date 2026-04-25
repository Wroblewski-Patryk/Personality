from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.observability_policy import (
    build_incident_evidence_bundle_manifest,
    format_incident_bundle_directory_name,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a canonical incident-evidence bundle from runtime health and debug surfaces.",
    )
    parser.add_argument("--base-url", required=True, help="Base runtime URL, for example http://localhost:8000")
    parser.add_argument("--text", default="AION incident evidence capture", help="Diagnostic payload text.")
    parser.add_argument("--user-id", default="incident-capture", help="User id used for the debug event.")
    parser.add_argument(
        "--output-root",
        default="artifacts/incident_evidence",
        help="Root directory where the bundle directory will be created.",
    )
    parser.add_argument(
        "--capture-mode",
        choices=("incident", "release_smoke", "behavior_validation"),
        default="incident",
        help="Capture mode written into the manifest.",
    )
    parser.add_argument(
        "--debug-token",
        default="",
        help="Optional debug token forwarded as X-AION-Debug-Token.",
    )
    parser.add_argument(
        "--behavior-validation-report-path",
        default="",
        help="Optional behavior validation report to attach as behavior_validation_report.json.",
    )
    parser.add_argument(
        "--trace-id",
        default="",
        help="Optional explicit trace id; defaults to a UTC timestamp-based value.",
    )
    return parser.parse_args()


def _json_request(
    *,
    method: str,
    url: str,
    payload: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, object]:
    request_headers = {"Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    body_bytes: bytes | None = None
    if payload is not None:
        request_headers["Content-Type"] = "application/json; charset=utf-8"
        body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = Request(url=url, method=method.upper(), headers=request_headers, data=body_bytes)
    try:
        with urlopen(request, timeout=30) as response:  # noqa: S310
            raw = response.read().decode("utf-8")
    except HTTPError as exc:  # pragma: no cover - exercised through integration path
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} while calling {url}: {detail}") from exc
    except URLError as exc:  # pragma: no cover - exercised through integration path
        raise RuntimeError(f"Unable to reach {url}: {exc.reason}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON returned by {url}.") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(f"Unexpected non-object JSON returned by {url}.")
    return parsed


def main() -> int:
    args = _parse_args()
    base_url = str(args.base_url).rstrip("/")
    captured_at = datetime.now(timezone.utc)
    trace_id = str(args.trace_id).strip() or f"incident-bundle-{captured_at.strftime('%Y%m%dT%H%M%SZ')}"
    debug_headers: dict[str, str] = {}
    if args.debug_token:
        debug_headers["X-AION-Debug-Token"] = str(args.debug_token)

    health_snapshot = _json_request(
        method="GET",
        url=f"{base_url}/health",
    )
    debug_payload = {
        "source": "api",
        "subsource": "incident_bundle_export",
        "text": str(args.text),
        "meta": {
            "user_id": str(args.user_id),
            "trace_id": trace_id,
        },
    }
    debug_response = _json_request(
        method="POST",
        url=f"{base_url}/internal/event/debug",
        payload=debug_payload,
        headers=debug_headers,
    )
    incident_evidence = debug_response.get("incident_evidence")
    if not isinstance(incident_evidence, dict):
        raise RuntimeError("Debug response did not include incident_evidence.")
    event_id = str(debug_response.get("event_id") or "")
    response_trace_id = str(debug_response.get("trace_id") or trace_id)
    source = str(incident_evidence.get("source") or debug_response.get("source") or "api")

    output_root = Path(str(args.output_root))
    bundle_dir = output_root / format_incident_bundle_directory_name(
        captured_at=captured_at,
        trace_id=response_trace_id,
        event_id=event_id,
    )
    bundle_dir.mkdir(parents=True, exist_ok=False)

    attached_behavior_report = False
    behavior_report_path_raw = str(getattr(args, "behavior_validation_report_path", "") or "").strip()
    if behavior_report_path_raw:
        source_report = Path(behavior_report_path_raw)
        if not source_report.exists():
            raise RuntimeError(f"Behavior validation report not found: {source_report}")
        shutil.copyfile(source_report, bundle_dir / "behavior_validation_report.json")
        attached_behavior_report = True

    manifest = build_incident_evidence_bundle_manifest(
        base_url=base_url,
        capture_mode=str(args.capture_mode),
        trace_id=response_trace_id,
        event_id=event_id,
        source=source,
        captured_at=captured_at,
        attached_behavior_report=attached_behavior_report,
    )
    (bundle_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (bundle_dir / "incident_evidence.json").write_text(
        json.dumps(incident_evidence, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (bundle_dir / "health_snapshot.json").write_text(
        json.dumps(health_snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "bundle_dir": str(bundle_dir),
        "capture_mode": str(args.capture_mode),
        "trace_id": response_trace_id,
        "event_id": event_id,
        "attached_behavior_report": attached_behavior_report,
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
