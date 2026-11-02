"""Persistence models. Shapes follow packages/contracts; lengths are millimetres.

Design state (`DesignRevision.status`) is only ever copied from the feasibility engine's result.
"""

import secrets
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from sewsure_api.db import Base, UTCDateTime, utcnow

# Contract Id pattern: ^[a-z][a-z0-9]*-[A-Za-z0-9_-]{1,64}$ ("prj-...", "rev-...").
JOB_QUEUED, JOB_RUNNING, JOB_COMPLETE, JOB_FAILED = "queued", "running", "complete", "failed"


def new_id(prefix: str) -> str:
    return f"{prefix}-{secrets.token_urlsafe(12)}"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(80), index=True)
    garment_id: Mapped[str] = mapped_column(String(80))
    title: Mapped[str | None] = mapped_column(String(120), default=None)
    measurements_id: Mapped[str | None] = mapped_column(String(80), default=None)
    latest_job_id: Mapped[str | None] = mapped_column(String(80), default=None)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)


class Garment(Base):
    __tablename__ = "garments"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    owner_id: Mapped[str] = mapped_column(String(80), index=True)
    category: Mapped[str] = mapped_column(String(32))
    fabric_family: Mapped[str] = mapped_column(String(32))
    attribute_origin: Mapped[str] = mapped_column(String(32))
    attributes_confirmed_at: Mapped[datetime | None] = mapped_column(UTCDateTime, default=None)
    visible_features: Mapped[list[str]] = mapped_column(JSON, default=list)
    condition_notes: Mapped[str | None] = mapped_column(String(500), default=None)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)


class MeasurementSet(Base):
    """One immutable measurements record. A new PUT inserts a new row and repoints the project."""

    __tablename__ = "measurement_sets"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    owner_id: Mapped[str] = mapped_column(String(80), index=True)
    garment: Mapped[dict[str, Any]] = mapped_column(JSON)  # dimension -> MeasurementValue
    body: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class Design(Base):
    """A design lineage: its revisions share `design_id`. Display fields only; the engine's
    verdict lives on the revision."""

    __tablename__ = "designs"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    owner_id: Mapped[str] = mapped_column(String(80), index=True)
    job_id: Mapped[str | None] = mapped_column(String(80), default=None)
    rank: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(80))
    # What the user asked for ("crop", "lengthen", ...). Display and routing only; never a verdict.
    transformation: Mapped[str | None] = mapped_column(String(40), default=None)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class DesignRevision(Base):
    """Immutable once written, except for `superseded_by_revision_id` and the engine's own
    SUPERSEDED transition for a revision that had passed. An edit inserts a new row."""

    __tablename__ = "design_revisions"
    __table_args__ = (UniqueConstraint("design_id", "revision_number"),)

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    design_id: Mapped[str] = mapped_column(ForeignKey("designs.id"), index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    garment_id: Mapped[str] = mapped_column(String(80))
    parent_revision_id: Mapped[str | None] = mapped_column(String(80), default=None)
    superseded_by_revision_id: Mapped[str | None] = mapped_column(String(80), default=None)
    revision_number: Mapped[int] = mapped_column(Integer)
    inputs_hash: Mapped[str] = mapped_column(String(64))
    inputs: Mapped[dict[str, Any]] = mapped_column(JSON)  # InputsSnapshot
    recipe_id: Mapped[str | None] = mapped_column(String(100), default=None)
    recipe_version: Mapped[str | None] = mapped_column(String(32), default=None)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    geometry_mm: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    checks: Mapped[dict[str, Any]] = mapped_column(JSON)  # contract ConstraintResult, whole
    status: Mapped[str] = mapped_column(String(32))  # copied from the engine result
    required_panels: Mapped[list[str]] = mapped_column(JSON, default=list)
    pending_checks: Mapped[list[str]] = mapped_column(JSON, default=list)
    cut_plan_id: Mapped[str | None] = mapped_column(String(80), default=None)
    engine_version: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class CutPlan(Base):
    __tablename__ = "cut_plans"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    revision_id: Mapped[str] = mapped_column(ForeignKey("design_revisions.id"), unique=True)
    document: Mapped[dict[str, Any]] = mapped_column(JSON)  # contract CutPlan
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    owner_id: Mapped[str] = mapped_column(String(80), index=True)
    kind: Mapped[str] = mapped_column(String(64))
    request: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)  # GenerateRequest
    status: Mapped[str] = mapped_column(String(16), default=JOB_QUEUED)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    error_code: Mapped[str | None] = mapped_column(String(64), default=None)
    error_message: Mapped[str | None] = mapped_column(Text, default=None)
    recoverable: Mapped[bool | None] = mapped_column(default=None)
    stage: Mapped[str | None] = mapped_column(String(32), default=None)
    result_outcome: Mapped[str | None] = mapped_column(String(32), default=None)
    result_design_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope", "key"),
        Index("ix_idempotency_owner_scope", "owner_id", "scope"),
    )

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(80))
    scope: Mapped[str] = mapped_column(String(160))
    key: Mapped[str] = mapped_column(String(255))
    request_hash: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
