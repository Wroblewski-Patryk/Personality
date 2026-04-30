from dataclasses import dataclass
import html
import re

from app.core.action_delivery import summarize_action_delivery_envelope
from app.core.contracts import ActionDelivery, ActionResult
from app.integrations.telegram.client import TelegramClient
from app.integrations.telegram.telemetry import (
    TELEGRAM_DELIVERY_MESSAGE_LIMIT,
    TELEGRAM_DELIVERY_SEGMENT_TARGET,
    TelegramChannelTelemetry,
)

_TELEGRAM_HTML_PARSE_MODE = "HTML"


@dataclass(frozen=True)
class _TelegramPreparedMessage:
    text: str
    parse_mode: str | None = None


class DeliveryRouter:
    def __init__(
        self,
        telegram_client: TelegramClient,
        *,
        telegram_telemetry: TelegramChannelTelemetry | None = None,
    ):
        self.telegram_client = telegram_client
        self.telegram_telemetry = telegram_telemetry

    async def deliver(self, delivery: ActionDelivery) -> ActionResult:
        envelope_note = summarize_action_delivery_envelope(delivery.execution_envelope)
        if delivery.channel == "api":
            return ActionResult(
                status="success",
                actions=["api_response"],
                notes=self._with_envelope_note("Response returned via API.", envelope_note),
            )

        if delivery.channel == "telegram":
            return await self._deliver_telegram(delivery, envelope_note=envelope_note)

        return ActionResult(
            status="fail",
            actions=[],
            notes=f"Unsupported delivery channel: {delivery.channel}",
        )

    async def _deliver_telegram(self, delivery: ActionDelivery, *, envelope_note: str) -> ActionResult:
        if delivery.chat_id is None:
            if self.telegram_telemetry is not None:
                self.telegram_telemetry.record_delivery_failure(
                    state="missing_chat_id",
                    note="telegram_chat_id_missing",
                    chat_id=None,
                )
            return ActionResult(
                status="fail",
                actions=[],
                notes=self._with_envelope_note(
                    "Telegram response requested but chat_id is missing.",
                    envelope_note,
                ),
            )

        prepared_messages: list[_TelegramPreparedMessage] = []
        formatting_state = "plain_text"
        try:
            prepared_messages = _prepare_telegram_messages(delivery.message)
            formatting_state = _telegram_formatting_state(prepared_messages)
            if self.telegram_telemetry is not None:
                self.telegram_telemetry.record_delivery_attempt(
                    chat_id=delivery.chat_id,
                    segment_count=len(prepared_messages),
                    formatting_state=formatting_state,
                )
            telegram_result = {"ok": True}
            for prepared in prepared_messages:
                telegram_result = await self.telegram_client.send_message(
                    chat_id=delivery.chat_id,
                    text=prepared.text,
                    parse_mode=prepared.parse_mode,
                )
                if not telegram_result.get("ok"):
                    break
        except Exception as exc:
            if self.telegram_telemetry is not None:
                self.telegram_telemetry.record_delivery_failure(
                    state="delivery_exception",
                    note=f"{type(exc).__name__}: {exc}",
                    chat_id=delivery.chat_id,
                    segment_count=len(prepared_messages) if prepared_messages else None,
                    formatting_state=formatting_state,
                )
            return ActionResult(
                status="fail",
                actions=["send_telegram_message"],
                notes=self._with_envelope_note(
                    f"Telegram delivery exception: {type(exc).__name__}: {exc}",
                    envelope_note,
                ),
            )
        if telegram_result.get("ok"):
            if self.telegram_telemetry is not None:
                self.telegram_telemetry.record_delivery_success(
                    chat_id=delivery.chat_id,
                    segment_count=len(prepared_messages),
                    formatting_state=formatting_state,
                )
            delivery_note = "Telegram message sent."
            if len(prepared_messages) > 1:
                delivery_note = f"Telegram message sent in {len(prepared_messages)} parts."
            return ActionResult(
                status="success",
                actions=["send_telegram_message"],
                notes=self._with_envelope_note(delivery_note, envelope_note),
            )
        if self.telegram_telemetry is not None:
            self.telegram_telemetry.record_delivery_failure(
                state="telegram_api_error",
                note=str(telegram_result.get("description", "telegram_api_error")),
                chat_id=delivery.chat_id,
                segment_count=len(prepared_messages) if prepared_messages else None,
                formatting_state=formatting_state,
            )
        return ActionResult(
            status="fail",
            actions=["send_telegram_message"],
            notes=self._with_envelope_note(f"Telegram API error: {telegram_result}", envelope_note),
        )

    def _with_envelope_note(self, base: str, envelope_note: str) -> str:
        if not envelope_note:
            return base
        return f"{base} Execution envelope: {envelope_note}."


