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
    normalized = normalize_for_matching(text)

    explicit = _detect_explicit_language_request(normalized)
    if explicit:
        return LanguageDecision(code=explicit, confidence=0.98, source="explicit_request")

    if _contains_polish_diacritic(text):
        return LanguageDecision(code="pl", confidence=0.94, source="diacritic_signal")

    tokens = tokenize_normalized(text)
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

    memory_language = infer_language_from_memory(recent_memory or [])
    if memory_language:
        return LanguageDecision(code=memory_language, confidence=0.72, source="recent_memory")

    profile_language = infer_language_from_profile(user_profile)
    if profile_language:
        return LanguageDecision(code=profile_language, confidence=0.66, source="user_profile")

    if best_score == 1 and best_score > other_score:
        return LanguageDecision(code=best_code, confidence=0.58, source="keyword_signal")

    return LanguageDecision(code="en", confidence=0.35, source="default")


def infer_language_from_memory(recent_memory: list[dict]) -> str | None:
    for memory_item in recent_memory:
        summary = str(memory_item.get("summary", ""))
        match = re.search(r"(?:response_)?language=([a-z]{2})", summary)
        if match:
            return match.group(1)
    return None


def infer_language_from_profile(user_profile: dict | None) -> str | None:
    if not user_profile:
        return None

    language = str(user_profile.get("preferred_language", "")).strip().lower()
    if re.fullmatch(r"[a-z]{2}", language):
        return language
    return None


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
