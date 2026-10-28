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

result = evaluate(garment, measurements, "woven_shirt_crop_v1", params,
                  revision_ref="rev-1")          # optional: checked_at=<datetime>
```

| Argument | Type | Notes |
|---|---|---|
| `garment` | `Garment` | `category` (`"woven_shirt"`), `material` (`"woven"`, = contract `fabric_family`); `None` or `"unknown"` = unknown. `panels` carry `prohibited_regions` (placket end, side-seam features); at least one back/front panel must have one, otherwise the cut cannot be checked and the result is `NEEDS_INPUT`. |
| `measurements` | `Mapping[str, Measurement]` | Contract keys, mm, each with `origin` and `confirmed_at`. Required: `shoulder_to_hem`, `chest_flat_width`. Optional `chest_circumference` is cross-checked (flat x 2, +-10 %). **`confirmed_at=None` counts as missing.** Use `Measurement.from_cm` at the UI boundary. |
| `recipe_id` | `str` | Must be on the allow-list (`ALLOWED_RECIPE_IDS`); anything else returns `IDEA_ONLY` + `UNSUPPORTED_RECIPE`. |
| `params` | `Mapping[str, float \| str \| bool]` | `finished_length_mm`, `hem_allowance_mm` (numbers, mm). `hem_finish` allowed. Other names are ignored and flagged `ignored_parameters`. |
| `revision_ref` | `str \| None` | Echoed into the result. |
| `checked_at` | `datetime \| None` | Defaults to now (UTC); pass a fixed value for reproducible results. |

Inputs are typed objects, not dicts: callers (N2's suite, K2's API) map their records to `Garment`,
`Measurement` and `FabricPanel`.

Returns a frozen `ConstraintResult`. Field names follow K1's contract `ConstraintResult` (PR #15):
`failure_codes`, `residuals` (`Residual`: `check_id`, `quantity`, `required_mm`, `available_mm`,
`residual_mm`), `missing_dimensions`, `uncertainty_flags` (lowercase slugs), `checks`
(`CheckOutcome`), `alternatives`, `engine_version`, `checked_at`; `hard_pass` is derived. The engine adds
`status` (`DesignState`, values = contract enum), `details`, `cut_mark_mm`, `recipe_id`,
`recipe_version`, `input_fingerprint`, `revision_ref`. `to_contract_dict()` is exactly the contract
shape (validated against `constraint-result.schema.json`); `to_dict()` wraps it with the engine fields.
`supersede(result)` returns a copy marked `SUPERSEDED`; it raises `ValueError` unless the result passed.
`alternatives` is always empty for now: the contract wants verified alternatives and none are computed yet.

Gate order: applicability (`IDEA_ONLY`; never returns cut points) -> required inputs, confirmation,
plausibility, consistency (`NEEDS_INPUT`, always names at least one missing dimension; no geometry runs)
-> recipe geometry (`FAILED_CHECKS` / `PASS_SUPPORTED_CHECKS`).

## `woven_shirt_crop_v1` (v1.0.0)

Cut mark from shoulder = `finished_length_mm + hem_allowance_mm`. Remainder = original length - cut mark
and must be strictly positive (`INSUFFICIENT_LENGTH` otherwise, including an exact fit). The horizontal
cut line must not touch any prohibited region on the back or front panels (sleeves ignored). A pass is
`PASS_SUPPORTED_CHECKS` only and is always flagged `side_seams_not_verified`.
Panel coordinates: origin at the shoulder seam, y down, mm.

Failure codes are the contract enum values the engine can emit (see `FailureCode`); every code has a test
in `tests/test_failure_codes.py`.

## Provisional values needing Narthananilaa's review

Plausible ranges (mm): shoulder-to-hem 250-1100, flat chest width 300-800, finished length 150-1100,
hem allowance 5-80. A value outside its range but inside it when multiplied or divided by 10 also sets
`possible_unit_error`. Flat/circumference tolerance 10 %. Exact fit (remainder 0) fails.
