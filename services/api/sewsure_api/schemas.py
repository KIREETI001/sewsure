"""Request/response models.

TODO(K1/K2): replace with generated models from packages/contracts. Every route imports its
shapes from this module only, so the swap is a single change.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    intention: str | None = Field(default=None, max_length=2000)


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    intention: str | None
    created_at: datetime


class RevisionCreate(BaseModel):
    """Recipe ID and parameters only; the API never accepts model-invented pattern geometry
    (rule 4). Allow-list validation against the contract schema arrives with K1."""

    recipe_id: str = Field(min_length=1, max_length=100)
    parameters: dict[str, Any] = Field(default_factory=dict)


class RevisionEdit(BaseModel):
    recipe_id: str | None = Field(default=None, min_length=1, max_length=100)
    parameters: dict[str, Any] | None = None


class RevisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    design_id: str
    revision_number: int
    parent_revision_id: str | None
    recipe_id: str
    parameters: dict[str, Any]
    state: str
    created_at: datetime


class JobCreate(BaseModel):
    kind: str = Field(min_length=1, max_length=64)


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    kind: str
    status: str
    attempts: int
    error_code: str | None
    error_message: str | None
    recoverable: bool | None
    result_revision_id: str | None
    created_at: datetime
    updated_at: datetime
