"""SewSure feasibility engine (standalone: no web, database or AI dependencies)."""

from sewsure_feasibility.body import (
    BODY_MEASUREMENT_KEYS,
    BodyProfile,
)
from sewsure_feasibility.engine import ENGINE_VERSION, evaluate, supersede
from sewsure_feasibility.models import (
    Alternative,
    CheckOutcome,
    ConstraintResult,
    DesignState,
    FabricPanel,
    FailureCode,
    Garment,
    Measurement,
    PatternPiece,
    Placement,
    Residual,
    Side,
    Zone,
    cm_to_mm,
)
from sewsure_feasibility.recipes import ALLOWED_RECIPE_IDS

__all__ = [
    "ALLOWED_RECIPE_IDS",
    "BODY_MEASUREMENT_KEYS",
    "ENGINE_VERSION",
    "GARMENT_MEASUREMENT_KEYS",
    "Alternative",
    "BodyProfile",
    "CheckOutcome",
    "ConstraintResult",
    "DesignState",
    "FabricComposition",
    "FabricPanel",
    "FabricProperties",
    "FabricStructure",
    "FailureCode",
    "Garment",
    "GarmentProfile",
    "Measurement",
    "PatternPiece",
    "Placement",
    "Residual",
    "Side",
    "StretchLevel",
    "Zone",
    "cm_to_mm",
    "evaluate",
    "supersede",
]

from sewsure_feasibility.fabric import (
    FabricComposition,
    FabricProperties,
    FabricStructure,
    StretchLevel,
)
from sewsure_feasibility.garment_profile import (
    GARMENT_MEASUREMENT_KEYS,
    GarmentProfile,
)
