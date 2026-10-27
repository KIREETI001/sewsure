# Constraint suite (blueprint §17.2, §5.5)

24 synthetic cases that check the feasibility engine blocks what it must block and passes what it can support. All inputs are invented. None comes from a real person or a real garment, and none is measured evidence.

| Class | Cases | Files |
|---|---|---|
| Supported successful transformations | 6 | `ss-*.json` |
| Insufficient fabric / invalid placement | 6 | `if-*.json` |
| Measurement missing / unit / implausible | 4 | `mu-*.json` |
| Unsupported garment or material (expect `IDEA_ONLY`) | 4 | `ug-*.json` |
| Revision / seam / edge-boundary | 4 | `rb-*.json` |

`SS-01` is the blueprint §5.3 example (780 mm shirt, 500 mm finished, 30 mm hem). `RB-04` is a three-step revision sequence, so the suite is 24 cases and 26 checks. Counts below use checks as the denominator.

## Run it

```bash
pip install -r requirements.txt
cd tests/benchmarks/constraints
python -m pytest            # data checks always run; engine tests skip if the engine is not importable
python report.py            # counts as numerator/denominator
python report.py --strict   # also fail on any status/code mismatch or indeterminate result
```

`report.py` exit codes: `0` ok, `1` a false acceptance on a destructive cut (the CI gate), `2` engine not importable (`--allow-skip` makes that `0`, for local use only), `3` `--strict` mismatch.

The engine is reached through one function, `adapter.evaluate_inputs`, which calls `evaluate(garment, measurements, recipe_id, params)` from `sewsure_feasibility` or `feasibility` (override with `SEWSURE_FEASIBILITY_MODULE`). The result needs `status` and `failure_codes`. If N1's entry point differs, change `adapter.py` only.

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
5. If you add or remove a case, update `CLASS_COUNTS` in `cases.py` and say why in the PR. Each new rule needs a passing and a failing case.

## Why expected results change only with a written reason

The expected values are the specification the engine is held to. If a failing case is "fixed" by editing its expectation, the suite stops catching the thing it exists to catch, and a false acceptance can be hidden as a change of mind. So a PR that changes any `expected`, `reason` or `destructive_cut` value must explain in its description which rule changed, who decided (Narthananilaa approves), and the blueprint or recipe reference. Never change an expectation to make a run green.

## Open points for Narthananilaa (needs-human)

- Failure-code names (`LENGTH_EXCEEDS_AVAILABLE`, `PROHIBITED_REGION_CONFLICT`, ...) are provisional until N1 publishes the engine's vocabulary. Align the cases, with a written reason.
- Boundary convention in `RB-01`/`RB-02`: cut mark equal to available length passes (zero overshoot); any overshoot, even 0.01 mm, fails. This is a rule decision, not a test detail.
- Which `NEEDS_INPUT` versus `IDEA_ONLY` versus `FAILED_CHECKS` status belongs to implausible and ambiguous-unit inputs (`MU-*`, `UG-02`).

## Files

`adapter.py` engine seam and `to_mm` · `cases.py` loader and scoring · `report.py` counts and gate · `test_case_files.py` data and scoring tests · `test_constraint_suite.py` the 24 cases · `test_properties.py` Hypothesis cm/mm and boundary properties · `ci-job.example.yml` for K5.
