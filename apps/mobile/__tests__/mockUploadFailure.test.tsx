import AsyncStorage from "@react-native-async-storage/async-storage";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { getApi, mockApi, setApi } from "@/api/client";
import { receiptFixture } from "@/api/fixtures";
import type { IntakeRequest } from "@/api/types";
import { applyIntakeSeed, createIntakeSeed } from "@/dev/intakeSeeds";
import {
  installMockUploadFailure,
  MOCK_UPLOAD_FAILURE_MESSAGE,
} from "@/dev/mockUploadFailure";
import { garmentSpecsFor } from "@/intake/measurements";
import { buildMeasurementRecords } from "@/intake/validation";
import { useIntakeStore } from "@/state/intakeStore";
import MeasurementsScreen from "../app/(intake)/measurements";

const seed = createIntakeSeed("measurements-confirmed");
const request: IntakeRequest = {
  front_photo_uri: seed.front!.uri,
  back_photo_uri: seed.back!.uri,
  category: "shirt",
  inspiration: { kind: "text", text: seed.inspirationDraft.text },
  fit_preference: "relaxed",
  skill_level: "beginner",
  tools: [],
  extra_materials: "",
  body_consent_version: null,
  measurements: buildMeasurementRecords(garmentSpecsFor("shirt"), seed.measurements),
};

let controller: ReturnType<typeof installMockUploadFailure> | undefined;
let queryClient: QueryClient | undefined;

beforeEach(async () => {
  setApi(mockApi);
  await useIntakeStore.persist.rehydrate();
  useIntakeStore.getState().reset();
});

afterEach(async () => {
  await cleanup();
  queryClient?.clear();
  queryClient = undefined;
  controller?.dispose();
  controller = undefined;
  jest.restoreAllMocks();
  setApi(mockApi);
  useIntakeStore.getState().reset();
});

it("rejects predictably until disabled, then returns the unchanged mock envelope", async () => {
  const upload = jest.spyOn(mockApi, "uploadIntake");
  const fetch = jest.spyOn(global, "fetch").mockRejectedValue(new Error("Network forbidden"));
  controller = installMockUploadFailure();
  for (let attempt = 0; attempt < 2; attempt++) {
    await expect(getApi().uploadIntake(request)).rejects.toThrow(MOCK_UPLOAD_FAILURE_MESSAGE);
  }
  expect(upload).not.toHaveBeenCalled();
  controller.setFailure(false);
  const response = await getApi().uploadIntake(request);
  expect(response).toEqual(await upload.mock.results[0]!.value);
  expect(response).toEqual({
    data: { intake_id: receiptFixture.intake_id, received_at: expect.any(String) },
    provenance: "mock",
  });
  expect(Number.isNaN(Date.parse(response.data.received_at))).toBe(false);
  expect(upload).toHaveBeenCalledWith(request);
  controller.setFailure(true);
  await expect(getApi().uploadIntake(request)).rejects.toThrow(MOCK_UPLOAD_FAILURE_MESSAGE);
  expect(upload).toHaveBeenCalledTimes(1);
  expect(fetch).not.toHaveBeenCalled();
});

it("leaves other API methods and the default mock object unchanged", () => {
  const originalUpload = mockApi.uploadIntake;
  controller = installMockUploadFailure();
  expect(getApi().signIn).toBe(mockApi.signIn);
  expect(getApi().suggestCategory).toBe(mockApi.suggestCategory);
  expect(getApi().surpriseMe).toBe(mockApi.surpriseMe);
  expect(mockApi.uploadIntake).toBe(originalUpload);
});

