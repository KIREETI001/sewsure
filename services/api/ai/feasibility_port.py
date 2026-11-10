"""The call shape between the pipeline and the feasibility engine.

The pipeline hands over a recipe ID, named levels and an opaque context ID, and
gets back the engine's own `ConstraintResult` unchanged. It never builds,
edits or upgrades a result or a design state. See `engine_adapter.py` for the
implementation over `sewsure_feasibility.evaluate`.
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict
from sewsure_feasibility import ConstraintResult


class FeasibilityRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    recipe_id: str
    parameters: dict[str, str | bool]  # AI levels; the adapter maps them to mm
    revision_context_id: str  # opaque; the context provider resolves garment and measurements


class FeasibilityChecker(Protocol):
    def check(self, request: FeasibilityRequest) -> ConstraintResult: ...
