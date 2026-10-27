# tests/benchmarks

Owner: Narthananilaa. Agent: N2 Constraint Test Designer. Also used by K3 (AI eval) and N4 (overlay QA).

## Suites

- `constraints/`: the 24-case suite (§17.2): 6 supported successes, 6 insufficient fabric or invalid placement, 4 missing/unit/implausible measurements, 4 unsupported garment or material, 4 revision/seam/edge cases. Plus the seven unit tests in §5.5.
- `ai/`: representative requests for the model, including near-boundary, missing-value, impossible and prompt-injection cases. Metrics: JSON parse rate, recipe-ID validity, false approvals.
- `overlay/`: calibration trials with independently measured reference points.

## Rules

- Each case records inputs, expected status, expected failure codes and why.
- Report counts as numerator/denominator: correct rejection, false acceptance, false rejection, indeterminate.
- Any false acceptance on a destructive cut fails CI.
- Expected results change only with a written reason in the PR.
- Inputs are synthetic or consented, never identifiable user data.
