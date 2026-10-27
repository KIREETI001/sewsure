from collections.abc import Iterator

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from sewsure_api import models  # noqa: F401
from sewsure_api.app import create_app
from sewsure_api.auth import CurrentUser
from sewsure_api.db import Base, make_engine, make_session_factory
from sewsure_api.settings import Settings

ALICE = {"X-Test-User": "alice"}
BOB = {"X-Test-User": "bob"}


class StubAuth:
    """Test stub: the X-Test-User header names the caller."""

    def authenticate(self, request: Request) -> CurrentUser | None:
        user = request.headers.get("X-Test-User")
        return CurrentUser(id=user) if user else None


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield make_session_factory(engine)
    engine.dispose()


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> TestClient:
    app = create_app(
        settings=Settings(database_url="sqlite:///:memory:"),
        session_factory=session_factory,
        auth_provider=StubAuth(),
    )
    return TestClient(app)


@pytest.fixture
def project_id(client: TestClient) -> str:
    r = client.post(
        "/v1/projects", json={"name": "Denim"}, headers={**ALICE, "Idempotency-Key": "k"}
    )
    return r.json()["id"]


@pytest.fixture
def revision_id(client: TestClient, project_id: str) -> str:
    r = client.post(
        f"/v1/projects/{project_id}/designs",
        json={"recipe_id": "shirt-to-top", "parameters": {"hem": "raw"}},
        headers=ALICE,
    )
    return r.json()["id"]


@pytest.fixture
def job_id(client: TestClient, project_id: str) -> str:
    r = client.post(f"/v1/projects/{project_id}/jobs", json={"kind": "generate"}, headers=ALICE)
    return r.json()["id"]
