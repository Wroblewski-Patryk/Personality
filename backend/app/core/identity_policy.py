from typing import Any


PROFILE_PREFERENCE_FIELDS: tuple[str, ...] = ("preferred_language",)
CONCLUSION_PREFERENCE_FIELDS: tuple[str, ...] = (
    "response_style",
    "collaboration_preference",
    "preferred_role",
)
SUPPORTED_LANGUAGE_CODES: tuple[str, ...] = ("en", "pl")


def identity_policy_snapshot() -> dict[str, Any]:
    return {
        "policy_owner": "identity_policy",
        "language_strategy": "heuristic_plus_profile_continuity",
        "profile_owner_fields": list(PROFILE_PREFERENCE_FIELDS),
        "conclusion_owner_fields": list(CONCLUSION_PREFERENCE_FIELDS),
        "relation_fallback_identity_write": "disallowed",
        "supported_language_codes": list(SUPPORTED_LANGUAGE_CODES),
        "multilingual_posture": "mvp_supported_languages_only",
    }


def resolve_identity_preferences(
    *,
    user_profile: dict | None = None,
    user_preferences: dict | None = None,
) -> dict[str, str | None]:
    profile = user_profile if isinstance(user_profile, dict) else {}
    preferences = user_preferences if isinstance(user_preferences, dict) else {}
    return {
        "preferred_language": _clean(profile.get("preferred_language")),
        "response_style": _clean(preferences.get("response_style")),
        "collaboration_preference": _clean(preferences.get("collaboration_preference")),
    }


def _clean(value: object) -> str | None:
    normalized = str(value or "").strip().lower()
    return normalized or None
