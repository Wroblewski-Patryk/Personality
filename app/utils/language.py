import re


POLISH_HINT_WORDS = {
    "czy",
    "jak",
    "co",
    "mozesz",
    "możesz",
    "pomoz",
    "pomóż",
    "prosze",
    "proszę",
    "dzieki",
    "dzięki",
    "zrob",
    "zrób",
    "robimy",
    "teraz",
    "potrzebuje",
    "potrzebuję",
}


def detect_language(text: str) -> str:
    lowered = text.lower()
    if any(char in lowered for char in "ąćęłńóśźż"):
        return "pl"

    tokens = set(re.findall(r"\b[\w-]+\b", lowered))
    if tokens.intersection(POLISH_HINT_WORDS):
        return "pl"

    return "en"
