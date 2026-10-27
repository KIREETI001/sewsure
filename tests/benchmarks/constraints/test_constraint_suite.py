"""The 24-case suite against the real feasibility engine (skipped until it is importable)."""
import pytest

import cases as C

ALL = C.load_cases()


@pytest.mark.parametrize("case", ALL, ids=lambda c: c["id"])
def test_case(case, engine):
    results = C.run_case(case, engine)
    for r in results:
        where = f"{case['id']} / {r.label}: {case['reason']}"
        assert r.bucket != C.FALSE_ACCEPTANCE, f"FALSE ACCEPTANCE ({where}); got {r.outcome.status}"
        assert r.bucket != C.INDETERMINATE, f"indeterminate ({where}); {r.outcome.error or r.outcome.status}"
        assert r.outcome.status == r.expected["status"], f"status ({where}); got {r.outcome.status}"
        assert sorted(r.expected["failure_codes"]) == r.outcome.failure_codes, (
            f"failure codes ({where}); got {r.outcome.failure_codes}"
        )


def test_non_shirt_never_gets_shirt_pass(engine):
    """Blueprint 5.5: a non-shirt must not receive shirt-specific pass status or cut points."""
    base = next(c for c in ALL if c["id"] == "UG-03")["inputs"]
    out = engine(base)
    assert out.status == "IDEA_ONLY"
    raw = out.raw if isinstance(out.raw, dict) else getattr(out.raw, "__dict__", {})
    assert not raw.get("cut_points") and not raw.get("cut_plan")
