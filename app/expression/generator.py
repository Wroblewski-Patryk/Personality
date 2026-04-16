from app.core.contracts import (
    ContextOutput,
    Event,
    ExpressionOutput,
    IdentityOutput,
    MotivationOutput,
    PerceptionOutput,
    PlanOutput,
    RoleOutput,
)
from app.integrations.openai.client import OpenAIClient
from app.utils.language import fallback_message
from app.utils.preferences import (
    apply_response_style,
    preferred_collaboration_preference,
    preferred_response_style,
)


class ExpressionAgent:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    async def run(
        self,
        event: Event,
        perception: PerceptionOutput,
        context: ContextOutput,
        plan: PlanOutput,
        role: RoleOutput,
        motivation: MotivationOutput,
        identity: IdentityOutput | None = None,
        user_preferences: dict | None = None,
        theta: dict | None = None,
    ) -> ExpressionOutput:
        text = str(event.payload.get("text", "")).strip()
        response_style = preferred_response_style(user_preferences)
        collaboration_preference = preferred_collaboration_preference(user_preferences)
        tone = self._select_tone(
            motivation=motivation,
            role=role,
            theta=theta,
            collaboration_preference=collaboration_preference,
        )
        message: str
        if not text:
            message = self._build_fallback_message(
                perception=perception,
                context=context,
                plan=plan,
                role=role,
                motivation=motivation,
                response_style=response_style,
                theta=theta,
                collaboration_preference=collaboration_preference,
            )
        else:
            llm_reply = await self.openai_client.generate_reply(
                user_text=text,
                context_summary=context.summary,
                role_name=role.selected,
                response_language=perception.language,
                response_style=response_style,
                plan_goal=plan.goal,
                motivation_mode=motivation.mode,
                response_tone=tone,
                collaboration_preference=collaboration_preference,
                identity_summary=identity.summary if identity is not None else "",
            )
            message = llm_reply or self._build_fallback_message(
                perception=perception,
                context=context,
                plan=plan,
                role=role,
                motivation=motivation,
                response_style=response_style,
                theta=theta,
                collaboration_preference=collaboration_preference,
            )

        channel = "telegram" if event.source == "telegram" else "api"
        return ExpressionOutput(
            message=message,
            tone=tone,
            channel=channel,
            language=perception.language,
        )

    def _build_fallback_message(
        self,
        perception: PerceptionOutput,
        context: ContextOutput,
        plan: PlanOutput,
        role: RoleOutput,
        motivation: MotivationOutput,
        response_style: str | None = None,
        theta: dict | None = None,
        collaboration_preference: str | None = None,
    ) -> str:
        if motivation.mode == "clarify":
            return apply_response_style(
                fallback_message(perception.language, "clarify", plan.goal),
                response_style,
            )

        if motivation.mode == "support" or role.selected == "friend":
            return apply_response_style(
                fallback_message(perception.language, "support", plan.goal),
                response_style,
            )

        if motivation.mode == "execute" or role.selected == "executor":
            return apply_response_style(
                fallback_message(perception.language, "execute", plan.goal),
                response_style,
            )

        if motivation.mode == "analyze" or role.selected == "analyst":
            return apply_response_style(
                fallback_message(perception.language, "analyze", plan.goal),
                response_style,
            )

        if role.selected == "mentor":
            return apply_response_style(
                fallback_message(perception.language, "mentor", plan.goal),
                response_style,
            )

        if "Relevant recent memory:" in context.summary:
            return apply_response_style(
                fallback_message(perception.language, "memory", plan.goal),
                response_style,
            )

        collaboration_key = self._collaboration_fallback_key(collaboration_preference)
        if collaboration_key is not None:
            return apply_response_style(
                fallback_message(perception.language, collaboration_key, plan.goal),
                response_style,
            )

        theta_key = self._theta_fallback_key(theta)
        if theta_key is not None:
            return apply_response_style(
                fallback_message(perception.language, theta_key, plan.goal),
                response_style,
            )

        return apply_response_style(
            fallback_message(perception.language, "default", plan.goal),
            response_style,
        )

    def _select_tone(
        self,
        motivation: MotivationOutput,
        role: RoleOutput,
        theta: dict | None = None,
        collaboration_preference: str | None = None,
    ) -> str:
        if motivation.mode == "support" or role.selected == "friend":
            return "supportive"
        if motivation.mode == "execute" or role.selected == "executor":
            return "action-oriented"
        collaboration_tone = self._collaboration_tone(
            collaboration_preference=collaboration_preference,
            motivation=motivation,
            role=role,
        )
        if collaboration_tone is not None:
            return collaboration_tone
        if motivation.mode == "analyze" or role.selected == "analyst":
            return "analytical"
        if role.selected == "mentor":
            return "guiding"

        theta_key = self._theta_fallback_key(theta)
        if theta_key == "support":
            return "supportive"
        if theta_key == "execute":
            return "action-oriented"
        if theta_key == "analyze":
            return "analytical"
        return "supportive"

    def _theta_fallback_key(self, theta: dict | None) -> str | None:
        if not theta:
            return None

        candidates = {
            "support": float(theta.get("support_bias", 0.0) or 0.0),
            "analyze": float(theta.get("analysis_bias", 0.0) or 0.0),
            "execute": float(theta.get("execution_bias", 0.0) or 0.0),
        }
        key, bias = max(candidates.items(), key=lambda item: item[1])
        if bias < 0.58:
            return None
        return key

    def _collaboration_fallback_key(self, collaboration_preference: str | None) -> str | None:
        if collaboration_preference == "hands_on":
            return "execute"
        if collaboration_preference == "guided":
            return "mentor"
        return None

    def _collaboration_tone(
        self,
        collaboration_preference: str | None,
        motivation: MotivationOutput,
        role: RoleOutput,
    ) -> str | None:
        if collaboration_preference == "hands_on":
            if motivation.mode in {"respond", "analyze"} or role.selected in {"advisor", "analyst", "mentor"}:
                return "action-oriented"
            return "action-oriented"
        if collaboration_preference == "guided":
            if motivation.mode in {"respond", "analyze"} or role.selected in {"advisor", "analyst", "mentor"}:
                return "guiding"
            return "guiding"
        return None
