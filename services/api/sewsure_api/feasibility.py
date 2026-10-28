"""Seam to packages/feasibility. The API never computes geometry or decides design state.

Shapes follow contract v1 (PR #15): `checks` is a ConstraintResult-shaped dict, `geometry_mm`
holds engine-computed `*_mm` values, `status` is a DesignState name. Replace the dataclasses
with the real `sewsure_feasibility` / `sewsure_contracts` types when both are importable.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol

from sewsure_api.models import DesignState


@dataclass(frozen=True)
class EvaluationRequest:
    recipe_id: str
    parameters: dict[str, Any]
    # Garment and measurement snapshots the engine needs. Populated once the garment and
    # measurement routes exist; kept opaque here so no body measurements are interpreted.
    inputs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationResult:
    status: DesignState
    checks: dict[str, Any]  # ConstraintResult-shaped; stored whole, never reduced to a bool
    geometry_mm: dict[str, float]
    engine_version: str
    recipe_version: str | None
    inputs_hash: str


class FeasibilityChecker(Protocol):
    def allowed_parameter_keys(self, recipe_id: str) -> frozenset[str] | None:
        """Allow-listed parameter keys for a reviewed recipe, or None if the recipe is unknown."""
        ...

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult: ...

    def supersede(self, previous: DesignState) -> DesignState:
        """State a parent takes when a newer revision replaces it (engine rule)."""
        ...


class UnconfiguredFeasibility:
    """Placeholder until packages/feasibility is wired in. No recipe is reviewable, so every
    recipe is unknown and no design can be created: nothing can reach a passing state."""

    def allowed_parameter_keys(self, recipe_id: str) -> frozenset[str] | None:
        return None

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        raise NotImplementedError("packages/feasibility is not wired in")

    def supersede(self, previous: DesignState) -> DesignState:
        raise NotImplementedError("packages/feasibility is not wired in")