def _prepare_telegram_messages(message: str) -> list[_TelegramPreparedMessage]:
    pending_segments = _split_telegram_text(message, max_length=TELEGRAM_DELIVERY_SEGMENT_TARGET)
    prepared: list[_TelegramPreparedMessage] = []

    while pending_segments:
        segment = pending_segments.pop(0)
        candidate = _format_telegram_segment(segment)
        if len(candidate.text) <= TELEGRAM_DELIVERY_MESSAGE_LIMIT:
            prepared.append(candidate)
            continue

        if candidate.parse_mode is not None:
            plain_text_candidate = _TelegramPreparedMessage(text=segment)
            if len(plain_text_candidate.text) <= TELEGRAM_DELIVERY_MESSAGE_LIMIT:
                prepared.append(plain_text_candidate)
                continue

        if len(segment) <= TELEGRAM_DELIVERY_MESSAGE_LIMIT:
            prepared.append(_TelegramPreparedMessage(text=segment))
            continue

        smaller_segments = _split_telegram_text(segment, max_length=TELEGRAM_DELIVERY_MESSAGE_LIMIT)
        if len(smaller_segments) == 1 and smaller_segments[0] == segment:
            smaller_segments = [
                segment[index : index + TELEGRAM_DELIVERY_MESSAGE_LIMIT]
                for index in range(0, len(segment), TELEGRAM_DELIVERY_MESSAGE_LIMIT)
            ]
        pending_segments = smaller_segments + pending_segments

    return prepared or [_TelegramPreparedMessage(text="")]


def _split_telegram_text(text: str, *, max_length: int) -> list[str]:
    if len(text) <= max_length:
        return [text]

    segments: list[str] = []
    remaining = text
    while len(remaining) > max_length:
        split_at = _preferred_split_index(remaining, max_length=max_length)
        segment = remaining[:split_at].rstrip()
        if not segment:
            segment = remaining[:max_length]
            split_at = len(segment)
        segments.append(segment)
        remaining = remaining[split_at:].lstrip()

    if remaining:
        segments.append(remaining)
    return segments


def _preferred_split_index(text: str, *, max_length: int) -> int:
    for separator in ("\n\n", "\n"):
        candidate = text.rfind(separator, 0, max_length + 1)
        if candidate > 0:
            return candidate

    sentence_boundary = _sentence_split_index(text, max_length=max_length)
    if sentence_boundary > 0:
        return sentence_boundary

    candidate = text.rfind(" ", 0, max_length + 1)
    if candidate > 0:
        return candidate
    return max_length


def _sentence_split_index(text: str, *, max_length: int) -> int:
    window = text[: max_length + 1]
    matches = list(re.finditer(r"(?<=[.!?])[\)\]\"']*\s+", window))
    if not matches:
        return -1
    return matches[-1].end()


def _format_telegram_segment(segment: str) -> _TelegramPreparedMessage:
    rendered = _render_supported_markdown_to_html(segment)
    if rendered is None:
        return _TelegramPreparedMessage(text=segment)
    return _TelegramPreparedMessage(text=rendered, parse_mode=_TELEGRAM_HTML_PARSE_MODE)


def _telegram_formatting_state(prepared_messages: list[_TelegramPreparedMessage]) -> str:
    parse_modes = {prepared.parse_mode for prepared in prepared_messages}
    if parse_modes == {_TELEGRAM_HTML_PARSE_MODE}:
        return "telegram_html"
    if parse_modes == {None}:
        return "plain_text"
    return "mixed_html_and_plain_text"


def _render_supported_markdown_to_html(text: str) -> str | None:
    if not any(marker in text for marker in ("```", "`", "**", "*")):
        return None

    if text.count("```") % 2 != 0:
        return None

    rendered = text
    placeholders: dict[str, str] = {}

    rendered = _replace_markdown_pattern(
        rendered,
        pattern=r"```(?:[\w#+.-]+\n)?(.*?)```",
        placeholders=placeholders,
        template=lambda inner: f"<pre><code>{html.escape(inner)}</code></pre>",
        flags=re.DOTALL,
    )
    if rendered is None:
        return None

    if rendered.count("`") % 2 != 0:
        return None

    rendered = _replace_markdown_pattern(
        rendered,
        pattern=r"`([^`\n]+)`",
        placeholders=placeholders,
        template=lambda inner: f"<code>{html.escape(inner)}</code>",
    )
    if rendered is None:
        return None

    if rendered.count("**") % 2 != 0:
        return None

    rendered = _replace_markdown_pattern(
        rendered,
        pattern=r"\*\*([^\n*](?:.*?[^\n*])?)\*\*",
        placeholders=placeholders,
        template=lambda inner: f"<b>{html.escape(inner)}</b>",
    )
    if rendered is None:
        return None

    if _unmatched_telegram_italic_marker_exists(rendered):
        return None

    rendered = _replace_markdown_pattern(
        rendered,
        pattern=r"(?<!\*)\*([^*\n]+?)\*(?!\*)",
        placeholders=placeholders,
        template=lambda inner: f"<i>{html.escape(inner)}</i>",
    )
    if rendered is None:
        return None

    if any(marker in rendered for marker in ("```", "`", "**")):
        return None

    escaped = html.escape(rendered)
    for token, replacement in placeholders.items():
        escaped = escaped.replace(token, replacement)
    return escaped


def _unmatched_telegram_italic_marker_exists(text: str) -> bool:
    stripped = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", "", text)
    for line in stripped.splitlines():
        if line.lstrip().startswith(("* ", "- ", "+ ")):
            continue
        if "*" in line:
            return True
    return False


def _replace_markdown_pattern(
    text: str,
    *,
    pattern: str,
    placeholders: dict[str, str],
    template,
    flags: int = 0,
) -> str | None:
    compiled = re.compile(pattern, flags)

    def _replacer(match: re.Match[str]) -> str:
        token = f"@@AION_TELEGRAM_{len(placeholders)}@@"
        placeholders[token] = template(match.group(1))
        return token

    try:
        return compiled.sub(_replacer, text)
    except Exception:
        return None
