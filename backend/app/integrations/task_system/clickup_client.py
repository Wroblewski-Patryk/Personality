from __future__ import annotations

from typing import Any

import httpx


class ClickUpTaskClient:
    def __init__(
        self,
        *,
        api_token: str | None = None,
        list_id: str | None = None,
        base_url: str = "https://api.clickup.com/api/v2",
        http_client: Any | None = None,
    ) -> None:
        self.api_token = str(api_token or "").strip()
        self.list_id = str(list_id or "").strip()
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    @property
    def ready(self) -> bool:
        return bool(self.api_token and self.list_id)

    async def create_task(self, *, name: str, description: str = "") -> dict[str, Any]:
        if not self.ready:
            raise RuntimeError("ClickUp task execution is not configured.")

        payload = {
            "name": name,
            "description": description,
        }
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/list/{self.list_id}/task"

        if self.http_client is not None:
            response = await self.http_client.post(url, headers=headers, json=payload)
            if hasattr(response, "raise_for_status"):
                response.raise_for_status()
            if hasattr(response, "json"):
                return response.json()
            return dict(response)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def list_tasks(self, *, limit: int = 10) -> list[dict[str, Any]]:
        if not self.ready:
            raise RuntimeError("ClickUp task execution is not configured.")

        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
        }
        params = {"page": 0}
        url = f"{self.base_url}/list/{self.list_id}/task"

        if self.http_client is not None:
            response = await self.http_client.get(url, headers=headers, params=params)
            if hasattr(response, "raise_for_status"):
                response.raise_for_status()
            payload = response.json() if hasattr(response, "json") else dict(response)
        else:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                payload = response.json()

        tasks = payload.get("tasks", [])
        if not isinstance(tasks, list):
            return []
        return [task for task in tasks[: max(1, int(limit))] if isinstance(task, dict)]

    async def update_task(self, *, task_id: str, status: str) -> dict[str, Any]:
        if not self.ready:
            raise RuntimeError("ClickUp task execution is not configured.")

        payload = {"status": status}
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/task/{task_id}"

        if self.http_client is not None:
            response = await self.http_client.put(url, headers=headers, json=payload)
            if hasattr(response, "raise_for_status"):
                response.raise_for_status()
            if hasattr(response, "json"):
                return response.json()
            return dict(response)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.put(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
