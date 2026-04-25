from app.utils.preferences import (
    apply_response_style,
    detect_response_style_preference,
    preferred_response_style,
)


def test_detect_response_style_preference_finds_concise_request() -> None:
    result = detect_response_style_preference("Please answer briefly from now on.")

    assert result is not None
    assert result.style == "concise"
    assert result.source == "explicit_request"


def test_detect_response_style_preference_finds_structured_request() -> None:
    result = detect_response_style_preference("Reply in bullet points, please.")

    assert result is not None
    assert result.style == "structured"


def test_preferred_response_style_reads_supported_value() -> None:
    assert preferred_response_style({"response_style": "structured"}) == "structured"
    assert preferred_response_style({"response_style": "unknown"}) is None


def test_apply_response_style_shortens_concise_message() -> None:
    message = "That sounds heavy. Let's take it one step at a time. Tell me what feels most pressing."

    assert apply_response_style(message, "concise") == "That sounds heavy."


def test_apply_response_style_structures_multi_sentence_message() -> None:
    message = "Start with the current state. Then name the blocker. Finally choose one next step."

    assert apply_response_style(message, "structured") == (
        "- Start with the current state.\n"
        "- Then name the blocker.\n"
        "- Finally choose one next step."
    )
