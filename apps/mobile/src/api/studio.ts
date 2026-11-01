/**
 * Studio API client layer (screens 5-6): generate, poll, list designs, read and create revisions.
 *
 * Screens only call `getStudioApi()`. K2 swaps the live client in with `setStudioApi`; the shapes
 * are the generated contract types, so nothing else changes. Every response is wrapped in an
 * Envelope whose `provenance` drives the visible mock marker.
 */
import { StudioApiError } from "@/studio/errors";
import { cloneScenario, DEFAULT_SCENARIO, type ScenarioName } from "@/studio/scenarios";
import type {
  DesignCandidate,
  DesignList,
  DesignRevision,
  Job,
  Parameters,
  RevisionCreate,
} from "@/studio/types";
import type { Envelope, InspirationInput } from "./types";

export interface StudioApi {
  /** "mock" means every response comes from a fixture; the UI marks it as such. */
  readonly mode: "mock" | "live";
  /** Same idempotency key returns the original job. A new key starts a new job. */
  generate(
    projectId: string,
    request: { inspiration: InspirationInput },
    opts: { idempotencyKey: string },
  ): Promise<Envelope<Job>>;
  getJob(jobId: string): Promise<Envelope<Job>>;
  listDesigns(projectId: string): Promise<Envelope<DesignList>>;
  getRevision(revisionId: string): Promise<Envelope<DesignRevision>>;
  /**
   * Creates a new revision from `body.parent_revision_id` and returns it already checked. The
   * server's feasibility engine sets the state; the client never does. 409 when the parent is not
   * the design's current revision.
   */
  createRevision(
    designId: string,
    body: RevisionCreate,
    opts: { idempotencyKey: string },
  ): Promise<Envelope<DesignRevision>>;
}

// ---------------------------------------------------------------------------------------------
// Fixture-backed client.
//
// MOCK ONLY. `createRevision` below stands in for the server's feasibility engine so the edit
// flow can be exercised without a backend. The real state always comes from packages/feasibility
// via the API. Nothing in this section ships behaviour to the live path.
// ---------------------------------------------------------------------------------------------

const mock = <T>(data: T): Envelope<T> => ({ data, provenance: "mock" });

/** Stages the mock job walks through before it settles, in contract order (§4.2). */
const MOCK_STAGES: NonNullable<Job["stage"]>[] = [
  "A_garment",
  "C_load_inputs",
  "D_propose",
  "E_check",
  "G_preview",
];

interface MockState {
  scenario: ScenarioName;
  jobs: Map<string, { job: Job; polls: number; scenario: ScenarioName }>;
  keys: Map<string, string>;
  designs: DesignList;
  revisions: Map<string, DesignRevision>;
  generateCalls: number;
  jobCounter: number;
  revisionCounter: number;
}

const freshState = (scenario: ScenarioName): MockState => {
  const s = cloneScenario(scenario);
  return {
    scenario,
    jobs: new Map(),
    keys: new Map(),
    designs: s.designs,
    revisions: new Map(s.revisions.map((r) => [r.revision_id, r])),
    generateCalls: 0,
    jobCounter: 0,
    revisionCounter: 0,
  };
};

let state = freshState(DEFAULT_SCENARIO);

/** Picks the fixture scenario the mock serves. Resets mock state. */
export const setMockScenario = (scenario: ScenarioName): void => {
  state = freshState(scenario);
};

export const getMockScenario = (): ScenarioName => state.scenario;

/** The scenario that follows a failed first attempt, so retry can be exercised end to end. */
const RECOVERS_TO: Partial<Record<ScenarioName, ScenarioName>> = {
  job_failed_no_designs: "woven_shirt_crop_pass",
};

const notFound = (what: string): StudioApiError =>
  new StudioApiError(
    { code: "NOT_FOUND", message: `${what} was not found.`, recoverable: false },
    404,
  );

const MM_KEY = /_mm$/;

