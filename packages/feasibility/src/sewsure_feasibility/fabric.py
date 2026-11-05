"""Fabric properties for SewSure's initial woven-shirt iteration."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum


class FabricComposition(StrEnum):
    COTTON = "cotton"
    POLYESTER = "polyester"
    COTTON_POLYESTER_BLEND = "cotton_polyester_blend"
    UNKNOWN = "unknown"


class FabricStructure(StrEnum):
    WOVEN = "woven"
    KNITTED = "knitted"


class StretchLevel(StrEnum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


@dataclass(frozen=True)
class FabricProperties:
    """Describes the material of an original garment.

    Initial supported scope:
    - Woven fabric only.
    - No meaningful stretch.
    - Composition may be unknown.
    - Thickness and GSM are optional.
    """

    composition: FabricComposition | str = FabricComposition.UNKNOWN
    structure: FabricStructure | str = FabricStructure.WOVEN
    stretch_level: StretchLevel | str = StretchLevel.NONE
    thickness_mm: float | None = None
    weight_gsm: float | None = None

    def __post_init__(self) -> None:
        # Validate and normalise categorical values.
        try:
            composition = FabricComposition(self.composition)
            structure = FabricStructure(self.structure)
            stretch = StretchLevel(self.stretch_level)
        except ValueError as exc:
            raise ValueError(f"Invalid fabric property: {exc}") from exc

        object.__setattr__(self, "composition", composition)
        object.__setattr__(self, "structure", structure)
        object.__setattr__(self, "stretch_level", stretch)

        # First iteration supports woven fabrics only.
        if structure is not FabricStructure.WOVEN:
            raise ValueError("Only woven fabrics are supported.")

        # First iteration supports non-stretch fabrics only.
        if stretch is not StretchLevel.NONE:
            raise ValueError("Only non-stretch fabrics are supported.")

        # Validate optional thickness.
        if self.thickness_mm is not None and (
            isinstance(self.thickness_mm, bool)
            or not isinstance(self.thickness_mm, (int, float))
            or not math.isfinite(self.thickness_mm)
            or self.thickness_mm <= 0
        ):
            raise ValueError("thickness_mm must be finite and greater than zero.")

        # Validate optional fabric weight.
        if self.weight_gsm is not None and (
            isinstance(self.weight_gsm, bool)
            or not isinstance(self.weight_gsm, (int, float))
            or not math.isfinite(self.weight_gsm)
            or self.weight_gsm <= 0
        ):
            raise ValueError("weight_gsm must be finite and greater than zero.")
