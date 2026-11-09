"""Cut plan for one PASS_SUPPORTED_CHECKS revision (contract CutPlan).

Every number is the engine's cut mark, a requested parameter or a user measurement; the only
constants are the ruler tolerance setting and the zero seam allowance of a straight crop.
Without a calibrated photo the plan is a dimensioned diagram, never an overlay.
"""

from datetime import datetime
from typing import Any

from sewsure_api.models import new_id


def build_cut_plan(
    *,
    revision_id: str,
    recipe_id: str,
    recipe_version: str,
    engine_version: str,
    cut_mark_mm: float,
    params: dict[str, Any],
    panel_widths_mm: dict[str, float],
    prohibited_regions: dict[str, list[str]],
    ruler_tolerance_mm: float,
    now: datetime,
) -> dict[str, Any]:
    finished = float(params["finished_length_mm"])
    hem = float(params["hem_allowance_mm"])
    pieces = []
    for slug, width in panel_widths_mm.items():
        pieces.append(
            {
                "piece_id": slug,
                "source_panel": slug,
                "lines": [
                    {
                        "line_id": "cut_line",
                        "kind": "cut",
                        "points_mm": [[0, cut_mark_mm], [width, cut_mark_mm]],
                        "label": f"Cut {cut_mark_mm:g} mm below shoulder",
                    },
                    {
                        "line_id": "hem_line",
                        "kind": "fold",
                        "points_mm": [[0, finished], [width, finished]],
                        "label": f"Finished hem {finished:g} mm",
                    },
                ],
                "prohibited_regions": prohibited_regions.get(slug, []),
            }
        )
    return {
        "cut_plan_id": new_id("cut"),
        "revision_id": revision_id,
        "recipe_id": recipe_id,
        "recipe_version": recipe_version,
        "units": "mm",
        "mode": "dimensioned_diagram",
        "coordinate_frame": {
            "origin_landmark": "high_shoulder_point",
            "x_axis": "across the body, towards centre front",
            "y_axis": "downwards, towards the hem",
        },
        "pieces": pieces,
        "allowances": {"seam_allowance_mm": 0, "hem_allowance_mm": hem},
        "ruler_checkpoints": [
            {
                "checkpoint_id": "cut_mark_from_shoulder",
                "instruction": (
                    f"Measure straight down from the high shoulder point and mark "
                    f"{cut_mark_mm:g} mm. "
                    "Check it against your shoulder-to-hem measurement before cutting."
                ),
                "from_landmark": "high_shoulder_point",
                "distance_mm": cut_mark_mm,
                "tolerance_mm": ruler_tolerance_mm,
            }
        ],
        "calibration": {"state": "none"},
        "provenance": {
            "source": "live",
            "schema_version": "1.0",
            "engine_version": engine_version,
            "model_id": None,
            "prompt_version": None,
        },
        "created_at": now.isoformat(),
    }
