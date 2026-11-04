"""One test per FailureCode, X1 review regressions, registry and model validation."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from conftest import CONFIRMED, meas, params, rect, shirt
from conftest import ev as evaluate
from sewsure_feasibility import (
    ALLOWED_RECIPE_IDS,
    DesignState,
    FabricPanel,
    FailureCode,
    Garment,
    Measurement,
    PatternPiece,
    Placement,
    Side,
    Zone,
    supersede,
)

EXPECTED_CODE_TESTS = {
    FailureCode.UNSUPPORTED_RECIPE: "test_code_unsupported_recipe",
    FailureCode.UNSUPPORTED_GARMENT_CATEGORY: "test_code_unsupported_garment_category",
    FailureCode.UNSUPPORTED_MATERIAL: "test_code_unsupported_material",
    FailureCode.MATERIAL_UNKNOWN: "test_code_material_unknown",
    FailureCode.CATEGORY_UNKNOWN: "test_unknown_category_needs_input",
    FailureCode.MISSING_DIMENSION: "test_code_missing_dimension",
    FailureCode.UNCONFIRMED_DIMENSION: "test_x1_1_unconfirmed_measurement_never_passes_or_cuts",
    FailureCode.MISSING_PARAMETER: "test_missing_param",
    FailureCode.INVALID_PARAMETER: "test_invalid_parameter",
    FailureCode.NON_FINITE_VALUE: "test_non_finite_values_need_input_not_crash",
    FailureCode.CONFLICTING_DIMENSIONS: "test_code_conflicting_dimensions",
    FailureCode.IMPLAUSIBLE_DIMENSION: "test_code_implausible_dimension_no_unit_explanation",
    FailureCode.POSSIBLE_UNIT_ERROR: "test_code_possible_unit_error_both_directions",
    FailureCode.INSUFFICIENT_LENGTH: "test_code_insufficient_length_finished_exceeds",
    FailureCode.NO_POSITIVE_REMAINDER: "test_code_no_positive_remainder",
    FailureCode.CUT_INTERSECTS_PROHIBITED_REGION: "test_code_cut_intersects_prohibited_region",
    FailureCode.MISSING_PROHIBITED_ZONES: "test_x1_2_no_zone_data_cannot_pass",
}


def test_every_failure_code_has_a_test() -> None:
    assert set(EXPECTED_CODE_TESTS) == set(FailureCode)
    for name in EXPECTED_CODE_TESTS.values():
        assert name in globals(), name


def test_failure_codes_match_contract_vocabulary() -> None:
    # Subset of K1 contract 1.0.0-draft.2 FailureCode the engine may emit.
    contract = {
        "UNSUPPORTED_RECIPE", "UNSUPPORTED_GARMENT_CATEGORY", "UNSUPPORTED_MATERIAL",
        "MATERIAL_UNKNOWN", "MISSING_DIMENSION", "CONFLICTING_DIMENSIONS",
        "IMPLAUSIBLE_DIMENSION", "INSUFFICIENT_LENGTH", "CUT_INTERSECTS_PROHIBITED_REGION",
        "CATEGORY_UNKNOWN", "UNCONFIRMED_DIMENSION", "POSSIBLE_UNIT_ERROR", "NON_FINITE_VALUE",
        "MISSING_PARAMETER", "INVALID_PARAMETER", "NO_POSITIVE_REMAINDER",
        "MISSING_PROHIBITED_ZONES",
    }  # fmt: skip
    assert {c.value for c in FailureCode} == contract


def test_code_unsupported_recipe(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(), "not_a_real_recipe")
    assert r.status is DesignState.IDEA_ONLY
    assert r.failure_codes == (FailureCode.UNSUPPORTED_RECIPE,)
    assert r.recipe_version is None and r.cut_mark_mm is None


def test_registry_is_allow_list() -> None:
    assert {"woven_shirt_crop_v1"} == ALLOWED_RECIPE_IDS
    for rid in ("woven_shirt_crop_v2", "WOVEN_SHIRT_CROP_V1", "woven_shirt_crop_v1 ", ""):
        r = evaluate(shirt(), meas(), rid)
        assert r.failure_codes == (FailureCode.UNSUPPORTED_RECIPE,)


def test_code_unsupported_garment_category() -> None:
    r = evaluate(shirt(category="other"), meas())
    assert r.status is DesignState.IDEA_ONLY
    assert r.failure_codes == (FailureCode.UNSUPPORTED_GARMENT_CATEGORY,)


@pytest.mark.parametrize("category", [None, "unknown"])
def test_unknown_category_needs_input(category: str | None) -> None:
    r = evaluate(shirt(category=category), meas())
    assert r.status is DesignState.NEEDS_INPUT
    assert r.failure_codes == (FailureCode.CATEGORY_UNKNOWN,)
    assert r.missing_dimensions == ("garment_category",)


def test_code_unsupported_material() -> None:
    r = evaluate(shirt(material="knit"), meas())
    assert r.status is DesignState.IDEA_ONLY
    assert r.failure_codes == (FailureCode.UNSUPPORTED_MATERIAL,)
    assert r.cut_mark_mm is None


@pytest.mark.parametrize("material", [None, "unknown"])
def test_code_material_unknown(material: str | None) -> None:
    r = evaluate(shirt(material=material), meas())
    assert r.status is DesignState.NEEDS_INPUT
    assert FailureCode.MATERIAL_UNKNOWN in r.failure_codes
    assert "fabric_family" in r.missing_dimensions


def test_code_missing_dimension(good_shirt: Garment) -> None:
    m = meas()
    del m["chest_flat_width"]
    r = evaluate(good_shirt, m)
    assert r.status is DesignState.NEEDS_INPUT
    assert r.failure_codes == (FailureCode.MISSING_DIMENSION,)
    assert r.missing_dimensions == ("chest_flat_width",)


def test_missing_param(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(), p={"finished_length_mm": 500.0})
    assert r.status is DesignState.NEEDS_INPUT
    assert r.failure_codes == (FailureCode.MISSING_PARAMETER,)
    assert r.missing_dimensions == ("hem_allowance_mm",)


def test_code_conflicting_dimensions(good_shirt: Garment) -> None:
    # X1 finding 4 (N2 case MU-04): flat 520 mm implies ~1040 mm circumference, not 800.
    m = meas()
    m["chest_circumference"] = Measurement(800.0, "user_tape_measured", CONFIRMED)
    r = evaluate(good_shirt, m)
    assert r.status is DesignState.NEEDS_INPUT
    assert r.failure_codes == (FailureCode.CONFLICTING_DIMENSIONS,)
    assert set(r.missing_dimensions) == {"chest_flat_width", "chest_circumference"}
    assert r.cut_mark_mm is None


def test_consistent_circumference_passes(good_shirt: Garment) -> None:
    m = meas()
    m["chest_circumference"] = Measurement(1050.0, "user_tape_measured", CONFIRMED)
    assert evaluate(good_shirt, m).status is DesignState.PASS_SUPPORTED_CHECKS


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_non_finite_values_need_input_not_crash(good_shirt: Garment, bad: float) -> None:
    r = evaluate(good_shirt, meas(), p=params(finished=bad))
    assert r.failure_codes == (FailureCode.NON_FINITE_VALUE,)
    assert r.missing_dimensions == ("finished_length_mm",)
    m = meas()
    m["chest_flat_width"] = Measurement(bad, "user_tape_measured", CONFIRMED)
    r2 = evaluate(good_shirt, m)
    assert r2.failure_codes == (FailureCode.NON_FINITE_VALUE,)
    assert r2.status is DesignState.NEEDS_INPUT
    assert r2.missing_dimensions == ("chest_flat_width",)


def test_code_possible_unit_error_both_directions(good_shirt: Garment) -> None:
    low = evaluate(good_shirt, meas(length_mm=78.0))  # cm entered as mm
    high = evaluate(good_shirt, meas(chest_mm=5200.0))
    for r in (low, high):
        assert r.status is DesignState.NEEDS_INPUT
        assert r.failure_codes == (FailureCode.POSSIBLE_UNIT_ERROR,)


def test_code_implausible_dimension_no_unit_explanation(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(chest_mm=5.0))
    assert r.failure_codes == (FailureCode.IMPLAUSIBLE_DIMENSION,)


def test_code_insufficient_length_finished_exceeds() -> None:
    r = evaluate(shirt(zones="minimal"), meas(500), p=params(600, 30))
    assert r.failure_codes == (FailureCode.INSUFFICIENT_LENGTH,)
    assert r.status is DesignState.FAILED_CHECKS
    assert r.checks[2].result == "fail"


def test_code_no_positive_remainder() -> None:
    r = evaluate(shirt(zones="minimal"), meas(500), p=params(480, 30))
    assert r.failure_codes == (FailureCode.NO_POSITIVE_REMAINDER,)
    assert r.residual_mm("garment_length") == -10.0


def test_code_cut_intersects_prohibited_region() -> None:
    # cut mark 420 crosses the side-seam feature on the back panel (y 400-450)
    r = evaluate(shirt(), meas(), p=params(390, 30))
    assert r.status is DesignState.FAILED_CHECKS
    assert r.failure_codes == (FailureCode.CUT_INTERSECTS_PROHIBITED_REGION,)
    assert r.checks[3].result == "fail"


# ---- X1 review regressions -------------------------------------------------------------


def test_x1_1_unconfirmed_measurement_never_passes_or_cuts(good_shirt: Garment) -> None:
    """Critical: a vision-suggested, unconfirmed length must not reach PASS or a cut mark."""
    m = {
        "shoulder_to_hem": Measurement(780.0, "vision_suggested", None),
        "chest_flat_width": Measurement(520.0, "vision_suggested", None),
    }
    r = evaluate(good_shirt, m, p=params(500, 25))
    assert r.status is DesignState.NEEDS_INPUT and not r.hard_pass
    assert r.cut_mark_mm is None and r.residuals == ()
    assert r.failure_codes == (FailureCode.UNCONFIRMED_DIMENSION,)
    assert set(r.missing_dimensions) == {"shoulder_to_hem", "chest_flat_width"}


def test_x1_1_one_unconfirmed_is_enough(good_shirt: Garment) -> None:
    m = meas()
    m["chest_flat_width"] = Measurement(520.0, "photo_estimate")
    r = evaluate(good_shirt, m)
    assert r.status is DesignState.NEEDS_INPUT
    assert r.missing_dimensions == ("chest_flat_width",)


def test_x1_1_confirmed_measurement_still_passes(good_shirt: Garment) -> None:
    assert evaluate(good_shirt, meas()).status is DesignState.PASS_SUPPORTED_CHECKS


def test_x1_2_no_zone_data_cannot_pass() -> None:
    """Major: a gate that did not run is not a gate that passed."""
    for g in (shirt(zones="none"), Garment("g-1", "woven_shirt", "woven")):
        r = evaluate(g, meas())
        assert r.status is DesignState.NEEDS_INPUT and not r.hard_pass
        assert r.failure_codes == (FailureCode.MISSING_PROHIBITED_ZONES,)
        assert r.missing_dimensions == ("prohibited_regions",)
        assert r.cut_mark_mm is None


def test_zones_on_only_some_panels_cannot_pass() -> None:
    """A cut through the placket must not pass because the front zones were never supplied."""
    zone = (Zone("yoke", "seam", rect(0, 0, 10, 10)),)
    placket = (Zone("placket_end", "placket_end", rect(230, 500, 260, 600)),)
    panel = {
        side: FabricPanel("g", side, rect(0, 0, 260, 780))
        for side in (Side.BACK, Side.FRONT_LEFT, Side.FRONT_RIGHT)
    }
    back = FabricPanel("g", Side.BACK, rect(0, 0, 520, 780), prohibited_regions=zone)
    left = FabricPanel("g", Side.FRONT_LEFT, rect(0, 0, 260, 780), prohibited_regions=placket)
    for panels in (
        (back,),
        (back, panel[Side.FRONT_LEFT], panel[Side.FRONT_RIGHT]),
        (back, left, panel[Side.FRONT_RIGHT]),
    ):
        r = evaluate(Garment("g", "woven_shirt", "woven", panels), meas(), p=params(530, 20))
        assert r.status is DesignState.NEEDS_INPUT and not r.hard_pass
        assert r.failure_codes == (FailureCode.MISSING_PROHIBITED_ZONES,)
        assert r.cut_mark_mm is None


def test_x1_3_string_and_bool_params_do_not_crash(good_shirt: Garment) -> None:
    """Major: K1's PASS fixture carries ``hem_finish: "double_fold"``."""
    r = evaluate(
        good_shirt, meas(), p={**params(500, 25), "hem_finish": "double_fold", "flag": True}
    )
    assert r.status is DesignState.PASS_SUPPORTED_CHECKS
    assert "IGNORED_PARAMETERS" in r.uncertainty_flags  # "flag" is not on the allow-list
    assert "hem_finish" not in " ".join(r.details)


