import { BODY_SPECS, garmentSpecsFor } from "@/intake/measurements";
import {
  buildMeasurementRecords,
  checkPhotoBasics,
  checkPlausibility,
  cmToMm,
  evaluateEntry,
  missingSpecs,
  parseCm,
} from "@/intake/validation";

const chest = garmentSpecsFor("shirt")[0]!;

describe("parseCm", () => {
  it.each([
    ["60", 60],
    ["60.5", 60.5],
    [" 60,5 ", 60.5],
  ])("accepts %s", (input, cm) => expect(parseCm(input)).toEqual({ ok: true, cm }));

  it.each([
    ["", "empty"],
    ["abc", "not_a_number"],
    ["60cm", "not_a_number"],
    ["50-60", "not_a_number"],
    ["0", "not_positive"],
    ["-5", "not_positive"],
  ])("rejects %j", (input, reason) => expect(parseCm(input)).toEqual({ ok: false, reason }));
});

describe("cmToMm", () => {
  it("stores millimetres to 0.1 mm", () => {
    expect(cmToMm(60)).toBe(600);
    expect(cmToMm(52.5)).toBe(525);
    expect(cmToMm(52.55)).toBe(525.5);
  });
});

describe("checkPlausibility", () => {
  it("accepts a typical chest", () => {
    expect(checkPlausibility(chest, 520).level).toBe("ok");
  });
  it("flags 6 cm where 60 cm is likely and suggests the fix", () => {
    expect(checkPlausibility(chest, cmToMm(6))).toEqual({
      level: "warn",
      code: "maybe_missing_zero",
      suggestedCm: 60,
    });
  });
  it("flags 600 cm where 60 cm is likely", () => {
    expect(checkPlausibility(chest, cmToMm(600))).toMatchObject({
      level: "warn",
      code: "maybe_extra_zero",
      suggestedCm: 60,
    });
  });
  it("warns but allows an unusual value inside hard limits", () => {
    expect(checkPlausibility(chest, 800)).toEqual({ level: "warn", code: "unusual" });
  });
  it("blocks values no garment could have", () => {
    expect(checkPlausibility(chest, cmToMm(3000)).level).toBe("error");
  });
});

describe("entries", () => {
  const entry = (inputCm: string, confirmedAt: string | null = null) => ({
    inputCm,
    confirmedAt,
    origin: "user_entered" as const,
  });

  it("requires confirmation, and clears it on edit", () => {
    expect(evaluateEntry(chest, entry("52")).state).toBe("needs_review");
    expect(evaluateEntry(chest, entry("52", "2026-10-28T00:00:00Z")).state).toBe("confirmed");
  });

  it("reports missing garment values", () => {
    const specs = garmentSpecsFor("shirt");
    const missing = missingSpecs(specs, { chest_flat: entry("52", "2026-10-28T00:00:00Z") });
    expect(missing.map((s) => s.key)).toEqual(["body_length", "shoulder_width", "sleeve_length"]);
  });

  it("builds mm records with origin and confirmed_at, skipping unconfirmed values", () => {
    const records = buildMeasurementRecords([chest, ...BODY_SPECS], {
      chest_flat: entry("52.5", "2026-10-28T00:00:00Z"),
      height: entry("170"),
    });
    expect(records).toEqual([
      {
        key: "chest_flat",
        group: "garment",
        value_mm: 525,
        origin: "user_entered",
        confirmed_at: "2026-10-28T00:00:00Z",
      },
    ]);
  });
});

describe("checkPhotoBasics", () => {
  it("warns on small photos only", () => {
    expect(checkPhotoBasics({ width: 4000, height: 3000 }).warnings).toEqual([]);
    expect(checkPhotoBasics({ width: 640, height: 480 }).warnings).toEqual(["low_resolution"]);
  });
});
