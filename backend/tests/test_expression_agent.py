from datetime import datetime, timedelta, timezone

import pytest

from app.core.contracts import (
    AffectiveAssessmentOutput,
    ContextOutput,
    Event,
    EventMeta,
    IdentityOutput,
    MotivationOutput,
    PerceptionOutput,
    PlanOutput,
    RoleOutput,
)
from app.expression.generator import ExpressionAgent
from tests.empathy_fixtures import EMPATHY_SUPPORT_SCENARIOS


class NoReplyOpenAI:
    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        foreground_awareness_summary: str,
        role_name: str,
        response_language: str,
        response_style: str | None,
        plan_goal: str,
        motivation_mode: str,
        response_tone: str,
        collaboration_preference: str | None,
        communication_boundary_summary: str = "",
        identity_summary: str = "",
        current_turn_timestamp: str = "",
    ) -> str | None:
        return None


class ReplyOpenAI:
    def __init__(self):
        self.calls: list[dict[str, str]] = []

    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        foreground_awareness_summary: str,
        role_name: str,
        response_language: str,
        response_style: str | None,
        plan_goal: str,
        motivation_mode: str,
        response_tone: str,
        collaboration_preference: str | None,
        communication_boundary_summary: str = "",
        identity_summary: str = "",
        current_turn_timestamp: str = "",
    ) -> str | None:
        self.calls.append(
            {
                "user_text": user_text,
                "context_summary": context_summary,
                "foreground_awareness_summary": foreground_awareness_summary,
                "role_name": role_name,
                "response_language": response_language,
                "response_style": response_style or "",
                "plan_goal": plan_goal,
                "motivation_mode": motivation_mode,
                "response_tone": response_tone,
                "collaboration_preference": collaboration_preference or "",
                "communication_boundary_summary": communication_boundary_summary,
                "identity_summary": identity_summary,
                "current_turn_timestamp": current_turn_timestamp,
            }
        )
        return "OpenAI response"


class GreetingOpenAI(ReplyOpenAI):
    async def generate_reply(self, *args, **kwargs) -> str | None:
        await super().generate_reply(*args, **kwargs)
        return "Czesc Patryk! Jasne, przechodze do konkretu."


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
    return ContextOutput(
        summary="ctx",
        related_goals=[],
        related_tags=["general"],
        risk_level=0.1,
        foreground_awareness_summary="Current turn timestamp: 2026-04-25T21:22:00+00:00.",
    )


def _perception(language: str = "en", affective: AffectiveAssessmentOutput | None = None) -> PerceptionOutput:
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
        affective=affective or AffectiveAssessmentOutput(),
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


def _identity() -> IdentityOutput:
    return IdentityOutput(
        mission="Help the user move forward with clear, constructive support.",
        values=["clarity", "continuity", "constructiveness"],
        behavioral_style=["direct", "supportive", "analytical"],
        boundaries=["do_not_fake_capabilities"],
        preferred_language="en",
        response_style=None,
        collaboration_preference=None,
        theta_orientation=None,
        summary="Mission: help the user move forward with clear, constructive support. Core style: direct, supportive, analytical.",
    )


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
        _motivation(mode="respond"),
        user_preferences={"response_style": "concise"},
    )

    assert result.message == "That sounds heavy."


async def test_expression_uses_supportive_fallback_for_affective_support_signal() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _event("Status update for today"),
        _perception(
            language="en",
            affective=AffectiveAssessmentOutput(
                affect_label="support_distress",
                intensity=0.7,
                needs_support=True,
                confidence=0.72,
                source="ai_classifier",
                evidence=["stressed", "overwhelmed"],
            ),
        ),
        _context(),
        _plan(),
        _role(selected="advisor"),
        _motivation(mode="respond"),
    )

    assert "one step at a time" in result.message
    assert result.language == "en"
    assert result.tone == "supportive"


async def test_expression_uses_supportive_tone_when_relation_prefers_high_support() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _event("Status update for today"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(selected="advisor"),
        _motivation(mode="respond"),
        relations=[
            {
                "relation_type": "support_intensity_preference",
                "relation_value": "high_support",
                "confidence": 0.76,
            }
        ],
    )

    assert "one step at a time" in result.message
    assert result.tone == "supportive"


