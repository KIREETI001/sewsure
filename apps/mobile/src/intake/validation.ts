import type { MeasurementOrigin, MeasurementRecord } from "@/api/types";
import type { MeasurementSpec } from "./measurements";

/** Centimetres in, millimetres out, kept to 0.1 mm. */
export const cmToMm = (cm: number): number => Math.round(cm * 100) / 10;
export const mmToCm = (mm: number): number => Math.round(mm) / 10;

export type ParseResult =
  { ok: true; cm: number } | { ok: false; reason: "empty" | "not_a_number" | "not_positive" };

/** Accepts "60", "60.5" and "60,5". Rejects units, ranges and anything else. */
export const parseCm = (input: string): ParseResult => {
  const trimmed = input.trim();
  if (trimmed === "") return { ok: false, reason: "empty" };
  if (!/^-?\d+([.,]\d+)?$/.test(trimmed)) return { ok: false, reason: "not_a_number" };
  const value = Number(trimmed.replace(",", "."));
  if (!Number.isFinite(value)) return { ok: false, reason: "not_a_number" };
  if (value <= 0) return { ok: false, reason: "not_positive" };
  return { ok: true, cm: value };
};

export type PlausibilityCode =
  "ok" | "out_of_range" | "maybe_missing_zero" | "maybe_extra_zero" | "unusual";

export interface Plausibility {
  /** `error` blocks the value; `warn` needs the user to fix or keep it. */
  level: "ok" | "warn" | "error";
  code: PlausibilityCode;
  /** Suggested replacement in cm, when a likely typo is detected. */
  suggestedCm?: number;
}

const within = (mm: number, [lo, hi]: readonly [number, number]): boolean => mm >= lo && mm <= hi;

export const checkPlausibility = (spec: MeasurementSpec, mm: number): Plausibility => {
  if (within(mm, spec.typicalMm)) return { level: "ok", code: "ok" };
  // Likely typo: a dropped or extra zero (6 cm where 60 cm is expected).
  if (within(mm * 10, spec.typicalMm)) {
    return { level: "warn", code: "maybe_missing_zero", suggestedCm: mmToCm(mm * 10) };
  }
  if (within(mm / 10, spec.typicalMm)) {
    return { level: "warn", code: "maybe_extra_zero", suggestedCm: mmToCm(mm / 10) };
  }
  if (!within(mm, spec.hardMm)) return { level: "error", code: "out_of_range" };
  return { level: "warn", code: "unusual" };
};

/** What the user has typed and decided for one field. Stored in the local draft. */
export interface MeasurementEntry {
  inputCm: string;
  /** Set when the user confirmed the value (clean entry on blur, or "keep my value"). */
  confirmedAt: string | null;
  origin: MeasurementOrigin;
}

export type EntryStatus =
  | { state: "empty" }
  | { state: "invalid"; reason: "not_a_number" | "not_positive" }
  | { state: "blocked"; plausibility: Plausibility; mm: number }
  | { state: "needs_review"; plausibility: Plausibility; mm: number }
  | { state: "confirmed"; mm: number };

export const evaluateEntry = (
  spec: MeasurementSpec,
  entry: MeasurementEntry | undefined,
): EntryStatus => {
  if (!entry) return { state: "empty" };
  const parsed = parseCm(entry.inputCm);
  if (!parsed.ok) {
    return parsed.reason === "empty"
      ? { state: "empty" }
      : { state: "invalid", reason: parsed.reason };
  }
  const mm = cmToMm(parsed.cm);
  const plausibility = checkPlausibility(spec, mm);
  if (plausibility.level === "error") return { state: "blocked", plausibility, mm };
  if (!entry.confirmedAt) return { state: "needs_review", plausibility, mm };
  return { state: "confirmed", mm };
};

/** Specs with no confirmed value yet. Drives the "missing values" edge state. */
export const missingSpecs = (
  specs: MeasurementSpec[],
  entries: Record<string, MeasurementEntry>,
): MeasurementSpec[] => specs.filter((s) => evaluateEntry(s, entries[s.key]).state !== "confirmed");

export const buildMeasurementRecords = (
  specs: MeasurementSpec[],
  entries: Record<string, MeasurementEntry>,
): MeasurementRecord[] => {
  const records: MeasurementRecord[] = [];
  for (const s of specs) {
    const entry = entries[s.key];
    const status = evaluateEntry(s, entry);
    if (status.state !== "confirmed" || !entry?.confirmedAt) continue;
    records.push({
      key: s.key,
      group: s.group,
      value_mm: status.mm,
      origin: entry.origin,
      confirmed_at: entry.confirmedAt,
    });
  }
  return records;
};

export interface PhotoBasics {
  warnings: "low_resolution"[];
}

/** Cheap, deterministic checks only. Blur and lighting stay a user checklist until K4 ships. */
export const checkPhotoBasics = (size: { width: number; height: number }): PhotoBasics => {
  const shortSide = Math.min(size.width, size.height);
  return { warnings: shortSide < 720 ? ["low_resolution"] : [] };
};