def test_x1_3_wrong_type_for_length_param(good_shirt: Garment) -> None:
    for bad in ("500", True):
        r = evaluate(good_shirt, meas(), p={"finished_length_mm": bad, "hem_allowance_mm": 30.0})
        assert r.status is DesignState.NEEDS_INPUT
        assert r.failure_codes == (FailureCode.INVALID_PARAMETER,)
        assert r.missing_dimensions == ("finished_length_mm",)


def test_invalid_parameter() -> None:
    for bad in (0.0, -30.0):
        r = evaluate(shirt(), meas(), p={"finished_length_mm": 500.0, "hem_allowance_mm": bad})
        assert r.status is DesignState.NEEDS_INPUT
        assert r.failure_codes == (FailureCode.INVALID_PARAMETER,)
        assert r.missing_dimensions == ("hem_allowance_mm",)


def test_x1_5_supersede_only_passed_results(good_shirt: Garment) -> None:
    failed = evaluate(shirt(zones="minimal"), meas(500), p=params(600, 30))
    with pytest.raises(ValueError, match="only a passed result"):
        supersede(failed)
    assert failed.status is DesignState.FAILED_CHECKS
    assert supersede(evaluate(good_shirt, meas())).status is DesignState.SUPERSEDED


# ---- contract shape ---------------------------------------------------------------------


