"""P0 path over HTTP with the real feasibility engine and the contract's fixtures."""

from typing import Any

from fastapi.testclient import TestClient

from tests.conftest import ALICE, idem, scenario


def _designs(client: TestClient, project_id: str) -> dict[str, Any]:
    r = client.get(f"/v1/projects/{project_id}/designs", headers=ALICE)
    assert r.status_code == 200, r.text
    return r.json()


def _revision(client: TestClient, revision_id: str) -> dict[str, Any]:
    return client.get(f"/v1/revisions/{revision_id}", headers=ALICE).json()


def _cut_plan_status(client: TestClient, revision_id: str) -> int:
    return client.get(f"/v1/revisions/{revision_id}/cut-plan", headers=ALICE).status_code


def test_feasible_crop_passes_with_dimensioned_cut_plan(client: TestClient) -> None:
    ctx = scenario(client, "woven_shirt_crop_pass")
    job = client.get(f"/v1/jobs/{ctx['job']['job_id']}", headers=ALICE).json()
    assert job["state"] == "complete"
    assert job["result"]["outcome"] == "designs"
    designs = _designs(client, ctx["project_id"])["designs"]
    assert len(designs) == 1
    assert designs[0]["status"] == "PASS_SUPPORTED_CHECKS"
    rev = _revision(client, designs[0]["current_revision_id"])
    assert rev["status"] == "PASS_SUPPORTED_CHECKS"
    assert rev["checks"]["hard_pass"] is True
    assert rev["geometry_mm"]["cut_mark_from_shoulder_mm"] == 530
    assert rev["cut_plan_id"]
    plan = client.get(f"/v1/revisions/{rev['revision_id']}/cut-plan", headers=ALICE)
    assert plan.status_code == 200
    body = plan.json()
    assert body["mode"] == "dimensioned_diagram"
    assert body["calibration"]["state"] == "none"
    cut = body["pieces"][0]["lines"][0]
    assert cut["kind"] == "cut"
    assert cut["points_mm"][0][1] == 530


def test_impossible_lengthening_fails_without_cut_plan(client: TestClient) -> None:
    ctx = scenario(client, "lengthening_impossible")
    job = client.get(f"/v1/jobs/{ctx['job']['job_id']}", headers=ALICE).json()
    assert job["result"]["outcome"] == "no_feasible_design"
    listing = _designs(client, ctx["project_id"])
    d = listing["designs"][0]
    assert d["status"] == "FAILED_CHECKS"
    assert "INSUFFICIENT_LENGTH" in d["failure_codes"]
    assert listing["binding_constraint"]["hard_pass"] is False
    rev = _revision(client, d["current_revision_id"])
    assert rev["checks"]["residuals"][0]["residual_mm"] < 0
    assert rev["cut_plan_id"] is None
    r = client.get(f"/v1/revisions/{rev['revision_id']}/cut-plan", headers=ALICE)
    assert r.status_code == 409
    assert r.json()["code"] == "REVISION_NOT_PASSING"


def test_unconfirmed_measurement_needs_input_without_cut_plan(client: TestClient) -> None:
    ctx = scenario(client, "needs_input")
    issues = ctx["measurements"]["issues"]
    assert any(
        i["dimension"] == "shoulder_to_hem" and i["code"] == "UNCONFIRMED_DIMENSION" for i in issues
    )
    assert "shoulder_to_hem" in ctx["measurements"]["missing_dimensions"]
    d = _designs(client, ctx["project_id"])["designs"][0]
    assert d["status"] == "NEEDS_INPUT"
    assert "shoulder_to_hem" in d["missing_dimensions"]
    rev = _revision(client, d["current_revision_id"])
    assert rev["cut_plan_id"] is None
    assert rev["geometry_mm"] == {}
    assert _cut_plan_status(client, rev["revision_id"]) == 409


