"""The single public entry point: :func:`evaluate`.

Gate order (hard gates before anything else; a hard failure is never outscored):
1. recipe allow-list, category, material      -> IDEA_ONLY (no cut points are ever returned)
2. required inputs, confirmation, plausibility,
   consistency                                -> NEEDS_INPUT (no geometry runs)
3. recipe geometry                            -> FAILED_CHECKS or PASS_SUPPORTED_CHECKS

A measurement with ``confirmed_at=None`` counts as missing (contract #15): it can never
reach a pass or a cut mark.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from sewsure_feasibility.models import (
    CheckOutcome,
    ConstraintResult,
    DesignState,
    FailureCode,
    Garment,
    Measurement,
)
from sewsure_feasibility.original_garment import OriginalGarmentRecord
from sewsure_feasibility.recipes import get_recipe
from sewsure_feasibility.recipes.base import Recipe

ENGINE_VERSION = "0.2.0"

ParamValue = float | str | bool

_CHECK_ORDER = ("supported_material", "required_dimensions", "length_gate", "structure")


def _canon(value: Any) -> Any:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return value
    return float(value)


def _fingerprint(
    garment: Garment,
    measurements: Mapping[str, Measurement],
    recipe_id: str,
    params: Mapping[str, ParamValue],
) -> str:
    payload = {
        "garment": dataclasses.asdict(garment),
        "measurements": {
            k: {**dataclasses.asdict(v), "value_mm": float(v.value_mm)}
            for k, v in measurements.items()
        },
        "recipe_id": recipe_id,
        "params": {k: _canon(v) for k, v in params.items()},
    }
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def _plausibility(
    name: str, value: float, recipe: Recipe, *, is_param: bool
) -> tuple[FailureCode, str] | None:
    """Return (code, detail) when ``value`` is outside the plausible range."""
    bounds = recipe.plausible_ranges_mm.get(name)
    if bounds is None:
        return None
    lo, hi = bounds
    if lo <= value <= hi:
        return None
    if value <= 0 and is_param:
        return (FailureCode.INVALID_PARAMETER, f"{name}={value:g} mm must be positive")
    if lo <= value * 10 <= hi or lo <= value / 10 <= hi:
        return (
            FailureCode.POSSIBLE_UNIT_ERROR,
            f"{name}={value:g} mm is outside {lo:g}-{hi:g} mm but fits if off by a factor of 10 "
            "(cm entered as mm, or the reverse?)",
        )
    return (
        FailureCode.IMPLAUSIBLE_DIMENSION,
        f"{name}={value:g} mm is outside {lo:g}-{hi:g} mm",
    )


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def evaluate(
    garment: Garment,
    measurements: Mapping[str, Measurement],
    recipe_id: str,
    params: Mapping[str, ParamValue],
    *,
    revision_ref: str | None = None,
    checked_at: datetime | None = None,
) -> ConstraintResult:
    """Decide the design state for ``recipe_id`` applied to ``garment``.

    ``measurements`` are :class:`Measurement` (mm, with origin and ``confirmed_at``); ``params``
    are recipe parameters (lengths in mm; strings/booleans allowed for options). Never raises for
    bad design inputs; returns a state with failure codes.
    """
    fingerprint = _fingerprint(garment, measurements, recipe_id, params)
    recipe = get_recipe(recipe_id)
    stamp = checked_at or datetime.now(UTC)

    def result(
        status: DesignState,
        codes: list[FailureCode],
        *,
        details: list[str],
        checks: dict[str, CheckOutcome],
        missing: list[str] | None = None,
        flags: tuple[str, ...] = (),
        outcome_residuals: tuple[Any, ...] = (),
        cut_mark: float | None = None,
    ) -> ConstraintResult:
        ordered = tuple(checks.get(cid, CheckOutcome(cid, "not_run")) for cid in _CHECK_ORDER)
        return ConstraintResult(
            status=status,
            failure_codes=tuple(dict.fromkeys(codes)),
            residuals=outcome_residuals,
            missing_dimensions=tuple(dict.fromkeys(missing or ())),
            uncertainty_flags=tuple(dict.fromkeys(flags)),
            checks=ordered,
            alternatives=(),
            details=tuple(details),
            cut_mark_mm=cut_mark,
            recipe_id=recipe_id,
            recipe_version=recipe.version if recipe else None,
            engine_version=ENGINE_VERSION,
            checked_at=stamp,
            input_fingerprint=fingerprint,
            revision_ref=revision_ref,
        )

    def material_gate(code: FailureCode, detail: str, result_kind: str) -> dict[str, CheckOutcome]:
        return {"supported_material": CheckOutcome("supported_material", result_kind, code, detail)}

    # Gate 1: applicability. Fails closed; never yields cut points.
    if recipe is None:
        detail = f"recipe {recipe_id!r} is not on the allow-list"
        return result(
            DesignState.IDEA_ONLY,
            [FailureCode.UNSUPPORTED_RECIPE],
            details=[detail],
            checks=material_gate(FailureCode.UNSUPPORTED_RECIPE, detail, "fail"),
        )
    category = garment.category.strip().lower() if garment.category else None
    material = garment.material.strip().lower() if garment.material else None
    if category == "unknown":
        category = None
    if material == "unknown":
        material = None
    if category is None or material is None:
        codes: list[FailureCode] = []
        names: list[str] = []
        if category is None:
            codes.append(FailureCode.CATEGORY_UNKNOWN)
            names.append("garment_category")
        if material is None:
            codes.append(FailureCode.MATERIAL_UNKNOWN)
            names.append("fabric_family")
        detail = "confirm garment category and fabric before any rule runs"
        return result(
            DesignState.NEEDS_INPUT,
            codes,
            details=[detail],
            checks=material_gate(codes[0], detail, "needs_input"),
            missing=names,
        )
    if category not in recipe.supported_categories:
        detail = f"category {category!r} is not supported by {recipe.recipe_id}"
        return result(
            DesignState.IDEA_ONLY,
            [FailureCode.UNSUPPORTED_GARMENT_CATEGORY],
            details=[detail],
            checks=material_gate(FailureCode.UNSUPPORTED_GARMENT_CATEGORY, detail, "fail"),
        )
    if material not in recipe.supported_materials:
        detail = f"material {material!r} is not supported by {recipe.recipe_id}"
        return result(
            DesignState.IDEA_ONLY,
            [FailureCode.UNSUPPORTED_MATERIAL],
            details=[detail],
            checks=material_gate(FailureCode.UNSUPPORTED_MATERIAL, detail, "fail"),
        )
    gate1 = {"supported_material": CheckOutcome("supported_material", "pass")}

    # Gate 2: required inputs, confirmation, plausibility, consistency. No geometry yet.
    codes = []
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
        elif m.confirmed_at is None:
            codes.append(FailureCode.UNCONFIRMED_DIMENSION)
            missing.append(name)
            details.append(f"{name} is unconfirmed ({m.origin}); confirm it to continue")
        elif not math.isfinite(m.value_mm):
            codes.append(FailureCode.NON_FINITE_VALUE)
            missing.append(name)
            details.append(f"{name} is not a finite number")
        else:
            values[name] = m.value_mm
    for name in recipe.required_params:
        p = params.get(name)
        if p is None:
            codes.append(FailureCode.MISSING_PARAMETER)
            missing.append(name)
        elif not _is_number(p):
            codes.append(FailureCode.INVALID_PARAMETER)
            missing.append(name)
            details.append(f"{name} must be a number of mm, got {p!r}")
        elif not math.isfinite(float(p)):  # type: ignore[arg-type]
            codes.append(FailureCode.NON_FINITE_VALUE)
            missing.append(name)
            details.append(f"{name} is not a finite number")
        else:
            params_mm[name] = float(p)  # type: ignore[arg-type]
    ignored = sorted(set(params) - set(recipe.required_params) - recipe.optional_params)
    if ignored:
        flags.append("IGNORED_PARAMETERS")
        details.append(f"parameters not on the recipe allow-list were ignored: {ignored}")
    for name in recipe.missing_garment_inputs(garment):
        codes.append(FailureCode.MISSING_PROHIBITED_ZONES)
        missing.append(name)
        details.append(f"{name} are required to check the cut line and were not provided")
    for name, value in {**values, **params_mm}.items():
        issue = _plausibility(name, value, recipe, is_param=name in params_mm)
        if issue is not None:
            codes.append(issue[0])
            missing.append(name)
            details.append(issue[1])
    for pair in recipe.consistency_pairs:
        flat = values.get(pair.flat_key)
        other_m = measurements.get(pair.other_key)
        if flat is None or other_m is None or other_m.confirmed_at is None:
            continue
        expected = flat * pair.factor
        if abs(other_m.value_mm - expected) > pair.tolerance_fraction * expected:
            codes.append(FailureCode.CONFLICTING_DIMENSIONS)
            missing.extend([pair.flat_key, pair.other_key])
            details.append(
                f"{pair.flat_key}={flat:g} mm implies {pair.other_key}~{expected:g} mm, "
                f"got {other_m.value_mm:g} mm"
            )
    if codes:
        return result(
            DesignState.NEEDS_INPUT,
            codes,
            details=details,
            checks={
                **gate1,
                "required_dimensions": CheckOutcome(
                    "required_dimensions", "needs_input", codes[0], details[0] if details else None
                ),
            },
            missing=missing,
            flags=tuple(flags),
        )
    gate2 = {**gate1, "required_dimensions": CheckOutcome("required_dimensions", "pass")}

    # Gate 3: recipe geometry.
    outcome = recipe.check(garment, values, params_mm)
    status = (
        DesignState.FAILED_CHECKS if outcome.failure_codes else DesignState.PASS_SUPPORTED_CHECKS
    )
    return result(
        status,
        list(outcome.failure_codes),
        details=[*details, *outcome.details],
        checks={**gate2, **{c.check_id: c for c in outcome.checks}},
        flags=(*flags, *outcome.uncertainty_flags),
        outcome_residuals=outcome.residuals,
        cut_mark=outcome.cut_mark_mm,
    )


def supersede(previous: ConstraintResult) -> ConstraintResult:
    """Mark a passed revision's result SUPERSEDED (the original object is left untouched).

    Only a ``PASS_SUPPORTED_CHECKS`` result can be superseded (contract #15); anything else
    raises ``ValueError`` so a failed or incomplete state is never overwritten.
    """
    if previous.status is not DesignState.PASS_SUPPORTED_CHECKS:
        raise ValueError(f"only a passed result can be superseded, got {previous.status.value}")
    return dataclasses.replace(previous, status=DesignState.SUPERSEDED)


def evaluate_original_garment(
    record: OriginalGarmentRecord,
    recipe_id: str,
    params: Mapping[str, ParamValue],
    *,
    revision_ref: str | None = None,
    checked_at: datetime | None = None,
) -> ConstraintResult:
    """Evaluate a transformation using a unified original garment record.

    Extracts the garment and its recorded measurements before delegating
    to the existing feasibility evaluation pipeline.
    """
    return evaluate(
        garment=record.garment,
        measurements=record.profile.measurements,
        recipe_id=recipe_id,
        params=params,
        revision_ref=revision_ref,
        checked_at=checked_at,
    )