def test_contract_dict_has_exactly_contract_keys(good_shirt: Garment) -> None:
    d = evaluate(good_shirt, meas()).to_contract_dict()
    assert set(d) == {
        "hard_pass",
        "failure_codes",
        "residuals",
        "missing_dimensions",
        "uncertainty_flags",
        "checks",
        "alternatives",
        "engine_version",
        "checked_at",
    }
    assert d["checked_at"] == "2026-10-28T12:00:00Z"
    assert d["residuals"][0] == {
        "check_id": "length_gate",
        "quantity": "garment_length",
        "required_mm": 530.0,
        "available_mm": 780.0,
        "residual_mm": 250.0,
        "tolerance_mm": None,
    }
    assert all(f.isupper() for f in d["uncertainty_flags"])


def test_needs_input_always_names_a_missing_dimension() -> None:
    cases = [
        evaluate(shirt(), meas(chest_mm=60.0)),
        evaluate(shirt(), meas(), p={}),
        evaluate(shirt(zones="none"), meas()),
        evaluate(shirt(material=None), meas()),
    ]
    for r in cases:
        assert r.status is DesignState.NEEDS_INPUT
        assert r.missing_dimensions


def test_hard_pass_implies_no_codes_or_missing(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas())
    assert r.hard_pass and r.failure_codes == () and r.missing_dimensions == ()


