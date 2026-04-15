from openai import AsyncOpenAI

from app.core.logging import get_logger


class OpenAIClient:
    def __init__(self, api_key: str | None, model: str):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None
        self.logger = get_logger("aion.openai")

    async def generate_reply(self, user_text: str, context_summary: str, role_name: str) -> str | None:
        if not self.client:
            return None

        try:
            response = await self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are AION, a supportive and concise assistant. "
                            f"Your current interaction role is '{role_name}'. "
                            "Respond clearly and use the context summary when useful."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Context: {context_summary}\n\nUser message: {user_text}",
                    },
                ],
                max_output_tokens=220,
            )
        except Exception as exc:  # pragma: no cover - defensive network fallback
            self.logger.warning("openai_request_failed model=%s error=%s", self.model, exc)
            return None

        text = getattr(response, "output_text", None)
        if text:
            return text.strip()

        return None
