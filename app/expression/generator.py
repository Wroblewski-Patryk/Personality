from app.core.contracts import (
    ContextOutput,
    Event,
    ExpressionOutput,
    MotivationOutput,
    PlanOutput,
    RoleOutput,
)
from app.integrations.openai.client import OpenAIClient


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
            message = "I did not receive text content. Please send a message."
        else:
            llm_reply = await self.openai_client.generate_reply(
                user_text=text,
                context_summary=context.summary,
                role_name=role.selected,
            )
            message = llm_reply or f"Echo ({role.selected}): {text}"

        channel = "telegram" if event.source == "telegram" else "api"
        return ExpressionOutput(message=message, tone="supportive", channel=channel)
