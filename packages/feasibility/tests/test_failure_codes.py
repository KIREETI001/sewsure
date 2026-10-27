"""One test per FailureCode, plus fail-closed registry behaviour and model validation."""

from __future__ import annotations

import pytest

from conftest import CONFIRMED, RECIPE, meas, params, rect, shirt
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
    evaluate,
)


def test_all_failure_codes_are_covered() -> None:
    names = [n for n in globals() if n.startswith("test_code_")]
    for code in FailureCode:
        assert any(
            n.removeprefix("test_code_") in code.value.lower() or code.value.lower() in n
            for n in names
        ), code


def test_code_recipe_not_allowed(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(), "not_a_real_recipe", params())
    assert r.status is DesignState.IDEA_ONLY
    assert r.failure_codes == (FailureCode.RECIPE_NOT_ALLOWED,)
    assert r.recipe_version is None and r.cut_mark_mm is None


def test_registry_is_allow_list() -> None:
    assert {"woven_shirt_crop_v1"} == ALLOWED_RECIPE_IDS
    # near-miss IDs must not resolve
    for rid in ("woven_shirt_crop_v2", "WOVEN_SHIRT_CROP_V1", "woven_shirt_crop_v1 ", ""):
        assert evaluate(shirt(), meas(), rid, params()).failure_codes == (
            FailureCode.RECIPE_NOT_ALLOWED,
        )


def test_code_category_unknown() -> None:
    r = evaluate(shirt(category=None), meas(), RECIPE, params())
    assert r.status is DesignState.NEEDS_INPUT
    assert FailureCode.CATEGORY_UNKNOWN in r.failure_codes
    assert "garment_category" in r.missing_dimensions


def test_code_category_not_supported() -> None:
    r = evaluate(shirt(category="dress"), meas(), RECIPE, params())
    assert r.status is DesignState.IDEA_ONLY
    assert r.failure_codes == (FailureCode.CATEGORY_NOT_SUPPORTED,)


def test_code_material_unknown() -> None:
    r = evaluate(shirt(material=None), meas(), RECIPE, params())
    assert r.status is DesignState.NEEDS_INPUT
    assert FailureCode.MATERIAL_UNKNOWN in r.failure_codes
    assert "material" in r.missing_dimensions


def test_code_material_not_supported() -> None:
    r = evaluate(shirt(material="knit"), meas(), RECIPE, params())
    assert r.status is DesignState.IDEA_ONLY
    assert r.failure_codes == (FailureCode.MATERIAL_NOT_SUPPORTED,)
    assert r.cut_mark_mm is None


def test_code_missing_dimension(good_shirt: Garment) -> None:
    m = meas()
    del m["chest_width"]
    r = evaluate(good_shirt, m, RECIPE, params())
    assert r.status is DesignState.NEEDS_INPUT
    assert r.failure_codes == (FailureCode.MISSING_DIMENSION,)
    assert r.missing_dimensions == ("chest_width",)


def test_code_missing_param(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(), RECIPE, {"finished_length_mm": 500.0})
    assert r.status is DesignState.NEEDS_INPUT
    assert r.failure_codes == (FailureCode.MISSING_PARAM,)
    assert r.missing_dimensions == ("hem_allowance_mm",)


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_code_non_finite_value(good_shirt: Garment, bad: float) -> None:
    r = evaluate(good_shirt, meas(), RECIPE, params(finished=bad))
    assert r.status is DesignState.NEEDS_INPUT
    assert r.failure_codes == (FailureCode.NON_FINITE_VALUE,)
    m = meas()
    m["chest_width"] = Measurement(bad, "tape_measure", CONFIRMED)
    assert evaluate(good_shirt, m, RECIPE, params()).failure_codes == (
        FailureCode.NON_FINITE_VALUE,
    )


def test_code_unit_mix_up_suspected_both_directions(good_shirt: Garment) -> None:
    low = evaluate(good_shirt, meas(length_mm=78.0), RECIPE, params())  # cm entered as mm
    high = evaluate(good_shirt, meas(chest_mm=5200.0), RECIPE, params())  # mm entered as cm*10
    for r in (low, high):
        assert r.status is DesignState.NEEDS_INPUT
        assert r.failure_codes == (FailureCode.UNIT_MIX_UP_SUSPECTED,)


def test_code_dimension_implausible(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(chest_mm=5.0), RECIPE, params())  # not a x10 slip either
    assert r.status is DesignState.NEEDS_INPUT
    assert r.failure_codes == (FailureCode.DIMENSION_IMPLAUSIBLE,)


def test_code_finished_length_exceeds_available() -> None:
    r = evaluate(shirt(with_zones=False), meas(500), RECIPE, params(600, 30))
    assert r.failure_codes == (FailureCode.FINISHED_LENGTH_EXCEEDS_AVAILABLE,)
    assert r.status is DesignState.FAILED_CHECKS


def test_code_no_positive_remainder() -> None:
    r = evaluate(shirt(with_zones=False), meas(500), RECIPE, params(480, 30))
    assert r.failure_codes == (FailureCode.NO_POSITIVE_REMAINDER,)
    assert r.residuals_mm["remainder_mm"] == -10.0


def test_code_prohibited_zone_intersection_side_seam_feature() -> None:
    # cut mark 420 crosses the side-seam feature on the back panel (y 400-450)
    r = evaluate(shirt(), meas(), RECIPE, params(390, 30))
    assert r.status is DesignState.FAILED_CHECKS
    assert r.failure_codes == (FailureCode.PROHIBITED_ZONE_INTERSECTION,)


def test_zone_clearance_reported_when_clear(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(), RECIPE, params(500, 30))  # cut 530, placket starts 600
    assert r.residuals_mm["clearance_mm:g1:front_left:placket_end"] == 70.0
    assert "PROHIBITED_ZONES_NOT_PROVIDED" not in r.uncertainty_flags


def test_no_zones_given_is_flagged_not_assumed_clear() -> None:
    r = evaluate(shirt(with_zones=False), meas(), RECIPE, params())
    assert r.status is DesignState.PASS_SUPPORTED_CHECKS
    assert "PROHIBITED_ZONES_NOT_PROVIDED" in r.uncertainty_flags


def test_unconfirmed_measurement_flagged(good_shirt: Garment) -> None:
    m = meas()
    m["chest_width"] = Measurement(520.0, "photo_estimate")
    r = evaluate(good_shirt, m, RECIPE, params())
    assert "MEASUREMENT_UNCONFIRMED" in r.uncertainty_flags


def test_sleeve_zones_not_checked_against_body_cut() -> None:
    sleeve = FabricPanel(
        "g1",
        Side.SLEEVE_LEFT,
        rect(0, 0, 200, 700),
        prohibited_regions=(Zone("cuff", "seam", rect(0, 500, 200, 600)),),
    )
    g = shirt(with_zones=False)
    g = Garment(g.garment_id, g.category, g.material, (*g.panels, sleeve))
    assert evaluate(g, meas(), RECIPE, params()).status is DesignState.PASS_SUPPORTED_CHECKS


def test_to_dict_has_everything_and_no_bare_boolean(good_shirt: Garment) -> None:
    d = evaluate(good_shirt, meas(), RECIPE, params()).to_dict()
    for key in (
        "status",
        "hard_pass",
        "failure_codes",
        "residuals_mm",
        "missing_dimensions",
        "uncertainty_flags",
        "recipe_id",
        "recipe_version",
        "engine_version",
    ):
        assert key in d


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
