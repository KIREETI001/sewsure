"""Engine-independent checks on the case data itself. These always run."""
import collections
import re

import pytest

import adapter
import cases as C

ALL = C.load_cases()


def test_suite_has_the_expected_class_split():
    assert len(ALL) == 26  # 24 from blueprint 17.2 + MU-05, MU-06 added after X1 review
    assert collections.Counter(c["class"] for c in ALL) == C.CLASS_COUNTS


def test_ids_unique():
    assert len({c["id"] for c in ALL}) == len(ALL)


@pytest.mark.parametrize("case", ALL, ids=lambda c: c["id"])
def test_case_is_well_formed(case):
    assert case["synthetic"] is True
    assert case["reason"].strip() and case["description"].strip()
    for step in C.steps_of(case):
        assert step["expected"]["status"] in adapter.STATES
        assert isinstance(step["expected"]["failure_codes"], list)
        # PASS never carries failure codes; every non-PASS carries at least one
        passed = step["expected"]["status"] == adapter.PASS
        assert bool(step["expected"]["failure_codes"]) != passed
        for name, meas in step["inputs"]["measurements"].items():
            assert not name.endswith("_mm"), "contract v1: dimension names carry no unit suffix"
            assert "origin" in meas and "confirmed_at" in meas, f"{name} lacks origin/confirmed_at"


@pytest.mark.parametrize("case", ALL, ids=lambda c: c["id"])
def test_expected_idea_only_cases_are_unsupported_inputs(case):
    # Guard against a case being relabelled IDEA_ONLY to hide an engine gap
    for step in C.steps_of(case):
        if step["expected"]["status"] == "IDEA_ONLY":
            assert case["class"] == "unsupported_garment_or_material"


def test_every_failing_length_case_overshoots_by_arithmetic():
    """The expected result must follow from the stated numbers, not from the engine."""
    for case in ALL:
        for step in C.steps_of(case):
            if step["expected"]["failure_codes"] == ["INSUFFICIENT_LENGTH"]:
                i = step["inputs"]
                length = i["measurements"]["shoulder_to_hem"]["value_mm"]
                mark = i["params"]["finished_length_mm"] + i["params"]["hem_allowance_mm"]
                assert mark >= length, case["id"]  # zero remainder fails (blueprint 5.3: positive remainder)
            if step["expected"]["status"] == adapter.PASS and not step["inputs"]["garment"]["prohibited_regions"]:
                i = step["inputs"]
                length = i["measurements"]["shoulder_to_hem"]["value_mm"]
                assert i["params"]["finished_length_mm"] + i["params"]["hem_allowance_mm"] < length, case["id"]


def test_blueprint_example_is_case_ss_01():
    c = next(c for c in ALL if c["id"] == "SS-01")
    p = c["inputs"]["params"]
    assert (c["inputs"]["measurements"]["shoulder_to_hem"]["value_mm"], p["finished_length_mm"], p["hem_allowance_mm"]) == (780, 500, 30)


def _outcome(status, codes=()):
    return adapter.Outcome(status, list(codes))


def test_scoring_buckets():
    exp_pass = {"status": adapter.PASS, "failure_codes": []}
    exp_fail = {"status": "FAILED_CHECKS", "failure_codes": ["X"]}
    assert C.score_step(exp_fail, _outcome(adapter.PASS)) == C.FALSE_ACCEPTANCE
    assert C.score_step(exp_fail, _outcome("NEEDS_INPUT")) == C.CORRECT_REJECTION
    assert C.score_step(exp_pass, _outcome("FAILED_CHECKS")) == C.FALSE_REJECTION
    assert C.score_step(exp_pass, _outcome(adapter.PASS)) == C.CORRECT_ACCEPTANCE
    assert C.score_step(exp_fail, _outcome(None)) == C.INDETERMINATE
    assert C.score_step(exp_fail, _outcome("SOMETHING_NEW")) == C.INDETERMINATE


def test_report_exits_nonzero_on_destructive_false_acceptance(monkeypatch, capsys):
    """An engine that passes everything must fail the gate."""
    import report

    monkeypatch.setattr(adapter, "load_engine", lambda: None)
    monkeypatch.setattr(adapter, "evaluate_inputs", lambda inputs: _outcome(adapter.PASS))
    assert report.main([]) == 1
    out = capsys.readouterr().out
    assert "FALSE ACCEPTANCE ON DESTRUCTIVE CUT" in out
    assert "false acceptance" in out and "/" in out


def test_report_clean_when_engine_matches_expectations(monkeypatch, capsys):
    import report

    expected = {}
    for c in ALL:
        for s in C.steps_of(c):
            expected[repr(s["inputs"])] = s["expected"]

    def oracle(inputs):
        e = expected[repr(inputs)]
        return _outcome(e["status"], e["failure_codes"])

    monkeypatch.setattr(adapter, "load_engine", lambda: None)
    monkeypatch.setattr(adapter, "evaluate_inputs", oracle)
    assert report.main(["--strict"]) == 0
    out = capsys.readouterr().out
    assert re.search(r"false acceptance\s+0/20", out) and re.search(r"false rejection\s+0/8", out)


def test_report_exits_2_when_engine_missing(monkeypatch):
    import report

    def boom():
        raise adapter.EngineUnavailable("test")

    monkeypatch.setattr(adapter, "load_engine", boom)
    assert report.main([]) == 2
    assert report.main(["--allow-skip"]) == 0
