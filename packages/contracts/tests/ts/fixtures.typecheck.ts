// Compile-time check: every fixture is assignable to the generated FixtureScenario type,
// so mobile can import fixtures with the same fields and states as the backend (§9.3).
import type { components } from "../../generated/ts/sewsure.v1";
import crop from "../../fixtures/woven_shirt_crop_pass.json";
import longer from "../../fixtures/lengthening_impossible.json";
import needsInput from "../../fixtures/needs_input.json";
import idea from "../../fixtures/idea_only.json";
import stale from "../../fixtures/stale_after_measurements_change.json";
import failed from "../../fixtures/job_failed_no_designs.json";

type FixtureScenario = components["schemas"]["FixtureScenario"];
type DesignState = components["schemas"]["DesignState"];

// JSON imports widen string literals, so assert through the wire shape the way a fetch() result would.
export const fixtures = [crop, longer, needsInput, idea, stale, failed] as unknown as FixtureScenario[];

// Exhaustive switch: adding or removing a design state breaks this file on purpose.
export function stateLabel(state: DesignState): string {
  switch (state) {
    case "IDEA_ONLY":
      return "Idea only";
    case "NEEDS_INPUT":
      return "Needs input";
    case "FAILED_CHECKS":
      return "Failed checks";
    case "PASS_SUPPORTED_CHECKS":
      return "Passed supported checks";
    case "SUPERSEDED":
      return "Superseded";
  }
}

// Lengths are numbers in mm; the UI converts to cm.
export function cutMarkCm(rev: components["schemas"]["DesignRevision"]): number | undefined {
  const mm = rev.geometry_mm["cut_mark_from_shoulder_mm"];
  return mm === undefined ? undefined : mm / 10;
}
