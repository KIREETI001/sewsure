/**
 * Display gates for the cut guide, the photo overlay and DIY steps.
 *
 * These functions only READ states and fields the API returned. They never set, derive or upgrade
 * a design state (CLAUDE.md non-negotiable 2). Every gate fails closed: unknown, missing or
 * inconsistent data means "do not open" or "use the diagram".
 */
import type {
  Calibration,
  CutPlan,
  DesignRevision,
  DesignState,
  DiySteps,
  PhotoRef,
  RecipeStatus,
} from "./types";

// ---- Cut guide access -------------------------------------------------------------------------

export type NextStep =
  "ask_tailor" | "add_measurements" | "choose_supported_change" | "open_newer_revision" | "go_back";

export type CutGuideAccess =
  | { allowed: true }
  | {
      allowed: false;
      /** i18n key suffix explaining why the guide is closed. */
      reason: "idea_only" | "needs_input" | "failed_checks" | "superseded" | "plan_mismatch" | "no_plan";
      next: NextStep;
      /** Set for SUPERSEDED when the API names the newer revision. */
      newerRevisionId: string | null;
    };

const blockedByState: Record<
  Exclude<DesignState, "PASS_SUPPORTED_CHECKS">,
  { reason: "idea_only" | "needs_input" | "failed_checks" | "superseded"; next: NextStep }
> = {
  IDEA_ONLY: { reason: "idea_only", next: "ask_tailor" },
  NEEDS_INPUT: { reason: "needs_input", next: "add_measurements" },
  FAILED_CHECKS: { reason: "failed_checks", next: "choose_supported_change" },
  SUPERSEDED: { reason: "superseded", next: "open_newer_revision" },
};

/**
 * Only a PASS_SUPPORTED_CHECKS revision opens the cut guide, and only with a cut plan that belongs
 * to exactly that revision. Anything else returns the reason and the allowed next step.
 */
export function cutGuideAccess(
  revision: DesignRevision | null | undefined,
  cutPlan: CutPlan | null | undefined,
): CutGuideAccess {
  if (!revision) {
    return { allowed: false, reason: "no_plan", next: "go_back", newerRevisionId: null };
  }
  const status: string = revision.status;
  if (status !== "PASS_SUPPORTED_CHECKS") {
    const blocked = blockedByState[status as keyof typeof blockedByState];
    if (blocked) {
      return {
        allowed: false,
        ...blocked,
        newerRevisionId: revision.superseded_by_revision_id ?? null,
      };
    }
    // A state this build does not know is treated as closed.
    return { allowed: false, reason: "no_plan", next: "go_back", newerRevisionId: null };
  }
  if (!cutPlan) {
    return { allowed: false, reason: "no_plan", next: "go_back", newerRevisionId: null };
  }
  if (
    cutPlan.revision_id !== revision.revision_id ||
    (revision.cut_plan_id !== null && revision.cut_plan_id !== cutPlan.cut_plan_id)
  ) {
    return { allowed: false, reason: "plan_mismatch", next: "go_back", newerRevisionId: null };
  }
  return { allowed: true };
}

// ---- Photo overlay vs dimensioned diagram -----------------------------------------------------

export type DiagramReason =
  | "mode_diagram"
  | "not_calibrated"
  | "rejected"
  | "out_of_tolerance"
  | "missing_calibration_data"
  | "missing_projection"
  | "photo_not_verified";

export interface OverlayProjection {
  /** Screen-independent pixels in the photo per millimetre of garment. */
  scalePxPerMm: number;
  /** Where the cut plan's origin landmark sits in the photo, in photo pixels. */
  originPx: [number, number];
}

export type OverlayDecision =
  | { kind: "overlay"; projection: OverlayProjection }
  | { kind: "diagram"; reason: DiagramReason; apiReason: string | null };

/**
 * The contract's Calibration has a scale but no photo origin. N4 is expected to add
 * `origin_px`. Until it does, no overlay can be placed, so we read it defensively and fall back.
 */
type CalibrationWithOrigin = Calibration & { origin_px?: [number, number] | null };

const finitePositive = (n: unknown): n is number => typeof n === "number" && Number.isFinite(n) && n > 0;

