"""Fit and ease (N3). Synthetic numbers only: no real garments or body measurements."""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pytest
from hypothesis import given
from hypothesis import strategies as st

from sewsure_feasibility import Measurement
from sewsure_feasibility.fit import (
    MAX_WARNING_CHARS,
    EaseConfig,
    FitAssessment,
    FitLabel,
    assess_fit,
    finished_dimensions,
    load_config,
    parse_config,
)

CONFIRMED = datetime(2026, 10, 28, tzinfo=UTC)
RECIPE = "woven_shirt_crop_v1"
SCHEMA = Path(__file__).parents[2] / "contracts" / "schemas" / "fit-assessment.schema.json"


def m(value_mm: float, confirmed: bool = True) -> Measurement:
    return Measurement(value_mm, "user_tape_measured", CONFIRMED if confirmed else None)


def fit(
    flat: float | None = 540.0,
    body: float | None = 940.0,
    *,
    garment_type: str | None = "woven_shirt",
    recipe: str = RECIPE,
    extra_garment: dict[str, Measurement] | None = None,
    flat_confirmed: bool = True,
    body_confirmed: bool = True,
    config: EaseConfig | None = None,
) -> FitAssessment:
    garment: dict[str, Measurement] = dict(extra_garment or {})
    if flat is not None:
        garment["chest_flat_width"] = m(flat, flat_confirmed)
    body_map = {"chest_circumference": m(body, body_confirmed)} if body is not None else {}
    return assess_fit(
        body_profile_id="bp-1",
        revision_id="rev-002",
        recipe_id=recipe,
        garment_type=garment_type,
        garment=garment,
        body=body_map,
        config=config,
    )


def text(a: FitAssessment) -> str:
    return " | ".join(a.warnings)


# --- labels (woven, provisional bands: <80 insufficient, <120 close, <180 regular, <250 relaxed)


def test_regular_label() -> None:
    a = fit(flat=540)  # 1080 - 940 = 140
    assert a.fit_label is FitLabel.REGULAR
    assert a.ease_mm == {"chest_circumference": 140.0}


def test_relaxed_label() -> None:
    a = fit(flat=580)  # 1160 - 940 = 220
    assert a.fit_label is FitLabel.RELAXED
    assert a.ease_mm["chest_circumference"] == 220.0


def test_oversized_label() -> None:
    a = fit(flat=650)  # 1300 - 940 = 360
    assert a.fit_label is FitLabel.OVERSIZED


def test_close_label_has_narrow_warning_not_a_pass() -> None:
    a = fit(flat=520)  # 1040 - 940 = 100
    assert a.fit_label is FitLabel.CLOSE
    assert "Narrow ease" in text(a)


def test_insufficient_ease_label_and_warning() -> None:
    a = fit(flat=470)  # 940 - 940 = 0
    assert a.fit_label is FitLabel.INSUFFICIENT_EASE
    assert "below the provisional minimum" in text(a)


def test_negative_ease_warning() -> None:
    a = fit(flat=450)  # 900 - 940 = -40
    assert a.fit_label is FitLabel.INSUFFICIENT_EASE
    assert a.ease_mm["chest_circumference"] == -40.0
    assert "Negative ease" in text(a)


@pytest.mark.parametrize(
    ("ease", "label"),
    [
        (79.9, FitLabel.INSUFFICIENT_EASE),
        (80.0, FitLabel.CLOSE),
        (119.9, FitLabel.CLOSE),
        (120.0, FitLabel.REGULAR),
        (179.9, FitLabel.REGULAR),
        (180.0, FitLabel.RELAXED),
        (249.9, FitLabel.RELAXED),
        (250.0, FitLabel.OVERSIZED),
    ],
)
def test_band_boundaries(ease: float, label: FitLabel) -> None:
    body = 1000.0
    a = assess_fit(
        body_profile_id="bp",
        revision_id="r",
        recipe_id=RECIPE,
        garment_type="woven_shirt",
        garment={"chest_circumference": m(body + ease)},
        body={"chest_circumference": m(body)},
    )
    assert a.fit_label is label


