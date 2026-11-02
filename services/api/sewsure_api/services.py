"""Domain operations. Every lookup is scoped to the owner; a miss and a wrong-user hit are
indistinguishable (NotFound). Design state is copied from the feasibility engine, never set here.
"""

import hashlib
import json
import re
from collections.abc import Callable
from typing import Any, cast

from sewsure_contracts.design_revision_schema import RevisionCreate
from sewsure_contracts.measurements_schema import MeasurementsInput
from sewsure_contracts.project_schema import ProjectCreate
from sewsure_feasibility import DesignState
from shapely.geometry import Polygon
from sqlalchemy import CursorResult, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sewsure_api import feasibility as engine
from sewsure_api.cutplan import build_cut_plan
from sewsure_api.db import utcnow
from sewsure_api.errors import ApiProblem, Conflict, NotFound, Unprocessable
from sewsure_api.models import (
    JOB_COMPLETE,
    JOB_FAILED,
    JOB_QUEUED,
    JOB_RUNNING,
    CutPlan,
    Design,
    DesignRevision,
    Garment,
    IdempotencyRecord,
    Job,
    MeasurementSet,
    Project,
    new_id,
)

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
            raise Conflict(
                "Idempotency-Key was already used with a different request",
                "IDEMPOTENCY_KEY_REUSED",
            )
        return record.resource_id, False

    existing = lookup()
    if existing is not None:
        return replay(existing)
    try:
        with db.begin_nested():
            resource_id = create()
            db.add(
                IdempotencyRecord(
                    id=new_id("idem"),
                    owner_id=owner_id,
                    scope=scope,
                    key=key,
                    request_hash=request_hash,
                    resource_id=resource_id,
                )
            )
    except IntegrityError:
        raced = lookup()  # a concurrent request with the same key won the race
        if raced is None:
            raise
        return replay(raced)
    return resource_id, True


# ---- projects, garments, measurements -------------------------------------------------


def get_project(db: Session, owner_id: str, project_id: str) -> Project:
    project = db.scalar(
        select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    )
    if project is None:
        raise NotFound("project")
    return project


def get_garment(db: Session, owner_id: str, garment_id: str) -> Garment:
    garment = db.scalar(
        select(Garment).where(Garment.id == garment_id, Garment.owner_id == owner_id)
    )
    if garment is None:
        raise NotFound("garment")
    return garment


def project_garment(db: Session, project: Project) -> Garment:
    return get_garment(db, project.owner_id, project.garment_id)


def create_project_idempotent(
    db: Session, owner_id: str, key: str, body: ProjectCreate
) -> tuple[Project, bool]:
    def create() -> str:
        now = utcnow()
        project_id, garment_id = new_id("prj"), new_id("gar")
        given = body.garment
        category = given.category.value if given and given.category else "unknown"
        fabric = given.fabric_family.value if given and given.fabric_family else "unknown"
        has_attrs = category != "unknown" or fabric != "unknown"
        db.add(
            Project(
                id=project_id,
                owner_id=owner_id,
                garment_id=garment_id,
                title=body.title,
                created_at=now,
                updated_at=now,
            )
        )
        db.flush()
        db.add(
            Garment(
                id=garment_id,
                project_id=project_id,
                owner_id=owner_id,
                category=category,
                fabric_family=fabric,
                attribute_origin="user_entered",
                attributes_confirmed_at=now if has_attrs else None,
                visible_features=[],
                created_at=now,
                updated_at=now,
            )
        )
        return project_id

    project_id, created = idempotent_create(
        db,
        owner_id,
        "POST /v1/projects",
        key,
        hash_body(body.model_dump(mode="json")),
        create,
    )
    db.flush()
    return get_project(db, owner_id, project_id), created


def current_measurements(db: Session, project: Project) -> MeasurementSet | None:
    if project.measurements_id is None:
        return None
    return db.get(MeasurementSet, project.measurements_id)


