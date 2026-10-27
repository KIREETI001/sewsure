from fastapi.testclient import TestClient

from tests.conftest import ALICE


def test_new_design_is_revision_one_and_not_passing(client: TestClient, project_id: str) -> None:
    r = client.post(
        f"/v1/projects/{project_id}/designs",
        json={"recipe_id": "x", "parameters": {}},
        headers=ALICE,
    )
    body = r.json()
    assert body["revision_number"] == 1
    # The unconfigured checker never reports a passing state.
    assert body["state"] == "IDEA_ONLY"


def test_edit_creates_new_revision_and_supersedes_old(client: TestClient, revision_id: str) -> None:
    r = client.post(
        f"/v1/revisions/{revision_id}/edits",
        json={"parameters": {"hem": "folded"}},
        headers=ALICE,
    )
    new = r.json()
    old = client.get(f"/v1/revisions/{revision_id}", headers=ALICE).json()
    assert new["id"] != revision_id
    assert new["revision_number"] == 2
    assert new["parent_revision_id"] == revision_id
    assert new["design_id"] == old["design_id"]
    assert new["parameters"] == {"hem": "folded"}
    assert old["state"] == "SUPERSEDED"
    assert old["parameters"] == {"hem": "raw"}  # content untouched


def test_cannot_edit_superseded_revision(client: TestClient, revision_id: str) -> None:
    client.post(f"/v1/revisions/{revision_id}/edits", json={"parameters": {}}, headers=ALICE)
    r = client.post(f"/v1/revisions/{revision_id}/edits", json={"parameters": {}}, headers=ALICE)
    assert r.status_code == 409


def test_edit_chain_numbers_increase(client: TestClient, revision_id: str) -> None:
    second = client.post(
        f"/v1/revisions/{revision_id}/edits", json={"parameters": {"a": 1}}, headers=ALICE
    ).json()
    third = client.post(
        f"/v1/revisions/{second['id']}/edits", json={"parameters": {"a": 2}}, headers=ALICE
    ).json()
    assert third["revision_number"] == 3