export function overlayDecision(
  cutPlan: CutPlan,
  photo: PhotoRef | null | undefined,
): OverlayDecision {
  const cal = cutPlan.calibration as CalibrationWithOrigin;
  const apiReason = cal.rejection_reason ?? null;
  const diagram = (reason: DiagramReason): OverlayDecision => ({ kind: "diagram", reason, apiReason });

  if (cutPlan.mode !== "calibrated_overlay") return diagram("mode_diagram");
  if (cal.state === "rejected") return diagram("rejected");
  if (cal.state !== "calibrated") return diagram("not_calibrated");

  // The API says "calibrated"; still check its own numbers agree before drawing anything.
  const { max_error_mm: maxError, tolerance_mm: tolerance, scale_px_per_mm: scale } = cal;
  if (
    !finitePositive(scale) ||
    typeof maxError !== "number" ||
    typeof tolerance !== "number" ||
    !Number.isFinite(maxError) ||
    !Number.isFinite(tolerance)
  ) {
    return diagram("missing_calibration_data");
  }
  if (maxError > tolerance) return diagram("out_of_tolerance");

  // Non-negotiable 5: an unverified image never reaches a screen that supports cutting.
  if (!photo || photo.status !== "verified" || photo.photo_id !== cal.reference_photo_id) {
    return diagram("photo_not_verified");
  }

  const origin = cal.origin_px;
  if (
    !Array.isArray(origin) ||
    origin.length !== 2 ||
    !origin.every((v) => typeof v === "number" && Number.isFinite(v))
  ) {
    return diagram("missing_projection");
  }
  return { kind: "overlay", projection: { scalePxPerMm: scale, originPx: [origin[0], origin[1]] } };
}

// ---- Recipe review status ---------------------------------------------------------------------

/**
 * Review status of each recipe, mirrored from `content/recipes/<id>/recipe.yaml`. The DiySteps
 * contract carries a review date but not the recipe's status, so the app keeps this list and a
 * test (recipeStatus.test.ts) fails if it drifts from the YAML. Unknown recipes count as draft.
 */
export const RECIPE_STATUS: Record<string, RecipeStatus> = {
  woven_shirt_crop_v1: "draft",
};

export const recipeStatusOf = (recipeId: string): RecipeStatus => RECIPE_STATUS[recipeId] ?? "draft";

export type GuideMode =
  /** Reviewed recipe, real data. */
  | "executable"
  /** Draft recipe on fixture data: viewable with a "not yet reviewed" label, never a real guide. */
  | "demo_preview"
  /** Draft or retired recipe on live data, or recipe and DIY content disagree. */
  | "blocked";

export function guideMode(
  diySteps: DiySteps | null,
  cutPlan: CutPlan | null,
  provenance: "mock" | "live",
): GuideMode {
  if (!diySteps) return "blocked";
  if (cutPlan && (cutPlan.recipe_id !== diySteps.recipe_id || cutPlan.recipe_version !== diySteps.recipe_version)) {
    return "blocked";
  }
  const status = recipeStatusOf(diySteps.recipe_id);
  if (status === "reviewed") return "executable";
  if (status === "draft" && provenance === "mock") return "demo_preview";
  return "blocked";
}

// ---- Ruler checkpoints ------------------------------------------------------------------------

/** Every ruler checkpoint in the cut plan must be ticked before any irreversible step. */
export function checkpointsComplete(
  cutPlan: CutPlan,
  ticked: Readonly<Record<string, boolean>>,
): boolean {
  return cutPlan.ruler_checkpoints.length > 0 && cutPlan.ruler_checkpoints.every((c) => ticked[c.checkpoint_id] === true);
}

export type StepLock = "checkpoint_required" | null;

/**
 * Irreversible steps (cuts) stay locked until the checkpoints are complete. There is no skip
 * path: nothing in the app writes "skipped" for a cut step.
 */
export function stepLock(
  step: { irreversible: boolean; phase: string },
  checkpointsDone: boolean,
): StepLock {
  const isCut = step.irreversible || step.phase === "cut";
  return isCut && !checkpointsDone ? "checkpoint_required" : null;
}
