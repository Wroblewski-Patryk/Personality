from __future__ import annotations

from typing import Any

from app.utils.language import language_name

try:  # pragma: no cover - optional dependency path
    from langchain_core.prompts import ChatPromptTemplate
except Exception:  # pragma: no cover - optional dependency path
    ChatPromptTemplate = None  # type: ignore[assignment]


class OpenAIPromptBuilder:
    """Builds OpenAI-ready chat payloads with optional LangChain templates."""

    def __init__(self) -> None:
        self.langchain_available = ChatPromptTemplate is not None

    def build_reply_messages(
        self,
        *,
        user_text: str,
        context_summary: str,
        role_name: str,
        response_language: str,
        response_style: str | None,
        plan_goal: str,
        motivation_mode: str,
        response_tone: str,
        collaboration_preference: str | None,
        identity_summary: str,
    ) -> list[dict[str, str]]:
        variables = {
            "role_name": role_name,
            "motivation_mode": motivation_mode,
            "response_tone": response_tone,
            "plan_goal": plan_goal,
            "response_language_name": language_name(response_language),
            "response_style": response_style or "default",
            "collaboration_preference": collaboration_preference or "default",
            "identity_summary": identity_summary or "default",
            "context_summary": context_summary,
            "user_text": user_text,
        }
        if self.langchain_available:
            return self._build_with_langchain_reply(variables)
        return self._build_without_langchain_reply(variables)

    def build_affective_messages(
        self,
        *,
        user_text: str,
        response_language: str,
    ) -> list[dict[str, str]]:
        variables = {
            "response_language_name": language_name(response_language),
            "user_text": user_text,
        }
        if self.langchain_available:
            return self._build_with_langchain_affective(variables)
        return self._build_without_langchain_affective(variables)

    def _build_with_langchain_reply(self, variables: dict[str, Any]) -> list[dict[str, str]]:
        template = ChatPromptTemplate.from_messages(  # type: ignore[union-attr]
            [
                (
                    "system",
                    (
                        "You are AION, a supportive and concise assistant. "
                        "Your current interaction role is '{role_name}'. "
                        "The current response mode is '{motivation_mode}'. "
                        "The desired response tone is '{response_tone}'. "
                        "The immediate goal is '{plan_goal}'. "
                        "The preferred response language is '{response_language_name}'. "
                        "The user's stable response style preference is '{response_style}'. "
                        "The user's stable collaboration preference is '{collaboration_preference}'. "
                        "The stable identity summary is '{identity_summary}'. "
                        "Respond clearly, preserve momentum, use the context summary when useful, "
                        "stay in the preferred response language unless the user explicitly asks to switch, "
                        "honor the response style preference when it is present, "
                        "keep the wording aligned with the desired response tone, "
                        "if a collaboration preference exists, match the response shape to it, "
                        "and do not contradict the stable identity."
                    ),
                ),
                (
                    "human",
                    "Context: {context_summary}\n\nUser message: {user_text}",
                ),
            ]
        )
        rendered = template.invoke(variables)
        return self._langchain_messages_to_openai(rendered.messages)

    def _build_with_langchain_affective(self, variables: dict[str, Any]) -> list[dict[str, str]]:
        template = ChatPromptTemplate.from_messages(  # type: ignore[union-attr]
            [
                (
                    "system",
                    (
                        "Classify the affective state of the user message. "
                        "Return only compact JSON with keys: "
                        "affect_label, intensity, needs_support, confidence, evidence. "
                        "Allowed affect_label values: neutral, support_distress, urgent_pressure, positive_engagement. "
                        "intensity and confidence must be numbers between 0 and 1. "
                        "needs_support must be true/false. "
                        "evidence must be a short list of supporting phrases."
                    ),
                ),
                (
                    "human",
                    (
                        "Preferred response language context: {response_language_name}.\n"
                        "User message: {user_text}"
                    ),
                ),
            ]
        )
        rendered = template.invoke(variables)
        return self._langchain_messages_to_openai(rendered.messages)

    def _build_without_langchain_reply(self, variables: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "You are AION, a supportive and concise assistant. "
                    f"Your current interaction role is '{variables['role_name']}'. "
                    f"The current response mode is '{variables['motivation_mode']}'. "
                    f"The desired response tone is '{variables['response_tone']}'. "
                    f"The immediate goal is '{variables['plan_goal']}'. "
                    f"The preferred response language is '{variables['response_language_name']}'. "
                    f"The user's stable response style preference is '{variables['response_style']}'. "
                    f"The user's stable collaboration preference is '{variables['collaboration_preference']}'. "
                    f"The stable identity summary is '{variables['identity_summary']}'. "
                    "Respond clearly, preserve momentum, use the context summary when useful, "
                    "stay in the preferred response language unless the user explicitly asks to switch, "
                    "honor the response style preference when it is present, "
                    "keep the wording aligned with the desired response tone, "
                    "if a collaboration preference exists, match the response shape to it, "
                    "and do not contradict the stable identity."
                ),
            },
            {
                "role": "user",
                "content": f"Context: {variables['context_summary']}\n\nUser message: {variables['user_text']}",
            },
        ]

    def _build_without_langchain_affective(self, variables: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "Classify the affective state of the user message. "
                    "Return only compact JSON with keys: "
                    "affect_label, intensity, needs_support, confidence, evidence. "
                    "Allowed affect_label values: neutral, support_distress, urgent_pressure, positive_engagement. "
                    "intensity and confidence must be numbers between 0 and 1. "
                    "needs_support must be true/false. "
                    "evidence must be a short list of supporting phrases."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Preferred response language context: {variables['response_language_name']}.\n"
                    f"User message: {variables['user_text']}"
                ),
            },
        ]

    def _langchain_messages_to_openai(self, messages: list[Any]) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        for message in messages:
            role = "user" if str(getattr(message, "type", "user")).strip().lower() == "human" else str(
                getattr(message, "type", "user")
            ).strip().lower()
            content = self._message_content_to_text(getattr(message, "content", ""))
            normalized.append({"role": role, "content": content})
        return normalized

    def _message_content_to_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    text = str(item.get("text", "")).strip()
                    if text:
                        parts.append(text)
                else:
                    text = str(item).strip()
                    if text:
                        parts.append(text)
            return " ".join(parts).strip()
        return str(content or "").strip()
