"""Unified original garment record for SewSure's first iteration.

Combines garment measurements, fabric properties,
construction components and physical condition.
"""

from __future__ import annotations

from dataclasses import dataclass

from sewsure_feasibility.components import GarmentConstruction
from sewsure_feasibility.condition import GarmentCondition
from sewsure_feasibility.fabric import FabricProperties
from sewsure_feasibility.garment_profile import GarmentProfile
from sewsure_feasibility.models import Garment


@dataclass(frozen=True)
class OriginalGarmentRecord:
    """Validated collection of information about one original garment."""

    profile: GarmentProfile
    fabric: FabricProperties
    construction: GarmentConstruction
    condition: GarmentCondition

    def __post_init__(self) -> None:
        expected_garment = self.profile.garment

        related_garments: tuple[Garment, ...] = (
            self.construction.garment,
            self.condition.garment,
        )

        for garment in related_garments:
            if garment != expected_garment:
                raise ValueError("All garment records must reference the same original garment.")

    @property
    def garment(self) -> Garment:
        """Return the original garment."""

        return self.profile.garment

    @property
    def garment_id(self) -> str:
        """Return the unique original garment identifier."""

        return self.garment.garment_id

    @property
    def is_damaged(self) -> bool:
        """Whether any physical defects have been recorded."""

        return self.condition.is_damaged
