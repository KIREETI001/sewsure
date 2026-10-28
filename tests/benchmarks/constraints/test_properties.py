"""Hypothesis properties: cm/mm equivalence and boundary values (blueprint 5.5)."""
import copy

import pytest
from hypothesis import given, settings, strategies as st

import adapter
import cases as C

SS01 = next(c for c in C.load_cases() if c["id"] == "SS-01")["inputs"]

# Lengths in tenths of a mm, so cm values are exact decimals (no float noise)
tenths = st.integers(min_value=1, max_value=20000)


@given(tenths)
def test_to_mm_cm_and_mm_agree(t):
    mm = t / 10
    cm = t / 100
    assert adapter.to_mm(cm, "cm") == adapter.to_mm(mm, "mm")


@given(st.integers(min_value=-10**6, max_value=10**6))
def test_to_mm_is_linear_and_roundtrips(n):
    assert adapter.to_mm(n, "cm") == 10 * n
    assert adapter.to_mm(n, "m") == 1000 * n


def test_to_mm_rejects_unknown_unit():
    with pytest.raises(ValueError):
        adapter.to_mm(5, "inch")


def _with(length_mm, finished_mm, hem_mm=30):
    i = copy.deepcopy(SS01)
    i["measurements"]["shoulder_to_hem"]["value_mm"] = length_mm
    i["params"]["finished_length_mm"] = finished_mm
    i["params"]["hem_allowance_mm"] = hem_mm
    return i


# --- engine-backed properties -------------------------------------------------

# Inside the engine's plausible ranges (shoulder_to_hem 250-1100 mm, hem 5-80 mm, finished >= 150 mm)
lengths = st.integers(min_value=400, max_value=1100)
hems = st.integers(min_value=10, max_value=60)


@settings(max_examples=100, deadline=None)
@given(length=lengths, hem=hems, extra_hundredths=st.integers(min_value=0, max_value=99))
def test_cm_and_mm_inputs_give_same_result(length, hem, extra_hundredths, engine):
    finished = length - hem - 100 - extra_hundredths / 100  # comfortably inside the garment
    mm_in = _with(length, finished, hem)
    cm_in = copy.deepcopy(mm_in)
    cm_in["measurements"]["shoulder_to_hem"] = {
        "value": length / 10, "unit": "cm", "origin": "tape_measure_user", "confirmed_at": "2026-01-01T00:00:00Z"}
    a, b = engine(mm_in), engine(cm_in)
    assert (a.status, a.failure_codes) == (b.status, b.failure_codes)


@settings(max_examples=100, deadline=None)
@given(length=lengths, hem=hems)
def test_exact_fit_has_no_positive_remainder_and_fails(length, hem, engine):
    out = engine(_with(length, length - hem, hem))
    assert out.status == "FAILED_CHECKS", "zero remainder must not pass (blueprint 5.3)"
    assert out.failure_codes == ["INSUFFICIENT_LENGTH"]


@settings(max_examples=200, deadline=None)
@given(length=lengths, hem=hems, over_hundredths=st.integers(min_value=1, max_value=99))
def test_overshoot_under_1mm_never_passes(length, hem, over_hundredths, engine):
    out = engine(_with(length, length - hem + over_hundredths / 100, hem))
    assert out.status != adapter.PASS, f"false acceptance at {over_hundredths / 100} mm overshoot"
    assert out.failure_codes == ["INSUFFICIENT_LENGTH"]


@settings(max_examples=100, deadline=None)
@given(length=lengths, hem=hems, under_hundredths=st.integers(min_value=1, max_value=99))
def test_remainder_under_1mm_but_positive_passes(length, hem, under_hundredths, engine):
    out = engine(_with(length, length - hem - under_hundredths / 100, hem))
    assert out.status == adapter.PASS
