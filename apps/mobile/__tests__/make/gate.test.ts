import fs from "fs";
import path from "path";
import crop from "../../../../packages/contracts/fixtures/woven_shirt_crop_pass.json";
import ideaOnly from "../../../../packages/contracts/fixtures/idea_only.json";
import needsInput from "../../../../packages/contracts/fixtures/needs_input.json";
import lengthening from "../../../../packages/contracts/fixtures/lengthening_impossible.json";
import { makeEn } from "../../src/make/i18n";
import {
  RECIPE_STATUS,
  checkpointsComplete,
  cutGuideAccess,
  guideMode,
  overlayDecision,
  stepLock,
} from "../../src/make/gate";
import type { CutPlan, DesignRevision, DiySteps, PhotoRef } from "../../src/make/types";

const plan = crop.cut_plan as unknown as CutPlan;
const diy = crop.diy_steps as unknown as DiySteps;
const photo = crop.garment.photos[0] as unknown as PhotoRef;
const rev = (id: string) =>
  [crop, ideaOnly, needsInput, lengthening].flatMap((f) => f.revisions as unknown as DesignRevision[]).find((r) => r.revision_id === id)!;

describe("cut guide access: only PASS_SUPPORTED_CHECKS opens", () => {
  it("opens for the passing revision with its own plan", () => {
    expect(cutGuideAccess(rev("rev-crop-a-2"), plan)).toEqual({ allowed: true });
  });

  it.each([
    ["rev-crop-a-1", "SUPERSEDED", "superseded", "open_newer_revision"],
    ["rev-idea-a-1", "IDEA_ONLY", "idea_only", "ask_tailor"],
    ["rev-unsure-a-1", "NEEDS_INPUT", "needs_input", "add_measurements"],
    ["rev-longer-a-1", "FAILED_CHECKS", "failed_checks", "choose_supported_change"],
  ])("%s (%s) is closed even if a plan is supplied", (id, status, reason, next) => {
    const r = rev(id);
    expect(r.status).toBe(status);
    const res = cutGuideAccess(r, plan);
    expect(res.allowed).toBe(false);
    if (!res.allowed) {
      expect(res.reason).toBe(reason);
      expect(res.next).toBe(next);
    }
  });

  it("names the newer revision for SUPERSEDED", () => {
    const res = cutGuideAccess(rev("rev-crop-a-1"), plan);
    expect(!res.allowed && res.newerRevisionId).toBe("rev-crop-a-2");
  });

  it("is closed with no plan, a plan for another revision, or an unknown state", () => {
    expect(cutGuideAccess(rev("rev-crop-a-2"), null).allowed).toBe(false);
    expect(cutGuideAccess(rev("rev-crop-a-2"), { ...plan, revision_id: "other" }).allowed).toBe(false);
    expect(cutGuideAccess({ ...rev("rev-crop-a-2"), status: "SAFE" } as unknown as DesignRevision, plan).allowed).toBe(false);
    expect(cutGuideAccess(null, plan).allowed).toBe(false);
  });
});

describe("overlay vs diagram", () => {
  const good = {
    ...plan,
    mode: "calibrated_overlay",
    calibration: {
      state: "calibrated",
      calibration_id: "cal-1",
      reference_photo_id: photo.photo_id,
      scale_px_per_mm: 4,
      median_error_mm: 1,
      max_error_mm: 2,
      tolerance_mm: 3,
      rejection_reason: null,
      origin_px: [100, 200],
    },
  } as unknown as CutPlan;

  it("falls back for the fixture (uncalibrated)", () => {
    const d = overlayDecision(plan, photo);
    expect(d).toMatchObject({ kind: "diagram", reason: "mode_diagram" });
  });
  it("draws only when calibrated, within tolerance, verified and placed", () => {
    expect(overlayDecision(good, photo).kind).toBe("overlay");
  });
  it.each([
    ["rejected", { state: "rejected" }, "rejected"],
    ["uncalibrated", { state: "uncalibrated" }, "not_calibrated"],
    ["out of tolerance", { max_error_mm: 4 }, "out_of_tolerance"],
    ["no error data", { max_error_mm: null }, "missing_calibration_data"],
    ["no scale", { scale_px_per_mm: null }, "missing_calibration_data"],
    ["no origin", { origin_px: null }, "missing_projection"],
  ])("diagram when %s", (_n, patch, reason) => {
    const p = { ...good, calibration: { ...good.calibration, ...patch } } as unknown as CutPlan;
    expect(overlayDecision(p, photo)).toMatchObject({ kind: "diagram", reason });
  });
  it("diagram when the photo is unverified or is not the calibrated one", () => {
    expect(overlayDecision(good, { ...photo, status: "uploaded" })).toMatchObject({ reason: "photo_not_verified" });
    expect(overlayDecision(good, { ...photo, photo_id: "x" })).toMatchObject({ reason: "photo_not_verified" });
    expect(overlayDecision(good, null)).toMatchObject({ reason: "photo_not_verified" });
  });
});

describe("ruler checkpoint cannot be skipped", () => {
  it("locks cut steps until every cut-plan checkpoint is ticked", () => {
    const cut = diy.steps.find((s) => s.irreversible)!;
    expect(stepLock(cut, false)).toBe("checkpoint_required");
    expect(stepLock(cut, true)).toBeNull();
    const ids = plan.ruler_checkpoints.map((c) => c.checkpoint_id);
    expect(ids.length).toBeGreaterThan(1);
    expect(checkpointsComplete(plan, { [ids[0]!]: true })).toBe(false);
    expect(checkpointsComplete(plan, Object.fromEntries(ids.map((i) => [i, true])))).toBe(true);
    expect(checkpointsComplete({ ...plan, ruler_checkpoints: [] }, {})).toBe(false);
  });
});

describe("draft recipe", () => {
  it("registry matches recipe.yaml", () => {
    const yaml = fs.readFileSync(path.join(__dirname, "../../../../content/recipes/woven_shirt_crop_v1/recipe.yaml"), "utf8");
    expect(/^status:\s*(\w+)/m.exec(yaml)?.[1]).toBe(RECIPE_STATUS.woven_shirt_crop_v1);
  });
  it("is demo-only on mock data and blocked on live data", () => {
    expect(guideMode(diy, plan, "mock")).toBe("demo_preview");
    expect(guideMode(diy, plan, "live")).toBe("blocked");
    expect(guideMode(null, plan, "mock")).toBe("blocked");
    expect(guideMode({ ...diy, recipe_id: "unknown_v1" }, { ...plan, recipe_id: "unknown_v1" }, "live")).toBe("blocked");
  });
});

describe("strings", () => {
  it("contain no guarantee wording", () => {
    const banned = /guarantee|perfect fit|precision ar|100%|exact(ly)?\b|accurate/i;
    for (const [k, v] of Object.entries(makeEn)) expect({ k, bad: banned.test(v) }).toEqual({ k, bad: false });
  });
});
