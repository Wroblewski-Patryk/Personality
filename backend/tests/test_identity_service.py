from app.identity.service import IdentityService


def test_identity_service_builds_stable_core_and_runtime_preferences() -> None:
    identity = IdentityService().build(
        user_profile={"preferred_language": "pl"},
        auth_user={"display_name": "Patryk"},
        user_preferences={
            "response_style": "structured",
            "collaboration_preference": "guided",
        },
        user_theta={
            "support_bias": 0.12,
            "analysis_bias": 0.71,
            "execution_bias": 0.17,
        },
    )

    assert identity.mission == "Help the user move forward with clear, constructive support."
    assert identity.values == ["clarity", "continuity", "constructiveness"]
    assert identity.behavioral_style == ["direct", "supportive", "analytical"]
    assert identity.display_name == "Patryk"
    assert identity.preferred_language == "pl"
    assert identity.response_style == "structured"
    assert identity.collaboration_preference == "guided"
    assert identity.theta_orientation == "analysis"
    assert "Known user display name: Patryk." in identity.summary
    assert "Preferred language context: pl." in identity.summary
    assert "Response style preference: structured." in identity.summary
    assert "Collaboration preference: guided." in identity.summary
    assert "Current adaptive emphasis: analysis." in identity.summary
