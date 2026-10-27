"""Model access: a protocol, a deterministic mock and an unused Azure stub.

No keys live here. The Azure client reads its endpoint and deployment from
environment variables and authenticates with a managed identity or Key Vault
secret supplied by the host once a founder has set up Azure (needs-human).
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from .schemas import RECIPE_ALLOW_LIST


class ModelError(Exception):
    """Recoverable model failure; the job can be retried or resumed."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code


class ModelTimeout(ModelError):
    def __init__(self, message: str = "") -> None:
        super().__init__("MODEL_TIMEOUT", message)


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
    """Stub for Azure AI Foundry. Not wired in; do not call until Azure exists."""

    ENDPOINT_ENV = "SEWSURE_AI_FOUNDRY_ENDPOINT"
    DEPLOYMENT_ENV = "SEWSURE_AI_FOUNDRY_DEPLOYMENT"

    def __init__(self, endpoint: str | None = None, deployment: str | None = None) -> None:
        self.endpoint = endpoint or os.environ.get(self.ENDPOINT_ENV, "")
        self.deployment = deployment or os.environ.get(self.DEPLOYMENT_ENV, "")
        if not self.endpoint or not self.deployment:
            raise ModelError(
                "MODEL_NOT_CONFIGURED",
                f"set {self.ENDPOINT_ENV} and {self.DEPLOYMENT_ENV}",
            )

    def complete(self, request: ModelRequest) -> ModelResponse:
        raise NotImplementedError(
            "Azure AI Foundry is not set up yet. Wire the SDK here with structured "
            "outputs (response_format=json_schema) and a credential from Key Vault."
        )


# ---------------------------------------------------------------- mock ----

Responder = Callable[[ModelRequest], str]

_CROP_PATTERNS = (
    ("very_cropped", r"very cropped|super cropped|bra[- ]?length|above the ribs"),
    ("cropped", r"\bcrop(ped)?\b|belly|navel|above the waist"),
    ("slightly_shorter", r"slightly shorter|a bit shorter|little shorter|shorten the hem|hip[- ]?length"),
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
        ops = []
        if attrs["crop_length"] != "none" and "shirt_crop_hem" in allowed:
            ops.append(("shirt_crop_hem", {"crop_level": attrs["crop_length"]}))
        if attrs["waist_shaping"] != "none" and "shirt_waist_darts" in allowed:
            ops.append(("shirt_waist_darts", {"shaping": attrs["waist_shaping"]}))
        if attrs["sleeve_style"] != "unchanged" and "shirt_short_sleeve" in allowed:
            ops.append(("shirt_short_sleeve", {"sleeve_length": attrs["sleeve_style"]}))
        candidates: list[dict[str, Any]] = []
        if ops:
            candidates.append({"operations": [{"recipe_id": r, "params": p} for r, p in ops]})
            # one notch less demanding on every operation
            eased = []
            for r, p in ops:
                ((name, level),) = p.items()
                levels = RECIPE_ALLOW_LIST[r][name]
                eased.append({"recipe_id": r, "params": {name: levels[max(0, levels.index(level) - 1)]}})
            candidates.append({"operations": eased})
            # the single most demanding operation alone
            r, p = ops[0]
            candidates.append({"operations": [{"recipe_id": r, "params": p}]})
        return json.dumps({"candidates": candidates})
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
