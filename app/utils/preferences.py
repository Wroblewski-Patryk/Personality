import re
from dataclasses import dataclass

from app.utils.language import normalize_for_matching


@dataclass(frozen=True)
class ResponseStylePreference:
    style: str
    confidence: float
    source: str


def detect_response_style_preference(text: str) -> ResponseStylePreference | None:
    normalized = normalize_for_matching(text)
    if not normalized:
        return None

    concise_signals = {
        "be concise",
        "keep it concise",
        "keep it short",
        "short answer",
        "short answers",
        "answer briefly",
        "reply briefly",
        "respond briefly",
        "be brief",
        "pisz krotko",
        "odpowiadaj krotko",
        "odpisuj krotko",
        "krotkie odpowiedzi",
        "krotka odpowiedz",
        "zwiezle",
        "bez lania wody",
    }
    structured_signals = {
        "in bullet points",
        "use bullet points",
        "reply in bullet points",
        "answer in bullet points",
        "respond in bullet points",
        "as a bullet list",
        "as a list",
        "w punktach",
        "w formie listy",
        "na liscie",
        "wypunktuj",
    }

    if any(signal in normalized for signal in concise_signals):
        return ResponseStylePreference(style="concise", confidence=0.95, source="explicit_request")

    if any(signal in normalized for signal in structured_signals):
        return ResponseStylePreference(style="structured", confidence=0.95, source="explicit_request")

    return None


def preferred_response_style(user_preferences: dict | None) -> str | None:
    if not user_preferences:
        return None

    style = str(user_preferences.get("response_style", "")).strip().lower()
    if style in {"concise", "structured"}:
        return style
    return None


def preferred_collaboration_preference(user_preferences: dict | None) -> str | None:
    if not user_preferences:
        return None

    preference = str(user_preferences.get("collaboration_preference", "")).strip().lower()
    if preference in {"hands_on", "guided"}:
        return preference
    return None


def apply_response_style(message: str, style: str | None) -> str:
    if not message or not style:
        return message

    if style == "concise":
        return _to_concise(message)

    if style == "structured":
        return _to_structured(message)

    return message


def _to_concise(message: str) -> str:
    normalized = " ".join(message.split())
    sentence_match = re.search(r"^(.+?[.!?])(?:\s|$)", normalized)
    if sentence_match:
        return sentence_match.group(1).strip()

    if len(normalized) <= 120:
        return normalized

    truncated = normalized[:117].rstrip()
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    return truncated.rstrip(" ,;:-") + "..."


def _to_structured(message: str) -> str:
    normalized = " ".join(message.split())
    if normalized.startswith("- "):
        return normalized

    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", normalized)
        if sentence.strip()
    ]
    if len(sentences) < 2:
        return normalized

    return "\n".join(f"- {sentence}" for sentence in sentences[:3])
