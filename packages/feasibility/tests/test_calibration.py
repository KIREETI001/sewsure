"""Calibration and overlay tests. Synthetic points only: no real photos or measurements."""

from __future__ import annotations

import json
import math
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from sewsure_feasibility.calibration import (
    APPROXIMATE_NOTICE,
    CalibrationConfig,
    CalibrationIssue,
    CalibrationModel,
    CalibrationPoint,
    OverlayIssue,
    PlanLine,
    build_overlay,
    fit_calibration,
    lines_from_cut_plan,
    project_points_mm_to_px,
)

CONFIRMED = datetime(2026, 10, 28, tzinfo=UTC)
CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"

# Landmarks on a 600 x 800 mm plane, spread so the set is not near-collinear.
PLANE_MM = [(0.0, 0.0), (500.0, 0.0), (500.0, 700.0), (0.0, 700.0), (250.0, 350.0), (120.0, 600.0)]


def similarity(scale: float, deg: float, tx: float, ty: float, pts: list[tuple[float, float]]):
    """plane mm -> image px, scale in px/mm."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(scale * (c * x - s * y) + tx, scale * (s * x + c * y) + ty) for x, y in pts]


def homography_px(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """A camera-tilt-like projective map, plane mm -> image px."""
    h = np.array([[2.0, 0.15, 300.0], [0.05, 1.8, 200.0], [0.0002, 0.0009, 1.0]])
    out: list[tuple[float, float]] = []
    for x, y in pts:
        v = h @ np.array([x, y, 1.0])
        out.append((float(v[0] / v[2]), float(v[1] / v[2])))
    return out


def make_points(
    px: list[tuple[float, float]],
    plane: list[tuple[float, float]] = PLANE_MM,
    confirmed: datetime | None = CONFIRMED,
) -> list[CalibrationPoint]:
    return [
        CalibrationPoint(f"p{i}", p, m, "user_tape_measured", confirmed)
        for i, (p, m) in enumerate(zip(px, plane, strict=True))
    ]


CFG = CalibrationConfig(tolerance_mm=3.0)  # test value only; the real tolerance is set by a human


def noisy(px: list[tuple[float, float]], sigma: float, seed: int = 7) -> list[tuple[float, float]]:
    rng = np.random.default_rng(seed)
    return [(x + float(rng.normal(0, sigma)), y + float(rng.normal(0, sigma))) for x, y in px]


# ---------------------------------------------------------------- config


def test_tolerance_has_no_default() -> None:
    with pytest.raises(TypeError):
        CalibrationConfig()  # type: ignore[call-arg]


@pytest.mark.parametrize("bad", [0.0, -1.0, math.nan, math.inf])
def test_tolerance_must_be_positive_finite(bad: float) -> None:
    with pytest.raises(ValueError):
        CalibrationConfig(tolerance_mm=bad)


# ---------------------------------------------------------------- scale fit


def test_recovers_known_scale_and_reports_zero_error() -> None:
    px = similarity(2.5, 12.0, 400.0, 300.0, PLANE_MM)
    r = fit_calibration(make_points(px), CFG)
    assert r.state == "calibrated"
    assert r.model is CalibrationModel.SCALE
    assert r.scale_px_per_mm == pytest.approx(2.5, rel=1e-6)
    assert r.max_error_mm == pytest.approx(0.0, abs=1e-6)
    assert r.rejection_reason is None


def test_projection_matches_known_transform() -> None:
    px = similarity(2.5, 12.0, 400.0, 300.0, PLANE_MM)
    r = fit_calibration(make_points(px), CFG)
    probe = [(100.0, 100.0), (300.0, 650.0)]
    got = project_points_mm_to_px(r, probe)
    for g, w in zip(got, similarity(2.5, 12.0, 400.0, 300.0, probe), strict=True):
        assert g == pytest.approx(w, abs=1e-6)


def test_noise_is_reported_as_leave_one_out_error_in_mm() -> None:
    px = noisy(similarity(2.0, -5.0, 100.0, 80.0, PLANE_MM), sigma=1.0)  # ~1 px = 0.5 mm
    r = fit_calibration(make_points(px), CalibrationConfig(tolerance_mm=10.0))
    assert r.max_error_mm is not None and r.median_error_mm is not None
    assert 0.05 < r.median_error_mm <= r.max_error_mm < 5.0
    assert r.in_sample_max_error_mm is not None
    assert r.in_sample_max_error_mm <= r.max_error_mm  # in-sample flatters; never the verdict


def test_error_over_tolerance_is_rejected() -> None:
    px = noisy(similarity(2.0, 0.0, 0.0, 0.0, PLANE_MM), sigma=3.0)
    r = fit_calibration(make_points(px), CalibrationConfig(tolerance_mm=0.5))
    assert r.state == "rejected"
    assert CalibrationIssue.ERROR_EXCEEDS_TOLERANCE in r.issues
    assert r.rejection_reason == "ERROR_EXCEEDS_TOLERANCE"
    assert r.max_error_mm is not None and r.max_error_mm > 0.5


def test_mirrored_view_is_declared_not_guessed() -> None:
    mirrored_plane = [(-x, y) for x, y in PLANE_MM]
    px = similarity(2.0, 3.0, 50.0, 60.0, mirrored_plane)
    assert fit_calibration(make_points(px), CFG).state == "rejected"  # reflection can't be fitted
    r = fit_calibration(make_points(px), CFG, mirrored=True)
    assert r.state == "calibrated" and r.max_error_mm == pytest.approx(0.0, abs=1e-6)
    back = project_points_mm_to_px(r, [(100.0, 200.0)])[0]
    assert back == pytest.approx(similarity(2.0, 3.0, 50.0, 60.0, [(-100.0, 200.0)])[0], abs=1e-6)


@settings(max_examples=40, deadline=None)
@given(
    scale=st.floats(0.5, 6.0),
    deg=st.floats(-45.0, 45.0),
    tx=st.floats(-500.0, 500.0),
    ty=st.floats(-500.0, 500.0),
)
def test_property_similarity_recovered(scale: float, deg: float, tx: float, ty: float) -> None:
    r = fit_calibration(make_points(similarity(scale, deg, tx, ty, PLANE_MM)), CFG)
    assert r.state == "calibrated"
    assert r.scale_px_per_mm == pytest.approx(scale, rel=1e-6)
    assert r.max_error_mm is not None and r.max_error_mm < 1e-4


# ---------------------------------------------------------------- perspective


def test_perspective_used_only_when_it_is_clearly_better() -> None:
    r = fit_calibration(make_points(homography_px(PLANE_MM)), CalibrationConfig(tolerance_mm=2.0))
    assert r.model is CalibrationModel.PERSPECTIVE
    assert r.state == "calibrated"
    assert r.scale_model_max_error_mm is not None and r.max_error_mm is not None
    assert r.scale_model_max_error_mm > 10 * r.max_error_mm
    got = project_points_mm_to_px(r, [(200.0, 300.0)])[0]
    assert got == pytest.approx(homography_px([(200.0, 300.0)])[0], abs=1e-4)


def test_flat_photo_stays_on_scale_model_even_with_many_points() -> None:
    plane = [*PLANE_MM, (400.0, 200.0), (50.0, 300.0)]
    px = noisy(similarity(2.0, 4.0, 10.0, 20.0, plane), sigma=0.3)
    r = fit_calibration(make_points(px, plane), CalibrationConfig(tolerance_mm=5.0))
    assert r.model is CalibrationModel.SCALE


def test_perspective_needs_five_points() -> None:
    plane = PLANE_MM[:4]
    r = fit_calibration(make_points(homography_px(plane), plane), CalibrationConfig(tolerance_mm=2.0))
    assert r.model is CalibrationModel.SCALE
    assert r.scale_model_max_error_mm == r.max_error_mm


# ---------------------------------------------------------------- degenerate input


def codes(points: list[CalibrationPoint], cfg: CalibrationConfig = CFG) -> set[CalibrationIssue]:
    r = fit_calibration(points, cfg)
    assert r.state in ("rejected", "none")
    assert r.image_to_plane is None and r.max_error_mm is None
    return set(r.issues)


def test_no_points() -> None:
    r = fit_calibration([], CFG)
    assert r.state == "none" and r.issues == (CalibrationIssue.NO_POINTS,)


def test_collinear_points_rejected() -> None:
    plane = [(0.0, 0.0), (200.0, 0.0), (400.0, 0.0), (600.0, 0.0)]
    px = similarity(2.0, 0.0, 0.0, 0.0, plane)
    assert CalibrationIssue.COLLINEAR_POINTS in codes(make_points(px, plane))


def test_near_collinear_points_rejected() -> None:
    plane = [(0.0, 0.0), (300.0, 4.0), (600.0, 0.0), (450.0, -3.0)]
    px = similarity(2.0, 0.0, 0.0, 0.0, plane)
    assert CalibrationIssue.COLLINEAR_POINTS in codes(make_points(px, plane))


def test_duplicate_points_rejected() -> None:
    px = similarity(2.0, 0.0, 0.0, 0.0, PLANE_MM)
    px[1] = px[0]  # same pixel for two different landmarks
    assert CalibrationIssue.DUPLICATE_POINTS in codes(make_points(px))
    plane = [*PLANE_MM[:5], PLANE_MM[0]]  # same landmark entered twice
    px2 = similarity(2.0, 0.0, 0.0, 0.0, plane)
    assert CalibrationIssue.DUPLICATE_POINTS in codes(make_points(px2, plane))


def test_too_short_ruler_rejected() -> None:
    plane = [(0.0, 0.0), (60.0, 0.0), (60.0, 40.0), (0.0, 40.0)]  # < 150 mm extent
    px = similarity(4.0, 0.0, 0.0, 0.0, plane)
    assert CalibrationIssue.RULER_TOO_SHORT in codes(make_points(px, plane))


def test_short_in_pixels_rejected() -> None:
    px = similarity(0.1, 0.0, 0.0, 0.0, PLANE_MM)  # 700 mm spans < 100 px
    assert CalibrationIssue.RULER_TOO_SHORT in codes(make_points(px))


def test_two_points_cannot_calibrate() -> None:
    plane = PLANE_MM[:2]
    px = similarity(2.0, 0.0, 0.0, 0.0, plane)
    assert CalibrationIssue.TOO_FEW_POINTS in codes(make_points(px, plane))


def test_unconfirmed_point_rejected() -> None:
    px = similarity(2.0, 0.0, 0.0, 0.0, PLANE_MM)
    assert CalibrationIssue.UNCONFIRMED_POINT in codes(make_points(px, confirmed=None))


def test_non_finite_point_rejected() -> None:
    px = similarity(2.0, 0.0, 0.0, 0.0, PLANE_MM)
    px[2] = (math.nan, 5.0)
    assert codes(make_points(px)) == {CalibrationIssue.NON_FINITE_POINT}


# ---------------------------------------------------------------- tolerance not set / fallback


def good_calibration(tolerance: float | None = 3.0):
    px = similarity(2.0, 6.0, 120.0, 90.0, PLANE_MM)
    return fit_calibration(make_points(px), CalibrationConfig(tolerance_mm=tolerance))


LINES = [
    PlanLine("front", "cut_line", "cut", ((0.0, 525.0), (280.0, 525.0)), "Cut"),
    PlanLine("front", "fold_line", "fold", ((0.0, 512.5), (280.0, 512.5)), "Fold"),
    PlanLine("front", "side_seam", "stitch", ((0.0, 0.0), (0.0, 500.0)), "Stitch"),
]


def test_no_tolerance_always_falls_back_even_with_perfect_points() -> None:
    cal = good_calibration(tolerance=None)
    assert cal.state == "uncalibrated" and cal.issues == (CalibrationIssue.TOLERANCE_NOT_SET,)
    assert cal.max_error_mm == pytest.approx(0.0, abs=1e-6)  # stats are kept for QA
    out = build_overlay(LINES, cal)
    assert out.mode == "dimensioned_diagram"
    assert out.layers is None
    assert out.fallback_issues == (OverlayIssue.CALIBRATION_NOT_ACCEPTED,)
    assert out.diagram_lines == tuple(LINES)  # mm lines still available for the diagram


def test_missing_calibration_falls_back() -> None:
    out = build_overlay(LINES, fit_calibration([], CFG))
    assert out.mode == "dimensioned_diagram" and out.layers is None
    assert out.to_dict()["calibration"]["state"] == "none"


def test_rejected_calibration_falls_back() -> None:
    px = noisy(similarity(2.0, 0.0, 0.0, 0.0, PLANE_MM), sigma=3.0)
    cal = fit_calibration(make_points(px), CalibrationConfig(tolerance_mm=0.5))
    out = build_overlay(LINES, cal)
    assert out.mode == "dimensioned_diagram" and out.layers is None
    assert out.to_dict()["calibration"]["rejection_reason"] == "ERROR_EXCEEDS_TOLERANCE"


def test_projection_failure_falls_back_rather_than_drawing() -> None:
    cal = fit_calibration(make_points(homography_px(PLANE_MM)), CalibrationConfig(tolerance_mm=2.0))
    assert cal.state == "calibrated" and cal.model is CalibrationModel.PERSPECTIVE
    # Beyond the plane's horizon (w < 0): 0.0002 x + 0.0009 y + 1 < 0 for x = -6000.
    horizon = PlanLine("p", "bad", "cut", ((-6000.0, 0.0), (0.0, 0.0)), "x")
    out = build_overlay([horizon], cal)
    assert out.mode == "dimensioned_diagram"
    assert out.fallback_issues == (OverlayIssue.PROJECTION_FAILED,)


def test_empty_lines_fall_back() -> None:
    out = build_overlay([], good_calibration())
    assert out.mode == "dimensioned_diagram" and out.fallback_issues == (OverlayIssue.NO_LINES,)


# ---------------------------------------------------------------- calibrated overlay


def test_calibrated_overlay_has_separate_layers_and_is_labelled_approximate() -> None:
    out = build_overlay(LINES, good_calibration())
    assert out.mode == "calibrated_overlay" and out.layers is not None
    assert [ln.line_id for ln in out.layers.cut] == ["cut_line"]
    assert [ln.line_id for ln in out.layers.fold] == ["fold_line"]
    assert [ln.line_id for ln in out.layers.stitch] == ["side_seam"]
    assert out.layers.reference == ()
    assert out.approximate is True and out.notice == APPROXIMATE_NOTICE
    want = similarity(2.0, 6.0, 120.0, 90.0, [(0.0, 525.0), (280.0, 525.0)])
    for got, exp in zip(out.layers.cut[0].points_px, want, strict=True):
        assert got == pytest.approx(exp, abs=1e-6)
    assert out.layers.cut[0].points_mm == ((0.0, 525.0), (280.0, 525.0))  # mm kept internally


def test_contract_calibration_record_matches_schema() -> None:
    schema = json.loads((CONTRACTS / "schemas" / "cut-plan.schema.json").read_text())
    cal_def = schema["$defs"]["Calibration"]
    rec = good_calibration().to_contract_dict("cal-1", "photo-1")
    assert set(rec) <= set(cal_def["properties"])
    assert set(cal_def["required"]) <= set(rec)
    assert rec["state"] in cal_def["properties"]["state"]["enum"]
    for state in (
        good_calibration(None).state,
        fit_calibration([], CFG).state,
        fit_calibration(make_points(similarity(2.0, 0.0, 0.0, 0.0, PLANE_MM)[:2], PLANE_MM[:2]), CFG).state,
    ):
        assert state in cal_def["properties"]["state"]["enum"]


def test_overlay_layer_kinds_are_contract_line_kinds() -> None:
    schema = json.loads((CONTRACTS / "schemas" / "cut-plan.schema.json").read_text())
    from sewsure_feasibility.calibration.overlay import LINE_KINDS

    assert set(LINE_KINDS) == set(schema["$defs"]["Line"]["properties"]["kind"]["enum"])


def test_lines_from_contract_fixture_and_overlay() -> None:
    fixture = json.loads((CONTRACTS / "fixtures" / "woven_shirt_crop_pass.json").read_text())
    lines = lines_from_cut_plan(fixture["cut_plan"])
    assert lines and {ln.kind for ln in lines} <= {"cut", "fold", "stitch", "reference"}
    out = build_overlay(lines, good_calibration())
    assert out.mode == "calibrated_overlay" and out.layers is not None
    assert len(out.layers.cut) == sum(ln.kind == "cut" for ln in lines)
    d = out.to_dict()
    assert set(d["layers"]) == {"cut", "stitch", "fold", "reference"}


def test_lines_from_cut_plan_rejects_non_mm() -> None:
    with pytest.raises(ValueError):
        lines_from_cut_plan({"units": "cm", "pieces": []})
