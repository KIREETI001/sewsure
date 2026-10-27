from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session, sessionmaker

from sewsure_api import services
from sewsure_api.models import Job, JobStatus, Project
from sewsure_api.services import InvalidTransition


@pytest.fixture
def db(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    with session_factory() as s:
        yield s


def _job(db: Session, max_attempts: int = 3) -> Job:
    p = Project(owner_id="u", name="p")
    db.add(p)
    db.flush()
    return services.enqueue_job(db, "u", p.id, "generate", max_attempts)


def test_happy_path(db: Session) -> None:
    job = _job(db)
    assert job.status == JobStatus.QUEUED
    services.start_job(job)
    services.complete_job(job)
    assert job.status == JobStatus.COMPLETE
    assert job.attempts == 1


def test_cannot_skip_states(db: Session) -> None:
    job = _job(db)
    with pytest.raises(InvalidTransition):
        services.complete_job(job)


def test_complete_is_terminal(db: Session) -> None:
    job = _job(db)
    services.start_job(job)
    services.complete_job(job)
    with pytest.raises(InvalidTransition):
        services.start_job(job)


def test_recoverable_failure_retries_until_attempts_exhausted(db: Session) -> None:
    job = _job(db, max_attempts=2)
    services.start_job(job)
    services.fail_job(job, "model_timeout", "timed out", recoverable=True)
    assert job.error_code == "model_timeout"
    services.requeue_job(job)
    services.start_job(job)
    services.fail_job(job, "model_timeout", "timed out", recoverable=True)
    with pytest.raises(InvalidTransition):
        services.requeue_job(job)


def test_unrecoverable_failure_cannot_retry(db: Session) -> None:
    job = _job(db)
    services.start_job(job)
    services.fail_job(job, "unsafe_image", "rejected", recoverable=False)
    with pytest.raises(InvalidTransition):
        services.requeue_job(job)


def test_restart_clears_previous_error(db: Session) -> None:
    job = _job(db)
    services.start_job(job)
    services.fail_job(job, "x", "y", recoverable=True)
    services.requeue_job(job)
    services.start_job(job)
    assert job.error_code is None
    assert job.recoverable is None
