import { StudioApiError } from "@/studio/errors";

const BASE = "http://127.0.0.1:8090/v1";
let enabled = false;
let session: string | null = null;

/** Explicit opt-in only. Session ids isolate demo owners; they are not authentication keys. */
export const isLocalJourney = (): boolean => {
  if (typeof __DEV__ === "undefined" || !__DEV__) return false;
  return (
    enabled ||
    (typeof sessionStorage !== "undefined" && sessionStorage.getItem("sewsure.local") === "1")
  );
};

export function enableLocalJourney(): void {
  enabled = true;
  if (typeof sessionStorage !== "undefined") sessionStorage.setItem("sewsure.local", "1");
}

export function disableLocalJourney(): void {
  enabled = false;
  if (typeof sessionStorage !== "undefined") sessionStorage.removeItem("sewsure.local");
}

function demoSession(): string {
  if (session) return session;
  const saved =
    typeof sessionStorage !== "undefined" ? sessionStorage.getItem("sewsure.local.session") : null;
  session = saved ?? `demo-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
  if (typeof sessionStorage !== "undefined")
    sessionStorage.setItem("sewsure.local.session", session);
  return session;
}

/** All traffic is to fixed loopback. No photo URIs, body profiles or credentials accepted here. */
export async function localRequest<T>(
  path: string,
  method = "GET",
  body?: unknown,
  key?: string,
): Promise<T> {
  if (!isLocalJourney()) throw new Error("Local demo is not enabled");
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60_000);
  try {
    const response = await fetch(`${BASE}${path}`, {
      method,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        "X-SewSure-Demo": demoSession(),
        ...(key ? { "Idempotency-Key": key } : {}),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new StudioApiError(
        {
          code: result.code ?? "LOCAL_DEMO_ERROR",
          message: result.message ?? "Local demo request failed.",
          recoverable: result.recoverable ?? true,
        },
        response.status,
      );
    }
    return result as T;
  } finally {
    clearTimeout(timeout);
  }
}
