from collections.abc import Iterator

from fastapi import APIRouter, Depends, FastAPI, Header, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker
from starlette.exceptions import HTTPException as StarletteHTTPException

from sewsure_api import services
from sewsure_api.auth import AuthProvider, CurrentUser, RejectAllAuth, get_current_user
from sewsure_api.db import make_engine, make_session_factory, session_scope
from sewsure_api.feasibility import FeasibilityChecker, UnconfiguredFeasibility
from sewsure_api.schemas import (
    DesignCreate,
    GenerateRequest,
    JobOut,
    ProjectCreate,
    ProjectOut,
    RevisionCreate,
    RevisionOut,
)
from sewsure_api.settings import Settings, get_settings


def get_db(request: Request) -> Iterator[Session]:
    yield from session_scope(request.app.state.session_factory)


def get_checker(request: Request) -> FeasibilityChecker:
    return request.app.state.feasibility


router = APIRouter(prefix="/v1")


def _replayed(response: Response, created: bool) -> None:
    if not created:
        response.status_code = status.HTTP_200_OK
        response.headers["Idempotent-Replayed"] = "true"


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    response: Response,
    idempotency_key: str = Header(min_length=1, max_length=255),
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project, created = services.create_project_idempotent(db, user.id, idempotency_key, body)
    _replayed(response, created)
    return project


@router.get("/projects/{project_id}", response_model=ProjectOut)
def read_project(
    project_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return services.get_project(db, user.id, project_id)


@router.get("/projects/{project_id}/designs", response_model=list[RevisionOut])
def list_designs(
    project_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return services.list_designs(db, user.id, project_id)


@router.post(
    "/projects/{project_id}/designs",
    response_model=RevisionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_design(
    project_id: str,
    body: DesignCreate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    checker: FeasibilityChecker = Depends(get_checker),
):
    return services.create_design(db, checker, user.id, project_id, body)


@router.get("/revisions/{revision_id}", response_model=RevisionOut)
def read_revision(
    revision_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return services.get_revision(db, user.id, revision_id)


@router.post(
    "/designs/{design_id}/revisions",
    response_model=RevisionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_revision(
    design_id: str,
    body: RevisionCreate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    checker: FeasibilityChecker = Depends(get_checker),
):
    return services.edit_revision(db, checker, user.id, design_id, body)


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
    idempotency_key: str = Header(min_length=1, max_length=255),
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    settings: Settings = request.app.state.settings
    job, created = services.enqueue_job_idempotent(
        db, user.id, project_id, idempotency_key, body.model_dump(), settings.job_max_attempts
    )
    _replayed(response, created)
    if not created:
        response.status_code = status.HTTP_202_ACCEPTED
    return JobOut.from_job(job)


@router.get("/jobs/{job_id}", response_model=JobOut)
def read_job(
    job_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return JobOut.from_job(services.get_job(db, user.id, job_id))


_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHENTICATED",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_FAILED",
}


def _http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Contract ApiError body for every non-2xx response."""
    code = _CODES.get(exc.status_code, "ERROR")
    return JSONResponse(
        {"code": code, "message": str(exc.detail), "recoverable": exc.status_code == 409},
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
    feasibility: FeasibilityChecker | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="SewSure API", version="0.1.0")
    app.state.settings = settings
    app.state.session_factory = session_factory or make_session_factory(
        make_engine(settings.database_url)
    )
    app.state.auth_provider = auth_provider or RejectAllAuth()
    app.state.feasibility = feasibility or UnconfiguredFeasibility()

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(router)
    app.add_exception_handler(StarletteHTTPException, _http_error)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation_error)  # type: ignore[arg-type]
    return app
