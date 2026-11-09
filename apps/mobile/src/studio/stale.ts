/** A missing flag is treated as stale, so an old response can never read as current. */
export const isStale = (r: { stale?: boolean }): boolean => r.stale !== false;

/** The cut guide opens only for a passing, current revision. */
export const canOpenCutGuide = (r: { status: string; stale?: boolean }): boolean =>
  r.status === "PASS_SUPPORTED_CHECKS" && !isStale(r);