export const mockStudioApi: StudioApi = {
  mode: "mock",

  async generate(projectId, _request, { idempotencyKey }) {
    const existing = state.keys.get(idempotencyKey);
    const prior = existing ? state.jobs.get(existing) : undefined;
    if (prior) return mock(prior.job);

    // A failed first attempt recovers on the next one, with a new job and the recovered scenario.
    const recovered = state.generateCalls > 0 ? RECOVERS_TO[state.scenario] : undefined;
    if (recovered) setMockScenarioKeepingCalls(recovered, state.generateCalls);
    state.generateCalls += 1;

    state.jobCounter += 1;
    const base = cloneScenario(state.scenario).job;
    const job: Job = {
      ...base,
      job_id: `${base.job_id}-${state.jobCounter}`,
      project_id: projectId,
      state: "queued",
      stage: null,
      result: null,
      error: null,
    };
    state.jobs.set(job.job_id, { job, polls: 0, scenario: state.scenario });
    state.keys.set(idempotencyKey, job.job_id);
    return mock(job);
  },

  async getJob(jobId) {
    const entry = state.jobs.get(jobId);
    if (!entry) throw notFound("The job");
    entry.polls += 1;
    const base = cloneScenario(entry.scenario).job;
    if (entry.scenario === "slow") {
      entry.job = { ...entry.job, state: "running", stage: "D_propose" };
    } else if (entry.polls <= MOCK_STAGES.length - 2) {
      entry.job = {
        ...entry.job,
        state: "running",
        stage: MOCK_STAGES[entry.polls - 1] ?? "A_garment",
      };
    } else {
      entry.job = { ...base, job_id: entry.job.job_id, project_id: entry.job.project_id };
    }
    return mock(entry.job);
  },

  async listDesigns(projectId) {
    return mock({ ...state.designs, project_id: projectId });
  },

  async getRevision(revisionId) {
    const revision = state.revisions.get(revisionId);
    if (!revision) throw notFound("The version");
    return mock(revision);
  },

  async createRevision(designId, body) {
    const design = state.designs.designs.find((d) => d.design_id === designId);
    if (!design) throw notFound("The design");
    const parent = state.revisions.get(body.parent_revision_id);
    if (!parent || parent.design_id !== designId) throw notFound("The version");
    if (parent.revision_id !== design.current_revision_id) {
      throw new StudioApiError(
        {
          code: "REVISION_CONFLICT",
          message: "This design changed since you opened it. Reload and edit the newest version.",
          recoverable: true,
        },
        409,
      );
    }
    const bad = Object.entries(body.parameters).find(
      ([k, v]) => MM_KEY.test(k) && !(typeof v === "number" && Number.isFinite(v) && v > 0),
    );
    if (bad) {
      throw new StudioApiError(
        { code: "VALIDATION_FAILED", message: "A length was not valid.", recoverable: true },
        422,
      );
    }
    return mock(mockRecheck(design, parent, body.parameters));
  },
};

function setMockScenarioKeepingCalls(scenario: ScenarioName, calls: number): void {
  const keys = state.keys;
  const jobs = state.jobs;
  const counter = state.jobCounter;
  state = freshState(scenario);
  state.keys = keys;
  state.jobs = jobs;
  state.jobCounter = counter;
  state.generateCalls = calls;
}

/** MOCK ONLY: a canned stand-in for the engine. Only the pass/fail split is faked; see header. */
function mockRecheck(
  design: DesignCandidate,
  parent: DesignRevision,
  changed: Parameters,
): DesignRevision {
  state.revisionCounter += 1;
  const parameters = { ...parent.parameters, ...changed };
  const finished = Number(parameters.finished_length_mm ?? 0);
  const hem = Number(parameters.hem_allowance_mm ?? 0);
  const original = parent.geometry_mm.original_length_mm;
  const cutMark = finished + hem;
  const fits = original === undefined || cutMark <= original;
  const nextNumber = parent.revision_number + 1;
  const id = `${design.design_id}-rev-${nextNumber}-m${state.revisionCounter}`;
  const now = new Date().toISOString();
  const checks = fits
    ? parent.checks
    : {
        ...parent.checks,
        hard_pass: false,
        failure_codes: ["INSUFFICIENT_LENGTH" as const],
        residuals: [
          {
            check_id: "length_gate",
            quantity: "garment_length",
            required_mm: cutMark,
            available_mm: original ?? 0,
            residual_mm: (original ?? 0) - cutMark,
            tolerance_mm: 0,
          },
        ],
        checks: parent.checks.checks.map((c) =>
          c.check_id === "length_gate"
            ? { ...c, result: "fail" as const, failure_code: "INSUFFICIENT_LENGTH" as const }
            : c.check_id === "structure" || c.check_id === "construction"
              ? { ...c, result: "not_run" as const }
              : c,
        ),
        checked_at: now,
      };

  const next: DesignRevision = {
    ...parent,
    revision_id: id,
    parent_revision_id: parent.revision_id,
    revision_number: nextNumber,
    parameters,
    geometry_mm: {
      ...parent.geometry_mm,
      finished_length_mm: finished,
      hem_allowance_mm: hem,
      ...(fits
        ? { cut_mark_from_shoulder_mm: cutMark, fabric_removed_mm: (original ?? cutMark) - cutMark }
        : { required_length_mm: cutMark }),
    },
    checks,
    status: fits ? "PASS_SUPPORTED_CHECKS" : "FAILED_CHECKS",
    cut_plan_id: fits ? `cut-${id}` : null,
    diy_suitability: fits ? parent.diy_suitability : null,
    pending_checks: fits ? parent.pending_checks : [],
    superseded_by_revision_id: null,
    created_at: now,
  };

  // The parent is never edited; only its status flips when it had passed.
  const supersededParent: DesignRevision = {
    ...parent,
    status: parent.checks.hard_pass ? "SUPERSEDED" : parent.status,
    superseded_by_revision_id: parent.checks.hard_pass ? id : parent.superseded_by_revision_id,
  };
  state.revisions.set(parent.revision_id, supersededParent);
  state.revisions.set(id, next);
  state.designs = {
    ...state.designs,
    designs: state.designs.designs.map((d) =>
      d.design_id === design.design_id
        ? {
            ...d,
            current_revision_id: id,
            status: next.status,
            parameters,
            failure_codes: next.checks.failure_codes,
            title: d.title,
          }
        : d,
    ),
  };
  return next;
}

let active: StudioApi = mockStudioApi;

export const getStudioApi = (): StudioApi => active;

/** Test seam, and the hook for swapping in the live client later. */
export const setStudioApi = (api: StudioApi): void => {
  active = api;
};
