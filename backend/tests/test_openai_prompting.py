from app.integrations.openai.prompting import OpenAIPromptBuilder


class _FakeMessage:
    def __init__(self, message_type: str, content: str):
        self.type = message_type
        self.content = content


class _FakeRenderedPrompt:
    def __init__(self, messages):
        self.messages = messages


class _FakeChatPromptTemplate:
    def __init__(self, messages):
        self.messages = messages

    @classmethod
    def from_messages(cls, messages):
        return cls(messages)

    def invoke(self, variables):
        rendered = []
        for role, template in self.messages:
            content = template.format(**variables)
            message_type = "human" if role == "human" else role
            rendered.append(_FakeMessage(message_type=message_type, content=content))
        return _FakeRenderedPrompt(rendered)


def test_openai_prompt_builder_fallback_without_langchain() -> None:
    builder = OpenAIPromptBuilder()
    builder.langchain_available = False

    messages = builder.build_reply_messages(
        user_text="hello",
        context_summary="ctx",
        role_name="advisor",
        response_language="en",
        response_style="concise",
        plan_goal="reply",
        motivation_mode="respond",
        response_tone="supportive",
        collaboration_preference="guided",
        identity_summary="helpful and clear",
    )

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "advisor" in messages[0]["content"]
    assert "English" in messages[0]["content"]
    assert messages[1] == {
        "role": "user",
        "content": "Context: ctx\n\nUser message: hello",
    }


def test_openai_prompt_builder_uses_langchain_template_when_available(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.integrations.openai.prompting.ChatPromptTemplate",
        _FakeChatPromptTemplate,
    )
    builder = OpenAIPromptBuilder()
    builder.langchain_available = True

    messages = builder.build_affective_messages(
        user_text="I feel overwhelmed",
        response_language="en",
    )

    assert messages[0]["role"] == "system"
    assert "affect_label" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "Preferred response language context: English." in messages[1]["content"]
    assert "I feel overwhelmed" in messages[1]["content"]
