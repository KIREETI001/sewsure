"""Wrong-user access pattern.

Every route is listed in ROUTES with a request that works against resources owned by ALICE.
The test calls it as BOB and expects 404 (never 403, so existence is not leaked), and as an
anonymous caller expecting 401. `test_every_route_is_covered` fails when a route is added
without an entry, which is how "a wrong-user test per route" is enforced.

Placeholders {project_id}, {garment_id}, {revision_id}, {design_id} and {job_id} are filled from
a completed crop scenario.
"""

import json
from typing import Any

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from tests.conftest import ALICE, BOB, idem, scenario

INSP = {"inspiration": {"text": "x", "skill_level": "beginner", "tools": ["ruler"]}}
MEAS = {
    "units": "mm",
    "garment": {
        "shoulder_to_hem": {
            "value_mm": 780,
            "origin": "user_tape_measured",
            "confirmed_at": "2026-10-28T09:00:00Z",
        }
    },
}

ROUTES: list[tuple[str, str, dict[str, Any] | None]] = [
    ("GET", "/v1/projects/{project_id}", None),
    ("GET", "/v1/garments/{garment_id}", None),
    ("PUT", "/v1/projects/{project_id}/measurements", MEAS),
    ("POST", "/v1/projects/{project_id}/generate", INSP),
    ("GET", "/v1/jobs/{job_id}", None),
    ("GET", "/v1/projects/{project_id}/designs", None),
    (
        "POST",
        "/v1/designs/{design_id}/revisions",
        {"parent_revision_id": "{revision_id}", "parameters": {"finished_length_mm": 450}},
    ),
    ("GET", "/v1/revisions/{revision_id}", None),
    ("GET", "/v1/revisions/{revision_id}/cut-plan", None),
]
NO_OWNER_ROUTES = {("POST", "/v1/projects"), ("GET", "/healthz")}


@pytest.fixture
def ids(client: TestClient) -> dict[str, str]:
    ctx = scenario(client, "woven_shirt_crop_pass")
    pid = ctx["project_id"]
    d = client.get(f"/v1/projects/{pid}/designs", headers=ALICE).json()["designs"][0]
    garment_id = client.get(f"/v1/projects/{pid}", headers=ALICE).json()["garment_id"]
    return {
        "project_id": pid,
        "garment_id": garment_id,
        "job_id": ctx["job"]["job_id"],
        "design_id": d["design_id"],
        "revision_id": d["current_revision_id"],
    }


@pytest.mark.parametrize(("method", "template", "body"), ROUTES)
def test_owner_ok_other_user_404_anonymous_401(
    client: TestClient,
    ids: dict[str, str],
    method: str,
    template: str,
    body: dict[str, Any] | None,
) -> None:
    path = template.format(**ids)
    if body is not None:
        body = json.loads(json.dumps(body).replace("{revision_id}", ids["revision_id"]))
    h = idem("access")
    assert client.request(method, path, json=body, headers={**ALICE, **h}).status_code < 300
    assert client.request(method, path, json=body, headers={**BOB, **h}).status_code == 404
    assert client.request(method, path, json=body, headers=h).status_code == 401


def test_every_route_is_covered(client: TestClient) -> None:
    covered = {(m, t) for m, t, _ in ROUTES} | NO_OWNER_ROUTES
    actual = {
        (method, route.path)
        for route in client.app.routes  # type: ignore[attr-defined]
        if isinstance(route, APIRoute)
        for method in route.methods or ()
    }
    assert actual <= covered, f"routes without a wrong-user test: {sorted(actual - covered)}"


def test_project_creation_requires_auth(client: TestClient) -> None:
    assert client.post("/v1/projects", json={}, headers=idem("p")).status_code == 401
