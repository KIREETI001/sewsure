"""FeasibilityChecker over the real `sewsure_feasibility.evaluate`.

A `ContextProvider` (K2: loads the revision's garment and confirmed measurements
from storage) supplies the garment record. The result of `evaluate` is returned
unchanged.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from sewsure_feasibility import Garment, Measurement, evaluate

from .feasibility_port import FeasibilityRequest
from .level_map import engine_params


@dataclass(frozen=True)
class RevisionContext:
    garment: Garment
    measurements: Mapping[str, Measurement]


class ContextProvider(Protocol):
    def load(self, revision_context_id: str) -> RevisionContext: ...


class EvaluateChecker:
    def __init__(self, provider: ContextProvider) -> None:
        self._provider = provider

    def check(self, request: FeasibilityRequest):
        ctx = self._provider.load(request.revision_context_id)
        length = ctx.measurements.get("shoulder_to_hem")
        params = engine_params(
            request.recipe_id, request.parameters, length.value_mm if length else None
        )
        return evaluate(
            ctx.garment,
            ctx.measurements,
            request.recipe_id,
            params,
            revision_ref=request.revision_context_id,
        )
