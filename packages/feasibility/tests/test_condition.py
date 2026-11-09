"""Tests for garment condition and defect records."""

from dataclasses import FrozenInstanceError

import pytest

from sewsure_feasibility import (
    DefectKind,
    DefectSeverity,
    FabricPanel,
    Garment,
    GarmentCondition,
    GarmentDefect,
    Repairability,
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
        "shirt-001",
        "woven_shirt",
        "woven",
        (
            FabricPanel(
                "shirt-001",
                Side.FRONT_LEFT,
                rectangle(),
            ),
            FabricPanel(
                "shirt-001",
                Side.BACK,
                rectangle(),
            ),
        ),
    )


def make_defect(
    defect_id: str = "D001",
    kind: DefectKind = DefectKind.HOLE,
    severity: DefectSeverity = DefectSeverity.MINOR,
    panel_id: str | None = "shirt-001:front_left",
) -> GarmentDefect:
    return GarmentDefect(
        defect_id=defect_id,
        kind=kind,
        severity=severity,
        panel_id=panel_id,
    )


def test_create_garment_defect() -> None:
    defect = make_defect()

    assert defect.kind is DefectKind.HOLE
    assert defect.severity is DefectSeverity.MINOR
    assert defect.repairability is Repairability.UNKNOWN


def test_create_garment_condition() -> None:
    condition = GarmentCondition(
        make_shirt(),
        (make_defect(),),
    )

    assert condition.is_damaged
    assert len(condition.defects) == 1


def test_undamaged_garment() -> None:
    condition = GarmentCondition(make_shirt())

    assert not condition.is_damaged
    assert condition.defects == ()


def test_get_defects_by_kind() -> None:
    condition = GarmentCondition(
        make_shirt(),
        (
            make_defect("D001", DefectKind.HOLE),
            make_defect("D002", DefectKind.STAIN),
            make_defect("D003", DefectKind.HOLE),
        ),
    )

    holes = condition.get_defects(DefectKind.HOLE)

    assert len(holes) == 2
    assert all(d.kind is DefectKind.HOLE for d in holes)


def test_get_defects_for_panel() -> None:
    condition = GarmentCondition(
        make_shirt(),
        (
            make_defect("D001"),
            make_defect(
                "D002",
                DefectKind.STAIN,
                panel_id="shirt-001:back",
            ),
        ),
    )

    result = condition.get_defects_for_panel("shirt-001:front_left")

    assert len(result) == 1
    assert result[0].defect_id == "D001"


def test_get_severe_defects() -> None:
    condition = GarmentCondition(
        make_shirt(),
        (
            make_defect("D001"),
            make_defect(
                "D002",
                DefectKind.TEAR,
                DefectSeverity.SEVERE,
            ),
            make_defect(
                "D003",
                DefectKind.STAIN,
                DefectSeverity.MODERATE,
            ),
        ),
    )

    severe = condition.get_severe_defects()

    assert len(severe) == 1
    assert severe[0].defect_id == "D002"


def test_reject_empty_defect_id() -> None:
    with pytest.raises(ValueError, match="defect_id"):
        make_defect(" ")


def test_reject_duplicate_defect_ids() -> None:
    with pytest.raises(ValueError, match="Duplicate"):
        GarmentCondition(
            make_shirt(),
            (
                make_defect("D001"),
                make_defect("D001", DefectKind.STAIN),
            ),
        )


def test_reject_unknown_panel_reference() -> None:
    defect = GarmentDefect(
        "D001",
        DefectKind.HOLE,
        DefectSeverity.MINOR,
        panel_id="shirt-001:unknown",
    )

    with pytest.raises(ValueError, match="Unknown fabric panel"):
        GarmentCondition(make_shirt(), (defect,))


def test_reject_empty_panel_reference() -> None:
    with pytest.raises(ValueError, match="panel_id"):
        GarmentDefect(
            "D001",
            DefectKind.HOLE,
            DefectSeverity.MINOR,
            panel_id=" ",
        )


def test_reject_empty_location_description() -> None:
    with pytest.raises(ValueError, match="location_description"):
        GarmentDefect(
            "D001",
            DefectKind.HOLE,
            DefectSeverity.MINOR,
            location_description=" ",
        )


def test_reject_empty_description() -> None:
    with pytest.raises(ValueError, match="description"):
        GarmentDefect(
            "D001",
            DefectKind.HOLE,
            DefectSeverity.MINOR,
            description=" ",
        )

def test_defect_is_immutable() -> None:
    defect = make_defect()

    attribute_name = "severity"

    with pytest.raises(FrozenInstanceError):
        setattr(defect, attribute_name, DefectSeverity.SEVERE)


def test_condition_is_immutable() -> None:
    condition = GarmentCondition(make_shirt())

    attribute_name = "defects"

    with pytest.raises(FrozenInstanceError):
        setattr(condition, attribute_name, (make_defect(),))

def test_defect_without_panel_is_allowed() -> None:
    defect = GarmentDefect(
        "D001",
        DefectKind.COMPONENT_DAMAGE,
        DefectSeverity.MODERATE,
        component=None,
        location_description="Missing button near upper placket",
    )

    condition = GarmentCondition(make_shirt(), (defect,))

    assert condition.is_damaged
    assert condition.defects[0].panel_id is None
