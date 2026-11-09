import { garmentSpecsFor } from "@/intake/measurements";
import { evaluateEntry, type MeasurementEntry } from "@/intake/validation";
import type { IntakeDraft, useIntakeStore } from "@/state/intakeStore";
import { syntheticBackUri, syntheticFrontUri } from "./syntheticPhotos";

export const INTAKE_SEED_NAMES = [
  "capture-ready",
  "inspiration-ready",
  "measurements-signed-in",
  "measurements-confirmed",
] as const;
export type IntakeSeedName = (typeof INTAKE_SEED_NAMES)[number];

const confirmedAt = "2026-01-01T00:00:00.000Z";
const shirtCm: Readonly<Record<string, string>> = {
  chest_flat_width: "52",
  shoulder_to_hem: "70",
  shoulder_width: "45",
  sleeve_length: "60",
};

/** Fresh complete drafts, never partial overlays. No authentication or API calls. */
export function createIntakeSeed(name: IntakeSeedName): IntakeDraft {
  if (!INTAKE_SEED_NAMES.includes(name)) throw new Error(`Unknown intake seed: ${name}`);
  const inspired = name !== "capture-ready";
  const signedIn = name === "measurements-signed-in" || name === "measurements-confirmed";
  const measurements: IntakeDraft["measurements"] = {};
  if (name === "measurements-confirmed") {
    for (const spec of garmentSpecsFor("shirt")) {
      const entry: MeasurementEntry = {
        inputCm: shirtCm[spec.key] ?? "",
        origin: "user_entered",
        confirmedAt: null,
      };
      const status = evaluateEntry(spec, entry);
      if (status.state !== "needs_review" || status.plausibility.level !== "ok") {
        throw new Error(`Synthetic shirt measurement needs review: ${spec.key}`);
      }
      measurements[spec.key] = { ...entry, confirmedAt };
    }
  }
  return {
    role: "user",
    guest: !signedIn,
    signedInAs: signedIn ? "Synthetic test user (mock; no authentication)" : null,
    category: "shirt",
    front: { uri: syntheticFrontUri, width: 800, height: 800, checked: true },
    back: { uri: syntheticBackUri, width: 800, height: 800, checked: true },
    fit: inspired ? "relaxed" : null,
    skill: inspired ? "beginner" : null,
    tools: [],
    extraMaterials: "",
    measurements,
    uploadStatus: "not_uploaded",
    uploadProvenance: null,
    bodyConsentVersion: null,
    inspirationMode: "text",
    inspirationDraft: {
      imageUri: null,
      text: inspired ? "Synthetic test idea: shorten the shirt sleeves." : "",
      surprisePrompt: null,
    },
  };
}

/**
 * Test helper only: pass an isolated store, or a quiescent, already-hydrated intake store.
 * One complete patch resets every draft field, including consent and upload state.
 * Never import this module from production entry points. Release routing is Part B.
 */
export function applyIntakeSeed(
  name: IntakeSeedName,
  target: Pick<ReturnType<typeof useIntakeStore.getState>, "patch">,
): void {
  target.patch(createIntakeSeed(name));
}
