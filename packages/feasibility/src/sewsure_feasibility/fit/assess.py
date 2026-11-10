"""Compute fit output for one design revision.

Narrow ease always carries a warning, never a pass. Output states measured and predicted
values with units (mm) and never claims fit or comfort.
"""

from __future__ import annotations

from collections.abc import Mapping

from sewsure_feasibility.fit.config import EaseConfig, EaseProfile, load_config
from sewsure_feasibility.fit.dimensions import finished_dimensions, read_body_chest
from sewsure_feasibility.fit.model import FitAssessment, FitLabel
from sewsure_feasibility.models import Measurement

SUPPORTED_RECIPE_IDS = frozenset({"woven_shirt_crop_v1"})
DIMENSION = "chest_circumference"

NO_GUARANTEE = "Estimate from flat measurements; fit and comfort are not guaranteed."
PROVISIONAL = "Ease ranges are provisional and not yet approved by a human."


def _label(ease: float, p: EaseProfile) -> FitLabel:
    t0, t1, t2, t3 = p.thresholds_mm()
    if ease < t0:
        return FitLabel.INSUFFICIENT_EASE
    if ease < t1:
        return FitLabel.CLOSE
    if ease < t2:
        return FitLabel.REGULAR
    if ease < t3:
        return FitLabel.RELAXED
    return FitLabel.OVERSIZED


def assess_fit(
    *,
    body_profile_id: str,
    revision_id: str,
    recipe_id: str,
    garment_type: str | None,
    garment: Mapping[str, Measurement],
    body: Mapping[str, Measurement] | None,
    config: EaseConfig | None = None,
) -> FitAssessment:
    """``garment``/``body`` are mm :class:`Measurement` values keyed by canonical dimension
    name. Missing, unconfirmed or implausible input gives label ``unknown`` and a reason."""
    cfg = config or load_config()
    warnings: list[str] = []

    def unknown(finished: dict[str, float]) -> FitAssessment:
        return FitAssessment(
            body_profile_id=body_profile_id,
            revision_id=revision_id,
            measurements_mm={},
            estimated_finished_mm=finished,
            ease_mm={},
            fit_label=FitLabel.UNKNOWN,
            warnings=tuple(dict.fromkeys([*warnings, NO_GUARANTEE])),
            ease_config_provisional=cfg.provisional,
            recipe_id=recipe_id,
        )

    if recipe_id not in SUPPORTED_RECIPE_IDS:
        warnings.append(f"No fit model for recipe {recipe_id}; ease not estimated.")
        return unknown({})
    profile = cfg.profile_for_garment_type(garment_type)
    if profile is None:
        warnings.append("No ease range for this garment type; ease not estimated.")
        return unknown({})

    dims = finished_dimensions(garment)
    if dims.chest_circumference_mm is None:
        warnings.append(dims.problem or "Garment chest width is needed to estimate ease.")
        return unknown({})
    finished = {DIMENSION: round(dims.chest_circumference_mm, 1)}

    body_reading = read_body_chest(body or {})
    if body_reading is None:
        warnings.append("Body chest circumference is needed to estimate ease.")
        return unknown(finished)
    if body_reading.value_mm is None:
        warnings.append(body_reading.problem or "Body chest circumference is unusable.")
        return unknown(finished)
    body_mm = body_reading.value_mm

    ease = dims.chest_circumference_mm - body_mm
    u = profile.uncertainty.value_mm
    label = _label(ease, profile)
    t0 = profile.insufficient_below.value_mm

    if ease < 0:
        warnings.append(f"Negative ease ({ease:.0f} mm): finished chest is smaller than the body.")
    if label is FitLabel.INSUFFICIENT_EASE:
        warnings.append(
            f"Ease {ease:.0f} mm is below the provisional minimum {t0:.0f} mm for this garment."
        )
    elif label is FitLabel.CLOSE:
        warnings.append(
            f"Narrow ease ({ease:.0f} mm; provisional minimum {t0:.0f} mm). Expect a close fit."
        )
    if label is not FitLabel.INSUFFICIENT_EASE and ease - u < t0:
        warnings.append(f"Within ±{u:.0f} mm uncertainty of insufficient ease.")
    if _label(ease - u, profile) is not _label(ease + u, profile):
        warnings.append(f"Label may fall in a neighbouring band (±{u:.0f} mm uncertainty).")
    if profile.name == "knit":
        warnings.append("Jersey stretch varies: wider uncertainty; relaxed designs only.")
    if cfg.provisional:
        warnings.append(PROVISIONAL)
    warnings.append(NO_GUARANTEE)

    return FitAssessment(
        body_profile_id=body_profile_id,
        revision_id=revision_id,
        measurements_mm={DIMENSION: round(body_mm, 1)},
        estimated_finished_mm=finished,
        ease_mm={DIMENSION: round(ease, 1)},
        fit_label=label,
        warnings=tuple(dict.fromkeys(warnings)),
        uncertainty_mm=u,
        ease_config_provisional=cfg.provisional,
        recipe_id=recipe_id,
    )
