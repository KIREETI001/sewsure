import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from sewsure_api import models  # noqa: F401
from sewsure_api.app import create_app
from sewsure_api.auth import CurrentUser
from sewsure_api.db import Base, make_engine, make_session_factory
from sewsure_api.settings import Settings

ALICE = {"X-Test-User": "usr-alice"}
BOB = {"X-Test-User": "usr-bob"}
FIXTURES = Path(__file__).resolve().parents[3] / "packages" / "contracts" / "fixtures"
CONFIRMED = "2026-10-28T09:00:00Z"


def fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def idem(key: str) -> dict[str, str]:
    return {"Idempotency-Key": f"{key}-idem-0000"}


class StubAuth:
    """Test stub: the X-Test-User header names the caller."""

    def authenticate(self, request: Request) -> CurrentUser | None:
        user = request.headers.get("X-Test-User")
        return CurrentUser(id=user) if user else None


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    # SEWSURE_TEST_DATABASE_URL runs the suite against Postgres (CI); default is in-memory SQLite.
    url = os.environ.get("SEWSURE_TEST_DATABASE_URL", "sqlite:///:memory:")
    engine = make_engine(url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield make_session_factory(engine)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> TestClient:
    app = create_app(
        settings=Settings(database_url="sqlite:///:memory:"),
        session_factory=session_factory,
        auth_provider=StubAuth(),
    )
    return TestClient(app)


def scenario(client: TestClient, name: str, *, headers: dict[str, str] = ALICE) -> dict[str, Any]:
    """Drive the P0 path over HTTP using a contract fixture's garment, measurements and
    inspiration: create project -> PUT measurements -> generate."""
    fx = fixture(name)
    garment = fx["garment"]
    r = client.post(
        "/v1/projects",
        json={
            "garment": {
                "category": garment["category"],
                "fabric_family": garment["fabric_family"],
            }
        },
        headers={**headers, **idem(name)},
    )
    assert r.status_code == 201, r.text
    project_id = r.json()["project_id"]
    dims = fx["measurements"]["measurements"]["garment"]
    # The engine needs a prohibited region; the fixtures do not carry the dimension that
    # supplies it, so the shirt scenarios add it (a valid contract dimension).
    if garment["category"] == "woven_shirt":
        dims.setdefault(
            "placket_end_from_shoulder",
            {"value_mm": 600, "origin": "user_tape_measured", "confirmed_at": CONFIRMED},
        )
    put = client.put(
        f"/v1/projects/{project_id}/measurements",
        json={"units": "mm", "garment": dims},
        headers=headers,
    )
    assert put.status_code == 200, put.text
    insp = fx["inspiration"]
    body = {
        "inspiration": {
            "text": insp["text"],
            "requested_features": insp["requested_features"],
            "skill_level": insp["skill_level"],
            "tools": insp["tools"],
        }
    }
    gen = client.post(
        f"/v1/projects/{project_id}/generate", json=body, headers={**headers, **idem(name)}
    )
    assert gen.status_code == 202, gen.text
    return {"project_id": project_id, "job": gen.json(), "measurements": put.json()}
