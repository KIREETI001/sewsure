"""User-text screening before anything reaches the model.

Production implementation: Azure AI Content Safety Prompt Shields (user prompt
attack detection). Not wired until a founder creates the resource.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SafetyVerdict:
    allowed: bool
    reason: str = ""  # a short code, never the user text


class SafetyScreen(Protocol):
    def screen(self, user_text: str) -> SafetyVerdict: ...


class AzurePromptShieldsScreen:
    """Stub for Azure AI Content Safety Prompt Shields. Not used yet."""

    ENDPOINT_ENV = "SEWSURE_CONTENT_SAFETY_ENDPOINT"

    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint or os.environ.get(self.ENDPOINT_ENV, "")

    def screen(self, user_text: str) -> SafetyVerdict:
        raise NotImplementedError("Content Safety is not set up yet; use MockSafetyScreen.")


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
