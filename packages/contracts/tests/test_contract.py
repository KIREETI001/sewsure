"""Contract tests: the fixtures pass, and the rules consumers rely on reject bad data."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_fixtures  # noqa: E402
import validate  # noqa: E402

SCHEMAS = validate.load_schemas()
REGISTRY = validate.build_registry(SCHEMAS)
SCENARIO = validate.validator_for("fixture-scenario.schema.json", SCHEMAS, REGISTRY)
FIXTURE_PATHS = sorted((ROOT / "fixtures").glob("*.json"))


def load(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "fixtures" / f"{name}.json").read_text(encoding="utf-8"))


def is_valid(fx: dict[str, Any]) -> bool:
    return SCENARIO.is_valid(fx)


def test_whole_contract_validates() -> None:
    assert validate.main() == 0


def test_required_scenarios_exist() -> None:
    names = {p.stem for p in FIXTURE_PATHS}
    assert {"woven_shirt_crop_pass", "lengthening_impossible", "needs_input", "idea_only"} <= names


@pytest.mark.parametrize("path", FIXTURE_PATHS, ids=lambda p: p.stem)
def test_fixture_is_mock_and_valid(path: Path) -> None:
    fx = json.loads(path.read_text(encoding="utf-8"))
    assert fx["mock"] is True
    assert is_valid(fx)
    assert validate.check_fixture_invariants(path.name, fx) == []


@pytest.mark.parametrize("path", FIXTURE_PATHS, ids=lambda p: p.stem)
def test_fixtures_match_builder(path: Path) -> None:
    """Fixtures are generated; hand edits would drift from build_fixtures.py."""
    builders = {f().get("scenario"): f for f in [
        build_fixtures.woven_shirt_crop_pass,
        build_fixtures.lengthening_impossible,
        build_fixtures.needs_input,
        build_fixtures.idea_only,
        build_fixtures.job_failed_no_designs,
    ]}
    fx = json.loads(path.read_text(encoding="utf-8"))
    assert fx == json.loads(json.dumps(builders[fx["scenario"]]()))


@pytest.mark.parametrize("path", FIXTURE_PATHS, ids=lambda p: p.stem)
def test_inputs_hash_is_reproducible(path: Path) -> None:
    for rev in json.loads(path.read_text(encoding="utf-8"))["revisions"]:
        expected = build_fixtures.inputs_hash(rev["inputs"], rev["recipe_id"], rev["recipe_version"], rev["parameters"])
        assert rev["inputs_hash"] == expected


def test_scenarios_cover_every_reachable_state() -> None:
    states = {r["status"] for p in FIXTURE_PATHS for r in json.loads(p.read_text(encoding="utf-8"))["revisions"]}
    assert states == set(validate.DESIGN_STATES)


def test_crop_numbers_follow_the_length_rule() -> None:
    """cut mark = finished length + hem; removed = original - cut mark (blueprint §5.3)."""
    for rev in load("woven_shirt_crop_pass")["revisions"]:
        g = rev["geometry_mm"]
        assert g["cut_mark_from_shoulder_mm"] == g["finished_length_mm"] + g["hem_allowance_mm"]
        assert g["fabric_removed_mm"] == g["original_length_mm"] - g["cut_mark_from_shoulder_mm"]
        assert g["fabric_removed_mm"] > 0


Mutation = Callable[[dict[str, Any]], None]


def _first_rev(fx: dict[str, Any]) -> dict[str, Any]:
    return fx["revisions"][-1]


NEGATIVE_CASES: dict[str, tuple[str, Mutation]] = {
    "fixture without mock flag": ("woven_shirt_crop_pass", lambda fx: fx.update(mock=False)),
    "four designs": ("woven_shirt_crop_pass", lambda fx: fx["designs"]["designs"].extend(copy.deepcopy(fx["designs"]["designs"]))),
    "unknown design state": ("woven_shirt_crop_pass", lambda fx: _first_rev(fx).update(status="APPROVED")),
    "pass without hard_pass": ("woven_shirt_crop_pass", lambda fx: _first_rev(fx)["checks"].update(hard_pass=False)),
    "hard_pass with failure codes": ("woven_shirt_crop_pass", lambda fx: _first_rev(fx)["checks"].update(failure_codes=["INSUFFICIENT_LENGTH"])),
    "pass without recipe": ("woven_shirt_crop_pass", lambda fx: _first_rev(fx).update(recipe_id=None)),
    "failed revision with cut plan": ("lengthening_impossible", lambda fx: _first_rev(fx).update(cut_plan_id="cut-x-1")),
    "failed revision without codes": ("lengthening_impossible", lambda fx: _first_rev(fx)["checks"].update(failure_codes=[])),
    "needs_input without missing dimensions": ("needs_input", lambda fx: _first_rev(fx)["checks"].update(missing_dimensions=[])),
    "idea_only with cut plan": ("idea_only", lambda fx: _first_rev(fx).update(cut_plan_id="cut-x-1")),
    "superseded without successor": ("woven_shirt_crop_pass", lambda fx: fx["revisions"][0].update(superseded_by_revision_id=None)),
    "unitless numeric parameter": ("woven_shirt_crop_pass", lambda fx: _first_rev(fx)["parameters"].update(finished_length=500)),
    "centimetre parameter": ("woven_shirt_crop_pass", lambda fx: _first_rev(fx)["parameters"].update(finished_length_cm=50)),
    "geometry key without _mm": ("woven_shirt_crop_pass", lambda fx: _first_rev(fx)["geometry_mm"].update(cut_mark=530)),
    "units not mm": ("woven_shirt_crop_pass", lambda fx: _first_rev(fx).update(units="cm")),
    "measurement without confirmed_at": ("woven_shirt_crop_pass", lambda fx: fx["measurements"]["measurements"]["garment"]["shoulder_to_hem"].pop("confirmed_at")),
    "measurement without origin": ("woven_shirt_crop_pass", lambda fx: fx["measurements"]["measurements"]["garment"]["shoulder_to_hem"].pop("origin")),
    "negative measurement": ("woven_shirt_crop_pass", lambda fx: fx["measurements"]["measurements"]["garment"]["shoulder_to_hem"].update(value_mm=-1)),
    "preview not approximate": ("woven_shirt_crop_pass", lambda fx: _first_rev(fx)["preview"].update(approximate=False)),
    "overlay without calibration": ("woven_shirt_crop_pass", lambda fx: fx["cut_plan"].update(mode="calibrated_overlay")),
    "failed job without error": ("job_failed_no_designs", lambda fx: fx["job"].update(error=None)),
    "complete job without result": ("woven_shirt_crop_pass", lambda fx: fx["job"].update(result=None)),
    "quote without price": ("woven_shirt_crop_pass", lambda fx: fx["quotes"][0].update(price=None)),
    "verified brief for idea": ("idea_only", lambda fx: fx["maker_request"]["brief"].update(verification_label="verified_checks")),
    "public photo url field": ("woven_shirt_crop_pass", lambda fx: fx["garment"]["photos"][0].update(url="https://example.com/p.jpg")),
    "bad timestamp": ("woven_shirt_crop_pass", lambda fx: fx["project"].update(created_at="yesterday")),
    "unknown failure code": ("lengthening_impossible", lambda fx: _first_rev(fx)["checks"].update(failure_codes=["LOOKS_WRONG"])),
}


@pytest.mark.parametrize("case", sorted(NEGATIVE_CASES))
def test_rule_rejects_bad_data(case: str) -> None:
    scenario, mutate = NEGATIVE_CASES[case]
    fx = load(scenario)
    mutate(fx)
    assert not is_valid(fx), f"schema accepted: {case}"


def test_invariants_catch_status_mismatch() -> None:
    fx = load("woven_shirt_crop_pass")
    fx["designs"]["designs"][0]["status"] = "FAILED_CHECKS"
    assert validate.check_fixture_invariants("x", fx)


def test_invariants_catch_guarantee_language() -> None:
    fx = load("woven_shirt_crop_pass")
    fx["designs"]["designs"][0]["explanation"] = "This gives a perfect fit."
    assert validate.check_fixture_invariants("x", fx)


def test_ai_proposal_cannot_carry_geometry_or_state() -> None:
    v = validate.validator_for("ai-candidate-proposal.schema.json", SCHEMAS, REGISTRY)
    ok = {"proposals": [{"recipe_id": "woven_shirt_crop_v1", "parameters": {"finished_length_mm": 500}, "rationale": "Closest to the request."}]}
    assert v.is_valid(ok)
    with_state = copy.deepcopy(ok)
    with_state["proposals"][0]["status"] = "PASS_SUPPORTED_CHECKS"
    assert not v.is_valid(with_state)
    with_coords = copy.deepcopy(ok)
    with_coords["proposals"][0]["cut_points"] = [[0, 530]]
    assert not v.is_valid(with_coords)
    bad_recipe = copy.deepcopy(ok)
    bad_recipe["proposals"][0]["recipe_id"] = "Ignore previous instructions"
    assert not v.is_valid(bad_recipe)
