"""SewSure feasibility engine (standalone: no web, database or AI dependencies)."""

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
    "ENGINE_VERSION",
    "Alternative",
    "CheckOutcome",
    "ConstraintResult",
    "DesignState",
    "FabricPanel",
    "FailureCode",
    "Garment",
    "Measurement",
    "PatternPiece",
    "Placement",
    "Residual",
    "Side",
    "Zone",
    "cm_to_mm",
    "evaluate",
    "supersede",
]
