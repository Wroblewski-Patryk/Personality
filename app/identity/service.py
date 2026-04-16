from app.core.contracts import IdentityOutput


class IdentityService:
    CORE_MISSION = "Help the user move forward with clear, constructive support."
    CORE_VALUES = ["clarity", "continuity", "constructiveness"]
    CORE_STYLE = ["direct", "supportive", "analytical"]
    CORE_BOUNDARIES = [
        "do_not_fake_capabilities",
        "respect_runtime_truth",
        "prefer_small_concrete_next_steps",
    ]

    def build(
        self,
        *,
        user_profile: dict | None = None,
        user_preferences: dict | None = None,
        user_theta: dict | None = None,
    ) -> IdentityOutput:
        preferred_language = self._clean(user_profile, "preferred_language")
        response_style = self._clean(user_preferences, "response_style")
        collaboration_preference = self._clean(user_preferences, "collaboration_preference")
        theta_orientation = self._theta_orientation(user_theta)

        return IdentityOutput(
            mission=self.CORE_MISSION,
            values=list(self.CORE_VALUES),
            behavioral_style=list(self.CORE_STYLE),
            boundaries=list(self.CORE_BOUNDARIES),
            preferred_language=preferred_language,
            response_style=response_style,
            collaboration_preference=collaboration_preference,
            theta_orientation=theta_orientation,
            summary=self._summary(
                preferred_language=preferred_language,
                response_style=response_style,
                collaboration_preference=collaboration_preference,
                theta_orientation=theta_orientation,
            ),
        )

    def _clean(self, payload: dict | None, key: str) -> str | None:
        if not payload:
            return None
        value = str(payload.get(key, "")).strip().lower()
        return value or None

    def _theta_orientation(self, user_theta: dict | None) -> str | None:
        if not user_theta:
            return None

        candidates = {
            "support": float(user_theta.get("support_bias", 0.0) or 0.0),
            "analysis": float(user_theta.get("analysis_bias", 0.0) or 0.0),
            "execution": float(user_theta.get("execution_bias", 0.0) or 0.0),
        }
        orientation, bias = max(candidates.items(), key=lambda item: item[1])
        if bias < 0.58:
            return None
        return orientation

    def _summary(
        self,
        *,
        preferred_language: str | None,
        response_style: str | None,
        collaboration_preference: str | None,
        theta_orientation: str | None,
    ) -> str:
        parts = [
            "Mission: help the user move forward with clear, constructive support.",
            "Core style: direct, supportive, analytical.",
        ]
        if preferred_language:
            parts.append(f"Preferred language context: {preferred_language}.")
        if response_style:
            parts.append(f"Response style preference: {response_style}.")
        if collaboration_preference:
            parts.append(f"Collaboration preference: {collaboration_preference}.")
        if theta_orientation:
            parts.append(f"Current adaptive emphasis: {theta_orientation}.")
        return " ".join(parts)
