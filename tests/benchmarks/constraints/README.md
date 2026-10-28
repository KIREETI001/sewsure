# Constraint suite (blueprint §17.2, §5.5)

26 synthetic cases (the 24 proposed in §17.2, plus `MU-05` and `MU-06` added after review, see below) that check the feasibility engine blocks what it must block and passes what it can support. All inputs are invented. None comes from a real person or a real garment, and none is measured evidence.

| Class | Cases | Files |
|---|---|---|
| Supported successful transformations | 6 | `ss-*.json` |
| Insufficient fabric / invalid placement | 6 | `if-*.json` |
| Measurement missing / unit / implausible | 6 | `mu-*.json` |
| Unsupported garment or material (expect `IDEA_ONLY`) | 4 | `ug-*.json` |
| Revision / seam / edge-boundary | 4 | `rb-*.json` |

`SS-01` is the blueprint §5.3 example (780 mm shirt, 500 mm finished, 30 mm hem). `RB-04` is a three-step revision sequence, so the suite is 26 cases and 28 checks. Counts below use checks as the denominator.

## Run it

```bash
pip install -r requirements.txt
cd tests/benchmarks/constraints
python -m pytest            # data checks always run; engine tests skip if the engine is not importable
python report.py            # counts as numerator/denominator
python report.py --strict   # also fail on any status/code mismatch or indeterminate result
```

`report.py` exit codes: `0` ok, `1` a false acceptance on a destructive cut (the CI gate), `2` engine not importable (`--allow-skip` makes that `0`, for local use only), `3` any indeterminate result (`--allow-indeterminate` to ignore) or, with `--strict`, any status/code mismatch. Mismatch lines show expected versus actual status and codes, and the engine error if it raised.

Case files use the contract v1 vocabulary (K1): dimension names without unit suffix (`shoulder_to_hem`), `woven_shirt` / `fabric_family`, origin `user_tape_measured`, contract failure codes. The engine is reached through one function, `adapter.evaluate_inputs`, which builds N1's `Garment`, `Measurement` and `FabricPanel`/`Zone` types, calls `sewsure_feasibility.evaluate(garment, measurements, recipe_id, params)` and maps N1's failure codes back to contract codes (tables in `adapter.py`). A seam margin widens each exclusion zone in the adapter. If either vocabulary changes, edit those tables only. Override the module with `SEWSURE_FEASIBILITY_MODULE`.

## What the counts mean

Per check, with "reject" meaning any status other than `PASS_SUPPORTED_CHECKS`:

- **correct rejection**: expected reject, engine rejected (n / expected rejects)
- **false acceptance**: expected reject, engine returned `PASS_SUPPORTED_CHECKS` (n / expected rejects)
- **correct acceptance** and **false rejection**: the same for expected passes (n / expected passes)
- **indeterminate**: the engine raised, returned nothing, or returned a status outside the five defined states (n / all checks). It is never counted as a pass.

Every case is marked `destructive_cut: true`, because a pass leads to a cut guide. One false acceptance fails CI. Per §17.2 a single confident false approval warrants investigation, whatever the denominator. 24 synthetic cases do not support a general accuracy claim.

## Add a case

1. Add `cases/<id>.json` copying an existing file. Required: `id`, `class` (one of the five above), `synthetic: true`, `description`, `reason` (one line), `destructive_cut`, `inputs` (or `steps` for a sequence) and `expected` with `status` and `failure_codes`.
2. All lengths in mm, as `<name>_mm` with `origin` and `confirmed_at`. The only exception is a measurement given as `{"value", "unit"}` to test unit handling; the adapter converts it to mm before the engine sees it.
3. `PASS_SUPPORTED_CHECKS` carries no failure codes. Every other status carries at least one.
4. Work out the expected result from the stated numbers, not by running the engine. `test_case_files.py` re-checks the length arithmetic.
5. If you add or remove a case, update `CLASS_COUNTS` and the count assertion in `test_case_files.py` in `cases.py` and say why in the PR. Each new rule needs a passing and a failing case.

## Why expected results change only with a written reason

The expected values are the specification the engine is held to. If a failing case is "fixed" by editing its expectation, the suite stops catching the thing it exists to catch, and a false acceptance can be hidden as a change of mind. So a PR that changes any `expected`, `reason` or `destructive_cut` value must explain in its description which rule changed, who decided (Narthananilaa approves), and the blueprint or recipe reference. Never change an expectation to make a run green.

## Expected results changed after X1 review (written reasons)

| Case | Was | Now | Reason |
|---|---|---|---|
| `RB-01` exact fit | PASS | FAILED_CHECKS / `INSUFFICIENT_LENGTH` | Blueprint §5.3 requires a positive remainder; zero remainder removes no fabric. Matches N1. Narthananilaa to confirm. |
| `IF-05`, `IF-06` | FAILED_CHECKS / `INVALID_PARAMETER` | NEEDS_INPUT / `IMPLAUSIBLE_DIMENSION` | Implausible values must stop before any geometry runs (§5.5, feasibility CLAUDE.md), so they ask for input. |
| `UG-01` | knit tee, `UNSUPPORTED_MATERIAL` | knit fabric on `woven_shirt`, same code | A tee is a garment-category failure in the engine; the material case now isolates the material gate. |
| `UG-02` | unknown material, IDEA_ONLY | unknown recipe ID, IDEA_ONLY / `UNSUPPORTED_RECIPE` | Unknown material asks for confirmation (§5.4), so it moved to new `MU-06` (NEEDS_INPUT). `UG-02` now tests fail-closed recipe allow-listing. |
| `UG-04` | elastane woven | jersey tee, `UNSUPPORTED_GARMENT_CATEGORY` | Contract v1 `FabricFamily` has no stretch-woven value. |
| Failure-code names | provisional | contract v1 enum | Cases use K1's codes; the adapter maps N1's. |

Added: `MU-05` (measurement `vision_suggested`, `confirmed_at: null`, expect NEEDS_INPUT / `MISSING_DIMENSION`, contract v1: unconfirmed counts as missing) and `MU-06` (fabric unknown, NEEDS_INPUT / `MATERIAL_UNKNOWN`).

## Known failures against N1 (PR #12)

`MU-04` (conflicting flat width and circumference) and `MU-05` (unconfirmed measurement) are false acceptances in N1's current engine. They are real engine gaps, so the suite fails by design until N1 fixes them. Do not edit the expectations.

## Open points for Narthananilaa (needs-human)

- Confirm the `RB-01` zero-remainder convention above.
- `MU-03` (bare number, no unit) maps to `IMPLAUSIBLE_DIMENSION` because contract v1 has no failure code for an ambiguous unit; K1 may want one.

## Files

`adapter.py` engine seam and `to_mm` · `cases.py` loader and scoring · `report.py` counts and gate · `test_case_files.py` data and scoring tests · `test_constraint_suite.py` the 24 cases · `test_properties.py` Hypothesis cm/mm and boundary properties · `ci-job.example.yml` for K5.
