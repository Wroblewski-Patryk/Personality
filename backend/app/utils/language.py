import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageDecision:
    code: str
    confidence: float
    source: str


LANGUAGE_HINT_WORDS = {
    "en": {
        "the",
        "and",
        "please",
        "help",
        "what",
        "how",
        "why",
        "can",
        "should",
        "deploy",
        "build",
        "fix",
        "write",
    },
    "pl": {
        "czy",
        "jak",
        "co",
        "prosze",
        "pomoz",
        "pomoc",
        "zrob",
        "teraz",
        "wdroz",
        "napraw",
        "plan",
        "dzieki",
        "moge",
    },
}
SUPPORTED_LANGUAGE_CODES = frozenset(LANGUAGE_HINT_WORDS.keys())
LANGUAGE_CONTINUITY_PRECEDENCE = (
    "explicit_request",
    "diacritic_signal",
    "strong_keyword_signal",
    "continuity_resolution",
    "weak_keyword_signal",
    "default",
)

LANGUAGE_NAMES = {
    "en": {"english", "angielski"},
    "pl": {"polish", "polski"},
}

FALLBACK_MESSAGES = {
    "en": {
        "clarify": "I didn't catch any text yet. Send me a short message and I'll help from there.",
        "support": (
            "That sounds heavy. Let's take it one step at a time. "
            "Tell me what feels most pressing right now, and we'll work from there."
        ),
        "execute": (
            "I'm ready to help move this forward. "
            "Share the exact change you want, and we'll turn it into the next concrete step."
        ),
        "analyze": (
            "Let's break this down clearly. "
            "Start with the current state, the target outcome, and the main blocker."
        ),
        "mentor": (
            "A good next move is to define the goal, name the main constraint, "
            "and pick the smallest actionable step."
        ),
        "memory": "I can help with that. I also have a bit of recent context, so we can keep building from it.",
        "default": "I'm here and ready to help. {plan_goal}",
    },
    "pl": {
        "clarify": (
            "Nie dostalem jeszcze tresci wiadomosci. Napisz krotka wiadomosc, "
            "a od razu pomoge."
        ),
        "support": (
            "Brzmi to ciezko. Wezmy to krok po kroku. "
            "Powiedz, co teraz najbardziej Cie przytlacza, a pojdziemy od tego."
        ),
        "execute": (
            "Jasne, lecimy z tym. "
            "Napisz dokladnie, jaka zmiane chcesz wprowadzic, a zamienimy to na najblizszy konkretny krok."
        ),
        "analyze": (
            "Rozbijmy to spokojnie. "
            "Zacznij od obecnego stanu, oczekiwanego wyniku i glownej blokady."
        ),
        "mentor": (
            "Dobry nastepny ruch to nazwac cel, glowne ograniczenie "
            "i najmniejszy sensowny krok."
        ),
        "memory": "Moge w tym pomoc. Mam tez troche swiezego kontekstu, wiec mozemy plynnie isc dalej.",
        "default": "Jestem tu i moge pomoc. {plan_goal}",
    },
}


