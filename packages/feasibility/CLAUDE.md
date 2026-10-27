# packages/feasibility

Owner: Narthananilaa. Agents: N1 Geometry Engine, N3 Fit & Ease Modeller, N4 Calibration & Overlay Math, N7 Library Expander.

Standalone Python package with no web or database dependencies. It is the only code allowed to decide a design state.

## Core types (§5.2)

- `FabricPanel`: source garment, side, polygon in mm, bounding dimensions, seam zones, prohibited regions, stretch family, scale provenance.
- `PatternPiece`: recipe ID, polygon or parametric template, grain and rotation limits, seam allowance, cut count.
- `Placement`: source panel, translation, permitted rotation, seam margin, revision reference.
- `ConstraintResult`: `hard_pass`, `failure_codes`, numeric residuals, `missing_dimensions`, uncertainty flags, suggested alternatives.

## Rules

- Units are mm everywhere. Reject implausible inputs (for example a 60 mm chest width) before any geometry runs.
- Hard gates run before any soft ranking. A hard failure can never be outscored.
- Every public function returns status, failure codes, measurements and the recipe/engine version. Never a bare boolean.
- A non-shirt input must never receive shirt-specific pass status or cut points.
- Each new rule ships with at least one passing and one failing fixture in `tests/benchmarks`.
- Recipes are allow-listed by ID and version. Unknown IDs fail closed.
- Calibration that misses the agreed tolerance returns the dimensioned-diagram fallback, not a precise overlay. The tolerance number is set by a human (H-02), not by an agent.
