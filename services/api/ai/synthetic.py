"""Synthetic garment contexts for tests and the eval harness. No real garments, photos
or body measurements. Mirrors the geometry used by packages/feasibility's own tests."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sewsure_feasibility import FabricPanel, Garment, Measurement, Side, Zone

from .engine_adapter import RevisionContext

CONFIRMED = datetime(2026, 10, 28, tzinfo=UTC)


def _rect(x0: float, y0: float, x1: float, y1: float) -> tuple[tuple[float, float], ...]:
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def build_context(spec: dict[str, Any] | None = None) -> RevisionContext:
    """spec keys (all optional): category, material, shoulder_to_hem_mm, chest_flat_width_mm,
    zones (full|minimal|none), confirmed (bool), omit (list of dimension names)."""
    s = {
        "category": "woven_shirt",
        "material": "woven",
        "shoulder_to_hem_mm": 780.0,
        "chest_flat_width_mm": 520.0,
        "zones": "full",
        "confirmed": True,
        "omit": [],
        **(spec or {}),
    }
    stamp = CONFIRMED if s["confirmed"] else None
    measurements = {
        "shoulder_to_hem": Measurement(s["shoulder_to_hem_mm"], "user_tape_measured", stamp),
        "chest_flat_width": Measurement(s["chest_flat_width_mm"], "user_tape_measured", stamp),
    }
    for name in s["omit"]:
        measurements.pop(name, None)
    front_zones = {
        "full": (Zone("placket_end", "placket_end", _rect(230, 600, 260, 780)),),
        "minimal": (Zone("collar_button", "placket_end", _rect(230, 0, 260, 50)),),
        "none": (),
    }[s["zones"]]
    back_zones = (
        (Zone("side_pocket", "side_seam_feature", _rect(0, 400, 20, 450)),)
        if s["zones"] == "full"
        else ()
    )
    garment = Garment(
        "g-synthetic",
        s["category"],
        s["material"],
        (
            FabricPanel(
                "g-synthetic",
                Side.FRONT_LEFT,
                _rect(0, 0, 260, 780),
                prohibited_regions=front_zones,
            ),
            FabricPanel(
                "g-synthetic", Side.BACK, _rect(0, 0, 520, 780), prohibited_regions=back_zones
            ),
        ),
    )
    return RevisionContext(garment, measurements)


class SyntheticContextProvider:
    """Returns the same synthetic context for any context ID."""

    def __init__(self, spec: dict[str, Any] | None = None) -> None:
        self._context = build_context(spec)

    def load(self, revision_context_id: str) -> RevisionContext:
        return self._context
