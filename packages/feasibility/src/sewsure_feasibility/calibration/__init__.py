"""Ruler-based calibration and cut-line overlay projection (blueprint §6).

Standalone: depends only on numpy. The accuracy tolerance is a human-set config value with no
default; without it every overlay request returns the dimensioned-diagram fallback.
"""

from sewsure_feasibility.calibration.config import CalibrationConfig
from sewsure_feasibility.calibration.fit import (
    CALIBRATION_VERSION,
    CalibrationIssue,
    CalibrationModel,
    CalibrationPoint,
    CalibrationResult,
    fit_calibration,
    project_points_mm_to_px,
)
from sewsure_feasibility.calibration.overlay import (
    APPROXIMATE_NOTICE,
    FALLBACK_NOTICE,
    OverlayIssue,
    OverlayLayers,
    OverlayLine,
    OverlayResult,
    PlanLine,
    build_overlay,
    lines_from_cut_plan,
)

__all__ = [
    "APPROXIMATE_NOTICE",
    "CALIBRATION_VERSION",
    "FALLBACK_NOTICE",
    "CalibrationConfig",
    "CalibrationIssue",
    "CalibrationModel",
    "CalibrationPoint",
    "CalibrationResult",
    "OverlayIssue",
    "OverlayLayers",
    "OverlayLine",
    "OverlayResult",
    "PlanLine",
    "build_overlay",
    "fit_calibration",
    "lines_from_cut_plan",
    "project_points_mm_to_px",
]
