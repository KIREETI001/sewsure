"""FastAPI app factory and routes. Request/response shapes are the generated contract models."""

from collections.abc import Iterator
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, Header, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sewsure_contracts.cut_plan_schema import CutPlan
from sewsure_contracts.design_candidate_schema import DesignCandidate, DesignList
from sewsure_contracts.design_revision_schema import DesignRevision as RevisionOut
from sewsure_contracts.design_revision_schema import RevisionCreate
from sewsure_contracts.garment_schema import Garment as GarmentOut
from sewsure_contracts.job_schema import GenerateRequest
from sewsure_contracts.job_schema import Job as JobOut
from sewsure_contracts.measurements_schema import MeasurementsInput, MeasurementsResult
from sewsure_contracts.project_schema import Project as ProjectOut
from sewsure_contracts.project_schema import ProjectCreate
from sqlalchemy.orm import Session, sessionmaker
from starlette.exceptions import HTTPException as StarletteHTTPException

from sewsure_api import feasibility as engine
from sewsure_api import models, services
from sewsure_api.auth import AuthProvider, CurrentUser, RejectAllAuth, get_current_user
from sewsure_api.db import make_engine, make_session_factory, session_scope
from sewsure_api.errors import ApiProblem
from sewsure_api.generation import Proposer, RuleProposer, run_generate_job
from sewsure_api.settings import Settings, get_settings

IdemKey = Header(min_length=8, max_length=128)


def get_db(request: Request) -> Iterator[Session]:
    yield from session_scope(request.app.state.session_factory)


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _ts(value: Any) -> Any:
    return value


