"""Allow-list, stage B attributes and the check on model proposals.

Stage D output is validated with the contract model
`sewsure_contracts.ai_candidate_proposal_schema.AiCandidateProposal` (packages/contracts,
1.0.0-draft.2). That model checks shape; `validate_proposals` adds what the contract
leaves to the server: the numeric-key rule, then the recipe allow-list and levels.
Everything fails closed.

Parameters are named levels, never numbers. `level_map.py` turns a level into
millimetres for the feasibility engine.
"""

from __future__ import annotations

import re
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import BaseModel, ConfigDict, ValidationError
from sewsure_contracts.ai_candidate_proposal_schema import AiCandidateProposal

MAX_DESIGNS_RETURNED = 3

# Contract vocabulary (draft.2): garment category and fabric family.
SUPPORTED_GARMENTS = frozenset({"woven_shirt"})
SUPPORTED_MATERIALS = frozenset({"woven"})
REQUIRED_DIMENSIONS = frozenset({"shoulder_to_hem", "chest_flat_width"})

# recipe_id -> {param: levels ordered least -> most demanding}. Keep in step with
# sewsure_feasibility.ALLOWED_RECIPE_IDS (checked by a test).
RECIPE_ALLOW_LIST: dict[str, dict[str, tuple[str, ...]]] = {
    "woven_shirt_crop_v1": {"crop_level": ("slightly_shorter", "cropped", "very_cropped")},
}

# Stage B attribute vocabulary. Pipeline-local: only crop_length maps to a reviewed recipe.
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
INSPIRATION_VALIDATOR = Draft202012Validator(INSPIRATION_SCHEMA)

_NUMERIC_KEY = re.compile(r"_(mm|cm|in|count)$")


def validate_proposals(payload: Any) -> bool:
    """Contract shape, no numeric keys, recipe IDs and levels on the allow-list."""
    try:
        parsed = AiCandidateProposal.model_validate(payload)
    except ValidationError:
        return False
    for prop in parsed.proposals:
        if any(_NUMERIC_KEY.search(k) for k in prop.parameters):
            return False
        allowed = RECIPE_ALLOW_LIST.get(prop.recipe_id)
        if allowed is None or set(prop.parameters) != set(allowed):
            return False
        values = {k: getattr(v, "root", v) for k, v in prop.parameters.items()}
        if any(values[name] not in levels for name, levels in allowed.items()):
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
