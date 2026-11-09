import { BODY_SPECS, garmentSpecsFor } from "@/intake/measurements";
import {
  buildMeasurementRecords,
  checkPhotoBasics,
  checkPlausibility,
  cmToMm,
  evaluateEntry,
  missingSpecs,
  unconfirmedSpecs,
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
  it("rejects 6 cm where 60 cm is likely, but suggests the fix", () => {
    expect(checkPlausibility(chest, cmToMm(6))).toEqual({
      level: "error",
      code: "maybe_missing_zero",
      suggestedCm: 60,
    });
  });
  it("rejects 500 cm, suggesting 50 cm, and never lets it be kept", () => {
    expect(checkPlausibility(chest, cmToMm(500))).toMatchObject({
      level: "error",
      code: "maybe_extra_zero",
      suggestedCm: 50,
    });
    const kept = {
      inputCm: "500",
      confirmedAt: "2026-10-28T00:00:00Z",
      origin: "user_entered" as const,
    };
    expect(evaluateEntry(chest, kept).state).toBe("blocked");
    expect(buildMeasurementRecords([chest], { chest_flat_width: kept })).toEqual([]);
  });
  it("only warns for an unusual value inside the hard range", () => {
    const waist = garmentSpecsFor("skirt")[0]!;
    expect(checkPlausibility(waist, 250)).toEqual({ level: "warn", code: "unusual" });
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
    const missing = missingSpecs(specs, { chest_flat_width: entry("52", "2026-10-28T00:00:00Z") });
    expect(missing.map((s) => s.key)).toEqual([
      "shoulder_to_hem",
      "shoulder_width",
      "sleeve_length",
    ]);
  });

  it("builds mm records with origin and confirmed_at, skipping unconfirmed values", () => {
    const records = buildMeasurementRecords([chest, ...BODY_SPECS], {
      chest_flat_width: entry("52.5", "2026-10-28T00:00:00Z"),
      height: entry("170"),
    });
    expect(records).toEqual([
      {
        key: "chest_flat_width",
        group: "garment",
        value_mm: 525,
        origin: "user_entered",
        entered_unit: "cm",
        confirmed_at: "2026-10-28T00:00:00Z",
      },
    ]);
  });
});

describe("body ranges", () => {
  it("never produce a blocking error", () => {
    const height = BODY_SPECS[0]!;
    expect(checkPlausibility(height, cmToMm(3000)).level).toBe("warn");
  });
});

describe("checkPhotoBasics", () => {
  it("warns on small photos only", () => {
    expect(checkPhotoBasics({ width: 4000, height: 3000 }).warnings).toEqual([]);
    expect(checkPhotoBasics({ width: 640, height: 480 }).warnings).toEqual(["low_resolution"]);
  });
});

describe("unconfirmedSpecs", () => {
  it("lists typed-but-unconfirmed values only", () => {
    const entries = {
      height: { inputCm: "250", confirmedAt: null, origin: "user_entered" as const },
      bust: { inputCm: "", confirmedAt: null, origin: "user_entered" as const },
      waist: {
        inputCm: "80",
        confirmedAt: "2026-10-28T00:00:00Z",
        origin: "user_entered" as const,
      },
    };
    expect(unconfirmedSpecs(BODY_SPECS, entries).map((x) => x.key)).toEqual(["height"]);
  });
});
