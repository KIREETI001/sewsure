"""Adapter over packages/feasibility (`sewsure_feasibility`). The API never decides a design
state: every status here is copied from the engine's `ConstraintResult`.

The adapter maps stored records to the engine's typed inputs and the engine's result back to the
contract fields stored on a revision. The one thing built here is the engine *input* panel model
(see `build_garment`); it has no contract record yet and is listed as an open item in the PR.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sewsure_feasibility import (
    ALLOWED_RECIPE_IDS,
    ConstraintResult,
    DesignState,
    FabricPanel,
    FailureCode,
    Garment,
    Measurement,
    Side,
    Zone,
    evaluate,
    supersede,
)
from sewsure_feasibility.models import Alternative, CheckOutcome, Residual
from sewsure_feasibility.recipes import get_recipe

PANEL_SLUGS = {
    Side.BACK: "back_panel",
    Side.FRONT_LEFT: "front_left",
    Side.FRONT_RIGHT: "front_right",
}

SIDE_SEAM_NOTE = "Side seams are not verified by these checks; measure with a ruler before cutting."
PENDING_RULER_CHECK = (
    "Verify the shoulder-to-hem reference with a ruler on the garment before cutting."
)


def recipe_known(recipe_id: str | None) -> bool:
    return recipe_id is not None and recipe_id in ALLOWED_RECIPE_IDS


def allowed_parameter_keys(recipe_id: str) -> frozenset[str] | None:
    """Parameter names the reviewed recipe accepts, or None for an unknown recipe."""
    recipe = get_recipe(recipe_id)
    if recipe is None:
        return None
    return frozenset(recipe.required_params) | frozenset(recipe.optional_params)


def required_dimensions(recipe_id: str) -> tuple[str, ...]:
    recipe = get_recipe(recipe_id)
    return tuple(recipe.required_dimensions) if recipe else ()


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def engine_measurements(garment_dims: Mapping[str, Mapping[str, Any]]) -> dict[str, Measurement]:
    """Stored MeasurementValue dicts -> engine Measurements (mm, origin, confirmed_at)."""
    return {
        name: Measurement(float(v["value_mm"]), str(v["origin"]), _parse_dt(v.get("confirmed_at")))
        for name, v in garment_dims.items()
    }


def _rect(x0: float, y0: float, x1: float, y1: float) -> tuple[tuple[float, float], ...]:
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def build_garment(
    garment_id: str,
    category: str,
    fabric_family: str,
    dims: Mapping[str, Measurement],
) -> Garment:
    """Engine input: flat panels as rectangles from the user's measurements.

    Panel sizes come only from `shoulder_to_hem` and `chest_flat_width` (back = full width,
    each front = half). A prohibited region on the fronts exists only if the user gave
    `placket_end_from_shoulder`: the band from that distance down to the hem (matching N1's
    placket-end zone convention). Without it no zone is passed and the engine answers
    NEEDS_INPUT (MISSING_PROHIBITED_ZONES); nothing is assumed. The panel model belongs in
    packages/feasibility; see the PR's open items.
    """
    length = dims.get("shoulder_to_hem")
    chest = dims.get("chest_flat_width")
    if length is None or chest is None:
        return Garment(garment_id, category, fabric_family, ())
    h, w = length.value_mm, chest.value_mm
    zones: tuple[Zone, ...] = ()
    placket = dims.get("placket_end_from_shoulder")
    if placket is not None and 0 < placket.value_mm < h:
        zones = (Zone("placket_end", "placket_end", _rect(0, placket.value_mm, w / 2, h)),)
    panels = (
        FabricPanel(garment_id, Side.BACK, _rect(0, 0, w, h)),
        FabricPanel(garment_id, Side.FRONT_LEFT, _rect(0, 0, w / 2, h), prohibited_regions=zones),
        FabricPanel(garment_id, Side.FRONT_RIGHT, _rect(0, 0, w / 2, h), prohibited_regions=zones),
    )
    return Garment(garment_id, category, fabric_family, panels)


def run_engine(
    garment: Garment,
    dims: Mapping[str, Measurement],
    recipe_id: str,
    params: Mapping[str, float | str | bool],
    revision_ref: str,
) -> ConstraintResult:
    return evaluate(garment, dims, recipe_id, params, revision_ref=revision_ref)


@dataclass(frozen=True)
class RevisionFields:
    """Everything stored on a revision that comes from the engine result."""

    status: str
    checks: dict[str, Any]
    inputs_hash: str
    engine_version: str
    recipe_version: str | None
    geometry_mm: dict[str, Any]
    pending_checks: list[str]
    cut_mark_mm: float | None


def revision_fields(
    result: ConstraintResult,
    params: Mapping[str, Any],
    dims: Mapping[str, Measurement],
) -> RevisionFields:
    """Copy the engine's verdict. `geometry_mm` echoes engine and user values only: the engine's
    cut mark (pass only), the user's measured length and the requested parameters. No arithmetic
    happens here."""
    geometry: dict[str, Any] = {}
    if result.status in (DesignState.PASS_SUPPORTED_CHECKS, DesignState.FAILED_CHECKS):
        if "shoulder_to_hem" in dims:
            geometry["original_length_mm"] = dims["shoulder_to_hem"].value_mm
        for key in ("finished_length_mm", "hem_allowance_mm"):
            if key in params:
                geometry[key] = params[key]
    if result.status is DesignState.PASS_SUPPORTED_CHECKS and result.cut_mark_mm is not None:
        geometry["cut_mark_from_shoulder_mm"] = result.cut_mark_mm
    passed = result.status is DesignState.PASS_SUPPORTED_CHECKS
    return RevisionFields(
        status=result.status.value,
        checks=result.to_contract_dict(),
        inputs_hash=result.input_fingerprint,
        engine_version=result.engine_version,
        recipe_version=result.recipe_version,
        geometry_mm=geometry,
        pending_checks=[PENDING_RULER_CHECK] if passed else [],
        cut_mark_mm=result.cut_mark_mm if passed else None,
    )


def required_panels(garment: Garment) -> list[str]:
    return [PANEL_SLUGS[p.side] for p in garment.panels if p.side in PANEL_SLUGS]


def superseded_status(checks: Mapping[str, Any], status: str, recipe_id: str | None) -> str:
    """Ask the engine to supersede a stored result (it refuses anything that did not pass)."""
    result = ConstraintResult(
        status=DesignState(status),
        failure_codes=tuple(FailureCode(c) for c in checks["failure_codes"]),
        residuals=tuple(Residual(**r) for r in checks["residuals"]),
        missing_dimensions=tuple(checks["missing_dimensions"]),
        uncertainty_flags=tuple(checks["uncertainty_flags"]),
        checks=tuple(
            CheckOutcome(
                c["check_id"],
                c["result"],
                FailureCode(c["failure_code"]) if c.get("failure_code") else None,
                c.get("detail"),
            )
            for c in checks["checks"]
        ),
        alternatives=tuple(Alternative(**a) for a in checks.get("alternatives", [])),
        details=(),
        cut_mark_mm=None,
        recipe_id=recipe_id or "",
        recipe_version=None,
        engine_version=str(checks["engine_version"]),
        checked_at=_parse_dt(checks["checked_at"]) or datetime.now(UTC),
        input_fingerprint="",
    )
    return supersede(result).status.value


def explanation(status: str, checks: Mapping[str, Any], params: Mapping[str, Any]) -> str:
    """User-facing text written from the stored ConstraintResult. No guarantee language."""
    codes = ", ".join(checks["failure_codes"])
    if status == DesignState.PASS_SUPPORTED_CHECKS.value:
        cut = next(
            (r["required_mm"] for r in checks["residuals"] if r["quantity"] == "garment_length"),
            None,
        )
        base = "The implemented checks passed for this design."
        if cut is not None:
            base += f" The cut mark is {cut:g} mm below the shoulder point."
        return f"{base} {SIDE_SEAM_NOTE}"[:600]
    if status == DesignState.FAILED_CHECKS.value:
        text = f"These checks did not pass: {codes}."
        for r in checks["residuals"]:
            if r["residual_mm"] < 0:
                text += (
                    f" The design needs {r['required_mm']:g} mm "
                    f"but {r['available_mm']:g} mm is available."
                )
                break
        return f"{text} No cut plan is offered."[:600]
    if status == DesignState.NEEDS_INPUT.value:
        missing = ", ".join(checks["missing_dimensions"]) or codes
        return (
            f"More input is needed before this can be checked: {missing}. Measure with a tape or "
            "ruler, confirm the value and check again. No cut plan is offered."
        )[:600]
    return (
        f"No reviewed recipe supports this idea yet ({codes}). It stays an idea you can explore or "
        "discuss with a tailor. No cut plan is offered."
    )[:600]
