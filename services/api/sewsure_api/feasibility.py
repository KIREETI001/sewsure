"""Seam to packages/feasibility. The API never computes geometry or decides design state.

`FeasibilityChecker.evaluate` has the same shape as N1's `sewsure_feasibility.evaluate`
(PR #12, 8d6db44): `(garment, measurements, recipe_id, params, *, revision_ref, checked_at)`
returning a ConstraintResult. `ConstraintResult` below mirrors the fields of N1's dataclass
that the API persists. When both packages are importable, replace it with the real type and
implement the checker as a thin adapter.
"""

import dataclasses
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from sewsure_api.models import DesignState


@dataclass(frozen=True)
class ConstraintResult:
    """Subset of N1's ConstraintResult (field names follow contract 1.0.0-draft.2)."""

    status: DesignState
    failure_codes: Sequence[Any]
    residuals: Sequence[Any]
    missing_dimensions: Sequence[str]
    uncertainty_flags: Sequence[str]
    checks: Sequence[Any]
    alternatives: Sequence[Any]
    cut_mark_mm: float | None
    recipe_id: str
    recipe_version: str | None
    engine_version: str
    checked_at: datetime
    input_fingerprint: str

    @property
    def hard_pass(self) -> bool:
        return self.status is DesignState.PASS_SUPPORTED_CHECKS


class FeasibilityChecker(Protocol):
    def allowed_parameter_keys(self, recipe_id: str) -> frozenset[str] | None:
        """Allow-listed parameter keys for a reviewed recipe, or None if the recipe is unknown."""
        ...

    def evaluate(
        self,
        garment: Mapping[str, Any],
        measurements: Mapping[str, Any],
        recipe_id: str,
        params: Mapping[str, Any],
        *,
        revision_ref: str | None = None,
        checked_at: datetime | None = None,
    ) -> ConstraintResult: ...

    def supersede_status(self, previous: DesignState) -> DesignState:
        """Status a passed parent takes when a newer revision replaces it. Adapter over N1's
        `supersede(ConstraintResult)`, which returns the whole result."""
        ...


class UnconfiguredFeasibility:
    """Placeholder until packages/feasibility is wired in. No recipe is reviewable, so every
    recipe is unknown and no design can be created: nothing can reach a passing state."""

    def allowed_parameter_keys(self, recipe_id: str) -> frozenset[str] | None:
        return None

    def evaluate(
        self,
        garment: Mapping[str, Any],
        measurements: Mapping[str, Any],
        recipe_id: str,
        params: Mapping[str, Any],
        *,
        revision_ref: str | None = None,
        checked_at: datetime | None = None,
    ) -> ConstraintResult:
        raise NotImplementedError("packages/feasibility is not wired in")

    def supersede_status(self, previous: DesignState) -> DesignState:
        raise NotImplementedError("packages/feasibility is not wired in")


def _plain(value: Any) -> Any:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {k: _plain(v) for k, v in dataclasses.asdict(value).items()}
    if isinstance(value, Mapping):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_plain(v) for v in value]
    return getattr(value, "value", value)  # enums


def checks_json(result: ConstraintResult) -> dict[str, Any]:
    """Contract `ConstraintResult` JSON, stored whole so the app can say why a design failed."""
    return {
        "hard_pass": result.hard_pass,
        "failure_codes": _plain(result.failure_codes),
        "residuals": _plain(result.residuals),
        "missing_dimensions": list(result.missing_dimensions),
        "uncertainty_flags": list(result.uncertainty_flags),
        "checks": _plain(result.checks),
        "alternatives": _plain(result.alternatives),
        "engine_version": result.engine_version,
        "checked_at": result.checked_at.isoformat(),
    }
