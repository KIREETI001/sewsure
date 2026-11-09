/**
 * Local fixtures standing in for packages/contracts/fixtures until K1 publishes them.
 * Synthetic only: no real photos, names or body measurements.
 */
import type { CategorySuggestion, IntakeReceipt, Session } from "./types";

export const sessionFixture: Session = { user_id: "mock-user-001", display_name: "Demo user" };

export const categorySuggestionFixture: CategorySuggestion = {
  category: "shirt",
  reason: "Sample suggestion. Check it against your garment.",
};

export const surprisePrompts: readonly string[] = [
  "Turn it into a relaxed cropped version with a boxy shape.",
  "Shorten the sleeves and take in the sides for a fitted look.",
  "Make it a sleeveless top with a straight hem.",
];

export const receiptFixture: IntakeReceipt = {
  intake_id: "mock-intake-001",
  received_at: "2026-10-28T00:00:00.000Z",
};
