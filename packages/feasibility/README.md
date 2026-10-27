# sewsure-feasibility

Standalone feasibility engine (blueprint §5). Python 3.12, NumPy, Shapely. No web, database or AI
dependencies. This package is the only code allowed to decide a design state.

## Setup and checks

```bash
cd packages/feasibility
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run pyright
```

## Public entry point

```python
from sewsure_feasibility import evaluate, Garment, Measurement

result = evaluate(garment, measurements, "woven_shirt_crop_v1", params, revision_ref="rev-1")
```

| Argument | Type | Notes |
|---|---|---|
| `garment` | `Garment` | `category` (`"button_up_shirt"`), `material` (`"woven"`); `None` = unknown. `panels` optional; their `prohibited_regions` are checked against the cut line. |
| `measurements` | `Mapping[str, Measurement]` | mm, each with `origin` and optional `confirmed_at`. Required: `shoulder_to_hem_length`, `chest_width`. Use `Measurement.from_cm` at the UI boundary. |
| `recipe_id` | `str` | Must be on the allow-list (`ALLOWED_RECIPE_IDS`); anything else returns `IDEA_ONLY` + `RECIPE_NOT_ALLOWED`. |
| `params` | `Mapping[str, float]` | mm. `finished_length_mm`, `hem_allowance_mm`. |
| `revision_ref` | `str \| None` | Echoed into the result. |

Returns a frozen `ConstraintResult`: `status` (`DesignState`), `hard_pass` (derived), `failure_codes`,
`residuals_mm` (original/finished/hem/cut mark/remainder and per-zone `clearance_mm:<panel>:<zone>`),
`missing_dimensions`, `uncertainty_flags`, `suggested_alternatives`, `details`, `cut_mark_mm`,
`recipe_id`, `recipe_version`, `engine_version`, `input_fingerprint`, `revision_ref`. `to_dict()` gives
a JSON-safe payload. `supersede(result)` returns a copy marked `SUPERSEDED` (the original is untouched).

Gate order: applicability (`IDEA_ONLY`; never returns cut points) -> required inputs and plausibility
(`NEEDS_INPUT`; no geometry runs) -> recipe geometry (`FAILED_CHECKS` / `PASS_SUPPORTED_CHECKS`).

## `woven_shirt_crop_v1` (v1.0.0)

Cut mark from shoulder = `finished_length_mm + hem_allowance_mm`. Remainder = original length - cut mark
and must be strictly positive. The horizontal cut line must not touch any prohibited region on the back
or front panels (sleeves ignored). A pass is `PASS_SUPPORTED_CHECKS` only: it is always flagged
`SIDE_SEAMS_NOT_VERIFIED`, and `PROHIBITED_ZONES_NOT_PROVIDED` / `MEASUREMENT_UNCONFIRMED` when applicable.
Panel coordinates: origin at the shoulder seam, y down, mm.

Failure codes: see `FailureCode` in `models.py`; every code has a test in `tests/test_failure_codes.py`.

## Provisional values needing Narthananilaa's review

Plausible ranges (mm): shoulder-to-hem 250-1100, flat chest width 300-800, finished length 150-1100,
hem allowance 5-80. A value outside its range but inside it when multiplied or divided by 10 is reported as
`UNIT_MIX_UP_SUSPECTED`; otherwise `DIMENSION_IMPLAUSIBLE`.

## Mapping to `packages/contracts` (pending K1)

Models are internal. Intended mapping once the contract lands: `ConstraintResult.to_dict()` -> feasibility
response; `Measurement` -> measurement record (`value_mm`, `origin`, `confirmed_at`); `DesignState` and
`FailureCode` -> shared enums. Any change to these shapes goes through `packages/contracts` first.
