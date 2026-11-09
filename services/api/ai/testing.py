"""Test doubles. Not geometry: verdicts come from rules written down per test case,
standing in for packages/feasibility so pipeline plumbing can be measured."""

from __future__ import annotations

from typing import Any

from .feasibility_port import FAILED, FeasibilityRequest, FeasibilityResult


class RuleFeasibilityChecker:
    """Each rule: {recipe_id, params (optional subset), status, codes, missing}.
    First matching rule wins; no rule means FAILED_CHECKS (fail closed)."""

    def __init__(self, rules: list[dict[str, Any]]) -> None:
        self.rules = rules
        self.calls = 0

    def verdict(self, recipe_id: str, parameters: dict[str, Any]) -> FeasibilityResult:
        for r in self.rules:
            if r["recipe_id"] == recipe_id and all(
                parameters.get(k) == v for k, v in r.get("params", {}).items()
            ):
                return FeasibilityResult(
                    status=r["status"],
                    failure_codes=tuple(r.get("codes", ())),
                    missing_dimensions=tuple(r.get("missing", ())),
                )
        return FeasibilityResult(status=FAILED, failure_codes=("NO_RULE_FOR_CANDIDATE",))

    def check(self, request: FeasibilityRequest) -> FeasibilityResult:
        self.calls += 1
        return self.verdict(request.recipe_id, request.parameters)
