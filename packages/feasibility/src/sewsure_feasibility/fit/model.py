"""Fit output (blueprint section 7.1) using the ``FitAssessment`` contract field names.

A fit label is an estimate from flat measurements. It is never a statement that a garment
fits or is comfortable, and it never sets a design state (only ``engine.evaluate`` does).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

MAX_WARNING_CHARS = 200  # contract: FitAssessment.warnings[].maxLength


class FitLabel(StrEnum):
    """Values are the contract ``FitAssessment.fit_label`` enum."""

    CLOSE = "close_estimate"
    REGULAR = "regular_estimate"
    RELAXED = "relaxed_estimate"
    OVERSIZED = "oversized_estimate"
    INSUFFICIENT_EASE = "insufficient_ease"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FitAssessment:
    body_profile_id: str
    revision_id: str
    measurements_mm: dict[str, float]  # body dimensions used
    estimated_finished_mm: dict[str, float]  # finished garment circumferences
    ease_mm: dict[str, float]  # finished circumference - body circumference
    fit_label: FitLabel
    warnings: tuple[str, ...]
    # Engine-side fields, deliberately not in the contract payload:
    uncertainty_mm: float | None = None
    ease_config_provisional: bool = True
    recipe_id: str | None = None

    def __post_init__(self) -> None:
        for w in self.warnings:
            if len(w) > MAX_WARNING_CHARS:
                raise ValueError(f"warning exceeds {MAX_WARNING_CHARS} chars: {w!r}")

    def to_contract_dict(self) -> dict[str, Any]:
        """Exactly the contract ``FitAssessment`` shape (no extra keys)."""
        return {
            "body_profile_id": self.body_profile_id,
            "revision_id": self.revision_id,
            "measurements_mm": dict(self.measurements_mm),
            "estimated_finished_mm": dict(self.estimated_finished_mm),
            "ease_mm": dict(self.ease_mm),
            "fit_label": self.fit_label.value,
            "warnings": list(self.warnings),
        }
