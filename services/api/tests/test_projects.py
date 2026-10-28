from fastapi.testclient import TestClient

from tests.conftest import ALICE, BOB


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
    assert client.post(url, headers=ALICE).status_code == 422
    h = {**ALICE, "Idempotency-Key": "once"}
    first = client.post(url, headers=h)
    second = client.post(url, headers=h)
    assert first.status_code == second.status_code == 202
    assert first.json()["id"] == second.json()["id"]
    assert second.headers["Idempotent-Replayed"] == "true"


def test_empty_design_list_is_valid(client: TestClient, project_id: str) -> None:
    assert client.get(f"/v1/projects/{project_id}/designs", headers=ALICE).json() == []
