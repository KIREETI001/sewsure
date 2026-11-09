import { act, fireEvent, render, screen } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { localStudioApi, prepareLocalProject, loadLocalMakeBundle } from "@/api/localJourney";
import { disableLocalJourney } from "@/api/localTransport";
import { startLocalDemo } from "@/studio/localDemo";
import { useIntakeStore } from "@/state/intakeStore";
import { useStudioStore } from "@/state/studioStore";
import { garmentSpecsFor } from "@/intake/measurements";
import { missingSpecs } from "@/intake/validation";
import MeasurementsScreen from "../app/(intake)/measurements";

jest.mock("expo-router", () => ({ useRouter: () => ({ push: jest.fn() }) }));
const originalFetch = global.fetch;
const mockFetch = jest.fn();
const ok = (data: unknown) => ({ ok: true, json: async () => data });

beforeEach(() => {
  disableLocalJourney();
  mockFetch.mockReset();
  global.fetch = mockFetch;
  useIntakeStore.getState().reset();
  useStudioStore.getState().reset();
});
afterEach(() => {
  disableLocalJourney();
  global.fetch = originalFetch;
});

it("starts with a complete synthetic shirt and an enabled continuation", async () => {
  const draft = startLocalDemo();
  expect(missingSpecs(garmentSpecsFor("shirt"), draft.measurements)).toEqual([]);
  useIntakeStore.getState().patch(draft);
  const client = new QueryClient({ defaultOptions: { mutations: { gcTime: Infinity } } });
  await render(
    <QueryClientProvider client={client}>
      <MeasurementsScreen />
    </QueryClientProvider>,
  );
  expect(screen.getByRole("button", { name: "Check redesign with local model" })).toBeEnabled();
  expect(screen.queryByText("Body measurements (optional)")).toBeNull();
  expect(screen.getByText(/Synthetic demo only/)).toBeTruthy();
  await fireEvent.changeText(screen.getByLabelText("Requested finished length (cm)"), "bad");
  expect(screen.getByRole("button", { name: "Check redesign with local model" })).toBeDisabled();
});

it("sends garment mm records without photos or body data and preserves request intent", async () => {
  const draft = startLocalDemo();
  mockFetch.mockResolvedValueOnce(ok({ project_id: "prj-local" })).mockResolvedValueOnce(ok({}));
  await prepareLocalProject(draft, 450, 600, "lengthen");
  const sent = JSON.parse(mockFetch.mock.calls[1][1].body);
  expect(sent.garment.shoulder_to_hem.value_mm).toBe(780);
  expect(sent.garment.placket_end_from_shoulder.value_mm).toBe(600);
  expect(sent.body).toBeUndefined();
  expect(JSON.stringify(mockFetch.mock.calls)).not.toContain("data:image");
  mockFetch.mockResolvedValueOnce(ok({ job_id: "job-local" }));
  await localStudioApi.generate(
    "prj-local",
    { inspiration: { kind: "text", text: "Synthetic request" } },
    { idempotencyKey: "local-test-0001" },
  );
  const generated = JSON.parse(mockFetch.mock.calls[2][1].body);
  expect(generated.inspiration.requested_features.transformation).toBe("lengthen");
  expect(generated.inspiration.requested_features.target_finished_length_mm).toBe(450);
});

it("uses the same revision id for cut and DIY, and retains server stale rejection", async () => {
  startLocalDemo();
  mockFetch
    .mockResolvedValueOnce(ok({ revision_id: "rev-new" }))
    .mockResolvedValueOnce(ok({ revision_id: "rev-new" }))
    .mockResolvedValueOnce(ok({ revision_id: "rev-new" }));
  const bundle = await loadLocalMakeBundle("rev-new");
  expect(bundle.cutPlan?.revision_id).toBe("rev-new");
  expect(mockFetch.mock.calls.map(([url]) => url)).toEqual([
    "http://127.0.0.1:8090/v1/revisions/rev-new",
    "http://127.0.0.1:8090/v1/revisions/rev-new/cut-plan",
    "http://127.0.0.1:8090/v1/revisions/rev-new/diy-steps",
  ]);
  mockFetch
    .mockResolvedValueOnce(ok({ revision_id: "rev-old" }))
    .mockResolvedValueOnce({
      ok: false,
      status: 409,
      json: async () => ({ code: "REVISION_STALE", message: "Recheck", recoverable: true }),
    });
  expect((await loadLocalMakeBundle("rev-old")).cutPlanError?.code).toBe("REVISION_STALE");
});

it("keeps local failures visible without falling back to preset passing data", async () => {
  startLocalDemo();
  mockFetch.mockRejectedValue(new Error("local service unavailable"));
  await act(async () => {
    await expect(loadLocalMakeBundle("rev-missing")).rejects.toThrow("local service unavailable");
  });
});
