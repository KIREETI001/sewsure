"""Typed core models (blueprint §5.2). All lengths are millimetres.

Aligned to K1's contract (PR #15): ``DesignState`` and ``FailureCode`` values are the contract
enums, ``Measurement`` mirrors ``MeasurementValue``, and ``ConstraintResult.to_contract_dict()``
emits the contract ``ConstraintResult`` shape. ``FabricPanel``/``Zone``/``Garment`` are engine
inputs with no contract record yet.
"""

from __future__ import annotations

import dataclasses
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Self

import numpy as np
from shapely.geometry import Polygon

Point = tuple[float, float]


class DesignState(StrEnum):
    """Design states. Only this package may produce them (CLAUDE.md non-negotiable 2)."""

    IDEA_ONLY = "IDEA_ONLY"
    NEEDS_INPUT = "NEEDS_INPUT"
    FAILED_CHECKS = "FAILED_CHECKS"
    PASS_SUPPORTED_CHECKS = "PASS_SUPPORTED_CHECKS"
    SUPERSEDED = "SUPERSEDED"


class FailureCode(StrEnum):
    """Hard-gate failure codes. Values are K1's ``FailureCode`` (draft.2);
    a new code is added to the contract by PR before the engine may emit it."""

    UNSUPPORTED_RECIPE = "UNSUPPORTED_RECIPE"
    UNSUPPORTED_GARMENT_CATEGORY = "UNSUPPORTED_GARMENT_CATEGORY"
    UNSUPPORTED_MATERIAL = "UNSUPPORTED_MATERIAL"
    MATERIAL_UNKNOWN = "MATERIAL_UNKNOWN"
    CATEGORY_UNKNOWN = "CATEGORY_UNKNOWN"
    MISSING_DIMENSION = "MISSING_DIMENSION"
    UNCONFIRMED_DIMENSION = "UNCONFIRMED_DIMENSION"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    NON_FINITE_VALUE = "NON_FINITE_VALUE"
    POSSIBLE_UNIT_ERROR = "POSSIBLE_UNIT_ERROR"
    MISSING_PROHIBITED_ZONES = "MISSING_PROHIBITED_ZONES"
    NO_POSITIVE_REMAINDER = "NO_POSITIVE_REMAINDER"
    CONFLICTING_DIMENSIONS = "CONFLICTING_DIMENSIONS"
    IMPLAUSIBLE_DIMENSION = "IMPLAUSIBLE_DIMENSION"
    INSUFFICIENT_LENGTH = "INSUFFICIENT_LENGTH"
    CUT_INTERSECTS_PROHIBITED_REGION = "CUT_INTERSECTS_PROHIBITED_REGION"


class Side(StrEnum):
    BACK = "back"
    FRONT_LEFT = "front_left"
    FRONT_RIGHT = "front_right"
    SLEEVE_LEFT = "sleeve_left"
    SLEEVE_RIGHT = "sleeve_right"


def cm_to_mm(value_cm: float) -> float:
    """The only cm -> mm conversion. Use at the UI boundary, never internally."""
    return value_cm * 10.0


@dataclass(frozen=True)
class Measurement:
    """A length in mm with its origin and confirmation time (non-negotiable 1)."""

    value_mm: float
    origin: str
    confirmed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.origin.strip():
            raise ValueError("Measurement.origin must be non-empty")

    @classmethod
    def from_cm(cls, value_cm: float, origin: str, confirmed_at: datetime | None = None) -> Self:
        return cls(cm_to_mm(value_cm), origin, confirmed_at)


def _validated_polygon(points: tuple[Point, ...], what: str) -> None:
    if len(points) < 3:
        raise ValueError(f"{what}: polygon needs at least 3 points")
    if not np.isfinite(np.asarray(points, dtype=float)).all():
        raise ValueError(f"{what}: polygon has non-finite coordinates")
    if not Polygon(points).is_valid:
        raise ValueError(f"{what}: polygon is not valid (self-intersecting or degenerate)")


@dataclass(frozen=True)
class Zone:
    """A named region in panel coordinates. Origin at the shoulder seam, y down, mm."""

    name: str
    kind: str  # e.g. "placket_end", "side_seam_feature", "seam"
    polygon_mm: tuple[Point, ...]

    def __post_init__(self) -> None:
        _validated_polygon(self.polygon_mm, f"Zone {self.name!r}")


@dataclass(frozen=True)
class FabricPanel:
    source_garment_id: str
    side: Side
    polygon_mm: tuple[Point, ...]
    seam_zones: tuple[Zone, ...] = ()
    prohibited_regions: tuple[Zone, ...] = ()
    stretch_family: str = "woven"
    scale_provenance: str = "unverified"

    def __post_init__(self) -> None:
        _validated_polygon(self.polygon_mm, f"FabricPanel {self.panel_id!r}")

    @property
    def panel_id(self) -> str:
        return f"{self.source_garment_id}:{self.side.value}"

    @property
    def bounding_dimensions_mm(self) -> tuple[float, float]:
        minx, miny, maxx, maxy = Polygon(self.polygon_mm).bounds
        return (maxx - minx, maxy - miny)


