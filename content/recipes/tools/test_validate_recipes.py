"""Tests for validate_recipes.py. Run: python -m pytest content/recipes/tools"""

import copy
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import validate_recipes as v  # noqa: E402

RECIPE = v.RECIPES_DIR / "woven_shirt_crop_v1" / "recipe.yaml"
LESSON_IDS = {p.stem for p in (v.RECIPES_DIR / "lessons").glob("*.yaml")}


def load():
    return yaml.safe_load(RECIPE.read_text(encoding="utf-8"))


def schema_errors(recipe):
    return v._schema_errors(v._schema("recipe.schema.json"), recipe, "t")


def test_repo_content_is_valid():
    assert v.validate_all() == []


def test_cut_without_checkpoint_before_is_rejected():
    r = load()
    i = next(n for n, s in enumerate(r["steps"]) if s["id"] == "cut_along_line")
    del r["steps"][i - 1]
    errs = v.check_recipe_rules(r, LESSON_IDS, "t")
    assert any("not directly preceded by a checkpoint" in e for e in errs)


def test_cut_step_must_be_marked_irreversible():
    r = load()
    next(s for s in r["steps"] if s["phase"] == "cut")["irreversible"] = False
    assert schema_errors(r)


def test_draft_cannot_carry_reviewer():
    r = load()
    r["reviewed_by"] = "Someone"
    assert schema_errors(r)


def test_reviewed_status_is_rejected_for_agents():
    r = load()
    r["status"] = "reviewed"
    assert any("only author status: draft" in e for e in v.check_recipe_rules(r, LESSON_IDS, "t"))


def test_unknown_lesson_reference_is_rejected():
    r = load()
    r["steps"][0]["lesson_ids"] = ["lesson_nope"]
    assert any("unknown lesson" in e for e in v.check_recipe_rules(r, LESSON_IDS, "t"))


def test_option_step_needs_sewist_confirmation():
    r = load()
    del next(s for s in r["steps"] if s["id"] == "hem_machine")["sewist_confirmation"]
    assert schema_errors(r)


def test_guarantee_language_is_rejected():
    r = copy.deepcopy(load())
    r["summary"] = "A perfect fit, guaranteed."
    assert v.check_language(r, "t")
