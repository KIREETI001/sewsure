"""Runs stages A-H and returns an outcome the API can store as job state.

`result` uses the contract `Job.result.outcome` values: designs | needs_input |
no_feasible_design | unsupported | blocked | needs_confirmation. A model or stage
failure is a failed job (`job_state="failed"`, result "error", recoverable).
`reasons` are contract FailureCodes where the engine or stage C supplied them,
plus pipeline-local codes (GARMENT_CATEGORY_LOW_CONFIDENCE, PROMPT_ATTACK_SUSPECTED,
NO_SUPPORTED_CHANGE_REQUESTED, MODEL_*), which are not in the contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .feasibility_port import IDEA_ONLY, NEEDS_INPUT, FeasibilityChecker
from .model_client import ModelClient
from .safety import SafetyScreen
from .stages import (
    RevisionStore,
    SavedRevision,
    StageError,
    Telemetry,
    log_call_summary,
    stage_a_confirm_garment,
    stage_b_parse_inspiration,
    stage_c_load_context,
    stage_d_propose_candidates,
    stage_e_check,
    stage_f_relax_and_rank,
    stage_g_visual_concept,
)


@dataclass(frozen=True)
class DesignRequest:
    garment_category: str  # contract category, e.g. "woven_shirt"
    garment_confidence: float
    fabric_family: str  # contract fabric family, e.g. "woven"
    inspiration_text: str
    provided_dimensions: frozenset[str]  # GarmentDimension names only, never values
    context_id: str = "ctx-unset"


@dataclass
class PipelineOutcome:
    job_state: str  # "complete" | "failed" (contract job states)
    result: str  # contract outcome, or "error" when job_state == "failed"
    designs: list[SavedRevision] = field(default_factory=list)
    reasons: tuple[str, ...] = ()
    recoverable: bool = False
    telemetry: Telemetry = field(default_factory=Telemetry)


def run_pipeline(
    request: DesignRequest,
    *,
    client: ModelClient,
    checker: FeasibilityChecker,
    screen: SafetyScreen,
    store: RevisionStore | None = None,
) -> PipelineOutcome:
    store = store or RevisionStore()
    tele = Telemetry()

    def done(job_state: str, result: str, **kw) -> PipelineOutcome:
        log_call_summary(tele, kw["designs"][0].revision_id if kw.get("designs") else None)
        return PipelineOutcome(job_state, result, telemetry=tele, **kw)

    confirmation = stage_a_confirm_garment(request.garment_category, request.garment_confidence)
    if confirmation.needs_user_confirmation:
        return done("complete", "needs_confirmation", reasons=("GARMENT_CATEGORY_LOW_CONFIDENCE",))

    context = stage_c_load_context(
        request.garment_category, request.fabric_family, set(request.provided_dimensions)
    )
    if context.rejection:
        return done("complete", "unsupported", reasons=(context.rejection,))

    verdict = screen.screen(request.inspiration_text)
    if not verdict.allowed:
        return done("complete", "blocked", reasons=(verdict.reason,))

    try:
        attributes = stage_b_parse_inspiration(client, request.inspiration_text, tele)
        if attributes.requested_crop() is None:
            # Nothing the reviewed recipes can do (sleeves, shaping, or no clear change).
            return done("complete", "unsupported", reasons=("NO_SUPPORTED_CHANGE_REQUESTED",))
        candidates = stage_d_propose_candidates(client, attributes, context, tele)
    except StageError as exc:
        return done("failed", "error", reasons=(exc.code,), recoverable=exc.recoverable)

    checked = stage_e_check(
        checker, candidates, request.garment_category, request.fabric_family, request.context_id
    )
    ranked = stage_f_relax_and_rank(
        checked,
        attributes,
        checker,
        request.garment_category,
        request.fabric_family,
        request.context_id,
    )
    if not ranked:
        codes = sorted(
            {c for ch in checked for c in (*ch.result.failure_codes, *ch.result.missing_dimensions)}
        )
        if checked and all(ch.result.status == IDEA_ONLY for ch in checked):
            return done("complete", "unsupported", reasons=tuple(codes) or ("IDEA_ONLY",))
        needs = any(ch.result.status == NEEDS_INPUT for ch in checked)
        return done(
            "complete",
            "needs_input" if needs else "no_feasible_design",
            reasons=tuple(codes) or ("NO_CANDIDATES",),
        )

    designs = [store.save(c, stage_g_visual_concept(c)) for c in ranked]
    return done("complete", "designs", designs=designs)
