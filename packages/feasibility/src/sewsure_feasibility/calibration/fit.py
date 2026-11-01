"""Fit scale (and perspective, only when the data supports it) from user-confirmed points (§6.1).

Each ``CalibrationPoint`` pairs an image pixel with a known position in mm on the garment plane
(a ruler tick, or a landmark the user measured with a ruler). Transforms map image -> plane (mm),
so the error is measured directly in mm on the fabric.

Reported error is **leave-one-out**: each point is predicted from a fit that excludes it. In-sample
residuals are also stored but are never used for the verdict, because an exactly determined fit
always reports zero.

Mirroring: if the photo shows the garment plane reflected relative to the garment frame (for
example a back view, where the garment frame's x-axis points to the wearer's left), the caller
passes ``mirrored=True``. It is declared, never guessed.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from itertools import combinations
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from sewsure_feasibility.calibration.config import CalibrationConfig

CALIBRATION_VERSION = "0.1.0"

Vec = NDArray[np.float64]
CalibrationState = Literal["none", "uncalibrated", "calibrated", "rejected"]


class CalibrationModel(StrEnum):
    SCALE = "scale"  # image -> plane similarity: uniform scale + rotation + translation
    PERSPECTIVE = "perspective"  # image -> plane homography


class CalibrationIssue(StrEnum):
    NO_POINTS = "NO_POINTS"
    TOLERANCE_NOT_SET = "TOLERANCE_NOT_SET"
    UNCONFIRMED_POINT = "UNCONFIRMED_POINT"
    NON_FINITE_POINT = "NON_FINITE_POINT"
    DUPLICATE_POINTS = "DUPLICATE_POINTS"
    TOO_FEW_POINTS = "TOO_FEW_POINTS"
    RULER_TOO_SHORT = "RULER_TOO_SHORT"
    COLLINEAR_POINTS = "COLLINEAR_POINTS"
    DEGENERATE_FIT = "DEGENERATE_FIT"
    ERROR_EXCEEDS_TOLERANCE = "ERROR_EXCEEDS_TOLERANCE"


@dataclass(frozen=True)
class CalibrationPoint:
    """One user-confirmed correspondence. ``plane_mm`` is in the garment frame (millimetres)."""

    point_id: str
    image_px: tuple[float, float]
    plane_mm: tuple[float, float]
    origin: str
    confirmed_at: datetime | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "point_id": self.point_id,
            "image_px": list(self.image_px),
            "plane_mm": list(self.plane_mm),
            "origin": self.origin,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
        }


@dataclass(frozen=True)
class CalibrationResult:
    state: CalibrationState
    issues: tuple[CalibrationIssue, ...]
    points: tuple[CalibrationPoint, ...]
    mirrored: bool
    model: CalibrationModel | None = None
    image_to_plane: tuple[tuple[float, float, float], ...] | None = None
    scale_px_per_mm: float | None = None
    median_error_mm: float | None = None
    max_error_mm: float | None = None
    in_sample_max_error_mm: float | None = None
    scale_model_max_error_mm: float | None = None
    tolerance_mm: float | None = None
    version: str = CALIBRATION_VERSION

    @property
    def rejection_reason(self) -> str | None:
        if self.state == "calibrated" or not self.issues:
            return None
        return ", ".join(i.value for i in self.issues)[:200]

    def to_contract_dict(
        self, calibration_id: str | None = None, reference_photo_id: str | None = None
    ) -> dict[str, Any]:
        """The cut-plan ``Calibration`` record (``cut-plan.schema.json#/$defs/Calibration``).

        Input points and the fit matrix are stored on this object (``points_as_dicts``) but are
        not part of the contract record yet; see the PR note on a contract change.
        """
        return {
            "state": self.state,
            "calibration_id": calibration_id,
            "reference_photo_id": reference_photo_id,
            "scale_px_per_mm": self.scale_px_per_mm,
            "median_error_mm": self.median_error_mm,
            "max_error_mm": self.max_error_mm,
            "tolerance_mm": self.tolerance_mm,
            "rejection_reason": self.rejection_reason,
        }

    def points_as_dicts(self) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self.points]


# --------------------------------------------------------------------------------------
# transforms


def _fit_similarity(src: Vec, dst: Vec) -> Vec:
    """Umeyama: proper rotation + uniform scale + translation, as a 3x3 matrix src -> dst."""
    mu_s, mu_d = src.mean(axis=0), dst.mean(axis=0)
    s0, d0 = src - mu_s, dst - mu_d
    var_s = float((s0**2).sum() / len(src))
    if var_s <= 0:
        raise ValueError("zero variance")
    cov = d0.T @ s0 / len(src)
    u, sv, vt = np.linalg.svd(cov)
    sign = np.diag([1.0, float(np.sign(np.linalg.det(u) * np.linalg.det(vt)) or 1.0)])
    rot = u @ sign @ vt
    scale = float((sv * np.diag(sign)).sum() / var_s)
    if scale <= 0:
        raise ValueError("non-positive scale")
    out = np.eye(3)
    out[:2, :2] = scale * rot
    out[:2, 2] = mu_d - scale * rot @ mu_s
    return out


def _normalise(pts: Vec) -> tuple[Vec, Vec]:
    c = pts.mean(axis=0)
    d = float(np.sqrt(((pts - c) ** 2).sum(axis=1)).mean())
    if d <= 0:
        raise ValueError("zero spread")
    s = math.sqrt(2.0) / d
    t = np.array([[s, 0, -s * c[0]], [0, s, -s * c[1]], [0, 0, 1.0]])
    return (pts - c) * s, t


def _fit_homography(src: Vec, dst: Vec) -> Vec:
    """Normalised DLT, src -> dst, needs >= 4 points in general position."""
    ns, ts = _normalise(src)
    nd, td = _normalise(dst)
    rows: list[list[float]] = []
    for (x, y), (u, v) in zip(ns, nd, strict=True):
        rows.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
        rows.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])
    _, sv, vt = np.linalg.svd(np.asarray(rows, dtype=float))
    if sv[-2] < 1e-9 * max(sv[0], 1.0):
        raise ValueError("degenerate point configuration")
    h = vt[-1].reshape(3, 3)
    full = np.linalg.inv(td) @ h @ ts
    w = np.hstack([src, np.ones((len(src), 1))]) @ full[2]
    if np.all(w < 0):
        full = -full
    elif not np.all(w > 0):
        raise ValueError("points straddle the horizon line")
    # With w > 0 on every point, det(H) > 0 means orientation is preserved. A reflection must be
    # declared with ``mirrored``; a homography must not absorb a left/right mix-up silently.
    if np.linalg.det(full) <= 0:
        raise ValueError("homography reverses orientation")
    return full / np.linalg.norm(full)


def apply_transform(matrix: Vec, pts: Vec) -> Vec:
    """Apply a 3x3 projective matrix to Nx2 points. Raises if a point maps to infinity/behind."""
    homog = np.hstack([pts, np.ones((len(pts), 1))]) @ matrix.T
    w = homog[:, 2]
    if not np.all(np.isfinite(homog)) or np.any(np.abs(w) < 1e-9):
        raise ValueError("projection is degenerate for these points")
    return homog[:, :2] / w[:, None]


def _as_matrix(rows: tuple[tuple[float, float, float], ...]) -> Vec:
    return np.asarray(rows, dtype=float)


def _to_rows(m: Vec) -> tuple[tuple[float, float, float], ...]:
    return tuple((float(r[0]), float(r[1]), float(r[2])) for r in m)


# --------------------------------------------------------------------------------------
# quality checks and errors


def _spread_ratio(pts: Vec) -> float:
    sv = np.linalg.svd(pts - pts.mean(axis=0), compute_uv=False)
    return float(sv[1] / sv[0]) if sv[0] > 0 else 0.0


def _max_pairwise(pts: Vec) -> float:
    return max(
        (float(np.hypot(*(a - b))) for a, b in combinations(pts, 2)),
        default=0.0,
    )


def _loo_errors(fit: Any, src: Vec, dst: Vec) -> Vec:
    errs = np.empty(len(src))
    for i in range(len(src)):
        keep = np.arange(len(src)) != i
        pred = apply_transform(fit(src[keep], dst[keep]), src[i : i + 1])
        errs[i] = float(np.hypot(*(pred[0] - dst[i])))
    return errs


def _local_scale_px_per_mm(image_to_plane: Vec, centre_px: Vec) -> float:
    """px per mm of the plane->image map at the point set's centre (1/s for a similarity)."""
    inv = np.linalg.inv(image_to_plane)
    c = apply_transform(image_to_plane, centre_px[None, :])[0]
    probes = np.array([c, c + [1.0, 0.0], c + [0.0, 1.0]])
    px = apply_transform(inv, probes)
    return float(math.sqrt(np.hypot(*(px[1] - px[0])) * np.hypot(*(px[2] - px[0]))))


# --------------------------------------------------------------------------------------
# public API


def fit_calibration(
    points: Sequence[CalibrationPoint],
    config: CalibrationConfig,
    *,
    mirrored: bool = False,
) -> CalibrationResult:
    """Fit a calibration. Never raises on bad data: it returns ``rejected``/``uncalibrated``/``none``.

    ``calibrated`` requires a human-set tolerance, valid points, and worst-case leave-one-out
    error within that tolerance.
    """
    pts = tuple(points)

    def fail(
        issues: list[CalibrationIssue], state: CalibrationState = "rejected"
    ) -> CalibrationResult:
        return CalibrationResult(
            state=state,
            issues=tuple(dict.fromkeys(issues)),
            points=pts,
            mirrored=mirrored,
            tolerance_mm=config.tolerance_mm,
        )

    if not pts:
        return fail([CalibrationIssue.NO_POINTS], "none")

    issues: list[CalibrationIssue] = []
    raw = np.array([[*p.image_px, *p.plane_mm] for p in pts], dtype=float)
    if not np.all(np.isfinite(raw)):
        return fail([CalibrationIssue.NON_FINITE_POINT])
    if any(p.confirmed_at is None or not p.origin.strip() for p in pts):
        issues.append(CalibrationIssue.UNCONFIRMED_POINT)
    if len(pts) < config.min_points_scale:
        issues.append(CalibrationIssue.TOO_FEW_POINTS)

    src = raw[:, :2].copy()
    dst = raw[:, 2:].copy()
    if mirrored:
        dst[:, 0] *= -1.0

    for a, b in combinations(range(len(pts)), 2):
        if (
            np.hypot(*(src[a] - src[b])) < config.min_duplicate_separation_px
            or np.hypot(*(dst[a] - dst[b])) < config.min_duplicate_separation_mm
        ):
            issues.append(CalibrationIssue.DUPLICATE_POINTS)
            break

    if len(pts) >= 2 and (
        _max_pairwise(dst) < config.min_extent_mm or _max_pairwise(src) < config.min_extent_px
    ):
        issues.append(CalibrationIssue.RULER_TOO_SHORT)
    if len(pts) >= 3 and (
        _spread_ratio(dst) < config.min_spread_ratio or _spread_ratio(src) < config.min_spread_ratio
    ):
        issues.append(CalibrationIssue.COLLINEAR_POINTS)
    if issues:
        return fail(issues)

    try:
        scale_fit = _fit_similarity(src, dst)
        scale_loo = _loo_errors(_fit_similarity, src, dst)
    except (ValueError, np.linalg.LinAlgError):
        return fail([CalibrationIssue.DEGENERATE_FIT])

    chosen, chosen_fit, loo = CalibrationModel.SCALE, scale_fit, scale_loo
    if len(pts) >= config.min_points_perspective:
        try:
            persp_fit = _fit_homography(src, dst)
            persp_loo = _loo_errors(_fit_homography, src, dst)
            if float(persp_loo.max()) <= config.perspective_improvement_ratio * float(
                scale_loo.max()
            ):
                chosen, chosen_fit, loo = CalibrationModel.PERSPECTIVE, persp_fit, persp_loo
        except (ValueError, np.linalg.LinAlgError):
            pass  # perspective unsupported by this point set; keep the scale fit

    try:
        in_sample = apply_transform(chosen_fit, src) - dst
        scale_px = _local_scale_px_per_mm(chosen_fit, src.mean(axis=0))
    except (ValueError, np.linalg.LinAlgError):
        return fail([CalibrationIssue.DEGENERATE_FIT])

    # Store the matrix against the *declared* plane frame (undo the mirror).
    full = np.diag([-1.0, 1.0, 1.0]) @ chosen_fit if mirrored else chosen_fit
    max_err = float(loo.max())
    state: CalibrationState
    out_issues: list[CalibrationIssue] = []
    if config.tolerance_mm is None:
        state = "uncalibrated"
        out_issues.append(CalibrationIssue.TOLERANCE_NOT_SET)
    elif max_err > config.tolerance_mm:
        state = "rejected"
        out_issues.append(CalibrationIssue.ERROR_EXCEEDS_TOLERANCE)
    else:
        state = "calibrated"

    return CalibrationResult(
        state=state,
        issues=tuple(out_issues),
        points=pts,
        mirrored=mirrored,
        model=chosen,
        image_to_plane=_to_rows(full),
        scale_px_per_mm=scale_px,
        median_error_mm=float(np.median(loo)),
        max_error_mm=max_err,
        in_sample_max_error_mm=float(np.hypot(in_sample[:, 0], in_sample[:, 1]).max()),
        scale_model_max_error_mm=float(scale_loo.max()),
        tolerance_mm=config.tolerance_mm,
    )


def project_points_mm_to_px(
    result: CalibrationResult, points_mm: Sequence[tuple[float, float]]
) -> list[tuple[float, float]]:
    """Plane (mm) -> image (px) using a fitted calibration. Raises ``ValueError`` if unfitted
    or the projection is degenerate. Does not check ``state``; ``build_overlay`` does."""
    if result.image_to_plane is None:
        raise ValueError("calibration has no fitted transform")
    arr = np.asarray(points_mm, dtype=float).reshape(-1, 2)
    if not np.all(np.isfinite(arr)):
        raise ValueError("non-finite plane coordinates")
    inv = np.linalg.inv(_as_matrix(result.image_to_plane))
    anchor = np.array([[*p.plane_mm, 1.0] for p in result.points]) @ inv[2]
    if np.all(anchor < 0):
        inv = -inv
    # Points on or beyond the horizon line (w <= 0) have no image position on this plane.
    if np.any(np.hstack([arr, np.ones((len(arr), 1))]) @ inv[2] <= 0):
        raise ValueError("plane point is on or beyond the horizon line")
    px = apply_transform(inv, arr)
    return [(float(x), float(y)) for x, y in px]
