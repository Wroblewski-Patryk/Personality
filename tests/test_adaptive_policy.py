from app.core.adaptive_policy import (
    PREFERRED_ROLE_CONFIDENCE_MIN,
    RELATION_CONFIDENCE_MIN,
    ROLE_COLLABORATION_RELATION_CONFIDENCE_MIN,
    THETA_DOMINANT_BIAS_MIN,
    dominant_theta_channel,
    is_role_adaptive_tie_break_turn,
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
