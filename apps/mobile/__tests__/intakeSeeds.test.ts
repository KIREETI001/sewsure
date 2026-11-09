import AsyncStorage from "@react-native-async-storage/async-storage";
import { applyIntakeSeed, createIntakeSeed, INTAKE_SEED_NAMES } from "@/dev/intakeSeeds";
import { BODY_SPECS, garmentSpecsFor } from "@/intake/measurements";
import {
  buildMeasurementRecords,
  checkPhotoBasics,
  evaluateEntry,
  missingSpecs,
} from "@/intake/validation";
import { inspirationFor, useIntakeStore } from "@/state/intakeStore";

const specs = garmentSpecsFor("shirt");

beforeEach(async () => {
  await useIntakeStore.persist.rehydrate();
  useIntakeStore.getState().reset();
});
afterEach(() => useIntakeStore.getState().reset());

describe("synthetic intake definitions", () => {
  it.each(INTAKE_SEED_NAMES)("creates a deterministic, isolated %s draft", (name) => {
    const first = createIntakeSeed(name);
    const second = createIntakeSeed(name);
    expect(first).toEqual(second);
    expect(first).not.toBe(second);
    expect(first.front).not.toBe(second.front);
    expect(first.back).not.toBe(second.back);
    expect(first.front).not.toBe(first.back);
    expect(first.tools).not.toBe(second.tools);
    expect(first.measurements).not.toBe(second.measurements);
    expect(first.inspirationDraft).not.toBe(second.inspirationDraft);
    expect(first.category).toBe("shirt");
    for (const photo of [first.front!, first.back!]) {
      expect(photo.checked).toBe(true);
      expect(checkPhotoBasics(photo).warnings).toEqual([]);
      expect(photo.uri).toMatch(/^data:image\/png;base64,/);
      const bytes = Buffer.from(photo.uri.split(",")[1]!, "base64");
      expect(bytes.subarray(0, 8).toString("hex")).toBe("89504e470d0a1a0a");
      expect(bytes.readUInt32BE(16)).toBe(photo.width);
      expect(bytes.readUInt32BE(20)).toBe(photo.height);
    }
    expect(first.front!.uri).not.toBe(first.back!.uri);
    expect(first.uploadStatus).toBe("not_uploaded");
    expect(first.uploadProvenance).toBeNull();
    expect(first.bodyConsentVersion).toBeNull();
    for (const spec of BODY_SPECS) expect(first.measurements[spec.key]).toBeUndefined();
  });

  it("capture-ready has checked photos but no inspiration or identity", () => {
    const draft = createIntakeSeed("capture-ready");
    expect(inspirationFor(draft.inspirationMode, draft.inspirationDraft)).toBeNull();
    expect(draft.fit).toBeNull();
    expect(draft.skill).toBeNull();
    expect(draft.signedInAs).toBeNull();
    expect(draft.guest).toBe(true);
    expect(draft.measurements).toEqual({});
  });

  it("inspiration-ready adds text, fit and sewing skill", () => {
    const draft = createIntakeSeed("inspiration-ready");
    expect(inspirationFor(draft.inspirationMode, draft.inspirationDraft)).toEqual({
      kind: "text",
      text: "Synthetic test idea: shorten the shirt sleeves.",
    });
    expect(draft.fit).toBe("relaxed");
    expect(draft.skill).toBe("beginner");
    expect(draft.guest).toBe(true);
    expect(draft.signedInAs).toBeNull();
    expect(draft.measurements).toEqual({});
  });

  it("measurements-signed-in adds only an explicitly synthetic mock identity", () => {
    const draft = createIntakeSeed("measurements-signed-in");
    expect(draft).toEqual({
      ...createIntakeSeed("inspiration-ready"),
      guest: false,
      signedInAs: "Synthetic test user (mock; no authentication)",
    });
    expect(missingSpecs(specs, draft.measurements)).toEqual(specs);
    expect(buildMeasurementRecords(specs, draft.measurements)).toEqual([]);
  });

  it("confirms all required shirt values through existing validation, in mm on export", () => {
    const draft = createIntakeSeed("measurements-confirmed");
    expect(draft).toEqual({
      ...createIntakeSeed("measurements-signed-in"),
      measurements: draft.measurements,
    });
    expect(Object.keys(draft.measurements)).toEqual(specs.map((spec) => spec.key));
    expect(missingSpecs(specs, draft.measurements)).toEqual([]);
    expect(buildMeasurementRecords(specs, draft.measurements)).toEqual(
      specs.map((spec, i) => ({
        key: spec.key,
        group: "garment",
        value_mm: [520, 700, 450, 600][i],
        entered_unit: "cm",
        origin: "user_entered",
        confirmed_at: "2026-01-01T00:00:00.000Z",
      })),
    );
    for (const spec of specs) {
      expect(evaluateEntry(spec, { ...draft.measurements[spec.key]!, confirmedAt: null }))
        .toMatchObject({ state: "needs_review", plausibility: { level: "ok" } });
    }
    // A seeded confirmation never overrides a hard validation error.
    draft.measurements.chest_flat_width!.inputCm = "500";
    expect(evaluateEntry(specs[0]!, draft.measurements.chest_flat_width).state).toBe("blocked");
    expect(missingSpecs(specs, draft.measurements)).toEqual([specs[0]]);
  });

  it("does not share mutable entries across calls or mutate the store on construction", () => {
    const before = useIntakeStore.getState();
    const draft = createIntakeSeed("measurements-confirmed");
    draft.front!.checked = false;
    draft.back!.uri = "synthetic:changed";
    draft.tools.push("scissors");
    draft.inspirationDraft.text = "changed";
    draft.measurements.chest_flat_width!.inputCm = "1";
    expect(useIntakeStore.getState()).toBe(before);
    const fresh = createIntakeSeed("measurements-confirmed");
    expect(fresh.front!.checked).toBe(true);
    expect(fresh.back!.uri).toMatch(/^data:/);
    expect(fresh.tools).toEqual([]);
    expect(fresh.inspirationDraft.text).toMatch(/^Synthetic/);
    expect(fresh.measurements.chest_flat_width!.inputCm).toBe("52");
  });
});

