"""Integration tests for unified original garment records."""

import pytest

from sewsure_feasibility import (
    FabricProperties,
    Garment,
    GarmentCondition,
    GarmentConstruction,
    GarmentProfile,
    OriginalGarmentRecord,
)


def make_garment(garment_id: str = "shirt-001") -> Garment:
    return Garment(
        garment_id,
        "woven_shirt",
        "woven",
    )


def make_record(
    garment: Garment | None = None,
) -> OriginalGarmentRecord:
    garment = garment or make_garment()

    return OriginalGarmentRecord(
        profile=GarmentProfile(
            profile_id="profile-001",
            garment=garment,
            measurements={},
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


def test_create_original_garment_record() -> None:
    record = make_record()

    assert record.garment_id == "shirt-001"
    assert record.garment == make_garment()


def test_record_preserves_all_four_models() -> None:
    record = make_record()

    assert isinstance(record.profile, GarmentProfile)
    assert isinstance(record.fabric, FabricProperties)
    assert isinstance(record.construction, GarmentConstruction)
    assert isinstance(record.condition, GarmentCondition)


def test_empty_defect_list_is_preserved() -> None:
    record = make_record()

    assert not record.is_damaged
    assert record.condition.defects == ()


def test_mismatched_construction_garment_is_rejected() -> None:
    record = make_record()

    invalid_construction = GarmentConstruction(
        garment=make_garment("shirt-002"),
        components=(),
    )

    with pytest.raises(ValueError, match="same original garment"):
        OriginalGarmentRecord(
            profile=record.profile,
            fabric=record.fabric,
            construction=invalid_construction,
            condition=record.condition,
        )


def test_mismatched_condition_garment_is_rejected() -> None:
    record = make_record()

    invalid_condition = GarmentCondition(
        garment=make_garment("shirt-002"),
        defects=(),
    )

    with pytest.raises(ValueError, match="same original garment"):
        OriginalGarmentRecord(
            profile=record.profile,
            fabric=record.fabric,
            construction=record.construction,
            condition=invalid_condition,
        )


def test_mismatched_garment_metadata_is_rejected() -> None:
    record = make_record()

    conflicting_garment = Garment(
        "shirt-001",
        "different_category",
        "woven",
    )

    invalid_construction = GarmentConstruction(
        garment=conflicting_garment,
        components=(),
    )

    with pytest.raises(ValueError, match="same original garment"):
        OriginalGarmentRecord(
            profile=record.profile,
            fabric=record.fabric,
            construction=invalid_construction,
            condition=record.condition,
        )


def test_original_garment_record_is_immutable() -> None:
    from dataclasses import FrozenInstanceError

    record = make_record()

    attribute_name = "fabric"

    with pytest.raises(FrozenInstanceError):
        setattr(record, attribute_name, FabricProperties())
