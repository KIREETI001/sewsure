import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

/**
 * Local record of ruler checkpoints and DIY ticks, kept per design revision so a new revision
 * starts clean (revisions are immutable and an edit invalidates downstream work). Persisted so
 * the user can resume after the app is closed.
 */
export interface RevisionProgress {
  /** Cut plan the checkpoints were ticked against. A different plan resets them. */
  cutPlanId: string;
  checkpoints: Record<string, boolean>;
  steps: Record<string, boolean>;
  updatedAt: string;
}

interface MakeState {
  byRevision: Record<string, RevisionProgress>;
  /** True after persisted state has been read, so screens don't flash an empty state. */
  hydrated: boolean;
  setCheckpoint(revisionId: string, cutPlanId: string, checkpointId: string, value: boolean): void;
  setStep(revisionId: string, cutPlanId: string, stepId: string, value: boolean): void;
  seedSteps(revisionId: string, cutPlanId: string, stepIds: string[]): void;
}

const blank = (cutPlanId: string): RevisionProgress => ({
  cutPlanId,
  checkpoints: {},
  steps: {},
  updatedAt: new Date(0).toISOString(),
});

/** Checkpoints from an older cut plan never carry over. Step ticks are kept only for the same plan. */
const current = (s: MakeState, revisionId: string, cutPlanId: string): RevisionProgress => {
  const existing = s.byRevision[revisionId];
  return existing && existing.cutPlanId === cutPlanId ? existing : blank(cutPlanId);
};

export const useMakeStore = create<MakeState>()(
  persist(
    (set) => ({
      byRevision: {},
      hydrated: false,
      setCheckpoint: (revisionId, cutPlanId, checkpointId, value) =>
        set((s) => {
          const p = current(s, revisionId, cutPlanId);
          const checkpoints = { ...p.checkpoints, [checkpointId]: value };
          // Screens treat a locked cut step as not done, so un-ticking here re-locks it.
          return {
            byRevision: {
              ...s.byRevision,
              [revisionId]: { ...p, checkpoints, updatedAt: new Date().toISOString() },
            },
          };
        }),
      setStep: (revisionId, cutPlanId, stepId, value) =>
        set((s) => {
          const p = current(s, revisionId, cutPlanId);
          return {
            byRevision: {
              ...s.byRevision,
              [revisionId]: {
                ...p,
                steps: { ...p.steps, [stepId]: value },
                updatedAt: new Date().toISOString(),
              },
            },
          };
        }),
      seedSteps: (revisionId, cutPlanId, stepIds) =>
        set((s) => {
          const p = current(s, revisionId, cutPlanId);
          if (Object.keys(p.steps).length > 0 || stepIds.length === 0) return s;
          return {
            byRevision: {
              ...s.byRevision,
              [revisionId]: {
                ...p,
                steps: Object.fromEntries(stepIds.map((id) => [id, true])),
              },
            },
          };
        }),
    }),
    {
      name: "sewsure.make.v1",
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (s) => ({ byRevision: s.byRevision }),
      onRehydrateStorage: () => () => useMakeStore.setState({ hydrated: true }),
    },
  ),
);
