"""Runs stages A-H and returns an outcome the API can store as job state."""

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
    garment_class: str
    garment_confidence: float
    material: str
    inspiration_text: str
    provided_measurements: frozenset[str]  # names only, never values
    context_id: str = "ctx-unset"


@dataclass
class PipelineOutcome:
    job_state: str  # "complete" | "failed" (API job states)
    result: str  # designs | needs_input | no_feasible_design | unsupported | blocked | needs_confirmation | error
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

    confirmation = stage_a_confirm_garment(request.garment_class, request.garment_confidence)
    if confirmation.needs_user_confirmation:
        return done("complete", "needs_confirmation", reasons=("GARMENT_CATEGORY_LOW_CONFIDENCE",))

    context = stage_c_load_context(
        request.garment_class, request.material, set(request.provided_measurements)
    )
    if context.rejection:
        return done("complete", "unsupported", reasons=(context.rejection,))

    verdict = screen.screen(request.inspiration_text)
    if not verdict.allowed:
        return done("complete", "blocked", reasons=(verdict.reason,))

    try:
        attributes = stage_b_parse_inspiration(client, request.inspiration_text, tele)
        if not attributes.requested():
            return done(
                "complete", "no_feasible_design", reasons=("NO_SUPPORTED_CHANGE_REQUESTED",)
            )
        candidates = stage_d_propose_candidates(client, attributes, context, tele)
    except StageError as exc:
        return done("failed", "error", reasons=(exc.code,), recoverable=exc.recoverable)

    checked = stage_e_check(
        checker, candidates, request.garment_class, request.material, request.context_id
    )
    ranked = stage_f_relax_and_rank(
        checked, attributes, checker, request.garment_class, request.material, request.context_id
    )
    if not ranked:
        codes = sorted(
            {c for ch in checked for c in (*ch.result.failure_codes, *ch.result.missing_inputs)}
        )
        needs = any(ch.result.status == NEEDS_INPUT for ch in checked)
        if checked and all(ch.result.status == IDEA_ONLY for ch in checked):
            return done("complete", "idea_only", reasons=tuple(codes) or ("IDEA_ONLY",))
        return done(
            "complete",
            "needs_input" if needs else "no_feasible_design",
            reasons=tuple(codes) or ("NO_CANDIDATES",),
        )

    designs = [store.save(c, stage_g_visual_concept(c)) for c in ranked]
    return done("complete", "designs", designs=designs)
