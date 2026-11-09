"""Model output schemas and the recipe allow-list.

Aligned to contract 1.0.0-draft.2 (PR #15, commit 2cfd24e): `AI_CANDIDATES_SCHEMA`
is a copy of `packages/contracts/schemas/ai-candidate-proposal.schema.json` with
`common#/$defs/RecipeId` and `AiParameters` inlined. REPLACE WITH THE GENERATED
packages/contracts MODEL once it is merged; nothing else in this package defines
what the model may return.

The contract schema checks shape only ("the server checks recipe_id against the
allow-list and each level against the recipe"). `validate_candidates` does that
second step and fails closed.

Parameters are named levels, never numbers: the model must not invent numeric
pattern geometry. The recipe (N5/N1) maps a level to millimetres before the
feasibility engine runs; that mapping is not implemented here.
"""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator
from pydantic import BaseModel, ConfigDict

CONTRACT_VERSION = "1.0.0-draft.2"
MAX_PROPOSALS_FROM_MODEL = 6  # contract maxItems
MAX_DESIGNS_RETURNED = 3

# Contract vocabulary: garment category and fabric family (draft.2 "kept stable").
SUPPORTED_GARMENTS = frozenset({"woven_shirt"})
SUPPORTED_MATERIALS = frozenset({"woven"})  # fabric_family

# Contract GarmentDimension names, used to say what is still needed.
REQUIRED_DIMENSIONS = frozenset({"shoulder_to_hem", "chest_flat_width"})

# recipe_id -> {param: levels ordered least -> most demanding}. Only recipes in
# packages/feasibility ALLOWED_RECIPE_IDS belong here.
RECIPE_ALLOW_LIST: dict[str, dict[str, tuple[str, ...]]] = {
    "woven_shirt_crop_v1": {"crop_level": ("slightly_shorter", "cropped", "very_cropped")},
}

# Stage B attribute vocabulary (blueprint 4.2 stage B). Only crop_length maps to a
# reviewed recipe today; the others are parsed so the app can say they are unsupported.
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

_LEVEL = {"type": "string", "pattern": "^[a-z][a-z0-9_]*$", "maxLength": 64}

AI_CANDIDATES_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "AiCandidateProposal",
    "type": "object",
    "required": ["proposals"],
    "additionalProperties": False,
    "properties": {
        "proposals": {
            "type": "array",
            "minItems": 0,
            "maxItems": MAX_PROPOSALS_FROM_MODEL,
            "items": {
                "type": "object",
                "required": ["recipe_id", "parameters"],
                "additionalProperties": False,
                "properties": {
                    "recipe_id": {"type": "string", "pattern": "^[a-z][a-z0-9_]*_v[0-9]+$"},
                    "parameters": {  # AiParameters
                        "type": "object",
                        "propertyNames": {
                            "pattern": "^[a-z][a-z0-9_]*$",
                            "maxLength": 64,
                            "not": {"pattern": "_(mm|cm|in|count)$"},
                        },
                        "additionalProperties": {"anyOf": [_LEVEL, {"type": "boolean"}]},
                    },
                },
            },
        }
    },
}

INSPIRATION_VALIDATOR = Draft202012Validator(INSPIRATION_SCHEMA)
CANDIDATES_VALIDATOR = Draft202012Validator(AI_CANDIDATES_SCHEMA)


def validate_candidates(payload: Any) -> bool:
    """Contract shape plus allow-list: unknown recipe IDs, parameter names or
    levels fail closed."""
    if not CANDIDATES_VALIDATOR.is_valid(payload):
        return False
    for prop in payload["proposals"]:
        allowed = RECIPE_ALLOW_LIST.get(prop["recipe_id"])
        if allowed is None or set(prop["parameters"]) != set(allowed):
            return False
        if any(prop["parameters"][name] not in levels for name, levels in allowed.items()):
            return False
    return True


class Candidate(BaseModel):
    """One contract proposal: a reviewed recipe plus named levels."""

    model_config = ConfigDict(frozen=True)

    recipe_id: str
    parameters: dict[str, str | bool]

    def key(self) -> tuple[str, tuple[tuple[str, str | bool], ...]]:
        return self.recipe_id, tuple(sorted(self.parameters.items()))


class InspirationAttributes(BaseModel):
    model_config = ConfigDict(frozen=True)

    crop_length: str
    waist_shaping: str
    sleeve_style: str
    closure_preservation: bool

    def requested_crop(self) -> str | None:
        return None if self.crop_length == "none" else self.crop_length