def put_measurements(
    db: Session, owner_id: str, project_id: str, body: MeasurementsInput
) -> tuple[MeasurementSet, list[dict[str, str]], list[str]]:
    """Store a new measurements record and report what blocks a check. Plausibility and unit
    problems are the engine's call at evaluation time; only missing and unconfirmed values are
    flagged here."""
    project = get_project(db, owner_id, project_id)
    dims = {k.value: v.model_dump(mode="json") for k, v in body.garment.items()}
    record = MeasurementSet(
        id=new_id("msr"),
        project_id=project.id,
        owner_id=owner_id,
        garment=dims,
        body=body.body.model_dump(mode="json") if body.body else None,
        updated_at=utcnow(),
    )
    db.add(record)
    project.measurements_id = record.id
    db.flush()

    issues: list[dict[str, str]] = []
    missing: list[str] = []
    garment_row = project_garment(db, project)
    needed = (
        (*engine.required_dimensions("woven_shirt_crop_v1"), engine.PLACKET)
        if engine.matches_crop_recipe(garment_row.category, garment_row.fabric_family)
        else ()
    )
    for name in needed:
        if name not in dims:
            missing.append(name)
            issues.append(
                {
                    "dimension": name,
                    "code": "MISSING_DIMENSION",
                    "message": f"Measure {name.replace('_', ' ')} with a tape and enter it.",
                }
            )
    for name, value in dims.items():
        if value.get("confirmed_at") is None:
            if name not in missing and name in needed:
                missing.append(name)
            issues.append(
                {
                    "dimension": name,
                    "code": "UNCONFIRMED_DIMENSION",
                    "message": f"Measure {name.replace('_', ' ')} with a tape and confirm it.",
                }
            )
    return record, issues, missing


# ---- designs and revisions ------------------------------------------------------------

NO_RECIPE = "no_reviewed_recipe_v0"  # sentinel sent to the engine for an idea with no recipe
_PROVENANCE = {"source": "live", "schema_version": "1.0"}


def get_revision(db: Session, owner_id: str, revision_id: str) -> DesignRevision:
    revision = db.scalar(
        select(DesignRevision)
        .join(Project, Project.id == DesignRevision.project_id)
        .where(DesignRevision.id == revision_id, Project.owner_id == owner_id)
    )
    if revision is None:
        raise NotFound("revision")
    return revision


def _panel_widths(garment: Any) -> dict[str, float]:
    widths: dict[str, float] = {}
    for panel in garment.panels:
        slug = engine.PANEL_SLUGS.get(panel.side)
        if slug:
            minx, _, maxx, _ = Polygon(panel.polygon_mm).bounds
            widths[slug] = maxx - minx
    return widths


def _prohibited(garment: Any) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for panel in garment.panels:
        slug = engine.PANEL_SLUGS.get(panel.side)
        if slug and panel.prohibited_regions:
            out[slug] = [z.name for z in panel.prohibited_regions]
    return out


