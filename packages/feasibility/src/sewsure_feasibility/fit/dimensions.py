"""Finished-garment dimensions and unit/flat-width plausibility. All lengths are mm.

A flat width is HALF the circumference (front + back laid flat). Ease is only ever computed
from circumferences, so a flat width is doubled here and nowhere else.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from sewsure_feasibility.models import Measurement

# Same flat-width range as recipes/woven_shirt_crop_v1.py (300-800 mm). Provisional.
FLAT_CHEST_RANGE_MM = (300.0, 800.0)
GARMENT_CHEST_CIRCUMFERENCE_RANGE_MM = (600.0, 1600.0)
BODY_CHEST_CIRCUMFERENCE_RANGE_MM = (600.0, 1700.0)  # provisional; sanity check only
CONSISTENCY_TOLERANCE = 0.10  # |circumference - 2 x flat| / (2 x flat); matches the recipe


@dataclass(frozen=True)
class Reading:
    """A usable value, or the reason there is none (``problem``)."""

    value_mm: float | None
    problem: str | None = None


def _in(value: float, rng: tuple[float, float]) -> bool:
    return rng[0] <= value <= rng[1]


def _get(source: Mapping[str, Measurement], name: str, who: str) -> Reading | None:
    m = source.get(name)
    if m is None:
        return None
    if m.confirmed_at is None:
        return Reading(None, f"{who} {name} is not confirmed yet; it is treated as missing.")
    return Reading(float(m.value_mm))


def read_flat_chest(garment: Mapping[str, Measurement]) -> Reading | None:
    r = _get(garment, "chest_flat_width", "Garment")
    if r is None or r.value_mm is None:
        return r
    v = r.value_mm
    if _in(v, FLAT_CHEST_RANGE_MM):
        return r
    if _in(v / 2, FLAT_CHEST_RANGE_MM):
        return Reading(
            None,
            f"Garment chest flat width {v:g} mm looks like a circumference. "
            "Enter the width across the laid-flat chest.",
        )
    if _in(v * 10, FLAT_CHEST_RANGE_MM) or _in(v / 10, FLAT_CHEST_RANGE_MM):
        return Reading(
            None, f"Garment chest flat width {v:g} mm may be in the wrong unit (cm vs mm)."
        )
    return Reading(None, f"Garment chest flat width {v:g} mm is outside the plausible range.")


def read_garment_circumference(garment: Mapping[str, Measurement]) -> Reading | None:
    r = _get(garment, "chest_circumference", "Garment")
    if r is None or r.value_mm is None:
        return r
    v = r.value_mm
    if _in(v, GARMENT_CHEST_CIRCUMFERENCE_RANGE_MM):
        return r
    if _in(v * 2, GARMENT_CHEST_CIRCUMFERENCE_RANGE_MM) and _in(v, FLAT_CHEST_RANGE_MM):
        return Reading(
            None,
            f"Garment chest circumference {v:g} mm looks like a flat width (half circumference).",
        )
    if _in(v * 10, GARMENT_CHEST_CIRCUMFERENCE_RANGE_MM) or _in(
        v / 10, GARMENT_CHEST_CIRCUMFERENCE_RANGE_MM
    ):
        return Reading(None, f"Garment chest circumference {v:g} mm may be in the wrong unit.")
    return Reading(None, f"Garment chest circumference {v:g} mm is outside the plausible range.")


def read_body_chest(body: Mapping[str, Measurement]) -> Reading | None:
    r = _get(body, "chest_circumference", "Body")
    if r is None or r.value_mm is None:
        return r
    v = r.value_mm
    lo, hi = BODY_CHEST_CIRCUMFERENCE_RANGE_MM
    if lo <= v <= hi:
        return r
    if lo <= v * 2 <= hi:
        return Reading(
            None, f"Body chest {v:g} mm looks like half a circumference. Use the full way round."
        )
    if lo <= v * 10 <= hi or lo <= v / 10 <= hi:
        return Reading(None, f"Body chest {v:g} mm may be in the wrong unit (cm vs mm).")
    return Reading(None, f"Body chest {v:g} mm is outside the plausible range.")


@dataclass(frozen=True)
class FinishedDimensions:
    chest_circumference_mm: float | None
    problem: str | None = None


def finished_dimensions(garment: Mapping[str, Measurement]) -> FinishedDimensions:
    """Finished chest circumference after the crop (a straight cut below the chest leaves it
    unchanged). Doubles a flat width; never treats a flat width as a circumference."""
    flat = read_flat_chest(garment)
    circ = read_garment_circumference(garment)
    for r in (flat, circ):
        if r is not None and r.problem:
            return FinishedDimensions(None, r.problem)
    flat_mm = flat.value_mm if flat else None
    circ_mm = circ.value_mm if circ else None
    if flat_mm is not None and circ_mm is not None:
        doubled = 2 * flat_mm
        if abs(circ_mm - doubled) / doubled > CONSISTENCY_TOLERANCE:
            return FinishedDimensions(
                None,
                f"Garment chest circumference {circ_mm:g} mm and flat width {flat_mm:g} mm "
                "disagree by more than 10%. Re-measure.",
            )
        return FinishedDimensions(doubled)
    if flat_mm is not None:
        return FinishedDimensions(2 * flat_mm)
    if circ_mm is not None:
        return FinishedDimensions(circ_mm)
    return FinishedDimensions(None, "Garment chest width is needed to estimate ease.")
