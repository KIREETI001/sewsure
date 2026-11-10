# AI eval cases

`cases.jsonl`: 30 synthetic requests (5 success, 4 near-boundary, 6 missing-value, 3 impossible, 5 unsupported, 5 prompt-injection, 2 malformed-output). Each records the request, a synthetic garment spec for the real feasibility engine, any scripted model output, the expected outcome and reasons, and why. Names follow contract 1.0.0-draft.2.

```bash
python tests/benchmarks/ai/run_eval.py --out result.json
pytest tests/benchmarks/ai services/api/ai
```

Needs `sewsure-feasibility`, `sewsure-contracts` (both in `packages/`), `pydantic`, `jsonschema`, `pytest`. Every metric is numerator/denominator.

The run uses the real engine but a MOCK model and a MOCK keyword screen, so it shows how the pipeline validates and routes output and relays the engine. It says nothing about real model quality or Prompt Shields detection. Expected results change only with a written reason in the PR (see `../CLAUDE.md`).
