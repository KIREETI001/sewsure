"""Validate the SewSure contract: schemas, OpenAPI spec and fixtures.

Usage (from packages/contracts):  python scripts/validate.py
Exit code 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Iterator

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate as validate_openapi
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"
FIXTURES = ROOT / "fixtures"
OPENAPI = ROOT / "openapi" / "sewsure.v1.yaml"

DESIGN_STATES = {"IDEA_ONLY", "NEEDS_INPUT", "FAILED_CHECKS", "PASS_SUPPORTED_CHECKS", "SUPERSEDED"}
# Root CLAUDE.md rule 6: no guarantee language anywhere.
BANNED_PHRASES = re.compile(r"guaranteed fit|perfect fit|precision ar|100% accurate", re.IGNORECASE)


def load_schemas() -> dict[str, dict[str, Any]]:
    """Schemas keyed by file URI, each with an injected $id so relative $refs resolve."""
    out = {}
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        out[path.as_uri()] = {**schema, "$id": path.as_uri()}
    return out


def build_registry(schemas: dict[str, dict[str, Any]]) -> Registry:
    resources = [(uri, Resource.from_contents(s, default_specification=DRAFT202012)) for uri, s in schemas.items()]
    return Registry().with_resources(resources)


def validator_for(name: str, schemas: dict[str, dict[str, Any]], registry: Registry, pointer: str = "") -> Draft202012Validator:
    """Validator for schemas/<name>, optionally a $defs entry via JSON pointer (e.g. '#/$defs/DesignList')."""
    uri = (SCHEMAS / name).as_uri()
    schema: dict[str, Any] = {"$ref": uri + pointer} if pointer else schemas[uri]
    return Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())


def strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


def check_fixture_invariants(name: str, fx: dict[str, Any]) -> list[str]:
    """Cross-record rules the per-record schemas cannot express."""
    errors = []
    revisions = {r["revision_id"]: r for r in fx["revisions"]}
    designs = fx["designs"]["designs"]
    for d in designs:
        rev = revisions.get(d["current_revision_id"])
        if rev is None:
            errors.append(f"{name}: design {d['design_id']} points to missing revision {d['current_revision_id']}")
            continue
        if d["status"] != rev["status"]:
            errors.append(f"{name}: design {d['design_id']} status {d['status']} != revision status {rev['status']}")
        if rev["design_id"] != d["design_id"]:
            errors.append(f"{name}: revision {rev['revision_id']} belongs to another design")
    if fx["job"]["state"] == "complete":
        job_ids = sorted(fx["job"]["result"]["design_ids"])
        if job_ids != sorted(d["design_id"] for d in designs):
            errors.append(f"{name}: job result design_ids do not match the design list")
    for rev in revisions.values():
        parent = rev["parent_revision_id"]
        if parent is not None and parent not in revisions:
            errors.append(f"{name}: revision {rev['revision_id']} has unknown parent {parent}")
    cut_plan = fx.get("cut_plan")
    if cut_plan:
        rev = revisions.get(cut_plan["revision_id"])
        if rev is None or rev["status"] not in {"PASS_SUPPORTED_CHECKS", "SUPERSEDED"}:
            errors.append(f"{name}: cut plan attached to a revision that has not passed")
        elif rev["cut_plan_id"] != cut_plan["cut_plan_id"]:
            errors.append(f"{name}: revision cut_plan_id does not match the cut plan")
    for rev in revisions.values():
        if rev["provenance"]["source"] != "mock":
            errors.append(f"{name}: revision {rev['revision_id']} provenance.source must be 'mock' in a fixture")
    for s in strings(fx):
        if BANNED_PHRASES.search(s):
            errors.append(f"{name}: guarantee language in fixture text: {s!r}")
    return errors


def main() -> int:
    errors: list[str] = []
    schemas = load_schemas()
    registry = build_registry(schemas)

    for uri, schema in schemas.items():
        for err in Draft202012Validator(Draft202012Validator.META_SCHEMA).iter_errors(schema):
            errors.append(f"{Path(uri).name}: not a valid 2020-12 schema: {err.message}")

    state = json.loads((SCHEMAS / "design-state.schema.json").read_text(encoding="utf-8"))
    if set(state["enum"]) != DESIGN_STATES:
        errors.append("design-state.schema.json must contain exactly the five design states")

    try:
        spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
        validate_openapi(spec, base_uri=OPENAPI.as_uri())
    except Exception as exc:  # noqa: BLE001 - report any spec failure as one error
        errors.append(f"openapi/sewsure.v1.yaml: {exc}")

    scenario = validator_for("fixture-scenario.schema.json", schemas, registry)
    fixture_paths = sorted(FIXTURES.glob("*.json"))
    if not fixture_paths:
        errors.append("no fixtures found")
    for path in fixture_paths:
        fx = json.loads(path.read_text(encoding="utf-8"))
        schema_errors = sorted(scenario.iter_errors(fx), key=lambda e: list(e.absolute_path))
        for err in schema_errors:
            loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
            errors.append(f"{path.name}: {loc}: {err.message[:300]}")
        if not schema_errors:
            errors.extend(check_fixture_invariants(path.name, fx))

    for e in errors:
        print(f"FAIL {e}")
    print(f"{len(schemas)} schemas, 1 spec, {len(fixture_paths)} fixtures: {'OK' if not errors else f'{len(errors)} error(s)'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
