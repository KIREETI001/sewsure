"""Print the constraint-suite counts as numerator/denominator.

Exit codes:
  0  no false acceptance on a destructive cut
  1  at least one false acceptance on a destructive cut (CI gate)
  2  engine not importable (use --allow-skip to exit 0 instead; local use only)
  3  --strict and any status/failure-code mismatch or indeterminate result
"""
from __future__ import annotations

import argparse
import json
import sys

import adapter
import cases as C


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="also fail on any mismatch or indeterminate result")
    ap.add_argument("--allow-skip", action="store_true", help="exit 0 if the engine is not importable")
    ap.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = ap.parse_args(argv)

    all_cases = C.load_cases()
    try:
        adapter.load_engine()
    except adapter.EngineUnavailable as exc:
        print(f"SKIPPED: {exc}", file=sys.stderr)
        return 0 if args.allow_skip else 2

    per_case = {c["id"]: C.run_case(c, adapter.evaluate_inputs) for c in all_cases}
    s = C.summarise(per_case, all_cases)
    n = s["counts"]

    rows = [
        ("correct rejection", n[C.CORRECT_REJECTION], s["expected_reject"]),
        ("false acceptance", n[C.FALSE_ACCEPTANCE], s["expected_reject"]),
        ("correct acceptance", n[C.CORRECT_ACCEPTANCE], s["expected_accept"]),
        ("false rejection", n[C.FALSE_REJECTION], s["expected_accept"]),
        ("indeterminate", n[C.INDETERMINATE], s["total"]),
    ]
    if args.json:
        print(json.dumps({"rows": [{"name": a, "numerator": b, "denominator": c} for a, b, c in rows],
                          "destructive_false_acceptances": s["destructive_false_acceptances"],
                          "mismatches": s["mismatches"]}, indent=2))
    else:
        print(f"SewSure constraint suite: {len(all_cases)} cases, {s['total']} checks (synthetic inputs)")
        for name, num, den in rows:
            print(f"  {name:<20} {num}/{den}")
        print(f"  exact status+code match {s['total'] - len(s['mismatches'])}/{s['total']}")
        for line in s["mismatches"]:
            print(f"    mismatch: {line}")
        for line in s["destructive_false_acceptances"]:
            print(f"    FALSE ACCEPTANCE ON DESTRUCTIVE CUT: {line}")

    if s["destructive_false_acceptances"]:
        return 1
    if args.strict and (s["mismatches"] or n[C.INDETERMINATE]):
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
