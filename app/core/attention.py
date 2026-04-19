from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from time import monotonic
from typing import Literal
from uuid import uuid4

from app.core.contracts import Event
from app.core.events import coalesce_turn_text


@dataclass
class TurnAssemblyDecision:
    should_process: bool
    event: Event
    turn_id: str | None = None
    queue_reason: str = ""
    source_count: int = 1


@dataclass
class _PendingTurn:
    turn_id: str
    conversation_key: str
    status: Literal["pending", "claimed", "answered"] = "pending"
    messages: list[str] = field(default_factory=list)
    event_ids: list[str] = field(default_factory=list)
    update_keys: set[str] = field(default_factory=set)
    created_at_monotonic: float = field(default_factory=monotonic)
    last_updated_monotonic: float = field(default_factory=monotonic)


class AttentionTurnCoordinator:
    """Coordinates short-window turn assembly for bursty Telegram user messages."""

    def __init__(
        self,
        *,
        burst_window_ms: int = 120,
        answered_ttl_seconds: float = 5.0,
        stale_turn_seconds: float = 30.0,
    ) -> None:
        self.burst_window_seconds = max(0.0, float(burst_window_ms) / 1000.0)
        self.answered_ttl_seconds = max(0.5, float(answered_ttl_seconds))
        self.stale_turn_seconds = max(self.answered_ttl_seconds, float(stale_turn_seconds))
        self._lock = asyncio.Lock()
        self._turns_by_conversation: dict[str, _PendingTurn] = {}

    async def prepare_event(self, event: Event) -> TurnAssemblyDecision:
        if not self._is_telegram_user_event(event):
            return TurnAssemblyDecision(should_process=True, event=event)

        conversation_key = self._conversation_key(event)
        update_key = self._update_key(event)
        text = str(event.payload.get("text", "")).strip()
        if not text:
            return TurnAssemblyDecision(should_process=True, event=event)

        turn_id: str | None = None
        is_owner = False
        now = monotonic()
        async with self._lock:
            self._cleanup_locked(now=now)
            turn = self._turns_by_conversation.get(conversation_key)
            if turn is None or turn.status == "answered":
                turn_id = str(uuid4())
                self._turns_by_conversation[conversation_key] = _PendingTurn(
                    turn_id=turn_id,
                    conversation_key=conversation_key,
                    status="pending",
                    messages=[text],
                    event_ids=[event.event_id],
                    update_keys={update_key},
                    created_at_monotonic=now,
                    last_updated_monotonic=now,
                )
                is_owner = True
            elif update_key in turn.update_keys:
                return TurnAssemblyDecision(
                    should_process=False,
                    event=event,
                    turn_id=turn.turn_id,
                    queue_reason="duplicate_update",
                    source_count=len(turn.messages),
                )
            elif turn.status == "pending":
                turn.messages.append(text)
                turn.event_ids.append(event.event_id)
                turn.update_keys.add(update_key)
                turn.last_updated_monotonic = now
                return TurnAssemblyDecision(
                    should_process=False,
                    event=event,
                    turn_id=turn.turn_id,
                    queue_reason="coalesced_into_pending_turn",
                    source_count=len(turn.messages),
                )
            else:
                return TurnAssemblyDecision(
                    should_process=False,
                    event=event,
                    turn_id=turn.turn_id,
                    queue_reason="turn_already_claimed",
                    source_count=len(turn.messages),
                )

        if not is_owner or turn_id is None:
            return TurnAssemblyDecision(should_process=True, event=event)

        if self.burst_window_seconds > 0:
            await asyncio.sleep(self.burst_window_seconds)

        async with self._lock:
            now = monotonic()
            self._cleanup_locked(now=now)
            turn = self._turns_by_conversation.get(conversation_key)
            if turn is None or turn.turn_id != turn_id:
                return TurnAssemblyDecision(
                    should_process=False,
                    event=event,
                    turn_id=turn_id,
                    queue_reason="turn_replaced",
                )
            if turn.status != "pending":
                return TurnAssemblyDecision(
                    should_process=False,
                    event=event,
                    turn_id=turn.turn_id,
                    queue_reason="turn_no_longer_pending",
                    source_count=len(turn.messages),
                )
            turn.status = "claimed"
            turn.last_updated_monotonic = now
            assembled_text = coalesce_turn_text(turn.messages)
            source_count = len(turn.messages)
            coalesced_event_ids = list(turn.event_ids)

        assembled_event = event.model_copy(
            update={
                "payload": {
                    **event.payload,
                    "text": assembled_text,
                    "turn_id": turn_id,
                    "turn_status": "claimed",
                    "turn_source_count": source_count,
                    "coalesced_event_ids": coalesced_event_ids,
                    "conversation_key": conversation_key,
                }
            }
        )
        return TurnAssemblyDecision(
            should_process=True,
            event=assembled_event,
            turn_id=turn_id,
            source_count=source_count,
        )

    async def finalize_event(self, event: Event) -> None:
        if not self._is_telegram_user_event(event):
            return
        turn_id = str(event.payload.get("turn_id", "")).strip()
        if not turn_id:
            return
        conversation_key = str(event.payload.get("conversation_key", "")).strip() or self._conversation_key(event)
        async with self._lock:
            now = monotonic()
            turn = self._turns_by_conversation.get(conversation_key)
            if turn is None or turn.turn_id != turn_id:
                self._cleanup_locked(now=now)
                return
            turn.status = "answered"
            turn.last_updated_monotonic = now
            self._cleanup_locked(now=now)

    def snapshot(self) -> dict[str, int]:
        pending = 0
        claimed = 0
        answered = 0
        now = monotonic()
        for turn in self._turns_by_conversation.values():
            age = now - turn.last_updated_monotonic
            if age > self.stale_turn_seconds:
                continue
            if turn.status == "pending":
                pending += 1
            elif turn.status == "claimed":
                claimed += 1
            else:
                answered += 1
        return {
            "pending": pending,
            "claimed": claimed,
            "answered": answered,
        }

    def _cleanup_locked(self, *, now: float) -> None:
        stale_keys: list[str] = []
        for conversation_key, turn in self._turns_by_conversation.items():
            age = now - turn.last_updated_monotonic
            if turn.status == "answered" and age > self.answered_ttl_seconds:
                stale_keys.append(conversation_key)
                continue
            if age > self.stale_turn_seconds:
                stale_keys.append(conversation_key)
        for conversation_key in stale_keys:
            self._turns_by_conversation.pop(conversation_key, None)

    def _is_telegram_user_event(self, event: Event) -> bool:
        return event.source == "telegram" and event.subsource == "user_message"

    def _conversation_key(self, event: Event) -> str:
        chat_id = event.payload.get("chat_id")
        if isinstance(chat_id, (int, str)):
            value = str(chat_id).strip()
            if value:
                return f"telegram:{value}"
        return f"telegram_user:{event.meta.user_id}"

    def _update_key(self, event: Event) -> str:
        update_id = event.payload.get("update_id")
        if update_id is not None:
            return f"update:{update_id}"
        return f"event:{event.event_id}"
