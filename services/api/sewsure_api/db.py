from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

from azure.identity import ManagedIdentityCredential
from sqlalchemy import URL, DateTime, Engine, create_engine, event
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.types import TypeDecorator

from sewsure_api.settings import Settings

POSTGRES_TOKEN_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"


class Base(DeclarativeBase):
    pass


class UTCDateTime(TypeDecorator[datetime]):
    """Timezone-aware UTC datetimes on every backend (SQLite drops tzinfo)."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("naive datetime not allowed")
        return value.astimezone(UTC) if value is not None else None

    def process_result_value(self, value: Any, dialect: Dialect) -> datetime | None:
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


def utcnow() -> datetime:
    return datetime.now(UTC)


def make_engine(url: str) -> Engine:
    if url.startswith("sqlite") and ":memory:" in url:
        return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True)


def engine_from_settings(settings: Settings, credential: Any = None) -> Engine:
    """Local URL by default; on Azure, connect with a fresh Entra token as the password."""
    if not settings.postgres_host:
        return make_engine(settings.database_url)
    url = URL.create(
        "postgresql+psycopg",
        username=settings.postgres_user,
        host=settings.postgres_host,
        database=settings.postgres_db,
    )
    engine = create_engine(url, pool_pre_ping=True, connect_args={"sslmode": "require"})
    credential = credential or ManagedIdentityCredential(
        client_id=settings.managed_identity_client_id
    )

    @event.listens_for(engine, "do_connect")
    def _use_token(dialect: Dialect, record: Any, cargs: Any, cparams: dict[str, Any]) -> None:
        cparams["password"] = credential.get_token(POSTGRES_TOKEN_SCOPE).token

    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)


def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Yield a session; commit on success, roll back on error."""
    with factory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
