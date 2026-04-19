from pydantic import BaseModel

from app.core.contracts import MotivationMode, RuntimeResult


class EventReplyResponse(BaseModel):
    message: str
    language: str
    tone: str
    channel: str


class EventRuntimeResponse(BaseModel):
    role: str
    motivation_mode: MotivationMode
    action_status: str
    reflection_triggered: bool


class EventQueueResponse(BaseModel):
    queued: bool
    reason: str
    turn_id: str | None = None
    source_count: int | None = None


class EventResponse(BaseModel):
    event_id: str
    trace_id: str
    source: str
    reply: EventReplyResponse | None = None
    runtime: EventRuntimeResponse | None = None
    queue: EventQueueResponse | None = None
    debug: RuntimeResult | None = None


class SetWebhookRequest(BaseModel):
    webhook_url: str
    secret_token: str | None = None
