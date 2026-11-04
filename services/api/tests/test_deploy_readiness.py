"""Audit must-fixes: commit before replying, Azure database login, token login, abandoned jobs."""

from datetime import timedelta
from types import SimpleNamespace
from typing import Any

import jwt
import psycopg
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker

from sewsure_api.app import create_app
from sewsure_api.auth import JwtAuth, RejectAllAuth, auth_from_settings
from sewsure_api.db import POSTGRES_TOKEN_SCOPE, engine_from_settings, utcnow
from sewsure_api.models import Job
from sewsure_api.settings import Settings
from tests.conftest import ALICE, StubAuth, idem, scenario

PROJECT = {"garment": {"category": "woven_shirt", "fabric_family": "woven"}}


def _app(session_factory: sessionmaker[Session], **settings: Any) -> TestClient:
    app = create_app(
        settings=Settings(database_url="sqlite:///:memory:", **settings),
        session_factory=session_factory,
        auth_provider=StubAuth(),
    )
    return TestClient(app, raise_server_exceptions=False)


def _fail_commits(session_factory: sessionmaker[Session]) -> None:
    def boom(session: Session) -> None:
        if not session.in_nested_transaction():
            raise RuntimeError("database went away at commit")

    event.listen(session_factory, "before_commit", boom)


def test_failed_commit_is_never_reported_as_success(
    session_factory: sessionmaker[Session],
) -> None:
    client = _app(session_factory)
    _fail_commits(session_factory)
    r = client.post("/v1/projects", json=PROJECT, headers={**ALICE, **idem("commit")})
    assert r.status_code >= 500


# ---- Azure database login ---------------------------------------------------------------


AZURE: dict[str, Any] = {
    "postgres_host": "db.example.test",
    "postgres_db": "sewsure",
    "postgres_user": "id-sewsure",
    "managed_identity_client_id": "client-id",
}


class _Credential:
    def __init__(self) -> None:
        self.scopes: list[str] = []

    def get_token(self, scope: str) -> SimpleNamespace:
        self.scopes.append(scope)
        return SimpleNamespace(token=f"token-{len(self.scopes)}")


class _Connected(Exception):
    pass


def test_azure_connections_use_a_fresh_entra_token(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[dict[str, Any]] = []

    def connect(*args: Any, **kwargs: Any) -> None:
        seen.append(kwargs)
        raise _Connected

    monkeypatch.setattr(psycopg, "connect", connect)
    credential = _Credential()
    engine = engine_from_settings(Settings(**AZURE), credential)
    for _ in range(2):
        with pytest.raises(_Connected):
            engine.connect()
    assert credential.scopes == [POSTGRES_TOKEN_SCOPE] * 2
    assert [c["password"] for c in seen] == ["token-1", "token-2"]
    assert seen[0]["host"] == "db.example.test"
    assert seen[0]["user"] == "id-sewsure"
    assert seen[0]["dbname"] == "sewsure"
    assert seen[0]["sslmode"] == "require"


def test_local_settings_keep_the_database_url() -> None:
    engine = engine_from_settings(Settings(database_url="sqlite:///:memory:"))
    assert engine.url.drivername == "sqlite"


# ---- token login ------------------------------------------------------------------------


ISSUER = "https://issuer.example.test/"
AUDIENCE = "sewsure-api"
_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _token(key: Any = _KEY, algorithm: str = "RS256", **overrides: Any) -> str:
    claims = {
        "sub": "usr-alice",
        "iss": ISSUER,
        "aud": AUDIENCE,
        "exp": utcnow() + timedelta(minutes=5),
        **overrides,
    }
    return jwt.encode({k: v for k, v in claims.items() if v is not None}, key, algorithm=algorithm)


def _authenticate(header: str | None) -> Any:
    auth = JwtAuth(ISSUER, AUDIENCE, lambda _: SimpleNamespace(key=_KEY.public_key()))
    headers = {"Authorization": header} if header is not None else {}
    return auth.authenticate(SimpleNamespace(headers=headers))  # type: ignore[arg-type]


def test_valid_token_names_the_user() -> None:
    user = _authenticate(f"Bearer {_token()}")
    assert user is not None and user.id == "usr-alice"


@pytest.mark.parametrize(
    "header",
    [
        None,
        "",
        "Bearer ",
        "Basic abc",
        "Bearer not-a-token",
        f"Bearer {_token(_OTHER_KEY)}",
        f"Bearer {_token('a-shared-secret-that-is-long-enough-for-hs256', 'HS256')}",
        f"Bearer {_token(None, 'none')}",
        f"Bearer {_token(exp=utcnow() - timedelta(minutes=5))}",
        f"Bearer {_token(exp=None)}",
        f"Bearer {_token(iss='https://other.example.test/')}",
        f"Bearer {_token(aud='another-api')}",
        f"Bearer {_token(sub=None)}",
        f"Bearer {_token(sub='')}",
        f"Bearer {_token(sub='x' * 81)}",
    ],
    ids=[
        "no-header",
        "empty",
        "no-token",
        "wrong-scheme",
        "garbage",
        "wrong-key",
        "shared-secret",
        "alg-none",
        "expired",
        "no-expiry",
        "wrong-issuer",
        "wrong-audience",
        "no-subject",
        "empty-subject",
        "subject-too-long",
    ],
)
def test_bad_tokens_are_rejected(header: str | None) -> None:
    assert _authenticate(header) is None


def test_auth_stays_closed_until_fully_configured() -> None:
    partial = Settings(auth_issuer=ISSUER, auth_audience=AUDIENCE)
    assert isinstance(auth_from_settings(partial), RejectAllAuth)
    full = Settings(auth_issuer=ISSUER, auth_audience=AUDIENCE, auth_jwks_url=f"{ISSUER}jwks")
    assert isinstance(auth_from_settings(full), JwtAuth)


# ---- abandoned jobs ---------------------------------------------------------------------


@pytest.mark.parametrize("status", ["queued", "running"])
def test_abandoned_job_becomes_a_recoverable_failure(
    client: TestClient, session_factory: sessionmaker[Session], status: str
) -> None:
    job_id = scenario(client, "woven_shirt_crop_pass")["job"]["job_id"]
    with session_factory() as db:
        job = db.get(Job, job_id)
        assert job is not None
        job.status = status
        job.result_outcome = None
        job.updated_at = utcnow() - timedelta(seconds=601)
        db.commit()

    r = client.get(f"/v1/jobs/{job_id}", headers=ALICE)
    assert r.status_code == 200
    assert r.json()["state"] == "failed"
    assert r.json()["error"]["recoverable"] is True
    # The failure was saved, so the next poll agrees.
    assert client.get(f"/v1/jobs/{job_id}", headers=ALICE).json()["state"] == "failed"


def test_recent_and_finished_jobs_are_left_alone(
    client: TestClient, session_factory: sessionmaker[Session]
) -> None:
    job_id = scenario(client, "woven_shirt_crop_pass")["job"]["job_id"]
    assert client.get(f"/v1/jobs/{job_id}", headers=ALICE).json()["state"] == "complete"

    with session_factory() as db:
        job = db.get(Job, job_id)
        assert job is not None
        job.updated_at = utcnow() - timedelta(days=1)
        db.commit()
    assert client.get(f"/v1/jobs/{job_id}", headers=ALICE).json()["state"] == "complete"

    with session_factory() as db:
        job = db.get(Job, job_id)
        assert job is not None
        job.status = "running"
        job.updated_at = utcnow()
        db.commit()
    assert client.get(f"/v1/jobs/{job_id}", headers=ALICE).json()["state"] == "running"
