import sample from "./fixtures/woven_shirt_crop_pass.json";
import type { IntakeDraft } from "@/state/intakeStore";
import { enableLocalJourney } from "@/api/localTransport";

/** Deliberate demo content, separate from QA-only seeds. Never an image of a real garment. */
const photo = (side: string) => ({
  uri: `data:image/svg+xml;utf8,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800"><rect width="800" height="800" fill="#e5eee8"/><path d="M250 150L130 240L190 350L250 310V650H550V310L610 350L670 240L550 150L450 200H350Z" fill="#8dad9a" stroke="#263b30" stroke-width="8"/><text x="400" y="730" text-anchor="middle" font-size="28">Synthetic ${side} — demo only</text></svg>`)}`,
  width: 800,
  height: 800,
  checked: true,
});

export function startLocalDemo(): IntakeDraft {
  enableLocalJourney();
  const dimensions = sample.measurements.measurements.garment;
  return {
    role: "user",
    guest: true,
    signedInAs: null,
    category: "shirt",
    front: photo("front"),
    back: photo("back"),
    fit: "relaxed",
    skill: "beginner",
    tools: ["scissors", "iron", "hand_sewing"],
    extraMaterials: "",
    bodyConsentVersion: null,
    uploadStatus: "not_uploaded",
    uploadProvenance: null,
    measurements: {
      ...Object.fromEntries(
        Object.entries(dimensions).map(([key, value]) => [
          key,
          {
            inputCm: String(value.value_mm / 10),
            origin: "user_entered" as const,
            confirmedAt: value.confirmed_at,
          },
        ]),
      ),
      shoulder_width: {
        inputCm: "45",
        origin: "user_entered",
        confirmedAt: "2026-11-09T10:00:00Z",
      },
      sleeve_length: { inputCm: "60", origin: "user_entered", confirmedAt: "2026-11-09T10:00:00Z" },
    },
    inspirationMode: "text",
    inspirationDraft: {
      imageUri: null,
      text: "Crop the bottom of this woven shirt and keep its sleeves.",
      surprisePrompt: null,
    },
  };
}
