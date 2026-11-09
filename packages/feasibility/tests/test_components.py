"""Unit tests for office-shirt construction components."""

from dataclasses import FrozenInstanceError

import pytest

from sewsure_feasibility import (
    ComponentKind,
    ComponentStatus,
    FabricPanel,
    Garment,
    GarmentComponent,
    GarmentConstruction,
    Side,
)


def rectangle() -> tuple[tuple[float, float], ...]:
    return (
        (0.0, 0.0),
        (250.0, 0.0),
        (250.0, 700.0),
        (0.0, 700.0),
    )


def make_shirt() -> Garment:
    return Garment(
        garment_id="shirt-001",
        category="woven_shirt",
        material="woven",
        panels=(
            FabricPanel("shirt-001", Side.FRONT_LEFT, rectangle()),
            FabricPanel("shirt-001", Side.BACK, rectangle()),
        ),
    )


def test_create_component() -> None:
    component = GarmentComponent(
        ComponentKind.COLLAR,
        ComponentStatus.PRESENT,
    )

    assert component.kind is ComponentKind.COLLAR
    assert component.status is ComponentStatus.PRESENT


def test_all_component_positions_exist() -> None:
    assert len(ComponentKind) == 9


def test_create_construction() -> None:
    construction = GarmentConstruction(
        make_shirt(),
        (
            GarmentComponent(
                ComponentKind.FRONT_LEFT,
                ComponentStatus.PRESENT,
                "shirt-001:front_left",
            ),
            GarmentComponent(ComponentKind.COLLAR, ComponentStatus.PRESENT),
        ),
    )

    assert len(construction.components) == 2


def test_get_existing_component() -> None:
    construction = GarmentConstruction(
        make_shirt(),
        (GarmentComponent(ComponentKind.COLLAR, ComponentStatus.PRESENT),),
    )

    component = construction.get_component(ComponentKind.COLLAR)
    assert component is not None
    assert component.status is ComponentStatus.PRESENT


def test_get_missing_component() -> None:
    construction = GarmentConstruction(make_shirt(), ())
    assert construction.get_component(ComponentKind.COLLAR) is None


def test_missing_or_unknown() -> None:
    construction = GarmentConstruction(
        make_shirt(),
        (
            GarmentComponent(ComponentKind.COLLAR, ComponentStatus.PRESENT),
            GarmentComponent(ComponentKind.SLEEVE_LEFT, ComponentStatus.UNKNOWN),
            GarmentComponent(ComponentKind.SLEEVE_RIGHT, ComponentStatus.MISSING),
        ),
    )

    assert construction.missing_or_unknown(
        (
            ComponentKind.COLLAR,
            ComponentKind.SLEEVE_LEFT,
            ComponentKind.SLEEVE_RIGHT,
            ComponentKind.CUFF_LEFT,
        )
    ) == (
        ComponentKind.SLEEVE_LEFT,
        ComponentKind.SLEEVE_RIGHT,
        ComponentKind.CUFF_LEFT,
    )


def test_reject_duplicate_components() -> None:
    with pytest.raises(ValueError, match="Duplicate"):
        GarmentConstruction(
            make_shirt(),
            (
                GarmentComponent(ComponentKind.COLLAR, ComponentStatus.PRESENT),
                GarmentComponent(ComponentKind.COLLAR, ComponentStatus.MISSING),
            ),
        )


def test_reject_unknown_panel_reference() -> None:
    with pytest.raises(ValueError, match="Unknown fabric panel"):
        GarmentConstruction(
            make_shirt(),
            (
                GarmentComponent(
                    ComponentKind.FRONT_LEFT,
                    ComponentStatus.PRESENT,
                    "shirt-001:nonexistent",
                ),
            ),
        )


def test_reject_wrong_panel_side() -> None:
    with pytest.raises(ValueError, match="Incorrect fabric panel"):
        GarmentConstruction(
            make_shirt(),
            (
                GarmentComponent(
                    ComponentKind.FRONT_LEFT,
                    ComponentStatus.PRESENT,
                    "shirt-001:back",
                ),
            ),
        )


def test_reject_panel_from_another_garment() -> None:
    garment = Garment(
        "shirt-001",
        "woven_shirt",
        "woven",
        (FabricPanel("other-shirt", Side.FRONT_LEFT, rectangle()),),
    )

    with pytest.raises(ValueError, match="another garment"):
        GarmentConstruction(
            garment,
            (
                GarmentComponent(
                    ComponentKind.FRONT_LEFT,
                    ComponentStatus.PRESENT,
                    "other-shirt:front_left",
                ),
            ),
        )


@pytest.mark.parametrize(
    "status",
    [ComponentStatus.MISSING, ComponentStatus.UNKNOWN],
)
def test_unavailable_component_cannot_reference_panel(
    status: ComponentStatus,
) -> None:
    with pytest.raises(ValueError, match="Only present"):
        GarmentComponent(
            ComponentKind.FRONT_LEFT,
            status,
            "shirt-001:front_left",
        )


def test_reject_empty_panel_reference() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        GarmentComponent(
            ComponentKind.COLLAR,
            ComponentStatus.PRESENT,
            " ",
        )


def test_component_is_immutable() -> None:
    component = GarmentComponent(
        ComponentKind.COLLAR,
        ComponentStatus.PRESENT,
    )

    attribute_name = "status"

    with pytest.raises(FrozenInstanceError):
        setattr(component, attribute_name, ComponentStatus.MISSING)