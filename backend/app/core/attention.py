from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from time import monotonic
from typing import Any, Literal
from uuid import uuid4

from app.core.contracts import Event
from app.core.events import coalesce_turn_text

AttentionCoordinationMode = Literal["in_process", "durable_inbox"]
DEFAULT_ATTENTION_COORDINATION_MODE: AttentionCoordinationMode = "in_process"
ATTENTION_COORDINATION_BASELINE_MODE: AttentionCoordinationMode = "in_process"
ATTENTION_PRODUCTION_BASELINE_BURST_WINDOW_MS = 120
ATTENTION_PRODUCTION_BASELINE_ANSWERED_TTL_SECONDS = 5.0
ATTENTION_PRODUCTION_BASELINE_STALE_TURN_SECONDS = 30.0


def normalize_attention_coordination_mode(value: str | None) -> AttentionCoordinationMode:
    normalized = str(value or "").strip().lower()
    if normalized == "durable_inbox":
        return "durable_inbox"
    return DEFAULT_ATTENTION_COORDINATION_MODE


def attention_coordination_readiness_snapshot(
    *,
    coordination_mode: str | None,
    pending: int,
    claimed: int,
    store_available: bool = True,
    stale_cleanup_candidates: int = 0,
    answered_cleanup_candidates: int = 0,
) -> dict[str, Any]:
    selected_mode = normalize_attention_coordination_mode(coordination_mode)
    turn_state_owner = "durable_attention_inbox" if selected_mode == "durable_inbox" else "in_process_coordinator"
    blocking_signals: list[str] = []
    if selected_mode == "durable_inbox" and not store_available:
        blocking_signals.append("durable_attention_contract_store_unavailable")
    return {
        "baseline_coordination_mode": ATTENTION_COORDINATION_BASELINE_MODE,
        "selected_coordination_mode": selected_mode,
        "ready": len(blocking_signals) == 0,
        "blocking_signals": blocking_signals,
        "turn_state_owner": turn_state_owner,
        "durable_inbox_expected": selected_mode == "durable_inbox",
        "persistence_owner": (
            "durable_attention_contract_store" if selected_mode == "durable_inbox" else "in_process_coordinator_store"
        ),
        "parity_state": (
            "durable_attention_contract_store_active"
            if selected_mode == "durable_inbox"
            else "in_process_baseline_active"
        ),
        "contract_store_state": (
            "repository_backed_contract_store_active"
            if selected_mode == "durable_inbox" and store_available
            else "durable_contract_store_unavailable"
            if selected_mode == "durable_inbox"
            else "in_process_only"
        ),
        "store_available": bool(store_available),
        "stale_cleanup_candidates": int(stale_cleanup_candidates),
        "answered_cleanup_candidates": int(answered_cleanup_candidates),
    }