async def test_expression_ignores_low_confidence_high_support_relation_signal() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _event("Execute deployment checklist"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(selected="executor"),
        _motivation(mode="execute"),
        relations=[
            {
                "relation_type": "support_intensity_preference",
                "relation_value": "high_support",
                "confidence": 0.67,
            }
        ],
    )

    assert result.tone == "action-oriented"


@pytest.mark.parametrize("scenario", EMPATHY_SUPPORT_SCENARIOS, ids=lambda scenario: scenario.key)
async def test_expression_uses_supportive_fallback_for_empathy_regression_scenarios(scenario) -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _event(scenario.text),
        _perception(language="en", affective=scenario.affective()),
        _context(),
        _plan(),
        _role(selected="advisor"),
        _motivation(mode="respond"),
    )

    assert "one step at a time" in result.message
    assert result.tone == "supportive"


async def test_expression_keeps_supportive_tone_from_negative_valence_without_support_mode() -> None:
    agent = ExpressionAgent(openai_client=NoReplyOpenAI())
    result = await agent.run(
        _event("I feel anxious and lonely"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(selected="advisor"),
        MotivationOutput(
            importance=0.6,
            urgency=0.2,
            valence=-0.45,
            arousal=0.55,
            mode="respond",
        ),
    )

    assert "one step at a time" in result.message
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
            "foreground_awareness_summary": "Current turn timestamp: 2026-04-25T21:22:00+00:00.",
            "role_name": "advisor",
            "response_language": "en",
            "response_style": "",
            "plan_goal": "reply",
            "motivation_mode": "respond",
            "response_tone": "supportive",
            "collaboration_preference": "",
            "communication_boundary_summary": "",
            "identity_summary": "",
            "current_turn_timestamp": openai.calls[0]["current_turn_timestamp"],
        }
    ]


async def test_expression_passes_communication_boundary_summary_to_openai() -> None:
    openai = ReplyOpenAI()
    agent = ExpressionAgent(openai_client=openai)
    await agent.run(
        _event("hello"),
        _perception(language="pl"),
        _context(),
        _plan(),
        _role(),
        _motivation(),
        relations=[
            {
                "relation_type": "interaction_ritual_preference",
                "relation_value": "avoid_repeated_greeting",
                "confidence": 0.96,
            }
        ],
    )

    assert "avoid greeting" in openai.calls[0]["communication_boundary_summary"]


async def test_expression_removes_repeated_greeting_when_relation_requests_it() -> None:
    agent = ExpressionAgent(openai_client=GreetingOpenAI())
    result = await agent.run(
        _event("hello"),
        _perception(language="pl"),
        _context(),
        _plan(),
        _role(),
        _motivation(),
        relations=[
            {
                "relation_type": "interaction_ritual_preference",
                "relation_value": "avoid_repeated_greeting",
                "confidence": 0.96,
            }
        ],
    )

    assert result.message == "Jasne, przechodze do konkretu."


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


async def test_expression_passes_identity_summary_to_openai() -> None:
    openai = ReplyOpenAI()
    agent = ExpressionAgent(openai_client=openai)
    await agent.run(
        _event("hello"),
        _perception(language="en"),
        _context(),
        _plan(),
        _role(),
        _motivation(),
        identity=_identity(),
    )

    assert "constructive support" in openai.calls[0]["identity_summary"]


async def test_expression_answers_name_question_from_identity_display_name() -> None:
    agent = ExpressionAgent(openai_client=ReplyOpenAI())
    result = await agent.run(
        _event("jak sie nazywam?"),
        _perception(language="pl"),
        _context(),
        _plan(),
        _role(),
        _motivation(),
        identity=_identity().model_copy(update={"display_name": "Patryk"}),
    )

    assert result.message == "Nazywasz sie Patryk."


async def test_expression_answers_time_question_from_event_timestamp() -> None:
    agent = ExpressionAgent(openai_client=ReplyOpenAI())
    event = _event("ktora godzina?")
    event = event.model_copy(
        update={
            "timestamp": datetime(
                2026,
                4,
                25,
                23,
                22,
                tzinfo=timezone(timedelta(hours=2), name="UTC+02:00"),
            )
        }
    )
    result = await agent.run(
        event,
        _perception(language="pl"),
        _context(),
        _plan(),
        _role(),
        _motivation(),
    )

    assert result.message == "W czasie tego turnu jest 2026-04-25 23:22:00 UTC+02:00."
