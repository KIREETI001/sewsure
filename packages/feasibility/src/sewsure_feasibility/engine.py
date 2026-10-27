"""The single public entry point: :func:`evaluate`.

Gate order (hard gates before anything else; a hard failure is never outscored):
1. recipe allow-list, category, material      -> IDEA_ONLY (no cut points are ever returned)
2. required dimensions/params, plausibility   -> NEEDS_INPUT (no geometry runs)
3. recipe geometry                            -> FAILED_CHECKS or PASS_SUPPORTED_CHECKS
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from collections.abc import Mapping

from sewsure_feasibility.models import (
    ConstraintResult,
    DesignState,
    FailureCode,
    Garment,
    Measurement,
)
from sewsure_feasibility.recipes import get_recipe
from sewsure_feasibility.recipes.base import Recipe

ENGINE_VERSION = "0.1.0"


def _fingerprint(
    garment: Garment,
    measurements: Mapping[str, Measurement],
    recipe_id: str,
    params: Mapping[str, float],
) -> str:
    payload = {
        "garment": dataclasses.asdict(garment),
        "measurements": {
            k: {**dataclasses.asdict(v), "value_mm": float(v.value_mm)}
            for k, v in measurements.items()
        },
        "recipe_id": recipe_id,
        "params": {k: float(v) for k, v in params.items()},
    }
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def _plausibility(name: str, value: float, recipe: Recipe) -> tuple[FailureCode, str] | None:
    bounds = recipe.plausible_ranges_mm.get(name)
    if bounds is None:
        return None
    lo, hi = bounds
    if lo <= value <= hi:
        return None
    if lo <= value * 10 <= hi or lo <= value / 10 <= hi:
        return (
            FailureCode.UNIT_MIX_UP_SUSPECTED,
            f"{name}={value:g} mm is outside {lo:g}-{hi:g} mm but fits if off by a factor of 10 "
            "(cm entered as mm, or the reverse?)",
        )
    return (FailureCode.DIMENSION_IMPLAUSIBLE, f"{name}={value:g} mm is outside {lo:g}-{hi:g} mm")


def evaluate(
    garment: Garment,
    measurements: Mapping[str, Measurement],
    recipe_id: str,
    params: Mapping[str, float],
    *,
    revision_ref: str | None = None,
) -> ConstraintResult:
    """Decide the design state for ``recipe_id`` applied to ``garment``.

    ``measurements`` are :class:`Measurement` (mm, with origin); ``params`` are recipe
    parameters in mm. Never raises for bad design inputs; returns a state with failure codes.
    """
    fingerprint = _fingerprint(garment, measurements, recipe_id, params)
    recipe = get_recipe(recipe_id)

    def result(
        status: DesignState,
        codes: list[FailureCode],
        *,
        details: list[str],
        missing: list[str] | None = None,
        flags: tuple[str, ...] = (),
        residuals: Mapping[str, float] | None = None,
        cut_mark: float | None = None,
        alternatives: tuple[str, ...] = (),
    ) -> ConstraintResult:
        return ConstraintResult(
            status=status,
            failure_codes=tuple(dict.fromkeys(codes)),
            residuals_mm=dict(residuals or {}),
            missing_dimensions=tuple(missing or ()),
            uncertainty_flags=flags,
            suggested_alternatives=alternatives,
            details=tuple(details),
            cut_mark_mm=cut_mark,
            recipe_id=recipe_id,
            recipe_version=recipe.version if recipe else None,
            engine_version=ENGINE_VERSION,
            input_fingerprint=fingerprint,
            revision_ref=revision_ref,
        )

    # Gate 1: applicability. Fails closed; never yields cut points.
    if recipe is None:
        return result(
            DesignState.IDEA_ONLY,
            [FailureCode.RECIPE_NOT_ALLOWED],
            details=[f"recipe {recipe_id!r} is not on the allow-list"],
        )
    category = garment.category.strip().lower() if garment.category else None
    material = garment.material.strip().lower() if garment.material else None
    if category is None or material is None:
        unknown: list[FailureCode] = []
        unknown_names: list[str] = []
        if category is None:
            unknown.append(FailureCode.CATEGORY_UNKNOWN)
            unknown_names.append("garment_category")
        if material is None:
            unknown.append(FailureCode.MATERIAL_UNKNOWN)
            unknown_names.append("material")
        return result(
            DesignState.NEEDS_INPUT,
            unknown,
            details=["confirm garment category and fabric before any rule runs"],
            missing=unknown_names,
            alternatives=("Confirm the garment category and fabric.",),
        )
    if category not in recipe.supported_categories:
        return result(
            DesignState.IDEA_ONLY,
            [FailureCode.CATEGORY_NOT_SUPPORTED],
            details=[f"category {category!r} is not supported by {recipe.recipe_id}"],
            alternatives=("Use a reviewed recipe for this garment category.",),
        )
    if material not in recipe.supported_materials:
        return result(
            DesignState.IDEA_ONLY,
            [FailureCode.MATERIAL_NOT_SUPPORTED],
            details=[f"material {material!r} is not supported by {recipe.recipe_id}"],
            alternatives=("Treat as inspiration only, or use a recipe reviewed for this fabric.",),
        )

    # Gate 2: required inputs and plausibility, before any geometry.
    codes: list[FailureCode] = []
    details: list[str] = []
    missing: list[str] = []
    flags: list[str] = []
    values: dict[str, float] = {}
    params_mm: dict[str, float] = {}
    for name in recipe.required_dimensions:
        m = measurements.get(name)
        if m is None:
            codes.append(FailureCode.MISSING_DIMENSION)
            missing.append(name)
        elif not math.isfinite(m.value_mm):
            codes.append(FailureCode.NON_FINITE_VALUE)
            details.append(f"{name} is not a finite number")
        else:
            values[name] = m.value_mm
            if m.confirmed_at is None and "MEASUREMENT_UNCONFIRMED" not in flags:
                flags.append("MEASUREMENT_UNCONFIRMED")
    for name in recipe.required_params:
        p = params.get(name)
        if p is None or isinstance(p, bool):
            codes.append(FailureCode.MISSING_PARAM)
            missing.append(name)
        elif not math.isfinite(p):
            codes.append(FailureCode.NON_FINITE_VALUE)
            details.append(f"{name} is not a finite number")
        else:
            params_mm[name] = float(p)
    for name, value in {**values, **params_mm}.items():
        issue = _plausibility(name, value, recipe)
        if issue is not None:
            codes.append(issue[0])
            details.append(issue[1])
    if codes:
        return result(
            DesignState.NEEDS_INPUT,
            codes,
            details=details,
            missing=missing,
            flags=tuple(flags),
            alternatives=("Re-check the highlighted measurements and units.",),
        )

    # Gate 3: recipe geometry.
    outcome = recipe.check(garment, values, params_mm)
    status = (
        DesignState.FAILED_CHECKS if outcome.failure_codes else DesignState.PASS_SUPPORTED_CHECKS
    )
    return result(
        status,
        list(outcome.failure_codes),
        details=list(outcome.details),
        flags=tuple(dict.fromkeys([*flags, *outcome.uncertainty_flags])),
        residuals=outcome.residuals_mm,
        cut_mark=outcome.cut_mark_mm,
        alternatives=outcome.suggested_alternatives,
    )


def supersede(previous: ConstraintResult) -> ConstraintResult:
    """Mark an earlier revision's result SUPERSEDED. The original object is left untouched."""
    return dataclasses.replace(previous, status=DesignState.SUPERSEDED)