def project_out(p: models.Project) -> ProjectOut:
    return ProjectOut.model_validate(
        {
            "project_id": p.id,
            "owner_id": p.owner_id,
            "garment_id": p.garment_id,
            "title": p.title,
            "measurements_id": p.measurements_id,
            "latest_job_id": p.latest_job_id,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
    )


def garment_out(g: models.Garment) -> GarmentOut:
    return GarmentOut.model_validate(
        {
            "garment_id": g.id,
            "project_id": g.project_id,
            "owner_id": g.owner_id,
            "category": g.category,
            "fabric_family": g.fabric_family,
            "attribute_origin": g.attribute_origin,
            "attributes_confirmed_at": g.attributes_confirmed_at,
            "visible_features": g.visible_features,
            "condition_notes": g.condition_notes,
            "photos": [],
            "created_at": g.created_at,
            "updated_at": g.updated_at,
        }
    )


def revision_out(r: models.DesignRevision, stale: bool = False) -> RevisionOut:
    pending = [*r.pending_checks, engine.STALE_CHECK] if stale else r.pending_checks
    return RevisionOut.model_validate(
        {
            "revision_id": r.id,
            "design_id": r.design_id,
            "project_id": r.project_id,
            "garment_id": r.garment_id,
            "parent_revision_id": r.parent_revision_id,
            "revision_number": r.revision_number,
            "inputs_hash": r.inputs_hash,
            "inputs": r.inputs,
            "recipe_id": r.recipe_id,
            "recipe_version": r.recipe_version,
            "parameters": r.parameters,
            "units": "mm",
            "geometry_mm": r.geometry_mm,
            "checks": r.checks,
            "status": r.status,
            "diy_suitability": None,
            "pending_checks": pending,
            "fit": None,
            "cut_plan_id": r.cut_plan_id,
            "preview": None,
            "superseded_by_revision_id": r.superseded_by_revision_id,
            "provenance": {
                "source": "live",
                "schema_version": "1.0",
                "engine_version": r.engine_version,
                "model_id": None,
                "prompt_version": None,
            },
            "created_at": r.created_at,
        }
    )


def job_out(j: models.Job) -> JobOut:
    result = (
        {"outcome": j.result_outcome, "design_ids": j.result_design_ids}
        if j.status == "complete" and j.result_outcome
        else None
    )
    error = (
        {
            "code": j.error_code or "INTERNAL_ERROR",
            "message": j.error_message or "",
            "recoverable": bool(j.recoverable),
        }
        if j.status == "failed"
        else None
    )
    return JobOut.model_validate(
        {
            "job_id": j.id,
            "kind": j.kind,
            "project_id": j.project_id,
            "state": j.status,
            "stage": j.stage,
            "result": result,
            "error": error,
            "created_at": j.created_at,
            "updated_at": j.updated_at,
        }
    )


def candidate_out(
    d: models.Design, r: models.DesignRevision, stale: bool = False
) -> DesignCandidate:
    note = f" {engine.STALE_CHECK}" if stale else ""
    return DesignCandidate.model_validate(
        {
            "design_id": d.id,
            "project_id": d.project_id,
            "rank": d.rank,
            "title": d.title,
            "current_revision_id": r.id,
            "status": r.status,
            "recipe_id": r.recipe_id,
            "parameters": r.parameters,
            "required_panels": r.required_panels,
            "explanation": (engine.explanation(r.status, r.checks, r.parameters) + note)[:600],
            "failure_codes": r.checks["failure_codes"],
            "missing_dimensions": engine.user_missing(r.checks["missing_dimensions"]),
            "preview": None,
            "provenance": {
                "source": "live",
                "schema_version": "1.0",
                "engine_version": r.engine_version,
                "model_id": None,
                "prompt_version": None,
            },
            "created_at": d.created_at,
        }
    )


router = APIRouter(prefix="/v1")


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    response: Response,
    idempotency_key: str = IdemKey,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project, created = services.create_project_idempotent(db, user.id, idempotency_key, body)
    if not created:
        response.status_code = status.HTTP_200_OK
        response.headers["Idempotent-Replayed"] = "true"
    return project_out(project)


@router.get("/projects/{project_id}", response_model=ProjectOut)
def read_project(
    project_id: str, user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    return project_out(services.get_project(db, user.id, project_id))


@router.get("/garments/{garment_id}", response_model=GarmentOut)
def read_garment(
    garment_id: str, user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    return garment_out(services.get_garment(db, user.id, garment_id))


@router.put("/projects/{project_id}/measurements", response_model=MeasurementsResult)
def put_measurements(
    project_id: str,
    body: MeasurementsInput,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record, issues, missing = services.put_measurements(db, user.id, project_id, body)
    return MeasurementsResult.model_validate(
        {
            "measurements": {
                "measurements_id": record.id,
                "project_id": record.project_id,
                "units": "mm",
                "garment": record.garment,
                "body": record.body,
                "updated_at": record.updated_at,
            },
            "issues": issues,
            "missing_dimensions": missing,
        }
    )


@router.post(
    "/projects/{project_id}/generate",
    response_model=JobOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def generate(
    project_id: str,
    body: GenerateRequest,
    request: Request,
    response: Response,
    background: BackgroundTasks,
    idempotency_key: str = IdemKey,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    settings = _settings(request)
    job, created = services.enqueue_generate_idempotent(
        db,
        user.id,
        project_id,
        idempotency_key,
        body.model_dump(mode="json"),
        settings.job_max_attempts,
    )
    snapshot = job_out(job)
    if created:
        db.commit()  # the runner opens its own session and must see the queued job
        background.add_task(
            run_generate_job,
            request.app.state.session_factory,
            request.app.state.proposer,
            job.id,
            settings.ruler_tolerance_mm,
        )
    else:
        response.headers["Idempotent-Replayed"] = "true"
    response.headers["Location"] = f"/v1/jobs/{job.id}"
    return snapshot


@router.get("/jobs/{job_id}", response_model=JobOut)
def read_job(
    job_id: str, user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    return job_out(services.get_job(db, user.id, job_id))


@router.get("/projects/{project_id}/designs", response_model=DesignList)
def list_designs(
    project_id: str, user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    pairs = services.list_designs(db, user.id, project_id)
    project = services.get_project(db, user.id, project_id)
    binding = None
    if pairs and not any(r.status == "PASS_SUPPORTED_CHECKS" for _, r in pairs):
        binding = pairs[0][1].checks
    return DesignList.model_validate(
        {
            "project_id": project_id,
            "job_id": project.latest_job_id,
            "designs": [candidate_out(d, r, services.is_stale(db, r)) for d, r in pairs],
            "binding_constraint": binding,
        }
    )


@router.post(
    "/designs/{design_id}/revisions",
    response_model=RevisionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_revision(
    design_id: str,
    body: RevisionCreate,
    request: Request,
    response: Response,
    idempotency_key: str = IdemKey,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    revision, created = services.revision_idempotent(
        db, user.id, design_id, idempotency_key, body, _settings(request).ruler_tolerance_mm
    )
    if not created:
        response.headers["Idempotent-Replayed"] = "true"
    return revision_out(revision, services.is_stale(db, revision))


@router.get("/revisions/{revision_id}", response_model=RevisionOut)
def read_revision(
    revision_id: str, user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    revision = services.get_revision(db, user.id, revision_id)
    return revision_out(revision, services.is_stale(db, revision))


@router.get("/revisions/{revision_id}/cut-plan", response_model=CutPlan)
def read_cut_plan(
    revision_id: str, user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    return CutPlan.model_validate(services.get_cut_plan(db, user.id, revision_id))


_STATUS_CODES = {
    401: "UNAUTHENTICATED",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_FAILED",
}


def _http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Contract ApiError body for every non-2xx response."""
    if isinstance(exc, ApiProblem):
        code, recoverable = exc.code, exc.recoverable
    else:
        code, recoverable = _STATUS_CODES.get(exc.status_code, "ERROR"), False
    return JSONResponse(
        {"code": code, "message": str(exc.detail), "recoverable": recoverable},
        status_code=exc.status_code,
    )


def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    fields = [
        {
            "field": "/" + "/".join(str(p) for p in e["loc"][1:]),
            "code": "INVALID",
            "message": str(e["msg"])[:300],
        }
        for e in exc.errors()
    ]
    return JSONResponse(
        {
            "code": "VALIDATION_FAILED",
            "message": "request validation failed",
            "recoverable": True,
            "field_errors": fields,
        },
        status_code=422,
    )


def create_app(
    settings: Settings | None = None,
    session_factory: sessionmaker[Session] | None = None,
    auth_provider: AuthProvider | None = None,
    proposer: Proposer | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="SewSure API", version="0.2.0")
    app.state.settings = settings
    app.state.session_factory = session_factory or make_session_factory(
        make_engine(settings.database_url)
    )
    app.state.auth_provider = auth_provider or RejectAllAuth()
    app.state.proposer = proposer or RuleProposer()

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(router)
    app.add_exception_handler(StarletteHTTPException, _http_error)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation_error)  # type: ignore[arg-type]
    return app
