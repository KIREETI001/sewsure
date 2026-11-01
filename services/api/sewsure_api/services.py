"""Domain operations. Every lookup is scoped to the owner; a miss and a wrong-user hit are
indistinguishable (NotFound)."""

import hashlib
import json
import re
from collections.abc import Callable
from typing import Any, cast

from sqlalchemy import CursorResult, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sewsure_api.db import utcnow
from sewsure_api.errors import Conflict, NotFound, Unprocessable
from sewsure_api.feasibility import ConstraintResult, FeasibilityChecker, checks_json
from sewsure_api.models import (
    DesignRevision,
    DesignState,
    IdempotencyRecord,
    Job,
    JobStatus,
    Project,
    new_id,
)
from sewsure_api.schemas import DesignCreate, ProjectCreate, RevisionCreate

# ---- idempotency ----------------------------------------------------------------------


def hash_body(body: Any) -> str:
    return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()


def idempotent_create(
    db: Session,
    owner_id: str,
    scope: str,
    key: str,
    request_hash: str,
    create: Callable[[], str],
) -> tuple[str, bool]:
    """Return (resource_id, created). Same key + same request replays the original resource;
    same key + different request is a 409. `create` must add the resource and return its ID."""

    def lookup() -> IdempotencyRecord | None:
        return db.scalar(
            select(IdempotencyRecord).where(
                IdempotencyRecord.owner_id == owner_id,
                IdempotencyRecord.scope == scope,
                IdempotencyRecord.key == key,
            )
        )

    def replay(record: IdempotencyRecord) -> tuple[str, bool]:
        if record.request_hash != request_hash:
            raise Conflict("Idempotency-Key was already used with a different request")
        return record.resource_id, False

    existing = lookup()
    if existing is not None:
        return replay(existing)
    try:
        with db.begin_nested():
            resource_id = create()
            db.add(
                IdempotencyRecord(
                    owner_id=owner_id,
                    scope=scope,
                    key=key,
                    request_hash=request_hash,
                    resource_id=resource_id,
                )
            )
    except IntegrityError:
        # A concurrent request with the same key won the race.
        raced = lookup()
        if raced is None:
            raise
        return replay(raced)
    return resource_id, True


# ---- projects -------------------------------------------------------------------------


def get_project(db: Session, owner_id: str, project_id: str) -> Project:
    project = db.scalar(
        select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    )
    if project is None:
        raise NotFound("project")
    return project


def create_project_idempotent(
    db: Session, owner_id: str, key: str, body: ProjectCreate
) -> tuple[Project, bool]:
    def create() -> str:
        project = Project(owner_id=owner_id, name=body.name, intention=body.intention)
        project.id = new_id()
        db.add(project)
        return project.id

    project_id, created = idempotent_create(
        db, owner_id, "POST /v1/projects", key, hash_body(body.model_dump()), create
    )
    db.flush()
    return get_project(db, owner_id, project_id), created


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


def list_designs(db: Session, owner_id: str, project_id: str) -> list[DesignRevision]:
    """Current (latest) revision of each design. Zero is a valid answer; callers must not
    assume any particular count."""
    get_project(db, owner_id, project_id)
    latest = (
        select(DesignRevision.design_id, func.max(DesignRevision.revision_number).label("n"))
        .where(DesignRevision.project_id == project_id)
        .group_by(DesignRevision.design_id)
        .subquery()
    )
    rows = db.scalars(
        select(DesignRevision)
        .join(
            latest,
            (DesignRevision.design_id == latest.c.design_id)
            & (DesignRevision.revision_number == latest.c.n),
        )
        .order_by(DesignRevision.created_at, DesignRevision.id)
    )
    return list(rows)


def _check_params(checker: FeasibilityChecker, recipe_id: str, parameters: dict[str, Any]) -> None:
    """Rule 4: only a reviewed recipe and its allow-listed parameter keys are accepted."""
    allowed = checker.allowed_parameter_keys(recipe_id)
    if allowed is None:
        raise Unprocessable(f"recipe {recipe_id!r} is not a reviewed recipe")
    unknown = sorted(set(parameters) - allowed)
    if unknown:
        raise Unprocessable(f"parameters not allowed for {recipe_id}: {', '.join(unknown)}")


def _revision_from(result: ConstraintResult, **fields: Any) -> DesignRevision:
    # Only values the engine returned are stored; the API derives nothing. Garment and
    # measurement snapshots are passed once those routes exist (empty until then).
    return DesignRevision(
        inputs_hash=result.input_fingerprint,
        geometry_mm={} if result.cut_mark_mm is None else {"cut_mark_mm": result.cut_mark_mm},
        checks=checks_json(result),
        engine_version=result.engine_version,
        recipe_version=result.recipe_version,
        status=result.status.value,
        **fields,
    )


