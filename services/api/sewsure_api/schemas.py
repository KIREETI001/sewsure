"""Request/response models.

TODO(K1/K2): replace with generated models from packages/contracts (`sewsure_contracts`, PR #15
and later). Names follow contract v1 (revision_id, status, checks, superseded_by_revision_id);
fields not yet stored (garment_id, inputs, pending_checks, preview, provenance, ...) are
omitted until the swap. Every route imports its shapes from this module only.
"""

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    from sewsure_api.models import Job

_KEY = re.compile(r"^[a-z][a-z0-9_]*$")
_RECIPE_ID = re.compile(r"^[a-z][a-z0-9_]*_v[0-9]+$")
_MM_LIMIT = 5000


def validate_parameters(params: dict[str, Any]) -> dict[str, Any]:
    """Mirror of common.schema.json#/$defs/Parameters: `_mm` keys are numbers within
    0..5000, `_count` keys are integers 0..100, everything else is a string or boolean.
    Unitless numbers, lists and objects (e.g. invented cut-line points) are rejected."""
    for key, value in params.items():
        if not _KEY.match(key) or len(key) > 64:
            raise ValueError(f"parameter key {key!r} is not allowed")
        if key.endswith("_mm"):
            ok = isinstance(value, int | float) and not isinstance(value, bool)
            if not ok or not 0 <= value <= _MM_LIMIT:
                raise ValueError(f"{key} must be a millimetre length from 0 to {_MM_LIMIT}")
        elif key.endswith("_count"):
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
                raise ValueError(f"{key} must be an integer 0..100")
        elif not isinstance(value, str | bool):
            raise ValueError(f"{key} must be a string or boolean; lengths need a _mm suffix")
    return params


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    intention: str | None = Field(default=None, max_length=2000)


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    intention: str | None
    created_at: datetime


class DesignCreate(BaseModel):
    """Provisional: the contract creates designs via the generate job. Recipe ID and
    allow-listed parameters only; the API never accepts invented pattern geometry (rule 4)."""

    recipe_id: str = Field(max_length=100, pattern=_RECIPE_ID.pattern)
    parameters: dict[str, Any] = Field(default_factory=dict)

    @field_validator("parameters")
    @classmethod
    def _params(cls, v: dict[str, Any]) -> dict[str, Any]:
        return validate_parameters(v)


class RevisionCreate(BaseModel):
    """POST /v1/designs/{design_id}/revisions (contract RevisionCreate)."""

    model_config = ConfigDict(extra="forbid")

    parent_revision_id: str = Field(min_length=1, max_length=64)
    parameters: dict[str, Any]

    @field_validator("parameters")
    @classmethod
    def _params(cls, v: dict[str, Any]) -> dict[str, Any]:
        return validate_parameters(v)

    @model_validator(mode="after")
    def _non_empty(self) -> Self:
        if not self.parameters:
            raise ValueError("parameters must change at least one value")
        return self


class RevisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    revision_id: str = Field(validation_alias="id")
    design_id: str
    project_id: str
    parent_revision_id: str | None
    revision_number: int
    inputs_hash: str
    recipe_id: str
    recipe_version: str | None
    parameters: dict[str, Any]
    units: str = "mm"
    geometry_mm: dict[str, Any]
    checks: dict[str, Any]
    status: str
    superseded_by_revision_id: str | None
    created_at: datetime


class GenerateRequest(BaseModel):
    """POST /v1/projects/{id}/generate body (contract GenerateRequest). The inspiration input is
    validated against the contract once generated models replace this module."""

    model_config = ConfigDict(extra="forbid")

    inspiration: dict[str, Any]


class JobResultOut(BaseModel):
    outcome: str
    design_ids: list[str]


class ApiErrorOut(BaseModel):
    code: str
    message: str
    recoverable: bool
    retry_after_s: int | None = None
    field_errors: list[dict[str, str]] | None = None
    request_id: str | None = None


class JobOut(BaseModel):
    """Contract Job: job_id, kind, project_id, state, stage, result, error, timestamps."""

    job_id: str
    kind: str
    project_id: str
    state: str
    stage: str | None
    result: JobResultOut | None
    error: ApiErrorOut | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_job(cls, job: "Job") -> "JobOut":
        result = (
            JobResultOut(outcome=job.result_outcome, design_ids=list(job.result_design_ids or []))
            if job.status == "complete" and job.result_outcome
            else None
        )
        error = (
            ApiErrorOut(
                code=job.error_code or "INTERNAL_ERROR",
                message=job.error_message or "",
                recoverable=bool(job.recoverable),
            )
            if job.status == "failed"
            else None
        )
        return cls(
            job_id=job.id,
            kind=job.kind,
            project_id=job.project_id,
            state=job.status,
            stage=job.stage,
            result=result,
            error=error,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
