
from datetime import UTC, datetime

import pytest

from sewsure_feasibility import BodyProfile, Measurement


CONFIRMED_AT = datetime(2026, 11, 5, tzinfo=UTC)


def make_measurement(value_mm: float) -> Measurement:
    return Measurement(
        value_mm=value_mm,
        origin="user_measured",
        confirmed_at=CONFIRMED_AT,
    )


def test_create_body_profile() -> None:
    profile = BodyProfile(
        profile_id="user_001",
        measurements={
            "bust_circumference": make_measurement(900),
            "waist_circumference": make_measurement(760),
            "hip_circumference": make_measurement(980),
        },
    )

    assert profile.profile_id == "user_001"
    assert profile.get_confirmed_value_mm(
        "bust_circumference"
    ) == 900


def test_missing_measurements_are_detected() -> None:
    profile = BodyProfile(
        profile_id="user_001",
        measurements={
            "bust_circumference": make_measurement(900),
        },
    )

    missing = profile.missing_or_unconfirmed(
        (
            "bust_circumference",
            "waist_circumference",
            "hip_circumference",
        )
    )

    assert missing == ("waist_circumference", "hip_circumference")


def test_unconfirmed_measurement_is_not_accepted() -> None:
    profile = BodyProfile(
        profile_id="user_001",
        measurements={
            "bust_circumference": Measurement(
                value_mm=900,
                origin="user_measured",
                confirmed_at=None,
            ),
        },
    )

    assert profile.get_confirmed_value_mm(
        "bust_circumference"
    ) is None

    assert profile.missing_or_unconfirmed(
        ("bust_circumference",)
    ) == ("bust_circumference",)


def test_unknown_measurement_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        BodyProfile(
            profile_id="user_001",
            measurements={
                "unknown_measurement": make_measurement(900),
            },
        )


def test_non_positive_measurement_is_rejected() -> None:
    with pytest.raises(ValueError, match="positive"):
        BodyProfile(
            profile_id="user_001",
            measurements={
                "bust_circumference": make_measurement(0),
            },
        )


def test_empty_profile_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="profile_id"):
        BodyProfile(
            profile_id=" ",
            measurements={},
        )


def test_profile_measurements_cannot_be_modified() -> None:
    profile = BodyProfile(
        profile_id="user_001",
        measurements={
            "bust_circumference": make_measurement(900),
        },
    )

    with pytest.raises(TypeError):
        profile.measurements["waist_circumference"] = (
            make_measurement(760)
        )