def evaluate_and_store(
    db: Session,
    *,
    garment_row: Garment,
    mset: MeasurementSet | None,
    design: Design,
    recipe_id: str | None,
    params: dict[str, Any],
    revision_number: int,
    parent: DesignRevision | None,
    ruler_tolerance_mm: float,
) -> DesignRevision:
    """Run the engine, copy its verdict onto a new immutable revision, and store a cut plan
    only when the engine says the checks passed."""
    dims = engine.engine_measurements(mset.garment if mset else {})
    garment = engine.build_garment(
        garment_row.id, garment_row.category, garment_row.fabric_family, dims, ruler_tolerance_mm
    )
    revision_id = new_id("rev")
    known = engine.recipe_known(recipe_id)
    result = engine.run_engine(
        garment, dims, recipe_id if known and recipe_id else NO_RECIPE, params, revision_id
    )
    fields = engine.revision_fields(result, params, dims)
    now = utcnow()
    revision = DesignRevision(
        id=revision_id,
        design_id=design.id,
        project_id=design.project_id,
        garment_id=garment_row.id,
        parent_revision_id=parent.id if parent else None,
        revision_number=revision_number,
        inputs_hash=fields.inputs_hash,
        inputs={
            "measurements_id": mset.id if mset else None,
            "garment_category": garment_row.category,
            "fabric_family": garment_row.fabric_family,
            "inspiration_id": None,
            "calibration_id": None,
        },
        recipe_id=recipe_id if known else None,
        recipe_version=fields.recipe_version if known else None,
        parameters=params if known else {},
        geometry_mm=fields.geometry_mm,
        checks=fields.checks,
        status=fields.status,
        required_panels=engine.required_panels(garment) if known else [],
        pending_checks=fields.pending_checks,
        engine_version=fields.engine_version,
        created_at=now,
    )
    db.add(revision)
    db.flush()
    if (
        result.status is DesignState.PASS_SUPPORTED_CHECKS
        and fields.cut_mark_mm is not None
        and recipe_id
        and fields.recipe_version
    ):
        plan = build_cut_plan(
            revision_id=revision.id,
            recipe_id=recipe_id,
            recipe_version=fields.recipe_version,
            engine_version=fields.engine_version,
            cut_mark_mm=fields.cut_mark_mm,
            params=params,
            panel_widths_mm=_panel_widths(garment),
            prohibited_regions=_prohibited(garment),
            ruler_tolerance_mm=ruler_tolerance_mm,
            now=now,
        )
        db.add(CutPlan(id=plan["cut_plan_id"], revision_id=revision.id, document=plan))
        db.flush()
        revision.cut_plan_id = plan["cut_plan_id"]
    return revision


def create_design(
    db: Session,
    *,
    project: Project,
    job_id: str | None,
    rank: int,
    title: str,
    recipe_id: str | None,
    params: dict[str, Any],
    ruler_tolerance_mm: float,
    transformation: str | None = None,
) -> DesignRevision:
    design = Design(
        id=new_id("des"),
        project_id=project.id,
        owner_id=project.owner_id,
        job_id=job_id,
        rank=rank,
        title=title[:80],
        transformation=transformation,
    )
    db.add(design)
    db.flush()
    return evaluate_and_store(
        db,
        garment_row=project_garment(db, project),
        mset=current_measurements(db, project),
        design=design,
        recipe_id=recipe_id,
        params=params,
        revision_number=1,
        parent=None,
        ruler_tolerance_mm=ruler_tolerance_mm,
    )


def current_revision(db: Session, design_id: str) -> DesignRevision | None:
    return db.scalar(
        select(DesignRevision)
        .where(DesignRevision.design_id == design_id)
        .order_by(DesignRevision.revision_number.desc())
        .limit(1)
    )


def list_designs(
    db: Session, owner_id: str, project_id: str
) -> list[tuple[Design, DesignRevision]]:
    """Up to three designs with their current revision. Zero is a valid answer."""
    project = get_project(db, owner_id, project_id)
    if project.latest_job_id is None:
        return []
    designs = db.scalars(
        select(Design)
        .where(Design.project_id == project_id, Design.job_id == project.latest_job_id)
        .order_by(Design.rank, Design.created_at)
        .limit(3)
    )
    out: list[tuple[Design, DesignRevision]] = []
    for design in designs:
        revision = current_revision(db, design.id)
        if revision is not None:
            out.append((design, revision))
    return out


