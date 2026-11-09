"""Construction components for conventional woven office shirts.

Component records identify physical garment parts.
FabricPanel remains the source of measured panel geometry.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from sewsure_feasibility.models import Garment, Side


class ComponentKind(StrEnum):
    FRONT_LEFT = "front_left"
    FRONT_RIGHT = "front_right"
    BACK = "back"
    SLEEVE_LEFT = "sleeve_left"
    SLEEVE_RIGHT = "sleeve_right"
    CUFF_LEFT = "cuff_left"
    CUFF_RIGHT = "cuff_right"
    COLLAR = "collar"
    BUTTON_PLACKET = "button_placket"


class ComponentStatus(StrEnum):
    PRESENT = "present"
    MISSING = "missing"
    UNKNOWN = "unknown"


PANEL_SIDES: dict[ComponentKind, Side] = {
    ComponentKind.FRONT_LEFT: Side.FRONT_LEFT,
    ComponentKind.FRONT_RIGHT: Side.FRONT_RIGHT,
    ComponentKind.BACK: Side.BACK,
    ComponentKind.SLEEVE_LEFT: Side.SLEEVE_LEFT,
    ComponentKind.SLEEVE_RIGHT: Side.SLEEVE_RIGHT,
}


@dataclass(frozen=True)
class GarmentComponent:
    """One construction component and its known availability."""

    kind: ComponentKind
    status: ComponentStatus
    source_panel_id: str | None = None

    def __post_init__(self) -> None:
        if self.source_panel_id is not None and not self.source_panel_id.strip():
            raise ValueError("source_panel_id cannot be empty")

        if self.status is not ComponentStatus.PRESENT and self.source_panel_id is not None:
            raise ValueError("Only present components may reference a fabric panel")


@dataclass(frozen=True)
class GarmentConstruction:
    """Validated component inventory linked to an existing Garment."""

    garment: Garment
    components: tuple[GarmentComponent, ...]

    def __post_init__(self) -> None:
        components = tuple(self.components)
        object.__setattr__(self, "components", components)

        seen: set[ComponentKind] = set()

        panels_by_id = {panel.panel_id: panel for panel in self.garment.panels}

        for component in components:
            if component.kind in seen:
                raise ValueError(f"Duplicate garment component: {component.kind.value}")

            seen.add(component.kind)
            panel_id = component.source_panel_id

            if panel_id is None:
                continue

            if panel_id not in panels_by_id:
                raise ValueError(f"Unknown fabric panel reference: {panel_id}")

            panel = panels_by_id[panel_id]

            if panel.source_garment_id != self.garment.garment_id:
                raise ValueError("Referenced fabric panel belongs to another garment")

            expected_side = PANEL_SIDES.get(component.kind)

            if expected_side is not None and panel.side != expected_side:
                raise ValueError(f"Incorrect fabric panel for {component.kind.value}")

    def get_component(
        self,
        kind: ComponentKind,
    ) -> GarmentComponent | None:
        """Return a component by kind, if recorded."""

        for component in self.components:
            if component.kind is kind:
                return component

        return None

    def missing_or_unknown(
        self,
        required: tuple[ComponentKind, ...],
    ) -> tuple[ComponentKind, ...]:
        """Return required components not confirmed as present."""

        unavailable: list[ComponentKind] = []

        for kind in required:
            component = self.get_component(kind)

            if component is None or component.status is not ComponentStatus.PRESENT:
                unavailable.append(kind)

        return tuple(unavailable)
