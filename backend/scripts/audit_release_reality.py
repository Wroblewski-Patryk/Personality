from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


WEB_REVISION_META_RE = re.compile(
    r'<meta\s+name="aion-web-build-revision"\s+content="(?P<revision>[^"]*)"\s*/?>',
    re.IGNORECASE,
)


@dataclass(frozen=True)
class FetchResult:
    ok: bool
    data: Any = None
    error: str = ""


def _git_value(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _json_get(url: str, *, timeout_seconds: int) -> FetchResult:
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
            return FetchResult(ok=True, data=json.loads(body))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return FetchResult(ok=False, error=str(exc))


def _text_get(url: str, *, timeout_seconds: int) -> FetchResult:
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            return FetchResult(ok=True, data=response.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return FetchResult(ok=False, error=str(exc))


def _extract_web_revision(html: str) -> str:
    match = WEB_REVISION_META_RE.search(html)
    if match is None:
        return ""
    return str(match.group("revision") or "")


def _resolve_origin_main() -> str:
    origin_sha = _git_value("rev-parse", "origin/main")
    if origin_sha:
        return origin_sha
    return _git_value("ls-remote", "origin", "refs/heads/main").split("\t")[0]


def _verdict(
    *,
    selected_sha: str,
    local_head: str,
    origin_main: str,
    backend_revision: str,
    web_revision: str,
    release_ready: bool | None,
    release_violations: list[Any],
    v1_final_acceptance_state: str,
) -> str:
    if not selected_sha:
        return "HOLD_NO_SELECTED_SHA"
    if not backend_revision or not web_revision:
        return "HOLD_HEALTH_OR_WEB_REVISION_MISSING"
    if backend_revision != selected_sha or web_revision != selected_sha:
        return "HOLD_REVISION_DRIFT"
    if local_head and local_head != selected_sha:
        return "HOLD_LOCAL_HEAD_DIFFERS_FROM_SELECTED_SHA"
    if origin_main and origin_main != selected_sha:
        return "HOLD_ORIGIN_MAIN_DIFFERS_FROM_SELECTED_SHA"
    if release_ready is not True or release_violations:
        return "HOLD_HEALTH_OR_READINESS"
    if v1_final_acceptance_state and v1_final_acceptance_state != "core_v1_bundle_ready":
        return "HOLD_V1_ACCEPTANCE"
    return "GO_FOR_SELECTED_SHA"


def build_report(
    *,
    base_url: str,
    selected_sha: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    base_url = base_url.rstrip("/")
    local_head = _git_value("rev-parse", "HEAD")
    origin_main = _resolve_origin_main()
    if not selected_sha:
        selected_sha = local_head

    health_result = _json_get(f"{base_url}/health", timeout_seconds=timeout_seconds)
    settings_result = _text_get(f"{base_url}/settings", timeout_seconds=timeout_seconds)

    health = health_result.data if health_result.ok and isinstance(health_result.data, dict) else {}
    deployment = health.get("deployment", {}) if isinstance(health.get("deployment", {}), dict) else {}
    release_readiness = (
        health.get("release_readiness", {}) if isinstance(health.get("release_readiness", {}), dict) else {}
    )
    v1_readiness = health.get("v1_readiness", {}) if isinstance(health.get("v1_readiness", {}), dict) else {}

    backend_revision = str(deployment.get("runtime_build_revision", "") or "")
    web_revision = _extract_web_revision(str(settings_result.data or "")) if settings_result.ok else ""
    release_violations = list(release_readiness.get("violations", []) or [])
    release_ready_raw = release_readiness.get("ready")
    release_ready = release_ready_raw if isinstance(release_ready_raw, bool) else None
    v1_final_acceptance_state = str(v1_readiness.get("final_acceptance_state", "") or "")

    verdict = _verdict(
        selected_sha=selected_sha,
        local_head=local_head,
        origin_main=origin_main,
        backend_revision=backend_revision,
        web_revision=web_revision,
        release_ready=release_ready,
        release_violations=release_violations,
        v1_final_acceptance_state=v1_final_acceptance_state,
    )

    return {
        "kind": "release_reality_audit",
        "base_url": base_url,
        "selected_sha": selected_sha,
        "local_head": local_head,
        "origin_main": origin_main,
        "production": {
            "health_ok": health_result.ok,
            "health_error": health_result.error,
            "settings_ok": settings_result.ok,
            "settings_error": settings_result.error,
            "backend_runtime_build_revision": backend_revision,
            "web_build_revision": web_revision,
            "release_ready": release_ready,
            "release_violations": release_violations,
            "v1_final_acceptance_state": v1_final_acceptance_state,
            "v1_final_acceptance_gate_states": v1_readiness.get("final_acceptance_gate_states", {}),
        },
        "verdict": verdict,
        "release_marker_allowed": verdict == "GO_FOR_SELECTED_SHA",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit release reality by comparing git, production revision, and readiness surfaces."
    )
    parser.add_argument("--base-url", default="https://aviary.luckysparrow.ch")
    parser.add_argument("--selected-sha", default="", help="Release SHA to verify. Defaults to local HEAD.")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--output", default="", help="Optional JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = build_report(
        base_url=str(args.base_url),
        selected_sha=str(args.selected_sha),
        timeout_seconds=int(args.timeout_seconds),
    )
    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    print(encoded)
    if args.output:
        from pathlib import Path

        output_path = Path(str(args.output))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(encoded + "\n", encoding="utf-8")
    return 0 if report["verdict"] == "GO_FOR_SELECTED_SHA" else 1


if __name__ == "__main__":
    raise SystemExit(main())
