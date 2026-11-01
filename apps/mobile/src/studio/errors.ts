import type { ApiErrorBody } from "./types";

/** A non-2xx response or failed job, in the contract's ApiError shape. User-safe by contract. */
export class StudioApiError extends Error {
  readonly code: string;
  readonly recoverable: boolean;
  readonly retryAfterS: number | null;
  readonly status: number | null;

  constructor(body: Pick<ApiErrorBody, "code" | "message" | "recoverable"> & {
    retry_after_s?: number | null;
  }, status: number | null = null) {
    super(body.message);
    this.name = "StudioApiError";
    this.code = body.code;
    this.recoverable = body.recoverable;
    this.retryAfterS = body.retry_after_s ?? null;
    this.status = status;
  }
}

export interface ShownError {
  code: string;
  message: string;
  recoverable: boolean;
  retryAfterS: number | null;
}

/** Anything thrown by the client layer becomes something the UI can show and retry. */
export const toShownError = (e: unknown, fallbackMessage: string): ShownError => {
  if (e instanceof StudioApiError) {
    return { code: e.code, message: e.message, recoverable: e.recoverable, retryAfterS: e.retryAfterS };
  }
  return { code: "NETWORK", message: fallbackMessage, recoverable: true, retryAfterS: null };
};
