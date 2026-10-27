"""Synthetic fixtures only: no real garments, photos or body measurements."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from sewsure_feasibility import FabricPanel, Garment, Measurement, Side, Zone

CONFIRMED = datetime(2026, 10, 28, tzinfo=UTC)
RECIPE = "woven_shirt_crop_v1"


def rect(x0: float, y0: float, x1: float, y1: float) -> tuple[tuple[float, float], ...]:
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def meas(length_mm: float = 780.0, chest_mm: float = 520.0) -> dict[str, Measurement]:
    return {
        "shoulder_to_hem_length": Measurement(length_mm, "tape_measure", CONFIRMED),
        "chest_width": Measurement(chest_mm, "tape_measure", CONFIRMED),
    }


def params(finished: float = 500.0, hem: float = 30.0) -> dict[str, float]:
    return {"finished_length_mm": finished, "hem_allowance_mm": hem}


def shirt(
    *,
    category: str | None = "button_up_shirt",
    material: str | None = "woven",
    with_zones: bool = True,
) -> Garment:
    front = FabricPanel(
        "g1",
        Side.FRONT_LEFT,
        rect(0, 0, 260, 780),
        prohibited_regions=(
            (Zone("placket_end", "placket_end", rect(230, 600, 260, 780)),) if with_zones else ()
        ),
    )
    back = FabricPanel(
        "g1",
        Side.BACK,
        rect(0, 0, 520, 780),
        prohibited_regions=(
            (Zone("side_pocket", "side_seam_feature", rect(0, 400, 20, 450)),) if with_zones else ()
        ),
    )
    return Garment("g1", category, material, (front, back))


@pytest.fixture
def good_shirt() -> Garment:
    return shirt()
