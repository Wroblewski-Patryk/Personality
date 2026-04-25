from app.core.contracts import (
    AffectiveAssessmentOutput,
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
from app.utils.language import fallback_message, normalize_for_matching
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
        relations: list[dict] | None = None,
    ) -> ExpressionOutput:
        text = str(event.payload.get("text", "")).strip()
        response_style = preferred_response_style(user_preferences)
        collaboration_preference = preferred_collaboration_preference(user_preferences)
        relation_support_intensity = self._relation_value(
            relations=relations or [],
            relation_type="support_intensity_preference",
            min_confidence=0.68,
        )
        tone = self._select_tone(
            affective=perception.affective,
            motivation=motivation,
            role=role,
            theta=theta,
            collaboration_preference=collaboration_preference,
            relation_support_intensity=relation_support_intensity,
        )
        message: str
        if not text:
            message = self._build_fallback_message(
                perception=perception,
                context=context,
                plan=plan,
                role=role,
                motivation=motivation,
                affective=perception.affective,
                response_style=response_style,
                theta=theta,
                collaboration_preference=collaboration_preference,
                relation_support_intensity=relation_support_intensity,
            )
        else:
            direct_reply = self._direct_foreground_reply(
                event=event,
                text=text,
                language=perception.language,
                identity=identity,
            )
            if direct_reply is not None:
                message = direct_reply
            else:
                llm_reply = await self.openai_client.generate_reply(
                    user_text=text,
                    context_summary=context.summary,
                    foreground_awareness_summary=context.foreground_awareness_summary,
                    role_name=role.selected,
                    response_language=perception.language,
                    response_style=response_style,
                    plan_goal=plan.goal,
                    motivation_mode=motivation.mode,
                    response_tone=tone,
                    collaboration_preference=collaboration_preference,
                    identity_summary=identity.summary if identity is not None else "",
                    current_turn_timestamp=event.timestamp.isoformat(),
                )
                message = llm_reply or self._build_fallback_message(
                    perception=perception,
                    context=context,
                    plan=plan,
                    role=role,
                    motivation=motivation,
                    affective=perception.affective,
                    response_style=response_style,
                    theta=theta,
                    collaboration_preference=collaboration_preference,
                    relation_support_intensity=relation_support_intensity,
                )
                if self._looks_like_false_capability_denial(message, context=context):
                    message = self._build_fallback_message(
                        perception=perception,
                        context=context,
                        plan=plan,
                role=role,
                motivation=motivation,
                affective=perception.affective,
                response_style=response_style,
                        theta=theta,
                        collaboration_preference=collaboration_preference,
                        relation_support_intensity=relation_support_intensity,
                    )

        if event.source == "telegram":
            channel = "telegram"
        elif event.source == "scheduler" and isinstance(event.payload.get("chat_id"), (int, str)):
            channel = "telegram"
        else:
            channel = "api"
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
        affective: AffectiveAssessmentOutput,
        response_style: str | None = None,
        theta: dict | None = None,
        collaboration_preference: str | None = None,
        relation_support_intensity: str | None = None,
    ) -> str:
        if motivation.mode == "clarify":
            return apply_response_style(
                fallback_message(perception.language, "clarify", plan.goal),
                response_style,
            )

        if (
            role.selected == "friend"
            or motivation.valence <= -0.3
            or self._needs_support(affective)
            or relation_support_intensity == "high_support"
        ):
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
        if context.memory_continuity_available:
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
        affective: AffectiveAssessmentOutput,
        motivation: MotivationOutput,
        role: RoleOutput,
        theta: dict | None = None,
        collaboration_preference: str | None = None,
        relation_support_intensity: str | None = None,
    ) -> str:
        if (
            role.selected == "friend"
            or motivation.valence <= -0.3
            or self._needs_support(affective)
            or relation_support_intensity == "high_support"
        ):
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

    def _needs_support(self, affective: AffectiveAssessmentOutput) -> bool:
        label = str(affective.affect_label).strip().lower()
        return bool(affective.needs_support) or label == "support_distress"

    def _direct_foreground_reply(
        self,
        *,
        event: Event,
        text: str,
        language: str,
        identity: IdentityOutput | None,
    ) -> str | None:
        normalized = normalize_for_matching(text)
        display_name = str((identity.display_name if identity is not None else "") or "").strip()
        if display_name and self._is_name_recall_question(normalized):
            if language == "pl":
                return f"Nazywasz sie {display_name}."
            return f"Your name is {display_name}."
        if self._is_time_question(normalized):
            return self._format_current_time_reply(event.timestamp, language=language)
        return None

    def _is_name_recall_question(self, normalized_text: str) -> bool:
        markers = (
            "jak sie nazywam",
            "pamietasz moje imie",
            "czy pamietasz moje imie",
            "what is my name",
            "do you know my name",
            "remember my name",
        )
        return any(marker in normalized_text for marker in markers)

    def _is_time_question(self, normalized_text: str) -> bool:
        markers = (
            "ktora godzina",
            "jaka jest godzina",
            "podaj godzine",
            "what time is it",
            "current time",
            "time is it",
        )
        return any(marker in normalized_text for marker in markers)

    def _format_current_time_reply(self, timestamp, *, language: str) -> str:
        exact = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z").strip()
        if language == "pl":
            return f"W czasie tego turnu jest {exact}."
        return f"For this turn, the current time is {exact}."

    def _looks_like_false_capability_denial(self, message: str, *, context: ContextOutput) -> bool:
        normalized = normalize_for_matching(message)
        denial_markers = (
            "i cannot remember",
            "i cant remember",
            "i do not have memory",
            "i don't have memory",
            "nie mam mozliwosci zapamietywania",
            "nie moge zapamietywac",
            "nie pamietam nic o tobie",
        )
        if not any(marker in normalized for marker in denial_markers):
            return False
        return context.memory_continuity_available or bool(context.known_user_name)

    def _relation_value(self, *, relations: list[dict], relation_type: str, min_confidence: float) -> str | None:
        for relation in relations:
            if str(relation.get("relation_type", "")).strip().lower() != relation_type:
                continue
            confidence = float(relation.get("confidence", 0.0) or 0.0)
            if confidence < min_confidence:
                continue
            value = str(relation.get("relation_value", "")).strip().lower()
            if value:
                return value
        return None
