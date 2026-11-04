"""Synthetic fixtures only: no real garments, photos or body measurements."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from sewsure_feasibility import (
    ConstraintResult,
    FabricPanel,
    Garment,
    Measurement,
    Side,
    Zone,
    evaluate,
)

CONFIRMED = datetime(2026, 10, 28, tzinfo=UTC)
RECIPE = "woven_shirt_crop_v1"


def rect(x0: float, y0: float, x1: float, y1: float) -> tuple[tuple[float, float], ...]:
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def meas(length_mm: float = 780.0, chest_mm: float = 520.0) -> dict[str, Measurement]:
    return {
        "shoulder_to_hem": Measurement(length_mm, "tape_measure", CONFIRMED),
        "chest_flat_width": Measurement(chest_mm, "tape_measure", CONFIRMED),
    }


def params(finished: float = 500.0, hem: float = 30.0) -> dict[str, float | str | bool]:
    return {"finished_length_mm": finished, "hem_allowance_mm": hem}


CHECKED_AT = datetime(2026, 10, 28, 12, tzinfo=UTC)


def shirt(
    *,
    category: str | None = "woven_shirt",
    material: str | None = "woven",
    zones: str = "full",  # full | minimal (harmless zone near the neckline) | none
) -> Garment:
    front_zones = {
        "full": (Zone("placket_end", "placket_end", rect(230, 600, 260, 780)),),
        "minimal": (Zone("collar_button", "placket_end", rect(230, 0, 260, 50)),),
        "none": (),
    }[zones]
    front_left = FabricPanel(
        "g1", Side.FRONT_LEFT, rect(0, 0, 260, 780), prohibited_regions=front_zones
    )
    front_right = FabricPanel(
        "g1", Side.FRONT_RIGHT, rect(0, 0, 260, 780), prohibited_regions=front_zones
    )
    back = FabricPanel(
        "g1",
        Side.BACK,
        rect(0, 0, 520, 780),
        prohibited_regions=(
            (Zone("side_pocket", "side_seam_feature", rect(0, 400, 20, 450)),)
            if zones == "full"
            else ()
        ),
    )
    return Garment("g1", category, material, (front_left, front_right, back))


@pytest.fixture
def good_shirt() -> Garment:
    return shirt()


def ev(
    garment: Garment,
    measurements: dict[str, Measurement],
    recipe_id: str = RECIPE,
    p: dict[str, float | str | bool] | None = None,
    **kw: str | None,
) -> ConstraintResult:
    """evaluate() with a fixed clock so results compare equal."""
    return evaluate(
        garment,
        measurements,
        recipe_id,
        p if p is not None else params(),
        checked_at=CHECKED_AT,
        **kw,
    )