def create_design(
    db: Session,
    checker: FeasibilityChecker,
    owner_id: str,
    project_id: str,
    body: DesignCreate,
) -> DesignRevision:
    project = get_project(db, owner_id, project_id)
    _check_params(checker, body.recipe_id, body.parameters)
    revision_id = new_id()
    result = checker.evaluate({}, {}, body.recipe_id, body.parameters, revision_ref=revision_id)
    revision = _revision_from(
        result,
        id=revision_id,
        project_id=project.id,
        design_id=new_id(),
        revision_number=1,
        recipe_id=body.recipe_id,
        parameters=body.parameters,
    )
    db.add(revision)
    db.flush()
    return revision


def edit_revision(
    db: Session,
    checker: FeasibilityChecker,
    owner_id: str,
    design_id: str,
    body: RevisionCreate,
) -> DesignRevision:
    """An edit never changes the parent's content or verdict. It inserts a new revision, links
    the parent to it via `superseded_by_revision_id`, and asks the engine (`supersede`) for the
    parent's new status, which applies only to a revision that had passed: a FAILED_CHECKS,
    NEEDS_INPUT or IDEA_ONLY parent keeps its own status and `checks`."""
    parent = get_revision(db, owner_id, body.parent_revision_id)
    if parent.design_id != design_id:
        raise NotFound("revision")
    if parent.superseded_by_revision_id is not None:
        raise Conflict("parent revision is not the current revision of this design")

    merged = {**parent.parameters, **body.parameters}
    _check_params(checker, parent.recipe_id, merged)
    new_revision_id = new_id()
    result = checker.evaluate({}, {}, parent.recipe_id, merged, revision_ref=new_revision_id)
    latest = db.scalar(
        select(func.max(DesignRevision.revision_number)).where(
            DesignRevision.design_id == parent.design_id
        )
    )
    new = _revision_from(
        result,
        id=new_revision_id,
        project_id=parent.project_id,
        design_id=parent.design_id,
        revision_number=(latest or 0) + 1,
        parent_revision_id=parent.id,
        recipe_id=parent.recipe_id,
        parameters=merged,
    )

    # Compare-and-set on the parent so two concurrent edits cannot both succeed.
    # The new row goes in first because the link is a plain column, not an enforced FK.
    try:
        with db.begin_nested():
            db.add(new)
            db.flush()
            claimed = db.execute(
                update(DesignRevision)
                .where(
                    DesignRevision.id == parent.id,
                    DesignRevision.superseded_by_revision_id.is_(None),
                )
                .values(superseded_by_revision_id=new.id)
            )
            if cast(CursorResult[Any], claimed).rowcount != 1:
                raise Conflict("parent revision is not the current revision of this design")
    except IntegrityError:
        raise Conflict("design was edited concurrently; reload and retry") from None
    db.refresh(parent)
    if parent.status == DesignState.PASS_SUPPORTED_CHECKS.value:
        parent.status = checker.supersede_status(DesignState.PASS_SUPPORTED_CHECKS).value
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


def enqueue_job_idempotent(
    db: Session,
    owner_id: str,
    project_id: str,
    key: str,
    request: dict[str, Any],
    max_attempts: int,
) -> tuple[Job, bool]:
    kind = "generate_designs"
    get_project(db, owner_id, project_id)  # authorise before touching idempotency state

    def create() -> str:
        return enqueue_job(db, owner_id, project_id, kind, max_attempts).id

    job_id, created = idempotent_create(
        db, owner_id, f"POST /v1/projects/{project_id}/generate", key, hash_body(request), create
    )
    return get_job(db, owner_id, job_id), created


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


JOB_OUTCOMES = frozenset(
    {"designs", "needs_input", "no_feasible_design", "unsupported", "blocked", "needs_confirmation"}
)


def complete_job(job: Job, outcome: str, design_ids: list[str] | None = None) -> None:
    """Record the run summary (contract JobResult). `outcome` is not a design state."""
    ids = design_ids or []
    if outcome not in JOB_OUTCOMES:
        raise ValueError(f"unknown job outcome {outcome!r}")
    if outcome == "designs" and not ids:
        raise ValueError("outcome 'designs' needs at least one design id")
    if outcome in {"blocked", "needs_confirmation"} and ids:
        raise ValueError(f"outcome {outcome!r} carries no designs")
    if len(ids) > 3:
        raise ValueError("a job reports at most three designs")
    _move(job, JobStatus.COMPLETE)
    job.result_outcome = outcome
    job.result_design_ids = ids


def fail_job(job: Job, code: str, message: str, recoverable: bool) -> None:
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", code):
        raise ValueError("error code must be UPPER_SNAKE (contract ApiError)")
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
