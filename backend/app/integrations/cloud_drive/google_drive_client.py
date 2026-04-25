from __future__ import annotations

from typing import Any

import httpx


class GoogleDriveMetadataClient:
    def __init__(
        self,
        *,
        access_token: str | None = None,
        folder_id: str | None = None,
        base_url: str = "https://www.googleapis.com/drive/v3",
        http_client: Any | None = None,
    ) -> None:
        self.access_token = str(access_token or "").strip()
        self.folder_id = str(folder_id or "").strip()
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    @property
    def ready(self) -> bool:
        return bool(self.access_token)

    async def list_files(self, *, file_hint: str, limit: int = 5) -> list[dict[str, str]]:
        if not self.ready:
            raise RuntimeError("Google Drive metadata execution is not configured.")

        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "pageSize": max(1, int(limit)),
            "fields": "files(id,name,mimeType,modifiedTime),nextPageToken",
            "orderBy": "modifiedTime desc",
        }
        query_parts = ["trashed = false"]
        if self.folder_id:
            query_parts.append(f"'{self.folder_id}' in parents")
        if str(file_hint or "").strip():
            safe_hint = str(file_hint).replace("'", "\\'")
            query_parts.append(f"name contains '{safe_hint[:40]}'")
        params["q"] = " and ".join(query_parts)
        url = f"{self.base_url}/files"

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

        files = payload.get("files", [])
        if not isinstance(files, list):
            return []
        bounded: list[dict[str, str]] = []
        for item in files[: max(1, int(limit))]:
            if not isinstance(item, dict):
                continue
            bounded.append(
                {
                    "id": str(item.get("id", "")).strip(),
                    "name": str(item.get("name", "")).strip(),
                    "mime_type": str(item.get("mimeType", "")).strip(),
                    "modified_time": str(item.get("modifiedTime", "")).strip(),
                }
            )
        return bounded
