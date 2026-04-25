from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from typing import Any

import httpx


class GoogleCalendarAvailabilityClient:
    def __init__(
        self,
        *,
        access_token: str | None = None,
        calendar_id: str | None = None,
        default_timezone: str = "UTC",
        base_url: str = "https://www.googleapis.com/calendar/v3",
        http_client: Any | None = None,
    ) -> None:
        self.access_token = str(access_token or "").strip()
        self.calendar_id = str(calendar_id or "").strip()
        self.default_timezone = str(default_timezone or "UTC").strip() or "UTC"
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    @property
    def ready(self) -> bool:
        return bool(self.access_token and self.calendar_id)

    async def read_availability(
        self,
        *,
        time_hint: str,
        slot_minutes: int = 60,
        slot_limit: int = 3,
    ) -> dict[str, Any]:
        if not self.ready:
            raise RuntimeError("Google Calendar availability execution is not configured.")

        normalized_window = self._normalize_time_window(time_hint=time_hint)
        payload = {
            "timeMin": normalized_window["window_start"],
            "timeMax": normalized_window["window_end"],
            "timeZone": normalized_window["time_zone"],
            "items": [{"id": self.calendar_id}],
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/freeBusy"

        if self.http_client is not None:
            response = await self.http_client.post(url, headers=headers, json=payload)
            if hasattr(response, "raise_for_status"):
                response.raise_for_status()
            result = response.json() if hasattr(response, "json") else dict(response)
        else:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

        busy_windows = self._normalize_busy_windows(result)
        free_slot_preview = self._candidate_free_slots(
            busy_windows=busy_windows,
            window_start=normalized_window["window_start_dt"],
            window_end=normalized_window["window_end_dt"],
            slot_minutes=max(15, int(slot_minutes)),
            slot_limit=max(1, int(slot_limit)),
        )
        return {
            "provider": "google_calendar",
            "calendar_id": self.calendar_id,
            "time_zone": normalized_window["time_zone"],
            "window_resolution": normalized_window["window_resolution"],
            "window_start": normalized_window["window_start"],
            "window_end": normalized_window["window_end"],
            "busy_window_count": len(busy_windows),
            "free_slot_preview": free_slot_preview,
        }

    def _normalize_time_window(self, *, time_hint: str) -> dict[str, Any]:
        now = datetime.now(UTC)
        lowered = str(time_hint or "").strip().lower()
        window_start = now.replace(minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(days=3)
        resolution = "rolling_72h_default"

        if "tomorrow" in lowered:
            day = (now + timedelta(days=1)).date()
            window_start = datetime.combine(day, time(hour=8), tzinfo=UTC)
            window_end = datetime.combine(day, time(hour=18), tzinfo=UTC)
            resolution = "tomorrow_business_window"
        elif "next week" in lowered:
            days_until_next_monday = (7 - now.weekday()) or 7
            start_day = (now + timedelta(days=days_until_next_monday)).date()
            window_start = datetime.combine(start_day, time(hour=8), tzinfo=UTC)
            window_end = window_start + timedelta(days=5, hours=10)
            resolution = "next_week_business_window"
        elif "today" in lowered:
            day = now.date()
            window_start = datetime.combine(day, time(hour=8), tzinfo=UTC)
            window_end = datetime.combine(day, time(hour=18), tzinfo=UTC)
            resolution = "today_business_window"

        return {
            "time_zone": self.default_timezone,
            "window_resolution": resolution,
            "window_start_dt": window_start,
            "window_end_dt": window_end,
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
        }

    def _normalize_busy_windows(self, payload: dict[str, Any]) -> list[tuple[datetime, datetime]]:
        calendars = payload.get("calendars", {})
        if not isinstance(calendars, dict):
            return []
        busy_rows = calendars.get(self.calendar_id, {}).get("busy", [])
        if not isinstance(busy_rows, list):
            return []

        normalized: list[tuple[datetime, datetime]] = []
        for row in busy_rows:
            if not isinstance(row, dict):
                continue
            start_raw = str(row.get("start", "")).strip()
            end_raw = str(row.get("end", "")).strip()
            if not start_raw or not end_raw:
                continue
            start_dt = self._parse_datetime(start_raw)
            end_dt = self._parse_datetime(end_raw)
            if start_dt is None or end_dt is None or end_dt <= start_dt:
                continue
            normalized.append((start_dt, end_dt))
        normalized.sort(key=lambda item: item[0])
        return normalized

    def _candidate_free_slots(
        self,
        *,
        busy_windows: list[tuple[datetime, datetime]],
        window_start: datetime,
        window_end: datetime,
        slot_minutes: int,
        slot_limit: int,
    ) -> list[str]:
        slot_delta = timedelta(minutes=slot_minutes)
        candidate = window_start
        preview: list[str] = []
        while candidate + slot_delta <= window_end and len(preview) < slot_limit:
            candidate_end = candidate + slot_delta
            overlaps = any(
                candidate < busy_end and candidate_end > busy_start
                for busy_start, busy_end in busy_windows
            )
            if not overlaps:
                preview.append(f"{candidate.isoformat()} -> {candidate_end.isoformat()}")
            candidate += slot_delta
        return preview

    def _parse_datetime(self, value: str) -> datetime | None:
        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
