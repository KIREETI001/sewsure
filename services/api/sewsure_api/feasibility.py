"""Seam to packages/feasibility. The API never computes geometry or decides design state."""

from typing import Any, Protocol

from sewsure_api.models import DesignState


class FeasibilityChecker(Protocol):
    def evaluate(self, recipe_id: str, parameters: dict[str, Any]) -> DesignState:
        """Return the state decided by the feasibility engine for this revision."""
        ...


class UnconfiguredFeasibility:
    """Placeholder until packages/feasibility is wired in. Nothing has been checked, so the
    only honest answer is IDEA_ONLY; it never reports a passing state."""

    def evaluate(self, recipe_id: str, parameters: dict[str, Any]) -> DesignState:
        return DesignState.IDEA_ONLY
