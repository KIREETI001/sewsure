"""Integration tests for original garment evaluation."""

import pytest

from conftest import CHECKED_AT, CONFIRMED, RECIPE, meas, params, shirt
from sewsure_feasibility import (
    DesignState,
    FabricComposition,
    FabricProperties,
    FailureCode,
    Garment,
    GarmentCondition,
    GarmentConstruction,
    GarmentProfile,
    Measurement,
    OriginalGarmentRecord,
    evaluate_original_garment,
)


def make_record(
    *,
    measurements: dict[str, Measurement] | None = None,
    garment: Garment | None = None,
) -> OriginalGarmentRecord:
    garment = garment if garment is not None else shirt()

    return OriginalGarmentRecord(
        profile=GarmentProfile(
            profile_id="profile-001",
            garment=garment,
            measurements=measurements if measurements is not None else meas(),
        ),
        fabric=FabricProperties(
            composition=FabricComposition.COTTON,
        ),
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


def test_matching_chest_circumference_passes() -> None:
    measurements = meas()
    measurements["chest_circumference"] = Measurement(
        1040.0,
        "tape_measure",
        CONFIRMED,
    )

    record = make_record(measurements=measurements)

    result = evaluate_original_garment(
        record,
        RECIPE,
        params(),
        checked_at=CHECKED_AT,
    )

    assert result.status is DesignState.PASS_SUPPORTED_CHECKS
    assert result.hard_pass
    assert result.failure_codes == ()


def test_conflicting_chest_circumference_needs_input() -> None:
    measurements = meas()
    measurements["chest_circumference"] = Measurement(
        1300.0,
        "tape_measure",
        CONFIRMED,
    )

    record = make_record(measurements=measurements)

    result = evaluate_original_garment(
        record,
        RECIPE,
        params(),
        checked_at=CHECKED_AT,
    )

    assert result.status is DesignState.NEEDS_INPUT
    assert FailureCode.CONFLICTING_DIMENSIONS in result.failure_codes
    assert result.cut_mark_mm is None


def test_missing_optional_chest_circumference_does_not_block_evaluation() -> None:
    record = make_record(measurements=meas())

    result = evaluate_original_garment(
        record,
        RECIPE,
        params(),
        checked_at=CHECKED_AT,
    )

    assert result.status is DesignState.PASS_SUPPORTED_CHECKS
    assert result.hard_pass
    assert FailureCode.CONFLICTING_DIMENSIONS not in result.failure_codes


def test_knitted_fabric_is_rejected() -> None:
    with pytest.raises(ValueError, match="Only woven fabrics are supported"):
        FabricProperties(
            structure="knitted",
        )


def test_stretchy_fabric_is_rejected() -> None:
    with pytest.raises(ValueError, match="Only non-stretch fabrics are supported"):
        FabricProperties(
            stretch_level="low",
        )
