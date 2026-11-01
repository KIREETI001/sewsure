"""Model access: a protocol, a deterministic mock and an unused Azure stub.

No keys live here. The Azure client reads its endpoint and deployment from
environment variables and authenticates with a managed identity or Key Vault
secret supplied by the host once a founder has set up Azure (needs-human).
"""

from __future__ import annotations

import json
import os
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from sewsure_contracts.ai_candidate_proposal_schema import AiCandidateProposal

from .azure_http import Transport, bearer_token, post_json, urllib_transport
from .errors import ModelError, ModelTimeout
from .schemas import INSPIRATION_SCHEMA, RECIPE_ALLOW_LIST


@dataclass(frozen=True)
class ModelRequest:
    stage: str  # "B" or "D"
    system_prompt: str
    user_payload: dict[str, Any]  # already minimised: no names, emails, body data
    schema_name: str
    prompt_version: str


@dataclass(frozen=True)
class ModelResponse:
    text: str
    deployment: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0


class ModelClient(Protocol):
    def complete(self, request: ModelRequest) -> ModelResponse: ...


class AzureFoundryClient:
    """Azure AI Foundry chat completions with JSON-schema structured output.

    Configured only through environment variables; nothing is read until the
    object is built, and nothing here calls Azure at import time.

    SEWSURE_AI_FOUNDRY_ENDPOINT    e.g. https://<resource>.services.ai.azure.com
    SEWSURE_AI_FOUNDRY_DEPLOYMENT  the model deployment name
    SEWSURE_AI_FOUNDRY_API_KEY     optional; injected from Key Vault. Without it,
                                   an Entra ID token (managed identity) is used.
    SEWSURE_AI_PRICE_IN_PER_1K / SEWSURE_AI_PRICE_OUT_PER_1K  optional USD, for the cost log.
    """

    ENDPOINT_ENV = "SEWSURE_AI_FOUNDRY_ENDPOINT"
    DEPLOYMENT_ENV = "SEWSURE_AI_FOUNDRY_DEPLOYMENT"
    API_KEY_ENV = "SEWSURE_AI_FOUNDRY_API_KEY"
    API_VERSION = "2024-10-21"
    SCOPE = "https://cognitiveservices.azure.com/.default"

    def __init__(
        self,
        endpoint: str | None = None,
        deployment: str | None = None,
        *,
        timeout_s: float = 30.0,
        transport: Transport | None = None,
    ) -> None:
        self.endpoint = (endpoint or os.environ.get(self.ENDPOINT_ENV, "")).rstrip("/")
        self.deployment = deployment or os.environ.get(self.DEPLOYMENT_ENV, "")
        if not self.endpoint or not self.deployment:
            raise ModelError(
                "MODEL_NOT_CONFIGURED", f"set {self.ENDPOINT_ENV} and {self.DEPLOYMENT_ENV}"
            )
        self._timeout = timeout_s
        self._transport = transport or urllib_transport

    @classmethod
    def configured(cls) -> bool:
        return bool(os.environ.get(cls.ENDPOINT_ENV) and os.environ.get(cls.DEPLOYMENT_ENV))

    def _auth(self) -> dict[str, str]:
        key = os.environ.get(self.API_KEY_ENV)
        return {"api-key": key} if key else {"Authorization": f"Bearer {bearer_token(self.SCOPE)}"}

    def complete(self, request: ModelRequest) -> ModelResponse:
        url = (
            f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions"
            f"?api-version={self.API_VERSION}"
        )
        body: dict[str, Any] = {
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": json.dumps(request.user_payload)},
            ],
            "temperature": 0,
            "max_tokens": 800,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": request.schema_name,
                    "schema": output_schema(request.stage),
                },
            },
        }
        started = time.perf_counter()
        data = post_json(
            url, body, auth_header=self._auth(), transport=self._transport, timeout=self._timeout
        )
        latency = (time.perf_counter() - started) * 1000
        try:
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            tin, tout = int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ModelError("AZURE_BAD_RESPONSE") from exc
        if not isinstance(text, str):
            raise ModelError("AZURE_BAD_RESPONSE")
        cost = tin / 1000 * float(
            os.environ.get("SEWSURE_AI_PRICE_IN_PER_1K", 0)
        ) + tout / 1000 * float(os.environ.get("SEWSURE_AI_PRICE_OUT_PER_1K", 0))
        return ModelResponse(text, self.deployment, tin, tout, latency, cost)


