from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from sewsure_api.app import create_app
from sewsure_api.settings import Settings
from tests.conftest import ALICE, RECIPE, StubAuth


def _create(client: TestClient, project_id: str, **params: object) -> dict[str, Any]:
    r = client.post(
        f"/v1/projects/{project_id}/designs",
        json={"recipe_id": RECIPE, "parameters": params},
        headers=ALICE,
    )
    assert r.status_code == 201, r.text
    return r.json()


def _edit(client: TestClient, design_id: str, parent: str, **params: object):
    return client.post(
        f"/v1/designs/{design_id}/revisions",
        json={"parent_revision_id": parent, "parameters": params},
        headers=ALICE,
    )


def _get(client: TestClient, revision_id: str) -> dict[str, Any]:
    return client.get(f"/v1/revisions/{revision_id}", headers=ALICE).json()


def test_new_design_stores_engine_result(client: TestClient, project_id: str) -> None:
    body = _create(client, project_id)
    assert body["revision_number"] == 1
    assert body["status"] == "PASS_SUPPORTED_CHECKS"
    assert body["checks"]["hard_pass"] is True
    assert body["units"] == "mm"
    assert body["superseded_by_revision_id"] is None


def test_edit_of_passing_revision_supersedes_it(client: TestClient, project_id: str) -> None:
    first = _create(client, project_id, hem="raw")
    new = _edit(client, first["design_id"], first["revision_id"], hem="folded").json()
    old = _get(client, first["revision_id"])
    assert new["revision_id"] != first["revision_id"]
    assert new["revision_number"] == 2
    assert new["parent_revision_id"] == first["revision_id"]
    assert new["parameters"] == {"hem": "folded"}
    assert old["status"] == "SUPERSEDED"
    assert old["superseded_by_revision_id"] == new["revision_id"]
    assert old["parameters"] == {"hem": "raw"}  # content untouched


@pytest.mark.parametrize(
    ("outcome", "status"),
    [("fail", "FAILED_CHECKS"), ("needs", "NEEDS_INPUT"), ("idea", "IDEA_ONLY")],
)
def test_edit_keeps_non_passing_parent_verdict(
    client: TestClient, project_id: str, outcome: str, status: str
) -> None:
    """Regression (X1 finding 1): an edit must not overwrite the engine verdict of a parent
    that never passed. The link to the newer revision is stored separately."""
    first = _create(client, project_id, outcome=outcome)
    assert first["status"] == status
    new = _edit(client, first["design_id"], first["revision_id"], hem="folded").json()
    old = _get(client, first["revision_id"])
    assert old["status"] == status
    assert old["checks"] == first["checks"]
    assert old["superseded_by_revision_id"] == new["revision_id"]


def test_cannot_edit_a_non_current_parent(client: TestClient, project_id: str) -> None:
    """Regression (X1 finding 4): a failed parent keeps its status but is no longer current,
    so a second edit of it would branch the design and is refused."""
    first = _create(client, project_id, outcome="fail")
    _edit(client, first["design_id"], first["revision_id"], hem="a")
    again = _edit(client, first["design_id"], first["revision_id"], hem="b")
    assert again.status_code == 409


def test_second_edit_of_superseded_passing_parent_conflicts(
    client: TestClient, project_id: str
) -> None:
    first = _create(client, project_id)
    _edit(client, first["design_id"], first["revision_id"], hem="a")
    assert _edit(client, first["design_id"], first["revision_id"], hem="b").status_code == 409


def test_lost_race_maps_to_conflict_not_500(
    client: TestClient, project_id: str, session_factory: sessionmaker[Session]
) -> None:
    """Regression (X1 finding 4): if another edit claims the parent between the read and the
    write, the caller gets 409. Simulated by pre-linking the parent after it is loaded."""
    from sqlalchemy import update

    from sewsure_api import services
    from sewsure_api.models import DesignRevision
    from sewsure_api.schemas import RevisionCreate
    from tests.conftest import StubChecker

    first = _create(client, project_id)
    checker = StubChecker()
    real_evaluate = checker.evaluate

    def racing_evaluate(request):  # type: ignore[no-untyped-def]
        with session_factory() as other:
            other.execute(
                update(DesignRevision)
                .where(DesignRevision.id == first["revision_id"])
                .values(superseded_by_revision_id="rev-winner")
            )
            other.commit()
        return real_evaluate(request)

    checker.evaluate = racing_evaluate  # type: ignore[method-assign]
    with session_factory() as db:
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            services.edit_revision(
                db,
                checker,
                "alice",
                first["design_id"],
                RevisionCreate(parent_revision_id=first["revision_id"], parameters={"hem": "x"}),
            )
        assert exc.value.status_code == 409


