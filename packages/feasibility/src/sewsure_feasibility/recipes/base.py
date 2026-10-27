"""Recipe description and the outcome a recipe's geometry check returns."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from sewsure_feasibility.models import FailureCode, Garment


@dataclass(frozen=True)
class GeometryOutcome:
    failure_codes: tuple[FailureCode, ...] = ()
    residuals_mm: Mapping[str, float] = field(default_factory=dict[str, float])
    cut_mark_mm: float | None = None
    uncertainty_flags: tuple[str, ...] = ()
    details: tuple[str, ...] = ()
    suggested_alternatives: tuple[str, ...] = ()


GeometryCheck = Callable[[Garment, Mapping[str, float], Mapping[str, float]], GeometryOutcome]


@dataclass(frozen=True)
class Recipe:
    recipe_id: str
    version: str
    supported_categories: frozenset[str]
    supported_materials: frozenset[str]
    required_dimensions: tuple[str, ...]
    required_params: tuple[str, ...]
    # (min_mm, max_mm) plausible range, keyed by measurement or param name.
    plausible_ranges_mm: Mapping[str, tuple[float, float]]
    check: GeometryCheck