it("restores the previous client and clears failure even for a retained wrapper", async () => {
  controller = installMockUploadFailure();
  const retained = getApi();
  controller.dispose();
  controller.dispose();
  expect(getApi()).toBe(mockApi);
  expect(() => controller!.setFailure(true)).toThrow("disposed");
  await expect(retained.uploadIntake(request)).resolves.toMatchObject({ provenance: "mock" });
  controller = installMockUploadFailure();
  await expect(getApi().uploadIntake(request)).rejects.toThrow(MOCK_UPLOAD_FAILURE_MESSAGE);
  controller.dispose();
  await expect(getApi().uploadIntake(request)).resolves.toMatchObject({ provenance: "mock" });
});

it("refuses other clients without invoking them", () => {
  const uploadIntake = jest.fn();
  const other = { ...mockApi, uploadIntake };
  setApi(other);
  expect(() => installMockUploadFailure()).toThrow("requires the default mock API");
  expect(getApi()).toBe(other);
  expect(uploadIntake).not.toHaveBeenCalled();
});

it("rejects nested installation and does not overwrite a subsequently installed client", () => {
  controller = installMockUploadFailure();
  const installed = getApi();
  expect(() => installMockUploadFailure()).toThrow("no nested installs");
  expect(getApi()).toBe(installed);
  const other = { ...mockApi };
  setApi(other);
  controller.dispose();
  expect(getApi()).toBe(other);
});

it("preserves the entire confirmed draft on failure and retries the same payload after recovery", async () => {
  applyIntakeSeed("measurements-confirmed", useIntakeStore.getState());
  controller = installMockUploadFailure();
  const upload = jest.spyOn(getApi(), "uploadIntake");
  queryClient = new QueryClient({
    defaultOptions: {
      mutations: { retry: false, gcTime: Infinity },
      queries: { retry: false, gcTime: Infinity },
    },
  });
  await render(
    <QueryClientProvider client={queryClient}>
      <MeasurementsScreen />
    </QueryClientProvider>,
  );
  await fireEvent.press(screen.getByRole("button", { name: "Upload" }));
  await waitFor(() => expect(useIntakeStore.getState().uploadStatus).toBe("failed"));
  expect(await screen.findAllByText(/Upload failed/)).not.toHaveLength(0);
  expect(useIntakeStore.getState()).toMatchObject({ ...seed, uploadStatus: "failed" });
  const persisted = JSON.parse((await AsyncStorage.getItem("sewsure.intake.draft.v1"))!);
  expect(persisted.state).toEqual({ ...seed, uploadStatus: "failed" });
  expect(upload).toHaveBeenCalledTimes(1);
  expect(upload).toHaveBeenNthCalledWith(1, request);

  controller.setFailure(false);
  await fireEvent.press(screen.getByRole("button", { name: "Try upload again" }));
  await waitFor(() => expect(useIntakeStore.getState().uploadStatus).toBe("uploaded"));
  expect(screen.getByLabelText("Sample data, not a real result")).toBeTruthy();
  expect(useIntakeStore.getState()).toMatchObject({
    ...seed,
    uploadStatus: "uploaded",
    uploadProvenance: "mock",
  });
  expect(upload).toHaveBeenCalledTimes(2);
  expect(upload).toHaveBeenNthCalledWith(2, request);
  expect(upload.mock.calls[1]![0]).toEqual(upload.mock.calls[0]![0]);
});

it("keeps the normal measurement validation gate active during simulation", async () => {
  applyIntakeSeed("measurements-signed-in", useIntakeStore.getState());
  controller = installMockUploadFailure();
  controller.setFailure(false);
  const upload = jest.spyOn(getApi(), "uploadIntake");
  queryClient = new QueryClient({ defaultOptions: { mutations: { retry: false, gcTime: Infinity } } });
  await render(
    <QueryClientProvider client={queryClient}>
      <MeasurementsScreen />
    </QueryClientProvider>,
  );
  await fireEvent.press(screen.getByRole("button", { name: "Upload" }));
  expect(screen.getByText(/Still needed: Chest/)).toBeTruthy();
  expect(upload).not.toHaveBeenCalled();
  expect(useIntakeStore.getState().uploadStatus).toBe("not_uploaded");
});
