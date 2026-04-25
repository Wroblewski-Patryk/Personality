from app.core.adaptive_policy import (
    PREFERRED_ROLE_CONFIDENCE_MIN,
    PROACTIVE_ATTENTION_RECENT_OUTBOUND_LIMIT,
    PROACTIVE_ATTENTION_UNANSWERED_LIMIT,
    RELATION_CONFIDENCE_MIN,
    ROLE_COLLABORATION_RELATION_CONFIDENCE_MIN,
    THETA_DOMINANT_BIAS_MIN,
    dominant_theta_channel,
    is_role_adaptive_tie_break_turn,
    proactive_attention_limits,
    proactive_interruption_adjustment,
    proactive_relevance_adjustment,
    relation_value,
    should_apply_motivation_adaptive_tie_break,
    preferred_role_allowed,
)


def test_relation_value_respects_default_and_override_confidence_thresholds() -> None:
    relations = [
        {
            "relation_type": "collaboration_dynamic",
            "relation_value": "guided",
            "confidence": RELATION_CONFIDENCE_MIN + 0.01,
        },
    ]

    assert relation_value(relations=relations, relation_type="collaboration_dynamic") == "guided"
    assert (
        relation_value(
            relations=relations,
            relation_type="collaboration_dynamic",
            min_confidence=ROLE_COLLABORATION_RELATION_CONFIDENCE_MIN,
        )
        is None
    )


def test_preferred_role_allowed_requires_supported_role_and_documented_confidence() -> None:
    allowed_roles = {"friend", "analyst", "executor", "mentor"}

    assert (
        preferred_role_allowed(
            preferred_role="analyst",
            preferred_role_confidence=PREFERRED_ROLE_CONFIDENCE_MIN,
            allowed_roles=allowed_roles,
        )
        is True
    )
    assert (
        preferred_role_allowed(
            preferred_role="advisor",
            preferred_role_confidence=0.95,
            allowed_roles=allowed_roles,
        )
        is False
    )
    assert (
        preferred_role_allowed(
            preferred_role="mentor",
            preferred_role_confidence=PREFERRED_ROLE_CONFIDENCE_MIN - 0.01,
            allowed_roles=allowed_roles,
        )
        is False
    )


def test_dominant_theta_channel_uses_documented_threshold() -> None:
    assert (
        dominant_theta_channel(
            {
                "support_bias": THETA_DOMINANT_BIAS_MIN - 0.01,
                "analysis_bias": 0.2,
                "execution_bias": 0.1,
            }
        )
        is None
    )
    assert (
        dominant_theta_channel(
            {
                "support_bias": 0.2,
                "analysis_bias": THETA_DOMINANT_BIAS_MIN + 0.01,
                "execution_bias": 0.3,
            }
        )
        == "analysis"
    )


def test_role_adaptive_tie_break_turn_matches_documented_ambiguous_posture() -> None:
    assert (
        is_role_adaptive_tie_break_turn(
            event_type="question",
            intent="share_information",
            topic="implementation",
        )
        is True
    )
    assert (
        is_role_adaptive_tie_break_turn(
            event_type="statement",
            intent="share_information",
            topic="implementation",
        )
        is False
    )


def test_motivation_adaptive_tie_break_requires_ambiguous_turn_and_no_stronger_signal() -> None:
    assert (
        should_apply_motivation_adaptive_tie_break(
            intent="request_help",
            topic="general",
            is_brief_turn=True,
            has_positive_signal=False,
            has_emotional_signal=False,
            has_execution_signal=False,
            has_analysis_signal=False,
        )
        is True
    )
    assert (
        should_apply_motivation_adaptive_tie_break(
            intent="request_help",
            topic="general",
            is_brief_turn=True,
            has_positive_signal=False,
            has_emotional_signal=False,
            has_execution_signal=True,
            has_analysis_signal=False,
        )
        is False
    )


def test_proactive_relevance_adjustment_uses_relation_and_theta_policy_context() -> None:
    baseline = proactive_relevance_adjustment(
        trigger="task_blocked",
        relations=[],
        theta=None,
    )
    adaptive = proactive_relevance_adjustment(
        trigger="task_blocked",
        relations=[
            {
                "relation_type": "collaboration_dynamic",
                "relation_value": "hands_on",
                "confidence": 0.79,
            },
            {
                "relation_type": "delivery_reliability",
                "relation_value": "high_trust",
                "confidence": 0.74,
            },
        ],
        theta={
            "support_bias": 0.1,
            "analysis_bias": 0.2,
            "execution_bias": 0.72,
        },
    )

    assert baseline == 0.0
    assert adaptive >= 0.1


def test_proactive_relevance_adjustment_can_reduce_low_trust_outreach_relevance() -> None:
    adjusted = proactive_relevance_adjustment(
        trigger="relation_nudge",
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "low_trust",
                "confidence": 0.79,
            }
        ],
        theta=None,
    )

    assert adjusted < 0.0


def test_proactive_interruption_adjustment_is_higher_for_low_trust_than_high_trust() -> None:
    high_trust = proactive_interruption_adjustment(
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "high_trust",
                "confidence": 0.79,
            }
        ],
        theta=None,
    )
    low_trust = proactive_interruption_adjustment(
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "low_trust",
                "confidence": 0.79,
            }
        ],
        theta=None,
    )

    assert high_trust < 0.0
    assert low_trust > 0.0


def test_proactive_attention_limits_only_tighten_guardrails() -> None:
    baseline = proactive_attention_limits(relations=[], theta=None)
    adaptive = proactive_attention_limits(
        relations=[
            {
                "relation_type": "support_intensity_preference",
                "relation_value": "high_support",
                "confidence": 0.76,
            }
        ],
        theta={
            "support_bias": 0.7,
            "analysis_bias": 0.2,
            "execution_bias": 0.1,
        },
    )

    assert baseline["recent_outbound_limit"] == PROACTIVE_ATTENTION_RECENT_OUTBOUND_LIMIT
    assert baseline["unanswered_proactive_limit"] == PROACTIVE_ATTENTION_UNANSWERED_LIMIT
    assert adaptive["recent_outbound_limit"] <= PROACTIVE_ATTENTION_RECENT_OUTBOUND_LIMIT
    assert adaptive["unanswered_proactive_limit"] <= PROACTIVE_ATTENTION_UNANSWERED_LIMIT
    assert adaptive["unanswered_proactive_limit"] == 1


def test_proactive_attention_limits_are_strictest_for_low_trust_delivery() -> None:
    adaptive = proactive_attention_limits(
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "low_trust",
                "confidence": 0.81,
            }
        ],
        theta=None,
    )

    assert adaptive["recent_outbound_limit"] == 1
    assert adaptive["unanswered_proactive_limit"] == 1
