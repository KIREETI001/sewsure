"""Project validated cut/fold/stitch coordinates into the photo, or return the fallback (§6.2).

The only inputs are mm coordinates that already belong to a cut plan for a
``PASS_SUPPORTED_CHECKS`` revision. This module never creates geometry (non-negotiable 4) and
never sets a design state (non-negotiable 2).

A precise overlay is returned only when ``calibration.state == "calibrated"``, which in turn needs
a human-set tolerance. Anything else yields ``dimensioned_diagram``. Even a calibrated overlay is
labelled approximate and carries the ruler-verification notice (non-negotiable 5).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal

from sewsure_feasibility.calibration.fit import CalibrationResult, project_points_mm_to_px

OverlayMode = Literal["calibrated_overlay", "dimensioned_diagram"]
LineKind = Literal["cut", "stitch", "fold", "reference"]
LINE_KINDS: tuple[LineKind, ...] = ("cut", "stitch", "fold", "reference")

APPROXIMATE_NOTICE = (
    "Approximate overlay. Check every dimension on the fabric with a ruler before cutting."
)
FALLBACK_NOTICE = (
    "Photo overlay is not available for this photo. Use the dimensioned diagram and measure "
    "each distance on the fabric with a ruler."
)


class OverlayIssue(StrEnum):
    CALIBRATION_NOT_ACCEPTED = "CALIBRATION_NOT_ACCEPTED"
    PROJECTION_FAILED = "PROJECTION_FAILED"
    NO_LINES = "NO_LINES"
    INVALID_LINE = "INVALID_LINE"


@dataclass(frozen=True)
class PlanLine:
    """A cut-plan line in mm (mirrors ``cut-plan.schema.json`` ``Line`` plus its piece ID)."""

    piece_id: str
    line_id: str
    kind: LineKind
    points_mm: tuple[tuple[float, float], ...]
    label: str


@dataclass(frozen=True)
class OverlayLine:
    piece_id: str
    line_id: str
    kind: LineKind
    label: str
    points_mm: tuple[tuple[float, float], ...]
    points_px: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class OverlayLayers:
    """Separate layers so the app can toggle each independently (§6.1 step 6)."""

    cut: tuple[OverlayLine, ...]
    stitch: tuple[OverlayLine, ...]
    fold: tuple[OverlayLine, ...]
    reference: tuple[OverlayLine, ...]


@dataclass(frozen=True)
class OverlayResult:
    mode: OverlayMode
    notice: str
    calibration: CalibrationResult
    fallback_issues: tuple[OverlayIssue, ...]
    layers: OverlayLayers | None
    diagram_lines: tuple[PlanLine, ...]
    """The same lines in mm, unprojected: the dimensioned diagram is drawn from these."""
    approximate: bool = True

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "mode": self.mode,
            "notice": self.notice,
            "approximate": self.approximate,
            "fallback_issues": [i.value for i in self.fallback_issues],
            "calibration": self.calibration.to_contract_dict(),
            "layers": None,
        }
        if self.layers is not None:
            d["layers"] = {
                kind: [
                    {
                        "piece_id": ln.piece_id,
                        "line_id": ln.line_id,
                        "label": ln.label,
                        "points_px": [list(p) for p in ln.points_px],
                    }
                    for ln in getattr(self.layers, kind)
                ]
                for kind in LINE_KINDS
            }
        return d


def lines_from_cut_plan(cut_plan: Mapping[str, Any]) -> list[PlanLine]:
    """Read lines from a contract ``CutPlan`` dict. Raises ``ValueError`` on a malformed plan."""
    if cut_plan.get("units") != "mm":
        raise ValueError("cut plan units must be mm")
    out: list[PlanLine] = []
    for piece in cut_plan.get("pieces", []):
        for line in piece["lines"]:
            kind = line["kind"]
            if kind not in LINE_KINDS:
                raise ValueError(f"unknown line kind {kind!r}")
            pts = tuple((float(x), float(y)) for x, y in line["points_mm"])
            out.append(PlanLine(piece["piece_id"], line["line_id"], kind, pts, line["label"]))
    return out


def build_overlay(lines: Sequence[PlanLine], calibration: CalibrationResult) -> OverlayResult:
    """Return the calibrated overlay, or the dimensioned-diagram fallback."""
    diagram = tuple(lines)

    def fallback(*issues: OverlayIssue) -> OverlayResult:
        return OverlayResult(
            mode="dimensioned_diagram",
            notice=FALLBACK_NOTICE,
            calibration=calibration,
            fallback_issues=tuple(issues),
            layers=None,
            diagram_lines=diagram,
        )

    if calibration.state != "calibrated":
        return fallback(OverlayIssue.CALIBRATION_NOT_ACCEPTED)
    if not diagram:
        return fallback(OverlayIssue.NO_LINES)
    if any(len(ln.points_mm) < 2 or ln.kind not in LINE_KINDS for ln in diagram):
        return fallback(OverlayIssue.INVALID_LINE)

    projected: list[OverlayLine] = []
    try:
        for ln in diagram:
            px = project_points_mm_to_px(calibration, ln.points_mm)
            projected.append(
                OverlayLine(ln.piece_id, ln.line_id, ln.kind, ln.label, ln.points_mm, tuple(px))
            )
    except ValueError:
        return fallback(OverlayIssue.PROJECTION_FAILED)

    def layer(kind: LineKind) -> tuple[OverlayLine, ...]:
        return tuple(ln for ln in projected if ln.kind == kind)

    return OverlayResult(
        mode="calibrated_overlay",
        notice=APPROXIMATE_NOTICE,
        calibration=calibration,
        fallback_issues=(),
        layers=OverlayLayers(layer("cut"), layer("stitch"), layer("fold"), layer("reference")),
        diagram_lines=diagram,
    )
