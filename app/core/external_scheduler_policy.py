from __future__ import annotations

from datetime import datetime, timezone

from app.core.scheduler_contracts import normalize_scheduler_execution_mode


MAINTENANCE_EXTERNAL_ENTRYPOINT = "scripts/run_maintenance_tick_once.py"
PROACTIVE_EXTERNAL_ENTRYPOINT = "scripts/run_proactive_tick_once.py"
EXTERNAL_CADENCE_EVIDENCE_MIN_STALE_SECONDS = 300


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _external_cadence_run_evidence(
    *,
    cadence_kind: str,
    entrypoint_path: str,
    last_run_at: str | None,
    last_summary: dict[str, object] | None,
    interval_seconds: int,
) -> dict[str, object]:
    summary = dict(last_summary or {})
    parsed_last_run = _parse_timestamp(last_run_at)
    stale_after_seconds = max(int(interval_seconds) * 2, EXTERNAL_CADENCE_EVIDENCE_MIN_STALE_SECONDS)
    now = datetime.now(timezone.utc)
    recent_success = False
    evidence_state = "missing_external_run_evidence"
    last_run_age_seconds = None
    if parsed_last_run is not None:
        last_run_age_seconds = max(0, int((now - parsed_last_run).total_seconds()))
        executed = bool(summary.get("executed", False))
        expected_reason = str(summary.get("reason", "") or "")
        if last_run_age_seconds > stale_after_seconds:
            evidence_state = "stale_external_run_evidence"
        elif executed and expected_reason == "external_scheduler_owner":
            recent_success = True
            evidence_state = "recent_external_run_evidence"
        else:
            evidence_state = "recent_external_run_non_success"
    return {
        "cadence_kind": cadence_kind,
        "entrypoint_path": entrypoint_path,
        "last_run_at": last_run_at,
        "last_run_age_seconds": last_run_age_seconds,
        "stale_after_seconds": stale_after_seconds,
        "evidence_state": evidence_state,
        "recent_success": recent_success,
        "last_summary": summary,
    }


def external_scheduler_policy_snapshot(
    *,
    scheduler_execution_mode: str | None,
    scheduler_running: bool = False,
    maintenance_last_run_at: str | None = None,
    maintenance_last_summary: dict[str, object] | None = None,
    maintenance_interval_seconds: int = 3600,
    proactive_enabled: bool = False,
    proactive_last_run_at: str | None = None,
    proactive_last_summary: dict[str, object] | None = None,
    proactive_interval_seconds: int = 1800,
) -> dict[str, object]:
    selected_execution_mode = normalize_scheduler_execution_mode(
        scheduler_execution_mode
    )
    maintenance_run_evidence = _external_cadence_run_evidence(
        cadence_kind="maintenance",
        entrypoint_path=MAINTENANCE_EXTERNAL_ENTRYPOINT,
        last_run_at=maintenance_last_run_at,
        last_summary=maintenance_last_summary,
        interval_seconds=maintenance_interval_seconds,
    )
    proactive_run_evidence = _external_cadence_run_evidence(
        cadence_kind="proactive",
        entrypoint_path=PROACTIVE_EXTERNAL_ENTRYPOINT,
        last_run_at=proactive_last_run_at,
        last_summary=proactive_last_summary,
        interval_seconds=proactive_interval_seconds,
    )
    duplicate_protection_state = (
        "app_local_conflict_detected"
        if selected_execution_mode == "externalized" and scheduler_running
        else "single_owner_boundary_clear"
    )
    cutover_proof_ready = (
        selected_execution_mode == "externalized"
        and duplicate_protection_state == "single_owner_boundary_clear"
        and bool(maintenance_run_evidence["recent_success"])
        and (
            not proactive_enabled
            or bool(proactive_run_evidence["recent_success"])
        )
    )
    production_baseline_ready = cutover_proof_ready
    return {
        "policy_owner": "external_scheduler_cadence_policy",
        "target_execution_mode": "externalized",
        "selected_execution_mode": selected_execution_mode,
        "maintenance_cadence_target_owner": "external_scheduler",
        "proactive_cadence_target_owner": "external_scheduler",
        "maintenance_entrypoint_path": MAINTENANCE_EXTERNAL_ENTRYPOINT,
        "proactive_entrypoint_path": PROACTIVE_EXTERNAL_ENTRYPOINT,
        "app_local_fallback_owner": "in_process_scheduler",
        "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
        "maintenance_run_evidence": maintenance_run_evidence,
        "proactive_run_evidence": proactive_run_evidence,
        "duplicate_protection_posture": {
            "state": duplicate_protection_state,
            "scheduler_running": bool(scheduler_running),
            "maintenance_entrypoint_idempotency_baseline": "single_tick_summary_per_invocation",
            "proactive_entrypoint_idempotency_baseline": "single_tick_candidate_evaluation_per_invocation",
            "rollback_owner_when_missing_proof": "in_process_scheduler",
        },
        "cutover_proof_ready": cutover_proof_ready,
        "cutover_proof_state": (
            "external_scheduler_cutover_proven"
            if cutover_proof_ready
            else "external_scheduler_target_only"
        ),
        "cutover_proof_hint": (
            "external_scheduler_cutover_proven"
            if cutover_proof_ready
            else "provide_recent_external_last_run_and_duplicate_protection_evidence"
        ),
        "production_baseline_ready": production_baseline_ready,
        "production_baseline_state": (
            "external_scheduler_baseline_aligned"
            if production_baseline_ready
            else (
                "external_scheduler_target_without_cutover_proof"
                if selected_execution_mode == "externalized"
                else "in_process_scheduler_transitional_fallback"
            )
        ),
        "production_baseline_hint": (
            "external_scheduler_owns_cadence"
            if production_baseline_ready
            else (
                "provide_external_cutover_proof_for_selected_target_baseline"
                if selected_execution_mode == "externalized"
                else "switch_scheduler_execution_mode_to_externalized_for_target_baseline"
            )
        ),
    }
