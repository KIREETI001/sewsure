"""Stages A-H (blueprint section 4.2) as small, separately testable functions.

Model-facing stages (B, D) validate every response against a JSON schema and
fail closed. Stage E is the only place a design's feasibility is decided, and
that decision belongs to the engine behind FeasibilityChecker.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sewsure_feasibility import ConstraintResult, DesignState

from .feasibility_port import FeasibilityChecker, FeasibilityRequest
from .model_client import ModelClient, ModelError, ModelRequest, ModelResponse
from .schemas import (
    INSPIRATION_VALIDATOR,
    MAX_DESIGNS_RETURNED,
    RECIPE_ALLOW_LIST,
    REQUIRED_DIMENSIONS,
    SUPPORTED_GARMENTS,
    SUPPORTED_MATERIALS,
    Candidate,
    InspirationAttributes,
    validate_proposals,
)

log = logging.getLogger("sewsure.ai")
PROMPT_DIR = Path(__file__).parent / "prompts"
PROMPT_VERSION = "v0"
MIN_GARMENT_CONFIDENCE = 0.7
MODEL_ATTEMPTS = 2  # model calls are idempotent, so one retry is safe


class StageError(Exception):
    """A stage could not complete. `recoverable` means the job may be retried."""

    def __init__(self, code: str, recoverable: bool = True) -> None:
        super().__init__(code)
        self.code = code
        self.recoverable = recoverable


@dataclass
class CallRecord:
    stage: str
    deployment: str = ""
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    parse_ok: bool = False
    schema_ok: bool = False
    recipe_ids_seen: int = 0
    recipe_ids_valid: int = 0
    error: str = ""


@dataclass
class Telemetry:
    """Per-call metrics for the eval harness. Never stores prompts or user text."""

    request_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    calls: list[CallRecord] = field(default_factory=list)


def load_prompt(stage_name: str, version: str = PROMPT_VERSION) -> str:
    return (PROMPT_DIR / f"{stage_name}_{version}.md").read_text(encoding="utf-8")


# ------------------------------------------------------------------ A ----


@dataclass(frozen=True)
class GarmentConfirmation:
    garment_class: str
    needs_user_confirmation: bool


def stage_a_confirm_garment(garment_class: str, confidence: float) -> GarmentConfirmation:
    """Low confidence asks the user to confirm the category rather than guessing."""
    return GarmentConfirmation(garment_class, confidence < MIN_GARMENT_CONFIDENCE)


# ------------------------------------------------------------------ model plumbing ----


def _call_model(
    client: ModelClient,
    request: ModelRequest,
    is_valid: Callable[[Any], bool],
    telemetry: Telemetry,
) -> dict[str, Any]:
    rec = CallRecord(stage=request.stage)
    telemetry.calls.append(rec)
    response: ModelResponse | None = None
    last_error = "MODEL_FAILED"
    for _ in range(MODEL_ATTEMPTS):
        started = time.perf_counter()
        try:
            response = client.complete(request)
        except ModelError as exc:
            last_error = exc.code
            continue
        rec.deployment = response.deployment
        rec.latency_ms = response.latency_ms or (time.perf_counter() - started) * 1000
        rec.cost_usd = response.cost_usd
        break
    if response is None:
        rec.error = last_error
        raise StageError(last_error)
    try:
        payload = json.loads(response.text)
        rec.parse_ok = True
    except (json.JSONDecodeError, TypeError):
        rec.error = "MODEL_OUTPUT_NOT_JSON"
        raise StageError(rec.error) from None
    if request.stage == "D":
        _count_recipe_ids(payload, rec)
    if is_valid(payload):
        rec.schema_ok = True
        return payload
    rec.error = "MODEL_OUTPUT_SCHEMA_INVALID"
    raise StageError(rec.error)


def _count_recipe_ids(payload: Any, rec: CallRecord) -> None:
    """Recipe-ID validity is measured on whatever IDs the model emitted, before
    validation rejects the response."""
    if not isinstance(payload, dict) or not isinstance(payload.get("proposals"), list):
        return
    for prop in payload["proposals"]:
        rid = prop.get("recipe_id") if isinstance(prop, dict) else None
        rec.recipe_ids_seen += 1
        if isinstance(rid, str) and rid in RECIPE_ALLOW_LIST:
            rec.recipe_ids_valid += 1


def log_call_summary(telemetry: Telemetry, revision_id: str | None = None) -> None:
    for c in telemetry.calls:
        log.info(
            "model_call request_id=%s revision_id=%s stage=%s deployment=%s "
            "latency_ms=%.1f cost_usd=%.6f error=%s",
            telemetry.request_id,
            revision_id or "-",
            c.stage,
            c.deployment,
            c.latency_ms,
            c.cost_usd,
            c.error or "-",
        )


# ------------------------------------------------------------------ B ----


def stage_b_parse_inspiration(
    client: ModelClient, inspiration_text: str, telemetry: Telemetry
) -> InspirationAttributes:
    request = ModelRequest(
        stage="B",
        system_prompt=load_prompt("stage_b"),
        user_payload={"inspiration_text": inspiration_text},
        schema_name="inspiration_attributes",
        prompt_version=PROMPT_VERSION,
    )
    payload = _call_model(client, request, INSPIRATION_VALIDATOR.is_valid, telemetry)
    return InspirationAttributes(**payload)


# ------------------------------------------------------------------ C ----


@dataclass(frozen=True)
class DesignContext:
    allowed_recipes: dict[str, dict[str, tuple[str, ...]]]
    missing_dimensions: tuple[str, ...]
    rejection: str = ""  # a contract FailureCode; non-empty means no model call is made


def stage_c_load_context(
    garment_category: str,
    fabric_family: str,
    provided_dimensions: set[str],
) -> DesignContext:
    """Reject unsupported garment/material combinations before spending a model call.
    Only dimension *names* are used here; values stay with the engine."""
    if garment_category not in SUPPORTED_GARMENTS:
        return DesignContext({}, (), "UNSUPPORTED_GARMENT_CATEGORY")
    if fabric_family not in SUPPORTED_MATERIALS:
        return DesignContext({}, (), "UNSUPPORTED_MATERIAL")
    missing = tuple(sorted(REQUIRED_DIMENSIONS - provided_dimensions))
    return DesignContext(dict(RECIPE_ALLOW_LIST), missing)


# ------------------------------------------------------------------ D ----


def stage_d_propose_candidates(
    client: ModelClient,
    attributes: InspirationAttributes,
    context: DesignContext,
    telemetry: Telemetry,
) -> list[Candidate]:
    request = ModelRequest(
        stage="D",
        system_prompt=load_prompt("stage_d"),
        user_payload={
            "attributes": attributes.model_dump(),
            "allowed_recipes": {
                k: {p: list(v) for p, v in ps.items()} for k, ps in context.allowed_recipes.items()
            },
        },
        schema_name="ai_candidate_proposal",
        prompt_version=PROMPT_VERSION,
    )
    payload = _call_model(client, request, validate_proposals, telemetry)
    seen: set[tuple] = set()
    out: list[Candidate] = []
    for raw in payload["proposals"]:
        cand = Candidate(recipe_id=raw["recipe_id"], parameters=raw["parameters"])
        if cand.key() not in seen:  # distinct only
            seen.add(cand.key())
            out.append(cand)
    return out


# ------------------------------------------------------------------ E ----


@dataclass(frozen=True)
class CheckedCandidate:
    candidate: Candidate
    result: ConstraintResult
    relaxed_from: Candidate | None = None


def stage_e_check(
    checker: FeasibilityChecker, candidates: list[Candidate], context_id: str
) -> list[CheckedCandidate]:
    """Ask the engine about each candidate. Its ConstraintResult is kept as returned.
    An engine exception fails the job (recoverable); it is never read as a pass or a fail."""
    out = []
    for cand in candidates:
        try:
            result = checker.check(
                FeasibilityRequest(
                    recipe_id=cand.recipe_id,
                    parameters=cand.parameters,
                    revision_context_id=context_id,
                )
            )
        except Exception as exc:
            raise StageError("ENGINE_ERROR") from exc
        out.append(CheckedCandidate(cand, result))
    return out


# ------------------------------------------------------------------ F ----


def _ease(candidate: Candidate) -> Candidate | None:
    """One notch less demanding, or None if already minimal."""
    levels_by_param = RECIPE_ALLOW_LIST[candidate.recipe_id]
    params = dict(candidate.parameters)
    changed = False
    for name, levels in levels_by_param.items():
        idx = levels.index(params[name])
        if idx > 0:
            params[name] = levels[idx - 1]
            changed = True
    return Candidate(recipe_id=candidate.recipe_id, parameters=params) if changed else None


def stage_f_relax_and_rank(
    checked: list[CheckedCandidate],
    attributes: InspirationAttributes,
    checker: FeasibilityChecker,
    context_id: str,
) -> list[CheckedCandidate]:
    """Retry FAILED_CHECKS candidates one notch easier (once), then rank survivors, max three.

    Only candidates the engine marked FAILED_CHECKS are relaxed; IDEA_ONLY, NEEDS_INPUT
    and SUPERSEDED are not. Hard gates run first: only PASS candidates are ranked. The
    score is an initial, untuned preference ordering, not a probability of success.
    """
    pool = list(checked)
    if (
        sum(c.result.status is DesignState.PASS_SUPPORTED_CHECKS for c in pool)
        < MAX_DESIGNS_RETURNED
    ):
        known = {c.candidate.key() for c in pool}
        eased: list[tuple[Candidate, Candidate]] = []
        for c in pool:
            if c.result.status is DesignState.FAILED_CHECKS:
                easier = _ease(c.candidate)
                if easier is not None and easier.key() not in known:
                    known.add(easier.key())
                    eased.append((c.candidate, easier))
        rechecked = stage_e_check(checker, [e for _, e in eased], context_id)
        pool += [
            CheckedCandidate(r.candidate, r.result, relaxed_from=orig)
            for (orig, _), r in zip(eased, rechecked, strict=True)
        ]

    survivors = [c for c in pool if c.result.status is DesignState.PASS_SUPPORTED_CHECKS]
    wanted = attributes.requested_crop()

    def score(c: CheckedCandidate) -> float:
        return 1.0 if c.candidate.parameters.get("crop_level") == wanted else 0.0

    survivors.sort(key=lambda c: (-score(c), repr(c.candidate.key())))
    return survivors[:MAX_DESIGNS_RETURNED]


# ------------------------------------------------------------------ G ----


@dataclass(frozen=True)
class VisualConcept:
    candidate: Candidate
    label: str = "Approximate concept. Not a pattern and not for cutting."
    image_ref: str | None = None  # image generation is not wired in v0


def stage_g_visual_concept(checked: CheckedCandidate) -> VisualConcept:
    """Build the concept from the accepted structured spec only (never from raw user text)."""
    return VisualConcept(candidate=checked.candidate)


# ------------------------------------------------------------------ H ----


@dataclass(frozen=True)
class SavedRevision:
    revision_id: str
    candidate: Candidate
    engine_result: ConstraintResult  # the engine's result, unchanged
    concept: VisualConcept

    @property
    def engine_status(self) -> DesignState:
        return self.engine_result.status


class RevisionStore:
    """In-memory stand-in for K2's persistence. Revisions are immutable: saving
    always mints a new ID."""

    def __init__(self) -> None:
        self._items: dict[str, SavedRevision] = {}

    def save(self, checked: CheckedCandidate, concept: VisualConcept) -> SavedRevision:
        rev = SavedRevision(uuid.uuid4().hex, checked.candidate, checked.result, concept)
        self._items[rev.revision_id] = rev
        return rev

    def get(self, revision_id: str) -> SavedRevision | None:
        return self._items.get(revision_id)
