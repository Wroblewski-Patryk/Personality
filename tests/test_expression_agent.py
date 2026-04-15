from datetime import datetime, timezone

from app.core.contracts import ContextOutput, Event, EventMeta, MotivationOutput, PlanOutput, RoleOutput
from app.expression.generator import ExpressionAgent


class NoReplyOpenAI:
    async def generate_reply(self, user_text: str, context_summary: str, role_name: str) -> str | None:
        return None


class ReplyOpenAI:
    async def generate_reply(self, user_text: str, context_summary: str, role_name: str) -> str | None:
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


def _plan() -> PlanOutput:
    return PlanOutput(goal="reply", steps=["reply"], needs_action=False, needs_response=True)


def _role() -> RoleOutput:
    return RoleOutput(selected="advisor", confidence=0.8)


async def test_expression_falls_back_to_echo() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(_event(), _context(), _plan(), _role(), _motivation())
    assert result.message.startswith("Echo")


async def test_expression_uses_openai_when_available() -> None:
    agent = ExpressionAgent(openai_client=ReplyOpenAI())
    result = await agent.run(_event(), _context(), _plan(), _role(), _motivation())
    assert result.message == "OpenAI response"