def create_revision(
    db: Session,
    owner_id: str,
    design_id: str,
    body: RevisionCreate,
    ruler_tolerance_mm: float,
) -> DesignRevision:
    """Edit = new immutable revision from `parent_revision_id`. The parent's content and
    verdict are untouched; the link to the newer revision is recorded, and the engine's
    `supersede` is asked for the parent's new status (it only applies to a revision that
    passed)."""
    parent = get_revision(db, owner_id, body.parent_revision_id)
    if parent.design_id != design_id:
        raise NotFound("revision")
    if parent.superseded_by_revision_id is not None:
        raise Conflict(
            "parent revision is not the current revision of this design", recoverable=True
        )
    if parent.recipe_id is None:
        raise Unprocessable("this design has no reviewed recipe to customise")
    design_row = db.get(Design, design_id)
    if (
        design_row is not None
        and design_row.transformation == "lengthen"
        and parent.recipe_id in engine.SHORTENING_RECIPES
    ):
        # The only recipe behind this design removes fabric. Re-checking a lengthen request with
        # it could hand out a plan that shortens the garment, so the user starts a new request.
        raise Unprocessable(
            "This design was a lengthen request and the available recipe only shortens. "
            "Start a new request instead of re-checking it.",
            code="LENGTHEN_NOT_SUPPORTED",
        )
    allowed = engine.allowed_parameter_keys(parent.recipe_id)
    changes = body.parameters.model_dump(mode="json", exclude_none=True)
    if allowed is None or set(changes) - allowed:
        names = ", ".join(sorted(set(changes) - (allowed or set())))
        raise Unprocessable(f"parameters not allowed for {parent.recipe_id}: {names}")
    merged = {**parent.parameters, **changes}

    design = db.get(Design, design_id)
    if design is None:
        raise NotFound("design")
    latest = db.scalar(
        select(func.max(DesignRevision.revision_number)).where(
            DesignRevision.design_id == design_id
        )
    )
    project = db.get(Project, parent.project_id)
    assert project is not None
    mset = current_measurements(db, project)  # corrected measurements must take effect
    try:
        new = evaluate_and_store(
            db,
            garment_row=get_garment(db, owner_id, parent.garment_id),
            mset=mset,
            design=design,
            recipe_id=parent.recipe_id,
            params=merged,
            revision_number=(latest or 0) + 1,
            parent=parent,
            ruler_tolerance_mm=ruler_tolerance_mm,
        )
    except IntegrityError:  # another edit took this revision number first
        raise Conflict(
            "design was edited concurrently; reload and retry", recoverable=True
        ) from None

    # Compare-and-set so two concurrent edits of one parent cannot both succeed.
    claimed = db.execute(
        update(DesignRevision)
        .where(
            DesignRevision.id == parent.id,
            DesignRevision.superseded_by_revision_id.is_(None),
        )
        .values(superseded_by_revision_id=new.id)
    )
    if cast(CursorResult[Any], claimed).rowcount != 1:
        raise Conflict(
            "parent revision is not the current revision of this design", recoverable=True
        )
    db.refresh(parent)
    if parent.status == DesignState.PASS_SUPPORTED_CHECKS.value:
        parent.status = engine.superseded_status(parent.checks, parent.status, parent.recipe_id)
    return new


def revision_idempotent(
    db: Session,
    owner_id: str,
    design_id: str,
    key: str,
    body: RevisionCreate,
    ruler_tolerance_mm: float,
) -> tuple[DesignRevision, bool]:
    # Authorise before touching idempotency state.
    parent = get_revision(db, owner_id, body.parent_revision_id)
    if parent.design_id != design_id:
        raise NotFound("revision")

    def create() -> str:
        return create_revision(db, owner_id, design_id, body, ruler_tolerance_mm).id

    revision_id, created = idempotent_create(
        db,
        owner_id,
        f"POST /v1/designs/{design_id}/revisions",
        key,
        hash_body(body.model_dump(mode="json")),
        create,
    )
    return get_revision(db, owner_id, revision_id), created


def get_cut_plan(db: Session, owner_id: str, revision_id: str) -> dict[str, Any]:
    revision = get_revision(db, owner_id, revision_id)
    plan = db.scalar(select(CutPlan).where(CutPlan.revision_id == revision.id))
    if plan is not None and revision.status == DesignState.PASS_SUPPORTED_CHECKS.value:
        if is_stale(db, revision):
            raise ApiProblem(
                409,
                "REVISION_STALE",
                "Measurements changed since this check. Recheck the design before cutting.",
                recoverable=True,
            )
        return plan.document
    # Only a current PASS_SUPPORTED_CHECKS revision hands out a plan. A SUPERSEDED one is
    # read-only history (non-negotiable 3), so it gets none.
    raise ApiProblem(
        409,
        "REVISION_NOT_PASSING",
        "This revision did not pass the implemented checks, or has been replaced; "
        "it has no cut plan.",
    )


