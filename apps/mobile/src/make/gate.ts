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

/**
 * No overlay is drawn from the app. The contract's Calibration carries a scale but no projection:
 * N4's fit can include rotation and perspective, per-piece panels sit on different photos, and
 * `max_error_mm` is measured against that fit. Placing lines as `origin + mm * scale` would draw
 * something the validated error does not describe. Until the API returns per-photo, per-piece
 * `points_px`, every plan falls back to the dimensioned diagram. The checks below stay so the
 * reason shown is the real one.
 */
export type OverlayDecision = { kind: "diagram"; reason: DiagramReason; apiReason: string | null };

const finitePositive = (n: unknown): n is number => typeof n === "number" && Number.isFinite(n) && n > 0;

export function overlayDecision(
  cutPlan: CutPlan,
  photo: PhotoRef | null | undefined,
): OverlayDecision {
  const cal: Calibration = cutPlan.calibration;
  const apiReason = cal.rejection_reason ?? null;
  const diagram = (reason: DiagramReason): OverlayDecision => ({ kind: "diagram", reason, apiReason });

  if (cutPlan.mode !== "calibrated_overlay") return diagram("mode_diagram");
  if (cal.state === "rejected") return diagram("rejected");
  if (cal.state !== "calibrated") return diagram("not_calibrated");

  const { max_error_mm: maxError, tolerance_mm: tolerance, scale_px_per_mm: scale } = cal;
  if (!finitePositive(scale) || !finitePositive(tolerance) || typeof maxError !== "number" || !Number.isFinite(maxError)) {
    return diagram("missing_calibration_data");
  }
  if (maxError > tolerance) return diagram("out_of_tolerance");

  // Non-negotiable 5: an unverified image never reaches a screen that supports cutting.
  if (!photo || photo.status !== "verified" || photo.photo_id !== cal.reference_photo_id) {
    return diagram("photo_not_verified");
  }
  // Photo size and a projection from the API are both needed before lines could be placed. The
  // contract provides neither yet, so this is always the diagram.
  return diagram("missing_projection");
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
  /** Reviewed recipe on live data. The only mode that reads as a real guide. */
  | "executable"
  /** Fixture data, or a draft recipe: viewable with a demo label in demo builds, never a real guide. */
  | "demo_preview"
  /** Draft or retired recipe on live data, or recipe and DIY content disagree. */
  | "blocked";

/** Demo previews of draft recipes exist only in development builds or an explicit demo flag. */
export const isDemoBuild = (): boolean =>
  (typeof __DEV__ !== "undefined" && __DEV__) || process.env.EXPO_PUBLIC_SEWSURE_DEMO === "1";

export type BlockedReason = "no_steps" | "version_mismatch" | "not_reviewed" | "no_checkpoint_step";

/** A cut with no ruler checkpoint step before it breaks the contract: nothing could unlock it. */
const lacksCheckpointStep = (d: DiySteps): boolean =>
  d.steps.some((s) => s.irreversible || s.phase === "cut") && !d.steps.some((s) => s.phase === "ruler_checkpoint");

export function blockedReason(diySteps: DiySteps | null, cutPlan: CutPlan | null): BlockedReason {
  if (!diySteps) return "no_steps";
  if (cutPlan && (cutPlan.recipe_id !== diySteps.recipe_id || cutPlan.recipe_version !== diySteps.recipe_version)) {
    return "version_mismatch";
  }
  if (lacksCheckpointStep(diySteps)) return "no_checkpoint_step";
  return "not_reviewed";
}

export function guideMode(
  diySteps: DiySteps | null,
  cutPlan: CutPlan | null,
  provenance: "mock" | "live",
  demoAllowed: boolean = isDemoBuild(),
): GuideMode {
  if (!diySteps) return "blocked";
  if (cutPlan && (cutPlan.recipe_id !== diySteps.recipe_id || cutPlan.recipe_version !== diySteps.recipe_version)) {
    return "blocked";
  }
  if (lacksCheckpointStep(diySteps)) return "blocked";
  const status = recipeStatusOf(diySteps.recipe_id);
  // Fixture data never reads as a real guide, whatever the recipe status.
  if (provenance === "mock") return (status === "draft" || status === "reviewed") && demoAllowed ? "demo_preview" : "blocked";
  return status === "reviewed" ? "executable" : "blocked";
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

// ---- Step order and locks ---------------------------------------------------------------------

export type StepLockReason = "earlier_required" | "checkpoint_required" | "cut_required";

export interface ResolvedStep<S> {
  step: S;
  done: boolean;
  lock: StepLockReason | null;
}

interface StepLike {
  step_id: string;
  order: number;
  phase: string;
  irreversible: boolean;
}

/** True when every step before `step` (other than the checkpoint step, which is derived) is ticked. */
const earlierDone = <S extends StepLike>(sorted: readonly S[], step: S, ticked: Readonly<Record<string, boolean>>) =>
  sorted.every((s) => s.order >= step.order || s.phase === "ruler_checkpoint" || ticked[s.step_id] === true);

/** Checkpoints can be ticked only once the steps before the first cut are done. */
export function checkpointsUnlocked(steps: readonly StepLike[], ticked: Readonly<Record<string, boolean>>): boolean {
  const sorted = [...steps].sort((a, b) => a.order - b.order);
  const firstCut = sorted.find((s) => s.irreversible || s.phase === "cut");
  return firstCut ? earlierDone(sorted, firstCut, ticked) : true;
}

/**
 * Resolves done and lock for every step, in order.
 * - The ruler checkpoint step has no tick of its own: it is done when every checkpoint is ticked
 *   (or a later cut is already recorded, e.g. restored from the server after a reinstall).
 * - Cut steps stay locked until every earlier step is done, then until the checkpoints are complete.
 * - Steps after a cut stay locked until that cut is done.
 * A step already recorded done is shown done, never locked: the lock stops new actions only.
 */
export function resolveSteps<S extends StepLike>(
  steps: readonly S[],
  checkpointsDone: boolean,
  ticked: Readonly<Record<string, boolean>>,
): ResolvedStep<S>[] {
  const sorted = [...steps].sort((a, b) => a.order - b.order);
  const cutTicked = (s: S) => (s.irreversible || s.phase === "cut") && ticked[s.step_id] === true;
  const out: ResolvedStep<S>[] = [];
  let cutPending = false;
  for (const step of sorted) {
    const isCut = step.irreversible || step.phase === "cut";
    let done: boolean;
    let lock: StepLockReason | null = null;
    if (step.phase === "ruler_checkpoint") {
      done = (checkpointsDone && earlierDone(sorted, step, ticked)) || sorted.some((s) => s.order > step.order && cutTicked(s));
    } else {
      done = ticked[step.step_id] === true;
      if (!done) {
        if (isCut && !earlierDone(sorted, step, ticked)) lock = "earlier_required";
        else if (isCut && !checkpointsDone) lock = "checkpoint_required";
        else if (cutPending) lock = "cut_required";
      }
    }
    out.push({ step, done, lock });
    if (isCut) cutPending = !done;
  }
  return out;
}
