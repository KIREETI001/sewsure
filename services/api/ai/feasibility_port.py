"""The only door to the feasibility engine.

Implemented by an adapter over packages/feasibility (N1, PR #12 head 8d6db44):
`evaluate(garment, measurements, recipe_id, params, ...) -> ConstraintResult`.
The adapter (not this package) loads the garment and confirmed measurements for
`revision_context_id`, maps the AI's named levels to the recipe's mm parameters
(`finished_length_mm`, `hem_allowance_mm`) and calls `evaluate`. That
level-to-mm mapping has no owner yet.

This module only relays the engine's verdict. All five design states from
contract 1.0.0-draft.2 pass through unchanged. A value outside those five, or an
engine exception, becomes FAILED_CHECKS (fail closed). Failure codes use the
contract `FailureCode` names.
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict

PASS = "PASS_SUPPORTED_CHECKS"
NEEDS_INPUT = "NEEDS_INPUT"
FAILED = "FAILED_CHECKS"
IDEA_ONLY = "IDEA_ONLY"
SUPERSEDED = "SUPERSEDED"
ENGINE_STATES = frozenset({PASS, NEEDS_INPUT, FAILED, IDEA_ONLY, SUPERSEDED})


class FeasibilityRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    recipe_id: str
    parameters: dict[str, str | bool]  # AI levels; the adapter maps them to mm
    garment_category: str  # contract category, e.g. "woven_shirt"
    fabric_family: str  # contract fabric family, e.g. "woven"
    revision_context_id: str  # opaque; the adapter resolves garment and measurements


class FeasibilityResult(BaseModel):
    """The subset of the engine's ConstraintResult that the pipeline reads."""

    model_config = ConfigDict(frozen=True)

    status: str  # DesignState
    failure_codes: tuple[str, ...] = ()
    missing_dimensions: tuple[str, ...] = ()
    uncertainty_flags: tuple[str, ...] = ()


class FeasibilityChecker(Protocol):
    def check(self, request: FeasibilityRequest) -> FeasibilityResult: ...


def normalise(result: FeasibilityResult) -> FeasibilityResult:
    if result.status in ENGINE_STATES:
        return result
    return FeasibilityResult(status=FAILED, failure_codes=("UNRECOGNISED_ENGINE_STATUS",))