def output_schema(stage: str) -> dict[str, Any]:
    """JSON schema sent to the service for structured output. Stage D uses the contract model."""
    if stage == "B":
        return INSPIRATION_SCHEMA
    if stage == "D":
        return AiCandidateProposal.model_json_schema()
    raise ModelError("UNKNOWN_STAGE", stage)


# ---------------------------------------------------------------- mock ----

Responder = Callable[[ModelRequest], str]

_CROP_PATTERNS = (
    ("very_cropped", r"very cropped|super cropped|bra[- ]?length|above the ribs"),
    ("cropped", r"\bcrop(ped)?\b|belly|navel|above the waist"),
    (
        "slightly_shorter",
        r"slightly shorter|a bit shorter|little shorter|shorten the hem|hip[- ]?length",
    ),
)
_SLEEVE_PATTERNS = (
    ("cap", r"cap sleeve"),
    ("short", r"short sleeve|sleeveless|shorter sleeves|roll(ed)? sleeve"),
)
_SHAPING_PATTERNS = (
    ("moderate", r"very fitted|cinched|hourglass|nipped|tight waist"),
    ("light", r"waist shaping|fitted|more shape|taper"),
)


def _first_match(patterns: tuple[tuple[str, str], ...], text: str, default: str) -> str:
    for label, pat in patterns:
        if re.search(pat, text):
            return label
    return default


def default_responder(request: ModelRequest) -> str:
    """Keyword rules standing in for a model. Deterministic, no network."""
    if request.stage == "B":
        text = str(request.user_payload.get("inspiration_text", "")).lower()
        attrs = {
            "crop_length": _first_match(_CROP_PATTERNS, text, "none"),
            "waist_shaping": _first_match(_SHAPING_PATTERNS, text, "none"),
            "sleeve_style": _first_match(_SLEEVE_PATTERNS, text, "unchanged"),
            "closure_preservation": "remove button" not in text and "no buttons" not in text,
        }
        return json.dumps(attrs)
    if request.stage == "D":
        attrs = request.user_payload["attributes"]
        allowed = request.user_payload["allowed_recipes"]
        proposals: list[dict[str, Any]] = []
        recipe = "woven_shirt_crop_v1"
        if attrs["crop_length"] != "none" and recipe in allowed:
            levels = RECIPE_ALLOW_LIST[recipe]["crop_level"]
            top = levels.index(attrs["crop_length"])
            # the requested level, then up to two notches less demanding
            for idx in range(top, max(top - 3, -1), -1):
                proposals.append({"recipe_id": recipe, "parameters": {"crop_level": levels[idx]}})
        return json.dumps({"proposals": proposals})
    raise ModelError("MOCK_UNKNOWN_STAGE", request.stage)


class MockModelClient:
    """Deterministic ModelClient.

    `scripted` maps a stage ("B"/"D") to raw text returned verbatim, so tests and
    the eval harness can feed malformed, unknown-ID or injection-compromised
    output through the real validation path. Keys may also be exceptions to raise.
    """

    deployment = "mock-deterministic-v0"

    def __init__(
        self,
        responder: Responder = default_responder,
        scripted: dict[str, str | Exception] | None = None,
    ) -> None:
        self._responder = responder
        self._scripted = scripted or {}
        self.calls: list[ModelRequest] = []

    def complete(self, request: ModelRequest) -> ModelResponse:
        self.calls.append(request)
        scripted = self._scripted.get(request.stage)
        if isinstance(scripted, Exception):
            raise scripted
        text = scripted if scripted is not None else self._responder(request)
        return ModelResponse(
            text=text,
            deployment=self.deployment,
            input_tokens=len(str(request.user_payload)) // 4,
            output_tokens=len(text) // 4,
            latency_ms=0.0,
            cost_usd=0.0,
        )


__all__ = [
    "AzureFoundryClient",
    "MockModelClient",
    "ModelClient",
    "ModelError",
    "ModelRequest",
    "ModelResponse",
    "ModelTimeout",
    "default_responder",
]
