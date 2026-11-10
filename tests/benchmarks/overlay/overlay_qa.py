"""Overlay QA (blueprint 6.3): median and worst-case error vs independently measured marks.

Input CSV columns: trial_id, synthetic, phone, angle_deg, fabric, mark_id, displayed_x_px,
displayed_y_px, observed_x_px, observed_y_px, px_per_mm, calibration_state, rejection_reason.
``synthetic`` must be ``true`` or ``false`` on every row; the report labels the data accordingly.
Error per mark = pixel distance between displayed overlay point and the observed physical mark,
divided by px_per_mm. Rejected trials are counted, not scored. The tolerance is optional and
human-set; without it no pass/fail verdict is given.
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

REQUIRED = (
    "trial_id",
    "synthetic",
    "phone",
    "angle_deg",
    "fabric",
    "mark_id",
    "displayed_x_px",
    "displayed_y_px",
    "observed_x_px",
    "observed_y_px",
    "px_per_mm",
    "calibration_state",
    "rejection_reason",
)


def load(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing columns: {missing}")
        rows = list(reader)
    for r in rows:
        if r["synthetic"].strip().lower() not in ("true", "false"):
            raise ValueError(f"row {r['trial_id']}/{r['mark_id']}: synthetic must be true/false")
    return rows


def error_mm(r: dict[str, str]) -> float:
    ppm = float(r["px_per_mm"])
    if not ppm > 0:
        raise ValueError(f"row {r['trial_id']}: px_per_mm must be > 0")
    dx = float(r["displayed_x_px"]) - float(r["observed_x_px"])
    dy = float(r["displayed_y_px"]) - float(r["observed_y_px"])
    return math.hypot(dx, dy) / ppm


def _stats(errs: list[float]) -> str:
    if not errs:
        return "no scored marks"
    return f"median {statistics.median(errs):.2f} mm, worst {max(errs):.2f} mm (n={len(errs)})"


def report(rows: list[dict[str, str]], tolerance_mm: float | None = None) -> str:
    synth = {r["synthetic"].strip().lower() == "true" for r in rows}
    label = {frozenset({True}): "SYNTHETIC DATA", frozenset({False}): "PHYSICAL DATA"}.get(
        frozenset(synth), "MIXED"
    )
    trials = {r["trial_id"] for r in rows}
    rejected = {r["trial_id"] for r in rows if r["calibration_state"] != "calibrated"}
    scored = [r for r in rows if r["trial_id"] not in rejected]
    errs = [error_mm(r) for r in scored]
    out = [f"# Overlay QA report ({label})", ""]
    out.append(
        f"Trials: {len(trials) - len(rejected)}/{len(trials)} calibrated and scored; "
        f"{len(rejected)}/{len(trials)} rejected (not scored)."
    )
    out.append(f"Overall: {_stats(errs)}")
    if tolerance_mm is None:
        out.append("Tolerance not set: no pass/fail verdict.")
    else:
        over = sum(e > tolerance_mm for e in errs)
        out.append(f"Marks over tolerance {tolerance_mm} mm: {over}/{len(errs)}")
    for col in ("phone", "angle_deg", "fabric"):
        groups: dict[str, list[float]] = defaultdict(list)
        for r, e in zip(scored, errs, strict=True):
            groups[r[col]].append(e)
        out += ["", f"## By {col}"] + [f"- {k}: {_stats(v)}" for k, v in sorted(groups.items())]
    reasons: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        if r["trial_id"] in rejected:
            reasons[r["rejection_reason"] or "unspecified"].add(r["trial_id"])
    out += ["", "## Rejections"]
    out += [f"- {k}: {len(v)}/{len(trials)}" for k, v in sorted(reasons.items())]
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path)
    ap.add_argument("--tolerance-mm", type=float, default=None)
    a = ap.parse_args()
    print(report(load(a.csv), a.tolerance_mm))


if __name__ == "__main__":
    main()
