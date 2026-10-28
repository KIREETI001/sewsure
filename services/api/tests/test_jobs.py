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
    return services.enqueue_job(db, "u", p.id, "generate_designs", max_attempts)


def test_happy_path(db: Session) -> None:
    job = _job(db)
    assert job.status == JobStatus.QUEUED
    services.start_job(job)
    services.complete_job(job, "no_feasible_design")
    assert job.status == JobStatus.COMPLETE
    assert job.attempts == 1


def test_cannot_skip_states(db: Session) -> None:
    job = _job(db)
    with pytest.raises(InvalidTransition):
        services.complete_job(job, "no_feasible_design")


def test_complete_is_terminal(db: Session) -> None:
    job = _job(db)
    services.start_job(job)
    services.complete_job(job, "no_feasible_design")
    with pytest.raises(InvalidTransition):
        services.start_job(job)


def test_recoverable_failure_retries_until_attempts_exhausted(db: Session) -> None:
    job = _job(db, max_attempts=2)
    services.start_job(job)
    services.fail_job(job, "MODEL_TIMEOUT", "timed out", recoverable=True)
    assert job.error_code == "MODEL_TIMEOUT"
    services.requeue_job(job)
    services.start_job(job)
    services.fail_job(job, "MODEL_TIMEOUT", "timed out", recoverable=True)
    with pytest.raises(InvalidTransition):
        services.requeue_job(job)


def test_unrecoverable_failure_cannot_retry(db: Session) -> None:
    job = _job(db)
    services.start_job(job)
    services.fail_job(job, "UNSAFE_IMAGE", "rejected", recoverable=False)
    with pytest.raises(InvalidTransition):
        services.requeue_job(job)


def test_restart_clears_previous_error(db: Session) -> None:
    job = _job(db)
    services.start_job(job)
    services.fail_job(job, "X", "y", recoverable=True)
    services.requeue_job(job)
    services.start_job(job)
    assert job.error_code is None
    assert job.recoverable is None


@pytest.mark.parametrize(
    ("outcome", "ids"),
    [("designs", []), ("blocked", ["rev-1"]), ("bogus", []), ("designs", ["a", "b", "c", "d"])],
)
def test_invalid_job_result_rejected(db: Session, outcome: str, ids: list[str]) -> None:
    job = _job(db)
    services.start_job(job)
    with pytest.raises(ValueError):
        services.complete_job(job, outcome, ids)


def test_error_code_must_be_upper_snake(db: Session) -> None:
    job = _job(db)
    services.start_job(job)
    with pytest.raises(ValueError):
        services.fail_job(job, "model_timeout", "x", recoverable=True)
