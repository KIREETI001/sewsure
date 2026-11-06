import { getApi, mockApi, setApi } from "@/api/client";
import type { SewSureApi } from "@/api/types";

export const MOCK_UPLOAD_FAILURE_MESSAGE = "Synthetic test: mock intake upload failed.";

/**
 * Explicit test installation only; importing this module does not change the API.
 * Refuse non-default clients so this control can never wrap a real backend.
 * Dispose in finally/afterEach after pending mutations have settled.
 */
export function installMockUploadFailure() {
  const previous = getApi();
  if (previous !== mockApi) {
    throw new Error("Mock upload simulation requires the default mock API (no nested installs).");
  }

  let failing = true;
  let disposed = false;
  const api: SewSureApi = {
    ...mockApi,
    async uploadIntake(request) {
      if (failing) throw new Error(MOCK_UPLOAD_FAILURE_MESSAGE);
      return mockApi.uploadIntake(request);
    },
  };
  setApi(api);

  return {
    /** Recovery delegates unchanged to the fixture client, including mock provenance. */
    setFailure(enabled: boolean): void {
      if (disposed) throw new Error("Mock upload simulation has been disposed.");
      failing = enabled;
    },
    /** Idempotent; never overwrite a client installed later by another owner. */
    dispose(): void {
      if (disposed) return;
      failing = false;
      disposed = true;
      if (getApi() === api) setApi(previous);
    },
  };
}
