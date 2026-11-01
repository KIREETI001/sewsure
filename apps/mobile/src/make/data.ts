/**
 * Mock data source for screens 7-8, built from packages/contracts/fixtures. Replace with the
 * generated API client; the screens only see `MakeBundle`.
 */
import crop from "../../../../packages/contracts/fixtures/woven_shirt_crop_pass.json";
import ideaOnly from "../../../../packages/contracts/fixtures/idea_only.json";
import needsInput from "../../../../packages/contracts/fixtures/needs_input.json";
import lengthening from "../../../../packages/contracts/fixtures/lengthening_impossible.json";
import type { DesignRevision, MakeBundle } from "./types";

type Fixture = {
  revisions: unknown[];
  cut_plan?: unknown;
  diy_steps?: unknown;
  diy_progress?: unknown;
  garment: { photos: unknown[] };
};

const fixtures = [crop, ideaOnly, needsInput, lengthening] as unknown as Fixture[];

/** Resolves to null for a revision the source does not know, so screens fail closed. */
export async function loadMakeBundle(revisionId: string): Promise<MakeBundle | null> {
  for (const f of fixtures) {
    const revision = (f.revisions as DesignRevision[]).find((r) => r.revision_id === revisionId);
    if (!revision) continue;
    const cutPlan = f.cut_plan as MakeBundle["cutPlan"] | undefined;
    const diy = f.diy_steps as MakeBundle["diySteps"] | undefined;
    const progress = f.diy_progress as MakeBundle["serverProgress"] | undefined;
    const photos = f.garment.photos as NonNullable<MakeBundle["photo"]>[];
    // Fixtures hold one plan for one revision. Other revisions get no plan, as the API would.
    const owns = cutPlan?.revision_id === revisionId;
    const photoId = cutPlan?.calibration.reference_photo_id;
    return {
      provenance: "mock",
      revision,
      cutPlan: owns && cutPlan ? cutPlan : null,
      diySteps: owns && diy ? diy : null,
      serverProgress: owns && progress ? progress : null,
      photo: owns ? (photos.find((p) => p.photo_id === photoId) ?? null) : null,
    };
  }
  return null;
}
