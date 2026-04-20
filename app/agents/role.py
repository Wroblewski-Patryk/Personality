from app.core.adaptive_policy import (
    ROLE_COLLABORATION_RELATION_CONFIDENCE_MIN,
    dominant_theta_channel,
    is_role_adaptive_tie_break_turn,
    preferred_role_allowed,
    relation_value,
)
from app.core.contracts import ContextOutput, Event, PerceptionOutput, RoleOutput
from app.utils.language import normalize_for_matching


class RoleAgent:
    PREFERRED_ROLES = {"friend", "analyst", "executor", "mentor"}

    def run(
        self,
        event: Event,
        perception: PerceptionOutput,
        context: ContextOutput,
        user_preferences: dict | None = None,
        relations: list[dict] | None = None,
        theta: dict | None = None,
    ) -> RoleOutput:
        text = str(event.payload.get("text", "")).strip()
        lowered = normalize_for_matching(text)
        affective_label = str(perception.affective.affect_label).strip().lower()
        affective_needs_support = bool(perception.affective.needs_support)
        preferred_role = str((user_preferences or {}).get("preferred_role", "")).strip().lower()
        preferred_role_confidence = float((user_preferences or {}).get("preferred_role_confidence", 0.0) or 0.0)
        collaboration_preference = str((user_preferences or {}).get("collaboration_preference", "")).strip().lower()
        relation_collaboration = relation_value(
            relations=relations or [],
            relation_type="collaboration_dynamic",
            min_confidence=ROLE_COLLABORATION_RELATION_CONFIDENCE_MIN,
        )
        relation_support = relation_value(
            relations=relations or [],
            relation_type="support_intensity_preference",
        )
        is_help_turn = perception.event_type == "question" or perception.intent == "request_help"
        is_general_turn = perception.topic == "general"
        is_role_tie_break_turn = is_role_adaptive_tie_break_turn(
            event_type=perception.event_type,
            intent=perception.intent,
            topic=perception.topic,
        )

        analysis_keywords = {
            "analyze",
            "analysis",
            "review",
            "compare",
            "debug",
            "explain",
            "analiza",
            "przeanalizuj",
            "porownaj",
            "wyjasnij",
            "sprawdz",
            "zaplanuj",
        }
        executor_keywords = {
            "build",
            "create",
            "write",
            "fix",
            "implement",
            "add",
            "setup",
            "deploy",
            "zbuduj",
            "stworz",
            "napisz",
            "napraw",
            "wdroz",
            "dodaj",
            "skonfiguruj",
            "ustaw",
            "zrob",
        }

        if affective_needs_support or affective_label == "support_distress":
            return RoleOutput(selected="friend", confidence=0.74)
        if relation_support == "high_support" and perception.event_type == "question":
            return RoleOutput(selected="mentor", confidence=0.68)

        if perception.topic == "planning" or any(keyword in lowered for keyword in analysis_keywords):
            return RoleOutput(selected="analyst", confidence=0.82)

        if any(lowered.startswith(keyword) for keyword in executor_keywords):
            return RoleOutput(selected="executor", confidence=0.78)

        if preferred_role_allowed(
            preferred_role=preferred_role,
            preferred_role_confidence=preferred_role_confidence,
            allowed_roles=self.PREFERRED_ROLES,
        ):
            if is_help_turn:
                return RoleOutput(selected=preferred_role, confidence=0.73)
            if is_general_turn:
                return RoleOutput(selected=preferred_role, confidence=0.68)

        collaboration_role = self._collaboration_role(collaboration_preference)
        if collaboration_role is not None and is_role_tie_break_turn:
            if is_help_turn:
                return RoleOutput(selected=collaboration_role, confidence=0.71)
            if is_general_turn:
                return RoleOutput(selected=collaboration_role, confidence=0.66)

        relation_role = self._collaboration_role(relation_collaboration or "")
        if relation_role is not None and is_role_tie_break_turn:
            if is_help_turn:
                return RoleOutput(selected=relation_role, confidence=0.69)
            if is_general_turn:
                return RoleOutput(selected=relation_role, confidence=0.64)

        theta_role = self._theta_role(theta)
        if theta_role is not None and is_role_tie_break_turn:
            if is_help_turn:
                return RoleOutput(selected=theta_role, confidence=0.69)
            if is_general_turn:
                return RoleOutput(selected=theta_role, confidence=0.64)

        if is_help_turn:
            return RoleOutput(selected="mentor", confidence=0.71)

        if context.risk_level >= 0.5:
            return RoleOutput(selected="advisor", confidence=0.7)

        return RoleOutput(selected="advisor", confidence=0.6)

    def _theta_role(self, theta: dict | None) -> str | None:
        channel = dominant_theta_channel(theta)
        if channel is None:
            return None
        role_by_channel = {
            "support": "friend",
            "analysis": "analyst",
            "execution": "executor",
        }
        return role_by_channel.get(channel)

    def _collaboration_role(self, collaboration_preference: str) -> str | None:
        if collaboration_preference == "hands_on":
            return "executor"
        if collaboration_preference == "guided":
            return "mentor"
        return None
