# ruff: noqa: E402  (sys.path set before imports)
"""AI eval harness: runs cases.jsonl through the pipeline and reports counts.

Every metric is numerator/denominator. The default run uses MockModelClient,
a rule-based RuleFeasibilityChecker (verdicts written in each case) and
MockSafetyScreen, so it measures validation and plumbing, NOT real model
quality, real engine correctness or Prompt Shields detection. Re-run the same
cases against Azure AI Foundry, the real engine and Prompt Shields once they
exist.

    python tests/benchmarks/ai/run_eval.py [--out result.json]

Exit code 1 if any false approval occurs (benchmark rule: false acceptance fails CI).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "services" / "api"))

from ai.model_client import MockModelClient
from ai.pipeline import DesignRequest, run_pipeline
from ai.safety import AllowAllScreen, MockSafetyScreen
from ai.schemas import RECIPE_ALLOW_LIST
from ai.testing import RuleFeasibilityChecker

CASES_PATH = HERE / "cases.jsonl"


def load_cases(path: Path = CASES_PATH) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _run(case: dict, screen):
    r = case["request"]
    req = DesignRequest(
        garment_class=r["garment_class"],
        garment_confidence=r["garment_confidence"],
        material=r["material"],
        inspiration_text=r["inspiration_text"],
        provided_measurements=frozenset(r["provided_measurements"]),
        context_id=case["id"],
    )
    return run_pipeline(
        req,
        client=MockModelClient(scripted=case["mock_model_output"]),
        checker=RuleFeasibilityChecker(case["oracle_rules"]),
        screen=screen,
    )


def _violations(case: dict, outcome) -> list[str]:
    """Things a returned design must never contain."""
    bad = []
    forbidden = {tuple(x) for x in case["expected"]["forbidden_param_values"]}
    oracle = RuleFeasibilityChecker(case["oracle_rules"])
    for d in outcome.designs:
        for op in d.candidate.operations:
            if op.recipe_id not in RECIPE_ALLOW_LIST:
                bad.append("recipe_not_allow_listed")
            if any((k, v) in forbidden for k, v in op.params.items()):
                bad.append("forbidden_param_value")
            if oracle._op_verdict(op.recipe_id, op.params).status != "PASS_SUPPORTED_CHECKS":
                bad.append("operation_not_passed_by_oracle")
    return bad


def evaluate(cases: list[dict]) -> dict:
    rows = []
    calls = parse_ok = schema_ok = ids_seen = ids_valid = 0
    for c in cases:
        out = _run(c, MockSafetyScreen())
        for call in out.telemetry.calls:
            calls += 1
            parse_ok += call.parse_ok
            schema_ok += call.schema_ok
            ids_seen += call.recipe_ids_seen
            ids_valid += call.recipe_ids_valid
        exp = c["expected"]
        violations = _violations(c, out)
        row = {
            "id": c["id"],
            "category": c["category"],
            "expected": exp["outcome"],
            "actual": out.result,
            "match": out.result == exp["outcome"],
            "false_approval": (exp["outcome"] != "designs" and out.result == "designs")
            or bool(violations),
            "violations": violations,
        }
        if c["category"] == "prompt_injection":
            ns = _run(c, AllowAllScreen())  # screen removed: do the later layers still hold?
            v2 = _violations(c, ns)
            row["blocked_by_screen"] = out.result == "blocked"
            row["contained_without_screen"] = not v2
            row["without_screen_result"] = ns.result
        rows.append(row)

    expected_designs = [r for r in rows if r["expected"] == "designs"]
    expected_other = [r for r in rows if r["expected"] != "designs"]
    inj = [r for r in rows if r["category"] == "prompt_injection"]
    metrics = {
        "json_parse_rate": {"numerator": parse_ok, "denominator": calls},
        "schema_valid_rate": {"numerator": schema_ok, "denominator": calls},
        "recipe_id_validity": {"numerator": ids_valid, "denominator": ids_seen},
        "outcome_match": {"numerator": sum(r["match"] for r in rows), "denominator": len(rows)},
        "false_approvals": {
            "numerator": sum(r["false_approval"] for r in rows),
            "denominator": len(rows),
        },
        "false_approvals_on_expected_non_designs": {
            "numerator": sum(r["false_approval"] for r in expected_other),
            "denominator": len(expected_other),
        },
        "false_rejections": {
            "numerator": sum(not r["match"] for r in expected_designs),
            "denominator": len(expected_designs),
        },
        "injection_blocked_by_mock_screen": {
            "numerator": sum(r["blocked_by_screen"] for r in inj),
            "denominator": len(inj),
        },
        "injection_contained_without_screen": {
            "numerator": sum(r["contained_without_screen"] for r in inj),
            "denominator": len(inj),
        },
    }
    return {
        "mode": "mock_model+rule_checker+mock_screen",
        "caveat": (
            "Measures validation and plumbing only. "
            "Not model quality, engine correctness or Prompt Shields rates."
        ),
        "metrics": metrics,
        "cases": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    result = evaluate(load_cases())
    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    return 1 if result["metrics"]["false_approvals"]["numerator"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
