"""Small HTTP helper shared by the Azure clients. Standard library only.

Credentials are never in code. Each client takes, in order: an API key from an
environment variable the host injects from Key Vault, or an Entra ID bearer token
from `azure-identity` (managed identity in Azure, `az login` locally), imported
only when needed. Neither value is logged or put into an error message.
"""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from .errors import ModelError, ModelTimeout

# (url, headers, body, timeout_s) -> (status, response_body)
Transport = Callable[[str, dict[str, str], bytes, float], tuple[int, bytes]]


def urllib_transport(url: str, headers: dict[str, str], body: bytes, timeout: float):
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (https endpoint from env)
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except TimeoutError as exc:
        raise ModelTimeout() from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, (TimeoutError, socket.timeout)):
            raise ModelTimeout() from exc
        raise ModelError("AZURE_UNREACHABLE") from exc


def bearer_token(scope: str) -> str:
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError as exc:
        raise ModelError(
            "AZURE_IDENTITY_MISSING", "install azure-identity or set the API key variable"
        ) from exc
    try:
        return DefaultAzureCredential().get_token(scope).token
    except Exception as exc:  # credential errors vary; do not leak their text
        raise ModelError("AZURE_AUTH_FAILED") from exc


def post_json(
    url: str,
    payload: dict[str, Any],
    *,
    auth_header: dict[str, str],
    transport: Transport,
    timeout: float,
) -> dict[str, Any]:
    headers = {"Content-Type": "application/json", **auth_header}
    status, raw = transport(url, headers, json.dumps(payload).encode(), timeout)
    if status in (408, 429) or status >= 500:
        raise ModelError(f"AZURE_HTTP_{status}")
    if status >= 400:
        raise ModelError(f"AZURE_HTTP_{status}")
    try:
        data = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise ModelError("AZURE_BAD_RESPONSE") from exc
    if not isinstance(data, dict):
        raise ModelError("AZURE_BAD_RESPONSE")
    return data
