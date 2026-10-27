"""``woven_shirt_crop_v1``: crop a woven button-up shirt by a straight cut.

Rule (blueprint §5.3): cut mark from shoulder = finished length + hem allowance; the
remainder (original length - cut mark) must be strictly positive; the horizontal cut line
must not intersect any prohibited zone (placket end, side-seam features) when given.
This rule alone does not verify side seams, so the outcome is always flagged for that.

Plausible ranges are provisional engineering values pending Narthananilaa's review.
"""

from __future__ import annotations

from collections.abc import Mapping

from shapely.geometry import LineString, Polygon

from sewsure_feasibility.models import FailureCode, Garment, Side
from sewsure_feasibility.recipes.base import GeometryOutcome, Recipe

RECIPE_ID = "woven_shirt_crop_v1"
RECIPE_VERSION = "1.0.0"
EPS_MM = 1e-9  # float noise only; not a fit tolerance

_CHECKED_SIDES = {Side.BACK, Side.FRONT_LEFT, Side.FRONT_RIGHT}


def _check(
    garment: Garment, measurements_mm: Mapping[str, float], params_mm: Mapping[str, float]
) -> GeometryOutcome:
    original = measurements_mm["shoulder_to_hem_length"]
    finished = params_mm["finished_length_mm"]
    hem = params_mm["hem_allowance_mm"]

    cut_mark = finished + hem
    remainder = original - cut_mark
    residuals: dict[str, float] = {
        "original_length_mm": original,
        "finished_length_mm": finished,
        "hem_allowance_mm": hem,
        "cut_mark_mm": cut_mark,
        "remainder_mm": remainder,
    }
    codes: list[FailureCode] = []
    details: list[str] = []
    flags = ["SIDE_SEAMS_NOT_VERIFIED"]
    alternatives: list[str] = []

    if finished >= original - EPS_MM:
        codes.append(FailureCode.FINISHED_LENGTH_EXCEEDS_AVAILABLE)
        details.append(f"finished length {finished:g} mm >= available {original:g} mm")
        alternatives.append("Choose a shorter finished length.")
    elif remainder <= EPS_MM:
        codes.append(FailureCode.NO_POSITIVE_REMAINDER)
        details.append(f"remainder {remainder:g} mm is not positive after hem allowance")
        alternatives.append("Shorten the finished length or reduce the hem allowance.")

    zones = [
        (p, z) for p in garment.panels if p.side in _CHECKED_SIDES for z in p.prohibited_regions
    ]
    if not zones:
        flags.append("PROHIBITED_ZONES_NOT_PROVIDED")
    for panel, zone in zones:
        minx, _, maxx, _ = Polygon(panel.polygon_mm).bounds
        line = LineString([(minx - 1000.0, cut_mark), (maxx + 1000.0, cut_mark)])
        zone_poly = Polygon(zone.polygon_mm)
        clearance = float(line.distance(zone_poly))
        residuals[f"clearance_mm:{panel.panel_id}:{zone.name}"] = clearance
        if line.intersects(zone_poly):
            codes.append(FailureCode.PROHIBITED_ZONE_INTERSECTION)
            details.append(f"cut at {cut_mark:g} mm intersects {zone.kind} {zone.name!r}")
            alternatives.append("Move the cut mark clear of the prohibited zone.")

    return GeometryOutcome(
        failure_codes=tuple(dict.fromkeys(codes)),
        residuals_mm=residuals,
        cut_mark_mm=cut_mark,
        uncertainty_flags=tuple(flags),
        details=tuple(details),
        suggested_alternatives=tuple(dict.fromkeys(alternatives)),
    )


RECIPE = Recipe(
    recipe_id=RECIPE_ID,
    version=RECIPE_VERSION,
    supported_categories=frozenset({"button_up_shirt"}),
    supported_materials=frozenset({"woven"}),
    required_dimensions=("shoulder_to_hem_length", "chest_width"),
    required_params=("finished_length_mm", "hem_allowance_mm"),
    plausible_ranges_mm={
        "shoulder_to_hem_length": (250.0, 1100.0),
        "chest_width": (300.0, 800.0),  # flat width, half circumference
        "finished_length_mm": (150.0, 1100.0),
        "hem_allowance_mm": (5.0, 80.0),
    },
    check=_check,
)