@dataclass(frozen=True)
class PatternPiece:
    recipe_id: str
    polygon_mm: tuple[Point, ...] | None = None
    template_params: Mapping[str, float] = field(default_factory=dict[str, float])
    grain_deg: float = 0.0
    rotation_limit_deg: float = 0.0
    seam_allowance_mm: float = 0.0
    cut_count: int = 1
    orientation_constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.polygon_mm is not None:
            _validated_polygon(self.polygon_mm, "PatternPiece")
        if self.seam_allowance_mm < 0 or not math.isfinite(self.seam_allowance_mm):
            raise ValueError("PatternPiece.seam_allowance_mm must be finite and >= 0")
        if self.cut_count < 1:
            raise ValueError("PatternPiece.cut_count must be >= 1")


@dataclass(frozen=True)
class Placement:
    source_panel_id: str
    translation_mm: Point
    revision_ref: str
    permitted_rotation_deg: float = 0.0
    seam_margin_mm: float = 0.0

    def __post_init__(self) -> None:
        if not self.revision_ref:
            raise ValueError("Placement.revision_ref is required")
        if self.seam_margin_mm < 0:
            raise ValueError("Placement.seam_margin_mm must be >= 0")


@dataclass(frozen=True)
class Garment:
    """What the engine is told about the garment. ``category``/``material`` of None = unknown."""

    garment_id: str
    category: str | None
    material: str | None
    panels: tuple[FabricPanel, ...] = ()


@dataclass(frozen=True)
class Residual:
    """Contract ``Residual``: ``residual_mm = available_mm - required_mm`` (negative = over)."""

    check_id: str
    quantity: str
    required_mm: float
    available_mm: float
    residual_mm: float
    tolerance_mm: float | None = None


@dataclass(frozen=True)
class CheckOutcome:
    """Contract ``CheckOutcome``. result: pass | fail | needs_input | not_applicable | not_run."""

    check_id: str
    result: str
    failure_code: FailureCode | None = None
    detail: str | None = None


@dataclass(frozen=True)
class Alternative:
    """A change the engine verified would pass. The engine emits none yet (see README)."""

    recipe_id: str
    parameters: Mapping[str, float | str | bool]
    reason: str


@dataclass(frozen=True)
class ConstraintResult:
    """Never a bare boolean. Field names follow K1's ``ConstraintResult`` (draft.2) plus
    the engine's ``status`` (the design state, which only this package decides)."""

    status: DesignState
    failure_codes: tuple[FailureCode, ...]
    residuals: tuple[Residual, ...]
    missing_dimensions: tuple[str, ...]
    uncertainty_flags: tuple[str, ...]
    checks: tuple[CheckOutcome, ...]
    alternatives: tuple[Alternative, ...]
    details: tuple[str, ...]
    cut_mark_mm: float | None
    recipe_id: str
    recipe_version: str | None
    engine_version: str
    checked_at: datetime
    input_fingerprint: str
    revision_ref: str | None = None

    @property
    def hard_pass(self) -> bool:
        """True only if every hard gate ran and passed."""
        return self.status is DesignState.PASS_SUPPORTED_CHECKS

    def residual_mm(self, quantity: str) -> float | None:
        for r in self.residuals:
            if r.quantity == quantity:
                return r.residual_mm
        return None

    def to_contract_dict(self) -> dict[str, Any]:
        """Exactly the contract ``ConstraintResult`` shape (no extra keys)."""
        return {
            "hard_pass": self.hard_pass,
            "failure_codes": [c.value for c in self.failure_codes],
            "residuals": [dataclasses.asdict(r) for r in self.residuals],
            "missing_dimensions": list(self.missing_dimensions),
            "uncertainty_flags": list(self.uncertainty_flags),
            "checks": [
                {
                    **dataclasses.asdict(c),
                    "failure_code": c.failure_code.value if c.failure_code else None,
                }
                for c in self.checks
            ],
            "alternatives": [dataclasses.asdict(a) for a in self.alternatives],
            "engine_version": self.engine_version,
            "checked_at": self.checked_at.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def to_dict(self) -> dict[str, Any]:
        """Contract payload plus the engine-owned fields the API stores beside it."""
        return {
            "status": self.status.value,
            "constraint_result": self.to_contract_dict(),
            "details": list(self.details),
            "cut_mark_mm": self.cut_mark_mm,
            "recipe_id": self.recipe_id,
            "recipe_version": self.recipe_version,
            "input_fingerprint": self.input_fingerprint,
            "revision_ref": self.revision_ref,
        }
