/**
 * Scenarios for the fixture-backed studio client. The five JSON files in ./fixtures are verbatim
 * copies of packages/contracts/fixtures (a Jest test fails if they drift). Metro cannot bundle
 * files outside the app root, so they are copied rather than imported across the repo.
 *
 * Two extra scenarios are derived here and exist only in the mock:
 * - `zero_designs`: a complete job with an empty design list and a binding constraint.
 * - `slow`: a job that never settles, to exercise the timeout state.
 */
import ideaOnly from "./fixtures/idea_only.json";
import jobFailed from "./fixtures/job_failed_no_designs.json";
import lengthening from "./fixtures/lengthening_impossible.json";
import needsInput from "./fixtures/needs_input.json";
import wovenPass from "./fixtures/woven_shirt_crop_pass.json";
import type { DesignList, DesignRevision, Job } from "./types";

export interface Scenario {
  job: Job;
  designs: DesignList;
  revisions: DesignRevision[];
}

const asScenario = (raw: unknown): Scenario => raw as Scenario;

const base = {
  woven_shirt_crop_pass: asScenario(wovenPass),
  lengthening_impossible: asScenario(lengthening),
  needs_input: asScenario(needsInput),
  idea_only: asScenario(ideaOnly),
  job_failed_no_designs: asScenario(jobFailed),
};

const zeroDesigns = (): Scenario => {
  const src = base.lengthening_impossible;
  return {
    job: {
      ...src.job,
      job_id: "job-zero",
      result: { outcome: "no_feasible_design", design_ids: [] },
    },
    designs: { ...src.designs, job_id: "job-zero", designs: [] },
    revisions: [],
  };
};

const slow = (): Scenario => {
  const src = base.woven_shirt_crop_pass;
  return { ...src, job: { ...src.job, job_id: "job-slow" } };
};

export type ScenarioName = keyof typeof base | "zero_designs" | "slow";

export const SCENARIO_NAMES: readonly ScenarioName[] = [
  "woven_shirt_crop_pass",
  "lengthening_impossible",
  "needs_input",
  "idea_only",
  "job_failed_no_designs",
  "zero_designs",
  "slow",
];

export const DEFAULT_SCENARIO: ScenarioName = "woven_shirt_crop_pass";

export const isScenarioName = (value: unknown): value is ScenarioName =>
  typeof value === "string" && (SCENARIO_NAMES as readonly string[]).includes(value);

/** A deep copy, so the mock can mutate state without touching the shared fixture objects. */
export const cloneScenario = (name: ScenarioName): Scenario => {
  const src = name === "zero_designs" ? zeroDesigns() : name === "slow" ? slow() : base[name];
  return JSON.parse(JSON.stringify(src)) as Scenario;
};
