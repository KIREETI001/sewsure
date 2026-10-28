"""Validate recipe, lesson and rights files under content/recipes.

Run from the repo root:
    python content/recipes/tools/validate_recipes.py
Needs PyYAML and jsonschema (pip install pyyaml jsonschema).

Checks beyond the JSON schemas:
- step ids are unique and every irreversible step (cut or trim) is directly
  preceded by a step with checkpoint: true
- lesson ids referenced by steps and prerequisites exist
- agents may only author status: draft
- no guarantee language (root CLAUDE.md rule 6)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

RECIPES_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = RECIPES_DIR / "schema"

IRREVERSIBLE_PHASES = {"cut", "trim"}

BANNED_PHRASES = [
    "guaranteed",
    "guarantee",
    "perfect fit",
    "precision ar",
    "100% accurate",
    "safe to cut",
]


def _load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _schema(name: str) -> Draft202012Validator:
    with (SCHEMA_DIR / name).open(encoding="utf-8") as fh:
        return Draft202012Validator(json.load(fh))


def _schema_errors(validator: Draft202012Validator, data, label: str) -> list[str]:
    return [
        f"{label}: {'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    ]


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


def check_language(data, label: str) -> list[str]:
    errors = []
    for text in _strings(data):
        low = text.lower()
        for phrase in BANNED_PHRASES:
            if phrase in low:
                errors.append(f"{label}: banned phrase {phrase!r} in: {text[:60]!r}")
    return errors


def check_recipe_rules(recipe: dict, lesson_ids: set[str], label: str) -> list[str]:
    errors = []
    if recipe.get("status") != "draft":
        errors.append(f"{label}: agents may only author status: draft")

    steps = recipe.get("steps", [])
    seen: set[str] = set()
    for i, step in enumerate(steps):
        sid = step.get("id")
        if sid in seen:
            errors.append(f"{label}: duplicate step id {sid!r}")
        seen.add(sid)
        if step.get("phase") in IRREVERSIBLE_PHASES and not step.get("irreversible"):
            errors.append(f"{label}: step {sid!r} is in phase {step['phase']!r} so it must have irreversible: true")
        if step.get("irreversible") or step.get("phase") in IRREVERSIBLE_PHASES:
            prev = steps[i - 1] if i > 0 else None
            if not prev or not prev.get("checkpoint"):
                errors.append(f"{label}: irreversible step {sid!r} is not directly preceded by a checkpoint step")
        if step.get("phase") == "checkpoint" and not step.get("checkpoint"):
            errors.append(f"{label}: step {sid!r} has phase checkpoint but checkpoint is false")
        for lid in step.get("lesson_ids", []):
            if lid not in lesson_ids:
                errors.append(f"{label}: step {sid!r} references unknown lesson {lid!r}")

    if not any(s.get("irreversible") for s in steps):
        errors.append(f"{label}: no irreversible (cut) step found; check the recipe")

    for pre in recipe.get("skill_prerequisites", []):
        lid = pre.get("lesson_id")
        if lid and lid not in lesson_ids:
            errors.append(f"{label}: prerequisite references unknown lesson {lid!r}")

    groups: dict[str, list[dict]] = {}
    for step in steps:
        if "option_group" in step:
            groups.setdefault(step["option_group"], []).append(step)
    for name, members in groups.items():
        if len(members) < 2:
            errors.append(f"{label}: option group {name!r} has fewer than two options")

    step_ids = seen
    for tool in recipe.get("required_tools", []) + recipe.get("optional_tools", []):
        needed = tool.get("needed_for")
        if needed and needed not in step_ids:
            errors.append(f"{label}: tool {tool['id']!r} needed_for unknown step {needed!r}")
    return errors


def validate_all(root: Path = RECIPES_DIR) -> list[str]:
    recipe_v = _schema("recipe.schema.json")
    lesson_v = _schema("lesson.schema.json")
    rights_v = _schema("rights.schema.json")
    errors: list[str] = []

    lessons: dict[str, dict] = {}
    for path in sorted((root / "lessons").glob("*.yaml")):
        label = str(path.relative_to(root))
        data = _load_yaml(path)
        errors += _schema_errors(lesson_v, data, label)
        errors += check_language(data, label)
        if isinstance(data, dict):
            if data.get("status") != "draft":
                errors.append(f"{label}: agents may only author status: draft")
            lessons[data.get("lesson_id", path.stem)] = data
    n_lessons = len(lessons)
    if not 4 <= n_lessons <= 6:
        errors.append(f"lessons: expected 4 to 6 micro-lessons, found {n_lessons}")

    recipe_ids: set[str] = set()
    for recipe_path in sorted(root.glob("*/recipe.yaml")):
        folder = recipe_path.parent
        label = str(recipe_path.relative_to(root))
        recipe = _load_yaml(recipe_path)
        errors += _schema_errors(recipe_v, recipe, label)
        errors += check_language(recipe, label)
        if isinstance(recipe, dict):
            if recipe.get("recipe_id") != folder.name:
                errors.append(f"{label}: recipe_id does not match folder name {folder.name!r}")
            recipe_ids.add(recipe.get("recipe_id"))
            errors += check_recipe_rules(recipe, set(lessons), label)

        rights_path = folder / "rights.yaml"
        if not rights_path.exists():
            errors.append(f"{folder.name}: rights.yaml is missing")
        else:
            rights = _load_yaml(rights_path)
            rlabel = str(rights_path.relative_to(root))
            errors += _schema_errors(rights_v, rights, rlabel)
            if isinstance(rights, dict):
                if rights.get("third_party_media_used") and not rights.get("media"):
                    errors.append(f"{rlabel}: third_party_media_used is true but media is empty")
                if re.search(r"\.(png|jpe?g|gif|mp4|webp|svg)\b", recipe_path.read_text(encoding="utf-8"), re.I) \
                        and not rights.get("media"):
                    errors.append(f"{label}: media referenced but rights.yaml lists none")

    for lid, lesson in lessons.items():
        for rid in lesson.get("used_by_recipes", []):
            if rid not in recipe_ids:
                errors.append(f"lesson {lid}: used_by_recipes names unknown recipe {rid!r}")
    return errors


def main() -> int:
    errors = validate_all()
    if errors:
        print("FAILED")
        for e in errors:
            print(" -", e)
        return 1
    print("OK: all recipes, lessons and rights files are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
