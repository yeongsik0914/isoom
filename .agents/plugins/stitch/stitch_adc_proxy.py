#!/usr/bin/env python3
"""STDIO-to-Streamable-HTTP MCP proxy for Google Stitch using GCP ADC.

Eliminates static API keys by authenticating against `https://stitch.googleapis.com/mcp`
with `google.auth.default()` Application Default Credentials.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Optional

import google.auth
import google.auth.transport.requests
import httpx

STITCH_MCP_URL = os.getenv("STITCH_MCP_URL", "https://stitch.googleapis.com/mcp")
CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"


class StitchAdcBridge:
    """Forwards JSON-RPC 2.0 MCP messages over STDIO to Stitch Streamable HTTP."""

    def __init__(self, url: str = STITCH_MCP_URL, timeout: float = 120.0) -> None:
        self.url = url
        self._creds, default_project = google.auth.default(scopes=[CLOUD_PLATFORM_SCOPE])
        self.project_id: Optional[str] = (
            os.getenv("GOOGLE_CLOUD_PROJECT")
            or os.getenv("GCP_PROJECT")
            or os.getenv("GCLOUD_PROJECT")
            or default_project
        )
        self._request = google.auth.transport.requests.Request()
        self._client = httpx.Client(timeout=timeout)
        self._session_id: Optional[str] = None

    def _get_token(self, force_refresh: bool = False) -> str:
        if force_refresh or not self._creds.valid or not self._creds.token:
            self._creds.refresh(self._request)
        return str(self._creds.token)

    def _build_headers(self, force_refresh: bool = False) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._get_token(force_refresh=force_refresh)}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.project_id:
            headers["X-Goog-User-Project"] = self.project_id
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        return headers

    def forward(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Sends a JSON-RPC payload to Stitch and returns parsed JSON-RPC response objects."""
        response = self._client.post(
            self.url,
            headers=self._build_headers(),
            json=payload,
        )
        if response.status_code == 401:
            response = self._client.post(
                self.url,
                headers=self._build_headers(force_refresh=True),
                json=payload,
            )

        session_hdr = response.headers.get("Mcp-Session-Id") or response.headers.get("mcp-session-id")
        if session_hdr:
            self._session_id = session_hdr

        if response.status_code in (202, 204) or not response.text.strip():
            return []

        content_type = response.headers.get("content-type", "").lower()
        if "text/event-stream" in content_type:
            messages: list[dict[str, Any]] = []
            for raw_line in response.text.splitlines():
                line = raw_line.strip()
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if data_str and data_str != "[DONE]":
                        messages.append(json.loads(data_str))
            return messages

        parsed = response.json()
        return parsed if isinstance(parsed, list) else [parsed]


def _write_message(msg: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _write_error(req_id: Any, code: int, message: str) -> None:
    if req_id is None:
        return
    _write_message(
        {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": code, "message": message},
        }
    )


def main() -> int:
    try:
        bridge = StitchAdcBridge()
    except Exception as exc:
        print(
            f"[stitch-mcp] Failed to initialize GCP ADC credentials: {exc}. "
            "Run `gcloud auth application-default login`.",
            file=sys.stderr,
            flush=True,
        )
        return 1

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            _write_error(None, -32700, f"Parse error: {exc}")
            continue

        req_id = payload.get("id") if isinstance(payload, dict) else None
        try:
            responses = bridge.forward(payload)
            for resp in responses:
                _write_message(resp)
        except Exception as exc:
            _write_error(req_id, -32603, f"Stitch ADC bridge error: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
