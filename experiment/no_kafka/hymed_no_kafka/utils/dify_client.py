from __future__ import annotations

import os
from typing import Any, AsyncIterator

import aiohttp


class DifyAPIError(RuntimeError):
    def __init__(self, status: int, message: str, payload: Any | None = None):
        super().__init__(f"Dify API error {status}: {message}")
        self.status = status
        self.message = message
        self.payload = payload


class DifyClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,
        timeout: int = 30,
        session: aiohttp.ClientSession | None = None,
    ):
        self._base_url = self._normalize_base_url(base_url)
        self._api_key = api_key
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = session

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        base_url = base_url.rstrip("/")
        if base_url.endswith("/v1"):
            return base_url
        return f"{base_url}/v1"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "DifyClient":
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        url = f"{self._base_url}{path}"
        session = await self._get_session()
        merged_headers = self._headers()
        if headers:
            merged_headers.update(headers)
        async with session.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            headers=merged_headers,
        ) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if resp.status >= 400:
                if "application/json" in content_type:
                    payload = await resp.json()
                    message = str(payload)
                else:
                    payload = await resp.text()
                    message = payload
                raise DifyAPIError(resp.status, message, payload)
            if "application/json" in content_type:
                return await resp.json()
            return await resp.text()

    async def send_message(
        self,
        query: str,
        *,
        user: str,
        inputs: dict[str, Any] | None = None,
        conversation_id: str | None = None,
        response_mode: str = "blocking",
        files: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "query": query,
            "user": user,
            "inputs": inputs or {},
            "response_mode": response_mode,
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id
        if files:
            payload["files"] = files
        if response_mode == "streaming":
            raise ValueError("send_message does not support streaming mode.")
        return await self._request("POST", "/chat-messages", json=payload)

    async def upload_file(self, file_path: str, *, user: str) -> dict[str, Any]:
        filename = os.path.basename(file_path)
        form = aiohttp.FormData()
        form.add_field("user", user)
        with open(file_path, "rb") as f:
            form.add_field("file", f, filename=filename, content_type="application/octet-stream")
            return await self._request("POST", "/files/upload", data=form)

    async def send_message_stream(
        self,
        query: str,
        *,
        user: str,
        inputs: dict[str, Any] | None = None,
        conversation_id: str | None = None,
        files: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[bytes]:
        payload: dict[str, Any] = {
            "query": query,
            "user": user,
            "inputs": inputs or {},
            "response_mode": "streaming",
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id
        if files:
            payload["files"] = files

        url = f"{self._base_url}/chat-messages"
        session = await self._get_session()
        async with session.post(url, json=payload, headers=self._headers()) as resp:
            if resp.status >= 400:
                content_type = resp.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    payload_err = await resp.json()
                    message = str(payload_err)
                else:
                    payload_err = await resp.text()
                    message = payload_err
                raise DifyAPIError(resp.status, message, payload_err)
            async for chunk in resp.content.iter_chunked(1024):
                yield chunk


__all__ = ["DifyClient", "DifyAPIError"]

