"""Allow-listed recipe registry. Unknown IDs fail closed (``get_recipe`` returns None)."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from sewsure_feasibility.recipes import woven_shirt_crop_v1
from sewsure_feasibility.recipes.base import GeometryOutcome, Recipe

_REGISTRY: Mapping[str, Recipe] = MappingProxyType(
    {woven_shirt_crop_v1.RECIPE_ID: woven_shirt_crop_v1.RECIPE}
)

ALLOWED_RECIPE_IDS: frozenset[str] = frozenset(_REGISTRY)


def get_recipe(recipe_id: str) -> Recipe | None:
    return _REGISTRY.get(recipe_id)


__all__ = ["ALLOWED_RECIPE_IDS", "GeometryOutcome", "Recipe", "get_recipe"]
