from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.deployment_policy import deployment_policy_snapshot


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def _infer_repository(explicit_repository: str) -> str:
    if explicit_repository:
        return explicit_repository

    remote_url = _git_value("config", "--get", "remote.origin.url")
    if not remote_url:
        return ""

    match = re.search(r"github\.com[:/](.+?)(?:\.git)?$", remote_url)
    if match is None:
        return ""
    return match.group(1)


def _resolve_after_sha(explicit_after_sha: str) -> str:
    if explicit_after_sha:
        return explicit_after_sha
    return _git_value("rev-parse", "HEAD")


def _resolve_before_sha(*, explicit_before_sha: str, after_sha: str) -> str:
    if explicit_before_sha:
        return explicit_before_sha
    if not after_sha:
        return ""
    before_sha = _git_value("rev-parse", f"{after_sha}^")
    return before_sha or after_sha


def _resolve_commit_message(after_sha: str) -> str:
    message = _git_value("log", "-1", "--pretty=%s", after_sha)
    return message or "manual deploy trigger"


def _build_payload(
    *,
    repository: str,
    branch: str,
    before_sha: str,
    after_sha: str,
    pusher_name: str,
    commit_message: str,
) -> dict[str, Any]:
    timestamp = _utc_now_iso()
    commit_url = f"https://github.com/{repository}/commit/{after_sha}"
    compare_url = f"https://github.com/{repository}/compare/{before_sha}...{after_sha}"
    owner = repository.split("/")[0]
    name = repository.split("/")[-1]

    return {
        "ref": f"refs/heads/{branch}",
        "before": before_sha,
        "after": after_sha,
        "compare": compare_url,
        "created": False,
        "deleted": False,
        "forced": False,
        "base_ref": None,
        "commits": [
            {
                "id": after_sha,
                "message": commit_message,
                "timestamp": timestamp,
                "url": commit_url,
                "author": {"name": pusher_name, "email": ""},
                "committer": {"name": pusher_name, "email": ""},
                "added": [],
                "removed": [],
                "modified": [],
            }
        ],
        "head_commit": {
            "id": after_sha,
            "message": commit_message,
            "timestamp": timestamp,
            "url": commit_url,
            "author": {"name": pusher_name, "email": ""},
            "committer": {"name": pusher_name, "email": ""},
            "added": [],
            "removed": [],
            "modified": [],
        },
        "repository": {
            "name": name,
            "full_name": repository,
            "private": False,
            "default_branch": branch,
            "html_url": f"https://github.com/{repository}",
            "clone_url": f"https://github.com/{repository}.git",
            "ssh_url": f"git@github.com:{repository}.git",
            "owner": {"name": owner, "login": owner},
        },
        "pusher": {"name": pusher_name},
        "sender": {"login": pusher_name},
    }


def _post_webhook(
    *,
    webhook_url: str,
    payload_bytes: bytes,
    signature: str,
) -> tuple[bool, int | None, str, str]:
    request = urllib.request.Request(
        webhook_url,
        data=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": signature,
            "User-Agent": "aion-coolify-webhook-trigger",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            return True, int(response.getcode()), response_body, ""
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, int(exc.code), body, f"http_error:{exc.code}"
    except urllib.error.URLError as exc:
        return False, None, "", f"url_error:{exc.reason}"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trigger Coolify deploy webhook with optional evidence capture.")
    parser.add_argument("--webhook-url", required=True)
    parser.add_argument("--webhook-secret", required=True)
    parser.add_argument("--repository", default="")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--before-sha", default="")
    parser.add_argument("--after-sha", default="")
    parser.add_argument("--pusher-name", default="codex")
    parser.add_argument("--evidence-path", default="")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    repository = _infer_repository(str(args.repository))
    if not repository:
        print(
            "Could not infer repository name from git remote. Pass --repository owner/name explicitly.",
            file=sys.stderr,
        )
        return 1

    after_sha = _resolve_after_sha(str(args.after_sha))
    if not after_sha:
        print("Could not determine HEAD commit. Pass --after-sha explicitly.", file=sys.stderr)
        return 1

    before_sha = _resolve_before_sha(explicit_before_sha=str(args.before_sha), after_sha=after_sha)
    if not before_sha:
        print("Could not determine previous commit. Pass --before-sha explicitly.", file=sys.stderr)
        return 1

    commit_message = _resolve_commit_message(after_sha)
    payload = _build_payload(
        repository=repository,
        branch=str(args.branch),
        before_sha=before_sha,
        after_sha=after_sha,
        pusher_name=str(args.pusher_name),
        commit_message=commit_message,
    )
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    signature = "sha256=" + hmac.new(
        str(args.webhook_secret).encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    triggered_at = _utc_now_iso()
    ok, status_code, response_body, error = _post_webhook(
        webhook_url=str(args.webhook_url),
        payload_bytes=body,
        signature=signature,
    )
    finished_at = _utc_now_iso()

    evidence = {
        "kind": "coolify_deploy_webhook_evidence",
        "policy_owner": deployment_policy_snapshot()["deployment_automation_policy_owner"],
        "generated_at": finished_at,
        "webhook_url": str(args.webhook_url),
        "repository": repository,
        "branch": str(args.branch),
        "before_sha": before_sha,
        "after_sha": after_sha,
        "pusher_name": str(args.pusher_name),
        "trigger_mode": "webhook_manual_fallback",
        "trigger_class": "manual_fallback",
        "canonical_coolify_app": deployment_policy_snapshot()["canonical_coolify_app"],
        "triggered_at": triggered_at,
        "finished_at": finished_at,
        "response": {
            "ok": ok,
            "status_code": status_code,
            "body": response_body,
            "error": error,
        },
    }

    if args.evidence_path:
        evidence_path = Path(str(args.evidence_path))
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if response_body:
        print(response_body)
    if not ok:
        print(
            f"Coolify deploy webhook trigger failed: status_code={status_code} error={error}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
