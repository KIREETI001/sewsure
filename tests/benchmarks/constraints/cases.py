"""Load case files and score them. Pure functions; the engine is injected."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from adapter import PASS, Outcome

CASES_DIR = Path(__file__).parent / "cases"

CLASS_COUNTS = {
    "supported_success": 6,
    "insufficient_fabric_or_placement": 6,
    "missing_unit_implausible": 4,
    "unsupported_garment_or_material": 4,
    "revision_seam_edge": 4,
}

# Scoring buckets
CORRECT_REJECTION = "correct_rejection"
CORRECT_ACCEPTANCE = "correct_acceptance"
FALSE_ACCEPTANCE = "false_acceptance"
FALSE_REJECTION = "false_rejection"
INDETERMINATE = "indeterminate"


def load_cases() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(CASES_DIR.glob("*.json"))]


def steps_of(case: dict) -> list[dict]:
    """A case is one step, or several for revision sequences."""
    if "steps" in case:
        return case["steps"]
    return [{"label": case["id"], "inputs": case["inputs"], "expected": case["expected"]}]


@dataclass
class StepResult:
    label: str
    expected: dict
    outcome: Outcome
    bucket: str
    status_match: bool
    codes_match: bool


def score_step(expected: dict, outcome: Outcome) -> str:
    exp_pass = expected["status"] == PASS
    if outcome.indeterminate:
        return INDETERMINATE
    got_pass = outcome.status == PASS
    if exp_pass:
        return CORRECT_ACCEPTANCE if got_pass else FALSE_REJECTION
    return FALSE_ACCEPTANCE if got_pass else CORRECT_REJECTION


def run_case(case: dict, evaluate: Callable[[dict], Outcome]) -> list[StepResult]:
    results = []
    for step in steps_of(case):
        outcome = evaluate(step["inputs"])
        exp = step["expected"]
        results.append(StepResult(
            label=step["label"], expected=exp, outcome=outcome,
            bucket=score_step(exp, outcome),
            status_match=outcome.status == exp["status"],
            codes_match=sorted(exp["failure_codes"]) == sorted(outcome.failure_codes),
        ))
    return results


def summarise(per_case: dict[str, list[StepResult]], cases: list[dict]) -> dict:
    """Counts with denominators. Denominators are steps, so the revision sequence counts three times."""
    by_id = {c["id"]: c for c in cases}
    counts = {k: 0 for k in (CORRECT_REJECTION, CORRECT_ACCEPTANCE, FALSE_ACCEPTANCE, FALSE_REJECTION, INDETERMINATE)}
    exp_reject = exp_accept = total = 0
    destructive_false_accept = []
    status_mismatch = []
    for cid, results in per_case.items():
        for r in results:
            total += 1
            counts[r.bucket] += 1
            if r.expected["status"] == PASS:
                exp_accept += 1
            else:
                exp_reject += 1
            if r.bucket == FALSE_ACCEPTANCE and by_id[cid].get("destructive_cut"):
                destructive_false_accept.append(f"{cid}: {r.label}")
            if not (r.status_match and r.codes_match):
                status_mismatch.append(f"{cid}: {r.label}")
    return {
        "counts": counts, "total": total, "expected_reject": exp_reject, "expected_accept": exp_accept,
        "destructive_false_acceptances": destructive_false_accept, "mismatches": status_mismatch,
    }
