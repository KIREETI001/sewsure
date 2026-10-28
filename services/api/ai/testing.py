"""Test doubles. Not geometry: verdicts come from rules written down per test case,
standing in for packages/feasibility so pipeline plumbing can be measured."""

from __future__ import annotations

from typing import Any

from .feasibility_port import (
    FAILED,
    IDEA_ONLY,
    NEEDS_INPUT,
    PASS,
    FeasibilityRequest,
    FeasibilityResult,
)


class RuleFeasibilityChecker:
    """Each rule: {recipe_id, params (optional subset), status, codes, missing}.
    First matching rule wins per operation; no rule means FAILED (fail closed)."""

    def __init__(self, rules: list[dict[str, Any]]) -> None:
        self.rules = rules
        self.calls = 0

    def _op_verdict(self, recipe_id: str, params: dict[str, str]) -> FeasibilityResult:
        for r in self.rules:
            if r["recipe_id"] == recipe_id and all(
                params.get(k) == v for k, v in r.get("params", {}).items()
            ):
                return FeasibilityResult(
                    status=r["status"],
                    failure_codes=tuple(r.get("codes", ())),
                    missing_inputs=tuple(r.get("missing", ())),
                )
        return FeasibilityResult(status=FAILED, failure_codes=("NO_RULE_FOR_OPERATION",))

    def check(self, request: FeasibilityRequest) -> FeasibilityResult:
        self.calls += 1
        verdicts = [
            self._op_verdict(op.recipe_id, op.params) for op in request.candidate.operations
        ]
        codes = tuple(sorted({c for v in verdicts for c in v.failure_codes}))
        missing = tuple(sorted({m for v in verdicts for m in v.missing_inputs}))
        if any(v.status == FAILED for v in verdicts):
            return FeasibilityResult(status=FAILED, failure_codes=codes, missing_inputs=missing)
        if any(v.status == IDEA_ONLY for v in verdicts):
            return FeasibilityResult(status=IDEA_ONLY, failure_codes=codes)
        if any(v.status == NEEDS_INPUT for v in verdicts):
            return FeasibilityResult(
                status=NEEDS_INPUT, failure_codes=codes, missing_inputs=missing
            )
        if all(v.status == PASS for v in verdicts):
            return FeasibilityResult(status=PASS)
        return FeasibilityResult(
            status="UNKNOWN", failure_codes=codes
        )  # normalised to FAILED upstream
