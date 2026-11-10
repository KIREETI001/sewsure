"""Named crop levels to engine parameters (mm).

PROVISIONAL: these fractions are engineering placeholders so the pipeline can be
wired to `evaluate`. They belong in the reviewed recipe (N5) or the engine (N1),
who should own and replace them. The AI model never sees or emits these numbers.
"""

from __future__ import annotations

from collections.abc import Mapping

DEFAULT_HEM_ALLOWANCE_MM = 30.0  # recipe default in content/recipes/woven_shirt_crop_v1

# Share of the original shoulder-to-hem length kept as the finished length.
CROP_LEVEL_KEEP_FRACTION: dict[str, float] = {
    "slightly_shorter": 0.88,
    "cropped": 0.70,
    "very_cropped": 0.55,
}


def engine_params(
    recipe_id: str, parameters: Mapping[str, str | bool], shoulder_to_hem_mm: float | None
) -> dict[str, float | str | bool]:
    """Engine parameters for a level. Missing inputs are left out so the engine reports them."""
    if recipe_id != "woven_shirt_crop_v1":
        return {}
    out: dict[str, float | str | bool] = {"hem_allowance_mm": DEFAULT_HEM_ALLOWANCE_MM}
    level = parameters.get("crop_level")
    if (
        shoulder_to_hem_mm is not None
        and isinstance(level, str)
        and level in CROP_LEVEL_KEEP_FRACTION
    ):
        out["finished_length_mm"] = round(shoulder_to_hem_mm * CROP_LEVEL_KEEP_FRACTION[level], 1)
    return out
