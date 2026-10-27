import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type {
  FitPreference,
  GarmentCategory,
  InspirationInput,
  Role,
  SkillLevel,
  Tool,
} from "@/api/types";
import type { MeasurementEntry } from "@/intake/validation";

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
  inspiration: InspirationInput | null;
  fit: FitPreference | null;
  skill: SkillLevel | null;
  tools: Tool[];
  extraMaterials: string;
  /** Keyed by measurement key. Cm text as typed; mm is derived on upload. */
  measurements: Record<string, MeasurementEntry>;
  uploadStatus: UploadStatus;
}

interface IntakeActions {
  patch: (partial: Partial<IntakeDraft>) => void;
  setMeasurement: (key: string, entry: MeasurementEntry) => void;
  reset: () => void;
}

const initial: IntakeDraft = {
  role: null,
  guest: false,
  signedInAs: null,
  front: null,
  back: null,
  category: null,
  inspiration: null,
  fit: null,
  skill: null,
  tools: [],
  extraMaterials: "",
  measurements: {},
  uploadStatus: "not_uploaded",
};

/**
 * The whole intake is a local draft until the upload succeeds, so a failed upload or a closed
 * app never loses input. An in-flight upload is not persisted as "uploading".
 */
export const useIntakeStore = create<IntakeDraft & IntakeActions>()(
  persist(
    (set) => ({
      ...initial,
      patch: (partial) => set(partial),
      setMeasurement: (key, entry) =>
        set((s) => ({
          measurements: { ...s.measurements, [key]: entry },
          // Any edit means what is on the server (if anything) is stale.
          uploadStatus: "not_uploaded",
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
