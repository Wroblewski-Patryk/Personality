from __future__ import annotations


def _normalize_trigger_mode(trigger_mode: str | None) -> str:
    normalized = str(trigger_mode or "").strip().lower()
    if normalized in {
        "source_automation",
        "webhook_manual_fallback",
        "ui_manual_fallback",
    }:
        return normalized
    return "source_automation"


def _trigger_class(trigger_mode: str) -> str:
    if trigger_mode == "source_automation":
        return "primary_automation"
    return "manual_fallback"


def deployment_policy_snapshot(
    *,
    runtime_build_revision: str | None = None,
    trigger_mode: str | None = None,
) -> dict[str, object]:
    selected_trigger_mode = _normalize_trigger_mode(trigger_mode)
    selected_trigger_class = _trigger_class(selected_trigger_mode)
    normalized_revision = str(runtime_build_revision or "").strip()
    revision_declared = bool(normalized_revision) and normalized_revision.lower() != "unknown"
    if revision_declared:
        runtime_revision_state = "runtime_build_revision_declared"
        runtime_revision_hint = "runtime_build_revision_can_be_compared_with_local_repo_head_or_deploy_evidence"
    else:
        runtime_revision_state = "runtime_build_revision_missing"
        runtime_revision_hint = "configure_app_build_revision_for_machine_visible_repo_to_production_parity"
    if selected_trigger_class == "primary_automation":
        provenance_state = (
            "primary_runtime_provenance_declared"
            if revision_declared
            else "primary_runtime_provenance_without_build_revision"
        )
    else:
        provenance_state = (
            "fallback_runtime_provenance_declared"
            if revision_declared
            else "fallback_runtime_provenance_without_build_revision"
        )
    return {
        "policy_owner": "deployment_standard_and_release_reliability",
        "deployment_automation_policy_owner": "coolify_repo_deploy_automation",
        "hosting_baseline": "coolify_medium_term_standard",
        "hosting_transition_state": "not_scheduled",
        "runtime_build_revision": normalized_revision or "unknown",
        "runtime_build_revision_state": runtime_revision_state,
        "runtime_build_revision_hint": runtime_revision_hint,
        "runtime_trigger_mode": selected_trigger_mode,
        "runtime_trigger_class": selected_trigger_class,
        "runtime_provenance_state": provenance_state,
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
        "rollback_posture": "release_smoke_failure_blocks_completion_and_keeps_manual_rollback_available",
    }
