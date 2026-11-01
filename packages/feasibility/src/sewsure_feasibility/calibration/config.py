"""Calibration configuration.

``tolerance_mm`` is the team-agreed overlay tolerance (decision H-02). It is chosen by a human,
so it has **no default**: the caller must pass it explicitly, and ``None`` means "not set yet".
With ``None`` every calibration is reported ``uncalibrated`` and every overlay request returns
the dimensioned-diagram fallback.

The remaining fields are input-validity guards (not accuracy claims). Their defaults are
engineering starting points for Narthananilaa to review; they never loosen the tolerance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class CalibrationConfig:
    tolerance_mm: float | None
    """Human-set max worst-case error (mm). ``None`` = not set: always fallback."""

    min_extent_mm: float = 150.0
    """Largest distance between two reference points (mm). Shorter = ruler too short."""

    min_extent_px: float = 100.0
    """Same, in image pixels: too few pixels cannot fit a scale."""

    min_spread_ratio: float = 0.1
    """Smallest/largest spread of the point set. Below this the points are near-collinear."""

    min_duplicate_separation_px: float = 0.5
    min_duplicate_separation_mm: float = 0.5

    min_points_scale: int = 3
    """Redundancy: 2 points fit exactly and would report a meaningless zero error."""

    min_points_perspective: int = 5
    """Perspective needs a point beyond the 4 that determine it, to cross-check."""

    perspective_improvement_ratio: float = 0.8
    """Perspective is used only if its worst-case error is at most this fraction of scale fit."""

    def __post_init__(self) -> None:
        if self.tolerance_mm is not None and not (
            math.isfinite(self.tolerance_mm) and self.tolerance_mm > 0
        ):
            raise ValueError("tolerance_mm must be a positive finite number of mm, or None")
        if self.min_points_scale < 3 or self.min_points_perspective < 5:
            raise ValueError("point-count minimums cannot go below 3 (scale) and 5 (perspective)")
        if not 0 < self.perspective_improvement_ratio <= 1:
            raise ValueError("perspective_improvement_ratio must be in (0, 1]")
