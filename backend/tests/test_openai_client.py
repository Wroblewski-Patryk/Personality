from types import SimpleNamespace

from app.integrations.openai.client import OpenAIClient


class _FakeResponses:
    def __init__(self, output_text: str | None):
        self.output_text = output_text

    async def create(self, **kwargs):  # noqa: ANN003
        return SimpleNamespace(output_text=self.output_text)


class _FakeClient:
    def __init__(self, output_text: str | None):
        self.responses = _FakeResponses(output_text=output_text)


async def test_openai_client_classify_affective_state_accepts_valid_structured_payload() -> None:
    client = OpenAIClient(api_key=None, model="gpt-test")
    client.client = _FakeClient(
        output_text=(
            '{"affect_label":"support_distress","intensity":0.78,'
            '"needs_support":true,"confidence":0.74,"evidence":["overwhelmed"]}'
        )
    )

    result = await client.classify_affective_state(
        user_text="I feel overwhelmed",
        response_language="en",
    )

    assert isinstance(result, dict)
    assert result["affect_label"] == "support_distress"
    assert result["needs_support"] is True
    assert result["evidence"] == ["overwhelmed"]


async def test_openai_client_classify_affective_state_extracts_json_object_from_wrapped_text() -> None:
    client = OpenAIClient(api_key=None, model="gpt-test")
    client.client = _FakeClient(
        output_text=(
            "```json\n"
            '{"affect_label":"neutral","intensity":0.11,"needs_support":false,'
            '"confidence":0.67,"evidence":[]}\n'
            "```"
        )
    )

    result = await client.classify_affective_state(
        user_text="hello",
        response_language="en",
    )

    assert isinstance(result, dict)
    assert result["affect_label"] == "neutral"
    assert result["needs_support"] is False


async def test_openai_client_classify_affective_state_returns_diagnostic_when_schema_keys_are_missing() -> None:
    client = OpenAIClient(api_key=None, model="gpt-test")
    client.client = _FakeClient(output_text='{"affect_label":"neutral"}')

    result = await client.classify_affective_state(
        user_text="hello",
        response_language="en",
    )

    assert result == {
        OpenAIClient.AFFECTIVE_FALLBACK_REASON_FIELD: "openai_affective_schema_missing_keys"
    }


async def test_openai_client_classify_affective_state_returns_diagnostic_when_schema_type_is_invalid() -> None:
    client = OpenAIClient(api_key=None, model="gpt-test")
    client.client = _FakeClient(
        output_text=(
            '{"affect_label":"neutral","intensity":"0.3","needs_support":"false",'
            '"confidence":0.67,"evidence":[]}'
        )
    )

    result = await client.classify_affective_state(
        user_text="hello",
        response_language="en",
    )

    assert result == {
        OpenAIClient.AFFECTIVE_FALLBACK_REASON_FIELD: "openai_affective_schema_invalid_needs_support_type"
    }


async def test_openai_client_classify_affective_state_returns_diagnostic_when_parse_fails() -> None:
    client = OpenAIClient(api_key=None, model="gpt-test")
    client.client = _FakeClient(output_text="not-json")

    result = await client.classify_affective_state(
        user_text="hello",
        response_language="en",
    )

    assert result == {
        OpenAIClient.AFFECTIVE_FALLBACK_REASON_FIELD: "openai_affective_parse_failed"
    }
