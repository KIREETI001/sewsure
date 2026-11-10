from datetime import UTC, datetime
from typing import cast

import pytest

from conftest import CONFIRMED
from sewsure_feasibility import (
    GARMENT_MEASUREMENT_KEYS,
    Garment,
    GarmentProfile,
    Measurement,
)

CONFIRMED_AT = datetime(2026, 11, 5, tzinfo=UTC)


def make_measurement(
    value: float = 500.0,
    confirmed: bool = True,
) -> Measurement:
    return Measurement(
        value,
        "tape_measure",
        CONFIRMED_AT if confirmed else None,
    )


def make_profile() -> GarmentProfile:
    return GarmentProfile(
        profile_id="shirt-001",
        garment=Garment(
            "shirt-001",
            "woven_shirt",
            "woven",
        ),
        measurements={
            "shoulder_to_hem": make_measurement(780.0),
            "chest_flat_width": make_measurement(520.0),
        },
    )


def test_garment_profile_creation():
    profile = make_profile()

    assert profile.profile_id == "shirt-001"
    assert profile.garment.category == "woven_shirt"


def test_supported_measurement_keys():
    assert "shoulder_to_hem" in GARMENT_MEASUREMENT_KEYS
    assert "chest_flat_width" in GARMENT_MEASUREMENT_KEYS


def test_rejects_unknown_measurement():
    with pytest.raises(ValueError, match="Unsupported"):
        GarmentProfile(
            "shirt-001",
            Garment("shirt-001", "woven_shirt", "woven"),
            {"unknown_dimension": make_measurement()},
        )


@pytest.mark.parametrize("value", [0.0, -10.0, float("inf"), float("nan")])
def test_rejects_invalid_measurements(value: float):
    with pytest.raises(ValueError):
        GarmentProfile(
            "shirt-001",
            Garment("shirt-001", "woven_shirt", "woven"),
            {"shoulder_to_hem": make_measurement(value)},
        )


def test_rejects_empty_profile_id():
    with pytest.raises(ValueError, match="non-empty"):
        GarmentProfile(
            " ",
            Garment("shirt-001", "woven_shirt", "woven"),
            {},
        )


def test_missing_or_unconfirmed_measurements():
    profile = GarmentProfile(
        "shirt-001",
        Garment("shirt-001", "woven_shirt", "woven"),
        {
            "shoulder_to_hem": make_measurement(780.0),
            "chest_flat_width": make_measurement(520.0, False),
        },
    )

    assert profile.missing_or_unconfirmed(
        ("shoulder_to_hem", "chest_flat_width", "waist_flat_width")
    ) == ("chest_flat_width", "waist_flat_width")


def test_get_confirmed_value():
    profile = make_profile()

    assert profile.get_confirmed_value_mm("shoulder_to_hem") == 780.0
    assert profile.get_confirmed_value_mm("unknown") is None


def test_unconfirmed_value_is_not_returned():
    profile = GarmentProfile(
        "shirt-001",
        Garment("shirt-001", "woven_shirt", "woven"),
        {"chest_flat_width": make_measurement(520.0, False)},
    )

    assert profile.get_confirmed_value_mm("chest_flat_width") is None


def test_measurements_are_immutable():
    profile = make_profile()

    mutable_view = cast(dict[str, Measurement], profile.measurements)

    with pytest.raises(TypeError):
        mutable_view["waist_flat_width"] = make_measurement()


def test_chest_circumference_measurement_is_accepted() -> None:
    profile = GarmentProfile(
        profile_id="profile-001",
        garment=Garment("shirt-001", "woven_shirt", "woven"),
        measurements={
            "chest_circumference": Measurement(
                1040.0,
                "tape_measure",
                CONFIRMED,
            ),
        },
    )

    assert profile.get_confirmed_value_mm("chest_circumference") == 1040.0
