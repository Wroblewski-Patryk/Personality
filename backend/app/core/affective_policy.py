from __future__ import annotations

from typing import Any, Literal


def affective_assessment_enabled(settings: Any) -> bool:
    enabled_toggle = getattr(settings, "is_affective_assessment_enabled", None)
    if callable(enabled_toggle):
        return bool(enabled_toggle())
    explicit = getattr(settings, "affective_assessment_enabled", None)
    if explicit is not None:
        return bool(explicit)
    environment = str(getattr(settings, "app_env", "")).strip().lower()
    return environment != "production"


def affective_assessment_source(settings: Any) -> Literal["explicit", "environment_default"]:
    if getattr(settings, "affective_assessment_enabled", None) is not None:
        return "explicit"
    return "environment_default"


def affective_classifier_available(settings: Any) -> bool:
    return bool(str(getattr(settings, "openai_api_key", "") or "").strip())


def affective_assessment_policy_snapshot(settings: Any) -> dict[str, Any]:
    enabled = affective_assessment_enabled(settings)
    classifier_available = affective_classifier_available(settings)
    if enabled and classifier_available:
        posture = "ai_assisted_active"
        hint = "ai_classifier_available_for_affective_assessment"
    elif enabled:
        posture = "fallback_only_classifier_unavailable"
        hint = "configure_openai_api_key_or_disable_ai_affective_assessment"
    else:
        posture = "fallback_only_policy_disabled"
        hint = "policy_disabled_use_deterministic_affective_baseline"
    return {
        "affective_assessment_enabled": enabled,
        "affective_assessment_source": affective_assessment_source(settings),
        "affective_classifier_available": classifier_available,
        "affective_assessment_posture": posture,
        "affective_assessment_hint": hint,
        "affective_assessment_owner": "affective_assessment_rollout_policy",
    }
