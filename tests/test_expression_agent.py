from datetime import datetime, timezone

from app.core.contracts import ContextOutput, Event, EventMeta, MotivationOutput, PlanOutput, RoleOutput
from app.expression.generator import ExpressionAgent


class NoReplyOpenAI:
    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        role_name: str,
        plan_goal: str,
        motivation_mode: str,
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
        plan_goal: str,
        motivation_mode: str,
    ) -> str | None:
        self.calls.append(
            {
                "user_text": user_text,
                "context_summary": context_summary,
                "role_name": role_name,
                "plan_goal": plan_goal,
                "motivation_mode": motivation_mode,
            }
        )
        return "OpenAI response"


def _event() -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "hello"},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _emotional_event() -> Event:
    return Event(
        event_id="evt-2",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "I feel stressed and overwhelmed"},
        meta=EventMeta(user_id="u-1", trace_id="t-2"),
    )


def _polish_event(text: str = "zrób plan wdrożenia") -> Event:
    return Event(
        event_id="evt-3",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-3"),
    )


def _context() -> ContextOutput:
    return ContextOutput(summary="ctx", related_goals=[], related_tags=["general"], risk_level=0.1)


def _motivation() -> MotivationOutput:
    return MotivationOutput(
        importance=0.5,
        urgency=0.2,
        valence=0.1,
        arousal=0.4,
        mode="respond",
    )


def _support_motivation() -> MotivationOutput:
    return MotivationOutput(
        importance=0.8,
        urgency=0.5,
        valence=-0.4,
        arousal=0.7,
        mode="support",
    )


def _plan() -> PlanOutput:
    return PlanOutput(goal="reply", steps=["reply"], needs_action=False, needs_response=True)


def _role() -> RoleOutput:
    return RoleOutput(selected="advisor", confidence=0.8)


async def test_expression_falls_back_to_echo() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(_event(), _context(), _plan(), _role(), _motivation())
    assert result.message == "I'm here and ready to help. reply"


async def test_expression_uses_supportive_fallback_for_emotional_messages() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _emotional_event(),
        _context(),
        _plan(),
        RoleOutput(selected="friend", confidence=0.8),
        _support_motivation(),
    )

    assert "one step at a time" in result.message


async def test_expression_uses_polish_fallback_for_polish_input() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _polish_event(),
        _context(),
        _plan(),
        RoleOutput(selected="executor", confidence=0.8),
        MotivationOutput(
            importance=0.8,
            urgency=0.8,
            valence=0.0,
            arousal=0.7,
            mode="execute",
        ),
    )

    assert result.message.startswith("Jasne, lecimy z tym.")


async def test_expression_uses_openai_when_available() -> None:
    openai = ReplyOpenAI()
    agent = ExpressionAgent(openai_client=openai)
    result = await agent.run(_event(), _context(), _plan(), _role(), _motivation())
    assert result.message == "OpenAI response"
    assert openai.calls == [
        {
            "user_text": "hello",
            "context_summary": "ctx",
            "role_name": "advisor",
            "plan_goal": "reply",
            "motivation_mode": "respond",
        }
    ]
