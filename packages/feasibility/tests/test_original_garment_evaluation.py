"""Integration tests for original garment evaluation."""

from conftest import CHECKED_AT, RECIPE, meas, params, shirt
from sewsure_feasibility import (
    DesignState,
    FabricProperties,
    FailureCode,
    GarmentCondition,
    GarmentConstruction,
    GarmentProfile,
    OriginalGarmentRecord,
    evaluate_original_garment,
)


def make_record(
    *,
    measurements=None,
    garment=None,
):
    garment = garment or shirt()

    return OriginalGarmentRecord(
        profile=GarmentProfile(
            profile_id="profile-001",
            garment=garment,
            measurements=measurements if measurements is not None else meas(),
        ),
        fabric=FabricProperties(),
        construction=GarmentConstruction(
            garment=garment,
            components=(),
        ),
        condition=GarmentCondition(
            garment=garment,
            defects=(),
        ),
    )


def test_valid_original_garment_passes() -> None:
    record = make_record()

    result = evaluate_original_garment(
        record,
        RECIPE,
        params(),
        checked_at=CHECKED_AT,
    )

    assert result.status is DesignState.PASS_SUPPORTED_CHECKS
    assert result.hard_pass
    assert result.failure_codes == ()


def test_missing_measurements_need_input() -> None:
    record = make_record(measurements={})

    result = evaluate_original_garment(
        record,
        RECIPE,
        params(),
        checked_at=CHECKED_AT,
    )

    assert result.status is DesignState.NEEDS_INPUT
    assert FailureCode.MISSING_DIMENSION in result.failure_codes
    assert result.cut_mark_mm is None


def test_unconfirmed_measurements_never_pass() -> None:
    from sewsure_feasibility import Measurement

    measurements = {
        "shoulder_to_hem": Measurement(
            780.0,
            "vision_suggested",
        ),
        "chest_flat_width": Measurement(
            520.0,
            "vision_suggested",
        ),
    }

    record = make_record(measurements=measurements)

    result = evaluate_original_garment(
        record,
        RECIPE,
        params(),
        checked_at=CHECKED_AT,
    )

    assert result.status is DesignState.NEEDS_INPUT
    assert FailureCode.UNCONFIRMED_DIMENSION in result.failure_codes
    assert result.cut_mark_mm is None


def test_unsupported_category_is_rejected() -> None:
    record = make_record(
        garment=shirt(category="other"),
    )

    result = evaluate_original_garment(
        record,
        RECIPE,
        params(),
        checked_at=CHECKED_AT,
    )

    assert result.status is DesignState.IDEA_ONLY
    assert FailureCode.UNSUPPORTED_GARMENT_CATEGORY in result.failure_codes


def test_unsupported_recipe_is_rejected() -> None:
    record = make_record()

    result = evaluate_original_garment(
        record,
        "unsupported_recipe",
        params(),
        checked_at=CHECKED_AT,
    )

    assert result.status is DesignState.IDEA_ONLY
    assert result.failure_codes == (FailureCode.UNSUPPORTED_RECIPE,)


def test_revision_reference_is_preserved() -> None:
    record = make_record()

    result = evaluate_original_garment(
        record,
        RECIPE,
        params(),
        revision_ref="revision-001",
        checked_at=CHECKED_AT,
    )

    assert result.revision_ref == "revision-001"
