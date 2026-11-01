"""Tests for make_report.py.

Every data row here is SYNTHETIC (record_status=synthetic, make ids SYN-*).
Nothing here is evidence of how SewSure performs.
"""

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import make_report as mr  # noqa: E402

TEMPLATE = Path(__file__).parents[3] / "docs" / "evaluation" / "physical-make-record.template.csv"
HEADER = ["make_id", "record_status", "dimension", "predicted_mm", "actual_mm", "abs_error_mm",
          "error_cause", "system_would_have_prevented"]


def write_csv(path, rows, header=HEADER):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    return path


def syn(make, dim, pred, act, rec="", status="synthetic"):
    return [make, status, dim, pred, act, rec, "synthetic cause", "unknown"]


def test_template_has_required_columns_and_reports_no_data(tmp_path):
    report = mr.run(TEMPLATE, tmp_path)
    text = report.read_text(encoding="utf-8")
    assert "No scored comparisons yet" in text
    assert not (tmp_path / "predicted_vs_actual.png").exists()


def test_template_covers_blueprint_17_3_fields():
    header = TEMPLATE.read_text(encoding="utf-8").splitlines()[0].split(",")
    for col in ["garment_id", "source_len_reading_1_mm", "source_len_reading_2_mm", "requested_change",
                "design_revision_id", "predicted_mm", "actual_mm", "abs_error_mm", "error_cause",
                "system_would_have_prevented", "rework", "time_minutes", "maker_confidence_1to5",
                "instructions_to_change", "consent_recorded", "images_allowed_for", "deletion_terms"]:
        assert col in header


def test_refuses_synthetic_without_flag(tmp_path):
    p = write_csv(tmp_path / "a.csv", [syn("SYN-1", "cut_mark_front", 530, 532)])
    with pytest.raises(SystemExit):
        mr.run(p, tmp_path / "out")


def test_one_make_works_and_is_stamped_synthetic(tmp_path):
    p = write_csv(tmp_path / "a.csv", [syn("SYN-1", "cut_mark_front", 530, 532),
                                       syn("SYN-1", "finished_length_front", 500, 497)])
    report = mr.run(p, tmp_path / "out", allow_synthetic=True)
    text = report.read_text(encoding="utf-8")
    assert "SYNTHETIC DATA" in text
    assert "1 make(s), 2 dimension comparison(s)" in text
    assert "| 1 | 2 | 2.5 | 3.0 | 2.0 |" in text
    assert (tmp_path / "out" / "predicted_vs_actual.png").stat().st_size > 0


def test_small_n_does_not_imply_confidence(tmp_path):
    p = write_csv(tmp_path / "a.csv", [syn("SYN-1", "d", 500, 503)])
    text = mr.run(p, tmp_path / "out", allow_synthetic=True).read_text(encoding="utf-8")
    assert "too few to say anything about typical error" in text
    assert "No confidence interval" in text
    lowered = text.lower()
    for banned in ["significant", "95%", "accurate", "reliable", "typical error is"]:
        assert banned not in lowered


def test_median_and_max_over_several_rows():
    rows = [mr.Row(2, "SYN-1", "synthetic", "d", 500, 500 + e, "", "", None) for e in (1, -2, 6)]
    s = mr.summarise(rows)
    assert (s["n"], s["makes"], s["median"], s["max"]) == (3, 1, 2, 6)


def test_negative_error_kept_as_absolute_and_signed(tmp_path):
    p = write_csv(tmp_path / "a.csv", [syn("SYN-1", "d", 500, 490)])
    text = mr.run(p, tmp_path / "out", allow_synthetic=True).read_text(encoding="utf-8")
    assert "-10.0" in text and "| 10.0 |" in text


def test_unscorable_rows_are_listed_not_dropped(tmp_path):
    p = write_csv(tmp_path / "a.csv", [syn("SYN-1", "d", 500, 505),
                                       syn("SYN-1", "e", 500, ""),
                                       syn("SYN-1", "f", "abc", 5),
                                       syn("SYN-1", "g", -5, 5)])
    text = mr.run(p, tmp_path / "out", allow_synthetic=True).read_text(encoding="utf-8")
    assert "Rows not scored (3)" in text
    assert "not filled in yet" in text and "non-numeric" in text and "positive millimetres" in text


def test_recorded_error_mismatch_is_flagged(tmp_path):
    p = write_csv(tmp_path / "a.csv", [syn("SYN-1", "d", 500, 505, rec="2")])
    text = mr.run(p, tmp_path / "out", allow_synthetic=True).read_text(encoding="utf-8")
    assert "does not match the readings" in text


def test_bad_status_is_not_scored(tmp_path):
    p = write_csv(tmp_path / "a.csv", [syn("M1", "d", 500, 505, status="maybe")])
    loaded = mr.load(p)
    assert loaded.rows == [] and "record_status" in loaded.skipped[0][2]


def test_missing_required_column_raises(tmp_path):
    p = write_csv(tmp_path / "a.csv", [["x", "y"]], header=["make_id", "dimension"])
    with pytest.raises(ValueError):
        mr.load(p)


def test_two_makes_counted_separately(tmp_path):
    p = write_csv(tmp_path / "a.csv", [syn("SYN-1", "d", 500, 502), syn("SYN-2", "d", 500, 497)])
    s = mr.summarise(mr.load(p).rows)
    assert (s["makes"], s["n"]) == (2, 2)
