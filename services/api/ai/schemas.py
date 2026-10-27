"""Model output schemas and the recipe allow-list.

REPLACE WITH packages/contracts SCHEMA once K1 publishes it. Everything the
model may return is defined here and nowhere else: pipeline code imports these
names, so swapping in the generated contract is a one-module change.

The allow-list is categorical on purpose. Parameters are named levels ordered
from least to most demanding, never millimetre values: the model must not
invent numeric pattern geometry (blueprint section 4.1). The feasibility
engine turns a level into geometry.

Recipe IDs and levels here are PLACEHOLDERS until N5 publishes reviewed recipes
in content/recipes/.
"""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator
from pydantic import BaseModel, ConfigDict

SCHEMA_VERSION = "v0"
MAX_CANDIDATES_FROM_MODEL = 8
MAX_OPERATIONS_PER_CANDIDATE = 3
MAX_DESIGNS_RETURNED = 3

SUPPORTED_GARMENTS = frozenset({"button_shirt"})
SUPPORTED_MATERIALS = frozenset({"woven_cotton", "woven_linen", "woven_blend"})

# recipe_id -> {param_name: levels ordered least -> most demanding}
RECIPE_ALLOW_LIST: dict[str, dict[str, tuple[str, ...]]] = {
    "shirt_crop_hem": {"crop_level": ("slightly_shorter", "cropped", "very_cropped")},
    "shirt_short_sleeve": {"sleeve_length": ("short", "cap")},
    "shirt_waist_darts": {"shaping": ("light", "moderate")},
}

# Stage B attribute vocabulary (blueprint 4.2 stage B).
CROP_LENGTHS = ("none", "slightly_shorter", "cropped", "very_cropped")
WAIST_SHAPINGS = ("none", "light", "moderate")
SLEEVE_STYLES = ("unchanged", "short", "cap")

INSPIRATION_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["crop_length", "waist_shaping", "sleeve_style", "closure_preservation"],
    "properties": {
        "crop_length": {"enum": list(CROP_LENGTHS)},
        "waist_shaping": {"enum": list(WAIST_SHAPINGS)},
        "sleeve_style": {"enum": list(SLEEVE_STYLES)},
        "closure_preservation": {"type": "boolean"},
    },
}


def _operation_schema() -> dict[str, Any]:
    branches = []
    for recipe_id, params in RECIPE_ALLOW_LIST.items():
        branches.append(
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["recipe_id", "params"],
                "properties": {
                    "recipe_id": {"const": recipe_id},
                    "params": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": list(params),
                        "properties": {name: {"enum": list(levels)} for name, levels in params.items()},
                    },
                },
            }
        )
    return {"oneOf": branches}


CANDIDATES_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["candidates"],
    "properties": {
        "candidates": {
            "type": "array",
            "minItems": 0,
            "maxItems": MAX_CANDIDATES_FROM_MODEL,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["operations"],
                "properties": {
                    "operations": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": MAX_OPERATIONS_PER_CANDIDATE,
                        "items": _operation_schema(),
                    }
                },
            },
        }
    },
}
# No free-text field is allowed in candidates: model prose is an injection
# channel. User-facing explanations are written from constraint results.

INSPIRATION_VALIDATOR = Draft202012Validator(INSPIRATION_SCHEMA)
CANDIDATES_VALIDATOR = Draft202012Validator(CANDIDATES_SCHEMA)


class Operation(BaseModel):
    model_config = ConfigDict(frozen=True)

    recipe_id: str
    params: dict[str, str]

    def key(self) -> tuple[str, tuple[tuple[str, str], ...]]:
        return self.recipe_id, tuple(sorted(self.params.items()))


class Candidate(BaseModel):
    model_config = ConfigDict(frozen=True)

    operations: tuple[Operation, ...]

    def key(self) -> tuple:
        return tuple(sorted(op.key() for op in self.operations))


class InspirationAttributes(BaseModel):
    model_config = ConfigDict(frozen=True)

    crop_length: str
    waist_shaping: str
    sleeve_style: str
    closure_preservation: bool

    def requested(self) -> dict[str, str]:
        """Attributes that ask for a change, keyed by the recipe parameter they map to."""
        out: dict[str, str] = {}
        if self.crop_length != "none":
            out["crop_level"] = self.crop_length
        if self.waist_shaping != "none":
            out["shaping"] = self.waist_shaping
        if self.sleeve_style != "unchanged":
            out["sleeve_length"] = self.sleeve_style
        return out
