import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type {
  FitPreference,
  GarmentCategory,
  InspirationInput,
  Provenance,
  Role,
  SkillLevel,
  Tool,
} from "@/api/types";
import type { MeasurementEntry } from "@/intake/validation";

export type InspirationMode = "image" | "text" | "surprise";

export type UploadStatus = "not_uploaded" | "uploading" | "uploaded" | "failed";

export interface PhotoDraft {
  uri: string;
  width: number;
  height: number;
  /** User ticked the sharp / lit / whole-garment checks. */
  checked: boolean;
}

export interface IntakeDraft {
  role: Role | null;
  guest: boolean;
  signedInAs: string | null;
  front: PhotoDraft | null;
  back: PhotoDraft | null;
  category: GarmentCategory | null;
  fit: FitPreference | null;
  skill: SkillLevel | null;
  tools: Tool[];
  extraMaterials: string;
  /** Keyed by measurement key. Cm text as typed; mm is derived on upload. */
  measurements: Record<string, MeasurementEntry>;
  uploadStatus: UploadStatus;
  /** Provenance of the last upload receipt; "mock" means nothing left the device. */
  uploadProvenance: Provenance | null;
  /** Consent version the user accepted for body measurements; null = not shared. */
  bodyConsentVersion: string | null;
  inspirationMode: InspirationMode;
  /** One draft per mode so switching modes never discards what was typed. */
  inspirationDraft: { imageUri: string | null; text: string; surprisePrompt: string | null };
}

interface IntakeActions {
  patch: (partial: Partial<IntakeDraft>) => void;
  setMeasurement: (key: string, entry: MeasurementEntry) => void;
  reset: () => void;
}

/** Changing these does not change the upload payload. */
const SESSION_KEYS = ["role", "guest", "signedInAs", "uploadStatus", "uploadProvenance"];

const initial: IntakeDraft = {
  role: null,
  guest: false,
  signedInAs: null,
  front: null,
  back: null,
  category: null,
  fit: null,
  skill: null,
  tools: [],
  extraMaterials: "",
  measurements: {},
  uploadStatus: "not_uploaded",
  uploadProvenance: null,
  bodyConsentVersion: null,
  inspirationMode: "text",
  inspirationDraft: { imageUri: null, text: "", surprisePrompt: null },
};

/** The inspiration that applies to the selected mode only. */
export const inspirationFor = (
  mode: InspirationMode,
  draft: IntakeDraft["inspirationDraft"],
): InspirationInput | null => {
  if (mode === "image") return draft.imageUri ? { kind: "image", uri: draft.imageUri } : null;
  if (mode === "text") return draft.text.trim() ? { kind: "text", text: draft.text } : null;
  return draft.surprisePrompt ? { kind: "surprise", prompt: draft.surprisePrompt } : null;
};

/**
 * The whole intake is a local draft until the upload succeeds, so a failed upload or a closed
 * app never loses input. An in-flight upload is not persisted as "uploading".
 */
export const useIntakeStore = create<IntakeDraft & IntakeActions>()(
  persist(
    (set) => ({
      ...initial,
      // Any change to what would be uploaded makes an earlier upload stale.
      patch: (partial) =>
        set(() => {
          const stale = Object.keys(partial).some((k) => !SESSION_KEYS.includes(k));
          return stale
            ? { ...partial, uploadStatus: "not_uploaded", uploadProvenance: null }
            : partial;
        }),
      setMeasurement: (key, entry) =>
        set((s) => ({
          measurements: { ...s.measurements, [key]: entry },
          // Any edit means what is on the server (if anything) is stale.
          uploadStatus: "not_uploaded",
          uploadProvenance: null,
        })),
      reset: () => set({ ...initial }),
    }),
    {
      name: "sewsure.intake.draft.v1",
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (s) => ({
        ...s,
        uploadStatus: s.uploadStatus === "uploading" ? "not_uploaded" : s.uploadStatus,
      }),
    },
  ),
);