def is_stale(db: Session, revision: DesignRevision) -> bool:
    """True when the project's measurements were replaced after this revision was checked.
    Nothing is written: a new engine run on the current values decides the new state."""
    project = db.get(Project, revision.project_id)
    return project is not None and project.measurements_id != revision.inputs.get("measurements_id")


# ---- jobs -----------------------------------------------------------------------------

_TRANSITIONS: dict[str, set[str]] = {
    JOB_QUEUED: {JOB_RUNNING},
    JOB_RUNNING: {JOB_COMPLETE, JOB_FAILED},
    JOB_FAILED: {JOB_QUEUED},  # retry, only when recoverable
    JOB_COMPLETE: set(),
}

JOB_OUTCOMES = frozenset(
    {"designs", "needs_input", "no_feasible_design", "unsupported", "blocked", "needs_confirmation"}
)


class InvalidTransition(Exception):
    pass


def get_job(db: Session, owner_id: str, job_id: str) -> Job:
    job = db.scalar(select(Job).where(Job.id == job_id, Job.owner_id == owner_id))
    if job is None:
        raise NotFound("job")
    return job


def enqueue_job(
    db: Session,
    owner_id: str,
    project_id: str,
    kind: str,
    request: dict[str, Any] | None = None,
    max_attempts: int = 3,
) -> Job:
    project = get_project(db, owner_id, project_id)
    job = Job(
        id=new_id("job"),
        project_id=project.id,
        owner_id=owner_id,
        kind=kind,
        request=request or {},
        max_attempts=max_attempts,
    )
    db.add(job)
    db.flush()
    project.latest_job_id = job.id
    return job


def enqueue_generate_idempotent(
    db: Session,
    owner_id: str,
    project_id: str,
    key: str,
    request: dict[str, Any],
    max_attempts: int,
) -> tuple[Job, bool]:
    project = get_project(db, owner_id, project_id)  # authorise first
    if current_measurements(db, project) is None:
        raise Conflict(
            "The project has no measurements yet; add measurements before generating.",
            "MEASUREMENTS_REQUIRED",
            recoverable=True,
        )

    def create() -> str:
        return enqueue_job(db, owner_id, project_id, "generate_designs", request, max_attempts).id

    job_id, created = idempotent_create(
        db,
        owner_id,
        f"POST /v1/projects/{project_id}/generate",
        key,
        hash_body(request),
        create,
    )
    return get_job(db, owner_id, job_id), created


def _move(job: Job, target: str) -> None:
    if target not in _TRANSITIONS[job.status]:
        raise InvalidTransition(f"{job.status} -> {target}")
    job.status = target
    job.updated_at = utcnow()


def start_job(job: Job) -> None:
    _move(job, JOB_RUNNING)
    job.attempts += 1
    job.error_code = job.error_message = None
    job.recoverable = None


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
    _move(job, JOB_COMPLETE)
    job.result_outcome = outcome
    job.result_design_ids = ids


def fail_job(job: Job, code: str, message: str, recoverable: bool) -> None:
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", code):
        raise ValueError("error code must be UPPER_SNAKE (contract ApiError)")
    _move(job, JOB_FAILED)
    job.error_code = code
    job.error_message = message
    job.recoverable = recoverable


def requeue_job(job: Job) -> None:
    """Retry a failed job. Only recoverable failures with attempts left may be retried."""
    if not job.recoverable:
        raise InvalidTransition("failure is not recoverable")
    if job.attempts >= job.max_attempts:
        raise InvalidTransition("attempts exhausted")
    _move(job, JOB_QUEUED)
