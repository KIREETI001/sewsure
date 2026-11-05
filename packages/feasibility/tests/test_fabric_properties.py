import pytest

from sewsure_feasibility import (
    FabricComposition,
    FabricProperties,
    FabricStructure,
    StretchLevel,
)


def test_cotton_woven_shirt_is_accepted() -> None:
    fabric = FabricProperties(composition="cotton")

    assert fabric.composition is FabricComposition.COTTON
    assert fabric.structure is FabricStructure.WOVEN
    assert fabric.stretch_level is StretchLevel.NONE


def test_polyester_woven_shirt_is_accepted() -> None:
    fabric = FabricProperties(composition="polyester")

    assert fabric.composition is FabricComposition.POLYESTER


def test_cotton_polyester_blend_is_accepted() -> None:
    fabric = FabricProperties(composition="cotton_polyester_blend")

    assert fabric.composition is FabricComposition.COTTON_POLYESTER_BLEND


def test_unknown_composition_is_accepted() -> None:
    fabric = FabricProperties(composition="unknown")

    assert fabric.composition is FabricComposition.UNKNOWN


def test_composition_defaults_to_unknown() -> None:
    fabric = FabricProperties()

    assert fabric.composition is FabricComposition.UNKNOWN


def test_optional_thickness_and_weight() -> None:
    fabric = FabricProperties(
        composition="cotton",
        thickness_mm=0.5,
        weight_gsm=150.0,
    )

    assert fabric.thickness_mm == 0.5
    assert fabric.weight_gsm == 150.0


def test_optional_measurements_can_be_missing() -> None:
    fabric = FabricProperties()

    assert fabric.thickness_mm is None
    assert fabric.weight_gsm is None


def test_knitted_fabric_is_rejected() -> None:
    with pytest.raises(ValueError, match="Only woven"):
        FabricProperties(structure="knitted")


@pytest.mark.parametrize("stretch", ["low", "moderate", "high"])
def test_stretch_fabric_is_rejected(stretch: str) -> None:
    with pytest.raises(ValueError, match="Only non-stretch"):
        FabricProperties(stretch_level=stretch)


def test_invalid_composition_is_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid fabric property"):
        FabricProperties(composition="silk")


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), True])
def test_invalid_thickness_is_rejected(value: float) -> None:
    with pytest.raises(ValueError, match="thickness_mm"):
        FabricProperties(thickness_mm=value)


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), True])
def test_invalid_weight_is_rejected(value: float) -> None:
    with pytest.raises(ValueError, match="weight_gsm"):
        FabricProperties(weight_gsm=value)


def test_fabric_properties_are_immutable() -> None:
    fabric = FabricProperties(composition="cotton")

    with pytest.raises((AttributeError, TypeError)):
        fabric.thickness_mm = 0.5  # type: ignore[misc]
