from collections.abc import Iterator

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from sewsure_api import models  # noqa: F401
from sewsure_api.app import create_app
from sewsure_api.auth import CurrentUser
from sewsure_api.db import Base, make_engine, make_session_factory
from sewsure_api.feasibility import EvaluationRequest, EvaluationResult
from sewsure_api.models import DesignState
from sewsure_api.settings import Settings

ALICE = {"X-Test-User": "alice"}
BOB = {"X-Test-User": "bob"}


RECIPE = "woven_shirt_crop_v1"


class StubChecker:
    """Stands in for packages/feasibility. The `outcome` parameter picks the verdict so tests
    can exercise each state; the API itself never decides one."""

    VERDICTS = {
        "pass": DesignState.PASS_SUPPORTED_CHECKS,
        "fail": DesignState.FAILED_CHECKS,
        "needs": DesignState.NEEDS_INPUT,
        "idea": DesignState.IDEA_ONLY,
    }

    def allowed_parameter_keys(self, recipe_id: str) -> frozenset[str] | None:
        if recipe_id != RECIPE:
            return None
        return frozenset({"outcome", "hem", "crop_length_mm", "fold_count"})

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        status = self.VERDICTS[str(request.parameters.get("outcome", "pass"))]
        return EvaluationResult(
            status=status,
            checks={
                "hard_pass": status == DesignState.PASS_SUPPORTED_CHECKS,
                "failure_codes": ["INSUFFICIENT_LENGTH"] if status == "FAILED_CHECKS" else [],
                "engine_version": "test",
            },
            geometry_mm={"finished_length_mm": 530.0},
            engine_version="test",
            recipe_version="1.0",
            inputs_hash="0" * 64,
        )

    def supersede(self, previous: DesignState) -> DesignState:
        return DesignState.SUPERSEDED


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
        feasibility=StubChecker(),
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
        json={"recipe_id": RECIPE, "parameters": {"hem": "raw"}},
        headers=ALICE,
    )
    return r.json()["revision_id"]


@pytest.fixture
def job_id(client: TestClient, project_id: str) -> str:
    r = client.post(
        f"/v1/projects/{project_id}/generate", headers={**ALICE, "Idempotency-Key": "g"}
    )
    return r.json()["id"]


@pytest.fixture
def design_id(client: TestClient, revision_id: str) -> str:
    return client.get(f"/v1/revisions/{revision_id}", headers=ALICE).json()["design_id"]