def test_every_narrow_result_carries_a_warning() -> None:
    for flat in range(450, 600, 5):
        a = fit(flat=float(flat))
        if a.fit_label in (FitLabel.CLOSE, FitLabel.INSUFFICIENT_EASE):
            assert any("Narrow" in w or "below" in w or "Negative" in w for w in a.warnings), flat


def test_near_minimum_warns_about_uncertainty() -> None:
    a = fit(flat=525)  # ease 110: regular? no, close; 110-20 = 90 >= 80 so no uncertainty warning
    assert a.fit_label is FitLabel.CLOSE
    b = fit(flat=505)  # ease 70 -> insufficient; boundary warning not duplicated
    assert b.fit_label is FitLabel.INSUFFICIENT_EASE
    c = fit(flat=545)  # ease 150 regular, 150-20 = 130 >= 120
    assert "uncertainty of insufficient" not in text(c)
    d = fit(flat=530)  # ease 120 regular but 120-20 = 100 -> close side; also spans bands
    assert "Label may fall in a neighbouring band" in text(d)


def test_regular_just_above_minimum_warns() -> None:
    # ease 90: close, and 90 - 20 = 70 < 80 -> within uncertainty of insufficient
    a = fit(flat=515)
    assert a.fit_label is FitLabel.CLOSE
    assert "uncertainty of insufficient ease" in text(a)


# --- jersey: wider uncertainty


def test_jersey_has_wider_uncertainty_and_warning() -> None:
    woven = fit(flat=540, garment_type="woven_shirt")
    knit = fit(flat=540, garment_type="jersey_tee")
    assert woven.uncertainty_mm is not None and knit.uncertainty_mm is not None
    assert knit.uncertainty_mm > woven.uncertainty_mm
    assert "Jersey stretch varies" in text(knit)
    assert "Jersey" not in text(woven)


def test_jersey_label_may_span_bands_where_woven_does_not() -> None:
    woven = fit(flat=540, garment_type="woven_shirt")  # ease 140, +-20 stays regular
    knit = fit(flat=540, garment_type="jersey_tee")  # ease 140, +-60 spans bands
    assert "neighbouring band" not in text(woven)
    assert "neighbouring band" in text(knit)


# --- flat width vs circumference


def test_flat_width_is_doubled_into_circumference() -> None:
    a = fit(flat=520, body=940)
    assert a.estimated_finished_mm == {"chest_circumference": 1040.0}
    assert a.ease_mm == {"chest_circumference": 100.0}  # not 520 - 940 = -420


def test_circumference_entered_as_flat_width_is_rejected() -> None:
    a = fit(flat=1040)
    assert a.fit_label is FitLabel.UNKNOWN
    assert a.estimated_finished_mm == {}
    assert "looks like a circumference" in text(a)


def test_flat_width_entered_as_circumference_is_rejected() -> None:
    a = assess_fit(
        body_profile_id="bp",
        revision_id="r",
        recipe_id=RECIPE,
        garment_type="woven_shirt",
        garment={"chest_circumference": m(520)},
        body={"chest_circumference": m(940)},
    )
    assert a.fit_label is FitLabel.UNKNOWN
    assert "looks like a flat width" in text(a)


def test_garment_circumference_alone_is_used_as_is() -> None:
    d = finished_dimensions({"chest_circumference": m(1040)})
    assert d.chest_circumference_mm == 1040.0


def test_consistent_flat_and_circumference_use_doubled_flat() -> None:
    d = finished_dimensions({"chest_flat_width": m(520), "chest_circumference": m(1060)})
    assert d.chest_circumference_mm == 1040.0


def test_conflicting_flat_and_circumference_is_unknown() -> None:
    a = fit(flat=520, extra_garment={"chest_circumference": m(1300)})
    assert a.fit_label is FitLabel.UNKNOWN
    assert "disagree" in text(a)


