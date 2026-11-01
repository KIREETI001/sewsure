"""Tests run on rows marked synthetic only."""

from pathlib import Path

import pytest
from overlay_qa import error_mm, load, report

SAMPLE = Path(__file__).parent / "sample_trials_synthetic.csv"


def test_sample_is_all_synthetic() -> None:
    assert all(r["synthetic"] == "true" and r["trial_id"].startswith("SYN-") for r in load(SAMPLE))


def test_error_known() -> None:
    r = {
        "trial_id": "SYN-x",
        "px_per_mm": "2",
        "displayed_x_px": "0",
        "displayed_y_px": "0",
        "observed_x_px": "6",
        "observed_y_px": "8",
    }
    assert error_mm(r) == pytest.approx(5.0)


def test_report_counts_and_rejections() -> None:
    text = report(load(SAMPLE))
    assert "SYNTHETIC DATA" in text and "3/4 calibrated" in text
    assert "ERROR_EXCEEDS_TOLERANCE: 1/4" in text and "no pass/fail verdict" in text
    assert "(n=12)" in text


def test_unlabelled_rows_rejected(tmp_path: Path) -> None:
    p = tmp_path / "x.csv"
    p.write_text(SAMPLE.read_text().replace("true", "maybe", 1))
    with pytest.raises(ValueError):
        load(p)