def test_checked_at_defaults_to_now_utc(good_shirt: Garment) -> None:
    from sewsure_feasibility import evaluate as raw

    r = raw(good_shirt, meas(), "woven_shirt_crop_v1", params())
    assert abs((datetime.now(UTC) - r.checked_at).total_seconds()) < 60


def test_zone_clearance_reported_when_clear(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(), p=params(500, 30))  # cut 530, placket starts 600
    assert r.residual_mm("clearance_g1_front_left_placket_end") == 70.0


def test_sleeve_zones_not_checked_against_body_cut() -> None:
    sleeve = FabricPanel(
        "g1",
        Side.SLEEVE_LEFT,
        rect(0, 0, 200, 700),
        prohibited_regions=(Zone("cuff", "seam", rect(0, 500, 200, 600)),),
    )
    g = shirt(zones="minimal")
    g = Garment(g.garment_id, g.category, g.material, (*g.panels, sleeve))
    assert evaluate(g, meas()).status is DesignState.PASS_SUPPORTED_CHECKS


def test_model_validation() -> None:
    with pytest.raises(ValueError):
        Measurement(100.0, " ")
    with pytest.raises(ValueError):
        FabricPanel("g", Side.BACK, ((0, 0), (1, 1)))
    with pytest.raises(ValueError):
        FabricPanel("g", Side.BACK, ((0, 0), (10, 10), (10, 0), (0, 10)))  # bow-tie
    with pytest.raises(ValueError):
        PatternPiece("woven_shirt_crop_v1", cut_count=0)
    with pytest.raises(ValueError):
        Placement("g:back", (0.0, 0.0), revision_ref="")
    assert FabricPanel("g", Side.BACK, rect(0, 0, 500, 780)).bounding_dimensions_mm == (500, 780)