def test_body_half_measure_is_rejected() -> None:
    a = fit(flat=520, body=470)
    assert a.fit_label is FitLabel.UNKNOWN
    assert "half a circumference" in text(a)
    assert a.estimated_finished_mm == {"chest_circumference": 1040.0}  # garment side still shown


# --- mm / cm mistakes


@pytest.mark.parametrize("flat", [52.0, 5200.0])
def test_garment_unit_error(flat: float) -> None:
    a = fit(flat=flat)
    assert a.fit_label is FitLabel.UNKNOWN
    assert "wrong unit" in text(a)


@pytest.mark.parametrize("body", [94.0, 9400.0])
def test_body_unit_error(body: float) -> None:
    a = fit(body=body)
    assert a.fit_label is FitLabel.UNKNOWN
    assert "wrong unit" in text(a)


def test_implausible_values_are_unknown() -> None:
    assert fit(flat=150).fit_label is FitLabel.UNKNOWN
    assert "outside the plausible range" in text(fit(flat=150))
    assert "outside the plausible range" in text(fit(body=2500))


def test_cm_values_are_not_silently_converted() -> None:
    # Someone passes the cm number (94) as if mm: it must never produce an ease figure.
    a = fit(body=94.0)
    assert a.ease_mm == {}


# --- missing / unconfirmed / unsupported


def test_missing_body_still_shows_finished_but_no_ease() -> None:
    a = fit(body=None)
    assert a.fit_label is FitLabel.UNKNOWN
    assert a.ease_mm == {}
    assert a.estimated_finished_mm == {"chest_circumference": 1080.0}
    assert "Body chest circumference is needed" in text(a)


def test_missing_garment_width_is_unknown() -> None:
    a = fit(flat=None)
    assert a.fit_label is FitLabel.UNKNOWN
    assert "Garment chest width is needed" in text(a)


def test_unconfirmed_garment_measurement_is_missing() -> None:
    a = fit(flat_confirmed=False)
    assert a.fit_label is FitLabel.UNKNOWN
    assert "not confirmed" in text(a)


def test_unconfirmed_body_measurement_is_missing() -> None:
    a = fit(body_confirmed=False)
    assert a.fit_label is FitLabel.UNKNOWN
    assert "not confirmed" in text(a)


def test_unknown_recipe_fails_closed() -> None:
    a = fit(recipe="made_up_recipe_v9")
    assert a.fit_label is FitLabel.UNKNOWN
    assert a.estimated_finished_mm == {}


@pytest.mark.parametrize("garment_type", [None, "other", "unknown", "dress"])
def test_unsupported_garment_type_is_unknown(garment_type: str | None) -> None:
    a = fit(garment_type=garment_type)
    assert a.fit_label is FitLabel.UNKNOWN
    assert "No ease range for this garment type" in text(a)


# --- wording: provisional, no guarantee


def test_provisional_warning_while_config_unapproved() -> None:
    a = fit()
    assert a.ease_config_provisional
    assert "provisional" in text(a)


def test_approved_config_drops_provisional_warning() -> None:
    raw = cast("dict[str, Any]", json.loads(_config_text()))
    raw["status"] = "approved"
    raw["approved_by"] = "Narthananilaa"
    a = fit(config=parse_config(raw))
    assert not a.ease_config_provisional
    assert "provisional" not in text(a).replace("provisional minimum", "")


def _config_text() -> str:
    path = Path(__file__).parents[1] / "src" / "sewsure_feasibility" / "fit" / "ease_ranges.json"
    return path.read_text("utf-8")


@pytest.mark.parametrize("flat", [450, 480, 500, 520, 540, 580, 650])
@pytest.mark.parametrize("garment_type", ["woven_shirt", "jersey_tee"])
def test_no_guarantee_language(flat: int, garment_type: str) -> None:
    a = fit(flat=float(flat), garment_type=garment_type)
    blob = text(a).lower()
    for banned in ("perfect", "will fit", "100%", "precision", "safe to cut", "comfortable"):
        assert banned not in blob
    assert "not guaranteed" in blob
    assert "guaranteed" not in blob.replace("not guaranteed", "")


