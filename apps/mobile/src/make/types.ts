/**
 * Types for the cut guide and DIY screens. They are the generated contract types, re-exported
 * so screens never declare API shapes themselves (CLAUDE.md non-negotiable 9).
 */
import type { components } from "../../../../packages/contracts/generated/ts/sewsure.v1";

type Schemas = components["schemas"];

export type DesignState = Schemas["design-state.schema"];
export type DesignRevision = Schemas["design-revision.schema"];
export type CutPlan = Schemas["cut-plan.schema"];
export type DiySteps = Schemas["diy-steps.schema"];
export type DiyProgress = Schemas["diy-progress.schema"];
export type PhotoRef = Schemas["photo-ref.schema"];

export type CutLine = CutPlan["pieces"][number]["lines"][number];
export type RulerCheckpoint = CutPlan["ruler_checkpoints"][number];
export type Calibration = CutPlan["calibration"];
export type DiyStep = DiySteps["steps"][number];

export type RecipeStatus = "draft" | "reviewed" | "retired";

/** Everything the make screens need for one revision. `provenance` "mock" means fixture data. */
export interface MakeBundle {
  provenance: "mock" | "live";
  revision: DesignRevision;
  /** Null when the API returned no cut plan (not an error for non-passing revisions). */
  cutPlan: CutPlan | null;
  diySteps: DiySteps | null;
  /** Progress the server already holds. Local progress is merged over it. */
  serverProgress: DiyProgress | null;
  /** The 409 the cut-plan endpoint returned (REVISION_STALE or REVISION_NOT_PASSING), if any. */
  cutPlanError?: { code: string; recoverable: boolean } | null;
  /** The garment photo the cut plan was calibrated against, if the API returned it. */
  photo: PhotoRef | null;
}
