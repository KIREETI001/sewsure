import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

/**
 * Studio state that must survive a failed call or a closed app: which project and job are
 * active, the idempotency key of the current attempt, and unsent edits (cm text as typed, per
 * design). The user's request itself lives in the intake store and is never cleared here.
 */
interface StudioState {
  projectId: string | null;
  jobId: string | null;
  idempotencyKey: string | null;
  /** designId -> parameter key -> cm text as typed. Cleared when a recheck succeeds. */
  editDrafts: Record<string, Record<string, string>>;
}

interface StudioActions {
  startAttempt: (projectId: string, idempotencyKey: string) => void;
  setJob: (jobId: string) => void;
  setEditText: (designId: string, key: string, text: string) => void;
  setEditDraft: (designId: string, draft: Record<string, string>) => void;
  clearEditDraft: (designId: string) => void;
  reset: () => void;
}

const initial: StudioState = { projectId: null, jobId: null, idempotencyKey: null, editDrafts: {} };

export const useStudioStore = create<StudioState & StudioActions>()(
  persist(
    (set) => ({
      ...initial,
      startAttempt: (projectId, idempotencyKey) => set({ projectId, idempotencyKey, jobId: null }),
      setJob: (jobId) => set({ jobId }),
      setEditText: (designId, key, text) =>
        set((s) => ({
          editDrafts: { ...s.editDrafts, [designId]: { ...s.editDrafts[designId], [key]: text } },
        })),
      setEditDraft: (designId, draft) =>
        set((s) => ({ editDrafts: { ...s.editDrafts, [designId]: draft } })),
      clearEditDraft: (designId) =>
        set((s) => {
          const { [designId]: _removed, ...rest } = s.editDrafts;
          return { editDrafts: rest };
        }),
      reset: () => set({ ...initial }),
    }),
    { name: "sewsure.studio", storage: createJSONStorage(() => AsyncStorage) },
  ),
);

/** Unique per attempt. Not a secret; it only de-duplicates retries of the same request. */
export const newIdempotencyKey = (): string =>
  `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