def attention_timing_policy_snapshot(
    *,
    burst_window_ms: int,
    answered_ttl_seconds: float,
    stale_turn_seconds: float,
) -> dict[str, Any]:
    deviations: list[str] = []
    if burst_window_ms < ATTENTION_PRODUCTION_BASELINE_BURST_WINDOW_MS:
        deviations.append("burst_window_lower_than_baseline")
    elif burst_window_ms > ATTENTION_PRODUCTION_BASELINE_BURST_WINDOW_MS:
        deviations.append("burst_window_higher_than_baseline")

    if answered_ttl_seconds < ATTENTION_PRODUCTION_BASELINE_ANSWERED_TTL_SECONDS:
        deviations.append("answered_ttl_lower_than_baseline")
    elif answered_ttl_seconds > ATTENTION_PRODUCTION_BASELINE_ANSWERED_TTL_SECONDS:
        deviations.append("answered_ttl_higher_than_baseline")

    if stale_turn_seconds < ATTENTION_PRODUCTION_BASELINE_STALE_TURN_SECONDS:
        deviations.append("stale_turn_window_lower_than_baseline")
    elif stale_turn_seconds > ATTENTION_PRODUCTION_BASELINE_STALE_TURN_SECONDS:
        deviations.append("stale_turn_window_higher_than_baseline")

    if deviations:
        alignment_state = "customized_timing_override"
        alignment_hint = "review_attention_timing_override_before_production_rollout"
    else:
        alignment_state = "aligned_with_production_baseline"
        alignment_hint = "production_attention_timing_baseline_selected"

    return {
        "production_baseline": {
            "burst_window_ms": ATTENTION_PRODUCTION_BASELINE_BURST_WINDOW_MS,
            "answered_ttl_seconds": ATTENTION_PRODUCTION_BASELINE_ANSWERED_TTL_SECONDS,
            "stale_turn_seconds": ATTENTION_PRODUCTION_BASELINE_STALE_TURN_SECONDS,
        },
        "current": {
            "burst_window_ms": int(burst_window_ms),
            "answered_ttl_seconds": float(answered_ttl_seconds),
            "stale_turn_seconds": float(stale_turn_seconds),
        },
        "alignment_state": alignment_state,
        "alignment_hint": alignment_hint,
        "deviations": deviations,
    }


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
        coordination_mode: str = "in_process",
        memory_repository: Any | None = None,
    ) -> None:
        self.coordination_mode = normalize_attention_coordination_mode(coordination_mode)
        self.burst_window_seconds = max(0.0, float(burst_window_ms) / 1000.0)
        self.answered_ttl_seconds = max(0.5, float(answered_ttl_seconds))
        self.stale_turn_seconds = max(self.answered_ttl_seconds, float(stale_turn_seconds))
        self.memory_repository = memory_repository
        self._lock = asyncio.Lock()
        self._turns_by_conversation: dict[str, _PendingTurn] = {}

    async def prepare_event(self, event: Event) -> TurnAssemblyDecision:
        if not self._is_telegram_user_event(event):
            return TurnAssemblyDecision(should_process=True, event=event)
        if self._use_durable_contract_store():
            return await self._prepare_event_with_durable_store(event)
        return await self._prepare_event_in_process(event)

    async def _prepare_event_in_process(self, event: Event) -> TurnAssemblyDecision:
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

    async def _prepare_event_with_durable_store(self, event: Event) -> TurnAssemblyDecision:
        conversation_key = self._conversation_key(event)
        update_key = self._update_key(event)
        text = str(event.payload.get("text", "")).strip()
        if not text:
            return TurnAssemblyDecision(should_process=True, event=event)

        turn_id: str | None = None
        is_owner = False
        async with self._lock:
            await self._cleanup_durable_store()
            turn = await self.memory_repository.get_attention_turn(
                user_id=event.meta.user_id,
                conversation_key=conversation_key,
            )
            if turn is None or str(turn.get("status", "")) == "answered":
                turn_id = str(uuid4())
                await self.memory_repository.upsert_attention_turn(
                    user_id=event.meta.user_id,
                    conversation_key=conversation_key,
                    turn_id=turn_id,
                    status="pending",
                    messages=[text],
                    event_ids=[event.event_id],
                    update_keys=[update_key],
                    source_count=1,
                    owner_mode=self.coordination_mode,
                )
                is_owner = True
            elif update_key in {str(item) for item in turn.get("update_keys", [])}:
                return TurnAssemblyDecision(
                    should_process=False,
                    event=event,
                    turn_id=str(turn.get("turn_id", "")) or None,
                    queue_reason="duplicate_update",
                    source_count=int(turn.get("source_count", 1) or 1),
                )
            elif str(turn.get("status", "")) == "pending":
                messages = [str(item) for item in turn.get("messages", [])]
                event_ids = [str(item) for item in turn.get("event_ids", [])]
                update_keys = [str(item) for item in turn.get("update_keys", [])]
                messages.append(text)
                event_ids.append(event.event_id)
                update_keys.append(update_key)
                await self.memory_repository.upsert_attention_turn(
                    user_id=event.meta.user_id,
                    conversation_key=conversation_key,
                    turn_id=str(turn.get("turn_id", "")),
                    status="pending",
                    messages=messages,
                    event_ids=event_ids,
                    update_keys=update_keys,
                    source_count=len(messages),
                    owner_mode=self.coordination_mode,
                )
                return TurnAssemblyDecision(
                    should_process=False,
                    event=event,
                    turn_id=str(turn.get("turn_id", "")) or None,
                    queue_reason="coalesced_into_pending_turn",
                    source_count=len(messages),
                )
            else:
                return TurnAssemblyDecision(
                    should_process=False,
                    event=event,
                    turn_id=str(turn.get("turn_id", "")) or None,
                    queue_reason="turn_already_claimed",
                    source_count=int(turn.get("source_count", 1) or 1),
                )

        if not is_owner or turn_id is None:
            return TurnAssemblyDecision(should_process=True, event=event)

        if self.burst_window_seconds > 0:
            await asyncio.sleep(self.burst_window_seconds)

        async with self._lock:
            await self._cleanup_durable_store()
            turn = await self.memory_repository.get_attention_turn(
                user_id=event.meta.user_id,
                conversation_key=conversation_key,
            )
            if turn is None or str(turn.get("turn_id", "")) != turn_id:
                return TurnAssemblyDecision(
                    should_process=False,
                    event=event,
                    turn_id=turn_id,
                    queue_reason="turn_replaced",
                )
            if str(turn.get("status", "")) != "pending":
                return TurnAssemblyDecision(
                    should_process=False,
                    event=event,
                    turn_id=str(turn.get("turn_id", "")) or None,
                    queue_reason="turn_no_longer_pending",
                    source_count=int(turn.get("source_count", 1) or 1),
                )
            messages = [str(item) for item in turn.get("messages", [])]
            event_ids = [str(item) for item in turn.get("event_ids", [])]
            update_keys = [str(item) for item in turn.get("update_keys", [])]
            assembled_text = coalesce_turn_text(messages)
            source_count = len(messages)
            coalesced_event_ids = list(event_ids)
            await self.memory_repository.upsert_attention_turn(
                user_id=event.meta.user_id,
                conversation_key=conversation_key,
                turn_id=turn_id,
                status="claimed",
                messages=messages,
                event_ids=event_ids,
                update_keys=update_keys,
                source_count=source_count,
                assembled_text=assembled_text,
                owner_mode=self.coordination_mode,
            )

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
        if self._use_durable_contract_store():
            async with self._lock:
                turn = await self.memory_repository.get_attention_turn(
                    user_id=event.meta.user_id,
                    conversation_key=conversation_key,
                )
                if turn is not None and str(turn.get("turn_id", "")) == turn_id:
                    await self.memory_repository.upsert_attention_turn(
                        user_id=event.meta.user_id,
                        conversation_key=conversation_key,
                        turn_id=turn_id,
                        status="answered",
                        messages=[str(item) for item in turn.get("messages", [])],
                        event_ids=[str(item) for item in turn.get("event_ids", [])],
                        update_keys=[str(item) for item in turn.get("update_keys", [])],
                        source_count=int(turn.get("source_count", 1) or 1),
                        assembled_text=str(turn.get("assembled_text", "")).strip() or None,
                        owner_mode=self.coordination_mode,
                    )
                await self._cleanup_durable_store()
            return
        async with self._lock:
            now = monotonic()
            turn = self._turns_by_conversation.get(conversation_key)
            if turn is None or turn.turn_id != turn_id:
                self._cleanup_locked(now=now)
                return
            turn.status = "answered"
            turn.last_updated_monotonic = now
            self._cleanup_locked(now=now)

    async def snapshot(self) -> dict[str, Any]:
        if self._use_durable_contract_store():
            stats = await self.memory_repository.get_attention_turn_stats(
                answered_ttl_seconds=self.answered_ttl_seconds,
                stale_turn_seconds=self.stale_turn_seconds,
            )
            return {
                "pending": int(stats.get("pending", 0)),
                "claimed": int(stats.get("claimed", 0)),
                "answered": int(stats.get("answered", 0)),
                "active_turns": int(stats.get("active_turns", 0)),
                "stale_cleanup_candidates": int(stats.get("stale_cleanup_candidates", 0)),
                "answered_cleanup_candidates": int(stats.get("answered_cleanup_candidates", 0)),
                "contract_store_mode": "repository_backed",
                "cleanup_owner": "attention_boundary",
            }
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
            "active_turns": pending + claimed + answered,
            "stale_cleanup_candidates": 0,
            "answered_cleanup_candidates": 0,
            "contract_store_mode": "in_process_only",
            "cleanup_owner": "attention_boundary",
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

    def _use_durable_contract_store(self) -> bool:
        if self.coordination_mode != "durable_inbox":
            return False
        return all(
            hasattr(self.memory_repository, name)
            for name in (
                "get_attention_turn",
                "upsert_attention_turn",
                "get_attention_turn_stats",
                "cleanup_attention_turns",
            )
        )

    async def _cleanup_durable_store(self) -> None:
        if not self._use_durable_contract_store():
            return
        await self.memory_repository.cleanup_attention_turns(
            answered_ttl_seconds=self.answered_ttl_seconds,
            stale_turn_seconds=self.stale_turn_seconds,
        )
