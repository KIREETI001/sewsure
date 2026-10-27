"""Domain operations. Every lookup is scoped to the owner; a miss and a wrong-user hit are
indistinguishable (NotFound)."""

import hashlib
import json

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sewsure_api.db import utcnow
from sewsure_api.errors import Conflict, NotFound
from sewsure_api.feasibility import FeasibilityChecker
from sewsure_api.models import (
    DesignRevision,
    DesignState,
    IdempotencyRecord,
    Job,
    JobStatus,
    Project,
    new_id,
)
from sewsure_api.schemas import ProjectCreate, RevisionCreate, RevisionEdit

# ---- projects -------------------------------------------------------------------------


def get_project(db: Session, owner_id: str, project_id: str) -> Project:
    project = db.scalar(
        select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    )
    if project is None:
        raise NotFound("project")
    return project


def _hash_body(body: ProjectCreate) -> str:
    return hashlib.sha256(json.dumps(body.model_dump(), sort_keys=True).encode()).hexdigest()


def create_project_idempotent(
    db: Session, owner_id: str, key: str, body: ProjectCreate
) -> tuple[Project, bool]:
    """Return (project, created). Same key + same body replays the original project;
    same key + different body is a 409."""
    scope = "POST /v1/projects"
    request_hash = _hash_body(body)

    def lookup() -> IdempotencyRecord | None:
        return db.scalar(
            select(IdempotencyRecord).where(
                IdempotencyRecord.owner_id == owner_id,
                IdempotencyRecord.scope == scope,
                IdempotencyRecord.key == key,
            )
        )

    def replay(record: IdempotencyRecord) -> tuple[Project, bool]:
        if record.request_hash != request_hash:
            raise Conflict("Idempotency-Key was already used with a different request body")
        return get_project(db, owner_id, record.resource_id), False

    existing = lookup()
    if existing is not None:
        return replay(existing)

    project = Project(id=new_id(), owner_id=owner_id, name=body.name, intention=body.intention)
    try:
        with db.begin_nested():
            db.add(project)
            db.add(
                IdempotencyRecord(
                    owner_id=owner_id,
                    scope=scope,
                    key=key,
                    request_hash=request_hash,
                    resource_id=project.id,
                )
            )
    except IntegrityError:
        # A concurrent request with the same key won the race.
        raced = lookup()
        if raced is None:
            raise
        return replay(raced)
    return project, True


# ---- revisions ------------------------------------------------------------------------


def get_revision(db: Session, owner_id: str, revision_id: str) -> DesignRevision:
    revision = db.scalar(
        select(DesignRevision)
        .join(Project, Project.id == DesignRevision.project_id)
        .where(DesignRevision.id == revision_id, Project.owner_id == owner_id)
    )
    if revision is None:
        raise NotFound("revision")
    return revision


def create_design(
    db: Session,
    checker: FeasibilityChecker,
    owner_id: str,
    project_id: str,
    body: RevisionCreate,
) -> DesignRevision:
    project = get_project(db, owner_id, project_id)
    revision = DesignRevision(
        project_id=project.id,
        design_id=new_id(),
        revision_number=1,
        recipe_id=body.recipe_id,
        parameters=body.parameters,
        state=checker.evaluate(body.recipe_id, body.parameters).value,
    )
    db.add(revision)
    db.flush()
    return revision


def edit_revision(
    db: Session,
    checker: FeasibilityChecker,
    owner_id: str,
    revision_id: str,
    body: RevisionEdit,
) -> DesignRevision:
    """An edit never changes the old revision's content: it inserts a new revision and marks
    the old one SUPERSEDED. Downstream artefacts of the old revision stay tied to its ID."""
    old = get_revision(db, owner_id, revision_id)
    if old.state == DesignState.SUPERSEDED.value:
        raise Conflict("revision is superseded; edit the latest revision of this design")

    recipe_id = body.recipe_id if body.recipe_id is not None else old.recipe_id
    parameters = body.parameters if body.parameters is not None else dict(old.parameters)
    latest = db.scalar(
        select(func.max(DesignRevision.revision_number)).where(
            DesignRevision.design_id == old.design_id
        )
    )
    new = DesignRevision(
        project_id=old.project_id,
        design_id=old.design_id,
        revision_number=(latest or 0) + 1,
        parent_revision_id=old.id,
        recipe_id=recipe_id,
        parameters=parameters,
        state=checker.evaluate(recipe_id, parameters).value,
    )
    old.state = DesignState.SUPERSEDED.value
    db.add(new)
    db.flush()
    return new


# ---- jobs -----------------------------------------------------------------------------

_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.QUEUED: {JobStatus.RUNNING},
    JobStatus.RUNNING: {JobStatus.COMPLETE, JobStatus.FAILED},
    JobStatus.FAILED: {JobStatus.QUEUED},  # retry, only when recoverable
    JobStatus.COMPLETE: set(),
}


class InvalidTransition(Exception):
    pass


def get_job(db: Session, owner_id: str, job_id: str) -> Job:
    job = db.scalar(select(Job).where(Job.id == job_id, Job.owner_id == owner_id))
    if job is None:
        raise NotFound("job")
    return job


def enqueue_job(
    db: Session, owner_id: str, project_id: str, kind: str, max_attempts: int = 3
) -> Job:
    project = get_project(db, owner_id, project_id)
    job = Job(project_id=project.id, owner_id=owner_id, kind=kind, max_attempts=max_attempts)
    db.add(job)
    db.flush()
    return job


def _move(job: Job, target: JobStatus) -> None:
    current = JobStatus(job.status)
    if target not in _TRANSITIONS[current]:
        raise InvalidTransition(f"{current.value} -> {target.value}")
    job.status = target.value
    job.updated_at = utcnow()


def start_job(job: Job) -> None:
    _move(job, JobStatus.RUNNING)
    job.attempts += 1
    job.error_code = job.error_message = None
    job.recoverable = None


def complete_job(job: Job, result_revision_id: str | None = None) -> None:
    _move(job, JobStatus.COMPLETE)
    job.result_revision_id = result_revision_id


def fail_job(job: Job, code: str, message: str, recoverable: bool) -> None:
    _move(job, JobStatus.FAILED)
    job.error_code = code
    job.error_message = message
    job.recoverable = recoverable


def requeue_job(job: Job) -> None:
    """Retry a failed job. Only recoverable failures with attempts left may be retried."""
    if not job.recoverable:
        raise InvalidTransition("failure is not recoverable")
    if job.attempts >= job.max_attempts:
        raise InvalidTransition("attempts exhausted")
    _move(job, JobStatus.QUEUED)
