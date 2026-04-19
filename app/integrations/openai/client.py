import json
from typing import Any

from openai import AsyncOpenAI

from app.core.logging import get_logger
from app.integrations.openai.prompting import OpenAIPromptBuilder


class OpenAIClient:
    def __init__(self, api_key: str | None, model: str):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None
        self.logger = get_logger("aion.openai")
        self.prompt_builder = OpenAIPromptBuilder()

    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        role_name: str,
        response_language: str,
        response_style: str | None,
        plan_goal: str,
        motivation_mode: str,
        response_tone: str,
        collaboration_preference: str | None,
        identity_summary: str = "",
    ) -> str | None:
        if not self.client:
            return None

        try:
            messages = self.prompt_builder.build_reply_messages(
                user_text=user_text,
                context_summary=context_summary,
                role_name=role_name,
                response_language=response_language,
                response_style=response_style,
                plan_goal=plan_goal,
                motivation_mode=motivation_mode,
                response_tone=response_tone,
                collaboration_preference=collaboration_preference,
                identity_summary=identity_summary,
            )
            response = await self.client.responses.create(
                model=self.model,
                input=messages,
                max_output_tokens=120 if response_style == "concise" else 220,
            )
        except Exception as exc:  # pragma: no cover - defensive network fallback
            self.logger.warning("openai_request_failed model=%s error=%s", self.model, exc)
            return None

        text = getattr(response, "output_text", None)
        if text:
            return text.strip()

        return None

    async def classify_affective_state(
        self,
        *,
        user_text: str,
        response_language: str,
    ) -> dict[str, Any] | None:
        if not self.client:
            return None

        try:
            messages = self.prompt_builder.build_affective_messages(
                user_text=user_text,
                response_language=response_language,
            )
            response = await self.client.responses.create(
                model=self.model,
                input=messages,
                max_output_tokens=120,
            )
        except Exception as exc:  # pragma: no cover - defensive network fallback
            self.logger.warning("openai_affective_request_failed model=%s error=%s", self.model, exc)
            return None

        text = getattr(response, "output_text", None)
        if not text:
            return None

        try:
            payload = json.loads(text.strip())
        except Exception as exc:  # pragma: no cover - defensive parse fallback
            self.logger.warning("openai_affective_parse_failed model=%s error=%s", self.model, exc)
            return None

        if not isinstance(payload, dict):
            return None
        return payload