def test_all_warnings_fit_contract_length() -> None:
    for flat in (450, 520, 540, 650, 1040, 52):
        for gt in ("woven_shirt", "jersey_tee"):
            for w in fit(flat=float(flat), garment_type=gt).warnings:
                assert len(w) <= MAX_WARNING_CHARS


# --- contract shape


def test_contract_dict_matches_schema_fields() -> None:
    schema = json.loads(SCHEMA.read_text("utf-8"))
    d = fit(flat=520).to_contract_dict()
    assert set(d) == set(schema["required"]) == set(schema["properties"])
    assert d["fit_label"] in schema["properties"]["fit_label"]["enum"]
    assert all(
        len(w) <= schema["properties"]["warnings"]["items"]["maxLength"] for w in d["warnings"]
    )
    for key in ("measurements_mm", "estimated_finished_mm", "ease_mm"):
        assert all(isinstance(v, float) for v in d[key].values())
    assert d["body_profile_id"] == "bp-1"
    assert d["revision_id"] == "rev-002"


def test_every_label_is_in_the_contract_enum() -> None:
    schema = json.loads(SCHEMA.read_text("utf-8"))
    assert {lbl.value for lbl in FitLabel} == set(schema["properties"]["fit_label"]["enum"])


def test_new_revision_id_is_carried_through() -> None:
    a = fit()
    b = assess_fit(
        body_profile_id="bp-1",
        revision_id="rev-003",
        recipe_id=RECIPE,
        garment_type="woven_shirt",
        garment={"chest_flat_width": m(540)},
        body={"chest_circumference": m(940)},
    )
    assert (a.revision_id, b.revision_id) == ("rev-002", "rev-003")
    assert a.ease_mm == b.ease_mm


# --- config


def test_every_config_value_has_a_source_and_is_unchecked() -> None:
    cfg = load_config()
    assert cfg.provisional
    assert cfg.approved_by is None
    for p in cfg.profiles.values():
        for v in (
            p.uncertainty,
            p.insufficient_below,
            p.close_below,
            p.regular_below,
            p.relaxed_below,
        ):
            assert v.source.strip()
            assert v.source_checked is False


def test_jersey_uncertainty_is_wider_than_woven_in_config() -> None:
    cfg = load_config()
    assert cfg.profiles["knit"].uncertainty.value_mm > cfg.profiles["woven"].uncertainty.value_mm


def test_config_rejects_missing_source() -> None:
    raw = cast("dict[str, Any]", json.loads(_config_text()))
    raw["profiles"]["woven"]["bands"]["close_below_mm"]["source"] = " "
    with pytest.raises(ValueError, match="source"):
        parse_config(raw)


def test_config_rejects_non_increasing_bands() -> None:
    raw = cast("dict[str, Any]", json.loads(_config_text()))
    broken = copy.deepcopy(raw)
    broken["profiles"]["woven"]["bands"]["close_below_mm"]["value"] = 10
    with pytest.raises(ValueError, match="increasing"):
        parse_config(broken)


# --- properties


@given(
    flat=st.floats(min_value=300, max_value=800),
    body=st.floats(min_value=600, max_value=1700),
)
def test_ease_is_finished_circumference_minus_body(flat: float, body: float) -> None:
    a = fit(flat=flat, body=body)
    assert a.fit_label is not FitLabel.UNKNOWN
    assert a.ease_mm["chest_circumference"] == pytest.approx(2 * flat - body, abs=0.11)


@given(
    lo=st.floats(min_value=300, max_value=800),
    hi=st.floats(min_value=300, max_value=800),
)
def test_label_never_gets_looser_as_ease_shrinks(lo: float, hi: float) -> None:
    order = [
        FitLabel.INSUFFICIENT_EASE,
        FitLabel.CLOSE,
        FitLabel.REGULAR,
        FitLabel.RELAXED,
        FitLabel.OVERSIZED,
    ]
    small, big = sorted((lo, hi))
    a, b = fit(flat=small), fit(flat=big)
    assert order.index(a.fit_label) <= order.index(b.fit_label)
