# AI eval cases

`cases.jsonl`: 28 synthetic requests (5 success, 4 near-boundary, 4 missing-value, 3 impossible, 5 unsupported, 5 prompt-injection, 2 malformed-output). Names follow contract 1.0.0-draft.2 (category `woven_shirt`, fabric family `woven`, recipe `woven_shirt_crop_v1`, FailureCode reasons). Each records the request, the feasibility verdicts the stand-in checker returns (`oracle_rules`), any scripted model output, the expected outcome and why.

```bash
python tests/benchmarks/ai/run_eval.py --out result.json
pytest tests/benchmarks/ai services/api/ai
```

Needs `pydantic`, `jsonschema`, `pytest`. Every metric is numerator/denominator. Default mode uses the mock model, a rule-based checker and a keyword safety screen, so it measures validation and plumbing only. Expected results change only with a written reason in the PR (see `../CLAUDE.md`).
