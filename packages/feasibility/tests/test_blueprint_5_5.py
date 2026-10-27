"""The seven unit tests from blueprint §5.5."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from conftest import CONFIRMED, RECIPE, meas, params, shirt
from sewsure_feasibility import (
    DesignState,
    FailureCode,
    Garment,
    Measurement,
    cm_to_mm,
    evaluate,
    supersede,
)


def test_1_normal_crop_positive_remainder_and_hem(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(), RECIPE, params(500, 30))
    assert r.status is DesignState.PASS_SUPPORTED_CHECKS and r.hard_pass
    assert r.cut_mark_mm == 530.0
    assert r.residuals_mm["remainder_mm"] == 250.0
    assert r.failure_codes == ()
    assert r.recipe_version == "1.0.0" and r.engine_version
    assert "SIDE_SEAMS_NOT_VERIFIED" in r.uncertainty_flags


def test_2_finished_length_greater_than_available(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(780), RECIPE, params(900, 30))
    assert r.status is DesignState.FAILED_CHECKS
    assert FailureCode.FINISHED_LENGTH_EXCEEDS_AVAILABLE in r.failure_codes
    assert not r.hard_pass


@pytest.mark.parametrize(
    ("finished", "hem", "status", "code"),
    [
        (749.5, 30.0, DesignState.PASS_SUPPORTED_CHECKS, None),  # 0.5 mm remainder
        (750.0, 30.0, DesignState.FAILED_CHECKS, FailureCode.NO_POSITIVE_REMAINDER),  # exact
        (750.5, 30.0, DesignState.FAILED_CHECKS, FailureCode.NO_POSITIVE_REMAINDER),  # -0.5 mm
    ],
)
def test_3_near_boundary_allowance(
    finished: float, hem: float, status: DesignState, code: FailureCode | None
) -> None:
    r = evaluate(shirt(with_zones=False), meas(780), RECIPE, params(finished, hem))
    assert r.status is status
    assert (code in r.failure_codes) if code else r.failure_codes == ()


def test_3_seam_exclusion_conflict(good_shirt: Garment) -> None:
    # cut mark 650 crosses the placket-end zone (y 600-780)
    r = evaluate(good_shirt, meas(780), RECIPE, params(620, 30))
    assert r.status is DesignState.FAILED_CHECKS
    assert FailureCode.PROHIBITED_ZONE_INTERSECTION in r.failure_codes
    assert r.residuals_mm["clearance_mm:g1:front_left:placket_end"] == 0.0


def test_4_cm_and_mm_agree(good_shirt: Garment) -> None:
    in_mm = {
        "shoulder_to_hem_length": Measurement(780.0, "tape_measure", CONFIRMED),
        "chest_width": Measurement(520.0, "tape_measure", CONFIRMED),
    }
    in_cm = {
        "shoulder_to_hem_length": Measurement.from_cm(78.0, "tape_measure", CONFIRMED),
        "chest_width": Measurement.from_cm(52.0, "tape_measure", CONFIRMED),
    }
    a = evaluate(good_shirt, in_mm, RECIPE, params(500, 30))
    b = evaluate(good_shirt, in_cm, RECIPE, params(cm_to_mm(50), cm_to_mm(3)))
    assert a == b


@given(cm=st.integers(min_value=25, max_value=110))
def test_4_cm_mm_agree_for_any_length(cm: int) -> None:
    g = shirt(with_zones=False)
    a = evaluate(g, meas(cm * 10.0), RECIPE, params(200, 30))
    b = evaluate(
        g,
        {
            "shoulder_to_hem_length": Measurement.from_cm(float(cm), "tape_measure", CONFIRMED),
            "chest_width": Measurement(520.0, "tape_measure", CONFIRMED),
        },
        RECIPE,
        params(200, 30),
    )
    assert a.status is b.status and a.failure_codes == b.failure_codes


def test_5_chest_width_6cm_for_60cm_flagged_before_geometry(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(chest_mm=60.0), RECIPE, params())
    assert r.status is DesignState.NEEDS_INPUT
    assert r.failure_codes == (FailureCode.UNIT_MIX_UP_SUSPECTED,)
    assert r.cut_mark_mm is None and r.residuals_mm == {}


def test_6_edit_creates_new_revision_old_frozen(good_shirt: Garment) -> None:
    old = evaluate(good_shirt, meas(), RECIPE, params(500, 30), revision_ref="rev-1")
    new = evaluate(good_shirt, meas(), RECIPE, params(480, 30), revision_ref="rev-2")
    assert old.revision_ref == "rev-1" and new.revision_ref == "rev-2"
    assert old.input_fingerprint != new.input_fingerprint
    assert old.cut_mark_mm == 530.0 and new.cut_mark_mm == 510.0  # rechecked, recalculated
    old_snapshot = old.to_dict()
    gone = supersede(old)
    assert gone.status is DesignState.SUPERSEDED and not gone.hard_pass
    assert old.to_dict() == old_snapshot  # original untouched
    with pytest.raises(AttributeError):
        old.status = DesignState.FAILED_CHECKS  # type: ignore[misc]


@pytest.mark.parametrize("category", ["t_shirt", "dress", "trousers", "hoodie"])
def test_7_non_shirt_never_gets_shirt_pass_or_cut_points(category: str) -> None:
    r = evaluate(shirt(category=category), meas(), RECIPE, params())
    assert r.status is DesignState.IDEA_ONLY
    assert not r.hard_pass
    assert r.cut_mark_mm is None
    assert "remainder_mm" not in r.residuals_mm
    assert r.failure_codes == (FailureCode.CATEGORY_NOT_SUPPORTED,)
