/**
 * REPLACE WITH GENERATED CLIENT.
 *
 * These hand-written types mirror what the intake screens need. They are the only place in
 * apps/mobile that declares API shapes. When packages/contracts publishes the generated client,
 * delete this file and re-export the generated types from here so the imports keep working.
 * Contract changes happen in packages/contracts, never here (CLAUDE.md non-negotiable 9).
 */

export type Role = "user" | "tailor";

export type GarmentCategory = "shirt" | "tee" | "jacket" | "trousers" | "skirt" | "dress";

export type FitPreference = "fitted" | "relaxed" | "oversized" | "no_preference";
export type SkillLevel = "beginner" | "intermediate" | "advanced";
export type Tool =
  "sewing_machine" | "hand_sewing" | "scissors" | "iron" | "overlocker" | "tailors_chalk";

/** Every measurement records where it came from and when the user confirmed it. */
export type MeasurementOrigin = "user_tape_measured" | "user_entered" | "saved_profile";
export type MeasurementGroup = "garment" | "body";

export interface MeasurementRecord {
  key: string;
  group: MeasurementGroup;
  /** Millimetres. Centimetres exist only in the UI. */
  value_mm: number;
  origin: MeasurementOrigin;
  /** Unit the user typed, kept for audit. `value_mm` is already converted. */
  entered_unit: "cm";
  confirmed_at: string;
}

export type InspirationInput =
  | { kind: "image"; uri: string }
  | { kind: "text"; text: string }
  | { kind: "surprise"; prompt: string };

export interface IntakeRequest {
  front_photo_uri: string;
  back_photo_uri: string;
  category: GarmentCategory;
  inspiration: InspirationInput;
  fit_preference: FitPreference;
  skill_level: SkillLevel;
  tools: Tool[];
  extra_materials: string;
  /** Set only when the user opted in to sharing body measurements. */
  body_consent_version: string | null;
  measurements: MeasurementRecord[];
}

export const BODY_CONSENT_VERSION = "body-v0-draft";

export interface IntakeReceipt {
  intake_id: string;
  received_at: string;
}

export interface Session {
  user_id: string;
  display_name: string;
}

/** Where a response came from. The UI shows a MockBadge for anything that is not "live". */
export type Provenance = "mock" | "live";

export interface Envelope<T> {
  data: T;
  provenance: Provenance;
}

export interface CategorySuggestion {
  category: GarmentCategory;
  /** Plain-language reason. No confidence number: it would need a source and a denominator. */
  reason: string;
}

export interface SewSureApi {
  signIn(): Promise<Envelope<Session>>;
  suggestCategory(frontPhotoUri: string): Promise<Envelope<CategorySuggestion>>;
  surpriseMe(): Promise<Envelope<{ prompt: string }>>;
  uploadIntake(request: IntakeRequest): Promise<Envelope<IntakeReceipt>>;
}
