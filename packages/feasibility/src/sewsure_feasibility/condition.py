"""Garment condition models for SewSure's woven-shirt iteration.

Records physical defects without independently deciding
whether affected fabric is suitable for reuse.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from sewsure_feasibility.components import ComponentKind
from sewsure_feasibility.models import Garment


class DefectKind(StrEnum):
    HOLE = "hole"
    TEAR = "tear"
    STAIN = "stain"
    DISCOLOURATION = "discolouration"
    FABRIC_WEAR = "fabric_wear"
    SEAM_DAMAGE = "seam_damage"
    COMPONENT_DAMAGE = "component_damage"


class DefectSeverity(StrEnum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"


class Repairability(StrEnum):
    REPAIRABLE = "repairable"
    NOT_REPAIRABLE = "not_repairable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class GarmentDefect:
    """A recorded physical defect on an original garment."""

    defect_id: str
    kind: DefectKind
    severity: DefectSeverity
    repairability: Repairability = Repairability.UNKNOWN
    panel_id: str | None = None
    component: ComponentKind | None = None
    location_description: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.defect_id.strip():
            raise ValueError("defect_id must be non-empty")

        if self.panel_id is not None and not self.panel_id.strip():
            raise ValueError("panel_id cannot be empty")

        if self.location_description is not None and not self.location_description.strip():
            raise ValueError("location_description cannot be empty")

        if self.description is not None and not self.description.strip():
            raise ValueError("description cannot be empty")


@dataclass(frozen=True)
class GarmentCondition:
    """Physical condition assessment linked to an existing garment."""

    garment: Garment
    defects: tuple[GarmentDefect, ...] = ()

    def __post_init__(self) -> None:
        defects = tuple(self.defects)
        object.__setattr__(self, "defects", defects)

        known_panel_ids = {panel.panel_id for panel in self.garment.panels}

        seen_ids: set[str] = set()

        for defect in defects:
            if defect.defect_id in seen_ids:
                raise ValueError(f"Duplicate defect ID: {defect.defect_id}")

            seen_ids.add(defect.defect_id)

            if defect.panel_id is not None and defect.panel_id not in known_panel_ids:
                raise ValueError(f"Unknown fabric panel reference: {defect.panel_id}")

    @property
    def is_damaged(self) -> bool:
        """Whether at least one defect has been recorded."""

        return bool(self.defects)

    def get_defects(
        self,
        kind: DefectKind,
    ) -> tuple[GarmentDefect, ...]:
        """Return all defects matching a particular category."""

        return tuple(defect for defect in self.defects if defect.kind is kind)

    def get_defects_for_panel(
        self,
        panel_id: str,
    ) -> tuple[GarmentDefect, ...]:
        """Return defects associated with a particular fabric panel."""

        return tuple(defect for defect in self.defects if defect.panel_id == panel_id)

    def get_severe_defects(self) -> tuple[GarmentDefect, ...]:
        """Return defects classified as severe."""

        return tuple(defect for defect in self.defects if defect.severity is DefectSeverity.SEVERE)
