import {
  categorySuggestionFixture,
  receiptFixture,
  sessionFixture,
  surprisePrompts,
} from "./fixtures";
import type { Envelope, SewSureApi } from "./types";

/**
 * Fixture-backed client. Swap this for the generated live client; every response is tagged
 * `provenance: "mock"` so screens render a MockBadge next to it.
 */
const mock = <T>(data: T): Envelope<T> => ({ data, provenance: "mock" });

let surpriseIndex = 0;

export const mockApi: SewSureApi = {
  async signIn() {
    return mock(sessionFixture);
  },
  async suggestCategory() {
    return mock(categorySuggestionFixture);
  },
  async surpriseMe() {
    const prompt = surprisePrompts[surpriseIndex % surprisePrompts.length] ?? "";
    surpriseIndex += 1;
    return mock({ prompt });
  },
  async uploadIntake() {
    return mock({ ...receiptFixture, received_at: new Date().toISOString() });
  },
};

let active: SewSureApi = mockApi;

export const getApi = (): SewSureApi => active;

/** Test seam, and the hook for swapping in the live client later. */
export const setApi = (api: SewSureApi): void => {
  active = api;
};
