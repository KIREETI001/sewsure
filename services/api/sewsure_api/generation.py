"""Generation job runner and the proposer seam.

A `Proposer` turns a garment and an inspiration into up to three (recipe_id, parameters)
proposals. K3's AI pipeline plugs in here later. The default `RuleProposer` is deterministic and
uses no model: it only maps what the user asked for to the reviewed recipe. Whatever is proposed,
the feasibility engine decides the state of each design.
"""

from dataclasses import dataclass
from typing import Any, Protocol

from sqlalchemy.orm import Session, sessionmaker

from sewsure_api import services
from sewsure_api.models import Garment

# recipe.yaml (content/recipes/woven_shirt_crop_v1) default hem allowance, in mm.
RECIPE_DEFAULT_HEM_ALLOWANCE_MM = 30
CROP_RECIPE = "woven_shirt_crop_v1"


@dataclass(frozen=True)
class Proposal:
    recipe_id: str | None  # None = no reviewed recipe fits (the design stays IDEA_ONLY)
    parameters: dict[str, Any]
    title: str


class Proposer(Protocol):
    def propose(
        self,
        garment: Garment,
        measurements: dict[str, Any],
        inspiration: dict[str, Any],
    ) -> list[Proposal]:
        """Return up to three (recipe_id, millimetre parameters, title) proposals.

        This is the seam for K3's pipeline: it validates its own output and returns plain
        proposals. It does not evaluate or store anything; `services.evaluate_and_store` is the
        only code that runs the engine and persists a verdict, so there is one evaluation path.
        `measurements` maps dimension name to the stored MeasurementValue dict."""
        ...


class RuleProposer:
    def propose(
        self,
        garment: Garment,
        measurements: dict[str, Any],
        inspiration: dict[str, Any],
    ) -> list[Proposal]:
        features = inspiration.get("requested_features") or {}
        transformation = features.get("transformation")
        target = features.get("target_finished_length_mm")
        original = (measurements.get("shoulder_to_hem") or {}).get("value_mm")
        lengthens_nothing = (
            transformation == "lengthen"
            and target is not None
            and original is not None
            and target <= original
        )
        if lengthens_nothing:
            # Contradictory: a "lengthen" that is not longer than the garment must never reach
            # the crop recipe, which would shorten it. It stays an idea.
            return [Proposal(None, {}, "Idea only: request does not lengthen")]
        if transformation in ("crop", "lengthen") and target is not None:
            verb = "Cropped" if transformation == "crop" else "Lengthened"
            return [
                Proposal(
                    CROP_RECIPE,
                    {
                        "finished_length_mm": target,
                        "hem_allowance_mm": RECIPE_DEFAULT_HEM_ALLOWANCE_MM,
                        "hem_finish": "double_fold",
                    },
                    f"{verb} shirt, {target:g} mm",
                )
            ]
        return [Proposal(None, {}, "Idea only: no reviewed recipe yet")]


def _outcome(statuses: list[str]) -> str:
    if "PASS_SUPPORTED_CHECKS" in statuses:
        return "designs"
    if "NEEDS_INPUT" in statuses:
        return "needs_input"
    if "FAILED_CHECKS" in statuses:
        return "no_feasible_design"
    return "unsupported"


def run_generate_job(
    session_factory: sessionmaker[Session],
    proposer: Proposer,
    job_id: str,
    ruler_tolerance_mm: float,
) -> None:
    """Run one queued generate job in its own transaction. Failures become a recoverable,
    user-safe `failed` job; nothing about the garment or measurements is logged or stored."""
    with session_factory() as db:
        job = db.get(services.Job, job_id)
        if job is None or job.status != "queued":
            return
        services.start_job(job)
        db.commit()
        try:
            project = db.get(services.Project, job.project_id)
            assert project is not None
            garment = services.project_garment(db, project)
            statuses: list[str] = []
            ids: list[str] = []
            mset = services.current_measurements(db, project)
            proposals = proposer.propose(
                garment, dict(mset.garment) if mset else {}, job.request.get("inspiration", {})
            )[:3]
            for rank, proposal in enumerate(proposals, start=1):
                revision = services.create_design(
                    db,
                    project=project,
                    job_id=job.id,
                    rank=rank,
                    title=proposal.title,
                    recipe_id=proposal.recipe_id,
                    params=proposal.parameters,
                    ruler_tolerance_mm=ruler_tolerance_mm,
                )
                statuses.append(revision.status)
                ids.append(revision.design_id)
            services.complete_job(job, _outcome(statuses), ids)
            db.commit()
        except Exception:
            db.rollback()
            job = db.get(services.Job, job_id)
            assert job is not None
            services.fail_job(
                job, "GENERATION_FAILED", "Generation could not finish. Try again.", True
            )
            db.commit()
