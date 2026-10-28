# Constraint suite (blueprint §17.2, §5.5)

27 synthetic cases (the 24 proposed in §17.2, plus `MU-05`, `MU-06`, `MU-07` added after review, see below) that check the feasibility engine blocks what it must block and passes what it can support. All inputs are invented. None comes from a real person or a real garment, and none is measured evidence.

| Class | Cases | Files |
|---|---|---|
| Supported successful transformations | 6 | `ss-*.json` |
| Insufficient fabric / invalid placement | 6 | `if-*.json` |
| Measurement missing / unit / implausible | 7 | `mu-*.json` |
| Unsupported garment or material (expect `IDEA_ONLY`) | 4 | `ug-*.json` |
| Revision / seam / edge-boundary | 4 | `rb-*.json` |

`SS-01` is the blueprint §5.3 example (780 mm shirt, 500 mm finished, 30 mm hem). `RB-04` is a three-step revision sequence, so the suite is 27 cases and 29 checks. Counts below use checks as the denominator.

## Run it

```bash
pip install -r requirements.txt
cd tests/benchmarks/constraints
python -m pytest            # data checks always run; engine tests skip if the engine is not importable
python report.py            # counts as numerator/denominator
python report.py --strict   # also fail on any status/code mismatch or indeterminate result
```

`report.py` exit codes: `0` ok, `1` a false acceptance on a destructive cut (the CI gate), `2` engine not importable (`--allow-skip` makes that `0`, for local use only), `3` any indeterminate result (`--allow-indeterminate` to ignore) or, with `--strict`, any status/code mismatch. Mismatch lines show expected versus actual status and codes, and the engine error if it raised.

Case files use the contract vocabulary (K1, 1.0.0-draft.2): dimension names without unit suffix (`shoulder_to_hem`), `woven_shirt` / `fabric_family`, origin `user_tape_measured`, contract failure codes. N1 uses the same names. The engine is reached through one function, `adapter.evaluate_inputs`, which builds N1's `Garment`, `Measurement` and `FabricPanel`/`Zone` types and calls `sewsure_feasibility.evaluate(garment, measurements, recipe_id, params)`. A seam margin widens each exclusion zone in the adapter. Override the module with `SEWSURE_FEASIBILITY_MODULE`.

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

## Expected results changed after review (written reasons)

Vocabulary is the contract's, 1.0.0-draft.2 (K1, PR #15); N1 (PR #12) uses the same names, so `adapter.py` has no translation tables.

| Case | Was | Now | Reason |
|---|---|---|---|
| `RB-01` exact fit | PASS | FAILED_CHECKS / `NO_POSITIVE_REMAINDER` | Blueprint §5.3 requires a positive remainder; zero remainder removes no fabric. Narthananilaa to confirm. |
| `RB-02` 0.5 mm overshoot, `IF-02` hem pushes past hem edge | `LENGTH_EXCEEDS_AVAILABLE` / `INSUFFICIENT_LENGTH` | `NO_POSITIVE_REMAINDER` | Finished length alone fits; the remainder after hem is not positive. draft.2 added the code for this. `IF-01` (finished >= available) stays `INSUFFICIENT_LENGTH`. |
| `IF-05` finished 0 mm | FAILED_CHECKS | NEEDS_INPUT / `IMPLAUSIBLE_DIMENSION` | Implausible values stop before geometry (§5.5). |
| `IF-06` hem -30 mm | FAILED_CHECKS | NEEDS_INPUT / `INVALID_PARAMETER` | Negative length is an invalid parameter (draft.2). |
| `MU-02` 60 mm chest | `IMPLAUSIBLE_DIMENSION` | `POSSIBLE_UNIT_ERROR` | 60 mm x 10 is in range: a likely cm/mm slip (draft.2). |
| `MU-03` bare number | ambiguous unit | `NON_FINITE_VALUE` | No unit means no usable mm value; the adapter passes a non-finite value. |
| `MU-05` unconfirmed | `MISSING_DIMENSION` | `UNCONFIRMED_DIMENSION` | draft.2 added the code. |
| `UG-01`, `UG-02`, `UG-04` | see PR history | knit fabric on shirt / unknown recipe / jersey tee | Isolate the material, recipe and category gates. Unknown fabric is NEEDS_INPUT (`MU-06`), not IDEA_ONLY (§5.4). |
| all pass cases | no zone data | armhole zone 0-150 mm | The engine requires zone data; a gate that did not run is not a pass. |

Added: `MU-05` (unconfirmed measurement), `MU-06` (unknown fabric), `MU-07` (no prohibited-region data, `MISSING_PROHIBITED_ZONES`). The suite is 27 cases: 24 from §17.2 plus these three.

## Engine gaps

Where an expectation is right and the engine disagrees, the case stays failing and is listed in the PR comment as "Engine gaps for N1". Never edit an expectation to make a run green.

## Open points for Narthananilaa (needs-human)

- Confirm the `RB-01` zero-remainder convention above.

## Files

`adapter.py` engine seam and `to_mm` · `cases.py` loader and scoring · `report.py` counts and gate · `test_case_files.py` data and scoring tests · `test_constraint_suite.py` the 24 cases · `test_properties.py` Hypothesis cm/mm and boundary properties · `ci-job.example.yml` for K5.
