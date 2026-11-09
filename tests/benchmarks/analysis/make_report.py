"""Predicted-vs-actual report for physical makes (blueprint section 17.3 / 17.4).

Reads the CSV described in docs/evaluation/physical-make-record.md and writes
a markdown report and a chart. Standard library plus matplotlib.

Design rules:
- Every row is shown. Rows that cannot be scored are listed with the reason, never dropped.
- Median and maximum absolute error are always printed with the sample size
  (makes and dimension comparisons). No confidence interval, no "typical error"
  claim, and a small-sample notice below MIN_N_FOR_SUMMARY comparisons.
- Synthetic rows are refused unless --allow-synthetic is given, and then every
  output is stamped SYNTHETIC.

Usage:
    python make_report.py physical-make-01.csv --out out/
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_COLUMNS = ["make_id", "record_status", "dimension", "predicted_mm", "actual_mm"]
# Below this many scored comparisons we only list errors; no summary is called representative.
MIN_N_FOR_SUMMARY = 5
# The recorded abs_error_mm may differ from the recomputed value by rounding only.
ABS_ERROR_TOLERANCE_MM = 0.05


@dataclass
class Row:
    line: int
    make_id: str
    status: str
    dimension: str
    predicted: float
    actual: float
    cause: str
    prevented: str
    recorded_abs: float | None

    @property
    def signed_error(self) -> float:
        return self.actual - self.predicted

    @property
    def abs_error(self) -> float:
        return abs(self.signed_error)


@dataclass
class Loaded:
    rows: list[Row] = field(default_factory=list)
    skipped: list[tuple[int, str, str]] = field(default_factory=list)  # (line, make_id, reason)
    mismatches: list[str] = field(default_factory=list)
    statuses: set[str] = field(default_factory=set)


def _num(text: str | None) -> float | None:
    if text is None or text.strip() == "":
        return None
    return float(text)


def load(path: Path) -> Loaded:
    out = Loaded()
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
        for i, rec in enumerate(reader, start=2):  # line 1 is the header
            if not any((v or "").strip() for v in rec.values()):
                continue
            make = (rec.get("make_id") or "").strip()
            status = (rec.get("record_status") or "").strip().lower()
            out.statuses.add(status)
            if status not in ("real", "synthetic"):
                out.skipped.append((i, make, f"record_status must be real or synthetic, got {status!r}"))
                continue
            try:
                pred = _num(rec.get("predicted_mm"))
                act = _num(rec.get("actual_mm"))
                rec_abs = _num(rec.get("abs_error_mm"))
            except ValueError as exc:
                out.skipped.append((i, make, f"non-numeric value ({exc})"))
                continue
            if not make or not (rec.get("dimension") or "").strip():
                out.skipped.append((i, make, "make_id or dimension empty"))
                continue
            if pred is None or act is None:
                out.skipped.append((i, make, "predicted_mm or actual_mm not filled in yet"))
                continue
            if pred <= 0 or act <= 0 or pred != pred or act != act:
                out.skipped.append((i, make, "predicted_mm and actual_mm must be positive millimetres"))
                continue
            row = Row(i, make, status, rec["dimension"].strip(), pred, act,
                      (rec.get("error_cause") or "").strip(),
                      (rec.get("system_would_have_prevented") or "").strip(),
                      rec_abs)
            if rec_abs is not None and abs(rec_abs - row.abs_error) > ABS_ERROR_TOLERANCE_MM:
                out.mismatches.append(
                    f"line {i} ({make}/{row.dimension}): recorded abs_error_mm {rec_abs:g} "
                    f"but |actual - predicted| = {row.abs_error:g}")
            out.rows.append(row)
    return out


def summarise(rows: list[Row]) -> dict:
    errs = [r.abs_error for r in rows]
    return {
        "n": len(errs),
        "makes": len({r.make_id for r in rows}),
        "median": statistics.median(errs) if errs else None,
        "max": max(errs) if errs else None,
        "min": min(errs) if errs else None,
    }


def _fmt(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.1f}"


def small_n_notice(s: dict) -> str:
    if s["n"] == 0:
        return "No scored comparisons yet. Nothing to report."
    parts = [f"Sample: {s['makes']} make(s), {s['n']} dimension comparison(s)."]
    if s["makes"] < 2 or s["n"] < MIN_N_FOR_SUMMARY:
        parts.append(
            "This is too few to say anything about typical error. The median and maximum below "
            "describe only these observations. No confidence interval is given and none should be "
            "inferred. Read the individual rows and their causes.")
    else:
        parts.append(
            "Median and maximum describe these observations only; comparisons from the same make "
            "are not independent, so the count of makes is the more honest sample size.")
    return " ".join(parts)


def build_markdown(data: Loaded, chart_name: str | None) -> str:
    synthetic = "synthetic" in {r.status for r in data.rows}
    s = summarise(data.rows)
    lines: list[str] = []
    if synthetic:
        lines += ["> **SYNTHETIC DATA. TEST OUTPUT ONLY. NOT EVIDENCE.**", ""]
    lines += ["# Physical make report", ""]
    lines += [small_n_notice(s), ""]
    if not data.rows:
        pass
    else:
        lines += [
            "## Summary (absolute error, mm)", "",
            "| Makes | Comparisons scored | Median | Maximum | Minimum |",
            "|---|---|---|---|---|",
            f"| {s['makes']} | {s['n']} | {_fmt(s['median'])} | {_fmt(s['max'])} | {_fmt(s['min'])} |",
            "", "## Predicted vs actual (all scored rows)", "",
            "| Make | Dimension | Predicted (mm) | Actual (mm) | Signed error (mm) | Absolute error (mm) | Cause | System would have prevented? |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in data.rows:
            lines.append(f"| {r.make_id} | {r.dimension} | {r.predicted:g} | {r.actual:g} | "
                         f"{r.signed_error:+.1f} | {r.abs_error:.1f} | {r.cause or 'not recorded'} | "
                         f"{r.prevented or 'not recorded'} |")
        by_dim: dict[str, list[Row]] = {}
        for r in data.rows:
            by_dim.setdefault(r.dimension, []).append(r)
        lines += ["", "## By dimension", "",
                  "| Dimension | n | Median abs error (mm) | Max abs error (mm) |", "|---|---|---|---|"]
        for dim, rs in sorted(by_dim.items()):
            d = summarise(rs)
            lines.append(f"| {dim} | {d['n']} | {_fmt(d['median'])} | {_fmt(d['max'])} |")
        if chart_name:
            lines += ["", f"![Predicted vs actual]({chart_name})"]
    if data.mismatches:
        lines += ["", "## Recorded error does not match the readings", ""]
        lines += [f"- {m}" for m in data.mismatches]
    if data.skipped:
        lines += ["", f"## Rows not scored ({len(data.skipped)})", "",
                  "| CSV line | Make | Reason |", "|---|---|---|"]
        lines += [f"| {ln} | {mk or '(none)'} | {why} |" for ln, mk, why in data.skipped]
    lines += ["", "## Notes", "",
              "- Error = actual minus predicted, in mm. No tolerance is applied here: the allowable "
              "tolerance is to be agreed with the sewing expert before looking at results (blueprint 6.3, 17.4).",
              "- Every row of the input appears above or in the not-scored list."]
    return "\n".join(lines) + "\n"


def make_chart(data: Loaded, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = data.rows
    synthetic = "synthetic" in {r.status for r in rows}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
    lo = min(min(r.predicted, r.actual) for r in rows)
    hi = max(max(r.predicted, r.actual) for r in rows)
    pad = max((hi - lo) * 0.1, 10)
    ax1.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color="grey", linestyle="--", label="actual = predicted")
    makes = sorted({r.make_id for r in rows})
    for mk in makes:
        rs = [r for r in rows if r.make_id == mk]
        ax1.scatter([r.predicted for r in rs], [r.actual for r in rs], label=mk, zorder=3)
    ax1.set_xlabel("Predicted (mm)")
    ax1.set_ylabel("Actual (mm)")
    ax1.set_title("Predicted vs actual")
    ax1.legend(fontsize=8)
    labels = [f"{r.make_id}\n{r.dimension}" for r in rows]
    ax2.barh(range(len(rows)), [r.abs_error for r in rows], color="#4477aa")
    ax2.set_yticks(range(len(rows)))
    ax2.set_yticklabels(labels, fontsize=7)
    ax2.invert_yaxis()
    ax2.set_xlabel("Absolute error (mm)")
    ax2.set_title("Absolute error per comparison")
    s = summarise(rows)
    foot = (f"n = {s['makes']} make(s), {s['n']} comparison(s). Median {_fmt(s['median'])} mm, "
            f"max {_fmt(s['max'])} mm. Observations only; no confidence level.")
    fig.text(0.01, 0.01, foot, fontsize=8)
    if synthetic:
        fig.suptitle("SYNTHETIC DATA. NOT EVIDENCE.", color="red", fontweight="bold")
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run(csv_path: Path, out_dir: Path, allow_synthetic: bool = False) -> Path:
    data = load(csv_path)
    if "synthetic" in data.statuses and not allow_synthetic:
        raise SystemExit("Refusing: the CSV contains synthetic rows. Use --allow-synthetic for tests "
                         "only; the output will be stamped SYNTHETIC.")
    out_dir.mkdir(parents=True, exist_ok=True)
    chart_name = None
    if data.rows:
        chart_name = "predicted_vs_actual.png"
        make_chart(data, out_dir / chart_name)
    report = out_dir / "make_report.md"
    report.write_text(build_markdown(data, chart_name), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("csv", type=Path)
    ap.add_argument("--out", type=Path, default=Path("out"))
    ap.add_argument("--allow-synthetic", action="store_true", help="tests only; output is stamped SYNTHETIC")
    args = ap.parse_args(argv)
    report = run(args.csv, args.out, args.allow_synthetic)
    print(f"Wrote {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
