"""Persistence models. Lengths are never stored here; geometry lives in packages/feasibility."""

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from sewsure_api.db import Base, UTCDateTime, utcnow


def new_id() -> str:
    return str(uuid.uuid4())


class DesignState(enum.StrEnum):
    """Names per contract v1. Values come from packages/feasibility only; the API stores them.
    SUPERSEDED is applied through the engine's supersede rule, and only to a revision that
    had passed."""

    IDEA_ONLY = "IDEA_ONLY"
    NEEDS_INPUT = "NEEDS_INPUT"
    FAILED_CHECKS = "FAILED_CHECKS"
    PASS_SUPPORTED_CHECKS = "PASS_SUPPORTED_CHECKS"
    SUPERSEDED = "SUPERSEDED"


class JobStatus(enum.StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(200))
    intention: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class DesignRevision(Base):
    """Immutable once written, except for the supersession link (and the engine's own
    SUPERSEDED transition for a revision that had passed). An edit inserts a new row.

    `status` and `checks` are the engine's verdict and are never overwritten by an edit;
    `superseded_by_revision_id` records that a newer revision exists, for any status."""

    __tablename__ = "design_revisions"
    __table_args__ = (UniqueConstraint("design_id", "revision_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    design_id: Mapped[str] = mapped_column(String(36), index=True)
    revision_number: Mapped[int] = mapped_column(Integer)
    parent_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey("design_revisions.id"), default=None
    )
    superseded_by_revision_id: Mapped[str | None] = mapped_column(String(36), default=None)
    recipe_id: Mapped[str] = mapped_column(String(100))
    recipe_version: Mapped[str | None] = mapped_column(String(32), default=None)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    inputs_hash: Mapped[str] = mapped_column(String(64))
    geometry_mm: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    checks: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    engine_version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    owner_id: Mapped[str] = mapped_column(String(64), index=True)
    kind: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default=JobStatus.QUEUED.value)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    error_code: Mapped[str | None] = mapped_column(String(64), default=None)
    error_message: Mapped[str | None] = mapped_column(Text, default=None)
    recoverable: Mapped[bool | None] = mapped_column(default=None)
    result_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey("design_revisions.id"), default=None
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope", "key"),
        Index("ix_idempotency_owner_scope", "owner_id", "scope"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(String(64))
    scope: Mapped[str] = mapped_column(String(64))
    key: Mapped[str] = mapped_column(String(255))
    request_hash: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
