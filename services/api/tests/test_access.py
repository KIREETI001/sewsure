"""Wrong-user access pattern.

Every route is listed in ROUTES with a request that works against a resource owned by ALICE.
The test calls it as BOB and expects 404 (never 403, so existence is not leaked), and as an
anonymous caller expecting 401. `test_every_route_is_covered` fails when a route is added
without an entry, which is how "a wrong-user test per route" is enforced.

To add a route: append a (method, path_template, json_body) entry. The placeholders
{project_id}, {revision_id} and {job_id} are filled from the fixtures.
"""

import json
from typing import Any

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from tests.conftest import ALICE, BOB, RECIPE

ROUTES: list[tuple[str, str, dict[str, Any] | None]] = [
    ("GET", "/v1/projects/{project_id}", None),
    ("GET", "/v1/projects/{project_id}/designs", None),
    ("POST", "/v1/projects/{project_id}/designs", {"recipe_id": RECIPE, "parameters": {}}),
    ("POST", "/v1/projects/{project_id}/generate", None),
    ("GET", "/v1/revisions/{revision_id}", None),
    (
        "POST",
        "/v1/designs/{design_id}/revisions",
        {"parent_revision_id": "{revision_id}", "parameters": {"hem": "folded"}},
    ),
    ("GET", "/v1/jobs/{job_id}", None),
]
# Routes with no resource ID: nothing to cross-access (project creation is tested for auth below).
NO_OWNER_ROUTES = {("POST", "/v1/projects"), ("GET", "/healthz")}


@pytest.fixture
def ids(project_id: str, revision_id: str, job_id: str, design_id: str) -> dict[str, str]:
    return {
        "project_id": project_id,
        "revision_id": revision_id,
        "job_id": job_id,
        "design_id": design_id,
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
    idem = {"Idempotency-Key": "access-test"}
    assert client.request(method, path, json=body, headers={**ALICE, **idem}).status_code < 300
    assert client.request(method, path, json=body, headers={**BOB, **idem}).status_code == 404
    assert client.request(method, path, json=body, headers=idem).status_code == 401


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
    r = client.post("/v1/projects", json={"name": "x"}, headers={"Idempotency-Key": "k"})
    assert r.status_code == 401
