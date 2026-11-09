import type { components } from "../../../../packages/contracts/generated/ts/sewsure.v1";
import type { StudioApi } from "./studio";
import type { IntakeDraft } from "@/state/intakeStore";
import { newIdempotencyKey, useStudioStore } from "@/state/studioStore";
import { buildMeasurementRecords } from "@/intake/validation";
import { garmentSpecsFor, INSPIRATION_ONLY } from "@/intake/measurements";
import { localRequest } from "./localTransport";
import type { MakeBundle } from "@/make/types";
import { StudioApiError } from "@/studio/errors";

type Schemas = components["schemas"];
type Project = Schemas["project.schema"];
type MeasurementsInput = Schemas["MeasurementsInput"];

// UI adapters construct existing generated contract requests, never a new wire format.
let requestedFeatures: NonNullable<Schemas["inspiration.schema"]["requested_features"]> = {};

export async function prepareLocalProject(
  draft: IntakeDraft,
  targetMm: number,
  placketMm: number | null,
  transformation: "crop" | "lengthen" | "other",
): Promise<string> {
  if (!draft.category) throw new Error("Choose a garment category");
  const categories: Record<string, Schemas["garment.schema"]["category"]> = {
    shirt: "woven_shirt",
    tee: "jersey_tee",
    jacket: "other",
    trousers: "other",
    skirt: "other",
    dress: "other",
  };
  const project = await localRequest<Project>(
    "/projects",
    "POST",
    {
      title: "Synthetic local demo",
      garment: {
        category: categories[draft.category],
        fabric_family: draft.category === "tee" ? "knit" : "woven",
      },
    } satisfies Schemas["ProjectCreate"],
    newIdempotencyKey(),
  );
  const garment = Object.fromEntries(
    buildMeasurementRecords(
      INSPIRATION_ONLY.includes(draft.category) ? [] : garmentSpecsFor(draft.category),
      draft.measurements,
    ).map((m) => [
      m.key,
      {
        value_mm: m.value_mm,
        origin: m.origin,
        confirmed_at: m.confirmed_at,
      },
    ]),
  );
  if (draft.category === "shirt" && placketMm !== null) {
    garment.placket_end_from_shoulder = {
      value_mm: placketMm,
      origin: "user_entered",
      confirmed_at: new Date().toISOString(),
    };
  }
  await localRequest(`/projects/${project.project_id}/measurements`, "PUT", {
    units: "mm",
    garment,
  } satisfies MeasurementsInput);
  requestedFeatures = { transformation, target_finished_length_mm: targetMm };
  // Keep the non-sensitive demo request options over page refreshes alongside this tab's session.
  if (typeof sessionStorage !== "undefined")
    sessionStorage.setItem("sewsure.local.features", JSON.stringify(requestedFeatures));
  useStudioStore.getState().startAttempt(project.project_id, newIdempotencyKey());
  return project.project_id;
}

const mock = <T>(data: T) => ({ data, provenance: "mock" as const });

export const localStudioApi: StudioApi = {
  // Synthetic demo: keep visible mock badges even though local engine calls are real.
  mode: "mock",
  async generate(projectId, request, opts) {
    const source = request.inspiration;
    if (source.kind === "image") throw new Error("Local text demo does not analyse images");
    const saved =
      typeof sessionStorage !== "undefined"
        ? sessionStorage.getItem("sewsure.local.features")
        : null;
    const body = {
      inspiration: {
        text: source.kind === "text" ? source.text : source.prompt,
        requested_features: saved ? JSON.parse(saved) : requestedFeatures,
        skill_level: "beginner",
        tools: [],
        surprise_me: source.kind === "surprise",
      },
    } satisfies Schemas["GenerateRequest"];
    return mock(
      await localRequest<Schemas["job.schema"]>(
        `/projects/${projectId}/generate`,
        "POST",
        body,
        opts.idempotencyKey,
      ),
    );
  },
  async getJob(id) {
    return mock(await localRequest<Schemas["job.schema"]>(`/jobs/${id}`));
  },
  async listDesigns(id) {
    return mock(await localRequest<Schemas["DesignList"]>(`/projects/${id}/designs`));
  },
  async getRevision(id) {
    return mock(await localRequest<Schemas["design-revision.schema"]>(`/revisions/${id}`));
  },
  async createRevision(id, body, opts) {
    return mock(
      await localRequest<Schemas["design-revision.schema"]>(
        `/designs/${id}/revisions`,
        "POST",
        body,
        opts.idempotencyKey,
      ),
    );
  },
};

export async function loadLocalMakeBundle(revisionId: string): Promise<MakeBundle> {
  const revision = await localRequest<MakeBundle["revision"]>(`/revisions/${revisionId}`);
  const base: MakeBundle = {
    provenance: "mock",
    revision,
    cutPlan: null,
    diySteps: null,
    serverProgress: null,
    photo: null,
  };
  try {
    base.cutPlan = await localRequest<NonNullable<MakeBundle["cutPlan"]>>(
      `/revisions/${revisionId}/cut-plan`,
    );
    base.diySteps = await localRequest<NonNullable<MakeBundle["diySteps"]>>(
      `/revisions/${revisionId}/diy-steps`,
    );
  } catch (error) {
    if (!(error instanceof StudioApiError) || error.status !== 409) throw error;
    base.cutPlanError = { code: error.code, recoverable: error.recoverable };
  }
  return base;
}