def test_unsupported_garment_is_idea_only_without_cut_plan(client: TestClient) -> None:
    ctx = scenario(client, "idea_only")
    job = client.get(f"/v1/jobs/{ctx['job']['job_id']}", headers=ALICE).json()
    assert job["result"]["outcome"] == "unsupported"
    d = _designs(client, ctx["project_id"])["designs"][0]
    assert d["status"] == "IDEA_ONLY"
    rev = _revision(client, d["current_revision_id"])
    assert rev["recipe_id"] is None
    assert rev["cut_plan_id"] is None
    assert _cut_plan_status(client, rev["revision_id"]) == 409


def test_edit_creates_new_revision_and_supersedes_passed_parent(client: TestClient) -> None:
    ctx = scenario(client, "woven_shirt_crop_pass")
    d = _designs(client, ctx["project_id"])["designs"][0]
    parent = d["current_revision_id"]
    r = client.post(
        f"/v1/designs/{d['design_id']}/revisions",
        json={"parent_revision_id": parent, "parameters": {"finished_length_mm": 450}},
        headers={**ALICE, **idem("edit")},
    )
    assert r.status_code == 201, r.text
    new = r.json()
    assert new["parent_revision_id"] == parent
    assert new["revision_number"] == 2
    assert new["parameters"]["finished_length_mm"] == 450
    old = _revision(client, parent)
    assert old["status"] == "SUPERSEDED"
    assert old["superseded_by_revision_id"] == new["revision_id"]
    assert old["parameters"]["finished_length_mm"] == 500
    again = client.post(
        f"/v1/designs/{d['design_id']}/revisions",
        json={"parent_revision_id": parent, "parameters": {"finished_length_mm": 400}},
        headers={**ALICE, **idem("edit2")},
    )
    assert again.status_code == 409


def test_edit_keeps_failed_parent_verdict(client: TestClient) -> None:
    ctx = scenario(client, "lengthening_impossible")
    d = _designs(client, ctx["project_id"])["designs"][0]
    parent = d["current_revision_id"]
    r = client.post(
        f"/v1/designs/{d['design_id']}/revisions",
        json={"parent_revision_id": parent, "parameters": {"finished_length_mm": 500}},
        headers={**ALICE, **idem("fix")},
    )
    assert r.json()["status"] == "PASS_SUPPORTED_CHECKS"
    old = _revision(client, parent)
    assert old["status"] == "FAILED_CHECKS"
    assert old["superseded_by_revision_id"] == r.json()["revision_id"]


def test_geometry_and_unknown_parameters_rejected(client: TestClient) -> None:
    ctx = scenario(client, "woven_shirt_crop_pass")
    d = _designs(client, ctx["project_id"])["designs"][0]
    for params in ({"cut_line_points_mm": [[0, 1]]}, {"length": 50}, {"sleeve_length_mm": 100}):
        r = client.post(
            f"/v1/designs/{d['design_id']}/revisions",
            json={"parent_revision_id": d["current_revision_id"], "parameters": params},
            headers={**ALICE, **idem("bad")},
        )
        assert r.status_code == 422, (params, r.text)


def test_generate_requires_measurements_and_project_create_is_idempotent(
    client: TestClient,
) -> None:
    pid = client.post("/v1/projects", json={}, headers={**ALICE, **idem("p")}).json()["project_id"]
    body = {"inspiration": {"text": "x", "skill_level": "beginner", "tools": ["ruler"]}}
    r = client.post(f"/v1/projects/{pid}/generate", json=body, headers={**ALICE, **idem("g")})
    assert r.status_code == 409
    assert r.json()["code"] == "MEASUREMENTS_REQUIRED"
    replay = client.post("/v1/projects", json={}, headers={**ALICE, **idem("p")})
    assert replay.status_code == 200
    assert replay.headers["Idempotent-Replayed"] == "true"
    assert client.post("/v1/projects", json={}, headers=ALICE).status_code == 422