describe("complete seed replacement", () => {
  it.each(INTAKE_SEED_NAMES)("resets every prior seed to %s without stale persisted data", async (name) => {
    for (const previous of INTAKE_SEED_NAMES) {
      applyIntakeSeed(previous, useIntakeStore.getState());
      useIntakeStore.getState().patch({
        role: "tailor",
        signedInAs: "Synthetic stale identity",
        category: "dress",
        tools: ["iron"],
        extraMaterials: "synthetic scraps",
        bodyConsentVersion: "synthetic-stale-consent",
        measurements: { stale: { inputCm: "1", origin: "user_entered", confirmedAt: null } },
        inspirationMode: "image",
        inspirationDraft: { imageUri: "synthetic:stale", text: "stale", surprisePrompt: "stale" },
      });
      useIntakeStore.getState().patch({ uploadStatus: "uploaded", uploadProvenance: "mock" });
      applyIntakeSeed(name, useIntakeStore.getState());
      expect(useIntakeStore.getState()).toMatchObject(createIntakeSeed(name));
      const persisted = JSON.parse((await AsyncStorage.getItem("sewsure.intake.draft.v1"))!);
      expect(persisted.state).toEqual(createIntakeSeed(name));
      await useIntakeStore.persist.rehydrate();
      expect(useIntakeStore.getState()).toMatchObject(createIntakeSeed(name));
    }
  });

  it.each(INTAKE_SEED_NAMES)("can reset %s to the normal empty intake", (name) => {
    const empty = useIntakeStore.getState();
    applyIntakeSeed(name, empty);
    useIntakeStore.getState().reset();
    expect(useIntakeStore.getState()).toEqual(empty);
    applyIntakeSeed(name, useIntakeStore.getState());
    expect(useIntakeStore.getState()).toMatchObject(createIntakeSeed(name));
  });

  it("rejects an unknown seed before changing the target", () => {
    const patch = jest.fn();
    expect(() => applyIntakeSeed("unknown" as never, { patch })).toThrow("Unknown intake seed");
    expect(patch).not.toHaveBeenCalled();
  });
});
