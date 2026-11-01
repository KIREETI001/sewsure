# ruff: noqa: E402  (sys.path set before imports)
"""AI eval harness: runs cases.jsonl through the pipeline and reports counts.

Every metric is numerator/denominator. The run uses the REAL feasibility engine
(`sewsure_feasibility.evaluate`, synthetic garments from each case) but a MOCK
model (MockModelClient) and a MOCK safety screen (keyword rules). The numbers
therefore show how the pipeline validates and routes model output and relays the
engine's verdicts. They say nothing about real model quality or Prompt Shields
detection rates; re-run the same cases against Azure once it exists.

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

from ai.engine_adapter import EvaluateChecker
from ai.model_client import MockModelClient
from ai.pipeline import DesignRequest, run_pipeline
from ai.safety import AllowAllScreen, MockSafetyScreen
from ai.schemas import RECIPE_ALLOW_LIST
from ai.synthetic import SyntheticContextProvider
from sewsure_feasibility import DesignState

CASES_PATH = HERE / "cases.jsonl"


def load_cases(path: Path = CASES_PATH) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _run(case: dict, screen):
    r = case["request"]
    req = DesignRequest(
        garment_category=r["garment_category"],
        garment_confidence=r["garment_confidence"],
        fabric_family=r["fabric_family"],
        inspiration_text=r["inspiration_text"],
        provided_dimensions=frozenset(r["provided_dimensions"]),
        context_id=case["id"],
    )
    return run_pipeline(
        req,
        client=MockModelClient(scripted=case["mock_model_output"]),
        checker=EvaluateChecker(SyntheticContextProvider(case["garment"])),
        screen=screen,
    )


def _violations(case: dict, outcome) -> list[str]:
    """Things a returned design must never contain."""
    bad = []
    forbidden = set(case["expected"]["forbidden_levels"])
    for d in outcome.designs:
        cand = d.candidate
        if cand.recipe_id not in RECIPE_ALLOW_LIST:
            bad.append("recipe_not_allow_listed")
        if cand.parameters.get("crop_level") in forbidden:
            bad.append("forbidden_level")
        if d.engine_status is not DesignState.PASS_SUPPORTED_CHECKS:
            bad.append("design_without_engine_pass")
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
            "reasons_match": set(exp["reasons"]) <= set(out.reasons),
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
        "reasons_match": {
            "numerator": sum(r["reasons_match"] for r in rows),
            "denominator": len(rows),
        },
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
        "mode": "real_engine+mock_model+mock_screen",
        "caveat": (
            "Real feasibility engine, MOCK model and MOCK screen. Says nothing about real "
            "model quality or Prompt Shields detection."
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
