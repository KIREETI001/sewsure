import { useQuery } from "@tanstack/react-query";
import { loadMakeBundle } from "./data";

/**
 * No id means no query: callers must show the gate screen. There is deliberately no default
 * revision, so a wrong or missing route param can never open someone else's passing guide.
 */
export const useMakeBundle = (revisionId: string | undefined) =>
  useQuery({
    queryKey: ["make", revisionId ?? "none"],
    queryFn: () => loadMakeBundle(revisionId as string),
    enabled: Boolean(revisionId),
  });

/** Route params can be string[]; only a single non-empty string is a revision id. */
export const revisionIdParam = (v: string | string[] | undefined): string | undefined =>
  typeof v === "string" && v.length > 0 ? v : undefined;
