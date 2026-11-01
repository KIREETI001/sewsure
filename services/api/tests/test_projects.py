from fastapi.testclient import TestClient

from tests.conftest import ALICE, BOB, GENERATE_BODY


def test_healthz(client: TestClient) -> None:
    assert client.get("/healthz").json() == {"status": "ok"}


def test_create_requires_idempotency_key(client: TestClient) -> None:
    assert client.post("/v1/projects", json={"name": "a"}, headers=ALICE).status_code == 422


def test_idempotent_replay_returns_same_project(client: TestClient) -> None:
    h = {**ALICE, "Idempotency-Key": "abc"}
    first = client.post("/v1/projects", json={"name": "a"}, headers=h)
    second = client.post("/v1/projects", json={"name": "a"}, headers=h)
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.headers["Idempotent-Replayed"] == "true"
    assert first.json()["id"] == second.json()["id"]


def test_same_key_different_body_conflicts(client: TestClient) -> None:
    h = {**ALICE, "Idempotency-Key": "abc"}
    client.post("/v1/projects", json={"name": "a"}, headers=h)
    assert client.post("/v1/projects", json={"name": "b"}, headers=h).status_code == 409


def test_same_key_other_user_is_independent(client: TestClient) -> None:
    a = client.post("/v1/projects", json={"name": "a"}, headers={**ALICE, "Idempotency-Key": "k"})
    b = client.post("/v1/projects", json={"name": "a"}, headers={**BOB, "Idempotency-Key": "k"})
    assert b.status_code == 201
    assert a.json()["id"] != b.json()["id"]


def test_validation_rejects_empty_name(client: TestClient) -> None:
    r = client.post("/v1/projects", json={"name": ""}, headers={**ALICE, "Idempotency-Key": "k"})
    assert r.status_code == 422


def test_generate_is_idempotent_and_requires_key(client: TestClient, project_id: str) -> None:
    url = f"/v1/projects/{project_id}/generate"
    assert client.post(url, json=GENERATE_BODY, headers=ALICE).status_code == 422
    h = {**ALICE, "Idempotency-Key": "once"}
    first = client.post(url, json=GENERATE_BODY, headers=h)
    second = client.post(url, json=GENERATE_BODY, headers=h)
    assert first.status_code == second.status_code == 202
    assert first.json()["job_id"] == second.json()["job_id"]
    assert second.headers["Idempotent-Replayed"] == "true"
    assert first.json()["kind"] == "generate_designs"
    assert first.json()["state"] == "queued"
    assert first.json()["result"] is None
    other = {"inspiration": {"kind": "other"}}
    assert client.post(url, json=other, headers=h).status_code == 409


def test_empty_design_list_is_valid(client: TestClient, project_id: str) -> None:
    assert client.get(f"/v1/projects/{project_id}/designs", headers=ALICE).json() == []


def test_errors_use_api_error_shape(client: TestClient) -> None:
    r = client.get("/v1/projects/nope", headers=ALICE)
    assert r.status_code == 404
    assert set(r.json()) == {"code", "message", "recoverable"}
    assert r.json()["code"] == "NOT_FOUND"
    v = client.post("/v1/projects", json={"name": ""}, headers={**ALICE, "Idempotency-Key": "k"})
    assert v.json()["code"] == "VALIDATION_FAILED"
    assert v.json()["field_errors"][0]["field"] == "/name"
