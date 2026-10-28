"""The seven unit tests from blueprint §5.5."""

from __future__ import annotations

import dataclasses

import pytest
from hypothesis import given
from hypothesis import strategies as st

from conftest import CONFIRMED, meas, params, shirt
from conftest import ev as evaluate
from sewsure_feasibility import (
    DesignState,
    FailureCode,
    Garment,
    Measurement,
    cm_to_mm,
    supersede,
)


def test_1_normal_crop_positive_remainder_and_hem(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(), p=params(500, 30))
    assert r.status is DesignState.PASS_SUPPORTED_CHECKS and r.hard_pass
    assert r.cut_mark_mm == 530.0
    assert r.residual_mm("garment_length") == 250.0
    assert r.failure_codes == ()
    assert r.recipe_version == "1.0.0" and r.engine_version
    assert "side_seams_not_verified" in r.uncertainty_flags
    assert [c.result for c in r.checks] == ["pass"] * 4


def test_2_finished_length_greater_than_available(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(780), p=params(900, 30))
    assert r.status is DesignState.FAILED_CHECKS
    assert FailureCode.INSUFFICIENT_LENGTH in r.failure_codes
    assert not r.hard_pass


@pytest.mark.parametrize(
    ("finished", "hem", "status", "code"),
    [
        (749.5, 30.0, DesignState.PASS_SUPPORTED_CHECKS, None),  # 0.5 mm remainder
        (750.0, 30.0, DesignState.FAILED_CHECKS, FailureCode.INSUFFICIENT_LENGTH),  # exact fit
        (750.5, 30.0, DesignState.FAILED_CHECKS, FailureCode.INSUFFICIENT_LENGTH),  # -0.5 mm
    ],
)
def test_3_near_boundary_allowance(
    finished: float, hem: float, status: DesignState, code: FailureCode | None
) -> None:
    r = evaluate(shirt(zones="minimal"), meas(780), p=params(finished, hem))
    assert r.status is status
    assert (code in r.failure_codes) if code else r.failure_codes == ()


def test_3_seam_exclusion_conflict(good_shirt: Garment) -> None:
    # cut mark 650 crosses the placket-end zone (y 600-780)
    r = evaluate(good_shirt, meas(780), p=params(620, 30))
    assert r.status is DesignState.FAILED_CHECKS
    assert FailureCode.CUT_INTERSECTS_PROHIBITED_REGION in r.failure_codes
    assert r.residual_mm("clearance_g1_front_left_placket_end") == 0.0


def test_4_cm_and_mm_agree(good_shirt: Garment) -> None:
    in_mm = {
        "shoulder_to_hem": Measurement(780.0, "user_tape_measured", CONFIRMED),
        "chest_flat_width": Measurement(520.0, "user_tape_measured", CONFIRMED),
    }
    in_cm = {
        "shoulder_to_hem": Measurement.from_cm(78.0, "user_tape_measured", CONFIRMED),
        "chest_flat_width": Measurement.from_cm(52.0, "user_tape_measured", CONFIRMED),
    }
    a = evaluate(good_shirt, in_mm, p=params(500, 30))
    b = evaluate(good_shirt, in_cm, p=params(cm_to_mm(50), cm_to_mm(3)))
    assert a == b


@given(cm=st.integers(min_value=25, max_value=110))
def test_4_cm_mm_agree_for_any_length(cm: int) -> None:
    g = shirt(zones="minimal")
    a = evaluate(g, meas(cm * 10.0), p=params(200, 30))
    m = meas()
    m["shoulder_to_hem"] = Measurement.from_cm(float(cm), "tape_measure", CONFIRMED)
    b = evaluate(g, m, p=params(200, 30))
    assert a == b


def test_5_chest_width_6cm_for_60cm_flagged_before_geometry(good_shirt: Garment) -> None:
    r = evaluate(good_shirt, meas(chest_mm=60.0))
    assert r.status is DesignState.NEEDS_INPUT
    assert r.failure_codes == (FailureCode.IMPLAUSIBLE_DIMENSION,)
    assert "possible_unit_error" in r.uncertainty_flags
    assert r.missing_dimensions == ("chest_flat_width",)  # NEEDS_INPUT always names something
    assert r.cut_mark_mm is None and r.residuals == ()


def test_6_edit_creates_new_revision_old_frozen(good_shirt: Garment) -> None:
    old = evaluate(good_shirt, meas(), p=params(500, 30), revision_ref="rev-1")
    new = evaluate(good_shirt, meas(), p=params(480, 30), revision_ref="rev-2")
    assert old.revision_ref == "rev-1" and new.revision_ref == "rev-2"
    assert old.input_fingerprint != new.input_fingerprint
    assert old.cut_mark_mm == 530.0 and new.cut_mark_mm == 510.0  # rechecked, recalculated
    snapshot = old.to_dict()
    gone = supersede(old)
    assert gone.status is DesignState.SUPERSEDED and not gone.hard_pass
    assert old.to_dict() == snapshot  # original untouched
    with pytest.raises(dataclasses.FrozenInstanceError):
        old.status = DesignState.FAILED_CHECKS  # type: ignore[misc]


@pytest.mark.parametrize("category", ["jersey_tee", "other", "dress", "trousers"])
def test_7_non_shirt_never_gets_shirt_pass_or_cut_points(category: str) -> None:
    r = evaluate(shirt(category=category), meas())
    assert r.status is DesignState.IDEA_ONLY
    assert not r.hard_pass
    assert r.cut_mark_mm is None
    assert r.residuals == ()
    assert r.failure_codes == (FailureCode.UNSUPPORTED_GARMENT_CATEGORY,)
