"""The only door to the feasibility engine.

Implemented by packages/feasibility (N1). This module defines the call shape and
nothing else: the pipeline never computes geometry and never sets a design
state. It relays the engine's verdict verbatim, and any status it does not
recognise is treated as FAILED_CHECKS (fail closed).
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict

from .schemas import Candidate

# Mirrors the engine's state names (root CLAUDE.md non-negotiable 2). The
# engine is the only producer; this module only recognises them.
PASS = "PASS_SUPPORTED_CHECKS"
NEEDS_INPUT = "NEEDS_INPUT"
FAILED = "FAILED_CHECKS"
ENGINE_STATES = frozenset({PASS, NEEDS_INPUT, FAILED})


class FeasibilityRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    candidate: Candidate
    garment_class: str
    material: str
    revision_context_id: str  # opaque; the engine resolves measurements itself


class FeasibilityResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    failure_codes: tuple[str, ...] = ()
    missing_inputs: tuple[str, ...] = ()


class FeasibilityChecker(Protocol):
    def check(self, request: FeasibilityRequest) -> FeasibilityResult: ...


def normalise(result: FeasibilityResult) -> FeasibilityResult:
    if result.status in ENGINE_STATES:
        return result
    return FeasibilityResult(status=FAILED, failure_codes=("UNRECOGNISED_ENGINE_STATUS",))
