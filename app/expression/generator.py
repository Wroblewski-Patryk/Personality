from app.core.contracts import (
    ContextOutput,
    Event,
    ExpressionOutput,
    MotivationOutput,
    PlanOutput,
    RoleOutput,
)
from app.integrations.openai.client import OpenAIClient
from app.utils.language import detect_language


class ExpressionAgent:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    async def run(
        self,
        event: Event,
        context: ContextOutput,
        plan: PlanOutput,
        role: RoleOutput,
        motivation: MotivationOutput,
    ) -> ExpressionOutput:
        text = str(event.payload.get("text", "")).strip()
        message: str
        if not text:
            message = self._build_fallback_message(
                text=text,
                context=context,
                plan=plan,
                role=role,
                motivation=motivation,
            )
        else:
            llm_reply = await self.openai_client.generate_reply(
                user_text=text,
                context_summary=context.summary,
                role_name=role.selected,
                plan_goal=plan.goal,
                motivation_mode=motivation.mode,
            )
            message = llm_reply or self._build_fallback_message(
                text=text,
                context=context,
                plan=plan,
                role=role,
                motivation=motivation,
            )

        channel = "telegram" if event.source == "telegram" else "api"
        return ExpressionOutput(message=message, tone="supportive", channel=channel)

    def _build_fallback_message(
        self,
        text: str,
        context: ContextOutput,
        plan: PlanOutput,
        role: RoleOutput,
        motivation: MotivationOutput,
    ) -> str:
        language = detect_language(text)
        if motivation.mode == "clarify":
            if language == "pl":
                return "Nie dostałem jeszcze treści wiadomości. Napisz krótką wiadomość, a od razu pomogę."
            return "I didn't catch any text yet. Send me a short message and I'll help from there."

        if motivation.mode == "support" or role.selected == "friend":
            if language == "pl":
                return (
                    "Brzmi to ciężko. Weźmy to krok po kroku. "
                    "Powiedz, co teraz najbardziej Cię przytłacza, a pójdziemy od tego."
                )
            return (
                "That sounds heavy. Let's take it one step at a time. "
                "Tell me what feels most pressing right now, and we'll work from there."
            )

        if motivation.mode == "execute" or role.selected == "executor":
            if language == "pl":
                return (
                    "Jasne, lecimy z tym. "
                    "Napisz dokładnie, jaką zmianę chcesz wprowadzić, a zamienimy to na najbliższy konkretny krok."
                )
            return (
                "I'm ready to help move this forward. "
                "Share the exact change you want, and we'll turn it into the next concrete step."
            )

        if motivation.mode == "analyze" or role.selected == "analyst":
            if language == "pl":
                return (
                    "Rozbijmy to spokojnie. "
                    "Zacznij od obecnego stanu, oczekiwanego wyniku i głównej blokady."
                )
            return (
                "Let's break this down clearly. "
                "Start with the current state, the target outcome, and the main blocker."
            )

        if role.selected == "mentor":
            if language == "pl":
                return (
                    "Dobry następny ruch to nazwać cel, główne ograniczenie "
                    "i najmniejszy sensowny krok."
                )
            return (
                "A good next move is to define the goal, name the main constraint, "
                "and pick the smallest actionable step."
            )

        if "Relevant recent memory:" in context.summary:
            if language == "pl":
                return "Mogę w tym pomóc. Mam też trochę świeżego kontekstu, więc możemy płynnie iść dalej."
            return "I can help with that. I also have a bit of recent context, so we can keep building from it."

        if language == "pl":
            return "Jestem tu i mogę pomóc. Napisz, co chcesz teraz ruszyć."

        return f"I'm here and ready to help. {plan.goal}"
