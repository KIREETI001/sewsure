# ruff: noqa: E402  (sys.path set before imports)
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "services" / "api"))

from run_eval import evaluate, load_cases


def test_case_file_shape():
    cases = load_cases()
    assert len(cases) == 30
    assert len({c["id"] for c in cases}) == 30
    cats = {c["category"] for c in cases}
    assert cats == {
        "success",
        "near_boundary",
        "missing_value",
        "impossible",
        "unsupported",
        "prompt_injection",
        "malformed_output",
    }
    for c in cases:
        assert c["expected"]["why"]


def test_no_false_approvals_and_all_outcomes_match():
    m = evaluate(load_cases())["metrics"]
    assert m["false_approvals"]["numerator"] == 0
    assert m["outcome_match"]["numerator"] == m["outcome_match"]["denominator"]
    assert m["reasons_match"]["numerator"] == m["reasons_match"]["denominator"]
    assert m["recipe_id_validity"]["numerator"] <= m["recipe_id_validity"]["denominator"]
    assert (
        m["injection_contained_without_screen"]["numerator"]
        == m["injection_contained_without_screen"]["denominator"]
    )
