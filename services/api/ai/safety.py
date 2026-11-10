"""User-text screening before anything reaches the model.

Production implementation: Azure AI Content Safety Prompt Shields (user prompt
attack detection). Not wired until a founder creates the resource.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Protocol

from .azure_http import Transport, bearer_token, post_json, urllib_transport
from .errors import ModelError


@dataclass(frozen=True)
class SafetyVerdict:
    allowed: bool
    reason: str = ""  # a short code, never the user text


class SafetyScreen(Protocol):
    def screen(self, user_text: str) -> SafetyVerdict: ...


class AzurePromptShieldsScreen:
    """Azure AI Content Safety Prompt Shields (user prompt attack detection).

    SEWSURE_CONTENT_SAFETY_ENDPOINT   e.g. https://<resource>.cognitiveservices.azure.com
    SEWSURE_CONTENT_SAFETY_API_KEY    optional; injected from Key Vault. Without it,
                                      an Entra ID token (managed identity) is used.

    If the service cannot be reached the screen raises ModelError and the pipeline
    fails the job (recoverable). It never answers "allowed" without an answer.
    """

    ENDPOINT_ENV = "SEWSURE_CONTENT_SAFETY_ENDPOINT"
    API_KEY_ENV = "SEWSURE_CONTENT_SAFETY_API_KEY"
    API_VERSION = "2024-09-01"
    SCOPE = "https://cognitiveservices.azure.com/.default"

    def __init__(
        self,
        endpoint: str | None = None,
        *,
        timeout_s: float = 10.0,
        transport: Transport | None = None,
    ) -> None:
        self.endpoint = (endpoint or os.environ.get(self.ENDPOINT_ENV, "")).rstrip("/")
        if not self.endpoint:
            raise ModelError("SAFETY_NOT_CONFIGURED", f"set {self.ENDPOINT_ENV}")
        self._timeout = timeout_s
        self._transport = transport or urllib_transport

    @classmethod
    def configured(cls) -> bool:
        return bool(os.environ.get(cls.ENDPOINT_ENV))

    def _auth(self) -> dict[str, str]:
        key = os.environ.get(self.API_KEY_ENV)
        if key:
            return {"Ocp-Apim-Subscription-Key": key}
        return {"Authorization": f"Bearer {bearer_token(self.SCOPE)}"}

    def screen(self, user_text: str) -> SafetyVerdict:
        url = f"{self.endpoint}/contentsafety/text:shieldPrompt?api-version={self.API_VERSION}"
        data = post_json(
            url,
            {"userPrompt": user_text, "documents": []},
            auth_header=self._auth(),
            transport=self._transport,
            timeout=self._timeout,
        )
        try:
            attack = data["userPromptAnalysis"]["attackDetected"]
        except (KeyError, TypeError) as exc:
            raise ModelError("SAFETY_BAD_RESPONSE") from exc
        if not isinstance(attack, bool):
            raise ModelError("SAFETY_BAD_RESPONSE")
        return SafetyVerdict(False, "PROMPT_ATTACK_SUSPECTED") if attack else SafetyVerdict(True)


class AllowAllScreen:
    """Used by the eval harness to test the layers behind the screen."""

    def screen(self, user_text: str) -> SafetyVerdict:
        return SafetyVerdict(True)


_MOCK_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"ignore (all |any )?(previous|prior|above) (instructions|rules)",
        r"disregard .{0,30}(instructions|rules|constraints)",
        r"(system|developer) (prompt|message)",
        r"you are now",
        r"reveal .{0,30}(prompt|key|secret)",
        r"mark (it|this|the design) as (safe|passed|approved)",
        r"(skip|bypass|override) .{0,30}(check|feasibility|validation)",
        r"```",
    )
)


class MockSafetyScreen:
    """Keyword stand-in for Prompt Shields. It is NOT evidence of Prompt Shields
    detection rates; real numbers need the Azure service and the same cases."""

    def screen(self, user_text: str) -> SafetyVerdict:
        for pat in _MOCK_PATTERNS:
            if pat.search(user_text):
                return SafetyVerdict(False, "PROMPT_ATTACK_SUSPECTED")
        return SafetyVerdict(True)
