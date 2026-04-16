from datetime import datetime, timezone

from app.core.contracts import (
    ContextOutput,
    Event,
    EventMeta,
    MotivationOutput,
    PerceptionOutput,
    PlanOutput,
    RoleOutput,
)
from app.expression.generator import ExpressionAgent


class NoReplyOpenAI:
    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        role_name: str,
        response_language: str,
        response_style: str | None,
        plan_goal: str,
        motivation_mode: str,
        response_tone: str,
        collaboration_preference: str | None,
    ) -> str | None:
        return None


class ReplyOpenAI:
    def __init__(self):
        self.calls: list[dict[str, str]] = []

    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        role_name: str,
        response_language: str,
        response_style: str | None,
        plan_goal: str,
        motivation_mode: str,
        response_tone: str,
        collaboration_preference: str | None,
    ) -> str | None:
        self.calls.append(
            {
                "user_text": user_text,
                "context_summary": context_summary,
                "role_name": role_name,
                "response_language": response_language,
                "response_style": response_style or "",
                "plan_goal": plan_goal,
                "motivation_mode": motivation_mode,
                "response_tone": response_tone,
                "collaboration_preference": collaboration_preference or "",
            }
        )
        return "OpenAI response"


def _event(text: str = "hello") -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _context() -> ContextOutput:
    return ContextOutput(summary="ctx", related_goals=[], related_tags=["general"], risk_level=0.1)


def _perception(language: str = "en") -> PerceptionOutput:
    return PerceptionOutput(
        event_type="statement",
        topic="general",
        topic_tags=["general"],
        intent="share_information",
        language=language,
        language_source="keyword_signal",
        language_confidence=0.8,
        ambiguity=0.1,
        initial_salience=0.5,
    )


def _motivation(mode: str = "respond") -> MotivationOutput:
    return MotivationOutput(
        importance=0.5,
        urgency=0.2,
        valence=0.1,
        arousal=0.4,
        mode=mode,
    )


def _plan() -> PlanOutput:
    return PlanOutput(goal="reply", steps=["reply"], needs_action=False, needs_response=True)


def _role(selected: str = "advisor") -> RoleOutput:
    return RoleOutput(selected=selected, confidence=0.8)


async def test_expression_uses_runtime_language_for_fallback() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _event("ok"),
        _perception(language="pl"),
        _context(),
        _plan(),
        _role(selected="executor"),
        _motivation(mode="execute"),
    )

    assert result.message.startswith("Jasne, lecimy z tym.")
    assert result.language == "pl"
    assert result.tone == "action-oriented"


async def test_expression_applies_concise_preference_to_fallback() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _event("I feel stressed and overwhelmed"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(selected="friend"),
        _motivation(mode="support"),
        user_preferences={"response_style": "concise"},
    )

    assert result.message == "That sounds heavy."


async def test_expression_uses_supportive_fallback_for_emotional_messages() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _event("I feel stressed and overwhelmed"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(selected="friend"),
        _motivation(mode="support"),
    )

    assert "one step at a time" in result.message
    assert result.language == "en"
    assert result.tone == "supportive"


async def test_expression_uses_openai_when_available() -> None:
    openai = ReplyOpenAI()
    agent = ExpressionAgent(openai_client=openai)
    result = await agent.run(
        _event("hello"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(),
        _motivation(),
    )
    assert result.message == "OpenAI response"
    assert result.language == "en"
    assert result.tone == "supportive"
    assert openai.calls == [
        {
            "user_text": "hello",
            "context_summary": "ctx",
            "role_name": "advisor",
            "response_language": "en",
            "response_style": "",
            "plan_goal": "reply",
            "motivation_mode": "respond",
            "response_tone": "supportive",
            "collaboration_preference": "",
        }
    ]


async def test_expression_passes_structured_preference_to_openai() -> None:
    openai = ReplyOpenAI()
    agent = ExpressionAgent(openai_client=openai)
    await agent.run(
        _event("hello"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(),
        _motivation(),
        user_preferences={"response_style": "structured"},
    )

    assert openai.calls[0]["response_style"] == "structured"


async def test_expression_uses_theta_for_analytical_tone_and_fallback() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _event("help me"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(selected="advisor"),
        _motivation(mode="respond"),
        theta={
            "support_bias": 0.14,
            "analysis_bias": 0.72,
            "execution_bias": 0.14,
        },
    )

    assert "Let's break this down clearly." in result.message
    assert result.tone == "analytical"


async def test_expression_uses_guided_collaboration_preference_for_tone_and_fallback() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _event("help me"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(selected="advisor"),
        _motivation(mode="respond"),
        user_preferences={"collaboration_preference": "guided"},
    )

    assert "A good next move is to define the goal" in result.message
    assert result.tone == "guiding"


async def test_expression_passes_collaboration_preference_to_openai() -> None:
    openai = ReplyOpenAI()
    agent = ExpressionAgent(openai_client=openai)
    await agent.run(
        _event("hello"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(),
        _motivation(),
        user_preferences={"collaboration_preference": "hands_on"},
    )

    assert openai.calls[0]["collaboration_preference"] == "hands_on"
    assert openai.calls[0]["response_tone"] == "action-oriented"