def normalize_for_matching(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(char for char in normalized if not unicodedata.combining(char))
    return stripped.lower()


def tokenize_normalized(text: str) -> set[str]:
    return set(re.findall(r"\b[\w-]+\b", normalize_for_matching(text)))


def language_name(code: str) -> str:
    if code == "pl":
        return "Polish"
    return "English"


def preferred_language_for_templates(code: str) -> str:
    if code in FALLBACK_MESSAGES:
        return code
    return "en"


def fallback_message(language_code: str, key: str, plan_goal: str) -> str:
    selected = FALLBACK_MESSAGES[preferred_language_for_templates(language_code)]
    return selected[key].format(plan_goal=plan_goal)


def detect_language(
    text: str,
    recent_memory: list[dict] | None = None,
    user_profile: dict | None = None,
) -> LanguageDecision:
    decision, _ = detect_language_with_diagnostics(
        text=text,
        recent_memory=recent_memory,
        user_profile=user_profile,
    )
    return decision


def language_continuity_policy_snapshot() -> dict[str, object]:
    return {
        "policy_owner": "language_continuity",
        "profile_owner_field": "preferred_language",
        "supported_language_codes": sorted(SUPPORTED_LANGUAGE_CODES),
        "precedence": list(LANGUAGE_CONTINUITY_PRECEDENCE),
        "continuity_sources": [
            "explicit_request",
            "diacritic_signal",
            "keyword_signal",
            "recent_memory",
            "user_profile",
            "default",
        ],
        "multilingual_posture": "mvp_supported_languages_only",
    }


def detect_language_with_diagnostics(
    text: str,
    recent_memory: list[dict] | None = None,
    user_profile: dict | None = None,
) -> tuple[LanguageDecision, dict[str, object]]:
    normalized = normalize_for_matching(text)

    explicit = _detect_explicit_language_request(normalized)
    if explicit:
        decision = LanguageDecision(code=explicit, confidence=0.98, source="explicit_request")
        return decision, _build_language_diagnostics(
            selected=decision,
            current_turn_posture="explicit_request",
            keyword_candidate=None,
            memory_candidate=_memory_language_decision(recent_memory or []),
            profile_candidate=_profile_language_decision(user_profile),
            continuity_resolution="not_needed_current_turn_signal",
        )

    diacritic_signal = _contains_polish_diacritic(text)
    if diacritic_signal:
        decision = LanguageDecision(code="pl", confidence=0.94, source="diacritic_signal")
        return decision, _build_language_diagnostics(
            selected=decision,
            current_turn_posture="diacritic_signal",
            keyword_candidate=None,
            memory_candidate=_memory_language_decision(recent_memory or []),
            profile_candidate=_profile_language_decision(user_profile),
            continuity_resolution="not_needed_current_turn_signal",
        )

    tokens = tokenize_normalized(text)
    keyword_decision = _keyword_language_decision(tokens)
    if keyword_decision is not None and keyword_decision.confidence >= 0.69:
        return keyword_decision, _build_language_diagnostics(
            selected=keyword_decision,
            current_turn_posture="strong_keyword_signal",
            keyword_candidate=keyword_decision,
            memory_candidate=_memory_language_decision(recent_memory or []),
            profile_candidate=_profile_language_decision(user_profile),
            continuity_resolution="not_needed_current_turn_signal",
        )

    memory_decision = _memory_language_decision(recent_memory or [])
    profile_decision = _profile_language_decision(user_profile)
    continuity_decision, continuity_resolution = _resolve_continuity_decision_with_reason(
        normalized_text=normalized,
        token_count=len(tokens),
        memory_decision=memory_decision,
        profile_decision=profile_decision,
        user_profile=user_profile,
    )
    if continuity_decision is not None:
        return continuity_decision, _build_language_diagnostics(
            selected=continuity_decision,
            current_turn_posture="weak_keyword_signal" if keyword_decision is not None else "no_current_turn_signal",
            keyword_candidate=keyword_decision,
            memory_candidate=memory_decision,
            profile_candidate=profile_decision,
            continuity_resolution=continuity_resolution,
        )

    if keyword_decision is not None:
        return keyword_decision, _build_language_diagnostics(
            selected=keyword_decision,
            current_turn_posture="weak_keyword_signal",
            keyword_candidate=keyword_decision,
            memory_candidate=memory_decision,
            profile_candidate=profile_decision,
            continuity_resolution="weak_keyword_fallback",
        )

    decision = LanguageDecision(code="en", confidence=0.35, source="default")
    return decision, _build_language_diagnostics(
        selected=decision,
        current_turn_posture="no_current_turn_signal",
        keyword_candidate=keyword_decision,
        memory_candidate=memory_decision,
        profile_candidate=profile_decision,
        continuity_resolution="default_fallback",
    )


def infer_language_from_memory(recent_memory: list[dict]) -> str | None:
    decision = _memory_language_decision(recent_memory)
    return decision.code if decision is not None else None


def infer_language_from_profile(user_profile: dict | None) -> str | None:
    decision = _profile_language_decision(user_profile)
    return decision.code if decision is not None else None


def _contains_polish_diacritic(text: str) -> bool:
    return any(char in text.lower() for char in "\u0105\u0107\u0119\u0142\u0144\u00f3\u015b\u017a\u017c")


def _detect_explicit_language_request(normalized: str) -> str | None:
    if not normalized:
        return None

    request_signals = {
        "reply in",
        "respond in",
        "answer in",
        "write in",
        "speak in",
        "odpisuj po",
        "odpowiadaj po",
        "pisz po",
        "mow po",
    }
    for code, names in LANGUAGE_NAMES.items():
        for name in names:
            if any(f"{signal} {name}" in normalized for signal in request_signals):
                return code
            if f"po {name}" in normalized:
                return code
    return None


def _keyword_language_decision(tokens: set[str]) -> LanguageDecision | None:
    scores = {
        code: len(tokens.intersection(words))
        for code, words in LANGUAGE_HINT_WORDS.items()
    }
    best_code = max(scores, key=scores.get)
    best_score = scores[best_code]
    other_score = max(score for code, score in scores.items() if code != best_code)

    if best_score >= 2 and best_score > other_score:
        confidence = min(0.9, 0.45 + (best_score * 0.12))
        return LanguageDecision(code=best_code, confidence=round(confidence, 2), source="keyword_signal")
    if best_score == 1 and best_score > other_score:
        return LanguageDecision(code=best_code, confidence=0.58, source="keyword_signal")
    return None


def _memory_language_decision(recent_memory: list[dict]) -> LanguageDecision | None:
    if not recent_memory:
        return None

    language_weights: dict[str, float] = {}
    for index, memory_item in enumerate(recent_memory[:6]):
        code = _extract_memory_language(memory_item)
        if code is None:
            continue
        recency_weight = max(0.2, 1.0 - (index * 0.18))
        language_weights[code] = language_weights.get(code, 0.0) + recency_weight

    if not language_weights:
        return None

    best_code, best_weight = max(language_weights.items(), key=lambda item: item[1])
    other_weight = max((weight for code, weight in language_weights.items() if code != best_code), default=0.0)
    if best_weight <= other_weight:
        return None

    confidence = min(0.84, 0.58 + (best_weight * 0.12))
    return LanguageDecision(code=best_code, confidence=round(confidence, 2), source="recent_memory")


def _extract_memory_language(memory_item: dict) -> str | None:
    payload = memory_item.get("payload")
    if isinstance(payload, dict):
        payload_language = _normalize_language_code(
            payload.get("response_language") or payload.get("language")
        )
        if payload_language is not None:
            return payload_language

    summary = str(memory_item.get("summary", ""))
    match = re.search(r"(?:response_)?language=([a-z]{2})", summary)
    if not match:
        return None
    return _normalize_language_code(match.group(1))


def _profile_language_decision(user_profile: dict | None) -> LanguageDecision | None:
    if not user_profile:
        return None

    language = _normalize_language_code(user_profile.get("preferred_language"))
    if language is None:
        return None

    raw_confidence = user_profile.get("language_confidence", 0.66)
    try:
        confidence = float(raw_confidence)
    except (TypeError, ValueError):
        confidence = 0.66
    confidence = max(0.55, min(0.95, confidence))
    return LanguageDecision(code=language, confidence=round(confidence, 2), source="user_profile")


def _resolve_continuity_decision(
    *,
    normalized_text: str,
    token_count: int,
    memory_decision: LanguageDecision | None,
    profile_decision: LanguageDecision | None,
    user_profile: dict | None,
) -> LanguageDecision | None:
    decision, _ = _resolve_continuity_decision_with_reason(
        normalized_text=normalized_text,
        token_count=token_count,
        memory_decision=memory_decision,
        profile_decision=profile_decision,
        user_profile=user_profile,
    )
    return decision


def _resolve_continuity_decision_with_reason(
    *,
    normalized_text: str,
    token_count: int,
    memory_decision: LanguageDecision | None,
    profile_decision: LanguageDecision | None,
    user_profile: dict | None,
) -> tuple[LanguageDecision | None, str]:
    if memory_decision is None:
        if profile_decision is None:
            return None, "no_continuity_candidate"
        return profile_decision, "profile_only"
    if profile_decision is None:
        return memory_decision, "memory_only"

    if memory_decision.code == profile_decision.code:
        if profile_decision.confidence > memory_decision.confidence + 0.12:
            return profile_decision, "aligned_profile_stronger"
        return memory_decision, "aligned_memory_preferred"

    if _is_ambiguous_follow_up(normalized_text=normalized_text, token_count=token_count):
        profile_source = str((user_profile or {}).get("language_source", "")).strip().lower()
        if profile_source == "explicit_request" and profile_decision.confidence >= 0.9:
            return profile_decision, "profile_explicit_request_override_on_ambiguous_follow_up"
    return memory_decision, "memory_preferred_over_profile"


def _is_ambiguous_follow_up(*, normalized_text: str, token_count: int) -> bool:
    if token_count <= 2:
        return True
    stripped = normalized_text.strip()
    return token_count <= 4 and len(stripped) <= 24


def _normalize_language_code(value: object) -> str | None:
    code = str(value or "").strip().lower()
    if code in SUPPORTED_LANGUAGE_CODES:
        return code
    return None


def _build_language_diagnostics(
    *,
    selected: LanguageDecision,
    current_turn_posture: str,
    keyword_candidate: LanguageDecision | None,
    memory_candidate: LanguageDecision | None,
    profile_candidate: LanguageDecision | None,
    continuity_resolution: str,
) -> dict[str, object]:
    return {
        **language_continuity_policy_snapshot(),
        "selected_language": selected.code,
        "selected_source": selected.source,
        "selected_confidence": selected.confidence,
        "current_turn_posture": current_turn_posture,
        "continuity_resolution": continuity_resolution,
        "fallback_posture": "selected_default" if selected.source == "default" else "not_used",
        "keyword_candidate": _decision_payload(keyword_candidate),
        "memory_candidate": _decision_payload(memory_candidate),
        "profile_candidate": _decision_payload(profile_candidate),
    }


def _decision_payload(decision: LanguageDecision | None) -> dict[str, object] | None:
    if decision is None:
        return None
    return {
        "code": decision.code,
        "confidence": decision.confidence,
        "source": decision.source,
    }