def test_parent_must_belong_to_design(client: TestClient, project_id: str) -> None:
    a = _create(client, project_id)
    b = _create(client, project_id)
    assert _edit(client, b["design_id"], a["revision_id"], hem="x").status_code == 404


def test_edit_chain_numbers_increase(client: TestClient, project_id: str) -> None:
    first = _create(client, project_id)
    second = _edit(client, first["design_id"], first["revision_id"], hem="a").json()
    third = _edit(client, first["design_id"], second["revision_id"], hem="b").json()
    assert third["revision_number"] == 3


def test_list_returns_only_current_revision_per_design(client: TestClient, project_id: str) -> None:
    first = _create(client, project_id)
    _create(client, project_id)
    second = _edit(client, first["design_id"], first["revision_id"], hem="a").json()
    listed = client.get(f"/v1/projects/{project_id}/designs", headers=ALICE).json()
    ids = {r["revision_id"] for r in listed}
    assert len(listed) == 2
    assert second["revision_id"] in ids
    assert first["revision_id"] not in ids


# ---- parameter validation (X1 finding 2) ----------------------------------------------


@pytest.mark.parametrize(
    "params",
    [
        {"cut_line_points_mm": [[0, 530], [600, 530]]},  # invented geometry
        {"crop_length_mm": "long"},
        {"crop_length_mm": 99999},
        {"length": 50},  # unitless length
        {"fold_count": 1.5},
        {"fold_count": True},
        {"Bad-Key": "x"},
        {"hem": {"nested": 1}},
    ],
)
def test_invalid_parameters_rejected(
    client: TestClient, project_id: str, params: dict[str, Any]
) -> None:
    r = client.post(
        f"/v1/projects/{project_id}/designs",
        json={"recipe_id": RECIPE, "parameters": params},
        headers=ALICE,
    )
    assert r.status_code == 422
    assert client.get(f"/v1/projects/{project_id}/designs", headers=ALICE).json() == []


def test_parameter_not_on_recipe_allow_list_rejected(client: TestClient, project_id: str) -> None:
    r = client.post(
        f"/v1/projects/{project_id}/designs",
        json={"recipe_id": RECIPE, "parameters": {"sleeve_mm": 100}},
        headers=ALICE,
    )
    assert r.status_code == 422


def test_unknown_recipe_rejected(client: TestClient, project_id: str) -> None:
    r = client.post(
        f"/v1/projects/{project_id}/designs",
        json={"recipe_id": "made_up_v1", "parameters": {}},
        headers=ALICE,
    )
    assert r.status_code == 422


def test_edit_rejects_invalid_parameters(client: TestClient, project_id: str) -> None:
    first = _create(client, project_id)
    assert _edit(client, first["design_id"], first["revision_id"], length=50).status_code == 422
    assert _get(client, first["revision_id"])["superseded_by_revision_id"] is None


def test_valid_mm_and_count_parameters_accepted(client: TestClient, project_id: str) -> None:
    body = _create(client, project_id, crop_length_mm=530.5, fold_count=2)
    assert body["parameters"] == {"crop_length_mm": 530.5, "fold_count": 2}


def test_unconfigured_checker_cannot_create_designs(
    session_factory: sessionmaker[Session],
) -> None:
    app = create_app(
        settings=Settings(database_url="sqlite:///:memory:"),
        session_factory=session_factory,
        auth_provider=StubAuth(),
    )
    c = TestClient(app)
    pid = c.post(
        "/v1/projects", json={"name": "p"}, headers={**ALICE, "Idempotency-Key": "k"}
    ).json()["id"]
    r = c.post(
        f"/v1/projects/{pid}/designs",
        json={"recipe_id": RECIPE, "parameters": {}},
        headers=ALICE,
    )
    assert r.status_code == 422
