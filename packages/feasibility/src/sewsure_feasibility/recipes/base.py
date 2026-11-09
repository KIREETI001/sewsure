"""Recipe description and the outcome a recipe's geometry check returns."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from sewsure_feasibility.models import CheckOutcome, FailureCode, Garment, Residual


@dataclass(frozen=True)
class GeometryOutcome:
    failure_codes: tuple[FailureCode, ...] = ()
    residuals: tuple[Residual, ...] = ()
    checks: tuple[CheckOutcome, ...] = ()
    cut_mark_mm: float | None = None
    uncertainty_flags: tuple[str, ...] = ()
    details: tuple[str, ...] = ()


GeometryCheck = Callable[[Garment, Mapping[str, float], Mapping[str, float]], GeometryOutcome]
GarmentInputCheck = Callable[[Garment], tuple[str, ...]]


@dataclass(frozen=True)
class ConsistencyPair:
    """``flat_key * factor`` should match ``other_key`` within ``tolerance_fraction``."""

    flat_key: str
    other_key: str
    factor: float
    tolerance_fraction: float


@dataclass(frozen=True)
class Recipe:
    recipe_id: str
    version: str
    supported_categories: frozenset[str]
    supported_materials: frozenset[str]
    required_dimensions: tuple[str, ...]
    required_params: tuple[str, ...]
    optional_params: frozenset[str]
    # (min_mm, max_mm) plausible range, keyed by measurement or param name.
    plausible_ranges_mm: Mapping[str, tuple[float, float]]
    consistency_pairs: tuple[ConsistencyPair, ...]
    # Geometry inputs the recipe needs from the garment; returns names of those missing.
    missing_garment_inputs: GarmentInputCheck
    check: GeometryCheck
