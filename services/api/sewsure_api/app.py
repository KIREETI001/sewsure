from collections.abc import Iterator

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request, Response, status
from sqlalchemy.orm import Session, sessionmaker

from sewsure_api import services
from sewsure_api.auth import AuthProvider, CurrentUser, RejectAllAuth, get_current_user
from sewsure_api.db import make_engine, make_session_factory, session_scope
from sewsure_api.feasibility import FeasibilityChecker, UnconfiguredFeasibility
from sewsure_api.schemas import (
    JobCreate,
    JobOut,
    ProjectCreate,
    ProjectOut,
    RevisionCreate,
    RevisionEdit,
    RevisionOut,
)
from sewsure_api.settings import Settings, get_settings


def get_db(request: Request) -> Iterator[Session]:
    yield from session_scope(request.app.state.session_factory)


def get_checker(request: Request) -> FeasibilityChecker:
    return request.app.state.feasibility


router = APIRouter(prefix="/v1")


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    response: Response,
    idempotency_key: str | None = Header(default=None, max_length=255),
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not idempotency_key:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Idempotency-Key header required")
    project, created = services.create_project_idempotent(db, user.id, idempotency_key, body)
    if not created:
        response.status_code = status.HTTP_200_OK
        response.headers["Idempotent-Replayed"] = "true"
    return project


@router.get("/projects/{project_id}", response_model=ProjectOut)
def read_project(
    project_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return services.get_project(db, user.id, project_id)


@router.post(
    "/projects/{project_id}/designs",
    response_model=RevisionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_design(
    project_id: str,
    body: RevisionCreate,
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
    "/revisions/{revision_id}/edits",
    response_model=RevisionOut,
    status_code=status.HTTP_201_CREATED,
)
def edit_revision(
    revision_id: str,
    body: RevisionEdit,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    checker: FeasibilityChecker = Depends(get_checker),
):
    return services.edit_revision(db, checker, user.id, revision_id, body)


@router.post(
    "/projects/{project_id}/jobs",
    response_model=JobOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_job(
    project_id: str,
    body: JobCreate,
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    settings: Settings = request.app.state.settings
    return services.enqueue_job(db, user.id, project_id, body.kind, settings.job_max_attempts)


@router.get("/jobs/{job_id}", response_model=JobOut)
def read_job(
    job_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return services.get_job(db, user.id, job_id)


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
    return app
