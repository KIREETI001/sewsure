import { useQuery } from "@tanstack/react-query";
import { DEFAULT_REVISION_ID, loadMakeBundle } from "./data";

export const useMakeBundle = (revisionId?: string) =>
  useQuery({
    queryKey: ["make", revisionId ?? DEFAULT_REVISION_ID],
    queryFn: () => loadMakeBundle(revisionId ?? DEFAULT_REVISION_ID),
  });
