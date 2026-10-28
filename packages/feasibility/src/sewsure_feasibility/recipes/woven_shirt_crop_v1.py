"""``woven_shirt_crop_v1``: crop a woven button-up shirt by a straight cut.

Rule (blueprint §5.3): cut mark from shoulder = finished length + hem allowance; the
remainder (original length - cut mark) must be strictly positive; the horizontal cut line
must not intersect any prohibited zone (placket end, side-seam features). Zone data is
required: a gate that did not run is never reported as passed. The rule alone does not
verify side seams, so a pass is always flagged ``SIDE_SEAMS_NOT_VERIFIED``.

Plausible ranges and the consistency tolerance are provisional engineering values pending
Narthananilaa's review.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from shapely.geometry import LineString, Polygon

from sewsure_feasibility.models import (
    CheckOutcome,
    FailureCode,
    Garment,
    Residual,
    Side,
)
from sewsure_feasibility.recipes.base import ConsistencyPair, GeometryOutcome, Recipe

RECIPE_ID = "woven_shirt_crop_v1"
RECIPE_VERSION = "1.0.0"
EPS_MM = 1e-9  # float noise only; not a fit tolerance

_CHECKED_SIDES = {Side.BACK, Side.FRONT_LEFT, Side.FRONT_RIGHT}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", text.lower()).strip("_")


def _missing_garment_inputs(garment: Garment) -> tuple[str, ...]:
    has_zones = any(p.prohibited_regions for p in garment.panels if p.side in _CHECKED_SIDES)
    return () if has_zones else ("prohibited_regions",)


def _check(
    garment: Garment, measurements_mm: Mapping[str, float], params_mm: Mapping[str, float]
) -> GeometryOutcome:
    original = measurements_mm["shoulder_to_hem"]
    finished = params_mm["finished_length_mm"]
    hem = params_mm["hem_allowance_mm"]

    cut_mark = finished + hem
    remainder = original - cut_mark
    residuals = [
        Residual("length_gate", "garment_length", cut_mark, original, remainder),
    ]
    codes: list[FailureCode] = []
    details: list[str] = []
    checks: list[CheckOutcome] = []

    if finished >= original - EPS_MM:
        codes.append(FailureCode.INSUFFICIENT_LENGTH)
        msg = f"finished length {finished:g} mm >= available {original:g} mm"
        details.append(msg)
        checks.append(CheckOutcome("length_gate", "fail", FailureCode.INSUFFICIENT_LENGTH, msg))
    elif remainder <= EPS_MM:
        codes.append(FailureCode.NO_POSITIVE_REMAINDER)
        msg = f"remainder {remainder:g} mm is not positive after hem allowance"
        details.append(msg)
        checks.append(CheckOutcome("length_gate", "fail", FailureCode.NO_POSITIVE_REMAINDER, msg))
    else:
        checks.append(CheckOutcome("length_gate", "pass"))

    zone_hit = False
    for panel in (p for p in garment.panels if p.side in _CHECKED_SIDES):
        minx, _, maxx, _ = Polygon(panel.polygon_mm).bounds
        line = LineString([(minx - 1000.0, cut_mark), (maxx + 1000.0, cut_mark)])
        for zone in panel.prohibited_regions:
            zone_poly = Polygon(zone.polygon_mm)
            clearance = float(line.distance(zone_poly))
            residuals.append(
                Residual(
                    "structure",
                    f"clearance_{_slug(panel.panel_id)}_{_slug(zone.name)}",
                    0.0,
                    clearance,
                    clearance,
                )
            )
            if line.intersects(zone_poly):
                zone_hit = True
                details.append(f"cut at {cut_mark:g} mm intersects {zone.kind} {zone.name!r}")
    if zone_hit:
        codes.append(FailureCode.CUT_INTERSECTS_PROHIBITED_REGION)
        checks.append(
            CheckOutcome(
                "structure", "fail", FailureCode.CUT_INTERSECTS_PROHIBITED_REGION, details[-1]
            )
        )
    else:
        checks.append(CheckOutcome("structure", "pass"))

    return GeometryOutcome(
        failure_codes=tuple(dict.fromkeys(codes)),
        residuals=tuple(residuals),
        checks=tuple(checks),
        cut_mark_mm=cut_mark,
        uncertainty_flags=("SIDE_SEAMS_NOT_VERIFIED",),
        details=tuple(details),
    )


RECIPE = Recipe(
    recipe_id=RECIPE_ID,
    version=RECIPE_VERSION,
    supported_categories=frozenset({"woven_shirt"}),
    supported_materials=frozenset({"woven"}),
    required_dimensions=("shoulder_to_hem", "chest_flat_width"),
    required_params=("finished_length_mm", "hem_allowance_mm"),
    optional_params=frozenset({"hem_finish"}),
    plausible_ranges_mm={
        "shoulder_to_hem": (250.0, 1100.0),
        "chest_flat_width": (300.0, 800.0),  # flat width, half circumference
        "finished_length_mm": (150.0, 1100.0),
        "hem_allowance_mm": (5.0, 80.0),
    },
    consistency_pairs=(ConsistencyPair("chest_flat_width", "chest_circumference", 2.0, 0.10),),
    missing_garment_inputs=_missing_garment_inputs,
    check=_check,
)
