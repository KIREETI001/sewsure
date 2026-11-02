import { useQuery, type QueryClient } from "@tanstack/react-query";
import { useFocusEffect } from "expo-router";
import { useCallback, useEffect, useRef } from "react";
import { AppState } from "react-native";
import { loadMakeBundle } from "./data";

/**
 * No id means no query: callers must show the gate screen. There is deliberately no default
 * revision, so a wrong or missing route param can never open someone else's passing guide.
 *
 * A guide left open can go stale or be superseded on another device, so the bundle is read again
 * whenever the screen regains focus and whenever the app returns to the foreground.
 */
export const useMakeBundle = (revisionId: string | undefined) => {
  const q = useQuery({
    queryKey: ["make", revisionId ?? "none"],
    queryFn: () => loadMakeBundle(revisionId as string),
    enabled: Boolean(revisionId),
  });
  const refetch = q.refetch;
  const enabled = Boolean(revisionId);
  const firstFocus = useRef(true);

  useFocusEffect(
    useCallback(() => {
      // The query already fetches on mount; only later focuses need a refetch.
      if (firstFocus.current) {
        firstFocus.current = false;
        return;
      }
      if (enabled) void refetch();
    }, [enabled, refetch]),
  );

  useEffect(() => {
    if (!enabled) return;
    const sub = AppState.addEventListener("change", (s) => {
      if (s === "active") void refetch();
    });
    return () => sub.remove();
  }, [enabled, refetch]);

  return q;
};

/** Call when a revision is created (an edit or a recheck): the old id's cached guide must not be reused. */
export const invalidateMake = (client: QueryClient, ...revisionIds: string[]) =>
  Promise.all(revisionIds.map((id) => client.invalidateQueries({ queryKey: ["make", id] })));

/** Route params can be string[]; only a single non-empty string is a revision id. */
export const revisionIdParam = (v: string | string[] | undefined): string | undefined =>
  typeof v === "string" && v.length > 0 ? v : undefined;
